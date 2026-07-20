# Task 010 — api.php cleanup, route organization & RESTful rename

- **Status:** `done` — full cutover shipped (Tiers 0–4) + closed out 2026-07-20; ledger D24
- **Opened:** 2026-07-19
- **Closed:** 2026-07-20
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
- [x] Delete dead commented-out routes (e.g. `~93, 150, 159–163, 173, 201, 340–348, 356–366, 453, 471–472, 487, 505, 635–638`).
- [x] Remove exact duplicate registrations: gates `store` (269–270), titles `store` (322–323),
      email-templates `store` (373–374), badges `store` (546–547), emails-config `show` (351/353),
      print-logs pair (533–534 vs 670–671).
- [x] Strip `// todo move it`, `// ???`, `// todo: move ?` noise comments.

### Tier 1 — dead-link audit (BIDIRECTIONAL) + dead-endpoint removal

Build one **route inventory** first (`php artisan route:list --json`), then reconcile it against callers
in **all** repos. Three checks, both directions:

- [x] **(a) Orphaned backend routes** — endpoint registered but no admin/frontend/mobile caller. Grep each
      path across admin + frontend (+ mobile if present) → candidates for removal.
- [x] **(b) Route → missing controller method** — a `Route::…([X::class, 'foo'])` where `X::foo()` doesn't
      exist. `route:list` loads fine but the endpoint 500s. Scan every action in `api.php` against its
      controller (given how much dup/typo cruft exists, expect a few).
- [x] **(c) Client → server dead links (404s)** — an admin/frontend/mobile API call whose path matches NO
      registered route (incl. the typo paths like `guests-status-other␣␣`). These are already-broken links;
      list them and decide fix-or-delete. **This check is re-run after the Tier 2 rename** (the rename is the
      main way a live call becomes a dead link).
- [x] Then remove confirmed dead endpoints — starting with the legacy `guests-status-*` block (455–461,
      **confirmed unused in admin**; includes the typo/trailing-space paths) + `GuestsController` methods,
      and verify-then-remove `send-sms/{id}` (cyan deleted `sendSMS` as dead), `print-test`,
      `send-e-badge-test`, `export-test`, `accept-with-days`.

### Tier 2 — reorg + RESTful rename + whereUuid (BACKEND) — produces the rename map
- [x] Fold flat `/admin/<resource>/...` routes into `Route::prefix('admin/<resource>')->group()` blocks.
- [x] Rename to RESTful shape (item 1 above); static routes ordered before `/{id}` wildcards.
- [x] Consolidate `block`+`activate` → `PATCH /{id}/toggle-status` (item 2) — add `toggleStatus()` where
      missing, delete `block()`/`activate()` route entries (keep or remove the methods per controller).
- [x] Add `->whereUuid('id')` to all UUID params.
- [x] **Deliverable: an old→new rename map** (table of every changed method+URI) — drives Tier 3 and
      becomes a mobile delta if any `mobile/*` URI changed. → `RENAME_MAP.md`.

### Tier 3 — cross-repo lockstep update (ADMIN + FRONTEND + mobile-if-touched)
- [x] Update the admin API client / all callers to the new URIs (grep the admin repo for each old path).
- [x] Repoint admin block/activate UI → `toggle-status`.
- [x] Update frontend callers if any hit a renamed public/admin URI (`countries/select` + `titles/select/{cat}`).
- [x] Mobile: only if a consumed URI changed — update the Flutter client + add a `RESPONSE_SHAPE_DELTAS`
      (or new notice) row. **N/A — no `mobile/*` URI changed.**

### Tier 4 — RBAC hardening (behavior change — verify against role matrix; land last)
- [x] Roll out `admin.can:<feature>` middleware to every admin group, cross-checked against
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
- 2026-07-19 — **Tier 2+3 executed (uncommitted, pending review).** Backend: added `toggleStatus()`
  to the 14 controllers that only had `block`/`activate`; rewrote the protected admin block of
  `routes/api.php` into `prefix()->group()` + new URIs + `whereUuid('id')` + `{id}/toggle-status`.
  **Scope correction:** endpoints with **zero admin callers** (all gate agent/scanning, `gates-select`,
  offline-sync `guest-data-*`/`printed-since`/`validate-check-in`/`attend`, and bulk-image
  `upload-zip`/`match-guests-images`) were **FROZEN** at their original URIs — they belong to the
  out-of-scope scanner client. Only endpoints the admin app actually calls were renamed, and those
  callers were moved in lockstep. Category updates went POST→PATCH. Route count 404→390.
  Admin: 13 listing toggles + shared `table-actions-modal` + 2 invitation see-more modals + all
  `-select`/rename call sites repointed. Frontend: public `countries/select` + `titles/select/{cat}`.
  Gates: backend route-diff = intended-only, all routes resolve, pint/phpstan clean, tests 457/3;
  admin + frontend `yarn type-check` clean; dead-link grep = 0 real calls. See `RENAME_MAP.md` §F.
