# Plan — Finalize Tailwind v4 + Drop `tailwind-bootstrap-grid`

> For a **new session** to execute. Context: Part 4 (Tailwind v3→v4.3.0 + `tailwind-bootstrap-grid` 5→7) is already merged to `dev` + pushed on all 3 Next apps (frontend/landing/admin). Config layer is clean v4 (`@import 'tailwindcss'`, `@tailwindcss/postcss`, no v3 config keys, `@plugin`+`@source inline` grid, `@layer base` border shim). This plan is **two independent workstreams**. See `UPGRADE_SUMMARY.md` + memory `tailwind-v4-audit` for the audit this came from.
>
> Guardrails (unchanged): yarn (not npm); EN+AR translations same commit; no `console.log`/`dd`; no widening TS to `any`; minimal scope / className-only where possible; branch off `dev`, merge per-app after green + visual QA; don't re-add Sentry/react-quill/`tailwindcss@3`/`tailwind-bootstrap-grid@5`.

---

## Workstream 1 — Finalize v3 leftovers (quick, low-risk, ~1 commit/app)

**Status of the audit:** zero *broken* leftovers (opacity utils, `bg-gradient-to-*`, `flex-grow/shrink`, important-prefix, `@tailwind` directives, v3 config keys all = 0). Only **semantic-shift** items remain. The one with a real visual change is bare `ring`.

### 1A — Standalone bare `ring` → restore v3 focus ring (CORE, ~30 real sites)
v4 renders bare `ring` as **1px currentColor**; v3 was **3px blue-500/50**. Standalone = a `ring` with no `ring-{color}` and no `ring-{width}` in the same className.

