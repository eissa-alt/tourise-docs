# Task 052: Newsletter import and Mailtrap tracking

- **Status:** `in-progress`: part 1 (import) **merged to `dev`** (PR #48: backend `1c3bc83`, admin `41782f5`),
  not on `main`. Part 2 (Mailtrap tracking) built on `feat/newsletter-tracking`, backend `80fb2cd`, admin
  `14b61e5`, pushed, not merged.
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
| 5 | **Mailtrap alone tracks opens and clicks** (option A): new emails carry no own pixel and no rewritten links. The old open and click links keep answering emails already sent; the click link redirects only for a token one of our emails carried (it was an open redirect). |
| 6 | **Newsletter events from either Mailtrap stream**, transactional or bulk; guest, invitation and nomination emails stay transactional only. A second webhook address, `/api/webhooks/mailtrap/bulk`, for the bulk stream's webhook. |
| 7 | **The newsletter's own SMTP account, on a Newsletter, Settings tab** (not on the list edit: a campaign need not use a list). Stored as `smtp_configs.is_newsletter_default`, one at most. A send uses the account picked, else the newsletter's, else the system default. The owner will create a `live.smtp.mailtrap.io` and a `bulk.smtp.mailtrap.io` account and set the bulk one. |
| 9 | **Settings is a box of its own** (Newsletter, Settings, owner 2026-10-12): changing the sending account needs it, not Update; the tab shows only with it; reading the account stays on the section (the Send dialog opens on it). Roles start without it. |
| 10 | **The Newsletter boxes follow the tabs** (option B, owner 2026-10-12): `subscribers_view`, `subscribers_import`, `subscribers_export`, `subscribers_add_to_list`, `dashboard_view`, `lists_view`, `lists_manage`, `campaigns_view`, `campaigns_send`, `campaigns_export`, `templates_view`, `templates_manage`, `settings`. Each tab shows with its view box, each button with its own. The old boxes (view, export, create, update, delete, send) are **taken off every role, not converted** ("nvm about the existing one"): roles are ticked again by hand. Template and list names, and the sending account, stay readable to the whole section (pickers and the Send dialog need them). |
| 11 | **Not delivered and Delivery delayed for newsletter emails too** (owner, 2026-10-12, before `main`), with Nominations' rules (task 051 decision 12): bounce or reject final, soft bounce or suspension retrying until a delivery clears it, a refused send reads Not delivered. The Bulk webhook is created with Delivery, Open, Click, Bounce, Soft Bounce, Reject, Suspension. |
| 8 | **One-click unsubscribe header** (RFC 8058, `List-Unsubscribe` + `List-Unsubscribe-Post`), which Gmail and Yahoo expect from bulk senders; a POST to the API's unsubscribe address unsubscribes without a page. |

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

## Design, part 2 (tracking)

- **Sending:** each email carries the metadata headers (`notification-newsletter-email`, the recipient's id);
  `AfterEmailSentListener` stores Mailtrap's message id on the recipient. A recipient reads **Sent** until
  Mailtrap reports the delivery (it used to read Delivered as soon as our SMTP server took it).
- **Webhook:** `NewsletterCampaignRecipient::recordMailtrapEvent` records delivery, open and click with their
  times, only for the recipient's own address, once per event id; an open or click fills a missing delivery.
  The campaign's delivered / opened / clicked counts move once per recipient.
- **Admin:** a page per campaign (tiles for recipients, sent, delivered, opened, clicked; every recipient with
  their stage and times, filtered by email and stage); the Campaigns list gains Delivered and loses Failed (the
  Nominations screens' rule, decision 11 of Task 051); Newsletter, Settings; the Send dialog opens on the
  newsletter's account; the SMTP picker and the SMTP list mark it "Newsletter".

## Deploy

- **Part 1:** no migration. Refresh cached routes (three new). Roles that should import need the newsletter
  **Create** box.
- **Part 2:** `migrate` (`2026_10_12_000001` smtp_configs, `2026_10_12_000002` recipients), refresh routes,
  restart the queue workers. **Then tick the new Newsletter boxes on every role that uses the section**:
  migration `2026_10_12_000003` takes the old ones off, so until then only Super Admins see Newsletter. Then, by the owner: create the SMTP accounts (`live.smtp.mailtrap.io`,
  `bulk.smtp.mailtrap.io`) and choose the bulk one on Newsletter, Settings; in Mailtrap add a **Bulk** stream
  webhook to `https://api-register.tourise.com/api/webhooks/mailtrap/bulk` (payload JSON, area Email Sending,
  stream "Bulk (excludes campaigns)", domain tourise.com, events Delivery, Open, Click, Bounce, Soft Bounce,
  Reject, Suspension), **after** the backend is
  deployed (the address does not exist before); keep the Transactional webhook as it is; check open and click tracking
  is on for the sending domain. Then one real send to see the numbers move. The webhook takes any request
  (Task 051 decision 8, lock-down on hold); the bulk address is the same handler.

## Log

- 2026-10-12: opened. Findings above; decisions 1 to 4 taken one at a time; part 1 built on
  `feat/newsletter-import`.
- 2026-10-12: part 1 merged to `dev` by the owner (PR #48). Decisions 5 to 8; part 2 built on
  `feat/newsletter-tracking`. Not tried in a browser; `yarn build` not run (a dev server was up).

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

## Built (2026-10-12, `feat/newsletter-tracking`)

- **Backend `80fb2cd`:** the two migrations; `NewsletterSender` (headers, no pixel or rewritten links, Sent until
  delivered, the account picked / newsletter / system default, the test send through the newsletter's account);
  `NewsletterCampaignRecipient` (`NOTIFICATION_TYPE`, `STAGES`, `stage()`, `whereStages()`,
  `recordMailtrapEvent()`); `AfterEmailSentListener` newsletter branch; `MailtrapWebhookController` (newsletter
  from either stream) and the bulk route; `NewsletterController::unsubscribeOneClick` and the click link's
  check; `AdminNewsletterController` settings, `campaignRecipients`, the newsletter account on a send, the SMTP
  name on a campaign, `from` / `to` in listing meta; `SMTPConfig::newsletterDefault()`, the flag in the resource
  and the select list. `NewsletterTrackingTest`, 9 tests; `NewsletterUnsubscribeTest` expects Sent.
- **Admin `14b61e5`:** `newsletter-campaign-details.tsx` and `/newsletter/campaigns/[id]`,
  `newsletter-settings.tsx` and `/newsletter/settings` (a sixth tab), the Campaigns list (link, Delivered, no
  Failed), the Send dialog's preselection, the SMTP picker's and the SMTP list's "Newsletter" mark. EN + AR.
- **Then:** the toolbar buttons in the admin's own sizes (admin `c7ea5ee`); the Settings box, decision 9
  (backend `8b005df`, admin `97a1cf8`); a Search box on Subscribers over first and last name, email and company,
  as Guests have, the export searching alike (backend `b2057fe`, admin `f90417c`); the boxes by tab, decision 10,
  with migration `2026_10_12_000003`, a Campaigns export (`GET /admin/newsletter/campaigns/export`,
  `NewsletterCampaignsExport`) and the catalog rule widened to per-tab `*_view` boxes (backend `cef1584`, admin
  `12683b3`, `useNewsletterBox` / `NewsletterNoAccess`, `TemplateModule.boxes`, 12 box labels EN + AR).
- **Gates:** backend `pint --test` clean, PHPStan at its 5 older errors, **1127 tests pass**; admin
  `type-check`, ESLint, Prettier, `check:rbac` green; `yarn build` not run (dev server up).

## Built (2026-10-12, `feat/newsletter-not-delivered`, decision 11)

- **Backend `b8711c2`:** migration `2026_10_12_000005` (recipients `bounced_at`, `bounce_type`, `bounce_reason`;
  campaigns `not_delivered_count`); `NewsletterCampaignRecipient` stages `delayed` / `not_delivered`, `whereStages`,
  `problemType()` / `problemReason()`, the bounce handling in `recordMailtrapEvent`; the campaign page's rows, the
  dashboard and the Campaigns export count Not delivered. 1140 tests pass, PHPStan at its 5.
- **Admin `7cf2fb0`:** the two stages on the campaign page (filter, badge, the Nominations reason line), a Not
  delivered tile, a column on Campaigns, a tile on the dashboard. EN + AR. Local demo data
  (`excel_import_fixes/tools/make-newsletter-demo-data.php`) gains one of each; run it after `migrate`.

## Definition of Done

- [ ] Part 1 merged to `dev` in backend and admin
- [ ] Part 2 decided, built and merged
- [ ] EN + AR translations in the same commit
- [ ] Quality gate green (backend `composer qa`; admin `yarn type-check`, `yarn check:rbac`, ESLint, `yarn build`)
- [ ] Docs updated (this TASK.md, index row, HANDOFF)
- [ ] Mobile contract checked: admin-only routes, nothing the app calls
