# Task 054, step 2: Tracking (plan)

- **Status:** approved and **built 2026-10-25** on `feat/crm-foundations` (backend, admin), uncommitted, with decision
  50 (the shorter journey) taken while building. Backend `composer qa` green (1,381 tests; `CrmTrackingTest` 7);
  admin type-check, ESLint, `check:rbac` and `yarn build` (from a copy) green. Needs migration
  `2026_10_25_000001` (run on the local `tourise_clean`: it only adds columns). **Not seen in a browser yet.**
- **Branch:** `feat/crm-foundations` in `tourise-backend` and `tourise-admin`; then merged into `testing`.
- **Rests on:** [TASK.md](TASK.md) decision 23 (Tracking is the heart of it) and 36 (invitation emails record their
  times), step 3 as built ([STEP_3_PLAN.md](STEP_3_PLAN.md): a contact keeps the invitation it was invited with) and
  revision 3 ([FIXED_LISTS_PLAN.md](FIXED_LISTS_PLAN.md)).

## Decisions (owner, 2026-10-25)

| # | Decision |
|---|---|
| 45 | **Link only, no email matching.** Tracking follows the contact's own CRM invitation and the guest who registered with it (`crm_contacts.invitation_id` → invitation → `guests.code_id`). Nothing is matched by email: one email can belong to another contact (a person invited as a@x.com registers as a.b@y.com while another contact holds a.b@y.com), and office emails are shared. Replaces the email part of decision 10 and of the V1 plan's part 11. A request someone files on their own is not linked, so the **Requested** step drops out. Invite still refuses an email already registered, invited or requested (step 3): a safety check, not Tracking. |
| 46 | **The CRM ID in Guests and Invitations.** A guest and an invitation that came from a CRM contact show "CRM C-000123", linked to the contact. Read through the same link, nothing stored. Shown only to an admin with the CRM box whose categories include the contact. |
| 47 | **Notifications wait for step 4**, when owners become admin accounts and the bell is built. Tracking reads live, so the alerts work from that day on. |
| 48 | **One column.** The contact's status column shows the team's status until the contact has an invitation (Not Sent, In Progress, Pending), then the Tracking step, with its date. No second column to disagree with the first. |
| 49 | **After Registered: Confirmed, Declined, Checked in** (the client's Registration Status names Confirmed without defining it). **Confirmed** when the guest's latest answer to "Will you attend?" is yes: the reconfirmation (`reconfirmed_will_attend`) when given, else the first answer (`will_attend`). **Declined** when it is no (the email's "Not interested" button records no). **Checked in** when the guest is checked in at the event (`checked_in_at`). The guest's own status (Accepted, Pending…) is shown beside it, for information: its names are the team's to edit, so no step depends on them. |
| 50 | **The shorter journey** (owner, while building: the email steps read as too technical for now). **In CRM → Invited → Sent → Registered → Confirmed → Checked in**, with **Declined** where it stops. Delivered, Opened and Clicked are **details under Sent** ("Sent · opened 24 Oct"), shown in the contact's window and used by a filter, not steps of their own. **Not delivered** is a red warning in Sent's place. It reads like the client's own Registration Status (Not started / Link sent / Registered / Confirmed). |

## 1. The journey

Each step is read from the record it names, never typed. The furthest step reached is the contact's Tracking
(decision 50).

| Step | Reached when | Read from | Shown with |
|---|---|---|---|
| **In CRM** | the contact exists | `crm_contacts` | date added, by whom, the import file |
| **Invited** | the contact has an invitation (step 3) | `crm_contacts.invitation_id` → `invitations` | date, the collection, channel, who invited |
| **Sent** | the invitation was sent | its emails (`invitation_emails.is_sent`), or `invitations.is_sent` for SMS and WhatsApp | date, channel; for an email, the details below |
| *Not delivered* | a warning in Sent's place: the email bounced or was rejected, and no copy was delivered | `invitation_emails` (new, as Nominations) | date, the reason |
| **Registered** | a guest registered with this invitation | `guests.code_id` = the invitation | registration date, number, category and sub-category, the email used if it differs |
| **Confirmed** / **Declined** | the guest's latest attendance answer is yes / no (decision 49) | `guests.reconfirmed_will_attend`, else `will_attend` | date of the answer |
| **Checked in** | the guest was checked in at the event | `guests.checked_in_at` | date and time |

**Details under Sent (email only):** delivered, opened and clicked, each with its date
(`invitation_emails.delivered_at`, `opened_at`, `clicked_at`, new). SMS and WhatsApp report none. A later delivery
(Mailtrap retrying) clears Not delivered, as on Nominations.

## 2. The one column (decision 48)

| The contact has | The column shows |
|---|---|
| no invitation | the team's status: **Not Sent**, **In Progress**, **Pending** (as today) |
| an invitation | the furthest Tracking step, e.g. **Sent · 24 Oct** (and "opened" beside it), with the steps as dots |
| a manual channel's answer set by hand (decision 30: **Accepted**, **Declined**) | that answer, until the system knows more: a registration or an attendance answer wins |

The tiles: **All · Not invited** (Not Sent, In Progress, Pending) **· Invited · Sent · Not delivered · Accepted**
(by hand) **· Registered · Confirmed · Declined · Checked in**. Each contact is counted once, at its current step,
so the tiles add up to All; each filters the list.

## 3. The screens

- **The contacts table:** the one column (chip, date, dots), sortable by step.
- **Filters:** by step (several), and two the team asked for: **sent, not opened after N days** (email) and
  **sent, not registered**.
- **The contact's window:** the journey as a timeline at the top, each step with its date and a link to its record
  (the invitation in its collection, the guest's card).
- **Guests and Invitations (decision 46):** a "CRM C-000123" chip on the guest's card and in the invitation's
  details, linking to the contact; only for an admin with the CRM box and the contact's category.
- **EN + AR** for every new label.

## 4. The backend

- **Computed, never stored.** One query adds each contact's step to the list, the tiles and the filters: the
  contact's invitation, its latest email and the latest guest registered with it, through indexes that already
  exist (`crm_contacts.invitation_id`, `invitation_emails.invitation_id`, `guests.code_id`). A stored copy would need
  updating from three modules. Filters are SQL on the same expression, so 20,000+ contacts stay fast.
- **Invitation emails record their times (decision 36),** as nomination emails do (`NominationEmail::recordMailtrapEvent`):
  new columns on `invitation_emails`: `delivered_at`, `opened_at`, `clicked_at`, and `is_bounced`, `bounced_at`,
  `bounce_type`, `bounce_reason` for Not delivered. The Mailtrap webhook fills them; an event already recorded is
  not applied twice. The migration fills the dates once from what each email already holds (`meta.events` keeps
  every event with its time today).
- **The guest and invitation answers** (decision 46) carry `crm_contact` (`id`, `crm_id`) for an admin allowed to
  see it.
- **The contact's answer** carries its journey (each step, its date, the record's id) for the window.

## 5. Tests

Each step reached and shown with its record; the furthest step wins; the email details (delivered, opened,
clicked) under Sent, and none for SMS and WhatsApp; a bounce (Not delivered), then a later delivery; Confirmed and Declined from the first answer and from a reconfirmation; Checked
in; a manual Accepted overtaken by a registration; the filters (by step, not opened after N days, sent not
registered) and the tiles; the webhook filling the new columns once; the CRM ID on a guest and an invitation, and
hidden from an admin without the box or the category.

## 6. Not in step 2

- **Notifications** (decision 47): step 4.
- **Matching by email**, and the **Requested** step (decision 45).
- **Export** (step 5) will carry the same column.

## Open

None. The owner's answers are decisions 45 to 50.

## As built (2026-10-25)

- **Backend:** `App\Services\Crm\CrmTracking`: one SQL expression for the column (list, tiles, filters, sort by the
  journey's order), `journeys()` reading the contacts on screen in three queries (invitation, its emails, the latest
  guest), and `contactFor()` for decision 46. `InvitationEmail::recordMailtrapEvent()` keeps each event's time and
  bounces, as nominations do; the webhook sends invitation emails there (a CC or BCC copy's events are not the
  invitee's). Contacts answer `tracking` (step, date, opened, reached) on each row and `journey` in the window.
  Filters: `tracking` (replaces the old Invitation Status filter), `not_opened_days`, `sent_not_registered`. Guest
  and invitation details answer `crm_contact` beside their data.
- **Admin:** the Status column (the team's status until invited, then the step chip with its date, an eye when the
  email was opened, and the six dots); the tiles, each a click to filter; the filters; the Journey card at the top of
  the contact's window (each step's date, the email details, Not delivered with its reason, the guest's
  registration number, category and status, links to the collection and the guest); the "CRM C-000123" chip in the
  guest's and the invitation's windows, opening `/crm?contact=…`. EN + AR.
- **Tiles count each contact once, at its current step,** so they add up to All.
