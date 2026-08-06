# Task 031 — Automation: manual (run-later) option + run/split UI cleanup

- **Status:** `done (code)` — pushed + merged to `main` 2026-08-06; manual QA pending
- **Opened:** 2026-07-28
- **Owner:** —
- **Sub-app(s):** backend + admin
- **Branch(es):** `dev`

## Goal

Add a third scheduling choice to automations — save now, run later by hand — alongside D39's *immediate*
and *scheduled*. Plus the run/split UI cleanup and run-neutral wording that landed with it.

## Scope

- In: `schedule_type = manual` in `AutomationSetupsController::store`; a "Run manually after review"
  option in the scheduling step; a Run-now action on draft rows; `ConfirmModal` for run/cancel; the
  details page's "More" dropdown replaced by direct Run + Split buttons; run-neutral wording.
- Out: a new endpoint — a manual automation runs through the **existing** manual send endpoint
  (`POST /automations/send/{id}`), the same one the details page already used.

## Decisions

- **A manual automation is a draft: `schedule_type = 'manual'`, `send_status = 'draft'`, not
  dispatched on create.** It joins D39's state machine rather than introducing a parallel one; the
  dispatch-on-create branch is now `if (! $isScheduled && ! $isManual)`.
- **No migration needed.** `schedule_type` is `string(20)`, not an enum (migration
  `2026_07_25_000002`), so the third value is accepted as-is. Recorded so nobody "fixes" it with a
  redundant migration.
- **Run-now is gated on `send_status === 'draft'` in the listing**, and the backend still guards against
  re-running a started/split automation. Cancel remains gated on `send_status === 'scheduled'`.
- **Run-neutral wording (admin `af2a24a`, stamped `P027.1`).** Not every automation sends a message — an
  actions-only automation just changes status/category — so "Send immediately" → "Run immediately",
  "When to send" → "When to run", and the status "Sent" → "Completed". Translation **values** changed,
  keys unchanged, EN + AR.
- **`ConfirmModal` instead of the native `alert`/`confirm`** for both run and cancel, matching the rest
  of the admin.

## Known gaps (carried forward)

- **D39 parked item #2 is still open, and this task touched the same button.** The details page's Run
  action is *not* gated on `send_status`, so it can still dispatch a *scheduled* automation before its
  time. The listing's new Run button is gated; the details one is not.
- **The details page's Run button label is a hardcoded `'Run'` literal**, not a translation key (it was
  a hardcoded `'Send To All'` before, so this is pre-existing rather than a new regression) — it will not
  render in Arabic.
- **`automation-details.tsx` carries commented-out dead code** — the old `Menu` imports and the whole
  former "More" dropdown block were commented out rather than deleted. Worth a cleanup pass.

## Log

- 2026-07-28 — backend `6e7fd94` (`P031.1`): `AutomationSetupsController.php`, +12/−8. Admin `3fc30c9`
  (`P031.1`): `automation-listing.tsx` (+Run action, ConfirmModal), `automation-details.tsx`,
  `automation-settings-fields.tsx`, `send-emails-action.tsx`, `split-emails-action.tsx`, EN + AR
  (5 keys each). Admin `af2a24a` (`P027.1`): wording only, EN + AR.
- 2026-08-01 — documented (this file, index row, D39 addendum, handoff). All three commits still
  unpushed at that point (backend `6e7fd94`; admin `3fc30c9` + `77cea97`).
- 2026-08-06 — all three **pushed and merged to `main`** (backend PR #4 `fcc2541`, admin PR #4
  `4405a04`). Full quality gate re-run: pint + phpstan clean, 488/489 tests pass (the 1 failure is the
  pre-existing `SessionsTest::test_search_finds_matching_sessions` flake, unrelated), admin
  `type-check` clean. `yarn production` not run — no local `.env.production` (expected, D22).

## Definition of Done

- [x] Code committed on `dev` in the relevant sub-app(s)
- [x] EN + AR translations in the same commit
- [x] Quality gate — pre-commit hooks green at commit time; **full gate re-run 2026-08-06** (see handoff)
- [x] Docs updated (this TASK.md; index row; D39 addendum; handoff)
- [x] Mobile contract unaffected — `/admin/automations*`, `routes/api.php` untouched
- [x] **Push** backend `6e7fd94` + admin `3fc30c9` after the gate is re-run — done 2026-08-06, and both
      merged to `main`
- [ ] Manual QA — create a manual automation, confirm it is *not* dispatched on create, then Run it from
      the listing and confirm the fan-out happens exactly once
- [ ] Close or re-park the three known gaps above
