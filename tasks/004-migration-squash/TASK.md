# Task 004 — Migration squash (full wholesale rewrite)

- **Status:** `in-progress` (planning)
- **Opened:** 2026-07-08
- **Owner:** AI agent
- **Sub-app(s):** backend (+ docs)
- **Branch(es):** `dev`

## Goal

Collapse the accumulated migration history (**129 files = 71 `create_` + 58 alter-type**) into
**73 clean per-table `create_<table>` migrations**, each showing a table's **final** shape (post the
already-committed boolean + datetime refactors, tasks 001/002). Fewer files, no "add column later"
archaeology. Plus one final `_add_foreign_keys` migration holding all FK constraints.

Full plan: [`../../upgrades/CLEANUP_AND_HARDENING_MASTER_PLAN.md`](../../upgrades/CLEANUP_AND_HARDENING_MASTER_PLAN.md) (Task 003 there = this task).

## Why now (time-sensitive)

Fresh basecode, **no production data anywhere**; `migrate:fresh` is already the workflow. The bool +
datetime column-type refactors are already committed, so the current schema **is** the clean target.
**Squashing is safe ONLY while no clone carries prod data** — the moment a downstream project has prod
data, this is off the table (forward migrations only). Do it now.

## Scope

- **In:** rewrite `database/migrations/` → 73 `create_<table>_table.php` (final shape) + one
  `9999_..._add_foreign_keys.php`. Keep framework-default tables as their own standard migrations.
  Keep all 23 seeders green.
- **Out:** ANY route/resource/controller change. `git diff routes/api.php` MUST be empty — this is
  schema-only. No column-type changes (001/002 already did those; this only relocates them).

## Decisions (this task)

- **Full squash APPROVED** (Option 3) — user, 2026-07-07. Overrides the "never squash old migrations"
  convention **for this fresh basecode only**. → **LEDGER D11** (below).
- **FK strategy: separate final `_add_foreign_keys` migration** (user-approved 2026-07-08). Create all
  tables columns-only, then add every FK constraint in one order-independent final migration. Robust vs
  pivots / self-refs / polymorphic; no create-order topological sort needed.
- **`badge_category` → standalone `create_badge_category_table.php`** (user-approved 2026-07-08) — one
  table per create file; 72 create files total. FKs go in `_add_foreign_keys`.
- **Acceptance = the schema-diff gate** (user-approved 2026-07-08): empty `before.schema == after.schema`
  + `migrate:fresh --seed` green + `composer qa` green is the correctness proof; no manual 72-file read
  required. Agent reports the diff outcome + file summary.

## Verified current-state (2026-07-08, read-only)

- **129 migration files** → 71 `_create_` + 58 alters (`add/modify/drop/rename/change/convert/remove/update/make`).
- **73 distinct tables** in the live schema (901 columns total) — the target `create_` count (minus
  framework tables kept separate). Plan text said "~71"; actual is 73.
- **Snapshot/acceptance gate — CHANGED from the plan.** `mysqldump` is **not installed** and
  `php artisan schema:dump` fails without it. Gate uses a **PHP `information_schema` fingerprint**
  instead (script: `scratchpad/fingerprint.sh`): dumps `table|column|type|nullable|default|key|extra`
  sorted → diffable. Cleaner than a raw dump (no AUTO_INCREMENT/ordering noise). **Baseline captured**
  (`before.schema`, 901 lines).
- **Ledger number is D11** (plan said D9; D9/D10 already used).

## Acceptance gate (stronger than "seed green")

1. **`diff before.schema after.schema` EMPTY** — proves no drift in column type, nullability, default,
   key, or extra. Seed-green alone is necessary but NOT sufficient.
2. `php artisan migrate:fresh --seed` clean · all 23 seeders green.
3. `composer qa` green (`pint --test` + `phpstan analyse` + `php artisan test` = 452/3 pre-existing).
4. **`git diff routes/api.php` empty** (schema task must not touch routes).

## Target count — 72 tables (recon-confirmed)

**72 `Schema::create()` targets, not 71.** The hidden 72nd is **`badge_category`** — created by
`2025_12_31_175855_convert_badge_category_to_many_to_many.php` (a `convert_`-named file, so the naive
`grep create_` undercounts). Decision needed: standalone `create_badge_category` vs inline pivot (§Decisions).

## Framework tables — keep as standard migrations (do NOT fold)

Present: `users` (`2014_10_12_000000`), **`password_resets`** (legacy name — NOT `password_reset_tokens`),
`failed_jobs`, `personal_access_tokens`, `jobs` (filename has no timestamp — nonstandard). **ABSENT:**
`job_batches`, `cache`, framework `sessions`. These 5 use bigint `id()`. **No framework `sessions`
collision** — `create_sessions_table` here is a DOMAIN table (conference sessions); `session_interested_users`
is a domain pivot. Both fold. `users` is vestigial (real auth = `admins`/`guests`) — keep as-is.

## ⚠️ Columns that NET OUT (added then later `up()`-dropped — must NOT appear in final creates)

The #1 drift trap. Final create files must reflect NET shape:
- **guests:** `secondary_status_id` (added `2026_01_15`, dropped `2026_06_23_000002`); session-preference
  set `breakout_session_1/2`, `synergy_collaboration/opportunity/support/support_other` (added
  `2026_03_30`, dropped `2026_05_17_000001`). Also `guests.status` is **commented out in create, never
  added** — do NOT reintroduce it (some seeders reference it but are already broken — see seeders).
- **categories:** `badge_id` (dropped by the convert-to-pivot migration); `has_secondary_participation`,
  `primary_status_field` (added `2026_01_15_000002`, dropped `2026_06_23_000004`).
