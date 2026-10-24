# Task 054, step 1: import and records (plan)

- **Status:** **revision 3 built 2026-10-24** (the fixed lists, [FIXED_LISTS_PLAN.md](FIXED_LISTS_PLAN.md)), on top
  of revision 2, which was **built 2026-10-21**, uncommitted on `feat/crm-foundations` (backend, admin); docs
  uncommitted on `main`. Backend `composer qa` green (Pint, PHPStan, 1,352 tests); admin `tsc`, ESLint (CRM files),
  `check:rbac` and `yarn build` (from a copy) green. Migrations run on the local `tourise_clean` 2026-10-22 (so no
  longer edited in place). **Not seen in a browser yet.** The sections after *Revision 2* describe what was built.
- **Branch:** `feat/crm-foundations` in `tourise-backend` and `tourise-admin` (merged once, when the whole CRM is
  final). The public site is not touched in step 1.
- **Rests on:** decisions 1 to 38 in [TASK.md](TASK.md) (38 is this plan's revision 2). Names follow decision 37: the section is **CRM**, each
  person a **contact**, tables `crm_*`.

## Revision 2 (2026-10-21 evening): old data is reference

> **Revision 3 (2026-10-24) replaces the supporting lists and the old CRITICAL note.** The CRM uses the system's
> own lists (Titles, Countries, Categories and Sub-categories, the forms' lists), matched exactly, nothing created
> by an import (decisions 41 to 44); only Source List and List Provided By stay in CRM, Lists, kept by the team.
> Contacts hold a system Category, so **each admin sees and writes only the contacts in their own categories**, as on
> Guests (decision 22). See [FIXED_LISTS_PLAN.md](FIXED_LISTS_PLAN.md). The rest of this file describes revision 2
> as built: where it speaks of supporting lists, values as the files wrote them, or no category scope, read
> revision 3.

**Why:** the team's notes. 20,000+ records will arrive in many batches of 2,000+, mostly bulk old data (last
year's registrations, older lists). Last year's category, tier, industry, prefix or anything else is not this
year's. Most CRM data is reference (guest-related); the team only updates the operational columns. This section
overrides the sections below where they differ; the first build (pieces 1 to 5, uncommitted, its migrations
never run) is reworked to it.

**The 37 fields** (the client's 36, plus Previous Category from the Contacts sheet):

| Kind | Fields |
|---|---|
| **Supporting list** (16) | Prefix, Company Location, Gender, Nationality, Country of Residence, Region, Sector, Industry, Sub-industry, Seniority Level, Category, Sub-category, Tier, Source List, List Provided By, History / Source |
| **Text** (13) | First Name, Last Name, Arabic Name, Job Title, Company, Email, Mobile, Relationship Owner, Follow-up Owner, Received By, Previous Engagement, Previous Category, Notes |
| **Fixed list** (3) | Invitation Channel, Security Clearance (the rules depend on them); Invitation Status (moved by the system) |
| **System** (3) | CRM ID; Invitation Sent Date and Sent By, from the invitation |
| **Date** (2) | Last Contact Date, Next Reminder Date |

**Supporting lists:** one table (`crm_list_values`: list, name, match key) for all sixteen. A value comes from an
import (matched ignoring case and spaces, created when new) and is **read-only** once created, so later imports
reuse it. Each list stands alone (Sub-industry and Sub-category are not under a parent). No links to the system's
values. A contact, one or many, can be pointed at another value of its list. Region is as written; Excel errors
and the template's "Check country" read as empty.

**Invitation Status:** Not Sent on import; In Progress when added to a CRM collection; Sent, Accepted, Declined
from the invitation (step 3). Sent Date and Sent By from the invitation. An old file's status and sent columns
are last year's facts, kept under "From the imports".

**Two "channels", two names:** the client's **Invitation Channel** (who delivers the invitation: H.E.'s Office,
MOFA, Royal Court, Other Ministries, Relationship Owner, CRM) keeps its name. The system's own channel (Email / SMS /
WhatsApp, on collections and invitations) reads **"Sending Channel"** ("قناة الإرسال") wherever it was labelled just
"Channel" (owner, 21 Oct; the one admin label, 10 places, changed).

**Owners as text, for now.** The admin-account version (decision 20: the "Can own contacts" box, owner pickers,
the category check) is taken out; owner notifications (decisions 21, 34, 35) wait for step 4, where how an
owner's name connects to an admin is decided. Kept aside on purpose, not dropped.

**Proposed (owner to confirm):**

1. The team can also set In Progress (while preparing) and Pending; nothing moves a contact backwards on its own.
   **Agreed 21 Oct.**
2. Manual channels: the contact is added to a collection and **"Mark as sent by hand"** (date, who delivered it)
   creates the invitation without sending anything; the registration link is sent from it later. **Agreed 21 Oct.**
3. Supporting lists are managed in CRM Settings: **add** a value; **switch one off only when no contact uses it**
   (move its contacts to another value first, in bulk); an import that brings a switched-off value back reuses it and
   switches it on again; never rename or delete one, so imports keep matching. "Add contact" by hand stays. **Agreed 21 Oct.**
4. A row needs a name and an email or a mobile; everything else may be empty. **Parked by the owner (21 Oct) for
   later improvement; built this way meanwhile**, with one addition (owner, 21 Oct): **Source List and List Provided
   By are required on every contact**, from the row or the file's default (as the client's Field List has them);
   History / Source may stay empty.
