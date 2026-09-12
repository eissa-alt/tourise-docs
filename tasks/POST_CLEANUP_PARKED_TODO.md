# Post-branch-cleanup — parked findings from the 2026-09-12 status sweep

**Parked:** 2026-09-12 (owner chose to park these and start a new set of tasks).
**Source:** a repo-state sweep run straight after the branch cleanup that reduced all three app
repos to `dev` + `main`. Nothing here was broken *by* the cleanup — these are pre-existing findings
the sweep surfaced while confirming the repos were clean.

**Repo state at park time — all green, so none of this blocks new work:**

| Repo | Branch | vs `origin` | vs `main` | Tree |
| ---- | ------ | ----------- | --------- | ---- |
| tourise-backend | `dev` | in sync | merged (`04a9aa9`) | clean |
| tourise-admin | `dev` | in sync | merged (`b0aec21`) | clean |
| tourise-frontend | `dev` | in sync | merged (`d6b35e9`) | clean |
| docs | `main` | in sync | — | clean |

Local dev DB: **136 migrations, 0 pending.** Only `dev` + `main` remain in each repo (7 local /
7 remote refs); the nine deleted branches and the three tip SHAs that are the only way back are
recorded outside this repo, in the session memory note `tourise-deleted-branch-shas`.

---

## Classification

