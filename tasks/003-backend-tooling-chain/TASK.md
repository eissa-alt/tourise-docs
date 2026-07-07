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
| 2026-07-08 | 0 | 124 (71 grouped entries) | initial baseline post-clone; 1 non-ignorable error fixed at source, not baselined. Goal: shrink 124→0, then bump L0→L1→… |

## Known baseline facts (don't let W1/W2 get blamed for these)

- `php artisan test` ≈ **452 pass / 3 fail** — pre-existing, unrelated (ExampleTest `/`→403 + 2 avatar tests).
- Repo is **not** Pint-clean at baseline today → W1's whole point is to fix that.

## Log

Newest at the bottom. Date each entry.

- 2026-07-07 — opened; plan reviewed + scoped (Larastan kept with ratchet, Rector dropped, hook
  hardened). Starting with W1.
- 2026-07-07 — **W1 done + committed** (backend `96413df`). Added `pint.json` (laravel preset +
  `no_unused_imports` + `ordered_imports`); one repo-wide Pint format = **172 files** (all cosmetic
  fixers; **34** genuinely-unused imports removed). `pint --test` now **passes** (repo Pint-clean →
  gate can flip off `--dirty`). `routes/api.php` untouched. `php artisan test` = 452 pass / 3 fail
  (pre-existing). Actual churn was ~172 files, not the plan's estimated "300+".
- 2026-07-07 — **W2 (Larastan) — DEFERRED to after the manual clone + backend deploy** (user
  decision). Was parked mid-step; now fully **undone** (`composer remove --dev larastan/larastan`
  + deleted `phpstan.neon` / `phpstan-baseline.neon`) so the backend tree is clean for the clone.
  W1 (Pint, `96413df`) stays committed. **When re-added after the clone:** measured raw error counts
  are worth reusing — **L0 = 125** (real structural: undefined method/class/signature), **L1 = 1437**,
  **L2 = 1609**, **L3 = 1647**, **L4 = 1697**; the L0→L1 jump is almost all Laravel dynamic-property /
  undefined-var noise. **Recommendation for the re-add:** start the ratchet at **L0** (125 real
  errors, genuinely shrinkable to zero, then bump the level) rather than the plan's L4 (1697-error
  baseline that never shrinks). Steps: `composer require --dev larastan/larastan` → `phpstan.neon`
  at chosen level → `phpstan analyse --generate-baseline --memory-limit=1G` → seed the ratchet
  tracker → commit.
- 2026-07-07 — **Dep-free items W5–W8 not started** (pre-commit hook, composer QA scripts, VS Code →
  Pint, install/deploy cleanup). Can be done independently of W2 / the clone whenever wanted.
- 2026-07-08 — **W2 (Larastan) DONE + W6 (composer scripts) DONE — clone complete, re-added.**
  Reinstalled `larastan/larastan ^3.10`; `phpstan.neon` at **level 0** (user-chosen ratchet start over
  L4 — see level table). Generated `phpstan-baseline.neon` = **124 errors** (71 grouped entries).
  **1 non-ignorable error fixed at source** (not baselined): `GuestOtpNotification::$locale` redeclared
  `public string $locale` over Laravel's untyped parent `Notification::$locale` (`property.extraNativeType`)
  → removed the redeclaration (property inherited; ctor still sets it, typed `string` at the boundary).
  **W6:** added composer scripts `lint` (`pint --test`), `lint:fix` (`pint`), `analyse`
  (`phpstan analyse --memory-limit=1G`), `test`, `qa` (`@lint`+`@analyse`+`@test`). Verified:
  `composer validate` valid · `composer lint` passed · `composer analyse` → **No errors** · full
  `composer qa` = lint+analyse green, test **452 pass / 3 fail** (documented pre-existing). Not yet
  committed at time of writing this line.
- 2026-07-08 — **W5 (pre-commit hook) + W8 (install cleanup) DONE. W7 (VS Code) DROPPED → N/A.**
  - **W5:** committed `.githooks/pre-commit` (POSIX sh) — runs Pint on staged `*.php`
    (`git diff --cached --diff-filter=ACM`), re-stages, **graceful-skips (exit 0 + warning) if
    `vendor/bin/pint` is absent** so a repo without `composer install` never blocks a commit.
    Installed via `git config core.hooksPath .githooks`, auto-wired from composer `post-autoload-dump`
    (guarded on `.git` existing). `.gitattributes`: `.githooks/pre-commit text eol=lf`; staged with
    mode `100755`. **Verified all 3 paths:** formats+re-stages a bad file · no-op when nothing staged ·
    graceful-skip when Pint hidden.
  - **W8:** removed the stale `pestphp/pest-plugin` allow-plugin (Pest not installed) → `allow-plugins`
    now empty. `composer validate --strict` → **valid** (no warnings). `composer audit` → **no
    security advisories**; note: `niklasravnsborg/laravel-pdf` is flagged **abandoned** (informational,
    not a vuln — it's a load-bearing prod dep for PDF/badge generation; left as-is, swap is out of scope).
  - **W7 DROPPED (N/A):** `.vscode/` is **gitignored** (`.gitignore:/.vscode`) and untracked — editor
    config can't be committed/shared without un-ignoring it, which is a deliberate repo convention +
    a cross-repo policy call, not a tooling-task side effect. And W7's goal (save-format matches the
    gate) is **already enforced by the W5 hook** regardless of editor settings. Local `.vscode/` edits
    were reverted to original (php formatter stays intelephense). **[user-approved drop 2026-07-08]**

## Definition of Done

- [ ] W1 `pint.json` + repo-wide Pint baseline (isolated commit); gate flipped to `pint --test`
- [x] W2 Larastan (level 0) + baseline (124 err); `composer analyse` green; ratchet tracker seeded
- [x] W5 pre-commit hook installed + verified (graceful-skip tested); `.gitattributes` entry
- [x] W6 composer QA scripts; `composer qa` runs the full gate
- [x] W7 ~~VS Code aligned to Pint~~ → **N/A** (`.vscode/` gitignored; W5 hook enforces the gate) · W8 install/deploy warnings cleaned (`composer validate --strict` valid)
- [x] Quality gate green (`pint --test` + `composer analyse` + `php artisan test` = 452/3 pre-existing)
- [x] Mobile contract: n/a (tooling only; `routes/api.php` untouched)
- [ ] Docs: this TASK.md → `done`; tasks index row; **LEDGER** entry (gate flip); HANDOFF refresh;
      `../../process/SETUP_AND_UPDATE.md` documents the hook install + `composer qa`
