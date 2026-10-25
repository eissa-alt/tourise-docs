# Task 059: CRM Speakers tab, an import and a dashboard per tab

- **Status:** `todo`: the team's requests received 2026-10-25. Questions first (one at a time), then a plan for
  review, then code.
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

## Questions for the owner (to ask one at a time)

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

## Definition of Done

- [ ] Questions answered; plan written and approved
- [ ] Code on `feat/crm-foundations` in backend and admin, then merged into `testing`
- [ ] EN + AR translations in the same commit
- [ ] Quality gate green (backend `composer qa`; admin type-check, `check:rbac`, `yarn build`)
- [ ] The import test sets rebuilt if the import changes
- [ ] Docs updated (this TASK.md, the index row)
