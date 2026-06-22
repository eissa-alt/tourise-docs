# Cyan → Alt-Static Feature-Parity Master Plan

> **Status:** 🅿️ planned (orchestration doc) — no track-specific code written yet beyond the
> already-executed GSSP Track A. This is the **single sequencing record** for migrating the useful
> features + UI/UX improvements from `cyan-admin` / `cyan-backend` into the alt-static lineage.
>
> **Scope:** `alt-static-basecode-admin` + `alt-static-basecode-backend`. The `-frontend` / `-landing`
> apps are out of scope. **Reference (source of every pattern):**
> `/Users/admin/Projects/ALT/115-cyan-basecode/cyan-basecode-repos/{cyan-admin,cyan-backend}`.
>
> **Hard guardrail (CLAUDE.md #4):** do **NOT** port cyan's `DynamicFormRenderer` / dynamic
> form-builder / form-shapes. Alt keeps its older static form-shapes on purpose. The cyan `forms/` and
> `exports/` admin modules are therefore **out of scope** even though cyan has them.

---

## 0. Decisions locked this session (2026-06-22)

| # | Decision | Choice |
|---|---|---|
| D1 | **Sequencing** | **RBAC first** (backend → frontend, the spine) → **UI refactor** → **secondary-status removal + SMTP** last. |
| D2 | **Mobile contract** | **Breaking is acceptable** — drop `type` / `secondary_status` from API responses now; mobile catches up. Deltas are still documented per track (CLAUDE.md #4 — record what changed in `routes/api.php` / resources). |
| D3 | **This session's deliverable** | Explore cyan + write this plan. **No app code.** |
| D4 | **Form builder** | Excluded permanently (CLAUDE.md #4). Cyan `forms/` + `exports/` modules not ported. |

> Track A (drop `getServerSideProps` → client `TypeGate`) is **already executed** — committed
> `48ea141` on `alt-static-basecode-admin` `dev` (132 files, type-check green). `TypeGate` is a
> **transitional** layer that Track 1 (RBAC) replaces with `checkFeaturePermission`.
>
> **Track 1 (RBAC) executed 2026-06-22 — spine complete, gate-green, committed (local only):**
> backend `4094a7f`; admin `4851887` + `932923b` + `3125b57`. `TypeGate` is now RBAC-aware (infers
> feature from route → `checkFeaturePermission`; legacy `types` fallback for unmapped routes). All
> additive (legacy `type` kept). **Pending in Track 1:** guests 4-listing consolidation and a later
> cleanup migration to drop `type`.
>
> **Track 1 leftover done 2026-06-22 — sidebar `access[]→featureId`** (`alt-admin` `dev` `b252ba7`,
> gate-green): each active sidebar link carries a catalog `featureId`; `sidebar-content` gates via
> `checkFeaturePermission` (sub-menus keep only visible subLinks; the Mobile App section header shows
> only when a following link is visible). All featureIds verified vs `AdminPermissions::CATALOG`;
> `hasAccess` util retained for the non-sidebar `user.type` readers (removed by the type-drop).
>
> **Track 1 leftover — guests 4-listing consolidation: BLOCKED on a product decision (not mechanical).**
> The 4 per-type listings (`guests-super` 1198 ln, `guests-guest` 981, `guests-badge` 783, `guests-view`
> 617; ~3,579 total) already gate **row actions** via `checkActionPermission`, and `guests-super` is the
> action **superset** (14 actions vs guest 8 / badge 3 / view 0). BUT their **columns + filters are not
> permission-gated** — `guests-super` renders its full column/filter set unconditionally. Collapsing to
> one listing therefore needs **per-role column/filter visibility rules**, which the catalog does NOT
> define (catalog = actions only). Mechanical "use super for everyone" would over-expose columns/data to
> lesser roles. Needs: (a) a decision on per-role column/filter visibility, (b) runtime QA per role.
> Works correctly as-is today (page `TypeGate`-gated; each `user.type` gets its component).
>
> **Track 2 (UI refactor) partially executed 2026-06-22 — clean/low-risk sub-tracks done,
> gate-green, committed (local only on `alt-admin` `dev`):**
> - ✅ **ST1 — form primitives + tokens** (`b8e4596`): added `forms/ui-select/` (Headless Listbox),
>   `forms/checkbox-dropdown.tsx`, `forms/custom-switch-input-boolean.tsx`; aligned `custom-input`
>   + `.custom-input`/`.custom-input-sm` CSS to cyan. **No new deps, no new translation keys.**
>   Primitives are **additive — not yet wired into call sites.**
> - ✅ **ST2 — login + auth-wrapper** (`02a07a5`): cyan card layout, gradient bar, subtitle, re-enabled
>   forgot-password link (route exists in alt); added `web:login_subtitle` (EN+AR).
> - ✅ **ST6 — modals (safe subset)** (`c512e87`): slate backdrop; removed dead `print-modal copy.tsx`.
>   `ModalBody` card restyle **deferred** — alt modals supply their own inner card today, so cyan's
>   `bg-white border shadow-xl` would nest cards; do it with the listing-stack modal migration.
>
> **Track 2 NOT done (deliberately deferred — large / runtime-risky / judgment-heavy; need
> supervision):**
> - ⏭️ **ST5 — drop `react-select`:** react-select is fully encapsulated in the `forms/custom-select`
>   wrapper (only 2 direct importers; **76** wrapper call sites). The single-select wrapper-swap to
>   `ui-select` is trivial, **but 23 files use `isMulti`** and need migrating to `CheckboxDropdown`,
>   which has a **different contract** (`string[]` vs react-select `{value,label}[]`) → per-site state
>   changes + runtime QA (guest form steps highest-risk). A hybrid `isMulti` branch in the wrapper is
>   a **forbidden dual code path** (CLAUDE.md #3), so this must be a full per-site migration.
> - ⏭️ **ST3 — sidebar shell:** collapse/drawer mechanics are portable, but grouping is a design
>   decision (plan says **don't** copy cyan's 4-group map verbatim — redesign for alt's module set).
> - ⏭️ **ST4 — listing stack:** the multi-week long pole (~42 listings); prerequisite for Track 4 SMTP.
>
> **Next:** ST5 / ST3 / ST4 (each its own session). ST1's primitives are ready to consume.

---

## 1. Track map & dependency order

```
Track 1  RBAC (roles + dynamic permissions)        ← the spine; drops static type model
   │        backend-first, then frontend
   ▼
Track 2  UI/UX refactor                            ← login, sidebar, listing-stack, forms,
   │        (listing-stack unblocks SMTP listing)     drop react-select, modals
   ▼
Track 3  Secondary-status removal                  ← de-scoping; touches admins table that
   │        backend + admin                           Track 1 just rewrote (see §4.3 friction note)
   ▼
Track 4  Email SMTP config (DB-driven)             ← additive admin module; reuses Track 2 listing
            backend + admin                           stack + Track 1 `smtp_configs` feature gate
```

**Why this order:** RBAC is the capability backbone — sidebar filtering, guests consolidation, and
the SMTP feature gate all depend on it. The UI refactor's **listing stack** is a prerequisite for the
cyan SMTP listing UI, so doing UI before SMTP avoids building a throwaway table. Secondary-status
removal is independent but touches the `admins` table/profile that Track 1 reshapes, so it lands
after RBAC to avoid churn on the same files mid-flight.

---

## TRACK 1 — Admin RBAC (roles + dynamic permissions)

**Goal:** replace alt's static `type` model (`super`/`guest`/`view`/`badge`/`gate`/`invitation`/`logistics`)
with cyan-parity roles + a feature×action permission matrix, **server-enforced**. This is **Track B** of
[ADMIN_RBAC_AND_GSSP_RESTRUCTURE_PLAN.md](ADMIN_RBAC_AND_GSSP_RESTRUCTURE_PLAN.md) — that doc remains
the authoritative detail; this section records the verified inventory + the alt-specific deltas.

### 1.1 Backend (alt-static-basecode-backend) — do first

Port from `cyan-backend`:

| Deliverable | Cyan reference |
|---|---|
| `roles` table + `Role` model (`permissions` JSON, `is_super`, `name_en`/`name_ar`) | `database/migrations/2026_06_03_000003_create_roles_table.php`, `app/Models/Role.php` |
| `admins.role_id` FK + **data migration** | `2026_06_03_000004_add_role_id_to_admins_and_migrate.php` |
| Permission catalog (18 features) | `app/Support/AdminPermissions.php` |
| `PermissionService` (resolve matrix; super short-circuit) | `app/Services/PermissionService.php` |
| `EnsureAdminPermission` middleware (`admin.can:<feature>[,<action>]`) | `app/Http/Middleware/EnsureAdminPermission.php` + `Kernel.php` alias |
| `RolesController` + `RolesResources` | `app/Http/Controllers/RolesController.php`, `app/Http/Resources/Admin/RolesResources.php` |
| Roles routes (catalog, CRUD, select) | `routes/api.php` (roles block) |
| `AdminsController` / `AdminsResources` → `role_id` (drop `type`/`action_ids`/`dashboard_component_ids`) | cyan equivalents |
| `AuthController@profile` + login resource → emit `role` + `permissions{}` | cyan `AuthController` |
| RBAC unit tests | `tests/Unit/Rbac/*` |

**Alt is NOT a copy-paste of cyan — key deltas:**

1. **No server-side authz exists today.** Alt's ~200 admin routes are `auth:sanctum` only;
   `type` is a *filter*, never a gate. Adding `admin.can:` to every route is the **real security
   boundary** and the largest mechanical task. (Mobile-feature admin routes add only an identity
   check `auth.admin`, not feature gates.)
2. **Data migration differs.** Cyan builds permissions from a `feature_ids` array alt never had.
   Alt must map **`type` → feature matrix** (e.g. `logistics` → guests_listing+logistics features;
   `invitation` → invitations + partial guests; `gate` → gate/scan ops), then merge each admin's
   `action_ids` → `guests_listing` actions and `dashboard_component_ids` → `dashboard` actions.
3. **~25+ alt-only features need NEW catalog entries** (cyan's 18 don't cover them). Grouped:
   - *Conference/mobile CMS:* `event_days`, `conference`, `sessions`, `workshops`, `publications`,
     `media_center`, `notifications`, `meeting_rooms`, `account_deletion_requests`
   - *Agenda/landing:* `agenda`, `speakers`, `sponsors`, `speaker_labels`, `sponsor_labels`, `zones`
   - *Logistics/travel:* `hotels`, `traveling_status`, `e_visa`, `tiers`
   - *Gate ops:* `areas`, `gates`, `scans`, gate-agent login (`/admin/login-agent`)
   - *Reference:* `positions`
   - *Integrations:* `rg_integration`, `cvent_integration`
   - *Ops/logs:* `bulk_print`, `email_logs`, `operation_actions`, `queue_control` (+ reuse cyan `countries`)
   - *Extend existing:* `guests_listing` += `send_issued_visa`; `dashboard` += `secondary_overall`,
     `other_status`, `rg_status`, `gates` widgets
4. **Alt-only per-admin scope is retained, NOT folded into roles:** `category_ids`, `guest_status_ids`,
   `area_id`/`gate_id`. (`secondary_status_ids` is also here today but is **removed by Track 3** — see §4.3.)

### 1.2 Frontend (alt-static-basecode-admin) — after backend

Port from `cyan-admin`:

| Deliverable | Cyan reference |
|---|---|
| Roles module (CRUD + permission-matrix UI) | `pages/[lang]/roles/*`, `components/admin-modules/roles/*`, `interfaces/role.tsx` |
| Permission utils | `utils/checkFeaturePermission.ts`, `utils/checkActionPermission.ts`, `utils/inferFeatureId.ts` |
| Feature catalog (frontend mirror) | `data/admin-features.tsx` |
| Admins form → `role_id` dropdown (`GET /roles/select`) | `components/admin-modules/admins/admins-form.tsx` |
| Sidebar `featureId` + `checkFeaturePermission` filtering | `data/sidebar-links.tsx`, `components/sidebar/sidebar-content.tsx` |
| Guests consolidation: 4 per-type listings → 1 `guests-listing` + `checkActionPermission` row actions | `components/admin-modules/guests/guests-listing.tsx` |

**The cutover surface (everything reading `user.type` / static arrays today):**

- `components/shared/auth/type-gate.tsx` (gate by `user.type`) — swap to `checkFeaturePermission`.
- `utils/checkActionPermission.ts` — currently reads `user.action_ids`; **rewrite** to the RBAC matrix.
- `components/admin-modules/dashbaord/index.tsx` — reads `user.dashboard_component_ids`; → `checkPermission('dashboard', widgetId)`.
- `data/sidebar-links.tsx` — `access: ['super',…]` arrays → `featureId`.
- `pages/[lang]/guests/index.tsx` — `switch(user.type)` listing selector → single listing.
- ~90 `TypeGate` pages with static `types={[...]}` arrays.
- Many module components with `user.type === 'super'` row-action guards (admins, invitations, guest
  steps, see-more modal, print-modal, top-section, export-data). Full reader list in the RBAC
  frontend exploration report.
- Retire static data: `data/admins-types.tsx`, `data/admins-types-select.tsx`,
  `data/guest-actions-list.tsx`, `data/dashboard-components-list.tsx`, `utils/hasAccess.ts`.

### 1.3 Gates

- Backend: `composer audit` clean · `./vendor/bin/pint --test` · `php artisan test` · **`git diff routes/api.php` reviewed** (mobile contract — breaking allowed per D2, but document the `type`-drop on `/get-profile`).
- Admin: `rm -rf .next && yarn type-check && yarn production`; EN+AR for `perm_feature_*` / `perm_action_*` / `not_authorized`.

---

## TRACK 2 — UI/UX refactor

**Goal:** bring cyan's interface polish into alt-admin. **Exclude** form-builder, exports, and the
guests `filters-config-dialog`/`columns-config-dialog` (tied to cyan's forms + listing-preferences API).

### 2.1 Sub-tracks (recommended internal order)

1. **CSS tokens + form primitives** — port cyan `custom-input`, admin button tokens, `ui-select`
   (Headless Listbox, same `{value,label}` contract), `checkbox-dropdown` (multi-select),
   `custom-switch-input-boolean`. Unblocks login + react-select drop. *Effort: medium.*
2. **Login + `auth-wrapper`** — card layout, subtitle, login CSS, re-enable forgot-password only if
   the route exists in alt. Quick visible win. *Effort: low.*
3. **Sidebar shell** — collapse (`w-60`/`w-20`), grouped collapsible sections, mobile drawer overlay,
   `SideBarProvider` collapse state. **Keep alt's larger link inventory**; redesign grouping for
   alt's module set (don't copy cyan's 4-group map verbatim). *Effort: medium-high.*
4. **Listing stack** — port `hooks/use-listing-state.ts` + `interfaces/listing.ts` +
   `components/shared/listing/*` (ListingTable, ListingFilters, ListingFooter, RowActions,
   ViewMoreModal, ConfirmModal). Pilot on `admins`, then migrate the **~42 legacy listings**
   module-by-module. **Biggest effort in the whole plan** (weeks). Keep URL param names compatible
   with existing deep links. *Effort: high.*
5. **Drop `react-select`** — replace the `custom-select` wrapper's internals with `ui-select` /
   `checkbox-dropdown`; remove `react-select` + `@types/react-select` deps + dead
   `custom-select copy.tsx`. **Blast radius: ~83 active call sites** (37 `shared/select/*`, 14 filters,
   7 modals, 22 forms incl. 5 guest-step files) + 15 `*-multi*` files needing `isMulti` →
   `CheckboxDropdown` refactor. Guest form steps are highest-risk. *Effort: medium-high.*
6. **Modals** — restyle base `modals.tsx` body (border/shadow, slate backdrop); add listing
   `ViewMoreModal`/`ConfirmModal`; clean dead `print-modal copy.tsx`. Keep alt-only feature modals.
   *Effort: low.*

### 2.2 Risk notes

- Listing migration is the long pole; do it incrementally with `yarn type-check && yarn production`
  per module and verify pagination/filter deep-links per listing.
- react-select → Listbox changes typeahead/async behavior; visual QA in modals (z-index/portal).
- Date strategy is a product decision: cyan's `MaskedDateInput` (Cleave) vs alt's `custom-day-input`
  (react-day-picker modal). Default: keep alt's day-picker unless you want the masked UX.

---

## TRACK 3 — Secondary-status removal

**Goal:** remove the alt-only "secondary status" feature entirely (backend + admin). Breaking the
mobile contract is acceptable (D2), but every touch point is flagged.

### 3.1 Critical distinction: `status_config` ≠ secondary status

Both arrived in migration `2026_01_15_000002`, but:

| Piece | Action |
|---|---|
| `categories.status_config` JSON (primary `on_register`/`on_accept`/`on_reject` → `primary_status_id`) | **KEEP** — primary workflow stays |
| `status_config.*.secondary_status_id` keys | **STRIP** from schema/seeder/form/model |
| `categories.has_secondary_participation` | **DROP** column + UI |
| `categories.primary_status_field` | **DROP** column + UI (always use `guest_status_id`) |
| `guests.secondary_status_id` | **DROP** column |
| `admins.secondary_status_ids` | **DROP** column + UI |

### 3.2 Removal shape

- **Wholesale delete:** admin `components/admin-modules/dashbaord/secondary-over-all.tsx`; backend
  `DashboardStatsController::secondaryOverall()` + route `GET /admin/dashboard/guests/secondary-status`.
- **Surgical edits (backend):** `Guest`/`Category`/`Admin` models (relations, fillable, helper
  methods like `getActiveStatus`, `hasSecondaryParticipation`); `GuestsController` (with/filter/access-filter/register/accept/reject); `AdminsController`, `AuthController@profile`; `GuestsResources`, `AdminsResources`, `CategoriesResources`; `CategorySeeder`.
- **Surgical edits (admin):** `categories-form.tsx` (largest surface — secondary switch + pickers),
  `admins-form.tsx`/`admins-listing.tsx`, guest filters + listings (mostly already-commented dead
  plumbing), `see-more-admin.tsx` (chip still **live**), `interfaces/{guest,admin,category}.tsx`,
  `hooks/useGuestStatusesSelect.ts`, `data/dashboard-components-list.tsx`, EN+AR translation keys.
- **DB:** new **forward** drop-column migrations (never edit old migrations); optional data
  migration to copy `secondary_status_id` → `guest_status_id` where a category used
  `primary_status_field = 'secondary_status_id'`; clean `'secondary_overall'` from stored
  `dashboard_component_ids`.

### 3.3 Ordering friction with Track 1

`admins.secondary_status_ids` + the profile/resource fields are touched by **both** Track 1 (RBAC
reshapes `admins`/profile) and Track 3 (drops the column). Since RBAC lands first, RBAC should
**retain** `secondary_status_ids` as per-admin scope, and Track 3 then drops it. Accept the
double-touch, or fold the column drop into the RBAC data migration if both are in flight together.

### 3.4 Open confirmations (from removal report §5)

- Keep primary `status_config` workflow (not revert to legacy `guest_status_id`-only)? *(assumed yes)*
- `active_status_id` on admin guest API → drop or alias to `guest_status_id`?
- RBAC access change: admins with **only** `secondary_status_ids` set today can see guests — migrate
  or accept breakage?
- Production data with populated secondary status → run the data migration in §3.2?

---

## TRACK 4 — Email SMTP config (DB-driven)

**Goal:** add cyan's DB-driven SMTP module. **Important:** this is **additive** — it does NOT replace
alt's existing `/emails/config` screen (that's email **branding**, not transport). Alt's SMTP is
`.env`/`config/mail.php` only today; cyan adds runtime-overridable DB configs.

### 4.1 Backend

Port: `smtp_configs` migration, `SMTPConfig` model (**`password` encrypted cast**, hidden),
`DynamicSmtpService` (runtime `Config::set` of a `dynamic_smtp` mailer; falls back to `.env` when no
active default), `SMTPConfigController` + `SMTPConfigResource` + `SMTPConfigsExport`, and the
`/admin/smtp-configs/*` routes (CRUD + `send-test-email` + `toggle-active` + `make-default` + `clone`
+ `check-default`).

**Wire `DynamicSmtpService::applyDefaultIfAvailable()` before every send path:** `AuthController`
(OTP/alerts/reset), `MobileAuthController` (guest OTP), all four notification classes
(`SendGuestEmail`, `SendInvitationEmail`, `SendAutomationEmail`, `GuestOtp`), and ideally
`EmailsTemplatesController::sendTest`.

**Dependency:** cyan's controller extends `BaseApiController` + `ApiResponse`/`AppliesListingFilters`
traits alt lacks — either port those or rewrite responses to alt's existing `{status,data}` shape.

### 4.2 Frontend

Port `pages/[lang]/emails/smtp-configs/{index,create,edit/[id]}.tsx` +
`components/admin-modules/smtp/*` (form, listing, send-test modal, delete modal) +
`interfaces/smtp-config.ts`; add the sidebar entry; copy SMTP translation keys **(EN+AR same commit)**.
**The cyan SMTP listing depends on the Track 2 listing stack** — another reason SMTP follows the UI
refactor. Gate with the Track 1 `smtp_configs` feature (interim `TypeGate types={['super']}` if SMTP
somehow precedes RBAC).

### 4.3 Notes

- Mobile contract: **no mobile-facing routes added** (admin-only). Behavioral change only — guest OTP
  starts using the DB default SMTP once wired. Note in release notes.
- `APP_KEY` stability required (encrypted passwords). Queue workers need DB access + `APP_KEY`.
- Optional separate sub-task: align alt's branding `emails-config` `with_*` columns from `string(3)`
  → `boolean` and adopt cyan's `CustomSwitchInputBoolean` UX. Not required for the SMTP port.

---

## Quality gates (every push, all tracks)

- **Backend:** `composer audit` clean · `./vendor/bin/pint --test` · `php artisan test` ·
  `routes/api.php` reviewed vs mobile contract (document breaking deltas per D2).
- **Admin:** `rm -rf .next && yarn type-check && yarn production`; EN+AR visual QA.
- **Commits:** branch off `dev`; EN+AR same commit; manifests only (locks gitignored);
  `P<phase>.<task>` or the repo's conventional-commit style; no `console.log`/`dd()`/`dump()`.

## Cross-references

- [ADMIN_RBAC_AND_GSSP_RESTRUCTURE_PLAN.md](ADMIN_RBAC_AND_GSSP_RESTRUCTURE_PLAN.md) — authoritative
  Track 1 (RBAC) detail; Track A (GSSP) already executed (`alt-admin` `48ea141`).
- [CYAN_BASECODE_MIGRATION_PLAYBOOK.md](CYAN_BASECODE_MIGRATION_PLAYBOOK.md) — house style for
  cyan-targeted replay docs.
- `../ai/ARCHITECTURE_NOTES.md` — the form-shapes "keep the older pattern" rule (no `DynamicFormRenderer`).
- Mobile contract: `../mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf`.

## Exploration provenance (verified 2026-06-22)

Inventories backing this plan were produced by five read-only codebase explorations: RBAC backend,
RBAC frontend, UI refactor, email/SMTP, and secondary-status removal. Re-verify counts (~200 ungated
admin routes, ~42 legacy listings, ~83 react-select call sites, ~90 `TypeGate` pages) against the live
repos before trusting a number in implementation.
