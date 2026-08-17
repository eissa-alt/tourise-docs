# Task 034 — Tourise form shapes (Tourise Public + Tourise Private)

- **Status:** `in-progress`
- **Opened:** 2026-08-17
- **Owner:** Eissa
- **Sub-app(s):** backend | admin | frontend | docs
- **Branch(es):** `dev`

## Goal

Add two client-specific form shapes to the existing form-shapes pattern — **Tourise Public**
(the full registration form: identity, passport, photo, visa assistance) and **Tourise Private**
(an invitation request, with an industry-gated conditional block) — reusing the current
components, validation and conditional-field idiom rather than introducing a new form-building
mechanism.

Named `default-tourise-public` / `default-tourise-private`. They were built as
"Main Registration Form" / "Request an Invitation" and renamed before any commit; no category had
been saved against the old values, so no data migration was needed.

## Scope

- **In:** two new shapes registered end to end (frontend step, admin step, see-more panel, both
  `COMPONENT_MAP`s, `FORM_SHAPES_CONFIG` in both apps, `FormShapeTypeSelect`, per-shape
  mandatory-field sets); a tourism industry dataset; two new guest columns; EN + AR keys.
- **Out:** the "Guest Mix" field (dropped by the owner — categories already cover it); any change
  to `default` / `default-one-step-rsvp` / `default-four-steps`; server-side enforcement of
  `mandatory_fields` for the primary guest (see "Known gaps").

## Decisions

- **D-1 — New shapes, existing pattern.** Both shapes go through `FORM_SHAPES_CONFIG` +
  `loadStepComponent`, per `AI_RULES.md` rule 4 and CLAUDE.md hard rule 4. No `DynamicFormRenderer`.
- **D-2 — Requiredness is never hardcoded.** Every field derives `isRequired` and its `required`
  rule from `mandatoryFields?.includes(<field>)`, fed by `categories.mandatory_fields`. The clean
  reference was `one-step/step-1.tsx`; **`fours-steps/step-1.tsx` was deliberately NOT copied** —
  it hardcodes `isRequired` on ~10 fields, which is the anti-pattern this task rules out.
- **D-3 — A separate tourism industry dataset**, not a rewrite of `industry-types-select`. The two
  lists share no values and `guests.industry` is a free string column, so replacing the old list in
  place would orphan the values already stored against the shapes that use it. The branch value is
  exported as `MEDIA_MARKETING_INFLUENCE` so the conditional check cannot drift from the options.
- **D-4 — Gender renders as a dropdown**, not the radio every other shape uses. Owner-specified;
  the male/female options are the existing ones. One-line swap if it should match the house style.
- **D-5 — ⚠️ Visa Assistance reuses `valid_visa`, INVERTED.** Owner decision, taken with the
  consequence stated: "Yes, I need assistance" stores `valid_visa = false`, and
  `EVisaController::383` treats **exactly** `valid_visa === false` as e-visa eligible. So every
  guest answering Yes on the public registration form is enrolled into the e-visa workflow
  (`/admin/e-visa` listing, package generation). That is a behaviour change to a live workflow —
  confirm it is wanted before this reaches production.
- **D-6 — Only the two social channels got new columns.** Additive, nullable, forward-only.

## Log

- 2026-08-17 — opened. Read the full form-shapes chain first (`FORM_SHAPES_CONFIG`, both
  `COMPONENT_MAP`s, the see-more panel tree, `mandatory-fields-by-form-shape`, the guests schema).
  Confirmed 13 of 16 requested fields already have both a component and a column.
- 2026-08-17 — backend: migration `2026_08_17_000001` (`social_media_channel_1/2`), `$fillable`,
  the two `GuestsController` assembly arrays + the `$request->only()` whitelist, `GuestsResources`
  (+ `country_of_residence_name`, the name twin of `nationality_name` — the see-more panels had no
  other way to render a country). New `SocialMediaChannelsTest` (3 tests).
- 2026-08-17 — frontend + admin: both shapes built and registered; tourism dataset mirrored in both
  apps (values verified identical); 24 EN + 24 AR keys per app.
- 2026-08-17 — gates green: backend `pint` + `phpstan` 0 errors + **524 tests** (was 521); admin
  `type-check` + `check:rbac` (32 links) + `build`; frontend `type-check` + `build`. eslint clean
  on every new file.
- 2026-08-17 — **renamed to Tourise Public / Tourise Private** at the owner's request, before any
  commit. Full rename, not just labels: shape values, the six folders, component names,
  `COMPONENT_MAP` paths, `flow` values, the mandatory-field constants, and the EN/AR label keys
  (`request_an_invitation` / `main_registration_form` dropped, `tourise_public` /
  `tourise_private` added). Checked the dev DB first — **0 categories** referenced either old
  value, so nothing had to be migrated. Public is listed above Private in the category dropdown.
  Gates re-run green after the rename.

## Field map (what reuses what)

| Requested field | Component | Guest column |
| --- | --- | --- |
| Gender | `StaticSelectNew` / `CustomSelect` (admin) | `gender` |
| Title | `TitleSelectNew` / `TitleSelect` | `title_id` |
| First / Last name, Job Title, Company | `CustomInput` | as named |
| Email | `CustomInput` + `isUniqueAttribute` | `email` |
| Industry | `StaticSelectNew` / `TourismIndustrySelect` | `industry` |
| Country of Residence, Nationality | `CountrySelectNew` / `CountrySelect` | FK → `countries` |
| Phone / Mobile Number | `PhoneInputV2` (E.164) | `phone` |
| Date of Birth | `MaskedDateInput` | `birth_date` |
| Passport / Iqama Number | `CustomInput` | `document_number` |
| Personal Photo | `CustomFileInput2` | `personal_image` |
| Social Media Channel 1 / 2 | `CustomInput` | **new** `social_media_channel_1/2` |
| Visa Assistance | `StaticSelectNew` / `CustomSelect` | `valid_visa` (**inverted**, D-5) |

## Known gaps (open, not defects introduced here)

- **`mandatory_fields` is not enforced server-side for the primary guest** — only for extra guests
  (`GuestsController.php:521`). Requiredness on these two shapes is therefore client-side only,
  which matches every existing shape. Worth a task of its own.
- **`GuestType.valid_visa` had to be widened to `boolean | string | null`** in the admin: the column
  and API are boolean, but the four-steps admin form writes `'yes'`/`'no'` strings. Widening
  surfaced a real pre-existing bug in the four-steps see-more panel (it rendered `web:true`); that
  one line was fixed because the type change exposed it.
- **Nothing has been opened in a browser.** Both shapes need a live click-through: the conditional
  block appearing/clearing, the OTP modal path, an admin edit round-trip, and the see-more panels.

## Definition of Done

- [x] Code written in backend / admin / frontend
- [x] EN + AR translations in the same commit
- [x] Quality gate green (backend `composer qa`; Next apps `yarn type-check` + `yarn build`, admin
      `yarn check:rbac`)
- [x] Docs updated (this TASK.md; index row)
- [x] Mobile contract checked — `routes/api.php` untouched. The guest payload gains two additive
      optional fields; nothing removed or renamed, so no mobile notice is required.
- [ ] Owner review of the diff, then commit + push
- [ ] Migration run on the dev DB, then prod
- [ ] Manual QA in a browser (see "Known gaps")
- [ ] **D-5 confirmed** — Visa Assistance = Yes enrolls the guest into the e-visa workflow
