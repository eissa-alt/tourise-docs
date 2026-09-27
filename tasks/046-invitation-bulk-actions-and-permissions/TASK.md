# Task 046: The collection's bulk actions, and a permission box for each

- **Status:** `done (code)`: merged to `dev` on 2026-09-28 (backend PR #20, admin PR #23), not yet on `main`.
  Owner browser review pending; **the team must be told about the new boxes before this
  reaches production** (see Decisions).
- **Opened:** 2026-09-27
- **Owner:** unassigned
- **Sub-app(s):** backend + admin
- **Branch(es):** `feat/audit-logs-and-invitation-fixes` (renamed from `feat/module-audit-logs`, Task 045)

## Goal

An invitation collection's **More** menu offers three bulk actions: change category, send, extract to
a new collection. The owner reviewed them one by one: make the three dialogs look and behave alike,
turn "Change category" into a general **Update invitations (bulk)** that behaves like the invitation
edit screen, fix what Extract got wrong, and give sending and each bulk action its own box in the role
editor.

## Scope

- In:
  - one shared list and footer for the three dialogs (`components/shared/modals/invitations/bulk-invitations-picker.tsx`)
  - **Update invitations (bulk)**, replacing Change category (bulk), front and back
  - **Send invitations (bulk)** and **Extract to new collection** moved onto the shared list
  - Extract's API: guest language, counts, and the admin's category scope
  - new Invitations permission boxes, and each button checking its own
- Out:
  - **Dignitary Parties' send** stays on `invitations.create` (owner, 2026-09-27). Recorded as a to-do
    under **Open** in Task 039.
  - Labels for the role editor's older actions: only the four new boxes got `perm_action_*` strings, so
    the rest still fall back to their English key names in Arabic.
  - The invitation edit screen's "With form" label is hardcoded English. The new bulk dialog's is
    translated.

## Log

- 2026-09-27: **Send invitations (bulk).** The table was wider than the dialog (the select column
  fell off the right edge), the footer buttons filled the whole width, and "Field is required" floated
  over them. Owner asked for smaller content and buttons, plus whether each invitation was sent and
  how often. `BulkInvitationsPicker` and `BulkDialogFooter` now hold the list and footer for all three
  dialogs: the select circle leads the row, first and last name share a Name column, **Is sent** and
  **Send count** columns were added, the count and "Select at least one invitation." sit on the left,
  and the buttons keep their own size on the right. Every dialog starts clean on each opening (the form
  outlived the dialog, so the old message and selection survived a close). A 422 shows the API's own
  message instead of the word "failed". Admin `dd61464`.
- 2026-09-27: **Update invitations (bulk)** (owner: "should be like the edit form"). Below the list,
  the edit screen's settings: **Category** (with the resend note once one is picked), **Email
  template**, **Change sender** (default account or another) and **With form** (Leave unchanged / On /
  Off). Everything starts at "keep as it is", since the picked invitations can differ, and only what
  is set is sent. Email settings show only for an email collection. Number of uses (a single-use
  invitation cannot change it) and Prefill data (always on) are left out. Admin `d283ff7`.
  - API: `PATCH /admin/invitations/{collection}/update-bulk` replaces `PATCH category-bulk`, which
    updated **whatever ids it was sent**: any invitation of any collection, whatever the admin's
    categories. The new one is limited to the collection and to `scopeToAdminCategories()`, the scope
    the dialog's own list now uses. Absent keys are left alone, `smtp_config_id: null` means the
    default account, an empty request gets "Fill in at least one field to update.", and the email
    settings only reach email invitations (the answer says how many were skipped). One `updated_bulk`
    audit row per save, since a mass update fires no model events. Backend `c40bea7`, 9 tests.
  - A first cut carried a note that SMS and WhatsApp invitations keep their email settings. The owner
    asked why; it could never apply (a collection has one channel, and Extract keeps it), so it went.
- 2026-09-27: **Extract to new collection.** Moved onto the shared list, and:
  - it asked for an email, SMS **and** WhatsApp template, with the email one required, while the API
    only uses the one for the collection's own channel. It now asks for that one only.
  - **Guest language** was required and written onto every moved invitation, so extracting English and
    Arabic guests with "En" turned the Arabic ones English. It is optional now and starts on "Keep
    each guest's language" (owner).
  - the API counted the ids sent, not the invitations moved, for the new collection's total and the
    audit row; used or inactive ones stay behind and are no longer counted. Nothing movable is a 422
    with no empty collection made, and the admin's category scope applies.
  - the title, buttons, counts and the More menu's "More", "Extract to new collection" and "Back to
    collections" were hardcoded English; all translated.

  Admin `d283ff7`, backend `1c0799b` (5 tests, the endpoint's first).
- 2026-09-27: **a box for each action** (owner's list: Send for one invitation; Update Bulk, Send
  Bulk and Extract for the More menu; Delete not needed). Before, sending needed only
  `invitations.view` and Extract borrowed `export`. The role editor reads the catalog from the API,
  so the boxes appear on their own; they got EN + AR labels. Backend `965dfbc` (3 tests), admin
  `658d051`.
- 2026-09-27: gates: backend `pint --test` clean, `php artisan test` 901 passed (17 new), PHPStan
  unchanged at the 6 errors that predate this work (Task 042 records them); admin `yarn type-check`,
  eslint, prettier and `yarn check:rbac` green. `yarn build` not run: the owner's dev server held
  `.next`.

## Decisions

- **Update in bulk behaves like the edit screen** (owner), with every setting starting at "keep".
- **One shared list for the bulk dialogs**, so they cannot drift apart again.
- **Extract keeps each guest's language unless one is picked** (owner).
- **Invitations permissions** (owner, 2026-09-27):

  | Box | Opens | Before |
  |---|---|---|
  | `send` | the row's Send (`PATCH /{id}/invite`) | `view` |
  | `update_bulk` | Update invitations (bulk) (`PATCH /{id}/update-bulk`) | `update` |
  | `send_bulk` | Send invitation bulk (`POST /{id}/send-bulk`), and `POST send-reminder-by-emails-list` | `view` |
  | `extract` | Extract to new collection (`POST /{id}/extract-bulk`) | `export` |
  | ~~`delete`~~ | removed: no route checked it, and nothing in invitations can be deleted | |

- **⚠️ Roles start unticked** (owner's choice), with no migration. After deploy, only Super Admins can
  send, update in bulk or extract until a Super Admin ticks the new boxes on each role. **Tell the team
  before this reaches production**, or sending stops for everyone else.

## Open

- Owner's browser pass over the three dialogs and the role editor.
- `send-reminder-by-emails-list` has no admin caller and matches unused invitations in **any**
  collection by email. It is gated on `send_bulk` now; whether it should exist at all is not decided.
- Dignitary Parties' sending, see Task 039 **Open**.

## Definition of Done

- [x] Code merged to `dev` in the relevant sub-app(s)
- [x] EN + AR translations in the same commit
- [x] Quality gate green (backend `pint --test` + `php artisan test`; admin `yarn type-check` + `yarn check:rbac`; `yarn build` pending)
- [ ] Docs updated (this TASK.md set to `done`; index row updated)
- [x] Mobile contract checked: every route touched is under `/api/admin`; nothing mobile calls them
