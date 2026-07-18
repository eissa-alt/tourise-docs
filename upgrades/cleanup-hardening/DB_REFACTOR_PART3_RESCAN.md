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
  appeared, and the `admins`↔`gates` cycle is the only deferred FK.
- **One create per domain table**: confirm every domain table is described by a single `create_` (no
  stray leftover `add_/modify_/change_/drop_` for a domain table); framework tables untouched.
- **Migration count** dropped roughly as expected vs. the pre-fold count.

## Gate

- `php artisan migrate:fresh --seed` clean.
- Part 2's **empty SQL-diff** still holds (no drift introduced by any touch-up here).
- `git diff routes/api.php` empty.

If all green → proceed to Part 4. If a real issue surfaces → fix it minimally (fold it in / delete it),
re-run the gate, then proceed.
