# Task 021 — Seating Plan Manager (port into the ALT baseline)

- **Status:** `done (code)` — Phases A/B/C implemented 2026-07-25, all gates green, on FEATURE BRANCHES
  (backend/admin `feat/seating`, seating repo `dev`), **NOT pushed**. Ledger D42. Pending owner: review + merge
  → `dev` + push; create the GitHub seating remotes; set `.env`; dev/prod migrate; live QA.
- **Opened:** 2026-07-25
- **Owner:** (unassigned)
- **Sub-app(s):** **new 4th sub-app** `alt-static-basecode-seating` + backend + admin (+ docs). Frontend/landing: none.
- **Branch(es):** `dev` → feature branch `feat/seating`
- **Investigation:** cross-repo workflow analysis 2026-07-25 (14 agents, adversarially verified against real 121 code).
- **Revalidated vs Task 020 (2026-07-25, after 020 landed):** re-checked all assumptions against the current
  tree — **plan holds, no new risks.** Only deltas: (1) migration slots `2026_07_25_000001–000004` are taken
  (000001/000002 automation, **000003/000004 = task 020**) → seating uses the **next free** (`000005`/`000006`+,
  re-check at build); (2) every `file:line` citation below is **pre-020 — re-derive against HEAD at build time**
  (updateGuest ~+10, routes ~+5, model/resource ~+2); (3) 121 admin has **one consolidated `guests-listing.tsx`**
  (per-type files merged in `599827f`); (4) the `seating` RBAC feature belongs in **backend
  `app/Support/AdminPermissions.php`**. No merge collision with 020, no mobile-contract break.

## Goal

Bring the **Seating Plan Manager** — the standalone venue-seating app the client demoed/tested for the last
month in **v1 (120-pif-private-events-platform)** — into the **121 ALT baseline as a general, reusable
feature**, so every current and future clone (starting with **123-pif-pep-v2**) inherits it via the normal
`--ff-only` catch-up instead of re-porting it per project.

Seating is a **standalone Vite/React SPA** that integrates **API-wire** (no UI merge): it authenticates as an
admin against the Laravel backend, pulls the guest roster, writes seat assignments + attendance back onto the
`guests` table, and stores the board design in a `seating_layouts` document. The port is therefore
**mostly backend + a new SPA repo** — the admin app only gains a launch button.

## Decision — base code (121), not the clone (123)

**Build in 121.** Rationale (all verified):
- The SPA is **decoupled** — it shares no code or TS types with the admin, talks only HTTP. Genuinely reusable.
- **123 is a byte-identical clone of 121** (same HEAD SHAs on all three sub-apps, clean trees, no PIF
  divergence yet). Landing seating in 121 means 123 inherits it for free; building it in 123 would strand it
  and force a re-port in every future clone.
- The backend pieces (attendance columns, `seating_layouts`, updateGuest allowlist) are **generic additive**
  changes — the same "improve the baseline, clones inherit" model used for automation scheduling / WhatsApp /
  reconfirmation.

## Scope

**In:**
- **New 4th sub-app** `alt-static-basecode-seating` — the Vite SPA (React 18, Tailwind v3, no TS), retargeted
  to 121's routes/response shapes. Mounted side-by-side like the other three (no monorepo tooling).
- **Backend (additive, forward-only):**
  - `seating_layouts` + `seating_layout_versions` tables + `SeatingLayout`/`SeatingLayoutVersion` models +
    `SeatingLayoutsController` (show/update **+ versions/showVersion read-back** — full port, D-6) + routes at
    the **exact path** `admin/seating-layout` (incl. `/versions` + `/versions/{id}`).
  - `seating_audit_logs` table + `SeatingAuditLog` model + `SeatingAuditLogsController` (index/store) + routes
    (full port, D-6). ⚠️ 120's SPA keeps its audit log **browser-local** — to actually *use* the server table,
    the SPA also needs wiring to POST/GET it (extra SPA work; flagged, not free with the backend port).
  - Six **event-attendance** columns on `guests` (`checked_in_at/by`, `checked_out_at/by`,
    `food_checked_in_at/by`) + fillable/casts/relations, **exposed for write** via the updateGuest allowlist,
    and **exposed for read** in `GuestsResources` (ISO-8601 + `*_by`).
  - Resolve the **legacy `check_in` ↔ new `checked_in_at`** source-of-truth question (Decision D-3).
