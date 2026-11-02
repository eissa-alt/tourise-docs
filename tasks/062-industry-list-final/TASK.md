# Task 062: The final industry list

- **Status:** `done`: on `main` 2026-10-29 in the three apps and live since the 2026-10-29 release. The Arabic for
  the new names is a draft, **to check by the team**.
- **Opened:** 2026-10-29
- **Owner:** Eissa
- **Sub-app(s):** backend + admin + frontend
- **Branch(es):** `feat/industry-list-final` (backend PR #121, admin #118, frontend #40), then `testing` into
  `main` (backend #122, admin #119, frontend #41)

## Goal

Use the team's final industry and sub-industry file (Rawand, 2026-10-29, `final industry and sub industry
file.xlsx`, no Arabic) everywhere the industry is asked or shown: the five registration forms, the admin's guest
forms and dashboard, and the CRM. It replaces Task 054's decision 44 ("the system's 18 until the client signs off").

## What changed

- **Four renamed, keys kept** (no stored value moves): `attractions_entertainment` is "Culture, Sport &
  Entertainment", `emerging_future` "Technology", `government_public_sector` "Government",
  `tourism_technology_digital` "Travel Technology & Digital".
- **Three new industries**, before Other: Retail (6 sub-industries), Non-Profit & Philanthropy (6), Professional
  Services & Consulting (5).
- **International Organizations** under 13 more industries (the existing key and name); **Research Institutes &
  Think Tanks** under Education.
- **Kept as before (owner's defaults):** "Others (please specify)" stays last in each list (the file puts it
  first); Other keeps no sub-list (the file adds one, but Other already asks the guest to specify); no migration and
  no aliases for the old names.
- 21 industries and 158 sub-industries, the same in `CrmFixedLists.php` (backend), the forms' and the admin's
  `data/tourism-industry-types-select.ts` and both `web.json` in EN and AR, checked by a script against the file.

## Log

- 2026-10-29: cross-checked against the system, built, merged into `testing` and `main`, live with the release.
  Only Media guests had registered and the CRM held no real data, so nothing needed moving.

## Open

- **The team:** check the Arabic drafts (4 renamed, 3 industries, 18 sub-industries).
- A CRM file that still writes an old name (for example "Attractions & Entertainment") is refused as not on the
  list: use a fresh sample. The v2 CRM test files use the four old names in six cells.
