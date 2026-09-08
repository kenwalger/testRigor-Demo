# Build the Golden Tire Customer Portal Baseline

Create a deliberately small Flask web application called the **Golden Tire Customer Portal**.

This application will be used later in a demonstration of AI-assisted code generation and end-to-end behavioral testing. It is a throwaway demonstration application, not a production system.

Optimize for:

1. Simplicity
2. Reliability
3. Readability
4. Minimal dependencies
5. Fast local startup
6. Easy modification by a coding agent

Do not over-engineer the application.

Most importantly, **do not implement functionality that has not been explicitly requested below.** Some missing functionality is intentional and will be added during a later demonstration.

---

## Company

The fictional company is:

**Golden Tire Company**

Tagline:

**Keeping You Rolling Since 1957**

The application is the company's customer-facing account portal:

**Golden Tire Customer Portal**

Golden Tire Company should feel like a long-established American automotive tire company whose traditional brand has been adapted into a simple modern web application.

The branding should be restrained and credible rather than cartoonish.

Use a visual identity based around:

* Warm golden yellow accents
* Charcoal or dark gray
* Warm off-white backgrounds
* Strong, straightforward typography
* A simple tire-inspired circular brand mark created with CSS if appropriate

Do not use external images, image-generation services, icon libraries, or other assets that introduce unnecessary dependencies.

The application should look polished enough for a screen-recorded technical demonstration, but frontend design is not the purpose of this project.

---

## Technology

Use:

* Python 3
* Flask
* SQLite
* Jinja templates
* Werkzeug password hashing
* Flask sessions
* Plain HTML
* Plain CSS
* Python's standard library `smtplib` and `email` modules for outbound mail

Do not use:

* React
* Vue
* Angular
* Tailwind
* Bootstrap
* JavaScript frameworks
* An ORM unless absolutely necessary
* Flask-Mail or any other mail extension
* Docker
* Redis
* External databases
* External authentication providers
* External APIs
* Cloud services
* Frontend build tools

Prefer Python's built-in `sqlite3` module rather than adding an ORM.

The only permitted third-party dependencies are Flask, Werkzeug, and `python-dotenv`.

Keep the entire application small enough that another coding agent can understand the repository quickly.

---

## Application structure

Use a simple structure similar to:

```text
golden-tire-portal/
├── app.py
├── mailer.py
├── reset_db.py
├── verify_email.py
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   └── account.html
├── static/
│   └── styles.css
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

You may make small changes to this structure if Flask requires them, but do not introduce unnecessary architectural layers.

---

## Database

Create a local SQLite database automatically if one does not already exist.

Create a `users` table containing only the fields required for this demonstration.

Seed exactly one user:

**Name:** Demo User

**Email:** `goldentire.demo@testrigor-mail.com`

**Password:** `oldpassword`

The password must be stored using Werkzeug password hashing.

Do not store plaintext passwords.

The seed email address is deliberately a real, deliverable address on an external testing domain rather than a reserved example domain. Do not change it to `example.com`, `.example`, `.test`, `.invalid`, `localhost`, or any other non-routable address. Mail must actually be able to reach this address.

Database initialization should be simple and deterministic so the application can easily be returned to its original state between demonstrations.

---

## Database reset script

Create `reset_db.py`.

Running `python reset_db.py` must:

1. Delete the existing SQLite database file if present
2. Recreate the schema
3. Reseed the single demo user described above
4. Print a short confirmation of what it did

This script exists so the application can be returned to a known state between recorded takes with a single command. It must be safe to run repeatedly and must never produce duplicate users.

---

## Email transport

Create `mailer.py` containing a single function:

```python
def send_email(to: str, subject: str, body: str) -> None:
```

Requirements:

* Send a plain-text email using `smtplib` over STARTTLS
* Read all configuration from environment variables: SMTP host, port, username, password, and the From address
* Load environment variables from a `.env` file using `python-dotenv`
* Raise a clear, readable exception if any required configuration is missing
* Log or print a short confirmation line on successful send

Create a `.env.example` documenting every required variable with placeholder values. Add `.env` to `.gitignore`. Never commit real credentials, and never hardcode credentials in source.

Create `verify_email.py`. Running `python verify_email.py` must send one test message to `goldentire.demo@testrigor-mail.com` using `send_email` and report success or failure. This exists solely so mail delivery can be confirmed before the demonstration begins.

**Critically: nothing in the Flask application may call `send_email`.** No route, no view, no helper. The mail transport must be fully working and completely unused. Wiring it into application behavior is explicitly out of scope for this task.

---

## Authentication

Implement simple session-based authentication.

The application should support:

* Login
* Authenticated session
* Protected pages
* Logout

Do not implement:

* Registration
* Forgot password
* Password reset
* Password reset tokens
* Change password
* Email verification
* Multi-factor authentication
* OAuth
* Social login
* Account deletion

Those omissions are intentional.

---

## Login page

Route:

`/login`

The page should prominently display:

**Golden Tire Company**

**Keeping You Rolling Since 1957**

**Customer Portal**

Include fields labeled:

**Email**

**Password**

Include a button labeled:

**Sign In**

If the credentials are invalid, display exactly:

**Invalid email or password**

Successful authentication should redirect to `/dashboard`.

If an authenticated user visits `/login`, redirect them to `/dashboard`.

---

## Dashboard

Route:

`/dashboard`

Authentication is required.

Unauthenticated visitors should be redirected to `/login`.

Display:

**Welcome, Demo User**

Display this supporting text:

**Manage your Golden Tire account and account settings.**

Include navigation links for:

* Dashboard
* Account Settings
* Logout

Keep the dashboard intentionally sparse.

Do not create fake tire inventory, vehicles, service records, appointments, orders, shopping functionality, or other application features merely to make the page look busier.

---

## Account Settings

Route:

`/account`

Authentication is required.

Display a heading:

**Account Settings**

Display the authenticated user's:

**Name**

**Email**

For the seeded account, the visible values should therefore be:

**Demo User**

**goldentire.demo@testrigor-mail.com**

Do not include any controls for changing the password.

Do not include a disabled or placeholder password-changing interface.

The absence of password-changing functionality is intentional.

---

## Logout

Route:

`/logout`

Logging out must destroy the authenticated session.

After logout, redirect the user to `/login`.

Attempting to visit `/dashboard` or `/account` after logout must redirect to `/login`.

---

## HTML and testability

Use semantic, accessible HTML.

This application will later be tested by an end-to-end behavioral testing system, so prioritize visible user-facing labels and predictable interactions.

Every form field must have a proper visible `<label>` associated with the input.

Every interactive control should have meaningful visible text.

Avoid interactions that depend on:

* CSS selectors
* Hover states
* JavaScript
* Dynamically generated identifiers
* Hidden controls
* Unlabeled icons

The application should be easily usable by both a human and a testing system interacting with it through visible behavior.

Do not add testing-specific IDs or attributes merely to make automation easier.

---

## Styling

Create a small `static/styles.css`.

The application should have a restrained Golden Tire Company visual identity.

Aim for the feeling of an established American industrial brand presented through a modern customer portal.

Suggested visual direction:

* Warm off-white page background
* Charcoal navigation/header
* Golden yellow accent
* White or warm-white cards
* Clear form controls
* Moderate border radius
* Generous but not excessive spacing
* Readable typography
* Simple tire-inspired circular company mark if it can be done cleanly in CSS

The application will be shown in a video, so prioritize:

* Legibility
* Clear hierarchy
* Large enough text
* Obvious form labels
* Clearly visible success/error messages

Do not spend significant effort on visual effects.

No animations are necessary.

---

## Configuration and security scope

This is a local demonstration application, but use sensible basic practices where they cost little:

* Hash passwords with Werkzeug
* Use parameterized SQLite queries
* Store authentication state in the Flask session
* Protect authenticated routes
* Read SMTP configuration from environment variables only

The Flask secret key must be read from an environment variable with a **fixed, hardcoded development fallback string**. Do not generate the fallback randomly at startup, and do not derive it from `os.urandom`, `uuid`, or the current time. A regenerated key would invalidate active sessions every time the development server reloads, which would break the demonstration. Add a short comment in the source explaining this constraint so a later agent does not "improve" it.

Do not turn this into a production security exercise.

The goal is a small, understandable application suitable for demonstrating a later feature addition.

---

## Startup

The application should run locally at `http://localhost:5000` with the Flask development server and the reloader enabled.

