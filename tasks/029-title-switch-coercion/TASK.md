# Task 029 — Fix title creation: coerce optional switches to booleans

- **Status:** `done (code)` — manual QA pending
- **Opened:** 2026-07-28
- **Owner:** —
- **Sub-app(s):** backend
- **Branch(es):** `dev`

## Goal

Creating a title failed when its optional toggles were left untouched. Coerce them so an untouched
switch stores `false` instead of a constraint-violating `null`.

## Scope

- In: `TitlesController::store` + `update`.
- Out: the columns themselves (they stay NOT NULL — that is the correct shape) and the admin form.

## Decisions

- **Fix at the controller, not the schema.** `show_in_badge` / `show_in_user_form` are NOT NULL columns;
  an unchecked switch simply isn't submitted, so `$request['show_in_badge']` was `null` and the insert
  violated the constraint. `$request->boolean(...)` is the same coercion `is_active` already used one
  line above — this makes the three consistent rather than loosening the columns.
- **Same coercion applied in `update`**, which had the identical bug on the `$request->has(...)` branches.
- **Two adjacent defensive fixes in the same commit:** `order` defaults to `0` when absent, and
  `allowed_genders` json-encodes `[]` rather than `null` when absent.
- Also deleted a stale `// todo :check why is not working` comment above a commented-out
  `Title::create($request->all())` — the explicit array *is* the working version, and this task explains
  why the mass-assign form failed.

## Log

- 2026-07-28 — backend `7b23178` (`P029.1`): `TitlesController.php`, +8/−10.
- 2026-08-01 — documented (this file, index row, handoff).

## Definition of Done

- [x] Code merged to `dev` in the relevant sub-app(s)
- [x] EN + AR — no user-facing strings
- [x] Quality gate — pint clean at commit time (pre-commit hook); **`composer qa` not re-run since**
      (see handoff)
- [x] Docs updated (this TASK.md; index row; handoff)
- [x] Mobile contract unaffected — `/admin/titles`, `routes/api.php` untouched
- [ ] Manual QA — create a title with both switches left off; confirm it saves and reads back as `false`
- [ ] No automated test covers title create/update
