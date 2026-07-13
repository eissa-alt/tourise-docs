# Storage Upload-URL Fix Playbook (portable)

> **Reusable across the ALT project family** (Laravel backend + Next.js admin). Recipe to fix the **admin image-upload preview 404** — where the base64 `upload()` endpoints return a URL that doesn't point at the file they just wrote.
>
> Executed on **alt-static-basecode** (2026-07-13, backend `ff97c7b`). This doc is the *diagnosis + the copy-paste fix* so the same change can be replayed onto any clone (cyan-basecode, saudi-forum, etc.) that carries these controllers.
>
> **Scope:** one self-contained bug fix across the base64 `upload()` endpoints. Two independent defects, two independent fixes — one is a code bug, the other is an `.env`/config misconfiguration. Honors the **no-new-`env()`-in-controllers** rule (Larastan ratchet, ledger D10).

---

## 0. The symptom

In the admin CMS, when you pick an image in a file input (e.g. a category logo, speaker photo, email-config background), the **preview before saving is broken (404)**. The record can still save, and the image often displays fine *after* a reload — because the *listing/detail* path builds URLs from a different source (API resources) than the *upload response* does.

The broken URL looks like one of:

```
/storage/categories/logo.png                       ← relative (no host)
http://127.0.0.1:8000/storage/categories/logo.png  ← wrong (missing folder segment)
```

The file actually lives at:

```
http://127.0.0.1:8000/storage/categories/logo_en/logo.png
```

---

## 1. Root cause — two independent defects

The base64 `upload()` action in each affected controller does roughly this:

```php
$folderName = $request->inputName;   // e.g. "logo_en"
$moduleName = $request->moduleName;  // e.g. "categories"
$imageName  = Str::lower(Str::random(16)).'.'.$extension;

// writes to  moduleName/folderName/imageName
Storage::disk('public')->put($moduleName.'/'.$folderName.'/'.$imageName, base64_decode($image));

// BUG: returns  moduleName/imageName  (folderName dropped)
$url = Storage::disk('public')->url($moduleName.'/'.$imageName);
```

### Defect #1 — path mismatch (code bug)
The `put()` writes to `moduleName/folderName/imageName`, but the returned `$url` is built from `moduleName/imageName` — the `$folderName` segment is dropped. So the URL points at a path that doesn't exist → 404. **This is the real code bug** and must be fixed in every affected controller.

### Defect #2 — relative host (env/config)
`Storage::disk('public')->url(...)` resolves via `config/filesystems.php`:

```php
'public' => [
    'driver' => 'local',
    'root'   => storage_path('app/public'),
    'url'    => env('APP_URL').'/storage',   // Laravel default
    ...
],
```

If **`APP_URL` is empty** (a common local-`.env` oversight), the result is a **relative** `/storage/...` URL that 404s against the *admin* origin (e.g. `localhost:3000`) instead of the backend. In production `APP_URL` is usually set, so **defect #2 is typically local-only** — but an empty `APP_URL` is a latent bug that also breaks signed URLs, password-reset / queued-mail links, etc., so fix it everywhere.

---

## 2. The fix

### 2a. Code — mirror the `put()` path in the returned URL

In every affected controller, make the `url()` argument **identical** to the `put()` argument:

```diff
- $url = Storage::disk('public')->url($moduleName.'/'.$imageName);
+ $url = Storage::disk('public')->url($moduleName.'/'.$folderName.'/'.$imageName);
```

> ⚠️ **Do NOT "fix" this with `env('PUBLIC_STORAGE_URL2').'/'.$moduleName.'/'...`** in the controller. It works, but it adds a new `env()` call outside `config/`, which the Larastan rule `larastan.noEnvCallsOutsideOfConfig` rejects (breaks the D10 baseline → red gate). Keep the idiomatic `Storage::disk('public')->url(...)`; the host comes from config (§2b).

### 2b. Env/config — give the disk an absolute host

Leave `config/filesystems.php` at the Laravel default (`'url' => env('APP_URL').'/storage'`) and **set `APP_URL` in every environment's `.env`**:

```dotenv
APP_URL=http://127.0.0.1:8000     # local; use the real backend origin in staging/prod
```

Then clear the cached config so it takes effect:

```bash
php artisan config:clear
```

