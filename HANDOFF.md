# Handoff — current state

> Rolling pointer, overwritten each session. For the durable record see the per-task `TASK.md`,
> `decisions/LEDGER.md`, and `upgrades/UPGRADE_SUMMARY.md`. Full plan: `upgrades/CYAN_FEATURE_PARITY_MASTER_PLAN.md`.

**2026-06-23 — Track 1 (RBAC / `user.type` drop) COMPLETE. Gate-green on `dev`, not pushed.**

`user.type` is fully gone from both the admin app and the backend. `admins.type` column dropped.
All admin authorization is role/permission driven via `App\Services\PermissionService`.

## Current SHAs (committed on `dev`, not pushed)

- `alt-admin` @ `327e744` (type-drop: interface + profile) — also `25f4250` (Bucket B + rename).
- `alt-backend` @ `38bacbc` (backend type→RBAC cutover + drop migration).
- `docs` (on `main`): cutover plan + README + this handoff.

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

## Next: Track 2 (UI refactor) — not started

Deferred trio is large/supervised: sidebar-shell grouping, listing-stack refactor (~42 listings),
drop `react-select` (×23 multi-selects). Scope one with the user before coding.

> Pint note: the backend repo is not Pint-clean at baseline; use `pint --dirty` (formats only
> changed files), never a repo-wide `pint` run (would churn 300+ unrelated files).
