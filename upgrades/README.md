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

## Where the actual work lives

The *code* changes are committed in the four sub-app git repos (`*-backend / -admin / -frontend / -landing`)
on `dev`. This folder is the **record + recipe**, not the code. Exact merged commit SHA ranges per
sub-app are in `UPGRADE_SUMMARY.md`.

**Legend:** ✅ executed · ♻️ portable reference · 🅿️ parked / planned.
