# Backend Tooling & Code-Quality Chain — plan + execution

> **Status:** ✅ **REVIEWED & SCOPED (2026-07-07)** — ready to execute as `docs/tasks/003-backend-tooling-chain/`.
> Brings `alt-static-basecode-backend`'s tooling/quality chain up to parity with the pass already done
> on the two Next apps (ESLint 9 flat config, Prettier 3, husky + lint-staged, `type-check`,
> 0-warning gate).
>
> **Review outcome (what changed from the first draft):**
> - **W4 (Rector) — removed from this task.** It's a run-once behavior-changing rewriter, not a gate;
>   W1 (`no_unused_imports`) + W2 (Larastan) cover the unused-import / dead-code asks. Moved to the
>   cleanup plan as an optional one-off during Tasks 003/007. See
>   [CLEANUP_AND_HARDENING_MASTER_PLAN.md](CLEANUP_AND_HARDENING_MASTER_PLAN.md).
> - **W2 (Larastan) — kept, WITH a ratchet commitment** (user decision 2026-07-07). Not a rubber-stamp
>   baseline: raising the level / shrinking the baseline is an explicit tracked step (§1 W2), so the
>   static-analysis bar actually rises over time. Runs in `composer analyse`/`qa`, **not** in the hook.
> - **W5 (hook) — hardened:** must degrade gracefully if `vendor/bin/pint` is absent (no `composer
>   install` yet), plus a `.gitattributes` entry for the hook's exec-bit + LF endings.
> - **W9 (CI) — stays optional/out** (neither Next app has CI).
> - **Gate flip needs a ledger entry:** switching `pint --dirty` → `pint --test` (via W1's clean
>   baseline) overrides the documented `--dirty` workaround → record as a `LEDGER` decision, not just a
>   HANDOFF line.
>
> **Why first:** do this **before** the heavy backend refactors in
> [CLEANUP_AND_HARDENING_MASTER_PLAN.md](CLEANUP_AND_HARDENING_MASTER_PLAN.md) (migration squash, base
> controller, response unification). A clean, enforced gate up front means every refactor commit lands
> pre-formatted + statically checked instead of dragging formatting churn through feature diffs.
>
> **Guardrails (from `../../CLAUDE.md`):** no new deps without justification · no framework bumps ·
> no `dd()`/`dump()` in committed code · match local patterns · **backend quality gate stays
> `pint` + `php artisan test`** (this plan hardens *how* that gate runs). Backend commits: `dev`,
> `P<phase>.<task> — …`, `composer.lock` gitignored (commit `composer.json` only).

---

## 0. Current-state audit (verified 2026-07-07)

### Present
- **Laravel Pint** `^1.29.3` (formatter) — but **no `pint.json`** (runs the implicit default preset),
  and the repo is **not Pint-clean at baseline** (`../HANDOFF.md`: a repo-wide `pint` churns 300+ files
  → the current gate is the workaround `pint --dirty`).
- **PHPUnit** `^11.5.55` + `phpunit.xml` (PHPUnit-11 schema), `nunomaduro/collision`, `mockery`,
  `fakerphp/faker`, `spatie/laravel-ignition`.
- **`.editorconfig`** (utf-8, LF, 4-space, final newline) — good, keep.
- **`.vscode/`** — `settings.json`, `extensions.json`, `README.md`.

### Absent / misconfigured (the gaps to close)
| Gap | Detail |
|---|---|
| **No static analysis** | No PHPStan / **Larastan**. This is the backend "type-check" equivalent — the single biggest gap. |
| **No `pint.json`** | Formatting rules are implicit; can't tune (e.g. enforce `no_unused_imports`, import ordering). |
| **Not Pint-clean** | Baseline dirty → gate is stuck on `pint --dirty` instead of a full `pint --test`. |
| **No pre-commit hook** | No husky/captainhook/grumphp; only git `*.sample` hooks. The Next apps have husky + lint-staged. |
| **No composer QA scripts** | No `lint` / `analyse` / `test` / `qa` scripts (admin has `lint`, `lint:fix`, `type-check`). |
| **No CI** | No `.github/workflows` (neither app has one either — optional here). |
| **VS Code PHP formatter mismatch** | `formatOnSave: true` but `[php].defaultFormatter = intelephense`, **not Pint** → save-format fights the Pint gate. Also leftover `source.fixAll.eslint` action + Tailwind/PostCSS/liveserver extension recs (irrelevant to a pure API backend). |
| **Install noise** | `config.allow-plugins.pestphp/pest-plugin` set, but Pest is not installed → stale. |

