import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()


class MailerConfigError(RuntimeError):
    pass


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise MailerConfigError(
            f"Missing required environment variable: {name}. "
            f"Copy .env.example to .env and set SMTP_HOST, SMTP_PORT, "
            f"SMTP_USERNAME, SMTP_PASSWORD, and SMTP_FROM."
        )
    return value


def send_email(to: str, subject: str, body: str) -> None:
    host = _require("SMTP_HOST")
    port_raw = _require("SMTP_PORT")
    username = _require("SMTP_USERNAME")
    password = _require("SMTP_PASSWORD")
    sender = _require("SMTP_FROM")

    try:
        port = int(port_raw)
    except ValueError as exc:
        raise MailerConfigError(
            f"SMTP_PORT must be an integer, got: {port_raw!r}"
        ) from exc

    message = EmailMessage()
    message["From"] = sender
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    # This function is intended to be called from inside a web request in a later
    # demonstration. Without a timeout, an unreachable or slow SMTP server would
    # hang the request thread indefinitely instead of failing cleanly.
    with smtplib.SMTP(host, port, timeout=10) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(username, password)
        smtp.send_message(message)

    print(f"Sent email to {to} via {host}:{port}")
