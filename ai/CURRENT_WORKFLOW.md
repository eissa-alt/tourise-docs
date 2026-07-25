# Current Workflow — alt-static-basecode

## Dev commands

### Backend

```bash
cd alt-static-basecode-backend
composer install
cp .env.example .env && php artisan key:generate     # first time only
php artisan migrate
php artisan db:seed                                    # optional default data
php artisan serve                                      # http://localhost:8000
```

### Admin / Frontend

```bash
cd alt-static-basecode-admin       # or -frontend
yarn install
yarn local                              # dev server with .env.local
yarn type-check                         # tsc only
yarn production                         # full build → catches lint + type errors
yarn check:rbac                         # ADMIN ONLY — sidebar featureId ↔ inferFeatureId parity (D33/D34)
```

> **`yarn check:rbac` is part of the admin gate** (not frontend). It cross-checks every sidebar `featureId`
> against `inferFeatureId` and fails on a mismatch — the `inferFeatureId` first-match-wins bug class that
> has shipped repeatedly (D33 six times, D40-era WhatsApp once more). It is a **separate** script — NOT run
> by `type-check` / `production` / `composer qa` — so run it explicitly on any change that touches routes,
> the sidebar, or `utils/inferFeatureId.ts`.

`.env.*` files are gitignored. `yarn.lock` is committed — do not switch to npm. **Sentry has been removed** (admin + frontend + backend) by the OWASP hardening — there are no `sentry.*.config.ts` files and `@sentry/nextjs` / `sentry/sentry-laravel` must not be re-added (CLAUDE.md hard rule 3). Note there are **two** Next apps, not three; the `-landing` app was dropped (ledger D2).

## End-to-end "add a feature" flow

Same as the other event-platform repos, with three extra considerations:

1. **Migration** — `database/migrations/2026_..._<concern>.php`. One concern per file.
2. **Model** — `app/Models/<Thing>.php`. JSON casts, relations, no business logic.
3. **Validation** — Form Request or inline `Validator::make()` — match the file you're editing.
4. **Service** — extract business logic into `app/Services/` if it spans models / external calls.
5. **Controller** — `app/Http/Controllers/<Thing>Controller.php`. Thin. Response `{ status, data }`.
6. **API Resource** — `app/Http/Resources/<Thing>Resource.php`.
7. **Route** — `routes/api.php`. If this endpoint is consumed by mobile, update `docs/mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.*` in the same PR.
8. **Admin axios** — `alt-static-basecode-admin/apis/modules/<thing>/`.
9. **Frontend axios** (if public-facing) — `alt-static-basecode-frontend/apis/modules/<thing>/`.
10. **Admin components + pages** — `components/admin-modules/<thing>/` + `pages/[lang]/<thing>/`.
11. **Permissions** — `checkActionPermission()` + shared SSR guard.
12. **Translations** — EN + AR keys in `translations/{en,ar}/web.json` (and namespaces as needed), **same commit.**
13. **History log + automation hook** — emit a `HistoryLog`; if there's an event other parts should react to, wire a listener/automation.
14. **Push notification?** — go through `AppNotification` + `NotificationRecipient` + `DeviceToken`. Don't call providers directly.

## Common AI tasks

| Task | Where to look first |
|---|---|
| Add an admin listing | clone an existing `components/admin-modules/<entity>/` (PIF-specific: `agenda/`, `sessions/`, `workshops/`, `publications/`, `media-center/`, `meeting-rooms/`, `notifications/`) |
| Add a session / workshop / agenda entry | `Session` / `Workshop` / `Agenda` models + admin pages under `pages/[lang]/sessions/` etc. |
| Add a feedback flow | `SessionFeedback` / `WorkshopFeedback` + relevant admin page + mobile contract update |
| Add a media item | `MediaCenter` + `MediaImage` / `MediaVideo` + `media-center/` admin page |
| Add a publication | `Publication` + `publications/` admin page |
| Add a meeting-room slot | `MeetingRoom` + `MeetingRoomSlot` + `meeting-rooms/` admin page |
| Add a push notification | `AppNotification` + `NotificationRecipient` + listener; respect `DeviceToken` |
| Add an in-app chat feature | `ChatRoom` + `ChatMessage` |
| Add a dynamic-form flow | `components/admin-modules/guests/froms/<project>/<flow>/` + `data/form-shapes-config.tsx` (admin); mirror in `-frontend/` `components/join/forms/<project>/…` |
| Tweak an email template | blade in `resources/views/emails/`; respect `DARK_MODE_EMAIL_NOTES.md` |

## Where docs live

- Repo root: `EMAIL_EDITOR_UPDATES.md`, `admin_ui_ux_refactor_plan.md`, `advanced_admin_redesign_rollout_checklist.md`, `OUTDATED_PACKAGES_REPORT.md`, `cursor_laravel_framework_upgrade_recomm.md`.
- `alt-static-basecode-admin/FORM_RESTRUCTURE_GUIDE.md` — dynamic-form folder layout.
- `alt-static-basecode-backend/DARK_MODE_EMAIL_NOTES.md` — email-template rules.
- `docs/` — backend changes for mobile (PDF + HTML).
- `docs/ai/` (this folder) — AI handoff.
- `Fund v2/` — client-supplied design / spec drops.
