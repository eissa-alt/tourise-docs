# Cleanup & Hardening Master Plan — next phase

> **Status:** 🅿️ **PLANNED — orchestration doc, NOT yet reviewed, NO code written.** This is a
> sequencing + scoping record for the next work phase, drafted for a second AI agent to review before
> anything is executed. Each task below is written to be picked up independently as its own
> `docs/tasks/NNN-…` folder.
>
> **Scope:** two tracks —
> - **Track A — Backend cleanup / cyan-aligned refactor** (`alt-static-basecode-backend`, some admin/frontend). **← the active track for this phase.**
> - **Track B — Security hardening backported from Saudi Forum 11** (`114-saudi-11`). **⏸️ OPTIONAL / LATER** —
>   captured here for completeness, but **deferred**; do not schedule Tasks 004/005 until Track A is done
>   and the user explicitly greenlights the security backports.
>
> **References (source of every pattern):**
> - cyan: `/Users/admin/Projects/ALT/115-cyan-basecode/cyan-basecode-repos/{cyan-backend,cyan-admin,cyan-frontend}`
> - saudi-11: `/Users/admin/Projects/ALT/114-saudi-11/saudi-forum-11-repo/{saudi-forum-11-backend,-admin,-frontend}`
>   + its security docs at `…/saudi-forum-11-repo/docs/security/`.
>
> **Hard guardrails (from `../../CLAUDE.md` + `../ai/AI_RULES.md`):** EN+AR translations same commit ·
> no new deps without justification · no framework bumps · no widening TS to `any` · no
> `console.log`/`dd()`/`dump()` · **`routes/api.php` is the mobile contract — check
> `../mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf` before touching endpoints or resource shapes** ·
> do **not** port cyan's `DynamicFormRenderer` / form-builder (CLAUDE.md #4) · Sentry stays removed.

---

## 0. Current-state baseline (verified 2026-07-07, read-only) — do NOT re-do these

Before planning new work, this is what the live repos **already** have, so the reviewer doesn't
scope duplicate effort:

| Concern | State in alt-static today | Implication |
|---|---|---|
| RBAC (roles + dynamic permissions) | **Ported** — `app/Services/PermissionService.php`, `app/Support/AdminPermissions.php`, `admin.can:` middleware | Track 1 of `CYAN_FEATURE_PARITY_MASTER_PLAN.md` is done; not re-planned here |
| `routes/api.php` grouping | **Already grouped** — `throttle:{public,sensitive,store-guest}-api` tiers, `auth:sanctum`, **50× `admin.can:`**, `Route::prefix('admin/…')` blocks (992 lines) | Todo-2A is ~complete → downgraded to hygiene only (Task 008) |
| API exception → JSON | **Already** — `app/Exceptions/Handler.php` renders JSON for `api/*` | No work |
| Resource collections | **Already** use `->additional(['status' => 'success'])` | Response unification builds on this |
| Tailwind | **Already v4** (`@tailwindcss/postcss`, `@config` bridge) — same lineage as saudi/cyan | Todo-2B(tw) → verify-only (Task 008) |
| Stack | Next 15 / React 18.3.1 / Headless UI v2 / Laravel 12 / PHP 8.2 | Matches saudi-11; no bumps |
| **Base API controller / response traits** | **ABSENT** — `Controller.php` is vanilla Laravel; **72 controllers hand-roll `response()->json(...)`** (GuestsController alone: 179) | Track A core work (Tasks 006–007) |
| **Shared upload helper** | **ABSENT** — base64/`disk('public')` upload logic duplicated across controllers | Task 005 (with P1) |
| **Private document storage** | **ABSENT** — `disk('public')` used heavily (GuestsController 23×, media 9×, …) → registrant PII on public CDN URLs | Task 005 (P1 gap) |
| **HttpOnly admin token** | **ABSENT** — admin reads `cookie.get('token')` across `auth/provider.tsx`, `withAuth.tsx`, `useFetch.ts`, … → JS-readable bearer | Task 004 (P2 gap) |
| Admin CSP | Minimal (`frame-ancestors 'none'`-ish only) | Task 004 (part of P2) |

**Provenance:** counts + file paths verified 2026-07-07 by three read-only explorations (alt backend
direct inspection; cyan-backend architecture; saudi-11 architecture/security). Re-verify any number
against the live repo before trusting it in implementation.

