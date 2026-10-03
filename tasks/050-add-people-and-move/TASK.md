# Task 050: Add people to a collection, move invitations into one

- **Status:** `done (code)`: **merged to `dev` and `main` on 2026-09-30** (backend PR #28 `2f99038`
  then #29; admin PR #30 `743e967` then #31), **not deployed**. Production needs migration
  `2026_09_30_000002` and the two new boxes ticked on roles (see *Deploy*). This file was written
  late, on 2026-10-01.
- **Opened:** 2026-09-30, picked up from Task 048's
  [PARKED-ADD-AND-MOVE.md](../048-admin-activity-notifications/PARKED-ADD-AND-MOVE.md)
- **Owner:** unassigned
- **Sub-app(s):** backend + admin
- **Branch(es):** `feat/add-people-and-move` in `tourise-backend` + `tourise-admin`, off `dev`,
  created `--no-track`. Deleted (local + GitHub) on 2026-10-01 after the merge; tips backend
  `7fdf9d5`, admin `812cf63`.

## Goal

A collection was fixed the moment it was made. Inviting three more people meant a second collection
with its own counts, and Extract only moves people into a **new** collection. امتنان added two API
actions for this on 2026-09-28 (backend `2ef2856`, the same commit as her bell), with no admin screen.
Task 048 found ten gaps in them and parked them. This task closes the gaps, gives both actions a
screen and their own permission boxes, and makes every invitation say who added it.

## Decisions (owner, 2026-09-30, asked one at a time)

| # | Decision |
|---|---|
| 1 | **Add people uses the same input as Create**: Manual cards and the Excel upload, with every import check, the problems dialog, points of contact and the sample download. The form gains a third mode, `add`, at `/invitations/details/{id}/add-people`. This was the parked file's open question. |
| 2 | **Separate boxes, `add_people` and `move`**, not riding on Create and Extract. Roles start unticked, as Task 046's did: no migration grants them, so only Super Admins can add or move until a role is ticked. |
| 3 | **An invitation already sent never changes category in a move** (gap 7, answer A). Its link is `/join/{category}/{token}` and the site refuses it once the category changes. The whole move is refused and those guests are named. Unsent invitations, and sent ones staying in their category, move as before. |
| 4 | **A move or an extract is also recorded on the collection the invitations left**: `moved_out_of_collection` and `extracted_out_of_collection`, with the same payload as the row on the target. Both trails show it, and the bell reaches the admins of either collection. One who sees both gets two lines, one per collection. |
| 5 | **"Who added it" is two columns on `invitations`** (option 1 of those offered): `created_by` (the admin) and `created_via` (`create`, `add_people`, `invitation_request` or `dignitary_party`). Shown as an **Added** line in History and **Added by** in See more. |
| 6 | **A moved or extracted invitation shows the move in its own History.** The row on the target lists the invitations it carried in `invitation_ids`; `AuditLog::shownPayload()` hides that list from the trail, the History panel and the trail's export. Still one row per click: no rows per invitation and no extra bell lines. |

## What was built

### Add people

`POST /admin/invitations/{id}/add-guests`, behind `invitations,add_people` (was `invitations,create`).

- New invitations **open the registration form** as the collection's others do (`with_from` from its
  first invitation, on when it has none) and always prefill, never lock (Task 044). Before, they
  opened no form (gap 1).
- **Create's gates**: 1000 rows, the guest's columns at varchar(255), points of contact checked with
  `Invitation::pocRules()` (an over-long one was a raw 500), and an address that already belongs to a
  guest refused with Create's own message (`refuseRegisteredEmails`, now shared). Gaps 2, 3, 4.
- An address **already invited in the collection** is refused, whatever its case or its invitation's
  state (gap 5).
- A **shared-link (multiple) collection** has no one to add to: the API refuses, and the admin page
  says so with no submit.
- Admin: the collection's name, category, channel and email template are shown, not asked; the API
  gives the new invitations the collection's own. The page posts only `guests_list` and returns to the
  collection.

### Move to collection

`POST /admin/invitations/{id}/move-to-collection`, behind `invitations,move` (was `invitations,extract`).

- A dialog under the collection page's **More** menu, for a single-use collection and an admin with
  the Move box: the bulk dialogs' invitation list, then **Move them to**, a picker of the single-use
  collections the admin can see, each with its category.
- A shared-link collection is refused **as the target** (gap 6) **and as the source**: its one
  invitation is the shared link itself.
- Someone already invited in the target is refused.
- Decision 3 in the dialog: when a picked collection would change a sent invitation's category, the
  dialog says how many and keeps Move off. The API refuses the same move and names the guests.
