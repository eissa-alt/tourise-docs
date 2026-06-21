# Baseline Decision & Upgrade Handoff

> Context handoff for Claude / future sessions.
> Date: 2026-06-05. Author: baseline assessment across the three ALT event-portal repos.
> **Decision: use `pif-directors-gathering-repos` as the primary baseline for the next project.**

---

## 1. TL;DR

- Three sibling ALT event-portal projects were compared: `saudi-forum-11-repo`, `pif-partners-forum-demo-repo`, `pif-directors-gathering-repos`.
- All share the same lineage (Laravel 11 + Next.js portal: guests, invitations, badges, gates/scans, email/SMS templating).
- **`pif-directors-gathering-repos` was chosen** because it has the full **mobile-app / engagement suite** (chat, push, sessions, workshops, meeting rooms, publications, media center, white-label) and the cleanest git history.
- **Trade-off accepted:** directors is still on the **legacy/vulnerable stack** (Next 12.3.4 / React 17 / Sentry). The Next upgrade + OWASP hardening **must be applied to directors before cloning the new project from it.**
- `saudi-forum-11-repo` already performed that exact upgrade + OWASP work, with **tagged, CVE-referenced commits** — use it as the literal playbook/recipe.

---

## 2. Why directors (not saudi)

| Factor | Verdict |
|---|---|
| Feature completeness | **Directors wins** — full mobile platform + agenda + all core modules |
| Git/code hygiene | **Directors** — consistent conventional commits (`feat(scope): ...`) |
| Security/framework stack | Saudi wins, **but** that work is replayable; rebuilding mobile on saudi is not |
| Decision driver | New project **requires the mobile suite** → directors is the cheaper path to parity |

Rebuilding directors' mobile suite on top of saudi would be a very large effort. Replaying saudi's upgrade chain onto directors is a known, bounded, recipe-driven effort. Hence directors + upgrade.

---

## 3. Repo snapshot (evidence)

### saudi-forum-11-repo — "the hardened core" (the UPGRADE PLAYBOOK)
- **Stack:** Next **15.5.18**, React **18.3.1**, framer-motion 11, swiper 12, TS 5.3 / Laravel 11, PHP 8.2, Sanctum 4.
- Backend security pins: `symfony/* ^7.4.12`, `league/commonmark ^2.8.2`, `phpoffice/phpspreadsheet ^1.30.4`, `setasign/fpdi ^2.6.7`.
- OWASP work complete (~21 CVEs), Sentry removed, formal SCA report + DEVELOPER_HANDOFF docs.
- Feature-light: **no Agenda, no Survey, no mobile suite.**

### pif-partners-forum-demo-repo — "survey on legacy stack"
- **Stack:** Next 12.3.4 / React 17 / Sentry 7 / `tailwindcss-dir` / plain `xlsx` (vulnerable, not upgraded).
- **Unique:** **Survey / post-event survey module** (`Survey`, `SurveyEmail`, `SurveyRecipient`; rating_comment type; recipients/bulk send; multi-sheet Excel stats export). Plus gates/scans + new email editor + Agenda.
- Noisy git history (many bare `fix` commits).

### pif-directors-gathering-repos — "full event platform + mobile" (CHOSEN BASELINE)
- **Stack:** Next 12.3.4 / React 17 / Sentry 7 (legacy, **needs upgrade**). Backend Laravel 11 **+ `laravel/reverb` (websockets), `kreait/laravel-firebase` (FCM push), `intervention/image`**.
- **Unique features (models + commits):** mobile passwordless OTP auth, **1-on-1 Chat** (Reverb + FCM), **Notifications** (push + in-app: `AppNotification`/`DeviceToken`/`NotificationRecipient`), **Sessions** (+feedback/media), **Event Days**, **Workshops** (capacity-aware + feedback), **Meeting Rooms** (auto slots, race-safe booking, category access), **Publications**, **Media Center**, **white-label/event-settings** (`Conference`), Apple-review account-deletion flow + demo bypass, Agenda, one-step RSVP, dietary requirements, photo consent, guest titles, table numbers.
- **Missing:** the **Survey** module (port from partners if needed) and saudi's security/framework upgrades.

---

## 4. Plan of record

1. Create a dedicated branch off directors `testing` (e.g. `next-upgrade` then `owasp-security-fixes`).
2. Apply the upgrade + OWASP work (Section 5) **on directors**, validate, merge to `testing`.
3. **Then** clone / branch the new project from upgraded directors.
4. Port Survey module from partners **after** the upgrade (on the new stack, never the old one), if the new project needs it.

