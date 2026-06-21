# Tailwind CSS v3 → v4 Migration Runbook (ALT lineage)

> **Purpose:** the complete, reproducible recipe for migrating an ALT Next.js app from **Tailwind v3 → v4**, as actually executed on `pif-directors-gathering` (frontend / admin / landing) in June 2026. Written to be **replayed on `cyan-basecode`** (and any sibling fork), which is still on Tailwind v3.4.x + `tailwind-bootstrap-grid@^5`.
>
> This is the *portable how-to*. The pif-specific execution log lives in `UPGRADE_SUMMARY.md`; remaining pif cleanup is in `TAILWIND_V4_CLEANUP_PLAN.md`.

---

## 0. TL;DR — what this migration actually is

Three distinct pieces of work, in order. **The config swap is necessary but NOT sufficient** — the component-level opacity migration is the part people forget.

1. **Dependency + config swap** (4 files/app): `package.json`, `postcss.config.js`, `css/tailwind.css`, `tailwind.config.js`.
2. **Official codemod** (`npx @tailwindcss/upgrade`): renames gradient/shadow/rounded/important-prefix/negative-value/`flex-grow` etc. across components.
3. **Manual `*-opacity-*` → `/modifier` migration** (~40–56 utils/app): the codemod does **not** do this. This is the bulk of the manual work.

Plus the **`tailwind-bootstrap-grid` story**: bump `5 → 7` (v7 is the first version with `tailwindcss: ^4` peer support — this single fact is what makes v4 reachable without rewriting the grid), register it via the CSS `@plugin` directive + `@source inline(...)`, and know the v4 `col-*` namespace collision.

---

## 1. Prerequisites (do these FIRST)

This migration assumes the app is already on:
- **Next 15 + React 18.3.1** (ALT "Part 1+2")
- **Headless UI v2** (ALT "Part 3")
- **yarn** (yarn-classic). `yarn.lock` / `composer.lock` are gitignored in this lineage → commits carry `package.json` only.
- Bilingual **EN/AR (RTL)** — RTL must not regress.

> For cyan: confirm it's on Next 15 / React 18 / HUI v2 before starting v4. If cyan is still Next 12/React 17, do those parts first — don't stack a Tailwind major on top of an old framework.

Branch: `chore/upgrade-to-tailwind-4` off `dev`, **per sub-app** (each sub-app is its own git repo, no monorepo tooling → no cross-repo conflicts).

---

## 2. Step 1 — Dependencies (`package.json`)

```diff
- "tailwindcss": "^3.1.6",
+ "tailwindcss": "^4.3.0",             // the floor that landed on pif
+ "@tailwindcss/postcss": "^4.3.0",    // NEW — the v4 PostCSS plugin
- "tailwind-bootstrap-grid": "^5.0.1",
+ "tailwind-bootstrap-grid": "^7",     // THE unlock: first version with peer tailwindcss ^4
```

