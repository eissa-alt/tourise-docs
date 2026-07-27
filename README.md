# alt-static-basecode-docs

Single source of truth for the **ALT Static Basecode** platform docs. This `docs/` folder is its
own git repo, cloned in place inside the `alt-static-basecode-repos` wrapper (the three sub-app
repos sit beside it). Only `CLAUDE.md` lives at the wrapper root; everything else is here.

Layout follows the shared **ALT axis-foldered** convention (same as `cyan-docs` /
`saudi-forum-11-docs`): foldered by axis, not by app or date. Folders are lowercase; doc files are
`SCREAMING_SNAKE_CASE.md`; a `_` prefix sorts templates to the top.

## Map

| Path | What's there |
|---|---|
| [HANDOFF.md](HANDOFF.md) | Rolling session pointer — read first for "what's the current state." Overwritten each session. |
| [ai/](ai/) | AI + dev onboarding package — read-order index in [ai/README.md](ai/README.md). Start here on a new session. |
| [tasks/](tasks/) | The work-log axis — one folder per task. [tasks/README.md](tasks/README.md) explains how to open one. |
| [decisions/](decisions/LEDGER.md) | Append-only ledger of durable, cross-task locked decisions (`D1…Dn`). |
| [upgrades/](upgrades/README.md) | Upgrade records + portable migration playbooks/runbooks (the Parts 1–5 initiative). |
| [process/](process/WORKING_MECHANISM.md) | How we work — branching, commit format, task flow, quality gate, Definition of Done. Also [SETUP_AND_UPDATE.md](process/SETUP_AND_UPDATE.md) (local run), [QUEUE_SETUP_PROD.md](process/QUEUE_SETUP_PROD.md) (prod queue worker + scheduler, md + pdf) + [CLONE_CHECKLIST.md](process/CLONE_CHECKLIST.md) (spin up a new project from this baseline). |
| [mobile/](mobile/) | The mobile API contract (PDF + HTML twin). **Read before touching `routes/api.php`.** |

## Start here

- **New session / new contributor →** [ai/README.md](ai/README.md) (5-min read-order), then this map.
- **First session in the repo →** paste [ai/KICKOFF_PROMPT.md](ai/KICKOFF_PROMPT.md) as the agent's first message.
- **Setting up / running locally (or after a `git pull`) →** [process/SETUP_AND_UPDATE.md](process/SETUP_AND_UPDATE.md).
- **Picking up / starting work →** [process/WORKING_MECHANISM.md](process/WORKING_MECHANISM.md) + open a [task](tasks/README.md).
- **Deploying to a production box (queue worker + scheduler) →** [process/QUEUE_SETUP_PROD.md](process/QUEUE_SETUP_PROD.md) — hand the PDF twin to DevOps.
- **Cloning this baseline into a new project →** [process/CLONE_CHECKLIST.md](process/CLONE_CHECKLIST.md).

## Conventions

- **Naming:** lowercase folders, `SCREAMING_SNAKE_CASE.md` files, `_TEMPLATE` / `_`-prefix sorts to top.
- **Long docs** split with a `_PART2` suffix rather than one giant file.
- **Cross-links** are relative and stay valid by uniform folder depth — keep new docs at the same level.
- **Decisions** are durable + global (`decisions/LEDGER.md`); task-local notes stay in the task.
- **Commits:** docs on `main`; code on `dev` (`P<phase>.<task> — …`); cross-cite SHAs when they pair.
