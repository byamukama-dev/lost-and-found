# CampusFind — MUST Lost & Found

A server-backed lost-and-found application for Mbarara University of Science and Technology.
The frontend uses HTML, CSS, Tailwind CSS and vanilla JavaScript. Flask serves both the
frontend and the JSON API. SQLite stores accounts, reports, claims, image bytes and audit history.

The board starts empty. There are no sample listings, default accounts, demo passwords,
or browser-only database adapters.

## 1. Open and install in VS Code (Windows)

Extract this ZIP into a **new folder**, rather than overwriting an older prototype.
Open the folder containing `app.py` and `index.html` in VS Code.

Open Terminal → New Terminal and run:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

These commands do not require PowerShell script activation or an execution-policy change.
Python 3.10 or later is required; the application was tested with Python 3.12.

## 2. Configure actual email delivery

Open `.env` in VS Code. Fill in the SMTP values supplied by your email delivery provider:

```dotenv
SMTP_HOST=your-provider-smtp-host
SMTP_PORT=587
SMTP_SECURITY=starttls
SMTP_USERNAME=your-provider-username
SMTP_PASSWORD=your-provider-password-or-app-password
MAIL_SENDER=CampusFind <your-verified-sender-address>
```

For providers using implicit TLS, set `SMTP_SECURITY=ssl` and the provider's SSL port.
Only encrypted SMTP connections are supported. Your provider may require sender/domain
verification or an application-specific password. Use the provider's setup instructions.
Do not paste SMTP passwords into chat, commit `.env`, or publish it.

Registration sends a real six-digit code over SMTP. An account is created only after that
code is verified. Codes expire after 10 minutes, allow five attempts and can be resent after
60 seconds. Password recovery also uses emailed codes. Codes are hashed on the server and
are never displayed in API responses or application logs.

**Email credentials have not been supplied in this ZIP.** Until you configure them,
registration reports that email delivery is unavailable; it does not bypass verification.
After configuring the provider, register your own address to confirm delivery, including
the spam folder, before inviting students. Automated tests intercept the email transport;
they do not prove delivery to a real mailbox.

## 3. Start the application

```powershell
.venv\Scripts\python.exe app.py
```

Open **http://127.0.0.1:5000**. Keep the terminal running. Stop with `Ctrl+C`.
The database is created automatically in `data/campusfind.db`.

Use the Python server for the whole application. VS Code Live Server serves static files
and cannot provide the database or send verification emails. Do not double-click HTML files.
After dependencies are installed, `start.bat` is an optional shortcut if `python` points to
the interpreter containing those dependencies. The explicit `.venv` command above is preferred.

## Registration rules

| Field | Accepted format |
| --- | --- |
| MUST student email | `2025bse063@std.must.ac.ug` |
| Personal email | An address ending in `@gmail.com` |
| Private-sponsored registration | `2025/BSE/063/PS` |
| Government-sponsored registration | `2025/BSE/063` |
| Ugandan phone | `0772123456`, `256772123456` or `+256772123456` |
| Password | 12–128 characters |

Registration numbers are normalised to uppercase; phone numbers to `+256` format.
A MUST email must match the registration year, programme and three-digit student number.
Programme codes contain 2–8 letters. `/PS` is optional only as the sponsorship suffix.
The same registration identity cannot register again by changing the sponsorship suffix.
Gmail users still enter a registration number. Email verification proves mailbox access;
it does not independently verify university enrolment or sponsorship against MUST records.

## 4. Create the administrator

There are no default admin credentials. From the same project terminal:

```powershell
.venv\Scripts\python.exe -m flask --app app create-admin
```

Enter the admin name, allowed email address, Ugandan phone and a private password when prompted.
This trusted server-operator command explicitly provisions the admin without an emailed
code. It never grants admin access through the public registration form.

Alternatively, promote an existing verified account:

```powershell
.venv\Scripts\python.exe -m flask --app app promote-admin youraddress@gmail.com
```

Log in again after promotion. The admin area is linked from the dashboard and is also
available at `/admin.html`.

## Item and handover workflow

1. A verified student posts a lost or found report, optionally with a JPG, PNG or WebP photo.
2. Another student submits a private ownership claim on a found item.
3. The reporter or an administrator reviews the evidence and approves or rejects the claim.
4. Approval reserves the handover and closes competing claims. It does **not** start the
   review clock. The approved claimant opens the item and selects **I have received my item**
   after physically collecting it.
5. Receipt starts a seven-day review period. The listing and image remain visible by
   selecting the recovered/all-status browse filter. Deletion is blocked during that period.
6. A signed-in student can select **Report incorrect handover** during the review period.
   A dispute preserves the record until an administrator reviews it, even beyond seven days.
7. Administrators review the dispute, record their decision and may reopen the item,
   invalidating the previous approval. Earlier report details and photos remain in history.
8. After seven days without an open dispute, the record leaves the public board. It is
   archived, not automatically erased from the database. Reporters, approved recipients and
   administrators retain access. Reporters or admins can then delete the listing.

