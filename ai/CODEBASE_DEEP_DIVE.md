# Codebase Deep Dive — alt-static-basecode

> **Stub — pending regeneration.** The previous deep dive was a dated (2026-05-24), pre-upgrade
> snapshot of the directors baseline (it described Laravel 11 / Next 12 and recorded directors-specific
> drift). It was **removed during the clone** rather than carried over stale, because a wrong-version
> deep dive misinforms more than no deep dive.

For the current, verified picture use:

- **`PROJECT_OVERVIEW.md`** — what this is + the inherited stack (Laravel 12 / Next 15 / React 18.3.1 / Tailwind v4 / Headless UI v2, Sentry removed).
- **`ARCHITECTURE_NOTES.md`** — the four-app split, backend model families, Next app folder convention, dynamic-forms pattern, data flow.
- **`../mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf`** — the binding mobile contract.

## Regenerate when needed

When a deep, code-level investigation is actually required, regenerate this file from a fresh
read-only pass across the four sub-apps + the mobile contract, and date it. Until then, treat
`PROJECT_OVERVIEW.md` + `ARCHITECTURE_NOTES.md` as the source of truth.
