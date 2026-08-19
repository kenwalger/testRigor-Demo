# Golden Tire Customer Portal

A small Flask demonstration application for **Golden Tire Company**. *Keeping You Rolling Since 1957.*

This is a deliberately limited baseline used for a screen-recorded demonstration of AI-assisted code generation and end-to-end behavioral testing. It is not a production system.

## Requirements

- Python 3.10 or newer

## Setup

```bash
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate it
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy the environment template and fill in SMTP values
cp .env.example .env
# then edit .env

# 5. Start the application
python app.py
```

The application runs at:

http://localhost:5000

## Demo credentials

- **Email:** `goldentire.demo@testrigor-mail.com`
- **Password:** `oldpassword`

These are intentionally synthetic credentials for a local demonstration application. They are not, and should not be treated as, real user credentials.

## Verifying email delivery

```bash
python verify_email.py
```

This sends a single test message to `goldentire.demo@testrigor-mail.com` using the SMTP settings in `.env`. The mail transport (`mailer.send_email`) is intentionally **not** connected to any application route, view, or template. It exists so that mail delivery can be confirmed separately before the demonstration begins.

## Resetting the application

```bash
python reset_db.py
```

This is the single command that returns the application to its original seeded state (one demo user). It is safe to run repeatedly.

## Recording the demonstration

### Why a public tunnel is needed

The end-to-end testing service runs tests from its own cloud infrastructure against a URL it can reach. An application running only on `localhost` is not reachable from that infrastructure, so the tests cannot hit it directly.

A tunnel exposes the local Flask development server at a public HTTPS URL. This keeps the fast local edit-and-reload cycle intact: code changes still trigger the Flask reloader instantly, without redeploying anything on every change.

### Installing and running ngrok

1. **Install ngrok.**

   On macOS with Homebrew:

   ```bash
   brew install --cask ngrok
   ```

   On Windows or Linux, download the binary from https://ngrok.com/download, unzip it, and place it somewhere on the `PATH`.

2. **Add your authtoken.** Copy the token from the ngrok dashboard, then run:

   ```bash
   ngrok config add-authtoken <your-authtoken>
   ```

   This only needs to be done once per machine.

3. **Start the tunnel against port 5000**, with the Flask app already running:

   ```bash
   ngrok http 5000
   ```

4. **Read the public forwarding URL** from the ngrok output. Look for the `Forwarding` line, for example:

   ```
   Forwarding  https://ab12-34-56-78-90.ngrok-free.app -> http://localhost:5000
   ```

   The `https://...ngrok-free.app` address is the public URL.

5. **Confirm the tunnel** by opening that HTTPS URL in a browser. You should see the Golden Tire Customer Portal login page.

> **Recommended: use a reserved static domain if your ngrok plan offers one.**
>
> Start the tunnel with:
>
> ```bash
> ngrok http --domain=your-reserved-domain.ngrok-free.app 5000
> ```
>
> Without a reserved domain, ngrok issues a new random subdomain every time the tunnel restarts, and the testing tool's URL has to be updated each time. A reserved domain stays the same across restarts, so the testing tool can be configured once.

### Order of operations before recording

1. Activate the virtual environment.
2. Run `python reset_db.py` to return to the seeded state.
3. Start the application with `python app.py`.
4. Start the ngrok tunnel with `ngrok http 5000` (or with `--domain=...` if a reserved domain is configured) and copy the forwarding URL.
5. Run `python verify_email.py` once and confirm the message is received at `goldentire.demo@testrigor-mail.com`, so mail delivery is known good before recording begins.
6. Set the tunnel URL as the test suite URL in the testing tool, and whitelist the domain there if the tool requires it.
7. Open a fresh private or incognito browser window before starting the take.

### Between takes

Resetting the database recreates the seeded user with the same row id. Because the Flask secret key is intentionally fixed, an existing session cookie will still be valid and will still resolve to that user. The practical consequence is that after a reset the browser can remain logged in, and visiting `/login` will redirect straight to `/dashboard`.

Remedy: clear cookies for the tunnel domain, or use a fresh private window for each take. This only affects the operator's own browser, since the testing service starts each run in a new browser session and never carries state between runs.

Do not "fix" this by randomizing the Flask secret key. The fixed key is deliberate. Randomizing it would log the operator out every time the Flask reloader picks up a code change during recording, which is worse than the occasional need to clear a cookie.

### Known timing

`mailer.send_email` performs a synchronous SMTP send with a 10 second timeout. Once it is called from a request during the demonstration, that request will take a few seconds to complete while the mail server is contacted. This is expected behavior, not a fault in the application.
