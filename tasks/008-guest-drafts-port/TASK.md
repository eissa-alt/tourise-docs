# Task 008 — Port the `guest-drafts` feature (backend) from deve-go

- **Status:** `todo` (plan approved; port not started)
- **Opened:** 2026-07-17
- **Owner:** AI agent
- **Sub-app(s):** backend (build) + admin (finish the UI) — **not** frontend, **not** mobile
- **Branch(es):** `dev`
- **Reference impl:** `97-deve-go` backend, commit **`60fe949` "draft guests"** (PRs #79/#81, branches
  `draft-guests` / `merge-draft-guests`). Not in deve-go's working tree (it's on branch `testing`) —
  read it via `git show 60fe949:<path>`.

## Goal

The admin `guest-drafts` UI was migrated into this basecode but its **backend was never carried over**,
so all three screens 404. Port the complete backend from deve-go `60fe949`, adapted to this repo's
conventions, so abandoned registrations are captured, listed, viewed, and exported.

**What the feature does:** captures **incomplete registrations** — a registrant who fills step 1 and
requests an OTP but never completes verification/submission. A `guest_drafts` row is upserted at
OTP-request time and **deleted on successful registration**, so the table is, by definition, everyone
who started and didn't finish. Gives the event team (a) a follow-up/lead-recovery list and (b) drop-off
diagnostics (where each person stalled: OTP sent? verified? attempts? email vs phone).

## Safety assessment (done 2026-07-17 — SAFE, low risk)

`guest_drafts` is a **new, self-contained table** with its own model/controller/routes/resource/export.
It does **not** touch the `guests` schema or existing behavior — it only observes the registration flow
and records. Blast radius on what already works is minimal.

- ✅ All 4 AuthController hook methods exist here (`emailVerification`, `emailConfirmation`,
  `phoneVerification`, `phoneConfirmation`) and are **near-identical** to deve-go (same lineage; only
  Pint formatting differs) → hooks graft cleanly at the top of each (right after validation).
- ✅ No collision — this basecode has zero `GuestDraft` / `guest_drafts` anything.
- ✅ Table deps present: `title_id`, `days` (added in D18), `personal_image`, the `titles` table.
- ✅ `store()` has a clean post-create point for the draft-delete.

## Required adaptations (deviations from a blind port)

1. **`personal_image` → SIGNED URL (D14).** deve-go's `GuestDraftResource` emits only the bare
   `personal_image` filename (the modal rebuilt a **public** URL client-side). This basecode moved
   registrant images to the **private disk, served via signed URLs** (ledger D14). So the ported
   resource must add **`personal_image_url` => `GuestDocumentController::signedUrl('personal_image',
   $this->personal_image)`**, and the admin modal must consume that field — NOT a public rebuild.
   Skipping this reproduces the §4a 404.
