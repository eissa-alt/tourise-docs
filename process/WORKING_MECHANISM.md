# Working Mechanism — how we work in this repo

Read-first process doc for anyone (human or AI) doing real work in alt-static-basecode.

## Source-of-truth files

| For… | Look at… |
|---|---|
| What/why of the current effort | the relevant [../tasks/](../tasks/)`NNN-*/TASK.md` |
| Durable locked decisions | [../decisions/LEDGER.md](../decisions/LEDGER.md) |
| What the upgrade initiative did (+ SHAs) | [../upgrades/UPGRADE_SUMMARY.md](../upgrades/UPGRADE_SUMMARY.md) |
| Agent/dev onboarding | [../ai/README.md](../ai/README.md) (read-order inside) |
| Mobile API contract | [../mobile/](../mobile/) — read before touching `routes/api.php` |
| Setting up / running locally | [SETUP_AND_UPDATE.md](SETUP_AND_UPDATE.md) |
| Cloning this baseline into a new project | [CLONE_CHECKLIST.md](CLONE_CHECKLIST.md) |

## The four sub-apps

Separate git repos mounted side by side, **no monorepo tooling**: `alt-static-basecode-backend`
(Laravel 12), `-admin` (Next 15), `-frontend` (Next 15), `-landing` (Next 15). `docs/` (this repo)
is a fifth, doc-only sibling.

## Branching & commits

- Working branch is **`dev`** in every sub-app. **Never push to `main`.**
- Commit format: **`P<phase>.<task> — <short imperative>`**.
- `composer.lock` / `yarn.lock` are gitignored in this lineage → commits carry
  `package.json` / `composer.json` only.
- Docs (this repo) commit on **`main`**; when a docs change pairs with a code change, cross-cite
  the SHAs both ways.

## Task flow

1. Open a task folder — `cp -r tasks/_TEMPLATE tasks/NNN-slug` (see [../tasks/README.md](../tasks/README.md)).
2. Plan-mode first for anything non-trivial (schema/migrations, agenda/sessions/workshops,
   chat/push, mobile endpoints, refactors > ~3 files). Confirm the plan before editing.
3. Do the work on `dev`; keep `TASK.md`'s Status + Log current.
4. Run the quality gate (below) before any push.
5. Close the task: Status `done`, tick the DoD, update the `tasks/README.md` index row; promote any
   durable decision to `decisions/LEDGER.md`.

## Quality gate (before any push)

- **Backend:** `./vendor/bin/pint --test` + `php artisan test --filter <FeatureTest>`
- **Admin / Frontend / Landing:** `yarn type-check` + `yarn production`

## Definition of Done

Code merged to `dev` · EN+AR translations same commit · quality gate green · `TASK.md` closed +
index updated · mobile contract checked if `routes/api.php` changed · no `console.log`/`dd()`/`dump()`,
no widened `any`, no unrelated reformatting.

## Anti-patterns (don't)

Feature flags / dual code paths / "legacy fallback" · porting cyan's `DynamicFormRenderer` (PIF keeps
the older form-shapes pattern on purpose) · re-adding Sentry / react-quill / `tailwindcss@3` /
`tailwind-bootstrap-grid@5` / npm `xlsx` · framework major bumps without a dedicated task + branch.
