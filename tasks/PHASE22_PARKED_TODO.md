# Phase 22 — parked follow-ups from the client-name sweep

**Parked:** 2026-07-22 (owner chose to park these and move on).
**Source:** the P22 de-branding sweep — removing every past-client name (PIF, HCI, EDGEx, TOURISE,
DeveGO, FAF, DGCA, ICAO) from the three code repos. Everything P22 actually *did* is shipped and
pushed; this file is what it **surfaced but did not fix**.

Shipped in P22, for context:

| Commit | Repo | What |
| ------ | ---- | ---- |
| `3822549` `2c1cb75` `ed5d187` | frontend / admin / docs | P22.1 — `forms/pif/` → `forms/default/`, `pif-one-step` dropped |
| `57f6d19` | backend | P22.2 — PIF branding out of the ICS calendar export |
| `8a937d4` `52f6ebf` `cdaf902` | backend / frontend / admin | P22.3 — live leakage: dead HCI email + badge views, `X-Mailer: DeveGo`, TOURISE site name |
| `4b27162` `aa78591` | admin / frontend | P22.4 — dead weight: orphan keys, `bizzabo_*`, commented HCI footer, `QrCodeEDGEX` |
| `343e6e8` `efabc6d` | backend / admin | P22.5 — invitation-PDF feature parked |
| `9d4d5f3` | backend | P22.6 — badge QR rendered locally, no more `api.qrserver.com` |

---

## 1. Email QR still calls `api.qrserver.com` — needs a design decision

`app/Services/EmailVariableResolver.php:42` builds the `{{qr_code}}` email variable as
`<img src="https://api.qrserver.com/v1/create-qr-code/?…&data={registration_number}">`.

That image is fetched **by the guest's mail client**, not by us. So on every open, qrserver.com
receives the guest's registration number, their IP address, and an open signal. Four live callers:
`SendGuestEmailNotification`, `SendInvitationEmailNotification`, `SendAutomationEmailNotification`,
and the template preview in `EmailsTemplatesController`.

**Do NOT "fix" this the way P22.6 fixed the PDFs.** Gmail and Outlook strip `data:` images, so
embedding the PNG would make the QR vanish for most recipients. A comment at the call site records
this. Two real options:

- **CID attachment** — proper inline image, works nearly everywhere. But `EmailVariableResolver`
  builds an HTML *string* and has no access to the message object, so each of the four notification
  classes has to attach it. Bigger change.
- **Serve the PNG from our own domain** — e.g. `GET /qr/{registration_number}.png` rendering via
  `App\Services\QrCodeGenerator`. One-line change in the resolver, identical remote-image behaviour,
  moves the tracking to our server. Simpler, but it is a public endpoint mapping a registration
  number to an image — needs a think about enumeration.

`QrCodeGenerator` (added in `9d4d5f3`) already does the local rendering either option needs.

## 2. Docs debt — two findings still unrecorded in the ledger

> **Corrected 2026-07-27.** The original heading here said "the ledger stops at D34". That is no longer
> true — `decisions/LEDGER.md` now runs to **D42** (D35–D42 landed 07-24 → 07-25, covering P23 audit
> hardening, WhatsApp, the automation channel/picker/scheduling work, and seating). The **two specific
> findings below are still genuinely absent** (re-checked: `forgetMailers` and the `GuestsResources`
> date-only fix return no ledger hits), so this item stays open — but only for these two, not for the
> whole post-P21.7 range.

The two things a future session would not rediscover by reading code:

- **System-wide date shift** — every date-only API field was arriving a day early. `JsonResource`
  serialised Carbon as ISO-with-timezone, and `Asia/Riyadh` (UTC+3) pushed the day back. Fixed by
  `->format('Y-m-d')` on seven fields in `GuestsResources`.
- **SMTP mailer memoisation** — Laravel's `MailManager` caches the resolved mailer, so a per-flow
  SMTP override applied only to the *first* send in a process. Fixed with `Mail::forgetMailers()` in
  `DynamicSmtpService`; `tests/Feature/DynamicSmtpOverrideTest.php` fails if that flush is removed.

Also unrecorded: the P21 bulk-actions menu, the category template picker, `yarn check:rbac`, and all
of P22.1–P22.6.

## 3. Cleanup backlog — translations

Measured 2026-07-22 by matching every key in `translations/en/web.json` against the concatenated
`.ts`/`.tsx` source (dynamic `` `web:${…}` `` sites were checked separately — they resolve only to
conference field labels, listing module names and step ids, so they cannot reach these):

