# Task 059: CRM Speakers tab, an import and a dashboard per tab (plan)

- **Status:** approved 2026-10-25 (owner: "use whatever seems fit", my defaults a to g and the working names
  kept; the team's feedback comes once it is on `testing`). **Built 2026-10-25** on `feat/crm-foundations`
  (backend, admin), **uncommitted**. Backend `composer qa` green (Pint, PHPStan, 1,392 tests; `CrmSpeakersTest`
  11); admin type-check, ESLint, `check:rbac` and `yarn build` (from a copy) green. Migration
  `2026_10_25_000002` run on the local `tourise_clean` (it only adds columns). **Not seen in a browser yet.**
- **Branch:** `feat/crm-foundations` in `tourise-backend` and `tourise-admin`, on top of Tracking (backend `8b029c9`,
  admin `e327a7b`, committed, not pushed); then merged into `testing`.
- **Source:** the team's sheet `docs/client/CRM_PLAN_V2/Speaker_Required_Fields (2).xlsx` (30 columns, 9 dropdowns,
  no rows).
- **Names:** "Contacts" and "Speakers" are working names. The owner gives the final ones (normal CRM vs speakers, or
  vs non-speakers).

## Decisions (owner and team, 2026-10-25)

| # | Decision |
|---|---|
| 1 | **Speakers are separate from contacts:** their own tab, fields, table columns and filters, so neither tab shows the other's empty cells or filters. The website's Speakers module (agenda, sessions, the Speakers Dashboard) is **not used**: it is for the website and the app, later. |
| 2 | **One record per person** (team: A). Each column of the sheet is a field on it. **Session is one dropdown**, like the other lists, not a list of sessions inside the record. |
| 3 | **The sheet's lists become fixed lists** in code (EN + AR), and a file must use their exact values: Day, Pillar, Session, Type, Continent. Gender and Country are the system's. |
| 4 | **Official invite to be sent by** takes the system's **Titles** (the Prefix list). A value it lacks (CEO, MOFA...) is added in Titles by the team. |
| 5 | **Status is the Tracking flow** (Task 054 decisions 48 to 50), as for contacts. The sheet's Status and Invitation Status are not fields. Speakers are invited with the same Invite. |
| 6 | **Parked** for the client and the team: Save the Date Invitations, Save the Date Status, Follow Up Status. Not built. |
| 7 | **No passport in the CRM.** The registration already collects it; the import keeps refusing a Passport column (PDPL). |
| 8 | **First Name and Last Name**, not one Speaker cell: the invitation and the registration use both. |
| 9 | **Every speaker field is required** (owner: "for now"), the headshot aside. |
| 10 | **One person, one place.** An email on a contact cannot be on a speaker, and the other way round. The same name with another email is flagged as a possible duplicate across both tabs. |
| 11 | **Roles:** extra boxes for the Speakers tab and for each tab's dashboard. |
| 12 | **No Imports tab:** one import inside each tab, with that tab's past imports. Still testing, so CRM data may be cleaned if needed. |
| 13 | **Dashboards:** no special requests from the team; built like the system's main dashboards. |
| 14 | **Picture:** the CRM photo goes into the edit form of contacts and speakers, with drag and drop. The Guest Picture (`personal_image`) is not changed. |
| 15 | Request 4 (dropdowns) is done (Task 054 revision 3). Request 6 (Imtinan's edit changes) is on hold. |

## 1. The tabs

**Contacts | Speakers | Settings.** Contacts and Speakers each open on their **Dashboard**, with a switch to their
**Data** (the table): the owner's "Dashboard → Data". An admin without the dashboard box lands on Data.

| Page | Contacts | Speakers |
|---|---|---|
| Dashboard | `/crm` | `/crm/speakers` |
| Data | `/crm/data` (was `/crm`) | `/crm/speakers/data` |
| Import | `/crm/import` (was `/crm/imports/new`) | `/crm/speakers/import` |
| Add, edit | `/crm/contacts/create`, `/crm/contacts/[id]/edit` (as today) | `/crm/speakers/create`, `/crm/speakers/[id]/edit` |

`/crm/imports` and `/crm/imports/new` go. **Changed while building:** each tab's dashboard is its root, so the
sidebar's CRM link (`/crm`) opens the contacts' dashboard and stays lit on every CRM page; the tables moved to
`.../data`. The CRM chip in Guests and Invitations (decision 46) opens `/crm/data?contact=` or
`/crm/speakers/data?contact=`. A page the admin has no box for sends them on to the first CRM page they may open.

## 2. A speaker's fields

In the sheet's order. **Shared** means the column contacts already use.

| Sheet heading | Field | Kind |
|---|---|---|
| Day | `event_day` (new) | list: 1, 2, 3 |
| Pillar | `pillar` (new) | list (7) |
| Session | `session` (new) | list (57) |
| Keyword | `keyword` (new) | text |
| Type | `speaker_type` (new) | list (5): Panelist, Moderator, Presentation, Presenter, FE |
| Option # | `option_number` (new) | whole number |
| First Name, Last Name (for "Speaker") | `first_name`, `last_name` (shared) | text |
| Gender | `gender` (shared) | the system's list |
| Title | `job_title` (shared) | text: the sheet's Title is the job title |
| Organization | `company` (shared) | text |
| Country | `country_id` (shared) | the system's countries |
| Continent | `continent` (new) | list (8), the sheet's own |
| Notes | `notes` (shared) | text |
| Program Team Relationship Owner | `relationship_owner` (shared) | text |
| Network to leverage | `network_to_leverage` (new) | text |
| Speaker Email | `email` (shared) | email, unique across contacts and speakers |
| Contact Person | `contact_person` (new) | text |
| Official invite to be sent by | `official_invite_title_id` (new) | the system's Titles |
| Contact Email | `contact_email` (new) | email, not unique (offices share them) |
| Invitation Sent by | `invitation_sent_by` (shared) | text |
| Follow Up Call/Text by | `follow_up_owner` (shared) | text |
| Bio | `bio` (new) | long text |
| Social Handles | `social_handles` (new) | text |
| headshot | `photo` (shared) | the picture field: not in the import, not required |

Not fields (decisions 5 to 7): Status, Invitation Status, Save the Date Invitations, Save the Date Status, Follow Up
Status, Passport. A speaker has none of the contacts' other fields (Prefix, Arabic name, Mobile, Nationality, Company
Location, Sector, Industry, Seniority, Category, Tier, Source List, Channel, Clearance...), and Speakers never shows
them.

