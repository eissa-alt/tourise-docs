# Task 058: The email magic link, merged onto testing

- **Status:** `in-progress`: merge branches made and pushed 2026-10-25 (see *Branches*); the merge itself is
  Imtinan's, with the open questions below. Nothing merged into `testing` yet.
- **Opened:** 2026-10-25
- **Owner:** Imtinan (the merge and the questions), Eissa (review, the PR into `testing`)
- **Sub-app(s):** backend + admin + frontend
- **Branch(es):** `merge/email-magic-link` in `tourise-backend`, `tourise-admin` and `tourise-frontend`, made from
  `origin/testing`; the work itself is on `feat/email-magic-link` (untouched)

## Goal

Get Imtinan's email magic link (built 27 to 30 Sep, never merged) onto the testing server, so it can be tested
while the CRM work goes on. Since that branch was made, the same email-code flow changed on `testing`: her own
partner API work (a partner's server asks us to send the code) and the security fixes. The merge has to keep all
three.

## What the magic link does (her branch)

- **One email, two ways to prove the address:** an 8-character code to type (the shape it always had) and a
  button to tap. Whichever is used first proves the address; the other stops working.
- **Kept safe:** code and link are stored only as an HMAC (keyed on the app key) and compared in constant time; the
  link is looked up by its hash, so the URL names nobody. 10 minutes to use them, 5 wrong codes and the session is
  locked, one email per address per 60 seconds.
- **A ticket, not the code:** once proven, the form gets a one-time ticket, and the registration or request submits
  that ticket instead of the code. It is checked against the address it belongs to and spent on submit.
- **Another device or tab:** the link opens `/{lang}/verify-email?token=…` on the public site; the tab that asked for
  the code waits (polls `GET /guests/email-verification/status` every couple of seconds) and carries on by itself,
  the form filled in. A service worker (`public/verification-sw.js`) passes the news between tabs.
- **The email:** the code in the preview line and at the top of the plain-text part (`OneTimeCodePreheader`); the
  button from `{{ verify_url }}` in the guest verification template; the admin's email editor offers that
  variable.

## Branches

| App | `feat/email-magic-link` | Into `testing` (test merge, 2026-10-25) |
|---|---|---|
| Backend | 9 commits (`70b1f18` to `4ec06fb`), 2 migrations | **Conflicts** in `AuthController`, `GuestsController`, `InvitationRequestsController` |
| Admin | 1 commit (`b483bac`): the editor offers the verification link variable | Merges cleanly |
| Frontend | 8 commits (`a6dde04` to `832675a`): the code screen waits for the link, the link page, back to the form filled in | Conflicts only in `translations/en/web.json` and `translations/ar/web.json` |

To merge, in each app:

```bash
git fetch origin
git checkout merge/email-magic-link
git merge origin/feat/email-magic-link
```

Then a PR from `merge/email-magic-link` into `testing` in each app (the owner opens them).

### Files on her branch

- **Backend:** `app/Services/EmailVerification.php` (new), `app/Services/Mail/OneTimeCodePreheader.php` (new),
  `EmailVariableResolver`, `SystemEmail`, `SystemEmailTemplatesSeeder`, the plain-text OTP views
  (`resources/views/emails/password_reset_plain/{en,ar}.blade.php`), `routes/api.php`, the three controllers, two
  migrations, tests `EmailVerificationOtpAndMagicLinkTest`, `OneTimeCodePreheaderTest`,
  `InvitationRequestEmailOtpTest`.
- **Frontend:** `pages/[lang]/verify-email.tsx`, `components/join/verify-email-form.tsx`,
  `hooks/use-resume-verification.ts`, `utils/verification-channel.ts`, `utils/verification-return.ts`,
  `utils/focus-form-tab.ts`, `public/verification-sw.js`, `components/shared/forms/custom-input.tsx`, step 1 of the
  nine join forms, translations.
- **Admin:** `components/admin-modules/emails/templates/email-editor-waypoint.tsx`.

### New endpoints (backend)

Both public, outside `sensitive-api` on purpose (a polling tab would use up the site-wide budget the code sends
depend on); Cloudflare carries the volume protection, as for the public submits.

| Method | Path | Does |
|---|---|---|
| GET | `/api/guests/verify-email?token=…` | The tapped link: proves the address, returns the ticket and session |
| GET | `/api/guests/email-verification/status?session_id=…` | What the waiting tab polls: verified or not, and the ticket |

### Migrations

- `2026_09_27_000001_add_magic_link_to_email_verifications`: adds `otp_hash`, `magic_token_hash`, `ticket_hash`,
  `session_id`, `expires_at`, `verified_at`, `used_at` (all nullable), indexes on `magic_token_hash` and
  `session_id`. Reversible.
- `2026_09_30_000001_put_the_verify_link_in_the_guest_otp_email`: **rewrites the guest verification email template**
  (`content_en/ar` and `editor_json_en/ar`) by blanking it and re-running the seeder, wherever `{{ verify_url }}` is
  missing. Not reversed. See question 2.

## Why the backend conflicts

The same flow moved on `testing` after her branch:

| Commit on `testing` | What it changed |
|---|---|
| `e04ea87` (1 Oct, Imtinan) | **Partner API, the email code server to server:** `POST /request-an-invitation/{slug}/send-code` (partner key and IP). We email the applicant a code; the partner's server files the request with the typed code as `otp_token`. Code sending moved to `App\Services\Mail\EmailOtpSender`, shared with our own form. |
| `d5453ef` | check-unique asks about email only; **an email code fits only its address** |
| `b628d48` | the public email lookups need a reCAPTCHA token |
| `a623bd0`, `ff18643` | forgot-password cannot be timed; admin setup link from `ADMIN_PANEL_URL` |

Her branch still skips the code for partners (`$fromPartner`), and checks a ticket where `testing` checks the typed
code.

## Proposed resolution (backend)

1. **`EmailVerification` is the one place codes are made and checked.** `EmailOtpSender` keeps the mail sending
   (template, the category's OTP mail account, headers) and mints through `EmailVerification::start()`.
2. **Our own forms:** her flow, unchanged: code or link, then the ticket on submit (`ticketIsValidFor`), spent with
   `forget()`.
3. **A partner's request:** no browser and no ticket, so the typed code is checked with
   `EmailVerification::confirmOtp($email, $code)` in `InvitationRequestsController::store`, then forgotten. The
   partner path keeps its refusals (address already on file, key and IP).
4. **The security fixes stay:** the code or ticket fits only its own address; reCAPTCHA on the public email
   lookups; nothing in the answers tells who is registered.

## Open questions (for Imtinan)

1. **Partner emails and the button.** After the merge the email has the link button. A partner's applicant who taps
   it proves the address on *our* site and spends the code, so the partner's submit with that code fails as
   "already used".
   - **A (recommended):** partner emails carry the **code only**, no button; our own forms send code and link.
   - **B:** partners get the button too, and the code is accepted even after the link was used (the code is no
     longer single-use).
2. **The template migration.** `2026_09_30_000001` replaces the guest verification email's wording wherever it has no
   link yet. On a server where the team edited that email, their wording goes. Keep it, or add the button by hand on
   each server and drop the migration? (Rule: template content is never edited silently.)
3. **The mobile login shares the table.** `MobileAuthController` (`/api/mobile/identity/check-email`,
   `verify-otp`) keeps its own 6-digit code in `email_verifications`, one row per email, written with
   `updateOrInsert` (plain `token`, `attempts`). Web and mobile already overwrite each other's row on `testing`
   today; her rows add hash columns that the mobile write never clears. Check that a web code cannot be confirmed
   from a row the mobile login has rewritten, and that the mobile login still works after a web verification. No
   mobile route changes, so the mobile contract stands.

## Checks before the PR into testing

- **Backend:** `composer qa` (Pint, PHPStan, every test), including her three test files, `GuestEmailOtpTest` and
  `PartnerInvitationRequestApiTest`.
- **Frontend and admin:** `yarn type-check` and `yarn build`.
- **By hand, on the testing server:**
  - registration with the code; with the link on the same device; with the link on another device (the first tab
    carries on by itself);
  - an expired code (after 10 minutes); 5 wrong codes (locked); asking again within 60 seconds (wait shown);
  - request an invitation, with code and with link;
  - a partner: `send-code`, then filing with the typed code (and, under answer A, no button in that email);
  - the mobile app's OTP login still works.

## On the testing server, after the merge

- `php artisan migrate` (the two migrations; the second only after question 2 is answered), then `config:cache`,
  `route:cache`, `queue:restart`.
- `PUBLIC_FRONTEND_URL` set in the backend's `.env` to the testing site's address: the link is built from it
  (`config('app.frontend_url')`, default `http://localhost:3000`).
- Frontend built and restarted (the service worker ships with it).

## Log

- 2026-10-25: opened. The owner wants the magic link on `testing`. Test merge of `feat/email-magic-link` into
  `origin/testing`: admin clean, frontend translations only, backend three controllers. A first merge attempt was
  stopped before resolving anything (nothing committed). The owner's call: Imtinan does the merge. Branches
  `merge/email-magic-link` made from `origin/testing` and pushed in all three apps; her branch untouched. The plan
  and questions 1 and 2 were sent to her on WhatsApp.

## Definition of Done

- [ ] Merged into `merge/email-magic-link` in the three apps, conflicts resolved as above (or as Imtinan decides)
- [ ] Questions 1 to 3 answered
- [ ] EN + AR translations in the same commit
- [ ] Quality gate green (backend `composer qa`; admin and frontend `yarn type-check` + `yarn build`)
- [ ] PRs into `testing` merged; migrations run on the testing server; `PUBLIC_FRONTEND_URL` set
- [ ] Tested by hand on the testing server (the list above)
- [ ] Docs updated (this TASK.md, the index row)
