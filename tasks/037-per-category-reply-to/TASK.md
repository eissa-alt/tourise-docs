# Task 037 — Per-category Reply-To

- **Status:** `done (code)` — dev-DB migrate + admin configuration + browser QA pending
- **Opened:** 2026-09-13
- **Owner:** Eissa
- **Sub-app(s):** backend, admin, docs
- **Branch(es):** `dev`

## Goal

Keep sending every guest email from the one authenticated mailbox
(`no-reply@tourise.com`) while a guest's **reply** reaches the team that owns their
category — `media@tourise.com` for Media, `vip@tourise.com` for VIP, and so on.

## Scope

- **In:** a nullable `reply_to_address` / `reply_to_name` pair on `smtp_configs`, applied
  by `DynamicSmtpService` through the global `mail.reply_to` key; the two fields in the
  admin SMTP form's Sender settings card; clone, export, listing detail and search.
- **Out (explicitly not this task):** a `categories.reply_to_email` column. Not needed —
  the per-category selection already exists (see Decisions #1). Also out: changing the
  `From` address per category, which would need SPF/DKIM per address and is the reason
  Reply-To is the right header here.

## Log

- 2026-09-13 — opened. Owner asked where a per-category reply address belongs: category
  edit, or the SMTP config create/edit screen.
- 2026-09-13 — investigated both. Landed on `smtp_configs` (Decisions #1). Backend +
  admin implemented, gates green, held uncommitted for owner review of the diff.
- 2026-09-13 — owner reviewed; one UI fix first: `custom-input`'s `help` branch rendered
  a bare unstyled `<div>`, so the hint came out as full-size body text. Styled with the
  app's form-hint idiom and the copy shortened to one line. **Nothing else in the app
  passes `help`**, so no other field moves. Committed: backend `ce437a7`, admin `69d734b`.
  **Not pushed.**

## Decisions

1. **It lives on `smtp_configs`, not on `categories`** — promoted to ledger **D50 #1**.
2. **OTP and admin system mail inherit whatever account they are pointed at** (owner
   decision, 2026-09-13). No code branch forcing them to no-reply: leaving Reply-To empty
   on the default account achieves the same thing and stays the admin's call. Note the
   consequence — setting a Reply-To on the **default** account gives one to admin login
   codes, admin invites and the two security alerts as well, since those all resolve
   through `applyDefaultIfAvailable()`.
3. **`reply_to_name` is sent as-is, not defaulted to `from_name`.** A Reply-To with no
   display name is normal; silently borrowing the sender's name would be surprising.

## Definition of Done

- [x] Code written in the relevant sub-app(s)
- [x] Code committed to `dev` after owner review — backend `ce437a7`, admin `69d734b`
- [ ] **Pushed** — held at owner's instruction, along with the 5 earlier unpushed commits
- [x] EN + AR translations in the same change (`reply_to_address`, `reply_to_name`,
      `reply_to_help`)
- [x] Quality gate green — backend `pint --test` + **644 tests** (641 → 644, the 3 new
      ones below); admin `type-check` + `build` + `check:rbac`. phpstan unchanged at the
      5 pre-existing larastan false positives, verified against a pristine worktree of
      `HEAD` rather than assumed.
- [x] Docs updated (this TASK.md, index row, ledger D50)
- [x] Mobile contract checked — **not mobile-facing.** No route added, removed or
      renamed; `admin/smtp-configs` is admin-only behind `admin.can:smtp_configs`.
- [ ] Dev DB `migrate`
- [ ] Admin configuration: clone the default account once per reply target, set its
      Reply-To, point each category at it
- [ ] Browser QA: send-test from an account with a Reply-To and confirm the header in a
      real client, EN + AR

## Tests

`tests/Feature/DynamicSmtpOverrideTest.php`, three added:

- `test_reply_to_from_the_config_reaches_the_message` — asserts the real `Reply-To`
  header on a built message over the array transport, not just the config value. This is
  what proves the no-plumbing claim in D50 #2.
- `test_reply_to_does_not_leak_into_the_next_send` — the regression this feature most
  easily introduces; see D50 #3.
- `test_fallback_clears_a_previously_applied_reply_to` — the same leak via the other exit.

## What the client configures

No new category UI. Three SMTP rows sharing one mailbox's credentials:

| Name | From | Reply-To |
|---|---|---|
| TOURISE — default | no-reply@tourise.com | *(empty)* |
| TOURISE — Media | no-reply@tourise.com | media@tourise.com |
| TOURISE — VIP | no-reply@tourise.com | vip@tourise.com |

Then **Categories → edit → "Use a specific SMTP account for register / accept / reject"**,
which already exists and is already wired. `POST /admin/smtp-configs/{id}/clone` makes the
duplication one click, and now carries the Reply-To into the copy.

⚠️ **The mailboxes must exist and be monitored** before this is switched on in production,
or replies bounce. That is a client-side dependency, not a deploy step.
