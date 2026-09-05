# Task 035 — Mandatory-field catalogue back in the admin bundle

- **Status:** `done (code)` — dev-DB migrate + manual browser QA pending
- **Opened:** 2026-09-06
- **Owner:** Eissa
- **Sub-app(s):** admin + backend
- **Branch(es):** `dev`

## Goal

Stop relying on `FormShapeFieldsSeeder`. Put the per-shape mandatory-field lists back in the
admin bundle behind `getMandatoryFieldsByFormShape`, exactly as the sibling clones do
(`128-pif-psf-2026` Task 039, `123-pif-pep-v2`), and remove the seeded table, its endpoints
and its model.

**This reverses [Task 033](../033-fork-port-back/TASK.md)'s `form_shape_fields` delivery.**
Owner's call.

## Why

The catalogue being *data* meant every environment needed
`php artisan db:seed --class=FormShapeFieldsSeeder` after any list change, or the picker
silently showed a stale set.

That is exactly what happened to the media shape. Backend `6c7ae93`
("fix(media): field catalogue for the mandatory-fields picker") added the `default-media`
list **to the seeder only**, so on any environment that had not been re-seeded the category
form's Mandatory-fields picker for Media Registration rendered **"No results found"**. In the
bundle the list ships with the build and cannot go stale per environment.

`128-pif-psf-2026` hit the same failure a different way — its Task 038 added `title_id` to the
public shape and the option only appeared after a re-seed — and removed the table for the same
reason on 2026-09-03.

## Scope

- **In:** new `admin/data/mandatory-fields-by-form-shape.tsx`; `mandatory-fields-select-multi.tsx`
  rewritten to read it; backend model, controller, seeder, routes and tests deleted; a migration
  dropping `form_shape_fields`.
- **Out:** any replacement drift guard — matching 128's owner decision, review only.
- **Out:** backend validation of mandatory fields. Not in scope and unchanged either way — see
  "What the backend actually validates" below.

## Decisions

- **Parity was proved before anything was deleted**, and proved against
  `FormShapeFieldsSeeder::catalogue()` — the source of truth — **not** against the live seeded
  table, which is precisely what was stale. All seven shapes came out **identical, order
  included**:

  | shape | fields |
  |---|---|
  | `default` | 9 |
  | `default-one-step-rsvp` | 9 (aliases `default`, as the seeder did) |
  | `default-four-steps` | 30 |
  | `default-tourise-public` | 22 |
  | `default-tourise-private` | 13 |
  | `default-request-invitation` | 5 |
  | `default-media` | 23 |

  111 rows across 7 shapes. The unknown/missing-shape fallback was checked separately and is
  the `default` list, matching both the old helper and `FormShapeFieldController::selectList()`.

- **Tourise has seven shapes, not PSF's five.** Four are fork-local (`tourise-public`,
  `tourise-private`, `request-invitation`, `media`), so this is a port of *this repo's* seeder,
  not a copy of 128's file. All seven keys already match `FORM_SHAPES_CONFIG` in
  `data/form-shapes-config.tsx`.

- **Full removal, not a dead table.** `FormShapeField`, `FormShapeFieldController`,
  `FormShapeFieldsSeeder`, its `DatabaseSeeder` entry, the two routes + import and
  `FormShapeFieldsTest` are gone, and `2026_09_06_000001` drops the table. Leaving it in place
  would have meant two sources for one list — the state that caused this. `down()` recreates the
  schema faithfully but **cannot repopulate**: the seeder that knew the rows goes with it.

- **The seeder's docblock knowledge was carried across, not deleted.** Chiefly the RSVP caveat:
  `default-one-step-rsvp` offers a copy of the default nine, which is wrong — that form registers
  only `will_attend` and `dietary_requirements` and never reads `mandatoryFields`. Kept as a copy
  so behaviour is unchanged, with the correction written out in the comment. Also carried: the
  tourise-public e-visa-block note, the "Request Invitation.xlsx = five fields" note, and the
  media "terms is a consent, not a mandatory field" note.

- **No translation work.** Every `web:*` key the lists reference already exists in **both**
  `translations/en/web.json` and `translations/ar/web.json` — checked including the media-only
  keys (`first_name_ar`, `last_name_ar`, `company_website`, `attendance_dates`, `linkedin`,
  `instagram`, `x_handle`) and the aliased labels (`web:id_type`, `web:id_number`,
  `web:visa_assistance`).

- **The endpoints were not in the mobile contract** — `BACKEND_INCOMING_CHANGES_FOR_MOBILE.html`
  greps clean for `form_shape` / `form shape`, and both routes were `admin/`-prefixed. CLAUDE.md
  hard rule 4 satisfied.

- **Removing them also closed a flagged exposure.** `admin/form-shape-fields` sat in the plain
  `auth:sanctum` group with **no `admin.can` gate** — readable by any sanctum token including a
  mobile guest's. The routes no longer exist.

- **The loading flash goes with the fetch.** All three pickers on the category form (user side,
  admin side, extra guests) rendered a spinner then the list; they now render the list.

## What the backend actually validates (unchanged by this task)

- **`extra_guest_mandatory_fields` IS enforced** — `GuestsController` loops the related guests and
  422s with `related guest #N missing required field: X`.
- **`mandatory_fields` and `mandatory_fields_admin` are NOT enforced.** They are stored and read
  back out; for the main guest, "mandatory" lives entirely in the frontend.
- **Nothing validates the field *keys*** against the shape. That is why a category switched
  between shapes can hold keys the new form never renders.

Nothing read `form_shape_fields` but the controller that served it, so dropping it changes no
behaviour, and `categories.mandatory_fields` / `mandatory_fields_admin` are untouched — every
category keeps its selections.

## Log

- 2026-09-06 — opened and delivered. Admin `b08a930`: `data/mandatory-fields-by-form-shape.tsx`
  added (7 shapes, 111 rows), `mandatory-fields-select-multi.tsx` rewritten (no `useFetch`, no
  loading/error branch). Backend `eaa6a1d`: model, controller, seeder (+ `DatabaseSeeder` entry),
  2 routes + import and `FormShapeFieldsTest` removed; migration `2026_09_06_000001` drops the
  table. Gates green: pint + phpstan + **540 tests** (547 → 540: the 7 `FormShapeFieldsTest`
  cases); admin `yarn type-check` + `yarn build` + `yarn check:rbac` + eslint.

## Definition of Done

- [x] Code committed to `dev` in both sub-apps
- [x] EN + AR translations — none needed; every `web:*` key already exists in both files
- [x] Quality gate green (backend `pint --test` + `phpstan` + 540 tests; admin `yarn type-check`
      + `yarn build` + `yarn check:rbac`)
- [x] Docs updated (this TASK.md; index row; Task 033 cross-reference)
- [x] Mobile contract checked — endpoints absent from the contract doc; `routes/api.php` lost two
      `admin/`-prefixed routes only
- [ ] `php artisan migrate` on the dev DB, then every other environment, to drop the table there
- [ ] Push both repos
- [ ] Manual browser QA — categories edit on all seven shapes: the picker lists the right options
      with no loading flash, **Media Registration is no longer empty**, and saving keeps the
      selections
