# Task 065: Close registration per category

- **Status:** `in-progress`: merged into `testing` 2026-11-03; for `main`, the same commits copied onto
  `feat/close-registration-main` (backend `901e436`, admin `76f2dfa`, frontend `a6614a7`), PRs pending.
- **Opened:** 2026-11-03
- **Owner:** Eissa
- **Sub-app(s):** backend + admin + frontend
- **Branch(es):** `feat/close-registration` in `tourise-backend`, `tourise-admin` and `tourise-frontend` (from `testing`);
  `feat/close-registration-main` in the same three (from `main`, the commits copied with `cherry-pick -x`)

## Goal

The London Reception registration had to close the next morning, with the client's own words on the page:

> Thank you for your interest in attending the TOURISE London Reception. The registration portal is now closed but,
> if you would like to attend, please email contact@tourise.com
>
> We looking forward to connecting with you in London.

The owner asked for it on **any** category, as a switch, with the text set by the team. Ported from gfeai-v2
(backend `c250126`, `bebec73`, `cb98171`; admin `ffd4f5f`, `d8c0bfc`, `0eb4349`; frontend `f499a27`, `8a23729`),
plus the message per category.

## How it works

- **Admin, category form, General tab:** a **Registration** switch, **Open / Closed**, under Status, and two boxes,
  **Closed message (English)** and **(Arabic)**, shown only while the switch is on Closed (owner, 2026-11-03);
  switching back to Open keeps what was typed. Every category starts Open.
- **Admin, categories list:** a **Registration** column (Open / Closed) and a filter for it.
- **Closed:** the category's public link and its invitation links (and their "not interested" links) show a
  **Registration Closed** page with the message in the page's language. The text shows as typed: line breaks and
  empty lines kept, emails and web links clickable. An empty box shows the default text ("Registration is now
  closed. Please contact the event organizer for assistance."). With the team's own message the page has no
  "Registration Closed" title over it (the team, 2026-11-03); the default text keeps it. Plain text only: no bold or colours (that would
  need an editor package in the admin and a cleaner on the website).
- **The server refuses any registration** for a closed category (`POST /guests`, declines included), even from a
  page opened before it closed: "Registration is closed." in a toast. Admins still add guests from the admin.
- **What it does not change:** the category stays active, its guests and invitations are untouched, and every other
  check reads as before (an unknown or used invitation still says so; a switched-off category still reads "not
  active"). A private category's public link stays "not found", closed or not.
- **Backend:** migration `2026_11_03_000001_add_registration_open_to_categories_table` adds `registration_open`
  (default true), `registration_closed_message_en` and `_ar` (text, empty). `verify-category` and
  `verify-invitation` answer 410 `reason: registration_closed` with `closed_message_en`, `closed_message_ar` and
  `visibility`. Messages up to 5,000 characters.

## Option set aside

- **A designed page per event, picked from a dropdown** (owner's idea, 2026-11-03): any formatting, but every new
  page or wording change needs a developer and a website deploy. The text box was chosen "for now".

## Log

- 2026-11-03: asked, planned and built. Backend: Pint, PHPStan, the full suite (1,717 passed; only the 10 known
  `SocialChannelsTest` failures, test-only); `RegistrationClosedTest` 16 tests. Admin and frontend: type-check,
  ESLint and Prettier green. EN + AR in the same change (admin 6 texts, frontend 2, backend 1).
- 2026-11-03: the owner's browser check: message boxes only while Closed; the team asked for no title over their
  message. Committed and pushed: backend `af69a68`, admin `ed19e0f`, frontend `cae2f89`.
- 2026-11-03: merged into `testing` by the owner. For production, only this task goes to `main` (owner's choice
  over testing into main, which would also carry 063, 064, Imtinan's dignitary success page `a4b4025` and the
  sub-events merge and its revert): `feat/close-registration-main` from `main`, the three commits copied (backend
  `901e436`, admin `76f2dfa`, frontend `a6614a7`), each applied cleanly; backend Pint, PHPStan and the full suite,
  admin and frontend type-check and ESLint, rerun on the copies.

## Open

- **Overlap with Imtinan's sub-events branch** ([060](../060-sub-events/TASK.md)): it has its own London closed
  page (`london_closed` variant, `utils/closed-form.ts`) in the same three join pages. Merging it later needs a
  hand merge there.
- **Deploy order matters:** run the migration right after the backend pull, in one line
  (`git pull && php artisan migrate --force`). Until it runs, the column is missing, the code reads it as empty and
  every category shows as Closed. A stricter check (only a category set to Closed is closed) was offered, not taken
  before the push. No new routes, so no `route:cache` for this task alone. Then the admin and frontend builds. Then, on production: open
  the London Reception category, switch Registration to Closed, write the two messages, save.

## Definition of Done

- [ ] Merged into `testing`
- [ ] Merged into `main`
- [x] EN + AR translations in the same commit
- [x] Quality gate green (backend Pint, PHPStan, tests; admin and frontend type-check, ESLint)
- [ ] Browser check by the owner
- [ ] This TASK.md set to `done`; the index row updated
