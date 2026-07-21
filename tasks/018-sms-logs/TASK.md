# Task 018 — SMS logs (guest + invitation)

- **Status:** `done` (code) — manual QA pending
- **Opened:** 2026-07-21
- **Owner:** —
- **Sub-app(s):** backend, admin
- **Branch(es):** `dev`

## Goal

Give SMS the same observability email already has: read-only **Guest SMS** and **Invitation SMS** log pages
under the Logs section, mirroring the guest/invitation email logs. See ledger **D31**.

## Scope

- **In:** new `sms_logs` RBAC feature (`view` / `export`); `guest_sms` + `invitation_sms` each get a
  controller / resource / export; routes `GET admin/guest-sms-logs(/export)` + `admin/invitation-sms-logs(/export)`
  behind `admin.can:sms_logs`; super-gated admin pages under `/logs/guest-sms` + `/logs/invitation-sms` on the
  shared Track-2 listing stack; sidebar links beside the email logs; `sms_template_name` exposed on the
  invitation resource; EN/AR (`guest_sms`, `invitation_sms`, `template`).
- **Out:** delivered/open/click columns (SMS has no such tracking); a unified/combined SMS log page (kept
  split guest vs invitation to match the email logs); automation SMS log (guest-backed → already lands in
  `guest_sms`).

## Log

- 2026-07-21 — built both SMS log stacks (backend + admin) mirroring the email logs; added the `sms_logs`
  permission + routes + sidebar links; committed backend `34e09e7`, admin `8b0960f`; pushed to `origin/dev`.

## Decisions

Durable ones promoted to ledger **D31**. Task-local: SMS `is_sent` is a real boolean (email logs store
`yes`/`no` strings) so the badge + `is_sent` filter are boolean-aware; Guest SMS shows the Workflow column,
Invitation SMS shows Usage status/type (matching their email twins).

## Definition of Done

- [x] Code merged to `dev` (backend + admin)
- [x] EN + AR translations in the same commit
- [x] Quality gate green (backend `pint --test` + `phpstan`; admin `yarn type-check` + eslint)
- [x] Docs updated (ledger D31; this TASK.md; index row)
- [x] Mobile contract checked — new admin-only endpoints, `mobile/*` untouched
- [ ] Manual QA: send SMS on a flow, confirm rows appear in the right log + export works