### Parity map — what each Next-app tool becomes on the backend
| Admin / FE (done) | Backend equivalent (this plan) |
|---|---|
| Prettier 3 (format) | **Pint** + `pint.json` (present; make it enforced + clean) |
| ESLint 9 (lint) | **Larastan** (static analysis) — the real "lint"/"type-check" |
| `tsc` (`type-check`) | **Larastan** level-based analysis |
| `eslint-plugin-unused-imports` | **Pint `no_unused_imports` rule** (+ optional Rector dead-code pass) |
| husky + lint-staged | **PHP-native pre-commit hook** (zero-dep; captainhook alt) running Pint (+ fast Larastan) on staged `*.php` |
| VS Code format-on-save (Prettier) | VS Code format-on-save → **Pint** (`open-southeners.laravel-pint`) |
| `yarn production` build check | `php artisan test` + `composer validate` + `composer audit` |

---

## 1. Work items

Each item: what · why · how · effort (S/M/L) · risk. New dev-deps are justified per CLAUDE.md.

### W1 — `pint.json` + one-time Pint baseline (format the whole repo, isolated commit) · S · low
**What.** Add an explicit `pint.json` (preset `laravel` + a few rules, e.g. `no_unused_imports`,
`ordered_imports`, `no_unused_lambda_imports`), then run **one** repo-wide `./vendor/bin/pint` and
commit the churn **on its own** (touches ~300+ files — do it alone, never inside a feature commit).
**Why.** Unblocks switching the gate from the `--dirty` workaround to a full **`pint --test`**; kills
the "why is my unrelated file reformatted" churn during the upcoming refactors; removes unused imports
repo-wide for free.
**How.**
```jsonc
// pint.json
{ "preset": "laravel",
  "rules": { "no_unused_imports": true, "ordered_imports": { "sort_algorithm": "alpha" } } }
```
`./vendor/bin/pint` → review diff is formatting-only → commit `P<phase>.<task> — chore: repo-wide Pint baseline`.
**Timing.** **Land this FIRST**, before the migration-squash/refactor tasks, so they start from a clean tree.
**Gate flip (LEDGER entry required).** This baseline lets the gate move from the `pint --dirty` workaround
to a full **`pint --test`**. That reverses a documented convention (the HANDOFF "Pint note" + CLAUDE.md), so
record it as a `../decisions/LEDGER.md` decision, not only a HANDOFF edit.
**Risk.** Large diff (mitigated: isolated commit, formatting-only, `php artisan test` still green after).

### W2 — Static analysis: Larastan (PHPStan for Laravel) · M · low→med
**What.** `composer require --dev larastan/larastan` (latest; targets PHP 8.2 / Laravel 12) + a
`phpstan.neon` with a **generated baseline** so existing violations don't block day-1.
**Why.** The backend has **no** static type-checking today — the biggest quality gap vs the TS apps.
Catches undefined methods/properties, bad types, dead branches, wrong Eloquent usage.
**How.**
```neon
# phpstan.neon
includes: [ vendor/larastan/larastan/extension.neon, phpstan-baseline.neon ]
parameters:
  level: 4            # start conservative (0–9); ratchet up over time
  paths: [ app ]
  # baseline swallows pre-existing errors so the gate is green from day 1:
```
`vendor/bin/phpstan analyse --generate-baseline` → commit baseline. Add `composer analyse` script (W6).
**Runs in `composer analyse`/`qa` only — NOT in the pre-commit hook** (too slow for a per-commit gate).

**Ratchet plan (COMMITTED — user decision 2026-07-07).** The baseline is green on day 1 by design, so
without a ratchet Larastan only guards *new* code and the bar never rises. To make the ratchet real, it's
a tracked step, not a vibe:
- Record the **starting level (4)** and **baseline error count** in the task `TASK.md` when W2 lands.
- Each subsequent backend-cleanup task (esp. 003/006/007) ends with a **"shrink the baseline"** step:
  delete any now-fixed entries; if the baseline hits ~zero at the current level, **bump `level` +1** and
  regenerate. Log the new level + count in `TASK.md` so progress is visible.
- Target: reach **level 6** by the end of the cleanup phase; treat any *increase* in baseline size in a
  PR as a red flag to review (new code should not add violations).

