# Task 002 — Date/time (timestamp) database cleanup + refactor

- **Status:** `done`
- **Opened:** 2026-07-07
- **Owner:** AI agent
- **Sub-app(s):** backend + admin + frontend (+ docs)
- **Branch(es):** `dev`

## Goal

Stop storing dates/times as Unix-timestamp **strings** (and mixed encodings). Move to proper DB
column types (`date` / `timestamp` / `time`), a single "capture now" convention (`Carbon::now()`),
and cyan's **masked date input** (Cleave) instead of the react-day-picker modal — TZ-safe for users
outside KSA. Sibling of Task 001 (boolean cleanup); same "mirror cyan, edit migrations in place,
`migrate:fresh`" playbook.

## Why (current problem)

- Date columns are `string` and encoded **inconsistently**: FE/admin day-picker fields
  (`birth_date`, `issue_date`, …) store a **Unix epoch string** (`getUnixTime()` +
  `zonedTimeToUtc(...)/1000`), while `printed_at`/`badge_collected_at` are set with `Carbon::now()`
  and therefore store a **`Y-m-d H:i:s` datetime string**. Same column, two formats by origin.
- Display goes through `utils/timezoneFix.ts` (`fromUnixTime → Asia/Riyadh → dd/MM/yyyy`), which
  only makes sense for the Unix-string fields and silently misreads the datetime-string ones.
- TZ handling is ambiguous (bare epoch strings, no column semantics). Real `date`/`timestamp`
  columns + display-time conversion fix this "automatically".

## Reference (cyan) — what it actually did

