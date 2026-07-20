# Task 015 — Per-flow SMTP override (choose which SMTP config sends each email flow)

- **Status:** `done (code)` — implemented + gates green (2026-07-20); manual QA pending
- **Opened:** 2026-07-20
- **Owner:** —
- **Sub-app(s):** backend + admin (+ docs)
- **Branch(es):** `dev`
- **Ordering:** intended to land **before** the broader SMS-notifications work (Task 014 + the accept/reject
  / automations / invitations SMS gaps), per the requester — the email side gets the override pattern first.

## Goal

Let admins **override the base/default SMTP** on a per-flow basis — pick which `smtp_configs` row sends each
email flow instead of always using the single active-default row. Falls back to the default when no override
is set. Flows in scope:

1. **Registration notifications** — `categories.smtp_config_id` for `register-complete` / `accept` /
   `reject` (one picker in the category form).
2. **Guest email-OTP** — separate `categories.otp_smtp_config_id` (second picker). Category-linked via the
   join-form `category` slug (`AuthController::emailVerification`).
3. **Automations** — override on the automation setup.
4. **Invitations** — override on the invitation (and/or invitation collection).

_Admin CMS login OTP is out of scope (not category-linked, unrelated to guest flows)._

## Current state (verified 2026-07-20, read-only audit)

**The runtime override mechanism already exists** — this is why the task is mostly wiring, not new infra:

- `app/Services/Mail/DynamicSmtpService.php`
  - `applyConfig(SMTPConfig $row)` — writes the row's host/port/encryption/user/pass into a runtime
    `dynamic_smtp` mailer + sets `mail.default` + `mail.from`. **This is exactly the override primitive.**
  - `applyDefaultIfAvailable()` — loads the single `is_default=true AND is_active=true` row and applies it;
    falls back to `.env` mailer if none. **Every real send calls this today.**
- The **test-send** path already proves per-row selection: `SMTPConfigController::sendTestEmail` (`:141–159`)
  calls `applyConfig($specificRow)` before `Mail::raw(...)`.
- **No `smtp_config_id` exists anywhere yet** (repo-wide search = 0 hits). No per-record SMTP on
  `guest_emails`, `invitation_emails`, `automations`, `automation_setups`, `invitations`,
  `invitation_collections`, or in `categories.notification_settings`.

Per-flow send paths + where SMTP is currently chosen (always the default):

| Flow | Dispatch site | Notification / send | SMTP call |
|------|---------------|---------------------|-----------|
| register-complete / accept / reject | `GuestsController` (`836–861`, `1637–1648`, `1735–1747`, `1795–1807`) | `GuestEmail::sendEmail()` → `SendGuestEmailNotification::toMail()` | `applyDefaultIfAvailable()` (`SendGuestEmailNotification.php:34`) |
| OTP email | `AuthController::emailVerification` (`499–536`) | `Mail::send(...)` | `applyDefaultIfAvailable()` (`:500`) |
| Automations | `AutomationController::send` (`65–82`) | `Automation::sendEmail()` → `SendAutomationEmailNotification::toMail()` | `applyDefaultIfAvailable()` (`:38`), **then** may switch to static `smtp-bulk` mailer if `MAIL_HOST_BULK` env set (`:76`) |
| Invitations | `InvitationsController` (`527–539`, `376–389`, `576–579`) | `InvitationEmail::sendEmail()` → `SendInvitationEmailNotification::toMail()` | `applyDefaultIfAvailable()` (`:29`) |

Category `notification_settings` JSON shape today (per event `on_register_complete`/`on_accept`/`on_reject`):
```jsonc
{ "on_<event>": {
    "enabled": true,
    "email": { "enabled": true, "email_template_id": "<uuid|null>" },   // ← add smtp_config_id here
    "sms":   { "enabled": true, "sms_template_id":   "<uuid|null>" }
} }
```
- Stored/read as a raw JSON string (no Eloquent cast); getter `Category::getNotificationTemplate($event,$channel)`
  (`Category.php:125–156`).
- Admin form email/sms pickers: `categories-form.tsx` — emails `1164–1344`, sms `1347–1510`;
  `NOTIFICATION_EVENTS = ['on_register_complete','on_accept','on_reject']` at `:50`; TS shape
  `interfaces/category.tsx:84–118`.