For a lost report, its reporter can confirm that the item was returned using **Mark as
recovered**. This also starts the seven-day period. A finder cannot confirm receipt on
behalf of an approved claimant.

Authors can edit/delete their own unprotected reports. Admins can edit/delete other
unprotected reports. During a review period or dispute, admin corrections are allowed and
audited, while deletion is blocked for everyone so evidence cannot disappear.
Audit snapshots and earlier images remain available to admins after a listing is deleted;
configure your operational privacy/retention policy before collecting real student data.

## Features

- Responsive home, browse/search, report/edit, item, dashboard and admin pages.
- Required email-code verification and password recovery.
- Session authentication, password hashing, CSRF checks and persistent request limits.
- Search, category/kind/status filters, ordering and pagination.
- Photo decoding, metadata removal and resizing to at most 1800×1800 pixels.
- Up to 5 MB per upload, with at most 25 megapixels decoded.
- Image bytes stored in SQLite, not browser storage or a public upload directory.
- Private claim evidence and restricted found-item contact details.
- Notifications for claims, category matches, receipt and disputes.
- Profile/password changes and invalidation of older sessions after password reset.
- Admin moderation, roles, report editing/deletion, dispute review and history.
- Atomic item/claim changes, so simultaneous approval requests cannot approve two owners.
- Responsive mobile menu, keyboard dialogs and reduced-motion support.

## Public hosting

Local setup is not a public deployment. To make the application available to students,
use a server with persistent local disk, a domain, an SMTP provider and HTTPS.

In the deployed `.env`, set:

```dotenv
APP_ENV=production
PUBLIC_ORIGIN=https://your-real-domain
SECRET_KEY=your-private-random-key-of-at-least-32-characters
CAMPUSFIND_DATA_DIR=/absolute/persistent/path/campusfind-data
```

Run the included production WSGI server:

```powershell
.venv\Scripts\python.exe run_server.py
```

On Linux, use `.venv/bin/python run_server.py` instead.
Terminate HTTPS at your hosting provider or a trusted reverse proxy, and forward requests
to `127.0.0.1:5000`. The same origin must serve HTML and API requests. Secure cookies are
enabled in production; do not use production mode on a plain HTTP URL.

Set `TRUST_PROXY=1` only if exactly one trusted proxy overwrites forwarded headers and
users cannot reach Waitress directly. Leave it disabled otherwise. Use the exact
`PUBLIC_ORIGIN` in the browser, including scheme and non-default port.

SQLite is suitable for one application server with modest campus traffic. Use a local
persistent disk, not an ephemeral container filesystem or shared network filesystem.
For multiple application servers or substantial concurrent writes, migrate the database
and image storage before scaling. SMTP delivery is synchronous and has a 20-second timeout.
The app has not been deployed, load-tested or subjected to an independent security review.

## Backups and maintenance

The SQLite database includes the photos. Create a consistent backup without copying an
actively written database file by hand:

```powershell
.venv\Scripts\python.exe backup.py backups\campusfind-backup.db
```

Also protect `.env` and `data/secret_key` if using the generated session/signing key.
Keep backups on a separate protected disk. To restore, stop the application and replace
the database with your backup; then restart. Do not leave stale `-wal`/`-shm` sidecars from
the previous database when restoring while the application is stopped.

Public archive expiry is checked on API requests. You can also run maintenance daily:

```powershell
.venv\Scripts\python.exe -m flask --app app maintenance
```

This archives expired recoveries and removes old challenges/rate counters. It does not
silently delete reports, disputes, audit records or photos.

## Editing the frontend

HTML pages are in the project root. Page JavaScript is in `static/js/`; shared helpers
are in `common.js`. Custom CSS is in `static/css/custom.css`. Compiled Tailwind is included.
After adding new Tailwind utility classes, rebuild with Node.js:

```powershell
npm.cmd install
npm.cmd run css:build
```

Ordinary custom CSS edits need no build. The backend and database do not require Node.js.

## Tests

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Tests use temporary databases and a test-only email interceptor. They do not populate the
real application database or send email to students. See `CHECKS.md` for tested behaviour
and verification limits.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `ModuleNotFoundError` | Use `.venv\Scripts\python.exe -m pip install -r requirements.txt`. |
| Email delivery unavailable | Fill SMTP settings and restart; verify provider credentials, sender and network access. |
| Code missing | Check spam; wait 60 seconds before resending. Codes expire after 10 minutes. |
| Request origin not permitted | Open the exact URL in `PUBLIC_ORIGIN`, or update that setting and restart. |
| Session expired | Refresh the page and submit again. |
| Port 5000 busy | Set `PORT=5001` and `PUBLIC_ORIGIN=http://127.0.0.1:5001` in `.env`. |
| Older prototype database rejected | Use a new folder and new data directory. No prototype data is imported automatically. |
| Cannot delete a recovered item | Wait for the seven-day period to end and resolve any open disputes. |
