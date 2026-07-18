# Database Refactor — Part 2: Migration Fold (in place)

Collapse the accumulated `add_*` / `modify_*` / `change_*` / `drop_*` history into each table's original
`create_*` migration, so every table's **final shape** is described in one file. Fewer files, no
"add-column-later" archaeology.

**This is the conservative fold-in-place formula — NOT the dropped wholesale rewrite** (old Tasks
003/004 in [CLEANUP_AND_HARDENING_MASTER_PLAN.md](CLEANUP_AND_HARDENING_MASTER_PLAN.md); dropped because
the wholesale-rewrite process didn't match the goal). Here we edit originals in place and delete the
now-empty follow-ups — we do not regenerate the schema from scratch.

**Runs after [Part 1 removals](DB_REFACTOR_PART1_REMOVALS.md).** Part 1 deletes `zones`, `bulk_prints`,
`guest_utms`, the edgex fields, and the landing layer — so the fold operates on a smaller set and the
per-table fold map (below) is built against the **post-removal** tree, not today's.

**Followed by [Part 3 — Post-Fold Re-scan](DB_REFACTOR_PART3_RESCAN.md)** (confirm the folded set is
clean), then [Part 4 — Model Hygiene](DB_REFACTOR_PART4_MODEL_HYGIENE.md). Any column *type* change model
hygiene turns up (e.g. a column that should be JSON) **folds into the `create_` here** — Part 4 does not
spawn ad-hoc migrations. Part 4 then reconciles `$casts`/`$fillable` against this final schema; Part 5
re-scans once more to close out.

---

## The formula (per table)

1. **Fold forward into the `create_`.** For each domain table, apply every later `add`/`modify`/
   `change`/`rename` to the original `create_<table>_table.php` so it reflects the current final columns,
   types, nullability, defaults, indexes, and uniques. Then **delete** those folded follow-up files.
2. **Net-out columns → never create.** If a column was added and later dropped, remove it from the
   `create` entirely and delete **both** the `add_*` and `drop_*` files. (Part 1 §"Handled by Part 2"
   lists the known net-outs; re-confirm each against the tree.)
3. **`->change()` mutations → final type only.** Fold the final type/nullability into the `create`;
   don't keep the intermediate. Watch columns that were retyped (e.g. `guest_status` → `guest_status_id`
   FK conversions) — the `create` must show the final FK column, and the old string column must be gone.
4. **Multi-table `modify_*` files.** A single `modify_*` migration that touches N tables gets split: its
   changes fold into each of the N `create_` files, then the `modify_*` file is deleted.
5. **Foreign keys.** Part 1's [safe table reordering](DB_REFACTOR_PART1_REMOVALS.md) already put the five
   lookups (`guest_statuses`, `areas`, `roles`, `speaker_labels`, `sponsor_labels`) ahead of their
   dependents, so their FKs (`guest_status_id` ×3, `area_id` ×2, `admins.role_id`, `speaker_label_id`,
   `sponsor_label_id`) now **inline** as `foreignId()->constrained()` in the folded `create_`. The one
   unavoidable **cycle — `admins` ↔ `gates`** — keeps `gates.related_agent` inline and defers
   `admins.gate_id` to a final `…_add_foreign_keys.php`. Also watch pivots / polymorphic /
   self-referencing tables (e.g. `session_interested_users`, badge↔category many-to-many).
6. **Do NOT fold framework-default tables** — keep as their own standard migrations: `users`,
   `password_resets`, `failed_jobs`, `personal_access_tokens`, `jobs`, `sessions`.
   (`session_interested_users` is a **domain** table → *do* fold.)
7. **`down()` hygiene.** Keep correct `down()`s in the final `create_` files even though the workflow is
   `migrate:fresh` (not `refresh`).

## Scope guards

- **Schema-only. Do NOT touch `routes/api.php`, controllers, resources, or models** — casts already
  match post-001/002 (boolean/datetime refactors). If a cast doesn't match a folded final type, fix the
  cast, but no behavioral change.
- **Mobile contract unaffected** — a fold changes migration files only. Re-read
  `../../mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf` only as a sanity check; expect zero endpoint/JSON
  change.
- Do not re-introduce anything Part 1 removed.

## Acceptance gate (stronger than "seed green")

1. **SQL structure diff is EMPTY.** Before starting (on the post-Part-1 tree): `migrate:fresh` → dump
   structure (`mysqldump --no-data --skip-comments` **or** `php artisan schema:dump`) → `before.sql`.
   After the fold: same dump → `after.sql`. **`diff before.sql after.sql` must be empty** (modulo
   `AUTO_INCREMENT`/ordering noise). This is the only proof there's no silent drift in type, nullability,
   default, index, or unique. **Seed-green alone is necessary but NOT sufficient.**
2. `php artisan migrate:fresh --seed` clean (all seeders green — several are schema-coupled:
   `CategorySeeder`, `EmailTemplatesSeeder`, `MigrateEmailContentToEditorJsonSeeder`, …).
3. `git diff routes/api.php` **empty**.
4. `composer qa` green.

## Per-table fold map

**Built at execution, against the post-Part-1 tree** — because Part 1 deletes tables/migrations and
resolves several net-outs, so any map drawn today would be stale. The mechanical inputs are: 71 `create_`
files (domain) + the remaining `add/modify/change/drop` files after Part 1. For each domain table, list:
`create_` target file → the follow-up files folding into it → files to delete → net-out columns to drop.
Produce this table first, get it reviewed, then execute table-by-table with the SQL-diff gate after each
batch.

## Risks / watch-outs

- Silent schema drift → mitigated by the empty-SQL-diff gate.
- FK ordering / cycles → final `…_add_foreign_keys.php` fallback.
- enum/string lengths, JSON/generated columns → fold the exact final definition.
- Retyped columns (string → FK) → ensure the old column is gone and the FK is the only survivor.
- Casts must still match folded final types (they do post-001/002; verify, don't rewrite logic).
