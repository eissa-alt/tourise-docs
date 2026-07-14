# Clone Checklist — spin up a new project from this baseline

This repo (`pif-directors-gathering`) is the **upgrade-then-clone baseline**. When you copy it to
start a new project (e.g. `119-xxx`), the *folders* are easy to rename — but the docs contain ~90
in-file references to the project identity that a folder-rename won't touch, plus some docs that
record *this* project's state and must be **reset**, not renamed.

Work the buckets top to bottom. **Bucket 1 is scripted; Buckets 2–3 need judgment — don't automate them.**

> Run everything below from the **wrapper repo root** — the folder that contains `CLAUDE.md` and
> `docs/` (after you've renamed it to the new project).

---

## Bucket 0 — what is intentionally NOT renamed

**`docs/upgrades/` stays frozen.** It's lineage/reference: `UPGRADE_SUMMARY.md` (this baseline's
Part 1–5 history + commit SHAs), `BASELINE_DECISION.md` (why directors was chosen), and the portable
`CYAN_*` / `TAILWIND_*` playbooks. They legitimately talk *about* directors/cyan — renaming would
corrupt the record. For your new project they document **what your inherited baseline already includes**
(Next 15, React 18.3.1, Headless UI v2, Tailwind v4, Laravel 12). Leave them as-is.

The rename in Bucket 1 therefore **excludes `docs/upgrades/`** (and this checklist itself).

---

## Bucket 0.5 — sub-app env files (carry over, do NOT skip)

> These are gitignored secrets — they're **never committed**. This bucket is about the *working-tree
> copy*: when you clone the four sub-apps, these files must come across so the new apps aren't left
> without runnable config. A folder copy that respects `.gitignore` (or a fresh `git clone`) will
> **drop them** — that's the trap this bucket exists to catch.

**Do NOT skip these when copying the sub-apps into the new project:**

- `pif-directors-gathering-backend/` → **`.env`** (the `.env.example` + `.env.example_prod` templates are
  tracked and come for free; only `.env` itself is gitignored and must be carried by hand)
- `pif-directors-gathering-admin/` → **`.env.local`** · **`.env.production`**
- `pif-directors-gathering-frontend/` → **`.env.local`** · **`.env.production`**

**Handling once carried:** copy **verbatim** so the new apps run immediately, then re-point the
directors values (API URLs, keys, DB creds, Vercel/deploy targets) to the new project by hand afterward.
These still hold directors' live secrets until you do — do not commit them and do not deploy on them as-is.

```bash
# sanity check after the sub-app copy — every line below must exist in the NEW project
ls -la <new>-backend/.env \
       <new>-admin/.env.local <new>-admin/.env.production \
       <new>-frontend/.env.local <new>-frontend/.env.production
```

---

## Bucket 1 — mechanical rename (scripted)

The identity is consistent, so it's basically three tokens. The slug `pif-directors-gathering`
also fixes `-backend` / `-admin` / `-frontend` / `-docs` and the remote URL in one pass.

```bash
# --- edit these four lines, then paste the whole block ---
OLD_SLUG="pif-directors-gathering"
NEW_SLUG="x-project"                 # MUST match your new sub-app folders: <NEW_SLUG>-backend, -admin, ...
OLD_NAME="PIF Directors Gathering"
NEW_NAME="X Project"                 # human-readable display name
OLD_ORG="eissa-alt"; NEW_ORG="eissa-alt"   # change only if the GitHub org differs

# rename across all markdown EXCEPT the frozen lineage + this checklist
find CLAUDE.md docs -name '*.md' \
  -not -path 'docs/upgrades/*' \
  -not -path 'docs/process/CLONE_CHECKLIST.md' \
  -not -path 'docs/.git/*' | while IFS= read -r f; do
  sed -i '' \
    -e "s#${OLD_SLUG}#${NEW_SLUG}#g" \
    -e "s#${OLD_NAME}#${NEW_NAME}#g" \
    -e "s#${OLD_ORG}#${NEW_ORG}#g" "$f"
done
echo "rename pass done"
```

> macOS BSD `sed` needs the `-i ''` form (already used). zsh does **not** word-split unquoted
> variables, so the `while IFS= read -r` loop (not `for f in $files`) is deliberate.

**Verify — expect only this checklist to still contain the old strings:**

```bash
grep -rIn -e "$OLD_SLUG" -e "$OLD_NAME" CLAUDE.md docs --include='*.md' | grep -v 'docs/upgrades/'
# Clean result = only docs/process/CLONE_CHECKLIST.md lines. Anything else → fix by hand.
# Also eyeball bare words the script won't catch:
grep -rIn -e '113-' -e '\bdirectors\b' CLAUDE.md docs --include='*.md' | grep -v 'docs/upgrades/'
```

Also (optional, non-`.md`): the comment header in `docs/.gitignore` names the old docs repo — tidy by hand.

---

## Bucket 2 — reset this project's state (wipe, don't rename)

These record directors' specific history; they're meaningless for the new project.

