# Task 047: Points of contact on an invitation

- **Status:** `done (code)`: backend `73b3d9c`, admin `ca0cd74`, merged to `dev` on 2026-09-28
  (backend PR #20, admin PR #23), not yet on `main`. Owner browser review pending. **Production
  needs migration `2026_09_27_000001_add_points_of_contact_to_invitations_table`.**
- **Opened:** 2026-09-27
- **Owner:** unassigned
- **Sub-app(s):** backend + admin
- **Branch(es):** `feat/audit-logs-and-invitation-fixes`

## Goal

The client asked for points of contact (POC) on an invitation: whom to reach about a guest, such as an
office manager or an assistant. Up to three, each a **name, a phone and an email**.

## Scope

- In: storing them; entering them in **Manual** mode and in the **Excel** import (and its sample);
  editing them in **Update info**; showing them in **See more**; the two invitation **exports**.
- Out (owner, 2026-09-27):
  - **Nothing is sent to them.** Reference data only: no email, no CC, no event.
  - **They stay on the invitation.** The guest record never receives them, and guest screens and
    exports do not show them.
  - **No bulk editing.** Update invitations (bulk) does not touch them; Update info is the only place
    to change them after creation.
  - The public invitation link (`verify-invitation`) does not return them.

## Log

- 2026-09-27: scoped with the owner. Every field optional, and zero POCs is fine: no POC inputs show
  until **Add POC** is pressed. Flat columns on `invitations` rather than a table or a JSON column,
  since there are never more than three and each maps one-to-one onto an import and export column.
  The owner suggested capping each at 100 characters to stay inside MySQL's row limit; measured, the
  table's declared row was 16,950 of 65,535 bytes (26%), so the columns are sized by what they hold
  instead: **name 150, phone 32, email 255**.
- 2026-09-27: **backend** (`73b3d9c`).
  - Migration `2026_09_27_000001`: nine nullable columns after `bcc_emails_list`,
    `poc_{1,2,3}_{name,phone,email}`.
  - Create (`guests_list.*.poc_*`) and Update info (`PUT /admin/invitations/{id}/details`) validate them
    through `Invitation::pocRules()`: email format, phone in E.164, and the column lengths.
  - `InvitationResource` returns them for the admin. `verify-invitation` lists its own fields and
    leaves them out (tested).
  - Both invitation exports add **POC 1 to 3 Name / Phone / Email at the end, before Created At**
    (owner), phones forced to text so the `+` survives. `ExportColumnAlignmentTest` pins those letters.
  - The import sample gains the nine columns after BCC Emails: POC phones as text that turn red, POC
    emails with the "@" check, and rows in the instructions' columns table. Rebuilt with
    `excel_import_fixes/tools/make-template.php`. The workbook service finds them by heading and
    treats them as optional, like Country Code.
- 2026-09-27: **admin** (`ca0cd74`).
  - **Manual card:** Guest language moves into the card header (compact, scoped to that one select),
    which leaves the grid three rows of three. Below it, **Add POC** opens one contact per press, up to
    three; **×** removes one and moves the later ones up. A contact left empty is dropped on save, and
    a phone holding only its country code counts as no phone.
  - `PointsOfContactFields` is the one block for the Manual card and the **Update info** dialog, at the
    guest grid's compact size. **See more** shows a "POC N" row for each contact holding anything.
  - **Excel:** "POC 1 Name" … "POC 3 Email" map by their exact names, and **any heading starting "POC"
    only ever maps to a POC field**. Read as the guest's, a column headed "POC Email" would have
    overwritten the guest's own address. The preview marks a bad POC email or phone and an over-long
    value red, and Create lists them in the problems dialog. POC phones are normalised like the guest's,
    with no country assumed. One more note line above the dropzone.
- 2026-09-27: **found on the way:** Laravel Excel leaves an export's value binder installed
  process-wide. After the new export test, a template test that writes a scratch formula into column
  Z (now a POC column of the export) read it back as text, in the full suite only. The export test
  restores the binder, and the template test writes that formula explicitly as a formula.
- 2026-09-27: test files: `excel_import_fixes/test-cases/poc/` (5 files and a README, built by
  `tools/make-poc-cases.php`), and `simulate.js` checks the POC rules. Every older test file reads the
  same with the new sample columns.
- 2026-09-27: gates: backend `pint --test` clean, `php artisan test` 912 passed, PHPStan unchanged at
  the 6 errors that predate this work; admin `yarn type-check`, eslint, prettier and `yarn check:rbac`
  green. `yarn build` not run: the owner's dev server held `.next`.

## Decisions

- **Up to three POCs, every field optional** (owner).
- **Reference data only; nothing is sent to them** (owner).
- **Invitation only**: not copied to or shown on the guest (owner).
- **Edited in Update info only**, not in bulk (owner).
- **Export: at the end, before Created At** (owner). The import sample keeps them after BCC Emails,
  next to the guest's own columns.
- **No country is assumed for a POC phone**, as for the guest's in the import (Task 042). The Country
  Code column applies to the guest's phone only.
- POC edits appear in the invitation's audit history like any other field (Task 045).

## Definition of Done

- [x] Code merged to `dev` in the relevant sub-app(s)
- [x] EN + AR translations in the same commit
- [x] Quality gate green (backend `pint --test` + `php artisan test`; admin `yarn type-check` + `yarn check:rbac`; `yarn build` pending)
- [ ] Docs updated (this TASK.md set to `done`; index row updated)
- [x] Mobile contract checked: the routes touched are under `/api/admin`, and the public `verify-invitation` answer is unchanged
