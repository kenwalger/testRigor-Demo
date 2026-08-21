import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash

import mailer
from config import DB_PATH, SEED_EMAIL, SEED_NAME, SEED_PASSWORD

load_dotenv()

app = Flask(__name__)

# The secret key uses a fixed development fallback on purpose. Generating a random
# fallback (os.urandom / uuid / time) would invalidate every active session each time
# the Flask reloader restarts the process, which would break the recorded demo.
# Do not "improve" this by making the fallback random.
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "golden-tire-dev-secret-key")

# The tunnel that exposes this server terminates TLS and forwards plain HTTP to
# 127.0.0.1. Without trusting its forwarded headers, url_for(_external=True) would
# build http://127.0.0.1:5000/... links, which are useless in a mail client.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# A reset link is good for one use, within this window.
RESET_TOKEN_TTL = timedelta(hours=1)


def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        g._db = db
    return db


@app.teardown_appcontext
def close_db(_exc):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL UNIQUE,
                expires_at TEXT NOT NULL,
                used_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        row = conn.execute(
            "SELECT id FROM users WHERE email = ?", (SEED_EMAIL,)
        ).fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (SEED_NAME, SEED_EMAIL, generate_password_hash(SEED_PASSWORD)),
            )
        conn.commit()
    finally:
        conn.close()


def current_user():
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return get_db().execute(
        "SELECT id, name, email FROM users WHERE id = ?", (user_id,)
    ).fetchone()


def create_reset_token(user_id):
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.now(timezone.utc) + RESET_TOKEN_TTL).isoformat()
    db = get_db()
    db.execute(
        "INSERT INTO password_reset_tokens (user_id, token, expires_at)"
        " VALUES (?, ?, ?)",
        (user_id, token, expires_at),
    )
    db.commit()
    return token


def valid_reset_token(token):
    """Return the token row, or None if it is unknown, used, or expired."""
    row = get_db().execute(
        "SELECT id, user_id, expires_at FROM password_reset_tokens"
        " WHERE token = ? AND used_at IS NULL",
        (token,),
    ).fetchone()
    if row is None:
        return None
    if datetime.fromisoformat(row["expires_at"]) <= datetime.now(timezone.utc):
        return None
    return row


def send_reset_email(user, link):
    text_body = f"""Hi {user['name']},

We received a request to reset the password for your Golden Tire Customer
Portal account.

Open this link to choose a new password:
{link}

The link can be used once and expires in one hour. If you did not ask for a
password reset, you can ignore this message.

- Golden Tire Company
"""

    html_body = f"""<html>
  <body style="font-family: Arial, Helvetica, sans-serif;">
    <p>Hi {user['name']},</p>
    <p>We received a request to reset the password for your Golden Tire
      Customer Portal account.</p>
    <p><a href="{link}">Reset your password</a></p>
    <p>The link can be used once and expires in one hour. If you did not ask
      for a password reset, you can ignore this message.</p>
    <p>&mdash; Golden Tire Company</p>
  </body>
</html>
"""

    mailer.send_email(
        to=user["email"],
        subject="Reset your Golden Tire password",
        body=text_body,
        html=html_body,
    )


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    error = None
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        row = get_db().execute(
            "SELECT id, password_hash FROM users WHERE email = ?", (email,)
        ).fetchone()
        if row is not None and check_password_hash(row["password_hash"], password):
            session.clear()
            session["user_id"] = row["id"]
            return redirect(url_for("dashboard"))
        error = "Invalid email or password"

    return render_template("login.html", error=error)


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    error = None
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        row = get_db().execute(
            "SELECT id, name, email FROM users WHERE email = ?", (email,)
        ).fetchone()
        if row is not None:
            token = create_reset_token(row["id"])
            link = url_for("reset_password", token=token, _external=True)
            try:
                send_reset_email(row, link)
            except (mailer.MailerConfigError, OSError) as exc:
                # smtplib's exceptions subclass OSError. Report the failure on the
                # page instead of returning a 500.
                print(f"Password reset email to {row['email']} failed: {exc}")
                error = "We could not send the reset email. Please try again."

        if error is None:
            # Shown whether or not the address matched an account, so this page
            # cannot be used to find out who has one.
            return render_template("forgot_password.html", sent=True)

    return render_template("forgot_password.html", error=error)


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    row = valid_reset_token(token)
    if row is None:
        # A link that was already used gets its own message, so a customer who
        # opens it twice is told what actually happened.
        used = get_db().execute(
            "SELECT 1 FROM password_reset_tokens"
            " WHERE token = ? AND used_at IS NOT NULL",
            (token,),
        ).fetchone() is not None
        return render_template("reset_password.html", invalid=True, used=used)

    error = None
    if request.method == "POST":
        password = request.form.get("password") or ""
        confirm_password = request.form.get("confirm_password") or ""
        if not password:
            error = "Please enter a new password"
        elif password != confirm_password:
            error = "Passwords do not match"
        else:
            db = get_db()
            db.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (generate_password_hash(password), row["user_id"]),
            )
            # Burn this link and any other outstanding one for the same customer.
            db.execute(
                "UPDATE password_reset_tokens SET used_at = ?"
                " WHERE user_id = ? AND used_at IS NULL",
                (datetime.now(timezone.utc).isoformat(), row["user_id"]),
            )
            db.commit()
            session.clear()
            return render_template("reset_done.html")

    return render_template("reset_password.html", token=token, error=error)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user())


@app.route("/account")
@login_required
def account():
    return render_template("account.html", user=current_user())


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


init_db()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
