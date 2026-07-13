# Storage-URL Consolidation Plan

> **Goal doc — the target end-state + the path to it.** Collapse the redundant, inconsistent
> storage-URL environment variables across backend + admin + frontend down to a **single source of
> truth**. Planning only; no code changed yet.
>
> **Context:** builds on the admin upload-preview 404 fix (backend `ff97c7b`, playbook
> [`STORAGE_UPLOAD_URL_FIX_PLAYBOOK.md`](STORAGE_UPLOAD_URL_FIX_PLAYBOOK.md)) which established `APP_URL`
> as the framework-native host source.
>
> **Pre-launch:** not in production yet — no live data, no CDN cache, mobile app not shipped. So we can
> take the aggressive/clean path (drop vars, change values) without back-compat gymnastics or a mobile
> byte-identical-URL guarantee.

---

## 1. The end-state (what we'll have when done)

| App | Before | After |
|---|---|---|
| **Backend** | `PUBLIC_STORAGE_URL` + `PUBLIC_STORAGE_URL2` | **none** — `APP_URL` only |
| **Admin** | 3 × `NEXT_PUBLIC_STORAGE_URL*` | **1** (`NEXT_PUBLIC_STORAGE_URL` = `…/storage` root) + `utils/storage.ts` |
| **Frontend** | 1 dead var | **none** |

### Backend — `.env` storage section
```diff
- PUBLIC_STORAGE_URL=http://127.0.0.1:8000/storage/uploads      # dead → delete
- PUBLIC_STORAGE_URL2=http://127.0.0.1:8000/storage             # replaced by APP_URL → delete
  APP_URL=http://127.0.0.1:8000                                 # the single source of truth
```
**Backend keeps ZERO `PUBLIC_STORAGE_URL*` vars.** Every public-asset URL is produced by
`Storage::disk('public')->url('module/folder/file')`, which resolves through
`config/filesystems.php` → `env('APP_URL').'/storage'` (Laravel default, already in place).

- Emitted URL: `http://127.0.0.1:8000/storage/{module}/{folder}/{file}` — **identical** to today's
  `PUBLIC_STORAGE_URL2` output, so nothing downstream visibly changes.

### Admin — `.env.local` storage section
```diff
- NEXT_PUBLIC_STORAGE_URL=http://127.0.0.1:8000/storage/uploads          # value changes ↓
+ NEXT_PUBLIC_STORAGE_URL=http://127.0.0.1:8000/storage                  # now the storage ROOT
- NEXT_PUBLIC_STORAGE_URL2=http://127.0.0.1:8000/storage                 # merged into the one above → delete
- NEXT_PUBLIC_STORAGE_URL_ATTACHMENTS=http://127.0.0.1:8000/storage/attachments  # derived in code → delete
```
**Admin keeps ONE var** — `NEXT_PUBLIC_STORAGE_URL` pointing at the storage **root** (`…/storage`). A tiny
`utils/storage.ts` derives the rest:
- `uploadUrl(field, file)` → `{base}/uploads/{field}/{file}`
- `attachmentsUrl(file)` → `{base}/attachments/{file}`
- `moduleUrl(module, field, file)` → `{base}/{module}/{field}/{file}`

> ⚠️ **Note the value change:** `NEXT_PUBLIC_STORAGE_URL` goes from `…/storage/uploads` to `…/storage`.
> The name previously implied "uploads"; post-refactor it means the storage **root**, and code appends the
> suffix. (Stretch option, §4.)

### Frontend — `.env.local`
```diff
- NEXT_PUBLIC_STORAGE_URL=http://127.0.0.1:8000/storage/uploads   # dead → delete
```
**Frontend keeps ZERO storage vars** (it only had dead/commented refs). *You'll clean FE `.env.local`
yourself after admin is done.*

---

## 2. Why (the audit that drives this)

### Backend (`.env`)
| Var | Value | Status |
|---|---|---|
| `PUBLIC_STORAGE_URL` | `…/storage/uploads` | **DEAD** — only commented refs (`GuestsExportView`, `GuestsResources`) |
| `PUBLIC_STORAGE_URL2` | `…/storage` | **live, ~40 sites / ~28 files** — always `env('PUBLIC_STORAGE_URL2').'/{module}/{folder}/'.$file` |

Two sites already self-heal via `env('PUBLIC_STORAGE_URL2', url('/storage'))` (`AppConfigController`,
`AdminConferenceController`/`Resource`) — `url('/storage')` derives from `APP_URL`, i.e. the target.

