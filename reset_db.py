import os
import sqlite3

from werkzeug.security import generate_password_hash

from config import DB_PATH, SEED_EMAIL, SEED_NAME, SEED_PASSWORD


def main() -> None:
    removed = False
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        removed = True

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL UNIQUE,
                expires_at TEXT NOT NULL,
                used_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (SEED_NAME, SEED_EMAIL, generate_password_hash(SEED_PASSWORD)),
        )
        conn.commit()
    finally:
        conn.close()

    action = "Reset" if removed else "Created"
    print(f"{action} database at {DB_PATH}")
    print(f"Seeded 1 user: {SEED_EMAIL}")


if __name__ == "__main__":
    main()
