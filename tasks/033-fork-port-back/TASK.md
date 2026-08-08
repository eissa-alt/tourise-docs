# Task 033 — Fork port-back (122-gfeai-v2 / 123-pif-pep-v2 / 124-ewc-2026-v2)

- **Status:** `in-progress` (analysis done, nothing ported)
- **Opened:** 2026-08-06
- **Owner:** Eissa
- **Sub-app(s):** backend | admin | frontend | seating | docs
- **Branch(es):** `dev`

## Goal

Copy back into this baseline the fixes and generic features the three clone projects found, so the
next clone starts from a better place. The full findings and the checkbox TODO live in
[../../upgrades/FORK_PORT_BACK_FINDINGS.md](../../upgrades/FORK_PORT_BACK_FINDINGS.md) — **that
document is the working list; this file is the "where is it" record.**

## Scope

- **In:** architectural fixes, new features, fixes to existing features, security fixes,
  data-integrity fixes, test/CI/tooling infrastructure. Also the defects the audit found in *this*
  baseline that no fork fixes (findings doc section 9).
- **Out:** branding, theming, colours, logos, fonts, SEO/OG images, copy edits,
  translation-content-only changes, each project's own form shapes and their business logic,
  project-specific export column sets, project-specific seeder content.

## Working process — binding

**One item at a time. No commit until the owner has reviewed the actual diff.**

Per item: make the change → run the app's quality gate → print the real `git diff` (not a summary)
→ stop → owner reviews → owner says commit → commit. Pushing is a separate approval.

Rationale is in the findings doc: much of this backlog touches shared code (one `ListingTable` edit
reaches 46 listings, one `ui-select` edit reaches every admin dropdown), so batching makes a bad
change hard to isolate and hard to reject. A dirty working tree between steps is intentional.

## Log

Newest at the bottom.

- **2026-08-06 — opened.** Three-pass audit run and recorded; no code ported.
  - **Pass 1** (18 agents) — read every fork commit, then a second set of agents tried to *disprove*
    each finding against this baseline's source. Two agents died mid-run and left coverage holes.
  - **Pass 2** (10 agents) — read the 166 commits nobody had read; challenged the pep + ewc findings,
    which pass 1 never covered; settled the open questions.
  - **Pass 3** (8 agents, 6 completed) — compared shared component *files* directly instead of
    reading commits. Highest-yield pass: found the two public-registration defects that three passes
    of commit-reading had walked past. Stopped early by the owner; the 2 remaining agents were the
    basecode-native audit and the scope-verifying critic.
  - Result: ~60 verified items, 87 checkboxes — 17 one-liners, 20 small, 8 medium, 5 large.
    Committed as `docs` `7f049d3`; working process added in `212d58a`.
  - **Three earlier conclusions were corrected by the audit** and are called out in the findings doc:
    P029.1 only half-fixed the title 500; the email-log boolean fix landed on the backend but not the
    admin; the guests listing drops **9** filters on pagination, not none.

