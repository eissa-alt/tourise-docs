# Task 006 — Private document storage + signed URLs (Saudi P1 backport)

- **Status:** `done` — code shipped + pushed on `dev`; `dev`→`main` merge deferred (user will merge after a repo check, 2026-07-18). ⚠️ **Mobile contract change** (avatar → 24h signed URL) — still needs mobile-team ack before the `dev`→`main` merge.
- **Opened:** 2026-07-12
- **Owner:** AI agent
- **Sub-app(s):** backend (+ admin previews consume the new URLs; mobile avatar contract change)
- **Branch(es):** `dev`
- **Source:** Saudi Forum 11 security **Point 1** (`114-saudi-11/.../docs/security/port-review-jul-2026/POINT_1_PRIVATE_DOCUMENT_STORAGE_PLAN.md`). Plan slot: `upgrades/cleanup-hardening/CLEANUP_AND_HARDENING_MASTER_PLAN.md` **Task 005 (Track B)**, un-deferred by user 2026-07-12 (pre-launch; no clone carries prod data). Follows task 005 (P2 admin HttpOnly).

## Goal

Move sensitive registrant files (**`personal_image`**, **`document_copy`** on `guests`) off the public
disk — where they were served via **unauthenticated, CDN-cacheable URLs** (anyone with/guessing a URL
could fetch a passport/photo) — onto a **`private`** disk served only via **short-lived signed URLs**.

## Decisions (this task)

- **Both columns go private.** `personal_image` + `document_copy` are the sensitive files in alt.
- **Dual TTL:** admin previews **30 min** (`ADMIN_TTL_MINUTES`); **mobile avatars 24 h**
  (`MOBILE_TTL_MINUTES`) so app caches survive a session (user decision 2026-07-12). Both still expire.
- **Build now, hold the merge.** Implement on `dev` now (pre-launch), write the mobile notice, and hold
  `dev`→`main` until the mobile team confirms the avatar change (user decision).
- **Public assets stay public:** sponsor/speaker photos, badge templates, media-center images,
  publications, email attachments — NOT moved (~19 other `disk('public')` sites untouched).

## What landed (backend; 13 files changed + 2 new)

1. **Config** — `private` disk in `config/filesystems.php` (root `storage/app/private`, `visibility:
   private`, NOT symlinked → never web-served). `signed` middleware already registered (verified).
2. **Serving** — new `app/Http/Controllers/GuestDocumentController.php`: `signedUrl($type,$file,$ttl?)`
   + `stream()` (type allow-list `TYPES`, `basename()` traversal guard, `Cache-Control: private,
   no-store`). Route `GET /api/files/guest-doc/{type}/{file}` under `signed` middleware
   (`guest.doc.stream`), `{file}` constrained to `[A-Za-z0-9._-]+`.
3. **Writes → private** — `personal_image`/`document_copy` uploads + `exists()` checks in
   `GuestsController` (4 writes, 2 checks) **and the mobile self-service avatar upload/replace in
   `MobileAuthController`** (`storeBase64Image` put + old-file delete — caught during verification).
4. **Resources → signed URLs** — admin `GuestsResources` `personal_image_url`/`document_copy_url` (30m);
   mobile `Guest::avatarUrlForSelf()`/`avatarUrlForOthers()` (24h; feeds `GuestMobileResource`/
   `QrGuestResource`; `display_photo_in_app` privacy toggle preserved).
5. **Server-side read-backs (16 sites / 7 files)** — every `base_path('public/storage/uploads/…')` →
   `Storage::disk('private')->path(…)`: `GuestsController`, `BulkPrintController`, `PdfController`,
   `GuestsTicketResources`, `GenerateSocialCardListener`, `SendAutomationEmailNotification`,
   `SendGuestEmailNotification` (badges, PDFs, social cards, email photo attachments).
6. **Admin `<img>` previews** — no code change needed; they already consume the `*_url` fields, which
   now carry signed URLs (a plain `<img>` loads a signed URL fine).
7. **Migration command** — `app/Console/Commands/MigrateGuestDocsToPrivate.php` (`guests:migrate-docs-to-private`,
   idempotent, `--dry-run`). No-op on a fresh clone; kept for downstream clones with data. Prints a
   CDN-purge reminder after moving files.
8. **phpstan-baseline** — removed 2 now-stale `env()`-in-`Guest.php`/`GuestsResources.php` ignore
   entries (the env calls they covered were replaced by signed-URL calls).

## Gates + verification

- `pint --test` **green**, `phpstan analyse` **No errors** (baseline shrank by 2), `php artisan test`
  **452 passed / 3 failed** — the 3 are the **documented pre-existing** failures (`ExampleTest` GET /→403
  + 2 avatar tests); **confirmed by stashing P1 and re-running on the clean parent** — those 2 avatar
  tests fail there too, so P1 caused no regression. `migrate:fresh --seed` **clean**.
- **Runtime (private-storage behavior), verified live:**
  1. file writes to `private`, is **NOT** on `public` (core guarantee) ✅
  2. private root is `storage/app/private/` (no symlink) ✅
  3. valid signed URL streams the file → **HTTP 200**, `Cache-Control: no-store, private`,
     `Content-Type: image/jpeg` ✅
  4. tampered signature → **403**; no signature → **403** ✅
  5. path-traversal (`..%2f..%2f.env`) → **404** (signature + `basename` guard) ✅
  6. the file is **not** reachable at a plain `/storage/uploads/personal_image/…` URL → **404** ✅
  7. unknown type → `signedUrl` returns null (allow-list) ✅
  8. mobile TTL = 1440 min (24h) ✅

## Mobile contract

**CHANGED** — guest `avatar` is now a signed, 24h-expiring URL (was a permanent public URL). Same field,
same string type; mobile must re-fetch after expiry and must NOT build the URL itself. Flagged in
**`docs/mobile/MOBILE_NOTICE_PRIVATE_AVATAR_SIGNED_URL.md`**. `routes/api.php` change = one additive
signed route (no existing endpoint renamed/removed). **Hold `dev`→`main` until mobile confirms.**

## Definition of Done

- [x] private disk + serving controller + signed route
- [x] writes (incl. mobile upload) + resources + 16 read-backs repointed to private
- [x] migration command; phpstan baseline cleaned
- [x] `composer qa` green (452/3 pre-existing) + `migrate:fresh --seed` + runtime private-storage checks
- [x] Docs: this TASK.md, ledger **D14**, HANDOFF, mobile notice
- [ ] Mobile team acks the avatar change; real-env browser QA (admin preview render, heavy export/PDF/
      email photo) — before `dev`→`main`