- **admins:** `type` (dropped `2026_06_23_000001`); `secondary_status_ids` (added `2026_01_20`, dropped `2026_06_23_000003`).
- **zones:** `color` (dropped `2025_11_09_183413`).
- **automation_setups:** `guest_status` (replaced by `guest_status_id`, `2025_12_10_164605`).
- **bulk_prints:** `photos_generated`, `photos_generate_success/failed/skipped` (dropped `2025_12_18_171408`).

## `->change()` mutations (final def must reflect the change, not replay it)

- `invitation_collections.email_template_id` — NOT NULL in create, made **nullable** by
  `2026_01_25_000001`. Final create must declare it `nullable()`.

## FK / relational hazards (recon-confirmed)

- **No polymorphic tables** (zero `morphs`). `*_type` columns are plain strings. Simplifies FKs.
- **All domain FKs are UUID** (`foreignUuid`/`uuid('id')`). Only 3 framework tables use bigint `id()`.
  Do NOT mix `foreignId`/`bigIncrements` into domain tables.
- **2 self-refs:** `guests.primary_guest_id→guests`, `categories.to_category_id→categories`.
- **9 pivots** (composite PK or unique): `badge_category`, `session_speaker`, `session_interested_users`,
  `workshop_speaker`, `workshop_registrations`, `chat_room_guest`, `meeting_room_categories`,
  `meeting_room_slot_guests`, `notification_recipients`.
- **Mixed FK styles to preserve** (do not normalize behavior away): older `foreignUuid()->references()->on()`
  (no cascade) vs newer `->constrained()->cascadeOnDelete()/nullOnDelete()`; `admins.role_id` uses raw
  `foreign()->references()->on('roles')->nullOnDelete()`. **Preserve each on-delete behavior.**
- Since we chose a **separate `_add_foreign_keys` migration**, all of the above go there — no create-order
  sort needed. (Self-refs could inline but go in the FK file too for uniformity.)

## Column-type edge cases (drift risks — the fingerprint gate catches these)

- **1 enum:** `session_media.type` = `enum('image','pdf')`.
- **json (many)** — keep as `json`, not `text`: categories `notification_settings`/`status_config`,
  admins `category_ids`/`guest_status_ids`, conferences `feature_labels`/`feature_icons`/`navigation`,
  roles `permissions`, meeting_rooms `available_dates`, `*_emails`/`guest_sms` `meta`, guests
  `edgex_education_levels`/`edgex_areas_of_interest`. (guests `synergy_support` json is dropped → not in final.)
- **No generated/computed columns.**
- **Non-default string lengths — do not let revert to 255:** flag strings `string(x,3)`
  (guests `terms`/`photo_consent`/`display_photo_in_app`/`will_attend`, admins `otp_to_login`);
  `(5)` time strings (flight times, room hours, slot times, `lang` on email/sms); `(2)` guests `lang`;
  wide `(2048)` media_videos `video_url`, `(512)` login_attempts `user_agent`, `(128)` admin_invites
  `token`, conferences `(500)` URLs / `(9)` colors; `(64)` tokens.
- **`unsignedInteger`/`unsignedSmallInteger` (NOT big, NOT FK):** jobs timestamps, invitations counters,
  workshops/sessions `duration`, meeting_rooms `capacity`/`slot_duration`, smtp_configs `port`,
  categories `number_of_extra_guests`.
- **Unique / composite indexes + composite PKs** — must be re-declared (full list in recon; incl. all
  pivot uniques/PKs, guests `email`/`registration_number`, admins `email`, etc.).
- **Boolean defaults per-column:** lookup tables `is_active default(true)`; guest/status flags
  `default(false)`. Do NOT blanket-default.
- **Timestamp `useCurrent()`:** `account_deletion_requests.created_at` (manual, no paired `updated_at` —
  don't auto-add), `failed_jobs.failed_at`.

## Seeder coupling (recon-confirmed)

- **`migrate:fresh --seed` runs only 8 seeders** (DatabaseSeeder): CountrySeederV2, AdminSeeder,
  GuestStatusSeeder, **CategorySeeder**, TitleSeeder, EmailConfigSeeder, EmailTemplatesSeeder, SMSTemplatesSeeder.
- **Only CategorySeeder is genuinely fragile:** needs `categories.form_shape`, `status_config` (json),
  `with_otp`, `guest_status_id` FK — all must survive the fold — AND named guest statuses
  (`accepted/invited/pending/rejected`) from GuestStatusSeeder. AdminSeeder needs `roles` + `admins.role_id`.
  EmailTemplatesSeeder touches only base cols (safe).
- **DO NOT "fix" GuestSeeder/GuestSeeder2** — they raw-`insert()` nonexistent `guests.status`/`days`/
  `employee_id_number` and are **already broken** against current schema; they're NOT in the seed path.
  Reintroducing dropped columns to appease them would corrupt the squash.
- **Keep `email_templates.editor_json_en/ar`** in the final create (MigrateEmailContentToEditorJsonSeeder
  backfills into them; not in run path but must still work via `--class=`).

## Log

- 2026-07-08 — opened (planning). Verified counts (129→73 tables), captured schema fingerprint baseline,
  proved the mysqldump-free acceptance gate, locked FK strategy (separate `_add_foreign_keys`).
  Recon agent inventorying per-table alter map + FK hazards + seeder coupling.

## Definition of Done

- [ ] 73 `create_<table>_table.php` (final shape) + `_add_foreign_keys.php` written; old alters removed
- [ ] `diff before.schema after.schema` EMPTY (no schema drift)
- [ ] `migrate:fresh --seed` clean; 23 seeders green
- [ ] `composer qa` green
- [ ] `git diff routes/api.php` empty (mobile contract untouched — schema only)
- [ ] Docs: this TASK.md → `done`; tasks index row; **LEDGER D11**; HANDOFF refresh