**~40 live sites, grouped:**
- **Admin resources:** `CategoriesResources`(2), `BadgesResources`(1), `ZonesResources`(1),
  `SpeakersResources`(1), `SponsorsResources`(1), `AdminWorkshopResource`(1), `OrganizationsResources`(2),
  `EmailConfigResources`(4), `EmailsResources`(4), `ScansResources`(1), `AdminMediaImageResource`(1),
  `AdminPublicationResource`(1), `AdminMediaCenterResource`(2), `AdminConferenceResource`(1).
- **Mobile resources:** `Mobile/WorkshopDetailResource`(2), `Mobile/SessionDetailResource`(2),
  `Mobile/SpeakerResource`(1), `Mobile/MediaCenterResource`(2), `Mobile/PublicationResource`(1),
  `Mobile/MediaImageResource`(1); + `MobileSponsorController`(1). *(Pre-launch → no byte-identical
  guarantee needed, but the output is identical anyway.)*
- **Landing resources:** `LandingPageZoneResource`(1), `LandingPageSpeakerResource`(1),
  `LandingPageSponsorResource`(1).
- **Controllers:** `EmailsTemplatesController`(3), `AdminSessionController`(2), `AppConfigController`(1),
  `AdminConferenceController`(1).

### Admin (`.env.local`, 3 vars)
| Var | Used by |
|---|---|
| `NEXT_PUBLIC_STORAGE_URL` (`…/uploads`) | `next.config.js` CSP (only `.origin`); `custom-file-input{,-3}.tsx` (`/${inputName}/`) — **LIVE path**, the guest `/upload` endpoints return no public `url` (private disk, §4); most guest see-more modals (`see-more-admin.tsx`, `by-admins/*/step-*.tsx`) use it **as fallback behind task-006 signed `*_url`** — but `see-more-guest-draft.tsx:214` has **no `_url` fallback** (see §4a, possible pre-existing 404) |
| `NEXT_PUBLIC_STORAGE_URL2` (`…/storage`) | `custom-file-input-poster-simple.tsx`, `custom-file-input-bg.tsx` (`/${moduleName}/${inputName}/`) |
| `NEXT_PUBLIC_STORAGE_URL_ATTACHMENTS` (`…/attachments`) | `custom-attachments-input.tsx` |

### Frontend (`.env.local`)
`NEXT_PUBLIC_STORAGE_URL` — **DEAD** (commented refs only in `share/`+`success/sharebtn-sections.tsx`,
`custom-file-input-3.tsx`).

### Problems this fixes
1. Three admin vars = same host + fixed suffix → redundant.
2. Two roots (`…/storage/uploads` vs `…/storage`); `/uploads` is legacy.
3. `.env.production` near-empty → `NEXT_PUBLIC_*` inlined as `undefined` at build. (Latent; not biting yet
   since pre-launch — but the `.env.example` deliverable prevents it.)
