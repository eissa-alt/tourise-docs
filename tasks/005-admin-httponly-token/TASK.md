# Task 005 — Admin HttpOnly token + Next BFF proxy + full CSP (Saudi P2 backport)

> Folder number is **005** (004 is taken by the dropped migration-squash). This implements the
> **plan's "Task 004 (Track B)"** in `upgrades/CLEANUP_AND_HARDENING_MASTER_PLAN.md` — the plan's internal
> numbering ≠ the `docs/tasks/` folder numbering.

- **Status:** `done` — code shipped + pushed on `dev`; `dev`→`main` merge deferred (user will merge after a repo check, 2026-07-18).
- **Opened:** 2026-07-12
- **Owner:** AI agent
- **Sub-app(s):** admin (backend + mobile untouched)
- **Branch(es):** `dev`
- **Source:** Saudi Forum 11 security **Point 2** (`114-saudi-11/.../docs/security/port-review-jul-2026/POINT_2_ADMIN_TOKEN_HTTPONLY_PLAN.md`). Plan slot: `upgrades/CLEANUP_AND_HARDENING_MASTER_PLAN.md` **Task 004 (Track B)**, un-deferred by user 2026-07-12 (pre-launch: no clone carries prod data yet).

## Goal

Move the admin Sanctum bearer out of the JS-readable `token` cookie into an **HttpOnly** cookie written
server-side, proxied through a **Next.js BFF** so the browser never handles the token; add a full CSP.
Closes the XSS → admin-account-takeover path that `secure`+`sameSite` alone (the earlier Phase-1 fix,
admin `af2298b`) cannot touch — `httpOnly` can only be set by a server, which is why the BFF exists.

## Why this ≠ the Phase-1 secure+sameSite fix

`af2298b` added `secure` + `sameSite:'lax'` to the **client-side** `cookie.set('token', …)`. Those stop
network sniffing and CSRF-style cross-site sends, but the cookie stays **JS-readable** (`js-cookie` writes
from the browser), so any XSS could read `document.cookie` and steal the token → full admin takeover. That
hole is only closed by `httpOnly`, and `httpOnly` cannot be set from JS — it needs a server `Set-Cookie`.
Hence the BFF. The two changes are complementary; the Phase-1 intent is preserved (`SameSite=Strict` +
`Secure` in prod on the new cookie).

## What landed (4 code commits + docs)

1. **BFF scaffolding** (net-new): `utils/auth-cookies.ts` (`TOKEN_COOKIE='token'` HttpOnly + JS-readable
   `AUTH_FLAG_COOKIE='alt_admin_auth'`; `AUTH_MAX_AGE_SECONDS = 6h`), `utils/server/proxy.ts` (cookie
   writers, header forwarding incl. `x-forwarded-for` preservation so Laravel `$request->ip()` stays
   correct, `forwardLoginAndCaptureToken`), `pages/api/proxy/[...path].ts` (streaming catch-all,
   `bodyParser:false` + `responseLimit:false` so multipart uploads / xlsx-pdf exports pass through),
   `pages/api/auth/{login,login-confirmation,logout}.ts`.
2. **Isomorphic axios + auth surface**: `utils/axios.ts` browser → `/api/proxy`, SSR → direct Laravel.
   `auth/provider.tsx` — `login()` no longer client-sets the token (the `/api/auth/*` route already set
   it HttpOnly); mount-effect + `logout()` use the flag cookie; `logout()` calls `/api/auth/logout`.
   `auth/withAuth.tsx` gates on the flag cookie. `components/login/{login-form,verify-email-form}.tsx`
   POST to `/api/auth/*` via raw `axios` and gate on `data.authenticated` (the proxy strips `token`).
3. **Codemod** (135 files, mechanical): removed every dead `cookie.get('token')` read (136 live sites)
   and every `Authorization: Bearer ${token}` header (261) — the proxy now injects auth server-side.
   Pruned `token` from effect-dep arrays, unwrapped `if (token)`/`if (X && token)` guards to their real
   condition, dropped orphaned `js-cookie`/`useMemo` imports. **No `pages/**` touched** (alt has no gSSP
   Bearer-via-cookie reads — verified). Net −399 lines across the task.
4. **Full CSP** in `next.config.js`, adapted to alt (NOT copied from Saudi): env-derived origin list
   (`NEXT_PUBLIC_API_BASE_URL`/`BASE_URL`/`FRONTEND_BASE_URL`/`STORAGE_URL`), reCAPTCHA v3 hosts only,
   **no iconify** (alt is on lucide, ledger D5), **no Maps/Google-Fonts** (alt loads neither),
   `blob:` frame/img for print-js, `'unsafe-eval'` **dev-only**. Kept `X-Frame-Options: DENY` + `nosniff`.

## Gates + verification

- `yarn type-check` **clean**; `yarn production` **green** (4 API routes compile as dynamic ƒ).
- **Runtime, driven against a stub upstream on a live `next dev`** (not just a build):
  1. `POST /api/auth/login` → body `{authenticated:true}` (token **stripped**); `Set-Cookie token=…;
     HttpOnly; SameSite=Strict; Max-Age=21600` + `alt_admin_auth=1` (no HttpOnly). ✅
  2. `GET /api/proxy/guests` with the jar → upstream saw `Authorization: Bearer <token>` (proxy injected
     it from the HttpOnly cookie; browser sent none). ✅
  3. `POST /api/auth/logout` → both cookies `Max-Age=0`. ✅
  4. OTP `login-confirmation` → same strip + HttpOnly set. ✅
  5. multipart POST streams through the proxy to the right path. ✅
  6. CSP header present + correctly built from env; reCAPTCHA hosts, no iconify. ✅
  7. `GET /api/auth/login` → 405. ✅

## Mobile contract

**Untouched.** Admin-web only; `routes/api.php` not modified; mobile uses its own `MobileAuthController`
token flow. No resource shapes changed.

## Follow-ups / watch-outs for real-env QA

- Drive a **real backend login** (this run used a stub — no live backend was available) incl. reCAPTCHA.
- Exercise the **heaviest real export/upload** (xlsx import, badge/PDF print) through the proxy under load.
- Watch for **CSP console violations** on first real load (fonts / reCAPTCHA iframe / print-js blob).
- Saudi hotfix-reverted their P2 once over these exact streaming/CSP edges — QA before merging to `main`.

## Definition of Done

- [x] BFF scaffolding + isomorphic axios + auth surface + codemod + CSP
- [x] `type-check` + `production` green; runtime BFF behavior verified
- [x] Mobile contract untouched (`routes/api.php` unchanged)
- [x] Docs: this TASK.md, ledger **D12**, HANDOFF refresh, tasks index row
- [ ] Real-env browser QA (backend login, reCAPTCHA, heavy export) — before `dev`→`main`
