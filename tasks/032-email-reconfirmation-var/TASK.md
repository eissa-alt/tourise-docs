# Task 032 — Email editor: expose the reconfirmation link variable

- **Status:** `done (code)` — pushed + merged to `main` 2026-08-06; manual QA pending
- **Opened:** 2026-07-28
- **Owner:** —
- **Sub-app(s):** admin
- **Branch(es):** `dev`

## Goal

Make `{{ reconfirmation_url }}` insertable from the email editor's variable palette. The backend
resolver already substituted it (Task 020 / shared `ReconfirmationLink`), but the editor never listed
it — so the one way to use the feature was to type the placeholder from memory.

## Scope

- In: one entry added to `GUEST_VARIABLES` in `email-editor-waypoint.tsx`.
- Out: the resolver, the SMS/WhatsApp template editors, and the reconfirmation flow itself — all
  shipped in Task 020.

## Decisions

- **Palette-only change.** Nothing about resolution changes; this closes a discoverability gap in a
  feature that was otherwise complete.

## Log

- 2026-07-28 — admin `77cea97` (`P032.1`): 1 line.
- 2026-08-01 — documented (this file, index row, handoff). Unpushed at that point.
- 2026-08-06 — **pushed and merged to `main`** (admin PR #4 `4405a04`). Admin `type-check` clean.

## Definition of Done

- [x] Code committed on `dev` in the relevant sub-app(s)
- [x] EN + AR — the chip reuses the existing variable-label mechanism, no new keys
- [x] Quality gate — pre-commit hooks green at commit time
- [x] Docs updated (this TASK.md; index row; handoff)
- [x] Mobile contract unaffected — admin UI only
- [ ] **Push** admin `77cea97`
- [ ] Manual QA — insert the chip into a template, send, and confirm the link resolves for a guest
      (folds into Task 020's outstanding reconfirmation QA)
