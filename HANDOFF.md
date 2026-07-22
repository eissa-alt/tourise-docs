# Handoff — current state

> Rolling pointer, overwritten each session. For the durable record see the per-task `TASK.md`,
> `decisions/LEDGER.md`, and `upgrades/UPGRADE_SUMMARY.md`. Full plan: `upgrades/CYAN_FEATURE_PARITY_MASTER_PLAN.md`.

**2026-07-22 (latest) — P22 client-name sweep (P22.1–P22.6). ALL PUSHED.**
- **Every past-client name is out of the three code repos** — PIF, HCI, EDGEx, TOURISE, DeveGO, plus
  dead FAF/DGCA/ICAO templates. `components/join/forms/pif/` is now `forms/default/`; `pif-one-step`
  was deleted rather than renamed (no category used it and the form-shape select never offered it).
  `docs/ai/AI_RULES.md` rule 4 was rewritten in the same breath: it protects the *form-shapes pattern*,
  not the `pif/` folder name, so a clone renames `default/` rather than resurrecting `pif/`.
- **Two dead-code finds carried real branding.** `emails/notify_guest/{en,ar}` (12 hardcoded
  @hci_ksa social links) had **zero** references anywhere — the live guest-email path is
  `emails.base.waypoint`, which renders socials from the `social_media_links` table.
- **The invitation-PDF feature is parked, not fixed** (`343e6e8`, `efabc6d`). Four call sites loaded
  `pdf.invitation`, a view that has **never existed in this repo's history**; `dinner_invite` is not a
  column either. Routes, the automation attachment branch and the admin toggle are gone; the DB column
  and API contract are untouched, so re-enabling needs no migration.
- **Badge QR codes now render locally** (`9d4d5f3`). They used to `<img src>` api.qrserver.com, so mPDF
  made an outbound request per badge — printing hung when that service was slow, and every guest's
  registration number went to a third party. New `App\Services\QrCodeGenerator`; badge printing
  **manually confirmed** by the owner. Note: **no automated test covers badge/PDF rendering.**
- **⚠️ The email QR still calls qrserver.com on purpose** — Gmail/Outlook strip `data:` images, so the
  PDF fix does not transfer. Parked with the decision written up.
- **Commits:** backend `57f6d19`, `8a937d4`, `343e6e8`, `9d4d5f3`; admin `2c1cb75`, `cdaf902`,
  `4b27162`, `efabc6d`; frontend `3822549`, `52f6ebf`, `aa78591`; docs `ed5d187`.
- **Parked follow-ups → [`tasks/PHASE22_PARKED_TODO.md`](tasks/PHASE22_PARKED_TODO.md)** — the email QR,
  the ledger debt below, 622 unused translation keys, branded PDF backgrounds needing real artwork, and
  the test-coverage gaps. **Read it before starting work in any of those areas.**

**2026-07-22 (later) — P20 correction pass (ledger D33). ALL PUSHED.**
- **`inferFeatureId` swept, not spot-checked.** The first-match-wins trap turned up **six** times, two
  of them in already-shipped code: `sms_logs` (`/logs/*-sms` gated on `email_logs`, shipped P18.2),
  `/emails/smtp-configs` and `/gate-scan` (both long-standing, the latter defeating the gate-agent role
  D23 exists for). A ~20-line script comparing every live sidebar link's declared `featureId` against
  `inferFeatureIdFromPath(href)` found the two nobody had spotted. **All 28 live links now agree —
  turn that script into a test.**
- **The logistics screen was dead on arrival** (`7193f6f`). It called `/admin/guests/...` while the
  admin axios base already ends in `/api/admin`, so every request 404'd and the screen rendered its
  error state on every load. It shipped that way in P19.4 and was only caught when re-reading the code
  to answer a question. **Rule: admin Axios paths never carry an `/admin/` prefix.**
- **Logistics 403 resolved** (`436d225`): the loader's `Promise.all` spans two features, so the guest
  leg is now tolerant — it hides the guest-declared fields when unreadable and drops them from the PUT
  so they cannot be nulled unseen. A logistics-only role stays viable.
- **`CategoriesExport` column shift** (`ecce5a6`): `map()` omitted `visibility`, printing 20 values
  under 21 headings.
- **`composer qa` is green end to end (467/0)** (`c9bbdf9`) and **`php artisan test` no longer wipes the
  dev database** — `phpunit.xml` now pins sqlite `:memory:`. The "465 pass / 3 pre-existing" baseline is
  retired; treat any failure as real.
- **Commits:** backend `ecce5a6`, `c9bbdf9`; admin `621abdb`, `7193f6f`, `1bd50e5`, `436d225`.
- **⚠️ Still unexercised:** none of Task 019 or P20 has been opened in a browser. The logistics screen
  is the priority — it has had zero real use. RBAC needs a real restricted login too; the sweep proves
  the map is self-consistent, not that the whole chain works.

**2026-07-22 — Logistics + e-visa re-added from the P5.trim (Task 019, ledger D32). Since PUSHED —
8 commits across backend / admin / frontend / docs.**
- **What:** hotels, rooms (nested), traveling-status, per-guest `guest_logistics` + 4 exports + the
  logistics screen with hotel assignment, and e-visa package generation / PDF / issued-visa handling /
  admin console. Recovered from this repo's own pre-trim code where it still matched (`08d542e^`,
  `e3a0677^`) and from hci-2026 `origin/main` for e-visa, which is a newer generation than what we
  deleted (`e_visa_files` with real audit timestamps, not `e_visa_exports`).
- **Modernized on the way in:** `status` → `is_active` booleans, six string date/time columns → `date` +
  `string(5)` `HH:mm`, `flight_costs` → decimal, `block`/`activate` → one `toggle-status`, RESTful
  groups + `admin.can` gating, `useFetch`, `masked-date-input`, `CustomSwitchInputBoolean`.
- **Six pre-existing defects found and fixed** (none were the task): `valid_visa` silently discarded on
  every registration; room inventory leaking on re-assignment; `GuestsExportFlights` exporting 20 blank
  columns; the visa PDF shipping literal `contact-email` placeholder text to embassies; every e-visa
  admin endpoint 404'ing on the wrong base path; and the `inferFeatureId` first-match-wins trap three
  times over.
- **Deliberately NOT ported:** February's e-visa "operations console". It is absent from hci `main`
  (never merged, abandoned), and it drives `e_visa_status` with `pending`/`in_process`/`received`
  against the shipped `in_progress`/`issued` — two state machines on one column.
- **Commits:** backend `303c629`, `0ed06f3`, `0ea04fb`, `89f1673`; admin `8641f65`, `01764ab`,
  `83ba223`; frontend `b0e7e49`.
- **Gates:** backend `pint --test` + `phpstan` **No errors** + `migrate:fresh --seed` clean; admin
  `yarn type-check` + `next build` **123/123**; frontend `type-check` + build clean; EN/AR parity
  1611/1611. **Mobile contract unaffected** (all new routes `/admin/*`, nothing removed/renamed) — no
  notice issued.
- **Still open:** the push itself (the `composer qa` gate runs `php artisan test`, which wipes the dev
  DB — see the phpunit.xml note below); `sendIssuedVisa` not ported, leaving `issued_visa_send_count` /
  `issued_visa_sent_at` written by nobody; the logistics screen's `Promise.all` failing hard for an
  admin with `guest_logistics` but not `guests_listing,see_more`; and manual QA of the whole flow.
- **⚠️ `phpunit.xml` runs `RefreshDatabase` against the real MySQL dev DB.** The obvious fix
  (uncommenting the sqlite/`:memory:` lines) makes it worse — 5 failures vs the documented 3, because
  `EventDaysTest` is MySQL-dependent. Unresolved; it blocks a clean `composer qa`.