- **2026-08-08 — section 4 (the quick wins) CLOSED.** Nine items shipped, one closed as won't-do.
  **11 commits on `dev` / docs `main`, none pushed.** Backend tests **489 → 494**. Every item followed
  the working process: change → gate → real diff → owner review → commit.
  - **Backend (7):** `afd4eee` test backdoors · `117da56` invitation link + 5 tests · `7bf1d9c`
    phantom `dinner_invite` · `880a7c0` `checked_in_at` · `e3591cc` the `dd()` · `9631e17` reCAPTCHA
    guard · `a19e8de` rate limit 200→500.
  - **Admin (2):** `9fb01fa` upload paths · `2db85bd` plain `build`. **Frontend (1):** `38f42d8`
    plain `build`. **Docs (1):** `a36d172` sidebar links won't-do.
  - **The gate is repaired.** `yarn production` could never run in CI — it wraps a gitignored
    `.env` file — which is why the handoff records it unrun batch after batch. With the plain `build`
    script the Next gate is now `yarn type-check` + `yarn build` (+ `check:rbac` on admin) and **ran
    green for the first time**. `CLAUDE.md` rule 5 + `process/SETUP_AND_UPDATE.md` updated to match.
  - **⚠️ Two findings-doc items had wrong descriptions** (file/line refs were sound; the summaries
    drifted). The upload item named `/admin/guests/upload`, which as an axios path resolves to
    `api/admin/admin/...` — the P20 trap; correct path is `guests/upload`. The sidebar item said three
    links; it is nine plus a section header, hidden deliberately. **Keep opening the file before
    editing — that is what caught both.**
  - **⚠️ New, not from any fork — `GOOGLE_RECAPTCHA_SECRET` is read via `env()` outside config**
    (`ReCaptcha.php:31`). Under `config:cache` that is `null`, which would reject **every login and
    registration** at 13 call sites. Recorded in findings section 9. **Check the real deploy before
    anything else.**
  - **Deferred by owner decision, all recorded:** pep's single-check-in 422 rewrite (needs
    iPad-scanner sign-off); the reCAPTCHA `ConnectionException` 500 (already fail-closed, so
    error-surface only); the mobile-CMS sidebar block; and whether `ExportEBadgesFiltered` gets a
    PARKED docblock or deletion.
  - **Still needs a human, unchanged:** does the admin CSP block reCAPTCHA on login (settle in a
    browser), and is the backend's reCAPTCHA secret Google's *test* secret.

## Decisions

Task-local. Durable ones → [`../../decisions/LEDGER.md`](../../decisions/LEDGER.md).

- **Take ewc `e647bb9` for the invitation-link fix, not gfeai `0e16754`.** Same controller change,
  but ewc's ships a 127-line `InvitationLinkTest` and documents why gfeai's own first attempt
  (`21037e6`) was wrong — gating on `usage_type` still blocked number-of-use invitations whose
  `usage_type` was `single` or unset.
- **Do not port gfeai's CSP widening.** It hardcodes a wildcard bucket host, which undoes this
  baseline's env-derived origin design (`next.config.js:14-29`). Move the 8 social icons to the
  project's own storage instead.
- **Do not port gfeai's SMS non-production guard.** This baseline removed that guard *deliberately*
  in P23.2 (`28eca40`, 2026-07-23) — after gfeai forked, so gfeai never added it, it just never got
  the removal. Porting it would reverse a locked decision. **Owner question, not a port.**
- **Port mechanisms, not values, for the export drift.** 28 classes in `app/Exports/` bind columns by
  hardcoded letter and several have already drifted. Fixing the letters leaves them ready to break
  again on the next column insert.
- **`PUT /admin/guests/attend` needs mobile sign-off before the wider pep rewrite.** `attend()`
  returns the whole Guest model, so it changes what the out-of-repo iPad scanner receives (not the
  Flutter app). Adding `checked_in_at` alone is additive and safe.

## Open questions

- **Does the admin CSP actually block reCAPTCHA on login?** Two agents reached opposite conclusions
  from source. **Settle it in a browser**, not by reading more code — open admin login with devtools
  and watch for a CSP violation. Adding the two Google hosts is cheap insurance either way.
- **Is the backend's `GOOGLE_RECAPTCHA_SECRET` Google's test secret?** gfeai `eafd3e4` says it is and
  that it does not match the site key the apps use. We do not read `.env`, so this is unverified —
  **check before enforcing reCAPTCHA in production.**
- **Some scope counts are single-agent claims** (14 sites / 46 components / 44 listings / 7 blob call
  sites). The verifying critic was stopped before it ran. The findings themselves were all verified.

## Definition of Done

Per-item, not per-task — this backlog will close in batches over several sessions.

- [ ] Code merged to `dev` in the relevant sub-app(s)
- [ ] EN + AR translations in the same commit (if any user-facing strings)
- [ ] Quality gate green (backend `composer qa`; Next apps `yarn type-check` + `yarn build`, plus
      `yarn check:rbac` on admin — see the 2026-08-08 log entry; `yarn production` is local-only)
- [ ] Findings-doc checkbox ticked for each item shipped
- [ ] Docs updated (this TASK.md log kept current; index row updated)
- [ ] Mobile contract checked if `routes/api.php` touched ([`../../mobile/`](../../mobile/))
