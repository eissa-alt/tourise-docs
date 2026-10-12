# Nominations and Newsletter update

What changed in the Nominations and Newsletter sections of the TOURISE 2027 admin, and what to check. 12 October 2026.

## 1. In short

**Nominations** gets CC and BCC for each nominee, a steadier batch page, and two new statuses that say when an email did not arrive and why: **Not delivered** and **Delivery delayed**. The **Newsletter** catches up with Nominations: an Excel import, delivery, opens and clicks reported by Mailtrap, a page for each campaign, a Settings tab for its sending account, and access set tab by tab.

> **What you need to do:** if you manage roles, tick the new Newsletter boxes on every role that uses the section once the update is live (part 4). Until then only Super Admins see the Newsletter. Nobody else needs to do anything.

**Status (12 October 2026):** going live on production today. The 48 failed reminder emails of 11 October are already marked (part 3).

## 2. Email statuses, in both sections

Nominations and the Newsletter now read an email's status the same way. Mailtrap, the service that sends our emails, reports each step back to the admin, usually within minutes.

| Status | What it means |
|---|---|
| **Sent** | We handed the email to Mailtrap. Mailtrap has not confirmed the delivery yet. |
| **Delivered** | The recipient's mail server accepted it. |
| **Opened** | The recipient opened it. Approximate: some mail apps and company filters open emails on their own, which also counts. |
| **Clicked** | The recipient clicked a link in it. |
| **Delivery delayed** (new) | The recipient's server asked Mailtrap to try again later (a soft bounce or a suspension). Mailtrap keeps retrying: the status moves on to Delivered if it gets through, or to Not delivered if Mailtrap gives up. |
| **Not delivered** (new) | The email will not arrive: the address or its domain does not exist, the server refused it (a bounce), Mailtrap rejected it, or our own mail server refused the send. |

Under a Not delivered or Delivery delayed status, a short grey line says what happened, in the receiving server's own words, and when. For example: *Bounce · 5.1.1 The email account that you tried to reach does not exist · 11/10/2026 12:22*.

### Reading the reason

| The reason says | What it usually means | What you can do |
|---|---|---|
| DNS error ... (NXDOMAIN), or No suitable IP address | The domain after the @ does not exist | Check the spelling first (one of the 48 below is the typo *srilanka.travelv*), otherwise find a working contact |
| The email account ... does not exist, No such recipient, Invalid recipient, mailbox disabled | The domain is real, the mailbox is not | Find another contact at that organisation |
| Recipient address rejected: Access denied (Office 365) | Their server only takes mail from senders it already knows | Ask for another address, or ask them to allow tourise.com |
| Network error: Unexpectedly disconnected (BANNER) | Their server cut the connection before taking the email | Often a strict or overloaded server: try another address for the same person |
| Rejected under suspicion of SPAM, Relaying denied, unauthenticated | Their server's own rules refused it | Reach them another way |
| Temporary DNS error (TIMEOUT) | Their domain did not answer in time | Usually passes; check the address is right |

## 3. Nominations

### CC and BCC for each nominee

- The Excel has two new optional columns, **CC Emails** and **BCC Emails**, just before Language: Title, First Name, Last Name, Email, Company, Phone, CC Emails, BCC Emails, Language. **Download Excel sample** on New batch already has them.
- A cell can hold several addresses, separated by commas, so each person can have their own assistant or office copied.
- A nominee's own address cannot be in their CC or BCC: the preview marks it red. A copy can be another nominee's address.
- The copies show small under the nominee's email on the batch page, can be changed in **Edit nominee** until the first email is sent, and are in the export.
- The status follows the nominee's own copy only: a CC opening the email does not mark the nominee Opened.

### "Before you upload" notes

New batch now lists the rules before you pick a file: start from the sample, columns are matched by their headings, one row is one nominee (blank rows are ignored), the same email cannot appear twice in a batch, an address already in another batch is refused, the nominee's own address cannot be in CC or BCC, phones are written with + and the country code, and a batch takes 1,000 nominees at most.

### Not delivered and Delivery delayed

| Where | Before | Now |
|---|---|---|
| A batch's page | A failed email could still read Sent; Bounced and Failed hidden | Both new statuses in the Status filter, the reason line under each status, a **Not delivered** tile, and a note under Sent when some emails are delayed |
| Batches list and Dashboard | No failure count | A **Not delivered** column; on the Dashboard a tile with its rate |
| A nominee's emails (History icon on the row) | Status only | Each email with its own status and reason |
| Export | No failure details | Three new columns: Problem reported at, Problem, Problem reason |

The old **Bounced** and **Failed** statuses are gone: they now read Not delivered, or Delivery delayed while Mailtrap is still retrying.

> **To email a corrected address:** a nominee cannot be edited once they have been emailed, so put the corrected address in a new batch.

### The 48 reminder emails of 11 October

Mailtrap showed 48 emails of the reminder "TOURISE Awards 2027, A Reminder to Submit Your Nomination" as Not delivered while the admin still said Sent: at the time Mailtrap was not reporting failures to us. It does now, and these 48 were marked Not delivered with Mailtrap's reasons on 12 October.

