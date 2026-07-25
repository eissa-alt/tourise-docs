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
| 004 | [migration-squash](004-migration-squash/TASK.md) | dropped |
| 005 | [admin-httponly-token](005-admin-httponly-token/TASK.md) | done (code) — QA pending |
| 006 | [private-document-storage](006-private-document-storage/TASK.md) | done (code) — mobile ack + QA pending |
| 007 | [rsvp-decline-not-interested](007-rsvp-decline-not-interested/TASK.md) | done (code) — QA pending |
| 008 | [guest-drafts-port](008-guest-drafts-port/TASK.md) | done (code) — QA'd; ledger D19 |
| 009 | [usefetch-adoption](009-usefetch-adoption/TASK.md) | done — standing convention (closed 2026-07-19) |
| 010 | [api-routes-cleanup](010-api-routes-cleanup/TASK.md) | done — cleanup + reorg + RESTful rename (cross-repo cutover) + whereUuid + RBAC gating (Tiers 0–4); closed + bulk-image leftovers folded in 2026-07-20, ledger D24 |
| 011 | [scan-into-admin](011-scan-into-admin/TASK.md) | done (code) — gate scanning ported into admin, standalone scanner retired, new `scanning` RBAC feature; live browser-QA pending |
| 012 | [linkedin-auto-post](012-linkedin-auto-post/TASK.md) | done (code) — per-category LinkedIn automatic "Share on LinkedIn" completed (backend + admin + frontend); ledger D25; LinkedIn-app + browser QA pending |
| 013 | [sms-provider-config](013-sms-provider-config/TASK.md) | done (code) — DB-driven SMS provider config ("SMS SMTP") ported from cyan (backend + admin), listener rewired off env, `services.unifonic` removed; ledger D26; prod send-test QA pending |
| 014 | [otp-sms-dynamic-config](014-otp-sms-dynamic-config/TASK.md) | done (code) — deleted the hardcoded FGC OTP gateway (+ committed creds) from `AuthController`; phone-OTP now uses the dynamic `SmsSender`/`SmsProviderConfig` stack; added SMS mirror of the D27 pickers (category `sms_config_id` + `otp_sms_config_id`) + `sms-provider-configs/select`; gates green; manual QA pending |
| 015 | [per-flow-smtp-override](015-per-flow-smtp-override/TASK.md) | done (code) — admins can override the default SMTP per flow: category has two pickers (notifications register/accept/reject + guest email-OTP), + automations + invitations; `applyConfigById` resolver, snapshot at create, override beats `MAIL_HOST_BULK`; gates green; manual QA pending |
| 016 | [sms-flow-parity](016-sms-flow-parity/TASK.md) | done (code) — SMS now fires on accept/reject (reuses `guest_sms`), automations (`with_sms_template` toggle), and invitations (new `invitation_sms` table + listener), each with its own SMS-provider override picker; migrations `000006`+`000007`; ledger D29; gates green; manual QA pending |
| 017 | [single-channel-invitations](017-single-channel-invitations/TASK.md) | done (code) — an invitation collection now sends on exactly one channel (email\|sms; whatsapp reserved); `channel` enum folded into `000006`, scoped template/provider, channel-aware guard + status, channel picker + observability; **reverses the parallel-send half of D29**; ledger D30; gates green; manual QA pending |
| 018 | [sms-logs](018-sms-logs/TASK.md) | done (code) — read-only guest + invitation SMS log pages mirroring the email logs, new `sms_logs` RBAC feature (view/export); ledger D31; gates green; manual QA pending |

| 019 | [logistics-evisa-port](019-logistics-evisa-port/TASK.md) | done (code) — re-added hotels/rooms, traveling-status, per-guest logistics + 4 exports, and e-visa generation/PDF/console, all modernized to Tasks 001/002/009/010; found and fixed 6 pre-existing defects incl. `valid_visa` being silently discarded on every registration; February's e-visa ops console deliberately NOT ported (dead on hci main); ledger D32; gates green; `sendIssuedVisa` + manual QA pending |
| 020 | [reconfirmation](020-reconfirmation/TASK.md) | in-progress (code) — guest attendance reconfirmation ("second RSVP"), built on 121's own machinery (not a 120 port): `reconfirmed_*` columns + `reconfirmation_tokens`, public `/reconfirm` page, `{{ reconfirmation_url }}` across email/SMS/WhatsApp via shared `ReconfirmationLink`, admin column/filter/see-more/exports; delivered by the D38/D39 automation; gates green (backend 474 tests, admin/frontend type-check); committed on `dev`/`main`, NOT pushed; dev-DB migrate + manual QA + mobile notice pending |
| 021 | [seating](021-seating/TASK.md) | planned — port the standalone **Seating Plan Manager** (Vite/React SPA from 120) into the baseline as a **4th sub-app** `alt-static-basecode-seating` (API-wire, no UI merge); 14-agent verified analysis; all design decisions LOCKED (D-1…D-8: build in 121, attendance-bridge, own-login handoff, dedicated `seating` RBAC feature, full port, keep Vite as-is); sequenced **after 020** (now landed) → ready to start; execution not begun |

_Add a row per task as you open it; newest at the bottom._

## Parked buckets

Not tasks — batches of follow-ups an owner explicitly chose to defer. Read before opening new work in
the same area, so a known-parked item isn't rediscovered as a "bug".

| File | Covers | Status |
|---|---|---|
| [PHASE3_PARKED_TODO.md](PHASE3_PARKED_TODO.md) | admin/frontend code-quality audit leftovers | closed 2026-07-19 |
| [PHASE22_PARKED_TODO.md](PHASE22_PARKED_TODO.md) | follow-ups surfaced by the P22 client-name sweep | **open** — parked 2026-07-22 |
