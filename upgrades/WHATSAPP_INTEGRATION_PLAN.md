# WhatsApp Integration — Plan

> **Status:** IN PROGRESS — Phase W0.1 started (provider-config backend written, uncommitted).
> **Phase:** P24 (commits `P24.x`). Working branch `dev` (code) / `main` (docs).
> **Started:** 2026-07-24. Follows the P23 email/SMS hardening pass (ledger D35).

## 1. Goal & scope

Add **WhatsApp** as a first-class communications channel, built as a **faithful twin of our
email/SMS implementation** (D26–D31). Provider: **Meta WhatsApp Cloud API** (Graph API v22.0),
which sends via **pre-approved message templates** (Meta reviews each template; the CMS stores a
*pointer* + variable/button mapping, not the copy).

**Scope — all four flows** (user-confirmed):

1. **Invitations** — WhatsApp as a third single-channel option (`email | sms | whatsapp`).
2. **Automations + guest notifications** — bulk WhatsApp + register/accept/reject.
3. **Inbound RSVP (two-way)** — guests reply via quick-reply buttons → invitation RSVP status →
   on confirm, auto-send the QR badge. Needs the Meta webhook (new public routes).
4. **WhatsApp OTP** — deliver the registration OTP over WhatsApp (net-new; no x-hci analog).

## 2. Source assessment (x-hci-campaign)

`/Users/admin/Projects/ALT/x-hci-campaign` has a real, complete Meta Cloud API WhatsApp build
(1,019-line `WhatsAppService`, templates, webhook w/ RSVP, admin UI). Verdict from the 7-slice
assessment: **suitable as a blueprint + salvageable transport core, NOT a drop-in base — reuse ≈ 40–45%.**

It branched **before our D26–D31 restructure**, so its conventions diverge and must NOT be adopted:

| Our convention | x-hci does instead (do not copy) |
|---|---|
| `channel` enum on invitations+collections; row-driven send | `delivery_channel` string on collection only; channel from request body |
| Separate `invitation_sms`/`invitation_emails` log tables | 6 inline `whatsapp_*` columns on the `invitations` row |
| DB `SmsProviderConfig` (encrypted, active+default, snapshot) | credentials in `.env`; no provider table |
| Event/listener + queued fan-out | synchronous in-request service calls |
| Category master gates (`getNotificationTemplate`) | no gate |
| Shared `{{ }}` placeholder resolution | two ~70-line duplicated inline variable maps |

**Reference x-hci for ONLY:** the Meta Graph send payload/approved-template mechanics, the webhook
signature (HMAC + constant-time compare — actually better than our Mailtrap webhook) + RSVP button
decode, and the template variable/URL-button mapping. Everything else copies **our** files.

## 3. Architecture decisions (locked)

- Un-reserve `whatsapp` in the invitation **`channel` enum** (code-only — validation `in:email,sms`
  → `in:email,sms,whatsapp` + off-channel null-ing in `store()`/`update()`/`extractBulk`). No `delivery_channel`.
- **Separate `invitation_whatsapp` log table** (twin of `invitation_sms`, + `reply_status`/`replied_at`).
- **`whatsapp_provider_configs`** DB table modeled 1:1 on `SmsProviderConfig` (encrypted
  `access_token`/`app_secret`/`verify_token`, plain `phone_number_id`/`waba_id`/`graph_url`,
  `is_active` + single `is_default`).
- **`guest_whatsapps`** for automation/guest sends (twin of `guest_sms`, with `workflow_value`).
- Sends go through a new **`App\Services\WhatsApp\WhatsAppSender`** (`SmsSender`-shaped) via
  **event/listener + queued** dispatch — never synchronous.
- Category **`with_whatsapp`** master gate + a `whatsapp` branch in `getNotificationTemplate`;
  **`with_whatsapp_otp`** for OTP (with cross-validation like L-nocrossvalidation).
- WhatsApp templates use our **`is_active` + toggle** convention (Meta's *approval* status is a
  separate external concern).
