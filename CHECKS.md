# Verification — 3 November 2026

The server-backed version passes **11 automated application tests**:

- The database begins with no accounts, listings or photos; application pages are served.
- MUST email/registration matching, Gmail acceptance and Ugandan phone normalisation.
- Verification is required before account creation, with hashed codes and single-use enforcement.
- Code expiry, resend cooldown and five-attempt lockout.
- Missing SMTP configuration fails without creating a usable account or challenge.
- CSRF protection and rejection of cross-origin write requests.
- Actual image decoding/re-encoding, SQLite image bytes, and author-only edit/delete permissions.
- Approved-claimant receipt confirmation starts retention; deletion is blocked during review.
- Admin edits generate audit history; expired recoveries leave the public board.
- Disputes preserve records after seven days; administrators can review and reopen them.
- Password recovery invalidates older login sessions.
- The SMTP integration invokes encrypted transport and authenticated delivery.

(The mail and validation tests contain multiple related assertions in one test method.)

A separate DOM integration check against the running Flask server passed:

- Empty homepage rendering.
- Registration form → email-code dispatch through a test transport.
- Verification form → authenticated account → student dashboard.
- Browse, item, create/edit report, found-item shortcut, recovery, help and not-found page scripts.
- Admin edit/delete controls.
- Escape cancels confirmation dialogs without leaving a pending result.
- No page-script errors were observed in the checked flows.

These checks use temporary databases. The distributed application contains no test accounts
or listings and does not expose a verification-code bypass.

Limits: real SMTP credentials were not supplied, so delivery to actual inboxes has not been
verified. A graphical browser could not be installed in the environment, so mobile/desktop
visual rendering has not been verified. Responsive layouts, mobile navigation and the
compiled Tailwind stylesheet are included. Hosting, HTTPS, backups, provider setup, load
testing and an independent security review remain deployment responsibilities.

Run the included application tests:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```