**Setup notes (avoid day-1 stalls).** Larastan over a Laravel-12 app usually needs `bootstrapFiles` and a
raised memory limit — expect `vendor/bin/phpstan analyse --memory-limit=1G` (or `parameters.tmpDir`) if it
OOMs. Firebase/Excel/PDF and other magic-heavy packages may need `ignoreErrors` stubs.
**Reproducibility caveat.** `composer.lock` is gitignored here, so the baseline is only reproducible if
contributors resolve the same dev-dep versions — fine for a small team; note it in `TASK.md`.
**Risk.** Level too high on day 1 = huge baseline → start at 4, ratchet per above.

### W3 — Unused imports & dead code · S · low
**What.** Mostly **free from W1** (`no_unused_imports`). For dead *code* (unused private methods/vars,
unreachable branches), fold into W2 (PHPStan flags many) or the optional W4 Rector pass.
**Why.** The user explicitly wants unused-import removal (the `eslint-plugin-unused-imports` equivalent).
**Risk.** Trivial once W1 lands.

### W4 — Rector · ❌ REMOVED from this task (moved to the cleanup plan)
**Decision (2026-07-07).** Rector is a **run-once, behavior-changing rewriter**, not a quality *gate* —
it doesn't belong in the tooling-chain task. W1's `no_unused_imports` + W2 (Larastan) already cover the
stated asks (unused imports, dead-code visibility). If a big mechanical cleanup is wanted later, run Rector
as an **optional one-off** during a cleanup task (003/007) with every diff reviewed and `php artisan test`
after — tracked in [CLEANUP_AND_HARDENING_MASTER_PLAN.md](CLEANUP_AND_HARDENING_MASTER_PLAN.md), not here.
It is **never** in the pre-commit hook.

### W5 — Pre-commit hook (the "husky" ask, PHP-native) · S · low
**What.** A git pre-commit hook that runs **Pint on staged `*.php`** (and optionally a fast Larastan on
changed files), mirroring the admin's `lint-staged` behavior.
**Why husky isn't the right tool here.** husky is a Node dev-dep; the backend has no `package.json`.
Adding Node just for a hook is a smell + a new-dep-without-justification. Use a PHP-native equivalent.
**Options (pick one — see §3 decision):**
- **(A) Zero-dep committed hook (recommended).** Commit `.githooks/pre-commit`; install it via a
  composer script (`post-install-cmd`/`post-autoload-dump`: `git config core.hooksPath .githooks`).
  No new dependency. The hook runs `./vendor/bin/pint` on the staged PHP files (via
  `git diff --cached --name-only --diff-filter=ACM -- '*.php'`) and re-stages.
- **(B) captainhook/captainhook** (`composer require --dev`) — nicer config (`captainhook.json`),
  auto-installs the hook; closest to lint-staged ergonomics. Costs one dev-dep.
- **(C) literal husky** — **not recommended** (Node in a PHP repo).
**Robustness (added at review).** The committed hook (A) must not break a repo without `composer install`:
- **Degrade gracefully** — if `./vendor/bin/pint` is missing, `echo` a warning and `exit 0` (skip), never
  block the commit. Same for a fast-Larastan variant if one is ever added.
- **`.gitattributes`** — add `.githooks/pre-commit text eol=lf` (and ensure the file is committed with the
  exec bit, `git update-index --chmod=+x`) so the hook actually runs on macOS/Linux and has LF endings.
- Fast (staged `*.php` only) and skippable in emergencies (`git commit --no-verify`, per policy only when
  explicitly allowed). Document the install (`core.hooksPath`) in `../process/SETUP_AND_UPDATE.md`.
**Risk.** Low, given the graceful-skip + exec-bit handling above.

### W6 — Composer QA scripts · S · low
**What.** Add scripts so the gate is one command (parity with admin's `lint`/`type-check`):
```jsonc
"scripts": {
  "lint":    "pint --test",
  "lint:fix":"pint",
  "analyse": "phpstan analyse",
  "test":    "php artisan test",
  "qa":      [ "@lint", "@analyse", "@test" ]
}
```
**Why.** One `composer qa` = the full backend gate; used by the hook + CI + humans.
**Risk.** None.

### W7 — VS Code alignment · S · low
**What.**
- Set `[php].editor.defaultFormatter` → **`open-southeners.laravel-pint`** (Pint), so format-on-save
  matches the gate. Keep **intelephense** for IntelliSense/navigation (not formatting).
- Remove the irrelevant `editor.codeActionsOnSave: { source.fixAll.eslint }` (no ESLint on the backend).
- Prune `extensions.json` recs that don't apply to a pure API backend (Tailwind, PostCSS, liveserver,
  prettier-for-php-files) and **add** `open-southeners.laravel-pint`. Keep intelephense, blade, laravel-goto.
