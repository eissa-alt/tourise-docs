# Task 020 — Reconfirmation (guest attendance re-confirmation)

- **Status:** `in-progress` — **Phase A + B implemented 2026-07-25 (uncommitted, all gates green)**: backend, frontend (email), admin surfacing, and the SMS + WhatsApp `{{ reconfirmation_url }}` variable (shared `ReconfirmationLink` helper). Manual QA + commit pending.
- **Opened:** 2026-07-25
- **Owner:** (unassigned)
- **Sub-app(s):** backend + admin + frontend (+ docs)
- **Branch(es):** `dev` → feature branch `feat/reconfirmation`

## Goal

Let the event team send a **follow-up "please reconfirm your attendance"** request to already-registered
guests (over email / SMS / WhatsApp), capture the guest's reconfirmation answer **separately** from their
original RSVP, and surface it in the guest listing / filter / see-more / exports.

Delivery rides on the existing **Automations** flow — the admin builds an automation (immediate **or
scheduled**) whose template carries the reconfirmation link, and picks the audience. No per-category
configuration. This is a lean, additive feature built on 121's own machinery, **not** a port of the
sibling implementation.

> **Revised 2026-07-25 (post D38/D39).** While this plan was drafted, the other session landed automation
> **scheduling** (D39: `AutomationDispatchService` + `automations:dispatch-scheduled` cron) and a
> **filter-and-select audience picker** (D38: `guest_ids` + `/guests/select-ids`), both **pushed**. This
> plan now builds *on* that machinery. Net effect: automatic (scheduled) reconfirmation is available **for
> free**, and we still change **no** automation code.

## Scope

**In:**
- 2 additive nullable `guests` columns: `reconfirmed_will_attend` (yes/no) + `reconfirmed_at`.
- A new per-guest, single-use reconfirmation link variable `{{ reconfirmation_url }}`, usable in email,
  SMS and WhatsApp templates (reuses the `question_tokens` mechanism).
- A new public page `/[lang]/reconfirm/[category]/[token]` (a lean twin of `/complete-data`) with a lean
  Yes/No + dietary form, backed by 2 additive public endpoints (verify-token + submit).
- Guest listing: column + filter + see-more + the 3 guest exports show the reconfirmation answer/date.
- Reconfirmation is **sent via the existing Automations flow** — admin creates their own reconfirmation
  email/SMS/WhatsApp templates and picks the audience (the D38 filter-and-select picker). No new send subsystem.
- **Immediate or scheduled** delivery — both come free from the D39 automation scheduler; we add no
  scheduling of our own.

**Out (explicitly not this task):**
- **A bespoke reconfirmation scheduler or send subsystem.** We reuse the D39 automation scheduler as-is —
  "send X days later automatically" is just a *scheduled* automation, not new infrastructure from us.
- **Multiple distinct rounds** (round 2, 3, … each recorded independently). Not now — see Decisions D-2.
  Re-sending the *same* request as a reminder is already free (the token re-mints).
- **A category toggle / status mapping / secondary-status track.** Deliberately none (Decisions D-3).
- **Side-effects of a "No"** (status change, seat release, notifications). Purely informational for now.
- **Link expiry.** Reuse `question_tokens` as-is (single-use, no TTL).

## Background — investigation summary (2026-07-25)

The feature already exists, fully built, in the sibling repo **120-pif-private-events-platform** ("PEP")
under the name **"Second RSVP"** (merged `feature/scheduled-automation-second-rsvp` branch + follow-ups;
covered by `tests/Feature/SecondRsvpTest.php`). 120 and 121 are both clones of `pif-directors-gathering`,
so the *concept* maps cleanly — but 120's implementation leans on subsystems 121 builds differently (a
parallel secondary-status track and guest-groups 121 lacks; a scheduler 121 **now has its own** via D39),
so we take the design lessons and build fresh on 121's own machinery rather than porting 120's code.

**What 120 does (for reference):** a second, independent RSVP round whose answer lands in a *separate*
`guests.secondary_status_id` (round-1 answer preserved), armed by a `categories.with_second_rsvp` toggle +
`status_config` JSON; the round "opens" by re-sending the invitation (never a date window); the link is
addressed to the individual guest via their unique `registration_number` (never the shared code); submit is
a dedicated `POST /guests/second-rsvp`.

**Why we don't port it — the 120→121 gap (all verified by grep):**

| 120 dependency | In 121? | Our decision |
|---|---|---|
| `secondary_status_id` / `status_config` parallel-status subsystem | absent | Design out — use a plain `reconfirmed_will_attend` column. |
| `guest_groups` / `FiltersGuests` targeting | absent | Not needed — automation audience is an ad-hoc list. |
| Automation scheduler (`AutomationDispatchService` + `automations:dispatch-scheduled` cron) | **present since D39 (2026-07-25)** | **Reuse** — reconfirmation sends immediate or scheduled, no work from us. |
| `admins.type` branching | absent (forbidden) | RBAC catalog only — reuse `automation` + `guests_listing`. |
| Per-guest single-use link | 121 has **`question_tokens` + `{{ missing_data_url }}`** | **Reuse** — it already solves "address the individual, not the shared code". |
| `will_attend` yes/no column + decline flow + `form_shape` reuse | **present** | **Reuse** as the state + form foundation. |