---

## 1. Task catalog

Each task is self-contained. **Effort:** S / M / L. **Mobile-contract risk** is called out explicitly
per task (breaking is *not* pre-approved here — flag + confirm before any resource/route shape change).

Proposed numbering continues the `docs/tasks/` sequence (last opened: `002`).

---

### Task 003 — Migration squash (full wholesale rewrite) · Track A · backend-only

- **Effort:** M · **Mobile-contract risk:** LOW *if* schema parity is proven (schema-only, no route/resource change).
- **Decision status:** ✅ **user-approved (Option 3, full squash)** — 2026-07-07. Overrides the written
  "never squash old migrations" convention **for this fresh basecode only** → needs ledger `D9` (below).

**Goal.** Collapse the accumulated migration history (**129 files = 71 `create_` + 56
`add/modify/drop/rename`**) into **~71 clean per-table `create` migrations**, each showing a table's
**final** shape (post the already-committed boolean + datetime refactors, tasks 001/002) in one place.
Fewer files, no "add column later" archaeology.

**Why now.** Fresh basecode, **no production data anywhere**; `migrate:fresh` is already the workflow
(tasks 001/002). The boolean + datetime column-type refactors are **already committed**, so the current
schema is the clean target — squashing now captures the good state.

**Reference.** cyan does **not** squash (keeps 64 incremental) — so this is an alt-specific deviation,
not a cyan port. Pattern is standard Laravel.

**Approach.**
1. **Snapshot the source of truth first.** On the current 129-migration tree:
   `migrate:fresh` → dump structure (`mysqldump --no-data --skip-comments` **or** `php artisan schema:dump`) → `before.sql`.
2. Rewrite: one `create_<table>_table.php` per domain table, folding every later `add/modify/drop` for
   that table into the single `create`. **Keep Laravel framework-default tables as their own standard
   migrations — do NOT fold:** `users`, `password_resets`, `failed_jobs`, `personal_access_tokens`,
   `jobs`, `sessions` (`session_interested_users` is a domain table → *do* fold).
3. **Foreign keys / relational columns (user-flagged).** Create all tables columns-only, then add all
   FK constraints in a **final `…_add_foreign_keys.php`** migration (order-independent, robust) — or
   order `create`s by dependency with inline `foreignId()->constrained()`. Watch pivot / polymorphic /
   self-referencing tables (e.g. `session_interested_users`).
4. Iterate with **`php artisan migrate:fresh --seed`** (not `refresh` — a rewrite shouldn't depend on
   `down()`; `fresh` just drops all). Still write correct `down()`s in the final files for hygiene.
5. Keep all **23 seeders** green — several are schema-coupled (`CategorySeeder`, `GuestSeeder`,
   `MigrateEmailContentToEditorJsonSeeder`, `EmailTemplatesSeeder`).

**Gate (acceptance test — stronger than "seed green").**
- **`diff before.sql after.sql` is EMPTY** (modulo `AUTO_INCREMENT`/ordering noise). This proves no
  silent drift in column type, nullability, default, index, or unique constraint. **Seed-green alone is
  necessary but NOT sufficient.**
- `php artisan migrate:fresh --seed` clean · `./vendor/bin/pint --dirty --test` green.
- `git diff routes/api.php` empty (schema task must not touch routes).

**Risks / watch-outs.** Silent schema drift (mitigated by the SQL diff gate); FK ordering; enum/string
lengths; JSON/generated columns; casts must still match the new column types (they already do post-001/002).

**Ledger `D9` (required).** Record: "full migration squash adopted on the fresh basecode; overrides the
'never squash old migrations' rule — **safe only while no clone of this baseline carries production
data**; the moment a downstream project has prod data, squashing is off the table (use forward
migrations)."

---

### Task 004 — Admin auth hardening: HttpOnly token + Next BFF proxy + full CSP (saudi P2) · Track B · admin (+ minor backend verify)

- **✅ DONE (code) 2026-07-12** — un-deferred by user (pre-launch, no clone has prod data). Executed as
  `docs/tasks/005-admin-httponly-token/` (folder 005; 004 = dropped squash). Ledger **D12**. Gates green +
  runtime-verified; real-env browser QA outstanding before `dev`→`main`. History below kept as the plan of record.
