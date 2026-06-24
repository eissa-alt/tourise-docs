# Handoff — current state

> Rolling pointer, overwritten each session. For the durable record see the per-task `TASK.md`,
> `decisions/LEDGER.md`, and `upgrades/UPGRADE_SUMMARY.md`. Full plan: `upgrades/CYAN_FEATURE_PARITY_MASTER_PLAN.md`.

**2026-06-24 — Track 2 ST4 (listing stack) wired, ST3 (sidebar accordion) DONE,
Track 4 (DB-driven SMTP) landed, + a large scope-trim removing 11 unused modules
across all four apps. Then a cyan-parity follow-up: form/input styling (C),
legacy status-admin-type cleanup (A), and the admins-form layout migration (B).
Gate-green on `dev`, not pushed. DB reseeded (`migrate:fresh --seed`).**

Builds on the 2026-06-23 state (Track 1 RBAC complete, Track 3 secondary-status removal complete).
This session: finished wiring the cyan listing stack into the surviving listings (ST4), shipped the
ST3 sidebar accordion grouping (previously deferred), added the DB-driven SMTP config module
(Track 4 / P4), and trimmed 11 modules the project doesn't need (P5.trim).

## Current SHAs (committed on `dev`, NOT pushed — no upstream set)

- `alt-backend` @ `bfff074` (P5.cleanup — legacy admin field drop) — also `08d542e` (P5.trim),
  `69844a0`/`6aab18f`/`2509ca5` (ST4 listing contract), `875b226` (P4 SMTP), `f6828ea` (T3
  secondary-status), `38bacbc` (T1 type-drop).
- `alt-admin` @ `1a3acb0` (P2.ST7 admins-form parity) — also `6836d34` (P5.cleanup status-admin-type),
  `34392cc` (P2.ST6 form/input styling), `e3a0677` (P5.trim), `1e449dc` (ST3 accordion),
  `c598fe0`/`b1442de`/`b3ec645`/`dd2d45b`/`e8031b3` (ST4 listing stack), `6b9c9d8` (P4 SMTP),
  `5505155` (T3 secondary-status), `d3dc88f` (ST3 shell).
- `alt-frontend` @ `f32e1ae` (P5.trim — positions field/select + agenda header fetch dropped).
- `alt-landing` @ `e6eb48a` (P5.trim — positions field/select + agenda refs dropped).
- `docs` (on `main`) @ `343a415` + this handoff.

## What landed this session

- **Track 4 — DB-driven SMTP** (`alt-backend` `875b226`, `alt-admin` `6b9c9d8`): `smtp_configs` table +
  `SMTPConfigController` + `DynamicSmtpService` (applies the active DB config at runtime, falls back to
  default), `sendTestEmail` endpoint; admin SMTP config module + sidebar entry + EN/AR. Smoke-test still
  pending (needs real SMTP creds / env).
- **Track 2 ST4 — listing stack wired** (`alt-backend` `6aab18f`/`2509ca5`/`69844a0`, `alt-admin`
  `e8031b3`→`c598fe0`): backend index controllers conformed to the `{data, meta}` + `sort`/`search`
  contract; admin migrated media-center, invitation-email-logs, rooms, invitations, and guests consoles
  onto the shared `use-listing-state` + `components/shared/listing/*` stack. (titles/positions/tiers/
  traveling-status were also migrated then removed by P5.trim below.)
- **Track 2 ST3 — sidebar accordion grouping DONE** (`alt-admin` `1e449dc`): the previously-deferred
  collapsible section *groups* are in — links grouped into Overview / Management / Communications /
  Operations via `resolveGroup`, cyan styling parity (pill links, group cards, active bar), collapsed
  brand fixed to an "AP" monogram, mobile-app links hidden. New `sidebar_group_*` EN/AR keys.
- **P5.trim — remove 11 unused modules** (all four repos): **Cvent / RG / Bizzabo integrations**,
  **External Guest Push API**, **Tiers**, **E-Visa**, **Traveling Status**, **Hotels**, **Rooms**,
  **Agenda**, **Positions**. Backend (`08d542e`, 146 files, −16.9k): models, controllers, resources,
  exports, listeners/events, middleware, routes, permission catalog, seeders, and the related
  guest/category/invitation columns. **Standalone tables removed and the original create-migrations
  edited in place → requires `migrate:fresh` (no incremental drop migration).** Admin (`e3a0677`,
  157 files, −17.9k): module pages/components/interfaces/selects + feature-id wiring + EN/AR keys.
  Frontend/landing: positions field + selects + interface + `/agenda` header fetch stripped from the
  public registration + landing forms.
- **DB reseeded**: `php artisan migrate:fresh --seed --force` — all migrations apply on a fresh schema,
  all seeders succeed.

### Cyan-parity follow-up (C → A → B, after P5.trim)

- **C — form / input styling parity** (`alt-admin` `34392cc`): admin-primary CSS vars + label
  typography normalization + cyan button styles in `css/web.css`; shared primitives (`label.tsx`,
  `form-wrapper.tsx` white-card, `custom-input.tsx`, `custom-switch-input.tsx`) aligned;
  `countries-select-new` reskinned dark→light; login form classes. (Filter-bar card chrome left as
  optional polish.)
