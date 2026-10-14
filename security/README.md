# Security

Security assessments of TOURISE 2027, what each one found, and what we did about it. One place to
see the state of every finding.

**Classification:** CONFIDENTIAL / TLP:AMBER. This folder describes weaknesses, some still open.
Do not copy it outside the team.

## Tracker

Every finding from every assessment, plus the ones we found ourselves. Update the row in the same
commit as the fix (code SHAs per repo) or the decision.

| ID | Finding | Source | Severity | Track | Status | Owner | Commits | Detail |
|---|---|---|---|---|---|---|---|---|
| M-001 | Outdated Next.js, 15.5.19 in frontend and admin | Haboob 2026-09 | Medium | CODE | **FIXED ON DEV**: Next.js 15.5.27 in frontend (PR #17) and admin (PR #63). Not on `main` yet. Deploy needs `yarn install --frozen-lockfile` and Node 20.9+ | dev | frontend `242552d`, admin `be036e9` | [triage 4.1](pentest-2026-09/PENTEST_TRIAGE/PENTEST_TRIAGE.md#41-m-001--outdated-nextjs) |
| M-002 | Debug output on production; handler turns 4xx into 500 once debug is off | Haboob 2026-09 | Medium | OPS + CODE | **FIXED, NOT DEPLOYED**: `APP_DEBUG=false` in the production `.env` (owner, 2026-10-13); B9 handler fix on `dev` and `main` (PRs #64, #65). To do: deploy the backend, confirm `config:show app.debug`, `_ignition` 404, `--no-dev` | devops | backend `c8a1885` | [triage 4.2](pentest-2026-09/PENTEST_TRIAGE/PENTEST_TRIAGE.md#42-m-002--improper-error-handling) |
| M-003 | `/api/guests/check-unique` queries any column; `mode=edit` returns the guest | Haboob 2026-09 | Medium | CODE | **FIXED ON DEV**: type must be `email`, compared ignoring case, no record returned (PR #66). Not on `main` yet. The missing rate limit goes with M-005 | dev | backend `d5453ef` | [triage 4.3](pentest-2026-09/PENTEST_TRIAGE/PENTEST_TRIAGE.md#43-m-003--database-column-names-disclosed) |
| M-004 | Email OTP not tied to the email registered | Haboob 2026-09 | Medium | CODE | **FIXED ON DEV**: the code is matched with the submitted email at registration (PR #66). Not on `main` yet. `email-confirmation` stays token-only (UI step only) | dev | backend `d5453ef` | [triage 4.4](pentest-2026-09/PENTEST_TRIAGE/PENTEST_TRIAGE.md#44-m-004--otp-bypass) |
| M-005 | Email enumeration on `/api/guests/check-unique` | Haboob 2026-09 | Medium | CODE | **FIXED ON DEV, RISK REDUCED**: reCAPTCHA required on every lookup (PRs #67, #18); the \"already registered\" message kept by the owner's decision, residual risk proposed to STA. Not on `main` yet; deploy the frontend first | dev | backend `b628d48`, frontend `487dd43` | [triage 4.5](pentest-2026-09/PENTEST_TRIAGE/PENTEST_TRIAGE.md#45-m-005--user-enumeration) |
| O-001 | Email enumeration on `/api/invitation-requests/check-unique` (added 2026-09-30, after the test) | Ours | Medium | CODE | **FIXED ON DEV, RISK REDUCED**: same change as M-005; the partner's `check-email` (key and server IP) untouched | dev | backend `b628d48`, frontend `487dd43` | [triage 4.5](pentest-2026-09/PENTEST_TRIAGE/PENTEST_TRIAGE.md#45-m-005--user-enumeration) |
| O-002 | CORS on `/api/*` allows any site if `CORS_ALLOWED_ORIGINS` is unset (the config's fallback is `*`) | Team WhatsApp 2026-09-13 | Low | OPS | **CLOSED**, no change needed: the production `.env` has `CORS_ALLOWED_ORIGINS` set to the admin and the public site only (owner, 2026-10-13). The `*` fallback remains for a server built without it | devops | | [triage 4.2](pentest-2026-09/PENTEST_TRIAGE/PENTEST_TRIAGE.md#42-m-002--improper-error-handling) |

**IDs.** An assessor's finding keeps its own ID (Haboob's `M-001-072` is written `M-001`). Our own
findings are `O-001`, `O-002`, and so on. **Status:** OPEN, TO CONFIRM, IN PROGRESS, FIXED (with commits),
DEPLOYED, CLOSED (no change, with the reason), DISPUTED.

### Tracks

| Track | Meaning |
|---|---|
| **CODE** | A repository change, with tests, through the usual branch and PR |
| **OPS** | A server, `.env`, nginx or Cloudflare setting. No repository change; needs whoever runs production |
| **DECISION** | Needs the owner's call before any work starts |

## Assessments

| Folder | Assessor | Tested | Findings | Status |
|---|---|---|---|---|
| [pentest-2026-09/](pentest-2026-09/README.md) | Haboob, for STA | 14 to 15 Sep 2026 | 5 Medium | Triaged 2026-10-13, nothing fixed yet |

## How this folder relates to Task 041

[Task 041](../tasks/041-security-port-wave-1/TASK.md) is the cross-project security wave: 23 items
ported from the other ALT projects' reviews, opened 2026-09-21. Where a finding here is also a
Task 041 item, the fix is one piece of work: record it in both places and keep the IDs side by side
(M-003 is B11, M-004 is B12, M-002 needs B9 first). Task 041 stays the plan for its own items; this
folder is the record per assessment.

## Rules

- **Assessors' reports stay out of git.** They are confidential to the client and the assessor.
  Keep them in `127-tourise/security_docs/` and point to them from the assessment's README.
- **No passwords, tokens or keys in this folder**, including the passwords of protected reports.
- **No captured internal values.** Describe what leaked (an internal address, a database name,
  personal data), never the values.
- **Each report is a folder** with `<NAME>.md`, `<NAME>.html` and `<NAME>.pdf`, in the TOURISE 2027
  theme: see [REPORT_GENERATION_WORKFLOW.md](REPORT_GENERATION_WORKFLOW.md). The `.md` is the source;
  regenerate the other two whenever it changes.
- **No em dashes** in these documents, as everywhere in this project.

## How we ship a security fix

The method behind Task 041, written down so the next fix (or the next project) works the same way
(Task 041 B22). Each rule comes from something that went wrong in pep-v2 or nearly did here.

1. **Check the problem exists here before copying a fix.** Another project's document may describe
   a fix that was never built, built differently, or later undone. Read this project's code first.
   *B15: pep-v2's two debug hooks were never in Tourise, so only the regression test was needed.
   B21: pep-v2's plan named the fix but never built it, so Tourise wrote its own.*
2. **Say how sure we are.** Mark each claim as proven by the code, proven by a test (and that the
   test fails on the old code), or only checkable on the server. *APP_DEBUG cannot be proven from
   outside since B9: it is read on the server (`php artisan config:show app.debug`).*
3. **Deploy order: whoever sends the new thing ships first.** When a fix changes what the API
   expects, the client that starts sending it goes out before the backend that starts requiring
   it. *reCAPTCHA on the email lookups (M-005): frontend first, or the live forms stop at the email
   field.* The reverse holds when the backend stops requiring something: *B3: backend first, since
   the old backend requires `back_link`.* Write the order in the deploy checklist.
4. **Run the suite with debug off too.** `APP_DEBUG=false php artisan test` as well as the normal
   run, every time. *B9: 94 tests passed only because debug was on, which hid that production
   answered 401, 403 and 422 as 500.*
5. **One owner per security header.** Before an app sets a header, check whether the server in
   front already sends it (`curl -sI`). Two copies either conflict or are enforced together. *B20:
   the edge sends X-Frame-Options, nosniff and Referrer-Policy, so the app sets only CSP and
   Permissions-Policy.*
6. **Query existing data before tightening a rule.** A stricter rule on a field that already holds
   data can break every later save of that record, or change what users see. *B4: before deploying,
   check whether any share text contains `<` or `>`.*

And for every fix: a test that fails on the old code, the full suite green both ways, the server
steps in the Task 041 deploy checklist, and `scripts/post-deploy-security-check.sh` after deploy.