---

## README

Create a concise `README.md` containing:

### Requirements

State the required Python version.

### Setup

Provide commands for:

1. Creating a virtual environment
2. Activating it
3. Installing dependencies
4. Copying `.env.example` to `.env` and filling in SMTP values
5. Starting the application

The application should run locally at:

`http://localhost:5000`

### Demo credentials

Document:

**Email:** `goldentire.demo@testrigor-mail.com`

**Password:** `oldpassword`

Clearly state that these are intentionally synthetic credentials for a local demonstration application.

### Verifying email delivery

Document `python verify_email.py` and state plainly that the mail transport is intentionally not connected to any application route.

### Resetting the application

Document `python reset_db.py` as the single command that returns the application to its original seeded state.

---

## Verification

After implementation, start the application and verify the following behavior yourself:

1. `/login` loads successfully.
2. `goldentire.demo@testrigor-mail.com` with `oldpassword` authenticates successfully.
3. Incorrect credentials display `Invalid email or password`.
4. Successful login redirects to `/dashboard`.
5. The dashboard displays `Welcome, Demo User`.
6. `/dashboard` cannot be accessed without authentication.
7. `/account` cannot be accessed without authentication.
8. Account Settings displays `Demo User`.
9. Account Settings displays `goldentire.demo@testrigor-mail.com`.
10. Account Settings contains no password-changing functionality.
11. Logout destroys the authenticated session.
12. Protected pages cannot be accessed after logout.
13. Restarting the application does not create duplicate users or otherwise corrupt the seed data.
14. `python reset_db.py` runs cleanly, can be run twice in a row, and leaves exactly one seeded user.
15. Editing a source file triggers the reloader without logging out an authenticated session.
16. `mailer.send_email` is not referenced anywhere in `app.py` or in any template.

Do not run `verify_email.py` yourself. It requires SMTP credentials that are not available to you. Confirm only that the script exists and is syntactically valid.

Fix any problems you find during the other verification steps.

---

## Important stopping point

Once all of the requirements above work, **stop**.

Do not anticipate future requirements.

Specifically, do not add:

* Change Password
* Forgot Password
* Password Reset
* Password Reset Tokens
* Any route, link, form, or view that sends email
* Any call to `send_email` from application code
* Registration
* Additional Users
* Automated Browser Tests
* End-to-End Tests
* Unit Tests
* testRigor Configuration
* Claude Code Configuration
* AI Agent Instructions

Do not suggest or implement those features as "next steps."

The intentionally limited baseline application is the finished deliverable for this task.

At completion, provide only:

1. A short summary of what was created.
2. The command required to start the application.
3. Confirmation that the verification steps passed.
4. Any assumptions or limitations I should know about.

Do not begin implementing anything beyond this baseline.