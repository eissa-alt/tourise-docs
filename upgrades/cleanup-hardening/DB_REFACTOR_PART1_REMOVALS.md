# Database Refactor — Part 1: Dead / Vestigial Removals

Remove confirmed-dead tables, columns, and their end-to-end logic (backend + admin + frontend)
**before** the migration fold (Part 2). Removing this first shrinks the set Part 2 has to fold:
`zones`, `bulk_prints`, `guest_utms`, and the edgex columns stop being "fold" candidates and become
plain deletes.

This supersedes the parked, **dropped** wholesale squash (old Tasks 003/004) — see
[CLEANUP_AND_HARDENING_MASTER_PLAN.md](CLEANUP_AND_HARDENING_MASTER_PLAN.md). The fold formula lives in
[DB_REFACTOR_PART2_FOLD.md](DB_REFACTOR_PART2_FOLD.md).

**Approach.** Edit the original `create_*` migrations in place (drop columns from the initial `create`,
delete now-obsolete `add_*`/`modify_*`/`create_*` files), then `php artisan migrate:fresh --seed`. This
baseline carries no production data. Each item below lists its full footprint — remove the whole chain,
not just the column.

---

## Sequencing & dependencies

- **Runs before Part 2 (the fold).** Decided.
- **Task-008 (guest-drafts) coordination — noted, not sequenced.** The backend working tree currently
  has uncommitted guest-drafts WIP that adds a migration and edits `routes/api.php`. Part 1 also edits
  migrations and `routes/api.php`. Land/branch order to be decided at execution time; do not run Part 1
  on top of a dirty tree without a plan for the overlap.
- Work on `dev`. Commit format `P<phase>.<task> — <short imperative>`.

## Baked-in gates (apply to every item)

1. **Step 0 — prove the baseline is green.** `php artisan migrate:fresh --seed` must succeed on the
   current tree *before* any edit (HANDOFF D13 claims the old `TitleSeeder` break is fixed — re-prove
   it), so our diff is attributable. This wipes the dev DB (including any guest-draft you were testing).
2. **`routes/api.php` changes are admin/web-only.** Part 1 removes `GET /landing-page`, the public
   `GET /speakers`, and the `/admin/zones*` + `/admin/bulk-print*` groups. **No mobile-facing endpoint
   is touched.** Re-read `../../mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf` and confirm the mobile
   block in `routes/api.php` is byte-identical after the change.
3. **EN + AR translation keys removed in the same commit.** No exceptions.
4. **Three-repo coordination.** Several items span backend + admin + frontend; keep the removal atomic
   per item across repos.
5. **Name-collision guards (stay surgical):**
   - `cat_list` also exists on `titles` — **keep** the titles one; only remove `countries.cat_list`.
   - `countries.guest_status` (a free string) is unrelated to `guest_status_id` / the `guest_statuses`
     table / `GuestStatus` model — **keep** all of those; only remove the countries string column.
6. **Final gates:** `composer qa` (pint --test + phpstan + test) green; admin & frontend
   `yarn type-check` + `yarn production` green; `migrate:fresh --seed` clean.

---

## 1. Countries vestigial fields — `override_registration_status`, `cat_list`, `guest_status`

Write-only in admin CRUD, never read in any runtime flow. Not mobile-facing.

- **Backend:** `database/migrations/2023_03_16_165738_create_countries_table.php` — drop the three
  column definitions. `app/Models/Country.php` — remove from `$fillable`/`$casts`. `CountriesController`
  — drop from validation + `create`/`update` assignment. `app/Http/Resources/**/CountriesResources.php`
  — drop the emitted keys. Check `CountrySeeder` for any references.
- **Admin:** countries form + interface (`interfaces/country.tsx`) — remove the three inputs/fields;
  any `defaultValues` entries.
- **Frontend:** verify the public country select (`countries-select` / `cont-list`) does not read them
  (expected: id/name only) — no change if so.
- **Note:** `override_registration_status` is also listed in the Boolean Refactor plan; if that runs
  first the column may already be boolean — remove it regardless.

