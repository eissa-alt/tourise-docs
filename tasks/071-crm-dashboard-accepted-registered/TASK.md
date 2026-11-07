# Task 071: the CRM dashboard's Accepted and Registered tiles

- **Status:** `on main`: merged into `testing` 2026-11-05 (backend PR #166 `5dcc77f`, admin PR #155 `ee6bc4b`) and
  `main` (backend PR #167 `ec3a150`, admin PR #156 `3983afd`); on production by 2026-11-07 (owner). Testing server
  not confirmed.
- **Opened:** 2026-11-05
- **Owner:** Eissa
- **Sub-app(s):** backend + admin
- **Branch(es):** `fix/crm-dashboard-accepted-registered` in `tourise-backend` and `tourise-admin` (from `testing`
  `b552830` / `cfb0898`), `--no-track`.

## The request (the client, 2026-11-05)

On the CRM dashboard filtered on the import file "CRM Invitation Tier1_ File1.xlsx" (Total 97, Sent 79, Accepted 0,
Declined 3, Registered 4):

1. "Accepted should also calculate who registered from the invited in the system as that's considered acceptance,
   plus whoever we mark as accepted manually."
2. "It shows 4 registered for this specific file when only 1 is registered."
3. "On invitation analytics below I need also not delivered and reason." Not in this task (owner: later; it is the
   invitation email status work on hold).

## What it was

- **Accepted** counted the contacts whose latest registration's status is Accepted, the team's approval in Guests.
  The invitation flow puts a registration in Invited (VIP), so it read 0 on production.
- **Registered** counted every contact with a registration. A no on the invitation's form is saved as a
  registration with Attendance Confirmation No, so the file's 3 who declined (C-001995, C-002001, C-002002) counted in
  Declined and in Registered; only C-002015 registered to attend.

## What changed (read only: how two tiles count; no data, no migration)

1. **Accepted = the CRM's Confirmed** (`CrmDashboardBlocks::headline`): Attendance Confirmation Yes with the
   registration Invited or Accepted (registering through an invitation is a yes since 2026-11-05), or Manually
   Accepted, checked in included. Who said no, or whose registration was Rejected or Canceled, stays out. Read from
   the Confirmed column already counted, so the CRM's state is not read twice. Hint, EN + AR: "Registered through
   their invitation, or Manually Accepted".
2. **Registered leaves out a latest answer of no** (the reconfirmation's first); an empty answer still counts.

No filter follows these tiles: only Sent is clickable, and the table's Status filter Registered already shows a no
as Declined.

## Figures (production dump of 2026-11-05 21:48)

| | Whole CRM (348) | Tier1 File1 (97) |
|---|---|---|
| Accepted, before / after | 0 / 1 | 0 / 1 |
| Registered, before / after | 241 / 238 | 4 / 1 |

A self-registration (London Reception, Media) counts as Accepted only with a Yes and its registration Invited or
Accepted; on production none does (RSVP'd or Pending, no answer).

## Quality gate

Backend `composer qa` green 2026-11-05: Pint, PHPStan, 1,790 tests (`CrmDashboardTest` headline test: Accepted = 3
of the Confirmed kinds, a Rejected registration leaves it, a no, also on the reconfirmation, leaves Registered).
Admin: type-check, ESLint, Prettier green (`yarn build` not run: the owner's dev server).

## Commits

- Backend `cb882c1` (point 1), `da39eae` (point 2). Admin `a39f7da` (the hint).

## Next

- On `testing` and `main` 2026-11-05 night. On each server: backend pull + `queue:restart`, admin pull, build and
  restart. No migration.
- 2026-11-07: the owner confirmed it is on production. Testing server not confirmed.
