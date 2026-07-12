# Mobile notice — guest `avatar` is now a signed, expiring URL

**Date:** 2026-07-12
**Severity:** Breaking URL-behavior change (field name + type unchanged — `avatar` is still a URL string; its *lifetime* changed)
**Affects:** Any mobile screen that renders or caches a guest **`avatar`** (self profile, attendee search, QR scan result, speaker/attendee lists)
**Reference:** ledger **D14**, `docs/tasks/006-private-document-storage/TASK.md`, `docs/decisions/LEDGER.md`
**Status:** committed on backend `dev` (not yet merged/released) — coordinate the release with mobile.

---

## TL;DR for the mobile team

Registrant photos moved off the public CDN onto a **private** disk. The guest **`avatar`** field is
now a **short-lived, signed URL** instead of a permanent public one:

```
before:  "https://<cdn>/storage/uploads/personal_image/xxx.jpg"          ← permanent, public, cacheable forever
after:   "https://<api>/api/files/guest-doc/personal_image/xxx.jpg?expires=..&signature=.."   ← signed, expires in 24h
```

- **Same field, same type.** `avatar` is still a plain URL string in the same place in the payload.
  Nothing renamed or removed. You can still drop it straight into an `<Image src>`.
- **The URL EXPIRES after 24 hours.** After that it returns **403** and the image won't load.
- **Do NOT cache the `avatar` URL indefinitely** (e.g. persist it in local storage and reuse it days
  later). Cache the *image bytes* if you like, but treat the **URL** as short-lived.
- **To refresh:** re-fetch the resource that carries the avatar (the same endpoint you already call —
  profile, attendee search, QR scan). Each response mints a fresh 24h URL.

## What you must NOT do

- ❌ Build the URL yourself from a filename + a base URL. Old integrations that did
  `PUBLIC_STORAGE_URL + "/personal_image/" + name` **will break** — those files are no longer public.
  Use the `avatar` value verbatim.
- ❌ Store the signed `avatar` URL in a long-lived cache/DB and render it later. It will 403 after 24h.

## Why this changed

Passports/IDs/photos were served from **public, unauthenticated, CDN-cached** URLs — anyone with (or
guessing) a URL could fetch a registrant's photo. They now live on a private disk and are served only
via short-lived **signed** URLs (the signature *is* the authorization, so a plain `<img>` still works
without an auth header). Admin-facing document URLs use a 30-minute TTL; **mobile avatars use a wider
24-hour TTL** specifically so app caches keep working within a normal session — but they still expire,
which is the behavior change above.

## Privacy toggle unchanged

`display_photo_in_app` still governs whether *other* guests see a photo. When it's off, the avatar
other guests see is `null` (as before) — that logic did not change.

## Backend reference (for questions)

- Serving route: `GET /api/files/guest-doc/{type}/{file}` (`signed` middleware), `guest.doc.stream`.
- URL minted by `App\Http\Controllers\GuestDocumentController::signedUrl()`; mobile TTL constant
  `MOBILE_TTL_MINUTES = 1440` (24h).
- Mobile avatar source: `App\Models\Guest::avatarUrlForSelf()` / `avatarUrlForOthers()`.