| Reason | Emails |
|---|---|
| The domain does not exist (one is the typo *srilanka.travelv*) | 16 |
| Their server dropped the connection (BANNER) | 10 |
| The mailbox does not exist or is disabled (one is the placeholder *name@email.com*) | 10 |
| Office 365 "Access denied" | 7 |
| Refused by the server's rules (spam suspicion, relaying, unauthenticated) | 3 |
| Temporary DNS timeout | 2 |
| **Total** | **48** |

### A steadier batch page

- **Selection bar**, as on Automation, Create: "Total selected: X of N", **Select all matching** (every nominee the filters find, on all pages), **Clear selection**, **Send to everyone not sent yet** and **Send to selected**.
- **Language filter fixed.** The page used to open filtered to English, hiding Arabic nominees, and Reset could make it reload endlessly. It now starts empty and shows everyone.
- **No endless refresh or flicker.** While emails wait in the queue, the page checks every 5 seconds for two minutes, then shows "N email(s) still waiting in the queue" with a Refresh button.
- The standard Edit icon and checkboxes, a **History** icon for a nominee's emails, and the right "Showing 1 to 20" counts in the footer.

## 4. Newsletter

The tabs are now: Subscribers, Dashboard, Lists, Campaigns, Newsletter Templates, **Settings**.

### Import subscribers from Excel

- **Subscribers, Import subscribers.** Columns: First Name, Last Name, **Email** (the only required one), Company, Language (EN or AR; blank means English). Start from **Download Excel sample**.
- Choose a list for the new subscribers, or leave it empty and they join the default list.
- The same flow as the other imports: a preview, problem cells in red, the list of problems, and the server checks everything again.
- Imported people are **subscribed**, with the source **Imported**. After the import, Subscribers opens filtered to Imported.
- An address already in the newsletter refuses the file, whether it came from a form, the website or an earlier import, subscribed or not. Remove it from the file and upload again. So an import never changes an existing subscriber, and never re-subscribes someone who left.
- 1,000 subscribers per import at most.

### Tracking from Mailtrap

| | Before | Now |
|---|---|---|
| Delivered | Our own server accepted the email | Mailtrap confirms the recipient's server accepted it; until then the email reads **Sent** |
| Opened, Clicked | Our own tracking image and links | Reported by Mailtrap, with the time of each |
| Failures | Not shown | **Not delivered** and **Delivery delayed**, with the reason, as in Nominations |

Campaigns sent before the update keep the numbers they already had.

### A page for each campaign

- **Campaigns, click a campaign's name.** The campaign's template, list, sending account and send date.
- Tiles: Recipients, Sent, Delivered, Opened, Clicked and **Not delivered**, with rates.
- Every recipient with their status, the reason line when there is a problem, and the time of each step; filter by email and by status.
- The Campaigns list gains Delivered and Not delivered columns, and the Dashboard a Not delivered tile for the latest campaign.

### Settings, Search, Export

- **Settings tab:** choose the email account (SMTP) newsletters go out from. The Send dialog opens on it, test sends use it, and the SMTP list marks it **Newsletter**. If none is chosen, the system's default account is used. The plan is a Mailtrap bulk account for newsletters, kept apart from the one that sends invitations and nominations.
- **Search on Subscribers:** one box over first and last name, email and company, as on Guests. Export follows the search.
- **Export on Campaigns:** an Excel file with each campaign's name, template, list, status, send date, recipients, and sent, delivered, opened, clicked and not delivered, with rates.
- **One-click unsubscribe:** newsletter emails carry the standard unsubscribe header Gmail and Yahoo expect from bulk senders. Many inboxes show an **Unsubscribe** link next to the sender's name; using it unsubscribes the person at once. The link inside the email works as before.
- **Template editor:** a single Back to the list, an English | Arabic switch, a smaller template picker, and buttons in the admin's standard sizes.

### Access, tab by tab

The Newsletter's role boxes now follow its tabs. A tab shows only with its View box, and each button only with its own box.

| Tab | Box | Lets the person |
|---|---|---|
| Subscribers | View subscribers | See the Subscribers tab |
| Subscribers | Import subscribers | Import from Excel |
| Subscribers | Export subscribers | Export subscribers to Excel |
| Subscribers | Add to list | Add selected subscribers to a list |
| Dashboard | View dashboard | See the Dashboard tab |
| Lists | View lists | See the Lists tab |
| Lists | Manage lists | Create, edit and delete lists |
| Campaigns | View campaigns | See campaigns and each campaign's page |
| Campaigns | Send newsletter | Send a newsletter |
| Campaigns | Export campaigns | Export the Campaigns list |
| Newsletter Templates | View templates | See the templates |
| Newsletter Templates | Manage templates | Create, edit, clone and switch off templates, upload images, send a test |
| Settings | Settings | See the Settings tab and change the sending account |