> `.env` files are gitignored — this change is **not** in the commit. You must apply it by hand in **local, staging, and prod**. That's the easiest step to forget; see the pitfalls table.

**Why not couple the disk `url` to `PUBLIC_STORAGE_URL2`?** Some clones have a `PUBLIC_STORAGE_URL2=…/storage` var that the API resources read directly. Pointing the disk at it (`env('PUBLIC_STORAGE_URL2', env('APP_URL').'/storage')`) works, but it couples the disk config to a var you may later consolidate/drop. `APP_URL` is the framework-native single source of truth — prefer it.

---

## 3. Find every affected controller first

The tell-tale is an `upload()` where the `url()` path differs from the `put()` path. Scan for all `public`-disk URL builders:

```bash
rg -n "Storage::disk\('public'\)->url\(" app/Http/Controllers
```

Then, for each hit, compare its `put()` and `url()` lines. On **alt-static-basecode** the mismatch (defect #1) existed in **6** controllers:

| Controller | fixed line |
|---|---|
| `EmailsConfigsController.php` | url now `moduleName/folderName/imageName` |
| `EmailsTemplatesController.php` | " |
| `CategoriesController.php` | " |
| `BadgesController.php` | " |
| `SponsorsController.php` | " |
| `SpeakersController.php` | " |

**Already-correct / auto-fixed by §2b (no code change needed):**
- `ZonesController.php` — its `url()` already included `$folderName`; only defect #2 applied, fixed by `APP_URL`.
- `GatesController.php` — a scan-badge upload with a fixed path (`scans/badge_images/…`); path was already correct, so `APP_URL` alone fixes it. ⚠️ **Different response shape (`image_url`) and possibly mobile-facing — do not restructure it; it's fixed for free by the config.**

> 🔶 **CLONE DELTA.** Controller set and line numbers drift between clones. Always re-run the `rg` scan and diff each `put()`/`url()` pair in the target repo — don't assume the same 6.

---

## 4. Verify

Confirm the disk resolves to an absolute, folder-correct URL:

```bash
php artisan config:clear
php artisan tinker --execute="echo Storage::disk('public')->url('categories/logo_en/example.png');"
# → http://127.0.0.1:8000/storage/categories/logo_en/example.png
```

Then smoke one real upload in the admin (e.g. a category logo): the **preview before save** should render instead of 404.

---

## 5. Quality gate

The backend gate must be green before push:

```bash
composer qa      # = pint --test  +  phpstan analyse  +  php artisan test
```

- `pint --test` — formatting (the fix is a 1-line change per file; stays clean).
- `phpstan analyse` — **must show `No errors`.** If you see `larastan.noEnvCallsOutsideOfConfig … occurred N times`, you added an `env()` call in a controller — revert to the `Storage::url(...)` form (§2a).

---

## 6. Git / tracking

- Work on `dev`. Stage **only** the controllers whose `url()` path you corrected.
- Commit (conventional style, matches repo history):

  ```
  fix: include folder segment in admin upload response URL
  ```

- alt-static-basecode SHA for cross-cite: **backend `ff97c7b`** (6 files, 6 insertions / 6 deletions).
- The `APP_URL` `.env` edit and `config:clear` are **operational steps, not commits** — note them in the deploy/handoff so staging + prod get `APP_URL` set.
- **Don't push without instruction.**

---

## 7. Pitfalls checklist (TL;DR)

| Pitfall | Guard |
|---|---|
| fixed the code but preview still 404s locally | you forgot `APP_URL` in `.env` (defect #2) — set it, then `php artisan config:clear` |
| set `APP_URL` locally, prod still broken | `.env` is gitignored — apply `APP_URL` in **staging + prod** too |
| gate goes red with a Larastan `env` error | you used `env(...)` in the controller — use `Storage::disk('public')->url(...)` instead (§2a) |
| assumed the same 6 controllers | re-run the §3 `rg` scan + diff each `put()`/`url()` pair; the set drifts per clone |
| "fixed" GatesController and changed its response | leave it — fixed for free by `APP_URL`; its `image_url` shape may be mobile-facing |
| config change didn't take effect | `php artisan config:clear` (cached config ignores `.env` edits) |
| coupled disk `url` to `PUBLIC_STORAGE_URL2` | prefer `APP_URL` — the framework-native single source of truth |