**2026-07-21 — Single-channel invitations (D30) + SMS logs (D31) + categories comms restructure + P17 UX
batch. ALL PUSHED across backend / admin / frontend `dev`; docs on `main`.**
- **Single-channel invitations (Task 017, ledger D30):** an invitation collection now sends on **exactly one**
  channel (`email` | `sms`; `whatsapp` reserved/disabled), reversing D29's parallel send. `channel` enum
  folded into migration `000006`; store/update scope the template + provider to the chosen channel; extract +
  collection-edit propagate `channel`; `invite` guard is channel-aware (checks `phone` for SMS); SMS success
  bumps `is_sent`/`send_count`. Admin: channel picker gated on a configured default (disabled + link when
  not), per-channel override sections on **both** create and collection-edit forms, channel badge in listing,
  SMS-history tab in see-more, wider bulk-send modal (channel/phone/template columns), reorganized update-info
  modal, `DialogShell` 4xl/5xl. Backend `0fcd3c5`, admin `f1589df`.
- **SMS logs (Task 018, ledger D31):** read-only Guest SMS + Invitation SMS log pages mirroring the email
  logs, behind a new `sms_logs` RBAC feature (view/export); `guest_sms` + `invitation_sms` each get a
  controller/resource/export + super-gated `/logs/*` page + sidebar link. Backend `34e09e7`, admin `8b0960f`.
- **Categories comms restructure (ledger D31):** master `with_email` / `with_sms` switches, **enforced** in
  `Category::getNotificationTemplate` (master off → never sends on that channel); `with_otp` →
  `with_email_otp` rename in lockstep across backend + admin + **frontend join pages** (mobile payload rename
  → notice `docs/mobile/MOBILE_NOTICE_CATEGORY_WITH_EMAIL_OTP_RENAME.md`); new "Admin access" tab +
  `assignable-admins` endpoint; validation-error surfacing; form width/gating. Backend `3c73f0f`, admin
  `702d9b1`, frontend `0d0d82b`.
- **P17 UX batch (earlier this session, admin):** gate scanning → its own `/gate-scan` page (`dac5c14`);
  sidebar SMS grouped under Communications + SMS-templates link (`2cf9409`); categories 5-tab form + provider
  override switches + OTP gating (`4c83678`); status dropdown → toggle switch across entity forms (`69ddd13`).
  Seeder: categories seeded with OTP off until a default SMTP exists (backend `c50ebb8`).
- **Also:** guests listing bottom spacing (admin `8c57f55`); the previously-unpushed LinkedIn OAuth commit
  (frontend `e8d7991`, Task 012) was pushed in the same round.
- **Gates:** backend `pint --test` + `phpstan` **No errors**; `composer qa` tests **465 pass / 3 fail** (the
  3 are pre-existing avatar-URL + `/`→403 env failures — verified my diff touches none of those areas). Admin
  + frontend `yarn type-check` + eslint/prettier (husky) green. **`yarn production` NOT run** — needs the
  gitignored `.env.production`. **Remaining:** manual QA with live SMTP/SMS providers; automation-form UX
  polish (mirror the invitations pass); WhatsApp channel (deliberately deferred — next big piece).

**2026-07-20 — Task 016 (SMS flow parity) code COMPLETE across backend + admin `dev` (ledger D29). ⚠️
Backend + admin + docs are UNCOMMITTED working-tree changes.**
- **What:** closes the SMS-vs-email gaps. Before, SMS only fired on register-complete + phone-OTP; now it
  fires on **accept/reject**, **automations**, and **invitations** too — each with its own optional SMS
  provider override, mirroring D27/D28.
- **Stage 1 (accept/reject):** `GuestsController` accept/acceptToCategory/reject create a `guest_sms` row
  (snapshot `sms_config_id`) + dispatch `SendGuestSMSEvent`; category "SMS notifications" picker relabelled
  register/accept/reject.
- **Stage 2 (invitations):** migration `2026_07_20_000006` — `invitations`/`invitation_collections` gain
  `sms_template_id`+`sms_config_id`; new `invitation_sms` table. New `InvitationSms` +
  `SendInvitationSmsEvent`/`SendInvitationSmsListener` (invitation-specific placeholders) fired from
  invite/bulk/reminder alongside the email; extract-bulk inherits/overrides the SMS template. Admin SMS
  template + provider pickers on invitation + collection forms + the extract modal.
- **Stage 3 (automations):** migration `2026_07_20_000007` — `automation_setups` gains `with_sms_template`
  + `sms_template_id` + `sms_config_id`. `AutomationController::send` creates a `guest_sms` row + dispatches
  `SendGuestSMSEvent` per guest when the toggle is on (independent of email); `split` carries the fields.
  Admin `with_sms_template` toggle + SMS template/provider pickers on the automation form.
- **Design:** guest-backed flows (accept/reject, automations) **reuse `guest_sms` + `SendGuestSMSEvent`**
  (same path as register-complete, non-prod block still applies); token-based invitations get their **own**
  `invitation_sms` table + listener (mirroring `invitation_emails`). Provider override rule = D28
  (blank/inactive → active-default, snapshot at create).
- **Touched (backend):** migrations `000006`+`000007`; `InvitationSms` + invitation SMS event/listener (+
  `EventServiceProvider`); `InvitationsController`/`InvitationsCollectionController` persist+dispatch;
  `AutomationSetupsController` store/split; `AutomationController::send`; `AutomationSetup`/`Invitation`/
  `InvitationCollection` fillable+casts; `Invitation`/`InvitationCollection`/`AutomationSetups` resources.
- **Touched (admin):** `sms-template-select` (`errors` prop optional) + provider/template pickers on
  invitation / collection / extract-bulk / automation forms + `with_sms_template` toggle + interfaces + EN/AR
  (`sms_override`, `with_sms_template`).
- **Gates:** backend `pint --test` passed + `phpstan` No errors; admin `yarn type-check` + eslint green;
  `mobile/*` untouched. **Still open:** manual QA with a real active provider. **Needs commit + push.**

**2026-07-20 — Task 014 (OTP SMS → dynamic provider + per-flow SMS override) code COMPLETE across backend +
admin `dev` (ledger D28). ⚠️ Backend + admin + docs are UNCOMMITTED working-tree changes.**
- **What:** deleted the hardcoded FGC OTP gateway (`cnc.fgc.sa` + committed `sdbankApi`/`SDB` password) from
  `AuthController` — **no static SMS code left**. Phone-OTP now flows through the DB-driven provider stack
  (D26: `SmsProviderConfig` + `SmsSender`, Unifonic today). Added the SMS mirror of D27's SMTP pickers:
  category has **two** SMS provider pickers — register-complete + phone-OTP. Blank/inactive → active-default.
- **⚠️ Behaviour change:** OTP calls `SmsSender` directly, so it still sends on **dev/stage** (a code the
  user waits for) — but now via the **real active-default provider**, not the old FGC test gateway. Register/
  notification SMS keeps the listener's non-prod block.
- **Touched (backend):** migration `2026_07_20_000005` (`categories.sms_config_id` + `otp_sms_config_id`,
  `guest_sms.sms_config_id`) + `AuthController::phoneVerification` rewrite + `SendGuestSMSListener` snapshot +
  `GuestsController` register/resend snapshot + `Category`/`GuestSMS` fillable + `CategoriesController`
  validation/persist + `CategoriesResources` + `SmsProviderConfigController::selectList` + `GET
  admin/sms-provider-configs/select`.
- **Touched (admin):** reusable `sms-provider-config-select` + two category pickers + `interfaces/category`
  + EN/AR. No frontend change (join form already forwards the `category` slug).
- **Gates:** pint + phpstan clean; admin `yarn type-check` + eslint green; `mobile/*` untouched. **Still
  open:** manual QA with a real active provider. **Needs commit + push.**

**2026-07-20 — Task 015 (per-flow SMTP override) CLOSED + pushed (ledger D27).** Backend `2adc387`, admin
`76ae079`, docs `8c9ef34`.
- **What:** admins can pick which SMTP account sends each email flow instead of always the default.
  Category has **two** pickers: notifications (register/accept/reject) + guest email-OTP. Also overrides
  on automations and invitations/collections. Blank = default. Inactive/deleted override → fall back to
  default. Automation override beats `MAIL_HOST_BULK`. **Still open:** manual QA with multiple SMTP accounts.

