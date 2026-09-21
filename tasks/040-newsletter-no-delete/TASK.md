# Task 040 — Newsletter subscribers and templates can no longer be deleted

- **Status:** `done (code)` — admin pushed to `dev` 2026-09-21; **kept off `main` on the owner's word**
- **Opened:** 2026-09-21
- **Owner:** —
- **Sub-app(s):** admin
- **Branch(es):** `dev`

## Goal

Remove the Delete action from the newsletter's **Subscribers** and **Newsletter Templates**
listings (owner, 2026-09-21: "remove Delete action in subscriber or template in newsletter").

## Scope

- In: the two admin listings — the action, its confirm dialog, and the request behind it.
- Out: the backend `DELETE /admin/newsletter/subscribers/{id}` and `/templates/{id}` routes stay —
  nothing in the admin calls them now, but the API still accepts them. Newsletter **Lists** keep
  their delete (not asked).

## Log

- 2026-09-21 — admin `d6683ec` on `dev`. Subscribers: Delete was the only row action, so the
  **Actions column is gone** with it. Templates: Delete leaves the row menu; Clone / Activate /
  Block stay, and **Block** is how a template is retired. `tsc` and eslint clean on both files.
- 2026-09-21 — the owner chose to keep it on `dev`: admin `main` is three commits behind `dev`
  (Tasks 038 + 039), and backend `main` has neither the Dignitary Parties routes nor the dashboard
  filters, so merging `dev` → `main` would have shipped an admin whose new pages 404 on production.

## Decisions

- Retire, don't delete: a template goes out of use with **Block**; a subscriber leaves by
  unsubscribing (the send already skips them).

## Definition of Done

- [x] Code merged to `dev` in the relevant sub-app(s)
- [x] EN + AR translations in the same commit (none — strings only removed)
- [ ] Quality gate green — `tsc --noEmit` + eslint green; `yarn production` not run
- [x] Docs updated (this TASK.md; index row; HANDOFF)
- [x] Mobile contract checked — no `routes/api.php` change
