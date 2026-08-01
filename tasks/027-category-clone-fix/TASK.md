# Task 027 — Category cloning copies all settings

- **Status:** `done (code)` — manual browser QA pending
- **Opened:** 2026-07-28
- **Owner:** —
- **Sub-app(s):** backend
- **Branch(es):** `dev`

> **Phase-number note:** admin `af2a24a` is also stamped `P027.1`, but it is unrelated work — the
> run-neutral automation wording. It belongs with [task 031](../031-automation-manual-run/TASK.md) and is
> logged there. This folder covers the backend clone fix only.

## Goal

Make "clone category" produce a genuine copy. The old implementation copied only part of the row and
none of the category's related records, so a cloned category came up missing settings the admin had to
re-enter by hand.

## Scope

- In: `CategoriesController::clone` — column copy, badge assignments, admin data scope, meeting-room
  links, share-poster files.
- Out (unchanged on purpose): the slug/name copy behaviour (`{slug}-copy`, `-copy-1`, … and
  `(Copy)` / `(نسخة)` appended to the names) and the `titles.cat_list` update.

## Decisions

- **`replicate()` instead of `getAttributes()` + `fill()`.** The old path ran the attribute array through
  `fill()`, so **any column missing from `$fillable` was silently dropped** — and the fix has to hold for
  columns added later, not just today's. `replicate()` copies every column regardless of `$fillable` and
  resets id/timestamps for us. This is the durable half of the fix (ledger D46).
- **Whole clone runs in one `DB::transaction`.** A clone now writes to five places; a partial clone would
  leave an orphan category with half its relations.
- **Poster files are duplicated, never shared.** `duplicatePoster()` copies each share-poster to a fresh
  random basename on the public disk, so editing or deleting one category's poster can never affect the
  other. If the referenced file is missing on disk, the original name is returned unchanged (nothing to
  copy) rather than failing the clone.
- **Related records copied:** badge assignments (`badge_category` pivot, via the Eloquent relation),
  admin data scope (`admins.category_ids` — a JSON column, no pivot, so it reuses the existing
  `adminsWithCategory()` / `syncCategoryAdmins()` helpers), and meeting-room links
  (`meeting_room_categories` — no Eloquent relation on `Category`, so the rows are inserted directly).
- **Admin scope is copied, i.e. the clone is visible to every admin who could see the original.** That is
  the intent ("a copy of this category"), but it means a clone inherits its source's visibility rather
  than starting private — worth knowing before cloning a category with a wide scope.

## Log

- 2026-07-28 — backend `0be944e` (`P027.1`): `CategoriesController.php`, +94/−41, plus the new private
  `duplicatePoster()` helper.
- 2026-08-01 — documented (this file, index row, ledger D46, handoff).

## Definition of Done

- [x] Code merged to `dev` in the relevant sub-app(s)
- [x] EN + AR — no user-facing strings
- [x] Quality gate — pint clean at commit time (pre-commit hook); **`composer qa` not re-run since**
      (see handoff)
- [x] Docs updated (this TASK.md; index row; ledger D46; handoff)
- [x] Mobile contract unaffected — `/admin/categories`, `routes/api.php` untouched
- [ ] Manual browser QA — clone a category that has badges, a meeting room, both share posters and a
      restricted admin scope; confirm all five carry over and that the two posters are separate files
- [ ] No automated test covers `clone` — worth adding alongside the QA
