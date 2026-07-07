# Tasks

The work-log axis for this **task-based** repo (alt-static-basecode is a reusable clone baseline,
not sprint-cadenced — so we track discrete tasks, not sprints). One folder per task; each holds a
single `TASK.md`. The team follows progress here.

## Layout

```
tasks/
├── README.md            ← this index
├── _TEMPLATE/TASK.md    ← copy to start a new task
└── NNN-short-slug/      ← one folder per task
    └── TASK.md
```

## How to open a task

```bash
cp -r _TEMPLATE NNN-short-slug      # NNN = next zero-padded number
# fill in TASK.md: goal, scope, status, log, DoD
```

- **`NNN`** is a zero-padded running number (`001`, `002`, …). Don't reuse numbers.
- **`short-slug`** is kebab-case, a few words (`001-docs-reorg`, `002-email-editor`).
- Keep `TASK.md` current as you work — the **Status** line + **Log** are the source of truth
  for "where is this task." When done, set Status to `done` and fill the DoD checklist.
- Decisions that outlive the task → promote them to [../decisions/LEDGER.md](../decisions/LEDGER.md)
  (don't bury a durable decision inside a closed task).
- Code commits still follow the repo convention: `P<phase>.<task> — <short imperative>` on `dev`
  in the relevant sub-app repo. This folder is the **narrative log**, the git history is the diff.

## Index

| # | Task | Status |
|---|---|---|
| 001 | [boolean-db-cleanup](001-boolean-db-cleanup/TASK.md) | in-progress |
| 002 | [datetime-db-cleanup](002-datetime-db-cleanup/TASK.md) | done |
| 003 | [backend-tooling-chain](003-backend-tooling-chain/TASK.md) | done |

_Add a row per task as you open it; newest at the bottom._
