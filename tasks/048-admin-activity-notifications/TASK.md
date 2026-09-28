# Task 048: Admin notifications (AdminActivity), the audit trail as a bell

- **Status:** `todo`: scoped and agreed with the owner on 2026-09-29, no code yet. Next: build on a
  branch off `dev`, after telling امتنان that their bell is being replaced.
- **Opened:** 2026-09-29
- **Owner:** unassigned
- **Sub-app(s):** backend + admin
- **Branch(es):** to be created off `dev`
- **Parked alongside:** [PARKED-ADD-AND-MOVE.md](PARKED-ADD-AND-MOVE.md), the two invitation actions
  that arrived in the same commit as امتنان's bell.

## Goal

The client does not want to open each record's history to find out what changed. Admins get a
**notification bell** showing the latest updates, and that feed **is the audit trail** (Task 045)
seen per admin: what happened since they last looked, read or unread. It starts with **invitation
collections and invitations** and grows to other modules on request, the same way the audit trail
does.

## Decisions (owner, 2026-09-29, asked one at a time)

| # | Decision |
|---|---|
| 1 | **Every audited action notifies**: created, updated, sent, sent in bulk, updated in bulk, moved (Extract), exported. Not a short list. |
| 2 | A **new section in the role editor**, "Admin notifications", with **one box per module**: Invitations (collections + invitations) for now; later Titles, Guests and others. A notification reaches an admin only if their role can also **view** that module, and the admin's **category restrictions** apply (a restricted admin never hears about a collection outside their categories). |
| 3 | **No separate "bell" box.** The bell shows whenever at least one box in "Admin notifications" is ticked. |
| 4 | **An admin's own actions never notify them.** |
| 5 | The bell covers **the last 30 days**, read or unread. Older events drop out of the bell and stay in the record history and the audit trail. When an admin first gets access, earlier events show **as already read**, so nobody starts with hundreds unread. |
| 6 | **Bell dropdown only** for now: newest first, "load more" within the 30 days, **Mark all as read**, and each line opens the record it is about. A full notifications page can come later. |
| 7 | The unread count is **checked every minute** (polling); the list is fetched when the bell opens. Live push can come later. |
| 8 | **Replace امتنان's bell** (backend `2ef2856`, admin `9af581d`, on `dev`, never on `main`, migrations run only on the owner's local DB). Reuse its look where it fits. |
| 9 | **Naming: `AdminActivity`**, free in tourise and pep-v2. Plain "Activity" is kept free for a real future module (and is what `spatie/laravel-activitylog` calls its model). |
| 10 | **No `/me/` routes** (owner dislikes them). The feed's routes sit under the feature's own path and always answer for the logged-in admin. |
| 11 | **Keep it apart from seating.** No shared tables, endpoints, controllers, or columns on `admins`. |

## Naming and routes

| Piece | Name |
|---|---|
| Role section (feature id) | `admin_activity`, labelled **"Admin notifications"** (EN + AR), box `invitations` |
| Controller | `AdminActivityController` |
| Service | `AdminActivityFeed`: builds one admin's feed from `audit_logs` |
| Tables | prefixed `admin_activity_…` (per-admin read state; nothing on `admins`) |
| Routes | `GET /admin/activity` (list, paged), `GET /admin/activity/unread-count`, `PATCH /admin/activity/{id}/read`, `POST /admin/activity/read-all` |
| Admin | `components/layout/admin-activity-bell.tsx`, strings `admin_activity_*` |

## Design (to confirm in code)

- **Read from the audit trail; store only read state.** No delivery row is copied per admin when
  something happens. Each request works out the admin's feed from `audit_logs` (their modules, their
  view permission, their categories, not their own actions, last 30 days). What is stored per admin is
  a **"read up to" time** (set on first access, so older events count as read, decision 5) plus
  **individual read marks** for items opened out of order. Consequences: a role change takes effect at
  once with nothing stale or leaked, a newly granted admin sees the recent month, and storage stays
  small.
- **Per module:** which feature an audit row belongs to is already on the row (`audit_logs.feature`).
  Adding a module later = a box in the section + nothing else, as long as the module is audited.
