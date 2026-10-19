# Task 054: Prospects (a CRM for people we may invite)

- **Status:** `todo`: plan only, nothing built. Revised 2026-10-19 around the client's
  `TOURISE_CRM_Fields_and_Import_Template_v4.1.xlsx` (replaces v3 and v4), and the owner's answer on
  sub-categories. Points that wait on the owner or the client are under *Open*.
- **Opened:** 2026-10-13
- **Owner:** unassigned
- **Sub-app(s):** backend + admin (+ frontend for the sub-category an invitation carries into registration)
- **Branch(es):** `feat/sub-categories` then `feat/prospects`, in `tourise-backend` + `tourise-admin`, off
  `dev`.

## Goal

The team keeps lists of people it may want at the event, today in Excel, with no way to tell from the sheet
whether a person has already asked for an invitation, been invited, or registered. This task adds a
**Prospects** section: import the client's CRM sheet, see where each person stands in the system, keep the
invitation status, channel, clearance, owner, tier, follow-up and activity the sheet tracks, and invite
them as an invitation collection.

It starts with **sub-categories** (decision 16), which the CRM needs and which the rest of the system takes
too: guests, invitations and the CRM all carry one.

## Decisions

| # | Date | Decision |
|---|---|---|
| 1 | 10-13 | **A section of its own.** Not built on Nominations: a nominee registers for nothing and gets no link, a prospect is someone we may invite. Own tables, own permission. |
| 2 | 10-13 | **Matched to the system by email**, trimmed and lower-cased, the rule the request form, the partner API and invitations use (ledger D56). A row may carry a mobile and no email (decision 8). |
| 3 | 10-13 | **Two statuses side by side.** One the system works out (where the person stands in TOURISE), one the team keeps (the template's **Invitation Status**, which replaced v3's Outreach Status). |
| 4 | 10-13 | **Actions:** invite; edit, log activity and update the status (one or many); open the linked request, invitation or guest; export to Excel. |
| 5 | 10-19 | **The columns are the client's template v4.1** (sheet *Contacts*, 37 columns), listed under *Columns*. |
| 6 | 10-18 | **Category comes from the Excel, or is chosen by hand.** It is one of the system's event categories. Required in v4.1, with a sub-category. |
| 7 | 10-18 | **A tab per category** (Speaker, Sponsor, Dignitary …), to work one category at a time. Inviting is not tied to the tab (decision 14). |
| 8 | 10-18 | **Importing never sends anything.** It only fills the CRM. A row with a mobile and no email is imported, and can be invited later on an SMS or WhatsApp collection, not an email one. |
| 9 | 10-18 | **Who did what is always known.** Every import, edit, status or owner change, activity, invite and delete records the admin who did it, shown on the record's History and in the audit trail. Prospects joins the admin activity notifications (Task 048). |
| 10 | 10-18 | **Tracked by link, not only by email.** A prospect invited from here keeps that invitation's id, and the invitation leads to the guest who registered with it (`guests.code_id`), so the prospect stays tracked if the person registers with another email. |
| 11 | 10-18 | **Inviting picks a collection**, and the CRM shows who was invited from it: a filter *Invited from CRM*, and on each row the collection and whether it was sent. |
| 12 | 10-18 | **The shared fields carry the guest table's own names and values**, so nothing is mapped between the CRM and Guests (`title_id`, `first_name`, `last_name`, `first_name_ar`, `last_name_ar`, `job_title`, `company`, `email`, `phone`, `gender`, `nationality`, `country_of_residence`, `sector`, `industry`, `sub_industry`, `seniority_level`, `category_id`, and now `sub_category_id`). |
| 13 | 10-18 | **The table shows the source and the statuses** as columns, not only on the record. |
| 14 | 10-18 | **The admin chooses the collection, not the category.** Invite works from any tab: pick any collection the admin may see, or make a new one; its category, channel and template decide the invitation. |
| 15 | 10-18 | **Search and filters** over every column worth asking about, held in the URL. |
| 16 | 10-19 | **Sub-categories exist, system-wide.** Defined per category in **Category settings**. Whenever a category is chosen, its sub-category is chosen beside it. It behaves like a **tag** on invitations, prospects and guests: shown, filtered and editable when sending invitations, adding a guest or editing one. See *Sub-categories*. |
| 20 | 10-19 | **The Relationship Owner and the Follow-up Owner are admin accounts** (was open 3) with the Prospects permission for the prospect's category. The owner picker offers only those admins. Each reassignment is logged: old owner, new owner, who changed it, when. An import names the owner by the admin's email or name; an unknown one is refused. |
| 21 | 10-19 | **Notifications go to the owner.** Being made owner, a reminder falling due, a reminder going overdue, and a change in the prospect's tracking (invitation sent, opened, registered, declined) notify the follow-up owner, else the relationship owner, in the admin bell (Task 048) and by email if they turn it on. A daily check raises the due and overdue ones. |
| 22 | 10-19 | **Prospects is set up in Roles, per category.** The Prospects boxes sit in the role editor with the other modules, and a role's category limits apply: an admin sees, owns, imports into and invites only the categories their role allows. Tier stays behind its own box. |
| 23 | 10-19 | **Tracking is the heart of it.** For every prospect the CRM shows where the person is in the system, as one journey: *In CRM, Requested, Invited, Sent, Delivered, Opened, Registered, Confirmed* (with *Declined* or *Rejected* where they stop), each step with its date and a link to the record. See *Tracking*. |