## Scope

- **In:** a shared "apply a chosen SMTP row, else fall back to default" primitive; storing the admin's chosen
  `smtp_config_id` per flow; applying it at send time; admin UI pickers (category form for the registration
  flow; automation form; invitation form/collection); EN + AR strings.
- **Out (explicitly NOT this task):** the SMS provider override analog (SMS still uses its single default
  `SmsProviderConfig`); the SMS-notification gaps themselves (Task 014 + accept/reject/automations/invitations
  SMS); any change to the `smtp_configs` CRUD itself.

## Proposed design

### 1. Shared primitive (backend, do first)
Extend `DynamicSmtpService` with a single resolver so there is **one code path**:
```php
// pseudocode
public function applyConfigById(?string $smtpConfigId): bool
{
    if ($smtpConfigId) {
        $row = SMTPConfig::query()->where('is_active', true)->find($smtpConfigId);
        if ($row) { $this->applyConfig($row); return true; }
    }
    return $this->applyDefaultIfAvailable(); // override missing/inactive/deleted → safe fallback
}
```
Every notification's `toMail()` changes from `applyDefaultIfAvailable()` to
`applyConfigById($resolvedOverrideId)` (null preserves today's behaviour exactly).

### 2. Where the chosen id lives — **snapshot onto the per-send row** (D1)
Add a nullable `smtp_config_id` to the per-send tables and copy the resolved override in at **create** time
(where the template is already resolved), so the notification just reads `$this->row->smtp_config_id`:
- `guest_emails.smtp_config_id` — set in `GuestsController` when creating the `GuestEmail`, copied from the
  category's whole-flow override `categories.smtp_config_id` (register-complete / accept / reject).
- `automations.smtp_config_id` — copied from `automation_setups.smtp_config_id` at expansion.
- `invitation_emails.smtp_config_id` — resolved at create from invitation → collection → default.
- **Guest email-OTP has no send-row** (`Mail::send` direct, tokens in `email_verifications`) → resolve at
  send time: read the `category` slug from the request → `Category::where('slug',…)->value('smtp_config_id')`
  → `applyConfigById()`.

Rationale: snapshot survives later category/setup edits, auditable, uniform read at send.

### 3. The admin choice fields
- **Registration notifications:** nullable `categories.smtp_config_id` for register-complete + accept + reject.
- **Guest email-OTP:** separate nullable `categories.otp_smtp_config_id` (migration `000004`). Two selects in
  `categories-form.tsx` Notifications section. OTP lookup: `->value('otp_smtp_config_id')`.
- **Automations:** nullable `smtp_config_id` on `automation_setups`, select in `automation-form.tsx` next to
  the email template picker (shown when `with_email_template`).
- **Invitations:** nullable `smtp_config_id` on `invitations` (per-invitation, `invitations-form.tsx:464–473`)
  and optionally `invitation_collections` (collection default). Send resolves invitation → collection → default.

## Log

- 2026-07-20 — opened; read-only audit confirmed `DynamicSmtpService::applyConfig()` already applies any
  specific SMTP row at runtime (proven by the test-send path), and no `smtp_config_id` exists anywhere yet.
- 2026-07-20 — decisions D1–D5 resolved. Verified guest email-OTP is category-linked (join form posts the
  `category` slug → `saveGuestDraft`), so OTP folds into the category whole-flow override. Status → `ready`.
- 2026-07-20 — implemented end-to-end. **Backend:** migration `2026_07_20_000003_add_smtp_config_override_columns`
  adds nullable `smtp_config_id` (FK → `smtp_configs`, null-on-delete) to `categories`, `automation_setups`,
  `invitations`, `invitation_collections` (source of choice) and `guest_emails`, `automations`,
  `invitation_emails` (snapshot). New `DynamicSmtpService::applyConfigById(?id)` (active-only, falls back to
  default). Guest-email/invitation/automation notifications read the snapshot; automation override now **wins
  over `MAIL_HOST_BULK`** (`smtp-bulk` only when no override). `GuestsController` snapshots
  `category.smtp_config_id` on register-complete (+ partners) / accept / accept-to-category / reject / manual
  resend (widened the restricted `category:` eager-loads to include `smtp_config_id`).
  `AuthController::emailVerification` resolves the category override live from the `category` slug.
  `InvitationEmail::createFromInvitation` resolves invitation → collection → default. Validation
  (`nullable|uuid|exists:smtp_configs,id`) added to category/automation/invitation stores. New ungated
  `GET admin/smtp-configs/select` (`selectList`) feeds the pickers. Fillable + resources updated.
  **Admin:** reusable `smtp-config-select.tsx` (blank = "use default"); pickers wired into the category form
  (one whole-flow override), automation form (under email template), invitation collection form; interfaces +
  EN/AR (`smtp_override`, `use_default_smtp`).
- 2026-07-20 — gates: backend `pint --test` pass, `phpstan` clean, `php artisan test` = only the documented
  baseline failures (ExampleTest 403, QrScanner avatars) + one suite-order faker flake in SessionsTest search
  (passes in isolation with/without these changes — not caused by 015). Admin `yarn type-check` pass, eslint
  clean.
- 2026-07-20 — **split OTP SMTP from notification SMTP** per user: new `categories.otp_smtp_config_id` +
  second admin picker; `AuthController` OTP reads `otp_smtp_config_id` only. Register/accept/reject keep
  `smtp_config_id`.

## Decisions (resolved 2026-07-20)

- **D1 — storage:** **snapshot** `smtp_config_id` onto per-send rows (`guest_emails`, `automations`,
  `invitation_emails`); guest email-OTP resolves live from the category slug (no send-row). Auditable,
  edit-proof.
- **D2 — automation bulk conflict:** **the per-flow DB override wins** over the static `smtp-bulk` mailer;
  only fall back to `smtp-bulk` (when `MAIL_HOST_BULK` set) if no override is present.
- **D3 — inactive/deleted override:** **silently fall back to the active default** (`applyConfigById`
  handles it); the admin picker lists only `is_active` configs.
- **D4 — OTP:** **included, as a separate category field** `otp_smtp_config_id` (guest OTP is category-linked —
  the join form posts the `category` slug). Not mixed with notification emails. Admin CMS login OTP out of scope.
- **D5 — granularity:** **two category pickers** — `smtp_config_id` for register/accept/reject (not per-event),
  `otp_smtp_config_id` for guest email-OTP.
- **Sequencing:** **all in one task/commit series** — shared resolver + registration (incl. OTP) +
  automations + invitations together.

## Risks / notes

- **Mobile contract:** unaffected. The only `routes/api.php` change is a new **admin-only** route
  (`GET admin/smtp-configs/select`); no `/api/mobile/*` route or public/OTP request/response shape changed.
  The choice lives in admin-managed config + internal `*_emails`/`automations` rows.
- Additive, nullable migrations only; null override = **identical** behaviour to today (default row).
- Keep one resolver (`applyConfigById`) so we don't fork SMTP-selection logic per flow.
- This mirrors, on the email side, the same "default row" pattern SMS uses — a future SMS provider override
  could reuse the shape, but that is out of scope here.

## Definition of Done

- [x] Decisions D1–D5 resolved + recorded (2026-07-20)
- [x] Backend: `DynamicSmtpService::applyConfigById(?id)`; guest-email + invitation + automation notification
      `toMail()` read the snapshotted `smtp_config_id`; guest email-OTP resolves the category override live
- [x] Backend: additive nullable `smtp_config_id` on `categories`, `guest_emails`, `automation_setups`,
      `automations`, `invitation_emails`, `invitations`, `invitation_collections`; snapshot at create;
      automation-bulk precedence per D2 (override wins)
- [x] Admin: one SMTP-override picker in the category form (whole registration flow), automation form,
      invitation collection form; uses new ungated `/smtp-configs/select` list (active only)
- [x] EN + AR translations in the same commit
- [x] Backend gates green (`pint --test` + `phpstan`; `php artisan test` = baseline failures only); admin
      `yarn type-check` + eslint clean
- [x] Mobile contract: `routes/api.php` touched but only an **admin** route added
      (`GET admin/smtp-configs/select`); no mobile (`/api/mobile/*`) or public shapes changed
- [ ] Manual QA: per-flow send picks the chosen account; blank = default; inactive/deleted override falls back
      to default; automation override beats `MAIL_HOST_BULK`; guest email-OTP honours the category account
- [x] Docs updated (this TASK.md → `done (code)`; index row; ledger D27; HANDOFF)
