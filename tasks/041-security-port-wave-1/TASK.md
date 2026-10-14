# Task 041 — Security port, wave 1 (from 123-pif-pep-v2)

- **Status:** `todo`
- **Opened:** 2026-09-21
- **Owner:** —
- **Sub-app(s):** backend + admin + frontend
- **Branch(es):** `security/wave-1` in each code repo, created from `dev` — see [Branch rules](#branch-rules)
- **Project phase:** ongoing — live (v2 template)

> Created uncommitted on 2026-09-21 by the cross-project security review, and committed on 2026-09-23, before the work starts. **Renumbered 038 → 041 then:** `main` already carried tasks 038–040, and 042 went to the invitation-import sample. The central `wave1_progress.py` was pointed at the new path.

## Start here — new session prompt

Open this repo in VS Code, start a fresh session, and send:

```text
Read docs/tasks/041-security-port-wave-1/TASK.md and docs/tasks/041-security-port-wave-1/ITEMS.md.
This is wave 1 of a cross-project security port. The fixes come from
123-pif-pep-v2 (reference code at /Users/admin/Projects/ALT/123-pif-pep-v2/pif-pep-v2-repos).
Start in Plan Mode. Before changing anything, verify each item against the
CURRENT code — line numbers in ITEMS.md were verified on 2026-09-20/21 and
may have drifted. Work the Plan steps in order, one step at a time.
Follow the Branch rules in TASK.md: work on security/wave-1 and DO NOT COMMIT —
stop after each step so the user can review the changes. Never merge or
push. Log each step in TASK.md. Stop and ask before touching any .env*
file.
```

## Branch rules

The work stays **off `dev`** until the user decides it is safe to merge.

- Every code change goes on **`security/wave-1`**, in each code repo you touch: `tourise-backend`, `tourise-admin`, `tourise-frontend`. The task files themselves live in the docs repo, which stays on `main`.
- **Do not commit.** Finish one step, leave its changes uncommitted, and stop, so the user can review the diff. The user then commits it, or tells you to commit that step on `security/wave-1` using the commit format in CLAUDE.md. Do not start the next step until the previous one is committed.
- If the branch does not exist yet in a repo: `git fetch`, then `git switch -c security/wave-1 origin/dev`.
- **Never** commit to, merge into, or push `dev` or `main`. **Do not push `security/wave-1` either.** The user merges it into `dev` and pushes when it is safe.
- Before starting each step — once the previous step is committed — bring the branch up to date: on `security/wave-1`, run `git fetch` then `git merge origin/dev`.
- Once a step is committed, record its commit SHA in each repo in the Log. That lets the user merge up to any single step on its own — for example the Day 0 items ahead of everything else.
- Leave the docs changes (this `TASK.md` and `PROGRESS.md`) uncommitted — the user commits them.
- You do not need to tick `PROGRESS.md` or run any progress script: progress is updated centrally after the work is verified in the code.

## Goal

Close the security gaps that 123-pif-pep-v2's pentest remediation fixed and this project still carries — above all the unauthenticated admin-takeover path through the password-reset link (C01). Where 122-gfeai-v2 has already landed an item, replay its diff: the affected code is identical across the three v2 projects.

## Scope

- **In:** the 23 items in the Plan below. Full detail for each is in [ITEMS.md](ITEMS.md).
- **Out:** The `where_null` scope fix is already here (`cdfbc5b` originated in this project). `C02-3.4` is already removed here. Non-security porting-matrix items belong to wave 2.

## Plan

This describes the plan. Progress is tracked centrally in [PROGRESS.md](PROGRESS.md) once the work is verified.

### Step 1 — Close the critical holes

C01 goes backend-first and needs `ADMIN_PANEL_URL` set on every box in the same change window. B15 is test-only here — this project has no debug hook to delete.

- **B3 · C01** _(day)_ — Build the admin reset and invite link from config('app.admin_url') and drop back_link from the request contract, bundling C01-3.1 (the config key), C01-3.7/3.9 (three admin senders plus ?lang= on r…
- **B10 · H01** _(day)_ — Move the whole forgot-password branch onto an AdminPasswordResetRequested event handled by a ShouldQueue listener with unconditional dispatch and a uniform response, plus H01.2 (no 500/200 split on…
- **B15 · H02.1** _(minutes)_ — Delete BOTH forced-500 debug hooks — RWYI82IWDG in InvitationsController::verifyInvitation and the sibling IUFRP3GYZ4ISPUEU in GuestsController's verify-status-token path — and port tests/Feature/I…

### Step 2 — Captcha and abuse controls

Enable enforcement in the dev environment first, before staging and production.

- **B7 · C02** _(day)_ — Port the rewritten app/Rules/ReCaptcha.php WITH its prerequisites, per project: the services.recaptcha config block, messages.recaptcha_required in EN and AR, GOOGLE_RECAPTCHA_SECRET pinned in phpu…
- **B11 · C02-2.2-checkunique** _(hours)_ — Write a fresh fix — no fix exists in pep either: replace the client-supplied column name in checkUnique with a per-project allow-list derived from that project's actual frontend callers.
- **B12 · C02-2.3-otp** _(hours)_ — Add `->where('email', $request->email)` to the OTP lookup, normalising both sides with trim + lowercase.

### Step 3 — Stored XSS and uploads

- **B4 · PHASE-1** _(minutes)_ — Render category share text as a React child inside a <div className="whitespace-pre-wrap wrap-break-word">{shareText}</div> instead of dangerouslySetInnerHTML, on BOTH the share page and the succes…
- **B13 · M04-SVG** _(hours)_ — Two different fixes under one id. In 129-pif-gamf and the three v2 targets, add the mimes rule to the conference upload (AdminConferenceController.php:276 in 129 takes pep's one-word change verbatim).

### Step 4 — Admin BFF write guard

Land the null-body correction (`047d31f`) in the same release.

- **B6 · M03-BFF** _(hours)_ — Port isSelfOriginatedWrite into pages/api/proxy/[...path].ts — read Sec-Fetch-Site first, fall back to Origin then Referer, compare host-to-host against the request's own Host (never an env var), r…

### Step 5 — Disclosure

- **B5 · C06** _(minutes)_ — Narrow AdminsSelectResources::toArray() to id plus trim(first_name.' '.last_name), exactly as pep commit d9f6476 did — deliberately WITHOUT gating the route.
- **B17 · H04** _(minutes)_ — Strip app and env from GET /api/health, keeping timestamp (the mobile contract names this route as how a client learns server time), and add the regression test asserting their absence.

### Step 6 — Error handling and exports

Re-baseline 5xx alerting BEFORE the PHASE-0 deploy; note `WhatsAppWebhookController.php:57` aborts 503 on an unauthenticated webhook, so P0.4 and P0.5 must land together. The export binder must ship both halves in ONE deploy.

- **B9 · PHASE-0** _(day)_ — Port the Handler::render rewrite with P0.1-P0.8 in the documented branch order (HttpResponseException, Throttle, Authentication, Validation, ModelNotFound, NotFound, generic 4xx, generic 500), keep…
- **L9 · P0.14** — Get a written confirmation per project that the mobile client implements the 401-to-OTP re-login handler its own contract documents, BEFORE the PHASE-0 backend deploy.
- **B8 · EXPORT-FORMULA** _(hours)_ — One change, two ordered steps, one deploy: (1) add `: bool` to every bindValue override, (2) introduce app/Exports/Concerns/TextSafeValueBinder.php and swap the parent, (3) port ExportClassesAreLoa…

### Step 7 — Headers, cookies and proxy trust

The trusted-proxy code is inert, so it can go on the branch freely; setting its value is a separate day, in a maintenance window.

- **B20 · M04-API** _(hours)_ — Add the SecurityHeaders global middleware to the API origin (closed CSP, Permissions-Policy, nosniff, X-Frame-Options, Referrer-Policy), keeping pep's deliberate omission of the `sandbox` directive…
- **B18 · M01** _(minutes)_ — Set the session cookie's Secure flag explicitly, keeping the env('APP_ENV') !== 'local' exemption, and document the key as ABSENT (commented out) in the env examples — never as a bare SESSION_SECUR…
- **B19 · H03.1** _(minutes)_ — Repair the 429 so it keeps Retry-After and reports the limiter that actually blocked, rather than the outer throttle decoration's ceiling.
- **B16 · H03.4** _(day)_ — Add config/trustedproxy.php and declare $headers in TrustProxies.php, leaving $proxies unset, plus utils/forwarded-for.ts and a `headers:` option on each Axios.get in getServerSideProps.

### Step 8 — Data integrity and triage

- **B21 · PHASE-6.6-refcheck** _(hours)_ — Handle the RESTRICT foreign keys and the dangling guest_status_ids JSON before a guest status is deleted: return a 409 with a message naming what still references it, instead of letting the driver…
- **B22 · PHASE-4-TRIAGE** _(hours)_ — Adopt the method, not just the fixes: verify each precondition in the target project before porting, tier the evidence (code-verified / harness-observed / needs-production, BRIEF-5), combine the th…
- **L3 · PHASE-3.4** — Add App\Models\PersonalAccessToken with the strict id|hash lookup and Sanctum::usePersonalAccessTokenModel, after tracing every token consumer — in 129-pif-gamf that means MobileQrController.php:23…

### Step 9 — Verify

- **L4 · PHASE-6.5-mobile-demo** — Confirm MOBILE_DEMO_EMAIL and MOBILE_DEMO_OTP are blank in every 129-pif-gamf environment and add an `if (! app()->environment('production'))` guard around both bypass blocks at MobileAuthControlle…
- **L14 · PHASE-6.7-smoke** — Write post-deploy-security-check.sh and wire it into the pipeline: read-only probes asserting the Secure cookie flag, the header set, /health's shape, APP_DEBUG behaviour and the _ignition 404.

## Decisions

- Finished projects (101-leap-dinner-v2, 113-pif-directors-gathering, 126-pif-hakathon) are sources only; nothing in this task changes them.
- Durable decisions → promote to `decisions/LEDGER.md`.

## Log

- 2026-09-21 — opened by the cross-project security review; 23 items selected for this project.
- 2026-10-13: Haboob's pentest for STA (tested 14 and 15 Sep 2026) found three of these items independently: **B11** is its M-003 and M-005, **B12** its M-004, and its M-002 (debug output on production) needs **B9** before `APP_DEBUG` can go off. Nothing closed yet. Triage and tracker: [security/](../../security/README.md), [PENTEST_TRIAGE](../../security/pentest-2026-09/PENTEST_TRIAGE/PENTEST_TRIAGE.md).
- 2026-10-13: **B9 done** (with M03-BACKEND), backend `c8a1885` on `fix/api-error-status-codes`, merged to `dev` (PR #64, `927df77`) and `main` (PR #65, `969b2fd`); not deployed. Ported from pep-v2 `c0db55d` + `c9688b4`; the 503 stays masked (P0.5). `ApiErrorHandlingTest` 10 tests; suite 1,163 pass with `APP_DEBUG` on and off (94 failed off before). Urgent because production's `.env` had just gone to `APP_DEBUG=false`. L9 (mobile 401 confirmation) still open; with debug off the app got 500 until this ships, so the fix restores the documented 401.
- 2026-10-13: **B11 and B12 done**, backend `d5453ef` on `fix/check-unique-and-otp-email`, merged to `dev` (PR #66, `895f320`); not on `main`, not deployed. B11: `checkUnique` takes `type: email` only (both callers, public forms and admin, send nothing else), compares trimmed and lower-cased, never returns the record. B12: `GuestsController::emailOtpFor()` matches code and email (trim + lowercase) at submit and at clean-up; no flow changes the email between request and submit except a person editing the field, who is then rightly refused; `email-confirmation` left token-only (UI step, the frontend sends no email there). Mobile `verifyOtp` already matched the email. `GuestCheckUniqueTest` 7, `GuestEmailOtpTest` 4; suite 1,174 pass with `APP_DEBUG` on and off.
- 2026-10-13: **B15 and B19 done**, tests only, backend `4298986` merged to `dev` (PR #68, `38ed495`). B15: this project never had the forced-500 hooks (`RWYI82IWDG`, `IUFRP3GYZ4ISPUEU` grep clean); `InvitationVerifyTest` (ported from pep-v2, plus `verify-status-token`) pins that no token value is special-cased. B19: B9's handler (`c8a1885`) already keeps the throttle headers, so a 429 has `Retry-After` again; the outer `throttle:api` is unlimited for anonymous callers (since `a32901d`), the only ones an inner limiter meters, so the 429 reports the blocking limiter. `ThrottleResponseTest` pins both and fails on the pre-B9 handler.
- 2026-10-13: **B3 done** on `security/wave-1` (not pushed): backend `ff18643`, admin `990251c`. The admin setup/reset link is built from `config('app.admin_url')` (`ADMIN_PANEL_URL`) via `Admin::setupLink()` on all three senders (forgot-password, create in invite mode, resend invite); `back_link` no longer read or sent; links expire after `auth.admin_invite_ttl_hours` (48), a null `created_at` counts as expired. Resend now passes `?lang=`. `AdminInviteLinkTest` (8, 7 fail on the old code); suite 1,192 pass with debug on and off. Deploy notes in the checklist below.
- 2026-10-13: **B10 done** on `security/wave-1` (not pushed): backend `a623bd0`. Forgot-password only fires `AdminPasswordResetRequested` (address trimmed and lower-cased) and answers the same every time; `SendAdminPasswordResetListener` (ShouldQueue) does the lookup, token, render and send via `Admin::setupLink`, and logs instead of sending when `app.admin_url` is empty. `password-reset` limiter: 5 an hour per address (sha256 key), not per IP (one shared bucket until B16). The invite path in `AdminsController` stays synchronous (authenticated, not an oracle). `AdminForgotPasswordTest` (8, the 4 about the fix fail on the old code); suite 1,200 pass with debug on and off.
- 2026-10-13: **B4 done** on `security/wave-1` (not pushed): frontend `bee9156`. The share page and the success modal render the category share text as a React child in a `whitespace-pre-wrap` div instead of `dangerouslySetInnerHTML`; `toHtml` removed. No `dangerouslySetInnerHTML` left in the public site. The write-rule half (PHASE-1b) stays separate. type-check, ESLint, Prettier, build green.
- 2026-10-14: **B8 done** on `security/wave-1` (not pushed): backend `440ab07`. New `App\Exports\Concerns\TextSafeValueBinder` (ported from pep-v2 7544e4f + 7ded37b); all 32 exports extend it, the 31 untyped `bindValue` overrides declare `: bool`, in one commit. Confirmed live before the fix: `GuestsExport` wrote a guest company `=HYPERLINK(...)` as a formula. No export writes its own formulas; the 4 import workbooks already write user data as explicit strings. `ExportClassesAreLoadableTest` (2) and `ExportFormulaInjectionTest` (4); suite 1,206 pass with debug on and off.
- 2026-10-14: **B13 done** on `security/wave-1` (not pushed): backend `ec1d184`, admin `eafe3f4`. The conference upload refuses SVG (`mimes:png,jpg,jpeg,webp`) and stores the file under `extension()` (from the content) instead of the client's extension; both holes confirmed on the old code (SVG accepted, a PNG named `evil.html` stored as `.html`). The admin's two pickers no longer offer SVG. ConferenceTest updated (+2); suite 1,208 pass with debug on and off.
- 2026-10-14: **B7 done** on `security/wave-1` (not pushed): backend `0f3213e`. `App\Rules\ReCaptcha` ported from pep-v2: score below `min_score` (0.3) refused while `enforce_score` is on (default, kept by the owner), optional hostname and action checks, fails closed (no secret, Google unreachable after 2 retries, error status, unreadable answer), POST, no `remoteip` (shared IP, B16). One `recaptcha.verify` info line per check, error lines per failure. `messages.recaptcha_required` added in EN and AR (it never existed). phpunit pins `GOOGLE_RECAPTCHA_SECRET`; the 15 Google fakes return a score. `tests/Unit/ReCaptchaRuleTest` (16, 8 fail on the old rule); suite 1,224 pass with debug on and off.
- 2026-10-14: **B5 done** on `security/wave-1` (not pushed): backend `541ca60`. `AdminsSelectResources` returns `id` and `trim(first last)` only, no email; route left ungated (the area form's gate-operator dropdown needs it without `admins_management`). Leak confirmed on the old code. `AdminsSelectTest` (3, from pep-v2); suite 1,227 pass with debug on and off.
- 2026-10-14: **B17 done** on `security/wave-1` (not pushed): backend `6433674`. `/api/health` returns `status` and `timestamp` only; `app` and `env` removed; `timestamp` kept for the mobile contract. `HealthEndpointTest` (4, from pep-v2; 2 fail on the old route); suite 1,231 pass with debug on and off.
- 2026-10-14: **B18 done** on `security/wave-1` (not pushed): backend `04df4ac`. `config/session.php` `'secure' => env('SESSION_SECURE_COOKIE', env('APP_ENV') !== 'local')`; the old setting followed `isSecure()`, false behind the load balancer, so neither cookie was flagged. `SessionCookieSecureTest` (4, from pep-v2); suite 1,235 pass with debug on and off.
- 2026-10-14: **L4 done** on `security/wave-1` (not pushed): backend `de0c44e`. Owner chose option B over the task's production guard: store reviewers test against production, and the owner confirmed `MOBILE_DEMO_EMAIL`/`MOBILE_DEMO_OTP` are not set and there is no mobile cycle yet. `MobileAuthController::isDemoLogin()` (both spots): both settings set, address matches, code at least 12 characters (shorter is refused and logged as `mobile.demo_login_refused`), `hash_equals`, every use logged as `mobile.demo_login`. `MobileDemoLoginTest` (5); suite 1,240 pass with debug on and off.
- 2026-10-14: **B6 done** on `security/wave-1` (not pushed): admin `1970795`. `isSelfOriginatedWrite()` in `utils/server/proxy.ts`; the proxy refuses POST/PUT/PATCH/DELETE not from the panel (403) and bodies that are not JSON or multipart (415, empty bodies exempt per pep-v2 047d31f); logout guarded too. Checked against a running build pointed at a dead API port: panel writes pass, same-site/cross-site/foreign/origin-less writes 403, form-encoded 415. No admin test runner, so no automated test.
- 2026-10-14: **B20 done** on `security/wave-1` (not pushed): backend `eb29fc0`. Global `SecurityHeaders` middleware: closed CSP and a deny-all Permissions-Policy on every API response. Narrower than pep-v2: X-Frame-Options, nosniff and Referrer-Policy left to the edge, which already sends them (2026-09 pentest responses); no `sandbox`. `SecurityHeadersTest` (4); suite 1,244 pass with debug on and off.
- 2026-10-14: **B21 done** on `security/wave-1` (not pushed): backend `0dc6a51`, admin `5ffef54`. Written fresh: pep-v2's `destroy()` still has no check (the item came from its Phase 6 plan, never built there). Deleting a status still used by guests, categories (default or `status_config`), automations or admins' `guest_status_ids` answers 409 with the counts; any other integrity error is 409 too. Old code: 500 for the FK cases, a silent dangling delete for the JSON ones. The admin listing had no catch (nothing on screen); it now shows the reason in EN and AR. `GuestStatusDeleteTest` (6); suite 1,250 pass with debug on and off. Worth porting back to pep-v2 and the other ALT projects.
- 2026-10-14: **L3 done** on `security/wave-1` (not pushed): backend `1513844`. `App\Models\PersonalAccessToken::findToken()` refuses a token without the `id|` prefix, registered via `Sanctum::usePersonalAccessTokenModel()`. Consumers traced: admin and mobile through the guard; `MobileQrController` uses the vendor class directly, unaffected (QrScannerTest green). `TokenFormatTest` (5); suite 1,255 pass with debug on and off. **Open question for the mobile team:** `/api/mobile/qr` falls back to resolving a scanned code as a guest's Sanctum token, which suggests a guest's QR may show their login token; if so, a photo of the QR is a 30-day login. Check when mobile work starts.

## Deploy checklist (security/wave-1)

Collected item by item, for the day `security/wave-1` is merged and deployed. Tell the owner before deploying.

- **B3 (admin setup link):**
  1. Add `ADMIN_PANEL_URL=https://admin-register.tourise.com` to the production backend `.env`, then `php artisan config:cache`. Unset, every reset and invite link points at localhost.
  2. On production, before deploying: `SELECT email FROM admin_invites WHERE created_at IS NULL OR created_at < NOW() - INTERVAL 48 HOUR`. Those links stop working on deploy; tell those admins to ask for a new one.
  3. Deploy the backend first, then the admin (the old backend requires `back_link`).
- **B10 (forgot-password queued):** the queue worker must be running on the production backend (`docs/process/QUEUE_SETUP_PROD.md`), as it already must for guest emails. If it is down, reset emails stop arriving with no error to the admin; watch `failed_jobs`.
- **B4 (share text):** nothing required. Optional check first: `SELECT slug FROM categories WHERE share_text_en REGEXP '[<>]' OR share_text_ar REGEXP '[<>]'`; any HTML in a share text will show as literal tags after deploy.
- **B8 (exports):** after deploying, download and open 2 or 3 exports from the admin (guests, invitations, the dashboard). The tests guard against the class-load crash, but every export changed.
- **B13 (conference uploads):** nothing required. Existing files keep serving; tell the team new logos and icons must be PNG, JPG or WebP (icons PNG or WebP), no SVG.
- **B7 (reCAPTCHA score):** enforcing by default (owner's call, 2026-10-14).
  1. Safe start: `GOOGLE_RECAPTCHA_ENFORCE_SCORE=false` for the first days, read the scores, then `true` (or remove the line) and `php artisan config:cache`. Skipped, real users and admins with a low score are refused from day one.
  2. Recommended: `GOOGLE_RECAPTCHA_HOSTNAMES=register.tourise.com,admin-register.tourise.com`.
  3. `GOOGLE_RECAPTCHA_SECRET` must be set (as today); without it everything is refused, with a `recaptcha.misconfigured` error line.
  4. `LOG_LEVEL` must be `info` or `debug` to get the per-check `recaptcha.verify` lines; optional `LOG_CHANNEL=daily` so `laravel.log` does not grow forever.
  5. Reading the logs, from the backend folder: refusals `grep 'recaptcha.verify' storage/logs/laravel.log | grep -v '"verdict":"pass"'`; errors `grep -E 'recaptcha\.(unreachable|upstream_error|malformed_response|misconfigured)' storage/logs/laravel.log`; scores `grep -o '"score":[0-9.]*' storage/logs/laravel.log | sort | uniq -c`.
- **B17 (/api/health):** ask devops whether an uptime monitor checks the body for `app` or `env`; if so, change it before deploying. A check on `200` or `"status":"ok"` is unaffected.
- **B18 (session cookie):** the production `.env` must not have a blank `SESSION_SECURE_COOKIE=` line (falsy, strips the flag); absent or `true` is fine.
- **L4 (mobile demo login):** nothing today (not set). For a store review later: set `MOBILE_DEMO_EMAIL` and a random `MOBILE_DEMO_OTP` of 12+ characters (never a value written in the repo), `config:cache`, and clear both after the review. Uses show as `mobile.demo_login` in `laravel.log`.
- **B6 (admin write guard):** on staging, click a save, an upload, an export, a delete and a toggle button before going live. Writes answering 403 there mean the server in front of the admin does not pass the real `Host` header (devops).
- **B20 (API headers):** before deploying, `curl -sI https://api-register.tourise.com/api/health`: the edge must not send its own `Content-Security-Policy` or `Permissions-Policy` (one owner per header); the edge keeps X-Frame-Options, nosniff and Referrer-Policy. After deploying, open a PDF, a badge, an export and a calendar file from the API.

## Definition of Done

- [ ] [PROGRESS.md](PROGRESS.md) at 100% — every item `[x]` done, or `[-]` closed with its reason in the Log
- [ ] All code committed on `security/wave-1` in the relevant repos — **not merged and not pushed**; the user merges into `dev` and pushes when it is safe
- [ ] Every step reviewed by the user before it was committed
- [ ] Each step's commit SHA per repo recorded in the Log
- [ ] EN + AR translations in the same commit (if any user-facing strings)
- [ ] Quality gate green (backend `pint --test` + `php artisan test`; Next apps `yarn type-check` + `yarn production`)
- [ ] Mobile contract checked where `routes/api.php` or status codes changed
- [ ] DevOps items for this project handed over with a named owner
- [ ] Post-deploy security smoke run (L14) where it applies
- [ ] This TASK.md set to `done`; index row added

## References

- Cross-project security review: `/Users/admin/Projects/ALT/operational-tasks/SECURITY_PORT_REVIEW_2026-09-21.md`
- Cross-project porting matrix: `/Users/admin/Projects/ALT/operational-tasks/PORTING_MATRIX_2026-09-20.md`
- pep-v2 source documents: `/Users/admin/Projects/ALT/123-pif-pep-v2/pif-pep-v2-repos/docs/security/`
