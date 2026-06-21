# Handoff — current state

> Rolling pointer, overwritten each session. For the durable record see the per-task `TASK.md`,
> `decisions/LEDGER.md`, and `upgrades/UPGRADE_SUMMARY.md`.

**2026-06-21 — new project, cloned from the `pif-directors-gathering` baseline. No work in flight.**

- Four sub-apps + docs copied from directors; identity renamed to `alt-static-basecode`.
- Inherited stack (frozen lineage in `upgrades/`): Next 15 / React 18.3.1 / Headless UI v2 / Tailwind v4 / Laravel 12.
- Git re-initialized fresh per repo (no directors history): code repos on `dev` (off `main`), docs on `main`. **Remotes not yet set.**
- See `decisions/LEDGER.md` D1 for the clone record and source SHAs.

**Next likely work:** set GitHub remotes, then re-point the carried-over `.env*` values to this project.
