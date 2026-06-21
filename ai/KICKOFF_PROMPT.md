# First-Session Kickoff Prompt — alt-static-basecode

Open this repo in Claude Code (or any AI coding agent), then send the prompt below as your very first message. No edits/refactors/commits in this session.

---

```text
We're starting fresh. I'm moving part of my workflow from Cursor to Claude Code.
Before any coding, warm up on this repo. No edits, no refactors, no commits, no
branch changes in this session.

Please run in Plan Mode (read-only).

Step 1 — Read, in this order:
  1. docs/ai/README.md
  2. docs/ai/PROJECT_OVERVIEW.md
  3. docs/ai/ARCHITECTURE_NOTES.md
  4. docs/ai/CODING_STYLE.md
  5. docs/ai/CURRENT_WORKFLOW.md
  6. docs/ai/AI_RULES.md
  7. alt-static-basecode-admin/FORM_RESTRUCTURE_GUIDE.md (dynamic-form folder layout)
  8. alt-static-basecode-backend/DARK_MODE_EMAIL_NOTES.md (email blade rules)
  9. EMAIL_EDITOR_UPDATES.md (repo root — email editor changes)
 10. admin_ui_ux_refactor_plan.md + advanced_admin_redesign_rollout_checklist.md (root)
 11. docs/mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.* (mobile API contract — critical)

Step 2 — Inspect the repo structure. Spot-check at least:
  - The four sub-app folders: pif-...-admin/, -frontend/, -backend/, -landing/
    (PIF is the only project with a 4th app)
  - alt-static-basecode-backend/composer.json (Laravel + PHP versions)
  - alt-static-basecode-admin/package.json (Next + React versions — still 12 / 17)
  - alt-static-basecode-backend/routes/api.php
  - alt-static-basecode-backend/app/Models/ (notable PIF-only: Conference,
    EventDay, Session, Workshop, MediaCenter, Publication, MeetingRoom,
    AppNotification, DeviceToken, ChatRoom, AccountDeletionRequest)
  - One end-to-end feature slice (pick e.g. sessions or workshops)
  - The dynamic-form folders under
    alt-static-basecode-admin/components/admin-modules/guests/froms/
  - alt-static-basecode-landing/ — note it's smaller (no apis/, no interfaces/)

Step 3 — Reply with a concise warm-up report, in this exact structure
(short bullets, no essays):

  1. Project type — 1–2 sentences (full conference platform, not just registration).
  2. Tech stack — versions and notable libs (Sentry in all three Next apps).
  3. Main modules / features — bullet list (incl. PIF-only: agenda tree, sessions,
     workshops, media center, publications, meeting rooms, push, in-app chat).
  4. Coding style + architecture patterns — bullets.
  5. Reusable components / helpers / services / hooks / base classes — name them.
  6. Shared/repeated patterns across the repo — bullets.
  7. Things to be careful about before future changes — bullets (mobile API
     contract via BACKEND_INCOMING_CHANGES_FOR_MOBILE, Sentry kept, Next 12/React 17
     on purpose, froms/ pattern still in use here, EN+AR commit rule, admin UI/UX
     redesign in progress).
  8. Drift check — anywhere docs/ai/*, EMAIL_EDITOR_UPDATES.md, admin_ui_ux_refactor_plan.md,
     or DARK_MODE_EMAIL_NOTES.md disagrees with the actual code. If none, say so.
  9. Open questions — up to 5, ranked by impact. Stop at 5.

Rules:
  - Do not edit, write, rename, delete, or move any file.
  - Do not stage, commit, branch, or push.
  - Do not run migrations, builds, or installs.
  - Do not touch the alt-static-basecode.pem deploy key (one level above the
    repos folder).
  - Do not touch any assets*/, badges/, documents/, fonts/, seo/, fav/,
    tech docs/, import_Test/ folders (client-supplied, not code).

Goal: by the end of this session I want you to know how I structure systems and
code, that this repo has an external mobile API consumer (so response shapes are
binding), and to flag anything in the existing docs that's wrong, missing, or
risky — so the next session can start implementing safely.
```
