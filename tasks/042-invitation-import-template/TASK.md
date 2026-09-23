# Task 042 — Invitation import: a sample Excel file, and phones in the form's shape

- **Status:** `in-progress` — code written and gates green, uncommitted, awaiting the owner's review
- **Opened:** 2026-09-22
- **Owner:** —
- **Sub-app(s):** backend + admin
- **Branch(es):** `dev`

## Goal

Invitations → Create → Fill mode **Excel** gets a **Download Excel sample** button under the
dropzone. The file is built by the API on click: the owner's template, its **Title** dropdown
filled with the titles active *right now*, plus per-invitation **CC Emails** and **BCC Emails**.
Phones are stored as the registration form stores them (`+966501234567`). The sample asks for `+`
and the country code, and the import also reads `050…` as Saudi, or a Country Code column when a
file has one. A phone that can't be read as a real number shows red in the file while it's typed,
red in the admin preview straight after upload, and stops the import at Create.

## Scope

- In:
  - per-invitation **BCC** (`invitations.bcc_emails_list`), alongside the existing CC
  - backend `GET /api/admin/invitations/import-template` (`admin.can:invitations,create`), served by
    `App\Services\InvitationImportWorkbook` from `resources/templates/tourise-invitation-import.xlsx`
  - the admin button, and phone normalising on submit (`utils/normalize-imported-phone.ts`)
  - EN + AR strings
- Out:
  - Operations → Import → Import Guests Excel has the same phone problem. The new util can be
    reused there; not done here.
  - The auto-mapper takes the first field whose name the header contains. "CC Emails List" maps to
    `email` and "Title ID" to `title`, so a CC column after Email overwrites the guest's email. The
    sample has neither column; not fixed here.
  - `public/documents/sample_create_invitations.xlsx` and `sample_to_import.xlsx` are linked from
    nowhere and have stale headers. Left in place.
  - How the backend resolves a title by name is unchanged (owner, 2026-09-22: titles don't share
    names; only active titles matter).

## Log

- 2026-09-22 — opened. The owner's draft (`excel_import_fixes/TOURISE_GUEST_IMPORT_TEMPLATE_EMPTY.xlsx`)
  was written for **Operations → Import**. Its instructions describe a Status choice and a "Read
  category from Excel" toggle that this page doesn't have. It has a **Category** column this page
  ignores (the collection has one category, chosen on the page). Its title list was copied from the
  **local** DB (Ambassador, H.H. Prince, …), which isn't production's.
- 2026-09-22 — template: Category column removed (Guests → Title, First Name, Last Name, Email,
  Phone, Company, Job Title). All seven headers auto-map with the existing matcher, so the mappings
  come pre-filled on upload. Instructions (EN + AR) rewritten for Invitations → Create: Quantity must
  equal the row count, creating sends nothing, and an already-registered or repeated email stops the
  import. The sample has **no example rows**, because every row is imported and counts against
  Quantity.
- 2026-09-22 — the service writes the active titles (`is_active`, by `order`, `name_en`) into the
  hidden Lists sheet. It then applies the Guests rules against what it wrote: the Title dropdown
  (`A2:A2001`), the email "@" check, and Phone as text. The template's own validation records aren't
  relied on to survive a PhpSpreadsheet read and re-write.
- 2026-09-22 — phones. The site's field stores E.164, but the import stored whatever the cell held:
  a number cell loses the `+`, a CSV loses the leading `0` too, and people write `00966 …`. Stored
  like that, the phone fails the form's own check when an invitation prefills it, and a **locked**
  invitation leaves the guest unable to fix it. The admin now reads each phone with the site field's
  `wholeNumberDigits` rule (Saudi as the default country), checks it with `libphonenumber-js`
  `isValid()`, and sends E.164. Any row that still fails **blocks the import**, listed by Excel row
  and value, the same way the duplicate-email guard works.
- 2026-09-22 — the owner asked for more guided phone entry and chose **two columns**, plus two extras:
  - **Country Code:** a dropdown written as "Saudi Arabia (+966)", with Saudi Arabia first and then
    A–Z (its source changed the same day, and the column was later taken out of the sample; see
    below). Empty means Saudi. A number that
    starts with `+` or `00` wins over it. A code cell with no digits in it is refused rather than
    guessed.
  - **Red as you type:** conditional formatting on Phone. It turns red when, after spaces, dashes,
    brackets and `+` are removed, something other than digits is left, or there are fewer than 7 or
    more than 17 digits. It adds no data, so empty rows stay empty. The test runs the rule through
    PhpSpreadsheet's calculation engine against sample values.
  - **Check before Create:** the upload preview gains a **Phone as saved** column (the E.164, or the
    cell in red) and a red "N phone(s) to fix" count. The block at Create stays.
  - The Country Code mapping (`country_code`) is added only on this page
    (`InvitationImportProps`). Operations → Import's shared list is untouched.
  - Arabic-Indic digits were offered and not taken.