- **Admin:** a **Seating Manager** launch entry-point in the guests-listing toolbar — a **gated deep-link**
  (D-4 = own login; no token handoff, no BFF route). Gated by the `seating` RBAC feature (D-5). One env var
  `NEXT_PUBLIC_SEATING_MANAGER_URL`.
- **RBAC:** a dedicated `seating` **feature-catalog** entry (like `scanning`), **not** `admins.type` (D-5).
- EN + AR for every admin-facing string in the same commit.

**Out (explicitly not this task):**
- **`admins.type` role branching.** 120 added `seating` / `seating-checkin` / `seating-view` **type** strings
  to the admin dropdown — forbidden in ALT ("never branch on `user.type`"). Model capability via RBAC instead.
- **Gate-scan ↔ attendance unification (LOCKED out — Q8 = separate task).** The SPA never calls a gate-scan
  endpoint (**verified — refuted as a dependency**). Making 121 gate scans also write the shared attendance
  columns (so door arrivals show live on the seating board, as in 120) is a *separate future task* — seating's
  own check-in works without it. Fold in later if the client runs door scanners and wants the board auto-updated.
- **Rebranding the SPA to neutral baseline identity (LOCKED out — Q7 = keep PIF for now).** PIF branding is
  correct for the immediate consumer (123-pif-pep-v2 *is* PIF). Kept as-is; neutralizing to generic ALT
  placeholders is a tracked follow-up (see Open items) before any **non-PIF** clone reuses the baseline — **not**
  left permanent.

## Background — investigation summary (2026-07-25)

**What seating is (v1 / 120):** `pif-private-events-platform-seating` — a **Vite 6 + React 18** SPA
(`seating-plan-manager` v4.0.0), its own git repo, plain JS/JSX (no TS), Tailwind v3. Deps are light and
self-contained: `@dnd-kit/core`, `exceljs`, `jspdf`, `html2canvas`, `lucide-react`,
`react-google-recaptcha-v3`. **No axios** (native `fetch`), **no Sentry** (consistent with the baseline rule).
Built to a static `dist/`, hosted on its own origin.

**Not created from the admin.** Independent codebase — 24 `.jsx`, zero imports from the admin. It only
*behaves* like an admin client: same accounts, `POST /admin/login` (+OTP), same reCAPTCHA site key, Sanctum
bearer. All backend coupling is string-built in `src/utils/pifApi.js`.

**Architecture fact:** seat **assignments** are NOT in `seating_layouts`. That table holds only the shared
board document (tables / custom layouts / setup config). Per-guest seats live on `guests.table_number` /
`guests.seat_number` and are written through the guest-update endpoint. Attendance (`checked_in_at` & co.)
also lives on `guests`.

**120 backend footprint** (what the seating build added there): 5 migrations (`seating_layouts`,
`seating_layout_versions`, `add_event_attendance_to_guests`, `add_scan_action_to_gates`,
`seating_audit_logs`), 3 models, 2 controllers, `Guest` model attendance fillable/casts + a `booted()`
legacy-sync hook, `updateGuest` attendance normalization, gate-scan attendance wiring, `GuestsResources`
attendance fields. **120 admin footprint** is tiny: 1 new file (`open-seating-manager-btn.tsx`), 2 modified
(`guests-super.tsx` render, `admins-types-select.tsx` seating types). **Frontend/landing: zero seating.**

### The 120 → 121 gap (verified against real 121 code)