5. A person already in the CRM, in a later batch: **kept as built for now** (owner, 21 Oct): a row whose email or
   mobile is already in the CRM, without that contact's CRM ID, is a problem and stops the file; a row with the CRM
   ID updates that contact. **Parked for later improvement** (proposed then: recognise and update, never refuse).
6. **Agreed 21 Oct (all three parts).** The import page: map the file's columns (automatic for known headings), set defaults for the file (Source
   List, List Provided By, History / Source, owners), check, then a summary (new contacts, contacts updated, new
   list values with their row counts), then import. All or nothing stays for real problems.
7. 2,000 rows per file stays for now (split bigger batches); a background import later if needed. **Agreed 21 Oct.**
8. This year's Category, Sub-category and Tier: kept out of step 1, and added with step 3, when inviting needs
   them. Consequence: an as-written Category ("Speaker Gold") is not a system category, so the per-admin category
   limits (decision 22) cannot apply in step 1. Whoever holds the CRM boxes sees every contact; give them only to
   the CRM team. The limits come back with this year's Category. **Agreed for step 1 (21 Oct); this year's Category
   and the limits are decided when step 3 is planned.**
9. Personal photo: uploaded by an admin later (one by one on the contact, or many named by CRM ID), never from a
   file. **Waits for the client's PDPL OK** (their template excludes photos).

**Rework of the first build (done 2026-10-21):** the contact table (list value ids instead of checked keys; owners as text;
status moved by the system), a new `crm_list_values` table replacing the Source List table, the save rules
(identity and operational only), the importer (mapping, defaults, values created, people updated, other columns
kept), the filters (a dropdown per list), the form and window (reference shown, list values changeable, text
reference read-only), Settings (the lists). The server's copy of the registration lists goes. Scope, audit,
history, the list screen, bulk, imports list, menu, Roles (minus "own") and the `check:rbac` fix stay. ("Scope"
here: as built there is no category scope at all, per the CRITICAL note and point 8.)

## What step 1 delivers (as built)

- **CRM** in the sidebar (Operations), with three tabs: **Contacts**, **Imports**, **Settings** (Settings only with
  its box).
- **Contacts:** the list with a tab per Category value (as the files wrote it), the Invitation Status tiles, search,
  a filter per supporting list (each with "No value") and the owners matched as text; add, see, edit and delete a
  contact; bulk edit.
- **A contact's window:** every field in the template's groups, the lists by their values' names, **From the
  imports** (every file row it came from or was updated by, each column as written), and History.
- **Imports:** any file of contacts; the column mapping, the file's defaults, *Check* (problems by row, or the
  summary), *Import* (all or nothing); past imports with their defaults and Tier Sign-off Reference; *Download
  template*.
- **Settings:** the sixteen supporting lists: add a value; switch one off only when no contact holds it; switch it
  on again.
- **Roles:** the CRM boxes. Revision 2 had no per-admin category limit; revision 3 brings it back (the note above).
- **History and audit trail** on every change.

