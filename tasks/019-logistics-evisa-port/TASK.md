# Task 019 — Re-add logistics + e-visa (ported from hci-2026)

- **Status:** `done (code)` — manual QA pending (nothing has been opened in a browser)
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
- **Out:** the February e-visa "operations console" (see Decisions), the tiers module (removed by
  the same trim, not being restored). `sendIssuedVisa` was initially out of scope and was completed
  afterwards as P21 — see Open.

## Log

- 2026-07-21 — opened. Established the trim commits and that `origin/e-visa` (March) is merged into
  hci `main` while `origin/evisa` + `origin/Imtnan` (February) are not.
- 2026-07-21 — P19.1 / P19.2: hotels, rooms, traveling-status — backend + admin.
- 2026-07-21 — P19.3 / P19.4: guest logistics — exports, screen, hotel assignment.
- 2026-07-22 — P19.5: `valid_visa` persistence fix (backend + frontend).
- 2026-07-22 — P19.6 / P19.7: e-visa generation, PDF, admin console.
- 2026-07-22 — P4 (ops console) dropped on evidence; see Decisions.
- 2026-07-22 — P19.8: test suite stopped wiping the dev DB; `composer qa` green 467/0.
- 2026-07-22 — P20: correction pass (ledger D33) — RBAC sweep, the logistics 404, the 403 policy,
  `CategoriesExport`, and the stale agent-facing docs.
- 2026-07-22 — P21: `sendIssuedVisa` completed + `yarn check:rbac` added.

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
   already shipped in `sms_logs` (P18.2). Fixed in P20.1, along with two further long-standing cases
   (`/emails/smtp-configs`, `/gate-scan`) found by sweeping every link instead of spot-checking.
   Six instances total; promoted to ledger **D33** with a `yarn check:rbac` guard.
7. **The logistics screen 404'd on every load.** It called `/admin/guests/...` while the admin axios
   base already ends in `/api/admin`. It shipped that way in P19.4 and was caught only when re-reading
   the code to answer a question — build and type-check both passed. Fixed in P20.3.
8. **`CategoriesExport` printed 20 values under 21 headings** (`map()` omitted `visibility`), shifting
   every column from position 6. Pre-existing; fixed in P20.2.
9. **The test suite wiped the dev database.** `phpunit.xml` had sqlite/`:memory:` commented out, so
   `php artisan test` ran `RefreshDatabase` against the real MySQL dev DB. Fixed in P19.8, together
   with the three long-standing failures — `composer qa` is now green end to end (467/0).

## Open / follow-up

- ✅ **`sendIssuedVisa` — DONE (2026-07-22, P21).** Backend `6219994`, admin `1416537`'s parent.
  Adds `categories.issued_visa_email` + `guests.issued_visa_sent_by`, `EVisaController::sendIssued`
  (GuestEmail with `workflow_value = ON_ISSUED_VISA` -> `SendGuestEmailEvent`, increments the send
  count, stamps sent_at/sent_by in a transaction), `POST admin/guests/{id}/e-visa/send`, the admin
  send action, and the category template picker. Status value is **`sent`**, not hci's typo'd
  `sended`; lifecycle is now null -> in_progress -> issued -> sent. `issued_visa_send_count` /
  `issued_visa_sent_at` are no longer orphans.
- ✅ **Logistics screen 403 — RESOLVED (P20.5).** The guest leg of the `Promise.all` is now tolerant:
  when it fails, `canReadGuest` goes false, the guest-declared fields are hidden rather than shown
  blank, and they are dropped from the PUT so a logistics-only admin cannot null values they were
  never shown. A logistics-only role stays viable; grant both permissions together for the strict
  reading, no code change needed.
- **TypeGate drift.** The logistics page uses `TypeGate` (which resolves via `inferFeatureIdFromPath`);
  sibling guest pages still pass legacy `types` arrays. Worth its own cleanup task.
- ⚠️ **Nothing has been opened in a browser.** Every claim above is type-check / build / phpstan /
  unit-test. The logistics screen is the priority — it shipped 404'ing and has had zero real use —
  and the e-visa **send** action has never been run at all (it emails a real guest).
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
| P19.8 (test suite) | `c9bbdf9` | — | — |
| P20 (corrections) | `ecce5a6` | `621abdb`, `7193f6f`, `1bd50e5`, `436d225` | — |
| P21 (send issued visa) | `6219994` | `1416537` + parent | — |
