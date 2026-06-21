# Cyan-Basecode Migration Playbook — replay the directors upgrades

> **Purpose.** `pif-directors-gathering` ("directors") is the upgrade-then-clone **baseline** (see `BASELINE_DECISION.md`). This doc is the portable, cyan-targeted log + recipe for bringing **`cyan-basecode`** up to the same state. It covers:
> 1. **Backend** — Laravel 11→12 (+ PHPUnit, zipstream) and the OWASP/framework backend bumps. *(log of what we did to directors' backend + the cyan delta)*
> 2. **Frontend/Admin** — Tailwind v3→v4 + the W1 focus-ring cleanup. *(Tailwind deep-dive lives in `TAILWIND_V3_TO_V4_MIGRATION_RUNBOOK.md`; this doc gives the cyan-specific steps + numbers and points there.)*
>
> **Cyan is similar but NOT identical to directors** — fewer sub-apps, different theme/PDF stack, already further along on some parts. Real deltas are called out throughout (🔶 **CYAN DELTA**). Re-verify every count in the cyan repo before trusting a number.
>
> Reference implementation + exact commit SHAs: `UPGRADE_SUMMARY.md`. This file is the *how-to-replay*; that file is the directors *execution log*.

---

## 0. Cyan current state (snapshot 2026-06-07) — what's done vs pending

Read directly from `cyan-basecode-repos/` (`cyan-backend`, `cyan-admin`, `cyan-frontend` — **3 sub-apps, no `-landing`**; all on `dev`, clean).

| Concern | directors target | cyan now | Action |
|---|---|---|---|
| Next.js | 15.5.19 | **15.5.19** | ✅ done |
| React / react-dom | 18.3.1 | **18.3.1** | ✅ done |
| Headless UI | ^2.2.10 | **2.2.10** | ✅ done |
| framer-motion / swiper / js-cookie | 11 / 12 / 3.x | **11 / 12 / 3.0.7** | ✅ done |
| Sentry (`@sentry/nextjs`, `sentry/sentry-laravel`) | removed | **absent** | ✅ done (do NOT re-add) |
| react-quill | removed | **absent** | ✅ done |
| admin `xlsx` → SheetJS CDN | CDN tarball | **CDN tarball** | ✅ done |
| Backend Symfony | 7.4.x | **7.4.x** | ✅ done (Part 2) |
| Backend commonmark / phpspreadsheet pins | 2.8.2 / 1.30.4 | **2.8.2 / 1.30.4** | ✅ done (Part 1 OWASP) |
| **Backend Laravel** | **^12.60** | **^11.0** | ❌ **PART A below** |
| **Backend PHPUnit** | **^11.5.3** | **^10.0** | ❌ Part A |
| **Backend zipstream** | **^5.7** | **^4.13** | ❌ Part A |
| **Tailwind CSS** | **^4.3.0** + `@tailwindcss/postcss` | **^3.1.6 (fe) / ^3.0.24 (ad)** | ❌ **PART B below** |
| **tailwind-bootstrap-grid** | **^7** | **^5.0.1** | ❌ Part B |
| W1 focus rings (v4 1px regression) | fixed | n/a (still v3) | ❌ **PART C** (after Part B) |

**Bottom line for cyan:** the remaining work is **(A) Backend Part 5 (Laravel 12)** and **(B) Frontend/Admin Tailwind v4 + (C) W1 rings**. Everything else from directors Parts 1–3 is already in cyan.

**Guardrails (same lineage, do not regress):** `yarn` (not npm); EN+AR translations same commit; branch per sub-app off `dev`, merge `--no-ff` after green; `composer.lock`/`yarn.lock` are **gitignored** → commits carry `composer.json`/`package.json` (+ `phpunit.xml`/`.gitignore`) only; no `console.log`/`dd()`/`dump()`; no widening TS to `any`; **never re-add** Sentry / react-quill / `tailwindcss@3` / `tailwind-bootstrap-grid@5` / npm `xlsx`. macOS `grep` has no `-P`; zsh doesn't word-split unquoted `$vars`.

---

## PART A — Backend: Laravel 11 → 12 (directors Part 5)

**Clears `CVE-2026-48019`** (CRLF injection in Laravel's default email validation rule; `< 12.60` is affected). Do it on its own branch `chore/laravel-12-upgrade` off `dev`, merge `--no-ff`.

🔶 **CYAN DELTA:** cyan already has Symfony 7.4.x + commonmark 2.8.2 + phpspreadsheet 1.30.4 (directors Parts 1–2), so **only the Laravel-12 trio + test-config below applies.** Cyan uses `spatie/laravel-pdf` + `spatie/browsershot` for PDF (directors uses mpdf) and has **no `setasign/fpdi`** — so directors' Part-2 fpdi/mpdf transitive bumps do **not** apply; cyan's forced transitive set will differ. Trust `composer update` + `composer audit`, not directors' exact transitive list.

### A.1 `composer.json` — 3 edits
```diff
  "require": {
-   "laravel/framework": "^11.0",
+   "laravel/framework": "^12.60",
-   "stechstudio/laravel-zipstream": "^4.13",
+   "stechstudio/laravel-zipstream": "^5.7",
  },
  "require-dev": {
-   "phpunit/phpunit": "^10.0",
+   "phpunit/phpunit": "^11.5.3",
  }
```
Then `composer update laravel/framework phpunit/phpunit stechstudio/laravel-zipstream --with-all-dependencies` (cyan's lock is gitignored — the commit carries `composer.json` only, plus `phpunit.xml`/`.gitignore` below).

**Forced transitive bumps (lock only)** on directors were: `maennchen/zipstream-php` 2.4→3.1.2, `psr/http-message` 1.1→2.0, `nunomaduro/collision` 8.5→8.9.4 (+ mpdf shim, which cyan likely lacks). Carbon was already 3.x. **Let composer resolve cyan's own set; confirm with `composer audit`.**

### A.2 `phpunit.xml` — migrate to the PHPUnit 11 schema
PHPUnit 11 replaces the `<coverage><include>` / `<filter>` block with `<source>`:
```diff
- <coverage>
-   <include>
-     <directory suffix=".php">app</directory>
-   </include>
- </coverage>
+ <source>
+   <include>
+     <directory suffix=".php">app</directory>
+   </include>
+ </source>
```
(Run `vendor/bin/phpunit --migrate-configuration` to auto-apply, then eyeball.)

### A.3 `.gitignore`
```diff
+ /.phpunit.cache
```

### A.4 Keep the legacy skeleton
Laravel 12 **supports the Laravel-10/11 app skeleton** (`app/Http/Kernel.php`, etc.). **Do NOT migrate to the slim bootstrap/app.php skeleton** — out of scope, high risk. Directors kept the legacy skeleton; cyan does the same.

### A.5 Verify (before merge)
```bash
composer audit                              # must be clean of in-scope advisories
git diff --stat routes/                     # routes/*.php BYTE-IDENTICAL (API contract intact)
php artisan test                            # run full suite; note pre-existing failures
./vendor/bin/pint --test                    # likely RED pre-existing — note, don't fix here
```
- **Routes must be byte-identical** — directors has a mobile contract (`docs/mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf`). 🔶 **CYAN DELTA:** confirm whether cyan has a mobile consumer; if not, this is just good hygiene.
- Smoke the zipstream v5 API (`Zip::create(...)` facade) — v4→v5 is a major bump.
- Record **pre-existing** test failures (env-dependent: storage URL, privacy toggles, an intentional `abort(403)` on `/`) — prove they fail identically on L11 before blaming the upgrade. Out of scope to fix.

---

## PART B — Frontend + Admin: Tailwind v3 → v4 (directors Part 4)

> **Authoritative deep-dive: `TAILWIND_V3_TO_V4_MIGRATION_RUNBOOK.md`** (full step list, the codemod's exact renames, the opacity-pairing algorithm, the bootstrap-grid `col-*` collision, every gotcha). This section is the **cyan-specific checklist + numbers**. Do it per app, branch `chore/upgrade-to-tailwind-4` off `dev`.

cyan's pre-v4 config is **structurally identical to directors'** (verified): `postcss.config.js` has the v3 plugin list; `tailwind.config.js` has `mode:'jit'`, `corePlugins:{container:false}`, `future`, `experimental`, a `variants{}` block, tbg via `require('tailwind-bootstrap-grid')(...)` in `plugins`, the `flip` plugin using the **old 2-arg `addUtilities(newUtilities, variants('flip'))`**, and `hocus`; `css/tailwind.css` uses `@tailwind base/components/utilities`. admin additionally has `darkMode:'class'`. ⇒ the runbook ports 1:1.

### B.1 `package.json` (each of `cyan-frontend`, `cyan-admin`)
```diff
- "tailwindcss": "^3.1.6",            // admin: ^3.0.24
+ "tailwindcss": "^4.3.0",
+ "@tailwindcss/postcss": "^4.3.0",
- "tailwind-bootstrap-grid": "^5.0.1",
+ "tailwind-bootstrap-grid": "^7",    // first version with peer tailwindcss ^4
```
`yarn install`. (The codemod in B.5 may also bump `prettier-plugin-tailwindcss` → harmless `prettier/plugins/angular` ESLint warning; non-blocking.)

### B.2 `postcss.config.js`
```js
module.exports = { plugins: ['@tailwindcss/postcss', 'postcss-flexbugs-fixes'] };
```
(Drop `postcss-nested` + `postcss-preset-env` from the **plugins array** — v4 has built-in nesting/autoprefixer. They stay in devDependencies as unused; removing is an optional later cleanup.)

### B.3 `css/tailwind.css` (the critical file)
```css
@import 'tailwindcss';
@config '../tailwind.config.js';

@plugin 'tailwind-bootstrap-grid' { rtl: true; }

/* force the full bootstrap grid (content-scan misses dynamic classNames) */
@source inline("row container");
@source inline("col-{1..12}");
@source inline("offset-{0..11}");
@source inline("order-{0..12}");

/* v4 compat: keep v3 default border color (v4 defaults to currentColor) */
@layer base {
  *, ::after, ::before, ::backdrop, ::file-selector-button {
    border-color: var(--color-gray-200, currentColor);
  }
}
```

### B.4 `tailwind.config.js` — remove v3-only keys, fix the flip plugin
```diff
- mode: 'jit',
- corePlugins: { container: false },
- future: { ... },
- experimental: { ... },
- variants: { ... },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
-   require('tailwind-bootstrap-grid')({ ... }),   // now registered via @plugin in CSS
-   plugin(function ({ addUtilities, variants }) {
-     addUtilities(newUtilities, variants('flip'));   // v4 dropped the 2nd arg
+   plugin(function ({ addUtilities }) {
+     addUtilities(newUtilities);
    }),
    plugin(function ({ addVariant }) { addVariant('hocus', ['&:hover', '&:focus']); }),
  ]
```
**KEEP:** `content`, the whole `theme` (🔶 **CYAN DELTA:** cyan's own colors/fonts — don't copy directors' palette), `@tailwindcss/forms` + `/typography`, `hocus`. admin `darkMode:'class'` still works via the `@config` bridge (optional later: v4-native `@custom-variant dark`).

### B.5 Official codemod
```bash
npx @tailwindcss/upgrade@latest --force   # run from each app dir
```
Renames gradients/shadows/rounded/important-prefix/negative-values/`flex-grow`→`grow` etc. **Verify it did NOT touch your already-migrated `css/tailwind.css` / `tailwind.config.js` / `postcss.config.js`** (md5 before/after).

### B.6 Manual `*-opacity-*` → `/modifier` (the codemod does NOT do this)
🔶 **CYAN COUNTS (verified 2026-06-07):** `cyan-frontend` **38**, `cyan-admin` **33** (directors was 40/56).
```bash
grep -rnE '(bg|text|border|ring|divide|placeholder)-opacity-[0-9]+' components pages
```
Pair within the same variant chain: `focus:ring-primary focus:ring-opacity-50` → `focus:ring-primary/50`. **No-color drop:** a bare `focus:ring focus:ring-opacity-50` → delete the opacity class (leaves bare `focus:ring` → feeds Part C). Re-grep must return **0**.

### B.7 Verify per app
```bash
rm -rf .next && yarn type-check && yarn production
```
Built CSS (`.next/static/css/*.css`): 12 distinct `.col-N{` + `offset-0..11` present; **zero** `*-opacity-*` rules; border shim present; migrated rings carry `/.5` alpha. Then **EN + AR visual QA** on grid-dense / focus-ring / brand-color surfaces. Merge `--no-ff` per app.

---

## PART C — W1 focus-ring restore (do right after Part B, per app)

v4 renders a **width-less `ring` as 1px** (v3 was 3px). Two className-only passes — see `TAILWIND_V4_CLEANUP_PLAN.md` W1 + `UPGRADE_SUMMARY.md` item 6 for the directors detail.

- **W1A — colorless bare rings** (no `ring-{color}`, no `ring-{width}`): → `ring-3` **+ explicit color** (recommend brand `ring-primary/50`; use `ring-blue-500/50` only for exact v3 parity).
- **W1B — colored bare rings** (already have `ring-{color}`, only width regressed): bump width only `focus:ring`→`focus:ring-3` (color-preserving). This is the **bigger, user-visible** one (every input/select/checkbox/button focus ring is 1px). A single boundary-aware sed `focus:ring([^-A-Za-z0-9])` → `focus:ring-3$1` catches both plain and the `focus:focus:ring` dup-typo's inner token.
- **W1D (admin):** dedup `focus:focus:ring-3` → `focus:ring-3`.

🔶 **CYAN COUNTS (rough, verify):** standalone-`ring` matches ≈ `cyan-frontend` 195, `cyan-admin` 476 (most are colored W1B, not all standalone — filter false positives in comments/the `langSwitcher copy` dup files).

### ⚠️⚠️ Admin v4 cascade-layer gotcha (will bite cyan-admin too)
In v4, **unlayered CSS outranks `@layer utilities`** regardless of specificity. directors-admin's `css/web.css` `.custom-input { border-color: ... }` (imported unlayered in `_app.tsx`) **beat** the focus-border utility, so `focus:border-primary` silently did nothing until changed to **`focus:border-primary!`** (important beats unlayered-normal — same trick the file's error state already used: `border-red-500!`). **If any cyan-admin Tailwind override looks "ignored," it's this** — add `!` or move `web.css` into a layer. Also note many admin `focus:{ring,border}-{undefined-color}` (`accent`/`light-blue`/`secondary`) are **dead no-ops** (theme defines only some colors) — pre-existing, not a v4 regression; 🔶 cyan's theme defines a different color set, so re-check which are real.

---

## PART D — (OPTIONAL / PARKED) Drop `tailwind-bootstrap-grid` (directors W2)

Strategic end-state is Tailwind-only (the v5→v7 peer break + the v4 `col-*` namespace collision are the motivation). On directors this is **parked** — see `TAILWIND_V4_CLEANUP_PLAN.md`. Not required for the v4 upgrade. If cyan does it, do the **frontend spike first**.

### ⚠️ CRITICAL — it is NOT a flat find/replace (corrects the old "uniform mapping" claim)
The "no responsive grid" assumption was **wrong** — both directors and cyan apply **Tailwind variant prefixes onto bootstrap base classes**. 🔶 **CYAN CONFIRMED (2026-06-07):** `cyan-frontend` uses `md:col-9` (15), `md:col-3` (15), `md:col-4` (9), `lg:col-8`, `lg:offset-2`, `xl:offset-2`…; `cyan-admin` uses `md:col-4` (39), `md:col-8` (36), `md:col-6` (34), bare `md:col` (5)… **Pervasive responsive grid.** A flat substitution silently breaks every responsive-only column below its breakpoint.

### What the plugin actually generates (gutter = default 1.5rem)
Gutter + base width + shrink live on **`.row > *`** (every direct child: `box-border shrink-0 width:100% max-width:100% padding-inline:.75rem`), **not** on `.col-*`. `.row` = `flex flex-wrap; margin-inline:-.75rem`. `.col-N` = only `flex:0 0 auto; width:(N/12)%`. `.offset-N` = `margin-inline-start:(N/12)%` (logical/RTL-safe). `.container` = `width:100%; margin-inline:auto; padding-inline:.75rem; max-width → theme.screens steps`. `.gx-0` = `--bs-gutter-x:0`. ⇒ a child with only `md:col-6` is full-width below md **only** because of `.row>*` → the codemod **must reinstate a base width**.

### Open decision (settle in the spike): flex-faithful vs CSS-grid
**flex-faithful is recommended** — one consistent rule, RTL-safe, pixel-identical, lowest QA risk. CSS-grid (`grid-cols-12`) **cannot** reproduce flex `justify-center`/`justify-end`/`items-center`/auto-`col` rows (on a full 12-track grid `justify-content` is inert; centering an odd span like `col-7` needs a non-integer `col-start`) — on directors-frontend that was 18/65 live rows, forcing flex *exceptions* anyway. Recommended mapping when un-held:
```
row              → flex flex-wrap -mx-3 [&>*]:px-3 [&>*]:shrink-0   (gutter on row handles gx-0 locally)
col-N            → w-{N}/12     (col-12 → w-full)
{bp}:col-N       → {bp}:w-{N}/12   (+ inject base w-full if no unprefixed col)
col (auto)       → grow basis-0
offset-N / {bp}: → ms-[{N/12*100}%]   (offset-0 → ms-0)   — logical, RTL-safe
order-N          → order-N (native 1–12; order-0 → order-none)
container        → container mx-auto px-3   (v4 core container already emits matching max-widths)
```
Then: remove the `@plugin`/`@source inline` grid lines from `css/tailwind.css` + the dep from `package.json`; built CSS must no longer contain `.row{display:flex}`/`.col-N{`; EN+AR QA; merge per app. **Re-census cyan's own counts; do not trust directors' numbers.**

---

## Order of operations for cyan

1. **Backend Part A** (independent repo, no frontend coupling) — Laravel 12 branch → verify → merge `--no-ff` → push `dev`.
2. **Frontend Part B + C** — `cyan-frontend` first (smaller), then `cyan-admin` (has the darkMode + unlayered-css gotchas). Per app: Tailwind v4 → W1 rings → green → EN/AR QA → merge.
3. **Part D** — optional/parked; only with a fresh go-ahead, frontend spike first.

## Quality gates (every push)
- **Backend:** `composer audit` clean · `./vendor/bin/pint --test` (note pre-existing) · `php artisan test`.
- **Frontend/Admin:** `rm -rf .next && yarn type-check && yarn production`.
- **Commits:** `P<phase>.<task> — <short imperative>`; branch `dev`; `--no-ff` merges; `composer.lock`/`yarn.lock` gitignored (commit manifests only); EN+AR translations same commit.

## Key differences from directors (quick reference)
- **3 sub-apps, no `-landing`** → Tailwind work spans **2** Next apps, not 3.
- Backend **already on Symfony 7.4 + OWASP pins** → only Laravel-12 trio remains.
- **PDF stack differs** (cyan: spatie/browsershot + laravel-pdf; directors: mpdf/fpdi) → different composer transitive bumps; no fpdi step.
- **No Sentry to remove** (already absent).
- **Different theme palette + color set** → keep cyan's `theme`; re-check which focus-ring colors are real vs no-op.
- **Re-census all counts** (opacity utils, rings, grid sites) in the cyan repo — the numbers here are cyan-2026-06-07 snapshots, not guarantees.
</content>
</invoke>