- Keep `.editorconfig` as-is.
**Why.** Today save-format uses intelephense's formatter, which diverges from Pint → editor churn.
**Risk.** Contributors must install the Pint extension (add to recs + note in `.vscode/README.md`).

### W8 — Install / deploy warning cleanup · S · low
**What.**
- Remove the stale `config.allow-plugins.pestphp/pest-plugin` (Pest not installed).
- `composer validate --strict` → fix any manifest warnings.
- Confirm `composer audit` clean (already pinned OWASP versions).
- Confirm `optimize-autoloader: true` (present) + document `composer install --no-dev -o` for deploy.
**Why.** The user's "remove most of the coded warnings on install/deploy."
**Risk.** None.

### W9 — CI (OPTIONAL) · S · low
**What.** A `.github/workflows/backend-qa.yml` running `composer qa` (Pint --test + PHPStan + tests) on
PR to `dev`/`main`.
**Recommendation.** Optional — neither app has CI today. Add only if you want server-side enforcement
beyond the local hook. Low effort if wanted.

---

## 2. Execution order & gates

```
W1 pint.json + repo-wide Pint baseline        ← FIRST, isolated commit (unblocks pint --test gate)
   ▼
W7 VS Code → Pint formatter                    ← so save-format matches the new clean baseline
   ▼
W6 composer scripts  +  W8 install/deploy cleanup
   ▼
W2 Larastan + baseline (level 4, ratchet)      ← the "type-check" equivalent
   ▼
W5 pre-commit hook (Pint on staged .php; graceful-skip if vendor absent)
   ▼
W3 unused imports  (mostly done by W1; verify)
   ▼
W9 CI                        (OPTIONAL — out for now)

  (W4 Rector removed from this task → optional one-off in the cleanup plan.)
```

**Per-commit gate (after this lands):** `composer qa` — i.e. `pint --test` (full, not `--dirty`) +
`phpstan analyse` (baseline-green) + `php artisan test`. Record the switch from `pint --dirty` →
`pint --test` in `../HANDOFF.md` + the Pint-note there.

**Known baseline facts to expect:** `php artisan test` ≈ **452 pass / 3 fail** (pre-existing, unrelated —
ExampleTest `/`→403 + 2 avatar tests); don't let W2/W1 get blamed for them.

---

## 3. Decisions needed before execution
| Decision | Options | Recommendation |
|---|---|---|
| Pre-commit hook mechanism (the "husky" ask) | (A) zero-dep committed hook + `core.hooksPath` · (B) captainhook dev-dep · (C) husky/Node | **(A)** — no new dep, PHP-native; (B) if lint-staged-style ergonomics are wanted |
| Larastan starting level | 0–9 | ✅ **4** + generated baseline, **with a committed ratchet** to level 6 over the cleanup phase (user decision 2026-07-07) |
| Rector (W4) | in / out | ✅ **Removed from this task** → optional one-off in the cleanup plan |
| CI (W9) | in / out | **Out for now** (optional) — local hook + `composer qa` first |
| Hook scope | Pint only · Pint + PHPStan | **Pint only** in the hook (fast); run PHPStan in `composer qa`/CI |

---

## 4. Cross-references
- [CLEANUP_AND_HARDENING_MASTER_PLAN.md](CLEANUP_AND_HARDENING_MASTER_PLAN.md) — the refactor tasks this
  precedes (migration squash, base controller, response unification). **Open this tooling task as the
  next `docs/tasks/NNN` folder, ahead of that plan's Track A.**
- [DEPENDENCY_HYGIENE_PLAYBOOK.md](DEPENDENCY_HYGIENE_PLAYBOOK.md) — dependency-audit house style.
- [../process/SETUP_AND_UPDATE.md](../process/SETUP_AND_UPDATE.md) — document the hook install + `composer qa` here.
- [../HANDOFF.md](../HANDOFF.md) — the `pint --dirty` note to update once the repo is Pint-clean.
- The Next-app tooling pass (mirror target): admin `.husky/pre-commit` + `lint-staged` in `package.json`;
  ESLint 9 flat config + `eslint-plugin-unused-imports`.

## 5. Provenance (2026-07-07, read-only)
Verified directly: backend `composer.json` (Pint present, no Larastan/Rector/hook/QA-scripts, stale
`pestphp` allow-plugin), no `pint.json`, no `.github/`, `.vscode/settings.json` PHP formatter =
intelephense (not Pint) + leftover eslint action, `.editorconfig` present; admin `.husky/pre-commit`
= `npx lint-staged` + `lint-staged` map in `package.json`. Re-verify before implementing.
