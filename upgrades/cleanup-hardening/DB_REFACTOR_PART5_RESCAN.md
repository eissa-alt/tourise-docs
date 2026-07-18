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
