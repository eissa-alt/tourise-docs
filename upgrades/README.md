# Upgrades & Migrations

Cross-cutting upgrade records, decision context, and **portable** playbooks/runbooks for the
directors "upgrade-then-clone baseline" initiative. These five docs are one tightly cross-linked
cluster — they reference each other by bare filename, so they live together here.

> **Reading order:** `BASELINE_DECISION` (why) → `UPGRADE_SUMMARY` (what we did + the SHA log) →
> the three how-to-replay recipes.

## Status

| Doc | Type | Status |
|---|---|---|
| [BASELINE_DECISION.md](BASELINE_DECISION.md) | decision record | ✅ locked — directors chosen as the clone baseline (2026-06-05). Ledgered as **D1** in [../decisions/LEDGER.md](../decisions/LEDGER.md). |
| [UPGRADE_SUMMARY.md](UPGRADE_SUMMARY.md) | execution log | ✅ Parts 1–5 merged to `dev` + pushed (all sub-apps). SHA source-of-truth. W1 rings complete. |
| [CYAN_BASECODE_MIGRATION_PLAYBOOK.md](CYAN_BASECODE_MIGRATION_PLAYBOOK.md) | reference (portable) | ♻️ how-to-replay the directors upgrades onto **cyan-basecode** (🔶 CYAN DELTA callouts). |
| [TAILWIND_V3_TO_V4_MIGRATION_RUNBOOK.md](TAILWIND_V3_TO_V4_MIGRATION_RUNBOOK.md) | reference (portable) | ♻️ engine-level Tailwind v3→v4 recipe for the ALT lineage. |
| [TAILWIND_V4_CLEANUP_PLAN.md](TAILWIND_V4_CLEANUP_PLAN.md) | open-work plan | 🅿️ W1 focus rings **done**; **W2** (drop `tailwind-bootstrap-grid`, ~2,200 sites) **parked**. |
| [DEPENDENCY_AUDIT.md](DEPENDENCY_AUDIT.md) | execution record | 🔒 2 CVEs patched (form-data ×3 + phpspreadsheet floor) on branches, gate-green, **not pushed**; 🧹 unused sweep = 0 removals (already clean); ✅ `zod` candidate investigated → load-bearing, kept. |
| [DEPENDENCY_HYGIENE_PLAYBOOK.md](DEPENDENCY_HYGIENE_PLAYBOOK.md) | reference (portable) | ♻️ audit → remove-unused → safe-bump → in-range-CVE recipe for the ALT lineage (Laravel 12 / 3 Next apps). |
| [COUNTDOWN_HOOK_REPLACEMENT_PLAYBOOK.md](COUNTDOWN_HOOK_REPLACEMENT_PLAYBOOK.md) | reference (portable) | ♻️ drop `reactjs-countdown-hook` (React 16 peer-dep warning) → local `useTimer` hook. ✅ done on alt (fe `17f3451` · la `d4dbd74`); 🔶 not yet ported to cyan. |
| [STORAGE_UPLOAD_URL_FIX_PLAYBOOK.md](STORAGE_UPLOAD_URL_FIX_PLAYBOOK.md) | reference (portable) | ♻️ fix admin upload-preview 404 — base64 `upload()` endpoints return the wrong URL (dropped folder segment + relative host from empty `APP_URL`). ✅ done on alt-backend `ff97c7b` (6 controllers); 🔶 re-scan per clone. |
| [STORAGE_URL_CONSOLIDATION_PLAN.md](STORAGE_URL_CONSOLIDATION_PLAN.md) | open-work plan | 🅿️ collapse redundant `*_STORAGE_URL*` vars → single source (backend `APP_URL`; admin one root var + `utils/storage.ts`; frontend none). Decided B3-full. Planning done, execution pending. |
| [ADMIN_RBAC_AND_GSSP_RESTRUCTURE_PLAN.md](ADMIN_RBAC_AND_GSSP_RESTRUCTURE_PLAN.md) | open-work plan | ✅ Track A done (drop `getServerSideProps` → client `TypeGate`, alt-admin `48ea141`, 132 files); 🅿️ Track B (cyan-parity roles/permissions RBAC, backend-first, ⚠️ `/get-profile` mobile-contract) = Track 1 of the master plan below. |
| [CYAN_FEATURE_PARITY_MASTER_PLAN.md](CYAN_FEATURE_PARITY_MASTER_PLAN.md) | open-work plan (orchestration) | 🅿️ planned — master sequencing for the cyan→alt feature/UI migration: **(1)** RBAC → **(2)** UI refactor (login/sidebar/listing-stack/forms/drop-react-select/modals) → **(3)** secondary-status removal → **(4)** DB-driven SMTP config. Decisions: RBAC-first, breaking mobile OK, no form-builder. No code yet. |
| [BACKEND_ADMIN_TYPE_RBAC_CUTOVER_PLAN.md](BACKEND_ADMIN_TYPE_RBAC_CUTOVER_PLAN.md) | execution record | ✅ executed 2026-06-23 — **Track 1 complete.** ~20 backend `$user->type` authz checks (`GuestsController`/`Hotels`/`Cvent`) migrated to `PermissionService`, gate-identity → `hasFeature('gates')`, `admins.type` dropped. Gate-green, not pushed: `alt-backend` `38bacbc` · `alt-admin` `327e744` (+ Bucket B `25f4250`). |

## Where the actual work lives

The *code* changes are committed in the four sub-app git repos (`*-backend / -admin / -frontend / -landing`)
on `dev`. This folder is the **record + recipe**, not the code. Exact merged commit SHA ranges per
sub-app are in `UPGRADE_SUMMARY.md`.

**Legend:** ✅ executed · ♻️ portable reference · 🅿️ parked / planned.