- **A — legacy status-admin-type cleanup** (`alt-backend` `bfff074`, `alt-admin` `6836d34`):
  dropped `action_ids` / `dashboard_component_ids` from the Admin model/controller/resource/profile +
  deleted their two migrations and the type→role backfill (RBAC is role-based now). Frontend: removed
  the guest-actions / dashboard-components multi-selects + data lists, switched dashboard widget gating
  to `checkPermission('dashboard', …)`, dropped the `guest_actions` listing column, cleaned commented
  per-type sub-links, fixed the stale `/admins/{slug}` redirect, and removed the 8 dead `admin_*` type
  keys (EN+AR). No leftover legacy guest/view/community/badge/gate/super admin-type artifacts in code.
- **B — admins management / super-admin flow**: the **listing was already at parity** (super-only
  screen, role-based `is_super` protection on block/activate, role_id filter, shared listing stack).
  The **admins-form** was migrated to cyan's sectioned-card layout (`alt-admin` `1a3acb0`): role
  Listbox + manage-roles hint, boolean status switch, collapsible data-scope (categories + guest
  statuses) with a live count, password keep/modify radio cards, security (OTP) section, sticky footer.
  Kept alt's data model (manual password, string `otp_to_login`).

> **(B) admin email-invite / `password_mode` flow — DONE** (branch `feat/admin-invite-flow`, both
> `alt-backend` + `alt-admin`, gate-green, NOT merged/pushed). Cyan's "send setup email" invite path is
> now ported, adapted to alt's conventions rather than blindly copying cyan's extra columns:
> - **Adapted (not ported):** alt keeps role-based `is_super` protection (no `is_seeded`), `status`
>   string activation (no `is_active`), and gates resend via `email_verified_at` (no `last_login_at`).
>   So the only new column is **`password_mode`** (`manual`|`invite`, default `manual`).
> - **Backend:** migrations `2026_06_24_000001` (add `password_mode`) + `2026_06_24_000002` (create
>   `admin_invites`); `AdminInvite` model; `AdminsController::store` branches manual vs invite (random
>   placeholder hash + `sendInviteEmail`); new `AdminsController::resendInvite` (gated on
>   `password_mode=invite` && not yet verified); `AuthController::resetpassword` implemented against
>   `admin_invites` (sets password + `email_verified_at`, deletes token); EN/AR
>   `emails/admin_invite/{en,ar}.blade.php`; routes `POST /admin/reset-password` (public) +
>   `POST /admin/admins/{id}/resend-invite` (gated `admins_management,create`); `AdminsResources` now
>   emits `password_mode` + derived `invite_pending`.
> - **Admin FE:** create-form password-strategy radio (set now vs send setup email) with
>   `smtp-configs/check-default` gating + "configure email" link; resend-invite row action on the
>   listing; `reset-password/[token]` page wired to `POST /reset-password`; `password_mode`/
>   `invite_pending` added to `AdminType`; EN+AR keys added (parity 1527=1527).
> - **Still needs live SMTP to verify actual email delivery** (same constraint as the Track 4 smoke
>   test). Mobile contract unaffected — the two new routes are admin-only.

## Gates

- Backend: `route:list` resolves (441 routes, no refs to deleted classes); `migrate:fresh --seed` clean;
  `pint --test` on the changed files = **passed**.
- Admin / Frontend / Landing: `yarn type-check` green; `yarn production` green (run during the listing /
  removal work this session).
- EN/AR translation parity intact (admin web.json: equal key counts, zero diff).
- **Mobile contract unaffected** — none of the trimmed modules are in the mobile surface; no
  `routes/api.php` mobile endpoint added/removed/renamed.

> ⚠️ Runtime-QA caveat: ST4 wired listings, the ST3 accordion (collapse + RTL), the P5.trim removals,
> and the cyan-parity follow-up (form styling, admin-type cleanup, the rebuilt **admins create/edit
> form**) compile + build green but were **not browser-tested** this session. Smoke-test the migrated
> consoles, the sidebar accordion (LTR + RTL, collapsed flyouts), the guest/join forms (positions field
> gone), and the new admins form (role Listbox, status/OTP switches, collapsible data-scope, password
> keep/modify, create + edit submit) before pushing.

## Next

- **Runtime / browser QA** — boot backend + admin (+ frontend/landing) and verify the above caveat list.
- **Track 4 SMTP smoke test** — hit `sendTestEmail` with real creds; confirm `DynamicSmtpService` applies
  the active DB config.
- **(B) admin email-invite / `password_mode` flow — DONE on `feat/admin-invite-flow`** (backend + admin).
  Browser-test the invite create path + reset-by-token page, then verify real email delivery with live
  SMTP. Merge the branch into `dev` once QA passes.
- **Push `dev`** — all four repos are ahead with no upstream; set upstream + push once QA passes.

> Pint note: the backend repo is not Pint-clean at baseline. Use `pint --dirty` (formats only changed
> files); a repo-wide `pint` run churns 300+ unrelated files. (This session a repo-wide run slipped in
> and was surgically reverted — only the ~51 genuinely-edited files kept their formatting.)
