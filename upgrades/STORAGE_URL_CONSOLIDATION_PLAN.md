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
| `NEXT_PUBLIC_STORAGE_URL` (`…/uploads`) | `next.config.js` CSP (only `.origin`); `custom-file-input{,-3}.tsx` (`/${inputName}/`); guest see-more modals (`/personal_image/`, `/document_copy/`, `/visa_copy/`, `/issued_visa/`, `/social_card/`) **as fallback behind task-006 signed `*_url`** |
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

## 4. Stretch (optional, decide at execution)

Admin previews could drop the storage var **entirely (0 vars)**: the upload endpoints already return a full
`url` (post-`ff97c7b`), and API resources already return full `*_url` fields — so the file-input components
could consume those directly instead of rebuilding `{base}/{module}/{field}/{file}`. Bigger component
refactor; primary plan keeps 1 admin var for a smaller, safer diff.

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