**Design lessons harvested from 120's git history (do not repeat):**
- A **date-window** to open the round was tried and **abandoned** (`fa8e9a1`) — it opened for everyone
  regardless of who was actually contacted. → Reconfirmation is opened only by the automation that mints a
  token for that guest.
- Addressing the link by a **shared code** was a correctness bug (`5e2329e`) — one guest's confirmation
  could land on another's row. → We use a **per-guest single-use token** (`question_tokens`), so this can't
  happen.
- The round-2 answer is written **beside** the first, never over it. → `reconfirmed_will_attend` is a
  separate column; `will_attend` is untouched.

## Design (locked)

### Data
- **Migration** `backend/database/migrations/2026_07_25_000003_add_reconfirmation_to_guests_table.php`
  (⚠️ **`_000003`** — the P24 session already used `2026_07_25_000001` (channel) + `_000002` (scheduling);
  ours must stack after them) — additive, forward-only (no `migrate:fresh`; real data exists):
  - `reconfirmed_will_attend` — nullable string `yes`/`no` (the reconfirmation answer).
  - `reconfirmed_at` — nullable timestamp (also the "has answered?" flag).
  - Add both to `Guest::$fillable`.
- **Migration** `2026_07_25_000004_create_reconfirmation_tokens_table.php` — a dedicated token table
  (twin of `question_tokens`: `email` primary + unique `token` + `created_at`). **Revised from D-5's
  "purpose flag on `question_tokens`"** because `question_tokens.email` is the PRIMARY KEY (one row per
  email) — sharing the table would make the missing-data and reconfirmation links clobber each other. A
  separate table lets a guest hold both, and touches none of the working missing-data code.

### Backend — link variable + endpoints
- `app/Services/EmailVariableResolver.php` — add a `{{ reconfirmation_url }}` branch mirroring the existing
  `{{ missing_data_url }}`: mint a `reconfirmation_tokens` row and return
  `{frontend_url}/{lang}/reconfirm/{categorySlug}/{token}`. Resolves on every email send path
  (`SendAutomationEmailNotification`, guest + invitation notifications).
- `app/Http/Controllers/GuestsController.php` — two new methods, thin twins of `verifyStatusAndToken()`
  and `updateGuestMissingData()`:
  - `verifyReconfirmationToken($token)` → returns the guest's name + current answers (lean array, minimal PII).
  - `submitReconfirmation(Request)` → reCAPTCHA-gated; look the guest up by token; write
    `reconfirmed_will_attend` + `reconfirmed_at = now()` (+ refresh `dietary_requirements` when Yes); burn
    the token; write a `HistoryLog` row. **Writes only the reconfirmation columns — never `will_attend`.**
- `routes/api.php` — 2 new **public** routes (`GET verify-reconfirm-token/{token}`, `POST reconfirm`).
  ⚠️ **Additive mobile-contract change** — check `docs/mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf`
  and issue an additive notice; nothing removed/renamed.
- `app/Http/Resources/Admin/GuestsResources.php` — expose `reconfirmed_will_attend` + `reconfirmed_at`.

### Frontend — the guest-facing page
- New page `frontend/pages/[lang]/reconfirm/[category]/[token].tsx` — styled on the lean `decline.tsx`
  page (card + reCAPTCHA + `LinkErrorSections`), SSR-verifies the token, then renders a **self-contained
  lean form** (Yes/No attendance, dietary shown only when Yes). **Revised from the plan's `form_shape`
  approach:** a reconfirmation is not a registration shape, so a dedicated component is simpler than
  registering a new `form_shape` across the three form surfaces — no `FORM_SHAPES_CONFIG` / `COMPONENT_MAP`
  change.
- No change to the `join` route. 9 new EN + AR `web:reconfirm_*` keys in the same change.

### Admin — surfacing the data (the mechanical bulk)
- Listing column in `guests-listing-by-admin/guests-listing.tsx` (mirrors the `will_attend` column).
- Filter control in `shared/forms/filters/guests/search-guests-by-super.tsx` (mirrors the `will_attend`
  select) + the backend `where` clause in `GuestsController::index` (yes / no / pending).
- See-more chip in `gusets-see-more-by-admin/see-more-admin.tsx`; `reconfirmed_will_attend` +
  `reconfirmed_at` added to `interfaces/guest.tsx` (`GuestType`). New `web:reconfirmation` EN/AR key.