| # | What seating needs | 121 state | Severity | Fix |
|---|---|---|---|---|
| 1 | `PUT /admin/guests-update/{id}` (seat write) | **renamed** → `PUT /admin/guests/{id}` (Task 010/D24) | medium | One-line SPA repoint in `pifApi.js:66`. `g.id` is already a UUID → satisfies `whereUuid`. `seat_number`/`table_number` are in `updateGuest` `only()` ✓. |
| 2 | `PUT /admin/gates-scan/{id}` | **not a dependency** — SPA never calls it (refuted) | none | — |
| 3 | `POST /admin/login` (+OTP) | present, unchanged; 6h bearer | low | none — SPA already sends `recaptcha` + handles the `/login-confirmation` OTP two-step. |
| 4 | `GET /admin/me` | **absent**; `/admin/get-profile` is **not** drop-in (flat body, no `data` wrapper the SPA requires) | low | Add a data-wrapped `GET /admin/me` alias returning `new AdminsResources($request->user())` — matches login's shape so `pifMe()` works unchanged. |
| 5 | Role mapping via `admin.type` | 121 **dropped `type`** from login + `AdminsResources` → every admin collapses to `ROLE.USER` | medium | SPA `mapAdminToUser` must read 121's `role`/`permissions`; seating capability lives in the RBAC catalog, not `admins.type`. |
| 6 | Attendance columns (6) | **absent** — only legacy `check_in`/`check_in_time`/`check_in_count`/`scanned_by` | **blocker** | Additive migration + append the 6 keys to `updateGuest` `only()`. **⚠️ Today writes fail SILENTLY** (columns absent AND not in allowlist → `update([])` → HTTP 200, nothing saved). |
| 7 | `check_in` ↔ `checked_in_at` sync | **absent** (no `booted()`/mutator/observer) | medium | Make `checked_in_at` canonical + migrate legacy readers (preferred, per "no dual code paths"). See D-3. |
| 8 | `seating_layouts` + `GET/PUT /admin/seating-layout` | **absent** | **blocker** | Full additive port. **PK is `$table->id()` bigint** (not UUID). Must also port `seating_layout_versions` (update() snapshots on every PUT or throws). Route path must be **exactly** `admin/seating-layout` (SPA hardcodes it). |
| 9 | Admin token → SPA (`?pif_token=` handoff) | token is **HttpOnly/server-only** (Task 005/D12) → unreadable by browser JS | high (button only) | The 120 client-side handoff can't work. **Default: Option B** — SPA uses its own login screen (works against 121 unchanged). Optional Option A: a server-side BFF redirect route. See D-4. |
| 10 | CORS external origin + Sanctum bearer-from-header | present (`config/cors.php` env-driven; `AppServiceProvider` strips `Bearer`) | low | Set `CORS_ALLOWED_ORIGINS=<spa-origin>` in backend `.env` (owner — gitignored). `supports_credentials=false` is correct for bearer auth. |
| 11 | reCAPTCHA v3 site key | present — `NEXT_PUBLIC_GOOGLE_RECAPTCHA_KEY` | none | Reuse the same key value in the SPA's `VITE_GOOGLE_RECAPTCHA_KEY`. |

**Design lessons from 120 (do not repeat):** attendance write-back failed silently in 121 because the
allowlist drops unknown keys — so tests must assert **persistence**, not just a 200. The `/me` alias must be
**data-wrapped** or `pifMe()` throws even against the right route.

## Design (proposed — confirm on review)

### The SPA (`alt-static-basecode-seating`)
- New repo cloned from 120's seating repo, mounted beside the other three. Retarget **only** `src/utils/pifApi.js`:
  - `guestUpdateEndpoint` → `/api/admin/guests/${id}` (was `/api/admin/guests-update/${id}`).
  - `pifMe` → keep `/api/admin/me` (backed by the new alias) — or repoint + reshape if we skip the alias.
  - `mapAdminToUser` (in `App.jsx`) → derive role from 121's `role`/`permissions`, not `admin.type`.
- Everything else (login, OTP, seat push, layout GET/PUT, guest read mapping — which already tolerates
  string-or-relation `title`/`category`) ports unchanged.
- Config: `VITE_PIF_API_BASE_URL` (base only, never a token), `VITE_GOOGLE_RECAPTCHA_KEY`.

