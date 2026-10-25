# Task 059: CRM Speakers tab, an import and a dashboard per tab

- **Status:** `built, uncommitted` (2026-10-25): decisions 1 to 15 and the plan ([PLAN.md](PLAN.md)) approved; built
  on `feat/crm-foundations` in backend and admin, gates green, not committed, not seen in a browser yet.
- **Opened:** 2026-10-25
- **Owner:** unassigned
- **Sub-app(s):** backend + admin
- **Branch(es):** `feat/crm-foundations` in `tourise-backend` and `tourise-admin` (then merged into `testing`)

## The team's requests (2026-10-25)

1. A **Speakers** tab.
2. **Separate the import:** no Imports tab of its own; one import inside **Contacts** and another inside **Speakers**.
3. A **dashboard for each tab** (one for all contacts, one for speakers) showing **statistics of the dropdown lists**.
4. The **fields that need it as dropdowns**, not text.
5. A **picture field in the edit form**, with **drag and drop**.
6. **Bring in Imtinan's changes to the edit screens** ("looks better"): **to be confirmed later**.

## Where the CRM stands (to build on)

- **Tabs today:** Contacts, Imports, Settings. The import page lives under Imports (`/crm/imports/new`), with the list
  of past imports beside it.
- **Lists:** every list field is already a dropdown of the system's own values (revision 3, decisions 41 to 44).
  Still **typed text**: Relationship Owner, Follow-up Owner, Received By, Previous Engagement, Previous Category,
  Invitation Sent By, Notes (owners as admin accounts were planned for step 4, now on hold).
- **Photo:** uploaded and removed on the round avatar of the contact's window (jpg, png or webp, up to 5 MB, private
  disk, signed link); not in the edit form.
- **Tracking** (step 2, decisions 45 to 50) is built: the Status column, tiles, filters, the journey. Its tiles already
  count contacts per step; a dashboard would add the lists.
- **Steps 4 and 5 are on hold** (owner, 2026-10-25).

## Answers (2026-10-25)

All six questions are answered; the decisions (1 to 15) are in [PLAN.md](PLAN.md). In short: speakers are their own
record in their own tab, one per person, with the team's sheet's fields (Session a dropdown, every field required for
now); status is Tracking; the passport stays with the registration; one person in one tab only; boxes by tab and
dashboard; an import per tab; dashboards like the main ones; the CRM photo in the edit form with drag and drop (the
Guest Picture unchanged); Imtinan's edit changes on hold. The final tab names come from the owner.

## Questions for the owner (as opened)

1. **What is a speaker in the CRM?** A contact whose Category is Speaker, shown in its own tab (the same record,
   filtered), or its own kind of record with columns of its own (session, topic, bio…) and its own template?
2. **The import per tab:** the same template and rules in both, the Speakers one filing every row as a speaker; or a
   speakers template of its own? And where the list of past imports goes (inside each tab?).
3. **The dashboards:** which lists (Category, Sub-category, Country, Nationality, Region, Industry, Sector, Seniority,
   Tier, Status, Channel, Clearance, Source List, List Provided By, Company Location, Gender), as counts or charts, and
   do they follow the tab's filters?
4. **Which fields become dropdowns,** and from which list: the owners (admin accounts, or a list kept in CRM
   Settings?), Received By, Previous Category (the system's categories?), others?
5. **The picture in the edit form:** the same rules as the window's (types, 5 MB, private, PDPL), and also when adding a
   contact?
6. **Imtinan's edit changes:** which branch. Her admin branches not in `testing` (2026-10-25):
   `feat/admin-forms-ui` (13 commits, "Guest edit asks what registration asks", 10-19), `feat/guest-profile`
   (35, 10-20), `feat/guest-live-status` (41, "Guest Add walks the public form's steps", 10-20). None touches the
   CRM; to confirm with her and the owner.

## State at opening

- Tracking committed locally, **not pushed**: backend `8b029c9`, admin `e327a7b`, docs `44d2e1c`. It needs the
  owner's browser check, then push and the merge into `testing` (one additive migration, `2026_10_25_000001`).
- The magic link (Task 058) is with Imtinan, on `merge/email-magic-link`.

## Log

- 2026-10-25: opened from the team's requests, for a new session. Nothing decided or built.
- 2026-10-25: the owner explained the requests and gave the team's sheet (`docs/client/CRM_PLAN_V2/Speaker_Required_Fields (2).xlsx`);
  questions answered one at a time (decisions 1 to 15); [PLAN.md](PLAN.md) written for review, with my defaults
  (a to g) to correct.
- 2026-10-25: plan approved (owner: "use whatever seems fit"; the team's feedback after `testing`). Built: backend
  (migration `2026_10_25_000002`, the speakers' columns, lists, rules, import, template, routes, two dashboard
  reads, the boxes; "headshot" refused in imports) and admin (Contacts | Speakers | Settings, each tab Dashboard ->
  Data, the speakers' table, window and form, the photo box with drag and drop in both forms, an import per tab
  with its past imports, the speakers' lists in Settings, EN + AR). Gates green; the speakers' import test set
  built and checked. Uncommitted.

## Definition of Done

- [x] Questions answered; plan written and approved
- [ ] Code on `feat/crm-foundations` in backend and admin (built, uncommitted), then merged into `testing`
- [x] EN + AR translations (to go in the same commit)
- [x] Quality gate green (backend `composer qa`; admin type-check, ESLint, `check:rbac`, `yarn build` from a copy)
- [x] The import test sets: the contacts' unchanged; a speakers' set added and checked
- [x] Docs updated (this TASK.md, PLAN.md, the index row)
- [ ] Browser check by the owner
