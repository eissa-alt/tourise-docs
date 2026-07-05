# Architecture Notes — alt-static-basecode

## Four-app split

```
…-frontend (public registration)  ─┐
…-landing  (marketing)           ──┼──▶ …-backend (Laravel 12 API) ◀── …-admin (CMS)
mobile     (external app)        ──┘            │
                                                ▼
                                          MySQL / MariaDB
                                          SMTP + SMS + push provider + queue
```

Auth: **Laravel Sanctum** tokens. Admin + Next apps store tokens in cookies; the mobile client uses bearer tokens.
(No Sentry — removed by the OWASP hardening; do not re-add `@sentry/nextjs` or `sentry/sentry-laravel`.)

## `alt-static-basecode-backend/` (Laravel 12, PHP 8.2)

Standard Laravel 12 layout:

```
app/
├── Http/
│   ├── Controllers/        thin
│   ├── Requests/
│   ├── Resources/
│   └── Middleware/
├── Models/                 ~69 models — see below
├── Services/               business logic
├── Mail/  Jobs/  Listeners/  Events/  Notifications/
├── Exports/                Excel/CSV exporters
├── Policies/ Rules/
└── Helpers.php
routes/api.php              all API routes (admin + public + mobile)
database/migrations/        one concern per file
database/seeders/
resources/views/emails/     blade email templates (see DARK_MODE_EMAIL_NOTES.md)
```

Model families (in addition to the standard guest/category/email/badge set):

- **Agenda tree** — `Conference`, `EventDay`, `Session`, `SessionFeedback`, `SessionMedia`, `Workshop`, `WorkshopFeedback`, `WorkshopRegistration`, `Agenda`
- **Content** — `MediaCenter`, `MediaImage`, `MediaVideo`, `Publication`
- **Meetings** — `MeetingRoom`, `MeetingRoomSlot`
- **Mobile / push** — `AppNotification`, `NotificationRecipient`, `DeviceToken`, `AccountDeletionRequest`
- **Chat** — `ChatRoom`, `ChatMessage`
- **Standard event ops** — `Guest`, `Category`, `Badge`, `BadgePrintLog`, `BulkPrint`, `Invitation`, `InvitationCollection`, `InvitationEmail`, `EmailTemplate`, `EmailConfig`, `EmailAttachment`, `SmsTemplate`, `Scan`, `Gate`, `Hotel`, `Room`, `Speaker`/`SpeakerLabel`, `Sponsor`/`SponsorLabel`, `Tier`, `Zone`, `Automation`, `AutomationSetup`, `HistoryLog`, RG/Cvent integration models, `EVisaExports`

> Before changing `routes/api.php` or any mobile-touching endpoint, check `docs/mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf` — those endpoints have an external consumer.

## Three Next 15 apps (`-admin`, `-frontend`, `-landing`)

Next 15 + React 18.3.1 + Tailwind v4 + Headless UI v2, **pages router**. Same internal folder convention in all three:

```
pages/
  [lang]/           EN/AR locale prefix
  _app.tsx _document.tsx _error.tsx
apis/               axios callers (admin/frontend; landing rarely)
auth/               guarded layouts / SSR helpers
components/
  admin-modules/    (admin only) one folder per domain
  shared/           primitives reused everywhere
  layout/ sidebar/  shell chrome
context/  hooks/  data/  utils/
i18n/  translations/   EN + AR JSON keys
interfaces/  icons/  svg/
public/
```

(No `sentry.*.config.ts` — removed.)

### Admin top-level domains (mirror of `alt-static-basecode-admin/pages/[lang]/`)

Standard: `admins`, `areas`, `automation`, `badges`, `bulk-print`, `categories`, `countries`, `cvent-integration`, `e-visa`, `emails`, `gates`, `guest-drafts`, `guest-statuses`, `guests`, `hotels`, `import`, `invitations`, `invitations-collection`, `landing-page`, `positions`, `print-logs`, `rg-integration`, `scans`, `sms`, `tiers`, `titles`, `traveling-status`, `logs`.

Conference-platform domains: `agenda`, `conference`, `event-days`, `events`, `meeting-rooms`, `media-center`, `notifications`, `publications`, `sessions`, `workshops`.

### Dynamic forms

Forms are organized by **project + flow** under `components/admin-modules/guests/froms/<project>/<flow>/`
and registered in `data/form-shapes-config.tsx`. Reference: `alt-static-basecode-admin/FORM_RESTRUCTURE_GUIDE.md`.
The same pattern lives mirrored under `components/join/forms/<project>/` in the public-facing
`-frontend/` and `-landing/` apps.

> **Keep the form-shapes pattern.** cyan-basecode deleted it in favor of `DynamicFormRenderer`; this
> baseline is **on the older pattern on purpose** (CLAUDE.md hard-rule #4). Do **not** port cyan's
> `DynamicFormRenderer` here without a dedicated, scoped task.

### Images: plain `<img>` vs `next/image`

Most images use `next/image` (`<Image />`) — **keep doing that** for static assets, remote CDN images,
and anything with a known/stable URL. That's where the optimizer, lazy-loading, and `srcset` pay off.

A handful of spots intentionally use a plain `<img>` and carry a scoped
`// eslint-disable-next-line @next/next/no-img-element` (with a `-- reason`). These are **dynamic,
client-only images** where `next/image` adds cost but no benefit:

- **User-upload previews** — the avatar/photo the user just picked, rendered from a `base64` data-URL
  or `blob:` object-URL (e.g. `personal_image_x`, `doc1_x`/`doc2_x` in `components/join/forms/**/step-*.tsx`).
- **Client-generated social/share cards** — the poster image built in the browser
  (`components/share/sharebtn-sections.tsx`, `components/success/sharebtn-sections.tsx`).

Why `<img>` here and not `<Image />`:

1. **No optimization possible.** The optimizer can't process `data:`/`blob:` sources, so you'd need
   `unoptimized` — i.e. `<Image />` with none of its upside, just extra props.
2. **Unknown dimensions.** These previews have no fixed width/height ahead of time; `<Image />` forces
   `width`/`height` (or `fill` + a sized parent) and would introduce layout/CLS risk for no gain.
3. **No remote-domain allowlist churn.** Avoids adding transient/user origins to `next.config` `images.remotePatterns`.
4. **History:** an earlier Next 12 **standalone/static-export** build here could not build with `next/image`
   in these spots; the code has used `<img>` for dynamic previews ever since. We're now on plain
   `next build` (SSR on Vercel), but the reasoning above still holds independently.

**Rule of thumb for agents:** static/remote/known-URL image → `next/image`. Dynamic `data:`/`blob:`/
runtime-generated preview → plain `<img>` + the scoped `eslint-disable-next-line` with a `-- reason`.
Do **not** "fix" the existing disabled `<img>` spots by converting them to `next/image`.

## `-landing/` (the 4th app)

Smaller than `-frontend/` — no `apis/`, no `interfaces/`. A mostly-static marketing site that still
ships EN/AR translations. Its `pages/`/`components/` shape mirrors the frontend's home + share +
speakers + registration-closed pages.

## Data flow for a new feature

```
migration → model → (Form Request) → Controller → (Service) → API Resource → routes/api.php
         → apis/modules/<feature>  (admin and/or frontend)
         → components/admin-modules/<feature>/  (admin)
         → pages/[lang]/<feature>/             (admin / frontend / landing)
         → translations/{en,ar}/<namespace>.json   (same commit)
         → docs/mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.* if it affects the mobile contract
```