Then `yarn install`. (The official codemod in Step 5 also bumps `prettier-plugin-tailwindcss` `^0.1.13 → ^0.8.0` on some apps — allowed; see gotcha #5.)

**Dropped from the PostCSS *plugins array* (Step 2) — no longer needed:** `postcss-nested`, `postcss-preset-env` nesting — v4 has built-in nesting + autoprefixer. Keep `postcss-flexbugs-fixes`. Note: on pif these two were only removed from `postcss.config.js`; they're **still listed in `devDependencies`** (now unused). Removing them from `package.json` is an optional follow-up cleanup, not done in Part 4.

---

## 3. Step 2 — `postcss.config.js`

```diff
  module.exports = {
-    plugins: [
-       'tailwindcss',
-       'postcss-flexbugs-fixes',
-       'postcss-nested',
-       ['postcss-preset-env', { autoprefixer: { flexbox: 'no-2009' }, stage: 3,
-          features: { 'custom-properties': false, 'nesting-rules': true } }],
-    ],
+    plugins: ['@tailwindcss/postcss', 'postcss-flexbugs-fixes'],
  };
```

---

## 4. Step 3 — `css/tailwind.css` (the most important file)

**Before (v3):**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**After (v4):**
```css
@import 'tailwindcss';

@config '../tailwind.config.js';

@plugin 'tailwind-bootstrap-grid' {
  rtl: true;
}

/* Force the full bootstrap grid so it never depends on content-scan extraction */
@source inline("row container");
@source inline("col-{1..12}");
@source inline("offset-{0..11}");
@source inline("order-{0..12}");

/* v4 compat: preserve the v3 default border color (v4 defaults to currentColor) */
@layer base {
  *,
  ::after,
  ::before,
  ::backdrop,
  ::file-selector-button {
    border-color: var(--color-gray-200, currentColor);
  }
}
```

**Why each block:**
- `@import 'tailwindcss'` — replaces the three `@tailwind` directives.
- `@config '../tailwind.config.js'` — keeps the existing JS config (theme/colors/fonts/plugins) instead of porting everything to CSS-first `@theme`. Officially supported bridge; lowest-churn.
- `@plugin 'tailwind-bootstrap-grid' { rtl: true }` — registers the grid plugin **via CSS** (not as a JS `plugins:[]` entry). `rtl: true` keeps the RTL offset mirroring (`margin-inline-start`).
- `@source inline(...)` — **critical.** v4 generates utilities on-demand from content scanning. The bootstrap grid classes (`col-6`, `offset-2`, …) are often built dynamically (`classNames(...)`) and get missed → grid renders partially. `@source inline` force-generates the full static grid: `col-1..12`, `offset-0..11`, `order-0..12`, plus `row`/`container`.
- `@layer base` border shim — v4 changed the default border color from `gray-200` to `currentColor`. Without this, every `border` without an explicit color silently changes. This restores v3 behavior.

---

## 5. Step 4 — `tailwind.config.js`

**Remove these v3-only keys** (v4 doesn't support them):
```diff
- mode: 'jit',
- corePlugins: { container: false },     // bootstrap-grid owns .container now via @plugin
- future: { purgeLayersByDefault: true },
- experimental: { ... },
- variants: { ... },                      // the entire legacy variants block
```

**In `plugins: []`:**
```diff
- require('tailwind-bootstrap-grid')({ ... }),   // REMOVE — now registered via @plugin in CSS
```

**Fix any custom plugin that used the old `variants()` signature** (v4 dropped the 2nd arg):
```diff
- plugin(function ({ addUtilities, variants }) {
-    addUtilities(newUtilities, variants('flip'));
+ plugin(function ({ addUtilities }) {
+    addUtilities(newUtilities);
  }),
```

**KEEP:** `content`, the whole `theme` (colors / fontFamily / backgroundImage — app-specific), `require('@tailwindcss/forms')`, `require('@tailwindcss/typography')`, and custom `addVariant` plugins (e.g. `hocus`). `darkMode: 'class'` (admin) still works via the `@config` bridge.

---

## 6. Step 5 — Official codemod

```bash
npx @tailwindcss/upgrade@latest --force
```
Run it from each app dir. It edits **component classNames** (does NOT touch the protected config files if you've already migrated them — verify by md5 that `css/tailwind.css`, `tailwind.config.js`, `postcss.config.js` are unchanged after).

**What it handles** (all v4-correct, behavior-preserving):
`bg-gradient-to-*` → `bg-linear-to-*` · important prefix `!class` → suffix `class!` · `flex-grow`→`grow`, `flex-shrink-0`→`shrink-0` · `break-words`→`wrap-break-word` · `-right-[50px]`→`right-[-50px]` · `p-[1px]`→`p-px`, `border-t-[2px]`→`border-t-2` · `bg-[length:…]`→`bg-size-[…]` · `bg-right-bottom`→`bg-bottom-right` · shadow/rounded/blur scale renames.

**What it does NOT handle → Step 6.**

---

## 7. Step 6 — Manual `*-opacity-*` → `/modifier` migration (the real work)

v4 **removed** the `*-opacity-*` utilities. The codemod does NOT migrate them. Counts on pif: **frontend 40, landing 48, admin 56**.

**Detect:**
```bash
grep -rnE '(bg|text|border|ring|divide|placeholder)-opacity-[0-9]+' components pages
```

**Pairing algorithm** (per className-chain element, respecting variant prefixes):
- `{VARIANTS}{TYPE}-{COLOR}` + `{VARIANTS}{TYPE}-opacity-{N}`  →  `{VARIANTS}{TYPE}-{COLOR}/{N}`
  - e.g. `focus:ring-primary focus:ring-opacity-50` → `focus:ring-primary/50`
- where `TYPE ∈ {bg, text, border, ring, divide, placeholder}` and the color + opacity share the **same variant chain** (both `focus:`, both `enabled:focus:`, etc.).
- **No-color drop:** if a `{TYPE}-opacity-{N}` has **no** same-chain `{TYPE}-{color}` sibling (e.g. a bare `focus:ring focus:ring-opacity-50`), **delete the opacity class**. The utility falls back to the default color at full opacity.
- Also migrate commented-out `@apply ... ring-opacity-50` lines in `*.module.css` to clear the grep (cosmetic; generates nothing either way).

**Known side effect to eyeball:** the no-color drops turn `focus:ring focus:ring-opacity-50` into a bare `focus:ring` — which in v4 is **1px currentColor** (was 3px blue/50 in v3). See §9 "bare ring".

**Verify:** re-grep returns **0**. In the built CSS, migrated rings carry real alpha, e.g. `.focus\:ring-primary\/50:focus{--tw-ring-color:oklab(... / .5)}`; old `*-opacity-*` produce nothing.

---

## 8. The `tailwind-bootstrap-grid` situation (read before touching grids)

- **v7 generates the same classes** as v5 (`.row` / `.col` / `.col-N` / `.offset-N` / `.container` / `.order-N`) and keeps the `rtl` option — so component grid markup does **not** need to change for the upgrade.
- **v4 core now ships its own `col-<n>` utility** (`grid-column: n`) that did not exist in v3. This **collides** with bootstrap's `.col-*`. The compiled CSS ends up with both:
  ```css
  .col-12 { grid-column:12 }       /* Tailwind v4 core */
  .col-12 { flex:none; width:100% } /* bootstrap-grid v7 */
  ```
- **Harmless when used correctly** (`.row` > `.col-N`): inside a flex `.row`, `grid-column` is inert, so bootstrap's flex/width always wins regardless of cascade order.
- **BREAKS the grid-in-grid antipattern:** a **Tailwind `grid` parent** (`grid grid-cols-3`) with **bootstrap `.col` children** collapses/overlaps under v4 (bare `.col` resolves to `display:initial; flex:1 0` — a flex-child util useless in a grid). **Fix = make that block pure Tailwind grid:** drop `className="col"` (plain grid items), and `col-12` → `col-span-full`. On pif this occurred in exactly **one** file (`admin .../invitations/invitations-form.tsx`); audit with:
  ```bash
  # files mixing a tailwind grid parent with bootstrap col children
  for f in $(grep -rl 'className="col"' components); do grep -q 'grid-cols' "$f" && echo "$f"; done
  ```

> **Strategic note:** this collision is the main reason to *eventually* drop `tailwind-bootstrap-grid` for native Tailwind grid. It's a deliberate ~2,200-site refactor (see `TAILWIND_V4_CLEANUP_PLAN.md` W2). Not required for the v4 upgrade itself.

---

## 9. v4 semantic shifts to audit (the "leftovers")

After the upgrade, these v3 classes still compile but **changed meaning** in v4:

| Item | v3 → v4 change | Action |
|---|---|---|
| **border default color** | `gray-200` → `currentColor` | Handled by the `@layer base` shim (§4). |
| **bare `ring`** | 3px blue-500/50 → **1px currentColor** | Standalone ones (no color) → `ring-3` + explicit color. ~30 on pif. |
| **`outline-none`** | transparent 2px outline → `outline-style:none` | Benign with custom rings; optional → `outline-hidden` for forced-colors a11y. |
| **`focus:focus:ring`** | (pre-existing typo, not v4) | Optional dedup → `focus:ring`. |

Audit greps:
```bash
# bare ring (no width) — render 1px in v4
grep -rnE '[ "'"'"'`:]ring[ "'"'"'`]' components pages | grep -vE 'ring-[a-z0-9]'
# residual broken v3 utilities (should all be 0 post-codemod)
grep -rnE '(bg|text|border|ring|divide|placeholder)-opacity-[0-9]'  components pages   # opacity
grep -rnE 'bg-gradient-to-[trbl]'                                   components pages   # gradients
grep -rnE 'flex-(grow|shrink)'                                      components pages   # flex-grow/shrink
grep -rnE '@tailwind (base|components|utilities)'                   css                # old directives
```

---

## 10. Verification recipe (per app, before merge)

```bash
yarn type-check          # tsc clean
yarn production          # Next build green
```
Then on the built CSS (`.next/static/css/*.css`):
- Grid complete: `col-1..12` (12 distinct `.col-N{` rules) + `offset-0..11` all present.
- Zero `*-opacity-*` rules.
- Border shim present: `*,::after,::before,…{border-color:var(--color-gray-200,currentColor)}`.
- Migrated rings carry `/.5` alpha.
- **EN + AR visual QA** on grid-dense / focus-ring / brand-color surfaces (the only thing automation can't cover).

Merge `chore/upgrade-to-tailwind-4` → `dev` per app after green + visual sign-off.

---

## 11. Gotchas / pitfalls (learned the hard way on pif)

1. **The opacity migration is the hidden 80%.** "Config-only, zero component changes" is WRONG — budget for ~40–56 className edits/app.
2. **Grid-in-grid antipattern** (§8) — silent overlap; not caught by the build, only by eyeballing.
3. **`_document.js.nft.json` ENOENT** on build = corrupted `.next` from back-to-back builds. Fix: `rm -rf .next` then rebuild once.
4. **`tsconfig.tsbuildinfo`** can get committed accidentally — add `*.tsbuildinfo` to `.gitignore`.
5. **`prettier-plugin-tailwindcss` 0.8.0** prints a non-fatal `Cannot find module 'prettier/plugins/angular'` ESLint warning during build. Non-blocking; optional follow-up cleanup.
6. **macOS `grep` has no `-P`** (PCRE); **zsh doesn't word-split unquoted `$vars`** in `for` loops. Use literal lists + ERE when scripting the audits.
7. **Don't re-add** removed deps when touching `package.json`: no Sentry, no `react-quill`, no `tailwindcss@3`, no `tailwind-bootstrap-grid@5`.
8. **`@source inline` is mandatory** for the grid — without it the grid generates only the few classes the scanner happens to see, and grid-heavy pages break in subtle ways.

---

## 12. Applying this to `cyan-basecode`

cyan is the same lineage (tailwindcss 3.4.19, `tailwind-bootstrap-grid ^5.0.1`, HUI v2) → this recipe ports **directly**. Deltas to check:

- **Confirm framework baseline first** (Next 15 / React 18 / HUI v2). Do those parts before v4 if missing.
- **Per-app theme differs** — keep cyan's own `theme.colors` / fonts; only the *structure* of `tailwind.config.js` (removed keys, plugins, flip-plugin fix) transfers.
- **`darkMode`** — replicate whatever cyan uses (pif admin uses `darkMode:'class'` via the bridge).
- **Re-run the §9 audits on cyan** — the bare-`ring` / `outline-none` / grid-in-grid counts will differ; don't assume pif's numbers.
- **Grid usage census first** (`grep -rohE '\bcol-([0-9]{1,2}|auto)\b'`) — cyan's grid surface may differ; confirm there's **no responsive grid** (`col-md-6`) which keeps everything uniform.
- **Same gates:** `yarn type-check` + `yarn production` + EN/AR visual QA; commit `package.json` only (lockfile gitignored); branch per sub-app off `dev`.

---

## 13. Appendix — pif commit ranges (reference implementation)

- **Part 4 (Tailwind v4) on `dev`:** frontend `63cc40b..4830349` · landing `21190c5..685d8a6` · admin `76e0d7f..483ee62`
  - per-app commit structure is **not uniform** — frontend split the codemod into its own commit; landing/admin folded the codemod into the opacity commit:
    - **frontend (3):** config+grid `d71cbf6` → codemod `3d83d2c` → opacity `f2f54fb`
    - **landing (2):** config+grid `50273ec` → codemod+opacity `2413fb6`
    - **admin (2):** config+grid `a713298` → codemod+opacity `7426d8e`
  - ⚠️ `3d83d2c` (the standalone codemod commit) exists **only in the frontend repo** — in landing/admin the codemod edits live inside `2413fb6` / `7426d8e`.
- **Grid-in-grid fix (admin):** `71ada39`
- Diff any of these for the exact, real edits.
