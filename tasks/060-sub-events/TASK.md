# Task 060: Sub-events

- **Status:** `in-progress` (Imtinan): built on `feat/sub-events` in the three apps on 2026-11-01, **not merged**
  into `testing` or `main`. Written on 2026-11-02 from her commits (the number is the one they use); **to check by
  Imtinan**, who owns the scope, the decisions and the merge.
- **Opened:** 2026-11-01
- **Owner:** Imtinan
- **Sub-app(s):** backend + admin + frontend
- **Branch(es):** `feat/sub-events` in `tourise-backend` (8 commits), `tourise-admin` (11) and `tourise-frontend` (3)

## Goal

Invite guests to the event's smaller occasions (the London Reception first) and keep their answers: a list per
sub-event built from the guests and the CRM, sending, capacity with a waitlist, and a public RSVP page.

## What is built (from the commits)

- **Backend:** the tables and models, and a `sub_events` permission; the admin API (set up, build the list,
  send, capacity and waitlist, the waitlist position); a public RSVP answered by a link; an Events section and
  filter in the CRM; a London Reception import; Events on the guest, a Sub-event filter on Guests and a
  Sub-events column in the guest export; the sub-event emails in the Email Logs with Mailtrap's events and resend;
  list tiles, Full, office keys with labels; RSVP only. Tests for the admin API, the public RSVP and the London
  import.
- **Admin:** a sidebar link and a Roles hint; the list, the set-up form, the detail with its Guests, Build list
  and Settings; Events in the CRM contact window and in the guest window, with Sub-event and Reply filters; History
  labels for a sub-event added, sent, replied and offered; sub-event sends in the Invitation emails log (type
  filter, with the guest and Cc); EN + AR.
- **Frontend:** the public RSVP page at `/{lang}/sub-events/rsvp/{token}`, the link the backend sends.
- **Migrations:** `2026_11_02_000001_create_sub_events`, `2026_11_02_000002_create_sub_event_invitations`,
  `2026_11_02_000003_create_sub_event_invitation_emails`.

## Log

- 2026-11-01: built and pushed on `feat/sub-events` in the three apps (Imtinan). Not merged.
- 2026-11-02: this record written from the commits (Eissa), for Imtinan to check.

## Open

- **For Imtinan:** the scope and decisions above, and when it merges into `testing`.
- Its first migration shares the `2026_11_02_000001` prefix with Task 054's Invitation Channel list
  (`..._make_crm_invitation_channel_a_team_list`, already on production). The names differ, so both run and in a
  fixed order; nothing to change, only worth knowing when reading `migrate:status`.
- After the merge: `migrate` (3 tables), the `sub_events` boxes in Roles, `route:cache` and `queue:restart` on the
  servers.

## Definition of Done

- [ ] Merged into `testing`, then `main`, in the three apps
- [ ] EN + AR translations in the same commits
- [ ] Quality gate green (backend `composer qa`; admin and frontend `yarn type-check` + `yarn build`)
- [ ] This TASK.md checked by Imtinan and set to `done`; the index row updated
- [ ] Roles: the `sub_events` boxes ticked after deploy
