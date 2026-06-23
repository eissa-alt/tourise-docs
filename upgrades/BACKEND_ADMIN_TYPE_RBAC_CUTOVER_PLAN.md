# Backend `admins.type` → RBAC Cutover Plan

> **Type:** execution record · **Status:** ✅ executed 2026-06-23 — gate-green on `dev`,
> not pushed. `alt-backend` `38bacbc` · `alt-admin` `327e744`. **Track 1 complete.**
> **Track:** finishes **Track 1 (RBAC / `user.type` drop)** of
> [CYAN_FEATURE_PARITY_MASTER_PLAN.md](CYAN_FEATURE_PARITY_MASTER_PLAN.md).
> **Repos:** `alt-static-basecode-backend` (+ one tiny `alt-static-basecode-admin` cleanup).
> Working branch: `dev`.

> **Outcome:** all ~20 backend `$user->type` authz checks now resolve through
> `PermissionService` (Super short-circuits → prior super-only behavior preserved);
> `admins.type` dropped. Backend `php artisan test`: 452 passed, 3 pre-existing
> environment failures only (avatar-URL ×2 + `/`-route `ExampleTest`, all confirmed
> failing on the pristine baseline). Pint clean (`--dirty`). Admin `yarn type-check`
> + `yarn production` green.

## Why this exists

Track 1 retired `user.type` from the **admin frontend** (Bucket A + Bucket B). Bucket B
landed on `alt-admin` `25f4250` (collapse guest form-shape per-type field-sets; rename
`pif-*` → `default-*` shapes). The frontend is gate-green and type-free.

But the **backend was never migrated.** Enumerating readers before writing the column-drop
migration surfaced **~20 live admin-`type` authorization checks** outside the routes the RBAC
middleware gates. The type→role seed migration explicitly warned of this:

> *"In this increment only the roles + admins-management routes are gated … Confirm/adjust the
> map before gating the remaining routes."*
> — `2026_06_22_000002_add_role_id_to_admins_and_seed_roles.php`

**Consequence:** `admins.type` is **not redundant**. Dropping it now would null out guest
export/verify/row-action authorization. (These already silently degrade for role-only admins
whose `type` is `NULL`.) So the column drop is blocked behind this cutover.

## What de-risks it

- `PermissionService::can()` / `hasFeature()` **short-circuit `true` for `is_super`**. Every
  `type === 'super'` check becomes `can($admin, <feature>, <action>)` and Super still passes.
- Row-level data scoping (`GuestsController::applyAdminGuestAccessFilter`) keys off
  `category_ids` / `guest_status_ids` / `secondary_status_ids` — **not `type`**. Untouched by
  the drop.
- The RBAC catalog (`App\Support\AdminPermissions::CATALOG`) already has the needed actions:
  `guests_listing` → `view, export, see_more, edit, verify, accept, hold, reject, cancel,
  resend, send_sms, print, collect, send_e_badge, notify, send_issued_visa`.

## Inventory — every live admin-`type` read → mapping

| File · line | Current check | Proposed |
|---|---|---|
| `GuestsController:386` | `type === 'verify'` (restrict listing to *accepted*) | `can(…, 'guests_listing', 'verify')` |
| `:2440` `Export` (full) | `super \|\| community` | `can(…, 'guests_listing', 'export')` |
| `:2460` `ExportGuestAdminView` | `super \|\| guest \|\| invitation \|\| logistics` | `guests_listing.export` |
| `:2479` `ExportFilteredGuestAdminView` | `super \|\| guest` | `guests_listing.export` |
| `:2497` `ExportView` | `super \|\| guest` | `guests_listing.export` |
| `:2518` `ExportFiltered` | `super` | `guests_listing.export` |
| `:2538` `ExportFilteredView` | `super` | `guests_listing.export` |
| `:2557` `ExportAccommodationComments` | `super` | `guests_listing.export` |
| `:2577` `ExportFlightsComments` | `super` | `guests_listing.export` |
| `:2615` `ExportFlights` | `super` | `guests_listing.export` |
| `:2637` `ExportAccommodation` | `super` | `guests_listing.export` |
| `:2657` `ExportFlightsFiltered` | `super` | `guests_listing.export` |
| `:2677` `ExportAccommodationFiltered` | `super` | `guests_listing.export` |
| `:2698` `ExportFlightsCommentsFiltered` | `super` | `guests_listing.export` |
| `:2719` `ExportAccommodationCommentsFiltered` | `super` | `guests_listing.export` |
| `:3112` `guestStatusOther` | reads `$userType` but **never uses it** | delete the dead read |
| `:3464` `ExportCustomList` | `super \|\| community` | `guests_listing.export` |
| `:5439` `authorizeUser()` helper | `super` only (gates row-actions: `sendSMS`, …) | per-action `guests_listing.<action>` (map callers) |
| `HotelsController:217` `Export` | `super` | `hotels.export` |
| `CventOperationsController:267` | `super` only | `cvent_integration` feature (or super-only) |