## 2. `guest_utms` table (dead — no model, zero references)

- **Backend:** delete `database/migrations/2025_03_26_145439_create_guest_utms_table.php`. Confirm no
  model, controller, resource, seeder, or `DB::table('guest_utms')` reference exists (verified: none).

## 3. Landing-page backend layer (frontend landing is commented-out; not in mobile contract)

Removes only the backend landing surface. **`speakers`, `sponsors`, `sponsor_labels`, `speaker_labels`
tables are KEPT** (mobile-facing / low-cost admin categorization).

- **Backend:** delete `app/Http/Controllers/LandingPageController.php`,
  `app/Http/Resources/LandingPageSpeakerResource.php`, `app/Http/Resources/LandingPageZoneResource.php`.
  `routes/api.php` — remove `GET /landing-page`, the public `GET /speakers`, and the
  `LandingPageController` import.
- **Verify:** the admin speakers/sponsors CRUD controllers + their admin resources remain untouched
  (they are separate from the landing resources).

## 4. `zones` table (orphaned admin module — no incoming FK, landing consumer now dead, not mobile)

- **Backend:** delete migrations `2025_11_09_183412_create_zones_table.php` and
  `2025_11_09_183413_remove_color_from_zones_table.php`; `app/Models/Zone.php`;
  `app/Http/Controllers/ZonesController.php`; `app/Http/Resources/Admin/ZonesResources.php`; the 8
  `/admin/zones*` routes; `database/seeders/ZoneSeeder.php` (and its `DatabaseSeeder` call); the `zones`
  entry in `app/Support/AdminPermissions.php`.
- **Admin:** `pages/[lang]/landing-page/zones/{index,create,edit/[id]}.tsx`;
  `components/admin-modules/zones/{zones-listing,zones-form}.tsx`; `interfaces/zone.tsx`; the `zones`
  entries in `data/module-icons.tsx` and `data/sidebar-links.tsx` (sidebar already commented); the zones
  permission in `components/admin-modules/roles/roles-form.tsx`; the zones branch in
  `components/shared/modals/table-actions-modal.tsx`; `zones*` keys in `translations/{en,ar}/web.json`.

## 5. `bulk_prints` table (standalone admin module — no incoming FK; user will re-add cleaner later)

- **Backend:** delete `create_bulk_prints` + `modify_bulk_prints` migrations; `app/Models/BulkPrint.php`;
  `BulkPrintController.php`; `app/Http/Resources/Admin/BulkPrintResources.php`; the ~13
  `/admin/bulk-print*` routes; the `bulk-print` entry in `app/Support/AdminPermissions.php`. Confirm no
  export/PDF/badge-log path references it (verified: none).
- **Admin:** `pages/[lang]/bulk-print/{index,create,edit/[id]}.tsx`;
  `components/admin-modules/bulk-print/{bulk-print-form,bulk-print-listing}.tsx`;
  `interfaces/bulk-print.tsx`; entries in `data/module-icons.tsx`, `utils/inferFeatureId.ts`,
  `data/sidebar-links.tsx`; the permission in `components/admin-modules/roles/roles-form.tsx`;
  `bulk-print*` keys in `translations/{en,ar}`.

## 6. EdgeX guest fields (dead orphans — columns exist but not in the `Guest` model, no reader anywhere)

- **Backend:** delete `database/migrations/2026_01_05_140552_add_edgex_fields_to_guests_table.php`. Not
  in `Guest` `$fillable`/`$casts`, no controller/resource/export touches them (verified).
- **Frontend + Admin:** remove orphaned `edgex_*` / `participation_type_edgex` keys from
  `{en,ar}/web.json` in **both** apps; remove the stale edgex line in `FORM_RESTRUCTURE_GUIDE.md`.

## 7. Adjacent dead code (small, bundled in this pass)

- **Phantom `guests.status`:** remove the commented `// $table->string('status', 50)...` line from
  `2023_08_19_171536_create_guests_table.php` (column is not created; the line is archaeology).
