# Task 054: Prospects (a CRM for people we may invite)

- **Status:** `todo`: plan only, nothing built. Six points wait on the owner (see *Open, with a recommendation*).
- **Opened:** 2026-10-13
- **Owner:** unassigned
- **Sub-app(s):** backend + admin
- **Branch(es):** `feat/prospects` in `tourise-backend` + `tourise-admin`, off `dev`.

## Goal

The team keeps lists of people it may want at the event. Today those lists live in Excel, and nobody can tell
from the sheet whether a person has already asked for an invitation, already been invited, or already
registered. This task adds a **Prospects** section: upload the list, see where each person stands in the
system, keep a follow-up status and notes, and invite from there.

## Decisions (owner, 2026-10-13)

| # | Decision |
|---|---|
| 1 | **A section of its own.** Not built on Nominations: a nominee registers for nothing and gets no link, a prospect is someone we may invite. Own tables, own permission. |
| 2 | **Matched by email only**, trimmed and lower-cased, the rule the request form, the partner API and invitations already use (ledger D56). No phone or name matching. |
| 3 | **Two statuses side by side.** One the system works out (where the person stands), one the team sets (where the follow-up stands). |
| 4 | **Four actions:** send an invitation; edit, note and update the status (one or many); open the linked request, invitation or guest; export to Excel. |

## Open, with a recommendation

Each is built as recommended unless the owner says otherwise.

| # | Question | Recommended | Why |
|---|---|---|---|
| A | Columns in the Excel | Title, First name, Last name, **Email** (the only required one), Company, Job title, Phone, Country, Language | The columns an invitation takes, so inviting is a straight copy with nothing to retype. |
| B | The team's status values | Fixed in v1: **New, Contacted, Interested, Not interested, Do not invite** | A fixed list can be filtered, counted and translated. An editable list is a settings screen of its own; add it when the five prove wrong. |
| C | One list or named lists | **Named lists**, one per upload ("Sponsor leads, October"), with a filter across all | The team thinks in lists, and "who came from which sheet" is the first question asked of a merged table. |
| D | An email that is already a prospect | **One person, one record.** The preview marks those rows and the import leaves them out, keeping the record that exists | Two rows for one person means two statuses and two sets of notes. See the note under *Import* on how this differs from the other imports. |
| E | Name of the section | **Prospects** | "CRM" names a product, "Leads" is sales. |
| F | Who sees it | Whoever holds the Prospects permission, the whole list | A prospect has no category until invited, so the guest category scope has nothing to read. Inviting still respects it: an admin only picks collections they may see. |

## The best approach, and what it avoids

**The system's status is read, never stored.** It is looked up by email each time the list is shown. A stored
copy would have to be corrected every time someone files a request, is invited, registers or is deleted, in
four other modules, and the first one that forgot would leave the section wrong without anyone noticing.

**Inviting goes through Invitations, not beside it.** The prospect is added to an invitation collection the
admin picks, by the same code "Add people" runs (Task 050). The collection already carries the category,
channel, template and sender, and that code already refuses a registered or already invited address. A
second way of minting invitations would have to copy all of that and keep it in step.

**A pending request is accepted, not bypassed.** Inviting someone whose request is waiting would leave the
request pending forever beside a live invitation. The section links to the request instead.

## Design

### Tables (two new, none changed)

- `prospect_lists`: `name`, `created_by`. One per upload; a prospect added by hand goes in a list too.
- `prospects`: `prospect_list_id`, `title_id`, `first_name`, `last_name`, `email` (**unique**, stored
  trimmed and lower-cased), `company`, `job_title`, `phone`, `country_id`, `lang`, `status` (the team's,
  default `new`), `note`, `created_by`, timestamps. Indexes on `status` and `prospect_list_id`.

An invitation made from a prospect is stamped `created_via = 'prospect'` (the column exists since Task 050),
so "how many invitations came from Prospects" can be counted without a link column.

### The system's status

Worked out from three lookups on the email, for the rows on screen. The furthest stage wins.

| Shown | When | Detail shown with it | Opens |
|---|---|---|---|
| **Registered** | a guest has this email | category, guest status | the guest |
| **Invited** | an invitation has this email | collection, sent or not, used or not, "from a request" when a request minted it | the invitation |
| **Requested** | an invitation request has this email and no invitation | pending / rejected, the request form | the request |
| **Not in system** | none of the above | | |

An accepted request always has its invitation, so it reads Invited. Filtering by this status is done in SQL
(`EXISTS` on each table), so it works across pages and in the export.

### Screens (Operations > Prospects)

- **Lists and upload.** New list: a name, the Excel file, the preview with mapped columns, the problems
  dialog, then Create. Download Excel sample.
- **Prospects.** One table across all lists: name, email, company, list, system status, team status,
  last update. Filters: list, system status, team status, company, search. Tiles above it counting the
  system statuses, each a filter when clicked.
- **A prospect.** Details, both statuses, the note, the linked record, and History.
- **Bulk:** set the team status, invite, export, delete.

### Import

The existing pattern: parsed in the browser, checked in the preview and again on the server, 1,000 rows.

- Refused, with the row and the reason: no email, bad email, the same email twice in the file, bad phone,
  unknown title or country, over 1,000 rows.