### Backend (additive, forward-only — real data exists, no `migrate:fresh`)
> **Migration numbering (revalidated 2026-07-25):** `2026_07_25_000001–000004` are already used (000001/000002
> automation channel+scheduling; 000003/000004 task-020 reconfirmation). Create M1–M3 at the **next free**
> timestamps — currently `2026_07_25_000005/000006/000007` — and re-check immediately before creating them in
> case more migrations land first. Never reuse a taken slot.
- **M1** `..._create_seating_layouts_table` — bigint id, `name` unique, `longText data`, nullable uuid
  `updated_by`, timestamps. Controller keys the single shared row by `name='default'`.
- **M2** `..._create_seating_layout_versions_table` — snapshot history (bigint fk, longText, updated_by,
  created_at); `update()` prunes to newest 30.
- **M3** `..._add_event_attendance_to_guests_table` — the 6 attendance columns (+ fillable, `datetime` casts
  on the `_at` fields, `belongsTo(Admin)` relations mirroring `scannedBy()`).
- `SeatingLayoutsController@show/@update`, routes inside the `['localization','auth:sanctum']` group at
  `admin/seating-layout` (match 120 gating; **flag** if we instead want an `admin.can:<feature>` gate — that's
  a new decision, not parity).
- `GuestsController@updateGuest` — append the 6 attendance keys to `only()`; normalize UTC ISO → app tz.
- `GET /admin/me` alias (data-wrapped).
- `GuestsResources` — expose the 6 attendance fields (ISO-8601 + `*_by`).

### Admin
- **121 has ONE consolidated `guests-listing.tsx`** (the old per-type `guests-super`/`guests-view` files were
  merged into it in commit `599827f`). The launch link goes in its **TopSection `customAction`** slot, beside
  the export button (slot ~line 804 post-020 — re-derive at build). It's a **gated deep-link** (D-4 = own login;
  a plain anchor to `NEXT_PUBLIC_SEATING_MANAGER_URL`, no BFF/token). EN + AR label.
- **Gate with `checkFeaturePermission('seating', user)`** — ANDed with the page's existing `guests_listing`
  module-access gate (`hasModuleAccess`), which is expected (the page already requires `guests_listing`).
- **Add the `seating` feature to the BACKEND catalog `app/Support/AdminPermissions.php`** — the authoritative
  catalog delivered in `user.permissions`, not a frontend file. Button-only (no sidebar link / route /
  `inferFeatureId` rule) keeps `yarn check:rbac` green; if scope ever adds a link/rule, the catalog entry must
  land first or `check:rbac` exits 1.

### Mobile contract
- New routes are **admin-only** (`/admin/seating-layout`, `/admin/me`) → not mobile-facing. The 6 new
  `GuestsResources` fields are **additive**. → Additive notice only; nothing removed/renamed. The **only**
  mobile-contract-touching risk is the optional token-minting endpoint (D-4 Option a2) — check
  `docs/mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf` before adding it.

## Implementation plan

### Phase 0 — sequence after Task 020 lands
Seating edits the **same backend files** as reconfirmation (`routes/api.php`, `GuestsController`, `Guest`,
`GuestsResources`, migrations). Land 020 first (or coordinate those shared files) to avoid merge friction and
migration-timestamp collisions — same discipline 020 used sequencing its Phase B after P24.

### Phase A — backend foundation (no SPA yet)
M1–M3 + models + `SeatingLayoutsController` + routes + `updateGuest` allowlist + `/admin/me` alias +
`GuestsResources` fields + resolve D-3. Feature tests: layout show/update round-trip; seat write persists;
**attendance write persists** (not just 200); the `/me` alias returns a `data`-wrapped admin.
Gate: `composer qa`.

### Phase B — the SPA repo
Clone → `alt-static-basecode-seating`, retarget `pifApi.js` + `mapAdminToUser`, wire config. Verify end to end
against a running 121 backend: login (+OTP), guest pull, seat drag→push→persist, attendance toggle→persist,
layout save/reload, live 10s re-poll. `yarn build` clean.

### Phase C — admin launch link
Add a `seating`-gated deep-link button (D-4 = own login → just an anchor to `NEXT_PUBLIC_SEATING_MANAGER_URL`,
no BFF route, no token) + env var + EN/AR. Gate: `yarn type-check` + `yarn production`.

