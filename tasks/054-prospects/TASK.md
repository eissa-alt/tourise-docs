# Task 054: CRM (contacts we may invite; called Prospects until 2026-10-21)

- **Status:** `in-progress`, **live on production**: steps 1 to 3 and 5 (import and records, Tracking, inviting,
  export), the Activity Log, the team's fixes of 28 and 29 October and the 1 to 2 November changes are on `main`
  and deployed (the 2026-10-29 release, backend `bd169df`; the 2026-11-02 deploy, migrations to
  `2026_11_02_000001`). Step 4 (notifications) in part: follow-up bells (decision 56). What was built after
  2026-10-25 is under *Log* and decisions 51 to 71; the plans ([STEP_1_PLAN.md](STEP_1_PLAN.md),
  [STEP_2_PLAN.md](STEP_2_PLAN.md), [STEP_3_PLAN.md](STEP_3_PLAN.md), [FIXED_LISTS_PLAN.md](FIXED_LISTS_PLAN.md))
  are as built then. *Open* was not re-checked after 2026-10-25. Imtinan's entries were written from her commits,
  for her to check. Based on the client's
  [`TOURISE_CRM_Fields_and_Import_Template_v4.1.xlsx`](../../client/CRM_PLAN_V1/TOURISE_CRM_Fields_and_Import_Template_v4.1.xlsx),
  then the team's FINAL template (28 columns, 2026-10-28). The client-facing guide is
  [`client/TOURISE_CRM_GUIDE`](../../client/TOURISE_CRM_GUIDE/README.md) (Imtinan, to 2026-10-29).
