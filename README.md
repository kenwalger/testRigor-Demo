# Golden Tire Customer Portal

A small Flask demonstration application for **Golden Tire Company**. *Keeping You Rolling Since 1957.*

This is a deliberately limited baseline used for a screen-recorded demonstration of AI-assisted code generation and end-to-end behavioral testing. It is not a production system.

The application ships **without** a password reset flow. That absence is intentional: the reset feature is generated live during the demonstration, and an end-to-end behavioral test written beforehand decides whether the generated implementation is correct.

## Requirements

- Python 3.10 or newer
- An ngrok account and the ngrok CLI
- An SMTP account for outbound mail
- An account with the end-to-end testing service

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

The seed address is deliberately a real, deliverable address on the testing service's inbox domain rather than a reserved example domain. Mail must actually reach it. Do not change it to `example.com`, `.test`, or any other non-routable address.

## Email configuration

The testing service supplies the destination inbox only. Outbound mail needs a separate SMTP provider.

### Gmail

Gmail no longer accepts account passwords over SMTP. An app-specific password is required, and app passwords are only available once 2-Step Verification is enabled on the account.

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your.address@gmail.com
SMTP_PASSWORD=<16 characters, spaces stripped>
SMTP_FROM=your.address@gmail.com
```

Three things that commonly go wrong:

- Using the account password instead of an app password. This fails with a `534 5.7.9 Application-specific password required` error.
- Leaving the spaces in the app password. Google displays it in four groups of four for readability. Strip them.
- Setting `SMTP_FROM` to an address other than the authenticated account. Gmail rejects the send.

### Alternatives

Brevo, Mailgun, and Resend all offer free tiers with SMTP credentials and no 2FA requirement. Worth using instead of a personal Gmail account if this repository is ever published.

### FLASK_SECRET_KEY

Leave this unset. The application falls back to a fixed development key, which is what the demonstration needs. See "Between takes" below.

## Verifying email delivery

```bash
python verify_email.py
```

This sends a single test message using the SMTP settings in `.env`. The mail transport (`mailer.send_email`) is intentionally **not** connected to any application route, view, or template in the baseline. It exists so mail delivery can be confirmed before the demonstration begins. The generated password reset feature wires it up.

**Note on how the email check behaves.** The testing service's email check is forward-looking: it starts watching the inbox when the step begins and waits for mail to arrive during its wait window. Messages that arrived before the step started do not match. Two consequences:

- Stale mail in the inbox will not cause false passes, so the inbox does not need clearing between runs.
- A standalone email check with nothing to trigger a send will always fail. The real test works because it clicks "Send reset link" a few steps earlier.
- That wait window is roughly a minute of real time in every full run. Budget for it.

## Resetting the database

```bash
python reset_db.py
```

Returns the application to its original seeded state (one demo user, password `oldpassword`). Safe to run repeatedly.

The database file is gitignored, so `git checkout` will not touch it. Resetting code and resetting data are two separate steps.

---

# Recording the demonstration

## Why a public tunnel is needed

The end-to-end testing service runs tests from its own cloud infrastructure against a URL it can reach. An application running only on `localhost` is not reachable from that infrastructure.

A tunnel exposes the local Flask development server at a public HTTPS URL. This keeps the fast local edit-and-reload cycle intact: code changes still trigger the Flask reloader instantly, without redeploying anything.

## Installing and running ngrok

1. **Install ngrok.**

   Windows with Chocolatey:

   ```powershell
   choco install ngrok
   ```

   macOS with Homebrew:

   ```bash
   brew install --cask ngrok
   ```

   Otherwise download the binary from https://ngrok.com/download, unzip it, and place it on the `PATH`.

   If ngrok was installed through a package manager, upgrade it through that package manager. Running `ngrok update` against a package-managed binary fails with an access-denied error and desynchronizes the package manager's records.

2. **Add your authtoken.** Once per machine:

   ```bash
   ngrok config add-authtoken <your-authtoken>
   ```

   Check existing configuration with `ngrok config check`.

3. **Start the tunnel** against port 5000, with the Flask app already running:

   ```bash
   ngrok http 5000
   ```

4. **Read the public forwarding URL** from the `Forwarding` line in the ngrok output.

5. **Confirm the tunnel** by opening that HTTPS URL in a browser. The Golden Tire login page should load.

> **Strongly recommended: use a reserved static domain.**
>
> ```bash
> ngrok http --url your-reserved-domain.ngrok.app 5000
> ```
>
> Older ngrok versions spell this flag `--domain`. Run `ngrok http --help` to confirm which your version uses.
>
> Without a reserved domain, ngrok issues a new random subdomain on every restart, and the test suite URL has to be updated and re-whitelisted each time. Across a rehearsal session and several takes this becomes the single most tedious part of the setup.

## One-time setup before the first rehearsal

1. Create the baseline tag on a clean working tree:

   ```bash
   git tag demo-baseline
   ```

   Everything after this point is generated live and thrown away between runs. The tag is what makes each run repeatable.

2. Create the test suite in the testing service. Set **AI test case generation to 0**. Auto-generated cases would contradict the premise that the specification was written by hand, first.

3. Set the suite URL to the ngrok forwarding URL, bare origin with no path. Whitelist the domain if required.

4. Set the suite login credentials to the seeded email and `oldpassword`.

5. Create the single password reset test case. Do not use the built-in `login` rule or `stored value "password"` anywhere inside it. The seeded password changes during the run, so those stored values go stale after the first pass.

6. Confirm the tunnel is reachable from the service with a two-step throwaway test: open the suite URL, check the page contains "Sign In". Delete it once it passes.

## Resetting to a clean state

Run this before every rehearsal pass and before every take. Not after: starting clean is what matters, and anything done after a reset leaves the next run in an unknown state.

```bash
# 1. Discard generated code and return to the baseline
git checkout demo-baseline

