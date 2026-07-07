# Task 003 — Backend tooling & code-quality chain

- **Status:** `in-progress`
- **Opened:** 2026-07-07
- **Owner:** AI agent
- **Sub-app(s):** backend (+ docs)
- **Branch(es):** `dev`

## Goal

Bring `alt-static-basecode-backend`'s tooling/quality chain up to parity with the pass already done on
the two Next apps (Prettier 3 → Pint, ESLint/`tsc` → Larastan, husky+lint-staged → PHP-native hook,
0-warning gate). Do this **before** the heavy backend refactors (migration squash, `BaseApiController`,
response unification) so every refactor commit lands pre-formatted + statically checked instead of
dragging formatting churn through feature diffs.

Full plan (reviewed + scoped): [`../../upgrades/BACKEND_TOOLING_CHAIN_PLAN.md`](../../upgrades/BACKEND_TOOLING_CHAIN_PLAN.md).

## Scope

- **In:**
  - **W1** `pint.json` (preset `laravel` + `no_unused_imports` + `ordered_imports`) + one repo-wide
    Pint baseline (isolated commit) → flip the gate `pint --dirty` → `pint --test`.
  - **W2** Larastan level 4 + generated baseline, **committed ratchet to level 6** over the cleanup
    phase. Runs in `composer analyse`/`qa` — **NOT** in the pre-commit hook.
  - **W3** unused imports (falls out of W1; verify).
  - **W5** PHP-native pre-commit hook — Pint on staged `*.php`, via committed `.githooks/pre-commit` +
    `core.hooksPath` (zero new dep). Graceful-skip if `vendor/bin/pint` absent; `.gitattributes` exec-bit/LF.
  - **W6** composer QA scripts (`lint`/`lint:fix`/`analyse`/`test`/`qa`).
  - **W7** VS Code → Pint formatter for `[php]`; drop the leftover eslint code-action + irrelevant
    extension recs; add `open-southeners.laravel-pint`.
  - **W8** install/deploy warning cleanup (drop stale `pestphp/pest-plugin` allow-plugin;
    `composer validate --strict`; confirm `composer audit`).
- **Out (explicitly not this task):**
  - **W4 Rector** — moved to the cleanup plan as an optional one-off (behavior-changing rewriter, not a gate).
  - **W9 CI** — optional/out for now (neither Next app has CI).
  - Any CLEANUP_AND_HARDENING refactor (migration squash / BaseApiController / response unification) —
    separate tasks.

## Decisions (this task)

- **Larastan: in, with a committed ratchet to level 6** over the cleanup phase (not a rubber-stamp
  baseline). Record starting level + baseline error count below; each later cleanup task shrinks the
  baseline / bumps the level. **[user-approved 2026-07-07]**
- **W4 Rector removed** from the tooling chain → optional one-off in the cleanup plan. **[user-approved]**
- **Pre-commit hook = zero-dep committed `.githooks/pre-commit` + `core.hooksPath`** (Option A), not
  captainhook, not husky (no Node in a PHP repo). Pint-only in the hook (fast); PHPStan in `composer qa`.
- Commit style follows the repo's **conventional-commit** convention (as task 001/002 did — `chore:`/
  `refactor:`/`fix:`), not the `P<phase>.<task>` template.

## Ledger candidates (promote to `../../decisions/LEDGER.md`)

- **Gate flip `pint --dirty` → `pint --test`** (enabled by W1's clean baseline) — reverses the
  documented `--dirty` workaround in HANDOFF + CLAUDE.md. Needs a ledger entry, not just a HANDOFF line.

## Larastan ratchet tracker

| Date | Level | Baseline errors | Note |
|---|---|---|---|
| _(W2 lands)_ | 4 | _tbd_ | initial generated baseline |

## Known baseline facts (don't let W1/W2 get blamed for these)

- `php artisan test` ≈ **452 pass / 3 fail** — pre-existing, unrelated (ExampleTest `/`→403 + 2 avatar tests).
- Repo is **not** Pint-clean at baseline today → W1's whole point is to fix that.

## Log

Newest at the bottom. Date each entry.

- 2026-07-07 — opened; plan reviewed + scoped (Larastan kept with ratchet, Rector dropped, hook
  hardened). Starting with W1.

## Definition of Done

- [ ] W1 `pint.json` + repo-wide Pint baseline (isolated commit); gate flipped to `pint --test`
- [ ] W2 Larastan level 4 + baseline; `composer analyse` green; ratchet tracker seeded
- [ ] W5 pre-commit hook installed + verified (graceful-skip tested); `.gitattributes` entry
- [ ] W6 composer QA scripts; `composer qa` runs the full gate
- [ ] W7 VS Code aligned to Pint; W8 install/deploy warnings cleaned (`composer validate --strict`)
- [ ] Quality gate green (`pint --test` + `composer analyse` + `php artisan test`)
- [ ] Mobile contract: n/a (tooling only; `routes/api.php` untouched) — confirm no diff
- [ ] Docs: this TASK.md → `done`; tasks index row; **LEDGER** entry (gate flip); HANDOFF refresh;
      `../../process/SETUP_AND_UPDATE.md` documents the hook install + `composer qa`
