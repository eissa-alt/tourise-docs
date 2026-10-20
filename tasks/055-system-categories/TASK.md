# Task 055: System Categories (a list under each category)

- **Status:** `in-progress`: built on `feat/crm-foundations` (backend + admin), committed locally, not
  pushed, not seen in a browser yet (2026-10-20). See *Log* and *Deploy*.
- **Opened:** 2026-10-20
- **Owner:** unassigned
- **Sub-app(s):** backend + admin (the public site needs no change)
- **Branch(es):** `feat/crm-foundations` in `tourise-backend` + `tourise-admin`, off `dev` (`--no-track`)

## Goal

The client's registration master (*Badge Categories* sheet in
[`client/CRM_PLAN_V2/`](../../client/CRM_PLAN_V2/)) splits each badge category into **System Categories**
(41, e.g. Dignitary: Head of State International, Ministers & Excellencies Local, Ambassadors). Our
categories stay as they are and **are** the client's Badge Category. This task adds the System Category under
them: picked next to the category wherever a guest or an invitation gets one, and shown, filtered, counted and
exported. It is the first gap closed between the system and the CRM plan (Task 054, its build step 0).

## Scope

- **In:**
  - The list per category, kept in **Category settings** (a new tab).
  - A System Category on guests, invitations and collections (the collection's is the default), plus the
    targets of the two automatic moves and the request category's default.
  - One rule on every place that sets a category (the nine below), and the Change category fixes.
  - The admin screens and exports listed under *Build order*, and the dashboard.
- **Out (explicitly not this task):**
  - A System Category choosing templates (decision 6: tag only).
  - Public categories reading the invitation link (see *Deferred*).
  - A column in the **guest** Excel import (waits for the guest import rework).
  - The Workforce and Exhibitor categories; Delegate's place (see *Deferred*).
  - Loading the client's 41 by code: admins enter them (decision 4).
  - The mobile app: nothing is exposed to it.
  - Per-admin System Category limits (decision 14).
  - The drift that already exists between an invitation's category and its collection's.
  - The CRM itself (Task 054).

## Decisions

All 2026-10-20, with the owner.

| # | Decision |
|---|---|
| 1 | **Categories stay as they are** and are the client's Badge Category. No parent level, no regrouping. |
| 2 | **Label:** "System Category" (EN), "النوع الفرعي" (AR). In the code: `sub_category` (`sub_categories`, `sub_category_id`), since "category" there already means the Badge Category. |
| 3 | **Managed in Category settings**, a new seventh tab *System Categories*: EN name, AR name, order, active. One in use is **switched off, never deleted**: records keep it, it is no longer offered. Whoever may edit a category may edit its list. Changes show in the category's audit trail. Cloning a category copies its list. |
| 4 | **Created and assigned by admins** (mainly Super Admins), not loaded by code. Names are unique **within** a category, so "Sponsors Guests" and "Knowledge Partners" may sit under two. |
| 5 | **Dependent dropdowns:** Category first, then a **filtered** System Category list (only that category's active ones). A category with none shows no second dropdown. Copies the admin's Industry → Sub-industry pattern (`hooks/use-industry-options.ts`, `useSubIndustryOptions`). |
| 6 | **Tag only.** The category still chooses the registration form, the emails and the badge. Templates per System Category can be added later with nothing to undo. |
| 7 | **Required on admin forms** when the category has an active list; **never asked on public forms**. A guest without one (self-registration, public categories) is found with a **"No System Category"** filter. |
| 8 | **One rule on every write path:** a System Category must belong to the record's category. A wrong pair sent by a person is refused with a message; a move made by the system without a target clears it. It never stays from the old category. |
| 9 | **The two automatic moves** (a category's *accept to category*, an automation's *move to category*) get a **target System Category**, **mandatory when the target category has a list**. Production has neither move set up, so no setting becomes invalid. A target switched off later keeps applying until the setting is edited. |
| 10 | **Change category is fixed in the same work:** the target category exists and is active; the admin may move only a guest they can see, into a category they may use; the System Category comes in the same step; the history reads "Category changed from Speaker / Speaker Tier 2 to VIP / Investors". |
| 11 | **Invitations work as the category does today.** The System Category is picked once on the collection, next to the category, and every invitation it creates takes it. There is no field on the guest card and no column in the invitation Excel. After creation it can be changed per invitation (single-invitation edit) or for many (Update invitations, bulk). Each invitation stores its own, so per-person entry can be added later with no database change. Changing the collection's later fills new invitations only and is not "out of sync". (Owner chose this over per-person entry, 2026-10-20.) |
| 12 | **Bulk Update, Move and Extract** (query-builder writes): the pair is checked once before the write, written in the same statement, and named in the audit entry those actions already record. On Move, an invitation keeps its own if it belongs to the target collection's category, else takes the target's default. Extract keeps each invitation's own. |
| 13 | **Inherited:** a registration or a decline through an invitation (private categories) takes the invitation's System Category; guests a registrant adds take the main guest's. |
| 14 | **No separate admin limits:** a System Category follows its category's access. |
| 15 | **Invitation requests:** the request category holds a default System Category next to its target category; the reviewer can change it on Accept. |

## Where a guest's category is set (decision 8 applies to each)

| # | Place | Code | System Category comes from |
|---|---|---|---|
| 1 | Public registration | `GuestsController.php:796` | The invitation (private categories only) |
| 2 | Guests a registrant adds | `GuestsController.php:849` | The main guest |
| 3 | Decline through the link | `GuestsController.php:1113` | The invitation |
| 4 | Admin create | `GuestsController.php:1359` | The form |
| 5 | Admin update | `GuestsController.php:1580` (category not editable here) | The form, within the same category |
| 6 | Change category | `GuestsController.php:1682` | The dialog (decision 10) |
| 7 | Accept to category | `GuestsController.php:2248` | The category's target (decision 9) |
| 8 | Automation move | `AutomationDispatchService.php:69` | The automation's target (decision 9) |
| 9 | Invitation request accept | `AdminInvitationRequestsController.php:289` | The request category's default, or the reviewer's (decision 15) |

The guest Excel import (`GuestsController.php:3886`) also sets a category; imported guests get no System
Category until the import rework adds the column.

## Deferred (reopen when asked)

- **Public categories and the invitation link.** The server reads the invitation only for private
  categories (`GuestsController.php:478`), so a guest registering through a Media invitation keeps no link to
  it and inherits nothing. Skipped unless the client insists or asks. Also limits Task 054's tracking by link.
- **Delegate** (General Delegates, Sponsors Guest, Knowledge Partners): under General Registration? The
  owner checks with the team. Once decided, admins add them in Category settings; no code change.
- **Workforce** and **Exhibitor**: left until requested; they need their own categories first.
- **Templates per System Category** (the client's "sets the exact template").
- **The guest Excel import column.**
- **A System Category filter on the invitation listings.** They have no category filter to sit beside.
- **The visa export** keeps its fixed 21 columns (the e-visa format), and **the scans export** keeps the
  category name it stores.
- **The dashboard's export workbook** and **the invitation charts** are not split by System Category.

## Database (all additive, nullable, no backfill)

- New table `sub_categories`: `id`, `category_id`, `name_en`, `name_ar`, `sort_order`, `is_active`,
  timestamps; unique (`category_id`, `name_en`).
- `sub_category_id` on `guests`, `invitations`, `invitation_collections`.
- Targets: on `categories` (beside `to_category_id`), on `automation_setups` (beside `to_category_id`), and a
  default on `invitation_request_categories` (beside `target_category_id`).
- Production needs the migrations; there are no guests with old values to convert (41 Media guests get one
  from an admin).

## Build order

Each step merges on its own.

0. **PHPStan green on `dev` first**, its own commit: the three relations it cannot find in
   `DashboardStatsController` and the two stale ignores. This task touches that file.
1. **Base (backend):** the table and columns, the shared rule (decision 8), the list's API (create, rename,
   reorder, switch off; clone copies; audited), the nine write paths, the Change category fixes. Tests through
   HTTP for each path.
2. **Guests (admin + backend):** the Category settings tab; the select in the guest create / edit wrappers
   (`guests-form-create.tsx`, `guests-form-edit.tsx`, so every form shape gets it without touching 18 files);
   the Change category dialog; See more; a column and filters on the guest list, including "No System
   Category"; the guest exports; the two move targets (category form, automation setup).
3. **Invitations (admin + backend):** the collection's System Category (create, edit, Add people takes it);
   single-invitation edit; Update (bulk), Move, Extract (decision 12); listings column and filter; the three
   invitation exports; registration and decline inheriting (decision 13); Invite someone. No guest-card field
   and no Excel column (decision 11), so the invitation import sample is unchanged.
4. **Requests and dashboard:** the request category's default and the Accept override; the dashboard's
   category charts split by System Category, with a filter.

## Cases (backend tests, through HTTP)

1. A pair that does not match (VIP with "Speaker Tier 1") is refused on create, update, Change category and
   bulk Update.
2. Change category without a System Category, into a category that has a list, is refused; into one without
   a list, it is accepted and the old one is cleared.
3. An admin limited to Speaker cannot move a guest into VIP, nor move a guest they cannot see.
4. Accept to category with a target lands the guest on the target pair; a moved guest never keeps the old
   category's System Category.
5. An automation move does the same.
6. Registration through a private category's invitation takes the invitation's System Category; the guests
   the registrant adds take the main guest's; a decline through the link takes it too.
7. A self-registered guest has none and appears under "No System Category".
8. A System Category switched off stays on its guests and invitations and is no longer offered; a move target
   that was switched off still applies.
9. A collection's System Category fills every invitation it creates (cards and Excel alike); one invitation
   changed afterwards keeps its own; changing the collection's later leaves existing invitations as they are.
10. Move: an invitation whose System Category belongs to the target category keeps it; one that does not takes
    the target's default. Extract keeps each one's own.
11. A request accepted with the default, and with the reviewer's override, mints invitations carrying it.
12. Cloning a category copies its list.
13. Every guest and invitation export carries the column.

## To check before building

- The three bulk writes (`InvitationsController.php:544`, `:1335`, `:1602`) bypass model events and
  `Auditable`; the rule must be called there explicitly.
- Hardcoded slugs (dignitary party roles, the dashboard's sponsor / speaker views, the mobile speaker flag)
  stay on the category; nothing reads the System Category instead.
- `scans.guest_category` stores the category name as text; leave it.
- The admin builds some category lists itself (guest filter, `guests-choose.tsx`); the new filter must use the
  admin's own categories.

## Log

Newest at the bottom.

- 2026-10-20: opened. Researched against the code (backend, admin, public site, mobile) and the production
  dump of 2026-10-19 (16 categories, 41 guests, 0 invitations, no category moves or automations). Owner's
  decisions 1 to 15 in one session; problem 1 (public categories and the invitation link) deferred.
- 2026-10-20: decision 11 changed: invitations follow the category's flow (set on the collection, changed
  per invitation afterwards), not per-person entry on the guest card. Open for Task 054: whether CRM
  invitations keep each person's own System Category or take the collection's.
- 2026-10-20: built, every step committed locally on `feat/crm-foundations` in each repo (owner's go,
  working alone). Gates green at each step: backend `composer qa` (1306 tests at the end), admin
  `tsc` + `eslint` + `yarn build` + `yarn check:rbac`.
  - **Step 0** (backend `e3adc52`, `0c4b831`): PHPStan green. The dashboard's guests-per-badge endpoint
    failed on every call (a query used as a relation, and a `guests.status` column that does not exist);
    the owner chose to repair it rather than remove it, for the badge printing work. It now counts per
    category, then per badge, behind the category chart's box.
  - **Step 1** (backend `dbb83e9`, `9d09b15`): the table, the fields, `SubCategoryRule`, the list saved
    with the category form (one audit row, clone copies), `admin/categories/{id}/sub-categories/select`,
    the nine places, Change category fixed.
  - **Step 2** (backend `9ef3efb`, admin `1b3a77a`): Category settings tab, guest create / edit,
    Change category, See more, guest list column and filter ("No System Category"), seven guest exports
    (last column), automations.
  - **Step 3** (backend `9a9c6a8`, admin `6a72987`): collection create / edit, single edit, bulk Update,
    Move, Extract, Add people, Invite someone (`admin/dignitary-parties/roles`), listings, three
    invitation exports.
  - **Step 4** (backend `775d0c8`, admin `c446a24`, `0b6fd72`): request category default and the Accept
    override; dashboard filter and the category chart split (`/dashboard/guests/sub-categories`).
  - **Where the build differs from the plan:** a new column goes LAST in each export (the house rule:
    saved import mappings keep their columns, and the letter-based formats stay put), not beside Category;
    the visa and scans exports are left out (see *Deferred*).
- 2026-10-20: branch renamed `feat/system-categories` to `feat/crm-foundations` in all three apps (owner), before
  the first push: the branch stays open for the CRM requirements as they close, merged with `dev` as it goes.

## Deploy

- `php artisan migrate`: `2026_10_20_000001` to `000003`, all additive. Nothing to backfill.
- No new permission box: the list is edited by whoever may edit categories.
- After deploy, a Super Admin enters the lists in Category settings → System Categories (the client's
  sheet is in `client/CRM_PLAN_V2/`). Until a category has a list, nothing changes for it.
- Change category now refuses an inactive category, a guest outside the admin's access, and a category
  the admin may not use (Super Admins unaffected): tell the team.
- The mobile app is not affected (no field exposed to it).

## Definition of Done

- [ ] Code merged to `dev` in backend and admin
- [x] EN + AR translations in the same commit
- [x] Quality gate green (backend `composer qa`; admin `yarn type-check` + `yarn build` + `yarn check:rbac`)
- [x] The cases above covered by backend tests, through HTTP
- [ ] Docs updated (this TASK.md, the index row, Task 054's step 0 pointing here)
- [x] Mobile contract checked (nothing exposed; no notice needed unless that changes)
- [ ] Seen working in a browser, by the owner
