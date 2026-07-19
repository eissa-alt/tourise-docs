# Task 010 — api.php cleanup, route organization & RESTful rename

- **Status:** `todo`
- **Opened:** 2026-07-19
- **Owner:** —
- **Sub-app(s):** backend + admin + frontend (+ mobile if a consumed URI changes)
- **Branch(es):** `dev` (feature branch strongly recommended — this is a cross-repo cutover)

## Goal

Bring `alt-static-basecode-backend/routes/api.php` up to the cyan-basecode standard: remove dead code +
duplicate registrations, organize into `Route::prefix()->group()` blocks, **rename the legacy admin
endpoints to cyan's RESTful shape**, add `->whereUuid('id')` constraints, and roll out per-feature
`admin.can:` RBAC gating. Today our file is **966 lines** of mostly-flat, ungated, non-RESTful routes;
cyan's is **559 lines**, grouped + gated + RESTful. The renamed URIs are a **hard cutover** — admin API
client + frontend callers (and mobile, only if a consumed URI changes) are updated in lockstep.

## Reference

- Cyan baseline: `/Users/admin/Projects/ALT/115-cyan-basecode/cyan-basecode-repos/cyan-backend/routes/api.php`
  — the target shape (prefix + `admin.can:` groups, `whereUuid`, RESTful verbs, no dupes, no dead code).
- Ours: `alt-static-basecode-backend/routes/api.php`.
- **`admin.can` exists here** → `app/Http/Kernel.php`: `'admin.can' => EnsureAdminPermission::class`
  (also `auth.admin` / `auth.guest`). Both `admin.can:feature` and `admin.can:feature,action` forms are
  already used. Feature keys live in `RolesController::catalog` / `app/Support/AdminPermissions.php`.
- **`routes/api.php` is also the mobile contract** — see `../../mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf`
  and `../../mobile/RESPONSE_SHAPE_DELTAS.md`. The `mobile/*` section is already RESTful; only touch a
  `mobile/*` URI if it is genuinely being renamed, and document it as a delta if so.

## Scope

- **In:** the legacy admin protected block (`~176–672`). Cleanup, reorg, **RESTful renaming**, verb
  consolidation (`block`+`activate` → `toggle-status`, replacing outright), `whereUuid`, and `admin.can:`
  gating — plus the matching admin/frontend/mobile client updates for every renamed URI.
- **Out (explicitly NOT this task):**
  - Controller response-body changes (that was response-unification, ledger D22).
  - Renaming `mobile/*` URIs unless a specific endpoint is deliberately reshaped (avoid; it's the mobile
    contract). Any that do change get a row in `../../mobile/RESPONSE_SHAPE_DELTAS.md` (or a new delta).

## Cutover decisions (from user notes, 2026-07-19)

1. **Rename admin paths to cyan's RESTful shape** — `POST /admin/guests-new` → `POST /admin/guests`,
   `PUT /admin/guests-update/{id}` → `PUT /admin/guests/{id}`, `/admin/x-select` → `/admin/x/select`,
   etc. **Hard cutover, no alias/back-compat window** — admin + frontend updated in the same change.
2. **Replace `block/{id}` + `activate/{id}` with a single `PATCH /{id}/toggle-status`** outright (do
   NOT keep the legacy pair). Requires adding `toggleStatus()` to controllers that only have
   `block()`/`activate()` and repointing the admin UI's block/activate buttons.
3. **`whereUuid('id')`** on every UUID route param, done as part of the reshape.
4. **`admin.can:<feature>`** gating on every admin group, mirroring cyan.

## Todo (ordered)

### Tier 0 — pure cleanup (backend only, zero contract change)
- [ ] Delete dead commented-out routes (e.g. `~93, 150, 159–163, 173, 201, 340–348, 356–366, 453, 471–472, 487, 505, 635–638`).
- [ ] Remove exact duplicate registrations: gates `store` (269–270), titles `store` (322–323),
      email-templates `store` (373–374), badges `store` (546–547), emails-config `show` (351/353),
      print-logs pair (533–534 vs 670–671).
- [ ] Strip `// todo move it`, `// ???`, `// todo: move ?` noise comments.

### Tier 1 — dead-link audit (BIDIRECTIONAL) + dead-endpoint removal

Build one **route inventory** first (`php artisan route:list --json`), then reconcile it against callers
in **all** repos. Three checks, both directions:

- [ ] **(a) Orphaned backend routes** — endpoint registered but no admin/frontend/mobile caller. Grep each
      path across admin + frontend (+ mobile if present) → candidates for removal.
- [ ] **(b) Route → missing controller method** — a `Route::…([X::class, 'foo'])` where `X::foo()` doesn't
      exist. `route:list` loads fine but the endpoint 500s. Scan every action in `api.php` against its
      controller (given how much dup/typo cruft exists, expect a few).
- [ ] **(c) Client → server dead links (404s)** — an admin/frontend/mobile API call whose path matches NO
      registered route (incl. the typo paths like `guests-status-other␣␣`). These are already-broken links;
      list them and decide fix-or-delete. **This check is re-run after the Tier 2 rename** (the rename is the
      main way a live call becomes a dead link).