**2026-07-20 — Task 013 (SMS provider config) CLOSED + pushed (ledger D26).** Backend `96a15ce`, admin
`661f134`, docs `f3802b3`. Manual Unifonic prod QA still pending.

**2026-07-20 — Task 012 (LinkedIn automatic "Share on LinkedIn") code COMPLETE across backend + admin +
frontend `dev` (ledger D25). ⚠️ All three apps + docs are UNCOMMITTED working-tree changes.**
- **What:** completed the `automatic` half of the per-category social share the admin form already
  advertised. Per-category LinkedIn app creds (`linkedin_client_id`/`linkedin_client_secret`, additive
  migration `2026_07_20_000001`) → `LinkedInController` (auth-url / call-back / post, cyan's Pint/phpstan-clean
  version, v2 consumer Share surface) → 3 **public** routes → guest OAuth flow on the success page that posts
  the generated social card. ALT keeps its **blade** social card (cyan's layout-designer Tier B was out of
  scope). Best-of-both port (cyan P37.4 + hci) adapted to ALT conventions.
- **Touched:** backend `LinkedInController` + migration + `Category` + `CategoriesController`
  (`getVisibility` now returns `share_type`; `update()` + `CategoriesResources` round-trip the creds) +
  new `config('app.frontend_url')` (phpstan: no `env()` in a controller) + `routes/api.php`; admin
  `categories-form.tsx` (creds inputs when `share_type=automatic`) + `interfaces/category.tsx` + EN/AR
  `web.json` (incl. `share_manual_hint`/`share_automatic_hint`); frontend new `linkedin-redirect.tsx` +
  `success/sharebtn-sections.tsx` (automatic OAuth flow, ALT-native lucide/toast/getApiError) +
  `success-sections.tsx` + `join/[category]/success.tsx` (thread `share_type`+`category_slug`).
- **Gates:** backend `composer qa` green (pint + phpstan No errors + tests 465/3 pre-existing); admin +
  frontend `yarn type-check` + eslint green; `mobile/*` untouched. **Still open:** manual QA needs a real
  LinkedIn "Share on LinkedIn" app + `PUBLIC_FRONTEND_URL` set + a running stack. **Needs commit + push.**

**2026-07-20 — Task 010 (api.php cleanup/reorg/RESTful rename) CLOSED (ledger D24). ⚠️ Backend
`routes/api.php` + docs edits are UNCOMMITTED working-tree changes — not yet committed/pushed.**
- **Reconciliation:** Tiers 0–4 were already committed + pushed earlier (backend `4cf7036`→`c5a3a31`→
  `9328d65`→`68723ee`, admin `e36b384`, frontend `53d42e0`) and Task 011 built on top. The "uncommitted,
  pending review" notes in the old task log were **stale** — the cutover had shipped. Re-verified the
  committed baseline green: backend `composer qa` (pint + phpstan No-errors + tests 465/3 pre-existing).
- **Final leftover folded in (this session, uncommitted):** the last two non-RESTful, ungated, zero-caller
  endpoints `POST /admin/guests-upload-zip` + `POST /admin/match-guests-images` → renamed into the guests
  group as `POST /admin/guests/upload-zip` + `/match-images` behind `admin.can:guests_listing,edit`. Pure
  rename (route count stayed 384); no in-repo or mobile caller to move; controller methods unchanged.
- **Left as-is:** the four offline-sync endpoints (`attend`, `guest-data-offline`, `guest-data-sync`,
  `guests-printed-since`) stay at their `/admin/*` URIs behind `admin.can:scanning` — the deliberate Task
  011 (D23) decision, not re-litigated.
- **Gates:** backend `composer qa` green (465/3 pre-existing); dead-link grep across all repos for every old
  path = 0 code references; `mobile/*` untouched → no mobile delta. **Still open:** manual browser smoke
  test per renamed/gated feature (needs a running stack + role matrix). **Needs commit + push** (backend +
  docs).

**2026-07-19 — Task 011 (scan-into-admin) code COMPLETE on backend + admin `dev` (ledger D23). Gate
scanning is now a first-party, RBAC-gated admin feature; the standalone "agent admin" scanner is retired.**
- **What:** ported the on-site scanner into the admin dashboard (from 108/112) and wired it onto ALT's RBAC
  — no `admins.type='gate'`, no separate agent login. New **`scanning`** catalog feature (`['view']`,
  distinct from `gates`/`areas`/`scans`); the dashboard shows the scanner when
  `checkFeaturePermission('scanning', user)` is true.
- **Backend `211e17d`→`cd66c21`:** new `/admin/gate-scan` group behind `admin.can:scanning`; server-side
  **data-scope enforcement** (`GatesController::deniesGateScope()` — bound `gate_id` and/or `area_id`, super
  short-circuits); dropped `loginAgent` + route + the 4 no-`/admin` scan aliases + the dangling
  `validate-check-in` route; offline-sync endpoints kept but re-gated; `admins/select` now filters by
  `scanning`; `tests/Feature/GateScanTest.php` (happy-path, RBAC 403, area/bind scope denial, super bypass,
  recovery search+link).
- **Admin `1c87ff0`:** `components/admin-modules/dashbaord/gate-scan/*` (setup / current-gate / camera +
  hardware-wedge modes / wrong-QR recovery), wired to the renamed endpoints **through the BFF proxy**
  (HttpOnly token, no manual Bearer). Camera lib **`react-web-qr-reader` → `html5-qrcode`** (maintained,
  dynamic-imported); dropped `react-lottie` for a CSS pulse (net deps ≈ 0). Recovery now **searches by name
  and links the guest to the orphan scan** (108/112 only uploaded a photo). Re-enabled "Gates & Scans" nav,
  added `/scans` icon, removed dead `type=gate` bits. EN + AR in the same commit.
- **Lifts Task 010's RENAME_MAP §F freeze** — recorded in a new §G there.
- **Deferred / open:** the `scans.gate_id` FK (still on the `gate_name` string link); and **live browser-QA +
  the RBAC/scope manual matrix** (needs a running stack + camera) — validated so far by feature tests +
  type-check/build only.
- **Gates:** backend `composer qa` green (pint + phpstan + tests incl. `GateScanTest`); admin `yarn
  type-check` + `next build` green (`yarn production` needs the gitignored `.env.production`). **Not
  mobile-facing** (`routes/api.php` mobile surface intact). **PUSHED** — backend `origin/dev` `cd66c21`,
  admin `origin/dev` `1c87ff0`, docs `origin/main` `eafc056`.
- **Queue parked (user, 2026-07-20):** the remaining "done (code) — QA pending" items (011 live
  browser-QA, 005 HttpOnly, 006 private docs, 007 RSVP), the deferred `scans.gate_id` FK debt, task 001
  boolean-cleanup, and the mobile-ack chase are all **intentionally set aside** — user is starting a new
  type of task. Pick these back up later.

**2026-07-19 — Task 007 (API response unification) COMPLETE on backend `dev` (ledger D22). All controllers
now return the standard `ApiResponse` envelope; mobile (Tier C) deltas documented + IMPLEMENTED.**
- **What:** admin (Tier A/B) landed earlier this session; this pass finished **mobile (Tier C)** — every
  `mobile/*` controller migrated to `BaseApiController` + `apiSuccess`/`apiError` (`MobileAuth`,
  `MobileEventDay`, `MobileSpeaker`, `MobileSponsor`, `MobileAttendee`, `MobileSession`(+`Feedback`),
  `MobileWorkshop`(+`Feedback`), `MobilePublication`, `MobileMediaCenter`, `MobileQr`, `MobileRoom`,
  `MobileNotification`, `MobileChat`). Payloads now live under `data`; `success`+`status`+`message` added.
- **`AppConfigController` intentionally left unwrapped** (config documents, not resources — delta §18).
- **Mobile break is documented:** `docs/mobile/RESPONSE_SHAPE_DELTAS.md` flipped **PLANNED → IMPLEMENTED**,
  per-endpoint. This is the "adapt later" artifact — the mobile team adapts the Flutter client against it.
- **`routes/api.php` unchanged** (body refactor only). Backend feature tests updated in lockstep.
- **Gates:** pint + phpstan **No errors**; tests **457 pass / 3 fail** (the 3 are pre-existing D14
  signed-avatar/env failures, not from this work).
