# Task 053: Admin session of 3 days

- **Status:** `done (code)`: **merged to `dev` on 2026-10-12** (backend PR #54 `053c538`, admin PR #53 `4af0cd1`),
  not on `main`, not deployed.
- **Opened:** 2026-10-12
- **Owner:** unassigned
- **Sub-app(s):** backend + admin
- **Branch(es):** `feat/admin-session-3-days` in `tourise-backend` + `tourise-admin`, off `dev`, created `--no-track`.

## Goal

An admin stays signed in for 3 days after logging in, instead of 6 hours (owner, 2026-10-12).

## Findings

- The 6 hours lived in two places that must agree: the login token's own expiry, set by `Admin::generateToken()`
  (`now()->addHours(6)`; every admin login path goes through it), and the admin app's login cookies,
  `AUTH_MAX_AGE_SECONDS` in `utils/auth-cookies.ts` (Task 005). `config/sanctum.php` `expiration` is `null`; the
  cookie's comment said it was 360 minutes (drift, fixed).
- No idle timer in the admin; the session is counted from login.
- Logout deletes all the admin's tokens; blocking deletes them too ("blocked means out now", the admin access hardening, ledger D55).
- **A password change does not end other sessions**, neither an admin's own reset nor a Super Admin setting one.
  With 6 hours the gap was small; with 3 days it is the usual way to throw out someone who got into an account.
  Put to the owner as a follow-up (recommended yes), not answered yet.
- Guest and mobile tokens are separate (`MobileAuthController`, days set there) and unchanged.

## Decisions

| # | Decision |
|---|---|
| 1 | **3 days from login**, not from the last click (the existing absolute expiry, longer). After it the admin signs in again. |

## Built (2026-10-12)

- **Backend `ec7f424`:** `Admin::TOKEN_LIFETIME_DAYS = 3`, used by `generateToken()`. `AdminTokenLifetimeTest`: the
  token works just before 3 days and returns 401 just after (fails on the old 6 hours). 1141 tests pass, Pint
  clean.
- **Admin `1a235fc`:** `AUTH_MAX_AGE_SECONDS = 60 * 60 * 24 * 3`; the comment points at the backend constant.
  Type-check and ESLint green.

## Deploy

Backend and admin together: with only the backend, the cookie still ends the session after 6 hours. No migration,
no `.env` change. Sessions opened before the deploy keep their 6 hours; the next login gets 3 days.

## Definition of Done

- [x] Code merged to `dev` in backend and admin
- [x] EN + AR translations in the same commit (none: no user-facing string)
- [x] Quality gate green (backend `pint --test` + `php artisan test`; admin `type-check`, ESLint)
- [x] Docs updated (this TASK.md, index row, HANDOFF)
- [x] Mobile contract checked: no route changed