- 2026-07-19 — **Tier 4 executed (RBAC gating, backend-only, uncommitted).** Added `admin.can:<feature>`
  to every admin route group, cross-checked against `AdminPermissions::CATALOG` +
  `EnsureAdminPermission`/`PermissionService` (Super-Admin short-circuits, deny-by-default). Pattern:
  group-level feature perm as baseline + per-action (`create`/`update`/`delete`/`export` + guest
  row-actions `accept`/`hold`/`reject`/`verify`/`send_e_badge`/`print`/etc.) on writes; dashboard gated
  **per-widget** (`overall`/`categories_status`/`guest_chart`/`gates`/`invitations_categories_status`).
  **Left ungated on purpose:** all `-select`/`select-all` + `categories/slug` (feed cross-module
  dropdowns / guest forms — gating them would 403 admins working in a *different* feature); the FROZEN
  gate agent/scanning + guest offline/scanner endpoints (new gate feature/logic coming separately);
  `operations`/`queue` ops endpoints; `account-deletion-requests` (auth.admin only). Feature-mapping
  calls: social-media-links(-per-temp) → `emails_templates`; history-logs → `guests_listing,see_more`.
  **Ops/queue dead-candidates** (0 live callers, flagged for later removal): `POST /admin/get-emails-list`
  (only a commented line in admin `test-apis`), `POST /admin/get-some-data`, `POST /admin/queue/{start,stop}`,
  `GET /admin/queue/status`. Test fixtures: the 14 pre-RBAC admin feature tests created a role-less admin
  (→ now 403); attached a `firstOrCreate(is_super)` Super-Admin role in each `setUp`. Gates: route:list
  resolves (395), pint/phpstan clean, tests 457/3 pre-existing (172 gating-403s → 3; the 3 — `ExampleTest`
  `/`, `Attendee`/`Qr` avatar signed-URL — also fail on a clean tree). Backend-only; admin already gates
  UI via the resolved permission map, so no client change.
- 2026-07-19 — **Ops/queue dead endpoints removed.** Deleted the 5 zero-caller Tier-4-flagged endpoints
  (`get-emails-list`, `get-some-data`, `queue/{start,stop,status}`) + both now-fully-dead controllers
  (`OperationActionsController`, `QueueController`) and their imports. Route count 395→390; no dangling
  refs; pint/phpstan clean. (Admin `test-api-listing.tsx` left as-is — its `/get-emails-list` ref is
  commented-out dead code in an inert dev harness.)
- 2026-07-20 — **CLOSED (ledger D24).** Reconciled state: Tiers 0–4 were in fact all committed + pushed
  (backend `4cf7036`/`c5a3a31`/`9328d65`/`68723ee`, admin `e36b384`, frontend `53d42e0`) — the earlier
  "uncommitted, pending review" log notes were stale; Task 011 already built on top. Re-verified the
  committed baseline: backend `composer qa` green (pint + phpstan No-errors + tests 465/3 pre-existing).
  **Final leftover handled:** the last two non-RESTful, ungated, zero-caller endpoints
  `POST /admin/guests-upload-zip` + `POST /admin/match-guests-images` were folded into the guests group as
  `POST /admin/guests/upload-zip` + `/match-images` behind `admin.can:guests_listing,edit` (route count
  384, unchanged — pure rename; no in-repo/mobile caller to move). The four offline-sync endpoints
  (`attend`, `guest-data-offline`, `guest-data-sync`, `guests-printed-since`) were **left at their URIs**
  per the deliberate Task 011 (D23) decision, behind `admin.can:scanning`. Dead-link grep across all repos
  for every old path = 0 code references. Mobile contract re-checked: `mobile/*` untouched, no delta.

## Decisions

- **RESTful rename is a hard cutover** — no alias/back-compat window; backend + admin (+ frontend/mobile
  as needed) change together. (Reverses the 2026-07-19 initial "out of scope" note.)
- **`block`/`activate` → single `toggle-status`, replaced outright** (not kept as legacy routes).
- **`mobile/*` stays RESTful and mostly frozen** — only reshape a mobile URI deliberately, with a delta.

## Definition of Done

- [x] Backend merged to `dev`; admin + frontend callers updated in the same cutover (mobile if touched)
- [x] Rename map (old→new) recorded; grep of all repos shows zero references to old paths
- [x] EN + AR translations in the same commit (if any user-facing strings change) — N/A, no user-facing strings changed
- [x] Backend `pint --test` + `phpstan analyse` + `php artisan test` green; admin/frontend `yarn type-check` green (`yarn production` needs the gitignored `.env.production`)
- [x] Mobile contract re-checked (`../../mobile/`); any changed `mobile/*` URI documented as a delta — no `mobile/*` URI changed
- [x] Docs updated (this TASK.md → `done`; README index row; ledger entry for the rename cutover + RBAC gating → D24)
- [ ] **Manual smoke test** per renamed feature + per gated feature (needs a running stack + role matrix) — deferred to the browser-QA pass
