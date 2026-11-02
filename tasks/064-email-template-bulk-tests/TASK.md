# Task 064: Email template tests in bulk

- **Status:** `in-progress`: merged into `testing` 2026-11-02 (backend PR #130, admin PR #127), not on `main` yet.
- **Opened:** 2026-11-02
- **Owner:** Eissa
- **Sub-app(s):** backend + admin
- **Branch(es):** `feat/email-templates-bulk-test` in `tourise-backend` and `tourise-admin` (from `testing`)

## Goal

The team tests many email templates, often again and again, and Send Test took one template, one language and one
address a click. Make a test of many templates, in both languages, for several team members, one click.

## How it works

- **Email Templates list:** a tick box on each row (and on the page), kept across pages, and a bar over the table
  with **Send test (N)** and Clear selection, as on Invitations.
- **The Send test window** (the list's button and the editor's): **English, Arabic or both**, **several team
  members** picked from the admins (searchable, the admin themselves first), and the number of test emails it will
  send. It remembers the last languages and people (this browser), so testing again is one click. The selection
  stays after sending.
- **Server:** `POST /admin/email-templates/send-tests` (`ids`, `versions`, `emails`, behind the Email templates box)
  checks every address is an admin's (one outsider and nothing is sent), then queues **one email per template,
  language and person** (`SendTemplateTestEmail`) and answers with how many. `GET /admin/email-templates/
  test-recipients` lists the switched-on admins for the window. The old one-at-a-time `send-test/{id}` is gone.
- **The test email is as before:** the sample guest (no real person's details, links not minted), `[TEST]` in the
  subject, the template's CC and BCC not copied, its attachments for that language, the default SMTP.
- **Limits:** 50 templates and 10 people a click.
- **Newsletter templates** keep their own Send Test window, unchanged.

## Log

- 2026-11-02: asked and planned with the owner; built. Backend: Pint, PHPStan, the full suite (1,711 tests; only
  the 10 known `SocialChannelsTest` failures, test-only). `TestEmailStaysInTheTeamTest` now 9 tests: the team-only
  checks through the new request, many at once (8 emails), one outsider stops all, the limits, the recipients.
  Admin: type-check and ESLint green. EN + AR (9 texts). Committed and pushed: backend `232bacd`, admin `a374841`.
- 2026-11-02: merged into `testing` (backend PR #130, `150d375`; admin PR #127, `eaf1b73`). On the testing server:
  backend pull, `route:cache`, `queue:restart` (new routes, no migration); admin build.

## Open

- The queue must be running on the server (it is for the other sends); a failed test email lands in `failed_jobs`
  rather than in the window.

## Definition of Done

- [x] Merged into `testing`
- [ ] Merged into `main`
- [x] EN + AR translations in the same commit
- [x] Quality gate green (backend Pint, PHPStan, tests; admin type-check and ESLint)
- [ ] Browser check by the owner
- [ ] This TASK.md set to `done`; the index row updated
