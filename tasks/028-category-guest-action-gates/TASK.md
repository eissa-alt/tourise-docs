# Task 028 — Gate guest row actions and the issued-visa template per category

- **Status:** `done (code)` — prod migrate + manual QA pending
- **Opened:** 2026-07-28
- **Owner:** —
- **Sub-app(s):** backend + admin
- **Branch(es):** `dev`

## Goal

Let each category decide which of the five guest-listing row actions its guests expose (resend email /
SMS / WhatsApp, print badge, mark collected), and put the issued-visa email template behind an explicit
on/off toggle instead of inferring it from "a template is selected".

## Scope

- In: six new boolean columns on `categories`, their validation / persistence / resource exposure, the
  row-action gating in the guests listing, the three shared comms buttons gaining a disabled state, and
  the issued-visa section of the categories form.
- Out: the guests-listing RBAC action permissions — the category switch is an **additional** gate layered
  on top of `checkActionPermission`, not a replacement.

## Decisions

- **Two additive, forward-only migrations.** `2026_07_28_000001` adds `with_resend_email`,
  `with_resend_sms`, `with_resend_whatsapp`, `with_print_badge`, `with_mark_collected`;
  `2026_07_28_000002` adds `with_issued_visa`.
- **⚠️ The five row-action toggles default to `false` and are NOT backfilled.** Deliberate — existing
  categories opt in explicitly. **Operational consequence: the moment this migration runs, every guest
  row action disappears from every category until an admin turns it back on**, including *print badge*.
  Turn the switches on per category immediately after the prod migrate, before any on-site use.
- **`with_issued_visa` IS backfilled** (`update … where issued_visa_email is not null`), so categories
  that already had a template selected keep working. The asymmetry with the five above is intentional:
  here the old behaviour was itself derived from a selected template, so the backfill reproduces it
  exactly; the row actions had no equivalent signal to derive from.
- **Gate = category switch AND RBAC permission.** Both must pass for the action to render.
- **Comms actions stay visible but disabled when their provider isn't configured.** A category can turn
  Resend Email/SMS/WhatsApp on while no default SMTP / SMS / WhatsApp provider exists; the button then
  greys out with a `web:provider_not_configured` tooltip rather than vanishing, so the admin can tell
  "not allowed here" from "not set up yet". Readiness comes from the three existing
  `*/check-default` endpoints, mirroring the categories and automation forms.
- **The listing reads the switches off the guest row's embedded category** (`row.category?.with_*`).
  `GuestsResources` serialises the whole `category` model, so the new columns ride along with no resource
  change needed — but that also means **the toggles only work while `category` stays eagerly loaded** on
  the guests index.

## Log

- 2026-07-28 — backend `072dff2` (`P028.1`): 2 migrations, `Category` `$fillable` + boolean casts,
  `CategoriesController` validation + persist, `CategoriesResources`. Admin `718bcf7` (`P028.1`):
  `guests-listing.tsx` gating + provider-readiness fetches, `resend-btn` / `send-sms-btn` /
  `send-whatsapp-btn` gain `disabled` + `disabledText`, `categories-form.tsx` switches + issued-visa
  restructure, `interfaces/category.tsx`, EN + AR.
- 2026-08-01 — documented (this file, index row, ledger D47, handoff). Dev DB confirmed migrated
  (`migrate:status`: both `2026_07_28_*` **Ran**).

## Definition of Done

- [x] Code merged to `dev` in the relevant sub-app(s)
- [x] EN + AR translations in the same commit (11 keys each)
- [x] Quality gate — pre-commit hooks green at commit time; **full gate not re-run since** (see handoff)
- [x] Docs updated (this TASK.md; index row; ledger D47; handoff)
- [x] Mobile contract unaffected — `/admin/*` only, `routes/api.php` untouched
- [x] Dev DB migrated
- [ ] **Prod `php artisan migrate`** — and then turn the five switches on per category (see the warning
      above) before anyone relies on the row actions
- [ ] Manual browser QA — toggle each switch, confirm the row action appears/disappears; unconfigure a
      provider and confirm the greyed-out tooltip
