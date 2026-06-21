# Dependency Hygiene Playbook (portable)

> **Reusable across the ALT project family** (Next.js pages-router apps + a Laravel API). A step-by-step recipe to **audit dependencies → remove unused → apply safe updates → patch in-range CVEs → clear downstream config cruft**, with the gotchas that bit us baked in.
>
> Distilled from cyan-basecode **Phase 23** and the directors **2026-06 audit** (see [`DEPENDENCY_AUDIT.md`](DEPENDENCY_AUDIT.md) for directors' concrete results). This doc is the *method*; that doc is the *record*.
>
> **Scope:** safe hygiene + in-range security only — remove dead deps, apply patch/minor-within-major bumps, pin/resolve known CVEs that have an in-range fix. **Out of scope:** major / framework bumps (dedicated branches; for directors that's the Parts 1–5 initiative). Honors the **no-framework-bump** rule (Next / React / Laravel / PHP majors never bump here).

---

## 0. Assumptions & policy (adjust per project)

- **JS apps:** Next.js (pages router), **Yarn 1.x**, TypeScript. Directors has **three**: `-admin`, `-frontend`, `-landing` (landing is directors-only — don't forget it). **PHP app:** Laravel **12**, Composer 2, PHP 8.2.
- **Lockfiles are gitignored** (`yarn.lock` / `composer.lock`). This changes everything about "updating" — see §4. **Check first:** `git check-ignore yarn.lock composer.lock`.
- **Policy:** never bump a major of Next / React / Laravel / PHP (and treat Tailwind / ESLint / TypeScript / Prettier majors as toolchain — dedicated branch). Patch/minor *within the current major* is "safe."
- **Quality gate is the safety net.** Nothing is "done" until it passes:
  - JS: `yarn type-check` + `yarn production` (the real build)
  - PHP: `./vendor/bin/pint --test` + `php artisan test` (or a targeted `--filter` for a deps-only change)
- **One branch per repo**, off `dev`. Commit format `chore(deps): …` (directors' existing convention) or `P<phase>.<task> — …`. PR into `dev`; docs PR into the docs repo's `main`.
- **`routes/api.php` is the mobile contract** — a dependency change must not alter it; if a bump touches routing/serialization, re-verify the routes are byte-identical.

---

## 1. Audit — counts

Exact counts (don't eyeball the manifest; `wc -l` lies on multi-line entries):

```bash
# JS (per app)
node -p "Object.keys(require('./package.json').dependencies||{}).length"
node -p "Object.keys(require('./package.json').devDependencies||{}).length"
# PHP
node -p "Object.keys(require('./composer.json').require||{}).length"          # incl. 'php'
node -p "Object.keys(require('./composer.json')['require-dev']||{}).length"
```

Record before/after totals per repo — the delta is the headline. *(Directors' 2026-06 delta was zero — already clean. A zero delta is a valid, documented outcome, not a skipped step.)*

---

## 2. Find unused — run **both** scans, trust neither tool raw

### 2a. Forward scan — depcheck

```bash
npx -y depcheck --json
```

⚠️ **depcheck is wrong in both directions. Never act on its output raw.**

- **False positives** (flags as unused but IS used) — depcheck misses packages used only in:
  - config files: `next.config.js`, `postcss.config.js`, `tailwind.config.js` / `css/tailwind.css` (the v4 `@plugin '…'` line), `.eslintrc`, `.prettierrc`, `tsconfig.json`
  - `package.json` `scripts` (e.g. `env-cmd`)
  - **type-only** packages (`@types/x` is "used" iff `x` is used)
  - dynamic `require(variable)`
- **False negatives** (misses genuinely-dead deps) — depcheck thinks a lib is used because of a **commented-out import**.

### 2b. Inverse scan — live-import count per declared dep (catches the false negatives)

For **every** declared dep, count import lines that are **not** commented. Zero live = dead, regardless of what depcheck said.

```bash
rg -n --glob '!node_modules' --glob '!.next' "(import|require|from).*['\"]PKG(/|['\"])" .
```

🔴 **The trap that cost cyan a whole wave:** `rg -t tsx '…'` — **`tsx` is not a built-in ripgrep type**, so the command errors and (with `|| echo`) silently reports "0 matches." Several packages were declared "used" off a filter that never ran. **Use `--glob` / no type filter, and READ the matched lines** to confirm they're real imports, not `// import …`.

Decision rule per candidate:
- Real `import`/`require` (uncommented) anywhere → **used**.
- Only comments / only the `package.json` line → **unused**.
- `@types/x` → mirror the status of `x` (verify `x` is live-imported; if so, keep the types).

### PHP — conservative grep (Laravel auto-discovers a lot)

```bash
rg -n -i 'PackageNamespace|Facade|ClassName' app config routes database tests bootstrap
composer why vendor/package          # transitive? only root-required = candidate
```

Treat as **used (indirect)** even with zero direct refs: framework transitive (`symfony/*`), HTTP (`guzzlehttp/guzzle`), schema (`doctrine/dbal`), markdown mailables (`league/commonmark`), and all dev tooling (pint/sail/collision/ignition/faker/phpunit/mockery). Only flag unused if **zero refs AND `composer why` shows only the root requires it.**

> **Directors gotcha (real example):** `setasign/fpdi` has zero app-code refs, but `composer why` shows `mpdf/mpdf` requires it transitively → **keep** (cyan removed it only because cyan dropped mPDF in D45). Same name, opposite verdict — always run `composer why`.

### The `yarn remove` reveal — peer-dependency entanglement

Removing a "dead" JS dep can surface a **peer dependency** you didn't see in source. Directors example: `zod` was declared in admin, imported nowhere — but `yarn remove zod` printed `@usewaypoint/email-builder … unmet peer dependency "zod@^1 || ^2 || ^3"`. A package can be peer-required by a **runtime** component the build won't exercise. **If removal triggers an unmet-peer warning on a runtime feature, stop and park it for a human smoke** — don't ship it on a green build alone.

---

## 3. Remove unused

```bash
yarn remove pkg-a @types/pkg-a …     # JS — also re-runs install
composer remove vendor/package --no-interaction   # PHP
```

Then **re-audit** (§2 again) and run the gate. Each removal = one commit; trivially revertable. After removing a lib, check for config it left behind (§5).

---

## 4. Apply safe updates — the lockfile decision

```bash
yarn outdated
composer outdated --direct --no-interaction   # '!' = patch/minor, '~' = major
```

Classify: ✅ **SAFE** = patch/minor within current major, no coupling/policy conflict. ⛔ **NOT SAFE** = any major / framework-pinned / toolchain major / coupled → dedicated branch.

### 🔑 The gitignored-lockfile insight

If lockfiles are gitignored **and** the new version is already inside the manifest's `^` range:
- A plain `yarn upgrade` / `composer update` changes **only the gitignored lockfile** → **no committable diff**. It floats to latest-in-range on the next clean install anyway.

**To make a safe update explicit & reviewable, floor-bump the manifest:**

```bash
yarn add pkg@^<new>                       # JS dependency
yarn add -D pkg@^<new>                     # JS devDependency
composer require -W "vendor/pkg:^<new>"    # PHP (-W drags transitive bumps; required)
```

> **Directors worked example (CVE floor):** `phpoffice/phpspreadsheet` — installed was already 1.30.5 (floated), `composer audit` already clean, but the manifest floor said `^1.30.4` (admits the CVE-2026-45034 version). `composer require -W "phpoffice/phpspreadsheet:^1.30.5"` pins the floor — a 1-line, reproducible, reviewable diff. **The "audit is clean" install can still hide a vulnerable manifest floor.**

### 🔑 In-range CVE in a *transitive* dep → `resolutions` (JS)

When the vulnerable package is pulled by a dep you don't control (e.g. `form-data` via `axios`), a manifest floor on *your* dep won't help. Pin the transitive version with a yarn **`resolutions`** entry:

```jsonc
// package.json
"resolutions": { "form-data": "^4.0.6" }
```

> **Directors worked example:** `axios`'s `form-data ^4.0.0` range admitted the vulnerable `form-data@4.0.5` (CRLF, npm 1120743). Adding `"form-data": "^4.0.6"` to `resolutions` + `yarn install` floored it; `yarn audit` High → 0. Applied to **all three** Next apps (don't forget landing). Confirm the installed version after: `node -e "console.log(require('./node_modules/form-data/package.json').version)"`.

### Coupling checks (don't trust "patch/minor" blindly)

- `composer require` that **auto-reverts** = a peer gate (e.g. `nunomaduro/collision` 8.9 needs `phpunit` ≥11.5; directors already cleared this in Part 5).
- `date-fns-tz` 3.x requires `date-fns` 3.x — move together.
- `resolutions`-pinned deps (`@types/react`) already float — don't floor-bump.
- CDN-tarball deps (`xlsx` from a SheetJS URL) show as `exotic` — can't version-compare; skip.

---

## 5. Downstream config cruft

A removed lib may leave a webpack/babel/postcss/eslint shim. Grep configs for the lib name before declaring the removal complete. Canonical case: **`babel.config.js` + `babel-plugin-transform-require-ignore`** existed only to strip FullCalendar's `require('*.css')`; once FullCalendar is gone, removing `babel.config.js` **re-enables Next's SWC compiler** (faster builds). *(N/A for directors — it has no `babel.config.js` and never had FullCalendar; check anyway on a new clone.)*

---

## 6. Quality gate — reading the results

- **JS:** `yarn type-check` catches removed symbols still imported; `yarn production` is the real test (loads `next.config.js`, exercises build-time plugins). **Neither validates runtime behavior of a rich client component** (e.g. the email editor) — peer-dep changes there need a manual smoke.
- **PHP:** `php artisan test`. Know your **pre-existing** failures (directors: stock `ExampleTest` `/`→403 by design + 2 avatar tests gated on `PUBLIC_STORAGE_URL`/privacy toggle) so you don't blame them on your change. `pint --test` is RED on pre-existing style debt across ~390 untouched files — **don't reformat them in a deps PR**.
- **Security:** re-run `yarn audit` / `composer audit` after the change. Know the **accepted residual** (admin `insane` ReDoS, no upstream patch) so a lingering Moderate isn't mistaken for a regression.

A dependency removal/bump has **zero runtime impact if nothing imported it** — the value is a smaller surface (fewer CVEs, faster installs), not behavior change.

---

## 7. Git / PR / tracking workflow

```bash
git checkout dev && git checkout -b chore/deps-cleanup   # or chore/cve-<pkg>
# … remove / bump / pin … run gate …
git add package.json    # (lockfile gitignored → manifest-only diff)
git commit -m "chore(deps): …"
```

- One concern per branch (directors kept the two 2026-06 CVEs on separate branches: `chore/cve-form-data-resolution`, `chore/cve-phpspreadsheet-1.30.5`).
- **Don't push without instruction.** `git push` prints a PR URL; or hand over `…/compare/dev...<branch>?expand=1`.
- After merge: `git checkout dev && git pull --ff-only && git branch -d <branch>`.
- **Track it like real work:** a record doc under `docs/upgrades/` ([`DEPENDENCY_AUDIT.md`](DEPENDENCY_AUDIT.md)) + an index row in [`README.md`](README.md) + a HANDOFF note.

---

## 8. Pitfalls checklist (the TL;DR)

| Pitfall | Guard |
|---|---|
| depcheck false +/- | run BOTH scans; verify every flag with plain `rg`; read the matched lines |
| `rg -t tsx` silently errors | use `--glob '!node_modules'`, never a `tsx` type |
| commented-out imports look used | confirm the match isn't `// import …` |
| `@types/x` orphaned | mirror status of `x`; keep iff `x` is live-imported |
| gitignored lockfile → bump has no diff | **floor-bump the manifest** to pin |
| audit clean but manifest floor vulnerable | pin the floor anyway (phpspreadsheet case) |
| CVE in a transitive dep | yarn `resolutions` pin (form-data case) — apply to ALL apps incl. landing |
| `composer require` reverts | add `-W`; a revert = a peer gate |
| "dead" dep is a runtime peer | `yarn remove` warns "unmet peer"; park for a human smoke, don't ship on green build |
| declared-but-unimported dep | may be load-bearing via transitive **type resolution** (directors `zod`↔email-builder: removal broke `tsc`+build). The gate is the arbiter — never remove on a source scan alone |
| `composer why` shows transitive requirer | keep (fpdi/mpdf case) |
| removed lib leaves config | grep configs (babel/postcss/webpack/eslint) for its name |
| pre-existing test/lint debt | know it; don't attribute to your change; don't reformat |
| framework major slipped in | Next/React/Laravel/PHP majors → never here |
| forgot the landing app | directors has 3 Next apps — fe + ad + **la** |
</content>
