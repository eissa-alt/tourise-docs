# Task 045 — Audit logs for every module

- **Status:** `todo` — scoped 2026-09-23/24, **on hold at the owner's request before any code**
- **Opened:** 2026-09-23
- **Owner:** —
- **Sub-app(s):** backend + admin
- **Branch(es):** none yet

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

- **In:** one generic audit table; a single write path; a per-record History tab reusing the existing
  From/To renderer; a global audit screen behind its own feature id.
- **Out:**
  - The six delivery tables and `login_attempts` / `badge_print_logs` — different axis, they stay.
  - `history_logs` — production data, guest-facing timeline, already rendered. **Not migrated.** It
    keeps serving guests and simply stops growing for new modules.
  - Backfill of any kind. There is nothing to backfill from.

## Design (proposed, not built)

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

## Cheap wins available independently of this task

Both are **columns, not log rows** — "who owns this collection" is an attribute you will want to filter
and sort by, and reconstructing it from a log table on every list query would be wrong:

- `created_by` on `invitation_collections`.
- Sender attribution on invitation sends.

These answer the team's literal question and do not need the audit system to exist.

## Log

- 2026-09-23 — opened. Team asked for invitation-collection logs; owner widened to every module and
  chose the **who + what changed** depth. Survey of existing logging done; the forward-only finding
  surfaced and is the headline.
- 2026-09-24 — one-table-vs-per-module settled in favour of one table, with the capacity math for 40K
  guests to March 2027 and the allowlist as the volume control. The two `history_logs` findings
  recorded and deliberately left unfixed. **Put on hold by the owner before any code, branch or
  schema.**

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

## Sequencing

Recommended **after task 041** (security port wave 1 — `todo`, 0/23, no branch). This feature copies PII
into a second table, and 041 exists to close disclosure holes; landing this first widens exactly the
surface 041 is meant to shrink. **Owner has not yet ruled on sequencing — this is a recommendation, not
a decision.**

## Definition of Done

- [ ] Code merged to `dev` in the relevant sub-app(s)
- [ ] EN + AR translations in the same commit (if any user-facing strings)
- [ ] Quality gate green (backend `pint --test` + `phpstan` + `php artisan test`; admin `yarn type-check`
      + `yarn build` + `yarn check:rbac`)
- [ ] Retention / pruning policy decided and implemented, not deferred
- [ ] Eloquent-bypass list above either converted or explicitly logged
- [ ] Team told the data is forward-only, before they see the UI
- [ ] Docs updated (this TASK.md set to `done`; index row updated)
- [ ] Mobile contract checked if `routes/api.php` touched (`../../mobile/`)
