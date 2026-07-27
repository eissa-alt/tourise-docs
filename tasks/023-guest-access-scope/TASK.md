# Task 023 — Scope single-guest reads to the admin's categories/statuses

- **Status:** `done` — committed + **pushed** (`origin/dev`)
- **Opened:** 2026-07-27
- **Owner:** —
- **Sub-app(s):** backend
- **Branch(es):** `dev`

## Goal

Close a read-scope hole: `applyAdminGuestAccessFilter` scoped guest **list** queries, but the
**single-record** reads (`GET /admin/guests/{id}` and `GET /admin/history-logs/{id}`) did not — a
scoped admin holding a UUID could open any guest, regardless of the categories/statuses they are
bound to. This mattered more after Task 022, which put the field-level before/after of every edit
behind the history endpoint.

## Scope

- In: a single-record twin of the list-scope filter, applied to `GuestsController::show` and
  `HistoryLogsController`.
- Out: `GuestDraftsController::show` has the same shape and `guest_drafts` does carry `category_id`,
  but it is a separate RBAC feature and whether drafts should be category-scoped at all is undecided —
  left deliberately.

## Decisions → promoted to LEDGER D44

- New `App\Support\GuestAccessScope::denies()` mirrors the list filter exactly: super bypasses; an admin
  with **no** restrictions set sees nothing (the list filter answers that with `0 = 1`); category and
  status bounds are ANDed; `null` is allowed in the status list for the admin UI's "No-Value" option.
  Shape follows `GatesController::deniesGateScope`. **If either side's rules change, change both.**
- Behaviour change: a scoped admin who could previously open any guest by UUID now gets **403**. The
  listing never showed them those guests, so no legitimate flow should depend on it.

## Log

- 2026-07-27 — `P023.1` (`ae1c210`): added `GuestAccessScope`, wired into `GuestsController::show` +
  `HistoryLogsController`. Gates: pint + phpstan clean, 489 tests (5 new). Committed + pushed to
  `origin/dev`. (Documented retroactively alongside Task 024.)

## Definition of Done

- [x] Code merged to `dev` and pushed
- [x] Quality gate green (pint + phpstan + 489 tests)
- [x] Docs updated (this TASK.md; index row; ledger D44; handoff)
- [x] Mobile contract unaffected (`/admin/*` reads; `routes/api.php` untouched)
- [ ] Manual RBAC matrix QA with a real scoped login