- ~~**⏸️ OPTIONAL / LATER (Track B — deferred).** Do not start until Track A is done + user greenlights.~~
- **Effort:** L · **Mobile-contract risk:** NONE expected (admin-web only; mobile uses its own
  `MobileAuthController` token flow) — **verify** the mobile guest OTP/login path is untouched.
- **Priority when scheduled:** HIGH value — closes XSS → account-takeover (admin currently stores a
  JS-readable bearer). High value ≠ high urgency here: it's parked until the security backports are
  greenlit.

**Goal.** Move the admin Sanctum token out of JS-readable cookies into an **HttpOnly cookie**, proxied
through a **Next.js BFF** so the browser never sees the bearer; add a **full Content-Security-Policy**.

**Current gap (verified).** Admin reads `cookie.get('token')` / `js-cookie` across `auth/provider.tsx`,
`auth/withAuth.tsx`, `hooks/useFetch.ts`, `hooks/use-listing-state.ts`, `components/profile/…`, etc.
Admin CSP is minimal.

**Reference (saudi-11 admin — implemented, with portable checklist).**
- Checklist: `…/docs/security/port-review-jul-2026/POINT_2_ADMIN_TOKEN_HTTPONLY_PLAN.md` +
  `…/PORTABLE_FEATURE_CHECKLIST.md` (§P2).
- Code: `utils/server/proxy.ts` (`setAuthCookies`/`clearAuthCookies`/`buildForwardHeaders`/
  `forwardLoginAndCaptureToken`); `pages/api/proxy/[...path].ts` (streaming catch-all, `bodyParser:false`,
  strips upstream `Set-Cookie`); `pages/api/auth/{login,login-confirmation,logout}.ts`;
  `utils/axios.ts` (isomorphic: browser → `/api/proxy`, SSR → direct Laravel w/ cookie token);
  `utils/auth-cookies.ts` (`TOKEN_COOKIE='token'` HttpOnly 6h; `AUTH_FLAG_COOKIE` JS-readable flag);
  `auth/provider.tsx` reads the **flag** cookie only; `next.config.js` env-derived full CSP.

**Approach (phased).**
1. Backend: no change expected (Sanctum bearer still issued) — **confirm** login response shape and that
   token TTL (6h) matches. Verify mobile auth routes untouched.
2. Admin BFF: add `/api/proxy/[...path]`, auth API routes, cookie helpers, isomorphic axios.
3. Codemod: remove **all** `cookie.get('token')` / `Cookies.get('token')` read sites (saudi did ~190) →
   auth injected by the proxy; gSSP reads token server-side from the request cookie.
4. `auth/provider.tsx` + `withAuth.tsx` → flag-cookie only; gSSP 401 → redirect to login.
5. `next.config.js` full CSP — adapt env origin list to alt's domains; `'unsafe-eval'` dev-only.

**Gate.** `rm -rf .next && yarn type-check && yarn production` green · EN+AR login/logout/refresh QA ·
manual: token **not** visible in `document.cookie`; uploads + binary exports still stream through proxy ·
CSP doesn't break fonts/scripts/analytics. **Mobile:** confirm `routes/api.php` + mobile auth untouched.

**Risks.** Streaming multipart uploads + xlsx/pdf exports through the proxy (saudi handles via
`bodyParser:false`, `responseLimit:false`) — test the heaviest export. CSP false-positives on inline
styles/3rd-party. SSR vs client base-URL split must be airtight.

---

### Task 005 — Private document storage + signed URLs (saudi P1) **+ extract shared UploadService** (Todo-2D) · Track B + A · backend (+ admin previews)

- **⏸️ OPTIONAL / LATER (Track B — deferred).** Do not start until Track A is done + user greenlights.
  **Note:** the **UploadService extraction (Todo-2D) is a Track A item** bundled here only because P1
  touches every upload path. If Track B stays deferred, **2D can be split out and executed on its own**
  as part of Track A (see §2).
- **Effort:** L · **Mobile-contract risk:** **HIGH — resource output changes** (document URLs become
  **signed/temporary**; mobile must consume signed URLs or the stream endpoint). **MOBILE CONTRACT
  CHANGE — flag in the mobile HTML/PDF and confirm before shipping.**
- **Priority when scheduled:** HIGH value — closes unauthenticated PII exposure (passports/IDs/photos on
  public CDN URLs). Parked until the security backports are greenlit.

