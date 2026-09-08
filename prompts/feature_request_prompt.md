
Add a password reset flow to the Golden Tire Customer Portal.

Customers who forget their password need a way to get back into their
account without contacting support.

Behavior:

- The login page gets a link whose visible text is exactly:
    Forgot password
- That link leads to a page with an "Email" field and a "Send reset
  link" button.
- Submitting a known email address sends that customer an email with a
  link back into the portal. Use the existing mailer.send_email helper.
- The email subject must be exactly:
    Reset your Golden Tire password
- The email body must contain a link whose visible text is exactly:
    Reset your password
- Opening that link shows a page with "New password" and "Confirm new
  password" fields and an "Update password" button.
- On success, show exactly:
    Your password has been updated
- The customer can then sign in with the new password.

Important: the link in the email must be an absolute URL built from the
incoming request host, not a hardcoded localhost address. Customers open
these links from their email client, so a localhost link would be
useless to them.

Keep it consistent with the existing app: same style, same structure,
sqlite3, Werkzeug hashing, no new dependencies.