- **All migrations additive / forward-only** — `migrate:fresh` is banned (real data). Explicit
  `$table` names everywhere (avoid Laravel's `whats_app` inference).
- Every admin screen follows **our** patterns: `/api/proxy` + `useFetch` (no manual Bearer),
  `checkFeaturePermission(featureId)` RBAC (never `user.type`), `DialogShell` + `lucide`,
  `CustomInput`/`FormWrapper`/listing primitives, EN+AR in the same commit.

## 4. Reuse matrix

| Component | Verdict | Effort | Adaptation |
|---|---|---|---|
| Transport (`WhatsAppService`) | adapt | L | Lift Graph payload builder, template/lang/button resolution, phone normalize, RSVP decode, HMAC verify into `WhatsAppSender`. Add timeout+try/catch, drop `.env` fallback, `env()`→`config()`, de-dup variable maps. |
| Provider config | build net-new | S–M | `whatsapp_provider_configs` 1:1 on `SmsProviderConfig`. Skip x-hci's `whatsapp_configs` (event metadata, not creds). |
| Template model + CRUD | adapt | M | Port field set; `BaseApiController` + `apiSuccess`/`apiError`; split config out; transactions; `is_active`. Re-author seeder to *our* approved Meta templates. |
| Migrations/schema | adapt | M | New additive migrations; separate `invitation_whatsapp` table (not inline cols); `guest_whatsapps` (clean table name). Skip the `fix_*` data patch. |
| Invitation flow | rewrite (seam) | M–L | Enum + off-channel null-ing; `InvitationWhatsApp::createFromInvitation` + `SendInvitationWhatsAppEvent` + queued listener. |
| Automation + guest flow | adapt/rewrite | M | `guest_whatsapps` + `SendGuestWhatsAppEvent`; boolean `with_whatsapp_template`; reinstate the M11 idempotency guard; no per-send columns on `automations`. |
| Webhook | adapt | M | Port verify/handle/signature skeleton; re-point writes to our tables; QR follow-up via event; fix null-deref; per-entry try/catch. |
| Admin UI | adapt | M | Blueprint only — rewire proxy/`useFetch`, `checkFeaturePermission`, `DialogShell`+`lucide`; whatsapp as a 3rd channel; route literals through `Translate`. |

## 5. Phased delivery (each phase = small reviewed batches, gate-clean, commit on approval)

### W0 — Foundation (no sends)
- **W0.1** `whatsapp_provider_configs` migration + `WhatsAppProviderConfig` model + resource +
  `WhatsAppProviderConfigController` (CRUD) + routes + `whatsapp_config` RBAC feature. *(started)*
- **W0.2** `whatsapp_templates` migration + `WhatsAppTemplate` model + resource/select-resource +
  `WhatsAppTemplatesController` + routes + `whatsapp_templates` RBAC + seeder shell.
- **W0.3** `App\Services\WhatsApp\WhatsAppSender` (SmsSender shape + Meta Graph core) + provider
  `send-test` (template-based).
- **W0.4** admin provider-config screens + `whatsapp-provider-config-select` (twin of `sms/provider-configs`).
- **W0.5** admin template screens + `whatsapp-template-select` (twin of `emails/sms`) + sidebar links.

### W1 — Invitations (outbound)
- `invitation_whatsapp` table + `whatsapp_template_id`(+`whatsapp_config_id`) FKs on
  invitations/collections; un-reserve `whatsapp` in the enum; extend channel null-ing.
- `InvitationWhatsApp` model + `SendInvitationWhatsAppEvent` + queued listener; invite/bulk/reminder wiring.
- Admin channel picker (3rd option) + template/provider pickers + `send-whatsapp-modal`;
  `invitation_whatsapp` logs (controller/resource/export + `whatsapp_logs` RBAC + page).
- Category `with_whatsapp` gate. Mobile notice (additive channel + category flags).

### W2 — Automations + guest notifications
- `guest_whatsapps` table + `GuestWhatsApp` model; `with_whatsapp_template` + `whatsapp_template_id`
  on `automation_setups`.
- `SendGuestWhatsAppEvent` + queued listener; automation fan-out (idempotent) + register/accept/reject
  + resend; admin toggles + guest-WhatsApp log page.

### W3 — Inbound RSVP (webhook)
- `WhatsAppWebhookController` (GET verify + HMAC-signed POST) + public `GET|POST /webhooks/whatsapp`
  routes (beside `/webhooks/mailtrap`).
- `processStatus` (delivery receipts → log tables) + `processReply` (YES/NO buttons → invitation RSVP)
  + confirm → QR follow-up via event. Per-entry try/catch. Mobile notice (informational — new public routes).

### W4 — WhatsApp OTP (net-new)
- `otp_whatsapp_config_id` + `with_whatsapp_otp` on categories; OTP-over-WhatsApp send (approved
  template) in `AuthController`; frontend option; cross-validation (`with_whatsapp_otp` requires
  `with_whatsapp`). Mobile notice (additive category flag).

## 6. Migrations (additive, forward-only — `migrate:fresh` banned)

1. `create_whatsapp_provider_configs_table` *(W0.1 — written)*
2. `create_whatsapp_templates_table` (fold button-index columns in) *(W0.2)*
3. `create_guest_whatsapps_table` (twin of `guest_sms`) *(W2)*
4. `add_whatsapp_template_to_invitations_and_collections` (FKs; NO `delivery_channel`, NO inline cols) *(W1)*
5. `create_invitation_whatsapp_table` (twin of `invitation_sms` + `reply_status`/`replied_at`) *(W1)*
6. `add_whatsapp_to_automation_setups` (`with_whatsapp_template` + `whatsapp_template_id`) *(W2)*
7. `add_whatsapp_otp_to_categories` (`with_whatsapp`, `with_whatsapp_otp`, `whatsapp_config_id`,
   `otp_whatsapp_config_id`) *(W1/W4)*
- Un-reserving the `channel` enum value is **code-only** (no migration).

## 7. Ops prerequisites (outside code — needed for live sends)

- A **Meta Business** account + **WhatsApp Business phone number** + **WABA id**.
- **Pre-approved message templates** in Meta (name + exact variable/button layout) for each purpose
  (invitation, QR, OTP, notifications). The `whatsapp_templates` row *points* at these by name; the
  schema cannot enforce that they're approved.
- **Webhook URL registered** in Meta (for W3) with the `verify_token` + `app_secret` matching a
  `whatsapp_provider_configs` row.

## 8. Mobile contract

WhatsApp is **additive** — mobile's surface (identity/agenda/speakers/sessions/chat/…) has no
invitation or WhatsApp routes, and there's zero existing WhatsApp mention. Two additive ripples to
document via a `MOBILE_NOTICE_*` (like the `with_email_otp` one): the new category `with_whatsapp` /
`with_whatsapp_otp` flags that ride the invitation-verify payloads, and the new public webhook routes
(mobile ignores them). **No breaking change.** Re-check the PDF before touching `routes/api.php`.

## 9. Open decisions (defaults chosen; flag to change)

- Observability: **separate `invitation_whatsapp` table** (recommended, chosen) vs inline columns.
- Provider config: **DB `whatsapp_provider_configs`** (recommended, chosen) vs `.env`.
- Template lifecycle: **`is_active` + toggle** (chosen) vs a Meta-lifecycle `status` string.
- Category gating: add `with_whatsapp` master switch (chosen).
