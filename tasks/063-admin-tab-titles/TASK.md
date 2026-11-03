# Task 063: Admin tab titles

- **Status:** `in-progress`: on `testing` and `main` 2026-11-03 (admin PR #135, testing into main), production
  deploy next.
- **Opened:** 2026-11-02
- **Owner:** Eissa
- **Sub-app(s):** admin
- **Branch(es):** `feat/admin-tab-titles` in `tourise-admin` (from `testing`)

## Goal

Every admin tab read "Tourise | admin", so several open tabs could not be told apart. The owner asked for each tab
to name its section: "Tourise | Templates", "Tourise | Guests" and so on.

## How it works

- **One place, no page edits:** `components/sidebar/section-title.tsx`, rendered in `pages/_app.tsx` after the
  default title. It takes the name of the sidebar link the page sits under (`data/sidebar-links.tsx`), in the
  admin's language: "Tourise | Guests", "Tourise | لوحة التحكم".
- **Pages inside a section** take its name (`/guests/edit/…` reads "Tourise | Guests"); the longest matching link
  wins.
- **A name two links share** takes its menu's in front: "Emails · Templates" and "SMS · Templates", "Emails ·
  Config" and "SMS · Config".
- **Pages the sidebar does not list** are named in the same file (`otherEntries`): collection edit (Invitations), SMS
  config, print logs, Print Wrong QR by Email, Static Badge Generator, Export Custom List, the modules whose links
  are off (Landing Page · Speakers and the like, media center, sessions, workshops, publications, notifications,
  meeting rooms, event days, conference) and the two developer pages.
- **A missing page** reads "Tourise | Page not found". **Login, profile and the password pages** keep their own
  titles, already in the same form ("Tourise | Login").
- All 179 pages checked by a script against the same rules: 174 by section, 4 their own, 1 the 404.
- Two new texts (EN + AR): `test_apis`, `see_more_coverage`.

## Log

- 2026-11-02: asked, built, type-check and ESLint green, committed (admin `80508ff`).
- 2026-11-02: merged into `testing` (admin PR #126, `55722e0`). Next: `testing` into `main`, then the admin build.

- 2026-11-03: `testing` into `main` (admin PR #135, `ec23120`); main equals testing. Production deploy next.

## Open

- Arabic: the sidebar names Guests and Invitations both "الدعوات", so their tabs read the same. A translation fix,
  not done here.
- A new sidebar link titles itself; a new page outside the sidebar needs a line in `otherEntries`.

## Definition of Done

- [x] Merged into `testing`
- [x] Merged into `main`
- [x] EN + AR translations in the same commit
- [x] Type-check and ESLint green
- [ ] This TASK.md set to `done`; the index row updated
