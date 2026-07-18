# Boolean Refactor Plan — alt-static-basecode

Store real booleans instead of string pseudo-booleans across backend + admin + frontend.
Adapted from the **cyan** reference (which completed this and documented it in
`115-cyan-basecode/cyan-basecode-repos/docs_old/BOOLEAN_REFACTOR_*.md`), remapped to our current
migration set. See task log: [../../tasks/001-boolean-db-cleanup/TASK.md](../../tasks/001-boolean-db-cleanup/TASK.md).

**Approach:** edit the original `create_*` (and the few `add_*`/`modify_*`) migrations in place —
no new migrations — then `php artisan migrate:fresh`. This baseline carries no prod data.

> **Cast ownership.** This plan **owns the boolean-cast conversion**. The later
> [DB Refactor Part 4 — Model Hygiene](DB_REFACTOR_PART4_MODEL_HYGIENE.md) only *verifies* boolean-cast
> coverage and handles the *non-boolean* casts (datetime/array/json). Don't double-implement booleans
> across the two.

---

## Track A — pseudo-boolean (`yes`/`null`, `yes`/`no`, `with_`/`is_`) → boolean

### Migrations (string → `boolean()->default(false)`)

Edit these in place; drop the length arg (`, 3`) where present.

- `2023_08_19_171536_create_guests_table.php` — `is_saudi`, `verified`, `checked`,
  `require_flights`, `require_transfer`, `require_accommodation`, `has_printed`,
  `badge_is_collected`, `e_badge_sent`, `check_in`. (`terms` is a consent value — keep as-is;
  the guest form-consent fields `photo_consent`, `display_photo_in_app`, `will_attend`,
  `is_email_verified`, `is_phone_verified` are reviewed case-by-case, see note below.)
- `2023_03_17_233144_create_categories_table.php` — `with_otp`, `with_alternative_email`,
  `with_share`, `show_in_success_page`, `override_company_name`.
- `2024_12_24_210421_modify_categories_table.php` — `accept_to_category`, `with_e_badge`,
  `with_notify_missing_data`, `with_issued_visa`, `with_logistics`, `with_extra_guests`.
- `2025_11_19_194239_add_with_sms_otp_to_categories_table.php` — `with_sms_otp`.
- `2026_02_08_120000_add_success_page_fields_to_categories_table.php` — `with_event_details`,
  `with_entry_qr_code`, `with_download_entry_qr_code`.
- `2023_03_17_167738_create_badges_table.php` — `with_picture`, `with_guest_info`,
  `with_guest_name`, `with_guest_company`, `with_guest_country`, `with_guest_position`,
  `show_background`, `with_qr_code`, `with_parking`, `with_date`, `with_rfid`, `with_crop`.
- `2025_12_11_124243_add_with_dot_and_dot_color_to_badges_table.php` — `with_dot`.
- `2023_06_03_234326_create_email_configs_table.php` — `with_header`, `with_footer`, `with_social`.
- `2023_07_06_154821_create_email_templates_table.php` — `override_poster`,
  `override_poster_footer`, `override_social_links`.
- `2024_05_17_155848_create_automation_setups_table.php` — `with_invitation`,
  `with_email_template`, `change_guest_status`, `to_generate_poster`, `to_category`, `with_e_badge`.
- `2023_03_16_165738_create_countries_table.php` — `override_registration_status`.
- `2023_03_17_233146_create_titles_table.php` — `show_in_badge`, `show_in_user_form`.
- `2025_12_11_095410_add_prefilldata_and_lock_data_to_invitations_table.php` — `prefilldata`,
  `lock_data`.
- `2026_02_16_000001_add_with_from_to_invitations_table.php` — `with_from`.
- `2025_08_22_190144_create_gates_table.php` — `assigned_to_ipad` (leave `scanning_status`).
- `2025_11_12_125249_add_show_in_homepage_to_speakers_table.php` — `show_in_homepage`.
- `2025_11_05_161501_create_guest_sms_table.php` — `is_sent`.
- `2025_09_07_150832_create_guest_emails_table.php` /
  `2026_02_02_000500_create_invitation_emails_table.php` — `is_sent`, `is_delivered`, `is_open`,
  `is_clicked`.
- `guest_logistics` create migration — `self_booking`.
- `2026_02_16_090000_add_plus_x_guests_fields.php` — audit any boolean-ish flags added there.

**Consent-field note:** `photo_consent` / `display_photo_in_app` / `will_attend` / `terms` carry
explicit user-consent semantics and flow through the public registration form and
`MobileAuthController` (`display_photo_in_app` → stored true→'yes'/false→null today). Convert the
storage to boolean AND update the mobile write, or leave as-is — decide per field, following cyan's
`BOOLEAN_REFACTOR_RECHECK.md`. Do not silently break the mobile write.

