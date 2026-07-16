# Task 007 — RSVP "Not interested" decline link + `will_attend` surfacing

- **Status:** `done` (code shipped on `dev` across backend/frontend/admin)
- **Opened:** 2026-06-28
- **Owner:** AI agent
- **Sub-app(s):** backend + frontend + admin
- **Branch(es):** `dev`
- **Origin chat:** requested in the "Change project info to TOURISE" session (2026-06-28) — see the
  transcript archive. Built same day; a follow-up fix landed 2026-06-30.

## Goal

Give invitees a **one-click "No / Not interested"** path straight from the invitation email, as a
sibling to the existing "Yes" RSVP link. "Yes" keeps opening the RSVP form to fill/adjust; "No"
records the decline in a single click (no form), back-fills the guest from their invitation, saves
`will_attend = no`, and shows a plain thank-you with **no QR code and no registration number**.
Also surface `will_attend` to admins (guest table, view-more, search).

## Scope

- **In:**
  - New email template variable `{{ invitation_link_not_interested }}` alongside `{{ invitation_link }}`.
  - Frontend one-time auto-submit decline page.
  - Backend one-click decline handler (skips OTP + email-uniqueness form gates).
  - `will_attend` shown in admin guest listing / view-more / search.
  - Label rename to "Attendance Confirmation"; hide one field in the invitations form.
  - EN + AR translations for all new user-facing strings.
- **Out (explicitly not this task):**
  - A dedicated "decline" email template / notification_settings hook (none exists; **no** email is
    sent on decline — see Decisions).
  - Any change to the normal "Yes" registration flow beyond ensuring it defaults `will_attend = yes`.

## How the two links resolve

Both are built by `EmailVariableResolver` from the guest's `invitation_token`
(`alt-static-basecode-backend/app/Services/EmailVariableResolver.php`, ~lines 63–72):

| Variable | URL | Behavior |
|---|---|---|
| `{{ invitation_link }}` | `{PUBLIC_FRONTEND_URL}/{lang}/join/{categorySlug}/{token}` | Opens the RSVP form to fill/adjust → `will_attend = yes` |
| `{{ invitation_link_not_interested }}` | …same base…`/decline` | One-click decline → `will_attend = no`, thank-you page |

Both variables are registered in the admin email-template variable picker
(`email-editor-waypoint.tsx`) as **"Invitation Link"** and **"Invitation Link – Not Interested"**.

## What landed

### Backend (`alt-static-basecode-backend`)
1. **`EmailVariableResolver.php`** — resolves `{{ invitation_link }}` and
   `{{ invitation_link_not_interested }}` (the latter = base + `/decline`); both empty when the guest
   has no `invitation_token`.
2. **`GuestsController@store`** — branches early: if `will_attend === 'no'` → `handleDecline()`.
   The normal path defaults `will_attend` to `yes`.
3. **`GuestsController@handleDecline()`** — one-click decline, no form:
   - Skips OTP and the email-uniqueness gate.
   - **Does NOT flip an already-registered guest** — if the email already belongs to a guest it
     returns `409 { reason: 'already_registered' }` and leaves them untouched (bug caught in
     testing, then fixed).
   - Creates the guest with data back-filled from the invitation, `will_attend = 'no'`,
     `source = website`, a generated registration number, and the category's on-register status.
   - Writes a `Guest Declined` history log and consumes the invitation code.
   - **Sends no confirmation email** on decline.

### Frontend (`alt-static-basecode-frontend`)
4. **`pages/[lang]/join/[category]/[token]/decline.tsx`** — SSR verifies the invitation via
   `verify-invitation/{category}/{token}`, then the client **auto-submits once** (guarded by a
   `useRef`) with `will_attend: 'no'` + reCAPTCHA, back-filling name/email/company/position/phone/
   title from the invitation. UI states: **Submitting → ThankYou** (`web:rsvp_success_message`, "Back
   to homepage" button, no QR / no reg number).
   - A `fully_used` / already-responded invite shows the friendly "already" thank-you (repeat clicks
     stay friendly).
   - `already_registered` → shows an "already submitted" error instead of a thank-you.
   - `429` → "too many attempts"; other failures → generic error.
5. EN + AR translation keys added (`translations/{en,ar}/web.json`).

### Admin (`alt-static-basecode-admin`)
6. `{{ invitation_link_not_interested }}` added to the template-variable list in
   `email-editor-waypoint.tsx`.
7. `will_attend` surfaced across guest management (listing, see-more modal, super-search,
   `interfaces/guest.tsx`, form-shape config); label shown as **"Attendance Confirmation"**; one
   field hidden in the invitations form. EN + AR translations updated.

## Commits (all on `dev`)

| Repo | SHA | Date | Message |
|---|---|---|---|
| backend | `4e77b25` | 2026-06-28 | feat: add RSVP decline handling and update invitation links in email templates |
| backend | `f136373` | 2026-06-30 | refactor: remove confirmation email logic for declined RSVPs in GuestsController |
| frontend | `9fa4ee1` | 2026-06-28 | feat(decline): add RSVP decline page with server-side handling |
| admin | `951445c` | 2026-06-28 | feat: add 'will attend' feature to guest management and update translations |

## Decisions (this task)

- **Don't flip existing guests.** A decline click for an email that's already registered returns
  `409 already_registered` and leaves the existing RSVP untouched (never downgrade attending → no).
- **No email on decline.** The register-complete template is a *registration confirmation* and would
  be misleading for a "not attending" RSVP; there is no dedicated decline template in
  `notification_settings`, so decline sends nothing (backend `f136373`).
- **One-time, no form.** Decline is a single auto-submit on page load; repeat clicks on a used invite
  land on a friendly thank-you rather than an error.
- **"Yes" flow unchanged** except that reaching the normal registration path defaults
  `will_attend = yes` (the "no" path is branched off earlier).

## Definition of Done

- [x] Code merged to `dev` in backend + frontend + admin
- [x] EN + AR translations in the same commit (decline page + `will_attend` labels)
- [x] `{{ invitation_link_not_interested }}` resolves and is selectable in the template editor
- [x] Existing-guest guard + no-email-on-decline verified in testing (user-confirmed)
- [ ] Quality gate re-run of record on current `dev` (`composer qa`; `yarn type-check` + `yarn production`)
- [ ] Real-env browser QA of the email → "No" button → thank-you flow (EN + AR)
- [x] `routes/api.php` unchanged (reuses existing `guests` + `verify-invitation` endpoints — no mobile-contract impact)
