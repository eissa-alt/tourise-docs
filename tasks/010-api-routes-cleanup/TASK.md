# Task 010 — api.php cleanup & route organization

- **Status:** `todo`
- **Opened:** 2026-07-19
- **Owner:** —
- **Sub-app(s):** backend (+ admin verification for Tier 3)
- **Branch(es):** `dev` (+ feature branch recommended for Tier 3)

## Goal

Bring `alt-static-basecode-backend/routes/api.php` up to the cyan-basecode standard: remove dead
code + duplicate registrations, organize the flat admin block into `Route::prefix()->group()` blocks,
add `->whereUuid('id')` constraints, and roll out per-feature `admin.can:` RBAC gating. Today our file
is **966 lines** of mostly-flat, largely-ungated routes; cyan's is **559 lines**, fully grouped and
gated. The mobile section and the ported admin-modules section are already clean — this task targets
the legacy admin block (roughly lines 176–672).

## Reference

- Cyan baseline: `/Users/admin/Projects/ALT/115-cyan-basecode/cyan-basecode-repos/cyan-backend/routes/api.php`
  — the target shape (prefix+`admin.can:` groups, `whereUuid`, no dupes, no dead code, tidy lookups block).
- Ours: `alt-static-basecode-backend/routes/api.php`.
- **`routes/api.php` is also the mobile contract** — see `../../mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf`
  and `../../mobile/RESPONSE_SHAPE_DELTAS.md`. **Do not change any `mobile/*` URI.**

## Scope

- **In:** the legacy admin protected block (`~176–672`) + the two public/sensitive blocks' dead comments.
  Cleanup, reorganization, `whereUuid`, and `admin.can:` gating.
- **Out (explicitly NOT this task):**
  - Renaming non-RESTful admin paths to cyan's RESTful shape (`/admin/guests-new` → `/admin/guests`,
    `/admin/guests-update/{id}`, `-select` suffixes, etc.). That breaks the admin frontend for no
    functional gain — kept as a **deliberate deviation**.
  - Any `mobile/*` route (URIs are the mobile contract; that section is already clean).
  - Controller response-body changes (that was the response-unification work, ledger D22).

## Todo (ordered safest-first)

### Tier 0 — pure cleanup (zero contract change)
- [ ] Delete dead commented-out routes (e.g. `~93, 150, 159–163, 173, 201, 340–348, 356–366, 453, 471–472, 487, 505, 635–638`).
- [ ] Remove exact duplicate registrations: gates `store` (269–270), titles `store` (322–323),
      email-templates `store` (373–374), badges `store` (546–547), emails-config `show` (351/353),
      print-logs pair (533–534 vs 670–671).
- [ ] Strip `// todo move it`, `// ???`, `// todo: move ?` and similar noise comments.

### Tier 1 — dead-endpoint removal (grep admin + mobile usage first, then drop route + orphaned controller method)
- [ ] Legacy `guests-status-*` block (455–461): `guestStatusOverAll/Categories/Badges/Other`,
      `getGuestChartData`, `printedCategoriesByDaysStatus`. **Confirmed not referenced in admin** (the
      dashboard uses `DashboardStatsController`), and includes the malformed paths
      `guests-status-catagories` (typo) and `guests-status-other␣␣` (trailing spaces). Remove block + methods.
- [ ] Verify-then-remove other likely-dead endpoints: `send-sms/{id}` (cyan already deleted `sendSMS`
      as dead legacy), `print-test`, `send-e-badge-test`, `export-test`, `accept-with-days`.

### Tier 2 — organization (no URI change — final paths stay byte-identical)
- [ ] Fold flat `/admin/<resource>/...` routes into `Route::prefix('admin/<resource>')->group()` blocks
      mirroring cyan's layout. Verify with a before/after `php artisan route:list` diff — the route
      table must be identical except ordering.
- [ ] Within each group, order static routes before `/{id}` wildcards (avoid wildcard collisions).

### Tier 3 — hardening (behavior change — needs admin-frontend verification; land last)
- [ ] Add `->whereUuid('id')` (and `whereUuid` on other UUID params) to `{id}` routes, cyan parity.
- [ ] Roll out `admin.can:<feature>` middleware to the ungated admin block, mirroring cyan's per-feature
      gating. Cross-check every feature against `RolesController::catalog` (permission-catalog) + the
      admin frontend's permission checks so no in-use admin loses access. Biggest/riskiest item.

## Verification gates

- After **every** tier: `php artisan route:list` diff (Tier 0–2 must be URI-identical bar ordering),
  `pint --test`, `phpstan analyse`, `php artisan test`.
- `git diff` on the `mobile/*` and `Route::middleware('signed')` sections must be **empty**.
- Tier 3: manual admin smoke test per gated feature (or confirm against the role matrix + frontend).

## Log

- 2026-07-19 — opened. Compared our `api.php` (966 lines, flat/ungated legacy admin block) against
  cyan (559 lines, fully grouped + `admin.can:` gated + `whereUuid`). Confirmed the `guests-status-*`
  block is dead (no admin references). Scope set to **all tiers** per user. Not yet started.

## Decisions

- **Keep non-RESTful admin path names** (`/admin/guests-new`, `/admin/guests-update/{id}`, `-select`
  suffixes) — renaming to cyan's RESTful shape would break the admin frontend contract for no
  functional gain. Deliberate deviation from cyan.
- **`mobile/*` URIs are frozen** — the mobile contract; only the legacy admin block is in scope.

## Definition of Done

- [ ] Code merged to `dev` (backend; admin only if a gating change needs a matching frontend tweak)
- [ ] EN + AR translations in the same commit (if any user-facing strings — unlikely for routes)
- [ ] Quality gate green (backend `pint --test` + `phpstan analyse` + `php artisan test`)
- [ ] `php artisan route:list` diff reviewed; `mobile/*` + `signed` sections unchanged
- [ ] Docs updated (this TASK.md → `done`; README index row; ledger entry if RBAC gating lands)
- [ ] Mobile contract re-checked (`../../mobile/`) — expected no-op
