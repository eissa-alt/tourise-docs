# Task 043 — The guest list is the quantity

- **Status:** `in-progress` — code written and gates green, uncommitted, awaiting the owner's review
- **Opened:** 2026-09-23
- **Owner:** —
- **Sub-app(s):** backend + admin
- **Branch(es):** `dev`

## Goal

Stop asking how many invitations to mint. On Invitations → Create, a **single-use** collection mints
one invitation per guest — a card added with **+** and dropped with **×**, or a row in the Excel
file. A **multiple-use** collection is one shared link, and says how many times it may be redeemed.

Ported from 123-pif-pep-v2 (admin `a5d59c2`, backend `a0c7cb8`, both 2026-09-13), with one
difference: pep hid the Multiple usage type, and tourise keeps it.

## Scope

- In: `POST /admin/invitations` (the `quantity` rule, the creation loop, `total_invites`), the
  invitation create form, the shared Excel parser, EN + AR strings, the sample file's instructions,
  the manual test files.
- Out:
  - Operations → Import keeps its own copy of the column auto-mapper.
  - The **edit** path of `invitations-form.tsx` is orphaned and was left alone — see the Log.
  - The form-locks-after-a-rejected-batch bug — see the Log.

## Log

- 2026-09-23 — why: `quantity` was typed by hand and everything hung off it. Manual rows were
  generated to match, an Excel file was refused unless its row count agreed
  (`validation:excel_rows_quantity_mismatch`), and the backend counted to it rather than over the
  guests (`for ($i = 0; $i < $request->quantity; $i++)`, with `$guestList[$i] ?? []` minting a blank
  invitation for every index past the end). The same number, asked twice, free to disagree.
- 2026-09-23 — **backend.** The `quantity` rule is gone. `guests_list` is
  `required_if:usage_type,single|array|min:1`, the rows to mint are the guest list (or exactly one
  blank row for `multiple`), `total_invites` is their count, and the loop is a `foreach`. A stale
  caller's `quantity` is ignored, not rejected, as in pep.
  - `valid_up_to` gained `required_if:usage_type,multiple|integer|min:1`. It had **no rule at all**
    and is written to `remaining`, so an omitted value minted a link with no uses left. Single-use
    links are now forced to 1 in the controller rather than trusted from the request.
  - `InvitationCollectionResource` dropped `'quantity' => $this->quantity` — no such column or
    accessor, so it always serialised `null` (pep dropped the same line). Its duplicated
    `'total_invites'` key went with it; pep still has both copies. The JSON is unchanged.
- 2026-09-23 — **admin.** Out: the Quantity inputs on both paths, `isQuantityValid` and the three
  sections it gated, the 400 ms debounce and the effect that sized the rows to it, the
  "clear guests when quantity invalid" effect, `quantity` in the payload, and the `totalGuests`
  prop. In: one guest card on opening manual mode, an **Add guest** button, and an **×** on every
  card past the first.
  - **Multiple** now shows **Number of use** where Quantity used to be, and no fill mode or guest
    rows at all; its payload carries no `fill_mode` and no guests.
  - Excel keeps the "nothing in the file" guard and the duplicate-email, phone and CC/BCC guards;
    only the rows-vs-quantity check is gone.
- 2026-09-23 — **the Excel parser** (`custom-excel-import.tsx`, shared with Operations → Import)
  drops rows where every cell is blank, and SheetJS's phantom `__EMPTY…` columns. `defval: ''` keeps
  a sheet's formatted-but-empty padding rows, and now that each row is one invitation, each of those
  would have minted an empty one. Test file `05-blank-rows.xlsx` pins it: 6 rows in, 3 guests out.
- 2026-09-23 — strings: `web:add_guest` / `web:remove_guest` added in EN + AR;
  `validation:excel_rows_quantity_mismatch`, `web:quantity` and `validation:max_number_10k` removed,
  their only call sites being the rules that went. `validation:min_number_1` stays — Number of use
  uses it. `interfaces/invitation-collection.tsx` lost its dead `quantity` field.
- 2026-09-23 — the sample file's step 3 now reads "Every row becomes one invitation, so this file
  decides how many there are", in EN and AR. Its columns are unchanged, so
  `InvitationImportTemplateTest` stands.
- 2026-09-23 — gates: backend `pint --test` clean, `php artisan test` 849 passed (6 new in
  `InvitationStoreTest`), PHPStan clean on the changed files; admin `yarn type-check`, eslint,
  prettier, `yarn check:rbac`, `yarn build` green. The SheetJS simulation over
  `excel_import_fixes/test-cases` gives the row counts the README claims.
- 2026-09-23 — **found, not fixed:**
  - The form's **edit** mode is orphaned. It GETs `/invitations/{id}`, which returns a paginated
    list of a collection's invitations, and PUTs `/invitations/{id}`, which does not exist. Editing
    a collection actually goes through `invitations-collection-form.tsx` →
    `PUT /admin/invitations-collection/{id}`, which never had a quantity.
  - A **rejected batch locks the form** until the page is reloaded: `guests_list` is a
    `useFieldArray` root, and react-hook-form never clears errors it does not own, so `handleSubmit`
    refuses every later submit. pep hit this and fixed it with `clearErrors()` at the top of submit
    (`d196a49`). Small, and worth doing next.

## Decisions

- **Single: the guest list is the count** (ported). Nobody types a number that can disagree with the
  rows.
- **Multiple: one shared link per collection** (owner, 2026-09-23). Number of use moves to where
  Quantity was. Minting several blank links at once was only ever "type a quantity and leave the
  rows empty", and the database holds no multiple-use collection, so nothing existing changes.
  Someone needing two different shared links makes two collections.
- `valid_up_to` is validated and forced to 1 for single-use links, instead of being written straight
  from the request.

## Definition of Done

- [ ] Code merged to `dev` in the relevant sub-app(s)
- [x] EN + AR translations in the same commit (`web:add_guest`, `web:remove_guest`; three removed)
- [x] Quality gate green (backend `pint --test` + `php artisan test`; admin `yarn type-check` + `yarn build` + `yarn check:rbac`)
- [ ] Docs updated (this TASK.md set to `done`; index row updated)
- [x] Mobile contract checked — `POST /admin/invitations` is admin-only; no mobile route reads it