**Goal.** Move sensitive registrant files off `disk('public')` to a **`private` disk** served via
**short-lived signed URLs**. Bundle with **Todo-2D**: extract the duplicated upload logic into a shared
`UploadService`/trait while every upload path is being touched anyway.

**Current gap (verified).** `disk('public')` used heavily: `GuestsController` 23×, `AdminMediaCenterController`
9×, `BulkPrintController` 5×, `CategoriesController`/`BadgesController`/`AdminPublicationController` 4×
each, speakers/sponsors/attachments 3× each.

**Reference (saudi-11 backend — implemented).**
- Checklist: `…/docs/security/port-review-jul-2026/POINT_1_PRIVATE_DOCUMENT_STORAGE_PLAN.md` +
  `PORTABLE_FEATURE_CHECKLIST.md` (§P1, incl. production migrate + CDN-purge runbook).
- Code: `config/filesystems.php` (`private` disk, **not** in `storage:link`);
  `app/Http/Controllers/GuestDocumentController.php` (`stream()` — type allow-list, `basename()`
  path-traversal guard, `Cache-Control: private, no-store`); signed route in `routes/api.php` (no bearer
  — **the signature is the auth**); uploads → `disk('private')`; `GuestsResources` emits signed URLs;
  server-side read-backs repointed (`EVisaExportsController`, `PdfController`, `BulkPrintController`, …);
  `app/Console/Commands/MigrateGuestDocsToPrivate.php` (idempotent, dry-run/restore); admin `<img>`
  previews use signed URLs (`upload-imgs-modal.tsx`, `custom-file-input-zip.tsx`).

**Approach.**
1. **Decide scope of "sensitive":** only registrant PII (passport/ID/personal photo) → `private`; keep
   genuinely public assets (sponsor logos, badge templates, media-center public images) on `public`.
   **This split is a decision — see §3.** cyan has **no** shared upload helper, so 2D is net-new.
2. Add `private` disk + `GuestDocumentController::stream` + signed route (mirror the traversal guard).
3. **Extract `UploadService`** (or a `HandlesUploads` trait): one `store(base64|UploadedFile, disk, path)`
   entry the 72 controllers reuse; replace the duplicated base64 decode/`put` blocks incrementally.
4. Repoint API resources to signed URLs for private files; repoint every server-side read-back
   (exports/PDF/print) to the private disk.
5. Migration command (fresh basecode → likely trivial, but keep it for downstream clones with data).

**Gate.** `pint --dirty --test` · `php artisan test` (note pre-existing failures) · `migrate:fresh --seed` ·
**`git diff routes/api.php` reviewed vs mobile contract** — signed-URL doc must be flagged in
`../mobile/*` · admin previews render · a private file is **not** reachable at a plain `/storage/…` URL.

**Risks.** Signed-URL TTL vs long admin sessions/exports; CDN caching of old public URLs (purge runbook);
mobile consumers (the contract change); making sure no public asset accidentally moves to `private`.

---

### Task 006 — `BaseApiController` + `ApiResponse` / `AppliesListingFilters` traits (Todo-2B) · Track A · backend

- **Effort:** S–M · **Mobile-contract risk:** NONE if adopted additively (no shape change yet).
- **Priority:** MEDIUM — best ROI of the backend-cleanup items; unblocks Task 007.

**Goal.** Introduce a shared base API controller + response/listing traits so controllers stop
hand-rolling responses. **Additive** — port the scaffolding; do not rewrite call sites yet.

**Reference (cyan-backend).**
- `app/Http/Controllers/BaseApiController.php` (uses the two traits; adds generic `applyFilters()` +
  `applySorting()`).
- `app/Http/Controllers/Concerns/ApiResponse.php` — `apiSuccess($data,$message,$meta,$status,$legacy)`
  → `{ success, status, message, data, meta? }`; `apiError($message,$errors,$status,$legacy)`
  → `{ success, status, message, error, data, errors? }`.
- `app/Http/Controllers/Concerns/AppliesListingFilters.php` — `resolvePerPage`, `resolveSort`,
  `applyExactFilters`, `applySearchFilter`, `applyLikeFilters`, `applyToggleFilters`.

