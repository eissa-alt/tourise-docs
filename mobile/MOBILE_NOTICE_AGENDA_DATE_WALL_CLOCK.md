# Mobile notice — agenda `date` is now venue-local wall-clock

**Date:** 2026-07-07
**Severity:** Breaking parse-behavior change (no field renamed/removed — the *meaning* of the value changed)
**Affects:** Any mobile screen that renders or sorts a session/workshop **`date`**
**Reference:** ledger **D8**, `docs/mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.html §24`, `docs/decisions/LEDGER.md`
**Status:** committed on backend `dev` (not yet merged/released) — coordinate the release with mobile.

---

## TL;DR for the mobile team

The scheduled agenda **`date`** field (sessions & workshops) **no longer carries a `Z`/UTC offset**.
It is now emitted as a **naive, venue-local wall-clock** string in **Asia/Riyadh**:

```
before:  "2026-11-04T11:30:00.000000Z"   ← UTC, ends in Z
after:   "2026-11-04T14:30:00"            ← venue-local wall-clock, no Z, no offset
```

**Do NOT convert `date` to the device timezone.** Parse it as a *local/wall-clock* time and display
it as-is. A user in London and a user in Riyadh must both see **14:30** for a 14:30-in-Riyadh session.

If your current code does `new Date(date)` (or any parser that treats a `Z`-less string as UTC, or
applies the device offset), the displayed time will be **wrong by the device's offset from Riyadh**
(e.g. −3h for a UTC device) once this ships.

---

## Why this changed

The `date` was being entered in the admin as a naive `datetime-local` (no timezone) but serialized to
the API as UTC (`toISOString()`). That mismatch silently shifted the time by the Riyadh offset every
time an admin re-saved a session/workshop. The fix makes the value **venue-local wall-clock
end-to-end** — matching how it is entered, and matching the existing cyan behavior. See ledger **D8**
for the full rationale.

## Exactly what to do (mobile)

- **Parse `date` as wall-clock**, not UTC. In practice: strip any TZ assumption and read the literal
  `YYYY-MM-DDTHH:mm:ss` components, or parse with an explicit `Asia/Riyadh` zone — **never** the device
  zone.
- **Display the components as-is.** No offset math. The event happens at that wall-clock time *at the
  venue*; that is the time to show every user.
- If you sort/group sessions by time, sort on the wall-clock value (lexical sort on the string works,
  since the format is fixed-width and no offset is present).

## Scope — what changed vs. what did NOT

**Changed (venue-local wall-clock, no `Z`)** — the scheduled agenda `date` in all 9 resources:
`SessionListResource`, `SessionDetailResource`, `FavoriteSessionResource`, `WorkshopListResource`,
`WorkshopDetailResource`, `RegisteredWorkshopResource`, and the sessions/workshops nested inside
`SpeakerResource` (admin `AdminSessionsResources` / `AdminWorkshopResource` too, but those are admin-only).

**UNCHANGED (still UTC ISO-8601 with `Z`)** — every audit/operational timestamp:
`created_at`, `updated_at`, `check_in_time`, and similar. Keep parsing those as UTC and converting to
device time as you do today. **Only the scheduled agenda `date` is venue-local.**

Also unchanged: field names, endpoints, and `routes/api.php`. This is purely a change in the string
*format/meaning* of one field's value.

## How to test after the backend releases

1. Fetch a session whose Riyadh start time is a round number (e.g. 14:30).
2. Set the test device to a non-Riyadh timezone (e.g. UTC or America/New_York).
3. Confirm the app still shows **14:30** — not 11:30, not 06:30. If it shifts, the parser is still
   applying an offset and needs the wall-clock fix above.

## Contact

Questions on the backend behavior → reference ledger **D8** and `tasks/002-datetime-db-cleanup/TASK.md`.
Please confirm receipt and flag if any mobile screen needs a coordinated release window.