# 2. Reset the database
python reset_db.py

# 3. Restart the application
python app.py
```

Then clear cookies for the tunnel domain, or open a fresh private browser window. See "Between takes" below for why.

The ngrok tunnel does not need restarting. Leave it running for the whole session.

## The demonstration loop

Three test runs, not two. The middle one is the point of the demonstration.

### Run 1: red against the baseline

Run the test case against the untouched application.

It fails almost immediately, on the "Forgot password" step, because the feature does not exist. This establishes that the specification is real and predates the implementation.

### Generate the feature

Give the coding agent `feature_request_prompt.md`.

The prompt is written the way a product manager would file a ticket. It names the pages, fields, and user-facing copy, and says nothing about how reset tokens should behave. That omission is deliberate.

When it finishes, reload the login page. A "Forgot password" link should now be present.

**Do not click through the reset flow by hand.** Doing so consumes the token and leaves the test running against an already-used link, which produces a confusing failure at the wrong step. Verification is the test's job. That is the argument the demonstration is making.

### Run 2: red on the reused link

Run the test case again.

The expected failure is the final step: after the reset link has been used to set a new password, opening the same link a second time still works. The token was never invalidated.

This is the failure the whole demonstration is built on. Confirm during rehearsal that it reproduces reliably.

### Repair

Copy the failing step text out of the test results. Paste it into the agent along with `repair_prompt.md`.

### Run 3: green

Run the test case once more. It should pass end to end.

## What to confirm during rehearsal

Run the full loop at least twice before recording, and confirm all four:

1. **The single-use failure reproduces.** If the agent gets it right on the first pass, find a different genuine gap in the specification rather than manufacturing one.
2. **The reset link points at the tunnel.** Check that the email contains the ngrok host and an `https` scheme, not `localhost` and not plain `http`. This is the most likely boring failure.
3. **Wall-clock time for a full pass.** The email wait alone is around a minute. Knowing the total decides whether the waits get narrated or cut.
4. **Nothing in the test relies on the old password.** After any full pass the seeded password is no longer `oldpassword` until the database is reset.

## Between takes

Resetting the database recreates the seeded user with the same row id. Because the Flask secret key is intentionally fixed, an existing session cookie remains valid and still resolves to that user. So after a reset the operator's browser can still be logged in, and visiting `/login` redirects straight to `/dashboard`.

Remedy: clear cookies for the tunnel domain, or use a fresh private window for each take. This only affects the operator's own browser. The testing service starts each run in a new browser session and carries no state between runs.

Do not "fix" this by randomizing the Flask secret key. The fixed key is deliberate. Randomizing it would log the operator out every time the Flask reloader picks up a code change during recording, which is considerably worse than clearing a cookie.

## Known timing

`mailer.send_email` performs a synchronous SMTP send with a 10 second timeout. Once the generated feature calls it from a request, that request takes a few seconds to complete while the mail server is contacted. This is expected, not a fault in the application.