- Exports: add the two fields to `GuestsExport`, `GuestsExportView`, `GuestsExportGuestView` (they already
  emit `will_attend`).
- **No category-form changes.** RBAC: reuse existing `automation` (send) + `guests_listing` (view)
  features — no new catalog entry.

### Channels & delivery
Delivery uses the existing **single-channel automation** (email | SMS | WhatsApp, per P24.22), now fanned
out by **`AutomationDispatchService`** (D39). Crucially, that service **fires the existing send events and
does not change the event → listener → renderer path** — so our `{{ reconfirmation_url }}` renders
identically whether the automation is sent immediately, manually, or on a schedule. **We change no
automation code**; the only per-channel work is making the variable resolvable in each channel's template
renderer (email resolver / SMS listener / WhatsApp renderer).

## Implementation plan

### Phase A — email channel, fully self-contained (no collision)
Everything above **except** SMS/WhatsApp link resolution. Touches nothing the WhatsApp session owns. Ship
this independently: migrations, `EmailVariableResolver` variable, the 2 endpoints + routes, the frontend
page + lean form_shape, and the admin listing/filter/see-more/export surfacing. Reconfirmation over **email**
works end to end. Gate: `composer qa` + `yarn type-check`/`production`; feature test for verify + submit +
the "writes reconfirmed_*, not will_attend" invariant + a permission/gate test.

### Phase B — SMS + WhatsApp
Add `{{ reconfirmation_url }}` to the SMS + WhatsApp rendering paths:
- SMS: `app/Listeners/SendGuestSMSListener.php` (builds `{{ invitation_link }}` at line 115) + the preview
  sample in `SmsTemplatesController.php:207`.
- WhatsApp: `app/Services/WhatsApp/WhatsAppTemplateRenderer.php` (+ the guest-WhatsApp listener/preview).
- **P24 is now pushed** (backend `38729eb`; scheduling + WhatsApp + RBAC all settled), so these files are
  stable and the earlier collision risk is largely gone. Only coordination left: if P24's *manual QA* edits
  the WhatsApp renderer, rebase our small variable addition on top. Do this phase after Phase A lands.

## Decisions

- **D-1 — Build fresh on 121, don't port 120.** 120's Second RSVP depends on secondary-status and guest
  groups (absent in 121) and a scheduler (121 now has its own via D39). Reuse 121's `question_tokens` +
  `will_attend` + the D38/D39 automation instead; take only 120's design lessons.
- **D-2 — Single reconfirmation round, preserve both answers.** `reconfirmed_will_attend` beside
  `will_attend`. Multiple recorded rounds → deferred; if ever needed, migrate to a child
  `guest_reconfirmations` table (do **not** keep adding column pairs).
- **D-3 — No category setting, no status side-effects, no link expiry.** Reconfirmation is just an
  automation; a "No" is informational only; the token is single-use with no TTL.
- **D-4 — All three channels.** Email in Phase A; SMS + WhatsApp in Phase B. P24 (WhatsApp + scheduling)
  is already pushed, so the resolver files are stable — Phase B just adds the variable there.
- **D-5 (revised in implementation) — dedicated `reconfirmation_tokens` table**, NOT a `purpose` flag on
  `question_tokens`. Discovered `question_tokens.email` is the PRIMARY KEY (one token per email), so a shared
  table would clobber missing-data vs reconfirmation links. A twin table isolates the flows and leaves the
  working missing-data code untouched.
- Promote D-1…D-4 to `../../decisions/LEDGER.md` on completion (next id after **D41**).

## Open items / risks

- **Mobile:** 2 new public routes → additive contract change; issue the notice before `dev`→`main`.
- **Phase B ordering:** P24 is pushed, so the shared resolver files are stable; rebase only if P24's manual
  QA later edits the WhatsApp renderer. Do Phase B after Phase A.
- **Lean form_shape** is the one non-trivial frontend piece — must register across the 3 form surfaces
  (public + admin create/edit + see-more) per the form-shape registry conventions.
- Minor pre-existing debt spotted nearby (not this task): `verifyStatusAndToken` carries a `// TODO: remove
  this test hook` forced-500 branch (`GuestsController.php:3617`). Leave as-is or clean separately.

## Definition of Done

- [ ] Code merged to `dev` in backend + admin + frontend
- [ ] EN + AR translations in the same commit (guest-facing form + admin column/filter labels)
- [ ] Quality gate green (backend `composer qa`; Next apps `yarn type-check` + `yarn production`)
- [ ] Feature tests: verify-token, submit (writes `reconfirmed_*` only), permission gate
- [ ] Docs updated (this TASK.md → `done`; index row; ledger entry; HANDOFF)
- [ ] Mobile contract checked — additive notice issued for the 2 new public routes
- [x] Phase B: `{{ reconfirmation_url }}` added to the SMS + WhatsApp renderers (shared `ReconfirmationLink`, guarded mint)