- ⏳ **Blocked — mobile ack:** backend `dev` → `main` now waits on the mobile team acknowledging **both** the
  D14 avatar signed-URL change **and** these D22 envelope deltas. User will bring the mobile repo into the
  parent project folder soon and update the Flutter client directly.

**2026-07-18 (session 2) — Four-step guest-draft `invitation_token` gap closed + task board tidied.**
- **invitation_token (task 008 follow-up, DONE + PUSHED):** the pif **four-step** form now forwards the
  invitation token into its OTP request, so abandoned four-step registrations capture `invitation_token`
  like one-step forms already did. Frontend `98cb380` — 2 files: `renderFormSteps.tsx` (the
  `personal-info-1` branch was the only one dropping `token`) + `pif/fours-steps/step-1.tsx` (prop +
  `formData.invitation_token`). Gates green (`type-check` + full `next build`). Closes the last known
  limitation from task 008 (D19). Backend already accepted the field — no backend/mobile change.
- **Task board:** **005** (admin HttpOnly) + **006** (private doc storage) marked **`done`** — code
  shipped + pushed on `dev`; the `dev`→`main` merge is **deferred to the user's own repo check**. ⚠️ 006
  still needs **mobile-team ack** (avatar → 24h signed URL) before that merge.
- **009 (useFetch) — ✅ CLOSED 2026-07-19 (by user).** Clean-candidate set fully converted (14/14, 19
  adopters); convention JSDoc lives atop `admin/hooks/useFetch.ts`. Further reach needs the
  `enabled`/`refetch` hook extension (its own task if/when needed); new fetch-once screens adopt it
  opportunistically. Removed from the active planning queue.
- **004** migration-squash is being **re-planned separately** (user + another agent); **001** boolean
  cleanup parked for a later check.
- ⏳ **Uncommitted (awaiting user review):** the doc updates above + the `useFetch.ts` convention note are
  edited but **not yet committed** (admin + docs repos).

**2026-07-18 — Guest-drafts feature shipped (D19). Abandoned-registration capture, ported from deve-go
`60fe949`; the admin UI existed across clones but its backend was never built. PUSHED, in-browser QA'd,
all app repos in sync. Task: `tasks/008-guest-drafts-port/TASK.md`.**
- **What:** a registrant who requests an OTP but never finishes is upserted into a new self-contained
  `guest_drafts` table (keyed by email), deleted on completion → a follow-up/drop-off list for the event
  team. Backend `7a96707`, admin `270a60d`, frontend `a8a94ec`.
- **Dedicated `guest_drafts` RBAC permission** (view/export/see_more), **route-enforced via `admin.can`** —
  grantable independently of `guests_listing` (and stricter than it — a deliberate deviation, since
  `guests_listing` routes have no `admin.can` gating). Shows as its own row in the roles editor.
- **Captures** gender/title/personal_image (frontend OTP payload now sends them), `category` (slug →
  `category_id`), and `invitation_token`; `personal_image` served as a **signed** URL (D14). Employee-ID +
  Days dropped from the see-more modal.
- **Known limitation:** the pif four-step form has no invitation-token prop → its drafts don't capture
  `invitation_token` (one-step forms do). **task 009** (useFetch adoption) remains the next parked item.

**2026-07-17 — Env templates unified (D17) + guest document/day fields completed (D18). All PUSHED; all
four repos clean and in sync with `origin`. Gates green throughout.**
- **D17 — one tracked `.env.example_prod` per app.** Backend `.env.example2`→`.env.example_prod`
  (`c7dd2ee`, `4dfdca9`); admin `.env.example`→`.env.example_prod` (`a5e83e6`→`0dcf74a`); frontend gained
  its **first** tracked template (`27bad95`, `a22bd5b`). Frontend cookie-age env vars → code constants
  (`7248f39`, `b5df5d3`, `220e65e`), parity with admin `a361586`. `CLONE_CHECKLIST` corrected (docs
  `2b118d5`). Backend env audited against Laravel 12.62 — **nothing unsupported**; it deliberately uses the
  **old** var names (`CACHE_DRIVER`/`BROADCAST_DRIVER`) because `config/` reads those — don't "modernise".
- **D18 — guest fields that had UI but no data layer.** `visa_copy`/`issued_visa`: upload 422'd
  ("failed to verify path name") and had **no column / no `$fillable` / no save** — files were silently
  dropped. Fixed `00fe02a` (allow-list + TYPES) → `4883f9d` (columns, persistence, signed `*_url`).
  `days`: a **phantom** field whose filter returned **500**; shipped the column (`ef218f6`) since only
  `98-pif-2026` had ever added it — **still has no writer** (write sites commented, no UI submits it).
  Also guarded `json_decode(null)` on `days` + `interests` (deprecation on every guest response), and
  repaired `GuestFactory` (dead `status` column) + added `CategoryFactory` (`9042919`).
- **Email:** admin-invite rebranded onto the OTP branded base template (`3e19f36`); `EmailTemplatesSeeder`
  genericised — no more TOURISE naming (`7603810`). **`EmailConfigSeeder` was checked and is clean.**
  `event_name_en` is NULL on a fresh clone **by design** — the super admin sets it after deploy.
- **Join form (frontend):** remove-photo button was an invisible X on a black circle → self-contained
  `CircleX` (`c548551`); photo-consent + app-visibility toggle hidden and `photo_consent`'s `required`
  dropped so the form still submits (`d010d3d`); terms text unlinked; visa label now says jpg/png, not PDF
  (`3c64c8a`) — the endpoint only accepts `jpeg/jpg/png`.
- **⚠️ Regression caught + fixed:** D16's sweep missed the **Blade email templates** — 22 refs, so every
  email poster rendered `nullemails-config/…` once the var was dropped. Fixed `a9a1ed4`. See the D16
  addendum.
- **Resolved (D21):** frontend GTM is kept and correctly wired — code reads `NEXT_PUBLIC_GTM`, and the var
  ships in `.env.local` + `.env.example_prod` (empty = disabled until a clone sets `GTM-XXXX`). Admin uses
  no GTM at all.

**2026-07-13 — Storage-URL env-var consolidation DONE (all 4 phases, ledger D16 + its 2026-07-17
addendum). Pushed. Plan: `upgrades/STORAGE_URL_CONSOLIDATION_PLAN.md` (status = DONE). Mobile contract
UNCHANGED (byte-identical URLs, tinker-verified) → no ack needed.**
- **Backend now keeps ZERO `PUBLIC_STORAGE_URL*` vars**, admin keeps ONE (`NEXT_PUBLIC_STORAGE_URL` =
  storage root + `utils/storage.ts`), frontend ZERO. Commits: FE `89c1ce3`; admin `b5bb5b2`→`9137fd9`→
  `fd628cd`; backend `58ca08c` (new public `social_card_image_url`) + `5cebb86` (46 `env('PUBLIC_STORAGE_URL2')`
  sites / 28 files incl. 7 mobile resources → `Storage::disk('public')->url()`; phpstan baseline pruned
  45→18 env ignores, masking nothing). Also earlier `efcc027` (dead `// 'url' =>` comment cleanup).
- **Gates:** FE+admin `type-check`+`production` green; backend `composer qa` green (pint + phpstan **No
  errors** + **452 pass/3 fail** pre-existing, confirmed identical on stashed parent) + `migrate:fresh
  --seed` clean.
- **Bugs fixed en route:** `social_card` see-more URL had a wrong path (`/social_card` vs
  `/uploads/social_card`) — now from the API; `visa_copy`/`issued_visa` confirmed dead (no column) so no URL
  added. **Deferred correctness item:** guest `custom-file-input{,-3}.tsx` still rebuild a *public* URL for
  now-*private*-disk files (the `/upload` endpoints return `data` only) — likely broken preview; fix = return
  a signed `url` from those endpoints. Tracked in the plan follow-up.
