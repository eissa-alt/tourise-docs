# Task 039 — The dignitary invites their own party

- **Status:** `done (code)` — pushed to `dev` 2026-09-21; dev `migrate`, choosing the invitation email, and a real submit on dev pending
- **Opened:** 2026-09-21
- **Owner:** —
- **Sub-app(s):** backend + admin + frontend
- **Branch(es):** `dev`

## Goal

A dignitary's delegation, security and protocol register themselves — frontend `a4f4f88`
(2026-09-09) dropped the dignitary's "+ Add Guest" rows for the confirmed master's three sheets.
Each one named their dignitary by a **name and registration code they typed** — one wrong character
and the record belonged to nobody, and the team had no list of who travels with whom.

Now **H.E. names the people travelling with him on his own form, and each receives a personal
invitation already tied to him.** Nobody types his name or code, and nobody on the team makes or
forwards a link.

## How it works

1. **H.E.'s form** has *Your Delegation, Security & Protocol*: group, email, first and last name per
   person, **+ Add person** (up to 30). Optional. Checked as he types (valid email, not his own, not
   twice) and confirmed on his review step. Sent as `party_invites`.
2. **When he submits,** each person gets a personal **single-use** invitation in their group's
   category — a normal invitation link — carrying `invitations.dignitary_guest_id`, pre-filled with
   the name and email he gave, in his language, and emailed at once.
3. **Their form opens filled in** (name, email; still editable) and shows H.E.'s name and
   registration code **read-only** instead of asking for them.
4. **Registering** — or declining — through it records the dignitary from the invitation. They get
   the group's on-register status (**Invited**, per the seeder).
5. **Admin → Dignitary Parties** (`/dignitary-parties`, sidebar under Guests): each dignitary with,
   per group, who registered and who is invited but not registered yet — with the email's state
   (sent / sending / not sent) and **Send / Resend**. **Invite someone** sends the same invitation
   for anyone H.E. left out. **Invitation email** chooses the template for all three groups.
6. **Guests** shows *Invited by H.E. …* under a party member's category; **See more** links to the
   party from both ends.

## Decisions

- **The invitation carries the dignitary.** `invitations.dignitary_guest_id` (nullable,
  `nullOnDelete` — a deleted dignitary leaves an ordinary invitation, never a broken one). →
  ledger **D49**.
- **Personal invitations, not shared links.** The first cut gave each dignitary one multi-use link
  per group that the team created on the admin page and forwarded. The owner rejected it (2026-09-21:
  "I don't want to create a link and send it … the dignitary adds his guests, they receive an
  invitation linked to his name"). Do not bring shared links back.
- **Not `primary_guest_id`.** That is the +1 / extra-guest relation; reusing it would make every
  delegate count as the dignitary's plus-one in exports, badges and the dashboard's companion filter.
- **The server decides who the dignitary is.** Public store overrides `accompanying_dignitary_name` +
  `dignitary_registration_code` from the invitation, whatever the form sends. The form's read-only
  block is presentation; the override is the guarantee.
- **Sent the moment the dignitary submits** (owner, 2026-09-21). The dignitary category is private —
  H.E. is invited, not pending approval — so there is nothing to wait for.
- **Pre-filled, not locked** (owner: "same invitation but prefilled"). `prefilldata = true`,
  `lock_data = false`: names H.E. types for someone else are where typos live.
- **One email for all three groups**, stored on the three `dignitary_party` collections. Invitations
  made before one is chosen are created unsent and take it at send time; the page shows a notice
  until it is chosen. New variable **`{{ dignitary_name }}`** (party invitation → the dignitary;
  an accompanying guest's own emails → their `accompanying_dignitary_name`).
- **A failed invitation never undoes the dignitary's registration.** Rows are validated *before*
  anything is saved (a malformed row fails the submit with 422); sending happens after, per person,
  logged on failure.
- **Already-registered emails are skipped** on the form path and **refused with a message** on the
  admin path; naming the same person twice reuses the unused invitation.
- **The list matches people two ways:** through the dignitary's invitation (`code_id`), or — for
  anyone registered before this — by the code they typed (`dignitary_registration_code =
  registration_number`), marked *matched by the code they typed*.
- **Permissions reuse the catalogue** — no new feature: view `guests_listing`; invite / send
  `invitations.create`; choose the email `invitations.update`. The admin's category/status scope
  applies through **`GuestAccessScope::apply()`**, the query twin of `denies()`. ⚠️ That rule now
  lives in **three** places (`GuestsController::applyAdminGuestAccessFilter`, `DashboardStatsController`,
  `GuestAccessScope`) — change all three together.
- **The registration-code field survives only for an invitation tied to no dignitary** (e.g. one made
  by hand on the Invitations screen). Through the dignitary's invitations it is never asked.
- **Sidebar:** *Invitation Requests* is its own item beside *Invitations*, no longer a submenu
  (owner); both, and *Dignitary Parties*, sit in Overview.

## Log

- 2026-09-21 — backend `ea4844b` — migration `2026_09_21_000002`, `App\Services\DignitaryParty`,
  `party_invites` on the public store, `invited_by` on verify-invitation, `{{ dignitary_name }}`,
  `/admin/dignitary-parties` (+ `settings`, `{guest}/invite`, `invitations/{invitation}/send`),
  `GuestAccessScope::apply()`. `DignitaryPartiesTest` (16 cases). Backend tests → **834**.
- 2026-09-21 — admin `35b260e` — Dignitary Parties page, invite / email modals, *Invited by* in
  Guests + See more, email-editor variable, *From dignitary parties* source filter, flat sidebar.
- 2026-09-21 — frontend `fa457c7` — the party section on the dignitary form; the linked, pre-filled
  form for a party invitation.
- 2026-09-21 — admin `1d3adcd` — the *Invite someone* dialog's group field showed
  "Missing translation for 'web:party_group'": the key existed only in the public site's
  translations. Scanned both apps afterwards — every static id resolves in EN + AR.
- All pushed to `dev`. Verified locally with Playwright on each screen; the dignitary's own submit
  could not be driven in a browser locally (reCAPTCHA) and is covered over HTTP by the tests.
- Flow walkthrough with screenshots, for the team: https://claude.ai/artifact/PSJaN91D7zzhWcoR1tQcLm

## Open

- **Dev `php artisan migrate`** — until `invitations.dignitary_guest_id` exists, a dignitary's own
  registration still saves but every party invitation fails (logged, not sent), and Dignitary
  Parties errors.
- **Choose the invitation email** on Dignitary Parties, on dev and on production. Until then
  invitations are created but not emailed.
- **One real submit on dev**, end to end: dignitary with two people → both emails arrive → one
  registers → shows under the dignitary.
- The dignitary categories' Reply-To is `protocol@tourise.com` (Task 036) — replies to a party
  invitation go there.
- **Not covered:** the admin's own *create/edit guest* form for a dignitary has no party section (use
  *Invite someone*); a registration re-opened through the complete-data link does not send
  invitations (the section is hidden there).

## Definition of Done

- [x] Code merged to `dev` in the relevant sub-app(s)
- [x] EN + AR translations in the same commit (the admin's two missed keys followed in `1d3adcd`)
- [x] Quality gate green (backend `pint --test` + `php artisan test`; admin + frontend type-check, lint)
- [x] Docs updated (this TASK.md; index row; ledger D49)
- [x] Mobile contract checked — `/admin/*` routes only; `verify-invitation` gains an additive
      `invited_by` and `POST /guests` an optional `party_invites`, both web-only and ignorable