- 2026-09-22 — the country list first came from the **Countries table**. The owner worried it
  differed from the phone field, and it does. Of the table's 244 countries with a code, **11 aren't
  offered by the phone field** (Netherlands Antilles, Guernsey, Isle of Man, Western Sahara, Mayotte,
  Aland Islands, …). **3 have other codes:** Dominican Republic +1809 and Puerto Rico +1787 against the
  field's +1, and Vatican City +379 against +39. 230 matched. Also, 10 of `ONLY_COUNTRIES`' codes don't
  exist in react-phone-input-2, so the field silently drops them.
  Owner: "rely on react-phone-input-2". The library doesn't export its data and the file is built in
  PHP, so the field's exact list is saved as `resources/templates/phone-field-countries.json`: 233
  countries (library data filtered by `ONLY_COUNTRIES`), with a note on how to regenerate it. It only
  changes when `ONLY_COUNTRIES` or the library does. A test checks its shape (2-letter ISO, 1–4 digit
  code, no duplicates).
- 2026-09-22 — **CC Emails** and **BCC Emails** columns (owner). CC per invitation already existed
  (`cc_emails_list`, added to the template's CC when sent). BCC existed only on the email template.
  The owner chose BCC **everywhere CC is**, so:
  - migration `2026_09_22_000001` adds `invitations.bcc_emails_list` (string, nullable);
  - it is wired through the model, the resource, `store` / `update`, both exports and the send
    (`SendInvitationEmailNotification` adds it to the template's BCC, as it does for CC);
  - in the admin it's on the manual form, the Update info modal and see-more.
  - **The exports' fixed column letters moved:** `COL_TITLE_FROM` AA→AB and `COL_PHONE_FROM` AG→AH.
    `ExportColumnAlignmentTest` pins them; this is the shift that once crashed the export.
  - One rule, `utils/email-list.ts`, now checks every CC/BCC entry point: the manual form, the
    modal and the import. That's the manual form's old rule, plus the column's 255-character limit.
    A bad CC or BCC blocks the import, listed by row.
  - **The auto-mapper was fixed on this page.** The first field whose name the header contained
    used to win, so "CC Emails" mapped to **Email** and overwrote the guest's address; "Title ID"
    became `title`. Now an exact name wins; otherwise the field name the header *ends with*, then
    the longer. So "Company Phone" is Phone and "Company Email" is Email. Across 26 sample headers
    every difference from the old matcher is a fix. Operations → Import keeps its own copy of the
    old matcher.
- 2026-09-22 — **Country Code column taken out of the sample, for now** (owner). The sample is back to
  one Phone column, and its instructions say to *always start with `+` and the country code*,
  with `+966501234567` as the example. The import still reads `050…` as Saudi.
  - `InvitationImportWorkbook` treats Country Code as optional. While a template has that column,
    it writes the phone field's countries and the dropdown, so bringing it back means adding the
    column to the template (scratchpad `make-template.with-country-code.php`), with no code
    change. That branch is untested while the column is absent; `countries()` itself is tested.
  - The admin still reads a Country Code column in any file (test file `08` is a CSV with one).
- 2026-09-22 — the downloaded file opened with **the whole Phone column selected**. PhpSpreadsheet's
  `getStyle($range)` also *selects* the range, and the selection is saved. Every sheet now opens at
  A1, and Guests at A2 (tested).
- 2026-09-22 — no green "number stored as text" triangle on the Phone column (E2:E2001, via
  `IgnoredErrors`) or on the instructions' Phone example. The example itself had silently become
  `966501234567`: PhpSpreadsheet's default binder turned `+966…` into a number when the template was
  built. It's now written as explicit text.
- 2026-09-22 — gates:
  - backend `pint --test` clean; `php artisan test` 843 passed (7 in `InvitationImportTemplateTest`,
    2 new in `InvitationStoreTest`, incl. the sent message's CC/BCC); PHPStan clean on the changed files
  - admin `yarn type-check`, eslint, prettier, `yarn check:rbac` and `yarn build` green
- 2026-09-22 — found, not ours: `composer qa`'s PHPStan step reports 5 `relationExistence` errors
  in `DashboardStatsController` / `RolesController`. They came in with backend `28da7a1` (Task 038),
  not this task.

## Decisions

- **The API builds the file, not a static copy in the admin.** Titles differ per environment and
  change in Management → Titles; any list saved inside a file goes stale somewhere.
- **Active titles only**, in their `order` (owner, 2026-09-22).
- **An unreadable phone blocks the import** (owner, 2026-09-22), matching the manual form, which
  refuses one too.
- A national number is read as **Saudi** unless Country Code says otherwise: the default the admin's
  and the site's phone fields use.
- **Phone is two columns** (owner, 2026-09-22), not one: people pick a country instead of typing a
  code, and the number stays the way they write it.
- **Country Code offers the phone field's countries, not the Countries table** (owner, 2026-09-22).
  The table serves nationality and residence; a phone is joined the way the field stores it.
- The template `.xlsx` is committed, like `tourise-equipment-list.xlsx`. It carries the look and the
  EN + AR instructions, so a revision is made in Excel and the file replaced. The code only fills in
  the lists and the rules.

## Definition of Done

- [ ] Code merged to `dev` in the relevant sub-app(s)
- [x] EN + AR translations in the same commit (`web:download_excel_sample`, `web:phone_as_saved`, `web:phones_to_fix`, `web:bcc_emails_list`, `validation:excel_invalid_phones`, `validation:bcc_emails_list`, `validation:excel_invalid_cc_bcc`)
- [x] Quality gate green (backend `pint --test` + `php artisan test`; admin `yarn type-check` + `yarn build` + `yarn check:rbac`)
- [ ] Docs updated (this TASK.md set to `done`; index row updated; any drift fixed)
- [x] Mobile contract checked — the new route and `bcc_emails_list` are admin-only; nothing mobile calls them
