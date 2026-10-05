# One invitation per email

A guest's email can now have only one invitation, across every collection, in the TOURISE 2027 admin. 5 October 2026.

## 1. In short

Until now the same email could be invited again in a **different** collection, and even inside one collection the check only worked in some screens. Now an email can have **only one invitation in the whole system**, whatever state that invitation is in (used, sent or inactive). The rule applies everywhere an invitation is made: the invitation screens, accepting invitation requests, and dignitary parties.

> **What you need to do:** nothing. To invite someone who already has an invitation into another collection, **move** their invitation (More, then Move to collection) or edit it, instead of creating a new one.

**Status (5 October 2026):** on the development version for testing; it reaches production with the next release. No clean-up is needed: the invitations on production today are test data.

## 2. What changed in the invitation screens

| Where | Before | Now |
|---|---|---|
| Create a collection (manual cards) | Duplicates checked only between the cards on screen | Each card is checked **while typing** against every invitation: "This email already has an invitation" |
| Create a collection (Excel) | Duplicates checked only inside the file | Rows already invited turn **red**, the preview counts them, and Create lists them in the problems dialog with the registered ones |
| Add people | Refused only if already in the same collection | Refused if already invited **anywhere** |
| Edit one invitation's email | Checked only in the same collection, and only in the browser | A new email is refused if any other invitation has it. Editing the rest of an invitation is never blocked |
| Move to collection | Moves the same invitation | Unchanged: a move never creates a second invitation |

Messages never name the other collection, so an admin limited to some categories does not learn about collections they cannot see.

## 3. Effects on invitation requests

- **Accepting a request whose email already has an invitation is refused** with "This email is already invited." The request **stays pending**, so the reviewer can reject it, or fix the existing invitation first.
- **Bulk accept** handles the others normally and lists the refused ones as failed, with the same reason.
- **The public request form and the partner API do not check invitations.** They refuse an email that is already a registered guest or already requested, as before, but a person an admin has already invited can still **submit** a request. It is only refused when someone tries to accept it. Stopping it at the form would be a separate change (the public email lookups are already an open security question).

## 4. Effects on dignitary parties

- **A dignitary naming someone who already has an invitation** (in their own registration form): that person is **skipped quietly**. The dignitary's registration still succeeds, and the person keeps the invitation they already have.
- **Two dignitaries naming the same person:** only the first one creates an invitation. The person appears in **the first dignitary's party only**, because a party lists the invitations made on that dignitary's behalf.
- **"Invite someone" on the Dignitary page** (by the team): refused with "This email is already invited."
- **The same dignitary naming the same person again** in the same role still returns their existing invitation, so a re-send works as before.

## 5. What to check

Use the test (development) admin. Write **Pass** or **Fail** in the last column.

| # | Steps | Expected result | Pass / Fail |
|---|---|---|---|
| 1 | Create collection **A** with a guest `test1@example.com` | Saved | |
| 2 | Create collection **B**; on a manual card type `TEST1@example.com` | Red under the field: "This email already has an invitation". Create is refused | |
| 3 | In one Create, use the same new email on two cards | "Duplicate email" | |
| 4 | Create **B** from an Excel file that includes `test1@example.com` | That row is red, the preview says "1 already invited", Create opens the problems dialog | |
| 5 | **Add people** to an existing collection with `test1@example.com` | Refused | |
| 6 | Open another invitation, change its email to `test1@example.com` | Refused | |
| 7 | Edit that invitation's company only, keep its email | Saved | |
| 8 | **Move** invitations from one collection to another | Works as before | |
| 9 | File an invitation request with `test1@example.com`, then **Accept** it | Refused: "This email is already invited." The request stays pending | |
| 10 | **Bulk accept** that request with another one | The other is accepted; this one is listed as failed with the same reason | |
| 11 | On the **Dignitary** page, Invite someone with `test1@example.com` | Refused: "This email is already invited." | |
| 12 | Register a dignitary who names `test1@example.com` in their party | Registration succeeds; no new invitation for test1 | |
| 13 | Do any of the above with a brand-new email | Works normally | |

## 6. For developers

- **The rule:** `Invitation::alreadyInvited($emails, $exceptId)` (trimmed and lower-cased on both sides, any state, any collection).
- **Applied in:** `InvitationsController` (`store` and `addGuests` through `refuseInvitedEmails()`, which also refuses repeats inside the batch; `update` checks a changed email; `check-unique` checks every collection; new `POST /admin/invitations/check-emails-list`), `AdminInvitationRequestsController::accept` (409), `DignitaryParty::invite` (skip) and `DignitaryPartiesController::invite` (422).
- **Admin:** `invitations-form.tsx` (manual cards, Excel preview and problems dialog, import note), `table-add-info-modal.tsx` (edit). EN + AR.
- **Tests:** `InvitationEmailUniqueTest` (6) and one in `DignitaryPartiesTest`, all failing on the code before. Backend 1058 tests pass.
- **Commits:** backend `36a325c` (PR #39), admin `eb4b772` (PR #40), on `dev`. No migration.
