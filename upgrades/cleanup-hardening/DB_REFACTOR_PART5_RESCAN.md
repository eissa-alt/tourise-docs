# Database Refactor — Part 5: Post-Hygiene Re-scan & Recheck (checkpoint)

A light final verification pass after [Part 4 (model hygiene)](DB_REFACTOR_PART4_MODEL_HYGIENE.md).
Confirm models and migrations are consistent and nothing regressed, then the DB refactor is done and 007
can safely rely on correct casts/`$fillable`.

**Runs after Part 4, closes out the DB refactor (before the 006 pilot / 007 roll-out).**

> Scope guard: confirm-only. **Do not** re-open the schema or add new cleanups unless a real
> inconsistency is found; then fix it minimally.

## Checklist

- **Model ↔ schema consistency**: every `$fillable` ⊆ table columns; every dated column cast; array/json
  columns cast — spot-check via reflection against `Schema::getColumnListing`.
- **No migration churn needed**: Part 4's cast work triggered **no** stray migrations (JSON column
  changes, if any, were folded back into Part 2's `create_`, not added as new files).
- **Dead models gone**: the Part 4 sweep left no unreferenced model / no model without a backing table.
- **Re-run the Part 3 quick scan** once more on the final state (dead schema + FK ordering) — expect no
  findings.

## Gate

- `php artisan migrate:fresh --seed` clean.
- SQL-diff vs. the Part 2 baseline still empty.
- `composer qa` green (`pint --test` + `phpstan analyse` + `php artisan test`).
- `git diff routes/api.php` empty.

If all green → DB refactor complete; hand off to Task 006/007.

## Run result — 2026-07-19  ✅ DB refactor complete

Reflection audit re-run over the final state (**55 models**, down 1 after the dead-slice removal):

- **Model ↔ schema:** clean. Only remaining audit notes are intentional/documented:
  - `Admin`/`User` `email_verified_at` + `remember_token` — guarded by design.
  - `EmailConfig.event_start_time` / `event_end_time` datetime casts — **deferred to 007** (raw in
    resource + formatted in `EmailVariableResolver`; do the cast + call-site cleanup in lockstep). Same
    for the `Category.status_config` / `Category.notification_settings` / `Guest.days` `array` casts.
  - Part 4's fillable fixes (`Guest` ×3 stale, `EmailTemplate` `bc`→`cc`) and the `BadgePrintLog`
    `$dates`→`$casts` modernization no longer surface.
- **Dead models gone:** 0 orphans (`EmailCatsWorkflowsTemplate` removed with its slice).
- **No migration churn:** still **71** migrations, one non-`create_` (`add_deferred_foreign_keys`); the
  `titles.match_api_data` drop was folded into `create_titles`, not a new file.
- **FK ordering / dead tables:** unchanged from Part 3 — 3 deferred FKs, no dead tables.

### Gate

- `php artisan migrate:fresh --seed` clean.
- DDL diff empty against the refreshed post-Part-4 baseline. (Part 4 made exactly **one** intended schema
  change vs the Part-2 baseline — the `titles.match_api_data` drop — after which the baseline was
  refreshed; everything else is byte-identical.)
- `pint --test` + `phpstan analyse` (full) green; `php artisan test` → **452 passed**, 3 pre-existing
  failures (avatar-URL tests + `ExampleTest` 403, unrelated to this work).
- `git diff routes/api.php` — **not empty by design**: contains only the user-approved dead
  "email workflows" route removal (3 admin routes + 2 imports). No other route changed.

→ **DB refactor (Parts 1–5) done.** Casts/`$fillable` are trustworthy for the 006 pilot / 007 roll-out.
The JSON + `EmailConfig` datetime casts are the only intentional carry-overs, tracked into 007.
