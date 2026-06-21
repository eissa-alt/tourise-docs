# Coding Style — alt-static-basecode

Short crib sheet. The actual codebase + `EMAIL_EDITOR_UPDATES.md` + `admin_ui_ux_refactor_plan.md` + `FORM_RESTRUCTURE_GUIDE.md` are the authoritative references for their topics.

## Frontend (admin / frontend / landing — Next 12 + TS + Tailwind)

- **Functional components only.** Hooks-based.
- **Translations:** `useTranslate()` / `<Translate>` — every user-facing string. Keys in `translations/en/*.json` and `translations/ar/*.json`. EN + AR **same commit.**
- **Pages stay thin.** Logic lives in `components/admin-modules/*` (admin) or feature components (frontend/landing), or in `hooks/`.
- **API calls** use `Axios`; tokens via `cookie`. Group callers under `apis/modules/<feature>/`.
- **Fetching pattern:** local `loading`, `hasError`, `setX` state. Reuse helpers like `fetch-data-url`.
- **Naming**
  - Files: `kebab-case`
  - Components: `PascalCase`
  - Types: `PascalCase`, props: `camelCase`
  - Wire query params: `snake_case` (`guest_status_ids`, `secondary_status_ids`)
- **Permissions:** `checkActionPermission()` for action visibility; shared SSR guard, not per-page checks.
- **UI primitives:** prefer existing shared inputs/selects/modals. Don't re-layout JSX without reason.
- **Dynamic forms:** see `alt-static-basecode-admin/FORM_RESTRUCTURE_GUIDE.md`.
- **Email editor:** the rich-text/block editor was iterated heavily — see `EMAIL_EDITOR_UPDATES.md` before touching.
- **Admin UI/UX redesign in progress:** `admin_ui_ux_refactor_plan.md` + `advanced_admin_redesign_rollout_checklist.md` — follow the locked decisions there for new admin screens.

## Backend (Laravel 11 + PHP 8.2)

- **Controllers** are thin. Validation with `Validator::make()` or Form Requests — match the surrounding file. Response shape `{ status, data, message? }`.
- **API Resources** under `app/Http/Resources/`. Use `whenLoaded` for relations.
- **Models** keep JSON casts (`'array'`), declare relations, no business logic.
- **Migrations** one concern per file, descriptive name.
- **Services** (`app/Services/`) for business logic that touches multiple models or external services.
- **Emails:** blade templates under `resources/views/emails/`. Follow the dark-mode rules in `DARK_MODE_EMAIL_NOTES.md` (inline styles, no `prefers-color-scheme` reliance on Outlook, etc.).
- **Mobile contract endpoints:** before changing any `routes/api.php` entry, check `docs/mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf`. If the mobile app consumes it, the change goes in a paired update.
- **Push notifications:** route through the `AppNotification` model + listeners/jobs; do not call providers directly from controllers.

## Permissions direction

- Action visibility: `checkActionPermission()`.
- Empty arrays mean "no selection" — handle consistently FE + BE.
- Move new code away from `user.type === 'super'` toward permission gating.

## Do / Don't

**Do**
- Reuse existing utilities and listing primitives.
- Add EN + AR translations in the same commit.
- Keep migrations small and reversible.
- Keep response shapes stable for endpoints with external consumers (mobile, integrations).

**Don't**
- Add new dependencies without justification.
- Rename files / classes / routes unless required.
- Add `console.log` / `dd()` / `dump()` to committed code.
- Reformat unrelated code in the same commit.
- Break the mobile API contract.
