<!-- report
eyebrow: CRM
subtitle: Everything on feat/crm-foundations, now on testing: what to test and what each step should show
meta: Server=testing|Date=2026-10-26
footer: CRM team test scenarios
-->
# CRM: team test scenarios

Everything below is on the **testing server** now (the `feat/crm-foundations` work: the CRM with Tracking,
Speakers and the dashboards, and the changes around it in Categories, Invitation Requests, Invitations, Guests and
the registration forms). Test with your own test inboxes only, and note anything that does not match the
**Expected** column (a screenshot helps).

**Your test files** (one set each, with its own README and PDF):

| Tester | Contacts | Speakers |
|---|---|---|
| Eissa | `eissa-test-cases-real-scenarios` | `eissa-test-cases-speakers` |
| Rawand | `rawand-test-cases-real-scenarios.zip` | `rawand-test-cases-speakers.zip` |
| Imtinan | `imtinan-test-cases-real-scenarios.zip` | `imtinan-test-cases-speakers.zip` |

No address is shared between testers, so everyone can import into the same CRM.

**Before you start (once, by an admin):**

1. **CRM, Settings:** add the Source List and List Provided By values your README lists. A contacts file that names a
   value not on the list is refused.
2. **Roles:** for any role other than Super Admin, tick the CRM boxes it needs: View, Create, Update, Delete,
   Invite, View dashboard (Contacts), and the speakers' ones (View speakers, Add and import speakers, Edit
   speakers, Delete speakers, Invite speakers, View speakers dashboard).

## 1. Tabs and pages

| # | Do | Expected |
|---|---|---|
| 1.1 | Open **CRM** from the sidebar | The tabs **Contacts, Speakers, Settings**; Contacts opens on its **Dashboard**. No Imports tab. |
| 1.2 | Click **Data**, then **Dashboard** | The table, then the charts. Filters set on one stay on the other. |
| 1.3 | Open **Speakers** | Its own Dashboard and Data, with the speakers' columns and filters only. |
| 1.4 | Log in with a role that has only the speakers' boxes | Only the Speakers tab (and Settings if ticked); the Contacts pages are not reachable. |

## 2. Contacts: add, edit and lists

| # | Do | Expected |
|---|---|---|
| 2.1 | **Add contact** with a required field empty | Refused, each field named; required fields are marked as in the client's sheet. Email or Mobile: one is enough. |
| 2.2 | Pick a **Category** | Its **Sub-category** is asked only when it has some, and offers only those under it. Industry and Sub-industry the same. |
| 2.3 | Pick a **Country of Residence** | **Region** fills itself (MENA, Europe...). |
| 2.4 | Every list field (Title, Nationality, Sector, Seniority, Tier...) | A dropdown of the system's own values, the same as on Guests. Tier only for a role with **View tier**. |
| 2.5 | Edit a cell in the table, or a field in the contact's window | Saved in place; a wrong value refused with the reason. |
| 2.6 | **Columns** | Hide and show columns; kept for you. |
| 2.7 | **Edit selected** (bulk) on a few contacts | One change to all; those the rules stop are listed with the reason. |
| 2.8 | A role limited to some categories | Sees and edits only those categories' contacts; another category is refused. |
| 2.9 | **History** in a contact's window; **Audit trail** on the page | Each change, who and when. |

## 3. Contacts import (CRM, Contacts, Data, Import contacts)

Follow your **real-scenarios README**, file by file. The points that changed recently:

| # | Do | Expected |
|---|---|---|
| 3.1 | Import `01` and `02` first | Clean, then imported (8 each). They show in Contacts, never in Speakers. |
| 3.2 | Check `03-speakers-programme` | **Refused**: "Speakers go in the Speakers tab, not in Contacts." on each Speaker row (one message per row); the Moderator row is fine. Nothing imported. |
| 3.3 | Check `20-not-on-the-list` | 16 problems, one per row, each naming the cell; row 15 says "Speakers go in the Speakers tab". |
| 3.4 | Choose `17-pdpl-columns` | Refused on the page: passport, ID, date of birth and photo (or headshot) columns are never imported. |
| 3.5 | Any value written differently from the list ("Saudi", "H.E" without the dot) | Refused, naming the cell. Only upper/lower case and extra spaces are ignored. |
| 3.6 | Below the import form | The **past imports** of Contacts only. |

## 4. Speakers import (CRM, Speakers, Data, Import speakers)

Follow your **speakers README** in order (01 to 08), into a CRM with no speakers yet.

| # | Do | Expected |
|---|---|---|
| 4.1 | `01-happy-path`: Check, then Import | 6 speakers added, Status **Not Sent**, shown in Speakers only. |
| 4.2 | `02` to `05` | Each refused as the README says: missing cells (every column is required for now), values not on the lists, repeats, an email already in the CRM. |
| 4.3 | `06-update-by-crm-id` | 2 speakers updated; the empty cells change nothing. |
| 4.4 | `07` and `08`: the team's own Speaker Required Fields sheet | 07 refused on the page (headshot, Passport); 08 refused because **Speaker** is one name: the sample has First Name and Last Name. |
| 4.5 | **Download sample** | The speakers' template: every heading dark blue, dropdowns for Day, Pillar, Session, Type, Gender, Country, Continent and Official invite to be sent by (the system's Titles). |

## 5. Dashboards (both tabs)

