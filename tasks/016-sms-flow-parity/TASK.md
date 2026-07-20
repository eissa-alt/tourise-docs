# Task 016 — SMS flow parity (accept/reject + automations + invitations)

- **Status:** `done (code)` — QA pending
- **Opened:** 2026-07-20
- **Owner:** —
- **Sub-app(s):** backend + admin
- **Branch(es):** `dev`

## Goal

Bring SMS coverage up to parity with email across the guest flows. Before this task, email
fired on register-complete, accept, reject, automations and invitations, but SMS only fired on
register-complete + phone-OTP. This task closes the three gaps — **accept/reject**, **automations**,
and **invitations** — each with its own optional SMS-provider override picker, mirroring the D27/D28
SMTP/SMS override work.

## Scope

- **In:**
  - Stage 1 — accept / acceptToCategory / reject send SMS (via `getNotificationTemplate(..., 'sms')`),
    snapshotting the provider onto `guest_sms`.
  - Stage 2 — invitations can carry an SMS template + provider (collection + per-invitation), sent
    alongside the invitation email via a new `invitation_sms` send-log table.
  - Stage 3 — an automation setup can also text its guests (`with_sms_template` mirrors
    `with_email_template`), reusing the existing `guest_sms` + `SendGuestSMSEvent` pipeline.
  - Admin pickers (SMS template + SMS provider override) + EN/AR strings on every touched form.
- **Out:**
  - OTP text templating (guest phone-OTP stays inline per D28).
  - Mobile login-OTP.
  - `SmsSender` still speaks Unifonic only (no new gateway).
  - No `routes/api.php` mobile-surface change.

## Log

- 2026-07-20 — opened; SMS-vs-email gap matrix confirmed automations + invitations had **no** SMS.
- 2026-07-20 — Stage 1 (accept/reject) done: `GuestsController` creates a `guest_sms` row +
  dispatches `SendGuestSMSEvent`; category "SMS notifications" picker relabelled register/accept/reject.
- 2026-07-20 — Stage 2 (invitations) done: migration `2026_07_20_000006_add_invitation_sms`
  (`invitations`/`invitation_collections` gain `sms_template_id` + `sms_config_id`; new
  `invitation_sms` table); `InvitationSms` model + `createFromInvitation`; `SendInvitationSmsEvent`
  + `SendInvitationSmsListener` (registered); wired into invite / bulk / reminder / extract-bulk;
  resources expose the fields; admin pickers on invitation + collection forms + extract modal.
- 2026-07-20 — Stage 3 (automations) done: migration `2026_07_20_000007_add_automation_sms`
  (`automation_setups` gains `with_sms_template` + `sms_template_id` + `sms_config_id`);
  `AutomationController::send` creates a `guest_sms` row + dispatches `SendGuestSMSEvent` per guest
  when `with_sms_template`; admin `with_sms_template` toggle + SMS template/provider pickers.
- 2026-07-20 — gates green (backend `pint --test` + `phpstan` clean; admin `yarn type-check` +
  eslint clean). Durable decisions promoted to ledger **D29**.

## Decisions

Durable decisions promoted to [../../decisions/LEDGER.md](../../decisions/LEDGER.md) **D29**. Task-local:

- Automations + accept/reject **reuse `guest_sms` + `SendGuestSMSEvent`** rather than adding new
  per-flow SMS tables — those flows already target a `Guest`, matching the register-complete path.
  Invitations are **not** guest-backed (token-based), so they get a dedicated `invitation_sms` table
  + listener (mirroring `invitation_emails`).
- Invitation SMS placeholders are invitation-specific (`{{ first_name }}`, `{{ last_name }}`,
  `{{ invitation_link }}`) built from the invitation token + category slug.
- SMS is **independent of email** on every flow — a setup/invitation may text, email, or both.

## Definition of Done

- [x] Code merged to `dev` in backend + admin
- [x] EN + AR translations in the same commit (`sms_override`, `with_sms_template`)
- [x] Quality gate green (backend `pint --test` + `phpstan`; admin `yarn type-check`)
- [x] Docs updated (this TASK.md; index row; ledger D29; HANDOFF)
- [x] Mobile contract checked — `routes/api.php` mobile surface untouched (only admin routes)
- [ ] Manual QA with a real active SMS provider (accept/reject text, invitation text, automation text)