> Do the upgrade on directors FIRST, then clone — not the other way around — so fixes stay in directors and aren't redone.

---

## 5. Upgrade checklist (replay saudi's tagged commits)

Each item maps to a tagged commit in `saudi-forum-11-repo` — read those for the exact diffs.

### Frontend + Admin
- [ ] Next 12.3.4 → 12.3.7 → 14 → **15.5.18** [9 Next CVEs incl. CVE-2025-29927, CVE-2024-51479]
- [ ] React 17 → **18.3.1**, framer-motion 6 → **11**, swiper 9 → **12** [CVE-2026-27212]
- [ ] Remove `@sentry/nextjs` [CVE-2026-27606]
- [ ] Remove root `tailwind` pkg + `tailwindcss-dir`; force `postcss@^8.5.14` [CVE-2026-41305, CVE-2021-23368/23382, CVE-2023-44270]
- [ ] Force `cookie@^0.7.2` [CVE-2024-47764], `lodash@^4.17.21` [CVE-2019-10744], `js-cookie@^3.0.7` [CVE-2026-46625] via resolutions
- [ ] Admin: `xlsx` → **SheetJS CDN tarball 0.20.3** [CVE-2023-30533, CVE-2024-22363]
- [ ] Admin: **remove `react-quill` + legacy email editor** [CVE-2021-3163] — directors admin still ships `react-quill ^2.0.0`
- [ ] Re-apply React 18 / Next patterns (DON'T "fix" these — intentional):
  - explicit `children?: React.ReactNode`
  - classnames ternaries (bigint compat)
  - `next/legacy/image` wrapper
  - `<Swiper modules={[...]}>` (never remove); no `SwiperCore.use([...])` in `_app.tsx`
  - `error?: any` on form-input wrappers (react-hook-form `FieldError | Merge<...>`)
  - no nested `<a>` inside `<Link>`

### Backend
- [ ] Remove `sentry/sentry-laravel`
- [ ] Pin `symfony/* ^7.4.12` + `setasign/fpdi ^2.6.7` [9 CVEs]
- [ ] Pin `league/commonmark ^2.8.2` [CVE-2026-33347, CVE-2026-30838]
- [ ] Pin `phpoffice/phpspreadsheet ^1.30.4` [CVE-2026-40902, CVE-2026-40863, CVE-2026-34084]

---

## 6. Directors-specific watch-outs (NOT covered by saudi)

Saudi never had these, so its playbook doesn't validate them — check explicitly:

1. **`laravel/reverb` (websockets) + `kreait/laravel-firebase` (FCM) + `intervention/image`** — confirm each is compatible with the pinned Symfony 7.4.12 and on a patched version before committing.
2. **Mobile app is a live API consumer** — backend upgrades must not break mobile API contracts (auth/OTP, chat, push, sessions). Smoke-test mobile endpoints, not just the web admin.
3. **Larger frontend surface** than saudi → more components to fix during React 17→18 (same patterns, more grind).
4. If the new project needs surveys, port the **Survey** module from partners onto the upgraded stack.

---

## 7. Guardrails (hard rules)

- **Never** re-introduce removed packages: `@sentry/nextjs`, `sentry/sentry-laravel`, `react-quill`, root `tailwind`, `tailwindcss-dir`, plain npm `xlsx`, `next-transpile-modules`.
- **EN + AR translations in the same commit.** No exceptions.
- **Do not unpin** `phpoffice/phpspreadsheet ^1.30.4`, `league/commonmark ^2.8.2`, or the React/Next majors.
- **Do not widen TS types to `any`** to silence build errors; fix the source.
- No `console.log` / `dd()` / `dump()` in committed code; no reformatting unrelated code in feature commits.
- **Quality gate before any push:**
  - Backend: `./vendor/bin/pint --test` + `php artisan test --filter <FeatureTest>`
  - Admin / Frontend: `yarn type-check` + `yarn production`
- Pair any contract/upgrade/config change with a commit in the docs repo (cross-linked SHAs).
- Work on `dev`/`testing` branches; **never push to `main`**. Never touch `.env*`.

---

## 8. Open items to verify

- Reverb / Firebase / intervention-image patched-version compatibility under Symfony 7.4.12.
- Whether the new project needs the Survey module (→ port from partners).
- saudi's `CLAUDE.md` still says "Next 14" though code is on **15.5.18** — use the package.json/commits as truth, not that doc string.
