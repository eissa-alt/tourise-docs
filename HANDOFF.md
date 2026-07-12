# Handoff — current state

> Rolling pointer, overwritten each session. For the durable record see the per-task `TASK.md`,
> `decisions/LEDGER.md`, and `upgrades/UPGRADE_SUMMARY.md`. Full plan: `upgrades/CYAN_FEATURE_PARITY_MASTER_PLAN.md`.

**2026-07-12 — Fixed `migrate:fresh --seed` (TitleSeeder null bug, ledger D13). Backend `dev` `a6fe3d1`,
pushed.** 6 `TitleSeeder` rows passed `show_in_user_form => null` into a NOT-NULL `boolean default(false)`
column → `SQLSTATE[23000]` crash mid-seed. Fixed the **seeder** (`null` → `false`; `null` meant "not
shown"), not the schema. This was the pre-existing bug the dropped migration-squash recon flagged. Verified:
full `migrate:fresh --seed` clean, 8 seeders green, 12 titles (6 shown / 6 hidden), Pint + Title tests pass.
Not mobile-facing.

**2026-07-12 — Admin HttpOnly token + Next BFF proxy + full CSP (Saudi P2 backport, task 005, ledger
D12). Code DONE, gates green, runtime-verified — committed + pushed (admin `dev` 4 commits
`d95a2e5`→`b006123`; docs `main` `2939d0b`). Real-env browser QA still outstanding before `dev`→`main`.
Plan: `upgrades/CLEANUP_AND_HARDENING_MASTER_PLAN.md` Task 004 (Track B); log:
`tasks/005-admin-httponly-token/TASK.md` (folder 005 — 004 is the dropped squash).**
- **What & why:** the admin bearer was a JS-readable cookie (XSS → account takeover). The Phase-1 fix
  (`af2298b`, secure+sameSite) couldn't close the XSS-read vector — only `httpOnly` can, and only a server
  can set it. So the token now lives ONLY in an **HttpOnly cookie** written by a **Next BFF proxy**; the
  browser never handles it. Un-deferred from Track B now because the basecode is **pre-launch (no clone has
  prod data)**, so the 135-file codemod is cheap to bake into every clone.
- **Landed (admin only, 144 files, net −399 lines):** new `utils/{auth-cookies,server/proxy}.ts` +
  `pages/api/{proxy/[...path],auth/{login,login-confirmation,logout}}.ts`; isomorphic `utils/axios.ts`
  (browser→`/api/proxy`, SSR→direct); provider/withAuth/login+verify onto a JS-readable flag cookie
  (`alt_admin_auth`) + `authenticated` marker; codemod removing 136 dead `cookie.get('token')` reads + 261
  `Authorization: Bearer` headers (proxy injects auth server-side now); **full CSP** in `next.config.js`
  adapted to alt (env origins, reCAPTCHA only, **no iconify** per D5, `'unsafe-eval'` dev-only).
- **Gates:** `yarn type-check` + `yarn production` **green**. **Runtime verified** against a stub upstream
  on `next dev`: login strips token + sets `HttpOnly; SameSite=Strict; Max-Age=6h` cookie, proxy injects
  `Bearer` from the cookie, logout clears both, OTP + multipart streaming + CSP header all confirmed.
- **Mobile:** untouched — admin-web only, `routes/api.php` unchanged.
- **Outstanding:** commit (4 commits) + **real-env browser QA** (live backend login, reCAPTCHA, heaviest
  export/upload through the proxy) before `dev`→`main`. Saudi hotfix-reverted their P2 once over these edges.

**2026-07-11 → 07-12 — Env-var / dead-code cleanup pass (admin + frontend). Committed on `dev`.
Frontend is pushed and in sync with `origin/dev` (`64037eb`). Admin `dev` is 4 ahead of `origin/dev`
(NOT yet pushed) — `f6bcf7b` → `a361586` → `37cf1a1` → `8345f19`.**
- **Admin (4 unpushed commits):** retired baseline env vars that were config-noise, moving the values
  to code constants. `f6bcf7b` drop `NEXT_PUBLIC_LISTING_PER_PAGE_LIMIT` from listing URLs
  (`utils/fetch-data-url.ts`, print-logs). `a361586` move cookie-age env vars → code constants
  (`auth/provider.tsx`, `i18n/provider.tsx`). `37cf1a1` retire `NEXT_PUBLIC_ENV` from 9 `data/*-select.tsx`
  files (incl. `status-types-select`, `sidebar-links`). `8345f19` remove unused `callback_url` /
  `back_link` from `guests` step-4 + `verify-email-form`. Pure config/dead-code hygiene, no behaviour
  change.
- **Frontend (pushed, `dev` @ `64037eb`):** `9a9a850` + `dedb4f6` clean up `utils/axios.ts` (drop unused
  token header/variable). `e75c9bf` remove `@vercel/analytics` dep + imports (`package.json`, `_app.tsx`,
  `yarn.lock`). `64037eb` untrack `.env.production` + add to `.gitignore`.
- **Gates:** admin `yarn type-check` **clean** + `yarn production` **green** (verified 2026-07-12).
  Not mobile-facing (`routes/api.php` untouched). **Admin still needs its 4 commits pushed to `origin/dev`.**

**2026-07-08 — Backend tooling & code-quality chain (task 003, ledger D10). All work items DONE;
committed on `dev` — backend `96413df` (W1, already pushed) + `bb61db9` (W2+W6) + `9741e90` (W5+W8)
+ `de75eed` (W7); docs on `main`. Backend `dev` is 4 ahead of `origin/dev` (W1 pushed earlier). Plan:
`upgrades/BACKEND_TOOLING_CHAIN_PLAN.md`; log: `tasks/003-backend-tooling-chain/TASK.md`.**
- **What landed:** brings the backend's quality chain to parity with the Next-app pass. **W1** —
  `pint.json` (laravel preset + `no_unused_imports` + `ordered_imports`) + one repo-wide Pint baseline
  (172 files, formatting-only) → repo is now **Pint-clean**, gate flips `pint --dirty` → **`pint --test`**.
  **W2** — **Larastan** static analysis at **level 0** + generated baseline (124 real structural
  errors), with a committed **ratchet** (shrink → bump the level toward 6; runs in `composer analyse`/
  `qa`, never the hook). Fixed 1 non-ignorable finding at source (`GuestOtpNotification::$locale`
  redeclared a native type over Laravel's untyped parent). **W6** — composer scripts `lint`/`lint:fix`/
  `analyse`/`test`/`qa` (one-command gate). **W5** — PHP-native `.githooks/pre-commit` runs Pint on
  staged `*.php` + graceful-skips if Pint absent (parity with admin/FE husky+lint-staged), auto-installed
  via `composer install`. **W7** — `.vscode/` **un-ignored + committed** with `[php]`→Pint (fixed an
  inconsistency: admin/FE tracked `.vscode/`, backend gitignored it). **W8** — dropped stale
  `pestphp/pest-plugin` allow-plugin; `composer validate --strict` valid; audit clean. **Rector + CI
  left out** (out of scope). Not mobile-facing (`routes/api.php` untouched).
- **Gates:** `composer qa` = `pint --test` green + `phpstan analyse` **No errors** (baseline-green) +
  `php artisan test` **452 pass / 3 fail** (pre-existing, unrelated). **New backend gate going forward
  is `composer qa`.**

**2026-07-07 (later) — `catch (e: any)` → `unknown` cleanup, closing the "cheap cleanups" phase
(ledger D9). Committed on `dev` (admin `5ceacc3`, frontend `8544c39`) — NOT yet pushed (part of the
same review batch as task 002). All original audit sub-phases ("fix first", "cheap cleanups") are now
complete; "later/opportunistic" is parked — see `tasks/PHASE3_PARKED_TODO.md`.**
- **What landed:** 94 `catch (error: any)` blocks across 82 files (68 admin + 14 frontend) → `catch
  (error: unknown)`. New shared helper `utils/api-error.ts` (`getApiError(unknown) → typed axios
  `ApiErrorResponse | undefined`) in both apps; response-reading catch bodies route through it, log-only
  bodies just re-annotate to `unknown`. Behaviour unchanged (same branches/toasts/status checks). Casts
  added only where an untyped value flows into a typed sink (RHF `setError`, `toast.error`). Gates green:
  `type-check` + lint 0 warnings, both apps. Not mobile-facing.
- **Also this session:** verified the other three "cheap cleanups" items were already done by a prior
  agent (iconify→lucide, 28+2 dead files deleted, commented-`// console.*` swept) — all confirmed clean
  against current code. Wrote **`docs/mobile/MOBILE_NOTICE_AGENDA_DATE_WALL_CLOCK.md`** — an actionable
  notice for the mobile team about the D8 venue-local `date` change (must not TZ-convert agenda `date`).

**2026-07-07 — Date/time (timestamp) DB cleanup + refactor (ledger D7, task 002). Committed on `dev`
(backend `86961dd`, admin `c6ee625` + follow-up `f340a0e`, frontend `5f2c55a`) and `main` (docs
`aeb4528` + `155d94b`) — NOT yet pushed (awaiting review). Full plan + per-step log:
`tasks/002-datetime-db-cleanup/TASK.md`.**
- **Display consistency pass (admin, `f340a0e`):** 34 views switched from `format(new Date(x))`
  (viewer's browser TZ) → shared `formatDateTime` (`Asia/Riyadh`) for real UTC Laravel timestamps
  (listing `created_at`, `registered_at`, session media `created_at`, guest-draft
  `created_at`/`updated_at`). Export-filename timestamps left on `format()`.
- **Agenda-date fix (ledger D8, MOBILE CONTRACT CHANGE):** session/workshop `date` was served as UTC
  `…Z` but entered as naive `datetime-local`, so the admin edit form pre-fill shifted the time −3h on
  every save. Switched all 9 `date` serializations (admin + mobile resources) from `->toISOString()`
  to naive-local `->format('Y-m-d\TH:i:s')` (venue = Asia/Riyadh). No FE logic change (pre-fill +
  `format(new Date())` display self-correct with a `Z`-less string). **Mobile must parse `date` as
  wall-clock, NOT convert to device TZ** — flagged in `docs/mobile/…FOR_MOBILE.html` §24. Backend
  `pint --dirty --test` green.
- **Backend:** date-only columns → real `date` (cast `date:Y-m-d`), datetime columns → `timestamp`
  (cast `datetime`, ISO 8601 UTC), flight times → `string(5)` `HH:mm`. Migrations edited in place +
  `migrate:fresh` (no prod data). Touched `guests` (+ `add_check_in_out_dates`), `invitation_emails`,
  `guest_emails`, `guest_sms`, `automations`, `bulk_prints`, `badge_print_logs`, `history_logs`;
  added casts to Guest/InvitationEmail/GuestEmail/BulkPrint/Automation/HistoryLog; printed-range
  query → `whereBetween` w/ Carbon; 3 `GuestsExport*` binders now format Carbon values; removed 4 dead
  unrouted debug methods from `OperationActionsController` (+ their commented routes).
- **FE + admin:** dropped the react-day-picker modal for cyan's **Cleave masked inputs**. Added
  `cleave.js` + `@types/cleave.js`, `components/shared/forms/masked-date-input.tsx` +
  `masked-time-input.tsx`, and shared `utils/date.ts` (`formatDate` / `formatDateTime`). Every
  `CustomDayInput` site → `MaskedDateInput` (`YYYY-MM-DD`); flight times → `MaskedTimeInput` (`HH:mm`,
  fixes the admin field that still emitted `hh:mm AM`); all active `timeZoneFix()` display → the new
  helpers. TZ conversion happens **at display** (`Asia/Riyadh`) so out-of-KSA users are correct.
  `masked-datetime-input.tsx` deleted (no user-entered datetime in alt). **Kept** `custom-day-input.tsx`
  (unused, for future) + therefore **kept** `timezoneFix.ts` (its only remaining consumer) — a
  deliberate revision of the "delete timezoneFix" plan.
- **Gates:** backend `pint --dirty --test` green, `migrate:fresh` clean, `php artisan test` 452 pass /
  3 fail (same pre-existing ExampleTest 403 + 2 avatar failures — unrelated). Admin + frontend
  `type-check` + `production` **green**. Mobile contract unaffected (guest dates only in Admin
  resources; offline QR `check_in_time` round-trips via the `datetime` cast; `routes/api.php`
  unchanged). No i18n keys moved.

**2026-07-06 (night) — Boolean DB cleanup + refactor, two tracks (ledger D6). Working-tree only on
`dev` across all three app repos — NOT yet committed/pushed (awaiting review). Full plan +
per-step log: `tasks/001-boolean-db-cleanup/TASK.md` + `upgrades/BOOLEAN_REFACTOR_PLAN.md`.**
- **Track A** (mirrors cyan's documented refactor): pseudo-booleans (`yes`/`null`, `yes`/`no`,
  `with_`/`is_`) → real `boolean`s. Migrations edited in place (`string(...)->nullable()` →
  `boolean()->default(false)`) across guests flags, categories (`with_*` + notification fields),
  badges, email configs/templates, automation setups, countries, titles, invitations, guest
  logistics, gates, guest_sms; model `$casts` added; controllers/resources/blade `=== 'yes'` →
  `$request->boolean()` / `=== true`; admin `CustomSwitchInput` → `CustomSwitchInputBoolean` +
  boolean interfaces; frontend join-form radios (`is_saudi`, `require_*`, `valid_visa`) → booleans,
  SSR `=== 'yes'` boundary drop. **Intentional string keeps** (cyan-aligned): CSV `Exports` yes/no,
  input normalization, and the 3-state consent fields `display_photo_in_app` / `photo_consent` /
  `will_attend` / `terms`.
- **Track B** (net-new, beyond cyan): entity `status` (`active`/`blocked`) → `is_active boolean
  default(true)` on ~16 tables (speakers, sponsors, speaker/sponsor labels, zones, areas, gates,
  badges, categories, titles, admins, sms/email templates, invitations, guest_statuses, countries);
  `$casts`/`$fillable`; ~18 controllers `where('status','active')` → `where('is_active',true)` +
  `block()`/`activate()` setters (route names preserved); `Mobile{Speaker,Sponsor}Controller`
  filters; notification senders. Admin: shared `Status` badge → `isActive:boolean`,
  `status-types-select` → `true`/`false` options, all entity listings (`FilterFieldDef key:'is_active'`
  → serializes to `?is_active=`), 8 status forms, `bulk-update-badges-modal`, ~12 interfaces.
- **Excluded (multi-value / process statuses):** `app_notifications`, `login_attempts`,
  `email_attachments`, sms send-state, guest-workflow `status`/`guest_status_id`, mobile guest
  status, `users` (dead `UsersController`), automation `is_sent/is_delivered/is_open/is_clicked`.
  `meeting_rooms` + `smtp_configs` were already boolean `is_active` by design (no change needed).
- **Gates:** backend `pint --dirty` green, `migrate:fresh` clean, `php artisan test` **452 pass /
  3 fail** — all 3 are **pre-existing, unrelated** (confirmed by re-running on a stashed clean tree):
  `ExampleTest` GET `/` → 403, and two avatar tests that assume `display_photo_in_app` defaults to
  `'yes'` (it's nullable, intentionally left a string). Admin + frontend `type-check` + `production`
  **green**. **Mobile contract unchanged** — storage/internal only; no converted-entity `status`
  is exposed in any mobile resource.

**2026-07-06 (late pm, 2) — "Cheap cleanups" pass (admin + frontend), two separate commits each.
(1) Deleted dead files: 28 unreferenced `interfaces/*.tsx` in admin (`f6cffae`) + 2 stale duplicate
copies in frontend (`i18n/link copy.tsx`, `data/area-of-interset-generic-select_.tsx`, `864f7df`).
(2) Removed commented-out `// console.*` debug lines: 115 across 43 admin files (`f66ede8`) + 33 across
11 frontend files (`88ac243`). Pure hygiene, zero behaviour change; all four gates green. Both `dev`
branches pushed. The `zod`-removal and `@iconify/react`-dep items from that phase are moot (zod is
load-bearing; iconify already removed by the lucide migration).**

**2026-07-06 (late pm, 1) — Icon-library unification complete. Both Next apps now use a single icon
library, `lucide-react`; `@iconify/react` (P1) and `@heroicons/react` (P2) are fully removed from
source + `package.json` + `yarn.lock`. All four gates green (`type-check` + `production` on admin &
frontend). See ledger D5.**

**Earlier 2026-07-06 (pm):** Forgot-password unified onto the invite reset-by-token flow (admin +
backend). The whole tooling/hygiene batch + admin email-invite flow is now merged to `main` via PR #1 on
all three app repos. The backend has adopted a `dev` branch — it no longer commits straight to `main`
(see ledger D4).

**Earlier this session (am):** tooling + hygiene pass across the two Next apps (ESLint 9 flat config,
Prettier 3, zero lint warnings, husky + lint-staged, GTM removed) + dead-dependency / dead-code cleanup
+ docs cleanup (dropped the `-landing` app). `origin` is set on all repos
(`github.com/eissa-alt/alt-static-basecode-*`) and each branch tracks + matches its upstream.

## Current SHAs (all pushed, in sync with `origin`)

- `alt-backend` — `dev` = `main` @ `4e1d532` (PR #1 merge). Forgot-password backend at `a8184ca`; admin
  email-invite / `password_mode` **backend** flow at `04001b3` (P2.ST8). **Backend uses `dev`** and PRs
  into `main`, matching admin/frontend. Untouched by the icon migration.
- `alt-admin` — `dev` @ `f66ede8` (**cheap cleanups**, pushed): console-sweep `f66ede8` + dead-file
  delete `f6cffae`, on top of icon P2 `de87b4b` / P1 `d2565d9`. Before that `main`=`ed2e679` (PR #1
  merge), forgot-password repoint `70e646c`, tooling pass `29548e3`, admin-invite **UI** `d3ed5db` /
  `f43543f`. **`dev` is now well ahead of `main`** (icon migration + cleanups all `dev`-only).
- `alt-frontend` — `dev` @ `88ac243` (**cheap cleanups**, pushed): console-sweep `88ac243` + dead-file
  delete `864f7df`, on top of icon P2 `c74b82c` / P1 `3033a18`. Before that `main`=`f6b61e8` (PR #1
  merge), tooling pass `41ae698` + form-shape `default-` prefix rename + a `react-select` → Headless UI
  Listbox select refactor. **`dev` is now well ahead of `main`.**
- `docs` (on `main`) — this handoff refresh + ledger **D5** (previously `37176b7`: stale stack-version
  fix; earlier D3/D4, `-landing` drop / **D2**, husky hook).

## What landed recently

- **"Cheap cleanups" pass** (admin + frontend, hygiene, two commits each): **(1) dead-file deletion** —
  28 unreferenced `interfaces/*.tsx` in admin (`f6cffae`) + 2 stale duplicate copies in frontend
  (`864f7df`); **(2) commented-`console.*` sweep** — 115 lines / 43 files in admin (`f66ede8`) + 33
  lines / 11 files in frontend (`88ac243`). Full-line comment removals only (verified no inline/multiline
  cases); complements the earlier no-console rule (which handled live calls). Zero behaviour change, gates
  green. The other two items from that phase are moot: **`zod`** stays (load-bearing runtime peer dep of
  the email-template editor — removing it crashes the editor); **`@iconify/react`** was already dropped by
  the lucide migration.
- **Icon-library unification → `lucide-react`** (admin + frontend, ledger **D5**): dropped **both**
  baseline icon libs. **P1** removed `@iconify/react` (admin `d2565d9` — 146 conversions / 40 files +
  the event-day DB registry; frontend `3033a18` — 5 files incl. the `bi:tiktok` inline-SVG replacement).
  **P2** removed `@heroicons/react` (admin `de87b4b` — 82 files; frontend `c74b82c` — 13 files) and
  stripped it from `package.json` + `yarn.lock`. Machine-verified 1-for-1 name map (e.g.
  `ArrowTopRightOnSquareIcon`→`ExternalLink`, `PencilSquareIcon`→`SquarePen`, `PaperAirplaneIcon`→`Send`,
  `TrashIcon`→`Trash2`, `DocumentDuplicateIcon`→`Copy`); `className` sizing preserved throughout. Gates
  green both apps; **admin `production` build now run (was outstanding)**. Not mobile-facing.
- **Forgot-password → reset-by-token unification** (admin + backend): new
  `AuthController::forgotPassword()` reuses the `AdminInvite` token machinery + shared `admin_invite`
  blade (EN/AR) behind a public `POST /admin/forgot-password` route; the admin `forgot-password-form`
  now posts `{ email, back_link }` there instead of the legacy `v2/password/forgot` guest flow, so admins
  land on the same `reset-password/[token]` page as invites. **Enumeration-safe** (always returns success
  — a deliberate deviation from cyan). Cyan parity, see **LEDGER D3**. Mobile contract unaffected
  (admin-only, additive route).
- **ESLint 9 flat-config migration** (admin + frontend) + `@next/eslint-plugin-next`; **Prettier 2 → 3**;
  all lint warnings → **0** (autofix, optional catch binding + config `ignoreRestSiblings` /
  `argsIgnorePattern`, scoped `exhaustive-deps` / `<img>` disables each with a `-- reason`).
- **husky + lint-staged pre-commit hook** (admin + frontend): staged `*.{js,jsx,ts,tsx}` → `eslint --fix`,
  other types → `prettier --write`, re-staged. Installed via `prepare: husky`. Verified end-to-end.
- **GTM removed** from both apps (`react-gtm-module` + dead `utils/analytics.ts`).
- **Dead-dependency / dead-code cleanup**: removed `@svgr/webpack` (+ dead icon assets), `swiper`
  (frontend), `filepond-plugin-image-transform`, and many orphaned components/modals; admin swapped its
  legacy Portal modal for a shared `DialogShell`; frontend replaced `react-select` with a Headless UI
  Listbox `ui-select`. **This supersedes the KEEP verdicts in `upgrades/DEPENDENCY_AUDIT.md`** for
  `@svgr/webpack` / `swiper` (see the dated addendum there).
- **Editor settings**: Tailwind `suggestCanonicalClasses` silenced; deprecated `typescript.tsdk` /
  `enablePromptUseWorkspaceTsdk` → `js/ts.tsdk.path` / `js/ts.tsdk.promptToUseWorkspaceVersion`.
- **Docs**: dropped the 4th `-landing` app from all current-state docs (now a **three sub-app** baseline:
  `-backend`, `-admin`, `-frontend` + `docs/`); documented the pre-commit hook; ledger **D2**. Historical
  `upgrades/*` and D1's clone-source SHAs left intact (accurate record).
- **Admin email-invite / `password_mode` flow — merged + pushed** (backend `04001b3`, admin `d3ed5db` +
  `f43543f`): `AdminInvite` model + `admin_invites` / `password_mode` migrations, invite/resend/reset
  endpoints, SMTP-gated password-mode UI + reset-by-token page.

## Gates

- **Admin / Frontend:** `yarn type-check` + `yarn production` **green**; ESLint **0 warnings**. The
  pre-commit hook enforces Prettier/ESLint autofix on every commit.
- **Backend:** `pint --dirty --test` **green** on the forgot-password change. Run `php artisan test`
  before the next backend push. (Repo isn't Pint-clean at baseline — always use `pint --dirty`.)
- **SMTP smoke test: DONE** — invite + reset-password email delivery verified against the active DB SMTP
  config (`DynamicSmtpService`).

## Next / outstanding

- **Push admin `dev`** — 4 unpushed env-var/dead-code cleanup commits (`f6bcf7b` → `8345f19`, 07-12);
  gates green (`type-check` + `production`). Frontend + backend + docs are all in sync with `origin`.
- **Browser QA** — forgot-password + invite create paths + reset-by-token page; plus the migrated
  listings + sidebar accordion (LTR/RTL) from the earlier P5.trim / cyan-parity session, which compiled
  green but were never browser-tested. **Add a visual pass on the migrated icons** (both apps) — the
  swaps compiled + built green but weren't eyeballed for glyph/size parity.
- **Merge `dev` → `main`** on admin + frontend when ready — the icon migration (P1+P2) **and** the cheap
  cleanups currently live only on `dev`; `main` is still at the PR #1 merge. (User asked to leave the PRs
  for now.)
- **`catch (X: any)` → `unknown`** — ✅ **DONE** (ledger D9, admin `5ceacc3` / frontend `8544c39`, on
  `dev`). Closed the "cheap cleanups" phase.
- **Phase 3 (later/opportunistic) — PARKED** by user, tracked in `tasks/PHASE3_PARKED_TODO.md`:
  `utils/cont-list.ts` cross-repo drift (real: the two apps have different country lists),
  `xlsx`/chart.js dynamic-import bundle wins, and `useFetch` adoption (5 sites vs ~64 hand-rolled).
- **Mobile team notice** — `docs/mobile/MOBILE_NOTICE_AGENDA_DATE_WALL_CLOCK.md` written; the mobile team
  still needs to be actually told + confirm receipt before the D8 change releases.

> Pint note (updated 2026-07-08, ledger **D10**): the backend is now **Pint-clean** (task 003 added
> `pint.json` + a repo-wide baseline, `96413df`). The gate is the **full `pint --test`** (`composer
> lint`), no longer the old `pint --dirty` workaround. Full backend gate = **`composer qa`** (`pint
> --test` + `phpstan analyse` + `php artisan test`). A `.githooks/pre-commit` hook also runs Pint on
> staged PHP (installed via `composer install`).
