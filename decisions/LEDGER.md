# Decision Ledger

Append-only record of **durable, cross-task locked decisions** for alt-static-basecode. Numbered
`D1…Dn`, never renumbered. A task-local choice lives in that task's `TASK.md`; a decision that
outlives the task gets promoted here. This is the source of truth when a decision and the code/docs disagree.

> Format: `D<n> — <date> — <one-line decision>` + a short why + where the detail lives.

---

## D1 — 2026-06-21 — cloned from pif-directors-gathering baseline

`alt-static-basecode` was cloned from the `pif-directors-gathering` upgrade-then-clone baseline
(source SHAs: backend `8745150` · admin `0f65026` · frontend `5e3fee2` · landing `55fd6b7` · docs `3cbca75`).
Inherited stack: **Next 15 / React 18.3.1 / Headless UI v2 / Tailwind v4 / Laravel 12** (Sentry removed,
OWASP-hardened). The frozen lineage record under `../upgrades/` documents what this baseline already includes.

- **What the baseline already includes:** [../upgrades/UPGRADE_SUMMARY.md](../upgrades/UPGRADE_SUMMARY.md)
- **Why directors was the chosen baseline:** [../upgrades/BASELINE_DECISION.md](../upgrades/BASELINE_DECISION.md)

## D2 — 2026-07-05 — dropped the `-landing` app

The directors baseline carried a 4th sub-app, `alt-static-basecode-landing` (Next 15 marketing site).
It is **not needed for this project** and has been dropped — `alt-static-basecode` is now a **three
sub-app** baseline (`-backend`, `-admin`, `-frontend`) plus `docs/`. Current-state docs were updated to
match; the frozen lineage under `../upgrades/` (and D1's clone-source SHAs) still mention `-landing` as
an accurate record of the baseline it came from.

## D3 — 2026-07-06 — unified admin forgot-password onto the invite reset-by-token flow

Admin "forgot password" now reuses the **same token machinery as the admin invite** instead of the
legacy `v2/password/forgot` guest endpoint. `AuthController::forgotPassword()` issues a one-per-email
`AdminInvite` token, emails the shared `emails.admin_invite.{en,ar}` blade (different subject only) via
a public `POST /admin/forgot-password`; the admin `forgot-password-form` posts `{ email, back_link }`
there, landing the admin on the same `reset-password/[token]` page as invites. This brings alt to
**cyan parity** on the reset flow, with **one deliberate deviation**: the endpoint is **enumeration-safe**
— it always returns success and only sends mail if the admin exists (cyan validates `exists:admins,email`,
which leaks account existence). The new route is **admin-only and additive**, so the mobile contract is
unaffected. Backend `a8184ca` / admin `70e646c` (both merged via PR #1). Detail: `HANDOFF.md`.

## D4 — 2026-07-06 — backend adopts the `dev` → PR → `main` workflow

The backend repo historically committed straight to `main` (it had no `dev` branch, diverging from
admin/frontend). It now uses **`dev`** as its working branch and merges to `main` via PR, matching the
other two app repos and CLAUDE.md's "work on `dev`, never push to `main`" rule. This resolves the
"backend branch convention" open item from the prior handoff. (`docs/` remains `main`-only — it is a
docs-only sibling repo with no app build/branch flow.)

## D5 — 2026-07-06 — lucide-react is the single icon library (dropped @iconify/react + @heroicons/react)

Both Next apps carried **two** icon libraries from the baseline (`@iconify/react` and
`@heroicons/react`). They are now unified on **`lucide-react`** and both old deps have been removed
from `package.json` + `yarn.lock`. The migration ran in two phases against a machine-verified
heroicon/iconify → lucide name map (P1: iconify removal incl. the `bi:tiktok` inline-SVG replacement;
P2: heroicons → lucide). All icon swaps are 1-for-1 (`className` sizing preserved), so this is a
zero-behaviour-change refactor — no icon is used by the mobile contract (admin/frontend only). Gates
green on both apps (`type-check` + `production`). Admin `de87b4b` (P2) / frontend `c74b82c` (P2),
stacked on the P1 lucide commits. Detail: `HANDOFF.md`.
