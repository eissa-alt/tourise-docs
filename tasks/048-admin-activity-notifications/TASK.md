# Task 048: Admin notifications (AdminActivity), the audit trail as a bell

- **Status:** `done (code)`: **merged to `dev` on 2026-09-29** (backend PR #22 `46ee2b8`, admin PR
  #25 `bf34baf`), **on `main` the same day** (backend PR #23, admin PR #26), **not deployed**. Built on
  `feat/admin-activity`: backend `191593c` `c80a5d2` `e687507` `855c78d` + merge of `dev` `a1e0a46`;
  admin `13979fa` `86961aa` `8e357bb` `648b23c`. **Production needs four migrations**
  (`2026_09_29_000003` to `000006`, see *Deploy*). Team testing next; امتنان to be told their bell
  was replaced.
  **Follow-up, set per admin on the admin form (decision 14):** backend `3392b13`, admin `f3b23f4`,
  **merged to `dev` and `main` on 2026-09-30** (backend PRs #24 / #25, admin PRs #27 / #29), with the
  list preload fix `d3b46d1`. `main` no longer has the Roles version.
- **Opened:** 2026-09-29
- **Owner:** unassigned
- **Sub-app(s):** backend + admin
- **Branch(es):** `feat/admin-activity` in `tourise-backend` + `tourise-admin`, off `dev` (`115fc5e` /
  `eabddbc`)
- **Parked alongside:** [PARKED-ADD-AND-MOVE.md](PARKED-ADD-AND-MOVE.md), the two invitation actions
  that arrived in the same commit as امتنان's bell. **Done since as
  [Task 050](../050-add-people-and-move/TASK.md)** (2026-09-30).

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
| 2 | A **new section in the role editor**, "Admin notifications", with **one box per module**: Invitations (collections + invitations) for now; later Titles, Guests and others. A notification reaches an admin only if their role can also **view** that module, and the admin's **category restrictions** apply (a restricted admin never hears about a collection outside their categories). | *Superseded by 14: set per admin, on the admin form.*
| 3 | **No separate "bell" box.** The bell shows whenever at least one box in "Admin notifications" is ticked. *Now: the bell shows when the admin hears about at least one module (ticked for them, and viewable by their role).* |
| 4 | **An admin's own actions never notify them.** |
| 5 | The bell covers **the last 30 days**, read or unread. Older events drop out of the bell and stay in the record history and the audit trail. When an admin first gets access, earlier events show **as already read**, so nobody starts with hundreds unread. |
| 6 | **Bell dropdown only** for now: newest first, "load more" within the 30 days, **Mark all as read**, and each line opens the record it is about. A full notifications page can come later. |
| 7 | The unread count is **checked every minute** (polling); the list is fetched when the bell opens. Live push can come later. |
| 8 | **Replace امتنان's bell** (backend `2ef2856`, admin `9af581d`, on `dev`, never on `main`, migrations run only on the owner's local DB). Reuse its look where it fits. |
| 9 | **Naming: `AdminActivity`**, free in tourise and pep-v2. Plain "Activity" is kept free for a real future module (and is what `spatie/laravel-activitylog` calls its model). |
| 10 | **No `/me/` routes** (owner dislikes them). The feed's routes sit under the feature's own path and always answer for the logged-in admin. |
| 11 | **Keep it apart from seating.** No shared tables, endpoints, controllers, or columns on `admins`. |
| 12 | **A bulk send and a bulk update record their collection** as the audit row's subject (owner, 2026-09-29, while building), so the category rule can place them. Forward-only. It also puts them in the trail opened from that collection, which never showed them. |
| 13 | **A row that names no collection** (an export of the whole collections list, of collections with their invitations, or of the audit trail) **reaches everyone with the box**, restricted or not (owner, 2026-09-29): the line shows no record, so nobody sees past their categories. |
| 14 | **Set per admin, on the admin create/edit form, not per role** (the team's ask, owner, 2026-09-29, after the merge to `dev`). Two admins in the same role can want different things, and the form already holds the categories the bell follows. Stored in `admin_activity_subscriptions` (admin + module), still nothing on `admins` (11 holds). A ticked module counts only where the role can view it. **Super Admins are no exception**: a module has to be ticked for them too, which answers the team's question of whether they can turn it off. The form has Select all, and greys out a module the chosen role cannot view. |

## Naming and routes

| Piece | Name |
|---|---|
| Where it is set | the admin create/edit form, section **"Admin notifications"**, one box per module (decision 14; was a role section `admin_activity` until then) |
| Controller | `AdminActivityController` |
| Service | `AdminActivityFeed`: builds one admin's feed from `audit_logs` |
| Tables | `admin_activity_cursors` (read up to, per admin per module), `admin_activity_reads` (lines opened one by one); nothing on `admins` |
| Routes | `GET /admin/activity` (list, paged), `GET /admin/activity/unread-count`, `PATCH /admin/activity/{id}/read`, `POST /admin/activity/read-all` |
| Admin | `components/layout/admin-activity-bell.tsx`, strings `admin_activity_*`; role labels `perm_feature_admin_activity`, `perm_hint_admin_activity` |

## Design (built; see *What changed while building* where they differ)

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

## What changed while building (2026-09-29)

1. **The cursor is per admin per module**, not per admin. It is created the first time that admin's
   bell asks about the module, at that moment. Decision 5 then holds for a module added later too:
   ticking Titles next year does not arrive as a month of unread Titles lines.
2. **`as_of`.** The list returns when its first page was served. Later pages send it back so they do
   not shift while lines arrive, and **Mark all as read** sends it so a line that came in after the bell
   opened, and was never on screen, stays unread. Mark all as read also deletes the one-by-one marks
   the cursor then covers, so `admin_activity_reads` stays small.
3. **The catalogue's "every feature has `view`" rule.** `admin_activity`'s boxes are modules, and there
   is no page to view (decision 3: no bell box). Nothing in the code relied on `view` being present
   (page access and `admin.can` take any action); only `AdminPermissionsTest` did. It now checks
   instead that each `admin_activity` box is a real feature.
4. **A line carries no payload and no token**: the action, who, the record, the collection it sits in
   (id + current name), a count, the export scope, read or not. The audit payloads hold names and emails
   the line does not need.
5. **Where a line opens:** its collection (`/invitations/details/{id}`). An invitation's line opens the
   collection it sits in, since its own screen is an edit form and the bell also reaches view-only
   admins. A line with no collection opens the Invitations list.
6. **The collection's `created` row is no longer edited after it is written.** امتنان's `store` looked
   the row up again and rewrote its payload to add a count; the count is already there
   (`total_invites`). Extract's row is back to what Task 045 wrote (the `from`/`to` names were for her
   sentence, and the trail already names both collections from their ids).
7. **امتنان's two migrations were rolled back on the owner's local DB** (`migrate:rollback --step=2`,
   2026-09-29, they were alone in batch 3) before their files were deleted. `2026_09_29_000003` drops
   the same table and column wherever they still exist (امتنان's DB, for one) and does nothing
   elsewhere.
8. **Found:** امتنان's bell never reached its API. The admin's Axios already calls through
   `/api/proxy` to `.../api/admin`, so `/admin/me/notifications` became `/api/admin/admin/me/...` and
   404'd, which the bell swallowed. Its links also pointed at `/invitations-collection/details/{id}`,
   which is not a page.
9. **Merged with `dev` (`a1e0a46`, 2026-09-29).** امتنان pushed `8f6fca8` to `dev` while PR #22 was
   open: her bell's "invitations sent" event, with the bulk send's row naming its collection. The merge
   keeps her way of finding that collection (from the invitations actually sent, none when they span
   more than one) over `c80a5d2`'s (from the URL), drops her call to the old bell and its tests, and adds
   a test for the two-collection case.
10. **Merged to `dev`** by the owner on GitHub the same day: backend PR #22 (`46ee2b8`), admin PR #25
   (`bf34baf`). `dev` no longer carries امتنان's bell, so the bell no longer blocks `dev` → `main`.
11. **The list is ready before the bell opens** (team feedback: it took a moment to show). Admin
   `d3b46d1`, pushed to `dev` by the owner: fetched in the background when the bell appears and whenever
   the unread count changes; refreshed quietly on open and every minute while open.
12. **Moved from Roles to the admin form** (decision 14), on `feat/admin-activity-per-admin`: backend
   `3392b13` (the subscriptions table, `admin_activity` saved on admin create/edit and read on show,
   `GET /admin/admins/activity-modules` for the form, `get-profile` returns the modules the admin will
   hear, the bell's routes answer 403 to an admin who hears none, the catalogue section removed); admin
   `f3b23f4` (the form section, the header reads the profile, Roles back to what it was). 969 backend
   tests; a role that had the old box keeps a stale key that nothing reads.

## Deploy

- **Migrations:** `2026_09_29_000003_drop_the_replaced_admin_notifications` (does nothing on
  production), `2026_09_29_000004_create_admin_activity_tables`,
  `2026_09_29_000005_add_feature_created_at_index_to_audit_logs`, and with the follow-up
  `2026_09_29_000006_create_admin_activity_subscriptions_table`. On top of Task 045's and 047's three.
- **Nobody gets the bell until it is ticked for them** on their admin form (**Admin notifications →
  Invitations**), Super Admins included, and their role needs **Invitations → View**.
- Refresh cached routes and config.

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
- **Merge order:** settled. `dev` no longer carries امتنان's bell (merged 2026-09-29).
- **`send-bulk` is not scoped** (found, not fixed): it sends whatever invitation ids it is given, from
  any collection and whatever the admin's categories. Its audit row names the collection the sent
  invitations belong to, and none when they span more than one. For Task 041.
- **Guests are not in `audit_logs`** (Task 045 kept them on `history_logs`), so a Guests box later is
  not "a box and nothing else": the feed would need guests audited, or to read `history_logs`.
- **The unread count runs every minute per open tab.** It is one indexed count on `audit_logs` (plus two
  subqueries for a restricted admin); worth an `EXPLAIN` on production data after deploy.

## Log

- 2026-09-29: scoped with the owner in eleven questions (table above). Findings: امتنان's bell
  (`2ef2856` / `9af581d`, 2026-09-28) covered 3 of 4 events ("invitations sent" was never fired), used
  a per-admin setting on `admins` rather than role access, and sat one letter away from the push
  module's `AdminNotificationController`. Its 18 tests passed. Replaced by this design; the two
  invitation actions in the same commit are parked (see the parked file).
- 2026-09-29: **built** on `feat/admin-activity`, off `dev`. Two more decisions asked one at a time
  (12 and 13 above). Backend: the first bell out (`191593c`), bulk rows name their collection
  (`c80a5d2`), the role box and read-state tables (`e687507`), the feed and its four routes
  (`855c78d`). Admin: the first bell out (`13979fa`), the role section (`86961aa`), the bell
  (`8e357bb`), then its look after the owner's review (`648b23c`: grouped by day, an icon per action in
  the trail's colours, the record in bold, sized down one step at the owner's choice). 21 `AdminActivityTest` tests, `InvitationAddAndMoveTest` (the parked actions' 6 tests,
  moved out of the first bell's file). Backend 962 tests, `pint --test` clean, PHPStan at its 6 older
  errors; admin type-check, eslint, prettier, `check:rbac` green. `yarn build` not run: the owner's dev
  server held `.next` (run later in a separate worktree: green). Owner's local DB: امتنان's two migrations rolled back; the three new ones run
  since, and the owner has reviewed the bell in the browser.
- 2026-09-30: the per-admin follow-up (decision 14, migration `2026_09_29_000006`) and the list preload
  fix merged to `dev` and `main` (backend PRs #24 / #25, admin PRs #27 / #29). The parked actions
  picked up and finished as [Task 050](../050-add-people-and-move/TASK.md). Still not deployed.

## Definition of Done

- [x] Code merged to `dev` in the relevant sub-app(s) (backend PR #22, admin PR #25)
- [x] EN + AR translations in the same commit
- [x] Quality gate green (backend `pint --test` + `phpstan` + `php artisan test`; admin `yarn type-check` + `yarn build` + `yarn check:rbac`): `yarn build` run on 2026-09-29 in a separate worktree, since the dev server held `.next`
- [x] امتنان's bell removed, including a migration dropping its two tables/columns
- [x] Docs updated (this TASK.md set to `done (code)`; index row updated)
- [x] Mobile contract checked: only `/api/admin` routes touched (the push module's `/mobile/notifications` and `/admin/notifications` untouched)