- **Broken guest seeders:** `database/seeders/GuestSeeder.php` and `GuestSeeder2.php` reference
  nonexistent columns (`status`, `days`, `employee_id_number`) and would fail if enabled. Remove them
  (and any `DatabaseSeeder` calls) or fix to the current schema — remove is preferred as they are dead.
- **Dead `EmailContent` model:** delete `app/Models/EmailContent.php` — zero references, no backing
  table.

---

## Safe table reordering (FK-ordering prep for Part 2)

Reorder (rename the timestamp prefix of) these `create_` migrations so each referenced **lookup** table
is created **before** its dependents. This lets Part 2 inline `foreignId()->constrained()` instead of
deferring the constraint, collapsing ~7 late `change_*`/`add_*` FK migrations. All five are pure lookups
with **no outgoing FK**, so moving them earlier cannot create a new violation.

| Move this `create_` earlier | To before | Unlocks inlining of |
|---|---|---|
| `guest_statuses` (`2025_12_03_141742`) | `categories` (`2023_03_17`), `guests` (`2023_08_19`), `automation_setups` (`2024_05_17`) | `guest_status_id` FK on 3 tables (via 3 `change_*` migrations) |
| `areas` (`2025_12_21_103859`) | `admins` (`2023_03_17`), `gates` (`2025_08_22`) | `area_id` FK on admins + gates |
| `roles` (`2026_06_22_000001`) | `admins` (`2023_03_17`) | `admins.role_id` FK |
| `speaker_labels` (`2025_11_09_183410`) | `speakers` (`2025_11_09_183408`) | `speakers.speaker_label_id` FK |
| `sponsor_labels` (`2025_11_20_135241`) | `sponsors` (`2025_11_09_183409`) | `sponsors.sponsor_label_id` FK |

**Cannot reorder — genuine cycle:** `admins` ↔ `gates` (`create_gates` references `admins.related_agent`
while `admins.gate_id` references `gates`). Keep `gates.related_agent` inline (gates after admins) and let
**Part 2** add `admins.gate_id`'s constraint in the final `…_add_foreign_keys` step. Flag, don't reorder.

**Notes.** Reordering is timestamp-prefix renames only — schema-neutral on `migrate:fresh` (no prod data);
Part 2's empty-SQL-diff gate still proves zero drift. Do it **after** the removals above (fewer files to
shuffle — `zones`/`bulk_prints`/`guest_utms` are already gone). `speaker_labels`/`sponsor_labels` are
**kept** (§3), so their reorder is in scope. This is prep only — the actual FK inlining lands in Part 2.

## Handled by Part 2 (net-out columns — "never create", not removed here)

These were added then later dropped; the fold simply never creates them (their `add_*` and `drop_*`
files both disappear). Listed here for traceability only — **do not** write separate drops in Part 1:

- `guests.secondary_status_id` (add `2026_01_15_000001` / drop `2026_06_23_000002`)
- `admins.secondary_status_ids` (drop `2026_06_23_000003`)
- guest session-preferences fields (add `2026_03_30_120000` / drop `2026_05_17_000001`)
- `guests.synergy_opportunity` — **decide in Part 2** whether it is a true net-out or still live
- categories secondary columns — `has_secondary_participation` / `primary_status_field`
  (drop `2026_06_23_000004`)
- The `secondary_status_ids` line inside `2026_01_20_000001_add_guest_access_fields_to_admins_table.php`

**Kept (explicitly NOT removed):** `speakers`, `sponsors`, `sponsor_labels`, `speaker_labels`,
`categories.status_config` (load-bearing — hard-required by `GuestsController`).

## Execution order

1. Step 0 baseline seed green.
2. Backend removals per item (migrations → models → controllers/resources → routes → seeders →
   `AdminPermissions`), then `migrate:fresh --seed`.
3. Admin removals per item (pages → components → interfaces → data → roles/permissions → translations).
4. Frontend/translation removals.
5. Safe table reordering (rename the 5 lookup `create_` prefixes; leave the `admins`↔`gates` cycle).
6. Gates (§6 above) + confirm `migrate:fresh --seed` still green after the reorder. Then proceed to Part 2.
