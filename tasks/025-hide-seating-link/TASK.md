# Task 025 — Hide the Seating Manager link from the guests listing

- **Status:** `done`
- **Opened:** 2026-07-28
- **Owner:** —
- **Sub-app(s):** admin
- **Branch(es):** `dev`

## Goal

Remove the `seating`-gated "Seating Manager" deep-link button from the guests-listing toolbar, so the
standalone seating SPA is not advertised from the admin until it is wanted.

## Scope

- In: the toolbar button in `guests-listing.tsx` (plus its now-unused `OpenSeatingManagerButton` and
  `checkFeaturePermission` imports).
- Out (deliberately left in place): the `seating` RBAC feature, the `alt-static-basecode-seating`
  sub-app, the `OpenSeatingManagerButton` component itself, its EN/AR labels, the backend
  `/admin/seating-*` endpoints, and `NEXT_PUBLIC_SEATING_MANAGER_URL`.

## Decisions

- **Hide the link, keep everything behind it.** Re-adding the button is a one-line change; nothing was
  deleted, so Task 021's work is not unwound. No permission or routing impact — an admin with the
  `seating` feature can still reach the SPA by its own URL, and its own login/RBAC still applies.
- **This partially reverses the "admin deep-link launch button" half of ledger D42.** Recorded there as
  an addendum so a future reader doesn't chase a button that no longer renders.

## Log

- 2026-07-28 — admin `5b19580` (`P025.1`). 1 file, +1/−7.
- 2026-08-01 — documented (this file, index row, D42 addendum, handoff) after a drift sweep found
  P025–P032 undocumented.

## Definition of Done

- [x] Code merged to `dev` in the relevant sub-app(s)
- [x] EN + AR — no string change (labels kept, unused)
- [x] Quality gate — pre-commit hook (eslint/prettier) green; no type surface changed
- [x] Docs updated (this TASK.md; index row; D42 addendum; handoff)
- [x] Mobile contract unaffected — admin UI only, `routes/api.php` untouched
