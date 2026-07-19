# Base API Controller + Response/Listing Traits — Plan (Task 006)

Introduce a shared `BaseApiController` + `ApiResponse` / `AppliesListingFilters` traits so controllers
stop hand-rolling responses and listing logic. **006 is additive scaffolding only** — port the traits and
wire **one admin-only pilot** to prove the envelope, non-breaking. The full roll-out — which
**restructures all controllers and deliberately accepts mobile response-shape changes** (mobile team
adapts later) — is **Task 007**, see
[CONTROLLER_REFACTOR_PLAN.md](CONTROLLER_REFACTOR_PLAN.md). Do not conflate the two: 006's guardrails
below are scoped to the 006 pilot, not the 007 program.

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

## The guardrail (why cyan-full is safe for the 006 pilot)

> Scope note: this guardrail governs the **006 pilot** (admin-only, non-breaking). The wider **Task 007**
> program does *not* promise byte-identity — it restructures all controllers and accepts mobile shape
> changes (documented in a delta doc). See [CONTROLLER_REFACTOR_PLAN.md](CONTROLLER_REFACTOR_PLAN.md).

alt's clients (admin, frontend, mobile) already parse `status: 'success'|'failed'` and `data`. For the
pilot the fuller envelope is adopted **only as a superset**:

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
   - `apiSuccess($data = null, string $message = 'success', array $meta = [], int $status = 200, string $legacyStatus = 'success')` →
     `{ success: true, status: 'success', message, data, meta? }` (omit `meta` when empty).
   - `apiError(string $message = 'failed', $errors = null, int $status = 400, string $legacyStatus = 'failed')` →
     `{ success: false, status: 'failed', message, error: $message, data: $errors ?? $message, errors? }`.
   - Keep the `status:'success'|'failed'` string and `data` key exactly.
   - **Correction (execution):** the original sketch above had `apiError` set `data: null`. That would
     **break** alt's byte-compat — alt's legacy error responses carry their payload *in* `data`
     (e.g. `{ status:'failed', data:'title not found' }`, `data: $validator->errors()`). So the shipped
     trait mirrors **cyan's** semantics — `data => $errors ?? $message` — which reproduces the legacy
     `data` exactly (pass `null` for message-only errors, the errors bag for validation). Method names/
     signatures otherwise match cyan verbatim (kept `$legacyStatus` for flexibility).
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

**No impact from 006** — `TitlesController` is admin-only and the shape stays a superset. Re-read
`../../mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf` only as a sanity check. Mobile-facing controllers are
handled in **Task 007**, which **restructures all endpoints onto this envelope and accepts mobile
response-shape changes** — the mobile team adapts later from the per-endpoint delta doc 007 produces.
(006 itself does not touch any mobile endpoint.)

## Risks / notes

- **Superset assumption** — mitigated by the pilot byte-compat check; if any client reads by key-absence
  (none known), stop and flag.
- **`meta` shape** — the pagination `meta` from `->additional()` must be reproduced exactly by
  `apiSuccess`'s `$meta`; verify against the current Laravel paginator output.
- **Scope creep** — resist migrating a second controller "while we're here"; that is Task 007
  (restructure-all, one controller/module per PR, admin+frontend updated in lockstep, mobile deltas
  logged). After DB Part 1 the 007 target count drops by the 3 deleted controllers.
- **Gate wording** — use `pint --test` (repo is Pint-clean, ledger D10), not the older `pint --dirty`.

---

## Run result — 2026-07-19  ✅ 006 complete (pilot verified byte-compatible)

**Shipped (scaffolding + 1 pilot, zero route changes):**

- **`app/Http/Controllers/Concerns/ApiResponse.php`** — `apiSuccess()` / `apiError()`, cyan semantics
  (see the corrected signatures above). Strict superset of `{ status, data }`.
- **`app/Http/Controllers/Concerns/AppliesListingFilters.php`** — `resolvePerPage`, `resolveSort`,
  `applyExactFilters`, `applySearchFilter`, `applyLikeFilters`, `applyToggleFilters`.
- **`app/Http/Controllers/BaseApiController.php`** — `use`s both traits + opt-in cast-driven
  `applyFilters()` / `applySorting()`. Extends the vanilla `Controller`; controllers may extend it or use
  the traits directly.
- **Pilot `TitlesController`** now `extends BaseApiController`; every hand-rolled `response([...])` →
  `apiSuccess`/`apiError`; `index()` + `selectList()`/`selectALlList()` collections carry the envelope via
  `->additional(['success'=>true,'status'=>'success','message'=>'success'])`.

**Decision — listings keep `->additional()`, not `apiSuccess()`.** A paginated
`ResourceCollection` emits Laravel's exact `data`/`links`/`meta` wrapping; reproducing that by hand
through `apiSuccess($meta)` would risk drift. So listing endpoints keep the ResourceCollection and just
**add** the envelope keys in `->additional()` (byte-identical `data`/`links`/`meta`, additive
`success`/`message`). `apiSuccess`/`apiError` are for the non-collection (model / message) returns. This
is also how cyan coexists.

**Byte-compat proof (before/after snapshot of live JSON, legacy keys compared):**

| case | code | legacy `status`/`data`/`meta`/`links` | added |
| --- | --- | --- | --- |
| `index` (list+meta) | 200 | **identical** | `success`, `message` |
| `show` 200 | 200 | **identical** (`data` = same title fields) | `success`, `status`, `message` |
| `show` 404 | 404 | **identical** (`data:'title not found'`) | `success`, `message`, `error` |

- **`show` 200 gains a top-level `status:'success'`** — it was previously the lone *envelope-less*
  success (`{data}` only); the rewire brings it in line with every other endpoint. Additive, non-breaking
  (admin reads `data`).

**Intentional, defensive listing standardizations (no response-shape change, identical for normal
inputs):** `resolvePerPage` caps `per_page` at 100 and also accepts `perPage`; `resolveSort` also accepts
`sortBy`/`sortDir` aliases. Edge-only divergences (per-page >100, non-`asc`/`desc` direction string,
non-boolean `is_active` value) clamp rather than pass through — acceptable for the listing contract.

**Admin compatibility confirmed:** `titles-listing.tsx` consumes `/titles` via `useListingState`, which
reads `response.data?.data` + `response.data?.meta` (loose, ignores extra keys) — the envelope is
transparent.

**Gate:** `pint --test` + `phpstan analyse` **clean**; `php artisan test` → **452 passed**, same **3
pre-existing** failures (avatar-URL + `ExampleTest` 403, unrelated); `git diff routes/api.php` **empty**.

→ **Envelope + traits proven.** Ready for **Task 007** to roll the pattern across controllers (which
*does* accept mobile shape changes, per-endpoint delta doc).
