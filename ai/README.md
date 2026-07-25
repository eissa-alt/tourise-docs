# AI Handoff — `alt-static-basecode-repos`

Single entry point for AI agents (Claude Code / Claude Desktop / Cursor / any LLM) working in this repo.

**First session in this repo? → `KICKOFF_PROMPT.md`** (paste it into the agent as the first message).

## Read in this order (5 min total)

1. `PROJECT_OVERVIEW.md` — what this project is.
2. `ARCHITECTURE_NOTES.md` — the **four-app** split, folder layout, data flow.
3. `CODING_STYLE.md` — conventions actually used in the code.
4. `CURRENT_WORKFLOW.md` — dev commands + how a feature is normally built.
5. `AI_RULES.md` — hard do/don't rules. **Treat as binding.**

## Pre-existing docs you should reuse, not duplicate

- `../upgrades/` — the upgrade-then-clone initiative: `UPGRADE_SUMMARY.md` (what was done + commit SHAs), `BASELINE_DECISION.md` (why directors is the baseline), and the portable Tailwind/cyan playbooks. Index: `../upgrades/README.md`.
- `../decisions/LEDGER.md` — durable, cross-task locked decisions (`D1…Dn`).
- `../process/WORKING_MECHANISM.md` — branching, commit format, task flow, quality gate, Definition of Done.
- `alt-static-basecode-admin/FORM_RESTRUCTURE_GUIDE.md` — project-based dynamic-form folder layout.
- `LISTING_SELECT_PATTERN.md` (this folder) — the reusable listing table + "clean select box" (`ListingTable` + `ListingFooter` + selection bar). Compose it; don't hand-roll a listing `<table>`.
- `alt-static-basecode-backend/DARK_MODE_EMAIL_NOTES.md` — email-template dark-mode rules.
- `../mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf` — backend contract changes for the mobile client.

If a file under `docs/ai/` disagrees with one of the pre-existing docs, the pre-existing doc wins for its topic.

## Sibling assets (one level up from `alt-static-basecode-repos/`)

The parent folder `121-alt-static-basecode/` holds non-code assets the AI should know exist but should **not** edit:

```
assets/  assets_v2/  assets_v3/  assets_v4/   ← design drops from the client
badges/    documents/   dns/    fav/   fonts/   seo/   tech docs/
import_Test/                                   ← sample import sheets
alt-static-basecode.pem                    ← deploy key, never read or move
```
