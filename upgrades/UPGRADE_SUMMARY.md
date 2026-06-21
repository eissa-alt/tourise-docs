# Directors Upgrade — Execution Summary (Parts 1–4)

> Replay of the saudi-forum-11 / cyan-basecode playbooks onto `pif-directors-gathering` as the clone baseline. See [BASELINE_DECISION.md](BASELINE_DECISION.md) for the why and `~/.claude/plans/reflective-crafting-blum.md` for the plan. Executed 2026-06-05. All work on `dev` (per-part feature branches merged in). yarn.lock / composer.lock are gitignored in this lineage, so commits carry `package.json` / `composer.json` only.

## Status at a glance

| Part | Scope | Result |
|---|---|---|
| **1** | OWASP round-1 + Next 12→14 + React 17→18.3.1 + framer 11 + swiper 12 + remove Sentry + admin xlsx→SheetJS CDN + remove react-quill + backend phpspreadsheet/commonmark pins | ✅ **merged to `dev` + pushed** (all 4 repos) |
| **2** | Next 14→15.5.19 + js-cookie 3.0.8 + backend Symfony 7.4.12 + setasign/fpdi 2.6.7 | ✅ **merged to `dev` + pushed** (all 4 repos) |
| **3** | Headless UI v1→v2.2.10 | ✅ **merged to `dev` + pushed** (all 3 Next apps) — admin modal click-outside smoke still recommended (see below) |
| **4** | Tailwind v3→v4.3.0 (+ `tailwind-bootstrap-grid` 5→7) | ✅ **merged to `dev` + pushed** (all 3 Next apps) — EN/AR visual QA still recommended (see below) |
| **5** | Backend Laravel 11→12 (`^12.60`, v12.61.1) + PHPUnit 10→11 + zipstream 4→5 — clears `CVE-2026-48019` | ✅ **merged to `dev` + pushed** (backend) — `composer audit` clean (see below) |

## Merged commit ranges (`dev`)

- **Part 1:** backend `94e671d..29e12e9` · admin `60a4d1b..3c43e8a` · frontend `16f65e4..b33372b` · landing `c03cf83..4b79542`
- **Part 2:** backend `29e12e9..d17a9f6` · admin `3c43e8a..e56245d` · frontend `b33372b..8f04c5b` · landing `4b79542..702aa00`
- **Part 3:** frontend `8f04c5b..63cc40b` · landing `702aa00..21190c5` · admin `e56245d..76e0d7f`
- **Part 4:** frontend `63cc40b..4830349` · landing `21190c5..685d8a6` · admin `76e0d7f..483ee62` — commit split differs per app (merged `--no-ff`): frontend = config+grid `d71cbf6` → codemod `3d83d2c` → opacity `f2f54fb` (3 commits); landing = config+grid `50273ec` → codemod+opacity `2413fb6` (2); admin = config+grid `a713298` → codemod+opacity `7426d8e` (2). The standalone codemod SHA `3d83d2c` exists **only in frontend**.
- **Part 5:** backend `d17a9f6..83f5aae` (work `3b34049` on `chore/laravel-12-upgrade`, merged `--no-ff`). **Pushed: YES** (`origin/dev` @ `83f5aae`).

Each part was independently verified (type-check + production build green; osv-scanner clean of in-scope advisories) before merge.

## ⏸️ Held / open items

1. **Admin Headless UI v2 — MERGED (2026-06-05), but modal click-outside smoke still recommended.** Now on `dev` (`e56245d..76e0d7f`, build-green, 0 dot-notation survivors). The **44 modals** (`Dialog.Overlay`→`DialogBackdrop`, 43 in `components/shared/modals/` + 1 in forms) still want a runtime click-outside-to-close / Esc / focus-trap smoke in **EN and AR**. v2 keys click-outside off `<DialogPanel>`; if a modal doesn't close on backdrop click, wrap its *content* (not the centering wrapper) in `<DialogPanel>` (post-merge fix-forward).

