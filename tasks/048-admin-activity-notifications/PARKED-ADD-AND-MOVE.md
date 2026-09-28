# Parked: add people to a collection, move invitations into a collection

**Status: parked by the owner on 2026-09-29.** Both are wanted, but neither is finished, so they are
held and not built on until picked up. They arrived in امتنان's backend commit `2ef2856` (2026-09-28)
together with the bell that [Task 048](TASK.md) replaces. They are **API only**: the admin has no
screen for either.

## What they are

| Action | Route | Permission | Method |
|---|---|---|---|
| **Add people to an existing collection** | `POST /admin/invitations/{collection}/add-guests` | `invitations,create` | `InvitationsController::addGuests` |
| **Move invitations into an existing collection** | `POST /admin/invitations/{collection}/move-to-collection` | `invitations,extract` | `InvitationsController::moveToCollection` |

Why they exist (from the commit): a collection was fixed the moment it was made. Inviting three more
people meant a second collection with its own counts; and Extract moves people into a **new**
collection, which suits splitting a set and not putting stragglers into the set they belong to.

Both already do some things right: new or moved rows take the **target collection's** channel,
templates and category; only open invitations move (`is_active`, `not_used`); the admin's category
scope applies (`adminMaySeeCollection`, `scopeToAdminCategories`); both collections' `total_invites`
are recounted; a shared-link (multiple) collection refuses added people.

## Gaps found on 2026-09-29 (read in code, not yet fixed)

**Add people (`add-guests`)**

1. **The invitations it makes have no registration-form link and no prefill.** `with_from` and
   `prefilldata` live on each invitation, default `false`, and are not set here (Create sets them).
   A guest added this way gets a link that opens no form. Fix: copy `with_from` from the collection's
   existing invitations, and `prefilldata = true` (Task 044: a single-use invitation always prefills).
2. **No "already registered" check.** Create refuses addresses that already belong to a guest.
3. **No 1000-per-request limit.** Create has `guests_list` `max:1000`.
4. **Points of contact are accepted but not validated.** `Arr::only(..., POC_FIELDS)` with no
   `Invitation::pocRules()`: an over-long value is a raw 500.
5. **No check against people already in the collection.** Adding someone already invited there is
   a situation Create never meets.

**Move invitations (`move-to-collection`)**

6. **It lets invitations move into a shared-link (multiple) collection.** `add-guests` refuses that
   target; this should too.
7. **Moving an invitation that was already sent into a collection with a different category breaks
   its link.** The category is part of the link, so the guest's link stops matching (the same reason
   as the admin's `category_change_resend_note`). Needs a refusal or a clear warning.

**Both**

8. **Their audit rows are written through the old bell** (`AdminNotifier::record(...)`, actions
   `people_added` and `moved_to_collection`). When Task 048 removes the bell they become plain
   `AuditLog::record()` calls. The admin also has **no labels** for these two audit actions
   (`audit_action_people_added`, `audit_action_moved_to_collection`), or colours in
   `audit-log-entries.tsx`, so they would show as raw codes in the audit trail.
9. **Their 4 tests live in the bell's test file** (`AdminNotificationsTest`: people can be added; an
   added invitation takes the collection's own settings; people can be moved; a used invitation does
   not move). They move to their own file when the bell goes.
10. **No admin screens.**

## Open question when this is picked up

**How should "Add people" work in the admin?** (asked 2026-09-29, not yet answered)

- **The same input as Create** (Manual cards and Excel upload, with all the import checks, the
  problems dialog and POCs), adding to an existing collection instead of creating one. Recommended:
  one way of entering guests, which the team already knows.
- **Manual cards only**: simpler, but 50 people are typed one by one.

"Move to collection" would most naturally be a dialog like Extract (the shared bulk list, plus a
target-collection picker), under the More menu with its own permission box if wanted.

## Risk while parked

The two routes are on `dev` and would reach `main` with the next `dev` → `main` merge. With no admin
screen nobody reaches them in normal use, but gap 1 means any invitation made through `add-guests`
has no form link. Worth fixing gap 1 before that merge even if the rest stays parked, or keeping the
merge back until Task 048 lands (which touches these methods anyway).
