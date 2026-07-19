# Task 011 — Port gate scanning into the admin app (retire the standalone scanner)

- **Status:** `todo` (plan approved — no code yet)
- **Opened:** 2026-07-19
- **Owner:** —
- **Sub-app(s):** backend + admin (+ docs)
- **Branch(es):** `dev` (+ feature branch, e.g. `feat/scan-into-admin`)

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
- [ ] Add `'scanning' => ['view']` (and consider `'recover'` for wrong-QR) to
      `app/Support/AdminPermissions.php::CATALOG`. Add EN + AR labels in the admin
      role-builder catalog mapping **in the same commit**.
- [ ] Fix the broken FROZEN route `GET /admin/guests/validate-check-in/{regNumber}` —
      `GuestsController@validateCheckIn` was removed in Task 010's dead-method sweep. Either
      restore the method (port from 112) or drop the route if the offline client is dead
      (decide during Phase 1 endpoint audit).
- [ ] **(Recommended) schema debt:** add a real `gate_id` FK on `scans` (today scans link to
      gates by `gate_name` string via `Gate::scopeWithUniqueCount`). Fold into the
      `create_scans` migration per the repo's fold-in-place convention; backfill logic n/a
      (fresh clone baseline). Keep `gate_name` denormalized column or drop it — decide in PR.

### Phase 1 — Backend endpoint modernization (mobile-contract-gated)
- [ ] **Read `docs/mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf` first** (CLAUDE.md rule 4).
      The iPad gate scanner is an out-of-repo client, NOT the Flutter app, but confirm none of
      the offline-sync / check-in URIs are in the mobile contract before renaming.
- [ ] RESTful-rename the agent/scan endpoints (see `010-api-routes-cleanup/RENAME_MAP.md` for
      the proposed shapes, e.g. `gates/{id}/scan`, `gates/{id}/start-scanning`,
      `gates/{id}/setup`, `gates/select`, `scans/…`). Un-freeze from Task 010.
- [ ] **Drop the duplicate no-`/admin` route aliases** (`/gates-scan/{id}`,
      `/gates-search-guests-by-name`, `/gates-upload-scan-image/{scanId}`,
      `/gates-update-scan-guest/{scanId}`) — they only existed for the standalone client.
- [ ] Add `->middleware('admin.can:scanning')` to the operator endpoints
      (scan / start / pause / setup / gates-select-for-agent / show-agent-side / search /
      upload-scan-image / update-scan-guest). `scans` reporting stays `admin.can:scans`.
- [ ] **Enforce data scope** in `GatesController` (or a small `EnsureGateScope` check):
      `scan`/`start`/`pause`/`setup` must assert the target gate matches `admin.gate_id`
      (once set) and/or falls inside `admin.area_id`. Super-admin short-circuits.
- [ ] **Delete `AuthController@loginAgent`** + its public route + `login-agent` references.
- [ ] Add feature tests: scanning happy-path, scope denial (agent A can't scan gate B),
      RBAC denial (no `scanning` feature → 403), gate setup binding.

### Phase 2 — Admin UI port (RBAC-rewired)
- [ ] Copy `gate-scan/*` from 112 into
      `alt-static-basecode-admin/components/admin-modules/dashbaord/gate-scan/`.
- [ ] **Rewire identity:** replace every `user.type === 'gate'` check with a
      `hasFeature('scanning')` check off the resolved permission map (ALT already resolves
      permissions client-side; reuse that, not the dead `type`).
- [ ] Wire calls to the **renamed** endpoints (not the old frozen URIs). Add the `Axios`
      base-path calls: gates-select-for-agent → setup → show-agent-side → start/pause → scan
      → wrong-QR recovery.
- [ ] **Complete the recovery flow** 108/112 left half-wired: actually call
      `searchGuestsByName` + `updateScanWithGuest` in `wrong-qr-recovery-modal.tsx` (they only
      upload a photo today).
- [ ] Dashboard entry: render the scanner for `scanning`-capable admins
      (`dashbaord/index.tsx`), keep the CMS dashboard for others.
- [ ] Re-enable the "Gates & Scans" nav (currently commented out in `data/sidebar-links.tsx`)
      gated by the `gates`/`scans`/`areas`/`scanning` features via `inferFeatureId`.
- [ ] Add `/scans` to `data/module-icons.tsx` (missing today). EN + AR strings same commit.
- [ ] Confirm camera lib: 112 uses `react-web-qr-reader ^1.0.4` — justify the new dep in the
      PR (CLAUDE.md rule) or swap to an already-present scanner lib.

### Phase 3 — Reference cleanup
- [ ] Remove dead `type=gate` client bits: `components/shared/select/admins-select.tsx`
      (`/admins/select?type=gate`) and `areas-form.tsx` (`/admins?type=gate`) — backend
      ignores `type`; switch to the `scanning`/`gates` feature filter already used by
      `AdminsController@selectList`.
- [ ] Grep backend + admin + docs for `login-agent`, `agent admin`, standalone-scanner
      references; remove or update. Update `010`'s `RENAME_MAP.md` §F (the freeze it recorded
      is now lifted) and note the alias removals.
- [ ] Ledger entry for the scan-into-admin cutover + the new `scanning` RBAC feature.

### Phase 4 — QA
- [ ] Browser-QA the full scan loop: camera permission, hardware-wedge input, success,
      `guest_not_found` → recovery, start/pause, gate setup + re-setup.
- [ ] RBAC matrix: a `scanning`-only role sees ONLY the scanner (no CMS); a `gates`-only role
      manages gates but gets no scanner; super sees both.
- [ ] Scope: operator bound to gate A is blocked (403) from scanning gate B.

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
- **New dependency** (`react-web-qr-reader`) needs PR justification per CLAUDE.md.

## Decisions

- See "Locked decisions (2026-07-19)" above. Durable ones (the `scanning` feature; scope
  enforcement; standalone-scanner retirement) → promote to `../../decisions/LEDGER.md` when
  Phase 1 lands.

## Definition of Done

- [ ] Backend merged to `dev`: `scanning` feature, renamed+gated+scope-enforced endpoints,
      `loginAgent` + no-`/admin` aliases removed, `validateCheckIn` resolved, tests green.
- [ ] Admin merged to `dev`: `gate-scan/*` ported + RBAC-rewired, nav re-enabled, `/scans`
      icon, dead `type=gate` bits removed.
- [ ] EN + AR translations in the same commit (new `scanning` label + any scanner UI strings).
- [ ] Quality gate green (backend `pint --test` + `phpstan` + `php artisan test`;
      admin `yarn type-check` + `yarn production`).
- [ ] Mobile contract checked (`../../mobile/`) — confirmed the retired URIs aren't in it.
- [ ] Docs updated (this TASK.md → `done`; index row; ledger entry; `010` RENAME_MAP §F note).
