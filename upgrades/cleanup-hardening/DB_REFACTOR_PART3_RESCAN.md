# Database Refactor — Part 3: Post-Fold Re-scan & Recheck (checkpoint)

A light verification pass, not a new workstream. After [Part 2](DB_REFACTOR_PART2_FOLD.md) the migration
set is much smaller and cleaner, so cheaply **re-run the Part 1 scans** to confirm nothing else is dead or
mis-ordered before moving to model hygiene.

**Runs after Part 2 fold, before [Part 4 (model hygiene)](DB_REFACTOR_PART4_MODEL_HYGIENE.md).**

> Scope guard: this is a confirm-only pass. **Do not** expand scope or invent new cleanups here — if
> something real surfaces, do a small targeted fix; otherwise proceed.

## Checklist

- **Re-scan for dead schema** on the folded set (easier now): any table/column with zero references that
  the first pass missed? (Re-use the [Part 1](DB_REFACTOR_PART1_REMOVALS.md) method.)
- **Re-check FK ordering**: confirm the 5 reordered lookups inlined correctly, no new backward FK
  appeared, and the deferred-FK set is exactly the expected one (the `admins`↔`gates` cycle plus the two
  `categories`→`email_templates` backward refs — see the [Part 2 §5 note](DB_REFACTOR_PART2_FOLD.md)).
- **One create per domain table**: confirm every domain table is described by a single `create_` (no
  stray leftover `add_/modify_/change_/drop_` for a domain table); framework tables untouched.
- **Migration count** dropped roughly as expected vs. the pre-fold count.

## Gate

- `php artisan migrate:fresh --seed` clean.
- Part 2's **empty SQL-diff** still holds (no drift introduced by any touch-up here).
- `git diff routes/api.php` empty.

If all green → proceed to Part 4. If a real issue surfaces → fix it minimally (fold it in / delete it),
re-run the gate, then proceed.

## Run result — 2026-07-19

**Schema/structure: clean.**

- **Structure:** 71 migrations, exactly **one** non-`create_` file
  (`2026_07_18_000002_add_deferred_foreign_keys.php`); every domain table has a single `create_`. Count
  `126 → 71` as expected.
- **Deferred FKs = 3 (as expected):** `admins.gate_id` (cycle), `categories.e_badge_email`,
  `categories.missing_data_email`. The 5 reordered lookups all inline; none wrongly deferred.
- **Dead tables:** none. All 70 tables are model-backed (56 models incl. convention-mapped ones),
  framework (`jobs`, `failed_jobs`, `password_resets`, `personal_access_tokens`, `sessions`), or pivots.
- **Gate:** `migrate:fresh --seed` clean; no migration file changed since Part 2 → empty DDL diff still
  holds; `git diff routes/api.php` empty.

### Finding → handed to Part 4 (not fixed here — out of confirm-only scope)

A **dead / broken "email workflows" feature slice** surfaced. It cannot execute: the `EmailWorkflow`
model **does not exist** yet is imported/used, and neither `email_workflows` nor
`email_cats_workflows_templates` tables exist. Any hit to its routes fatals. Full slice:

- **Routes** (`routes/api.php`, admin-only, not in the mobile contract): `GET /admin/email-workflows`,
  `GET /admin/emails-link-with-categories`, `PUT /admin/emails-link-with-categories` (+ the two `use`
  imports).
- **Controllers:** `EmailsWorkflowController`, `EmailsLinkWithCategoriesController`.
- **Resources:** `EmailsWorkflowResources`, `EmailsCatsWorkflowsResources`.
- **Model:** `EmailCatsWorkflowsTemplate` (orphan — no backing table); references a nonexistent
  `EmailWorkflow`.
- **Stale import:** commented `use App\Models\EmailCatsWorkflowsTemplate;` in `CategoriesController`.

This is a dead-endpoint + dead-model removal (touches `routes/api.php`), so it belongs to
[Part 4 §D](DB_REFACTOR_PART4_MODEL_HYGIENE.md) rather than the confirm-only fold pass — needs user
sign-off before deleting routes.
