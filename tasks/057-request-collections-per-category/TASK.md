# Task 057: Request collections per category

- **Status:** `in-progress`: built on `feat/crm-foundations` in backend and admin, committed locally, not
  pushed, not seen in a browser yet (2026-10-21). See *Log*.
- **Opened:** 2026-10-21
- **Owner:** unassigned
- **Sub-app(s):** backend + admin
- **Branch(es):** `feat/crm-foundations` in `tourise-backend` and `tourise-admin` (the Task 055 / 056 branch)

## Goal

Gap 5 of the owner's queue, the invitations flow. Today each request category has **one fixed
collection** ("Request" on production), and accepting always files the invitation there and sends that
request category's invitation template:

- An admin who accepts someone into VIP (the dialog's override) puts a VIP invitation into a collection
  labelled General Registration.
- Everyone accepted gets the same email ("General Registration - Invitation Email"), whatever category
  they are accepted into. The link is right (`/join/vip/...`), the email around it is not.
- Every accept rewrites the collection from the request category, so editing it in Collections does not
  last.

Instead (owner, 2026-10-21): **one collection per category, made the first time someone is accepted into
it**, the pattern dignitary parties already use (`DignitaryParty::collectionFor`). Nothing is set up in
advance for the 11 active categories.

## Decisions

All 2026-10-21, with the owner.

| # | Decision |
|---|---|
| 1 | **One request collection per category.** Accepting into a category files the invitation in that category's "From invitation requests" collection, found by its type (`source = invitation_request`) and its category, never by its name (the admin's to rename). If there is none, it is made then. |
| 2 | **Other collections are never used.** "Created manually" and "From dignitary parties" collections of the same category never receive accepted requests. |
| 3 | **The first accept asks for the template (option A).** When the category has no request collection yet, the accept dialog says so and asks for the invitation template of the channel; channel and sending account start from the request category and can be changed there. The new collection is named "Invitation requests - <category>", with " (2)" if the name is taken. |
| 4 | **After that, the collection decides.** Every accept uses the collection's channel, template and account. Editing them in Collections now lasts (accepting no longer rewrites the collection) and applies to invitations made from then on; invitations already made keep their own. |
| 5 | **What the request category keeps:** its form, the email code, the default target category and System Category, the holding and decline emails and the account they go from, the channel and account a new collection starts with, usage type, uses, prefill and lock. **What it loses:** its invitation templates and its link to one collection (columns dropped). |
| 6 | **Tier from the collection.** Accepted invitations take the collection's tier, set in Collections (not in the dialog). The System Category stays per invitation, as today. |
| 7 | **The category of a request collection cannot change**, since it is how the collection is found; the same for dignitary collections, which have the same hole. Neither needs a System Category of its own: they hold people of several. |
| 8 | **A type tag in the Collections list**, with the labels the Source filter already uses: Created manually / From invitation requests / From dignitary parties (EN and AR exist). |
| 9 | **A mixed selection without the override:** rows whose category already has a request collection go in; rows whose category has none are reported as failed ("accept one of them on its own first"). Production has one request category, so this is rare. |
| 10 | **Production:** the owner deletes the two current collections ("Request" and "Request An Invitation ( to be deleted)", 0 invitations each) in phpMyAdmin; there is no delete in the admin. The first accept into General Registration then makes its collection and asks for the template. |

## Build order

Each step merges on its own.

1. **Backend.**
   - Migration: drop `invitation_collection_id`, `email_template_id`, `sms_template_id` and
     `whatsapp_template_id` from `invitation_request_categories`.
   - Find-or-make the request collection per category, as `DignitaryParty::collectionFor`.
   - `accept` and `bulk`: without a collection and without a template, refuse with
     `reason: collection_needed` so the dialog can ask; in a bulk, the first row makes it and the rest
     find it. The invitation takes the collection's channel, template, account and tier.
   - New `GET admin/invitation-requests/target-collection?category_id=`, behind the `invitation_requests`
     box: that category's request collection (name, channel, template) or none, plus the starting values.
     Registered before `admin/invitation-requests/{id}`.
   - `syncInvitationCollection` removed, from the model, the request category save and accept.
   - Collection update: the category of a request or dignitary collection is refused if changed; no
     System Category required for them.
   - Tests through HTTP.