**Excluded — not admin-`type`:** `GuestsController:1970` (`$request['type']` = guest field
lookup), `InvitationsController:321` (`$request->input('type')` request param),
`AdminWorkshopResource` / `AdminSessionsResource` / `Mobile*Resource` `'type' => $this->type`
(workshop/session **entity** type, not admin). The earlier kickoff TODO mislabeled the two
Admin*Resource files as emitting admin `type` — they do not; **no change needed there.**

## Decisions locked (2026-06-23)

| # | Decision | Choice |
|---|---|---|
| 1 | Gate-agent identity after the drop | **Permission-based** — `hasFeature($admin, 'gates')`. RBAC-consistent (Super also passes `loginAgent`, acceptable). |
| 2 | The ~12 currently **super-only** flight/accommodation exports | **Broaden** to `guests_listing.export` (any export-capable role; Super still passes). Accepted behavior change. |
| 3 | `community` / `verify` admins migrated to **empty-permission roles** (those types weren't in `TYPE_MODULE_MAP`) | **Skip the backfill (D1)** — fresh basecode, no real legacy admins to preserve. |

## Sequence (executed — each `P1.typedrop` on `dev`)

- **~~D1~~** ~~Data migration to backfill community/verify/logistics roles~~ — **dropped** per decision 3.
- **✅ D2 — Swapped guest authorization reads.** ~15 guest exports → `guests_listing.export`;
  `:386` verify-desk filter → `guests_listing.verify`; deleted the dead `:3112` `$userType`
  read; `authorizeUser()` callers (`pushToCvent`, `markCventAsAttended`) → `cvent_integration`
  (more accurate than `guests_listing` — both are Cvent pushes). `HotelsController` →
  `hotels.export`; `CventOperationsController` → `cvent_integration`.
- **✅ D3 — Gate identity.** `AuthController::loginAgent` + `AdminsController::selectList` →
  `hasFeature($admin, 'gates')`. Mobile contract checked (`docs/mobile/...html`): `loginAgent`
  is **not** in the documented mobile surface (that's OTP guest auth + guest-token QR); route +
  response shape unchanged, only the predicate. `routes/api.php` untouched.
- **✅ D4 — Stopped emitting/accepting `type`.** Removed from `AdminsResources`,
  `/get-profile`, `Admin::$fillable`, `AdminsController` store/update + `index` filter.
- **✅ D5 — Dropped the column.** `2026_06_23_000001_drop_type_from_admins_table.php`
  (`down()` restores nullable). Dropped `type` from `alt-admin/interfaces/admin.tsx` +
  `profile-details.tsx` (now shows role name).
- **✅ D6 — Verified.** Pint `--dirty` clean; `php artisan test` 452 pass / 3 pre-existing env
  failures; admin `yarn type-check` + `yarn production` green. Instead of new tests (avoiding
  recaptcha/external flake + over-scope), relied on the green suite + existing
  `Unit/Rbac/PermissionServiceTest` which covers `can`/`hasFeature` semantics.

> **Deviation from the original D2 note:** `authorizeUser()` mapped to `cvent_integration`
> (not `guests_listing`) because both its callers are Cvent push operations.
>
> **Pre-existing unrelated failures (not regressions, confirmed on pristine baseline):**
> `AttendeeTest`/`QrScannerTest` avatar-URL (need `PUBLIC_STORAGE_URL2` env) + `ExampleTest`
> `/`-route 403.

## Current state at scoping time

- `alt-admin` @ `25f4250` (Bucket B + rename, committed, gate-green).
- `alt-backend` **pristine** (no `type` changes committed or staged).
- This plan = the record. Code lands in `alt-static-basecode-backend` on `dev` per D2–D6.