2. **`employee_id_number`** is not a `guests` column in this basecode (it is referenced in the guest
   resource but the column doesn't exist). `guest_drafts` is its own table, so keep the column; it just
   stays null unless the join form submits it. Not a blocker — note it, don't chase it.
3. **Repo conventions:** UUID PK + `HasUuids` (match existing models), `foreignUuid` FKs, Pint-clean,
   phpstan **No errors** (guard array/attribute access the way Larastan expects), i18n EN+AR.

## The port — file by file (source: deve-go `60fe949`)

**New backend files (port + adapt):**

| Target (this repo) | Source | Notes |
|---|---|---|
| `database/migrations/2026_07_1x_..._create_guest_drafts_table.php` | `2025_11_26_150403_create_guest_drafts_table.php` | UUID PK, `title_id` foreignUuid→titles; step-1 fields (gender, names, email, company, job_title, phone, employee_id_number, days, personal_image, lang) + OTP tracking (`email_otp_token`, `phone_otp_token`, `verification_attempts` default 0, `email_otp_token_sent`, `email_otp_token_verified`, `phone_otp_token_sent`, `phone_otp_token_sent_verified`) + timestamps. `email` is the upsert key. |
| `app/Models/GuestDraft.php` | same | `HasUuids`; `$fillable`; `title()` belongsTo. |
| `app/Http/Controllers/GuestDraftsController.php` | same | `index` (filters: email, phone, first_name, last_name, `email_otp_token_sent`/`_verified`, `phone_otp_token_sent`/`_verified`, `created_from`/`_to`; `per_page` pagination), `show`, `export`. |
| `app/Http/Resources/GuestDraftResource.php` | same | **+ `personal_image_url` signed** (adaptation 1). `days` already guarded in source. |
| `app/Exports/GuestDraftsExport.php` | same | Excel export used by `export()`. |

**Existing backend files (additive edits — verify each insertion point against this repo, don't blind-apply):**

| File | Edit |
|---|---|
| `routes/api.php` | 3 routes under the admin group: `GET /admin/guest-drafts` (index), `/{id}` (show), `/export/excel` (export). |
| `app/Http/Controllers/AuthController.php` | private `saveGuestDraft(Request): ?GuestDraft` (upsert by email, phone fallback, merge step-1 fields without clobbering); call it in `emailVerification()` + `phoneVerification()` (after validation); mark verified in `emailConfirmation()` (by email) + `phoneConfirmation()` (by phone+token). |
| `app/Http/Controllers/GuestsController.php` `store()` | after the guest is created, `if ($request->email) { GuestDraft::where('email',$request->email)->first()?->delete(); }`. |

**Admin (finish the already-migrated UI):**

| File | Edit |
|---|---|
| `components/shared/modals/guest-drafts/see-more-guest-draft.tsx` | consume signed `draft.personal_image_url` (not the `${STORAGE_URL}/personal_image/...` rebuild at ~:214). |
| `components/shared/forms/filters/guest-drafts/search-guest-drafts.tsx` | **bring this file over from deve-go admin** — the basecode is missing the search filter the listing expects. |
| `data/sidebar-links.tsx` | un-comment the `guest-drafts` entry (lines ~49–50). |
| `translations/{en,ar}/web.json` | any new keys the search filter / statuses need (EN+AR, same commit). |

## Definition of done

- A draft is **captured** on OTP request (email or phone), **updated** on OTP verify, and **deleted** on
  successful registration.
- `GET /admin/guest-drafts` lists + filters + paginates; `/{id}` returns one with a **working signed**
  `personal_image_url`; `/export/excel` downloads.
- Admin listing + search + see-more work end to end; sidebar link live.
- Gates: `composer qa` (pint + phpstan No-errors + tests) + `migrate:fresh --seed` clean; admin
  `type-check` + `production`. **Not mobile-facing** — confirm `routes/api.php` mobile section untouched.

## Todo (execution order)

- [ ] **Backend, new files** — port migration, `GuestDraft`, `GuestDraftsController`,
      `GuestDraftResource` (**+ signed `personal_image_url`**), `GuestDraftsExport`.
- [ ] **Backend, routes** — add the 3 admin routes.
- [ ] **Backend, capture** — `saveGuestDraft()` in AuthController; hook `emailVerification` +
      `phoneVerification`; verify-marking in `emailConfirmation` + `phoneConfirmation`. Eyeball each
      insertion point against this repo's (hardened) AuthController before applying.
- [ ] **Backend, cleanup** — draft-delete in `GuestsController::store()`.
- [ ] **Migrate + smoke** — `migrate:fresh --seed`; tinker: create a draft, verify it lists + the signed
      `personal_image_url` resolves, then simulate completion and confirm the draft is deleted.
- [ ] **Admin** — signed URL in see-more; port `search-guest-drafts.tsx`; un-comment sidebar; EN+AR keys.
- [ ] **Gate** — `composer qa` + `migrate:fresh --seed`; admin `type-check` + `production`.
- [ ] **Docs** — promote the durable decision to `../../decisions/LEDGER.md` (new D#); note SHAs; mark
      this task done.

## Log

- 2026-07-17 — opened as a generic "frontend follow-ups" doc; refocused solely on the guest-drafts port
  after locating the full reference impl in deve-go `60fe949`. Safety analysis done (see above). The
  `useFetch` item split out to **task 009**.

## Decisions

- **Build, not remove** (2026-07-17) — the feature has a real purpose (abandoned-registration recovery +
  drop-off diagnostics) and a complete, safe-to-port reference. Durable once shipped → promote to
  `../../decisions/LEDGER.md`.
- **`personal_image` served as a signed URL** here (not deve-go's public rebuild), per D14.