2. **Tailwind v4 — MERGED to `dev` + pushed on all 3 (2026-06-06); EN/AR visual QA still recommended.** The earlier NO-GO was reversed: **`tailwind-bootstrap-grid@7.0.0`** (published 2026-01-18) declares `peerDependencies: { tailwindcss: "^4" }`, emits the same `.row`/`.col-N`/`.offset-N`/`.container` classes, and keeps the `rtl` option — so no off-grid rewrite was needed. What landed per app:
   - **Config (4 files):** `package.json` (tailwindcss 3→**4.3.0**, +`@tailwindcss/postcss`, grid **5→7**), `postcss.config.js` (→`@tailwindcss/postcss` + `postcss-flexbugs-fixes`), `css/tailwind.css` (`@import 'tailwindcss'` + `@config` + `@plugin 'tailwind-bootstrap-grid' { rtl: true }` + `@source inline(...)` to force the full grid + a `@layer base` border-color compat shim so v4's `currentColor` default doesn't change borders), and a v3-key cleanup in `tailwind.config.js` (dropped `mode:'jit'`/`corePlugins`/`future`/`experimental`/`variants{}`).
   - **Components:** the official `@tailwindcss/upgrade` codemod (gradient/shadow/rounded/important/negative-value renames) **plus** a manual `*-opacity-*` → `/modifier` migration the codemod does **not** handle (frontend 40, landing 48, admin 56 utils). className-only edits; no logic/RTL/translation changes.
   - **Verified (work + independent verify agent, each fresh clean rebuild):** `yarn type-check` + `yarn production` green on all 3; grid intact (`col-1..12` + `offset-0..11` = 12/12 each); **zero** `*-opacity-*` left in source or built CSS; migrated rings render real `/.5` alpha.
   - **Merged + pushed** `--no-ff` to `dev`: frontend `4830349` · landing `685d8a6` · admin `483ee62` (tips `f2f54fb`/`2413fb6`/`7426d8e`). `chore/upgrade-to-tailwind-4` branches retained locally.
   - **Remaining = human visual QA only (fix-forward on `dev`):** EN **and** AR pass on grid-dense + brand-color surfaces. (The standalone focus-ring shift is now fixed — see item 6.) Also worth a cleanup follow-up: the codemod bumped `prettier-plugin-tailwindcss` on frontend/landing, which prints a non-fatal `prettier/plugins/angular` ESLint warning during build.

3. **Backend `laravel/framework` CVE-2026-48019** (CRLF in default email rule) — ✅ **RESOLVED in Part 5.** Upgraded `^11.0`→`^12.60` (installed v12.61.1; audit confirms `<12.60` was affected, so the floor is firmly 12.60). Done as its own `chore/laravel-12-upgrade` branch, merged `--no-ff` to backend `dev` (`3b34049` / merge `83f5aae`) and **pushed** (`origin/dev` @ `83f5aae`). Details:
   - **composer.json = 3 edits:** `laravel/framework ^12.60`, `phpunit/phpunit ^11.5.3`, `stechstudio/laravel-zipstream ^5.7`. Plus `phpunit.xml` migrated to PHPUnit-11 `<source>` schema and `.phpunit.cache` added to `.gitignore`. `composer.lock` is gitignored in this lineage, so the commit carries `composer.json`/`phpunit.xml`/`.gitignore` only.
   - **Forced transitive bumps (lock only):** `maennchen/zipstream-php` 2.4→3.1.2, `mpdf/psr-http-message-shim` 1.0.0→2.0.1, `psr/http-message` 1.1→2.0, `nunomaduro/collision` 8.5→8.9.4. Carbon was already on 3.x. The legacy app skeleton (`app/Http/Kernel.php`) was retained — L12 supports it, no slim-skeleton migration.
   - **Verified:** `composer audit` clean; `routes/*` byte-identical to pre-upgrade (mobile contract untouched); `Zip::create()` facade smoke ok; `php artisan test` = **442 passed**. The **3 remaining failures are pre-existing**, proven by downgrading to L11 and re-running (they fail identically): `ExampleTest` (`/` does `abort(403)` by design) + 2 avatar tests (`AttendeeTest`/`QrScannerTest`) that depend on `env('PUBLIC_STORAGE_URL')` + the `display_photo_in_app` privacy toggle, null in the test env. **Out of scope to fix here.**
   - **Pre-existing repo health:** `./vendor/bin/pint --test` is RED on `dev` (390 files, identical before/after) — untouched style debt, separate cleanup.

