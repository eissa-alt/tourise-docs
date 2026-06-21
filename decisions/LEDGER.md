# Decision Ledger

Append-only record of **durable, cross-task locked decisions** for alt-static-basecode. Numbered
`D1…Dn`, never renumbered. A task-local choice lives in that task's `TASK.md`; a decision that
outlives the task gets promoted here. This is the source of truth when a decision and the code/docs disagree.

> Format: `D<n> — <date> — <one-line decision>` + a short why + where the detail lives.

---

## D1 — 2026-06-21 — cloned from pif-directors-gathering baseline

`alt-static-basecode` was cloned from the `pif-directors-gathering` upgrade-then-clone baseline
(source SHAs: backend `8745150` · admin `0f65026` · frontend `5e3fee2` · landing `55fd6b7` · docs `3cbca75`).
Inherited stack: **Next 15 / React 18.3.1 / Headless UI v2 / Tailwind v4 / Laravel 12** (Sentry removed,
OWASP-hardened). The frozen lineage record under `../upgrades/` documents what this baseline already includes.

- **What the baseline already includes:** [../upgrades/UPGRADE_SUMMARY.md](../upgrades/UPGRADE_SUMMARY.md)
- **Why directors was the chosen baseline:** [../upgrades/BASELINE_DECISION.md](../upgrades/BASELINE_DECISION.md)