- **`.env` edits — ✅ DONE by the user (2026-07-17).** admin `.env.local` retargeted
  `NEXT_PUBLIC_STORAGE_URL` → `…/storage` and dropped `NEXT_PUBLIC_STORAGE_URL2` +
  `NEXT_PUBLIC_STORAGE_URL_ATTACHMENTS`; frontend `.env.local` dropped `NEXT_PUBLIC_STORAGE_URL`;
  backend `.env` dropped `PUBLIC_STORAGE_URL` + `PUBLIC_STORAGE_URL2`. Originals kept under `backup.env/`.
  (Any **new** clone must retarget the same way — the code appends `/uploads` to the root, so a
  `…/storage/uploads` value double-suffixes.)

**2026-07-13 — Two Tailwind v4 regression fixes (Saudi `FIX_TAILWIND_V4_REGRESSIONS.md`, ledger D15).
Committed on `dev`, gates green — NOT pushed. className-only, no logic/backend/mobile impact.**
- **Fix 1 — error focus-ring → `/50`** (v4 dropped `ring-opacity-*`): admin `5d99b43` (11 files) + frontend
  `052f16f` (5). **Fix 2 — drop `rtl:space-x-reverse`** (v4 `space-x-*` is now RTL-aware → the class
  double-flips): admin `aadadf8` (124 occ/69 files) + frontend `721d458` (25 occ/9). Four separate commits.
- **Gates:** `type-check` + `production` green on both apps. **Visual EN/AR QA pending** (soft red ring on
  invalid inputs; RTL spacing on checkboxes/radios/back+share buttons/toolbars).
- Note: an early scripted Fix-2 attempt corrupted indentation (global whitespace collapse); fully reverted
  and redone surgically. Final diffs are proportionate (one line per token).

**2026-07-12 — Private document storage + signed URLs (Saudi P1 backport, task 006, ledger D14). Code
DONE on backend `dev`, gates green, runtime-verified — NOT yet committed/pushed (working tree). MOBILE
CONTRACT CHANGE — hold `dev`→`main` until mobile acks. Plan: `CLEANUP_AND_HARDENING_MASTER_PLAN.md` Task
005 (Track B); log: `tasks/006-private-document-storage/TASK.md` (folder 006).**
- **What & why:** registrant PII (`guests.personal_image` photos + `document_copy` passport/ID) was on
  the **public** disk at raw unauthenticated CDN URLs — anyone with the URL fetched a passport. Now on a
  **`private`** disk (`storage/app/private`, never web-served), served only via short-lived **signed
  URLs** (`GuestDocumentController` + `signed`-middleware route `GET /api/files/guest-doc/{type}/{file}`).
  Un-deferred pre-launch (no clone has prod data).
- **Landed (backend, 13 files + 2 new):** private disk; serving controller (signedUrl + stream w/
  basename traversal guard, allow-list, no-store); writes repointed incl. **mobile avatar upload**
  (`MobileAuthController`); admin resource URLs → 30m signed, **mobile `avatar` → 24h signed**; **16
  server-side read-backs** (badges/PDF/social-card/email-photo, 7 files) → `disk('private')->path()`;
  idempotent `guests:migrate-docs-to-private --dry-run` command; 2 stale phpstan-baseline env ignores removed.
- **Gates:** `composer qa` green (pint + phpstan No-errors + tests **452/3 pre-existing** — the 2 avatar
  failures confirmed to fail on the clean parent too → no regression); `migrate:fresh --seed` clean.
  **Runtime verified:** private file streams **200** on valid signature, **403** on tamper/no-sig, **404**
  on traversal, **404** at the old public `/storage` path.
- **MOBILE CONTRACT:** `avatar` is now a signed 24h-expiring URL (same field/type; mobile must re-fetch
  after expiry, not build the URL). Flagged in `docs/mobile/MOBILE_NOTICE_PRIVATE_AVATAR_SIGNED_URL.md`.
- **Outstanding:** commit + **mobile team ack** + real-env QA (admin preview render, heavy export/PDF/email
  photo) before `dev`→`main`. NOTE: the plan's bundled UploadService extraction (Todo-2D) was NOT done.

