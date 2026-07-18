# Database Refactor — Part 4: Model Hygiene & Cast Unification

Bring every Eloquent model into line with the **final folded schema** (Part 2, re-confirmed clean in
Part 3): correct casts, accurate `$fillable`, sane relations/methods, and no dead model files. This is
model-file work, the natural continuation of the schema work — and a **hard prerequisite** for the
controller refactor.

**Why this is a prerequisite, not just hygiene.** The 006 `BaseApiController::applyFilters()` that
[Task 007](CONTROLLER_REFACTOR_PLAN.md) rolls out reads each model's `$casts` + `$fillable` to choose the
filter operator (boolean → exact, numeric → exact, else → `LIKE`) and to whitelist sortable columns. If
casts/fillable are wrong, generic filtering and sorting misbehave. So Part 4 runs **after the Part 3
re-scan confirms the folded schema is clean** and **before 007 Tier-A work begins.**

**Sequencing:** DB Part 1 (removals) → DB Part 2 (fold) → DB Part 3 (post-fold re-scan) → **DB Part 4
(this)** → DB Part 5 (post-hygiene re-scan) → 006 pilot (independent, can land earlier) → 007 roll-out.

---

## Scope

All models in `alt-static-basecode-backend/app/Models`. Per model, run the checklist below. Backend-only
except where a cast change forces a controller update (feed those into 007 / do in lockstep) or a column
type change (fold into Part 2, **no ad-hoc migration**).

## Checklist (per model)

### A. Casts

- **Boolean casts → owned by [BOOLEAN_REFACTOR_PLAN.md](BOOLEAN_REFACTOR_PLAN.md), not duplicated here.**
  Part 4 only *verifies* every boolean column has its `'boolean'` cast after that plan runs; it does not
  re-plan the boolean conversion. Reconcile the two so there is one owner.
- **Datetime/timestamp casts** — add `'datetime'` (or `:format`) casts for every date/datetime column
  missing one. If a controller currently hand-formats that field, update it → **007 or lockstep**.
- **Array/JSON casts** — add `'array'` / `'json'` casts for JSON columns. If a column *should* be JSON
  but isn't yet, that column-type change **folds into Part 2** (edit the `create_`), never a new
  migration.

### B. `$fillable` vs DB (both directions)

- Every `$fillable` attribute maps to a real column in the folded schema (drop stale entries — e.g.
  anything left over from the Part 1 removals or net-outs).
- Every non-system column is either in `$fillable` or intentionally guarded (document the intent for
  guarded columns).
- Note: `applyFilters`/`applySorting` treat `$fillable` as the allow-list for filtering/sorting — so an
  over-broad `$fillable` widens the filter surface. Keep it tight and correct.

### C. Relations & methods

- Add missing relations that the code already assumes; remove dead relations/accessors/scopes with zero
  references.
- Verify relation return types and foreign keys match the folded schema (esp. the columns the fold
  retyped, e.g. `*_status_id` FKs).

### D. Dead models → delete

- Full usage sweep (grep model class + `::` + relation references + `DB::table`). Delete models with no
  backing table and no references.
- `EmailContent` is already slated in [DB Part 1 §7](DB_REFACTOR_PART1_REMOVALS.md); Part 4 does the
  complete sweep for any others.

## Validation / gates

- `php artisan migrate:fresh --seed` clean on the folded schema (casts don't break seeders).
- A quick reflection check: for each model, `$fillable` ⊆ table columns and every dated column is cast
  (a tinker/one-off script or a test asserting model casts vs `Schema::getColumnListing`).
- Any controller touched by a cast change is updated and its tests green (or the change is deferred into
  007 with a note).
- `composer qa` green (`pint --test` + `phpstan analyse` + `php artisan test`).
- `git diff routes/api.php` **empty**.

## Risks / notes

- **Cast change = behavior change.** Adding a `'boolean'`/`'datetime'`/`'array'` cast changes what a
  model attribute returns and what a resource emits — which can ripple into responses (a 007 concern).
  Sequence cast changes so their controller/response impact is captured by 007's delta tracking, not
  silently shipped.
- **Boolean overlap** — do not double-implement; Boolean Refactor plan owns the conversion, Part 4 only
  verifies coverage.
- **JSON column changes fold into Part 2** — keep the "no ad-hoc migrations" rule intact.
- Keep `$fillable` tight — it is now also the filter/sort allow-list under 007.
