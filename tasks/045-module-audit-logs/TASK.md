# Task 045 — Audit logs for every module

- **Status:** `in-progress`: titles + invitations built, gates green, merged to `dev` on 2026-09-28 (backend PR #20, admin PR #23), not yet on `main`. The blueprint below is now measured rather than predicted.
- **Opened:** 2026-09-23
- **Owner:** —
- **Sub-app(s):** backend + admin
- **Branch(es):** `feat/audit-logs-and-invitation-fixes` (was `feat/module-audit-logs`) in `tourise-backend` + `tourise-admin`, off `dev`

## Goal

The team asked for logs on **invitation collections** — created by whom, when, sent by whom. The
owner widened it: with many admins working the system until the event, every module needs a record of
who did what. Depth chosen (owner, 2026-09-23): **who did what *and* what changed** — field-level
before/after, not just an action name.

## The finding that reshapes the request: it is forward-only

None of what the team asked for exists, and none of it can be recovered:

- `InvitationsCollectionController` writes **no log rows of any kind**.
- `invitation_collections` has **no `created_by` / `admin_id` column** — it stores `collection_name`,
  `usage_type`, `fill_mode`, `total_invites`, `email_template_id`, `category_id`, `timestamps`. "When"
  exists; "who" was never written.
- `invitation_emails` records delivery (`sent_at`, `is_delivered`, `is_open`, `is_clicked`) but
  **never which admin pressed send**. The same is true of all six delivery tables.

So existing collections will read "—" for creator, permanently. **Tell the team this before they see
the UI**, or they will read the blanks as a bug.

## What exists today

Three families, doing genuinely different jobs. Only the first is an audit trail.

| Family | Tables | Actor? | Field diffs? |
|---|---|---|---|
| **Audit** | `history_logs` (guests + invitation requests), `seating_audit_logs` (seating) | `admin_id`; seating also snapshots `actor_name` / `actor_role` | only `history_logs`, and only since task 022 |
| **Delivery** | `guest_emails`, `guest_sms`, `guest_whatsapps`, `invitation_emails`, `invitation_sms`, `invitation_whatsapp` | **none** | n/a |
| **Security / ops** | `login_attempts`, `badge_print_logs` (has `admin_id`), `login_authentication` (misleading name — an OTP/token store, not a log) | partial | n/a |

**Admin attribution exists in 4 places out of 46 permission features** — guests, invitation requests,
seating, badge prints. There is **no audit coverage at all** for invitation collections, categories,
email/SMS/WhatsApp templates, admins & roles, sessions, workshops, publications, media center, hotels,
gates, areas, newsletters, automations, app config, dignitary parties or meeting rooms.

## Scope

- **In:** one generic audit table; a single write path; a per-record history panel and a per-module
  trail, both reusing one From/To renderer; an export of the trail.
- **Out:**
  - The six delivery tables and `login_attempts` / `badge_print_logs` — different axis, they stay.
  - `history_logs` — production data, guest-facing timeline, already rendered. **Not migrated.** It
    keeps serving guests and simply stops growing for new modules.
  - Backfill of any kind. There is nothing to backfill from.

## Design (built)

**One table, not one per module.** `audit_logs`, polymorphic:

- `admin_id` (nullable, `nullOnDelete`) **plus `actor_name` / `actor_role` snapshots** — copied from
  the `seating_audit_logs` precedent, so a row still reads after an admin is deleted.
- `feature` + `action` — taken straight from `admin.can:<feature>,<action>`, so the taxonomy stays in
  step with permissions instead of being a second list to maintain.
- `subject_type` + `subject_id` + `subject_label` (label snapshotted, so a deleted collection still
  names itself).
- `previous_payload` / `payload` — **deliberately the same column names and JSON shape as
  `history_logs`**, so one renderer serves both.
- `route`, `method`, `ip`, `created_at`.

Indexes: `(subject_type, subject_id, created_at)`, `(admin_id, created_at)`,
`(feature, action, created_at)`, `(created_at)`.

**How it gets written.** "Who did what" and "what changed" live at two layers and neither alone has
both: the permission middleware knows actor + module + action (it is already on **390 routes / 46
features**, 210 of 267 write routes) but not what changed; Eloquent model events know the exact diff
but not the module, and have no actor in queued or console context. So: `EnsureAdminPermission`
publishes actor/feature/action into a request-scoped context, and an opt-in `Auditable` model trait
writes the row enriched with it.

**Opt-in per model, not global.** Auditing all 78 models would log pivot tables, notification
recipients and the log tables themselves — an audit of the audit log.

**PII rules are ported, not reinvented.** `GuestsController::guestChangeDelta()` already solved this:
only changed fields, never a snapshot; file fields recorded as `'[file]'` so private-disk paths never
reach a plain JSON column (ledger D14). This is also why **Spatie `laravel-activitylog` was rejected**
— it logs full dirty attributes by default and would undo that decision, on top of being a new
dependency.

**Reading it is itself a disclosure channel** — new feature id, Super-Admin by default, the way
`guests_listing,see_more` already gates guest history.

## Why one table rather than one per module

- **Sharding saves nothing.** 46 tables hold the same rows as 1 — same bytes, same inserts. It only
  scatters them.
- **It kills the questions that motivated the task.** "What did admin X do last Tuesday" is one
  indexed query against one table, and a 46-way `UNION` against many — one that breaks every time a
  module is added.
- **The repo already decided this.** The migration that linked invitation requests into `history_logs`
  (`c90e0cd`, 2026-09-05) argues it in its own comment: *"Same table rather than a second one: there is
  one idea of 'what happened to this record', and splitting it would mean two screens that have to be
  read together to answer one question."*
- **`history_logs` also shows the failure mode of the alternative** — it grew a second nullable FK for
  invitation requests, and this task would have added a third. Polymorphic `subject_type` /
  `subject_id` ends that, and a new module then costs **zero migrations**.

## Capacity — 40K guests, now to 23–25 March 2027

The owner's concern was exponential growth. It is **linear**: rows come from admin actions, bounded by
headcount and hours, and nothing generates audit rows from audit rows.

- Admin lifecycle writes: 40,000 × 8–20 ≈ **320K–800K rows** over ~6 months.
- Event-night, 23–25 March: check-in / check-out / food check-in ≈ 120K–200K, plus seat assignment
  ≈ 40K–200K — **~300K rows compressed into three days**. (`guests.check_in_count` exists, so repeat
  scans are expected: that is a floor.)

Roughly **1–1.5 GB** with indexes — a small MySQL table, answering in single-digit milliseconds.

**The volume control is the allowlist, not the table count.** Event-night telemetry must never enter
the audit table: `checked_in_at` / `_by`, `checked_out_at` / `_by`, `food_checked_in_at` / `_by`,
`check_in_count`, `seat_number`. None of them answers an accountability question — `checked_in_by`
already holds the answer, and seat moves have `seating_audit_logs`. Excluding those seven fields
removes most of the March spike. This is the same warning `guestChangeDelta()` carries: *the Seating
Plan Manager writes through the guest endpoint on every seat drag.*

**The structural hedge is partitioning, not sharding** — MySQL native partitioning by month on
`created_at`. Queries stay single-table, the planner touches only relevant partitions, and archiving
becomes `DROP PARTITION` (instant) rather than a `DELETE` of 300K rows.

## Blind spots — writes that bypass Eloquent events

A model observer sees none of these; they would log **nothing, silently**:

- **4 mass updates**, including `InvitationsCollectionController.php:161` —
  `Invitation::where('invitation_collection_id', $id)->update([...])`, a bulk update **inside the very
  module the team asked about**.
- **2 mass deletes** (`AdminMeetingRoomController`, `MobileNotificationController`).
- **24 raw `DB::table` writes** — 8 in `AuthController`, 6 in `GuestsController`.
- **Queued jobs** (`SendNewsletterCampaign`) run with no auth context; the actor is null unless passed.

Each needs converting to a model-level write or an explicit manual log call. **This is what makes
"every module" a project rather than a trait drop-in**, and it belongs in any estimate.

## Pre-existing findings (found while scoping; not caused by this task)

**1. `history_logs` payloads are double-encoded by one of its two writers.**
`AdminInvitationRequestsController::logRequestAction()` passes `json_encode($previous)` into columns the
`HistoryLog` model already casts as `'array'`, so Laravel encodes again and the DB holds JSON wrapped in
a JSON string. `GuestsController` passes raw arrays — correct. Two writers, two conventions, same
columns.

> **Do not "clean up" the `json_decode` in `AdminInvitationRequestsController::history()`.** It is a
> deliberate compensation and the only reason the request-details modal renders correctly. Removing the
> writer's `json_encode` *alone* makes that reader call `json_decode()` on an array → PHP 8.2 TypeError
> → 500 on the modal.

The latent half: `HistoryLogsResources` returns the cast value raw, so a double-encoded row reaching it
yields a **string**, and the admin renderer's `Object.keys(log.payload)` on a string produces one
From/To row per character.

**2. `invitation_requests.guest_id` is a dead column — and is the only thing keeping (1) latent.**
`logRequestAction()` sets `'guest_id' => $invitationRequest->guest_id`, which would pull these rows into
the guest history endpoint. Nothing populates it: line ~284 reads `$result['guest_id'] ?? null` and
`acceptAsInvitation()` never returns that key, because accepting mints an invitation and *"never creates
a guest directly."* The `?? null` is a vestige of an older flow.

> **Push back on anyone proposing to populate that column before (1) is fixed.** It looks like a
> harmless improvement and it activates the rendering bug.

**Decision (owner, 2026-09-24): leave both as they are.** No user-visible impact today, and a reader
tolerant of both shapes would be the dual-code-path / legacy-fallback logic `CLAUDE.md` forbids. Fix
inside this task, which touches those columns anyway — a correct fix is three coupled parts: writer +
reader + a backfill of `history_logs WHERE invitation_request_id IS NOT NULL`, written since 2026-09-05.

## The team's original ask — answered (2026-09-26)

Both were **columns and actions, not just log rows**:

- **`created_by` on `invitation_collections`** — a column, because the list is filtered and sorted by
  it; reconstructing it from a log table on every query would be the wrong shape. Stamped in the
  model's `creating` hook rather than at each of the three creation sites (the invitation form,
  extract-bulk, and the dignitary service), so a fourth cannot miss it. Shown as **Created by** on the
  collections listing.
