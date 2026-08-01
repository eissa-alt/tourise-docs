# Task 030 — Fix automation creation: `guest_status_id` only required when changing status

- **Status:** `done (code)` — manual QA pending
- **Opened:** 2026-07-28
- **Owner:** —
- **Sub-app(s):** backend
- **Branch(es):** `dev`

## Goal

Creating an automation that does **not** change guest status was blocked by validation. Make
`guest_status_id` genuinely optional unless the "change guest status" action is on.

## Scope

- In: one validation rule in `AutomationSetupsController::store`.
- Out: the `change_guest_status` action itself and the admin form.

## Decisions

- **Two bugs in one rule, both fixed:**
  1. `guest_status_id` had no `nullable`, so the `uuid|exists` rules ran against `null` and failed even
     when the field was legitimately absent.
  2. `required_if:change_guest_status,yes` matched the string `'yes'`, but the form sends a real
     **boolean** — so the condition never fired and the rule never applied when it should have.

  Result: `nullable|required_if:change_guest_status,true|uuid|exists:guest_statuses,id`.
- **Matched to what the form actually sends (`true`), not the other way round.** The admin form's boolean
  is the correct shape; the `'yes'` string was a leftover.

## Log

- 2026-07-28 — backend `5e40445` (`P030.1`): `AutomationSetupsController.php`, +4/−1.
- 2026-08-01 — documented (this file, index row, handoff).

## Definition of Done

- [x] Code merged to `dev` in the relevant sub-app(s)
- [x] EN + AR — no user-facing strings
- [x] Quality gate — pint clean at commit time (pre-commit hook); **`composer qa` not re-run since**
      (see handoff)
- [x] Docs updated (this TASK.md; index row; handoff)
- [x] Mobile contract unaffected — `/admin/automations-setups`, `routes/api.php` untouched
- [ ] Manual QA — create an automation with "change guest status" **off** (should save) and **on** with
      no status picked (should 422 on `guest_status_id`)