**Left for later steps:** tracking and the system status (step 2); inviting, CRM collections, "Mark as sent by
hand", prefill, this year's Category and the category limits (step 3); activities, reminders, the bell, Tier 1
escalation, the report, the Activity Log sheet (step 4); export (step 5). Photos wait for the client's PDPL OK.

## Database (four new tables, nothing changed on existing ones)

Migrations `2026_10_21_000003` to `000005`, edited in place for revision 2 (they had never run anywhere). Run on the
local `tourise_clean` 2026-10-22: from now on a change is a rollback first, or a new migration.

| Table | Columns |
|---|---|
| `crm_list_values` | `id` (uuid), `list` (one of the sixteen keys), `name` (as the file first wrote it), `match_key` (unique per list), `is_active`, `created_by`, timestamps |
| `crm_imports` | `id`, `file_name`, `rows_created`, `rows_updated`, `tier_signoff_reference`, `defaults` (json), `mapping` (json: the file's heading => the CRM column it was read as, or null), `created_by`, timestamps |
| `crm_import_rows` | `id`, `crm_import_id` (cascade), `crm_contact_id`, `row_number`, `cells` (json: heading => cell, the filled cells as written), timestamps. No foreign key to the contact (the table is made first); the model removes a contact's rows with it |
| `crm_contacts` | `id`, `crm_number` (unique, shown as C-000001); text: `first_name`, `last_name`, `first_name_ar`, `last_name_ar`, `job_title`, `company`, `email` and `phone` (each nullable, unique); the sixteen `<list>_value_id` (crm_list_values); reference text `received_by`, `previous_engagement`, `previous_category`; operational `relationship_owner`, `follow_up_owner` (text), `invitation_channel`, `security_clearance`, `invitation_status` (default `not_sent`), `invitation_sent_at`, `invitation_sent_by`, `last_contact_date`, `next_reminder_date`, `notes`; `possible_duplicate`, `crm_import_id`, `created_by`, `updated_by`, timestamps |

## The values each field takes

| Kind | Fields | Kept where |
|---|---|---|
| Supporting list (16) | Prefix (`title`), Company Location, Gender, Nationality, Country of Residence (`country`), Region, Sector, Industry, Sub-industry, Seniority Level (`seniority`), Category, Sub-category, Tier, Source List, List Provided By, History / Source | `crm_list_values`, held as `<list>_value_id`; the keys and labels in `App\Support\CrmLists` |
| Fixed list | Invitation Channel, Security Clearance (with the labels the import reads), Invitation Status | `App\Support\CrmContactValues` |
| Text | names, Arabic names, job title, company, email, mobile, the two owners, Received By, Previous Engagement, Previous Category, notes | the contact |
| Date | Last Contact Date, Next Reminder Date; Sent Date (from the invitation) | the contact |

A value is matched by its **match key**: lower-cased, spaces collapsed, curly apostrophes and no-break spaces made
plain. A cell reads as **empty** when blank, an Excel error (`#REF!`, `#N/A`, `#VALUE!` and the rest) or, in Region,
the template's "Check country".

## Rules checked on every write (add, edit, bulk edit, every import row), on the server

`App\Services\Crm\CrmContactRules`:

1. **A first name or a last name.**
2. **An email or a mobile**, each once in the CRM (mobile compared as `+` and digits, a leading 00 read as +).
3. **Source List and List Provided By** on every contact.
4. **A list value of its own list, switched on**, unless the contact already has it (a switched-off value stays on
   its contacts).
5. **Status:** the team sets Not Sent, In Progress or Pending; a status the contact already has is left alone; Sent
   Date and Sent By are never written by a save.
6. **H.E.'s Office with clearance Not Required** is refused.
7. **Tier** only with *View tier* (decision 29): its column, filter, value, Settings list and import column; a tier
   sent without the box is ignored.
8. **Possible duplicate** (decision 28): the same first and last name as another contact with another email is
   saved and flagged; *Not a duplicate* clears it.

No longer checked (first build): owners as admin accounts, the category scope, a sub-category within its category
or a sub-industry within its industry, and the sent and clearance rules for Sent and later (the invitation sets
those in step 3).

## Import (as built)

**In the admin** (`crm-import-form.tsx`, SheetJS):

1. **The sheet:** *Contacts* if the file has it, else the first.
2. **The heading row:** of the first three rows, the one with most headings the CRM knows; else the first filled
   row. Columns with a heading or any data; blank rows skipped.
3. **Refused before upload (PDPL):** a passport, ID, date of birth or photo column.
4. **Up to 2,000 rows.** Mobiles turned into `+` and digits (`utils/normalize-imported-phone.ts`).
5. **Columns:** each file column, its first value and what it is read as. Known headings and their other spellings
   are mapped once, automatically; any column can be changed or left *Keep with the row only*; a CRM column picked
   for a second heading moves there. Tier is not offered without *View tier*. The three invitation columns say they
   are kept as the file's record.
6. **Defaults for the file:** Source List, List Provided By and History / Source (the list's switched-on values
   suggested, any text taken), Relationship Owner, Follow-up Owner.
7. **Check**, then **Import** once the check is clean. Any change to the mapping or the defaults asks for a new check.

**The API:** `GET admin/crm/imports/columns` (each column's key, heading, kind and other headings; the PDPL words;
what may have a default; the row limit). `POST admin/crm/imports/check` and `POST admin/crm/imports` take
`{file_name, tier_signoff_reference, headings, mapping, defaults, rows: [{row, cells}]}`: the headings in the file's
order, the CRM column each is read as (or null), and every row's cells in the same order.

**On the server** (`App\Services\Crm\CrmContactImporter`), each mapped cell by its column's kind
(`App\Support\CrmImportColumns`):

- `crm_id` finds the contact; an unknown CRM ID is a problem.
- `text` is kept as written (the Arabic Name split on its first space).
- `list` is matched to its list's value by match key, or becomes a **new value** (the first spelling kept); a
  switched-off value the file brings back is **switched on**. Empty cells are skipped.
- `fixed` must be one of the list's keys or labels.
- `date`: an Excel serial number, `dd-mmm-yyyy` and the usual others; anything else is a problem.
- `history` (Invitation Status, Sent Date, Sent By) is not written to the contact: last year's facts stay with the
  row.

The defaults fill what a row leaves empty; on a row with a CRM ID only what the contact does not have yet. What a
whole file lacks is said once, not on every row: no name column, no email or mobile column, a required list neither
mapped nor given a default, two headings read as one column. Then every row is held to the rules above; the same
email, mobile or CRM ID twice in the file refuses each of those rows; an email or mobile already in the CRM on a row
without its CRM ID is refused, naming the CRM ID (point 5, as built). The client's example row (Notes "EXAMPLE ROW")
is skipped.

**The check** returns the problems, or the summary: rows, new contacts, contacts updated, the new list values with
how many rows bring each, and the switched-off values it would switch on.

**The import**, in one transaction and only when nothing is wrong: the CRM number is locked first (a second import
waits); the import row with its defaults and mapping; the new list values inserted together; switched-off values
switched on through the model (audited); new contacts inserted together as Not Sent; updated contacts saved through
the model (each one's History has the change); **every row's cells saved** to `crm_import_rows`, mapped or not; one
audit row with the counts.

**Measured** (2,000 rows, SQLite test database): check 2.2 s, 6 queries; import 2.2 s, 21 queries; the same 2,000
again by CRM ID 4.9 s, about 4,000 queries (each updated contact's save and its History row). The request body was
0.6 MB; a full 37-column file can pass 1 MB (see *Before deploy*).

**The template** (`CrmContactImportWorkbook`, *Download template*): the 37 headings, dropdowns from each list's
switched-on values (Tier with *View tier*) and the two fixed lists. A list's dropdown warns and lets a new value
through, which the import adds; a fixed list's refuses. The three invitation headings carry a note: kept with the
row, this year's come from the invitation.

## Screens (admin, as built)

- **Contacts** (`/[lang]/crm`, `crm-contacts-listing.tsx`): tabs *All* and one per Category value with contacts
  (`?tab=`); the tiles; search over name (EN, AR), email, mobile, company, job title and CRM ID; filters in the URL:
  Invitation Status, channel, clearance, Sub-category, Tier (with the box), both owners (text), next reminder
  (overdue, this week), last contact date, every other list, import file, date added, possible duplicate; columns
  CRM ID, name (prefix, duplicate chip, email), company and job title, Category and Sub-category, Tier (with the
  box), relationship owner, channel, clearance, status, next reminder (orange when overdue).
- **Bulk bar** (ticked rows, or *select all matching*, up to 2,000): *Edit selected* (`crm-bulk-modal.tsx`: the
  status, the team's three; channel; clearance; an owner as text; or any list, pointed at another of its values),
  *Not a duplicate*, delete. The contacts a change could not reach are listed with the reason.
- **A contact** (`crm-contact-modal.tsx`): as above, with *History* (with *Record History*) and *Edit*.
- **Add / edit** (`crm-contact-form.tsx`): names, contact details and the operational fields are typed; each list is
  a searchable dropdown of its switched-on values (and the contact's own); Received By, Previous Engagement,
  Previous Category, Sent Date and Sent By are shown, not edited; the status offers the team's three (and the
  contact's own when the invitation set it).
- **Imports** (`/[lang]/crm/imports`): past imports with their defaults; *Import contacts* (`/[lang]/crm/imports/new`).
- **Settings** (`/[lang]/crm/settings`, `crm-lists-settings.tsx`): the sixteen lists (required ones starred), each
  value with how many contacts hold it (a link to them), *Add value*, and the switch (off refused while contacts
  hold it).
- `crm-source-list-settings.tsx` and `crm-owner-select.tsx` are gone; `use-crm-lists.ts` loads the lists for the
  filters, the form, the bulk bar, Settings and the import's defaults.

## Permissions (Roles)

`crm` in `AdminPermissions::CATALOG`: `view`, `create` (add and import), `update` (edit, bulk edit, *Not a
duplicate*), `delete`, `settings` (the lists), `record_history`, `audit_trail`. **`own` removed** with owners as
admin accounts. Tier uses *View tier* (decision 29). `check:rbac` reads `tourise-backend`: all 41 menu links agree.

Since revision 3 these boxes show only the contacts in the admin's own categories (decision 22); a Super Admin sees
all.

## The admin API (`admin/crm`, admin-only, not part of the mobile contract)

| Endpoint | Box |
|---|---|
| `GET contacts` (rows, `tabs`, `tiles`), `GET contacts/ids`, `GET contacts/{id}` (with `imports`) | any CRM box |
| `POST contacts` | `create` |
| `PUT contacts/{id}` | `update` |
| `DELETE contacts/{id}` | `delete` |
| `POST contacts/bulk` (`update`, `not_duplicate`, `delete`) | any; checked again per action |
| `GET contacts/{id}/logs` | `record_history` |
| `GET lists` | any CRM box |
| `POST lists/{list}/values`, `PUT lists/values/{id}` (`is_active`) | `settings` |
| `GET imports` | any CRM box |
| `GET imports/columns`, `GET imports/template`, `POST imports/check`, `POST imports` | `create` |
| `GET logs`, `GET logs/export` | `audit_trail` |

`GET owners` and the `source-lists` endpoints are gone.

## History and audit

- `CrmContact` and `CrmListValue` use `Auditable` (feature `crm`): each add, edit and delete records the fields
  changed and by whom; a value added in Settings, or switched off or on, is a row of its own.
- `*_value_id` reads by the value's name in every trail (`AuditLabels`, one pattern); `crm_import_id` by file name.
- An import writes one audit row (file, created, updated, unchanged, list values created and switched on, Tier
  Sign-off Reference). The contacts and list values it inserts together have no row each; the contacts it updates
  and the values it switches on go through the model.
- Bulk edits go through the model row by row, in one transaction.

## Tests (backend, through HTTP)

`CrmContactsTest` (14) and `CrmImportTest` (15), 268 assertions:

1. Add: the CRM ID is the next number; the list value's name in the answer; an audit row.
2. Only a name, an email or mobile and the two source lists are required; a last name and a mobile are enough.
3. A value of another list is refused; a switched-off value is kept by its contact and refused for a new one.
4. Email and mobile once each, the mobile written another way.
5. Sent, Accepted, Declined refused; In Progress and Pending taken; Sent Date and Sent By never saved; H.E.'s
   Office needs a clearance.
6. **No category limit:** an admin limited to another category sees, opens, edits and reads the History of every
   contact.
7. Tier: not in the rows or the lists without the box, its filter and value ignored.
8. Possible duplicate flagged until cleared.
9. Bulk: pointed at another value (read by name in History), owners as text, a refused row listed with its reason,
   Sent refused.
10. Bulk boxes; delete takes the import rows with it; search, filters (a list, "none", an owner), tabs, tiles; the
    boxes; Settings add (once per list, any case or spacing), counts, switch off refused while in use, off and on.
11. Import as the client writes it: values matched any case and spacing, new ones made, Region "Check country" and
    `#REF!` empty, the old status and sent date not written.
12. Every row kept as written, unknown column included; *From the imports*; the Tier cell hidden without the box.
13. The check: problems by row, the new values with their row counts, nothing written.
14. One bad row and nothing is written (no contacts, values, import or rows).
15. Defaults fill what a row leaves empty, a row's own cell wins; a required list neither mapped nor defaulted said
    once; two headings for one column.
16. A CRM ID row updates, its empty cells and the defaults change nothing it has; the change in History; an
    unknown CRM ID.
17. Repeats in the file; an email already in the CRM without its CRM ID.
18. The same name twice flagged; a switched-off value brought back switched on; a passport column; the example
    row; Tier not read without the box.
19. The template: 37 headings, the history note, the switched-on values and fixed labels only; the columns
    endpoint and the boxes.

## Where the build differs from the plan

- **Reference text read-only on the form, not in the API.** The form shows Received By, Previous Engagement and
  Previous Category without editing them (revision 2, "text reference read-only"), and leaves them off the add form;
  the API still accepts them (`CrmContact::TEXT_FIELDS`), as the backend rework had it.
- **Defaults never overwrite.** On a row with a CRM ID, a default fills only a field the contact has empty.
- **The mapping is kept with the import** (`crm_imports.mapping`), so *From the imports* labels each cell with the
  column it was read as, and hides a Tier cell from admins without *View tier*.
- **What a whole file lacks is one problem**, not 2,000 (no name, no email or mobile, a required list without a
  column or a default, a column read twice).
- **Template dropdowns warn, not refuse, on the lists**, since the import adds new values.
- **Values an import makes are not audited one by one**; the import's audit row counts them.
- **Tabs are the Category values in use**; a contact without a Category is under *All* only.
- **Tier in History:** a tier change still shows in History and the audit trails to any admin who can open them
  (found 10-21; owner: leave it as it is).
- **The tiles count, they do not filter**, and **a bulk edit sets one field at a time**, as in the first build.

## To try it (local)

1. Backend: `php artisan migrate` (`2026_10_21_000003` to `000005`: four new tables, nothing else changes).
2. A Super Admin has every CRM box; for anyone else tick the CRM boxes in Roles (and *View tier* to see Tier).
   Each box holder sees the contacts in their own categories (revision 3).
3. CRM, Imports, *Import contacts*: choose any file (or *Download template* and fill a few rows), check the
   mapping, set Source List and List Provided By as defaults if the file has no such columns, *Check the file*,
   read the summary, *Import*.
4. Open a contact: *From the imports* shows its row as written. Edit one; bulk-move a few to another Category
   value; in Settings, switch the emptied value off.

## Before deploy

- **The team's two lists:** add the Source List and List Provided By values in CRM, Lists before the first import
  (revision 3, decision 42).
- **Upload size:** a 2,000-row file's request body can pass 1 MB, nginx's default `client_max_body_size`; check it
  (and PHP's `post_max_size`) on the server, or split files.
- **Roles:** the old `own` box no longer exists; nothing to untick (it was never deployed).

## Questions for the owner

Asked one at a time.

1. **All or nothing on import?** The other three imports refuse the whole file when one row is wrong; the
   preview shows every problem first, so the file is fixed and uploaded again. The alternative imports the good
   rows and lists the rest. Recommended: all or nothing, the house pattern; nothing is ever half imported.
   **Answered 10-21: all or nothing, for now.**
2. **A backend copy of the industry, sub-industry, seniority and gender lists?** The backend checks them nowhere
   today (guests store whatever arrives); the lists live in the admin and the public site. The template is built by
   the backend and needs them for its dropdowns, and the import should check them on the server. Recommended: one
   copy of the keys and English names in the backend, used by the CRM only, with a note to change all three
   together; guests unchanged.
   **Answered 10-21: yes, the backend copy (A).** Superseded by revision 2: these lists are supporting lists kept
   as the files write them, so the copy (`RegistrationLists`) was removed.