- **Opened:** 2026-10-13
- **Owner:** Eissa and Imtinan
- **Sub-app(s):** backend + admin (+ frontend for the registration's side)
- **Branch(es):** `feat/crm-foundations` (to 2026-10-26), `crm-foundations-2` (2026-10-26 and 27), then one branch
  per change from `testing` (named in the *Log*); `testing` into `main` per release. `dev` is no longer used.

## Goal

The team keeps lists of people it may want at the event, today in Excel, with no way to tell from the sheet
whether a person has already asked for an invitation, been invited, or registered. This task adds a
**Prospects** section: import the client's CRM sheet, see where each person stands in the system, keep the
invitation status, channel, clearance, owner, tier, follow-up and activity the sheet tracks, and invite
them as an invitation collection.

What the CRM shares with the rest of the system was built first, on the guest and the invitation:
**sub-categories** ([Task 055](../055-system-categories/TASK.md)), **Company Location, Sector and Tier**
([Task 056](../056-company-location-sector-tier/TASK.md)) and **targeted collections** for accepted requests
([Task 057](../057-request-collections-per-category/TASK.md)). The CRM stores those fields under the same
names and values (decision 12).

## Decisions

| # | Date | Decision |
|---|---|---|
| 1 | 10-13 | **A section of its own.** Not built on Nominations: a nominee registers for nothing and gets no link, a prospect is someone we may invite. Own tables, own permission. |
| 2 | 10-13 | **Matched to the system by email**, trimmed and lower-cased, the rule the request form, the partner API and invitations use (ledger D56). A row may carry a mobile and no email (decision 8). |
| 3 | 10-13 | **Two statuses side by side.** One the system works out (where the person stands in TOURISE), one the team keeps (the template's **Invitation Status**, which replaced v3's Outreach Status). |
| 4 | 10-13 | **Actions:** invite; edit, log activity and update the status (one or many); open the linked request, invitation or guest; export to Excel. |
| 5 | 10-19 | **The columns are the client's template v4.1** (sheet *Contacts*: 36 columns, plus the sheet's own Row Check; count corrected 10-21), listed under *Columns*. |
| 6 | 10-18 | **Category comes from the Excel, or is chosen by hand.** It is one of the system's event categories. Required in v4.1, with a sub-category (required when the category has an active list, as on every admin form: Task 055 decision 7). |
| 7 | 10-18 | **A tab per category** (Speaker, Sponsor, Dignitary …), to work one category at a time. Inviting is not tied to the tab (decision 14), but each CRM collection serves one category (decision 33). |
| 8 | 10-18 | **Importing never sends anything.** It only fills the CRM. A row with a mobile and no email is imported, and can be invited later on an SMS or WhatsApp collection, not an email one. |
| 9 | 10-18 | **Who did what is always known.** Every import, edit, status or owner change, activity, invite and delete records the admin who did it, shown on the record's History and in the audit trail. Prospects joins the admin activity notifications (Task 048). |
| 10 | 10-18 | **Tracked by link, not only by email.** A prospect invited from here keeps that invitation's id, and the invitation leads to the guest who registered with it (`guests.code_id`), so the prospect stays tracked if the person registers with another email. |
| 11 | 10-18 | **Inviting picks a collection**, and the CRM shows who was invited from it: a filter *Invited from CRM*, and on each row the collection and whether it was sent. |
| 12 | 10-18 | **The shared fields carry the guest table's own names and values**, so nothing is mapped between the CRM and Guests (`title_id`, `first_name`, `last_name`, `first_name_ar`, `last_name_ar`, `job_title`, `company`, `email`, `phone`, `gender`, `nationality`, `country_of_residence`, `sector`, `industry`, `sub_industry`, `seniority_level`, `category_id`, and since Tasks 055 and 056 `sub_category_id`, `company_location` and `tier`). |
| 13 | 10-18 | **The table shows the source and the statuses** as columns, not only on the record. |
| 14 | 10-18 | **The admin chooses the collection, not the category.** Invite works from any tab: pick any collection the admin may see, or make a new one; its category, channel and template decide the invitation, and since Tasks 055 to 057 its sub-category, tier and link settings too (*Open* 11 asks whether a prospect's own sub-category and tier win). Narrowed 10-21 by decision 33: a CRM collection of the prospects' category. |
| 15 | 10-18 | **Search and filters** over every column worth asking about, held in the URL. |
| 16 | 10-19 | **Sub-categories exist, system-wide.** Built as [Task 055](../055-system-categories/TASK.md): a list per category in **Category settings**, entered by admins (not loaded from the client's sheet), labelled "Sub-category" (AR "النوع الفرعي"), chosen beside the category on every admin form, a **tag** only (*Open* 6 closed). See *Step 0*. |
| 20 | 10-19 | **The Relationship Owner and the Follow-up Owner are admin accounts** (was open 3) with the Prospects permission for the prospect's category. The owner picker offers only those admins. Each reassignment is logged: old owner, new owner, who changed it, when. An import names the owner by the admin's email or name; an unknown one is refused. |
| 21 | 10-19 | **Notifications go to the owner.** Being made owner, a reminder falling due, a reminder going overdue, and a change in the prospect's tracking (invitation sent, opened, registered, declined) notify the follow-up owner, else the relationship owner, in the admin bell (Task 048) and by email if they turn it on. A daily check raises the due and overdue ones. |
| 22 | 10-19 | **Prospects is set up in Roles, per category.** The Prospects boxes sit in the role editor with the other modules, and the admin's own category limits apply (set on each admin account, `admins.category_ids`; corrected 10-21, was "the role's"): an admin sees, owns, imports into and invites only their categories; a Super Admin sees all. Tier stays behind the *View tier* box (decision 29). |
| 23 | 10-19 | **Tracking is the heart of it.** For every prospect the CRM shows where the person is in the system, as one journey: *In CRM, Requested, Invited, Sent, Delivered, Opened, Registered, Confirmed* (with *Declined* or *Rejected* where they stop), each step with its date and a link to the record. See *Tracking*. |
| 24 | 10-20 | **Company Location, Sector and Tier live on the guest**, not in the CRM only ([Task 056](../056-company-location-sector-tier/TASK.md)). Company Location `local` / `international`; Sector Public / Private only (`public_sector` / `private_sector`); Tier `tier_1` to `tier_3`, set on the admin guest form and on collections, carried to the guest at registration, seen only with the *View tier* box (`guests_listing.view_tier`). The CRM stores the same keys. |
| 25 | 10-21 | **Accepted requests go through targeted collections** ([Task 057](../057-request-collections-per-category/TASK.md)): one per category, made with a button on Invitation Requests. Accepting asks only which one, and the collection decides category, sub-category, tier, channel, template, account and link settings. The CRM never accepts a request itself (*The approach*). |
| 26 | 10-21 | **Industry is the system's list, as it is, for now** (was part of *Open* 1). The client's 07.10 list differs (4 industries renamed, Retail, Non-Profit & Philanthropy and Professional Services & Consulting new, sub-industry changes); aligning the two waits. The import checks the system's list and refuses any other value with the row and the reason; *Download template* offers the system's list. |
| 27 | 10-21 | **Both versions of the template are read** (was *Open* 8). A prospect holds 37 fields: the Contacts sheet's 36 plus *Last Contact Date* from the Field List. The import reads the Follow-up Owner under either heading (*Follow-up Owner*, or the Contacts sheet's *Follow-up sent*), and *Last Contact Date* and *Previous Category* when the file has them. *Download template* carries all 37 under the Field List's names. |
| 28 | 10-21 | **Duplicates are refused or flagged, never merged** (was *Open* 9; owner: no invitation has gone out yet, keep it simple). The same email or mobile twice in a file: both rows refused; mobiles compared by their digits. An email or mobile already in the CRM on a row without a CRM ID: refused, naming the existing CRM ID. The same first and last name with another email: imported and flagged *Possible duplicate*; an admin clears the flag ("not a duplicate") or deletes one of the two. A merge tool can come later with nothing to undo. |
| 29 | 10-21 | **One tier box** (was *Open* 12). Prospects uses the *View tier* box Task 056 added (`guests_listing.view_tier`) and its rule (`GuestFieldValues::tierVisibleTo()`): whoever may see tier sees it on guests, invitations and prospects alike. Its label in Roles says it covers the CRM too (e.g. "View tier (guests, invitations, prospects)"), EN + AR. |
| 30 | 10-21 | **No accept step before registration** (was *Open* 2; A for the CRM channel, C for the manual ones). **CRM channel:** the invitation email is the registration link, as today; registering through it reads *Accepted*, its "Not interested" button (`invitation_link_not_interested`, a one-click decline that already exists) reads *Declined*. **Manual channels** (H.E.'s Office, MOFA, Royal Court, Other Ministries, Relationship Owner): the team sets *Accepted* or *Declined* by hand from what the office reports; *Accepted* only lets the team send that person the registration link from the CRM (Invite, picking a collection), the one exception to decision 17. Setting a status never sends anything by itself, so a bulk status change cannot send emails. The client's "Accepted opens registration through the CRM" is read this way (to tell them in one line). |
| 31 | 10-21 | **After registration the prospect stays, linked, and the guest wins** (was *Open* 4, B). The shared fields (decision 12, Tier included since Task 056) are shown from the guest and edited on the guest; the CRM keeps and edits only what it alone holds: owners, channel, clearance, Invitation Status, source, activities, history. A re-import with a CRM ID leaves a registered prospect's shared fields as they are, and the preview says so. |
| 32 | 10-21 | **Registration is prefilled with what the CRM knows, still editable** (was *Open* 5, B; to confirm with the client). On top of today's seven (title, first and last name, email, phone, company, job title): gender, nationality, country of residence, Company Location, sector, industry, sub-industry and seniority level on all ten forms in use; only what the category's form shows is filled. **Not** the Arabic first and last name (owner): the Media form still asks the guest to type them. Category, sub-category and tier travel with the invitation; region comes from the country. Built by the invitation check returning the linked prospect's fields (no new invitation columns) and the five form files behind the ten forms reading them; the collection's lock works as today. Step 3. |
| 33 | 10-21 | **Tier and sub-category are the CRM's until registration** (was *Open* 11; owner: "ok for now", final after the team's testing). (1) They are set on the prospect only (import, edit, bulk edit). (2) Inviting from the CRM uses a **CRM collection**, a new collection type beside "From invitation requests" and "From dignitary parties" (its own tag in the Collections list), **one per category**, with category, channel, template, account and link settings but **no tier and no sub-category of its own**: each invitation copies the prospect's. A prospect of another category is skipped with the reason. (3) Changed on the prospect before registration: the unused invitation changes with it. (4) After registration the guest holds them (decision 31): the CRM shows them read-only, with a link to the guest. Editing them from the CRM screen as well (saved to the guest) was asked and left for later; a two-copy sync is not used. |
| 34 | 10-21 | **Notifications in the bell only, for now** (was *Open* 14, A). No email; it can be added later with nothing to undo. The bell still needs work in step 4: today it is a feed of audit rows for the modules an admin ticks, and only Invitations is one (`AdminActivityFeed::MODULES`). The CRM adds a `prospects` module to that feed (imports, edits, deletes) **and** a new kind of bell item addressed to one admin (made owner, reminder due or overdue, tracking moves, a request filed by their contact), raised by the daily check and by the tracking. |
| 35 | 10-21 | **Tier 1 declines escalate at once to a list kept in CRM Settings** (was *Open* 15, A). An admin ticks who receives Tier 1 escalations (e.g. Fahad's account, the stream leads). When a Tier 1 contact is declined ("Not interested" in the email, or marked Declined by hand), those admins and the contact's owner get a bell item addressed to them (decision 34) the same moment. Step 4. |
| 36 | 10-21 | **Invitation emails record when they are delivered, opened and clicked** (was *Open* 16, A), the way nomination emails do (Task 051, `NominationEmail::recordMailtrapEvent`): three date columns on `invitation_emails`, set by the same Mailtrap webhook that sets the yes / no today. Production has 0 invitations, so nothing is lost. SMS and WhatsApp have no delivery information: their journey goes from *Sent* to *Registered*. Step 2. |
| 37 | 10-21 | **Named "CRM", each person a "contact"** (was *Open* 17, A), the client's words (sheet *Contacts*, "CRM ID"). Menu item and page title **CRM**; one person a **contact** ("Add contact", "Import contacts"), "CRM contact" where "contact" alone could be confused with "Contact information" or "Points of contact"; Roles boxes under **CRM**; tables `crm_*` (`crm_contacts`). Arabic labels proposed with the step 1 plan. This file still says "prospect" in its older text: read it as "CRM contact". The task folder keeps its name. |
| 38 | 10-21 | **Step 1, revision 2: old data is reference** ([STEP_1_PLAN.md](STEP_1_PLAN.md), points 1 to 9, with the owner after the team's notes). Most of a contact is kept as the files wrote it, in sixteen read-only **supporting lists**; the team works on the operational columns; the Invitation Status is moved by the system (the team sets Not Sent, In Progress, Pending); Sent Date and Sent By come from the invitation. For step 1 it overrides decisions 6 (Category is as written, not a system category), 12 (no shared keys with the guest), 20 (owners are text for now; the admin-account version and its notifications wait for step 4), 22 (**no per-admin category limits until this year's Category, step 3**: *Before release*) and 26 (Industry is as written). Built 2026-10-21. |
| 39 | 10-22 | **The collection decides, as for requests** ([STEP_3_PLAN.md](STEP_3_PLAN.md)): a CRM invitation takes the targeted collection's category, sub-category, tier, channel, template, account and link settings. Replaces decision 33 (2) and (3). |
| 40 | 10-22 | **Add only, or Add and send** ([STEP_3_PLAN.md](STEP_3_PLAN.md)): the contact moves to In Progress, and to Sent only when its invitation is actually sent. |
| 41 | 10-24 | **Revision 3: a value not on the system's list refuses the file**, each cell named ([FIXED_LISTS_PLAN.md](FIXED_LISTS_PLAN.md)). No auto-mapping and no assumptions: only case and extra spaces are ignored ("H.E" is not "H.E.", "Saudi" is not Saudi Arabia). Replaces decision 38's supporting lists for every list the system has; restores decisions 6, 12, 22 and 26 for those fields. |
| 42 | 10-24 | **Source List and List Provided By are the team's lists in CRM, Lists** ("Add value" back); **History / Source is fixed** to the template's 4 values. |
| 43 | 10-24 | **Delegate, Workforce and Exhibitor wait for the client**; until then a file naming them is refused. |
| 44 | 10-24 | **The industry list stays in code**, the system's 18, with a backend copy; the client's 21 waits for their sign-off. |
| 45 to 50 | 10-25 | **Step 2, Tracking** ([STEP_2_PLAN.md](STEP_2_PLAN.md)): link only, no email matching (45); the CRM ID shown in Guests and Invitations (46); notifications wait for step 4 (47); one column (48); Confirmed and Declined from the guest's attendance answer, then Checked in (49); the shorter journey In CRM → Invited → Sent → Registered → Confirmed → Checked in, the email's delivery and opening as details (50). |
| 51 | 10-26 | **A title in use cannot be deleted**: Titles get Delete, refused with what uses the title (guests, invitations, drafts, nominees, CRM contacts), as Guest Statuses. |
| 52 | 10-27 | **Speakers are Speaker-category contacts** (Imtinan's master dashboard, the owner's "all will be contact"): their own columns move to `crm_speaker_details`; the kind follows the category. Replaces Task 059's separate records. |
| 53 | 10-27 | **The CRM reads the whole system** (Imtinan): everyone invited, requesting, registering or imported in Guests is one linked contact, matched by link or email (reverses 45); a registration updates the contact (the guest wins). |
| 54 | 10-27 | **Several targeted collections per category**, each with a unique name the admin types (Task 057). |
| 55 | 10-27 | **Activity Log, first version**: type, outcome, date, notes and a next reminder; no On Behalf Of, import or reminders yet. Files on an entry since 10-29 (5 files, 5 MB each). |
| 56 | 10-27 | **Follow-up bells** (Imtinan): a bell beside a contact that needs following up, a daily check, settings in CRM Settings. The system's own lines stay out of the admin bell (owner). |
| 57 | 10-28 | **A request enters the CRM only once accepted** (Imtinan), with a one-time cleanup in CRM Settings. |
| 58 | 10-28 | **The FINAL template** (the team): 28 columns in its order, required headings red; the contacts import **only adds** (an email already there is refused, naming who added it); 5,000 rows a file; Received By gone; List Provided By typed. |
| 59 | 10-28 | **Export** of the ticked or filtered rows, in the import's columns (own Export boxes), and an **Export log** of every export in the system. |
| 60 | 10-28 | **A contact is changed through Edit**, with a confirmation listing the changes; no editing in the table; See more read only (the team). Partly reversed by 68. |
| 61 | 10-29 | **Partial import**: the good rows go in, the rest come back as an Excel with an Import problems column; red cells can be fixed and rows deleted in the preview. |
| 62 | 10-29 | **Update contacts by import**, by CRM ID, from the Export's file; an empty cell changes nothing; own box. |
| 63 | 10-29 | **Delete is Archive** (the client): an archived contact keeps its email; a file meeting it says to bring it back (a Bring back button in the preview); a new registration, invitation or accepted request brings it back by itself (the team chose A); Delete permanently from the Archive page. |
| 64 | 10-29 | **A CRM ID is never given again**, even after Delete permanently; contacts and speakers share one numbering (`last_crm_number`). |
| 65 | 10-29 | **History / Source and Source List (File Name) are typed** (revert by migration if the client asks); an import keeps a Relationship Owner who is no admin as written (B). Replaces 42. |
| 66 | 11-01 | **Point of Contact** (Imtinan): an admin who takes over the owner's notifications and the own-contacts scope; Relationship Owner is plain text. Replaces 20 and the owner part of 65. |
| 67 | 11-01 | **Dignitary parties in the CRM** (Imtinan): members linked to their dignitary, the dignitary chosen per person on Invite, an optional Dignitary column in the import ([Task 039](../039-dignitary-parties/TASK.md)). |
| 68 | 11-01 | **Edit in See more** back behind its own boxes (`quick_edit`, `speakers_quick_edit`, with Update): the pencils and the photo upload. |
| 69 | 11-01 | **H.E.'s Office is a channel like the others**: its clearance rule is dropped (see 18); the dashboard's clearance card counts every contact. |
| 70 | 11-01 | **Invitation Channel is the team's list in CRM Settings** (the client): the six channels its first values, with an Arabic name, more added by the team; contacts keep holding a code; CRM locked on. |
| 71 | 11-01 | **Manually Sent**: the team may set Sent when the channel is not CRM (decision 19's manual send, back). |

## Open

| # | Question | Where it stands |
|---|---|---|
| 1 | **The values behind the dropdowns.** v4.1's dropdowns read `#REF!` again (its lookup sheets were deleted, as in v3). The *Field List* and *Status Definitions* sheets give most values (below), and the Contacts and Activity Log header notes give **Outcome** (Accepted, Declined, Pending, Moved Role, Follow-up Needed, Information Only) and most of **Activity Type** (Call, Meeting, Email, Reminder, Minister outreach, Owner reassigned, "..."). Still missing: **Source List** (its note says only "Which list this person came from"). **Industry** is not missing but different: the client's list (Master 07.10, sheet *Industry_Sector*, EG review 08.10, in [`client/CRM_PLAN_V2/`](../../client/CRM_PLAN_V2/)) is not the system's (other industries and names, e.g. "Culture, Sport & Entertainment", "Technology"; Research Institutes & Think Tanks; International Organizations under every industry) | Source List: waiting on the client. Industry: decided 10-21, the system's list as it is (decision 26). Outcome and Activity Type: step 4. Planned as lists an admin keeps in the section's Settings. |
| 2 | ~~**"Accepted opens registration through the CRM."**~~ v4.1 makes acceptance a step before registration: the guest accepts, then the CRM sends the registration email. Our invitation email *is* the registration link today | Decided 10-21: A for the CRM channel, C for the manual ones, C refined (decision 30). |
| 3 | ~~**Relationship Owner**~~ | Decided 10-19: admin accounts with the Prospects permission (decision 20). |
| 4 | ~~**After registration: one record or two.**~~ | Decided 10-21: B, linked, the guest wins (decision 31). |
| 5 | ~~**Prefilled registration (for the client).**~~ An invitation prefills only name, email, phone, company, position and title today; a prospect also holds nationality, country, sector, industry and more. The same question came up in the invitation requests review (2026-10-21, point a), parked to be decided here | Decided 10-21: B, every shared field the form asks for, still editable (decision 32); to confirm with the client. |
| 6 | ~~**Does a sub-category choose the template?**~~ | Decided 10-20: a tag (Task 055 decision 6); templates per sub-category can come later with nothing to undo. |
| 7 | ~~**Is a sub-category required?**~~ | Decided 10-20: required on admin forms when the category has an active list, never on public forms (Task 055 decision 7). The import follows the same rule. |
| 8 | ~~**The template disagrees with itself**~~ on two columns, once *Follow-up sent* is read by its note (it is the Follow-up Owner): Contacts has *Previous category* and no *Last Contact Date*, the Field List the reverse (see *Template findings*) | Decided 10-21: take both (decision 27). Worth mentioning to the client in passing. |
| 9 | ~~**Possible duplicates and merging.**~~ v4.1 flags duplicates (email, mobile, then name) and has the CRM admin merge them before invitations go out. Merging was out of scope | Decided 10-21: A, no merge tool (decision 28). |
| 10 | **Sub-event Invitations** (a system field: "summary of sub-event RSVPs", from a sheet or screen of that name) | Not in the file and not in the system. To ask the client what sub-events are, and leave it out of the first build. |
| 11 | ~~**CRM invitations: the prospect's sub-category and tier, or the collection's?**~~ Since Tasks 055 and 056 a collection carries a sub-category and a tier and gives them to every invitation it makes (each changeable on the invitation afterwards); a targeted collection locks them (Task 057). A prospect has its own of both | Decided 10-21, for now, final after the team's testing: CRM collections without a tier or sub-category of their own (decision 33). |
| 12 | ~~**One tier box or two?**~~ Task 056 added *View tier* on Guests (`guests_listing.view_tier`); the plan gave Prospects its own | Decided 10-21: one box (decision 29). |
| 13 | ~~**Category limits are per admin, not per role.**~~ Decision 22 and *Roles* said "the role's category limits"; the system keeps them on each admin (`admins.category_ids`; a role carries no data scope, `Role.php`) | Wording fixed 10-21 (decision 22, *Roles*): the admin's own categories, through `GuestAccessScope::allowsCategory()`. What an admin sees is the same either way. |
| 14 | ~~**Notifications by email.**~~ Decision 21 says "and by email if they turn it on"; the admin bell (Task 048) has no email channel | Decided 10-21: bell only for now (decision 34). |
| 15 | ~~**Tier 1 declines escalate the same day.**~~ In the client's requirements, left for the CRM by Task 056 (decision 12), not in this plan yet | Decided 10-21: a list in CRM Settings, plus the owner (decision 35). |
| 16 | ~~**Delivered and Opened dates.**~~ *Tracking* shows a date per step, but invitation emails record only yes / no for delivered and opened (`invitation_emails.is_delivered`, `is_open`); SMS records no delivery, WhatsApp only replies. Nominations' `nomination_emails` has the `*_at` columns to copy | Decided 10-21: record the times, as Nominations does (decision 36). |
| 17 | ~~**The name.**~~ "Prospect" is ours (the task's title, 10-13, carried into CRM Plan V1); the client's template says *contacts* (sheet *Contacts*, "the CRM contact"). Suggested: the section **CRM**, each person a **CRM contact** (`crm_contacts`); "Contacts" alone would sit beside "Contact information" and invitations' "Points of contact" | Decided 10-21: CRM / contacts (decision 37). |

**Accepted and registration, the options (open 2)**

| Option | What happens | For | Against |
|---|---|---|---|
| A. **Accepted = registered** (chosen 10-21, CRM channel) | The invitation email stays the registration link. The CRM's Invitation Status reads *Accepted* once the person registers through it (and *Declined* when they answer no) | No new step for the guest; nothing in the registration flow changes | The client's two steps (accept, then a registration email) become one |
| B. Two steps | The CRM's invitation asks *accept / decline* first (an RSVP page); *Accepted* sends a second email with the registration link | Follows the template's wording | A new public page and email, and every invited guest clicks twice |
| C. Manual (chosen 10-21, manual channels, refined: setting it unlocks Invite, it does not send) | *Accepted* is set by hand (accepted by phone, through H.E.'s Office…); setting it sends the registration invitation from the CRM | Fits invitations sent outside the system | A guest invited by the CRM itself still needs someone to set it |

A and C live together: a CRM-channel invitation follows A, a manual channel follows C (decision 30).

**Duplicates, the options (open 9)**

| Option | What happens | For | Against |
|---|---|---|---|
| A. **Refuse on import, flag on name** (chosen 10-21) | Same email or mobile: refused, naming the existing CRM ID (the current rule). Same first and last name with a different email: imported and flagged *Possible duplicate*, for an admin to look at; no merge tool | Nothing is merged by mistake | Two records for one person until someone deletes one |
| B. A merge tool | The flagged pair can be merged: one record keeps both histories | What the template asks | A merge across activities, invitations and history to get right |

## Step 0, done: what the CRM builds on (Tasks 055 to 057)

Built before the CRM, on the guest and the invitation, because the rest of the system needs them too
(2026-10-20 to 10-21, on `feat/crm-foundations`). The CRM reuses them as they are:

| What | Built in | What the CRM takes |
|---|---|---|
| Sub-categories | [Task 055](../055-system-categories/TASK.md) | `sub_category_id` on `prospects`; `App\Support\SubCategoryRule` (the pair must match; required when the category has an active list); the shared select `components/shared/select/sub-categories-select.tsx`; the "No sub-category" filter |
| Company Location, Sector | [Task 056](../056-company-location-sector-tier/TASK.md) | `company_location`, `sector`, with the guest's keys and lists (`App\Support\GuestFieldValues`) |
| Tier | [Task 056](../056-company-location-sector-tier/TASK.md) | `tier`, with the guest's keys, behind the same *View tier* box through `GuestFieldValues::tierVisibleTo()` (decision 29) |
| Targeted collections | [Task 057](../057-request-collections-per-category/TASK.md) | Nothing directly: a prospect who files a request is accepted through one (decision 25) |

What those tasks settled that this plan has to respect:

- **Sub-categories are entered by admins** in Category settings (a tab of their own), not loaded from the
  client's sheet. A switched-off one stays on its records and is no longer offered. Delegate, Workforce and
  Exhibitor (6 of the client's 41) have no category to sit under yet.
- **A sub-category is a tag:** the category still picks the registration form, the emails and the badge.
- **A public category (Media, for one) does not read the invitation link** at registration (Task 055,
  *Deferred*), so someone invited into one is tracked by email only, not by link (decision 10).
- **A collection's sub-category and tier fill each invitation it makes**, changeable per invitation
  afterwards; on a targeted collection they are locked.
- **New columns go last in every export** (the house rule: saved mappings keep their columns).

## Columns (sheet *Contacts*, headings in row 2; row 3 is the client's example and is skipped)

36 columns plus Row Check, and *Last Contact Date* from the Field List (decision 27). Required as the
*Field List* marks them; `*` = Email **or** Mobile. **Same as
registration** means the guest record already has the field with the same values, so the CRM stores it the
same way.

| Group | Column | Required | Stored as | Registration |
|---|---|---|---|---|
| Identity | CRM ID | auto | `crm_id`, made by the system (`C-000001`). Blank = new; filled = **update** that person | CRM only |
| | Prefix | yes | `title_id` | Same |
| | First Name, Last Name | yes | text, as per passport where known | Same |
| | Arabic Name | no | `first_name_ar`, `last_name_ar`, split on the first space | Same; needed for KSA security clearance |
| | Job Title, Company | yes | text (company: full official name, one spelling) | Same |
| | Company Location | yes | `company_location`: `local` / `international` | Same (Task 056) |
| | Email | yes* | unique, trimmed, lower-cased | Same |
| | Mobile | yes* | `+` and the country code | Same (`phone`) |
| | Gender | no | `male` / `female` | Same |
| | Nationality, Country of Residence | yes | country ids | Same |
| | Region | auto | read from the country | Same (`countries.region`) |
| Classification | Sector | yes | `sector`: `public_sector` / `private_sector` | Same (Task 056 cut the list to these two) |
| | Industry, Sub-industry | yes | the registration keys | Same lists, kept as they are for now; the client's list differs (decision 26) |
| | Seniority Level | yes | the registration keys | Same list |
| | Category | yes | `category_id` | Same |
| | Sub-category | yes, when the category has an active list | `sub_category_id`, within the category | Same (Task 055) |
| | Tier | yes | `tier`: `tier_1` / `tier_2` / `tier_3` (Tier 4 removed), admin only, never guest-facing | Same (Task 056): on guests, invitations and collections |
| Relationship & Source | Source List | yes | a list (*Open* 1) | CRM only |
| | List Provided By | yes | text (entity, office or team) | CRM only |
| | Relationship Owner | **yes** | an admin account (decision 20); each change logged | CRM only |
| Invitation | Invitation Channel | yes | `he_office`, `mofa`, `royal_court`, `other_ministries`, `relationship_owner`, `crm` | CRM only |
| | Security Clearance | yes | `not_required`, `not_submitted`, `pending`, `approved`, `not_approved` | CRM only |
| | Invitation Status | yes | `not_sent`, `in_progress`, `sent`, `pending`, `accepted`, `declined` | CRM only |
| | Invitation Sent Date | if sent | date | CRM only |
| | Invitation Sent By | if sent | text (H.E.'s Office, MOFA, EG (CRM) …) | CRM only |
| Follow-up | Follow-up Owner | no | an admin account; blank = the relationship owner. Read under either heading: *Follow-up Owner*, or the Contacts sheet's *Follow-up sent* (decision 27) | CRM only |
| | Last Contact Date | no | date. Field List only; read when the file has it (decision 27) | CRM only |
| | Next Reminder Date | no | date; overdue reads orange | CRM only |
| History | History / Source | no | `tourise_2025`, `external_event`, `manual_invitation_2027`, `other` | CRM only (the guest's `source` is how they registered) |
| | Received By, Previous Engagement, Previous Category, Notes | no | text. Previous Category is on the Contacts sheet only; read when the file has it (decision 27) | CRM only |
| Check | Row Check | no | the sheet's own formula; ignored on import (the server checks again) | not stored |

**Not to be imported (PDPL):** passport and ID numbers, dates of birth, photos. The import has no such
columns, and a file that carries them is refused rather than silently ignored.

**System fields** (filled by the CRM, never imported): Registration Status (read from the system, see *The
system's status*), Registration Link Sent date, Tier Sign-off Reference, Owner History (activity entries),
Possible Duplicate (decision 28), Last Updated / By. Sub-event Invitations is *Open* 10.

The sheet **Activity Log** (CRM ID or Email, First Name, Last Name, Date, Activity Type, Outcome, Logged By,
On Behalf Of, Next Reminder Date, Notes) is imported with it, one row per activity, matched by CRM ID, else
email. Its dates arrive as Excel serial numbers and are read as dates.

The sheet **Tier Sign-off** is the client's approval step (Fahad signs off before import) and is **not
imported**: the Tier on *Contacts* is what lands, and the CRM admin records the *Tier Sign-off Reference*
(e.g. "Tier list v1 · 18 Oct") on the import.

## Invitation channel, clearance and status (decisions 17 to 19)

| # | Date | Decision |
|---|---|---|
| 17 | 10-19 | **Only the CRM channel sends from the system.** For H.E.'s Office, MOFA, Royal Court, Other Ministries and Relationship Owner, the invitation goes out elsewhere and is **recorded** in the CRM (status, sent date, sent by). A recorded invitation stops the CRM sending its own, until the team marks the person *Accepted* (decision 30). |
| 18 | 10-19 | **Clearance gates sending.** H.E.'s Office needs *Approved* before the status can move to *Sent*; *Not Required* is refused for that channel; *Not Submitted* and *Pending* block any send; *Not Approved* blocks it and shows "escalate to Fahad". Enforced on the server, in bulk too. **Changed:** an empty clearance does not block (owner, 2026-10-28); the H.E.'s Office parts are dropped (owner, 2026-11-01: H.E.'s Office is a channel like the others, any clearance allowed). *Not Submitted*, *Pending* and *Not Approved* still block CRM Invite. |
| 19 | 10-19 | **Invitation Status follows the system where the system knows** (replaces open 2 of v3): *Sent* is set when the CRM sends; a manual channel sets *Sent* with date and sender; *Accepted* / *Declined* per decision 30. *In Progress* and *Pending* stay the team's. |

The **Status Definitions** sheet's wording is shown as help beside each value.

## The approach, and what it avoids

**The system's status is read, never stored.** Looked up each time the list is shown, from the link first
(decision 10) and the email for anyone the CRM did not invite. A stored copy would have to be corrected from
four modules every time someone files a request, is invited, registers or is deleted.

**Inviting goes through Invitations.** Prospects are added to a collection by the code "Add people" already
runs (Task 050), which refuses a registered or already invited address. One way of minting invitations.

**A pending request is accepted, not bypassed.** The section links to the request instead, where it is
accepted into a targeted collection (decision 25).

**The template comes from the system.** v4.1's dropdowns are broken like v3's. *Download template* builds
37 columns (decision 27) with working dropdowns fed from the system's own lists (titles, countries, sectors,
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
| **Delivered**, **Opened** | the email provider says so (email only; SMS and WhatsApp skip these steps) | date (decision 36) |
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
- **A public category's registration is matched by email only:** it does not read the invitation link
  (Task 055, *Deferred*), so *Registered* through the link works for private categories.

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
- **Same name, different email:** imported and flagged *Possible duplicate* (decision 28).
- **Not refused:** someone who has already requested, been invited or registered. The preview counts them.
- **With a CRM ID:** the row updates that prospect; an empty cell leaves the field as it was; a registered
  prospect's shared fields are left alone, with a note in the preview (decision 31). An owner change
  is logged as a reassignment.

### Inviting

From any tab, tick prospects and **Invite** (decision 14): choose a **CRM collection** of their category (or
make one: name, category, channel, template, sender, usage, uses, prefill, lock; no tier or sub-category),
then send now or only add. Each invitation copies the prospect's tier and sub-category (decision 33); a
prospect of another category is skipped with the reason.

| Prospect | Invite |
|---|---|
| Not in system | Allowed |
| Channel is not CRM | Not from here: "Record the invitation" (date, sender) instead (decision 17); once marked *Accepted* by hand, Invite sends the registration link (decision 30) |
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
Create, Update, Delete, Invite, Export, Settings, Record History, Audit Trail and **Can own prospects** (who
may be chosen as relationship or follow-up owner). Inviting also needs the Invitations permission. Tier
follows the existing **View tier** box (decision 29), not a box of its own.

**Per category.** The admin's own category limits (`admins.category_ids`, through
`GuestAccessScope::allowsCategory()`; a Super Admin sees all) apply to every part of the section: the tabs,
the list, the counts, the report and the export show only the allowed categories; an import row in another
category is refused; the owner picker offers only admins whose own categories cover the prospect's; a
prospect moved to a category its owner cannot see asks for a new owner.

**Notifications** (decision 21), in the bell only for now (decision 34):

| Event | Goes to |
|---|---|
| Made relationship or follow-up owner (one, or a bulk count) | the new owner |
| Next Reminder Date is today; it has passed (once a day while overdue) | the follow-up owner, else the relationship owner |
| Tracking moves: sent, opened, registered, confirmed, declined | the same |
| A **Tier 1** contact declines | the admins ticked for Tier 1 escalations in Settings, and the owner, at once (decision 35) |
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
| Creating the collection, adding people, sending | Invitations (Task 050) | Add people's body moves into a service; collections already carry a sub-category and a tier (Tasks 055, 056) |
| Tabs, listing, filters, bulk bar | `use-listing-state`, the invitation requests listing | None |
| Sub-category select and rule | `sub-categories-select.tsx`, `SubCategoryRule` (Task 055) | None |
| Company Location, Sector, Tier lists; who sees tier | `GuestFieldValues` (Task 056) | None |
| Export | `TouriseSheetStyle` | New class |
| History, audit trail, notifications | `AuditLog::record()`, `AdminActivityFeed` | A `prospects` feature |

## Cases

1. A prospect files a request after the import: reads Requested on the next load.
2. A prospect is invited from Invitations, not from here: reads Invited all the same.
3. A prospect registers through the CRM's invitation: reads Registered, the guest takes the invitation's
   sub-category, and the Invitation Status reads Accepted (decision 30).
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
19. A prospect is moved to a category its owner cannot see: the move asks for a new owner.
20. An admin limited to Speakers imports a file with a Sponsor row: that row is refused.
21. A prospect opens the invitation, then registers with another email: the owner is notified twice, and
    the journey reads Opened then Registered, through the link.

## Build order

Each step is committed on its own on `feat/crm-foundations`; the branch merges once, when the CRM is final
(owner, 2026-10-21).

0. **Done** (2026-10-20 to 10-21): sub-categories ([Task 055](../055-system-categories/TASK.md)), Company
   Location, Sector and Tier on the guest ([Task 056](../056-company-location-sector-tier/TASK.md)),
   targeted collections ([Task 057](../057-request-collections-per-category/TASK.md)). See *Step 0*.
1. **Import and records.** Tables, settings lists, the template, import with CRM ID update, the table with
   tabs, the record, edit, bulk edit, permissions, audit. Planned in [STEP_1_PLAN.md](STEP_1_PLAN.md) (2026-10-21,
   for the owner's review).
2. **Tracking.** The journey lookup, the column with its steps, filters, funnel tiles, the timeline, links.
3. **Inviting.** The shared minting service, channel and clearance rules, recording manual invitations.
4. **Activity log, follow-up, notifications and the report.** Log activity, owners' reminders and the daily
   check, the owner notifications (the bell learns items addressed to one admin, decision 34), the Activity Log
   sheet, the report.
5. **Export.**

## Out of scope

- Matching to the system by mobile or by name for the system status (name only flags a possible duplicate).
- Merging two prospects (*Open* 9 B).
- The Tier Sign-off workflow inside the system (stays the client's sheet).
- Sub-event invitations (*Open* 10).
- Emailing prospects without inviting them: that is Nominations.
- Any public route (the registration taking the invitation's sub-category and tier is done, Tasks 055 and
  056); the mobile app.

## Template findings (v4.1)

- **Every dropdown reads `#REF!`**, and the Category → Sub-category and Industry → Sub-industry lists
  (`OFFSET(#REF! …)`) do too: the lookup sheets were deleted before the file was shared. The values are
  recovered from the *Field List* and *Status Definitions* sheets, and Outcome and most of Activity Type from
  the header notes. Source List has no values, and the industry hierarchy is the 07.10 master's, which is
  not the system's (*Open* 1).
- **The Contacts sheet and the Field List disagree** (*Open* 8, rechecked 2026-10-21):
  - The Contacts sheet's **Follow-up sent** column carries the Field List's **Follow-up Owner** note
    ("Person responsible for the next follow-up. Blank = the relationship owner."): the same field under
    another heading.
  - The Field List has **Last Contact Date**; the Contacts sheet does not.
  - The Contacts sheet has **Previous category**; the Field List does not.
  - Both count **36 fields**, as the Read Me says: the Contacts sheet has 36 columns plus Row Check, the
    Field List 43 rows (36 plus seven system fields).
- **Dates** in the Activity Log are Excel serial numbers (46309); read as dates.
- **Region** says "Check country" in the example row: the formula's lookup is broken too; the system fills
  it from the country.

## To check before building

- **The dropdown lists** (*Open* 1) before step 1 can validate those columns.
- **`invitations.email` has no index**: add it in step 2.
- **Mixed-case emails:** every match compares lower-cased on both sides.
- **Sub-categories entered on production** before a real import: a row's sub-category must be on its
  category's list, and admins enter the lists themselves (Task 055 decision 4).

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
- 2026-10-21: brought up to date with Tasks 055 to 057, which are build step 0 (done, on
  `feat/crm-foundations`): sub-categories as built (decision 16, *Step 0*; open 6 and 7 closed), Company
  Location, Sector and Tier on the guest (decision 24, the *Columns* rows), targeted collections (decision
  25), branch and merge. v4.1 rechecked: 36 columns plus Row Check, Field List 43 rows, *Follow-up sent* is
  the Follow-up Owner by its note, Outcome and most of Activity Type in the header notes, the client's
  industries differ from the system's (open 1 and 8 narrowed). New open points 11 to 16: CRM invitations'
  sub-category and tier, one tier box or two, category limits per admin, email notifications, Tier 1
  escalation, delivered and opened dates. Open 5 takes point (a) of the invitation requests review.
- 2026-10-21: the owner kept the system's industry list as it is for now (decision 26, from open 1). Source
  List stays as planned: a list admins keep in Settings, the import's preview naming a value not on it.
  Open 8 decided "for now": both versions of the template are read, 37 fields (decision 27). Open 9: no
  merge tool, refuse or flag (decision 28; owner: no invitation has gone out yet, keep it simple). Open 12:
  one tier box (decision 29). Open 13 was wording only: category limits are the admin's own, not the role's
  (decision 22, *Roles*, case 19 corrected). Open 2: no accept step; registering is Accepted on the CRM channel,
  Accepted by hand unlocks the registration link on the manual ones (decision 30). Open 4: linked, the guest
  wins (decision 31). Open 5: prefilled with every shared field the form asks for, still editable, to confirm
  with the client (decision 32), the Arabic name left out (owner). Open 11: CRM collections with no tier or
  sub-category of their own, the prospect's copied (decision 33, for now, final after the team's testing).
  New open 17: the name (prospect, or the client's "contact"). Open 14: bell only for now (decision 34); the
  bell itself needs items addressed to one admin, which it cannot do today. Open 15: Tier 1 declines go at
  once to admins ticked in CRM Settings, plus the owner (decision 35). Open 16: invitation emails record
  delivered, opened and clicked times, as Nominations does (decision 36). Open with the owner: none; with the
  client: Source List values (1), sub-events (10). Open 17: named "CRM", each person a "contact" (decision 37).
- 2026-10-21: step 1 planned in [STEP_1_PLAN.md](STEP_1_PLAN.md), for the owner's review; two questions in it.
- 2026-10-21: the owner answered both: import all or nothing (for now); a backend copy of the industry,
  sub-industry, seniority and gender lists, for the CRM only. Step 1 pieces 1 and 2 (backend) built on
  `feat/crm-foundations`, uncommitted: migrations `2026_10_21_000003` to `000005`, the `crm` boxes, the rules, the
  list, the contact, bulk edit, owners, Source List, history, the import (check, all or nothing, CRM ID updates),
  the template; 27 tests, 1,350 in all, Pint and PHPStan clean. Tier lines stay visible in History to admins
  without View tier (owner: leave as is).
- 2026-10-21: step 1 pieces 3 to 5 built, uncommitted: the admin's CRM section (Contacts with category tabs, tiles,
  search, filters, the contact window, add / edit, bulk edit, delete; Imports with the import page and past imports;
  Settings with the Source List), EN + AR, the `check:rbac` path fixed. Admin `tsc`, ESLint, Prettier, `check:rbac`
  green; `yarn build` green from a copy (the owner's dev server was running). Not seen in a browser: needs the three
  migrations on the local database first.
- 2026-10-21 (night): the team's notes changed the design (decision 38, [STEP_1_PLAN.md](STEP_1_PLAN.md) revision 2), and
  step 1 was reworked to it, uncommitted. Backend: `crm_list_values` (sixteen supporting lists) replaces the Source
  List; `crm_imports` keeps each file's defaults and column mapping, `crm_import_rows` every row as written; the
  contact holds list value ids and owners as text; the rules keep identity and operational checks only; the
  importer maps columns, takes the file's defaults, matches or makes list values (switched-off ones switched back
  on), keeps the old status and sent columns with the row only, and sums up before importing; Settings adds a
  value or switches one off once unused; the `own` box, the owners endpoint, the category scope and the backend
  copy of the registration lists are gone. 29 CRM tests; `composer qa` green (1,352 tests). Admin: the list (a
  filter per list, a tab per Category value), the form, the contact window with *From the imports*, bulk edit,
  Settings *Lists*, the import page (columns, defaults, summary), EN + AR; `tsc`, ESLint on the CRM files,
  `check:rbac` and `yarn build` (from a copy) green. Not seen in a browser: needs the three migrations locally.
- 2026-10-22: the three CRM migrations run on the local `tourise_clean` (owner's go): four empty tables, the 16 list
  value keys and the unique list index in place. Not seen in a browser yet.
- 2026-10-22: step 3 (inviting from the CRM) planned and built ([STEP_3_PLAN.md](STEP_3_PLAN.md), decisions 39
  and 40).
- 2026-10-24: revision 3, the CRM on the system's fixed lists (decisions 41 to 44, the team's request of 10-22),
  planned with the owner and built on `feat/crm-foundations`, uncommitted ([FIXED_LISTS_PLAN.md](FIXED_LISTS_PLAN.md)):
  one migration (`2026_10_24_000001`, empties the CRM's test data); each list matched exactly, nothing created;
  Sub-category under its Category, Sub-industry under its Industry; Region from the country; CRM, Lists keeps the
  team's two lists with Add value; **the category limits are back** (decision 22). Backend `composer qa` green
  (1,369 tests); admin type-check, ESLint, `check:rbac` and `yarn build` (from a copy) green. The seven test sets
  rebuilt with the system's values and checked against the real rules. Migrations `2026_10_22_000002` (photo) and
  `2026_10_24_000001` run on the local `tourise_clean` (owner's go): the CRM tables empty. Not seen in a browser.
- 2026-10-25: step 2 (Tracking) decided with the owner (45 to 50) and built on `feat/crm-foundations`, uncommitted
  ([STEP_2_PLAN.md](STEP_2_PLAN.md)). Migration `2026_10_25_000001` (invitation emails keep their event times and
  bounces) run on the local `tourise_clean`. Backend `composer qa` green (1,381 tests); admin type-check, ESLint,
  `check:rbac`, `yarn build` (from a copy) green. Not seen in a browser.

- 2026-10-26: Titles Delete (decision 51, backend PR #79, admin #74), the last of `feat/crm-foundations`; the
  CRM continues on `crm-foundations-2`. Urgent multiple-use invitation fix on `main` ([Task 043](../043-guest-list-is-the-quantity/TASK.md)).
- 2026-10-27 (Imtinan): the master dashboard and speakers as Speaker-category contacts (52; backend PR #85, admin
  #79), Relationship Owner from the admins and the dashboard as donuts, bars and lines (#88, #82), **the CRM reads
  the whole system** (53; #90, #86), follow-up bells and statuses (56; #91, #87), Guests links open the table
  (#92), fewer dashboard cards (admin #90). The CRM went to `main` (`crm/to-main`, backend #86, admin #80).
- 2026-10-27 (Eissa): Activity Log (55) and the edit form laid out as See more (on `crm-foundations-2`, backend
  #87, admin #81 and #84); targeted collection names (54; backend #93, admin #88); bell gaps (backend #94, admin
  #89: texts, system lines out of the bell, one History line per activity).
- 2026-10-28 (Eissa): Export (59; backend #96, admin #92) and the Export log (backend #98, admin #94); the team's
  first list of fixes on `feat/crm-fixes-improvements` (backend #100 then #110, admin #100 then #108): the FINAL
  template (58), 5,000 rows, the sample's Sub-category following its Category in Excel, Source List renamed, Email
  required, Received By and inline table editing gone, Edit with a confirmation (60), the popup before the
  sample, "added by" on a refused email, the record's origin in History.
- 2026-10-28 (Imtinan): requests enter only once accepted and the cleanup (57; backend #106, #108, admin #106),
  Total contacts and the bell's tip (admin #95).
- 2026-10-29 (Eissa, `feat/crm-fixes-improvements` and `-2`, backend #110, #113 to #117, admin #108, #111 to #116):
  partial import and fixing in the preview (61), Update contacts (62), Activity Log files, Archive (63), CRM ID
  never reused (64), preview polish (problem rows orange, fixed cells green, Delete a row with a confirmation),
  owner kept as written, History / Source and Source List typed (65), the labels in messages (backend #119).
- 2026-10-29 (Imtinan): the dashboard's tracking step from 115 s to 0.4 s at 1,000 contacts (backend #111, index
  migration `2026_10_29_000005`), the form's dropdowns no longer clipped (admin #109), the funnel and the In CRM filter
  removed and "Invited" read "Added" (on `testing` directly).
- 2026-10-29: **release** to `main` (`release/crm-2026-10-29`: backend #116, admin #115; frontend #39), then the
  evening's follow-ups (backend #117 to #122, admin #116 to #119, frontend #40 and #41), and **production** (backend
  `bd169df` with 8 migrations, then the evening's `main`). The final industry list
  the same evening ([Task 062](../062-industry-list-final/TASK.md)).
- 2026-11-01 (Imtinan): Point of Contact (66) and dignitary parties in the CRM (67): backend #123 to #127, admin
  #120 to #122; migrations `2026_11_01_000001` (Point of Contact, moves each owner link to it, drops
  `relationship_owner_id`), `100001`, `200001`, `200002`.
- 2026-11-02 (Eissa, `feat/crm-tasks-2026-11-01`, backend #128, admin #124): Edit in See more (68), H.E.'s Office
  (69), Invitation Channel in Settings (70; migration `2026_11_02_000001`, reversible: contacts on a channel added
  in Settings lose it), Manually Sent (71). `testing` into `main` (backend #129, admin #125); **deployed** the same
  day (5 migrations).

## Before release (critical)

- ~~No per-admin category limits in the CRM~~: **closed by revision 3** (2026-10-24,
  [FIXED_LISTS_PLAN.md](FIXED_LISTS_PLAN.md) section 4). Contacts hold a system Category, and each admin sees and
  writes only the contacts in their own categories, as on Guests (decision 22).
- ~~The team's two lists first~~: **gone**, Source List and List Provided By are typed (decisions 58 and 65).
  Instead, a **new Invitation Channel** goes into CRM Settings before a file names it (decision 70).
- **Upload size:** a 5,000-row import's request body passes 1 MB (nginx's default `client_max_body_size`); 5,000
  rows took about 22 seconds to check and 23 to import on the test database. Check nginx, PHP's `post_max_size`,
  `max_execution_time` and memory with a real file before the first big import ([STEP_1_PLAN.md](STEP_1_PLAN.md),
  *Before deploy*).
- **Roles after each deploy:** the new boxes start unticked: Export and Speakers export (59), the Archive's view
  and delete for both tabs (63), Update contacts by import (62), Edit in See more for both tabs (68), and Export
  log's view and export (feature `export_logs`).

## Definition of Done

- [ ] Code merged to `dev` in backend and admin (with the rest of `feat/crm-foundations`, once the CRM is final)
- [ ] EN + AR translations in the same commit
- [ ] Quality gate green (backend `pint --test` + `php artisan test`; admin type-check + production build)
- [ ] The cases above covered by backend tests, through HTTP
- [ ] Docs updated (this TASK.md, the index row)
- [ ] Roles: the CRM boxes ticked on the roles that need them, after deploy (each role sees its own categories'
  contacts, decision 22)