Detect:
```bash
grep -rnE '[ "'"'"'`:]ring[ "'"'"'`]' components pages \
  | grep -vE 'ring-(primary|secondary|accent|gray|light-blue|accent-1|error|red|white|black|slate|blue|[0-9])'
```
Known locations (re-grep to confirm; **filter false-positives** — the hits in `components/shared/avatar-cursor-tracker-elegant.tsx` are the word "ring" in comments, NOT utilities — skip them):
- **frontend (≈11 real):** `success/sharebtn-sections.tsx:389`, `join/verify-email-form.tsx:331,397,453,518`, `join/forms/pif/fours-steps/step-2.tsx:961,997`, `shared/forms/custom-file-input-2/custom-file-input.tsx:472,487`, `shared/select/countries-select-new.tsx:183`, `shared/select/nationalities-select-new.tsx:140`
- **landing (≈15 real):** same set + `join/forms/hci/fours-steps/step-2.tsx:961,997`, `join/forms/ewc/fours-steps/step-2.tsx:962,998`
- **admin (≈5 real):** `shared/forms/custom-email-input.tsx:460`, `shared/forms/custom-file-input-2/custom-file-input.tsx:463,478`, `shared/buttons/button-btn.tsx:46`, `shared/select/countries-select-new.tsx:183`

Fix rule (className-only, EN/AR-safe): standalone `ring` → **`ring-3`** (restores 3px) **+ an explicit color**. Recommend the brand `ring-primary/50` (these are form-focus rings in a brand-green app; v3's accidental blue was almost certainly unintended). Use `ring-blue-500/50` only where exact v3 parity is wanted. **Eyeball each** — a couple are `focus-within:ring` on selects.

### 1B — (OPTIONAL) bare `ring` WITH a color sibling — width-only shift
~95 more bare `ring` across the 3 apps that already carry a `ring-{color}` → now 1px instead of 3px (color unchanged, subtle). Convert `ring`→`ring-3` only if you want exact 3px everywhere. Low priority.

### 1C — (OPTIONAL) `outline-none` → `outline-hidden`
Many sites. v4 `outline-none` = `outline-style:none` (vs v3 transparent 2px). Benign — paired with custom rings everywhere; only matters for forced-colors a11y. Skip unless you want exact parity.

### 1D — (OPTIONAL) `focus:focus:ring` dedup (admin, ~22 files)
Pre-existing typo (confirmed at pre-Part-4 commit `76e0d7f`), cosmetic. Codemod `focus:focus:ring` → `focus:ring`. Nice-to-have, not a v4 issue.

**Verify W1:** `yarn type-check` + `yarn production` green per app; re-grep standalone `ring` = 0; quick EN/AR focus-ring eyeball.

---

## Workstream 2 — Drop `tailwind-bootstrap-grid` (big, deliberate, app-by-app)

**Goal:** remove the dependency and the Tailwind-v4 `col-*` namespace collision; replace `.row`/`.col`/`.col-N`/`.offset-N`/`.container`/`.order-N` with native Tailwind utilities. (Why: the v4 core `col-<n>` utility now collides with bootstrap's `.col-*` — harmless in correct `.row` usage but a footgun, e.g. the `invitations-form.tsx` grid-in-grid bug. Plus: unfamiliar to new devs, and a 2nd surprise after the v5→v7 peer break.)

### Census (no responsive grid anywhere → uniform, codemod-able mapping)
| app | files | ~sites |
|---|---|---|
| frontend | 52 | ~311 |
| landing | 60 | ~455 |
| admin | 237 | ~1456 |

### Class mapping — recommended: **flex-faithful** (Tailwind-only, preserves bootstrap gutters)
Our `@plugin` uses the v7 **default 1.5rem gutter** → `px-3` per col + `-mx-3` per row. **First step: capture the exact current generated CSS** (`.row`, `.col`, `.col-6`, `.offset-2`, `.container`) from a current production build so the replacement matches pixel-for-pixel.

| bootstrap | Tailwind-native | notes |
|---|---|---|
| `row` | `flex flex-wrap -mx-3` | negative gutter |
| `col` (auto) | `grow shrink-0 basis-0 px-3` | v7 `.col` = `flex:1 0 0%` |
| `col-N` (1..11) | `w-{N}/12 shrink-0 px-3` | `w-6/12` etc. are default-scale |
| `col-12` | `w-full shrink-0 px-3` | |
| `offset-N` | `ms-[{N/12*100}%]` | **logical** margin (RTL-safe) |
| `order-N` | `order-{N}` (7..12 → `order-[N]`) | |
| `container` | replicate exact bootstrap max-widths via a custom `@utility container {…}` in `css/tailwind.css`, or `mx-auto px-3 max-w-[…]` per breakpoint | audit real usage first (the ~31/31/20 "container" census includes false positives) |

**Alternative (cleaner, more visual-QA): CSS-grid** — `row`→`grid grid-cols-12 gap-x-6`, `col-N`→`col-span-N`, `offset-N`→`col-start-[N+1]`. Changes gutter→`gap` box model. **Decide in the frontend spike.**

### 3 traps — must handle (these are why it's not a blind find/replace)
1. **RTL** — offsets must use logical `ms-*` (`margin-inline-start`), never `ml-*`. Apps are bilingual EN/AR; verify Arabic still mirrors.
2. **Gutters** — bootstrap `.col` has internal padding + `.row` negative margins. The `px-3`/`-mx-3` mapping preserves it; a naive `w-1/2` (no padding) shifts every layout.
3. **`.container`** — bootstrap breakpoint max-widths differ from Tailwind's `container`. Replicate exact values (grab from current built CSS).

### Config + dep changes (per app, after the className codemod)
- `css/tailwind.css`: remove the `@plugin 'tailwind-bootstrap-grid' { rtl: true }` block **and** the 4 grid `@source inline(...)` lines (`row container` / `col-{1..12}` / `offset-{0..11}` / `order-{0..12}`). **Keep** `@import 'tailwindcss'`, `@config`, and the `@layer base` border-color shim. If replacing `.container`, add the custom utility here.
- `package.json`: remove `"tailwind-bootstrap-grid": "^7"`; `yarn install`.

### Execution order (branch `chore/drop-bootstrap-grid` per app, off `dev`)
1. **FRONTEND SPIKE FIRST** (52 files, smallest): write the codemod, validate mapping + RTL + gutters + container on real grid-dense pages (EN **and** AR), lock the exact token strings. This de-risks the other two. Get sign-off before rolling on.
2. **Landing** (60).
3. **Admin** (237) — biggest. `invitations-form.tsx` manual-guests block is already pure Tailwind grid (fixed this session) — use as a reference for the target style.

### Codemod approach
- Scripted (sed/node) for the uniform mappings (no responsive variants → simple). One pass per class type.
- **Manual review for:** `.col` (auto) wrappers, `.container`, the rare cases where `row`/`col`/`container` is a JS variable or string literal (false positives — only touch className/classNames), and any remaining grid-in-grid mixes.
- Post-codemod grep must show **0** residual bootstrap grid classes (allow legit Tailwind `col-span-*`/`order-*` if the grid-mapping uses them).

### Verify per app
- `yarn type-check` + `yarn production` green.
- Built CSS no longer contains bootstrap-grid output (`.col-1{flex…}`, `.row{display:flex…}` gone).
- grep: 0 residual `.row`/`.col`/`.col-N`/`.offset-N` in classNames.
- **EN + AR visual QA** on grid-dense pages (registration forms, admin listings/forms).
- Merge `chore/drop-bootstrap-grid` → `dev` per app after sign-off. Update `UPGRADE_SUMMARY.md` + memory.

### Risk / rollback
Per-app branch; a regressing page is fix-forward or per-app revert. The frontend spike contains the unknowns before the big admin pass.

---

## Sequencing
1. **W1 first** (quick win — restore the ~30 standalone focus rings, 1 commit/app).
2. **W2** (frontend spike → review → landing → admin).
Both independent; W1 can also be folded into each app's W2 branch if you prefer one branch per app.
