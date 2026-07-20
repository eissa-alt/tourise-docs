# Decision Ledger

Append-only record of **durable, cross-task locked decisions** for alt-static-basecode. Numbered
`D1…Dn`, never renumbered. A task-local choice lives in that task's `TASK.md`; a decision that
outlives the task gets promoted here. This is the source of truth when a decision and the code/docs disagree.

> Format: `D<n> — <date> — <one-line decision>` + a short why + where the detail lives.

---

## D1 — 2026-06-21 — cloned from pif-directors-gathering baseline

`alt-static-basecode` was cloned from the `pif-directors-gathering` upgrade-then-clone baseline
(source SHAs: backend `8745150` · admin `0f65026` · frontend `5e3fee2` · landing `55fd6b7` · docs `3cbca75`).
Inherited stack: **Next 15 / React 18.3.1 / Headless UI v2 / Tailwind v4 / Laravel 12** (Sentry removed,
OWASP-hardened). The frozen lineage record under `../upgrades/` documents what this baseline already includes.

- **What the baseline already includes:** [../upgrades/UPGRADE_SUMMARY.md](../upgrades/UPGRADE_SUMMARY.md)
- **Why directors was the chosen baseline:** [../upgrades/BASELINE_DECISION.md](../upgrades/BASELINE_DECISION.md)

## D2 — 2026-07-05 — dropped the `-landing` app

