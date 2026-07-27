# Task 022 — Guest history payload (what an edit actually changed)

- **Status:** `done (code)` — backend + admin committed on `dev` (`0df228e`, `a959703`, `5ae2afb`), all gates green, all three render paths verified in the browser. Not pushed. Prod `php artisan migrate` pending.
- **Opened:** 2026-07-27
- **Owner:** (unassigned)
- **Sub-app(s):** backend + admin (+ docs)
- **Branch(es):** `dev`

## Goal

The guest action history could only say *that* something happened — "Guest updated by admin@altsa.co
at 27/07/2026 14:32". It could not say **what changed**. Give the log a before/after so the event team
can answer "who changed this guest's seat / email / passport number, and what was it before".

Prompted by a comparison against `115-cyan-basecode`, which already had a richer version.

## Scope

- **In:** `previous_payload` / `payload` on `history_logs`; capture in `updateGuest`; the admin renders
  a `Field | From | To` diff; a "No changes in edit" note; the view surfaced as a see-more tab.
- **Out (explicitly not this task):**
  - The other 27 `HistoryLog::create` sites (25 in `GuestsController`, 3 in `GuestLogisticsController`).
    They are state transitions — `Badge Printed`, `Guest Accepted`, `Hotel Assigned` — where the action
    name already says everything. They keep writing bare rows and render as one-liners.
  - Backfill. Impossible: the old values were never recorded. Pre-task rows stay `null` forever.
  - The unlogged write paths: `importGuestsExcel`, the `upload*` methods, `attend()` /
    `guestsSyncOffline()`, `reGenerateSMP()`, the commented-out `RFID Updated`
    (`GuestsController.php:2732`), and `MobileAuthController::updateProfile` — which mutates guest phone
    and avatar and writes no audit row at all. **So "a complete audit trail" is not yet a true claim.**
  - `ip` / `user_agent` capture (cyan has both; see D-4).
  - The N+1 in `HistoryLogsController` (`$this->admin?->email` with no eager load) and its missing
    `applyAdminGuestAccessFilter` data scoping. Both pre-existing, both real — see Open items.

## Log

- 2026-07-27 — opened. Compared 121 against cyan: same base `history_logs` table, but cyan added
  `payload` / `previous_payload` / `source` / `actor_type` / `ip` / `user_agent`
  (`2026_05_06_000004_extend_history_logs_for_payload.php`).
- 2026-07-27 — **coupling question settled** (the thing that decided whether this was portable at all):
  cyan's *renderer* has zero dynamic-forms coupling — `diffActivity()` walks a `Record<string, unknown>`
  and prints raw keys. Only the payload *producer* is coupled, and totally:
  `'payload' => $this->formDataNormalizer->normalize($form, …)` is the `guests.form_data` blob. So the
  idea ports, the backend half is re-authored. CLAUDE.md hard-rule 4 is not engaged.
- 2026-07-27 — backend `0df228e` (P022.1), admin `a959703` (P022.2), see-more tab `5ae2afb` (P022.3).
- 2026-07-27 — dev DB migrated. Verified in the browser: diff table, "No changes in edit" note, modal tab.

## Decisions

- **D-1 — Delta, never a snapshot.** *Promoted to ledger D43.* Only the fields that changed are stored.
- **D-2 — File fields record only that they changed.** *Promoted to ledger D43.*
- **D-3 — `[]` ≠ `null`.** An empty delta is stored as `[]` ("we looked, nothing changed" → the note);
  `null` means unknown (a pre-task row, or an action that never carried an edit) → the plain one-liner.
  Conflating them would make the UI assert something it cannot know about historic rows.
- **D-4 — No `source` / `actor_type` / `ip` / `user_agent`.** Cyan has all four. Skipped: `source`
  collides with the existing `guests.source` column (written as `'website'`); `actor_type` invites
  confusion with the retired `admins.type`; and cyan's own resource never renders `ip` while
  `user_agent` is not even exposed — speculative storage. Capturing registrant IP on the public
  `/complete-data` and `/reconfirm` routes is also a privacy-notice decision, not a code one.
- **D-5 — Field labels are humanised from the key**, not looked up in `web:*`. The existing keys are
  guest-facing form *questions* — `web:will_attend` is "Kindly Confirm Your Attendance" — and
  `web:document_copy` carries a `{{id}}` placeholder that would `console.warn` on every render. Cost:
  field names stay English in AR. A curated `web:field_<key>` map would fix that in its own task.
- **D-6 — Host it in the see-more modal**, not (only) the `/extra/{id}` page. That page is reachable
  by direct URL alone — the listing's see-more button opens the modal — so the feature was invisible.
  Cyan reached the same conclusion and deleted its equivalent page outright.

## Open items / risks

- **The log fires even when nothing changed.** `updateGuest` writes a "Guest updated" row
  unconditionally, so a save that touches nothing still appears in the history (now labelled "No
  changes in edit"). Making the row conditional is a one-line change but alters existing behaviour.
- **`HistoryLogsController::index` has no data scoping.** The guest listing runs
  `applyAdminGuestAccessFilter`; this endpoint runs a bare `where('guest_id', …)->get()`. Today that
  leaks action names to an admin scoped out of that category — **now it would leak the field diff too.**
  Worth closing.
- **No pagination**: `->get()` returns every row, and the modal maps the whole array.
- **Retention**: nothing prunes `history_logs`. Delta-only payloads make this far less urgent than a
  snapshot would have, but it is unaddressed.
- A single unexplained test failure was observed once during this task and did not reproduce across
  five subsequent full runs; the failing test was not captured. `PHASE22_PARKED_TODO.md` §7 records a
  known one-off flake in `SessionsTest > search finds matching sessions` — **possibly a second
  occurrence, unconfirmed.**

## Definition of Done

- [x] Code merged to `dev` in the relevant sub-app(s) — `0df228e`, `a959703`, `5ae2afb` (not pushed)
- [x] EN + AR translations in the same commit — 5 new keys, parity 1760 / 1760
- [x] Quality gate green — backend `pint --test` + `phpstan` No errors + **484 tests**; admin
      `yarn type-check` + `eslint` + `check:rbac` (32/32). `yarn production` not run (no local
      `.env.production`).
- [x] Docs updated (this TASK.md; index row; ledger D43; HANDOFF)
- [x] Mobile contract checked — `routes/api.php` **untouched**; no mobile route reads `history_logs`.
      Only an existing admin-only response body grew (two additive keys), so no
      `mobile/RESPONSE_SHAPE_DELTAS.md` row is needed.
