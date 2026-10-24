# Task 054, step 1, revision 3: the CRM on fixed lists (plan)

- **Status:** approved and **built 2026-10-24**, uncommitted on `feat/crm-foundations` (backend, admin). Backend
  `composer qa` green (Pint, PHPStan, 1,369 tests; `CrmContactsTest` 15, `CrmImportTest` 19); admin type-check,
  ESLint, `check:rbac` and `yarn build` (from a copy) green. Needs migration `2026_10_24_000001`, which empties the
  CRM's test data: run on the local `tourise_clean` 2026-10-24 (owner's go), with step 3's photo migration
  `2026_10_22_000002`; the CRM tables are empty. **Not seen in a browser yet.** See *As built* at the end.
- **Branch:** `feat/crm-foundations` in `tourise-backend` and `tourise-admin`; then merged into `testing`.
- **Replaces:** decision 38's "supporting lists" (STEP_1_PLAN.md, revision 2, point 3) for every list the system
  already has. Everything else in revision 2 stays.
- **Research:** the data-match report (`testing_notes/CRM_DATA_MATCH_GAPS` and `_FULL`, 2026-10-22): each list
  field compared with the client's files in `client/CRM_PLAN_V2`.

## Why (the team, 2026-10-22)

Values kept as each file wrote them let wrong data and mismapped content in ("Saudi" beside "Saudi Arabia", one
category spelled three ways), and reports cannot add them up. The CRM uses the system's own lists instead, the ones
guests already use, so the same value is the same everywhere and reporting is clean.

## Decisions (owner, 2026-10-24)

| # | Decision |
|---|---|
| 41 | **A value not on the list refuses the file**, each cell named, as Invitation Channel does today. **No auto-mapping and no assumptions:** only upper/lower case and extra spaces are ignored. "H.E" is not "H.E.", "Russian Federation" is not Russia, "Saudi" is not Saudi Arabia. Files use the system's exact values: the Download sample's dropdowns give them; the client's sheets and old files are cleaned first. |
| 42 | **Source List and List Provided By are short lists the team keeps in CRM Settings** ("Add value" comes back); files must use those values. **History / Source is fixed:** the template's 4 values (TOURISE 2025 Data, External Event, Manual Invitation (2027), Other). |
| 43 | **Delegate, Workforce and Exhibitor wait for the client.** No category is assumed (not even Delegate = General Registration); until they exist, a file naming them is refused. |
| 44 | **The industry list stays in code**, today's 18 (signed off, live on the forms); the backend gets its own copy to check files. The client's new 21 waits for their sign-off, then changes in code everywhere at once. |

## 1. Each field and its list

| Field | The list | Stored on the contact | Matched in a file by |
|---|---|---|---|
| Title | Titles (active) | `title_id` | its English name |
| Company Location | Local / International | `company_location` (key) | its label |
| Gender | Male / Female | `gender` (key) | its label |
| Nationality | Countries (ticked as nationality) | `nationality_id` | the country's English name |
| Country of Residence | Countries (ticked as residence) | `country_id` | the country's English name |
| Region | the country's region | not stored: read from the country | a file's Region column is not read (kept under "From the imports") |
| Sector | Public / Private | `sector` (key) | its label |
| Industry | the 18 industries (code) | `industry` (key) | its English name |
| Sub-industry | that industry's sub-industries | `sub_industry` (key) | its English name; must belong to the industry |
| Seniority Level | the 11 levels | `seniority_level` (key) | its label |
| Category | categories (active) | `category_id` | its English name |
| Sub-category | that category's active sub-categories | `sub_category_id` | its English name; must belong to the category |
| Tier | Tier 1 / 2 / 3 (with View tier, as now) | `tier` (key) | its label |
| History / Source | the 4 fixed values | `history_source` (key) | its label |
| Source List | CRM Settings list | `source_list_value_id` (as now) | its name |
| List Provided By | CRM Settings list | `list_provided_by_value_id` (as now) | its name |

The same columns and keys as on `guests`, so a contact and the guest it becomes hold the same values.

## 2. The import

- Each list cell is matched against its list (case and extra spaces ignored). A value not found is a problem on
  that cell: "*'Saudi' is not on the Nationality list.*" A Sub-category not under the row's Category, or a
  Sub-industry not under its Industry, is a problem too. The file is refused; nothing is created.
- The import never adds a value to any list (it used to create supporting-list values).
- **The Download Excel sample** gets a hidden *Lists* sheet with every list, and each list column a dropdown from
  it. Sub-category and Sub-industry list all their values; the import checks they fit the row's Category and
  Industry.
