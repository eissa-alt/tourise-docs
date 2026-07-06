# Dependency Audit & Cleanup

> **Status:** 🔒 **Security: 3 CVE advisories patched (2026-06-15→18)** — `form-data` High (×3 Next apps) + `phpoffice/phpspreadsheet` floor (both **merged to `dev`** 2026-06-16, see HANDOFF) + **`mtdowling/jmespath.php` `^2.9.1`** (CVE-2026-54133, backend; branch pushed, awaiting review — see §jmespath). 🧹 **Unused-dep sweep: 0 removals** — directors was already scrubbed during the Parts 1–5 upgrade. ✅ The one candidate (`zod` in admin) was investigated and **confirmed load-bearing** (email-builder type resolution) — kept. 🔗 **In-range alignment (2026-06-17):** 4 JS packages floor-bumped to latest-in-range across the 3 Next apps for saudi-forum-11 parity (see §In-range alignment). Last updated 2026-06-17.
>
> **Governance:** pure dependency hygiene + security — no scope/contract/locked-decision change, so **no new D-number**. Honors the no-framework-bump rule (Next / React / Laravel / PHP majors gated) per `CLAUDE.md`. This doc is the directors *record*; the portable *method* is [`DEPENDENCY_HYGIENE_PLAYBOOK.md`](DEPENDENCY_HYGIENE_PLAYBOOK.md). Cross-project sibling record: cyan-basecode `docs/upgrades/DEPENDENCY_AUDIT.md` (this run mirrors cyan's two 2026-06-15 patches).

## Method

- **Unused (JS):** `npx depcheck` per app **+ manual `rg` verification of every flag** (depcheck is wrong in both directions). Two scans were run, because depcheck alone misses both directions:
  1. **forward** (depcheck's "unused" list) — each candidate verified against source + config (`next.config.js`, `postcss.config.js`, `tailwind.css` `@plugin`, `.eslintrc`, `.prettierrc`) + `package.json` scripts before any decision;
  2. **inverse** — for *every* declared dep, count **live** (uncommented) import lines; a dep with zero live imports is dead even if depcheck thinks it's used (the commented-import trap that cost cyan a whole wave).
- **Unused (PHP):** conservative `rg` over `app/ config/ routes/ database/` + `composer why` (Laravel auto-discovery / transitive deps treated as used; only root-only-required + zero-ref = removable).
- **Security:** `composer audit` (PHP) + `yarn audit` (JS) per app.
- **Lockfiles are gitignored** in this lineage (`git check-ignore yarn.lock composer.lock` → ignored), so every change is a **manifest-only** committable diff; floor-bumps / `resolutions` pins are how a safe update is made explicit.

## 🔒 Security fixes — 2026-06-15/16

Two advisories surfaced on the cyan-basecode audit (2026-06-15) and were confirmed present on directors via live `yarn audit` / installed-version checks; both fixed in-range, no major bump.

| Sev | Package | Repo(s) | Advisory | Fix | Branch (off `dev`, not pushed) |
|---|---|---|---|---|---|
| 🟠 High | `form-data` 4.0.5→4.0.6 (via `axios`) | frontend · admin · landing | CRLF injection (npm 1120743) | `resolutions` pin `^4.0.6` | `chore/cve-form-data-resolution` — fe `c3d65ca` · ad `694b101` · la `2672843` |
| 🟡 Floor | `phpoffice/phpspreadsheet` `^1.30.4`→`^1.30.5` | backend | CVE-2026-45034 (patch bypass of CVE-2026-34084, `<=1.30.4`) | manifest floor-bump (`composer require -W`) | `chore/cve-phpspreadsheet-1.30.5` — `0299ff6` |

- **form-data:** `axios`'s `form-data ^4.0.0` range admitted the vulnerable 4.0.5 (installed in all 3 apps). The `resolutions` pin floors it to 4.0.6. `yarn audit` High → **0** on frontend + landing; on admin the High cleared (1 **Moderate** remains = the accepted `insane` residual, see below). Directors ships `axios` in **landing** too, so the pin applies to 3 apps (cyan only needed fe+ad). Gates: `type-check` + `production` green on all 3.
- **phpspreadsheet:** the **installed** tree was already 1.30.5 (gitignored lock floated in-range), so `composer audit` was already clean — this pins the **manifest floor** to firmly exclude 1.30.4 (the gitignored-lockfile trap; see playbook §4). In-range of `maatwebsite/excel ^3.1`, so **not** the gated 1→5 major. Gate: `composer audit` clean + `WorkshopFeedbackTest` 13 passed.

## 🔒 Security fix — `mtdowling/jmespath.php` CVE (2026-06-18) {#jmespath}

A third advisory surfaced **after** the 06-15/16 batch, found on directors' own `composer audit` (not mirrored from cyan). Fixed in-range, no major bump.

| Sev | Package | Repo | Advisory | Fix | Branch (off `dev`, **pushed**) |
|---|---|---|---|---|---|
| 🔴 Code-injection | `mtdowling/jmespath.php` 2.8.0→2.9.1 | backend | CVE-2026-54133 / GHSA-pcw8-m77r-2528 — CompilerRuntime code injection via unescaped function names (`<2.9.1`), reported 2026-06-11 | explicit root `require` floor `^2.9.1` | `chore/cve-jmespath-2.9.1` — `429660c` |

- **Transitive**, pulled by `kreait/firebase-php 7.24.1` (under direct `kreait/laravel-firebase ^6.2`) with constraint `^2.8.0` — so **2.9.1 is already in-range**, just not installed (the gitignored-lockfile trap again: the floated install sat at the vulnerable 2.8.0). No root constraint controlled it, so the fix is an **explicit root require** flooring it to `^2.9.1` — same manifest-pin pattern as `form-data` (resolutions) and `phpspreadsheet` (floor).
- **Isolation verified:** `composer audit` → clean; installed `2.8.0`→`2.9.1`; before/after `composer show -i` diff shows **only** jmespath moved (179→179 packages, no additions/removals, no major pulled). Manifest-only diff (1 added `require` line).
- **Gate:** `php artisan test` → **442 passed, 3 failed**. The 3 failures (welcome-route `/` 403 + avatar-URL-when-image-exists ×2) were **proven pre-existing** — they fail identically on clean `dev` (no jmespath line), and exercise no Firebase/jmespath code path. Zero regressions from the pin. (Backend `pint --test` untouched — manifest-only change, no PHP source, pre-existing style debt per CLAUDE.md.)

## 🔄 Backend in-range floor-align — 2026-06-18

The four backend in-range bumps **deferred** during the jmespath pass, done now. Pure freshness — **no CVE driver** (`composer audit` was already clean post-jmespath). They showed as "behind latest-in-range" only because the gitignored lockfile pinned older versions; this raises the manifest **floor** and reconciles the install.

| Package | Section | From | To (floor) | Installed |
|---|---|---|---|---|
| `guzzlehttp/guzzle` | require | `^7.11` | `^7.12.0` | 7.12.1 |
| `laravel/framework` | require | `^12.60` | `^12.62.0` | 12.62.0 |
| `setasign/fpdi` | require | `^2.6.7` | `^2.6.8` | 2.6.8 |
| `laravel/pint` | require-dev | `^1.29` | `^1.29.3` | 1.29.3 |

- **`composer update <4 targets> --with-dependencies`:** 9 upgrades, 0 downgrades, 0 removals, 0 installs — the 4 targets + 5 transitive (`guzzlehttp/psr7`, `guzzlehttp/uri-template`, `nesbot/carbon`, `ramsey/uuid`, `symfony/polyfill-php83`), **all same-major**. No major pulled; 179→179 packages.
- **Gate:** `composer audit` clean; `php artisan test` → **442 passed**, same **3 pre-existing** failures unchanged (welcome `/` 403 + avatar-URL ×2), **zero new** — framework/carbon/guzzle bumps break nothing. Manifest-only diff (4 lines).
- **Branch** `chore/deps-backend-floor-align` off `dev`, **pushed** (awaiting review) — `86f60cd`.

## 🔗 In-range alignment with saudi-forum-11 — 2026-06-17

Pure in-range hygiene (patch/minor **within current major** only) to keep directors unified with the sibling **saudi-forum-11**, which was just floor-bumped to latest-in-range. Four JS packages — currently **identical across all 3 Next apps** — floor-bumped in each of admin · frontend · landing. **Backend unchanged.** No new deps, no removals, no major/framework bump.

| Package | Section | From | To | Major |
|---|---|---|---|---|
| `axios` | deps | `^1.17.0` | `^1.18.0` | 1.x (unchanged) |
| `react-hook-form` | deps | `^7.77.0` | `^7.79.0` | 7.x (unchanged) |
| `tailwindcss` | devDeps | `^4.3.0` | `^4.3.1` | 4.x (unchanged) |
| `@tailwindcss/postcss` | devDeps | `^4.3.0` | `^4.3.1` | 4.x (unchanged) |

- **Already current, left untouched:** `next` / `@next/bundle-analyzer` `^15.5.19`, `libphonenumber-js` `^1.13.6`. None of the 4 bumped packages are pinned in any app's `resolutions`, so the floor-bumps take effect directly.
- **Manifest-only diff** (lockfile gitignored) — exactly 4 lines changed per `package.json`, sections preserved (tailwind pair kept in `devDependencies`). Installed versions verified post-install: axios 1.18.0 · react-hook-form 7.79.0 · tailwindcss 4.3.1 · @tailwindcss/postcss 4.3.1.
- **Gate green on all 3:** `yarn type-check` + `yarn production` passed.
- **Branches** `chore/deps-align-latest` off `dev`, **not pushed** (awaiting review): admin `e8613b7` · frontend `90bbedc` · landing `7bcb82c`.

This closes the directors side of the saudi ↔ directors in-range alignment.

## 🧹 Unused-dependency sweep — result: 0 certain removals

Directors is **already clean**. The Parts 1–5 upgrade had removed the usual dead weight (Sentry, react-quill, npm `xlsx`→SheetJS CDN, etc.), so depcheck + the inverse live-import scan surfaced **no certain-dead package** in any of the four repos. Declared-dep counts are unchanged:

| Repo | deps | devDeps | total | removed |
|---|---|---|---|---|
| admin | 51 | 24 | 75 | 0 |
| frontend | 40 | 23 | 63 | 0 |
| landing | 40 | 23 | 63 | 0 |
| backend | 21 (req) | 7 (req-dev) | 28 | 0 |
| **Total** | | | **229** | **0** |

Everything depcheck/the scan flagged was a **verified false-positive** (config / script / type-resolution use):

| Flagged "unused" | Verdict | Evidence |
|---|---|---|
| `tailwind-bootstrap-grid` (×3) | KEEP | `@plugin 'tailwind-bootstrap-grid'` in `css/tailwind.css` (v4 grid) |
| `@tailwindcss/postcss`, `postcss-flexbugs-fixes` (×3) | KEEP | `postcss.config.js` plugins |
| `@svgr/webpack` (×3) | KEEP | `loader: '@svgr/webpack'` in `next.config.js` |
| `env-cmd` (×3) | KEEP | every `build`/`start` script |
| `prettier` + eslint toolchain (×3) | KEEP | `.eslintrc` shorthand (`plugin:react/*`, `@typescript-eslint`, `prettier`); `prettier` script |
| every `@types/*` | KEEP | base package is live-imported (e.g. `import mime from 'mime-types'`) |

> **Addendum — 2026-07-06 (supersedes some verdicts above):** the tooling/hygiene + dead-code pass later
> removed several of these once the code that referenced them was deleted. **No longer present** in
> `-admin` / `-frontend`: **`@svgr/webpack`** (the `next.config.js` SVG loader + dead icon assets were
> removed, so the KEEP rationale no longer holds), **`swiper`** (frontend — the swiper-backed sections
> were dropped), and **`filepond-plugin-image-transform`**. Builds stay green. Treat the "KEEP" rows for
> `@svgr/webpack` / `swiper` as historical (accurate at 2026-06-16, changed since). See `HANDOFF.md` →
> "Dead-dependency / dead-code cleanup".

## Differ from cyan — packages cyan removed that **directors keeps** (it actually uses them)

The user's explicit ask: *"report if any from [cyan's] 41 differ."* Cross-mapping cyan's 41 removals against directors, these are **present and live here** (cyan found them dead in cyan's codebase; directors genuinely uses them) → **all KEEP**:

| Package | Where | Why directors keeps it |
|---|---|---|
| `react-circular-progressbar` | fe · ad · la | live in `menu-steps-md.tsx` |
| `react-day-picker` | fe · ad · la | live `DayPicker` in `custom-day-input.tsx` + CSS in `_app.tsx` |
| `validator` (+`@types/validator`) | fe · ad · la | live in many form `step-*.tsx` (admin 9, landing 9, fe 3) |
| `next-cookies` | fe · ad · la | live SSR cookie reads (admin **101** import sites) |
| `react-responsive` | fe · ad · la | live `useMediaQuery` |
| `@vercel/analytics` | fe · la | live `<Analytics/>` in `_app.tsx` (admin: only a **stale commented import**, and not declared in admin — nothing to remove) |
| `@next/eslint-plugin-next` | ad | **wired** in admin `.eslintrc` (`plugins: [..., "@next/next"]`) — cyan removed it as inert; directors' is referenced |
| `setasign/fpdi` | backend | `composer why` → required by `mpdf/mpdf` (transitive) **and** deliberately pinned `^2.6.7` (Part 2). cyan removed it post-D45 (mPDF→Browsershot); directors still uses mPDF (`niklasravnsborg/laravel-pdf`) |

Every other cyan-41 package (FullCalendar suite, `react-query`, `recharts`, `luxon`, `lucide-react`, `tslint`, `js-base64`, `next-build-id`, `react-tiny-popover`, `browser-image-compression`, …) **does not exist in directors at all** — never added in this codebase.

## ✅ Resolved finding — `zod` in admin is **load-bearing, keep it** (2026-06-16)

`zod ^4.3.6` is declared in **admin** `dependencies` and **never imported in app source** — so it *looked* like stray scaffold cruft. **Provenance:** present since the initial scaffold commit (`c54cb70 "add project files"`, 2026-03-12), not added for a feature; `cyan-admin` carries the identical line (shared admin-basecode), admin-only. So we tested removing it — and **the build broke**:

- The admin email editor is live — `components/admin-modules/emails/templates/email-editor-waypoint.tsx` imports `@usewaypoint/email-builder ^0.0.9`, whose exported types are zod-derived.
- On a throwaway branch, `yarn remove zod` (which lets zod fall to the `tailwind-bootstrap-grid`-provided **zod@3.25.76**) made **`yarn type-check` AND `yarn production` FAIL** in the email editor: `Type 'string' is not assignable to type '"Container"'`. email-builder's types only line up against **zod@4**.
- Reverted. **Verdict: `zod ^4.3.6` is a transitive _type-level_ dependency of the admin email editor — keep it.** depcheck was correct not to flag it. Downgrading to `^3` would break the same way (it's the zod@3 types that fail), so the email-builder peer-range "mismatch" (`^1–3`) is cosmetic in practice — the admin code compiles against zod@4's inferred types.

**Lesson (now in the playbook):** a *declared-but-unimported* dep can still be load-bearing via transitive **type resolution**. The build gate is the arbiter — never remove on a source-scan alone. Same `zod ^4` line in **cyan-admin** is likewise load-bearing → **do not remove there either**.

## Other observations (not acted on)

- **`mime-types` is imported but not declared** (`import mime from 'mime-types'` in all 3 apps) — currently resolved transitively (depcheck "missing"). An **add**, not a remove; out of this sweep's scope. Worth declaring it directly later.
- **`@types/swiper` (fe · la)** — `swiper` is live, but modern Swiper bundles its own types, so `@types/swiper` may be redundant. Not certain-dead (a `tsc` check would prove it); parked.
- **No `lint` script** in any Next app — the wired `.eslintrc` toolchain only runs via IDE / manual `npx eslint`, never in build/CI. Kept (all devDeps, low-risk); flagged as a workflow gap.

## Accepted residual (no upstream fix — same as cyan/saudi)

- **admin `insane` ReDoS (Moderate, CVE-2020-26303)** via `@usewaypoint/email-builder > @usewaypoint/block-text`. **No patch available.** Admin-only self-DoS in the email editor. Resolvable only by replacing email-builder — a separate tracked follow-up, not a dependency-hygiene fix. (This is the 1 Moderate that remains in admin `yarn audit` after the form-data High cleared.)

## Deferred backlog — major / framework bumps (dedicated branches only)

Unchanged from the Parts 1–5 record ([UPGRADE_SUMMARY.md](UPGRADE_SUMMARY.md)). Framework majors (Next 15→16 · React 18→19 · already on Laravel 12 / PHP 8.2) and toolchain/library majors stay gated. `phpoffice/phpspreadsheet` 1→5 stays a deferred **non-security** future bump (the 1.30.5 floor handles the CVE).

## Related open follow-ups

- **Gitignored lockfiles** (`yarn.lock` / `composer.lock`) → installs not reproducible/pinned. Project-wide decision still open (commit them, or accept range-floating) — same as cyan.
- **`zod` / email-builder** decision above.
- **email-builder replacement** (`insane` ReDoS) — no upstream fix.
- **Backend `pint --test`** is RED on pre-existing style debt (~390 files, identical before/after) — untouched; don't reformat in a deps PR.
</content>
</invoke>