| # | Do | Expected |
|---|---|---|
| 5.1 | Open each tab's Dashboard after importing | One card per dropdown list with the counts (Contacts: Category, Sub-category, Tier, Seniority, Sector, Industry, Country, Region, Nationality, Gender, Source List, Channel, Clearance and the rest; Speakers: Day, Pillar, Session, Type, Gender, Country, Continent, Official invite). No tiles. |
| 5.2 | Switch **Chart / Table** | The same numbers as bars, then as a table with shares. |
| 5.3 | Click a bar | The page filters to that value; click it again to lift it. **Data** then shows the same contacts. |
| 5.4 | Apply a filter (e.g. Tier 1) | Every card counts only those. |
| 5.5 | Watch the page load | The charts draw once, no flicker. |
| 5.6 | **Print report** | A clean landscape report of the cards. |

## 6. Speakers: table, window and form

| # | Do | Expected |
|---|---|---|
| 6.1 | Speakers, Data | The sheet's columns in its order (Day, Pillar, Session, Keyword, Type, Option #, First and Last Name, ...). |
| 6.2 | Filters | Search, Day, Pillar, Session, Type, Status always shown; more under **+ Add filter**. |
| 6.3 | Edit a cell in the table | Saved in place; a wrong value is refused with the reason. |
| 6.4 | Open a speaker (the eye) | Cards: Session, Speaker, Invitation, Contact person, Profile, History. |
| 6.5 | **Add speaker** with a field empty | Refused: every field is required for now, each named. |
| 6.6 | Edit selected (bulk) | Status, the two owners, or any of the speakers' lists, for many at once. |

## 7. Photo, with drag and drop

| # | Do | Expected |
|---|---|---|
| 7.1 | Edit a contact or a speaker, drop an image on **Photo** | Uploaded at once; it shows in the form and the window. |
| 7.2 | Open the window, drop an image on the **round photo** | Uploaded; a blue ring while dragging. |
| 7.3 | **Add** a contact or speaker with a photo dropped | The photo is saved right after the record. |
| 7.4 | Drop a PDF, or an image over 5 MB | Refused with a message; JPG, PNG and WebP only. |

## 8. One person, one place

| # | Do | Expected |
|---|---|---|
| 8.1 | Add a speaker with an email already on a contact | Refused: "This email is already on CRM contact C-...". |
| 8.2 | Add a contact with an email already on a speaker | Refused: "This email is already on CRM speaker C-...". |
| 8.3 | Contacts: Category filter, form and bulk edit | No **Speaker** category (speakers have their own tab). Moderator is still there for now. |
| 8.4 | Same name, other email, in either tab | Saved, marked as a possible duplicate. |

## 9. Tracking and Invite (both tabs)

| # | Do | Expected |
|---|---|---|
| 9.1 | **Create targeted collection**, then tick records and **Invite** (Add and send) | The Status column moves to **Invited**, then **Sent** once the email goes. |
| 9.2 | Register with the invitation's link (your test inbox) | Status **Registered**. |
| 9.3 | Answer "Will you attend?" yes / no | **Confirmed** / **Declined**. |
| 9.4 | Check the guest in at the event | **Checked in**. |
| 9.5 | Open the record's window | The journey with each step's date; the email's delivery and opening under Sent. |
| 9.6 | Guests and Invitations | The guest or invitation shows **CRM C-...**, opening the contact or speaker. |
| 9.7 | Status filter; "sent, not opened after N days"; "sent, not registered" | Each finds the right records. |

## 10. Settings

| # | Do | Expected |
|---|---|---|
| 10.1 | CRM, Settings | Source List and List Provided By (add, switch off); below, the system's lists read-only, then the speakers' lists read-only. |
| 10.2 | Click a list low down | Its values open beside it, in view; the list of lists scrolls on its own. |

## 11. Sub-categories (Categories)

| # | Do | Expected |
|---|---|---|
| 11.1 | Categories, a category's **Sub-categories** | Add, rename, switch on and off; one save per click. |
| 11.2 | Guests, Invitations, Invitation Requests | Each record carries its Sub-category beside its Category; lists, filters and exports show it. |
| 11.3 | The main **Dashboard** | Filters by Sub-category, and splits a category by its sub-categories. |

## 12. Invitation Requests and targeted collections

| # | Do | Expected |
|---|---|---|
| 12.1 | **Accept** a request | You pick the **targeted collection** it goes into (one request collection per category); the invitation lands there. |
| 12.2 | Create a targeted collection, then try to change its sub-category, tier or link settings | Locked once made: the collection decides them for every invitation in it. |
| 12.3 | Open an accepted request's (or a CRM) invitation link | The registration form opens. |

## 13. Invitations

| # | Do | Expected |
|---|---|---|
| 13.1 | A collection's page | A bulk bar as on the other modules; **Select all matching** ticks every invitation the filters find. |
| 13.2 | An invitation made from the CRM | Shows **CRM C-...**, opening the contact or speaker. |

## 14. Guests and the registration forms

| # | Do | Expected |
|---|---|---|
| 14.1 | Guests: add, edit, list, filters | **Company Location** (Local / International), **Sector** (Public / Private) and **Tier** (with View tier only). |
| 14.2 | The public registration form (frontend) | Company Location and Sector asked as **dropdowns**, not radio buttons; saved on the guest. |

## Not in this round

- **Save the Date** (two columns) and **Follow Up Status**: parked, waiting for the client and the team.
- **Moderator** in the contacts' Category: still allowed; to confirm with the team.
- **Imtinan's edit-form changes**: on hold.
- CRM steps 4 (activities, reminders, notifications) and 5 (export): on hold.
