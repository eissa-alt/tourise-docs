# Task 014 — Unify OTP SMS onto the dynamic SMS provider config

- **Status:** `planned` (not started) — plan documented, awaiting kickoff + the 3 open decisions below
- **Opened:** 2026-07-20
- **Owner:** —
- **Sub-app(s):** backend (+ docs; admin only if an `fgc` provider form field is added)
- **Branch(es):** `dev`

## Goal

Make **all guest-facing SMS flow through one admin-managed provider** — the DB-driven
`sms_provider_configs` / `SmsSender` stack shipped in Task 013 (ledger D26). Registration
(register-complete) already does. The **registration phone-OTP** path does **not**: it bypasses the
dynamic config entirely and calls a **hardcoded FGC gateway with hardcoded credentials in source**. This
task moves OTP onto the dynamic stack (and removes the hardcoded secret).

## Current state (verified 2026-07-20, read-only audit)

- **Registration (register-complete): already on the dynamic config.** ✅
  `GuestsController::store()` → `GuestSMS::create` + `event(new SendGuestSMSEvent(...))`
  (`app/Http/Controllers/GuestsController.php:865–875`) → `SendGuestSMSListener` → `SmsSender` →
  active-default `SmsProviderConfig` row. **No provider change needed here.** (Separate, out-of-scope
  gaps: related/partner guests + admin-created `storeGuest` send no SMS.)
- **Registration phone-OTP: hardcoded, NOT on the dynamic config.** ❌
  `AuthController::phoneVerification()` (`app/Http/Controllers/AuthController.php:971`):
  - `authenticateSMSAPI()` (`:1099`) — two-step auth to `https://cnc.fgc.sa/authenticate` with
    **hardcoded credentials in source** (`sdbankApi` / `e#E2qrg%y6YU`).
  - `sendSMS()` (`:1144`) — posts to `https://cnc.fgc.sa/sendSmsNotifications`, header `SDB`,
    `messageTypeId: 3`, inline body `"Your verification code is: {otp}"`.
  - Fully bypasses `SmsSender` / `SmsProviderConfig`. Fires regardless of env (works in dev today).
  - `phoneConfirmation()` (`:1043`) just validates the `phone_verifications` token — no send, unaffected.
- **Email-OTP path** (`emailVerification`, `:449` `Mail::send`) is a separate concern — **out of scope**;
  this task is SMS delivery only.

FGC is a **different provider shape** than Unifonic (two-step auth + `SDB` sender header), and `SmsSender`
currently only knows `provider_key = 'unifonic'`.

## Scope

- **In:** route registration phone-OTP delivery through the dynamic SMS stack instead of the hardcoded
  FGC calls; remove the hardcoded FGC credentials from source; keep the OTP verify/confirm token machinery
  (`phone_verifications`, drafts) unchanged.
- **Out (explicitly NOT this task):** email-OTP; the accept/reject SMS gap; automations SMS; invitations
  SMS; related/admin-created-guest registration SMS; mobile-app login OTP. (Tracked separately.)

## Open decisions (BLOCKING — needed before coding; recommended default in **bold**)

1. **Provider strategy for OTP:**
   - **(a) Add an `fgc` provider to `SmsSender` + `SmsProviderConfig`** (two-step authenticate→token→send,
     `SDB` header, `messageTypeId`), so OTP keeps the **same gateway** it uses today but configurably
     (creds move to the DB row / env). ← **recommended** — FGC/`SDB` looks client-mandated for OTP; don't
     silently switch gateways.
   - (b) Reuse the generic default provider (Unifonic) for OTP. Simpler, but **changes the actual gateway**
     that delivers OTP — needs client confirmation first.
   - _Note:_ if (a), OTP may need to target a **specific** provider row (its own `fgc` config) rather than
     the single active-default row, since register-complete SMS (Unifonic) and OTP (FGC) could use
     different gateways simultaneously. Decide selection: by `provider_key`, a role/purpose flag on the
     config row, or a dedicated "otp provider" setting.
2. **Non-production behaviour:** the dynamic listener **blocks sends in non-production**
   (`SendGuestSMSListener:62`); OTP currently sends in dev. Keep OTP **sending in non-prod** (exempt it) or
   apply the same non-prod block? **Default: exempt OTP** (dev/stage need real OTP to test the join flow) —
   but confirm.
3. **OTP message source:** OTP body is a per-send dynamic string, not a stored `SmsTemplate`. Send via
   `SmsSender` **directly with an inline message** (not `SendGuestSMSEvent`, which is template + `guest_sms`
   -log oriented), or introduce a dedicated **OTP SMS template**? **Default: inline direct `SmsSender` call**
   (OTP isn't a marketing/guest template; keep it simple), optionally logging to `guest_sms`.

## Proposed approach (assuming defaults a + exempt + inline)

1. **Backend `SmsSender`:** add a `sendViaFgc()` branch (authenticate → token → send, `SDB` header,
   `messageTypeId`) alongside `sendViaUnifonic()`; widen the controller `provider_key` enum + validation to
   include `fgc` (with its own required fields: `username`/`password` or reuse `api_key`/`api_secret` slots,
   `sender_id` = `SDB`).
2. **Provider selection for OTP:** resolve the OTP provider config (by `provider_key='fgc'` active row, or a
   purpose flag — per decision 1) and call `SmsSender` directly with the OTP text; drop
   `authenticateSMSAPI()` + `sendSMS()` hardcoded methods from `AuthController`.
3. **Secret removal:** the hardcoded `sdbankApi` / `e#E2qrg%y6YU` creds move into the DB config row (encrypted,
   like the other secrets) — nothing sensitive left in source.
4. **Env guard:** apply the chosen non-prod behaviour (decision 2).
5. **Admin (only if needed):** surface the `fgc` provider option + its fields in
   `sms-provider-configs` form (the form already branches on `provider_key`).

## Risks / notes

- `routes/api.php` phone-verification endpoints (`phone-verification` / `phone-confirmation`) are **public
  guest routes** — confirm whether they appear in the **mobile contract**
  (`docs/mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf`) before touching signatures. The plan does **not**
  change request/response shapes, only the delivery mechanism, so mobile impact should be nil — but verify.
- Removing the hardcoded creds is a security improvement (secret currently committed in source).
- Registration register-complete needs **no change** — already dynamic.

## Definition of Done

- [ ] The 3 open decisions above resolved + recorded
- [ ] Backend: OTP delivery goes through `SmsSender` / `SmsProviderConfig`; hardcoded FGC creds removed
- [ ] Non-prod behaviour per decision 2; OTP request/response shapes unchanged
- [ ] Admin `fgc` provider fields (only if decision 1a needs them) + EN/AR strings in the same commit
- [ ] Backend `composer qa` green (pint + phpstan + tests); admin `yarn type-check` + eslint if touched
- [ ] Mobile contract checked for the phone-verification endpoints (`docs/mobile/…`)
- [ ] Docs updated (this TASK.md → `done`; index row; ledger entry if the provider abstraction changes durably)