> **Heads-up:** the old Newsletter boxes (View, Export, Create, Update, Delete, Send) are removed by the update, not converted. Until the new boxes are ticked on each role, only Super Admins see the Newsletter.

## 5. Right after the update

1. **Roles:** tick the new Newsletter boxes on every role that uses the section.
2. **The 48 reminder emails:** done. They were marked Not delivered with their reasons on 12 October.
3. **Mailtrap:** a second webhook is added for the bulk sending stream, and the newsletter's bulk account is chosen on Newsletter, Settings.
4. **One test newsletter** is sent, to see Delivered and then Opened appear on its campaign page.

Numbers move as Mailtrap reports them, usually within minutes. A Delivery delayed email can still change to Delivered or to Not delivered later.

## 6. What to check

Checks 1 to 12 can be done on the test (development) admin. Checks 13 to 18 need the live admin, because Mailtrap reports only to it. Write **Pass** or **Fail** in the last column.

| # | Steps | Expected result | Pass / Fail |
|---|---|---|---|
| 1 | Nominations, New batch: **Download Excel sample** | CC Emails and BCC Emails sit just before Language | |
| 2 | Import a nominee with two CC addresses, separated by a comma | Saved; both copies show under the nominee's email | |
| 3 | Import a nominee with their own email in CC Emails | The cell is red and Create lists the problem | |
| 4 | Open a batch with English and Arabic nominees | Everyone shows; the Language filter is empty. Reset reloads once | |
| 5 | Filter a batch, then **Select all matching** | "Total selected: N of N" across all pages; Clear selection empties it | |
| 6 | Export a batch | Has CC, BCC, Problem reported at, Problem and Problem reason columns | |
| 7 | Newsletter, Subscribers, **Import subscribers** with three new addresses | Three subscribers, subscribed, source Imported; the list opens filtered to Imported | |
| 8 | Import a file that holds an address already in the newsletter | That row is red with its status and source; Create is refused | |
| 9 | Search part of a company name on Subscribers, then Export | Only the matching subscribers, in the list and in the file | |
| 10 | Settings: choose an account, then open Send | The Send dialog shows that account; the SMTP list marks it Newsletter | |
| 11 | Give a role only **View subscribers** and sign in with it | Only the Subscribers tab; no Import, Export or Add to list buttons | |
| 12 | Campaigns, **Export** | An Excel file with the columns listed in part 4 | |
| 13 | Send a nomination to your own address | Sent, then Delivered, then Opened once you open it | |
| 14 | Send a nomination with a CC; open only the CC's copy | The nominee stays at Delivered | |
| 15 | Send a nomination to an address on a domain that does not exist | Not delivered, with "Bounce · DNS error ..." under it; the Not delivered tile goes up | |
| 16 | Open the 11 October reminder batch | The 48 read Not delivered, each with its reason | |
| 17 | Send a newsletter to a small list with your own address | Its campaign page shows Sent, then Delivered, then Opened | |
| 18 | Include an address on a domain that does not exist | Not delivered on the campaign page, with its reason; counted in the Campaigns list | |

## 7. For developers

- **Commits:** Nominations CC and BCC, backend and admin PRs #46 and #47 (8 October). Newsletter import PR #48; tracking, Settings, boxes by tab, Search and Campaigns export PR #49; Nominations Not delivered PR #50; Newsletter Not delivered PR #51 (each PR number in both repos). The 48 failures command, backend PR #52. On `main`: backend PR #53 (`df6bfc2`), admin PR #52 (`7f379a3`).
- **Migrations:** `2026_10_08_000001` (nominee copies); `2026_10_12_000001` (`smtp_configs.is_newsletter_default`), `000002` (recipients' `message_id`, `meta`), `000003` (clears the old Newsletter boxes from roles), `000004` (`nomination_emails.bounce_reason`, re-reads Bounced nominees), `000005` (recipients' bounce columns, campaigns' `not_delivered_count`).
- **The 48:** `php artisan nominations:import-mailtrap-failures [--dry-run]`, the rows kept in the command. Run on production on 12 October after `migrate`: 48 marked, 0 already, 0 not found. Running it again changes nothing.
- **Webhooks:** `/api/webhooks/mailtrap/transactional` is unchanged; new `/api/webhooks/mailtrap/bulk`. Both go to `MailtrapWebhookController::receive`. Newsletter events are taken from either stream; guest, invitation and nomination events from the transactional stream only. The Bulk webhook: JSON, Email Sending, stream "Bulk (excludes campaigns)", domain tourise.com, events Delivery, Open, Click, Bounce, Soft Bounce, Reject, Suspension.
- **Newsletter sending:** metadata headers, `List-Unsubscribe` and `List-Unsubscribe-Post` (RFC 8058, `POST /api/newsletter/unsubscribe/{token}`); no own tracking image or rewritten links. The account: the one picked on Send, else the newsletter's, else the system default.
- **Tests:** backend 1140 pass, PHPStan at its 5 older errors. No new package, no new `.env` key. Restart the queue workers after the deploy.
