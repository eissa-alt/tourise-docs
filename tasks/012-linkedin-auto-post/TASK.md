# Task 012 — LinkedIn automatic posting for category social share

- **Status:** `done` (code) — manual browser + LinkedIn app QA pending
- **Opened:** 2026-07-20
- **Closed:** 2026-07-20
- **Owner:** —
- **Sub-app(s):** backend + admin + frontend
- **Branch(es):** `dev`

## Goal

ALT already ships the **manual** half of the per-category social-share feature (`with_share`,
`share_poster{,_ar}`, `share_type` = `manual|automatic`, `share_text_{en,ar}`, blade-generated social
card, admin form section, bulk-update modal). But the **`automatic` (LinkedIn auto-post)** path the admin
form already advertises is **not wired** anywhere. This task completes it: a registrant on the success page
can authorise a LinkedIn app (configured per category) and publish their social card automatically.

Ported best-of-both from `115-cyan-basecode` (P37.4, Pint/phpstan-clean controller + polished FE) and
`104-hci-2026` (origin, clean cred round-trip), adapted to ALT conventions (real boolean `with_share`,
RESTful/gated admin routes, `Storage::disk('public')`).

## Scope

- **In:** per-category `linkedin_client_id` / `linkedin_client_secret` (DB + model + admin form +
  resource round-trip); `LinkedInController` (auth-url / call-back / post) + 3 public routes;
  `getVisibility()` returning `share_type`; frontend automatic-share flow + `linkedin-redirect` OAuth
  landing page; success page passing `share_type` + `category_slug`. EN + AR strings.
- **Out (explicitly NOT this task):** CYAN's Social Card **Layout Designer** / JSON document-rendering
  engine (Tier B) — ALT keeps its existing blade social card. No change to `mobile/*`.

## Decisions

- **Tier A only** (LinkedIn auto-post), per user 2026-07-20. Blade social card kept; no document engine.
- **Best-of-both source**, adapted to ALT: CYAN's `LinkedInController` (already Pint/phpstan-clean), HCI's
  clean cred persistence on `update()`/resource, ALT's own boolean `with_share` + gated admin routes.
- **LinkedIn API surface kept on v2** (`/v2/ugcPosts`, `/v2/assets?action=registerUpload`, `/v2/userinfo`,
  `X-Restli-Protocol-Version: 2.0.0`) — this is the current documented surface for the consumer
  "Share on LinkedIn" product (`w_member_social`); the `/rest/*` Posts API needs a Marketing product. Do
  not "modernise" to `/rest/*`.
- **Per-category credentials** (each category holds its own LinkedIn app id/secret) — matches HCI/cyan.
- **Routes are public** (guest-facing OAuth, no admin/guest auth) — mirrors cyan; keyed by category slug.

## Log

- 2026-07-20 — opened. Three-way investigation (alt vs cyan vs hci) done: ALT has manual share + social
  card but no LinkedIn creds/controller/routes, `getVisibility` omits `share_type`, FE OAuth commented out,
  no `linkedin-redirect` page. Chose Tier A, best-of-both. Confirmed ALT stores the social card at the same
  `base_path('public/storage/uploads/social_card/...')` path the cyan/hci controller expects — no path
  adaptation needed.
- 2026-07-20 — **code complete (ledger D25).** Backend: new migration
  `2026_07_20_000001_add_linkedin_config_to_categories` (both creds nullable, after `share_type`) +
  `Category` fillable; `LinkedInController` (cyan's Pint/phpstan-clean version verbatim — same v2 Share
  product surface + same social-card path); 3 **public** routes (`GET /linkedin/auth-url`,
  `GET /linkedin/call-back`, `POST /linkedin/post`) in the public/localization group; `getVisibility()` now
  returns `share_type`; `update()` `$request->only()` + `CategoriesResources` round-trip the two creds.
  **phpstan fix:** the controller's frontend-URL read moved off `env()` (larastan
  `noEnvCallsOutsideOfConfig`) to a new `config('app.frontend_url')` key (mirrors `PUBLIC_FRONTEND_URL`).
  Admin: `categories-form` shows LinkedIn client-id/secret inputs when `share_type === 'automatic'`, and the
  two hardcoded English hints were replaced with `share_manual_hint` / `share_automatic_hint` keys;
  `interfaces/category.tsx` + EN/AR web.json updated. Frontend: new `pages/[lang]/linkedin-redirect.tsx`
  OAuth landing page; `success/sharebtn-sections.tsx` gained the automatic OAuth flow (login → token cookie →
  `linkedin/post`) alongside the existing manual buttons (kept ALT's lucide `Share2` + `getApiError` +
  `react-hot-toast`, no iconify/ThreeDotsWave); `success.tsx` → `success-sections.tsx` now thread
  `share_type` + `category_slug` through to the share component. **Gates:** backend `composer qa` green
  (pint + phpstan **No errors** + tests **465/3** — the 3 are the pre-existing `ExampleTest` `/`→403 + two
  avatar signed-URL fails, not from this work); admin + frontend `yarn type-check` green; changed files
  eslint-clean. `mobile/*` untouched.

## Definition of Done

- [x] Backend: migration (`linkedin_client_id`, `linkedin_client_secret` on `categories`) + model fillable
- [x] Backend: `LinkedInController` + 3 routes; `CategoriesController` persists creds on `update()`;
      `getVisibility()` returns `share_type`; `CategoriesResources` exposes creds. _(Left `bulkUpdateSocialMedia`
      untouched — LinkedIn creds are per-category app credentials, set individually in the form, not in bulk.)_
- [x] Admin: `categories-form` LinkedIn credential inputs (when `share_type === 'automatic'`) + interface +
      EN/AR translation keys (hints too)
- [x] Frontend: `linkedin-redirect` page + automatic share flow in `sharebtn-sections`; success page fetches
      and passes `share_type` + `category_slug`
- [x] EN + AR translations in the same commit
- [x] Backend `pint --test` + `phpstan analyse` + `php artisan test` green (465/3 pre-existing); admin/frontend
      `yarn type-check` green. _(Frontend `yarn production` needs `.env.production` — deferred to real-env QA.)_
- [x] Mobile contract unaffected (`routes/api.php` `mobile/*` untouched — new routes are public web only)
- [x] Docs updated (this TASK.md → `done`; index row; ledger D25)
- [ ] **QA (manual, needs a real LinkedIn "Share on LinkedIn" app + running stack):** set a category to
      `share_type=automatic`, fill client id/secret, register a guest, run the OAuth login → auto-post → verify
      the social card lands on the LinkedIn feed; confirm manual mode unchanged. `PUBLIC_FRONTEND_URL` must be
      set so the OAuth redirect URI resolves.
