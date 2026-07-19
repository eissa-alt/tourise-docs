# Task 011 — Port gate scanning into the admin app (retire the standalone scanner)

- **Status:** `done` (backend + admin shipped to `dev`; Phase 0 `gate_id` FK deferred — see note)
- **Opened:** 2026-07-19
- **Landed:** 2026-07-19
- **Owner:** —
- **Sub-app(s):** backend + admin (+ docs)
- **Branch(es):** `dev`
- **Commits:** backend `P11.1` (scanning feature + endpoints), `P11.3` (admins/select filter);
  admin `P11.2` (gate-scan UI port)

## What actually shipped (deviations from the plan)

- **Camera lib swapped.** Plan floated `react-web-qr-reader ^1.0.4` (108/112's dep) but it
  pins React 16/17 and is unmaintained — replaced with the maintained, framework-agnostic
  **`html5-qrcode`** (dynamic-imported so it never runs server-side). Also dropped
  `react-lottie` (108/112 used it for the scan pulse) for a CSS pulse — one less dep.
- **`validateCheckIn` route dropped, not restored.** The handler was already deleted in Task
  010 and it had **no in-repo callers**, so the dangling `GET /admin/guests/validate-check-in/{regNumber}`
  route was removed rather than ported back. The offline-sync group (`attend`,
  `guest-data-offline`, `guest-data-sync`, `guests-printed-since`) was kept and moved behind
  `admin.can:scanning`.
- **`scans.gate_id` FK deferred.** The recommended Phase 0 schema debt (real FK instead of the
  `gate_name` string link) was **not** done — the port ships on the existing string link. Still
  open (see risks). No migrations were touched by this task.
- **`scanning` shipped with `['view']` only** (no separate `recover` action); recovery is part
  of operating the gate, so it lives under the same `view` grant.

## Goal

Move on-site **gate scanning** into the ALT admin app as a first-party feature (as
`108-tasama` / `112-pif-partners-forum-demo` already did), retire the old **standalone
"agent admin" scanner** client, and wire the whole thing onto ALT's **RBAC** model
(the `type='gate'` concept those projects use is already gone here). Clean every
reference to the old agent/standalone scanner along the way.

## Background — what the reference projects do vs where ALT stands

Two explore passes confirmed **108-tasama and 112-pif-partners-forum-demo are the same
port** (interchangeable — trivial cosmetic deltas only). ALT is the deliberate outlier,
which is *why* this task exists.

| | 108 / 112 (source of the port) | ALT (current) |
|---|---|---|
| Operator identity | `admins.type = 'gate'` | **`type` dropped → RBAC** |
| Scanner UI in admin | ✅ `dashbaord/gate-scan/*` tree | ❌ **none** (only gates/areas/scans CRUD; nav commented out) |
| `loginAgent` | checks `type==='gate'` (unused by admin UI) | checks `hasFeature('gates')` (no admin UI proxy) |
| Scan endpoints | live, dual-prefix (`/admin/*` + `/*`) | **FROZEN** (Task 010) + dual-prefix, **no `admin.can`** |
| Data-scope enforce | UX-only (security gap: any token scans any gate) | `category_ids`/`guest_status_ids` enforced; `area_id` partial; `gate_id` stored-only |

**Source to port from (either):**
`…/112-pif-partners-forum-demo/pif-partners-forum-demo-repo/pif-partners-forum-demo-admin/components/admin-modules/dashbaord/gate-scan/`
→ `index.tsx`, `setup-gate.tsx`, `current-gate.tsx`, `qr-code-edgex.tsx` (camera,
`react-web-qr-reader`), `scanner-eda51.tsx` (hardware wedge input), `wrong-qr-recovery-modal.tsx`.

Backend surface already present in ALT (frozen): `GatesController` agent methods
(`selectList`, `showAgentSide`, `startScanning`, `pauseScanning`, `scan`, `setupGate`,
`searchGuestsByName`, `uploadScanImage`, `updateScanWithGuest`), `ScansController`
(`index`/`Export`/`ExportUnique`), models `gates`/`scans`/`areas`, admin scope fields
`area_id`/`gate_id`.

## Locked decisions (2026-07-19)

1. **Operator identity → a NEW `scanning` catalog feature** (distinct from the `gates`
   CMS-management feature). Role grants `scanning` ⇒ the admin gets the scanner UI. Keeps
   "manage gates in the CMS" (`gates`) cleanly separate from "operate a gate" (`scanning`).
2. **Enforce gate/area data-scope on the scan endpoints** — close the 108/112 security gap:
   an operator may only scan the gate they're bound to (`admin.gate_id`) and/or a gate
   within their `admin.area_id`. Not UX-only.
3. **Modernize the endpoints** — un-freeze, RESTful-rename, add `admin.can:scanning` gating,
   and **drop the duplicate no-`/admin` aliases + `loginAgent`** (standalone scanner is
   retired, so the compatibility shims go).
4. **Normal admin login** — no separate agent login screen; the scanner appears on the
   dashboard for scan-capable admins (mirrors what 108/112 admin actually does). `loginAgent`
   is deleted.
5. **Deliverable now = this plan doc only** (no code yet).

## Scope

- **In:** new `scanning` RBAC feature + EN/AR labels; port `gate-scan/*` admin UI onto RBAC;
  modernize + gate + scope-enforce the scan/gate-agent endpoints; delete `loginAgent` + the
  no-`/admin` scan aliases + dead `type=gate` client bits; fix the broken `validateCheckIn`
  route; tests; docs/ledger.
- **Out:** the Flutter mobile app's own `/mobile/qr` guest-networking scan (unrelated); a
  full offline-first PWA rebuild (keep the existing offline-sync endpoints' behavior, just
  re-home/gate them); redesigning the badge-print pipeline.

## Plan (phased)

### Phase 0 — RBAC + schema foundation (backend + admin labels)
- [x] Add `'scanning' => ['view']` to `app/Support/AdminPermissions.php::CATALOG` (+ EN/AR
      labels in the same commit). Shipped `view` only — no separate `recover` action.
- [x] Resolve the broken FROZEN route `GET /admin/guests/validate-check-in/{regNumber}` —
      **dropped** (handler gone since Task 010, no in-repo callers) rather than restored.
- [ ] ~~**(Recommended) schema debt:** real `gate_id` FK on `scans`~~ — **deferred.** Port
      ships on the existing `gate_name` string link (`Gate::scopeWithUniqueCount`). Still open.

### Phase 1 — Backend endpoint modernization (mobile-contract-gated)
- [x] **Read `docs/mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf` first** (CLAUDE.md rule 4) —
      confirmed the gate-scan / offline-sync URIs are the out-of-repo iPad client, not the
      Flutter contract, so renaming is safe.
- [x] RESTful-rename the agent/scan endpoints into a `/admin/gate-scan` group
      (`gates`, `gates/{id}`, `gates/{id}/setup|start|pause|scan`, `search-guests`,
      `scans/{id}/image`, `scans/{id}/guest`). Un-frozen from Task 010.
- [x] **Dropped the duplicate no-`/admin` aliases** (`/gates-scan/{id}`,
      `/gates-search-guests-by-name`, `/gates-upload-scan-image/{scanId}`,
      `/gates-update-scan-guest/{scanId}`).
- [x] Added `->middleware('admin.can:scanning')` to the whole `gate-scan` group + the retained
      offline-sync endpoints (`attend`, `guest-data-offline`, `guest-data-sync`,
      `guests-printed-since`). `scans` reporting stays `admin.can:scans`.
- [x] **Enforce data scope** via `GatesController::deniesGateScope()` on
      `showAgentSide`/`setup`/`start`/`pause`/`scan`: target gate must match `admin.gate_id`
      (once bound) and/or fall inside `admin.area_id`. Super-admin short-circuits.
- [x] **Deleted `AuthController@loginAgent`** + its public route.
- [x] Feature tests (`tests/Feature/GateScanTest.php`): happy-path, scope denial, area denial,
      RBAC denial (403), setup-binding, bound-lock, super bypass, recovery search+link.

### Phase 2 — Admin UI port (RBAC-rewired)
- [x] Ported `gate-scan/*` into
      `alt-static-basecode-admin/components/admin-modules/dashbaord/gate-scan/`.
- [x] **Rewired identity:** `type === 'gate'` → `checkFeaturePermission('scanning', user)`.
- [x] Wired to the renamed `/gate-scan/*` endpoints through the BFF proxy (HttpOnly token) —
      dropped the manual `cookie.get('token')` + Bearer headers.
- [x] **Completed the recovery flow:** `wrong-qr-recovery-modal.tsx` now searches by name
      (`POST /gate-scan/search-guests`) **and links** the guest to the orphan scan
      (`PUT /gate-scan/scans/{id}/guest`), plus the photo upload.
- [x] Dashboard entry renders the scanner for `scanning`-capable admins; CMS widgets stay.
- [x] Re-enabled the "Gates & Scans" nav (`data/sidebar-links.tsx`), feature-gated.
- [x] Added `/scans` to `data/module-icons.tsx`; EN + AR strings in the same commit.
- [x] Camera lib: swapped `react-web-qr-reader` → `html5-qrcode` (dynamic import), dropped
      `react-lottie` for a CSS pulse. See "What actually shipped".

### Phase 3 — Reference cleanup
- [x] Removed dead `type=gate` client bits from `admins-select.tsx` and `areas-form.tsx`;
      `AdminsController@selectList` now filters by the `scanning` feature.
- [x] Swept `login-agent` / agent-admin references; `RENAME_MAP.md` §F updated (freeze lifted).
- [x] Ledger entry for the scan-into-admin cutover + the new `scanning` RBAC feature.

### Phase 4 — QA
- [x] Backend gate green: `pint --test` + `phpstan` + `php artisan test` (incl. `GateScanTest`).
- [x] Admin gate: `yarn type-check` + `next build` (prod build; `yarn production` needs the
      gitignored `.env.production`, so validated via `next build` directly).
- [ ] **Browser-QA the live scan loop** (camera permission, hardware-wedge, `guest_not_found`
      → recovery, start/pause, setup/re-setup) — not yet run; needs a device + camera.
- [ ] **RBAC matrix + scope** manual pass on a running stack — not yet run.

## RBAC model — how scanning fits the role system (answers the "how do we solve RBAC" question)

- **Two separate concerns, two features:**
  - `gates` / `areas` / `scans` = **CMS management** (create/edit gates, define areas, read
    the scan log/exports) — for admins/managers.
  - `scanning` (NEW) = **operate a gate** (the live scan UI) — for on-site gate agents.
- **A "gate agent" is just a role** whose permission matrix grants `scanning` (and usually
  nothing else). No `type` column, no separate login — they log in normally and the dashboard
  shows them the scanner because `hasFeature('scanning')` is true.
- **Data scope** reuses the existing per-admin fields (`area_id`, `gate_id`) that ALT already
  stores and partially enforces: `area_id` limits which gates appear in setup; `gate_id`
  (set by `setupGate`) binds them to one gate; Phase 1 makes the **scan endpoints enforce**
  both (super-admin short-circuits). This closes the 108/112 gap where any token could scan
  any gate.
- **Super Admin** short-circuits everything (existing `PermissionService` behavior), so a
  super admin can both manage and operate without extra grants.

## Open items / risks

- **Standalone scanner truly retired?** Decisions assume yes. If any old iPad scanner is
  still in the field, dropping the no-`/admin` aliases + `loginAgent` breaks it — confirm
  before Phase 1 ships. (Reversible: re-add aliases if needed.)
- **`scans.gate_name` string link** is fragile (renaming a gate breaks unique counts); the
  Phase 0 `gate_id` FK is recommended but optional — can ship the port without it.
- **Scan ≠ check-in:** `scan()` writes only to `scans`; it does not set `guest.check_in`.
  Keep that behavior unless product wants scanning to also mark attendance (separate ask).
- **New dependency** (`html5-qrcode`) — justified: replaces the stack-incompatible,
  unmaintained `react-web-qr-reader` (React 16/17) 108/112 shipped; net dep count is flat
  because `react-lottie` was also dropped.
- **Live QA not yet run** — the scan loop and RBAC/scope matrix were only validated by unit/
  feature tests + type-check/build; they still need a manual pass on a running stack + camera.

## Decisions

- See "Locked decisions (2026-07-19)" above. Durable ones (the `scanning` feature; scope
  enforcement; standalone-scanner retirement) → promote to `../../decisions/LEDGER.md` when
  Phase 1 lands.

## Definition of Done

- [x] Backend merged to `dev`: `scanning` feature, renamed+gated+scope-enforced endpoints,
      `loginAgent` + no-`/admin` aliases removed, `validateCheckIn` resolved, tests green.
- [x] Admin merged to `dev`: `gate-scan/*` ported + RBAC-rewired, nav re-enabled, `/scans`
      icon, dead `type=gate` bits removed.
- [x] EN + AR translations in the same commit (new `scanning` label + scanner UI strings).
- [x] Quality gate green (backend `pint --test` + `phpstan` + `php artisan test`;
      admin `yarn type-check` + `next build`).
- [x] Mobile contract checked (`../../mobile/`) — confirmed the retired URIs aren't in it.
- [x] Docs updated (this TASK.md → `done`; index row; ledger entry; `010` RENAME_MAP §F note).
- [ ] **Live browser-QA + RBAC/scope manual pass** — deferred (needs a running stack + camera).