## Open

| # | Question | Where it stands |
|---|---|---|
| 1 | **The values behind the dropdowns.** v4.1's dropdowns read `#REF!` again (its lookup sheets were deleted, as in v3). The *Field List* and *Status Definitions* sheets give most values (below); still missing: **Source List**, **Activity Type**, **Outcome**, and the **Industry Hierarchy** with EG's pending proposals | Waiting on the client for those four. Planned as lists an admin keeps in the section's Settings. |
| 2 | **"Accepted opens registration through the CRM."** v4.1 makes acceptance a step before registration: the guest accepts, then the CRM sends the registration email. Our invitation email *is* the registration link today | Options below; recommended A. |
| 3 | ~~**Relationship Owner**~~ | Decided 10-19: admin accounts with the Prospects permission (decision 20). |
| 4 | **After registration: one record or two.** | Recommended B (linked; the guest wins), unchanged. |
| 5 | **Prefilled registration (for the client).** | Unchanged: to ask the client. |
| 6 | **Does a sub-category choose the template?** The Field List says the sub-category "sets the exact template (e.g. Ministers & Excellencies Local)". The owner asked for a tag | Options below; recommended A (tag now, template later). |
| 7 | **Is a sub-category required?** The CRM template requires one. Guests and invitations? | Recommended: required when the chosen category has sub-categories defined, optional otherwise. |
| 8 | **The template disagrees with itself** on four columns (see *Template findings*) | To confirm with the client before the import is built. |
| 9 | **Possible duplicates and merging.** v4.1 flags duplicates (email, mobile, then name) and has the CRM admin merge them before invitations go out. Merging was out of scope | Options below; recommended A. |
| 10 | **Sub-event Invitations** (a system field: "summary of sub-event RSVPs", from a sheet or screen of that name) | Not in the file and not in the system. To ask the client what sub-events are, and leave it out of the first build. |

**Accepted and registration, the options (open 2)**