- **"Sent by"** — both send paths now record: `sent` for one invitation, `sent_bulk` for a selection
  (one row for the action, not one per recipient). The six delivery tables record that a message went
  out and what happened to it, but never which admin caused it.

**Still forward-only.** Collections made before the column exists read "—" for ever.

## What changed while building (this supersedes the design above where they disagree)

Five decisions moved between the plan and the code. They are recorded here rather than edited into the
design above, so the reasoning for each is not lost.

1. **Per-module permissions replaced the global `audit_logs` feature** (owner, 2026-09-25). Each module
   grants **`record_history`** (one record's history) and **`audit_trail`** (the module's whole trail)
   separately, and both are distinct from `see_more`, which opens the record. The owner wanted full
   per-module control. The global feature was removed with its cross-module endpoint — which also
   removed an Export checkbox that granted nothing.
2. **A popup, not a page.** `/audit-logs` was built, then deleted at the owner's request. The trail
   opens from each module's toolbar and hits `GET /admin/<module>/logs`.
3. **`subject_type` / `subject_id` are nullable.** An export is audited and has no single subject — it
   is of the list, not of one record. Changed in the migration before it was committed.
4. **Exports are logged.** The trait cannot see them (nothing is written, so no model event fires), so
   the controller calls `AuditLog::record()` directly. Exporting the *trail* is logged too, with
   `scope: audit_trail` to keep it apart from exporting the module's own data.