- The collections listing takes `usage_type`, for the picker.
- Kept from امتنان's version: moved rows take the target's channel, templates and category; only open
  invitations move (active, not used); the admin's category scope applies; both collections'
  `total_invites` are recounted.

### Who added an invitation

- `Invitation::origin()` answers who, how and when. The History endpoint sends it beside the rows as
  `origin`, the details endpoint (See more) as `data.origin`. Listings do not, so they ask nothing
  extra per row.
- **Forward-only, nothing backfilled.** An invitation older than the columns is credited to its
  collection's creator only when it was made **within 60 seconds** of the collection; otherwise it
  reads "not recorded". No admin signed in (the dignitary's own form) leaves `created_by` null.
- History: a green **Added** line, last, as the oldest thing that happened. With nothing else to show,
  it replaces "No history yet", which every invitation showed until someone edited it.

### Audit trail and bell

- Gap 8 closed: **People added** and **Moved to collection** no longer fall back to grey (Created's
  green and Extract's indigo). The two new rows on the source collection get EN + AR labels, the
  indigo, and the bell's move icon.
- Moves made before backend `7fdf9d5` list no `invitation_ids`, so they stay out of an invitation's
  History.

## The parked file's gaps

| Gap | What | Closed by |
|---|---|---|
| 1 | Added invitations opened no form, no prefill | backend `97dd608` |
| 2 | No "already registered" check | backend `97dd608` |
| 3 | No 1000-row limit | backend `97dd608` |
| 4 | Points of contact not validated (raw 500) | backend `97dd608` |
| 5 | No check against people already in the collection | backend `97dd608` |
| 6 | Move allowed into a shared-link collection | backend `97dd608` |
| 7 | A move could break a sent invitation's link | backend `97dd608`, decision 3 |
| 8 | Audit labels and colours | Task 048, then admin `35cb5d4` |
| 9 | Tests | Task 048 (6), then 24 in `InvitationAddAndMoveTest` |
| 10 | No admin screens | admin `c444424`, `915fb00` |

## Deploy

- **Migration** `2026_09_30_000002_add_created_by_to_invitations_table` (two nullable columns). It
  lands with Task 045's, 047's and 048's migrations and امتنان's `2026_09_30_000001` (API key
  allowed IPs). See [HANDOFF.md](../../HANDOFF.md) for the full list.
- **Tell the team first**, then tick **Invitations → Add people** and **Invitations → Move** on the
  roles that should have them. Until then only Super Admins see either action.
- Refresh cached routes.
- Owner's local DB: `2026_09_30_000001` and `000002` ran together as batch 5, so
  `migrate:rollback --step=1` undoes only `000002`.

## Log

- 2026-09-28: امتنان's backend `2ef2856` adds both actions, API only, with her bell.
- 2026-09-29: parked in Task 048 with ten gaps; 8 and 9 mostly done there.
- 2026-09-30: picked up as Task 050 on `feat/add-people-and-move`, six decisions asked one at a time
  (table above). Backend `97dd608` (the gaps), `d852cc6` (the boxes), `e65174e` (the row on the source
  collection), `d637f79` (who added it, the migration), `7fdf9d5` (moves in an invitation's History).
  Admin `c444424` (Add people), `915fb00` (the Move dialog), `35cb5d4` (trail and bell styles),
  `812cf63` (Added / Added by). Tests in `InvitationAddAndMoveTest`, `InvitationExtractTest` and
  `InvitationPermissionsTest`. Merged to `dev` (backend PR #28, admin PR #30) and `main` (#29 / #31)
  the same evening. Not deployed.
- 2026-10-01: the branch deleted, local and GitHub. This file written; the parked file marked done.
  Gate on `dev` (`833b493`, with امتنان's partner-API work of the day on top): backend `pint --test`
  clean, PHPStan at its 6 older errors, **1014 tests pass**; admin `type-check` and `check:rbac` green
  (`check:rbac` covers the sidebar half only in this checkout). Admin `yarn build` not run here.

## Definition of Done

- [x] Code merged to `dev` in the relevant sub-app(s) (backend PR #28, admin PR #30), and to `main`
- [x] EN + AR translations in the same commit (admin `translations/{en,ar}/web.json`)
- [x] Quality gate green (backend `pint --test` + `phpstan` + `php artisan test`; admin `yarn type-check`
      + `yarn check:rbac`), run on `dev` on 2026-10-01. Admin `yarn build` not run.
- [x] The parked file marked done
- [x] Docs updated (this TASK.md, index row, HANDOFF)
- [x] Mobile contract checked: only the two `/api/admin/invitations` routes changed, and only their
      permission
- [ ] Deployed: the migration run, the team told, the two boxes ticked
