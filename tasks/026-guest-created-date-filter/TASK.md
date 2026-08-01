# Task 026 — Filter guests by creation date range

- **Status:** `done (code)` — manual browser QA pending
- **Opened:** 2026-07-28
- **Owner:** —
- **Sub-app(s):** backend + admin
- **Branch(es):** `dev`

## Goal

Let an admin narrow the guests listing (and every guests export) to a registration-date window.

## Scope

- In: `created_from` / `created_to` bounds on the backend's shared `applyFilters()`; a date-range input
  in the guest search panel, threaded through the listing fetch, pagination and the export query string.
- Out: any other date field (the reconfirmation / attendance dates keep their own filters), and a
  time-of-day component.

## Decisions

- **Filter goes in the shared `applyFilters()`, not the `index` method.** That helper already backs both
  the listing and all guests exports, so the range applies to exports for free and cannot drift between
  the two.
- **`whereDate`, so both bounds are inclusive and date-only.** `created_at` is a real UTC timestamp;
  comparing the date part avoids the "end date excludes that day" trap of a naive `<=` against a
  timestamp. Either bound may be supplied on its own.
- **Admin sends `YYYY-MM-DD`** — the new `date-range-input.tsx` (react-day-picker in range mode, inside
  the shared `DialogShell`) reads and writes exactly the two backend query params, so it stays a drop-in
  with no mapping layer.

## Log

- 2026-07-28 — backend `6abee02` (`P026.1`): 10 lines in `GuestsController::applyFilters()`.
  Admin `6978795` (`P026.1`): new shared `components/shared/forms/date-range-input.tsx` (+154),
  wired into `search-guests-by-super.tsx`, `guests-listing.tsx`, `pages/[lang]/guests/index.tsx`
  and `utils/fetch-data-url.ts`.
- 2026-08-01 — documented (this file, index row, handoff).

## Definition of Done

- [x] Code merged to `dev` in the relevant sub-app(s)
- [x] EN + AR translations in the same commit
- [x] Quality gate — pre-commit hooks green at commit time; **full gate not re-run since** (see handoff)
- [x] Docs updated (this TASK.md; index row; handoff)
- [x] Mobile contract unaffected — `/admin/guests` only, `routes/api.php` untouched
- [ ] Manual browser QA — pick a range, confirm the listing, pagination and an export all honour it,
      and that a single open-ended bound works