### Models (`$casts`)

Add `'boolean'` casts for every converted column: `Guest`, `Category`, `Badge`, `EmailConfig`,
`EmailTemplate`, `AutomationSetup`, `Country`, `Title`, `Invitation`, `GuestLogistics`, `Gate`,
`Speaker`, `GuestSms`, `GuestEmail`, `InvitationEmail`.

### Controllers / resources / blade

- `== 'yes'` / `=== 'yes'` → `$request->boolean('x')` (input) or `=== true` (model value).
- Resources return the raw boolean (model cast handles it), not `'yes'`/`'no'`.
- Blade: `=== 'yes'` → `=== true`.
- Seeders / factories: seed booleans, not `'yes'`/`'no'`.
- **Keep** (cyan-intentional): CSV `Exports` emit `yes`/`no` for humans; any input-normalization
  helper that accepts both; HTML meta `content="yes"`.

### Admin

- Swap `CustomSwitchInput` (emits `'yes'|null`) → `CustomSwitchInputBoolean` (raw boolean) in its
  ~13 consumer forms: categories, invitations (form + invitation-form), badges, automation,
  emails-config, emails-templates, titles, countries, conference, and the two bulk-update modals.
- Filter option data (`data/yse-no-types-select.tsx`, `data/verified-types-select.tsx`,
  `data/yse-no-empty-types-select.tsx`) → `value: true` / `value: false`.
- Retype boolean-as-string fields in `interfaces/*` → `boolean`.
- Form `defaultValues`: `null` / `'yes'` → `false`.

### Frontend

- Convert join-step `CustomRadioInput` yes/no fields (`valid_visa`, `require_flights`,
  `require_transfer`, `require_accommodation`) and `is_saudi` set/watch logic to booleans.
- Drop the `=== 'yes'` → boolean conversions at the page SSR boundary (`join/[category]` pages).
- Retype `interfaces/guest.tsx`.
- The public frontend has no `isEnabled` / `CustomSwitchInputBoolean` — do not add cyan's.

---

## Track B — `status` (`active`/`blocked`) → `is_active boolean default(true)` (NEW, beyond cyan)

Cyan left `status` as a string on purpose. We are converting the strictly 2-value ones.

### Audit gate (do first)

Confirm each `status` column is exactly `active`/`blocked`. Convert those; **exclude** multi-value
process statuses: `app_notifications.status` (Pending), `login_attempts.status` (failed),
`email_attachments.status`, `sms_templates` send-state, guest workflow `guest_status_id`, mobile
guest `status` (accepted/invited), and the API-envelope `status` strings (`valid`/`success`).
Decide `guest_statuses` (active/inactive) separately.

### Migrations / models

- Rename `status` string → `is_active boolean default(true)` on the confirmed `create_*` tables
  (edit in place). Update `$fillable` + add `'boolean'` cast.

### Controllers (~18)

- `->where('status', 'active')` → `->where('is_active', true)`.
- `block()` → `is_active = false`; `activate()` → `is_active = true`.
- Update the two `Mobile*Controller` internal queries (`MobileSpeakerController`,
  `MobileSponsorController`) and the notification senders (`SendGuestEmailNotification`,
  `SendInvitationEmailNotification`, `SendAutomationEmailNotification`).
- **Preserve** the `/{resource}/block/{id}` + `/{resource}/activate/{id}` route names.

### Admin

- `components/shared/admin-modules/status.tsx` badge → read `is_active` boolean.
- `data/status-types-select.tsx` → boolean options.
- Entity listings (filter/column/row-action) + forms `setValue('status', …)` (~14 entities) →
  `is_active`.
- Retype `status: string` → `is_active: boolean` in the ~12 interfaces.

### Frontend

None — confirmed zero `active`/`blocked` entity-status reads.

---

## Mobile contract

`/api/mobile/*` request/response JSON is **unaffected**: mobile speaker/sponsor resources don't
expose `status`; mobile already sends real booleans. This refactor only changes storage + internal
queries. Re-read `../../mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf` before touching any resource a
mobile endpoint returns, and update `Mobile*Controller` queries in the same pass.

## Order & gates

1. Track A: migrations → model casts → backend logic → admin → frontend.
2. Track B: audit → migrations/models → controllers → admin.
3. `php artisan migrate:fresh`.
4. Gates: backend `./vendor/bin/pint --dirty --test` + `php artisan test`; admin & frontend
   `yarn type-check` + `yarn production`.