**Important compatibility note.** cyan itself runs **three** coexisting response styles (`apiSuccess`/
`apiError`, Resource `->additional(['status'=>'success'])`, and legacy raw `response([...])`) — it never
fully unified. alt already uses the Resource style. So the trait's `status`/`success` keys must be
**backward-compatible** with alt's current `{status, data}` shape that admin/frontend/mobile already
parse (keep `status: 'success'|'failed'`; `success`/`message` are additive).

**Approach.** Port the base + two `Concerns` traits verbatim (namespace-adjusted). Wire into **one pilot
controller** (e.g. a low-risk admin CRUD) to prove the shape is byte-compatible with the existing client
parsing. Ship the scaffolding; leave the other 71 controllers for Task 007.

**Gate.** `pint --dirty --test` · pilot controller's existing tests green · admin listing that hits the
pilot still parses `{status,data,meta}` identically.

---

### Task 007 — Incremental response unification (Todo-2C) · Track A · backend (multi-PR)

- **Effort:** L (spread over many small PRs) · **Mobile-contract risk:** **HIGH per endpoint** — response
  shape is the contract. **Never** big-bang; migrate module-by-module and diff the JSON.
- **Priority:** MEDIUM — depends on Task 006. Explicitly **not** a blind 72-file sweep.

**Goal.** Migrate the ~72 controllers' hand-rolled `response()->json(...)` onto `apiSuccess`/`apiError`
**where the emitted shape is already identical**, one module at a time.

**Why incremental.** `GuestsController` alone has 179 raw responses; many are mobile-facing. A blanket
rewrite risks silently changing keys mobile/admin/frontend depend on. cyan didn't unify fully for the
same reason.

**Approach (per module).** Snapshot the endpoint's current JSON → refactor to the trait → **diff the JSON
is identical** → gate → commit. Prioritize **admin-only** controllers first (no mobile risk); do
**mobile-facing** controllers (`Mobile*`, `AuthController`, guest register/accept/reject) last, only after
confirming the shape against `../mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf`.

**Gate (per PR).** Endpoint JSON byte-identical (or documented + mobile-flagged) · `pint --dirty --test` ·
`php artisan test` · `git diff routes/api.php` empty.

---

### Task 008 — Hygiene grab-bag: routes polish (2A) + tailwind verify (2B/tw) + `osv-scanner` audit workflow · Track A/B · low priority

- **Effort:** S · **Mobile-contract risk:** NONE (routes stay byte-stable).

Three small, independent items — bundle or split as convenient:
- **Routes hygiene (Todo-2A, mostly done):** remove dead commented lines (e.g. the empty
  `Route::middleware("localization")->group(function () {});` at ~L181), tidy grouping/ordering. **Keep
  routes byte-stable for mobile** — cosmetic only.
- **Tailwind verify (Todo-2B/tw):** alt is already v4; confirm parity with saudi/cyan v4 config
  (`@config` bridge, `focus:ring-3` restores, `*-opacity-*` → `/modifier` all zero). Likely a no-op +
  a note.
- **`osv-scanner` audit workflow (added — not on the original list):** saudi documents that `yarn audit`
  is broken on Next 15 with gitignored lockfiles; a fresh-install + `osv-scanner` pass is the authoritative
  dependency check. Cheap, real. Ref: saudi `docs/security/part-2-may-2026/`.

---

## 2. Recommended sequencing & dependency graph

```
Track A (backend) — ACTIVE               Track B (security) — ⏸️ OPTIONAL / LATER (deferred)
──────────────────                       ──────────────────────────────
003 migration squash  ── independent     004 admin HttpOnly + BFF + CSP (P2)   ── independent (admin)
        │                                         │
006 BaseApiController + traits (2B)      005 private docs + signed URLs (P1)    ── backend + admin
        │                                     + UploadService (2D — Track A, see note)
        ▼
007 response unification (2C, multi-PR, depends on 006)
        ▲
008 hygiene (routes / tailwind-verify / osv-scanner) — anytime, low priority

  (2D UploadService: bundled into 005 for efficiency, but can be split out into Track A
   as a standalone task if Track B stays deferred.)
```

**Recommended global order (my opinion):**
1. **Track A now:** **003 (squash)** can start immediately — backend-only, independent of the in-flight
   admin `catch: any → unknown` work.
2. **006 → 007** — backend response cleanup; 007 trails 006 and is many small PRs.
3. **008** — polish, whenever.
4. **If Track A defers 005:** decide whether to pull **Todo-2D (UploadService)** out as a standalone
   Track A task or leave it parked with P1.
