# AI Rules — alt-static-basecode

Binding rules for any AI agent operating in this repo.

## Must do

1. **Read the file you're about to change first.** Match its style and structure.
2. **EN + AR translations in the same commit.** No hardcoded user-facing strings in either Next app (`-admin`, `-frontend`).
3. **Preserve existing API response shapes.** This repo has an external mobile consumer — see `docs/mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf` before touching `routes/api.php` or `app/Http/Resources/*`.
4. **Use `checkActionPermission()`** for action gating in the admin UI.
5. **Email templates** follow the rules in `alt-static-basecode-backend/DARK_MODE_EMAIL_NOTES.md`.
6. **Push notifications** go through `AppNotification` + `NotificationRecipient` + `DeviceToken`. Do not call providers directly from controllers.
7. **Quality gate before any push:**
   - Backend: `php artisan test --filter <FeatureTest>` for the touched area.
   - Each touched Next app: `yarn type-check` + `yarn production`.

## Must not

1. **Do not touch `.env*` files** or the deploy key `alt-static-basecode.pem` (one level above the repos folder).
2. **Do not bump framework versions** (Next, React, Laravel, PHP) without an explicit task and a dedicated branch. This project is still Next 12 / React 17.
3. **Do not break the mobile API contract.** If a change is unavoidable, the `docs/mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.*` file gets a matching update in the same PR.
4. **Do not delete or replace the form-shapes pattern** — `components/admin-modules/guests/froms/` (admin) and `components/join/forms/` (frontend), driven by `FORM_SHAPES_CONFIG` + the `loadStepComponent` registries. cyan-basecode retired that pattern; this baseline has not, and CLAUDE.md hard rule 4 still stands (do not port cyan's `DynamicFormRenderer`). The *pattern* is protected, not the client folder names: the `pif/` subtree was renamed to `default/` in P22.1 (the baseline ships no client-branded shapes), so a future clone renames `default/` → its own client rather than resurrecting `pif/`.
5. **Do not re-add Sentry.** It was removed from admin, frontend and backend by the OWASP hardening; there are no `sentry.*.config.ts` files left and neither `@sentry/nextjs` nor `sentry/sentry-laravel` should return (CLAUDE.md hard rule 3).
6. **Do not introduce new dependencies** without justification.
7. **Do not rename files, classes, or routes** unless required by the task.
8. **Do not edit `assets*/`, `badges/`, `documents/`, `fav/`, `fonts/`, `seo/`, `tech docs/`, `import_Test/`** one level above this repos folder — those are client-supplied assets and one-off sheets, not code.
9. **Do not reformat unrelated code** in the same commit as a feature change.
10. **Do not widen TypeScript to `any`** to silence build errors.
11. **Do not leave `console.log` / `dd()` / `dump()`** in committed code.
12. **Do not branch on `user.type === 'super'`** in new code. Move toward `checkActionPermission()`.

## When in doubt

- Grep for an existing similar entity (e.g. `Session`, `Workshop`, `Publication`, `MediaCenter`) and copy the pattern.
- For form work: `FORM_RESTRUCTURE_GUIDE.md`.
- For email work: `EMAIL_EDITOR_UPDATES.md` + `DARK_MODE_EMAIL_NOTES.md`.
- For admin redesign: `admin_ui_ux_refactor_plan.md` + `advanced_admin_redesign_rollout_checklist.md`.
- For the mobile contract: `docs/mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf`.
- Otherwise: stop and ask. Do not invent.

## Presenting multi-option decisions (planning tasks)

When a task carries several design choices (planning, ports, refactors), surface them to the owner like this
(validated on Task 021):

1. **One decision at a time**, in sequence — not a batched wall of questions.
2. **"The problem, plainly"** — state what's being decided and why it matters, in short, simple language.
3. **List options** as short labelled choices (a/b/c), each one line, with the concrete trade-off.
4. **Give an explicit recommendation** + a one-line why; mark it "(recommend)".
5. **Ask to lock it** ("Lock Qn = (a)?"), then **record the answer in the task's `TASK.md` Decisions section
   (marked LOCKED)** before moving on. Promote durable ones to `../decisions/LEDGER.md` on completion.

Keep replies short. Prefer this conversational one-by-one flow over batching many questions into one modal.