| # | Item | Class | Where | Effort |
| - | ---- | ----- | ----- | ------ |
| 1 | Bulk mailer silently skipped under `config:cache` | **High — live-firing, silent** | backend | S (+ test) |
| 2 | ISR revalidation silently dead under `config:cache` | Moderate — silent no-op | backend | S |
| 3 | Security-alert emails go to nobody under `config:cache` | Low — monitoring blind spot | backend | XS |
| 4 | Category field visibility never landed (closed PR #4) | Moderate — feature gap | frontend | M |
| 5 | Task 033 fork-port-back: 52 of 89 items open | Moderate — known backlog | all | L |
| 6 | Task 034 marked `in-progress` but appears shipped | Bookkeeping | docs | XS |
| 7 | Task 035 browser QA still unticked | Bookkeeping — QA only | docs | S |
| 8 | `HANDOFF.md` / `CLAUDE.md` / setup docs describe a repo that isn't here | Bookkeeping — actively misleads | docs | S |
| 9 | Contradictory header comment on the request-invitation form | Low — cosmetic | frontend | XS |
| 10 | Two superseded status files at the wrapper root, outside any git repo | Low — housekeeping | root | XS |

**Class meanings.** *High* = wrong behaviour in production today, no error surfaced.
*Moderate* = real but bounded, or a paid-for feature that isn't reachable. *Low* = cosmetic or
observability. *Bookkeeping* = docs and status only, no code consequence.

---

## 1. Bulk mailer silently skipped under `config:cache` — **the only item worth fixing before new work**

`app/Notifications/SendAutomationEmailNotification.php:79`

```php
// The static bulk mailer only applies when there is no explicit per-flow
// SMTP override — an admin-chosen config wins over MAIL_HOST_BULK (D2).
if (! $overrideApplied && env('MAIL_HOST_BULK')) {
    $message->mailer('smtp-bulk');
}
```

Laravel stops loading `.env` once config is cached, so `env('MAIL_HOST_BULK')` reads `null` and the
branch never fires. **Every automation / campaign email without a per-flow SMTP override then goes
out through the default transactional mailer** instead of the bulk host. No exception, no log entry.
The cost is deliverability, not a crash: bulk blasts hitting the transactional SMTP's rate limits
and spending the main sending domain's reputation.

**Why this is believed live, not theoretical.** The reCAPTCHA outage (backend `bf31b85`,
`ReCaptcha.php:31`) was the identical bug class and is recorded as a *real production* defect —
`env()` → `NULL`, `config()` → present, every login and registration rejected. That incident is the
evidence production caches config. Scope is conditional on one unknown nobody has read from here:
whether `MAIL_HOST_BULK` is actually set in the production `.env`. If it is unset, nothing is
broken and bulk routing was never in play.

> ### ⚠️ The obvious fix is a trap — read before touching this
> `config/mail.php:50` defaults the host: `env('MAIL_HOST_BULK', 'bulk.smtp.mailtrap.io')`. So
> swapping the guard to `config('mail.mailers.smtp-bulk.host')` is **never falsy** — the branch
> would then fire on *every* automation email and route the lot to Mailtrap, a test inbox, where
> they disappear silently. That is strictly worse than today's bug.
>
> The fix needs a **dedicated boolean config key** resolved inside the config file (where `env()`
> is legitimate), e.g. a `mail.bulk_enabled` fed by `env('MAIL_HOST_BULK')`, with the guard reading
> that key. Confirm the production `.env` first, and check whether the deploy actually runs
> `config:cache` — there is no deploy script in the repo, so that is still unverified.

Related: this is the `noEnvCallsOutsideOfConfig` larastan rule, **suppressed** in
`phpstan-baseline.neon`. Six entries remain across the six files in items 1–3 — the rule was already
catching the reCAPTCHA bug before it shipped. Fixing an item means deleting its baseline entry too,
or the rule stays blind to the next one.

## 2. ISR revalidation silently dead under `config:cache`

Four sites, same shape: `SpeakersController.php:25-26`, `SpeakerLabelsController.php:137-138`,
`SponsorsController.php:48-49`, `SponsorLabelsController.php:141-142`.

```php
$frontendUrl = env('FRONTEND_BASE_URL');
$secretToken = env('REVALIDATE_SECRET_TOKEN');

if (! $frontendUrl || ! $secretToken) {
    return; // Skip if not configured
}
```

These are **explicitly guarded and wrapped in try/catch**, so under a cached config they take the
early return and skip the revalidation call. Consequence: an admin edits speakers or sponsors, saves
successfully, and the public site does not refresh. Confusing to diagnose from the admin side,
non-destructive, no crash. Lower than item 1 because it fails visibly-ish (stale page) rather than
quietly misrouting mail.

## 3. Security-alert emails go to nobody under `config:cache`

`app/Http/Controllers/AuthController.php:197`

```php
$recipients = array_filter(array_map('trim', explode(',', (string) env('SECURITY_ALERT_EMAILS', ''))));
```

Cached config → `''` → empty recipient list → the alert is composed and sent to no one. A monitoring
blind spot rather than a defect: nothing user-facing changes, but the alerts that exist to tell
someone about auth trouble are the thing that stopped working. XS fix, same config-key pattern as
item 1.

## 4. Category-driven field visibility never landed (closed PR #4)

`components/join/forms/default/request-invitation/step-1.tsx` uses `mandatoryFields` for
**requiredness only** — `isRequired={mandatoryFields?.includes('first_name') ?? false}`. There is no
`shows()` helper, so **no field is ever hidden**, and `optionalFields` is declared at line 55, passed
in by the page at line 84, and never read — a dead prop.

The result: the backend stores `mandatory_fields` / `optional_fields` per invitation-request
category (`2026_09_08_000001_add_form_fields_to_request_categories`), `GET
invitation-requests/config/{slug}` serves them, and admin shipped the UI to set them — and the
frontend honours none of it for visibility. Configure a category to stop asking for nationality and
the field still renders; it just isn't required. Coverage also narrowed: **5 fields** are
config-driven on `dev` (`company`, `email`, `first_name`, `job_title`, `last_name`) against **11** on
the branch that was closed.

**How to pick this up.** PR #4 (`feat/invitation-requests-and-newspaper`) was closed unmerged and
deleted on 2026-09-12, tip `83139bd`. Do not revive the branch — `dev` had moved 110 commits past it
with zero patch equivalence, and everything else on it was re-implemented at different paths. Port
**only the visibility layer** from that tip, and note the branch's own `shows()` carried a bug worth
not copying:

```ts
const shows = (field: string) => askedFor.length === 0 || askedFor.includes(field);
```

An empty array there means "show everything", but the backend contract is the opposite — `[]` is a
real answer meaning *ask for nothing*, because `fieldSplit()` resolves `null` into a concrete list
before responding. Severity is bounded: the form over-asks, never under-asks, and the extra fields
render optional.

## 5. Task 033 fork-port-back — 52 of 89 items still open

`upgrades/FORK_PORT_BACK_FINDINGS.md`: 37 checked, 52 open. Section 4 is closed and section 5 was
started; the remainder are section 5's lower-severity items. Two standing cautions from the task,
both still true: **the findings doc's summaries have been wrong repeatedly while its file/line refs
have been right every time** — open the file before editing — and the binding process is **one item
at a time, no commit until the owner reviews the diff**.

## 6. Task 034 marked `in-progress` but appears shipped

`tasks/034-tourise-form-shapes/TASK.md:3` still says `in-progress` and the index row says "not yet
committed, not browser-tested", but the two Tourise form shapes are on `dev` and merged to `main`.
Needs a verify-and-close pass, or a written note of what genuinely remains.

## 7. Task 035 browser QA still unticked

Code is done, committed and pushed; the migrate item is satisfied locally (136 ran, 0 pending) but
other environments are unconfirmed. The open DoD box is manual browser QA: categories edit on all
seven shapes, the picker lists the right options with no loading flash, **Media Registration is no
longer empty**, and saving keeps the selections.

## 8. The docs this repo tells you to read first describe a repo that isn't here

- **`HANDOFF.md`** — last touched 2026-08-08, five weeks stale at park time. It is the designated
  "read first for current state" pointer and still says *"ALL COMMITTED, NOTHING PUSHED"* and
  *"section 5 has ~30 items left"*. Everything after — tasks 034 and 035, and the whole newsletter /
  media-equipment / invitation-requests / VIP-shape stream through 2026-09-12 — is invisible in it.
  For scale: **~327 non-merge code commits** since its last entry (frontend 170, backend 79, admin
  78) against **9 docs commits**.
- **Root `CLAUDE.md`, `README.md`, `process/SETUP_AND_UPDATE.md`** name `alt-static-basecode-backend/`,
  `-admin/`, `-frontend/` plus a fourth `alt-static-basecode-seating/` sub-app. The real layout is
  three apps — `tourise-backend/`, `tourise-admin/`, `tourise-frontend/` — and **no seating app
  exists here**. A session trusting that folder list looks for directories that aren't there.
- **`SETUP_AND_UPDATE.md` tells you to delete `yarn.lock`**, which is tracked in both Next apps.
  Don't.
- **No task folder exists for the work after 035** — newsletter pages, VIP registration shape, media
  equipment sheet, photo face check, partner API keys, dignitary attendants, onboarding tokens,
  `university_location`. The index stops at 035.

Until this is fixed, derive current state from `git log` on `dev` and from the highest-numbered
`tasks/*/TASK.md`, not from `HANDOFF.md`.

## 9. Contradictory header comment on the request-invitation form

`components/join/forms/default/request-invitation/step-1.tsx:32` says *"Two stages behind one card:
details, then review"* while line 191 says *"There is no review screen on this shape"*. Line 191 is
current — there is no `ReviewStep` or `goTo('review')` anywhere in the request flow, and the form
posts directly. Stale comment left after the trim; one-line delete. (`ReviewStep` does exist and is
used, but by the dignitary / speaker / sponsor / media / tourise-public shapes.)

## 10. Two superseded status files at the wrapper root

`FRONTEND-PR4-STATUS.md` and `INVITATION-REQUESTS-MERGE-QUESTIONS.md` (both 2026-09-09) sit at the
wrapper root, which is **not a git repo** — so they are untracked by anything and invisible to the
docs history. Both are historical now: every question they pose was answered by shipped code or by
the PR being closed, except the one carried forward as item 4 above. Their answer tables are still
blank. Candidates for deletion, or for moving into `tasks/` if the narrative is worth keeping.
