# Handoff — current state

> Rolling pointer, overwritten each session. For the durable record see the per-task `TASK.md`,
> `decisions/LEDGER.md`, and `upgrades/UPGRADE_SUMMARY.md`. Full plan: `upgrades/CYAN_FEATURE_PARITY_MASTER_PLAN.md`.

**2026-07-06 — Tooling + hygiene pass across the two Next apps (ESLint 9 flat config, Prettier 3,
zero lint warnings, husky + lint-staged pre-commit hooks, GTM removed) + docs cleanup (dropped the
`-landing` app, documented the hook). Remotes are now set on every repo and all branches are pushed +
in sync. The admin email-invite / `password_mode` flow is merged into mainline — the old
`feat/admin-invite-flow` branch is gone (folded in), so it is NOT a dangling/unmerged branch.**

This supersedes the earlier "no upstream / not pushed" state: `origin` is set on all repos
(`github.com/eissa-alt/alt-static-basecode-*`) and each branch tracks + matches its upstream.

## Current SHAs (all pushed, in sync with `origin`)

- `alt-backend` (on **`main`**) @ `10e85c7` — recent app work: RSVP-decline handling + invitation-link
  updates and email-template / guest-ticket fixes. The admin email-invite / `password_mode` **backend**
  flow is in at `04001b3` (P2.ST8). *Note: backend has no `dev` branch — it works on `main`, unlike
  admin/frontend.*
- `alt-admin` (on `dev`) @ `29548e3` — ESLint 9 + Prettier 3 + husky/lint-staged + GTM removal + editor
  settings. Admin-invite **UI** at `d3ed5db` (P2.ST8) / `f43543f` (P2.ST19).
- `alt-frontend` (on `dev`) @ `f1da93e` — same tooling pass (through `41ae698`) + a form-shape
  `default-` prefix rename.
- `docs` (on `main`) @ `c00c677` — `<img>` vs `next/image` note; dropped `-landing` from current-state
  docs (+ ledger **D2**); documented the husky hook.

## What landed recently

- **ESLint 9 flat-config migration** (admin + frontend) + `@next/eslint-plugin-next` wired; **Prettier
  2 → 3**; all lint warnings driven to **0** — `prettier/prettier` autofixed, `no-unused-vars` via
  optional catch binding + config (`ignoreRestSiblings`, `argsIgnorePattern`), `exhaustive-deps` scoped
  disables, `<img>` scoped disables each with a `-- reason`.
- **husky + lint-staged pre-commit hook** (admin + frontend): staged `*.{js,jsx,ts,tsx}` → `eslint --fix`,
  other types → `prettier --write`, re-staged automatically. Installed on `yarn install` via
  `prepare: husky`. Verified end-to-end (real commit auto-formats). Non-blocking on `warn`-level rules.
- **GTM removed** from both apps (`react-gtm-module` + dead `utils/analytics.ts`).
- **Editor settings**: Tailwind `suggestCanonicalClasses` silenced; deprecated `typescript.tsdk` /
  `enablePromptUseWorkspaceTsdk` → `js/ts.tsdk.path` / `js/ts.tsdk.promptToUseWorkspaceVersion`.
- **Docs**: dropped the 4th `-landing` app from all current-state docs (now a **three sub-app** baseline:
  `-backend`, `-admin`, `-frontend` + `docs/`); documented the pre-commit hook in the quality gate; added
  ledger **D2**. Historical `upgrades/*` and D1's clone-source SHAs left intact (accurate record).
- **Admin email-invite / `password_mode` flow — merged + pushed** (backend `04001b3`, admin `d3ed5db` +
  `f43543f`): `AdminInvite` model + `admin_invites` / `password_mode` migrations, invite/resend/reset
  endpoints, SMTP-gated password-mode UI + reset-by-token page.

## Gates

- **Admin / Frontend:** `yarn type-check` + `yarn production` **green** on the tooling pass; ESLint **0 warnings**.
  The pre-commit hook now enforces Prettier/ESLint autofix on every commit.
- **Backend:** not re-run this pass (backend RSVP/email work landed separately). Run `pint --dirty --test`
  + `php artisan test` before the next backend push.

## Next / outstanding

- **SMTP smoke test** — send a real invite + reset-password email with live SMTP creds; confirm
  `DynamicSmtpService` applies the active DB config. (Pending since the Track 4 / invite work — needs env.)
- **Browser QA** — invite create path + reset-by-token page; plus the migrated listings + sidebar
  accordion (LTR/RTL) from the earlier P5.trim / cyan-parity session, which compiled green but were never
  browser-tested.
- **Backend branch convention** — decide whether the backend should adopt `dev` (it currently commits on
  `main`, diverging from admin/frontend).

> Pint note: the backend repo is not Pint-clean at baseline. Use `pint --dirty` (formats only changed
> files); a repo-wide `pint` run churns 300+ unrelated files.
