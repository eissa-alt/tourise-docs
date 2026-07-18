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
- **Dead "email workflows" slice (found in [Part 3 re-scan](DB_REFACTOR_PART3_RESCAN.md)).** A whole
  vertical is dead/broken — the `EmailWorkflow` model does **not exist** yet is imported/used, and no
  `email_workflows` / `email_cats_workflows_templates` tables exist, so its routes fatal on any call.
  Remove together: model `EmailCatsWorkflowsTemplate` (orphan, no table); controllers
  `EmailsWorkflowController` + `EmailsLinkWithCategoriesController`; resources `EmailsWorkflowResources` +
  `EmailsCatsWorkflowsResources`; the 3 admin routes (`GET /admin/email-workflows`,
  `GET`+`PUT /admin/emails-link-with-categories`) and their two `use` imports in `routes/api.php`; the
  stale commented `use App\Models\EmailCatsWorkflowsTemplate;` in `CategoriesController`. Admin-only, not
  in the mobile contract — but it **touches `routes/api.php`**, so get user sign-off first.
  **✅ Done 2026-07-19** — see the "Run result" section below.

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

---

## Run result — 2026-07-19

Reflection audit over all **56 models** (script introspects each model vs the live folded schema:
`$fillable` ↔ columns both ways, `$casts` vs column type). **Boolean-cast coverage is complete** — zero
missing `'boolean'` casts across the 101 `tinyint(1)` columns, confirming the
[Boolean Refactor Plan](BOOLEAN_REFACTOR_PLAN.md) already ran. Findings were small.

### Done now (behavior-neutral hygiene)

- **`Guest.$fillable`** — dropped 3 stale entries with no backing column (Part 1 net-out leftovers):
  `employee_id_number`, `org_size`, `industry_other`.
- **`EmailTemplate.$fillable`** — fixed typo `'bc'` → `'cc'` (the real column is `cc`, already assigned
  directly by `EmailsTemplatesController`; `'bc'` was a phantom).
- **`BadgePrintLog`** — modernized legacy `protected $dates = [...]` → `$casts` with
  `'attempted_at' => 'datetime'` (behavior-identical; `created_at`/`updated_at` cast by default).

### Deferred to 007 (lockstep — response/behavior-affecting, NOT safe as a bare cast add)

These columns are the right type but code hand-rolls their (de)serialization, so adding a cast in
isolation would double-encode/decode or change response shape. Do the cast **and** the call-site cleanup
together under 007's delta tracking:

- **JSON `array` casts:** `Category.status_config`, `Category.notification_settings`, `Guest.days` — each
  is `json_encode`d on write / `json_decode`d on read across `CategoriesController`, `GuestsController`,
  `AuthController`, exports, and resources (incl. **mobile-facing `GuestsResources`** and
  `GuestDraftResource`). Adding `'array'` requires removing every manual encode/decode in the same pass.
- **Datetime casts:** `EmailConfig.event_start_time`, `EmailConfig.event_end_time` (`dateTime` columns) —
  returned raw by `EmailConfigResources` and formatted in `EmailVariableResolver`; a cast changes the
  serialized format, so update those sites in lockstep.

### Done (user-approved 2026-07-19) — dead "email workflows" slice removed

Whole broken slice deleted together (touched `routes/api.php`, admin-only, not in mobile contract):
controllers `EmailsWorkflowController` + `EmailsLinkWithCategoriesController`; resources
`EmailsWorkflowResources` + `EmailsCatsWorkflowsResources` + orphan `EmailsWorkflowSelectResources`;
model `EmailCatsWorkflowsTemplate`; the 3 admin routes + their 2 `use` imports; the stale commented
imports in `CategoriesController` + `GuestsController`; and the 3 now-obsolete `EmailWorkflow`
entries in `phpstan-baseline.neon`.

### Done (user-approved 2026-07-19) — `titles.match_api_data` dropped

Dead column (every read/write was commented out). Folded the drop into `create_titles` (no ad-hoc
migration) and removed the commented refs in `Title`, `TitlesController`, `TitlesResources`, and
`TitleSeeder` (×12). Schema diff vs the Part-2 baseline = exactly this one column removed.

### Noted, not acted on

- **Guarded-by-design** (correctly absent from `$fillable`): `Admin`/`User` `email_verified_at` +
  `remember_token`.

### Gate

- `php artisan migrate:fresh --seed` clean; `pint --test` + `phpstan analyse` green on touched models.
- `php artisan test` → **452 passed**, 3 failures (the same pre-existing avatar-URL / ExampleTest-403
  failures carried since before this work — unrelated).
- `git diff routes/api.php` **empty**.