5. **The action filter is derived, not declared.** The trail returns the actions that module has
   actually recorded, read before the action filter is applied. Titles are blocked and never deleted,
   so a fixed list offered a `Deleted` filter that could only return nothing — and a module that later
   logs a send or a bulk update needs no change to have it appear. Unknown actions fall back to a
   humanised label, so a new one is legible before its translation exists.

**Guests are not part of this.** They stay on `history_logs`, including their exports (owner,
2026-09-25).

## Blueprint — what module 2 costs

Six touch points, **no migration, no new table, no schema decision**. The action filter, the From/To
renderer, the export and the permission wiring all follow.

| # | Where | Cost |
|---|---|---|
| 1 | The model — `use Auditable;` + `protected string $auditFeature = '<feature>';` | 2 lines |
| 2 | `AuditLogsController` — three wrappers delegating to `featureTrail` / `featureTrailExport` / `subjectLogs` | ~12 lines |
| 3 | `routes/api.php` — `/logs`, `/logs/export`, `/{id}/logs` under the module's prefix | 3 lines |
| 4 | `AdminPermissions` — add `record_history` + `audit_trail` to the feature | 1 line |
| 5 | The listing — two permission checks, the history button, `AuditTrailButton`, two modals | ~25 lines, mirrors titles |
| 6 | *Only if it stores ids* — add the field to `CATEGORY_ID_FIELDS` so they read as names | 1 line |