- **Index:** the unread count runs every minute per open admin tab; `audit_logs` needs an index that
  serves `(feature, created_at)` with the 30-day lookback.
- **Wording:** each line is rendered from the audit action and subject in EN and AR, reusing the
  audit trail's labels (`audit_action_*`) so the two never disagree.

## Why the existing "notification" code is not renamed (owner asked, 2026-09-29)

The owner considered renaming existing "notification" code (thought to be seating's) to free the name.
In tourise that code is **push notifications to guests' phones**, not seating: `AdminNotificationController`,
permission `notifications` (view, create), tables `app_notifications` + `notification_recipients`,
and `/mobile/notifications`. It is shared baseline code (pep-v2 has the same). Renaming it would touch
the **mobile contract**, every production role's stored permissions, and production tables, and would
make tourise differ from the baseline, so porting the new feature to pep-v2 would collide again. A new
name that is free everywhere (`AdminActivity`) gives the clean start instead.

Seating's admin notifications exist only in **pep-v2** (not in tourise): `admins.seating_notification_settings`
(2026-08-03), then `categories.seating_admin_ids` + `notification_settings[event][channel].notify_admins`
(2026-08-26), sent by `GuestSeatingObserver`. They are outbound messages through channels, not an
in-app bell. Nothing here may use those names, and nothing is stored on `admins`.

## What replacing امتنان's bell removes

All on `dev` (backend `2ef2856`, merged in `115fc5e`; admin `9af581d`, merged in `eabddbc`); none of it
is on `main`. **Do not merge `dev` to `main` until this task has replaced it**, or production gets the version
being removed plus its two migrations.

- Backend: `AdminNotificationsController`, `AdminNotification`, `AdminNotifier`,
  `AdminNotificationEvents`, migrations `2026_09_29_000001_create_admin_notifications_table` and
  `2026_09_29_000002_add_notification_events_to_admins_table` (replace them with a migration that drops
  what they created, since they ran on the owner's local DB), the `notification_events` pieces in
  `AdminsController` / `AdminsResources` / `Admin`, the five `/admin/me/notifications` routes, and the
  bell tests in `AdminNotificationsTest` (its 4 add/move tests move to their own file, see the parked
  file).
- `AuditLog::record()` returning its row can stay (harmless and useful).
- `InvitationsController`: the `AdminNotifier` calls in `store`, `addGuests`, `moveToCollection`,
  `extractBulk` become plain `AuditLog::record()` calls (the feed reads the trail, so they still notify).
- Admin: `components/layout/notifications-bell.tsx` (reuse the look), its line in `header.tsx`, the
  "who hears what" section in `admins-form.tsx`, `notification_events` in `interfaces/admin.tsx`, and
  its `web.json` strings (EN + AR).

## Open for later (not decided, not in scope)

- A full notifications page with filters (decision 6 leaves room for it).
- Live push instead of polling (decision 7).
- An admin muting things for themselves on top of their role.
- Email or other channels for notifications.
- Which modules follow Invitations.

## Concerns

- **Task 041** (security wave) has not run; the feed shows guest names from `audit_logs`, which 041
  should review together with Task 045.
- **Merge order:** `dev` currently carries امتنان's bell (see above); it must not reach `main` first.

## Log

- 2026-09-29: scoped with the owner in eleven questions (table above). Findings: امتنان's bell
  (`2ef2856` / `9af581d`, 2026-09-28) covered 3 of 4 events ("invitations sent" was never fired), used
  a per-admin setting on `admins` rather than role access, and sat one letter away from the push
  module's `AdminNotificationController`. Its 18 tests passed. Replaced by this design; the two
  invitation actions in the same commit are parked (see the parked file).

## Definition of Done

- [ ] Code merged to `dev` in the relevant sub-app(s)
- [ ] EN + AR translations in the same commit
- [ ] Quality gate green (backend `pint --test` + `phpstan` + `php artisan test`; admin `yarn type-check` + `yarn build` + `yarn check:rbac`)
- [ ] امتنان's bell removed, including a migration dropping its two tables/columns
- [ ] Docs updated (this TASK.md set to `done`; index row updated)
- [ ] Mobile contract checked: only `/api/admin` routes touched
