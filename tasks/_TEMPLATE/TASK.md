# Task NNN — <short title>

- **Status:** `todo` | `in-progress` | `blocked` | `done` | `dropped`
- **Opened:** YYYY-MM-DD
- **Owner:** <name>
- **Sub-app(s):** backend | admin | frontend | docs
- **Branch(es):** `dev` (+ feature branch if any)

## Goal

One or two sentences: what outcome this task delivers and why.

## Scope

- In: …
- Out (explicitly not this task): …

## Log

Newest at the bottom. Date each entry. This is the "where is it" record.

- YYYY-MM-DD — opened; …

## Decisions

Sprint/task-local choices. **Durable** decisions → promote to `../../decisions/LEDGER.md`.

- …

## Definition of Done

- [ ] Code merged to `dev` in the relevant sub-app(s)
- [ ] EN + AR translations in the same commit (if any user-facing strings)
- [ ] Quality gate green (backend `pint --test` + `php artisan test`; Next apps `yarn type-check` + `yarn production`)
- [ ] Docs updated (this TASK.md set to `done`; index row updated; any drift fixed)
- [ ] Mobile contract checked if `routes/api.php` touched (`../../mobile/`)