| Option | What happens | For | Against |
|---|---|---|---|
| A. **Accepted = registered** (recommended) | The invitation email stays the registration link. The CRM's Invitation Status reads *Accepted* once the person registers through it (and *Declined* when they answer no) | No new step for the guest; nothing in the registration flow changes | The client's two steps (accept, then a registration email) become one |
| B. Two steps | The CRM's invitation asks *accept / decline* first (an RSVP page); *Accepted* sends a second email with the registration link | Follows the template's wording | A new public page and email, and every invited guest clicks twice |
| C. Manual | *Accepted* is set by hand (accepted by phone, through H.E.'s Office…); setting it sends the registration invitation from the CRM | Fits invitations sent outside the system | A guest invited by the CRM itself still needs someone to set it |

A and C can live together: a CRM-channel invitation follows A, a manual channel follows C (decision 18).

**Sub-category and templates, the options (open 6)**

| Option | What happens | For | Against |
|---|---|---|---|
| A. **A tag now** (recommended) | The sub-category is shown, filtered, exported and carried from invitation to guest. The category still picks the form and the emails | What the owner asked for; small | The client's "exact template per sub-category" waits |
| B. Template per sub-category | A sub-category may name its own invitation, registration and confirmation templates; empty falls back to the category's | Follows the Field List | Every template lookup learns a second level; more to set up per category |

**Duplicates, the options (open 9)**

| Option | What happens | For | Against |
|---|---|---|---|
| A. **Refuse on import, flag on name** (recommended) | Same email or mobile: refused, naming the existing CRM ID (the current rule). Same first and last name with a different email: imported and flagged *Possible duplicate*, for an admin to look at; no merge tool | Nothing is merged by mistake | Two records for one person until someone deletes one |
| B. A merge tool | The flagged pair can be merged: one record keeps both histories | What the template asks | A merge across activities, invitations and history to get right |

## Sub-categories (decision 16)

Built first, on its own branch, because guests and invitations take it as well as the CRM.

**Defined in Category settings.** The category form gets a **Sub-categories** section: a list of name (EN,
AR), order and active, added, renamed, reordered and switched off there. A sub-category in use cannot be
deleted, only switched off: an inactive one stays on the records that have it and is no longer offered.
Seeded from the client's *Badge Categories* sheet (about 40 *System Categories*, e.g. Dignitary: Head of
State International, Ministers & Excellencies International, Ambassadors …).

**Stored once, used everywhere.** One table and one nullable column on each record that has a category:

- `sub_categories`: `id`, `category_id`, `name_en`, `name_ar`, `sort_order`, `is_active`, timestamps;
  unique (`category_id`, `name_en`).
- `sub_category_id` on `guests`, `invitations`, `invitation_collections` (the default for its
  invitations) and `prospects`.

The server checks that a sub-category belongs to the record's category; anything else is refused.

**Chosen with the category, wherever a category is chosen:**

