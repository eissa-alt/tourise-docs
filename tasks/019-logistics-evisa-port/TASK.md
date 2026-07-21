# Task 019 — Re-add logistics + e-visa (ported from hci-2026)

- **Status:** `done (code)` — manual QA pending
- **Opened:** 2026-07-21
- **Owner:** AI agent
- **Sub-app(s):** backend + admin + frontend (+ docs)
- **Branch(es):** `dev`

## Goal

Bring back the logistics and e-visa feature set that the P5.trim removed on 2026-06-24, modernized
to the conventions this repo adopted afterwards. Source: this repo's own pre-trim code where it
still matched, hci-2026 `origin/main` where hci had moved on.

## Why

`08d542e` (backend) and `e3a0677` (admin), both 2026-06-24, removed hotels/rooms, traveling-status,
guest logistics and e-visa as "unused modules". They are wanted again. Everything landed AFTER the
trim — the boolean cleanup (Task 001), the datetime cleanup (Task 002), the RESTful route cutover +
`admin.can` gating (Task 010), useFetch (Task 009), the P17.4 toggle-switch change — so this is a
re-add plus a modernization, not a revert.

## Scope

- **In:** hotels, rooms (nested under a hotel), traveling-status, per-guest logistics
  (`guest_logistics`), the four logistics exports, the per-guest logistics screen with hotel
  assignment, e-visa package generation + PDF + issued-visa handling, the e-visa admin console,
  and the `valid_visa` registration fix found en route.
- **Out:** the February e-visa "operations console" (see Decisions), `sendIssuedVisa` (see Open),
  the tiers module (removed by the same trim, not being restored).

## Log

- 2026-07-21 — opened. Established the trim commits and that `origin/e-visa` (March) is merged into
  hci `main` while `origin/evisa` + `origin/Imtnan` (February) are not.
- 2026-07-21 — P19.1 / P19.2: hotels, rooms, traveling-status — backend + admin.
- 2026-07-21 — P19.3 / P19.4: guest logistics — exports, screen, hotel assignment.
- 2026-07-22 — P19.5: `valid_visa` persistence fix (backend + frontend).
- 2026-07-22 — P19.6 / P19.7: e-visa generation, PDF, admin console.
- 2026-07-22 — P4 (ops console) dropped on evidence; see Decisions.

## Decisions

Promoted to the ledger as **D32**.

- **`guest_logistics` stayed a separate 1:1 table** rather than folding into `guests`. The initial
  read was that it duplicated ~10 guest columns; it does not. `guests` holds what the registrant
  DECLARED on the join form (`expected_date_of_arrival`, `flight_arrival_time`, `check_in_date`),
  `guest_logistics` holds what operations BOOKED (`arrival_date`, `arrival_time`, `check_in_date`).
  Both legitimately carry `check_in_date`. The pre-trim admin UI labelled the ops side `admin_*` for
  exactly this reason, and those ~24 label keys were still sitting in EN+AR untouched.
- **The February e-visa ops console was NOT ported.** It does not exist on hci `main` — no
  `EVisaOperationsController`, no `deriveGuestState`, no `guest_e_visa_notes`. hci's last e-visa
  commits are 2026-03-03 and the branch was abandoned. It also collides: it drives `e_visa_status`
  with `pending`/`in_process`/`received` while the shipped March lifecycle uses
  `in_progress`/`issued` — two state machines on one column, with `in_process` vs `in_progress` as a
  silent trap.

## Verification

- Backend: `pint --test` passed, `phpstan` **No errors**, `migrate:fresh --seed` clean.
- Admin: `yarn type-check` clean, `next build` **123/123 pages**, EN/AR at parity (1611/1611).
- Frontend: `yarn type-check` clean, `next build` compiled.
- Room inventory (assign / re-assign / unassign) exercised against the database.
- All four logistics exports + the visa export smoke-tested on a seeded guest.
- **Mobile contract: unaffected.** Every new route is `/admin/*`; nothing was removed or renamed and
  no `Mobile*` resource or controller changed. No mobile notice required.

## Defects found and fixed (none of these were the task)

1. **`valid_visa` was silently discarded on every registration.** The join form collects it from
   foreign nationals and types it, but the backend had no column, no fillable entry, no validation.
   Fixed in P19.5 as a nullable boolean (Task 001 Track A), frontend converted to match.
2. **Room inventory leaked.** `assignHotel` decremented `rooms.remaining` unconditionally, so
   re-assigning a guest never returned the old room — a hotel drifted toward phantom occupancy.
   Now releases the old room first, refuses a room at `remaining = 0`, validates the room belongs to
   the hotel, and runs in a transaction.
3. **`GuestsExportFlights` exported 20 blank columns.** It read `$guest->admin_*` fields that had
   moved to `guest_logistics` before the trim; the sheet looked right and was empty. Repointed.
4. **The visa PDF contained placeholder text.** `visa-document.blade.php` rendered the literal
   strings `contact-email` / `contact-phone` under the email/phone headers — in a document sent to
   an embassy.
5. **Every e-visa admin endpoint 404'd.** The admin axios base already resolves to `/api/admin`, so
   ported URLs became `/api/admin/e-visa/...`.
6. **`inferFeatureId` first-match-wins**, three times: rooms live under `/hotels/[hotel_id]`,
   logistics under `/guests/[slug]`, and e-visa needed its own rule. Each needs its specific rule
   ordered BEFORE the broader one or the page gates on the wrong feature — the same bug class
   already shipped in `sms_logs` (P18.2, still open).

## Open / follow-up

- **`sendIssuedVisa` is not ported.** hci `main` emails the issued visa to the guest via a
  `GuestEmail` with `workflow_value = 'ON_ISSUED_VISA'`, increments `issued_visa_send_count`, stamps
  `issued_visa_sent_at` and sets `e_visa_status = 'sended'`. `issued_visa_send_count` and
  `issued_visa_sent_at` exist here with casts, and the console renders a send-count column, but
  **nothing writes them**. Kept deliberately (this is a basecode; the columns will be wanted).
  Missing prerequisites: `categories.issued_visa_email`, `guests.issued_visa_sent`,
  `guests.issued_visa_sent_by`, and the `ON_ISSUED_VISA` workflow value.
- **Logistics screen 403 fragility.** It loads the guest (gated `guests_listing,see_more`) and the
  logistics record in one `Promise.all`, so an admin holding `guest_logistics` but not `see_more`
  fails the whole load instead of degrading. Needs a policy call on how `guest_logistics` is granted.
- **TypeGate drift.** The logistics page uses `TypeGate` (which resolves via `inferFeatureIdFromPath`);
  sibling guest pages still pass legacy `types` arrays. Worth its own cleanup task.
- Manual QA: create a hotel → add rooms → assign a guest → set dates via the masked input → export
  accommodation/flights → generate an e-visa package → upload an issued file. Verify RBAC by logging
  in without each new feature and confirming the sidebar link and the page gate agree.

## Commits

| Phase | Backend | Admin | Frontend |
|---|---|---|---|
| P19.1 / P19.2 | `303c629` | `8641f65` | — |
| P19.3 / P19.4 | `0ed06f3` | `01764ab` | — |
| P19.5 | `0ea04fb` | — | `b0e7e49` |
| P19.6 / P19.7 | `89f1673` | `83ba223` | — |