Two notes for whoever does it:

- **Audited models must not bypass Eloquent.** `Model::where(...)->update()` and raw `DB::table()`
  writes fire no events and log nothing, silently. The inventory is in *Blind spots* below.
- **Step 2 is collapsible.** Those three wrappers only bind a feature name and a model class; a
  route-level `->defaults('feature', '<feature>')` plus a feature → model map would reduce them to two
  entries. Left explicit for the first module — fold them when they start to feel like boilerplate.

### Measured against module 2 (invitations, 2026-09-26)

The six steps held: no migration for the audit table, no new table, and the action filter, renderer,
export and permission wiring all followed. **Two things the checklist did not predict:**

1. **Bulk-created models need `$auditEvents`.** A collection is minted with all of its invitations in
   one `saveMany()`, which would have written hundreds of identical `created` rows for one click. The
   trait grew a per-model event opt-out; invitations record `updated` and `deleted` only.
2. **Exclusions are per-model security work, not a checklist line.** Titles needed none. Invitations
   needed `invitation_token` kept out — it redeems the invitation, and the trail is readable by anyone
   with `audit_trail` — plus the send counters, which move on every send and answer nothing.

**What cost more than the six steps:** the module's own bypasses. Four actions wrote nothing until
they were logged explicitly — the bulk category change and extract-to-collection (mass updates), and
both send paths (which write no model at all). Budget for that per module; it is the real variable,
not the wiring.

Step 6 generalised on the way: a single `CATEGORY_ID_FIELDS` set became `AuditLabels`, a column → model
map that resolves any referenced id to a name at read time.

## Log

- 2026-09-23 — opened. Team asked for invitation-collection logs; owner widened to every module and
  chose the **who + what changed** depth. Survey of existing logging done; the forward-only finding
  surfaced and is the headline.
- 2026-09-24 — one-table-vs-per-module settled in favour of one table, with the capacity math for 40K
  guests to March 2027 and the allowlist as the volume control. The two `history_logs` findings
  recorded and deliberately left unfixed. **Put on hold by the owner before any code, branch or
  schema.**
- 2026-09-24/26 — built on titles: `audit_logs`, the `Auditable` trait, `AuditLog::record()` as the
  single writer, the record-history panel, the module trail popup and its export. Titles also gained
  the **See more** it never had, and the listing was fixed along the way — two boolean columns were
  blank on every row (no render, and React draws a boolean as nothing), two headers were raw column
  names with no Arabic, a Categories column was added, and listing filters gained `multiselect`,
  reusing the forms' `CheckboxDropdown`. 16 tests. Backend `d8bd2b7` + `96b9e46`, admin `5172c93` +
  `bdbd2d5`, on `feat/module-audit-logs` in each repo — **not merged to `dev`**.
- 2026-09-26/27 — **module 2: invitations + collections**, both under the `invitations` feature.
  `invitation_token` and the send counters excluded; no per-invitation `created` rows; the four
  previously-silent actions logged (bulk category change, extract-to-collection, `sent`, `sent_bulk`)
  plus all three exports. `created_by` added to collections, answering the team's first question, and
  the send logging answering the second. **A collection stopped rewriting its invitations**, and what
  it no longer sets — category, email template, SMTP override — is editable on the invitation instead.
  `AuditLabels` resolves ids, tokens and parent collections at read time for both the screen and the
  sheet. Found and fixed on the way: a single-use invitation could have its number of uses raised,
  turning one guest's personal link into a shared one. 13 tests; 882 total. Backend `4dece91`, admin
  `3fb9632`.