## Decisions

- **D-1 — Build in 121 baseline, not 123.** Decoupled + reusable; 123 (a clean clone) inherits via `--ff-only`.
- **D-2 — Seating is a 4th standalone sub-app**, API-wire, no UI merge. Retarget its API client, don't rebuild.
- **D-3 — Attendance source of truth: LOCKED = Bridge.** Add the 6 new columns; a `Guest::booted()` saving
  hook keeps legacy `check_in`/`check_in_time` in sync from `checked_in_at` (what 120 does). All existing legacy
  readers (resources/exports/mobile/dashboards) keep working unchanged. Owner accepts the temporary
  two-representation state as a **known exception** to "no dual code paths." The "one truth" cleanup (make
  `checked_in_at` canonical + migrate all legacy readers) is deferred to its **own later task**, not this one.
- **D-4 — Admin→SPA handoff: LOCKED = Option B (own login).** Seating is a separate app at its own URL; the
  admin just **deep-links** to it (a plain anchor, no token). Operators sign in on the SPA's own login screen
  (same accounts, reCAPTCHA + OTP already built). Zero token exposure, zero backend change. **Knock-on:** the
  admin-side work shrinks to a gated link button — no BFF handoff route, no `pif_token`, no `open-seating-manager`
  token logic to port. If the client later wants one-click SSO, add Option a2 (BFF + a short-lived seating-scoped
  minted token; touches `routes/api.php` → mobile-contract check) as a small follow-up. Option A (forward the
  raw 6h admin bearer in a URL) is **rejected** — it re-exposes the token the Task 005 hardening hides.
- **D-5 — Seating access = dedicated `seating` RBAC feature with 3 graded actions (LOCKED; granularity
  provisional until testing).** Add a `seating` feature to the backend catalog `app/Support/AdminPermissions.php`
  (mirrors `scanning` from Task 011), grantable to any role independently — so on-site event staff get seating
  without guest-edit/admin rights. **Actions = `view` / `check_in` / `manage`**, mapping directly onto the SPA's
  existing internal permission presets:
  - `seating:view` → `SEE_PREVIEW` (read-only).
  - `seating:check_in` → `+ MARK_ATTENDANCE` (preview + attendance).
  - `seating:manage` → `+ EDIT_LAYOUT, ADJUST_SEAT_COUNT, MANAGE_GUESTS, IMPORT/EXPORT, ALLOCATE, RESET,
    VIEW_AUDIT_LOG` (full manager). (Existing **super** stays super; v1's **demo** sandbox is not ported.)
  - **Audit finding (v1, 2026-07-25):** the SPA is already permission-array-driven (11 `hasPerm()` permissions);
    `admin.type` only *seeds* the array in one function `mapAdminToUser` (App.jsx:415-495). So the SPA change is
    **that one function** — build the permission array from 121's granted `seating` actions instead of hardcoded
    `type` presets; every downstream UI gate is unchanged. v1's `seating`/`seating-checkin`/`seating-view` (+
    `view`/`gate`/`checkin` aliases) collapse to exactly these 3 levels.
  - **Enforce BOTH sides:** gate the backend seating routes on `admin.can:seating,<action>` AND the SPA UI on the
    mapped permissions. ⚠️ v1 enforced the tiers **client-side only** (backend checked nothing — a "view" admin
    could write via the API); 121 fixes that. Never `admins.type` — do not port 120's seating `type` strings.
  - **Provisional:** re-confirm the exact action split (esp. whether `check_in` and `manage` should separate
    further, and whether audit-log needs its own action) once we test with real seating operators.