- [ ] **Re-init the docs git repo** (it still points at `…/pif-directors-gathering-docs.git`):
  ```bash
  rm -rf docs/.git
  git -C docs init -b main
  # create the <NEW_SLUG>-docs repo on GitHub first, then:
  git -C docs remote add origin https://github.com/${NEW_ORG}/${NEW_SLUG}-docs.git
  ```
  > **Branch process (docs):** docs lives on **`main`** — that's its working branch. Do **not** add a
  > `dev` branch here. (Code repos differ — see below.)
- [ ] **Re-init each code sub-app's git** — fresh history, no directors upstream. Per the
  branch process, **make `main` first, then branch `dev` off it** (code works on `dev`):
  ```bash
  for app in backend admin frontend; do
    repo="<NEW_SLUG>-${app}"
    rm -rf "$repo/.git"
    git -C "$repo" init -b main          # 1. main branch first
    git -C "$repo" add -A
    git -C "$repo" commit -m "chore: initialize ${repo} from pif-directors-gathering baseline"
    git -C "$repo" branch dev            # 2. then a new dev branch off main
    git -C "$repo" switch dev            #    land on dev — the working branch
    # create the GitHub repo first, then:
    git -C "$repo" remote add origin https://github.com/${NEW_ORG}/${repo}.git
  done
  ```
  > **Branch process (code):** every code repo gets **`main` created first, then a new `dev` branch**
  > off it; `dev` is the working branch (never push to `main`). Reminder — env files are gitignored,
  > so this initial commit will **not** include them (Bucket 0.5 carries them separately).
- [ ] **Wipe the task log** — start fresh numbering:
  ```bash
  rm -rf docs/tasks/0*-*/        # removes 001-docs-reorg (and any later directors tasks)
  ```
  Then blank the index table in `docs/tasks/README.md` back to a header-only "no tasks yet."
- [ ] **Reset the decision ledger** `docs/decisions/LEDGER.md` — drop D1/D2, seed a fresh:
  > `D1 — <date> — cloned from pif-directors-gathering baseline @ <baseline-sha>. Inherited stack:
  > Next 15 / React 18.3.1 / Headless UI v2 / Tailwind v4 / Laravel 12 (see upgrades/UPGRADE_SUMMARY.md).`
- [ ] **Reset `docs/HANDOFF.md`** to a one-liner: "New project, cloned from directors baseline on `<date>`. No work in flight."

---

## Bucket 3 — re-author / decide (real content work)

Rename gets the strings right; it does **not** make these *true* for the new project.

- [ ] **Mobile contract** — `docs/mobile/` holds directors' binary contract.
  - **No mobile app?** Remove it and its references:
    ```bash
    rm -rf docs/mobile
    grep -rIl 'BACKEND_INCOMING_CHANGES_FOR_MOBILE\|mobile contract' CLAUDE.md docs --include='*.md'
    ```
    Then delete CLAUDE.md **hard-rule #4** and trim the mobile lines the grep listed (notably across `docs/ai/*`).
  - **Has mobile?** Replace the PDF/HTML with the new contract; keep the rule.
- [ ] **Rewrite the code-describing AI docs** — these describe directors' *actual* code and will be
  wrong until redone:
  - `docs/ai/PROJECT_OVERVIEW.md` — replace the conference-platform scope with the new project's.
  - `docs/ai/ARCHITECTURE_NOTES.md` — fix the app split; **remove the directors-only callout**
    ("don't port cyan's `DynamicFormRenderer` / older form-shapes pattern") unless it applies.
  - `docs/ai/CODEBASE_DEEP_DIVE.md` — directors-specific deep-dive + drift findings; regenerate or delete.
- [ ] **Review `CLAUDE.md` project-specific rules** — e.g. the form-shapes rule (#4) and the
  sub-app list. Keep the inherited guardrails (Sentry removed, quality gate, commit format,
  no framework bumps).
- [ ] **Lighter touch (rename usually enough, skim once):** `docs/ai/CODING_STYLE.md`,
  `CURRENT_WORKFLOW.md`, `AI_RULES.md`, `KICKOFF_PROMPT.md`, `docs/process/*`,
  `docs/process/SETUP_AND_UPDATE.md` (confirm clone URLs + the prereqs/versions still hold).

---

## Final — commit the fresh baseline

```bash
git -C docs add -A
git -C docs commit -m "chore: initialize <NEW_SLUG> docs from pif-directors-gathering baseline"
# git -C docs push -u origin main   # after creating the GitHub repo
```

## Done when

- [ ] Sub-app env files carried over (Bucket 0.5): backend `.env` (the `.env.example*` templates are tracked); admin/frontend `.env.local` + `.env.production` — all present in the new project, none skipped
- [ ] Verify grep (Bucket 1) returns only this checklist
- [ ] `docs/upgrades/` left untouched (lineage intact)
- [ ] `docs/.git` re-inited + new remote; no `pif-directors-gathering-docs` remote left; docs on `main`
- [ ] each code sub-app re-inited: `main` created first, then `dev` branched off it; landed on `dev`; new remote set; no directors upstream left
- [ ] task log empty; ledger + HANDOFF reset to the new project
- [ ] mobile decision made; AI overview/architecture docs reflect the **new** project, not directors
- [ ] `SETUP_AND_UPDATE.md` clone URLs point at the new repos