4. **Mobile API smoke** — `routes/api.php` is byte-unchanged through Parts 1–2 (verified); Symfony 7.4.12 + reverb/firebase/intervention all resolve. A live mobile auth/chat/push/sessions smoke is still recommended before a release (not exercisable from the dev box).

5. **Accepted residuals (no upstream fix, same as saudi/cyan):** admin `insane@2.6.2` (Waypoint editor, admin-only self-DoS) + `xlsx@0.20.3` ×2 (SheetJS CDN tarball, scanner false-match). Documented, not fixable.

6. **Tailwind v4 cleanup W1 (focus rings) — DONE, MERGED to `dev` + PUSHED (2026-06-07); EN/AR visual QA deferred by user.** v4 renders a width-less `ring` as 1px (v3 = 3px). Fixed in two passes, both className-only (no translation keys), both merged `--no-ff` and pushed to `origin/dev`:
   - **W1A — standalone (colorless) bare rings → `ring-3` + brand `ring-primary/50`.** 30 live sites (fe 11 / la 15 / ad 4). Branch `chore/finalize-tailwind-v4-rings`. Merges: fe `26aab24` · la `ba8e889` · ad `6c1f06d`.
   - **W1B — width-less rings that already carry a color → bump width to `ring-3` (color-preserving).** This was the bigger, more-visible regression (every text input/select/checkbox/button focus ring was 1px): fe 21 / la 19 / ad 42 lines. Surfaced by user QA. Each control keeps its own color (accent/amber, primary, light-blue, error/red…); 1 live admin `@apply` in `styles.module.css` fixed; dead/commented lines + `langSwitcher copy.tsx` left untouched. Branch `chore/finalize-tailwind-v4-rings-w1b`. Merges: fe `2fa17d6` · la `34c6ff8` · ad `2f4e89b` (commits `d366237`/`fdba4c0`/`4b93a23`).
   - **W1 finalize (admin only, 2026-06-07): admin input ring + W1D.** Branch `chore/admin-input-focus-ring`, merged `--no-ff` → admin `5f470ef` (commits `57e1272` ring, `e801a97` W1D).
     - **Admin input focus ring:** admin `custom-input.tsx` only changed border on focus via `focus:border-accent` — but **`accent` is NOT a theme color** (admin defines only `primary` `#3B82F6`), so that class is a dead no-op; the visible blue focus was the `@tailwindcss/forms` default. Added a real **3px `ring-primary/50`** (brand blue) so admin inputs match the public site's ring treatment. ⚠️ Note: several admin focus-ring colors (`accent`, `light-blue`, `accent-1`, `secondary`) are likewise **undefined no-ops** — pre-existing, not a v4 regression (no-ops in v3 too); those rings take the forms-plugin/currentColor color. Out of W1 scope.
     - **W1D:** deduped the pre-existing `focus:focus:` typo (28 live `focus:focus:ring-3`→`focus:ring-3`); 4 dead commented occurrences left as-is.
   - **Verified:** type-check + production build green on all 3 (every pass); built CSS confirms `ring-3` = `calc(3px + …)` and `ring-primary/50` renders real `/.5` blue. `origin/dev` current (0 ahead) on all 3.
   - **W1 is COMPLETE** (1A ✅ · 1B ✅ · admin input ring ✅ · 1D ✅). **Not done — intentionally:** 1C (`outline-none`→`outline-hidden`) is benign (forced-colors a11y only), skipped. **W2 (drop `tailwind-bootstrap-grid`, ~2,200 sites) remains parked** — see `TAILWIND_V4_CLEANUP_PLAN.md`.

## Guardrails applied (do not regress)

Sentry removed (CLAUDE.md rule #3 updated); never re-add `@sentry/nextjs` / `sentry/sentry-laravel` / `react-quill` / junk `tailwind` / `tailwindcss-dir` / npm `xlsx`. Keep React-18/Next/Swiper patterns. React stays 18.3.1 (React 19 deferred). Headless UI floor is v2 (all 3 Next apps merged). **Tailwind floor is v4.3.0 with `tailwind-bootstrap-grid@7` once Part 4 merges** — keep the `@plugin`+`@source inline` grid registration and the `@layer base` border-color shim; do not re-add npm `tailwindcss@3` or `tailwind-bootstrap-grid@5`.