5. **Track B (004 P2, 005 P1) — deferred.** Revisit only after Track A completes **and** the user
   explicitly greenlights the security backports. When scheduled, 004 (admin) should wait for the
   `any → unknown` cleanup to land to avoid collisions; both remain HIGH *value*.

**Rationale:** security (P1/P2) closes *real* PII + XSS holes and would normally rank high — but per the
current directive it's **optional / later**. Track A (migration squash + backend response cleanup)
proceeds now. Response unification is the largest, riskiest, most mobile-sensitive item → last,
incremental, gated per module.

---

## 3. Decisions needed before execution (ledger candidates)

| # | Decision | Needed for | Default recommendation |
|---|---|---|---|
| D9 | Adopt full migration squash on fresh basecode (overrides "never squash"), safe only while no clone has prod data | 003 | ✅ approved 2026-07-07 — record it |
| — | Response envelope: keep `status: 'success'/'failed'` as the stable key (add `success`/`message` additively)? | 006/007 | Yes — backward-compatible with current admin/frontend/mobile parsing |
| — | If Track B stays deferred, split **Todo-2D (UploadService)** into a standalone Track A task? | 005/2D | Split it out only if the shared-upload cleanup is wanted before P1 is greenlit |
| ⏸️ | *(deferred with Track B)* Which files are "sensitive → private disk" vs stay public | 005 | Only registrant PII (passport/ID/photo) → private; public assets stay public |
| ⏸️ | *(deferred with Track B)* Accept the P1 **mobile-contract change** (signed URLs) | 005 | Confirm with mobile owner; flag in `../mobile/*` before shipping |
| ⏸️ | *(deferred with Track B)* Signed-URL TTL vs long admin export sessions | 005 | Match saudi's default; lengthen only if exports time out |

---

## 4. Quality gates (every push, all tasks)

- **Backend:** `./vendor/bin/pint --dirty --test` · `php artisan test` (note pre-existing failures —
  ExampleTest 403 + 2 avatar tests) · `migrate:fresh --seed` clean · **`git diff routes/api.php` reviewed
  vs the mobile contract**.
- **Admin / Frontend:** `rm -rf .next && yarn type-check && yarn production` · ESLint 0 warnings ·
  EN+AR translations in the **same** commit · EN+AR visual QA.
- **Commits:** branch off `dev`; `P<phase>.<task> — <short imperative>`; manifests only
  (`composer.lock`/`yarn.lock` gitignored); no `console.log`/`dd()`/`dump()`.
- **Docs:** this plan + per-task `TASK.md` on `main`; promote durable decisions to `../decisions/LEDGER.md`.

---

## 5. Cross-references

- [CYAN_FEATURE_PARITY_MASTER_PLAN.md](CYAN_FEATURE_PARITY_MASTER_PLAN.md) — RBAC/UI/SMTP tracks (RBAC done).
- [CYAN_BASECODE_MIGRATION_PLAYBOOK.md](CYAN_BASECODE_MIGRATION_PLAYBOOK.md) — house style for cyan replays.
- [../decisions/LEDGER.md](../decisions/LEDGER.md) — D1…D8; add **D9** (migration squash) here.
- [../tasks/README.md](../tasks/README.md) — open `003`…`008` folders from `_TEMPLATE` as each starts.
- [../HANDOFF.md](../HANDOFF.md) — current session state.
- Mobile contract: [../mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf](../mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf).
- saudi-11 security checklists (P1/P2): `114-saudi-11/saudi-forum-11-repo/docs/security/port-review-jul-2026/`.

## 6. Exploration provenance (2026-07-07, read-only)

Backing inventories were produced by three read-only explorations: (a) direct inspection of
`alt-static-basecode-backend` (base controller absent, 72 controllers, 129 migrations = 71 create + 56
alter, routes already grouped, `disk('public')` heavy, admin `cookie.get('token')` heavy); (b)
`cyan-backend` architecture (BaseApiController + `Concerns/{ApiResponse,AppliesListingFilters}`, 3
coexisting response styles, no shared upload helper, 64 incremental migrations); (c) `saudi-11`
architecture + security (P1 private-doc storage, P2 HttpOnly BFF + CSP, portable checklists). **Re-verify
every count against the live repos before trusting it in implementation.**