2. **Admin.**
   - Accept dialog: "Goes into <collection>, email <template>", or "New collection for <category>" with
     the template (required), channel and account.
   - Request category form: the template pickers go; the section keeps channel, account, usage, uses,
     prefill, lock.
   - Request categories list: the collection column goes.
   - Collections list: the type tag. Collection edit: the category locked for request and dignitary
     collections.
   - EN + AR.
3. **Docs.**

## Cases (backend tests, through HTTP)

1. The first accept into a category with no request collection and no template is refused with
   `collection_needed`; with a template it makes the collection (type, category, channel, template,
   account, name) and files the invitation in it, sent with that template.
2. A second accept into the same category files into the same collection without asking for a template.
3. An accept into another category makes a second collection.
4. A bulk of three into a new category makes one collection with three invitations.
5. A manual or dignitary collection of the category is never used.
6. Saving the request category touches no collection; a template changed on the request collection is
   used by the next accept.
7. A request collection's category cannot be changed; its System Category is not required.
8. The invitation takes the collection's tier.
9. A mixed bulk: rows whose category has a collection go in, the others fail with the message.

## Deploy

- The owner deletes the two current collections in phpMyAdmin (either side of the deploy; both have 0
  invitations). If someone accepts before the new code is live, the old code makes a new "Request"
  collection, and the new code takes it as General Registration's.
- `php artisan migrate` (drops the four request category columns).
- Tell the team: the first accept into each category asks for the invitation template.

## Log

- 2026-10-21: opened, with the owner's decisions 1 to 10. Approved the same night.
- 2026-10-21: built and committed locally (backend `e62f4a4`, admin `af423c8`), not pushed. Gates: backend Pint + PHPStan clean, 1325 tests (10 new in
  `RequestCollectionsTest`, two accept tests in `SubCategoryWritePathsTest` now pick a template); admin
  `tsc` + `eslint` + `prettier` + `check:rbac` green. **`yarn build` not run**: the owner's admin dev server
  was running, and the two share `.next`.
  - **Backend:** migration `2026_10_21_000001`; `App\Support\RequestCollections` (`for`, `startingValues`,
    `newSettings`, `make`); accept and bulk file into it (`reason: collection_needed` without one and
    without a template; a mixed bulk forwards no template); `GET admin/invitation-requests/target-collection`;
    `syncInvitationCollection` and the request category's collection link and templates gone; the collection
    update refuses a new category on request and dignitary collections and needs no System Category for
    them (`messages.collection_category_fixed`, EN + AR); the collection resource returns `source`.
  - **Admin:** the accept dialog shows the collection and its email, or asks for the new one's channel,
    template and account; the request category form keeps channel + account under "Invitation settings";
    the request categories list loses its collection column; the Collections list shows the type tag (one
    label map for the filter and the tag); the collection edit form locks the category for request and
    dignitary collections. EN + AR.
  - **Where the build differs from the plan:** the dialog says "this category" rather than naming it; a
    mixed selection gets a one-line note that rows into a category with no collection are skipped.

## Definition of Done

- [ ] Code merged to `dev` in backend and admin
- [x] EN + AR translations in the same commit
- [ ] Quality gate green (backend `composer qa`; admin `yarn type-check` + `yarn build` + `yarn check:rbac`)
- [x] The cases above covered by backend tests, through HTTP
- [ ] Docs updated (this TASK.md, the index row)
- [x] Mobile contract checked (admin routes only)
- [ ] Seen working in a browser, by the owner