**2026-07-12 — Fixed `migrate:fresh --seed` (TitleSeeder null bug, ledger D13). Backend `dev` `a6fe3d1`,
pushed.** 6 `TitleSeeder` rows passed `show_in_user_form => null` into a NOT-NULL `boolean default(false)`
column → `SQLSTATE[23000]` crash mid-seed. Fixed the **seeder** (`null` → `false`; `null` meant "not
shown"), not the schema. This was the pre-existing bug the dropped migration-squash recon flagged. Verified:
full `migrate:fresh --seed` clean, 8 seeders green, 12 titles (6 shown / 6 hidden), Pint + Title tests pass.
Not mobile-facing.

**2026-07-12 — Admin HttpOnly token + Next BFF proxy + full CSP (Saudi P2 backport, task 005, ledger
D12). Code DONE, gates green, runtime-verified — committed + pushed (admin `dev` 4 commits
`d95a2e5`→`b006123`; docs `main` `2939d0b`). Real-env browser QA still outstanding before `dev`→`main`.
Plan: `upgrades/cleanup-hardening/CLEANUP_AND_HARDENING_MASTER_PLAN.md` Task 004 (Track B); log:
`tasks/005-admin-httponly-token/TASK.md` (folder 005 — 004 is the dropped squash).**
- **What & why:** the admin bearer was a JS-readable cookie (XSS → account takeover). The Phase-1 fix
  (`af2298b`, secure+sameSite) couldn't close the XSS-read vector — only `httpOnly` can, and only a server
  can set it. So the token now lives ONLY in an **HttpOnly cookie** written by a **Next BFF proxy**; the
  browser never handles it. Un-deferred from Track B now because the basecode is **pre-launch (no clone has
  prod data)**, so the 135-file codemod is cheap to bake into every clone.
- **Landed (admin only, 144 files, net −399 lines):** new `utils/{auth-cookies,server/proxy}.ts` +
  `pages/api/{proxy/[...path],auth/{login,login-confirmation,logout}}.ts`; isomorphic `utils/axios.ts`
  (browser→`/api/proxy`, SSR→direct); provider/withAuth/login+verify onto a JS-readable flag cookie
  (`alt_admin_auth`) + `authenticated` marker; codemod removing 136 dead `cookie.get('token')` reads + 261
  `Authorization: Bearer` headers (proxy injects auth server-side now); **full CSP** in `next.config.js`
  adapted to alt (env origins, reCAPTCHA only, **no iconify** per D5, `'unsafe-eval'` dev-only).
- **Gates:** `yarn type-check` + `yarn production` **green**. **Runtime verified** against a stub upstream
  on `next dev`: login strips token + sets `HttpOnly; SameSite=Strict; Max-Age=6h` cookie, proxy injects
  `Bearer` from the cookie, logout clears both, OTP + multipart streaming + CSP header all confirmed.
- **Mobile:** untouched — admin-web only, `routes/api.php` unchanged.
- **Outstanding:** commit (4 commits) + **real-env browser QA** (live backend login, reCAPTCHA, heaviest
  export/upload through the proxy) before `dev`→`main`. Saudi hotfix-reverted their P2 once over these edges.

**2026-07-11 → 07-12 — Env-var / dead-code cleanup pass (admin + frontend). Committed on `dev`.
Frontend is pushed and in sync with `origin/dev` (`64037eb`). Admin `dev` is 4 ahead of `origin/dev`
(NOT yet pushed) — `f6bcf7b` → `a361586` → `37cf1a1` → `8345f19`.**
- **Admin (4 unpushed commits):** retired baseline env vars that were config-noise, moving the values
  to code constants. `f6bcf7b` drop `NEXT_PUBLIC_LISTING_PER_PAGE_LIMIT` from listing URLs
  (`utils/fetch-data-url.ts`, print-logs). `a361586` move cookie-age env vars → code constants
  (`auth/provider.tsx`, `i18n/provider.tsx`). `37cf1a1` retire `NEXT_PUBLIC_ENV` from 9 `data/*-select.tsx`
  files (incl. `status-types-select`, `sidebar-links`). `8345f19` remove unused `callback_url` /
  `back_link` from `guests` step-4 + `verify-email-form`. Pure config/dead-code hygiene, no behaviour
  change.
- **Frontend (pushed, `dev` @ `64037eb`):** `9a9a850` + `dedb4f6` clean up `utils/axios.ts` (drop unused
  token header/variable). `e75c9bf` remove `@vercel/analytics` dep + imports (`package.json`, `_app.tsx`,
  `yarn.lock`). `64037eb` untrack `.env.production` + add to `.gitignore`.
- **Gates:** admin `yarn type-check` **clean** + `yarn production` **green** (verified 2026-07-12).
  Not mobile-facing (`routes/api.php` untouched). **Admin still needs its 4 commits pushed to `origin/dev`.**

**2026-07-08 — Backend tooling & code-quality chain (task 003, ledger D10). All work items DONE;
committed on `dev` — backend `96413df` (W1, already pushed) + `bb61db9` (W2+W6) + `9741e90` (W5+W8)
+ `de75eed` (W7); docs on `main`. Backend `dev` is 4 ahead of `origin/dev` (W1 pushed earlier). Plan:
`upgrades/BACKEND_TOOLING_CHAIN_PLAN.md`; log: `tasks/003-backend-tooling-chain/TASK.md`.**
- **What landed:** brings the backend's quality chain to parity with the Next-app pass. **W1** —
  `pint.json` (laravel preset + `no_unused_imports` + `ordered_imports`) + one repo-wide Pint baseline
  (172 files, formatting-only) → repo is now **Pint-clean**, gate flips `pint --dirty` → **`pint --test`**.
  **W2** — **Larastan** static analysis at **level 0** + generated baseline (124 real structural
  errors), with a committed **ratchet** (shrink → bump the level toward 6; runs in `composer analyse`/
  `qa`, never the hook). Fixed 1 non-ignorable finding at source (`GuestOtpNotification::$locale`
  redeclared a native type over Laravel's untyped parent). **W6** — composer scripts `lint`/`lint:fix`/
  `analyse`/`test`/`qa` (one-command gate). **W5** — PHP-native `.githooks/pre-commit` runs Pint on
  staged `*.php` + graceful-skips if Pint absent (parity with admin/FE husky+lint-staged), auto-installed
  via `composer install`. **W7** — `.vscode/` **un-ignored + committed** with `[php]`→Pint (fixed an
  inconsistency: admin/FE tracked `.vscode/`, backend gitignored it). **W8** — dropped stale
  `pestphp/pest-plugin` allow-plugin; `composer validate --strict` valid; audit clean. **Rector + CI
  left out** (out of scope). Not mobile-facing (`routes/api.php` untouched).
- **Gates:** `composer qa` = `pint --test` green + `phpstan analyse` **No errors** (baseline-green) +
  `php artisan test` **452 pass / 3 fail** (pre-existing, unrelated). **New backend gate going forward
  is `composer qa`.**

**2026-07-07 (later) — `catch (e: any)` → `unknown` cleanup, closing the "cheap cleanups" phase
(ledger D9). Committed on `dev` (admin `5ceacc3`, frontend `8544c39`) — NOT yet pushed (part of the
same review batch as task 002). All original audit sub-phases ("fix first", "cheap cleanups") are now
complete; "later/opportunistic" is parked — see `tasks/PHASE3_PARKED_TODO.md`.**
- **What landed:** 94 `catch (error: any)` blocks across 82 files (68 admin + 14 frontend) → `catch
  (error: unknown)`. New shared helper `utils/api-error.ts` (`getApiError(unknown) → typed axios
  `ApiErrorResponse | undefined`) in both apps; response-reading catch bodies route through it, log-only
  bodies just re-annotate to `unknown`. Behaviour unchanged (same branches/toasts/status checks). Casts
  added only where an untyped value flows into a typed sink (RHF `setError`, `toast.error`). Gates green:
  `type-check` + lint 0 warnings, both apps. Not mobile-facing.
- **Also this session:** verified the other three "cheap cleanups" items were already done by a prior
  agent (iconify→lucide, 28+2 dead files deleted, commented-`// console.*` swept) — all confirmed clean
  against current code. Wrote **`docs/mobile/MOBILE_NOTICE_AGENDA_DATE_WALL_CLOCK.md`** — an actionable
  notice for the mobile team about the D8 venue-local `date` change (must not TZ-convert agenda `date`).

**2026-07-07 — Date/time (timestamp) DB cleanup + refactor (ledger D7, task 002). Committed on `dev`
(backend `86961dd`, admin `c6ee625` + follow-up `f340a0e`, frontend `5f2c55a`) and `main` (docs
`aeb4528` + `155d94b`) — NOT yet pushed (awaiting review). Full plan + per-step log:
`tasks/002-datetime-db-cleanup/TASK.md`.**
- **Display consistency pass (admin, `f340a0e`):** 34 views switched from `format(new Date(x))`
  (viewer's browser TZ) → shared `formatDateTime` (`Asia/Riyadh`) for real UTC Laravel timestamps
  (listing `created_at`, `registered_at`, session media `created_at`, guest-draft
  `created_at`/`updated_at`). Export-filename timestamps left on `format()`.
- **Agenda-date fix (ledger D8, MOBILE CONTRACT CHANGE):** session/workshop `date` was served as UTC
  `…Z` but entered as naive `datetime-local`, so the admin edit form pre-fill shifted the time −3h on
  every save. Switched all 9 `date` serializations (admin + mobile resources) from `->toISOString()`
  to naive-local `->format('Y-m-d\TH:i:s')` (venue = Asia/Riyadh). No FE logic change (pre-fill +
  `format(new Date())` display self-correct with a `Z`-less string). **Mobile must parse `date` as
  wall-clock, NOT convert to device TZ** — flagged in `docs/mobile/…FOR_MOBILE.html` §24. Backend
  `pint --dirty --test` green.
- **Backend:** date-only columns → real `date` (cast `date:Y-m-d`), datetime columns → `timestamp`
  (cast `datetime`, ISO 8601 UTC), flight times → `string(5)` `HH:mm`. Migrations edited in place +
  `migrate:fresh` (no prod data). Touched `guests` (+ `add_check_in_out_dates`), `invitation_emails`,
  `guest_emails`, `guest_sms`, `automations`, `bulk_prints`, `badge_print_logs`, `history_logs`;
  added casts to Guest/InvitationEmail/GuestEmail/BulkPrint/Automation/HistoryLog; printed-range
  query → `whereBetween` w/ Carbon; 3 `GuestsExport*` binders now format Carbon values; removed 4 dead
  unrouted debug methods from `OperationActionsController` (+ their commented routes).
- **FE + admin:** dropped the react-day-picker modal for cyan's **Cleave masked inputs**. Added
  `cleave.js` + `@types/cleave.js`, `components/shared/forms/masked-date-input.tsx` +
  `masked-time-input.tsx`, and shared `utils/date.ts` (`formatDate` / `formatDateTime`). Every
  `CustomDayInput` site → `MaskedDateInput` (`YYYY-MM-DD`); flight times → `MaskedTimeInput` (`HH:mm`,
  fixes the admin field that still emitted `hh:mm AM`); all active `timeZoneFix()` display → the new
  helpers. TZ conversion happens **at display** (`Asia/Riyadh`) so out-of-KSA users are correct.
  `masked-datetime-input.tsx` deleted (no user-entered datetime in alt). **Kept** `custom-day-input.tsx`
  (unused, for future) + therefore **kept** `timezoneFix.ts` (its only remaining consumer) — a
  deliberate revision of the "delete timezoneFix" plan.
- **Gates:** backend `pint --dirty --test` green, `migrate:fresh` clean, `php artisan test` 452 pass /
  3 fail (same pre-existing ExampleTest 403 + 2 avatar failures — unrelated). Admin + frontend
  `type-check` + `production` **green**. Mobile contract unaffected (guest dates only in Admin
  resources; offline QR `check_in_time` round-trips via the `datetime` cast; `routes/api.php`
  unchanged). No i18n keys moved.

**2026-07-06 (night) — Boolean DB cleanup + refactor, two tracks (ledger D6). Working-tree only on
`dev` across all three app repos — NOT yet committed/pushed (awaiting review). Full plan +
per-step log: `tasks/001-boolean-db-cleanup/TASK.md` + `upgrades/cleanup-hardening/BOOLEAN_REFACTOR_PLAN.md`.**
- **Track A** (mirrors cyan's documented refactor): pseudo-booleans (`yes`/`null`, `yes`/`no`,
  `with_`/`is_`) → real `boolean`s. Migrations edited in place (`string(...)->nullable()` →
  `boolean()->default(false)`) across guests flags, categories (`with_*` + notification fields),
  badges, email configs/templates, automation setups, countries, titles, invitations, guest
  logistics, gates, guest_sms; model `$casts` added; controllers/resources/blade `=== 'yes'` →
  `$request->boolean()` / `=== true`; admin `CustomSwitchInput` → `CustomSwitchInputBoolean` +
  boolean interfaces; frontend join-form radios (`is_saudi`, `require_*`, `valid_visa`) → booleans,
  SSR `=== 'yes'` boundary drop. **Intentional string keeps** (cyan-aligned): CSV `Exports` yes/no,
  input normalization, and the 3-state consent fields `display_photo_in_app` / `photo_consent` /
  `will_attend` / `terms`.
- **Track B** (net-new, beyond cyan): entity `status` (`active`/`blocked`) → `is_active boolean
  default(true)` on ~16 tables (speakers, sponsors, speaker/sponsor labels, zones, areas, gates,
  badges, categories, titles, admins, sms/email templates, invitations, guest_statuses, countries);
  `$casts`/`$fillable`; ~18 controllers `where('status','active')` → `where('is_active',true)` +
  `block()`/`activate()` setters (route names preserved); `Mobile{Speaker,Sponsor}Controller`
  filters; notification senders. Admin: shared `Status` badge → `isActive:boolean`,
  `status-types-select` → `true`/`false` options, all entity listings (`FilterFieldDef key:'is_active'`
  → serializes to `?is_active=`), 8 status forms, `bulk-update-badges-modal`, ~12 interfaces.
- **Excluded (multi-value / process statuses):** `app_notifications`, `login_attempts`,
  `email_attachments`, sms send-state, guest-workflow `status`/`guest_status_id`, mobile guest
  status, `users` (dead `UsersController`), automation `is_sent/is_delivered/is_open/is_clicked`.
  `meeting_rooms` + `smtp_configs` were already boolean `is_active` by design (no change needed).
- **Gates:** backend `pint --dirty` green, `migrate:fresh` clean, `php artisan test` **452 pass /
  3 fail** — all 3 are **pre-existing, unrelated** (confirmed by re-running on a stashed clean tree):
  `ExampleTest` GET `/` → 403, and two avatar tests that assume `display_photo_in_app` defaults to
  `'yes'` (it's nullable, intentionally left a string). Admin + frontend `type-check` + `production`
  **green**. **Mobile contract unchanged** — storage/internal only; no converted-entity `status`
  is exposed in any mobile resource.

**2026-07-06 (late pm, 2) — "Cheap cleanups" pass (admin + frontend), two separate commits each.
(1) Deleted dead files: 28 unreferenced `interfaces/*.tsx` in admin (`f6cffae`) + 2 stale duplicate
copies in frontend (`i18n/link copy.tsx`, `data/area-of-interset-generic-select_.tsx`, `864f7df`).
(2) Removed commented-out `// console.*` debug lines: 115 across 43 admin files (`f66ede8`) + 33 across
11 frontend files (`88ac243`). Pure hygiene, zero behaviour change; all four gates green. Both `dev`
branches pushed. The `zod`-removal and `@iconify/react`-dep items from that phase are moot (zod is
load-bearing; iconify already removed by the lucide migration).**

**2026-07-06 (late pm, 1) — Icon-library unification complete. Both Next apps now use a single icon
library, `lucide-react`; `@iconify/react` (P1) and `@heroicons/react` (P2) are fully removed from
source + `package.json` + `yarn.lock`. All four gates green (`type-check` + `production` on admin &
frontend). See ledger D5.**

**Earlier 2026-07-06 (pm):** Forgot-password unified onto the invite reset-by-token flow (admin +
backend). The whole tooling/hygiene batch + admin email-invite flow is now merged to `main` via PR #1 on
all three app repos. The backend has adopted a `dev` branch — it no longer commits straight to `main`
(see ledger D4).

**Earlier this session (am):** tooling + hygiene pass across the two Next apps (ESLint 9 flat config,
Prettier 3, zero lint warnings, husky + lint-staged, GTM removed) + dead-dependency / dead-code cleanup
+ docs cleanup (dropped the `-landing` app). `origin` is set on all repos
(`github.com/eissa-alt/alt-static-basecode-*`) and each branch tracks + matches its upstream.

## SHAs as of 2026-07-06 — HISTORICAL, do not read as current

> ⚠️ This snapshot is 102 backend commits stale (`4e1d532` was HEAD on 2026-07-06). It is kept as a
> record of that session, not as the current state — see the dated entries at the top of this file.
> Everything below this line is likewise historical: statements about gates, versions and outstanding
> work were true when written and have not been rewritten.

- `alt-backend` — `dev` = `main` @ `4e1d532` (PR #1 merge). Forgot-password backend at `a8184ca`; admin
  email-invite / `password_mode` **backend** flow at `04001b3` (P2.ST8). **Backend uses `dev`** and PRs
  into `main`, matching admin/frontend. Untouched by the icon migration.
- `alt-admin` — `dev` @ `f66ede8` (**cheap cleanups**, pushed): console-sweep `f66ede8` + dead-file
  delete `f6cffae`, on top of icon P2 `de87b4b` / P1 `d2565d9`. Before that `main`=`ed2e679` (PR #1
  merge), forgot-password repoint `70e646c`, tooling pass `29548e3`, admin-invite **UI** `d3ed5db` /
  `f43543f`. **`dev` is now well ahead of `main`** (icon migration + cleanups all `dev`-only).
- `alt-frontend` — `dev` @ `88ac243` (**cheap cleanups**, pushed): console-sweep `88ac243` + dead-file
  delete `864f7df`, on top of icon P2 `c74b82c` / P1 `3033a18`. Before that `main`=`f6b61e8` (PR #1
  merge), tooling pass `41ae698` + form-shape `default-` prefix rename + a `react-select` → Headless UI
  Listbox select refactor. **`dev` is now well ahead of `main`.**
- `docs` (on `main`) — this handoff refresh + ledger **D5** (previously `37176b7`: stale stack-version
  fix; earlier D3/D4, `-landing` drop / **D2**, husky hook).

## What landed recently

- **"Cheap cleanups" pass** (admin + frontend, hygiene, two commits each): **(1) dead-file deletion** —
  28 unreferenced `interfaces/*.tsx` in admin (`f6cffae`) + 2 stale duplicate copies in frontend
  (`864f7df`); **(2) commented-`console.*` sweep** — 115 lines / 43 files in admin (`f66ede8`) + 33
  lines / 11 files in frontend (`88ac243`). Full-line comment removals only (verified no inline/multiline
  cases); complements the earlier no-console rule (which handled live calls). Zero behaviour change, gates
  green. The other two items from that phase are moot: **`zod`** stays (load-bearing runtime peer dep of
  the email-template editor — removing it crashes the editor); **`@iconify/react`** was already dropped by
  the lucide migration.
- **Icon-library unification → `lucide-react`** (admin + frontend, ledger **D5**): dropped **both**
  baseline icon libs. **P1** removed `@iconify/react` (admin `d2565d9` — 146 conversions / 40 files +
  the event-day DB registry; frontend `3033a18` — 5 files incl. the `bi:tiktok` inline-SVG replacement).
  **P2** removed `@heroicons/react` (admin `de87b4b` — 82 files; frontend `c74b82c` — 13 files) and
  stripped it from `package.json` + `yarn.lock`. Machine-verified 1-for-1 name map (e.g.
  `ArrowTopRightOnSquareIcon`→`ExternalLink`, `PencilSquareIcon`→`SquarePen`, `PaperAirplaneIcon`→`Send`,
  `TrashIcon`→`Trash2`, `DocumentDuplicateIcon`→`Copy`); `className` sizing preserved throughout. Gates
  green both apps; **admin `production` build now run (was outstanding)**. Not mobile-facing.
- **Forgot-password → reset-by-token unification** (admin + backend): new
  `AuthController::forgotPassword()` reuses the `AdminInvite` token machinery + shared `admin_invite`
  blade (EN/AR) behind a public `POST /admin/forgot-password` route; the admin `forgot-password-form`
  now posts `{ email, back_link }` there instead of the legacy `v2/password/forgot` guest flow, so admins
  land on the same `reset-password/[token]` page as invites. **Enumeration-safe** (always returns success
  — a deliberate deviation from cyan). Cyan parity, see **LEDGER D3**. Mobile contract unaffected
  (admin-only, additive route).
- **ESLint 9 flat-config migration** (admin + frontend) + `@next/eslint-plugin-next`; **Prettier 2 → 3**;
  all lint warnings → **0** (autofix, optional catch binding + config `ignoreRestSiblings` /
  `argsIgnorePattern`, scoped `exhaustive-deps` / `<img>` disables each with a `-- reason`).
- **husky + lint-staged pre-commit hook** (admin + frontend): staged `*.{js,jsx,ts,tsx}` → `eslint --fix`,
  other types → `prettier --write`, re-staged. Installed via `prepare: husky`. Verified end-to-end.
- **GTM removed** from both apps (`react-gtm-module` + dead `utils/analytics.ts`).
- **Dead-dependency / dead-code cleanup**: removed `@svgr/webpack` (+ dead icon assets), `swiper`
  (frontend), `filepond-plugin-image-transform`, and many orphaned components/modals; admin swapped its
  legacy Portal modal for a shared `DialogShell`; frontend replaced `react-select` with a Headless UI
  Listbox `ui-select`. **This supersedes the KEEP verdicts in `upgrades/DEPENDENCY_AUDIT.md`** for
  `@svgr/webpack` / `swiper` (see the dated addendum there).
- **Editor settings**: Tailwind `suggestCanonicalClasses` silenced; deprecated `typescript.tsdk` /
  `enablePromptUseWorkspaceTsdk` → `js/ts.tsdk.path` / `js/ts.tsdk.promptToUseWorkspaceVersion`.
- **Docs**: dropped the 4th `-landing` app from all current-state docs (now a **three sub-app** baseline:
  `-backend`, `-admin`, `-frontend` + `docs/`); documented the pre-commit hook; ledger **D2**. Historical
  `upgrades/*` and D1's clone-source SHAs left intact (accurate record).
- **Admin email-invite / `password_mode` flow — merged + pushed** (backend `04001b3`, admin `d3ed5db` +
  `f43543f`): `AdminInvite` model + `admin_invites` / `password_mode` migrations, invite/resend/reset
  endpoints, SMTP-gated password-mode UI + reset-by-token page.

## Gates

- **Admin / Frontend:** `yarn type-check` + `yarn production` **green**; ESLint **0 warnings**. The
  pre-commit hook enforces Prettier/ESLint autofix on every commit.
- **Backend:** `pint --dirty --test` **green** on the forgot-password change. Run `php artisan test`
  before the next backend push. (Repo wasn't Pint-clean at baseline then — the advice at the time was
  `pint --dirty`. **Superseded:** ledger D10 made the repo Pint-clean and the gate is now the full
  `pint --test`; see CLAUDE.md hard rule 5.)
- **SMTP smoke test: DONE** — invite + reset-password email delivery verified against the active DB SMTP
  config (`DynamicSmtpService`).

## Next / outstanding

> Refreshed 2026-07-17. **Everything is pushed — all four repos are clean and in sync with `origin`.**
> Any "NOT pushed / not yet committed" wording in the dated entries above is point-in-time history, not
> current state.

- **Blocked — mobile ack:** backend `dev` → `main` is held until the mobile team acknowledges **both**:
  (1) the **D14** contract change (`avatar` is now a signed, 24h-expiring URL — mobile must re-fetch, not
  rebuild it; notice `docs/mobile/MOBILE_NOTICE_PRIVATE_AVATAR_SIGNED_URL.md`), and (2) the **D22** Task 007
  envelope deltas (every `mobile/*` payload now under `data`; `docs/mobile/RESPONSE_SHAPE_DELTAS.md`,
  IMPLEMENTED). User will bring the mobile repo into the parent folder and update the Flutter client directly.
- **Browser QA — visa upload (new):** `visa_copy`/`issued_visa` now persist end-to-end (D18) but have only
  been verified via tinker + signed-URL checks. Worth a real run: DB + local storage were wiped clean on
  07-16, so it's a clean slate.
- **`days` column removed (D20):** the phantom `guests.days` (no writer, read-only consumers, dead in the
  `122-gfeai-v2` clone too — superseded there by `forum_days`) was dropped fully across all three repos.
  Supersedes D18's ship-it call.
- **GTM decided (D21):** kept in **frontend** (`_app`/`_document` read `NEXT_PUBLIC_GTM`; the var ships in
  `.env.local` + `.env.example_prod`, empty = disabled until a clone sets `GTM-XXXX`). **Not in admin** —
  no code, no env var; nothing to remove.
- **Task 010 — api.php cleanup, reorg & RESTful rename (NEW, todo):** our `routes/api.php` is 966 lines of
  mostly-flat, ungated, non-RESTful legacy admin routes vs cyan's 559-line grouped + `admin.can:`-gated +
  `whereUuid` + RESTful shape. Tiered plan: cleanup → dead-code → reorg+**RESTful rename**+`whereUuid`
  (backend) → **cross-repo lockstep** (admin+frontend+mobile-if-touched) → RBAC gating. Scope now includes
  renaming as a **hard cutover** (reverses the initial "URIs frozen" call) and replacing `block`/`activate`
  with `toggle-status`. `admin.can`/`EnsureAdminPermission` confirmed present. `mobile/*` stays RESTful,
  only touched deliberately + documented. See `tasks/010-api-routes-cleanup/TASK.md`.
- **Browser QA** — forgot-password + invite create paths + reset-by-token page; plus the migrated
  listings + sidebar accordion (LTR/RTL) from the earlier P5.trim / cyan-parity session, which compiled
  green but were never browser-tested. **Add a visual pass on the migrated icons** (both apps) — the
  swaps compiled + built green but weren't eyeballed for glyph/size parity.
- **Merge `dev` → `main`** on admin + frontend when ready — the icon migration (P1+P2) **and** the cheap
  cleanups currently live only on `dev`; `main` is still at the PR #1 merge. (User asked to leave the PRs
  for now.)
- **`catch (X: any)` → `unknown`** — ✅ **DONE** (ledger D9, admin `5ceacc3` / frontend `8544c39`, on
  `dev`). Closed the "cheap cleanups" phase.
- **Phase 3 (later/opportunistic) — ✅ CLOSED 2026-07-19** (re-checked against code): `cont-list.ts`
  drift reconciled (now byte-identical admin↔frontend), `xlsx` now `await import()`, chart.js widgets all
  `next/dynamic({ ssr:false })` + `ChartCanvas` runtime-imports `chart.js/auto`, and `useFetch` adoption
  promoted to task 009 (closed). Only the *optional* drift-check script remains unbuilt. See
  `tasks/PHASE3_PARKED_TODO.md`.
- **Mobile team notice** — `docs/mobile/MOBILE_NOTICE_AGENDA_DATE_WALL_CLOCK.md` written; the mobile team
  still needs to be actually told + confirm receipt before the D8 change releases.

> Pint note (updated 2026-07-08, ledger **D10**): the backend is now **Pint-clean** (task 003 added
> `pint.json` + a repo-wide baseline, `96413df`). The gate is the **full `pint --test`** (`composer
> lint`), no longer the old `pint --dirty` workaround. Full backend gate = **`composer qa`** (`pint
> --test` + `phpstan analyse` + `php artisan test`). A `.githooks/pre-commit` hook also runs Pint on
> staged PHP (installed via `composer install`).