- **Not refused:** an email that has already requested, been invited or registered. Showing that is the
  purpose of the section, so the preview counts them ("12 already invited, 4 already registered") and
  imports them.
- **Already a prospect** (point D): left out, and the preview says how many. This differs on purpose from
  Invitations, Nominations and the Newsletter, which refuse the whole file. There a duplicate means a
  second email to the same person. Here it means the same person arrived on two lists, which is normal,
  and making the admin edit the sheet each time would be work for no gain.

### Inviting

The admin picks a single-use collection they may see, and whether to send now or only add.

| System status | Invite |
|---|---|
| Not in system | Allowed |
| Requested, pending | Not from here. "Open the request" to accept it there |
| Requested, rejected | Asks first: "This person's request was rejected. Invite anyway?" |
| Invited, Registered | Not offered; the linked record is |
| Team status **Do not invite** | Not offered until the status is changed |

In bulk, those allowed are invited and the answer lists the rest with the reason for each. The server
repeats every check, because the list on screen may be minutes old.

### Permissions and audit

A new `prospects` feature in `AdminPermissions`: View, Create, Update, Delete, Invite, Export, Record
History, Audit Trail. Roles start unticked. Inviting also needs the Invitations permission the same action
needs there. Audited from the start (Task 045): the import, edits, status changes, deletes, invites,
exports.

## What is reused

| Need | Taken from | Change to it |
|---|---|---|
| Excel parsing, preview, problems dialog, sample file | Nominations and Newsletter import (Tasks 051, 052) | None; new column map |
| "Already invited" | `Invitation::alreadyInvited()` | None |
| "Already registered" | `InvitationsController::refuseRegisteredEmails()` | Moved where both can call it |
| Minting the invitations | `InvitationsController::addGuests()` (Task 050) | Its body moves into a service that both call. One path, not two |
| Sending them | `InvitationsController::sendInvitationsBulk()` | None |
| Listing, filters, bulk bar | `use-listing-state`, the invitation requests listing | None |
| Export | `TouriseSheetStyle`, an export class like `NominationsExport` | New class |
| History and audit trail | `AuditLog::record()`, `AuditLogsController` | A `prospects` feature added |
| Permissions | `AdminPermissions`, `admin.can` | One entry |
| Sidebar group | `resolveGroup()` sends an unknown link to Operations | One link |

New: two tables, one controller, the status lookup, three screens, one export, translations in EN and AR.

## Cases

1. A prospect files a request after the upload: reads Requested on the next load, nothing to do.
2. A prospect is invited from Invitations, not from here: reads Invited all the same.
3. A prospect registers: reads Registered; the team status is left as the team set it.
4. The linked request, invitation or guest is deleted: falls back to the stage before it.
5. A prospect's email is edited: the match is re-read; the new email must not be another prospect's.
6. A prospect is deleted: only the prospect goes. Never the request, invitation or guest.
7. A list is deleted: its prospects go with it, after a confirmation naming how many.
8. The same person on two uploads: one record, in the first list (point D).
9. Bulk invite of 200 with 30 not allowed: 170 invited, 30 listed with reasons, nothing half done.
10. The collection picked is a shared link (`usage_type = multiple`): refused, as Add people refuses it.
11. An admin with Prospects but not Invitations: sees everything, cannot invite.
12. An Arabic prospect (`lang = ar`): invited with the collection's Arabic template, as any invitation.

## Build order

Each step is mergeable alone.

1. **Lists, upload, table.** Tables, import, listing with the team status, edit, notes, delete,
   permissions, audit. Useful by itself as a shared list.
2. **The system's status.** The lookup, the column, the filter, the tiles, the links to the records.
3. **Inviting.** The shared minting service, the collection picker, the per-status rules, bulk.
4. **Export.** One list or the filtered table, both statuses included.

## Out of scope

- Matching by phone or name, and merging two people (decision 2).
- Emailing prospects without inviting them. That is what Nominations is.
- Assigning prospects to an admin, reminders, a contact log.
- Any public route. Nothing here is reachable without an admin login.
- The mobile app: admin routes only, the mobile contract is untouched.

## To check before building

- **Size.** The lookups run per page, so a list of thousands is fine. The status filter runs `EXISTS`
  against `invitations.email`, which has no index (guests and requests have one). Add the index in step 2
  if the client expects more than a few thousand prospects.
- **How emails are stored.** Requests are stored lower-cased; guests and invitations may hold mixed case.
  The match must compare lower-cased on both sides, as `alreadyInvited()` does, or it will miss people.
- **D56's open point.** Someone already invited can still file a request. The section will show them as
  Invited, which is correct, but the stray pending request stays in the queue.

## Log

- 2026-10-13: opened. Decisions 1 to 4 taken with the owner; plan written. Points A to F wait on the owner.

## Definition of Done

- [ ] Code merged to `dev` in backend and admin
- [ ] EN + AR translations in the same commit
- [ ] Quality gate green (backend `pint --test` + `php artisan test`; admin type-check + production build)
- [ ] The twelve cases above covered by backend tests, through HTTP
- [ ] Docs updated (this TASK.md, the index row, D-ledger if point D is confirmed)
- [ ] Roles: the Prospects boxes ticked on the roles that need them, after deploy
