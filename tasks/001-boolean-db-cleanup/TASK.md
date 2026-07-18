# Task 001 — Boolean database cleanup + refactor (two tracks)

- **Status:** `in-progress`
- **Opened:** 2026-07-06
- **Owner:** AI agent
- **Sub-app(s):** backend + admin + frontend (+ docs)
- **Branch(es):** `dev`

## Goal

Store real booleans (`true`/`false`) instead of string pseudo-booleans across the stack.
Two tracks:

- **Track A** — the `yes`/`null`, `yes`/`no`, and `with_`/`is_` flag conversions that the
  **cyan** reference already did and documented. Maps 1:1 to our tables.
- **Track B** — a **new** conversion cyan never attempted: 2-value `status` (`active`/`blocked`)
  columns → `is_active boolean default(true)`.

See the full plan: [../../upgrades/cleanup-hardening/BOOLEAN_REFACTOR_PLAN.md](../../upgrades/cleanup-hardening/BOOLEAN_REFACTOR_PLAN.md).

## Scope

- **In (Track A):** guest flags, category flags, badge flags, email-config/template flags,
  automation-setup flags, country/title flags, invitation `prefilldata`/`lock_data`/`with_from`,
  `guest_logistics.self_booking`, `gates.assigned_to_ipad`, `speakers.show_in_homepage`,
  `guest_sms.is_sent`, email-log `is_sent`/`is_delivered`/`is_open`/`is_clicked`. Backend
  migrations (edit in place), model casts, controllers/resources/blade, admin
  `CustomSwitchInput`→`CustomSwitchInputBoolean` + interfaces + form defaults, frontend join-form
  radios/switches + interfaces + SSR boundary.
- **In (Track B):** `status` → `is_active` on the confirmed 2-value tables only; ~18 backend
  controllers (`where('status','active')` + `block()`/`activate()`), `Mobile*Controller` queries,
  notification senders; admin `Status` badge + `status-types-select` + listings + forms + interfaces.
- **Out:** multi-value `status` columns (`app_notifications` Pending, `login_attempts` failed,
  `email_attachments`, `sms_templates` send-state), guest workflow `guest_status_id`, mobile guest
  `status` (accepted/invited). Do NOT re-add cyan's `isEnabled` helper (neither app has one).

## Log

Newest at the bottom. Date each entry.

- 2026-07-06 — opened; plan approved (both tracks; `status`→`is_active` default true; edit
  original migrations in place + `migrate:fresh`). Reference docs live in cyan
  `docs_old/BOOLEAN_REFACTOR_*.md`.
- 2026-07-06 — Track A backend done (migrations + casts + controllers/blade/seeders/factories).
  `automations.is_sent/is_delivered/is_open/is_clicked` kept as string (multi-state, reverted).
  Track A admin + frontend delegated to parallel subagents (type-check + production gates).
- 2026-07-06 — Track B audit gate CLOSED. Confirmed 16 tables are strictly 2-value:
  categories, titles, speakers, sponsors, sms_templates, email_templates, zones, sponsor_labels,
  speaker_labels, areas, gates (`status` only), badges, admins, invitations (`status` only),
  countries (block/activate currently commented — convert column for consistency), and
  guest_statuses (`active`/`inactive`, has real block/activate). Excluded: `users` (no status
  column — legacy `UsersController` dead code), `automation_setups.status` (`'started'`…),
  `gates.scanning_status`, `invitations.usage_status`, `bulk_prints.generate_status`,
  `app_notifications.status`, `login_attempts.status`, `email_attachments.status` (internal
  text flag, lone `block()`, not a standard listing), `guests.residency_status`, guest
  workflow `guest_status_id`.

## Decisions

- **Migration style:** edit the original `create_*` migrations in place, then `migrate:fresh`
  (matches cyan; this baseline has no prod data to preserve).
- **`status` target shape:** rename to `is_active boolean default(true)` (durable → LEDGER D6).
- Intentional `yes`/`no` keeps (from cyan `BOOLEAN_REFACTOR_RECHECK.md`): CSV `Exports` (human
  readability), input normalization helpers, HTML meta.

## Definition of Done

- [ ] Code merged to `dev` in backend + admin + frontend
- [ ] EN + AR translations in the same commit (if any user-facing strings move)
- [ ] Quality gate green (backend `pint --dirty --test` + `php artisan test`; Next apps
      `yarn type-check` + `yarn production`)
- [ ] `migrate:fresh` runs clean
- [ ] Mobile contract re-checked (`../../mobile/`) — resources/queries touched by the refactor
- [ ] Docs updated (this TASK.md → `done`; index row; LEDGER D6; HANDOFF refresh)
