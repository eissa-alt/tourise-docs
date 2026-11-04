# Task 066: Social channels minimum per form

- **Status:** `in-progress`: at least 1 / 2 on `testing`, `main` and production 2026-11-04; the follow-up (Speaker
  / Moderator take **exactly** one) pushed on `fix/social-channels-speaker-one` (backend `433a39c`, frontend
  `4711a04`), PRs into `testing` next.
- **Opened:** 2026-11-04
- **Owner:** Eissa
- **Sub-app(s):** backend + admin + frontend
- **Branch(es):** `fix/social-channels-minimum` in `tourise-backend`, `tourise-admin` and `tourise-frontend` (from `testing`)

## Goal

Imtinan's `feat/registration-copy-and-one-channel` (2026-11-03, on `main` and production the same night) lowered
the social channels minimum from 2 to 1 for every category whose Mandatory fields ask for them. The team, the
next morning: "Only speakers and moderators must add at least 1, the rest of the categories remains 2."

## How it works

- **Speaker and Moderator forms** (form shapes `default-speaker`, `default-moderator`): **exactly 1** channel
  (follow-up, the team, 2026-11-04: "force only one, not at least"), "Choose one social media channel" (Imtinan's
  text). On the website, picking a second channel replaces the first; the server refuses two, even where the
  category does not ask for them. The admin's speaker form stays at least 1 with no maximum, so speakers who
  registered with two channels before stay editable.
- **Every other form:** at least **2**, "Choose at least 2 social media channels" (new texts, EN + AR).
- Only where the category's Mandatory fields ask for social channels, as before.
- By form shape, not the category's name or link: the slug follows the name when a category is renamed.
- **Backend:** `SocialChannels::MINIMUM = 2`, `ONE_CHANNEL_FORMS`, `minimumFor($formShape)`; `rules()` takes the
  form shape (the public `POST /guests`). **Website and admin:** `MINIMUM_CHANNELS = 2`,
  `SPEAKER_MINIMUM_CHANNELS = 1`; the social channels field takes a `minimum`, which the speaker form (and the
  moderator form built on it) passes. Imtinan's "Enter your username" under each channel stays. Follow-up:
  `maximumFor($formShape)` (1 on those two forms) adds `max:1`; the website field takes a `maximum`
  (`SPEAKER_MAXIMUM_CHANNELS = 1`).

## Log

- 2026-11-04: the team's note; checked (not applied: 1 for everyone on production), built. Backend: Pint,
  PHPStan, the full suite **1,732 passed, none failing**: `SocialChannelsTest` now tests 2 for other forms and 1
  for speaker and moderator, and its fake reCAPTCHA answer carries a score, which ends the 10 to 11 long-standing
  403 failures (test-only). Admin and frontend: type-check, ESLint, Prettier green. EN + AR: 2 texts per app.

- 2026-11-04: committed and pushed (backend `17970ff`, admin `4c7a67f`, frontend `3ac8efc`); merged into
  `testing` (backend PR #140, admin PR #138, frontend PR #52), after Imtinan's `fix/photo-errors-clear` (backend
  PR #139, frontend PR #51: a refused photo or document on submit says which and why). Rechecked together on
  testing: backend full suite 1,740 passed, none failing; admin and frontend type-check green. `testing` into `main`
  (backend PR #141, admin PR #139, frontend PR #53); main equals testing. Deployed to production: backend
  `fb09c0d..6a35e1e` + `queue:restart`, admin `df92c8b..a01f7aa`, frontend `d2c8358..bbe5fd1`, built and
  restarted; her photo and document errors went live with it.

- 2026-11-04, follow-up: the team, "for speakers and moderators form, it should force only one for social media
  and not at least". Built on `fix/social-channels-speaker-one` (backend + frontend, from `testing`): backend
  `SocialChannelsTest` 20 passed (exactly one on both forms, two refused even when not asked; the picker test
  sends one channel on the speaker form); Pint, PHPStan, full suite 1,742 passed, none failing; frontend type-check
  and ESLint green. Admin unchanged (see above).

## Open

- The owner's browser check on production.

## Definition of Done

- [x] Merged into `testing`
- [x] Merged into `main`
- [x] EN + AR translations in the same commit
- [x] Quality gate green (backend Pint, PHPStan, tests; admin and frontend type-check, ESLint)
- [ ] Browser check by the owner
- [ ] This TASK.md set to `done`; the index row updated
