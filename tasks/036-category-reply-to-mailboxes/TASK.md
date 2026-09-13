# Task 036 — Per-category Reply-To mailboxes

- **Status:** `done (code)` — seeded on production 2026-09-13; three routing questions open with the client
- **Opened:** 2026-09-13
- **Owner:** —
- **Sub-app(s):** backend + admin
- **Branch(es):** `dev`

## Goal

Route a guest's **reply** to the team that owns their audience. Every category shipped with
`smtp_config_id` null, so every send fell through to the single default account and therefore to one
Reply-To — a sponsor's reply and a dignitary's reply landed in the same inbox.

Builds on Task 015, which added the per-flow override *mechanism* (`categories.smtp_config_id` /
`otp_smtp_config_id`). This task is the **mailbox plan that sits on top of it**: the accounts
themselves, seeded rather than hand-made.

## Scope

- **In:** `reply_to_address` / `reply_to_name` on `smtp_configs`; `CategorySmtpConfigsSeeder`;
  a bulk edit for SMTP accounts; Reply-To surfaced in the admin listings.
- **Out:** the mailboxes themselves (client-side, IT), provider domain verification,
  `technical-support@` (belongs in the template footer) and `contact@` (the website's own address).

## The client's Phase 1 mailbox plan

Received 2026-09-13, launch 2026-09-16. **From is one address for everything**; only Reply-To varies.

| Reply-To | Reply-To name | Categories | Responsible |
|---|---|---|---|
| `protocol@tourise.com` | TOURISE 2027 Protocol | Dignitary, Dignitary Delegation, Dignitary Protocol, Dignitary Security | NA at this phase |
| `programming@tourise.com` | TOURISE 2027 Programming | Speaker, Moderator | Vida |
| `VIP@tourise.com` | TOURISE 2027 VIP | VIP | Vida |
| `sponsors@tourise.com` | TOURISE 2027 Sponsors | Sponsor | Arwa Alsadi |
| `media@tourise.com` | TOURISE 2027 Media | Media | Rami Alotibi |
| `exhibitor@tourise.com` | TOURISE 2027 Exhibitors | Exhibitors | NA at this phase |
| `workforce@tourise.com` | TOURISE 2027 Workforce | Workforce | TBC |

From: **`noreply@tourise.com`** (no hyphen) as **`TOURISE 2027`**, on every account.

Two addresses from the client's sheet are deliberately **not** seeded:
`technical-support@tourise.com` goes in the template footer, not a Reply-To header, and
`contact@tourise.com` is the website contact page's own address.

## Decisions

- **Reply-To is a map, not a derivation.** The first cut built it as `{category-slug}@tourise.com`.
  Checked against the client's sheet, **only `media@` was real** — it would have invented nine
  mailboxes nobody owns, and mail to a non-existent Reply-To fails silently for the guest who hit
  reply. It is now an explicit `MAILBOXES` const.
- **An account belongs to a mailbox, not to a category.** Several categories share one inbox: the
  four dignitary categories all reply to `protocol@`, Speaker and Moderator both to `programming@`.
- **Accounts are matched on `reply_to_address`, not on the account name.** The address is the
  account's real identity — one audience, one inbox — while the name carries the brand and would
  orphan every row the day the brand changes.
- **From name is a constant, not inherited.** It first took its brand prefix from the default
  account's `from_name`, an operational field someone can set to anything — it read `APP TEST` on
  the dev database, which would have become the brand on live mail.
- **Brand From, category Reply-To** (owner, 2026-09-13). `from_name` is `TOURISE 2027` on every
  account so the inbox line is identical; the team surfaces only on the reply line as
  `TOURISE 2027 Media`. Alternatives considered: the category in both, or a bare team label.
- **The seeder is not in `DatabaseSeeder`.** It needs a default account to copy transport from and
  nothing seeds one — those are real provider credentials, created by hand.
- **Categories are matched on slug *and* English name**, since a hand-created row may carry either
  spelling. A label that already has capitals is left alone so `VIP` does not become `Vip`.
- **Bulk edit is select-then-edit, not push-from-default** (owner, 2026-09-13). A first cut synced
  the default account's transport onto every other row behind a confirm dialog; replaced with the
  badges-style pattern — pick the accounts, fill only the fields to change.
- **Reply-To is deliberately absent from the bulk form.** It is the field that makes each account
  its own; setting it in bulk would collapse them all onto one inbox.

## Log

- 2026-09-13 — `reply_to_address` / `reply_to_name` added to `smtp_configs` (migration
  `2026_09_13_000001`), backend `ce437a7`, admin `69d734b`.
- 2026-09-13 — `CategorySmtpConfigsSeeder` first cut, slug-derived (backend `1bcaa7c`).
- 2026-09-13 — bulk edit: backend `4145e50` (`POST /admin/smtp-configs/bulk-update`, gated
  `admin.can:smtp_configs,update`, 8 tests), admin `dc3f0c9`.
- 2026-09-13 — brand-name fix + Reply-To matching key (backend `cd0a9cf`).
- 2026-09-13 — **rewritten to the client's sheet** (backend `923ac76`, 13 tests).
- 2026-09-13 — admin surfacing: invitation collections show their email template
  (backend `45d50e7`, admin `90f4e91`); categories get a **View more** naming both SMTP accounts
  (backend `17a41c4`, admin `2e2bb03`); the SMTP listing merges From into one column and gains
  Reply-To (admin `53a3874`, backend `c916f80` adds `reply_to_address` to the sort whitelist).
- 2026-09-13 — **seeded on production.** 7 accounts created, **9 categories wired, 0 left alone**:
  4 dignitary → `protocol@`, Speaker + Moderator → `programming@`, VIP, Sponsor, Media each to
  their own. `exhibitor@` and `workforce@` created with **no category matched** — those categories
  do not exist yet.

## Open — needs the client

1. **General Registration has no mailbox.** The client's sheet routes *General delegates* to
   `contact@`, which the owner excluded. It currently falls through to the default account, so its
   replies do **not** reach Saud Alamri. Confirm intended, or add `contact@`.
2. **`Media-other` (slug `media-other`) is unmapped** — probably belongs on `media@`.
3. **`exhibitor@` / `workforce@` have no categories yet.** The accounts exist and are ready;
   **re-run the seeder** once those categories are created, or they stay on the default.

`Request an Invitation`, `RSVP` and `test share` staying on the default all look correct.

## Open — operational

- **⚠️ Provider domain verification.** All seven accounts now send as `noreply@tourise.com` while
  the default sends as `altsa.co`. If the provider is not verified for `tourise.com`, **all seven
  fail at send time** and the first symptom is a guest not receiving an invitation. Verify with
  *Send test email* on any seeded row before launch.
- **⚠️ The seven mailboxes must exist and be monitored.** Setting a Reply-To header costs nothing;
  if `protocol@tourise.com` is not a real inbox, a dignitary's reply disappears with no bounce
  anyone sees.
- **Stale accounts on the dev database** from the slug-derived run: `TOURISE 2027 — Attendee` and
  `— Guest` (still on the old `no-reply@`), plus the older hand-made `MEDIA stmp`. The seeder never
  deletes, so these need clearing by hand. Not present on production.

## How to run it

Migrations **first** — the seeder writes `reply_to_address`, added by `2026_09_13_000001`.

```bash
php artisan migrate --force
php artisan db:seed --class=CategorySmtpConfigsSeeder --force
```

Never run bare `php artisan db:seed` on production — that runs `DatabaseSeeder`. It needs a default
SMTP account to exist, and aborts with an error if there is none. Safe to re-run: accounts are
updated in place, a hand-picked category override is left alone, and nothing is ever deleted.

Read the output's **"No mailbox in the Phase 1 plan covers these categories"** list — it names the
account each unmapped category currently sends through, not what it would use on a fresh database.

## Definition of Done

- [x] Code merged to `dev` in backend + admin
- [x] EN + AR translations in the same commit (verified at exact key parity)
- [x] Quality gate green (pint + phpstan + 676 backend tests; admin type-check / build / check:rbac)
- [x] Docs updated (this TASK.md; index row)
- [x] Mobile contract checked — `bulk-update` is admin-only, under `admin/smtp-configs`; no mobile surface
- [ ] Production mailboxes confirmed to exist and be monitored
- [ ] Provider verified to send as `tourise.com`
- [ ] The three routing questions above answered
