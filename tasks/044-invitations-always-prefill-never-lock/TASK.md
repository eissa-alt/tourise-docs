# Task 044 — An invitation always prefills, and never locks

- **Status:** `in-progress` — code written and gates green, uncommitted, awaiting the owner's review
- **Opened:** 2026-09-23
- **Owner:** —
- **Sub-app(s):** admin
- **Branch(es):** `dev`

## Goal

From the team (2026-09-23): "Hide the locked data button from creating the invitation" and "make the
prefilled option forced on always, not to be turned off."

So: **Prefill data** shows on and takes no input, and **Lock data** is off the page. A guest opening
their invitation finds their details already filled in, and can always correct them.

## Scope

- In: the invitation **create** form and the **single-invitation edit** screen
  (`/invitations/details/{id}/edit/{code_id}`) — the owner asked for both, so an admin cannot
  re-lock an invitation after it is made.
- Out:
  - **The duplicate-emails popup is on hold** at the team's request, until they have tested what
    happens today. For that test: an imported file with the same email twice raises a red toast,
    "Duplicate email: …", listing them, and **clears the uploaded sheet**, so the file has to be
    chosen again. The check is case-insensitive and covers only that one file; an address that is
    already a registered guest is refused separately by the server, with its own message.
  - The API still accepts `prefilldata` / `lock_data` from any caller — this is a change to the two
    admin screens, not an enforced rule.
  - Request an Invitation categories keep their own Lock data setting; different feature, untouched.
  - Multiple-use collections keep `prefilldata: false`: a shared link belongs to nobody, so there is
    nothing to prefill.

## Log

- 2026-09-23 — create form (`invitations-form.tsx`): the Prefill switch is rendered on and
  `disabled`, with its help text kept; the Lock switch and its help text are gone. The payload sends
  `prefilldata: usage_type !== 'multiple'` and `lock_data: false`, and the form's defaults match.
- 2026-09-23 — edit screen (`invitation-form.tsx`), same treatment, same reasons. **Note:** that
  screen now sends `lock_data: false` on every save, so editing an invitation that was locked before
  this change unlocks it. Locally nothing is locked (0 of 6 invitations), and the team wants lock
  unused, so this is the intended direction rather than a surprise.
- 2026-09-23 — `web:lock_data` and `web:lock_data_help` stay: the see-more panel still shows what an
  invitation holds, and the Request an Invitation category form has its own switch.
- 2026-09-23 — gates: admin `yarn type-check`, eslint, prettier, `yarn build` green. No backend
  change, so no PHP gate to run.

## Decisions

- **Prefill is shown, not hidden** (owner, 2026-09-23): an admin can see that invitations prefill,
  rather than the behaviour being invisible.
- **The edit screen follows the create form** (owner, 2026-09-23), so the two cannot disagree.

## Definition of Done

- [ ] Code merged to `dev` in the relevant sub-app(s)
- [x] EN + AR translations in the same commit (none — strings only removed from a screen, and both
      keys are still used elsewhere)
- [x] Quality gate green (admin `yarn type-check` + `yarn build` + `yarn check:rbac`)
- [ ] Docs updated (this TASK.md set to `done`; index row updated)
- [x] Mobile contract checked — no `routes/api.php` change
