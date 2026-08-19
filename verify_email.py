import sys

from mailer import send_email

TARGET = "goldentire.demo@testrigor-mail.com"


def main() -> int:
    try:
        send_email(
            to=TARGET,
            subject="Golden Tire Customer Portal mail transport check",
            body=(
                "This is a test message from the Golden Tire Customer Portal "
                "verify_email.py script. If you received this, SMTP is "
                "configured correctly."
            ),
        )
    except Exception as exc:
        print(f"Email delivery FAILED: {exc}", file=sys.stderr)
        return 1

    print(f"Email delivery succeeded to {TARGET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
