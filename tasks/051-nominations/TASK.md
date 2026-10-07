# Task 051: Nominations

- **Status:** `done (code)`: **merged to `dev` and `main` on 2026-10-07** (backend PR #44 `6709fdb` then #45
  `2ff2082`, admin PR #44 `a5c5ead` then #45 `857fe06`), not deployed. Built the same day on `feat/nominations` (backend `851dc05` + `0e9f105`, admin
  `6ef82c7` + `c418096`).
- **Opened:** 2026-10-07
- **Owner:** unassigned
- **Sub-app(s):** backend + admin
- **Branch(es):** `feat/nominations` in `tourise-backend` + `tourise-admin`, off `dev`, created `--no-track`.

## Goal

The client has its own list of people to email about nominations. They are not guests and not invitees,
so neither Invitations nor Automations fits. This task adds a **Nominations** section under Operations:
import the list from Excel in batches, email it with the section's own templates, follow each email
(sent, delivered, opened, bounced, failed), see it on a dashboard, and export it.

## Decisions (owner, 2026-10-07, asked one at a time)

| # | Decision |
|---|---|
| 1 | **Its own module and tables.** The newsletter is the closest screen, but its subscribers are the public opt-in list: putting nominees there would put them in the newsletter's "Everyone still subscribed" audience. The section reuses the plumbing invitations already have (Excel parser, problems dialog, SMTP picker, email builder, the Mailtrap webhook, the sheet style), not the newsletter's sender. |
| 2 | **Seven columns, only Email required**: Title (from the Titles list, a dropdown in the sample), First name, Last name, Email, Company, Phone number, Language (EN / AR, blank = English). The owner dropped First name as required ("no need for now"), so a template's blank variables are tidied ("Dear ," reads "Dear,"). Phone is reference only and follows the invitations rule (`+` and the country code). |
| 3 | **One email, one batch** (option B). The import refuses an address already in any batch, compared trimmed and lower-cased, in the preview and again on the server, the way invitations refuse an address already invited (ledger D56). |
| 4 | **About 1,000 people per batch.** The import takes 1,000 rows at most, like invitations. Emails go out on Mailtrap's transactional stream, as invitations do; the webhook reads only that stream. |
| 5 | **No link in the email** (option C): it is information only. No public page, no token per nominee, no new public route. Statuses lead with Sent, Delivered, Opened; a click is still recorded if a template carries a link (a logo, the footer icons). |
| 6 | **Opt-out link: on hold** until the team answers. Built without it, nothing added for it in advance. |
| 7 | **Templates of its own**, in a Templates tab inside Nominations (option A): English and Arabic versions, the shared builder, clone, block, test send, no delete (as the newsletter since Task 040). The newsletter's template screens take their address as a setting rather than being copied; the newsletter behaves as before. |
| 8 | **The Mailtrap webhook lock-down is on hold** ("we will check it later"). The webhook takes any request today, with no secret or signature; nominations ship on it as it is. |
| 9 | **Edit or delete a nominee, or delete a batch, only while nothing has been sent to them.** Deleting frees the address for a corrected re-import; after the first send the nominee stays. |

## Design

### Tables (four new, no change to existing ones)

- `nomination_templates`: the newsletter template's shape (`name`, `subject`, `subject_ar`, `html`,
  `html_ar`, `editor_json`, `editor_json_ar`, `is_active`, `created_by`).
- `nomination_batches`: `name`, `template_id`, `smtp_config_id`, `created_by`. A send uses the batch's
  template and SMTP, which can be changed on the batch.
- `nominees`: `batch_id`, `title_id`, `first_name`, `last_name`, `email` (unique, stored trimmed and
  lower-cased), `company`, `phone`, `lang`, and `status`, the furthest stage of the nominee's latest email.
- `nomination_emails`: **one row per email sent**, like `invitation_emails`, with the same flag names
  (`is_sent`, `is_delivered`, `is_open`, `is_clicked`, `message_id`, `error_message`, `meta`) and what
  that table lacks: `nominee_id`, `batch_id`, `template_id`, `smtp_config_id`, `sent_by`, the time of
  each event (`delivered_at`, `opened_at`, `clicked_at`, `bounced_at`), `is_bounced`, `bounce_type`, and
  an index on `message_id`.

### Tracking

1. **Send** (batch screen): one `nomination_emails` row per nominee, then queued jobs of small chunks.
   Each email carries the row id and the type `notification-nomination-email` in its metadata headers,
   as invitation emails do.
2. **Sent:** `AfterEmailSentListener` gains a third branch beside invitations and guests: marks the row
   sent and stores Mailtrap's message id.
3. **Failed:** a send the mail server refuses writes its reason to `error_message`; the nominee reads
   Failed. (Invitations never record this.)
4. **Webhook:** `MailtrapWebhookController` hands every event to `NominationEmail` before its existing
   filter, so nominations also learn bounce, soft bounce, spam and reject. The guest and invitation
   lines are unchanged and still ignore those.
5. **Nominee status:** Not sent, Queued, Sent, Delivered, Opened, Clicked; **Bounced** and **Failed**
   override. It never moves back: Mailtrap can report an open before the delivery.

