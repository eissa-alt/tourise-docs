# Handoff — current state

> Rolling pointer, overwritten each session. For the durable record see the per-task `TASK.md`,
> `decisions/LEDGER.md`, and `upgrades/UPGRADE_SUMMARY.md`. Full plan: `upgrades/CYAN_FEATURE_PARITY_MASTER_PLAN.md`.

**2026-06-23 — Track 1 COMPLETE + Track 2 (UI refactor) ST5/ST3/ST4-foundation landed.
Gate-green on `dev`, not pushed.**

Track 1 (RBAC / `user.type` drop) is complete: `user.type` is gone from admin + backend,
`admins.type` dropped, all authz is role/permission driven via `App\Services\PermissionService`.
Track 2 this session: dropped `react-select` (ST5), added the desktop-collapse + mobile-drawer
sidebar shell (ST3), and ported the reusable listing stack as additive infra (ST4 foundation).

## Current SHAs (committed on `dev`, not pushed)

- `alt-admin` @ `e8031b3` (ST4 listing-stack port) — also `d3dc88f` (ST3 sidebar),
  `c37103d` (ST5 react-select drop), `327e744` (T1 type-drop), `25f4250` (T1 Bucket B).
- `alt-backend` @ `38bacbc` (backend type→RBAC cutover + drop migration).
- `docs` (on `main`): cutover plan + master-plan status + README + this handoff.

## What landed this session

- **Bucket B + form-shapes** (`alt-admin` `25f4250`): collapsed the 4 `switch(user.type)` guest
  registration step-1 forms + see-more panels into single `form_shape`-driven field-sets;
  un-gated email-history tab; renamed `pif-four-steps`→`default-four-steps`,
  `pif-one-step-rsvp`→`default-one-step-rsvp` (`pif-one-step` kept).
- **Backend cutover** (`alt-backend` `38bacbc`): ~15 guest exports → `guests_listing.export`;
  verify-desk filter → `guests_listing.verify`; `authorizeUser()` (Cvent pushes) →
  `cvent_integration`; `HotelsController` → `hotels.export`; `Cvent` → `cvent_integration`;
  `loginAgent` + `selectList` gate-identity → `hasFeature('gates')`; stopped emitting/accepting
  `type` (`AdminsResources`, `/get-profile`, `$fillable`, store/update/index); **dropped
  `admins.type`** (migration `2026_06_23_000001`, reversible). Factory/seeder/15 feature tests
  cut from `type=super` to role-based. Super short-circuits everywhere, so prior behavior holds.
- **Admin frontend** (`alt-admin` `327e744`): dropped `type` from `interfaces/admin.tsx`;
  `profile-details.tsx` shows role name (EN/AR) instead of `type`.

## Gates

- Backend: Pint `--dirty` clean; `php artisan test` = **452 pass / 3 pre-existing env failures**
  (`AttendeeTest`+`QrScannerTest` avatar-URL need `PUBLIC_STORAGE_URL2`; `ExampleTest` `/`→403)
  — all confirmed failing on the pristine baseline, not regressions.
- Admin: `yarn type-check` + `yarn production` green.
- Mobile contract unaffected (`loginAgent` route + response shape unchanged; not in the mobile
  surface). Note: `loginAgent` returns `AdminsResources`, so the gate-scanner login response no
  longer includes `type` — flag for any external scanner app that read it.

## Track 2 (UI refactor) — progress this session (all gate-green, committed on `dev`)

- **ST5 — drop `react-select`** (`c37103d`): `CustomSelect` single-select wrapper now re-exports the
  Headless `ui-select` primitive (same `{value,label}` contract). The 11 multi-select components
  (`*-select-multi` + `admins-select` dual) now use `CheckboxDropdown` internally while preserving
  their external `callBack(options[])` contract — so **consuming forms are untouched**. Converted the
  one bare `isMulti CustomSelect` (titles `allowed_genders`). Removed `react-select` +
  `@types/react-select` deps and dead `custom-select copy.tsx` / `css/react-select.tsx`.
- **ST3 — sidebar shell** (`d3dc88f`): `SideBarProvider` gains persisted `isCollapsed/toggleCollapsed`
  (localStorage); desktop animates `w-60`↔`w-20` (icon-only) with collapsed submenus as portaled
  Headless `anchor` flyouts; mobile drawer gains a click-to-dismiss backdrop + auto-close on nav.
  Existing section grouping + RBAC `featureId` filtering kept intact.
- **ST4 — listing stack (FOUNDATION only)** (`e8031b3`): ported `interfaces/listing.ts`,
  `hooks/use-listing-state.ts`, and `components/shared/listing/*` (ListingTable, ListingFilters,
  ListingFooter, RowActions, ViewMoreModal, ConfirmModal) from cyan. **Additive — not wired to any
  live listing**, so the ~42 working listings are untouched. alt's `{data, meta}` paginated API
  already matches the hook's contract (verified against `admins`).

> ⚠️ Runtime-QA caveat: ST5 multi-select + the sidebar collapse/RTL flyouts compile + build green
> but were not browser-tested this session (user away). Smoke-test guest-form multi-selects, the
> admins guest-access multis, and the collapsed-sidebar submenu flyouts (LTR + RTL) before pushing.

## Next: Track 2 remaining

- **ST4 per-listing migration** — the multi-week long pole: pilot `use-listing-state` + the listing
  components on the `admins` listing, then migrate the ~42 legacy listings module-by-module (keep URL
  param names compatible). Prerequisite for Track 4 SMTP. Needs supervision + runtime QA.
- **ST3 accordion grouping** (deferred) — collapsible section *groups* are a design decision; the flat
  `isSection` grouping was kept deliberately. Redesign with the user before coding.

> Pint note: the backend repo is not Pint-clean at baseline; use `pint --dirty` (formats only
> changed files), never a repo-wide `pint` run (would churn 300+ unrelated files).