4. Post-006 dead public fallbacks for sensitive files (now on the private disk).
5. ~40 scattered `env('PUBLIC_STORAGE_URL2')` calls (also what Larastan's `noEnvCallsOutsideOfConfig` discourages).

---

## 3. Decisions (locked with user, 2026-07-13)

- **Backend = B3-full:** drop **both** backend vars; single source = `APP_URL`.
- **Admin:** collapse 3 → **1** (`NEXT_PUBLIC_STORAGE_URL` = storage root) + `utils/storage.ts`.
- **Frontend:** delete the dead var (user cleans FE `.env.local` after admin).
- **Task-006 cleanup:** remove the dead sensitive-file public fallbacks; rely on signed `*_url`.
- **Pre-launch:** aggressive path OK — value/name changes fine, no mobile byte-identical constraint.
- **`.env.example`:** ship tracked templates (admin + frontend) as the guard against empty prod env.

---

## 4. Stretch (0 admin vars) — PARTIALLY BLOCKED (verified 2026-07-13)

The original stretch idea was "drop the admin storage var entirely — every upload endpoint returns a full
`url`, so the file-input components consume that directly." **That premise is only half true**, verified
against the controllers. It splits cleanly by disk:

**Public-disk uploads → 0-var-ready.** The *module* upload controllers return a live `'url' => $url`
(a real public `/storage` URL):
- `BadgesController`, `CategoriesController` (share posters), `SpeakersController`, `SponsorsController`,
  `EmailsTemplatesController`, `EmailsConfigsController`, `EmailsAttachmentsController` — all
  `Storage::disk('public')`.
- Consumers: `custom-file-input-poster-simple.tsx`, `custom-file-input-bg.tsx` (both already
  `response.data.url || <rebuild>`), `custom-attachments-input.tsx` (`item.url || <rebuild>`). These can drop
  the env-var rebuild half and rely on the live `url` — **the `STORAGE_URL2` + `_ATTACHMENTS` vars go away
  regardless (that's the primary plan); the stretch only removes their dead `||` fallbacks.**

**Private-disk (guest PII) uploads → NOT 0-var-ready, and the rebuild is LIVE, not dead.** The guest
endpoints `POST /upload`, `/upload-document` (+ their `*Admin` variants) write to `Storage::disk('private')`
(`personal_image`, `document_copy`, `visa_copy` — task-006/D14). A private file has **no public URL**, so
these endpoints return `data` (filename) **only** — the `'url'` key is not just commented, it's *impossible*
to fill with a public URL. Therefore in `custom-file-input.tsx` / `custom-file-input-3.tsx` the
`${NEXT_PUBLIC_STORAGE_URL}/${inputName}/...` branch is **the live path**, not a fallback — dropping the var
there would break the guest upload preview. These sites keep the 1 admin var. (This is why the primary plan
keeps exactly 1 var — it's structurally required by the private-disk sites, not just "safer".)

> **Correction to an earlier framing:** the guest upload comments `// 'url' => $image/$url,` were removed as
> dead code (backend `efcc027`) — but the reason is *private disk → no public URL*, not "almost-ready to
> uncomment." Re-enabling them is impossible for private files. The stale duplicate public-disk `return`
> blocks in `BadgesController`/`CategoriesController` were removed in the same commit (those *are* public;
> the live return right below already emits `'url' => $url`).

**Verdict:** don't chase 0 admin vars. Take the public-side fallback cleanup opportunistically *if* doing the
component pass anyway; the private-side sites pin the count at **1 admin var** no matter what.

### 4a. `see-more-guest-draft` — TRACED: dead/stub feature, no live 404 (2026-07-13)

`see-more-guest-draft.tsx:214` renders `<img src={`${NEXT_PUBLIC_STORAGE_URL}/personal_image/${draft.personal_image}`} />`
with **no `_url` fallback** and `personal_image` now on the private disk — so at first glance a 404 risk.
**Traced end-to-end: the whole feature is a stub, so the `<img>` is never reached.**

- Admin: `guest-drafts-listing.tsx:195` sets `moduleName: 'guest-drafts'` → the modal fetches
  `GET /guest-drafts/{itemId}` (`see-more-guest-draft.tsx:69`).
- Backend: **no `guest-drafts` route, controller, or resource exists.** Confirmed 3 ways — no string in
  `routes/api.php`, no `*Draft*` controller, and live `php artisan route:list` (329 routes) has **zero** draft
  entries. The fetch 404s in `useEffect` → modal shows its error state → line 214 never renders.

So this is **not a live bug** — it's a UI stub (listing page + modal) wired to a backend endpoint that was
never built. Matches "not really used; may enable later."

**When re-enabling this feature (checklist, NOT part of this plan):**
1. Build the backend `guest-drafts` route + controller + `GuestDraftResource`.
2. In that resource expose `personal_image` as a **signed** URL via `GuestDocumentController::signedUrl(...)`
   — same pattern as `GuestsResources.php:76` — because the file is private.
3. Change `see-more-guest-draft.tsx:214` to consume the signed `draft.personal_image_url`, **not** the
   `${NEXT_PUBLIC_STORAGE_URL}/personal_image/...` rebuild (that line was written for the old public-disk
   world and is wrong on both counts now: endpoint absent + file private).

**Consequence for THIS plan:** line 214 needs no special handling during the env-var consolidation — it's
unreachable. The 1 admin var it references is kept anyway (pinned by the live guest file-input sites, §4).

---

## 5. Execution order (phased — each its own commit, gate-green)

1. **Frontend** — delete dead `NEXT_PUBLIC_STORAGE_URL`; scrub commented refs. `yarn type-check` + `yarn production`.
2. **Admin** — add `utils/storage.ts`; repoint ~10 call sites + `next.config.js`; drop 2 vars; remove dead
   sensitive fallbacks; add `.env.example`. Gate green.
3. **Backend** — replace ~40 `env('PUBLIC_STORAGE_URL2')` with `Storage::disk('public')->url(...)`
   (null-guards preserved); delete both `.env` vars; prune any stale phpstan-baseline `env()` ignores;
   `composer qa` + `migrate:fresh --seed`.
4. **Docs** — set this doc's status to done; note SHAs; promote durable choice to `../decisions/LEDGER.md`;
   refresh `../HANDOFF.md`.

**Status:** planning complete — execution not started.
