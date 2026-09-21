# Task 038 — The dashboard as the registration report, and guest filters the admin chooses

- **Status:** `done (code)` — pushed to `dev` 2026-09-21; dev `migrate` + browser QA on dev pending
- **Opened:** 2026-09-21
- **Owner:** —
- **Sub-app(s):** backend + admin
- **Branch(es):** `dev`

## Goal

The team leaves the event with a registration report. The client's two reference decks
(*TOURISE Registration Dashboard 23 Oct*, *OASIS Dashboard 16 SEP*) slice every figure by category
and seniority; our dashboard counted the whole event in every widget and could not be filtered at
all. And the guest list could not filter on half of what a guest record holds — companion and
delegation among them.

## Scope

- **In:** a filterable dashboard that reads the guest list's own filters; the reports' figures that
  fit our data; guest-list filters for everything the record holds, without burying the everyday
  ones; each admin's filter choices kept server-side.
- **Out:** targets / "vs plan" figures (owner: actual only for now); a reusable cross-project
  dashboard package (owner: TOURISE only for now); re-theming the admin.

## Decisions

- **One filter implementation.** `App\Support\GuestFilters` is the listing's filters, lifted out of
  `GuestsController::applyFilters`. The listing, its exports and the dashboard all call it, and the
  dashboard sends the listing's own query parameters — so the dashboard counts exactly the guests the
  listing would show for the same query string. The verify-station restriction is about *who is
  asking*, not *what they asked for*, so it stays in the controller. The admin's category/status
  scope still applies on top: a filter narrows, never widens. → ledger **D48**.
- **"Confirmed" is `will_attend = yes`** (owner: "based on our data and system"). **"No reply yet"
  is `will_attend` null or `''`** — both occur, so `will_attend=pending` matches both.
- **Actual figures only**, no targets (owner, 2026-09-21).
- **Clicking a chart or a key figure filters the dashboard in place** — a second click lifts it. An
  earlier cut sent the click to the guest list; the owner rejected it ("I want the dashboard to show
  more, not take me to the guest table").
- **Charts use the TOURISE palette, the admin keeps its own blue.** A first pass re-themed the whole
  admin to TOURISE purple; the owner stopped it ("only the charts in Tourise, don't change the
  admin"). → ledger **D48**.
- **Local vs international:** local = nationality SA, or no nationality with `is_saudi = true`;
  international = a nationality that is not SA; everything else is *unknown*. `is_saudi` is
  `NOT NULL DEFAULT false`, so a `false` proves nothing and is never counted as international.
- **Guest-list filters: essentials always on screen, the rest added.** Status, category, attendance,
  registration number, names, email, phone and registration date are fixed; every other filter is
  picked from **+ Add filter** and shows while it is added *or* holding a value. The choice is stored
  per admin, keyed by screen, in `admins.preferences` (the PEP P025.2 pattern); generic listings use
  the same store for *hidden* filters.
- **`/admin/me/preferences` has no `admin.can` gate** — it reads and writes only the signed-in admin's
  own bag, so there is nothing one admin could reach on another's. `auth.admin` keeps guest (mobile)
  tokens out. Capped at 64 KB.
- **Print is the report.** A named A4-landscape page; the sidebar, header and footer drop out; charts
  scale to the page; a widget moves to the next page whole.

## What the dashboard shows

Filter bar (category, seniority, status, region, industry, registration dates) + an **All /
Confirmed / Declined / No reply** switch, all in the URL. Key figures: registered (+ last 7 days),
confirmed, declined, no reply, new today vs yesterday; reconfirmed, printed, badge collected, checked
in, pending requests. Registrations over time for the whole period (click a day to filter to it),
status, categories (registered vs confirmed), audience profile (seniority, industry, region,
nationality, country, top companies, gender, local/international, attendance by day), invitations and
invitation requests — each with a chart/table toggle.

## Log

- 2026-09-21 — backend `28da7a1` — `GuestFilters`, dashboard filters, `/admin/dashboard/guests/summary`,
  companion/delegation + `will_attend=pending` filters. `DashboardFiltersTest`, `GuestListingFiltersTest`.
- 2026-09-21 — backend `f66aa10` — `admins.preferences` (migration `2026_09_21_000001`) +
  `GET/PUT /admin/me/preferences`. `AdminPreferencesTest`.
- 2026-09-21 — admin `45924c2` — the filterable dashboard, chart-kit, print report; guest filters
  with **+ Add filter**; per-admin hidden filters on the generic listings. EN + AR in the same commit.
- 2026-09-21 — gates: backend `pint --test` + tests green on each commit on its own (812 → 818);
  admin `tsc`, eslint, `check:rbac`, prettier green on its commit on its own. **Pushed to `dev`.**

## Open

- **Dev `php artisan migrate`** — `admins.preferences` does not exist until it runs; the preferences
  endpoints 500 without it.
- **Browser QA on dev.** Verified locally (SQLite, Playwright), not on dev data.
- Offered, not built: show Invitation Requests as one split bar while only one request form exists.

## Definition of Done

- [x] Code merged to `dev` in the relevant sub-app(s)
- [x] EN + AR translations in the same commit
- [x] Quality gate green (backend `pint --test` + `php artisan test`; admin type-check, lint, `check:rbac`)
- [x] Docs updated (this TASK.md; index row; ledger D48)
- [x] Mobile contract checked — new routes are `/admin/*` only; the guest-facing API is unchanged