| Where | How |
|---|---|
| Category settings | Defines the list |
| Guest: admin Add, See more / profile (in place), Change category | A second select beside the category, offering that category's sub-categories |
| Guest import (Excel) | A *Sub-category* column, matched by name within the row's category |
| Invitations: new collection | The collection's default sub-category |
| Invitations: Add people, the guest card, invitation import | Per person, starting from the collection's default |
| Invite someone (dignitary party) | Picked with the group |
| CRM: import, record, bulk edit | A column, a field, a bulk action |
| Registration | Not asked of the guest (it is the team's tag). A guest who registers through an invitation takes the invitation's sub-category; one who registers without an invitation has none until an admin sets it |

**Changing the category** clears the sub-category (the old one belongs to the old category), and the Change
category dialog asks for the new one in the same step.

**Shown as a tag** beside the category: a column and a filter on the guest list, the invitations list, the
collection details and the CRM; a chip in See more and the profile; a column in every export; a field in
the guest's history and the audit trail. A bulk action on the guest list sets it for the ticked guests.

Saving it touches the guest's **three save paths** (public store, admin create, admin update), which have
drifted before; each is tested through HTTP.

## Columns (sheet *Contacts*, headings in row 2; row 3 is the client's example and is skipped)

Required as the *Field List* marks them; `*` = Email **or** Mobile. **Same as registration** means the guest
record already has the field with the same values, so the CRM stores it the same way.

| Group | Column | Required | Stored as | Registration |
|---|---|---|---|---|
| Identity | CRM ID | auto | `crm_id`, made by the system (`C-000001`). Blank = new; filled = **update** that person | CRM only |
| | Prefix | yes | `title_id` | Same |
| | First Name, Last Name | yes | text, as per passport where known | Same |
| | Arabic Name | no | `first_name_ar`, `last_name_ar`, split on the first space | Same; needed for KSA security clearance |
| | Job Title, Company | yes | text (company: full official name, one spelling) | Same |
| | Company Location | yes | `local` / `international` | CRM only |
| | Email | yes* | unique, trimmed, lower-cased | Same |
| | Mobile | yes* | `+` and the country code | Same (`phone`) |
| | Gender | no | `male` / `female` | Same |
| | Nationality, Country of Residence | yes | country ids | Same |
| | Region | auto | read from the country | Same (`countries.region`) |
| Classification | Sector | yes | Public / Private | Same list (two of its five values) |
| | Industry, Sub-industry | yes | the registration keys | Same lists (EG proposals pending, *Open* 1) |
| | Seniority Level | yes | the registration keys | Same list |
| | Category | yes | `category_id` | Same |
| | Sub-category | yes | `sub_category_id`, within the category | **Same** (decision 16) |
| | Tier | yes | `tier_1` / `tier_2` / `tier_3` (Tier 4 removed), admin only, never guest-facing | CRM only |
| Relationship & Source | Source List | yes | a list (*Open* 1) | CRM only |
| | List Provided By | yes | text (entity, office or team) | CRM only |
| | Relationship Owner | **yes** | an admin account (decision 20); each change logged | CRM only |
| Invitation | Invitation Channel | yes | `he_office`, `mofa`, `royal_court`, `other_ministries`, `relationship_owner`, `crm` | CRM only |
| | Security Clearance | yes | `not_required`, `not_submitted`, `pending`, `approved`, `not_approved` | CRM only |
| | Invitation Status | yes | `not_sent`, `in_progress`, `sent`, `pending`, `accepted`, `declined` | CRM only |
| | Invitation Sent Date | if sent | date | CRM only |
| | Invitation Sent By | if sent | text (H.E.'s Office, MOFA, EG (CRM) …) | CRM only |
| Follow-up | Follow-up Owner | no | an admin account; blank = the relationship owner | CRM only |
| | Last Contact Date | no | date | CRM only |
| | Next Reminder Date | no | date; overdue reads orange | CRM only |
| History | History / Source | no | `tourise_2025`, `external_event`, `manual_invitation_2027`, `other` | CRM only (the guest's `source` is how they registered) |
| | Received By, Previous Engagement, Previous Category, Notes | no | text | CRM only |
| Check | Row Check | — | the sheet's own formula; ignored on import (the server checks again) | — |

**Not to be imported (PDPL):** passport and ID numbers, dates of birth, photos. The import has no such
columns, and a file that carries them is refused rather than silently ignored.

**System fields** (filled by the CRM, never imported): Registration Status (read from the system, see *The
system's status*), Registration Link Sent date, Tier Sign-off Reference, Owner History (activity entries),
Possible Duplicate (*Open* 9), Last Updated / By. Sub-event Invitations is *Open* 10.

The sheet **Activity Log** (CRM ID or Email, First Name, Last Name, Date, Activity Type, Outcome, Logged By,
On Behalf Of, Next Reminder Date, Notes) is imported with it, one row per activity, matched by CRM ID, else
email. Its dates arrive as Excel serial numbers and are read as dates.

The sheet **Tier Sign-off** is the client's approval step (Fahad signs off before import) and is **not
imported**: the Tier on *Contacts* is what lands, and the CRM admin records the *Tier Sign-off Reference*
(e.g. "Tier list v1 · 18 Oct") on the import.

## Invitation channel, clearance and status (decisions 17 to 19)

| # | Date | Decision |
|---|---|---|
| 17 | 10-19 | **Only the CRM channel sends from the system.** For H.E.'s Office, MOFA, Royal Court, Other Ministries and Relationship Owner, the invitation goes out elsewhere and is **recorded** in the CRM (status, sent date, sent by). A recorded invitation stops the CRM sending its own. |
| 18 | 10-19 | **Clearance gates sending.** H.E.'s Office needs *Approved* before the status can move to *Sent*; *Not Required* is refused for that channel; *Not Submitted* and *Pending* block any send; *Not Approved* blocks it and shows "escalate to Fahad". Enforced on the server, in bulk too. |
| 19 | 10-19 | **Invitation Status follows the system where the system knows** (replaces open 2 of v3): *Sent* is set when the CRM sends; a manual channel sets *Sent* with date and sender; *Accepted* / *Declined* per *Open* 2. *In Progress* and *Pending* stay the team's. |

The **Status Definitions** sheet's wording is shown as help beside each value.

## The approach, and what it avoids

**The system's status is read, never stored.** Looked up each time the list is shown, from the link first
(decision 10) and the email for anyone the CRM did not invite. A stored copy would have to be corrected from
four modules every time someone files a request, is invited, registers or is deleted.

**Inviting goes through Invitations.** Prospects are added to a collection by the code "Add people" already
runs (Task 050), which refuses a registered or already invited address. One way of minting invitations.

**A pending request is accepted, not bypassed.** The section links to the request instead.

**The template comes from the system.** v4.1's dropdowns are broken like v3's. *Download template* builds
the same 37 columns with working dropdowns fed from the system's own lists (titles, countries, sectors,
industries, seniority, categories and their sub-categories, the CRM's lists), as the invitation and
nomination templates are built. The client's own file still uploads: columns are read by heading.

### Tracking (decision 23)

The question the section answers first: **where is this person in the system?** Each prospect has a
journey, read live from the records it links to, never typed:

| Step | Reached when | Shown with |
|---|---|---|
| **In CRM** | imported or added | date, by whom, the import file |
| **Requested** | a request has the email | pending / accepted / rejected, the form, date |
| **Invited** | an invitation exists (from the CRM or a request) | collection, channel, who invited, date |
| **Sent** | the invitation was sent, or a manual send was recorded | date, by the system or by whom (H.E.'s Office, MOFA …) |
| **Delivered**, **Opened** | the email or message provider says so | date |
| **Registered** | a guest registered with the invitation, or with the email | registration number, category and sub-category, date, the email used if it differs |
| **Confirmed** | the guest's status is confirmed / attending | guest status, attending or not |
| *Declined*, *Rejected* | the guest declined, or the request was rejected | date, who |

- **On the list:** one *Tracking* column with the furthest step as a chip (and the date), and the steps as
  dots, so a glance shows how far each person got. A filter per step ("invited, not opened after 7 days",
  "sent, not registered").
- **On the record:** the journey as a timeline at the top, each step a link to its request, invitation or
  guest, followed by the team's activities and the history.
- **Tiles** count the open tab per step, as a funnel: in CRM → invited → sent → opened → registered →
  confirmed.
- **Changes notify the owner** (decision 21).

### The system's status

| Shown | When | With it | Opens |
|---|---|---|---|
| **Registered** | a guest has this email, or registered with the CRM's invitation | registration number, category and sub-category, guest status, attending or not, the email they registered with when it differs | the guest |
| **Invited** | an invitation has this email, or the CRM made one | collection; not sent / sent / delivered / opened; not used / used; from CRM or from a request; the invitation link | the invitation |
| **Requested** | a request has this email and no invitation | pending / accepted / rejected | the request |
| **Not in system** | none of the above | | |
| **No email** | the prospect has no email | | |

The template's *Registration Status* (Not started / Link sent / Registered / Confirmed) is this column in its
words: Link sent = Invited and sent, Registered = Registered, Confirmed = registered and attending.

### Screens (Operations > Prospects: Prospects | Imports | Settings | Report)

- **Prospects.** Tabs: All, one per category that has prospects, No category. The table (name, company,
  category and sub-category, tier, owner, channel, clearance, invitation status, system status, next
  reminder), filters, tiles counting the statuses.
- **A prospect.** All columns, both statuses, the linked record, the activity log with *Log activity*,
  owner history, History.
- **Bulk bar:** set invitation status, channel, clearance, owner, tier, category and sub-category; record a
  manual invitation (date, sender); invite; export; delete.
- **Imports.** Upload, preview, problems, Create; past imports with their Tier Sign-off Reference;
  *Download template*.
- **Settings.** The admin-kept lists (*Open* 1).
- **Report.** Owners down, invitation statuses across, counts, filtered by category, sub-category, tier and
  channel; overdue reminders by owner; exported to Excel.

### Search and filters

One search box over name (EN, AR), email, mobile, company, job title and CRM ID. Filters, combinable, kept in
the URL and applied to the export:

| Group | Filters |
|---|---|
| Where they stand | In TOURISE; Invited from CRM; collection |
| The team's follow-up | Invitation Status; Invitation Channel; Security Clearance; Relationship Owner; Follow-up Owner; Tier; next reminder (overdue, this week); last contact date; no activity yet |
| Who they are | Category (also the tabs); Sub-category; Sector; Industry; Sub-industry; Seniority Level; Gender |
| Where they are | Nationality; Country of Residence; Region; Company Location |
| Where they came from | Source List; List Provided By; History / Source; import file; date added; Possible duplicate |

### Import

Parsed in the browser, checked in the preview and again on the server. 2,000 rows, the template's size.

- **Skipped:** the grey example row (row 3), and any row whose Notes read "EXAMPLE ROW".
- **Refused, with the row and the reason:** neither email nor mobile; bad email or mobile; a required column
  empty; a value not in its list (prefix, country, sector, industry, sub-industry not under that industry,
  seniority, category, sub-category not under that category, tier, channel, clearance, status, source
  list, owner); Sent or later without a sent date and sender; H.E.'s Office with clearance *Not Required*; a
  CRM ID that does not exist; the same email or mobile twice in the file; a passport, ID, date of birth or
  photo column (PDPL).
- **An email or mobile already in the CRM with no CRM ID:** refused, naming the existing CRM ID.
- **Same name, different email:** imported and flagged *Possible duplicate* (*Open* 9).
- **Not refused:** someone who has already requested, been invited or registered. The preview counts them.
- **With a CRM ID:** the row updates that prospect; an empty cell leaves the field as it was. An owner change
  is logged as a reassignment.

### Inviting

From any tab, tick prospects and **Invite** (decision 14): choose a collection (or make one: name,
category, **sub-category**, channel, template, sender, usage), then send now or only add. Each invitation
takes the prospect's sub-category, else the collection's.

| Prospect | Invite |
|---|---|
| Not in system | Allowed |
| Channel is not CRM | Not from here: "Record the invitation" (date, sender) instead (decision 17) |
| Clearance blocks it | Refused with the reason (decision 18) |
| No email | Allowed on an SMS or WhatsApp collection only |
| Requested, pending | Not from here: "Open the request" |
| Requested, rejected; Declined | Asks first |
| Already sent (by the CRM or recorded) | Not offered |
| Invited, Registered | Not offered; the linked record is |

In bulk, those allowed are invited and the answer lists the rest with the reason for each. The server
repeats every check.

### Roles, permissions and notifications

A new `prospects` feature in `AdminPermissions`, ticked in **Roles** like every module (decision 22): View,
Create, Update, Delete, Invite, Export, Settings, Record History, Audit Trail, **View tier** (tier is
admin-only) and **Can own prospects** (who may be chosen as relationship or follow-up owner). Inviting also
needs the Invitations permission.

**Per category.** The role's category limits apply to every part of the section: the tabs, the list, the
counts, the report and the export show only the allowed categories; an import row in another category is
refused; the owner picker offers only admins whose role covers the prospect's category; a prospect moved to a
category its owner cannot see asks for a new owner.

**Notifications** (decision 21), in the bell and, if the admin turns it on, by email:

| Event | Goes to |
|---|---|
| Made relationship or follow-up owner (one, or a bulk count) | the new owner |
| Next Reminder Date is today; it has passed (once a day while overdue) | the follow-up owner, else the relationship owner |
| Tracking moves: sent, opened, registered, confirmed, declined | the same |
| A request filed by one of your prospects | the same |
| Everything else (imports, edits, deletes) | admins who follow Prospects in their notification settings (Task 048) |

A daily scheduled check raises the due and overdue reminders. Audited from the start (Task 045); the bell
picks it up through `AdminActivityFeed::MODULES`.

Sub-categories need no permission of their own: who may edit a category may edit its sub-categories, and who
may edit a guest or an invitation may set its sub-category.

## What is reused

| Need | Taken from | Change to it |
|---|---|---|
| Excel parsing, preview, problems dialog | Nominations and Newsletter import (Tasks 051, 052) | New column map |
| The template with working dropdowns | `InvitationImportWorkbook`, `NominationImportWorkbook` | New workbook class; dependent lists (industry, category) |
| Titles, countries and region, sectors, industries, seniority | The registration form's lists | None |
| "Already invited" / "already registered" | `Invitation::alreadyInvited()`, `refuseRegisteredEmails()` | The second moves where both can call it |
| Creating the collection, adding people, sending | Invitations (Task 050) | Add people's body moves into a service; both take a sub-category |
| Tabs, listing, filters, bulk bar | `use-listing-state`, the invitation requests listing | None |
| Sub-category select | The category selects already on these forms | A dependent select beside each |
| Export | `TouriseSheetStyle` | New class |
| History, audit trail, notifications | `AuditLog::record()`, `AdminActivityFeed` | A `prospects` feature |

## Cases

1. A prospect files a request after the import: reads Requested on the next load.
2. A prospect is invited from Invitations, not from here: reads Invited all the same.
3. A prospect registers through the CRM's invitation: reads Registered, the guest takes the invitation's
   sub-category, and the Invitation Status reads Accepted (*Open* 2 A).
4. The linked request, invitation or guest is deleted: falls back to the stage before it.
5. A prospect's email is edited: the match is re-read; the new email must not be another prospect's.
6. Re-import with CRM IDs: those rows update, blank cells change nothing, an owner change is logged.
7. The same person sent by two teams: the second upload is refused with the first's CRM ID.
8. A prospect with a mobile and no email: imported, shows No email; invited only on SMS or WhatsApp.
9. A prospect's category is changed: its sub-category is cleared and a new one asked for; it moves tab.
10. Bulk invite of 200 with 30 not allowed (channel, clearance, status): 170 invited, 30 listed with reasons.
11. H.E.'s Office with clearance Pending: cannot be marked Sent, by hand or in bulk.
12. An invitation recorded as sent by MOFA: the CRM never sends its own for that person.
13. An admin without *View tier*: the tier column, filter and export column are not there.
14. A sub-category is switched off: records keep it; it is no longer offered.
15. A guest's category is changed from See more: the dialog asks for the new category's sub-category.
16. Invited from the CRM as a@x.com, registers as a.b@y.com: still Registered, through the link.
17. The client's file with its example row and broken dropdowns: the example row is skipped; values are read
    as text and checked against the system's lists.

18. An owner's reminder passes: they get one notification that day and one each day after, until it is
    moved or done.
19. A prospect is moved to a category its owner's role does not cover: the move asks for a new owner.
20. An admin limited to Speakers imports a file with a Sponsor row: that row is refused.
21. A prospect opens the invitation, then registers with another email: the owner is notified twice, and
    the journey reads Opened then Registered, through the link.

## Build order

Each step is mergeable alone.

0. **Sub-categories** (`feat/sub-categories`): table and Category settings; `sub_category_id` on guests,
   invitations, collections; the dependent select on the guest forms, See more, Change category, the
   collection form, Add people, the guest card and the imports; inherited at registration; column, filter,
   bulk set and export on the guest and invitation lists. Tests through HTTP on the three guest save paths.
1. **Import and records.** Tables, settings lists, the template, import with CRM ID update, the table with
   tabs, the record, edit, bulk edit, permissions, audit.
2. **Tracking.** The journey lookup, the column with its steps, filters, funnel tiles, the timeline, links.
3. **Inviting.** The shared minting service, channel and clearance rules, recording manual invitations.
4. **Activity log, follow-up, notifications and the report.** Log activity, owners' reminders and the daily
   check, the owner notifications, the Activity Log sheet, the report.
5. **Export.**

## Out of scope

- Matching to the system by mobile or by name for the system status (name only flags a possible duplicate).
- Merging two prospects (*Open* 9 B).
- The Tier Sign-off workflow inside the system (stays the client's sheet).
- Sub-event invitations (*Open* 10).
- Emailing prospects without inviting them: that is Nominations.
- Any public route except the registration taking the invitation's sub-category; the mobile app.

## Template findings (v4.1)

- **Every dropdown reads `#REF!`**, and the Category → Sub-category and Industry → Sub-industry lists
  (`OFFSET(#REF! …)`) do too: the lookup sheets were deleted before the file was shared. The values are
  recovered from the *Field List* and *Status Definitions* sheets, except Source List, Activity Type, Outcome
  and the industry hierarchy (*Open* 1).
- **The Contacts sheet and the Field List disagree** (*Open* 8):
  - The Field List has **Follow-up Owner** and **Last Contact Date**; the Contacts sheet has neither, and a
    column **Follow-up sent** the Field List does not mention.
  - The Contacts sheet has **Previous category**; the Field List does not.
  - The Read Me counts **36 fields**; the Contacts sheet has 36 data columns plus Row Check, the Field List 37
    rows including seven system fields.
- **Dates** in the Activity Log are Excel serial numbers (46309); read as dates.
- **Region** says "Check country" in the example row: the formula's lookup is broken too; the system fills
  it from the country.

## To check before building

- **The dropdown lists** (*Open* 1) before step 1 can validate those columns.
- **`invitations.email` has no index**: add it in step 2.
- **Mixed-case emails:** every match compares lower-cased on both sides.
- **The guest's three save paths** must all take `sub_category_id` (step 0), tested through HTTP.
- **Seeding sub-categories** from the client's *Badge Categories* sheet: which of our categories each of its
  badge categories is.

## Log

- 2026-10-13: opened. Decisions 1 to 4 with the owner; first plan written.
- 2026-10-18: revised around the client's template v3 (decisions 5 to 15); open points written out.
- 2026-10-19: revised around v4.1 (replaces v3 and v4): Tier 1 to 3; category and sub-category required;
  Relationship Owner required with reassignment logged; Invitation Channel, Security Clearance and
  Invitation Status (replacing Outreach Status) with their rules (decisions 17 to 19); manual invitation
  tracking; follow-up dates; duplicates; PDPL; system fields. The owner answered on sub-categories: they
  exist, are defined in Category settings, are chosen with the category and work as a tag on invitations,
  the CRM and guests (decision 16, build step 0). New open points: acceptance and registration, sub-category
  and templates, whether a sub-category is required, the template's inconsistencies, duplicates, sub-events.
- 2026-10-19: the owner answered: owners are admin accounts with the Prospects permission (decision 20, was
  open 3); reminders and tracking changes notify the owner (21); Prospects is set in Roles, limited by
  category (22); tracking where each person is in the system is the heart of the section (23, *Tracking*).

## Definition of Done

- [ ] Code merged to `dev` in backend and admin (and frontend for step 0)
- [ ] EN + AR translations in the same commit
- [ ] Quality gate green (backend `pint --test` + `php artisan test`; admin type-check + production build)
- [ ] The cases above covered by backend tests, through HTTP
- [ ] Docs updated (this TASK.md, the index row)
- [ ] Roles: the Prospects boxes ticked on the roles that need them, after deploy
