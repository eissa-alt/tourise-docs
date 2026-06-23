# Handoff — current state

> Rolling pointer, overwritten each session. For the durable record see the per-task `TASK.md`,
> `decisions/LEDGER.md`, and `upgrades/UPGRADE_SUMMARY.md`. Full plan: `upgrades/CYAN_FEATURE_PARITY_MASTER_PLAN.md`.

**2026-06-23 — Track 1 (RBAC / `user.type` drop) ~90% done. All work committed & gate-green on `dev`.**

This session removed every **mechanically-safe** `user.type` reader from the admin app:

- Exports gated by permissions: `export` action added to all export-bearing catalog features
  (`alt-backend` `60cc378`); `ExportActionArrayType.access[]` → `featureId`+`action`, gated via
  `checkPermission` across 3 export components + ~18 listings (`alt-admin` `f61b5f5`).
- `top-section` add/trash/custom → route-resolved `checkFeaturePermission`; `guests-form-edit` likewise.
- `admins-listing` → shows **role** (not entity `type`), `!admin.role?.is_super` guards (`5a4bbf4`).
- Admins **create/edit/filter** cut over to **role**: backend `store` `role_id` required / `type` nullable
  (`5e4786f`); `admins-form` dropped the type select (role select now required), `search-admins` filters by
  role (`740ed40`); deleted the orphaned legacy chooser chain + retired `utils/hasAccess.ts` (`d993de4`).
- Gates green throughout: `yarn type-check` + `yarn production`; `pint` + RBAC unit tests (10/10).
  NB: one **pre-existing, unrelated** `QrScannerTest` avatar-URL failure (verified failing before changes).

**BLOCKED — needs a product decision before Track 1 can finish (the `admins.type` column drop):**
`user.type` is now fully retired from the admin app **except Bucket B** — the `pif` / per-admin-type guest
**form-shape** variants: `guests/froms/{default/one-step, pif/one-step, pif/one-step-rsvp, pif/fours-steps}/
step-1.tsx` (`switch(user.type)`, different field sets per type) + the see-more panels
(`gusets-see-more-by-admin/by-admins/pif/**` + `see-more-admin.tsx`). No RBAC signal exists for `pif`
(migration never mapped it) and no permission maps to "show the badge field-set". **Decide:**
1. Is `pif` still needed in this basecode, or PIF-leftover to remove?
2. Should per-type field-sets collapse to ONE form driven by the guest's category/`form_shape`, or be re-keyed to roles?

Once Bucket B is resolved, the column drop also needs: `AdminsController@selectList` (gate-agents via
`type='gate'` → role), `AdminWorkshopResource` + `AdminSessionsResource` + `AdminsResources` (still emit
`type`), then the forward migration. Mobile contract already confirmed admin-`type`-safe.

**Track 2 (UI refactor) — not started.** Remaining deferred trio is large/supervised: sidebar-shell grouping,
listing-stack refactor (~42 listings), drop `react-select` (×23 multi-selects). Scope one with the user before coding.
