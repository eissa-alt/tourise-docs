# Task 013 — SMS provider config (DB-driven "SMS SMTP") port from cyan

- **Status:** `done` (code) — manual send-test QA pending (needs prod env + real Unifonic creds)
- **Opened:** 2026-07-20
- **Closed:** 2026-07-20
- **Owner:** —
- **Sub-app(s):** backend + admin
- **Branch(es):** `dev`

## Goal

Bring cyan's **SMS provider config** stack ("SMS SMTP") into ALT so SMS transport credentials are managed
in the DB (admin CRUD, multi-row, `is_active` + a single `is_default`) exactly like the existing
`smtp_configs` mail stack — instead of being pinned to `.env` via `config('services.unifonic')`. This is
the foundation for the follow-up SMS tasks the user flagged.

Ported from `115-cyan-basecode` (`sms_provider_configs` table + controller + resource + `SmsSender` +
admin `sms/provider-configs` UI), adapted to ALT conventions: mirrors ALT's own `SMTPConfig*` shape
(`BaseApiController` + `apiSuccess/apiError`, `admin.can:` gating, BFF proxy calls, lucide + `getApiError`
+ `react-hot-toast`, no `js-cookie`/Bearer, no heroicons).

## Scope

- **In:** `sms_provider_configs` table (additive migration) + `SmsProviderConfig` model (encrypted
  `app_sid`/`api_key`/`api_secret`, `$hidden`) + `SmsProviderConfigResource` (masks `app_sid`) +
  `SmsProviderConfigController` (index/store/show/update/destroy/toggle-active/make-default/check-default/
  send-test) + `SmsSender` service (unifonic adapter) + admin routes gated `admin.can:sms_config` +
  `AdminPermissions` `sms_config` widened to CRUD+block. Rewire `SendGuestSMSListener` to read the active
  default DB row via `SmsSender`. Admin UI: listing + form + delete/send-test modals + 3 pages + sidebar +
  module-icon + EN/AR strings.
- **Cutover cleanup:** removed the `config/services.php` `unifonic` block (env creds no longer consulted),
  and pruned dead debug methods `sendSMS2`/`sendSMS3`/`smsReplacePlaceholders`/`buildQrCodeLink`/
  `buildInvitationLink` (+ their commented `web.php` routes + stale phpstan baseline entry) from
  `GuestsController` — they duplicated the real listener path and only referenced the old env creds.
- **Out (explicitly NOT this task):** SMS **templates** UI/CRUD (already present in ALT, unlinked) and any
  new send/scheduling flows — those are the follow-up "new tasks regarding SMS" the user flagged. No
  `mobile/*` change (admin-only routes).

## Decisions

- **Mirror `smtp_configs`, not cyan verbatim** — ALT already has the DB-driven SMTP pattern; the SMS stack
  reuses its exact shape (multi-row + `is_active` + single `is_default`, masked secret on the wire,
  leave-blank-to-keep on edit) so admins get one mental model for both transports.
- **Provider abstraction via `SmsSender` + `provider_key`** — v1 validates `unifonic` only
  (`Rule::in(['unifonic'])`); a new provider is a one-line enum append + a `sendVia*` branch +
  (optionally) surfacing the generic `api_key`/`api_secret` slots in the form. Unknown `provider_key`
  throws so a stale row fails loud.
- **Secrets encrypted at rest** (`app_sid`/`api_key`/`api_secret` `encrypted` casts); resource returns only
  `app_sid_masked` (last 4), `api_key`/`api_secret` never leave the backend (`$hidden`).
- **`send-test` honours the non-production guard** the listener uses — on non-prod it returns
  `sent:false` + reason instead of hitting the provider, so dev/stage test clicks never send real SMS.
- **RBAC:** `sms_config` feature widened `['view','update']` → `['view','create','update','delete','block']`
  to cover the new CRUD + toggle (block) actions, matching `smtp_configs`.
- **`config/services.php` `unifonic` removed** (not left as a fallback) — no dual code path; a fresh env
  setting `UNIFONIC_*` would silently do nothing, so the block is gone to avoid the trap.

## Log

- 2026-07-20 — opened. Studied cyan's `sms_provider_configs` stack + ALT's `SMTPConfig*` analog + ALT's
  current `SendGuestSMSListener` (was reading `config('services.unifonic')`). Confirmed ALT already had an
  unlinked `sms/templates` + `sms/config` admin page set and a live guest-SMS listener/event — only the
  provider-config layer was missing.
- 2026-07-20 — **code complete (ledger D26).** Backend: migration
  `2026_07_20_000002_create_sms_provider_configs_table` + `SmsProviderConfig` model + `SmsProviderConfigResource`
  (masks `app_sid`) + `SmsProviderConfigController` (mirrors `SMTPConfigController`, minus export/clone) +
  `App\Services\Sms\SmsSender` (unifonic adapter, returns raw `Response`) + admin route group
  `admin/sms-provider-configs` gated `admin.can:sms_config`; `SendGuestSMSListener` rewired to the active
  default DB row via `SmsSender`; `AdminPermissions` `sms_config` widened; `config/services.php` `unifonic`
  block removed; dead `GuestsController` SMS/link debug methods + commented `web.php` routes removed + the
  now-stale `GuestsController` `env()` phpstan-baseline entry (`count: 2`) pruned. Admin: `sms-provider-config`
  interface + `sms-provider-configs-{form,listing}` + `sms-provider-{delete,send-test}-modal` + 3 pages
  (`/[lang]/sms/provider-configs/{index,create,edit/[id]}`) gated `checkFeaturePermission('sms_config')` +
  live SMS sidebar section (was commented) + module-icon + EN/AR strings. **Gates:** backend `composer qa`
  green (pint **passed** + phpstan **No errors** + tests **465/3** pre-existing baseline); admin
  `yarn type-check` + eslint clean + `next build` compiles (new `/sms/provider-configs*` routes present).
  `mobile/*` untouched.

## Definition of Done

- [x] Backend: `sms_provider_configs` migration + model (encrypted secrets, `$hidden`) + resource (masked)
- [x] Backend: `SmsProviderConfigController` (CRUD + toggle-active + make-default + check-default + send-test)
      + `SmsSender` service + gated `admin/sms-provider-configs` routes + `AdminPermissions` widened
- [x] Backend: `SendGuestSMSListener` reads the active default DB row via `SmsSender`;
      `config/services.php` `unifonic` removed; dead `GuestsController` debug methods pruned
- [x] Admin: listing + form + delete/send-test modals + 3 pages + sidebar + module-icon
- [x] EN + AR translations in the same commit
- [x] Backend `pint --test` + `phpstan analyse` + `php artisan test` green (465/3 pre-existing); admin
      `yarn type-check` + eslint clean + `next build` compiles. _(`yarn production` needs `.env.production` —
      deferred to real-env QA, same as Task 012.)_
- [x] Mobile contract unaffected (`routes/api.php` `mobile/*` untouched — new routes are admin-only)
- [x] Docs updated (this TASK.md → `done`; index row; ledger D26; HANDOFF)
- [ ] **QA (manual, needs prod env + real Unifonic app):** create a provider config, set active+default, fire
      a guest SMS (or `send-test`) in production and confirm delivery; confirm non-prod `send-test` returns
      `sent:false` with a reason (no provider call); confirm delete/deactivate of the default row is blocked.
