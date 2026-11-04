# Task 068: Manually Accepted / Declined, System templates search, empty import files not shown

- **Status:** `in-progress`: built 2026-11-04 on `feat/crm-tasks-2026-11-04`, quality gates green, committed and
  pushed (backend `6017301`, `63c6a6c`; admin `7b75d71`, `2cac99c`, `1f8c9d6`); PRs into `testing` next.
- **Opened:** 2026-11-04
- **Owner:** Eissa
- **Sub-app(s):** backend + admin
- **Branch(es):** `feat/crm-tasks-2026-11-04` in `tourise-backend` (from `testing` `fe2a244`) and `tourise-admin`
  (from `testing` `6e3cf4a`), `--no-track`. Three requests on one branch (owner).

## 1. Manually Accepted and Manually Declined (the team, 2026-11-04)

- **Contacts only** (speakers have no Invitation Channel).
- When the **Invitation Channel is set and is not CRM**, the Invitation Status (form and See more) also offers
  **Manually Accepted** and **Manually Declined**, beside Not Sent, In Progress, Pending and Manually Sent. The
  server allows the same, in Edit selected too. CRM, or no channel, still leaves Sent, Accepted and Declined to the
  invitation.
- **The Status column and the dashboard** read them as **Confirmed** and **Declined**, as Manually Sent reads as Sent
  (the team: "Yes correct"; Tracking already maps a hand-set answer, Task 054 decision 30).
- **Invite:** a Manually Accepted contact with no invitation yet can be invited through the CRM, despite its channel.
  Its channel and its answer stay, so it is still Confirmed. Manually Declined stays refused, and an invited one is not
  invited again.

## 2. A name search on System templates (the team, 2026-11-04)

"Search the list itself, on the page I am on, no over-scoping", name only. The Event, Newsletter and Nomination
template lists already search by name; **Emails, Config, System templates** had none. It now has a search box that
finds a template by its English or Arabic name, as you type.

## 3. Empty import files not shown (the team, 2026-11-04)

The team's example: the Contacts table's **Import file** filter offered "ACP list.xlsx" though no contact from it was
left ("No data").

- A file is **not shown** in the **Import file** filter (Contacts, Speakers, the Contacts dashboard) or in **Past
  imports** only when it is **100% empty**: no contact from it is left, archived ones counting as none. It is shown
  again once one is brought back from the Archive.
- **The Archive page's** Import file filter shows the files with an archived contact, so they can still be found
  and brought back.
- **Nothing is deleted:** the import, its rows and its audit line stay. While a file is not shown, the download of its
  "rows not imported" cannot be reached from Past imports.

## What changed

- **Backend:** `CrmContactValues::MANUAL_STATUSES`; `CrmContactRules` (the status rule); `CrmContactInviter` (Manually
  Accepted passes the channel and "already accepted" checks, and keeps its answer); `AdminCrmImportsController::index`
  (files with a contact left; `archived=1` for the Archive). Tests: Manually Accepted / Declined set by the team, the
  invite after Manually Accepted, the empty import not shown.
- **Admin:** the status lists in the form and See more; EN + AR labels and the status note; the System templates search;
  the Archive's filter asks with `archived`.
- **Not touched:** the bulk edit's status list (it never offered Manually Sent either); mobile; the frontend.

## Quality gate

Backend: Pint, PHPStan, 1,749 tests. Admin: type-check, ESLint, Prettier, `yarn build` (from a copy, the owner's dev
server running), `check:rbac`.

## Log

- 2026-11-04: the three requests explained and decided with the owner and the team (Manually Accepted / Declined
  confirmed by the team's "Yes correct"; the search "name only, no over-scoping"; empty files "not shown", the owner's
  wording). Built on `feat/crm-tasks-2026-11-04`, gates green; committed and pushed on the owner's word, one commit
  per request (backend `6017301` Manually Accepted / Declined, `63c6a6c` empty files; admin `7b75d71`, `2cac99c`,
  `1f8c9d6`).

## Definition of Done

- [x] Decisions made with the owner and the team
- [x] Committed and pushed on the owner's word
- [x] EN + AR translations in the same change
- [x] Quality gate green
- [ ] Merged into `testing`; testing server: pull, `route:cache`, `queue:restart`, admin rebuild (no migration)
- [x] Docs (this TASK.md, the index row, a HANDOFF line)
