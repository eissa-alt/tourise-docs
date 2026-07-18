# Base API Controller + Response/Listing Traits — Plan (Task 006)

Introduce a shared `BaseApiController` + `ApiResponse` / `AppliesListingFilters` traits so controllers
stop hand-rolling responses and listing logic. **Additive only** — port the scaffolding and wire **one
pilot** controller to prove byte-compatibility; the other controllers are migrated later in **Task 007**
([CLEANUP_AND_HARDENING_MASTER_PLAN.md](CLEANUP_AND_HARDENING_MASTER_PLAN.md), Todo-2B → 2C).

**Locked formula (agreed):**
1. **Trait source:** author **lean alt-native** traits from the documented signatures, matching cyan's
   method names for future parity — **no cross-repo dependency** on `cyan-backend`.
2. **Envelope:** adopt cyan's fuller `{ success, status, message, data, meta }` shape — **as a strict
   superset** of alt's current `{ status, data }` (see the guardrail below).
3. **Pilot:** `TitlesController` (small, admin-only, untouched by the DB refactor).
4. **Scope:** scaffolding + 1 pilot only; **zero** other call-site rewrites (those are Task 007).

---

## Current state

- **Base `Controller` is vanilla** — only `AuthorizesRequests, DispatchesJobs, ValidatesRequests`; no
  shared response or listing helpers.
- **Three response styles coexist**, hand-rolled per controller:
  - Resource `->additional(['status' => 'success'])` on listing/collection endpoints (~40 controllers) →
    `{ data: [...], meta: {pagination…}, status: 'success' }`.
  - Raw `return response([...], code)` — the dominant style, **hundreds** of sites (GuestsController 185,
    Invitations 38, Gates 33, MobileRoom 24, …) → `{ status: 'success'|'failed', data: … }`.
  - `response()->json([...])` — ~100 ad-hoc sites (Guests 45, Invitations 21, Dashboard 11, …).
- **Listing/filtering is hand-rolled** per controller: `->paginate($perPage)` + inline `where` / `like`
  filters, no shared resolver.

## The guardrail (why cyan-full is safe here)

alt's clients (admin, frontend, mobile) already parse `status: 'success'|'failed'` and `data`. The fuller
envelope is adopted **only as a superset**:

- `apiSuccess()` → `{ success: true, status: 'success', message, data, meta? }` — `status` + `data` stay
  byte-identical to today; `success`/`message` are additive; **`meta` keeps the exact pagination shape**
  the current `->additional()` listings emit.
- `apiError()` → `{ success: false, status: 'failed', message, error, data, errors? }` — `status` +
  `data` preserved; the rest additive.

If any client depends on the *absence* of keys, that's a break — but none do (they read by key). The
pilot proves this empirically before we go further.

## Scope

**In:** `app/Http/Controllers/Controller.php` (or a new `BaseApiController`), two `Concerns` traits, and
**only** `TitlesController` rewired to use them.

**Out:** every other controller (Task 007), any route change, any model/resource change, any admin/
frontend change.

## Prerequisites

- DB Refactor Part 1 relationship: the pilot (`TitlesController`) is **not** touched by the removals, so
  006 can proceed independently of the DB refactor. Do **not** pick `CountryController` (edited by DB
  Part 1) or `Zones`/`BulkPrint`/`LandingPage` controllers (deleted by DB Part 1) as pilots.
- Baseline green: `composer qa` passing on the current tree.

## Implementation plan

1. **`Concerns/ApiResponse` trait** (alt-native, cyan method names):
   - `apiSuccess($data = null, string $message = '', array $meta = [], int $status = 200)` →
     `{ success: true, status: 'success', message, data, meta? }` (omit `meta` when empty).
   - `apiError(string $message = '', array $errors = [], int $status = 400)` →
     `{ success: false, status: 'failed', message, error: $message, data: null, errors? }`.
   - Keep the `status:'success'|'failed'` string and `data` key exactly.
2. **`Concerns/AppliesListingFilters` trait** (alt-native, cyan method names): `resolvePerPage`,
   `resolveSort`, `applyExactFilters`, `applySearchFilter`, `applyLikeFilters`, `applyToggleFilters` —
   thin wrappers over the query builder mirroring the current inline patterns (no behavior change).
3. **`BaseApiController`** using both traits; optional generic `applyFilters()` / `applySorting()`
   convenience over the listing trait. Controllers may extend it or keep extending `Controller` and use
   the traits directly — decide during the pilot, keep it minimal.
4. **Pilot: `TitlesController`** — rewire its index (listing + pagination + filters) and its
   success/error returns to the trait methods, **emitting the identical JSON** the admin already parses.

## Validation / gates

- **Pilot JSON is byte-compatible:** snapshot `TitlesController`'s current responses (index list + meta,
  a 200 success, a 404 "not found") → after the rewire, `status` + `data` + pagination `meta` are
  identical; only additive `success`/`message` appear.
- `TitlesController`'s existing tests green.
- The admin titles listing/CRUD screen still parses `{ status, data, meta }` identically (runtime check).
- `composer qa` (`pint --test` + `phpstan analyse` + `php artisan test`) green.
- `git diff routes/api.php` **empty** — 006 touches no routes.

## Mobile contract

**No impact** — `TitlesController` is admin-only and the shape stays a superset. Re-read
`../mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf` only as a sanity check. Mobile-facing controllers are
explicitly deferred to Task 007, migrated last and JSON-diffed per endpoint.

## Risks / notes

- **Superset assumption** — mitigated by the pilot byte-compat check; if any client reads by key-absence
  (none known), stop and flag.
- **`meta` shape** — the pagination `meta` from `->additional()` must be reproduced exactly by
  `apiSuccess`'s `$meta`; verify against the current Laravel paginator output.
- **Scope creep** — resist migrating a second controller "while we're here"; that is Task 007, which is
  incremental and per-module JSON-diffed. After DB Part 1 the 007 target count drops by the 3 deleted
  controllers.
- **Gate wording** — use `pint --test` (repo is Pint-clean, ledger D10), not the older `pint --dirty`.
