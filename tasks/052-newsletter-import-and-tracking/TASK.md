# Task 052: Newsletter import and Mailtrap tracking

- **Status:** `in-progress`: part 1 (import) built on `feat/newsletter-import`, backend `408c7a0`, admin
  `0442232`, pushed, not merged. Part 2 (tracking) not started; two owner questions open.
- **Opened:** 2026-10-12
- **Owner:** unassigned
- **Sub-app(s):** backend + admin
- **Branch(es):** `feat/newsletter-import` (part 1), then `feat/newsletter-tracking` (part 2), in
  `tourise-backend` + `tourise-admin`, off `dev`, created `--no-track`.

## Goal

Bring the Newsletter section up to what Nominations has (Task 051): (1) add subscribers from the client's own
Excel sheet, recorded with the source **Imported**; (2) follow each newsletter email through the Mailtrap
webhook (delivery, open, click) instead of counting "delivered" when our SMTP server accepts it.

## Findings (2026-10-12)

- **Subscribers** only arrive through public flows: the website signup (`website`), the registration opt-in
  (`registration`), the invitation-request opt-in (`invitation_request`). `source` is a free string; the
  listing and export filter it through `NewsletterSubscriber::SOURCE_GROUPS`. No admin add, no import; an
  Export exists. `NewsletterSubscription::subscribe()` re-subscribes an address that left and keeps the first
  source, so the import does not reuse it.
- **Sending:** one queued job per campaign (`SendNewsletterCampaign`, `NewsletterSender`), `Mail::html()` with no
  metadata headers and no provider message id. A recipient reads "delivered" as soon as SMTP accepts the send.
  Opens and clicks come from our own pixel and click redirect (`/api/newsletter/track/open|click/{token}`, the
  open redirect noted in Task 051's log). `AfterEmailSentListener` has no newsletter branch.
- **Admin:** Campaigns is a list of counts; no page per campaign, no per-recipient view, although
  `newsletter_campaign_recipients` keeps sent / delivered / opened / clicked times per address.
- **Not audited** (no `Auditable`, no trail screens); permissions `newsletter`: view, export, create, update,
  delete, send.
- **Found on the way, not this task** (owner to decide): "{count} unsubscribed, will be skipped" shows a literal
  `{count}` (single braces); the Send success toast reads the campaign's `sent_count`, 0 while queued; the
  Subscribed-on sort is ignored by the API; the Subscribers screen has no Lists column though the API sends
  them; Export, Add to list, Send and the list buttons are shown to anyone who can open the section (the API
  enforces the boxes).

## Decisions (owner, 2026-10-12, asked one at a time)

| # | Decision |
|---|---|
| 1 | **Two parts, import first.** Part 2 (tracking) does not depend on part 1. |
| 2 | **An imported subscriber is source `imported`, status subscribed.** |
| 3 | **An address already in the newsletter refuses the file**, whatever its source (a form, the website, an earlier import) and status (subscribed or not), as the other imports refuse theirs: red in the preview with its status and source, listed in the problems dialog, and refused again by the server. The team cleans the file by hand. So an import never changes an existing subscriber, and never subscribes again someone who left. |
| 4 | **1,000 rows per import**, as the invitation and nomination imports. |

## Design, part 1 (import)

- **Admin:** Subscribers gets an **Import subscribers** button (newsletter Create box) opening Newsletter -
  Import: an optional list (the default list otherwise), "Before you upload" notes, the file (xlsx, xls, csv),
  **Download Excel sample**, the preview with columns mapped by heading, red cells, the problems dialog. After
  Create, Subscribers opens filtered to Imported.
- **Columns:** First Name, Last Name, Email (required), Company, Language (EN / AR, blank = English).
- **Refused:** a missing or bad email, the same email twice in the file, an email already in the newsletter, an
  unknown language, a value over 255 characters, more than 1,000 rows.
- **API** (all on `admin.can:newsletter,create`): `POST /admin/newsletter/subscribers/import`,
  `POST /admin/newsletter/subscribers/check-emails`, `GET /admin/newsletter/subscribers/import-template`.
  Admin-only, nothing the mobile app calls. No migration: `source` is a free string.

## Part 2 (tracking), to settle before building

- Our own open pixel and click redirect: keep them, or let Mailtrap track opens and clicks alone (which would
  also close the open redirect).
- Which Mailtrap stream production newsletters use: transactional (the webhook already listens) or bulk (a
  second webhook in Mailtrap, and the controller accepting bulk events for newsletter emails only).
- Then, as Task 051: metadata headers on each email, the message id stored by `AfterEmailSentListener`, events
  recorded per recipient with times and matched to the recipient's own address, counts from the rows, a
  Delivered column, and a page per campaign listing its recipients. One migration (message id, event log).

## Deploy (part 1)

No migration, no `.env` change. Refresh cached routes (three new). Roles that should import need the
newsletter **Create** box.

## Log

- 2026-10-12: opened. Findings above; decisions 1 to 4 taken one at a time; part 1 built on
  `feat/newsletter-import`.

## Built (2026-10-12, `feat/newsletter-import`)

- **Backend `408c7a0`:** `AdminNewsletterController::importSubscribers` (bulk insert in a transaction, the
  unsubscribe token set there since a bulk insert skips the model hook, the chosen or default list attached, a
  unique-index race answered 422), `checkSubscriberEmails`, `importTemplate`; `NewsletterImportWorkbook`;
  `NewsletterSubscriber::SOURCE_IMPORTED` and the `imported` source group; 3 routes. `NewsletterImportTest`,
  8 tests.
- **Admin `0442232`:** `newsletter-import-form.tsx` (the nominations import's flow: mapping by heading, red
  cells, problems dialog, notes, sample; an existing address shown with its status and source), page
  `/newsletter/import`, the Import subscribers button, `sources.ts` (source labels with Imported, used by the
  listing and the import), the Source filter's Imported option, the form header's `import` mode. EN + AR.
- **Gates:** backend `pint --test` clean, PHPStan at its 5 older errors, **1118 tests pass**; admin
  `type-check`, ESLint, Prettier, `check:rbac` (40 links) and `yarn build` green. Not tried in a browser.

## Definition of Done

- [ ] Part 1 merged to `dev` in backend and admin
- [ ] Part 2 decided, built and merged
- [ ] EN + AR translations in the same commit
- [ ] Quality gate green (backend `composer qa`; admin `yarn type-check`, `yarn check:rbac`, ESLint, `yarn build`)
- [ ] Docs updated (this TASK.md, index row, HANDOFF)
- [ ] Mobile contract checked: admin-only routes, nothing the app calls
