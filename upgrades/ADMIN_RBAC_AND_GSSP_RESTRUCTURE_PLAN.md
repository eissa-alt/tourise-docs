# Admin RBAC + `getServerSideProps` Restructure Plan

> **Status:** 🅿️ planned — no code written yet. This is the design/decision record for two **related but separable** admin migrations, mirroring `cyan-admin`:
> - **Track A — `getServerSideProps` (GSSP) restructure** (frontend-only, achievable on alt's *existing* `type` model).
> - **Track B — Admin roles/access RBAC** (multi-repo: backend-first + frontend roles module; touches the mobile contract).
>
> **Scope:** `alt-static-basecode-admin` (+ `alt-static-basecode-backend` for Track B). The `-frontend`/`-landing` apps are out of scope.
> **Reference implementation:** `cyan-basecode-repos/cyan-admin` (+ `cyan-backend`). Re-verify every count against the live repo before trusting a number.
> **Guardrails (lineage):** `yarn` (not npm); EN+AR translations same commit; branch per sub-app off `dev`; `yarn.lock`/`composer.lock` gitignored → commit manifests only; no `console.log`/`dd()`/`dump()`; no widening TS to `any`; **do NOT port cyan's `DynamicFormRenderer`/form-shapes** (CLAUDE.md #4 + `../ai/ARCHITECTURE_NOTES.md`).

---

## 0. Why these two tracks are entangled

Every protected alt page carries an ~80-line `getServerSideProps` that does **two unrelated jobs**:

1. **Access gate** — server-side `Axios.get('/get-profile')` then redirect if `admin.type !== 'super'` (some pages allow a small set, e.g. invitations allow `super | invitation | logistics`).
2. **Query → props** — read `?page=&first_name=&status=…` and pass them as props into the listing component.

`cyan-admin` deleted GSSP from **all** pages by replacing those two jobs with:

1. `checkFeaturePermission('<feature>', user)` — a **client-side** gate that reads `user.permissions` → **this depends on the RBAC system (Track B)**.
2. `useListingState(...)` — the hook that reads/writes `router.query` → **this is part of the listing-stack (tables) migration**.

So GSSP removal is the visible tip of two bigger migrations. The good news: **Track A can be done independently** by keeping alt's existing `type` model and a minimal query-reader, *then* Track B can layer RBAC on top without re-restructuring the pages.

### Snapshot (verified 2026-06-22)

| Metric | cyan-admin | alt-admin |
|---|---|---|
| Page `.tsx` files | ~67 | ~144 |
| Files with `export const getServerSideProps` | **0** | **122** |
| `withAuth` HOC | present, **byte-identical to alt** | present |
| Access gate | `user.permissions[featureId]` (roles) | `admin.type` string, enforced in GSSP |
| Query params | `useListingState` → `router.query` | GSSP → props |
| Roles module (`/roles/*`) | full CRUD | **does not exist** |
| Backend `Role` model / permission catalog / `admin.can` middleware | yes | **none** |

---

## 1. Critical constraints (read before scoping)

1. **Alt's admin API has no server-side authorization.** `/admins` sits under `auth:sanctum` only; `AdminsController` treats `type` as a *filter*, not a gate. **Today the GSSP `type` check is the only (UX-level) gate** — the API already returns admin data to any authenticated admin. Consequences:
   - Moving the gate client-side (Track A) is **security-neutral** (the API was already open; GSSP was only a redirect).
   - **Real** access control (Track B) requires adding backend enforcement (`admin.can:<feature>`), or RBAC is cosmetic/bypassable.
2. **Track B reshapes `/get-profile`** (drop `type`; add `role` + `permissions{}`). `/get-profile` is in the **mobile contract** — per CLAUDE.md #4, **read `docs/mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf` before changing it**, and prefer an additive shape (keep `type` until mobile is confirmed) over a breaking one.
3. **~20 alt-only conference routes have no cyan feature IDs** — sessions, workshops, agenda, event-days, meeting-rooms, publications, media-center, notifications, hotels, e-visa, traveling-status, positions, tiers, areas, gates, scans, landing-page, rg-integration, cvent-integration, guest-drafts, bulk-print, email logs. Track B must **design new feature IDs + catalog entries** for these; they cannot be copied from cyan.
4. **Alt's admin model is richer than cyan's.** Alt has admin `type` tabs (`data/admins-types.tsx`), `action_ids`, `dashboard_component_ids`, and per-type guest listings (`guests-super`, `guests-guest`, …) selected by `admin.type` in GSSP. Cyan collapsed all of this into one `/admins` route + one `guests-listing` + roles. Track B is therefore also a **data + UX consolidation**, not just an auth swap.

---

## TRACK A — `getServerSideProps` restructure (frontend-only)

**Goal:** make alt pages lean like cyan, **without** backend changes, by keeping alt's existing `type` model. Reversible, no mobile-contract impact.

### A.0 What replaces each GSSP responsibility

| GSSP concern (today) | Track A replacement |
|---|---|
| Auth redirect | `withAuth` (already client-side, cookie token) — **no change** |
| Profile fetch | `components/layout/header.tsx` already does `GET /get-profile` → `updateUser` — **no change** |
| Access gate (`type`) | client-side check in the page shell using `user.type` |
| Query → props | listing component reads `useRouter().query` (minimal) or `useListingState` (if/when the tables track lands) |
| Lang/i18n | `_app.tsx` already resolves lang client-side — **no change** |
| Root `/` + 404 redirects | convert to cyan's client-only pattern (optional cleanup) |

### A.1 Introduce a small client-side gate helper

Add a thin wrapper so pages stay 6–10 lines and the `type` rule lives in one place. Two viable shapes (pick one in the pilot):

- **Option 1 — keep `withAuth`, add a `<TypeGate types={['super']}>` shell component** that reads `useAuth().user`, shows `<APiLoading/>` while `user` is loading, renders a "not authorized" panel otherwise. Page becomes:
  ```tsx
  const Admins = () => (
    <TypeGate types={['super']}>
      <AdminsListing />
    </TypeGate>
  );
  export default withAuth(Admins, { comeback: true });
  ```
- **Option 2 — extend `withAuth` config** with `allow?: string[]` that performs the same `user.type` check internally. (Closer to cyan's eventual `feature` option; smoother upgrade path to Track B.)

> Recommendation: **Option 1** for the pilot (smallest blast radius, no change to the shared `withAuth`), revisit Option 2 if Track B is greenlit.

### A.2 Per-page-shape recipes

Pages fall into a handful of shapes. Map each to a recipe:

| Page shape | Example | Recipe |
|---|---|---|
| **Listing** (gate + query→props) | `admins/index.tsx`, `categories/index.tsx`, `guests/index.tsx` | Strip GSSP; gate via §A.1; move filter reads into the listing component (`useRouter().query`); delete the `*ListingProps` prop type + plumbing. |
| **Create / Edit** (gate + `params.id`) | `admins/create.tsx`, `admins/edit/[id].tsx` | Strip GSSP; gate via §A.1; read `id` from `useRouter().query.id` in the form component (it already runs client-side after hydration). |
| **Gate-only** (no query) | `profile.tsx`, dashboards | Strip GSSP; gate via §A.1 (or just `withAuth` if no type restriction). |
| **Redirect-only** (`/`, `[...notFound]`) | `pages/index.tsx`, `[...notFound].tsx` | Convert to cyan's client `useEffect` redirect using cookie/browser lang. |
| **Special** (multi-type allow-lists, slug-driven guest listings) | `invitations/*`, `guests/[slug]/*` | Port the allow-list into `types={[...]}`; for per-type guest listings, **keep alt's per-type components for Track A** (consolidation is a Track B concern). |

### A.3 The guests module caveat

Alt selects a *different listing component per `admin.type`* inside GSSP (`guests-super` vs `guests-guest` …). For **Track A**, do **not** consolidate — keep the per-type components and pick them client-side from `user.type`. (Consolidation into one `guests-listing` is explicitly **Track B**, because it depends on the roles model.)

### A.4 Race condition to handle

GSSP guaranteed `user` existed before render; client-side it does not. Every gated shell **must** render `<APiLoading/>` while `user` is undefined (header is still fetching `/get-profile`), then evaluate the gate — otherwise a brief flash of unauthorized content or a false redirect. Cyan's pattern: `if (!authenticated) return <APiLoading/>;` then the feature check (returns false until `user` loads).

### A.5 Scope & sequencing

- **Pilot first:** `admins/{index,create,edit}` + one multi-type page (`invitations/index`) to prove all recipe shapes, gate green, then roll the remaining ~118 pages in batches grouped by shape.
- This is mechanical but large (122 files). Per-area commits (`refactor(admin): drop getServerSideProps from <area> pages`).

### A.6 Quality gate (Track A)

- `yarn type-check` + `yarn production` after each batch.
- Manual: log in as `super` and (if available) a non-`super` admin; confirm gated pages redirect/deny correctly client-side; confirm listing filters still hydrate from the URL (`?page=2&status=…`), and that deep-linking + browser back/forward still work.
- EN+AR for any new "not authorized" copy (add `web:not_authorized`).

### A.7 Risks (Track A)

- **Cosmetic gate** — unchanged from today (API already open); document, don't pretend it's enforcement.
- **URL-state regressions** — the biggest functional risk; without GSSP the component owns query parsing. Test pagination/filter deep-links per migrated listing.
- **SEO/SSR** — admin is auth-gated, non-indexed; losing SSR is irrelevant here.

---

## TRACK B — Admin roles/access RBAC (backend-first, multi-repo)

**Goal:** cyan-parity roles & feature-permissions: roles CRUD, a feature×action permission matrix, admins assigned a `role_id`, and **server-enforced** authorization. **Backend must land first** or the frontend gate is cosmetic.

### B.1 Backend (alt-static-basecode-backend) — do first

Mirror cyan-backend:

1. **`roles` table + `Role` model** (`permissions` JSON, `is_super` flag, `name_en`/`name_ar`); seed a Super Admin role.
2. **`admins.role_id`** FK + **data migration** mapping legacy `type` (+ `action_ids`, `dashboard_component_ids`) → seeded roles (e.g. roles mirroring `guest`, `badge`, `invitation`, `logistics`, `view`).
3. **Permission catalog** (`app/Support/AdminPermissions::CATALOG` equivalent) — feature×action matrix. **Extend it with the ~20 alt-only conference features** (see §1.3); each needs feature id + actions.
4. **`PermissionService`** — resolve an admin's matrix; Super Admin short-circuits to the full catalog server-side.
5. **`EnsureAdminPermission` middleware** (`admin.can:<feature>[,<action>]`) — wrap admin API routes. **This is the actual security boundary.**
6. **`/get-profile` + login resource** — emit `role` + `permissions{}`. ⚠️ **Mobile contract:** read the PDF first; prefer **additive** (keep `type` alongside `role`/`permissions` until mobile migrates) to avoid breaking the mobile client.
7. Endpoints to add (cyan reference): `GET /permission-catalog`, `GET /roles`, `GET /roles/select`, `POST /roles`, `GET /roles/:id`, `PUT /roles/:id`, `DELETE /roles/:id`; admins endpoints accept `role_id`.

Backend gates: `composer audit` clean · `./vendor/bin/pint --test` · `php artisan test` · `git diff routes/api.php` reviewed against the mobile contract.

### B.2 Frontend (alt-static-basecode-admin) — after backend

1. **Port utils:** `utils/checkFeaturePermission.ts` (`checkFeaturePermission`, `checkPermission`), `utils/checkActionPermission.ts`, `utils/inferFeatureId.ts`.
2. **Port roles module:** `pages/[lang]/roles/{index,create,edit/[id]}.tsx` + `components/admin-modules/roles/{roles-listing,roles-form}.tsx` (checkbox permission matrix, Super Admin read-only) + `interfaces/role.tsx`.
3. **Update admins module:** `admins-form` → `role_id` dropdown (from `GET /roles/select`) replacing the `type`/`action_ids`/`dashboard_component_ids` pickers; `interfaces/admin.tsx` (`role_id`, `role`, `permissions?`; remove `type`).
4. **Swap page gates:** replace Track-A `type` gates with `checkFeaturePermission('<feature>', user)`.
5. **Sidebar:** replace `access: ['super',…]` with `featureId: '…'` per link (cyan `data/sidebar-links.tsx` pattern), filter via `checkFeaturePermission`.
6. **Guests consolidation:** collapse per-type guest listings → single `guests-listing` + `checkActionPermission` for row actions (this is the big UX change deferred from Track A §A.3).
7. **Translations:** add `web:perm_feature_*` / `web:perm_action_*` matrix labels + `web:not_authorized` (EN+AR).
8. **Audit `user.type` readers** (print modal, integrations, guest listings) → migrate to `checkPermission`.

### B.3 Risks (Track B)

- **Mobile-contract break** on `/get-profile` — highest-risk item; additive shape + PDF check mandatory.
- **Data migration correctness** — legacy `type` → roles must preserve every admin's current effective access; needs a reversible migration + verification query.
- **Catalog completeness** — missing a conference feature id = that page is unreachable (gate returns false). Inventory all ~20 alt-only routes before flipping sidebar to `featureId`.
- **Two-system window** — while migrating, some pages on `type`, some on `permissions`; keep both readable on the profile until the cutover commit.

---

## Order of operations

1. **Decision** — confirm Track A only, Track B only, or A→B (recommended: A first as the lean-page foundation, then B layers RBAC without re-restructuring pages).
2. **Track A** — pilot (`admins` + `invitations`) → batch-roll the remaining GSSP pages → gate-green per batch.
3. **Track B.1 (backend)** — roles/catalog/middleware/profile on a backend branch off `dev`; mobile-contract check; data migration; gate-green.
4. **Track B.2 (frontend)** — roles module + gate swap + sidebar `featureId` + guests consolidation; gate-green; EN/AR QA.

## Quality gates (every push)

- **Backend:** `composer audit` clean · `./vendor/bin/pint --test` · `php artisan test` · `routes/api.php` reviewed vs mobile contract.
- **Admin:** `rm -rf .next && yarn type-check && yarn production`; EN+AR visual QA on auth/sidebar/listing surfaces.
- **Commits:** branch off `dev`; EN+AR same commit; manifests only (locks gitignored).

## Open decisions (settle before coding)

- **Track A gate shape:** `<TypeGate>` shell (Option 1) vs `withAuth({ allow })` (Option 2).
- **Track B `/get-profile`:** additive (keep `type`) vs breaking — gated on the mobile-contract PDF.
- **Guests consolidation:** keep per-type components (Track A) vs collapse to one listing (Track B) — confirm timing.
- **Conference feature catalog:** who owns designing the ~20 new feature ids/actions.

## Cross-references

- GSSP/RBAC exploration (this session): cyan `withAuth` is byte-identical; gate is `user.permissions[featureId]`; 122 alt GSSP files vs 0 in cyan.
- `../ai/ARCHITECTURE_NOTES.md` — the form-shapes "keep the older pattern" rule (do not port `DynamicFormRenderer`).
- `CYAN_BASECODE_MIGRATION_PLAYBOOK.md` — house style for cyan-targeted replay docs.
- Mobile contract: `../mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf` (read before any `/get-profile` change).
