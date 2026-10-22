# Task 054, step 3: inviting from the CRM (plan)

- **Status:** approved and **built 2026-10-22** on `feat/crm-foundations`: backend `25453f7`, admin `df0f5bc`. Backend
  `composer qa` green (1,359 tests, then the 44 affected after the last change; `CrmInviteTest` 4); admin type-check,
  ESLint, Prettier and `check:rbac` green. Needs migration `2026_10_22_000001`. **Not seen in a browser yet.**
- **Branch:** `feat/crm-foundations` in `tourise-backend` and `tourise-admin` (merged once, when the whole CRM is
  final). The public site is not touched.
- **Rests on:** [TASK.md](TASK.md) decisions 1 to 38 and step 1 as built ([STEP_1_PLAN.md](STEP_1_PLAN.md)). Step 2
  (Tracking) is parked; this step does not need it.

## The idea (owner, 2026-10-22)

**Inviting from the CRM works like accepting an invitation request** ([Task 057](../057-request-collections-per-category/TASK.md),
R1 to R3): a **"Create targeted collection"** button makes one collection per category, and **Invite** asks only for
that collection. The collection decides everything about the invitation; the contact gives only who the person is.

## Decisions this step adds

| # | Date | Decision |
|---|---|---|
| 39 | 10-22 | **The collection decides, as for requests.** A CRM invitation takes the targeted collection's category, **sub-category and tier**, channel, template, sending account and link settings (usage, uses, prefill, lock): this year's, set once when the collection is made. The contact's own Category, Sub-category and Tier are old data, kept as reference as the files wrote them (decision 38), and inviting does not read them. Owner: "for now". Replaces decision 33 (2) and (3) (each invitation copying the prospect's tier and sub-category, and changing with it). |
| 40 | 10-22 | **Add only, or Add and send** (owner, after trying it; first built as "always sends"). Add only makes the invitations, to send later from Invitations. Either way the contact moves to **In Progress**, and to **Sent** with the day only when its invitation is actually sent (by any channel, now or later), so a failed email never reads Sent. Sent By is the admin who pressed Add and send; empty for Add only. No making a collection inside the dialog beyond its link to the same form (decision 14 narrowed). |

## 1. "Create targeted collection" in the CRM

- A button on the CRM page header, beside *Import contacts*, opening the same form as on Invitation Requests
  (`targeted-collection-modal.tsx`): category (only categories without a CRM collection), its sub-category
  (required when the category has a list), channel, template, sending account, tier (with *View tier*), usage
  type, uses, prefill, lock.
- It makes the category's **CRM collection**, named "CRM - <category>" (" (2)" when the name is taken), stamped
  `source = crm`. **One per category**, found by its type and category, never by its name.
- In Collections it gets its own tag, **From the CRM** (AR "من CRM"), and the Source filter offers it. It is edited
  there as a request collection is (its category is fixed).
- Backend: the request version (`RequestCollections`, `TargetedCollectionsController`) takes the source as a
  parameter, so both kinds share one code path; nothing changes for requests.

## 2. Invite

- In the CRM's bulk bar, beside *Edit selected*: tick contacts (or *Select all matching*, up to 2,000), **Invite**.
- The dialog asks only for the **CRM collection** (each shows its channel, email template and sub-category), with
  a *Create targeted collection* link that opens the form above. An admin with category limits sees only
  collections of their categories.
- Each contact the checks allow gets an invitation in that collection and it is **sent** (after the save, as
  Accept does, so a mail failure never undoes an invitation).
- **From the contact:** first and last name, email, mobile, company, job title (as *position*). Not the Title:
  the CRM's is text from the files and the invitation's is the system's Titles list.
- **On the contact:** Invitation Status becomes **Sent**, Sent Date today, Sent By the admin's name, and the
  contact keeps the invitation's id (decision 10). The record shows the invitation as a link
  ("Invitation · TOKEN"), as Invitation Requests shows "Landed in".
- **On the invitation:** `created_via = crm`, the admin who invited (as every invitation since Task 050).
- **History:** one CRM trail entry per click (the collection and how many were invited), and each contact's
  record shows its status change.
- The answer: "N invited", then each contact skipped with its reason.

## 3. Who is skipped, and why (the server checks every contact)

| Contact | Result |
|---|---|
| Channel is not CRM (H.E.'s Office, MOFA, Royal Court, Other Ministries, Relationship Owner) | Skipped: "Invited through <channel>, not from the system" (decision 17). Recording those invitations by hand comes later. |
| Clearance *Not Submitted* or *Pending* | Skipped: "Security clearance is <value>" (decision 18) |
| Clearance *Not Approved* | Skipped: "Security clearance not approved: escalate to Fahad" (decision 18) |
| No email, on an email collection | Skipped: "No email". On an SMS or WhatsApp collection a mobile is enough. |
| No mobile, on an SMS or WhatsApp collection | Skipped: "No mobile number" |
| Already a guest with that email | Skipped: "Already registered" |
| Already invited (any collection, the one-invitation-per-email rule) | Skipped: "Already invited" |
| A pending invitation request with that email | Skipped: "Has a pending request: accept it on Invitation Requests" |
| Status already Sent, Accepted or Declined | Skipped: "Already <status>" |

*Approved* and *Not Required* pass. The contact's CRM Category is not checked against the collection's (decision
38: it is text from the files); the admin picks the collection.

## 4. Permissions

A new CRM box, **Invite** (`crm.invite`), for both the button and Invite. Roles start unticked: tick it for the CRM
team. Making a collection with it is limited to the CRM kind.

## 5. Database

One migration: `crm_contacts.invitation_id` (nullable, the invitation, emptied if the invitation is ever deleted).
`invitation_collections.source` and `invitations.created_via` are text already, so `crm` needs no change.

## 6. Tests

The collection form (one per category, sub-category required, tier only with *View tier*); Invite sends and sets
Sent, Sent Date, Sent By and the link; every skip row in section 3; a mixed selection; the box; an admin with
category limits.

## Not in this step

- Recording an invitation sent by an office (manual channels), and *Accepted* / *Declined* (decision 30).
- Re-inviting someone who declined.
- The journey column and tiles (step 2, parked).
- The per-admin category limits stay off (the CRITICAL note in STEP_1_PLAN.md is unchanged): this step gives the
  invitation a system category, not the contact.
