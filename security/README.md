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
| M-005 | Email enumeration on `/api/guests/check-unique` | Haboob 2026-09 | Medium | DECISION | **OPEN** | owner | | [triage 4.5](pentest-2026-09/PENTEST_TRIAGE/PENTEST_TRIAGE.md#45-m-005--user-enumeration) |
| O-001 | Email enumeration on `/api/invitation-requests/check-unique` (added 2026-09-30, after the test) | Ours | Medium | DECISION | **OPEN** | owner | | [triage 4.5](pentest-2026-09/PENTEST_TRIAGE/PENTEST_TRIAGE.md#45-m-005--user-enumeration) |
| O-002 | CORS on `/api/*` allows any site if `CORS_ALLOWED_ORIGINS` is unset (the config's fallback is `*`) | Team WhatsApp 2026-09-13 | Low | OPS | **TO CONFIRM**: set on production on 2026-09-14 (Haboob's headers show only `register.tourise.com`); check the `.env` lists only the site and the admin | devops | | [triage 4.2](pentest-2026-09/PENTEST_TRIAGE/PENTEST_TRIAGE.md#42-m-002--improper-error-handling) |

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