The directors baseline carried a 4th sub-app, `alt-static-basecode-landing` (Next 15 marketing site).
It is **not needed for this project** and has been dropped — `alt-static-basecode` is now a **three
sub-app** baseline (`-backend`, `-admin`, `-frontend`) plus `docs/`. Current-state docs were updated to
match; the frozen lineage under `../upgrades/` (and D1's clone-source SHAs) still mention `-landing` as
an accurate record of the baseline it came from.

## D3 — 2026-07-06 — unified admin forgot-password onto the invite reset-by-token flow

Admin "forgot password" now reuses the **same token machinery as the admin invite** instead of the
legacy `v2/password/forgot` guest endpoint. `AuthController::forgotPassword()` issues a one-per-email
`AdminInvite` token, emails the shared `emails.admin_invite.{en,ar}` blade (different subject only) via
a public `POST /admin/forgot-password`; the admin `forgot-password-form` posts `{ email, back_link }`
there, landing the admin on the same `reset-password/[token]` page as invites. This brings alt to
**cyan parity** on the reset flow, with **one deliberate deviation**: the endpoint is **enumeration-safe**
— it always returns success and only sends mail if the admin exists (cyan validates `exists:admins,email`,
which leaks account existence). The new route is **admin-only and additive**, so the mobile contract is
unaffected. Backend `a8184ca` / admin `70e646c` (both merged via PR #1). Detail: `HANDOFF.md`.

## D4 — 2026-07-06 — backend adopts the `dev` → PR → `main` workflow

The backend repo historically committed straight to `main` (it had no `dev` branch, diverging from
admin/frontend). It now uses **`dev`** as its working branch and merges to `main` via PR, matching the
other two app repos and CLAUDE.md's "work on `dev`, never push to `main`" rule. This resolves the
"backend branch convention" open item from the prior handoff. (`docs/` remains `main`-only — it is a
docs-only sibling repo with no app build/branch flow.)

## D5 — 2026-07-06 — lucide-react is the single icon library (dropped @iconify/react + @heroicons/react)

Both Next apps carried **two** icon libraries from the baseline (`@iconify/react` and
`@heroicons/react`). They are now unified on **`lucide-react`** and both old deps have been removed
from `package.json` + `yarn.lock`. The migration ran in two phases against a machine-verified
heroicon/iconify → lucide name map (P1: iconify removal incl. the `bi:tiktok` inline-SVG replacement;
P2: heroicons → lucide). All icon swaps are 1-for-1 (`className` sizing preserved), so this is a
zero-behaviour-change refactor — no icon is used by the mobile contract (admin/frontend only). Gates
green on both apps (`type-check` + `production`). Admin `de87b4b` (P2) / frontend `c74b82c` (P2),
stacked on the P1 lucide commits. Detail: `HANDOFF.md`.

## D6 — 2026-07-06 — real booleans over string pseudo-booleans; `status` → `is_active`

The baseline stored many flags as strings: `yes`/`null` and `yes`/`no` toggles (`is_saudi`,
`with_share`, `prefilldata`, …) and 2-value `status` (`active`/`blocked`) columns. These are being
converted to **real booleans**. Two tracks: **(A)** the `yes`/`no`/`null` + `with_`/`is_` flags —
this mirrors the **cyan** reference, which already did and documented it
(`115-cyan-basecode/.../docs_old/BOOLEAN_REFACTOR_*.md`); **(B)** a **new** conversion cyan never
attempted — strictly 2-value `status` columns become **`is_active boolean default(true)`**.
Multi-value process statuses (`app_notifications` Pending, `login_attempts` failed,
`email_attachments`, `sms_templates` send-state, guest workflow `guest_status_id`, mobile guest
`accepted`/`invited`) are **excluded**. Migrations are edited **in place** + `migrate:fresh` (no prod
data). The `/api/mobile/*` contract is unaffected (storage/internal only; mobile already sends
booleans and its speaker/sponsor resources don't expose `status`). Plan +
detail: [../upgrades/cleanup-hardening/BOOLEAN_REFACTOR_PLAN.md](../upgrades/cleanup-hardening/BOOLEAN_REFACTOR_PLAN.md) /
[../tasks/001-boolean-db-cleanup/TASK.md](../tasks/001-boolean-db-cleanup/TASK.md).

## D7 — 2026-07-07 — real date/time column types + cyan masked date input (no more Unix-string dates)

Dates/times were stored as **Unix-epoch strings** (day-picker fields: `getUnixTime()` +
`zonedTimeToUtc(…)/1000`) mixed with `Y-m-d H:i:s` datetime strings (`Carbon::now()` fields) in the
**same** `string` columns. Converted to proper types: date-only → **`date`** (cast `date:Y-m-d`,
API/forms `YYYY-MM-DD`), datetime → **`timestamp`** (cast `datetime`, ISO 8601 UTC), time-only kept
as **`string(5)` `HH:mm`** (matches cyan `meeting_room_slots`). Columns edited **in place** +
`migrate:fresh` (no prod data; same playbook as D6). FE/admin drop the react-day-picker modal for
cyan's **Cleave masked inputs** (`masked-date/-time/-datetime-input.tsx` + shared `utils/date.ts`
`formatDate`/`formatDateTime`); TZ conversion happens **at display** (`Asia/Riyadh`) so users outside
KSA are handled correctly. **`custom-day-input.tsx` is kept** (unused, for future custom cases) and —
revising the original plan — **`timezoneFix.ts` is kept too** because it is that component's only
remaining dependency (matches cyan). Mobile contract unaffected: guest dates live only in **Admin**
resources; the offline QR `check_in_time` write round-trips through the new `datetime` cast and
`routes/api.php` is unchanged. Gates green: backend `pint --dirty --test` + `migrate:fresh` +
`php artisan test`; both Next apps `type-check` + `production`. Detail:
[../tasks/002-datetime-db-cleanup/TASK.md](../tasks/002-datetime-db-cleanup/TASK.md).

## D8 — 2026-07-07 — agenda `date` is venue-local wall-clock (mobile contract change)

Follow-on to D7. Session/Workshop `date` (a `dateTime` column, cast `datetime`) was serialized with
`->toISOString()` (UTC `…Z`) while being **entered** via a native `datetime-local` (naive wall-clock,
no TZ). Because the API emitted UTC, the admin edit form's `data.date.slice(0,16)` pre-filled the
input with the **UTC** clock (`11:30` for a `14:30` Riyadh event), so opening a session/workshop and
saving **silently shifted the time −3h** (the Riyadh offset). **Decision (mirrors cyan, which never
UTC-converts these): treat agenda `date` as venue-local (Asia/Riyadh) wall-clock end-to-end.** All 9
resources (`AdminSessionsResources`, `AdminWorkshopResource`, Mobile `SessionList/Detail`,
`FavoriteSession`, `WorkshopList/Detail`, `RegisteredWorkshop`, nested in `SpeakerResource`) now emit
`->format('Y-m-d\TH:i:s')` (naive, **no `Z`**). No FE code change needed: the admin `.slice(0,16)`
pre-fill and `format(new Date(date))` display both become correct for every viewer (a `Z`-less string
parses as local, and format renders in local — the shift cancels). The `datetime` cast + naive
`datetime-local` submit already round-trip through the app's `Asia/Riyadh` timezone. **Mobile contract
change (flagged in `docs/mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.html` §24):** mobile must parse
`date` as wall-clock and NOT convert to the device timezone. Audit timestamps
(`created_at`/`updated_at`, `check_in_time`, etc.) stay UTC ISO 8601 — only the scheduled agenda
`date` is venue-local. Gates: backend `pint --dirty --test` passed; isolated `SessionsTest` /
`WorkshopFeedbackTest` green (the one combined-filter search failure is a pre-existing test-isolation
flake, passes in isolation and cannot be affected by a serialization-format change). Detail:
[../tasks/002-datetime-db-cleanup/TASK.md](../tasks/002-datetime-db-cleanup/TASK.md).

## D9 — 2026-07-07 — caught errors are typed `unknown`, read via the `getApiError` helper

Closes the "cheap cleanups" phase. Every `catch (error: any)` in both Next apps (94 blocks across 82
files) was changed to `catch (error: unknown)`. Bodies that read the axios error now go through a new
shared helper **`utils/api-error.ts`** — `getApiError(error: unknown): ApiErrorResponse | undefined`
(returns `error.response` when `isAxiosError`, else `undefined`) — so `error?.response?.data?.*` reads
become `getApiError(error)?.data?.*` with real types instead of `any`. Log-only bodies
(`console.error(error)` / `throw error`) are simply re-annotated to `unknown`. This satisfies
CLAUDE.md's "no widening to `any`" rule and gives one canonical place to evolve the API-error shape.
**Going forward, new code must use `catch (error: unknown)` + `getApiError`, never `catch (e: any)`.**
`@typescript-eslint/no-explicit-any` stays **off** globally (unchanged) — this was a targeted burn-down,
not a rule flip. Commits: admin `5ceacc3`, frontend `8544c39` (both on `dev`, unpushed pending review).
Gates green: `type-check` + lint 0 warnings, both apps.

## D10 — 2026-07-08 — backend gate is `pint --test` (repo is Pint-clean); backend tooling chain adopted

The backend was **not** Pint-clean at baseline, so the gate had been the workaround `pint --dirty`
(format only changed files; a repo-wide run churned ~170+ unrelated files). Task 003 (backend tooling
chain) closes that: an explicit **`pint.json`** (laravel preset + `no_unused_imports` + `ordered_imports`)
plus **one repo-wide Pint baseline** (commit `96413df`, 172 files, formatting-only) made the repo
Pint-clean. **Decision: the backend format gate is now the full `pint --test` (`composer lint`), not
`pint --dirty`.** Alongside it the chain added: **Larastan** static analysis at **level 0** (`bb61db9`)
with a generated baseline (124 real structural errors) and a **committed ratchet** (shrink to zero →
bump the level toward 6; runs in `composer analyse`/`qa`, never in the hook); **composer QA scripts**
(`lint`/`lint:fix`/`analyse`/`test`/`qa`); a **PHP-native pre-commit hook** (`.githooks/pre-commit`,
`9741e90`) that runs Pint on staged `*.php` and graceful-skips if Pint is absent (parity with the
admin/FE husky+lint-staged hook); and `.vscode/` **un-ignored + committed** with `[php]`→Pint
(`de75eed`) — fixing an inconsistency where admin/FE tracked `.vscode/` but the backend gitignored it.
Rector + CI were considered and left out (Rector = optional one-off in the cleanup plan; no repo has CI).
**Going forward the backend quality gate is `composer qa` = `pint --test` + `phpstan analyse` +
`php artisan test`.** Detail: [../tasks/003-backend-tooling-chain/TASK.md](../tasks/003-backend-tooling-chain/TASK.md).

## D12 — 2026-07-12 — admin bearer token is HttpOnly via a Next BFF proxy (Saudi P2 backport)

The admin stored its Sanctum bearer in a **JS-readable** `token` cookie (read by `cookie.get('token')`
across ~136 client sites), so any XSS in the admin could exfiltrate it → full account takeover. The
Phase-1 fix (`af2298b`, `secure`+`sameSite:'lax'`) hardened transport/CSRF but **could not** close the
XSS-read vector — `httpOnly` can only be set server-side. **Decision: adopt Saudi Forum 11's Point 2 —
the token lives ONLY in an HttpOnly cookie set by a Next.js BFF proxy; the browser never handles it.**
Un-defers Task 004 from Track B of `CLEANUP_AND_HARDENING_MASTER_PLAN.md` (user, 2026-07-12) — done now
because the basecode is **pre-launch with no clone carrying prod data**, so the large 135-file codemod is
cheap to bake into every future clone. What landed: `utils/{auth-cookies.ts,server/proxy.ts}` +
`pages/api/{proxy/[...path],auth/{login,login-confirmation,logout}}.ts`; isomorphic `utils/axios.ts`
(browser→`/api/proxy`, SSR→direct Laravel); `auth/provider.tsx`+`withAuth.tsx`+login/verify forms moved
onto a JS-readable **flag cookie** (`alt_admin_auth`) + an `authenticated` marker; a codemod removing all
dead `cookie.get('token')` reads (136) and `Authorization: Bearer` headers (261); and a **full CSP** in
`next.config.js` adapted to alt (env-derived origins, reCAPTCHA only — **no iconify** per D5, no Maps/Fonts,
`blob:` for print-js, `'unsafe-eval'` dev-only). Cookie is `HttpOnly; SameSite=Strict; Secure(prod);
Max-Age=6h`. **Not mobile-facing** — admin-web only, `routes/api.php` untouched, mobile keeps its own
`MobileAuthController` flow. Gates green (`type-check` + `production`); BFF behavior verified at runtime
(login strips token + sets HttpOnly cookie, proxy injects Bearer from the cookie, logout clears both, OTP
+ streaming + CSP header all confirmed). **Real-env browser QA (live backend login, reCAPTCHA, heavy
export through the proxy) is still outstanding before `dev`→`main`** — Saudi hotfix-reverted their P2 once
over the streaming/CSP edges. Detail: [../tasks/005-admin-httponly-token/TASK.md](../tasks/005-admin-httponly-token/TASK.md)
(folder `005`; implements the plan's "Task 004 / Track B").

## D13 — 2026-07-12 — fix TitleSeeder null → `migrate:fresh --seed` restored

`php artisan migrate:fresh --seed` was **broken on `dev`**: 6 `TitleSeeder` rows passed
`show_in_user_form => null`, but that column is a NOT NULL `boolean default(false)` (D6 boolean refactor)
and is cast to boolean on the model — so the insert threw `SQLSTATE[23000] Column 'show_in_user_form'
cannot be null` and seeding died at Title (Country/Admin/GuestStatus/Category ran first). This was the
pre-existing bug the dropped migration-squash recon surfaced (see `tasks/004-migration-squash/TASK.md`
closing note); tasks 001/002 gates had run `migrate:fresh` **without** `--seed`, so it went unnoticed.
**Decision: fix the seeder, not the schema** — `null` meant "not shown", which for a NOT-NULL boolean is
`false`; the column + cast are correct as designed. Changed the 6 `null` → `false`. Verified: full
`migrate:fresh --seed` clean, all 8 seed-path seeders green, 12 titles seed (6 shown / 6 hidden / 0 null),
Pint + Title tests pass. Backend `dev` `a6fe3d1`. Not mobile-facing (seed data only). No other seeder in
the run path had the same null-into-bool pattern.

## D14 — 2026-07-12 — sensitive registrant files are private + served via signed URLs (Saudi P1 backport)

Registrant PII files — `guests.personal_image` (photos) and `guests.document_copy` (passport/ID copies)
— were written to Laravel's **`public` disk** and handed out as **raw, unauthenticated, CDN-cacheable
URLs** (`PUBLIC_STORAGE_URL/personal_image/…`), so anyone with or guessing a URL could fetch someone's
passport. **Decision: adopt Saudi Forum 11's Point 1 — sensitive files live on a `private` disk
(`storage/app/private`, never web-served) and are delivered only through short-lived signed URLs.**
Un-defers the plan's Task 005 / Track B (user, 2026-07-12); done now because the basecode is pre-launch
with no clone carrying prod data (squash/migration of live files would otherwise complicate it). What
landed: `private` disk in `filesystems.php`; new `GuestDocumentController` (`signedUrl()` +
signature-validated `stream()` with a `basename()` traversal guard, type allow-list, `Cache-Control:
no-store`); a `signed`-middleware route `GET /api/files/guest-doc/{type}/{file}` (`guest.doc.stream`);
uploads (incl. the **mobile self-service avatar** in `MobileAuthController`) repointed to `private`;
admin resource URLs → signed (30-min TTL) and **mobile `avatar` → signed (24-h TTL)**; 16 server-side
read-backs (badges/PDF/social-card/email-photo across 7 files) repointed from
`base_path('public/storage/…')` to `Storage::disk('private')->path(…)`; an idempotent
`guests:migrate-docs-to-private --dry-run` command (no-op on fresh clones, kept for clones with data +
a CDN-purge reminder); 2 stale phpstan-baseline `env()` ignores removed. **Dual TTL by decision:** admin
30 min vs mobile 24 h so app caches survive a session. **MOBILE CONTRACT CHANGE** — `avatar` is now a
signed, expiring URL (same field/type, bounded lifetime); mobile must re-fetch after expiry, not build
the URL itself → flagged in `docs/mobile/MOBILE_NOTICE_PRIVATE_AVATAR_SIGNED_URL.md`; **hold `dev`→`main`
until mobile acks.** Public assets (sponsor/speaker/badge/media/publication/attachment images) stay
public by design. Gates: `composer qa` green (`pint --test` + phpstan **No errors** + tests **452/3
pre-existing** — the 2 avatar failures confirmed to fail on the clean parent too, so no regression);
`migrate:fresh --seed` clean; runtime verified (private file streams 200 via valid signature, 403 on
tamper/no-sig, 404 on traversal, 404 at the old public path). Detail:
[../tasks/006-private-document-storage/TASK.md](../tasks/006-private-document-storage/TASK.md).

## D15 — 2026-07-13 — fix two Tailwind v4 regressions (error focus-ring + rtl:space-x-reverse)

Backport of Saudi Forum 11's `docs/upgrades/FIX_TAILWIND_V4_REGRESSIONS.md` — two v4-upgrade regressions
that alt's own v3→v4 pass missed (alt did the *normal* focus-ring restore, ledger D-era `TAILWIND_V4_CLEANUP_PLAN`,
but not these). Both className-only, no logic change. **Fix 1 — error focus-ring → `/50`:** v4 dropped
`ring-opacity-*`/`--tw-ring-opacity`, so a bare `focus:ring-red-500` / `focus-within:ring-error` on
error-state inputs rendered at full opacity (harsh solid ring) vs the soft `/50` normal ring. Carried the
opacity on the color class (`…/50`) — admin 11 files (commit `5d99b43`), frontend 5 files (`052f16f`).
Decorative rings that already had `/50` (e.g. the PIF step-2 Trash2 button) intentionally left alone.
**Fix 2 — drop `rtl:space-x-reverse`:** v4 rewrote `space-x-*` to logical properties
(`margin-inline-start/end`) that already flip under `dir="rtl"`, so `rtl:space-x-reverse` now *double*-flips
— RTL horizontal spacing landed on the wrong side. Deleted it everywhere (nothing replaces it) — admin 124
occ / 69 files (`aadadf8`), frontend 25 occ / 9 files (`721d458`). **Method note:** the removal is a
className-only token delete; an early scripted attempt corrupted indentation via a global whitespace
collapse and was fully reverted before redoing it surgically (token + one adjacent space only). Gates:
`type-check` + `production` green on both apps. Not backend/mobile-facing. **Visual EN/AR QA still pending**
(soft red ring on invalid inputs; RTL spacing on checkboxes/radios/back+share buttons/toolbars) — the one
thing automation can't confirm.

## D16 — 2026-07-13 — consolidate storage-URL env vars to a single source of truth

Collapsed the redundant/inconsistent storage-URL env vars across all three apps onto **framework-native
hosts**. Plan + full detail: [../upgrades/STORAGE_URL_CONSOLIDATION_PLAN.md](../upgrades/STORAGE_URL_CONSOLIDATION_PLAN.md).
Pre-launch (no prod data / CDN cache / shipped mobile), so the aggressive path — drop vars, change values,
no byte-identical-URL guarantee needed — was fine; the emitted URLs came out identical anyway.

**End state:** backend keeps **zero** `PUBLIC_STORAGE_URL*` vars (public URLs via
`Storage::disk('public')->url()` → `config/filesystems` → `APP_URL.'/storage'`); admin keeps **one**
(`NEXT_PUBLIC_STORAGE_URL` = storage **root**) + `utils/storage.ts` deriving `/uploads`, `/attachments`,
`/{module}` paths; frontend keeps **zero** (its var was comment-only dead). Sensitive registrant files stay
on the private disk + signed `*_url` (D14) — never rebuilt from an env var.

**Landed (on `dev`, unpushed):** FE `89c1ce3`; admin `b5bb5b2`→`9137fd9`→`fd628cd` (+ tracked `.env.example`);
backend `58ca08c` (new public `social_card_image_url`) + `5cebb86` (46 `env('PUBLIC_STORAGE_URL2')` sites /
28 files, incl. 7 mobile resources, → `Storage::disk('public')->url()`; self-healing sites →
`rtrim(...url(''),'/')`; phpstan baseline pruned 45→18 env ignores, masking nothing). Byte-identical output
verified via tinker (bare + leading-slash) → **mobile contract unchanged, no ack needed.**

**Fixed en route:** the `social_card` see-more URL had a wrong path (`/social_card` vs `/uploads/social_card`)
— now correct from the API. `visa_copy`/`issued_visa` confirmed **dead** (no column; upload allow-lists
`document_copy` only) so no URL added. **Deliberately deferred (separate correctness item, not env-var work):**
guest `custom-file-input{,-3}.tsx` still rebuild a public `/storage/uploads/{field}/` URL for files that now
live on the **private** disk (the `/upload` endpoints return `data` only) — likely a broken preview; fix by
returning a signed `url` from those endpoints. Tracked in the plan's follow-up.

**Gates:** FE + admin `type-check` + `production` green; backend `composer qa` green (`pint --test` + phpstan
**No errors** + tests **452 pass / 3 fail** — the same pre-existing ExampleTest-403 + 2 avatar failures,
confirmed identical on the stashed parent → no regression) + `migrate:fresh --seed` clean. **User owns the
gitignored `.env` edits** (drop the retired vars; retarget `NEXT_PUBLIC_STORAGE_URL` to the root).

> **Addendum 2026-07-17 — three corrections to the above. All pushed now (the "unpushed" note is stale).**
>
> 1. **The refactor missed the Blade email templates.** `5cebb86` swept `app/` only, so **22
>    `env('PUBLIC_STORAGE_URL2')` refs across 8 email views survived** (`otp/{en,ar}`,
>    `notify_guest/{en,ar}`, `password_reset/{en,ar}`, `partials/{header,footer}-poster`). When the var was
>    then dropped from `.env` (`4dfdca9`), `env()` returned null and **every email poster URL rendered as
>    `nullemails-config/…` — broken banners in all outgoing mail**. Repointed to
>    `\Storage::disk('public')->url()` in **`a9a1ed4`**; byte-identical, views compile (`view:cache`).
>    Lesson: sweep `resources/` as well as `app/` when retiring an env var.
> 2. **"Zero refs" only became true later.** `c1606a5` removed the last dead commented
>    `PUBLIC_STORAGE_URL` handlers from `GuestsExportView`. Verified zero across
>    `app/ config/ routes/ resources/ database/`.
> 3. **"`visa_copy`/`issued_visa` confirmed dead" is superseded by D18** — they were never dead, just
>    unfinished. They now have columns and full persistence.

## D17 — 2026-07-17 — one tracked env template per app: `.env.example_prod`

Unified how env templates are named, tracked and shaped across all three apps, so a clone gets a complete,
accurate template for free instead of hand-carrying files.

**Convention:** each app tracks **`.env.example_prod`** — a production-shaped template holding only
**live** vars, placeholder values, **no secrets**. `.env` / `.env.local` / `.env.production` stay gitignored
and are carried/created per environment (DevOps creates `.env.production` on deploy; its absence is why
`yarn production` can't run locally — expected, not a fault).

- **Backend:** `.env.example2` → **`.env.example_prod`** (`c7dd2ee`), retired `PUBLIC_STORAGE_URL*` +
  `APP_DEBUG=false` (`4dfdca9`). `.env.example` stays the Laravel-stock file. **Audited all 60 vars against
  Laravel 12.62: nothing unsupported.** Note the app deliberately runs on the **old** var names
  (`CACHE_DRIVER`, `BROADCAST_DRIVER`) because `config/` still reads those — do **not** "modernise" to L12's
  `CACHE_STORE`/`BROADCAST_CONNECTION` without changing `config/` too, or they'll be silently ignored.
- **Admin:** `.env.example` → **`.env.example_prod`** (`a5e83e6`), `NEXT_PUBLIC_ENV` moved to the top
  (`e79e537`), structure unified with `.env.local` (`6f5ecdc`, `0dcf74a`). Down to the 6 live vars.
- **Frontend:** had **no** tracked template at all — added one (`27bad95`, `a22bd5b`) documenting the 5 live
  vars.
- **Cookie-age vars → code constants** (frontend parity with admin `a361586`): `NEXT_PUBLIC_LANG_COOKIES_AGE`
  (`7248f39`), `NEXT_PUBLIC_{,REMEMBER_}TOKEN_COOKIES_AGE` (`b5df5d3`, doc comment `220e65e`). Identical in
  every environment, so they're `LANG_COOKIE_AGE_DAYS=30` / `TOKEN_COOKIE_AGE_DAYS=1` /
  `REMEMBER_TOKEN_COOKIE_AGE_DAYS=7` in code now, not env.
- **`CLONE_CHECKLIST` corrected** (docs `2b118d5`): it claimed the prod template was gitignored and must be
  carried by hand — it's tracked (placeholders only), so only `.env` itself is carried.

**Known gap (accepted):** frontend `_app`/`_document` read `NEXT_PUBLIC_GTM`, but the old env files set
`NEXT_PUBLIC_GOOGLE_TAG_MANAGER` — a name mismatch, so **GTM has been dormant, never firing**. The template
now documents the correct name; wiring it up (or removing the GTM blocks) is a separate task.

## D18 — 2026-07-17 — guest document + day fields are first-class in the basecode

Three guest fields had UI but no working data layer. Completed all of them rather than leave half-built
features that fail silently or 500.

- **`visa_copy` / `issued_visa` (`00fe02a` → `4883f9d`):** the public join form has `visa_copy`; the **admin
  guest create/edit forms have both** as real uploads. But `/upload-document` allow-listed only
  `document_copy` (→ **422 "failed to verify path name"**), and there was **no column, no `$fillable`, no
  save** — an uploaded visa hit the private disk and was then **silently dropped**. Widened both allow-lists
  + `GuestDocumentController::TYPES`, added the columns (mirroring `document_copy`), wired `store()` /
  `storeGuest()` / `updateGuest()`, and emit signed `*_url` (private disk, D14).
- **`days` (`ef218f6`):** was a **phantom** — `$fillable` + an index() `JSON_CONTAINS(days,…)` filter + an
  export column + a dashboard breakdown, but **no clone except `98-pif-2026` ever added the column**.
  `GET /admin/guests?days=X` returned **500** (`Unknown column 'days'`). `DashboardStats`/`GuestsExportView`
  were already guarded (`Schema::hasColumn` / ternary) — which is what revealed the field was *intentionally
  opt-in per clone*. **Decision: ship the column in the basecode** (`json` nullable, mirroring pif-2026's
  migration) so every clone gets it. **Still has no writer** — all 3 write sites stay commented and no UI
  submits it, so it reads NULL until a clone wires them up.
- **`json_decode(null)` guards (`ef218f6`):** `days` **and** `interests` were unguarded → a PHP 8.2
  deprecation on *every* guest response. The migration alone does **not** fix this — the deprecation fires on
  the null **value**, not the missing column, and both fields are nullable. Guarded with the ternary already
  used in `GuestsExportView:92`; output unchanged.
- **Factories repaired (`9042919`):** `Guest::factory()` threw `Unknown column 'status'` — it still set the
  free-text `status` column retired in the guest-status refactor (now the `guest_status_id` FK). Nothing
  caught it because the feedback tests use `Guest::create()` directly. Also wired
  `category_id => Category::factory()` (**new `CategoryFactory`**) since `category_id` is NOT NULL and always
  was — so the factory could never stand alone despite three sibling factories declaring
  `'guest_id' => Guest::factory()`.

**Gates (all):** `pint` + phpstan **No errors** + `migrate:fresh --seed` clean + tests **452 pass / 3 fail**
(same pre-existing ExampleTest-403 + 2 avatar). **Not mobile-facing** — `routes/api.php` untouched.

## D19 — 2026-07-18 — guest-drafts: capture abandoned registrations (own RBAC feature)

The admin carried a `guest-drafts` UI across clones but its **backend was never built** (no clone had it —
verified against pif-directors-gathering, gfeai-v2, etc.), so all three screens 404'd. Ported the complete
backend from **deve-go `60fe949`** (`draft-guests` branch) and finished the UI. Task + file-by-file port:
[../tasks/008-guest-drafts-port/TASK.md](../tasks/008-guest-drafts-port/TASK.md).

**What it is:** a registrant who fills step 1 and requests an OTP but never completes is upserted into a new
`guest_drafts` table (keyed by email); the draft is **deleted on successful registration**. So the table is,
by definition, everyone who started and didn't finish — a follow-up/lead-recovery list plus drop-off
diagnostics (OTP sent/verified/attempts, email vs phone). New: migration, `GuestDraft`, `GuestDraftResource`,
`GuestDraftsController` (index/show/export), `GuestDraftsExport`. Capture hooks are **additive** in
`AuthController` (`saveGuestDraft()` in email/phone `Verification`; mark-verified in the `Confirmation`s) +
`GuestsController::store()` (delete on complete). `guest_drafts` is a **self-contained new table** — it does
not touch the `guests` schema, so blast radius on existing behaviour is nil.

**Durable decisions:**
1. **Build, not remove.** Real purpose + a complete, safe-to-port reference. (The earlier "guest-drafts is a
   dead stub" note in the storage plan §4a is superseded.)
2. **Dedicated `guest_drafts` RBAC permission** (`view`/`export`/`see_more`) in
   `app/Support/AdminPermissions.php`, **enforced on the 3 routes via `admin.can`** — so this PII (people who
   never finished) is grantable independently of `guests_listing`. Note this is *stricter* than
   `guests_listing`, whose routes have no `admin.can` gating (frontend-only) — a deliberate deviation.
3. **`personal_image` served as a signed URL** (private disk, D14), not deve-go's public rebuild.
4. **Capture more than the reference did.** deve-go dropped several step-1 fields. Here the frontend OTP
   payload (`VerifyEmailForm.formData`) also sends **gender/title_id/personal_image**, and the backend
   additionally captures **`category`** (frontend sends the slug → resolved to `category_id`) and
   **`invitation_token`**. Employee-ID + Days rows were removed from the see-more modal (never populated).

**Known limitation:** the pif **four-step** form has no invitation-token prop, so its drafts don't capture
`invitation_token` (one-step forms do). Separate wiring if needed.

**Landed (pushed):** backend `7a96707`, admin `270a60d`, frontend `a8a94ec`. Admin listing already used the
modern `ListingFilters` stack, so deve-go's separate `search-guest-drafts.tsx` was **not** ported.

**Gates:** pint + phpstan **No errors** + `migrate:fresh --seed` clean + tests **452/3** pre-existing; admin +
frontend `type-check` + build green. In-browser QA confirmed capture (incl. signed photo, category via slug,
invitation token) and delete-on-completion. **Not mobile-facing.**

## D20 — 2026-07-19 — dropped the dead `days` guest column (supersedes D18's ship-it call)

D18 shipped `guests.days` on the theory a clone would wire the writer. A re-audit this session confirmed
it stayed a **phantom**: no writer anywhere (the registration store and every `Guest::create`/`update`
omit it; the 3 write sites remained commented), with read-only consumers only — the admin
`JSON_CONTAINS(days,…)` filter, the dashboard "by days" stats, the export column, and the admin resource
— all against an always-NULL column. Cross-checked the sibling clone **`122-gfeai-v2`**: same dead column
there too, populated only by a demo seeder and **superseded by a new `forum_days` field**, so `days`
carries no live meaning in the lineage. **Decision: remove it fully** — column + `$fillable` + filter +
stats + export cell/heading + resource field + the commented writes — lockstep across all three repos,
including the orphaned `days` / `days_want_to_attend` / `day1-3` translations (EN+AR). **Kept:** the live
`guest_drafts.days`, the `event_days` module, and the frontend countdown `days` label (a timer string,
unrelated). Backend `4899cfd`, admin `c4f86c5`, frontend `e2da469`. Gates: pint + phpstan **No errors** +
`migrate:fresh --seed` clean + tests **457/3** pre-existing; admin + frontend `type-check` green.

## D21 — 2026-07-19 — GTM: keep in frontend (correctly wired), never in admin

Closes the D17 "GTM dormant" gap. **Admin: no GTM at all** — verified zero component code and no GTM env
var in either `.env.example_prod` or `.env.local`; nothing to remove. **Frontend: keep it** — `pages/_app`
+ `_document` read `NEXT_PUBLIC_GTM` (via `@next/third-parties/google`), and that variable now ships in
**both** the tracked `.env.example_prod` and the local `.env.local`, **empty by default (disabled)** so a
clone just drops in its `GTM-XXXX`. The old `NEXT_PUBLIC_GOOGLE_TAG_MANAGER` name mismatch that made it
dormant is already gone. No code/env changes were required — this entry records the decision and the
verified state.

## D22 — 2026-07-19 — Task 007: API response unification onto the standard envelope

Every API controller now returns the standard envelope from the 006 `ApiResponse` trait
(`{ success, status, message, data, meta? }` / `{ success:false, status:'failed', message, data, errors? }`),
via `BaseApiController::apiSuccess`/`apiError`. Rolled out in tiers: **admin (Tier A/B)** landed earlier this
session; **mobile (Tier C)** completes it — all `mobile/*` controllers migrated (`MobileAuth`, `MobileEventDay`,
`MobileSpeaker`, `MobileSponsor`, `MobileAttendee`, `MobileSession`(+`Feedback`), `MobileWorkshop`(+`Feedback`),
`MobilePublication`, `MobileMediaCenter`, `MobileQr`, `MobileRoom`, `MobileNotification`, `MobileChat`).

**Durable decisions:**
1. **Mobile break is accepted + documented.** Payloads that were flat/scalar/root-level now live under `data`.
   The per-endpoint delta is [../mobile/RESPONSE_SHAPE_DELTAS.md](../mobile/RESPONSE_SHAPE_DELTAS.md) (flipped to
   **IMPLEMENTED**), the "adapt later" artifact required by the Task 007 formula.
2. **`AppConfigController` left unwrapped** (`/app-config`, `/app-config/version`) — config documents the Flutter
   client deserializes wholesale, wrapping adds churn with no unification value. Flagged in delta §18.
3. **`status` keeps legacy values** (`"success"`/`"failed"` or the endpoint's existing custom value) so any
   superset reader survives; `success`+`message` are additive on every response.
4. **`routes/api.php` unchanged** — body refactor only, so the route contract (also the mobile contract) is intact.
5. Two listing-only controllers (`GuestEmailLogsController`, `InvitationEmailLogsController`) keep extending
   `Controller` to avoid a `private applyFilters()` collision with `BaseApiController`; they carry the full
   envelope via `->additional([...])` instead.

**Gates:** pint + phpstan **No errors**; tests **457/3** (the 3 are pre-existing D14 signed-avatar/env failures,
not from this work). Backend feature tests updated in lockstep with each controller. **Remaining:** mobile-team
ack of the deltas, then backend `dev` → `main`.

## D23 — 2026-07-19 — gate scanning is a first-party admin feature (standalone "agent admin" retired; new `scanning` RBAC feature)

On-site gate scanning was an **out-of-repo standalone web client** (the "agent admin"), reached via a
separate `loginAgent` and dual-prefix (`/admin/*` **and** no-`/admin`) scan endpoints that Task 010 had
frozen. `108-tasama` and `112-pif-partners-forum-demo` had already pulled the scanner **into** their admin
CMS keyed off an `admins.type='gate'` column — but ALT dropped `type` in favour of RBAC, so it was the
deliberate outlier with no in-admin scanner. **Decision: port scanning into the ALT admin as a first-party,
RBAC-gated feature and retire the standalone client + its shims.** Task + phase-by-phase detail:
[../tasks/011-scan-into-admin/TASK.md](../tasks/011-scan-into-admin/TASK.md).

**Durable decisions:**
1. **New `scanning` RBAC feature** (`['view']`) in `app/Support/AdminPermissions.php`, **distinct from
   `gates`/`areas`/`scans`.** `gates`/`areas`/`scans` = *manage/report* gates in the CMS; `scanning` =
   *operate* a gate (the live scan UI). A "gate agent" is just a role granting `scanning` (usually nothing
   else) — **no `type` column, no separate login**. They log in normally and the dashboard shows the scanner
   because `checkFeaturePermission('scanning', user)` is true.
2. **Data scope is enforced server-side** (closes the 108/112 gap where any token scanned any gate).
   `GatesController::deniesGateScope()` gates `showAgentSide`/`setup`/`start`/`pause`/`scan`: the target gate
   must match `admin.gate_id` (once bound by `setup`) and/or fall inside `admin.area_id`; **super-admin
   short-circuits**.
3. **Endpoints modernized + un-frozen** into a `/admin/gate-scan` group behind `admin.can:scanning`
   (`gates`, `gates/{id}`, `gates/{id}/setup|start|pause|scan`, `search-guests`, `scans/{id}/image`,
   `scans/{id}/guest`). The retained offline-sync endpoints (`attend`, `guest-data-offline`,
   `guest-data-sync`, `guests-printed-since`) moved behind the same feature. **Dropped:**
   `AuthController@loginAgent` + route, the four no-`/admin` scan aliases, and the dangling
   `validate-check-in/{regNumber}` route (handler gone since Task 010, no callers). This **lifts Task 010's
   RENAME_MAP §F freeze.**
4. **Camera lib swapped, dep count flat.** 108/112's `react-web-qr-reader` (unmaintained, React 16/17) →
   **`html5-qrcode`** (maintained, framework-agnostic, dynamic-imported so it never runs server-side); also
   dropped `react-lottie` (their scan-pulse dep) for a CSS pulse — net new deps ≈ 0.
5. **Recovery flow completed.** 108/112 only uploaded a badge photo for an unrecognised QR; ALT's
   `wrong-qr-recovery-modal` also **searches by name and links the guest to the orphan scan**
   (`search-guests` → `scans/{id}/guest`).
6. **Not mobile-facing.** The scanner is the web iPad client, not the Flutter app; the retired/renamed URIs
   were confirmed absent from the mobile contract, so `routes/api.php`'s mobile surface is intact.

**Deferred (still open):** the recommended `scans.gate_id` FK — the port ships on the existing `gate_name`
string link (`Gate::scopeWithUniqueCount`); and **live browser-QA + the RBAC/scope manual matrix** (needs a
running stack + camera), validated so far only by feature tests + type-check/build.

**Landed (on `dev`):** backend `211e17d` (scanning feature + endpoints + `GateScanTest`) → `cd66c21`
(`admins/select` filters by `scanning`); admin `1c87ff0` (gate-scan UI port + nav + `/scans` icon +
`type=gate` cleanup + EN/AR). **Gates:** backend `composer qa` green (pint + phpstan + tests incl.
`GateScanTest`); admin `yarn type-check` + `next build` green (`yarn production` needs the gitignored
`.env.production`).

## D24 — 2026-07-20 — `routes/api.php` brought to the cyan RESTful standard (grouped + `admin.can:` gated + `whereUuid` + `toggle-status`)

The legacy admin surface of `routes/api.php` was 966 lines of mostly-flat, ungated, non-RESTful routes
(vs cyan's 559-line grouped/gated/RESTful shape). Task 010 rewrote it as a **hard cutover** — no
alias/back-compat window; backend + admin + frontend callers moved together. Task + rename map:
[../tasks/010-api-routes-cleanup/TASK.md](../tasks/010-api-routes-cleanup/TASK.md) +
[../tasks/010-api-routes-cleanup/RENAME_MAP.md](../tasks/010-api-routes-cleanup/RENAME_MAP.md).

**Durable decisions:**
1. **Every admin resource folded into a `Route::prefix('admin/<res>')->group()` block**, static routes
   before `/{id}` wildcards, `->whereUuid('id')` on every UUID param.
2. **RESTful rename is a hard cutover** — `/x-select` → `/x/select`, `/guests-new` → `POST /guests`,
   `/guests-update/{id}` → `PUT /guests/{id}`, `/invitations-list/{id}` → `/invitations/{id}/list`, etc.
   Category updates went `POST` → `PATCH`. Admin API client + frontend public `countries/select` +
   `titles/select/{cat}` repointed in lockstep.
3. **`block/{id}` + `activate/{id}` replaced by a single `PATCH /{id}/toggle-status`** outright (no legacy
   pair kept); `toggleStatus()` added to the 14 controllers that only had `block`/`activate`.
4. **`admin.can:<feature>` gating on every admin group**, cross-checked against `AdminPermissions::CATALOG`
   (Super-Admin short-circuits, deny-by-default); per-action perms on writes; dashboard gated per-widget.
   **Left ungated on purpose:** all `-select`/`select-all` + `categories/slug` (feed cross-module dropdowns
   / guest forms — gating them would 403 an admin working in a *different* feature).
5. **Dead code removed:** dead comments, duplicate registrations, 7 orphaned `GuestsController` methods,
   the dead `guests-status-*` block, and 5 zero-caller ops/queue endpoints (+ `OperationActionsController`,
   `QueueController`).
6. **`mobile/*` is untouched** — the mobile contract (also `routes/api.php`) is intact; no `mobile/*` URI
   changed, so no `RESPONSE_SHAPE_DELTAS` row was needed. (The scanner/agent surface was frozen by Task 010
   then un-frozen + modernized by Task 011 / D23.)
7. **Final close-out (2026-07-20):** the last two non-RESTful, ungated, zero-caller leftovers —
   `POST /admin/guests-upload-zip` + `POST /admin/match-guests-images` (bulk guest-image upload/match) —
   were folded into the guests group as `POST /admin/guests/upload-zip` + `POST /admin/guests/match-images`
   behind `admin.can:guests_listing,edit`. The four offline-sync endpoints (`attend`, `guest-data-offline`,
   `guest-data-sync`, `guests-printed-since`) were **left at their URIs** — a deliberate Task 011 decision
   (D23), kept behind `admin.can:scanning`.

**Landed (on `dev`):** backend `4cf7036` (Tier 0+1 dead-code/endpoint cleanup) → `c5a3a31` (Tier 2 RESTful
cutover + prefix groups + `whereUuid` + `toggle-status`) → `9328d65` (Tier 4 `admin.can` gating) → `68723ee`
(dead ops/queue removal); admin `e36b384` (API client repoint + `toggle-status`); frontend `53d42e0`
(public `countries/select` + `titles/select`). **Route count 418 → 384.** **Gates:** backend `composer qa`
green (pint + phpstan **No errors** + tests **465/3** — the 3 are the pre-existing `ExampleTest` `/`→403 +
two avatar signed-URL fails, not from this work); admin + frontend `yarn type-check` green. **Remaining:**
manual smoke test per renamed/gated feature (needs a running stack + role matrix).

## D25 — 2026-07-20 — LinkedIn **automatic** "Share on LinkedIn" completed for the per-category social share

ALT already shipped the **manual** half of the category social-share feature (`with_share`,
`share_poster{,_ar}`, `share_type` = `manual|automatic`, `share_text_{en,ar}`, blade social card, admin form
section, bulk-update modal), but the **`automatic`** path the admin form advertised was never wired. Task 012
completed it, ported **best-of-both** from cyan (P37.4) + hci and adapted to ALT conventions. Task:
[../tasks/012-linkedin-auto-post/TASK.md](../tasks/012-linkedin-auto-post/TASK.md).

**Durable decisions:**
1. **Scope = Tier A only** (LinkedIn auto-post). ALT keeps its **blade** social card; cyan's Social Card
   **Layout Designer** / JSON document-rendering engine (Tier B) was explicitly **out of scope**.
2. **Per-category LinkedIn app credentials** — two nullable columns `linkedin_client_id` /
   `linkedin_client_secret` on `categories` (additive migration `2026_07_20_000001`), only consulted when
   `share_type = automatic`; unset → the OAuth endpoints 422. Creds round-trip through `update()`
   `$request->only()` + `CategoriesResources` (the gap cyan had). Not added to `bulkUpdateSocialMedia` — an
   app id/secret is inherently per-category, set individually in the form.
3. **LinkedIn API surface stays on v2** (`/v2/ugcPosts`, `/v2/assets?action=registerUpload`, `/v2/userinfo`,
   header `X-Restli-Protocol-Version: 2.0.0`) — the current documented surface for the **consumer**
   "Share on LinkedIn" product (`w_member_social`). The `/rest/*` Posts API needs a Marketing product and
   would 403 here; **do not "modernise" to `/rest/*`.**
4. **The three OAuth routes are public** (guest-facing, no admin/guest auth), in the public/localization
   group: `GET /linkedin/auth-url`, `GET /linkedin/call-back`, `POST /linkedin/post`. `getVisibility()` now
   also returns `share_type` so the public success page knows manual vs automatic.
5. **Frontend URL read via `config('app.frontend_url')`, not `env()`** — new config key mirroring
   `PUBLIC_FRONTEND_URL`, added so `LinkedInController` satisfies larastan `noEnvCallsOutsideOfConfig`
   (the pervasive legacy `env('PUBLIC_FRONTEND_URL')` calls elsewhere stay baselined; new code uses config).
6. **Frontend kept ALT-native** — the ported share component uses lucide `Share2`, `getApiError`, and
   `react-hot-toast` (not cyan's iconify / `ThreeDotsWave`). New `pages/[lang]/linkedin-redirect.tsx` OAuth
   landing page; `share_type` + `category_slug` thread `success.tsx` → `success-sections.tsx` →
   `sharebtn-sections.tsx`.
7. **`mobile/*` untouched** — new routes are public web only; no mobile contract delta.

**Landed (working tree, on `dev`):** backend — migration + `LinkedInController` + `Category` fillable +
`CategoriesController` (`getVisibility`+`update`) + `CategoriesResources` + `config/app.php` + `routes/api.php`;
admin — `categories-form.tsx` + `interfaces/category.tsx` + EN/AR `web.json`; frontend — `linkedin-redirect.tsx`
+ `success/sharebtn-sections.tsx` + `success/success-sections.tsx` + `join/[category]/success.tsx`. **Gates:**
backend `composer qa` green (pint + phpstan **No errors** + tests **465/3** pre-existing); admin + frontend
`yarn type-check` + eslint green. **Remaining:** manual QA with a real LinkedIn Share app + running stack.

## D26 — 2026-07-20 — SMS provider config moved from `.env` to a DB-driven admin CRUD (cyan "SMS SMTP" port)

SMS transport credentials were pinned to `.env` via `config('services.unifonic')` and read directly in
`SendGuestSMSListener`. Task 013 ported cyan's **SMS provider config** stack so SMS credentials are now
DB-managed by admins (multi-row, `is_active` + a single `is_default`) exactly like the existing
`smtp_configs` mail stack — the foundation for the follow-up SMS tasks. Task:
[../tasks/013-sms-provider-config/TASK.md](../tasks/013-sms-provider-config/TASK.md).

**Durable decisions:**
1. **Mirror `smtp_configs`, not cyan verbatim** — ALT already runs the DB-driven SMTP pattern, so the SMS
   stack reuses its exact shape: multi-row, `is_active` + single `is_default`, secret masked on the wire
   (`app_sid_masked`, last 4), leave-blank-to-keep on edit, `BaseApiController` + `apiSuccess/apiError`,
   `admin.can:` gating, admin BFF-proxy calls, lucide + `getApiError` + `react-hot-toast` (no
   `js-cookie`/Bearer, no heroicons). Additive migration `2026_07_20_000002_create_sms_provider_configs_table`.
2. **Provider abstraction via `App\Services\Sms\SmsSender` + `provider_key`** — v1 validates `unifonic`
   only (`Rule::in(['unifonic'])`); a new provider = one enum append + a `sendVia*` branch + (optionally)
   surfacing the generic `api_key`/`api_secret` slots in the form. Unknown `provider_key` throws
   (`InvalidArgumentException`) so a stale row fails loud instead of silently no-op'ing. `SmsSender` returns
   the raw HTTP `Response` (Unifonic returns 200 even on failure — the `success` JSON key is the real signal).
3. **Secrets encrypted at rest** — `app_sid`/`api_key`/`api_secret` use the `encrypted` cast; the resource
   returns only `app_sid_masked`, and `api_key`/`api_secret` never leave the backend (`$hidden`).
4. **`send-test` + the listener honour the non-production guard** — on non-prod both return/record
   `sent:false` + a reason instead of hitting the provider, so dev/stage never sends real SMS.
5. **RBAC `sms_config` widened** `['view','update']` → `['view','create','update','delete','block']` to
   cover the new CRUD + toggle-active (block), matching `smtp_configs`. Routes live under a gated
   `admin/sms-provider-configs` group (admin-only).
6. **Clean cutover, no dual path** — the `config/services.php` `unifonic` block was **removed** (a fresh env
   setting `UNIFONIC_*` would silently do nothing), and the dead `GuestsController` debug methods
   `sendSMS2`/`sendSMS3`/`smsReplacePlaceholders`/`buildQrCodeLink`/`buildInvitationLink` (+ their commented
   `web.php` routes + the now-stale `env()` phpstan-baseline entry, `count: 2`) were pruned — they duplicated
   the real listener path and only referenced the old env creds.
7. **SMS templates left as-is (out of scope)** — ALT already has an unlinked `sms/templates` + `sms/config`
   admin page set; only the provider-config layer was missing. The follow-up "new SMS tasks" the user flagged
   will surface those. **`mobile/*` untouched** — new routes are admin-only.

**Landed (working tree, on `dev`):** backend — migration + `SmsProviderConfig` + `SmsProviderConfigResource`
+ `SmsProviderConfigController` + `Services/Sms/SmsSender` + `SendGuestSMSListener` (rewired) +
`AdminPermissions` + `config/services.php` (unifonic removed) + `GuestsController` + `routes/{api,web}.php` +
`phpstan-baseline.neon`; admin — `interfaces/sms-provider-config.ts` + `admin-modules/sms/provider-configs/*`
(form + listing + delete/send-test modals) + `pages/[lang]/sms/provider-configs/{index,create,edit/[id]}` +
`data/sidebar-links.tsx` + `data/module-icons.tsx` + EN/AR `web.json`. **Gates:** backend `composer qa` green
(pint **passed** + phpstan **No errors** + tests **465/3** pre-existing); admin `yarn type-check` + eslint
clean + `next build` compiles (new `/sms/provider-configs*` routes present). **Remaining:** manual send-test /
delivery QA in production with a real Unifonic app.

## D27 — 2026-07-20 — Per-flow SMTP override (choose which SMTP account sends each email flow)

Emails always used the single active-default `smtp_configs` row via `DynamicSmtpService::applyDefaultIfAvailable()`.
Task 015 lets admins pick a different SMTP account per flow, falling back to the default when blank/inactive.
Task: [../tasks/015-per-flow-smtp-override/TASK.md](../tasks/015-per-flow-smtp-override/TASK.md).

**Durable decisions:**
1. **One shared resolver** — `DynamicSmtpService::applyConfigById(?id)` applies an active override, else the
   active default (or `.env`). Inactive/deleted overrides never hard-fail a send.
2. **Category SMTP is two pickers** — `categories.smtp_config_id` covers notification emails
   (register-complete / accept / reject). Guest email-OTP uses a separate
   `categories.otp_smtp_config_id` (join form posts the `category` slug). Both blank → active default.
   Admin CMS login OTP is out of scope.
3. **Snapshot at create** — the resolved override is copied onto `guest_emails` / `automations` /
   `invitation_emails` so later category/setup edits don't change what a queued/sent row used. Guest
   email-OTP has no send-row → resolves live from the category slug.
4. **Automations: DB override beats `MAIL_HOST_BULK`** — the static `smtp-bulk` mailer is only used when no
   override is present.
5. **Invitations resolve invitation → collection → default** — nullable `smtp_config_id` on both
   `invitations` and `invitation_collections`.
6. **Admin pickers** list active configs only via ungated `GET admin/smtp-configs/select` (blank = use
   default). Additive migration `2026_07_20_000003_add_smtp_config_override_columns`.
7. **`mobile/*` untouched** — only an admin select route was added; public/OTP request/response shapes
   unchanged.

**Landed (working tree, on `dev`):** backend — migration + `applyConfigById` + snapshot wiring in
`GuestsController` / `InvitationEmail::createFromInvitation` / automation expansion + notification
`toMail()` paths + `AuthController` guest OTP + validation/resources + `smtp-configs/select`; admin —
`smtp-config-select` + pickers on category / automation / invitation / invitation-collection forms + EN/AR.
**Gates:** pint + phpstan clean; admin `yarn type-check` green. **Remaining:** manual QA with multiple SMTP
accounts.
