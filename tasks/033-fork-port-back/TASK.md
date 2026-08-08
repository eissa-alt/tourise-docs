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
- [ ] Quality gate green (backend `composer qa`; Next apps `yarn type-check` + `yarn production`)
- [ ] Findings-doc checkbox ticked for each item shipped
- [ ] Docs updated (this TASK.md log kept current; index row updated)
- [ ] Mobile contract checked if `routes/api.php` touched ([`../../mobile/`](../../mobile/))
