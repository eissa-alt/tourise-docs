# Task 017 — Single-channel invitations (email | sms)

- **Status:** `done` (code) — manual QA pending
- **Opened:** 2026-07-21
- **Owner:** —
- **Sub-app(s):** backend, admin
- **Branch(es):** `dev`

## Goal

Make an invitation collection send on **exactly one** delivery channel (email or SMS) instead of firing
both at once, so status, error-tracking, and resend are unambiguous. Reverses the parallel-send half of
Task 016 (D29). WhatsApp is reserved but deferred. See ledger **D30**.

## Scope

- **In:** `channel` enum on `invitation_collections` + `invitations`; store/update scope the template +
  provider to the chosen channel (null the other side); `extractBulk` + collection-edit propagate `channel`
  to child invitations; channel-aware `invite` guard (checks `phone` for SMS); SMS success bumps
  `is_sent`/`send_count`; `channel` + `sms_template_name` in resources; admin channel picker with
  disabled/unconfigured gating + per-channel override sections on the create **and** collection-edit forms;
  channel badge in the listing; SMS-history tab in see-more; wider bulk-send modal (channel/phone/template
  columns); reorganized update-info modal; `DialogShell` 4xl/5xl; `ui-select` disabled options; titles
  preloaded once.
- **Out:** WhatsApp send path (reserved, disabled "coming soon"); automation-form UX polish (separate);
  mobile `routes/api.php` shape (unchanged — payload only).

## Log

- 2026-07-21 — built the single-channel model end-to-end (backend + admin); brought the collection-edit form
  to parity with create; reworked the bulk-send + update-info modals; committed backend `0fcd3c5`, admin
  `f1589df`; pushed to `origin/dev`.

## Decisions

Durable ones promoted to ledger **D30**. Task-local: bulk-send row is click-to-toggle; empty-state row when
no invitations; SMS `is_sent` is boolean-aware in the UI badges.

## Definition of Done

- [x] Code merged to `dev` (backend + admin)
- [x] EN + AR translations in the same commit
- [x] Quality gate green (backend `pint --test` + `phpstan`; admin `yarn type-check` + eslint)
- [x] Docs updated (ledger D30; this TASK.md; index row)
- [x] Mobile contract checked — `routes/api.php` shape unchanged for invitations (no mobile delta)
- [ ] Manual QA: send a collection on each channel, resend, extract-bulk, verify logs
