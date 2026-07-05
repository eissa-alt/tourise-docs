# Project Overview — alt-static-basecode

## What this is

**Reusable ALT clone baseline** — `alt-static-basecode` is a starter platform cloned from the
`pif-directors-gathering` upgrade-then-clone baseline. It carries the most feature-rich of the ALT
event-platform layouts (the full conference/gathering feature set) so a new project can start from a
current, hardened stack rather than an old fork.

It is a **full event/conference platform** (not just a registration site): agenda, sessions,
workshops, publications, media center, in-app chat, push notifications, and a mobile-facing backend
contract on top of the standard "guest registration + admin CMS" base. Trim what a given project
doesn't need rather than rebuild what it does.

## Inherited stack (current — verified in code)

| Layer | Version |
|---|---|
| Backend | **Laravel 12** (`^12.62`), PHP **8.2**, Sanctum |
| Next apps | **Next 15** (`^15.5`), **React 18.3.1**, **Tailwind v4** (`^4.3`), **Headless UI v2** |
| Observability | **Sentry removed** (OWASP hardening — do not re-add) |

This reflects the Parts 1–5 upgrade initiative on the directors baseline. The frozen lineage record
in `../upgrades/` (`UPGRADE_SUMMARY.md`, `BASELINE_DECISION.md`) documents exactly what was done.

## Top-level layout

```
alt-static-basecode-repos/
├── alt-static-basecode-backend/     Laravel 12 API (PHP 8.2, Sanctum) — serves admin, frontend, mobile
├── alt-static-basecode-admin/       Next.js 15 + React 18 CMS (TS, Tailwind v4, pages router)
├── alt-static-basecode-frontend/    Next.js 15 + React 18 public registration site
└── docs/                            project docs (own sibling git repo: ai/ upgrades/ tasks/ decisions/ process/ mobile/)
```

> The directors baseline carried a 4th `-landing/` marketing app; it was dropped from
> `alt-static-basecode` (not needed here) — see [`../decisions/LEDGER.md`](../decisions/LEDGER.md) (D2).

## Purpose of each sub-app

| Sub-app | Serves | Notes |
|---|---|---|
| `alt-static-basecode-backend` | REST API for admin, public site, **and mobile** | ~69 models — see `ARCHITECTURE_NOTES.md` |
| `alt-static-basecode-admin` | Admin CMS: guests, invitations, categories, emails, SMS, badges, exports, agenda, conferences, sessions, workshops, publications, media center, notifications, logs | pages router |
| `alt-static-basecode-frontend` | Public registration + complete-data site (EN/AR) | |

## Domain features that exist here

The standard event-platform features (guests, dynamic forms, categories, invitations, emails, SMS,
badges, exports, scans, gates, hotels, rooms, e-Visa, RG/Cvent integration, automations, history
logs) **plus** the conference-platform extras:

- **Conference / EventDay / Session / Workshop** — full agenda tree
- **Session feedback / Workshop feedback / Workshop registration**
- **MediaCenter / MediaImage / MediaVideo / SessionMedia**
- **Publication**
- **MeetingRoom + MeetingRoomSlot** — appointment booking
- **AppNotification + NotificationRecipient + DeviceToken** — push notifications
- **ChatRoom + ChatMessage** — in-app chat
- **AccountDeletionRequest** — app-store-required user data-removal flow
- **Mobile-facing API surface** — see `docs/mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf` before touching `routes/api.php`

## Project status

- **Freshly cloned (2026-06-21)** from the directors baseline. No work in flight — see `../HANDOFF.md`.
- Git re-initialized fresh per repo (no directors history): code repos on `dev` (off `main`), docs on `main`.
- **Remotes not yet set** and the carried-over `.env*` values still point at directors — re-point them
  before deploying (see `../HANDOFF.md` "next likely work").
- Bilingual EN + AR throughout — keep both locales' keys in the same commit.