**Country:** 189 of the sheet's 196 names are the system's. The other 7 are spelled differently or missing (Cabo
Verde, Congo, Israel, Ivory Coast, Myanmar, North Macedonia, Türkiye); a file uses the system's names, as for contacts.

## 3. How it is stored

**One table, `crm_contacts`, with a new `kind`** (`contact` or `speaker`) and the 12 new columns above (empty on
contacts). One table because:

- the email rule across both tabs (decision 10) is the unique index the table already has;
- one CRM ID counter (C-000123) for both;
- Tracking, Invite, the photo, the record history and the audit trail work for speakers as built.

Each tab reads and writes only its own kind. A contact's CRM ID in the speakers' import, or a speaker's in the
contacts', is refused.

**Migration, additive:** `kind` (default `contact`, so today's contacts stay contacts), the new columns, and
`crm_imports.kind` (today's imports stay the contacts'). Nothing is emptied: cleaning is allowed (decision 12) but not
needed.

## 4. The rules

- One place in code says each kind's columns and what they require (`CrmImportColumns`: today's list for contacts, a
  new one for speakers). The save rules, the import, the template, the form's markers and Settings' stars read it, as
  today. The contacts' rules do not change.
- Speakers: the 24 fields required (decision 9). Contact Email must be an email. Option # is a whole number from 1.
- Email: one per person across both tabs; the message names the tab ("already on CRM speaker C-000045").
- Possible duplicate: the same first and last name with another email, across both kinds (as `looksDuplicate` does
  for contacts today).

## 5. The import in each tab

- **Contacts:** the same template and rules; the page moves from Imports into Contacts.
- **Speakers:** a template of its own (Download sample): CRM ID first, then the sheet's columns in its order, First
  Name and Last Name for Speaker, without the columns decisions 5 to 7 take out; each list a dropdown.
- **The same flow in both:** Check the file, then Import; all or nothing; a value not on its list refuses the file and
  names the cell (Task 054 decision 41); a row with a CRM ID updates that record; a Passport or photo heading refuses
  the file (PDPL).
- Each import page lists that tab's past imports below the form.
- **Test sets:** a speakers set in `~/Projects/ALT/127-tourise/crm_import_tests`, made by a script in its `tools/`,
  like the others.

## 6. The dashboards

Built like the main dashboards (`components/admin-modules/dashbaord`): the same chart kit and cards, a chart or table
view per card, and a click on a bar filters the page.

- **Top:** the title, "Data as of", **Print report**.
- **Filters:** the tab's own, the same as its Data view, kept in the address, so moving between Dashboard and Data
  keeps them.
- **Figures:** the Tracking tiles (All, Not invited, Invited, Sent, Not delivered, Accepted, Registered, Confirmed,
  Declined, Checked in), each one filtering.
- **One card per list,** with the count on each bar:
  - **Contacts (17):** Category, Sub-category, Tier (only with View tier), Seniority Level, Sector, Industry,
    Sub-industry, Company Location, Country of Residence, Region, Nationality, Gender, Source List, List Provided By,
    History / Source, Invitation Channel, Security Clearance.
  - **Speakers (8):** Day, Pillar, Session, Type, Gender, Country, Continent, Official invite to be sent by.