Limits to tell the client: Opened is approximate (Apple Mail and some company filters load images on their
own); an email whose server reply has no message id stays at Sent, as for invitations.

### Screens (Operations > Nominations: Batches | Dashboard | Templates)

- **Batches:** each batch with its counts. **New batch**: name, template, SMTP, the Excel file, the
  preview with mapped columns, the problems dialog (bad email, duplicate in the file, already in a
  batch, bad phone, unknown title, over 1,000 rows), then Create. **Download Excel sample.**
- **A batch:** its nominees with status and filters; Send to the ticked or to everyone not sent yet;
  edit or delete before the first send; See more with the nominee's sends.
- **Dashboard:** nominees, sent, delivered, opened, bounced or failed, with rates; a funnel to Opened;
  a row per batch; a batch filter. Counted from the rows, so nothing drifts.
- **Templates:** the newsletter's screens, the builder's own nominee variables: `{{ title }}`,
  `{{ first_name }}`, `{{ last_name }}`, `{{ full_name }}`, `{{ company }}`, `{{ email }}`.
- **Export:** one batch or all, each nominee with status and times, in `TouriseSheetStyle`.

### Permissions and audit

A new `nominations` feature: View, Create, Update, Delete, Send, Export, Record History, Audit Trail.
Roles start unticked. Audited from the start (Task 045): the import, edits, deletes, each Send click,
templates, exports, one row per click.

## Deploy

Migrate (four new tables), refresh routes, restart the queue workers, then tick the Nominations boxes on the
roles that need them. No `.env` change.

## Log

- 2026-10-07: opened. Findings: the newsletter tracks with its own pixel and redirect and counts "delivered"
  when the mail server accepts; it never stores a provider message id and has no import. Invitations track
  through the Mailtrap webhook, which handles only delivery, open and click and keeps no times. Decisions 1
  to 9 taken one at a time; build started on `feat/nominations`.
- 2026-10-07: built and pushed on `feat/nominations` in both repos (see *Built*). Not merged, not tried in
  a browser; the local database needs `php artisan migrate` first.
- 2026-10-07: the sample's headings sat at the bottom of their taller row, leaving an empty band above them
  (owner); centred vertically, backend `0e9f105`. Manual test files for Rawand built in
  `excel_import_fixes/test-cases-rawand/nominations/` (16 files, README of expected results) by
  `excel_import_fixes/tools/make-nomination-cases-rawand.php`, checked with `simulate-nominations.js`.
- 2026-10-07: **merged to `dev` by the owner** (backend PR #44 `6709fdb`, admin PR #44 `a5c5ead`), and to `main`
  the same afternoon (backend PR #45 `2ff2082`, admin PR #45 `857fe06`). Not deployed.
- 2026-10-07: found on the way, not this task: the newsletter's click tracker
  (`/api/newsletter/track/click/{token}?url=`) redirects to any valid address, even with a token that matches
  nothing, so it can launder a phishing link. Not in Task 041's list.

## Built (2026-10-07, `feat/nominations`)

- **Backend `851dc05`:** the four migrations (`2026_10_07_000001` to `000004`), models `NominationTemplate`,
  `NominationBatch`, `Nominee`, `NominationEmail`; `NominationsController` (batches, import, check-emails,
  nominees, send, dashboard, export, sample) and `NominationTemplatesController`; job `SendNominationEmails`
  (chunks of 50, one try, a refused send writes its reason); `SendNominationEmailNotification` with the
  metadata headers; `NominationVariableResolver`; `NominationImportWorkbook`; `NominationsExport`. The third
  branch in `AfterEmailSentListener` and the step in `MailtrapWebhookController`. 26 routes under
  `/api/admin/nominations`. 27 tests.
- **Found while building:** Mailtrap's event times are Unix seconds; read without the app's timezone they
  were stored three hours early (`Asia/Riyadh`). A worker that dies leaves a nominee Queued, which the
  double-click guard would block for ever: a send waiting over 15 minutes may now be replaced, and the
  stuck email is closed so a late worker cannot send it as well.
- **Admin `6ef82c7`:** the newsletter's four template screens take a `TemplateModule` setting (paths,
  titles, tabs, the builder's variables); the newsletter's is the default and its pages are unchanged.
- **Admin `c418096`:** Operations > Nominations: Batches, New batch (mapping, red cells, problems
  dialog, sample), a batch's page (filters, Send, polling while queued, sends per nominee, edit / delete
  before the first email, settings, export, History), Dashboard, Templates; the builder's `nomination`
  palette; sidebar link and `inferFeatureId` rule; 61 EN + AR strings.
- **Gates:** backend `pint --test` clean, PHPStan at its 5 older errors, **1105 tests pass**; admin
  `type-check`, ESLint, Prettier and `check:rbac` green (40 links); every new page compiles on the dev server
  (`yarn build` not run: a dev server was up).

## Definition of Done

- [ ] Code merged to `dev` in backend and admin
- [ ] EN + AR translations in the same commit
- [ ] Quality gate green (backend `composer qa`; admin `yarn type-check`, `yarn check:rbac`, ESLint, `yarn build`)
- [ ] Docs updated (this TASK.md, index row, HANDOFF)
- [ ] Mobile contract checked: admin-only routes, nothing the app calls
