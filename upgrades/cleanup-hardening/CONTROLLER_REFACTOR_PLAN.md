# Controller Refactor — Response Unification + Listing Standardization (Task 007)

Roll the [006 scaffolding](BASE_API_CONTROLLER_PLAN.md) across **all** controllers: every response goes
through the standard `apiSuccess`/`apiError` envelope, and every index endpoint adopts the
`AppliesListingFilters` + cast-driven `applyFilters`/`applySorting` conventions. This is the full
program 006 piloted.

**Locked formula (agreed):**
1. **Restructure all controllers** — Tiers A/B/C, nothing capped or parked.
2. **Breaking the mobile response contract is accepted** — the mobile team adapts later. **We generate a
   per-endpoint delta doc** (old shape → new shape) so they can.
3. **Admin + frontend are updated by us, in lockstep** — they live in this repo set; any shape change to
   an endpoint they consume is fixed in the *same* PR. Only **mobile** is "adapt later."
4. **Scope = envelope + listing/sorting trait** (not envelope-only). This is the one extra cyan
   best-practice worth bringing (cast-driven filtering + whitelist sorting). FormRequests and wholesale
   service extraction are **out** (cyan doesn't use FormRequests; its extra services are feature-specific
   or the banned form-builder; upload logic is the separate Todo-2D `UploadService`).
5. **One controller/module per PR**, never batched.
6. **Deviation ledger:** this supersedes the master plan's cautious "migrate only where byte-identical,
   never break mobile" 007 (Todo-2C). Record the reversal (restructure-all + accept mobile break) as a
   ledger entry.

---

## Prerequisites (ordering)

1. **006 shipped** — traits + `BaseApiController` exist and the pilot proved the envelope.
2. **DB Refactor Part 1 + Part 2 done** — 3 controllers deleted (`Zones`/`BulkPrint`/`LandingPage`);
   folded schema is stable.
3. **DB Refactor Part 4 (Model hygiene) done** (and Part 5 re-scan green) — **hard prerequisite for the
   cast-driven filtering.** `applyFilters()` reads each model's `$casts`/`$fillable`; if those are wrong,
   generic filtering misbehaves. See [DB_REFACTOR_PART4_MODEL_HYGIENE.md](DB_REFACTOR_PART4_MODEL_HYGIENE.md).

## The target shapes (from 006)

- `apiSuccess($data, $message, $meta, $status)` → `{ success, status, message, data, meta? }`
- `apiError($message, $errors, $status)` → `{ success, status, message, error, data, errors? }`

Flat/ad-hoc responses get wrapped under `data` — **this is the intended breaking change** for whatever
parses the current flat shape (mobile). `status`/`data` are retained so admin/frontend (superset readers)
keep working; where a client reads a *flat* payload, we update it (admin/frontend) or log it (mobile).

## Risk tiers → migration order

| Order | Tier | Controllers | Client work in the same PR |
|---|---|---|---|
| 1st | **A — admin-only** | `Titles` (done in 006), `GuestStatuses`, `Areas`, `EventDays`, `SocialMediaLinks*`, `Admin*` (media/publication/notification/session/workshop), `Roles`, `SmsTemplates`, `EmailsConfigs/Templates`, `Badges`, `Categories` (admin), `Gates`, `Scans`, `Dashboard`, … | admin only, if any |
| 2nd | **B — public-frontend-facing** | `AuthController` (register/login), `CountryController`, `GuestsController` (register/accept/reject/invitation), `Categories` (public form) | **frontend updated in lockstep** |
| 3rd | **C — mobile-facing** | all `Mobile*` (~15), `MobileAuthController`, mobile-hit slices of `GuestsController`/`AuthController` | **no client change — log deltas** |

`GuestsController` is the giant (~230 sites, spans B + C) — split its migration by endpoint group
(admin CRUD vs public register/accept/reject vs mobile), not all at once.

## The mobile delta doc (the "adapt later" artifact)

Maintained as endpoints are migrated — e.g. `docs/mobile/RESPONSE_SHAPE_DELTAS.md`:

- One row per mobile-facing endpoint: method + path, **old shape**, **new shape**, the key that moved
  (usually "payload now under `data`", "added `success`/`message`").
- Cross-checked against `../../mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf`.
- This is the hand-off the mobile team consumes; without it, "adapt later" has nothing to work from.

## Per-PR workflow (per controller/module)

1. Rewire responses → `apiSuccess`/`apiError`; rewire index → `resolvePerPage`/`resolveSort` +
   `applyFilters`/`applySorting` (or the granular filter helpers).
2. If Tier B: update the frontend consumer(s) in the same PR (unwrap under `data`, etc.).
3. If Tier C: add/append the endpoint's row(s) to the mobile delta doc.
4. Update backend tests to the new shape.
5. Gates (below) → commit `P<phase>.<task> — unify <Controller> responses`.

## Gate (replaces 006's "byte-identical")

- Every touched response conforms to the standard envelope.
- Backend feature tests updated & green (`php artisan test`).
- `composer qa` green (`pint --test` + `phpstan analyse` + `php artisan test`).
- **Admin/frontend updated in lockstep** where consumed → their `yarn type-check` + `yarn production`
  green.
- **Mobile deltas logged** for every Tier-C endpoint touched.
- `git diff routes/api.php` **empty** — this is a response refactor, not a routing change.

## Risks / notes

- **Breaking mobile is intentional but must be *tracked*** — an untracked shape change is the failure
  mode. The delta doc is the mitigation; treat a missing delta row as a broken build.
- **`GuestsController` blast radius** — 230 sites, mixed tiers; migrate in small endpoint-group PRs.
- **Cast dependency** — do not start Tier work before Part 4 model hygiene lands, or `applyFilters`
  will filter wrongly.
- **Lockstep discipline** — a Tier-B PR that changes shape without the matching frontend edit is
  incomplete; keep them atomic.