- **622 unused keys** — 277 frontend, 345 admin. The frontend set is mostly *client event content*
  rather than names: venue lines (`about_city` = "Riyadh - King Abdulaziz Convention Center"),
  specific dates (`about_dates_range`, `may_3_5_2026`), `beyond_readiness` = "#TheHumanCode", and at
  least one person's name (`fares_al_hamlan`). P22.4 removed only the 15 that carried a client
  *name*; the rest is a bigger and separate call.
- **2 duplicate keys** in `frontend/translations/en/web.json` — `finance_investment` and
  `entertainment`. Harmless while untouched, but **any JSON parse/dump round-trip silently collapses
  them to the last value**. P22.4 deliberately removed keys line-by-line to avoid this.
- **103-key EN/AR gap** in the frontend, almost all `privacy_policy_*`. Pre-existing, predates P22.
  Admin parity is exact (1654 / 1654).
- **Privacy-policy copy is hardcoded JSX**, not translation keys —
  `components/join/forms/default/fours-steps/step-1.tsx` carries the whole policy inline in English.
  P22.3 de-branded the text in place rather than converting it, which is why it is still there.

## 4. Branded assets that need real replacement files

De-branding these needs artwork, not edits — blanking the URLs breaks the render:

| File | Bucket |
| ---- | ------ |
| `resources/views/pdf/guest-ticket.blade.php:21` | `tourise.…` |
| `resources/views/pdf/base-wrong-qr.blade.php:56` | `devego.…` |
| `app/Http/Controllers/GuestsController.php:2961` (static badge bg) | `devego.…` |
| `resources/views/pdf/social_card.blade.php:62,64` + `social_card_ar` same lines | `hci-2026.…` |
| `resources/views/pdf/visa-document.blade.php:227,457` | `glmc.…`, `temp-001.…` |
| `frontend/public/images/eg-logo.png` — live header logo, `components/layout/header.tsx:28` | EDGEx artwork |

Also `resources/views/pdf/temp/invitation.blade.php` — FAF artwork, kept on purpose (see item 5).

## 5. The `pdf.invitation` feature is parked, not fixed

P22.5 (`343e6e8`) removed every path that could reach it. Background: four call sites loaded the view
`pdf.invitation`, which **has never existed in this repo's history**. Two blockers remain for whoever
picks up the refactor:

1. The only invitation template is `resources/views/pdf/temp/invitation.blade.php` — another client's
   artwork whose QR box is pixel-tuned to that background (`padding-top: 812px`,
   `margin-left: 525px`). Kept in place deliberately as the starting point.
2. `dinner_invite` is **not a column** on `guests` — no migration defines it — and the `'yes'`
   comparison in `GuestsController::ExportInvitations` predates the task 001 boolean work.

The two `Export*` methods survive with `PARKED` docblocks; routes, the automation attachment branch,
and the admin toggle are gone. The DB column, cast, resource and validation are **untouched**, so
re-enabling needs no migration — only UI and a route.

## 6. Test coverage gaps

- **No automated test covers badge or PDF rendering.** `git grep` over `tests/` finds nothing for
  `pdf.base` or badge PDFs. P22.6 was verified by rendering the blade to HTML and asserting the
  inline PNG, plus a manual print by the owner — there is no regression guard.
- ~~**`yarn check:rbac` is not in the quality gate.**~~ **RESOLVED (D41, 2026-07-25).** It exists
  (`admin/scripts/check-rbac-map.mjs`) and catches `inferFeatureId` ↔ sidebar mismatches — the bug class
  that shipped six times (D33) plus once more on WhatsApp (D41). Now written into the documented gate in
  `ai/CURRENT_WORKFLOW.md` + `process/SETUP_AND_UPDATE.md`, beside `yarn type-check`.

## 7. Watch

- `SessionsTest > search finds matching sessions` flaked **once** during a `composer qa` run and has
  passed every run since. Not reproduced; noted so a second occurrence is recognised as a pattern
  rather than investigated from scratch.

---

## Owner's manual QA — still outstanding

Not parked, just not done. Two things have never been exercised in a browser:

- **Logistics screen** — shipped 404'ing in P19.4 (an `/admin` path double-prefix), fixed in P20.3,
  but never opened since.
- **E-visa send** — never run. It emails a real guest via a real template, and P21.16 added a bulk
  variant that fans out over the same endpoint.

Badge printing **was** manually confirmed on 2026-07-22 (P22.6).