- **D-6 — Full port (LOCKED).** Bring the complete 120 backend seating footprint: `seating_layouts` +
  `seating_layout_versions` (+ `versions`/`versions/{id}` read-back endpoints) AND `seating_audit_logs` +
  `SeatingAuditLogsController` (index/store). Note: the SPA as-is doesn't call the audit-log or version-browse
  endpoints (its audit log is browser-local), so a "full port" ships those endpoints ready-to-use; **wiring the
  SPA to consume them is optional additional SPA work**, flagged in Scope. (Excludes the `gates.scan_action` /
  gate-scan attendance changes — that's Q8, a separate decision, not part of the seating port.)
- **D-7 — Keep the Vite SPA as-is; do NOT rebuild as Next.js (LOCKED).** It's proven (a month of client
  testing), decoupled (HTTP-only, no shared code), and canvas-heavy — SSR buys nothing. Rewriting = weeks +
  regression risk vs days to retarget. Accept the stack divergence (Vite / plain-JS / Tailwind v3, own build +
  lint chain). Light-touch only: reuse the shared reCAPTCHA key; give it its own lint/prettier config; TS is an
  optional later increment, never a blocker.
- **D-8 — Repo bring-in: name `alt-static-basecode-seating`, executed AFTER Task 020 (LOCKED).** Cloned from the
  120 seating source (source only — exclude `node_modules`/`dist`/`.env.local`/old `.git`), fresh `git init`,
  updated `package.json` name. **Division of labor:** agent does the local copy + retarget in one pass when work
  starts; **owner creates the GitHub remote** (`eissa-alt/alt-static-basecode-seating`) — no remote creation or
  push without owner go. Hosting origin is a deploy-time detail (must be added to backend `CORS_ALLOWED_ORIGINS`).
- Promote D-1…D-8 to `../../decisions/LEDGER.md` on completion (next id after **D41**).

## Open items / risks

- **Branding exception:** the SPA ships with PIF branding into a deliberately brand-neutral baseline (P22).
  Kept short-term per owner (timing) → **track a follow-up to neutralize** before the baseline is "clean."
- **Baseline consistency:** the SPA is **Vite / plain-JS / Tailwind v3** vs the baseline's **Next 15 / TS /
  Tailwind v4**. Fine for a standalone app, but note the divergence (own lint/build chain; not covered by the
  admin/frontend husky gates).
- **Attendance ripple:** D-3's "migrate legacy readers" path touches exports, mobile resources, dashboards —
  scope it before committing. Silent-write-loss is the trap; tests must assert persistence.
- **Sequencing vs Task 020** (shared backend files) — Phase 0.
- **`.env` (owner):** `CORS_ALLOWED_ORIGINS`, `NEXT_PUBLIC_SEATING_MANAGER_URL`, `VITE_*` — gitignored, set on
  the server; do not edit `.env*`.
- **✅ Done:** `CLAUDE.md` + `process/WORKING_MECHANISM.md` updated to "four sub-apps".

## Definition of Done

- [x] `alt-static-basecode-seating` repo mounted + builds; API client retargeted to 121.
- [x] Backend: migrations + models + `SeatingLayoutsController`/`SeatingAuditLogsController` + routes +
      `updateGuest` allowlist + `/admin/me` alias + `GuestsResources` fields; D-3 bridge resolved.
- [x] Admin: `seating`-gated launch deep-link (D-4 own-login) + EN + AR in the same commit.
- [x] Feature tests: layout round-trip, seat write **persists**, attendance write **persists**, `/me` shape,
      permission gate (`SeatingTest`, 6 tests).
- [x] Quality gate green — backend `composer qa` (pint + phpstan + **480 tests**); admin `type-check` +
      `check:rbac`; SPA `npm run build`. ⚠️ `yarn production` NOT run (needs the gitignored `.env.production`).
- [x] Mobile contract: new routes are admin-only + the 6 guest fields additive → additive-only, documented in
      HANDOFF + ledger D42. No mobile route removed/renamed; no D-4 a2 mint endpoint added.
- [x] Docs: this TASK.md → `done (code)`; index row; ledger D42; HANDOFF; `CLAUDE.md` + `WORKING_MECHANISM.md`
      "four sub-apps".
- [x] Task 020 landed first (Phase 0).
- [ ] **Owner:** merge feature branches → `dev` + push; create seating GitHub remotes; set `.env`; dev/prod
      migrate; live end-to-end QA against a running stack.