- Unchanged: required fields, email or mobile, duplicates, PDPL columns, 2,000 rows, the history-kind columns, the
  example row, "From the imports" keeping every cell as the file wrote it.

**Ready option, not built now:** *import the correct rows, skip the wrong ones*. After Check, a second button
imports the clean rows and offers an Excel of the skipped rows, each with its reason, to fix and import again.
Rows go in whole or not at all. About a day's work when the client asks.

## 3. The screens

- **Contact form, table cells, contact window, Edit selected:** each list field a dropdown from its list.
  Sub-category follows the chosen Category, Sub-industry the chosen Industry. Region shows the country's, read-only.
- **Filters:** the same lists (Region filters by the country's region).
- **CRM Settings:** only Source List and List Provided By, with **Add value** back and the on/off switch.
- **Labels:** each value in the admin's language (English and Arabic names from the lists).

## 4. Category limits come back (decision 22)

Contacts now hold a real Category, so the CRM is limited to the admin's own categories as Guests is
(`GuestAccessScope`): the list, the counts, Select all matching, the export later, and every write. This removes
the **CRITICAL** "everyone sees every contact" note (STEP_1_PLAN.md) and its *Before release* line. A Super
Admin still sees all.

## 5. The database

One migration on `crm_contacts`:

- **Add:** `title_id`, `nationality_id`, `country_id`, `category_id`, `sub_category_id` (links to their tables),
  and `company_location`, `gender`, `sector`, `industry`, `sub_industry`, `seniority_level`, `tier`,
  `history_source` (keys).
- **Drop:** the 14 `<list>_value_id` columns now covered by system lists. **Keep** `source_list_value_id` and
  `list_provided_by_value_id`.
- `crm_list_values` keeps only Source List and List Provided By.

**The CRM's data today is test data only** (local and the testing server; production has no CRM). The migration
empties it (contacts, import history, list values) rather than guess a mapping for each test value (decision 41).
After it, the test sets are rebuilt with the system's exact values and imported again.

## 6. Tests

Each list matched and refused (wrong value, wrong parent, inactive value); no value created; Settings lists add
and switch off; the sample's dropdowns; the category limits (list, counts, ids, writes, Super Admin); the
migration. The seven test sets in `crm_import_tests` are rebuilt.

## 7. Waiting on the client (refused until then)

Delegate, Workforce and Exhibitor and their 6 sub-categories; the 21-industry list; the Source List values (the
team adds them meanwhile); the Arabic names of the sub-categories.

## The review (owner, 2026-10-24)

1. The migration **empties the CRM's test data** (local and testing) instead of carrying values across: **yes**.
2. **Category limits (section 4)** come back in this same piece of work, the same per-admin categories as Guests
   and Invitations: **yes**.

## As built (2026-10-24)

What the build added to the plan, or settled on the way:

- **A Category edit carries its Sub-category.** In a table cell, the contact's window and *Edit selected*, changing
  a Category asks for the Sub-category with it, from the new category's own, and saves the two together (an
  Industry its Sub-industry the same). Otherwise every contact with a sub-category would be refused, since the old
  one is not under the new category. *Edit selected* no longer offers Sub-category or Sub-industry on their own.
- **Sub-industry keys repeat under each industry** ("Other" under 17 of them), as the guest forms store them; the
  contact's Industry tells which is meant. The filter lists "Other" once.
- **The filters:** a Sub-category or Sub-industry reads with its parent's name, "Investors (VIP)", since names
  repeat across parents. Region offers the countries' regions as stored ("MENA", "Europe"), as on Guests.
- **Messages:** "*'Saudi' is not on the Nationality list. Use the value as the list writes it.*"; "*'Moderators' is
  not a Sub-category of Category 'Speaker'.*"; a category outside the admin's: "*You cannot use this category.*"
- **The team's two lists are emptied too** by the migration, so after it the team adds its Source List and List
  Provided By values in CRM, Lists before any import. The rebuilt test sets list the values each needs.
- **Inviting is unchanged** (decision 39): the collection still decides the invitation's category, sub-category and
  tier; the contact's own are now the system's, shown beside it.
- **Test sets:** the seven in `crm_import_tests` rebuilt with the system's exact values (local `tourise_clean` on
  2026-10-24), each with a "not on the list" file (`20` in the real-scenario sets, `25` in the others: "H.E",
  "Saudi", "KSA", "Delegate", "Private"…, all refused). Each build checks every list cell against the lists, and the
  checkers load the same lists into the test database.
- **Found in the local data:** two switched-on titles are both named "H.E.", so the sample's Title dropdown shows it
  twice and a file's "H.E." lands on the first by order. Worth tidying in Titles.