- **Backend:** one read per tab (`GET /admin/crm/dashboard`, `GET /admin/crm/speakers/dashboard`): the counts per
  list over the same filters and access as the table, beside an empty `data` as the table's tiles sit beside its
  rows, so the page reads its filters as the table does.
- **As built:** a chart shows a list's 15 biggest values (its table view lists them all); lists with an order of
  their own (Day, Pillar, Type, Continent, Tier, Seniority, Gender…) keep it, the rest read biggest first, "No
  value" last.

## 7. The picture in the edit form

- The edit form of a contact and of a speaker gets a **Photo** box: drop an image on it, or click to choose; a
  preview; Remove.
- The same rules as the window's avatar today: jpg, png or webp, up to 5 MB, private disk, signed link. The same
  endpoint (`/admin/crm/contacts/{id}/photo`, and its speakers twin).
- **Adding:** the photo is chosen in the form and uploaded right after the record is saved.
- The avatar upload in the window stays. The Guest Picture is not changed (decision 14).
- Drag and drop with the browser's own events, as the invitations import's dropzone; no new dependency.

## 8. Roles

The `crm` feature gets boxes by tab, as Newsletter did (Task 052):

- **Contacts keeps today's boxes:** view, create, update, delete, invite. Roles on `testing` keep their ticks; nothing
  to migrate.
- **New:** `dashboard_view` (Contacts' dashboard), `speakers_view`, `speakers_create` (add and import),
  `speakers_update`, `speakers_delete`, `speakers_invite`, `speakers_dashboard_view`.
- **Shared by both tabs:** settings, record_history, audit_trail.
- The contacts' routes move from "any CRM box" to `crm,view`, so a speakers-only role cannot read contacts, and the
  other way round.
- New boxes start unticked: the team ticks them in Roles before production.

## 9. Not touched

The website's Speakers module, sessions and Speakers Dashboard; the Guest Picture; Imtinan's edit changes; the magic
link (Task 058); CRM steps 4 and 5; the parked fields (decision 6). **Mobile:** nothing; every route here is under
`/admin/crm`.

## 10. Build order and checks

1. **Backend:** the migration and model; the new fixed lists (`CrmFixedLists`: Day, Pillar, Session, Type,
   Continent, EN + AR); the speakers' columns; the rules, filters, import and template made per kind; the speakers'
   routes (the same controllers, the kind set by the route); the two dashboard reads; the boxes.
2. **Backend tests:** a speaker's save and required fields, the email across both kinds, the speakers' import and
   template, the dashboard counts, the boxes. Today's CRM tests stay green.
3. **Admin:** the tabs and the Dashboard / Data switch; the speakers' table (its own columns and filters), form and
   window; an import page per tab; the two dashboards; the Photo box; the box labels in Roles; EN + AR in the same
   commit.
4. **Quality gate:** backend `composer qa`; admin type-check, ESLint, `check:rbac`, `yarn build` from a copy (the
   owner's dev server is running).
5. **Docs:** this plan, TASK.md, the index row; the test sets rebuilt.

## 11. My defaults, to correct (all kept, owner 2026-10-25)

| # | Default |
|---|---|
| a | **Arabic names** for the new lists, the 57 sessions included: I draft them and the team checks. (Or the session titles stay in English on the Arabic screens too.) |
| b | **Dashes in session names:** five use a long dash ("Actor: Screen to Suitcase", the four "Appendix" ones) and three a short one (the "After Hours" ones). I'd write each as a plain hyphen, to match the system's text. Files made from our template carry our values; the team's own sheet is changed once. |
| c | **Two sessions look like one:** "Frenemy Exchange: Rail vs Wings" and "Rail vs Wings: Competition, Coexistence or Convergence?". Kept both, as given, with the four "Appendix" ones not yet scheduled. |
| d | **All required** (decision 9) means a speaker not yet invited still needs Invitation Sent by and Follow Up Call/Text by filled in. |
| e | **Category limits** (Task 054 decision 22): speakers have no Category, so the Speakers boxes alone decide who sees them. |
| f | **Excel export** of the dashboards (the main ones have it): left for later, with CRM step 5 (export) on hold. Print is in. |
| g | **Continent** is the sheet's own list, chosen by the team, not worked out from the Country as the contacts' Region is. |

## 12. Added while building

- **"headshot" is refused like "photo"** in any CRM import (`CrmImportColumns::FORBIDDEN`): the team's sheet has a
  headshot column, and a photo never comes through a file (PDPL). The photo is the edit form's.
- **The speakers' import test set:** `~/Projects/ALT/127-tourise/crm_import_tests/eissa-test-cases-speakers` (8
  files, README and PDF), built by `tools/make-crm-speakers-cases.php`, checked through the real API by
  `tools/CrmSpeakerCasesServerCheck.php`: all 8 as the README says (2026-10-25).