- [ ] Then remove confirmed dead endpoints — starting with the legacy `guests-status-*` block (455–461,
      **confirmed unused in admin**; includes the typo/trailing-space paths) + `GuestsController` methods,
      and verify-then-remove `send-sms/{id}` (cyan deleted `sendSMS` as dead), `print-test`,
      `send-e-badge-test`, `export-test`, `accept-with-days`.

### Tier 2 — reorg + RESTful rename + whereUuid (BACKEND) — produces the rename map
- [ ] Fold flat `/admin/<resource>/...` routes into `Route::prefix('admin/<resource>')->group()` blocks.
- [ ] Rename to RESTful shape (item 1 above); static routes ordered before `/{id}` wildcards.
- [ ] Consolidate `block`+`activate` → `PATCH /{id}/toggle-status` (item 2) — add `toggleStatus()` where
      missing, delete `block()`/`activate()` route entries (keep or remove the methods per controller).
- [ ] Add `->whereUuid('id')` to all UUID params.
- [ ] **Deliverable: an old→new rename map** (table of every changed method+URI) — drives Tier 3 and
      becomes a mobile delta if any `mobile/*` URI changed.

### Tier 3 — cross-repo lockstep update (ADMIN + FRONTEND + mobile-if-touched)
- [ ] Update the admin API client / all callers to the new URIs (grep the admin repo for each old path).
- [ ] Repoint admin block/activate UI → `toggle-status`.
- [ ] Update frontend callers if any hit a renamed public/admin URI.
- [ ] Mobile: only if a consumed URI changed — update the Flutter client + add a `RESPONSE_SHAPE_DELTAS`
      (or new notice) row. Expected minimal (mobile section is already RESTful).

### Tier 4 — RBAC hardening (behavior change — verify against role matrix; land last)
- [ ] Roll out `admin.can:<feature>` middleware to every admin group, cross-checked against
      `RolesController::catalog` + the admin frontend permission checks so no in-use admin loses access.

## Verification gates

- **Tier 0–1:** `php artisan route:list` diff should show only removals; `pint --test` + `phpstan` + `php artisan test`.
- **Tier 2+ (URIs change intentionally):** the route:list diff is NO LONGER an identity check — instead
  verify every removed old URI has a corresponding new URI in the **rename map**, and that no caller
  still references an old path (grep admin + frontend + mobile repos = clean).
- **Dead-link gate (both directions, run at start AND after the rename):** (a) no orphaned routes left
  unaccounted for, (b) every `api.php` action resolves to a real controller method, (c) zero client calls
  point to a non-existent route. Check (c) is the one that catches a missed caller during the cutover.
- `pint --test` + `phpstan analyse` + `php artisan test` green after each tier; admin/frontend
  `yarn type-check` + `yarn production` green after Tier 3.
- Manual smoke test per renamed feature + per gated feature (Tier 4).

## Log

- 2026-07-19 — opened. Compared our `api.php` (966 lines, flat/ungated/non-RESTful legacy admin block)
  against cyan (559 lines, grouped + `admin.can:` + `whereUuid` + RESTful). Confirmed `guests-status-*`
  is dead and that `admin.can`/`EnsureAdminPermission` already exists here.
- 2026-07-19 — scope expanded per user notes: RESTful **renaming is now IN scope** (hard cutover across
  admin + frontend + mobile-if-touched), and `block`/`activate` are **replaced** by `toggle-status`
  outright. Reversed the earlier "keep URIs frozen" / "no rename" decisions.
- 2026-07-19 — added an explicit **bidirectional dead-link audit** to Tier 1 (orphaned routes,
  route→missing-method, client→404 links) + a dead-link verification gate, re-run after the rename.
- 2026-07-19 — **Tier 0+1 executed** (backend `4cf7036`). Dead-link audit found 7 route→missing-method
  bugs + confirmed the `guests-status-*`/`guests-chart`/etc. block dead (0 callers, no tests). Removed
  dead comments, dup registrations, and dead endpoints; deleted 7 orphaned `GuestsController` methods.
  Route count 418→400; pint+phpstan clean; tests 457/3 pre-existing. **Tier 2/3 paused** — drafted
  `RENAME_MAP.md` (proposed URIs + open naming decisions) for review before the cross-repo cutover.

## Decisions

- **RESTful rename is a hard cutover** — no alias/back-compat window; backend + admin (+ frontend/mobile
  as needed) change together. (Reverses the 2026-07-19 initial "out of scope" note.)
- **`block`/`activate` → single `toggle-status`, replaced outright** (not kept as legacy routes).
- **`mobile/*` stays RESTful and mostly frozen** — only reshape a mobile URI deliberately, with a delta.

## Definition of Done

- [ ] Backend merged to `dev`; admin + frontend callers updated in the same cutover (mobile if touched)
- [ ] Rename map (old→new) recorded; grep of all repos shows zero references to old paths
- [ ] EN + AR translations in the same commit (if any user-facing strings change)
- [ ] Backend `pint --test` + `phpstan analyse` + `php artisan test` green; admin/frontend `yarn type-check` + `yarn production` green
- [ ] Mobile contract re-checked (`../../mobile/`); any changed `mobile/*` URI documented as a delta
- [ ] Docs updated (this TASK.md → `done`; README index row; ledger entry for the rename cutover + RBAC gating)