- 2026-09-27: branch renamed `feat/module-audit-logs` → `feat/audit-logs-and-invitation-fixes` in
  both repos (owner), since it also carries the invitation import work (admin `fdec832`, backend
  `92e0554`), and pushed under the new name. The old name is still on GitHub, three commits behind. The
  owner merges the whole branch to `dev` once the remaining work is done.
- 2026-09-28: **merged to `dev`** (backend PR #20, admin PR #23) with everything else on
  `feat/audit-logs-and-invitation-fixes`, after merging `origin/dev` in (the Sponsors / Speakers
  dashboards; the only conflict was keys appended to `translations/{en,ar}/web.json`, both kept). The
  merged backend `dev` passes 924 tests. Not on `main` yet. See Sequencing for Task 041.

## Decisions

- **Depth: who did what + what changed** (owner, 2026-09-23) — field-level diffs, not an action spine.
- **One table, polymorphic** (2026-09-24) — sharding saves no storage and costs the cross-admin
  queries that motivated the task; consistent with the `c90e0cd` precedent.
- **Volume is controlled by the field allowlist**, with monthly partitioning as the hedge. Event-night
  attendance and seating fields are excluded.
- **No Spatie `laravel-activitylog`** — new dependency, and its default full-attribute logging would
  reverse the deliberate no-snapshot PII decision.
- **`history_logs` is not migrated or absorbed.**
- **The two pre-existing findings stay unfixed** until fixed properly here (owner, 2026-09-24).
- **`record_history` and `audit_trail` are per-module and separate** (owner, 2026-09-25), replacing the
  global `audit_logs` feature.
- **The trail is a popup per module**, not a cross-module page (owner, 2026-09-25).
- **Exports are audited**, including the trail's own export (2026-09-25). Remove the latter if it reads
  as noise — it is one row per export, not a loop.
- **Offered actions are derived from the data**, not declared per model (2026-09-26).
- **A collection no longer writes to its invitations** (owner, 2026-09-26). Its copy of the shared
  fields is what reporting and exports read; sends read each invitation's own. The two can therefore
  diverge, with nothing to reconcile them — the form marks each field In sync / Out of sync / Not
  applied so it is visible rather than silent. Channel is read-only there, and on the invitation, since
  templates are channel-specific and a switch would strand them.
- **Secrets are resolved, never stored** (2026-09-26). `invitation_token` is read for the screen and
  the sheet and written to no audit row: it redeems the invitation, and a stored copy would be a
  working credential in a table that outlives the record.
- **Per-module trails are scoped** (2026-09-27). The trail opened from one collection shows that
  collection and its invitations — rows, action filter and export alike — not the whole module.

## Sequencing

Recommended **after task 041** (security port wave 1 — still `todo`, 0/23, no branch). This feature
copies PII into a second table, and 041 exists to close disclosure holes; landing it first widens
exactly the surface 041 is meant to shrink.

**What actually happened:** the titles work was built first, on its own branch and not merged. The
recommendation stands for the **merge**, not the build — 041 should land before this reaches `dev`,
or the two should be reviewed together. The exposure here is narrow while it is one low-risk module
(titles carry no PII), and grows with every module added.

**Then (2026-09-28):** the owner merged it to `dev` before task 041, together with the invitations
module and the work of tasks 042, 043, 046 and 047 on the same branch. So the second copy of
invitation data in `audit_logs` is on `dev` while 041 is still `todo`; 041's review should include it.

## Definition of Done

- [x] Code merged to `dev` in the relevant sub-app(s)
- [ ] EN + AR translations in the same commit (if any user-facing strings)
- [ ] Quality gate green (backend `pint --test` + `phpstan` + `php artisan test`; admin `yarn type-check`
      + `yarn build` + `yarn check:rbac`)
- [x] **Module 2 onboarded**, proving the blueprint above — invitations + collections (2026-09-26)
- [ ] Retention / pruning policy decided and implemented, not deferred
- [ ] Eloquent-bypass list above either converted or explicitly logged
- [ ] Team told the data is forward-only, before they see the UI
- [ ] Docs updated (this TASK.md set to `done`; index row updated)
- [ ] Mobile contract checked if `routes/api.php` touched (`../../mobile/`)