- **Not documented** in cyan's live docs. Only a stale, non-portable `docs_old/other/
  DATE_TIME_REFACTORING_PLAN.md` (references `pif-partners-forum-*` paths + a `utils/date.ts` cyan
  never created). This task documents the pattern properly for the first time.
- cyan is **greenfield dynamic-forms** — its guest dates live in `form_data` JSON via
  `DynamicFormRenderer`'s `date-fields.tsx`. **Do NOT port DynamicFormRenderer** (CLAUDE.md #4). So
  cyan only covers 1:1 the **operational** columns + the masked-input UX; alt's per-guest personal
  date columns are alt-only and designed here to cyan's storage best-practice.
- cyan storage best-practice: date-only → `date` (`YYYY-MM-DD`), datetime → `timestamp` (UTC, ISO
  8601), time-only → `time` or `string(5)` (`HH:mm`).
- cyan masked inputs (Cleave.js + date-fns): `components/shared/forms/masked-date-input.tsx`
  (out `YYYY-MM-DD`), `masked-datetime-input.tsx` (out ISO UTC via `zonedTimeToUtc(…,'Asia/Riyadh')`),
  `masked-time-input.tsx` (out `HH:mm`). Admin ships only the date one; frontend ships all three.
  Deps: `cleave.js` + `@types/cleave.js` (alt has neither yet).

## Decisions (this task)

- **Date-only columns → real `date`** (API/forms use `YYYY-MM-DD`). Cast as `date:Y-m-d` for clean
  JSON. **[user-approved]**
- **Scope = ALL date sites** across admin + frontend (not just guest forms — also
  agenda/sessions/logistics/exports UI, timers). **[user-approved]**
- **Order: backend first**, gate it, then FE + admin. **[user-approved]**
- Datetime columns → `timestamp` (cast `datetime`, ISO 8601). Time-only → keep `string(5)` `HH:mm`
  (matches cyan `meeting_room_slots`) unless a real `time` type is clearly better per field.
- Migrations edited **in place** + `migrate:fresh` (no prod data; matches D6).
- **Keep** `custom-day-input.tsx` + `day-picker.css` + `react-day-picker` dep (unused by default) —
  may be reused for custom cases. **[user-asked]**
- Adopt cyan's masked inputs; add `cleave.js` + `@types/cleave.js` (justified new dep — the approved
  UX). Add one shared display helper (`formatDate`/`formatDateTime`) and migrate **all active**
  `timeZoneFix()` display sites to it.
- **`timezoneFix.ts` is KEPT, not deleted** — revision of the original plan. Its only remaining
  consumer is the retained (unused-by-default) `custom-day-input.tsx`, which the user asked us to
  keep for future custom cases. Deleting it would break that component's compile + the `yarn
  production` gate. It matches cyan, which also keeps `timezoneFix.ts`. All *active* code paths no
  longer touch it.

## Scope — backend column inventory (audited 2026-07-07)

`guest_logistics` does NOT exist in alt — all travel dates live on `guests`.

### `guests` (+ `add_check_in_out_dates` migration)
| Column | Current | New |
|---|---|---|
| `issue_date` | `string(100)` | `date` |
| `expiration_date` | `string(100)` | `date` |
| `birth_date` | `string(100)` | `date` |
| `expected_date_of_arrival` | `string(100)` | `date` |
| `expected_date_of_departure` | `string(100)` | `date` |
| `check_in_date` | `string(100)` | `date` |
| `check_out_date` | `string(100)` | `date` |
| `flight_arrival_time` | `string(8)` (`00:00 AM`) | `string(5)` `HH:mm` (normalize) |
| `flight_departure_time` | `string(8)` | `string(5)` `HH:mm` |
| `printed_at` | `string(50)` | `timestamp` |
| `badge_collected_at` | `string(50)` | `timestamp` |
| `e_badge_sent_at` | `string(25)` | `timestamp` |
| `check_in_time` | `string(25)` | `timestamp` |

### Other tables (string → `timestamp`)
`invitation_emails.sent_at`, `bulk_prints.generated_at`, `bulk_prints.last_download_at`,
`guest_sms.sent_at`, `guest_emails.sent_at`, `automations.sent_at`,
`badge_print_logs.attempted_at`, `history_logs.action_time`.

### Leave as-is (already correct types)
`conferences.start_date/end_date` (`date`), `sessions.date`/`workshops.date` (`dateTime`),
`event_days.date` (`date`), `email_configs.event_*_time` (`dateTime`),
`meeting_room_slots.date` (`date`) + `start_time/end_time` (`string(5)`),
`meeting_rooms.available_dates` (json), framework `jobs`/`*_verified_at`/`read_at`/`created_at`.

## Backend read/write hot spots
`GuestsController.php` (40 refs — write sites `Carbon::now()`, printed-report queries at ~L4381/L4454
that use string comparison, store/update accepting FE input), `Http/Resources/Admin/
GuestsResources.php` + `GuestsOfflineResources.php`, `Exports/GuestsExport.php` +
`GuestsExportView.php`, `BulkPrintController.php`, `OperationActionsController.php`, `Models/Guest.php`
(casts), seeders/factories, visa PDF blade.

## Mobile contract

Guest date fields appear only in **Admin** resources, not any `Mobile*Resource` → not mobile-facing.
**Verify** the mobile QR check-in write path (`MobileQrController` sets `check_in`/`check_in_time`)
still works with a `timestamp` column. `routes/api.php` unchanged expected.

## FE/admin site inventory

See explore-audit output (appended to Log). Categories: `CustomDayInput` call sites, `timeZoneFix()`
display calls, `format(new Date())`/`getUnixTime`/`fromUnixTime` usages, timers, export-filename
helpers, date-typed interfaces.

## Log

Newest at the bottom.

- 2026-07-07 — opened; audited backend columns + hot spots; decisions approved (real `date`;
  all sites; backend-first). FE/admin exhaustive audit delegated to explore subagent.
- 2026-07-07 — **Backend track done.** Converted columns in place (guests date-only → `date`,
  `printed_at`/`badge_collected_at`/`e_badge_sent_at`/`check_in_time` → `timestamp`, flight times →
  `string(5)` HH:mm; `add_check_in_out_dates` → `date`; `sent_at`/`generated_at`/`last_download_at`/
  `attempted_at`/`action_time` → `timestamp` across invitation_emails/guest_emails/guest_sms/
  automations/bulk_prints/badge_print_logs/history_logs). Added casts to Guest (`date:Y-m-d` +
  `datetime`), InvitationEmail/GuestEmail/BulkPrint/Automation/HistoryLog (`datetime`). Cleaned the
  printed-range query to `whereBetween` w/ Carbon; made 3 `GuestsExport*` binders format Carbon
  values (drop unix assumption). Removed 4 dead unrouted debug methods from `OperationActionsController`
  (`test`/`list`/`check`/`convert` — did unix-on-`birth_date`) + their commented routes; kept
  `findMissingEmails`/`getSomeData`. No seeders/factories/tests/PDF blades referenced these columns.
  **Gates:** `pint --dirty --test` passed, `migrate:fresh` clean, `php artisan test` = 452 pass /
  3 fail (same pre-existing ExampleTest 403 + 2 avatar/`personal_image` failures — unrelated).
  Mobile: guest dates only in Admin resources; offline scanner `check_in_time` round-trips via
  datetime cast (shape ISO now). `routes/api.php` only lost 3 commented dead-route lines.
- 2026-07-07 — **FE + admin track done.** Added `cleave.js` + `@types/cleave.js` to both apps;
  ported cyan's masked inputs into `components/shared/forms/` and added shared `utils/date.ts`
  (`formatDate` = date-only `YYYY-MM-DD → dd/MM/yyyy`, no TZ shift; `formatDateTime` = ISO UTC →
  `Asia/Riyadh` `dd/MM/yyyy HH:mm`). Swapped **every** `CustomDayInput` call site to `MaskedDateInput`
  (frontend `pif/fours-steps` step-2/3/4 = 7 fields; admin `default/fours-steps` step-2/3/4 = 6
  fields), sending `YYYY-MM-DD`. **Flight times** (`flight_arrival_time`/`flight_departure_time`) now
  use `MaskedTimeInput` (out `HH:mm`) in **both** apps — this both fixes the admin field (it still
  emitted the old 8-char `hh:mm AM`, incompatible with the new `string(5)` column) and unifies the
  frontend (its ad-hoc local `formatTimeInput`/`isValidTimeString` helpers were deleted). Migrated all
  active `timeZoneFix()` display sites (see-more `by-admins` step-2/3/4 date panels → `formatDate`);
  the commented-out print-panel datetime rows in `see-more-admin.tsx` were also switched to
  `formatDateTime` for when re-enabled. Removed dead unix-conversion imports (`getUnixTime`/`getYear`/
  `zonedTimeToUtc`/`CalendarIconAppend`/`Calendar`) + a stale commented unix block in admin step-2.
  **`masked-datetime-input.tsx` was deleted from both apps** — alt has no user-entered datetime field
  (all `timestamp` columns are backend-set via `Carbon::now()` / scanner), so it was dead code.
  **Kept** `custom-day-input.tsx` (now unused) and therefore **kept** `timezoneFix.ts` (its sole
  remaining consumer). No new i18n keys (masked placeholders `dd/mm/yyyy` / `hh:mm` are non-translatable
  format hints). **Gates:** `yarn type-check` + `yarn production` green on **both** apps; edited/ported
  files prettier-clean.
- 2026-07-07 — **Audit-driven cleanup of raw datetime displays.** The FE/admin audit surfaced admin
  sites that render now-`datetime`-cast fields **raw** (or via `format(new Date())`, which renders in
  the viewer's browser TZ, not `Asia/Riyadh`) — a cosmetic/TZ regression once those columns became
  ISO/UTC. Wrapped with `formatDateTime`: `guest-actions-history.tsx` (`action_time`),
  `see-more-admin.tsx` email-history `sent_at` (+ commented `printed_at`/`badge`/`e_badge`),
  `table-see-more-invitation-modal.tsx` (`sent_at`), `logs/invitation-email-logs-listing.tsx` +
  `logs/guest-email-logs-listing.tsx` (`sent_at`), `bulk-print-listing.tsx`
  (`generated_at`/`last_download_at`), `automation-details.tsx` (`sent_at`). Admin `type-check` +
  `  production` re-run green. **Deleted** the dead `utils/parseDate.ts` from both apps (0 imports; a
  Safari `new Date('Y-m-d H:i:s')` workaround made obsolete — datetimes now serialize as ISO 8601 and
  date-only values parse via date-fns `parse()`, both Safari-safe).
- 2026-07-07 — **Committed task 002 (pre-consistency-pass).** backend `86961dd`, admin `c6ee625`,
  frontend `5f2c55a` (all on `dev`), docs `aeb4528` (`main`). Repo uses conventional-commit style
  (matching task 001), not the `P<phase>` template. Nothing pushed.
- 2026-07-07 — **created_at/timestamp display consistency pass (admin).** Switched **34 files** from
  `format(new Date(x), 'dd/MM/yyyy HH:mm')` (which renders in the viewer's browser TZ) to the shared
  `formatDateTime` (Asia/Riyadh) for real UTC Laravel timestamps: 31 listing grids' `created_at`
  (export `value` + column `render`), plus `workshop-registrants` `registered_at`, `session-detail`
  media `created_at`, and `see-more-guest-draft` `created_at`/`updated_at` (the latter drops seconds:
  `HH:mm:ss` → `HH:mm`). Removed the now-unused `date-fns` `format` import in those files (kept in
  `session-detail` for the agenda `date`). **Deliberately NOT changed:** agenda `date` fields
  (`sessions`/`workshops` — `dateTime` columns entered as local wall-clock via `datetime-local` with
  no TZ conversion, so pinning to Riyadh would shift the displayed time; agenda is a CLAUDE.md-flagged
  sensitive area and needs its own timezone-semantics decision) and the `format(new Date(),
  'dd_MM_yyyy_HH_mm')` **export-filename** timestamps (current time for a download name, not stored
  data). Admin `type-check` + `production` green.

## Definition of Done

- [x] Backend: columns converted + casts + queries/exports/resources/blade/seeders; `migrate:fresh`
      clean; `pint --dirty --test` + `php artisan test` green
- [x] FE + admin: masked inputs adopted, all `CustomDayInput`/`timeZoneFix` sites migrated,
      `custom-day-input.tsx` kept (+ `timezoneFix.ts` kept as its dependency); `yarn type-check` +
      `yarn production` green (both apps)
- [x] EN + AR translations in the same commit (n/a — no user-facing strings moved)
- [x] Mobile contract re-checked (QR check-in path); `routes/api.php` untouched
- [x] Docs: this TASK.md → `done`; tasks index row; LEDGER **D7**; HANDOFF refresh
