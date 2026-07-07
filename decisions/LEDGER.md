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
detail: [../upgrades/BOOLEAN_REFACTOR_PLAN.md](../upgrades/BOOLEAN_REFACTOR_PLAN.md) /
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
