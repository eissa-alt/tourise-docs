# Task 057: Request collections per category

- **Status:** `in-progress`: revised (R1 to R5) and pushed on `feat/crm-foundations` (backend, admin), seen by
  the owner in a browser on their local copy (2026-10-21). Merged with the rest of the CRM work. See *Log*.
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

## Revision: targeted collections, no default (2026-10-21)

The owner tried the first build the same night and changed the flow: the template fields inside the
accept dialog were poor UX, and accepting should never follow a default. These replace decisions 3, 5 and
9, and narrow 1 (a collection is no longer made by accepting).

| # | Decision |
|---|---|
| R1 | **"Create targeted collection"**, a button on the Invitation Requests page (beside Request Categories). Its form: the category (only categories without one), its sub-category (from that category's list, required when it has one, always shown in the form; owner, 2026-10-21), channel (greyed when it has no enabled account), template (required), sending account (enabled accounts only, refused otherwise), tier (with the View tier box), usage type, uses, prefill, lock. It makes that category's "From invitation requests" collection, named "Invitation requests - <category>" (renamed in Collections if wanted). Still one per category. |
| R2 | **No default on accept.** The accept dialog asks only for the **targeted collection** (only those made by the button, showing the email and sub-category each gives). The sub-category is the collection's, not picked on accept (owner, 2026-10-21, replacing option A's per-accept change); one person's is changed on their invitation afterwards, as their category is. One choice covers the whole selection, so a mixed selection is no longer a case. The dialog creates nothing; a "Create targeted collection" link in it opens the same form. |
| R3 | **The collection decides everything about the invitation:** category, channel, template, account, tier, usage type, uses, prefill, lock. `invitation_collections` gains `uses`, `prefilldata`, `lock_data`; they are edited in Collections for a targeted collection. |
| R4 | **The request category is only the form and the applicant's emails:** basic information, form fields, email code, the holding and decline emails. The SMTP account moves up beside them, shown once in "When a request is submitted" ("also sends the rejection email"). **"Where they are invited" and "Invitation settings" go**: `target_category_id`, `target_sub_category_id`, `channel`, `sms_config_id`, `whatsapp_config_id`, `usage_type`, `uses`, `prefilldata`, `lock_data` dropped. |
| R5 | The request categories list loses its target category column. |

## Build order

Each step merges on its own.

**Rework (the revision):**

- **Backend.** Migration `2026_10_21_000002`: drop the R4 columns (the System Category's key first), add
  `uses`, `prefilldata`, `lock_data` to `invitation_collections`. `GET` and `POST
  admin/invitation-requests/targeted-collections` (list for the dialog; create, one per category,
  `invitation_requests,update`). Accept and bulk take `invitation_collection_id` (a targeted collection)
  and `sub_category_id`; the invitation takes everything else from the collection. The collection update
  saves `uses`, `prefilldata`, `lock_data` for a targeted collection. `target-collection`, the
  `collection` body and `RequestCollections::newSettings` / `startingValues` go. Tests rewritten.
- **Admin.** The button and its form (a modal); the accept dialog rebuilt (collection, System Category,
  the link); the request category form (two sections out, SMTP moved up); the list column out; the
  collection edit form shows uses, prefill and lock for a targeted collection. EN + AR.

**First build (kept where the revision does not replace it):**

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

After the revision:

1. Creating a targeted collection makes it with the category, channel, template, account and link
   settings; a second one for the same category, or one without a template, is refused.
2. The list returns only targeted collections, with the email each sends.
3. Accepting needs a targeted collection: none, a manual one or a dignitary one is refused.
4. The invitation takes the category, channel, template, account, tier, usage type, uses, prefill and
   lock from the collection, and the System Category from the dialog (required when the category has a
   list, refused when it is not that category's).
5. A bulk files every row into the chosen collection.
6. A template changed on the collection in Collections is what the next accept sends; its uses, prefill
   and lock are editable there.
7. A targeted collection's category cannot be changed; its System Category is not required.
8. The request category saves without a target, channel or link settings.

First build (replaced by the above):

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
  collection; delete it too, or create the targeted collections fresh.
- `php artisan migrate` (both migrations: the request category columns go, the collection gains its link
  settings).
- Create a targeted collection for each category requests are accepted into (Invitation Requests, "Create
  targeted collection"), before the first accept. Tell the team: accepting now asks which one.
- **What the migrations remove on production is settings, not data.** No guest, request or invitation
  changes; the pending requests stay pending. Production's "Request" request category today (dump of
  2026-10-19), to recreate as the General Registration targeted collection: target **General
  Registration**, no System Category, channel **email**, invitation email **"General Registration -
  Invitation Email"**, SMTP **"TOURISE 2027 - Request An Invitation"** (stays on the request category for
  the holding and decline emails), **single** use, **prefill on**, **lock off**.

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
- 2026-10-21: pushed (`feat/crm-foundations` in the three apps; owner merges once the whole CRM is final).
  The owner tried it in the browser and revised the flow: decisions R1 to R5 (targeted collections made
  by a button, no default on accept, the collection holds the link settings, the request category only
  the form and the applicant's emails). Also seen: the dialog showed the mixed-selection line for a single
  request (it lost the request's category); the rework removes that line.
- 2026-10-21: rework built, uncommitted. Backend: migration `2026_10_21_000002`;
  `TargetedCollectionsController` (`GET` / `POST admin/invitation-requests/targeted-collections`, enabled
  accounts only, one per category); accept and bulk take `invitation_collection_id` + `sub_category_id`
  (absent: the collection's default); the collection update saves uses, prefill, lock for a targeted one;
  `RequestCollections` reduced to `for`, `find`, `make`, `uses`. Tests: `RequestCollectionsTest` rewritten
  (11), three Task 055 accept tests folded into one; 1323 pass, Pint + PHPStan clean. Admin: the "Create
  targeted collection" button and modal (also opened from the accept dialog), the accept dialog rebuilt,
  the request category form down to form + emails with SMTP moved up, the list's target column out,
  uses / prefill / lock on a targeted collection's edit form, `toHideIds` on the category picker; the
  reject confirm no longer titled "Accept" for a bulk reject (it only knew `'reject'`); 13 translation
  keys left unused removed. `tsc`, `eslint`, `prettier`, `check:rbac` green; `yarn build` waits for the
  owner's dev server.
- 2026-10-21: after trying it, the owner took the sub-category out of the accept dialog: the targeted collection's
  is given to everyone accepted into it (required on a targeted collection whose category has a list, in its
  create form, always shown there, and its edit form; a dignitary collection still needs none). An accept
  whose collection's sub-category no longer fits is refused, naming the collection to fix. Also: the requests
  list in the nominations style (rounded checkboxes, icon actions, the selection card; "Move to category"
  hidden for now), the reject confirm shows the count, the category form's tabs smaller and its Save guard
  fixed (a double click sent two saves).
- 2026-10-21: committed and pushed. Backend `50420d3` (the sub-category rename), `5ebe4d5` (the revision);
  admin `0c6bdfd` (rename), `e7c864a` (category form: one save per click, compact tab), `b4abd45` (the
  revision and the requests list). Gates: backend 1323 tests, Pint, PHPStan; admin `tsc`, `eslint`,
  `check:rbac`, `yarn build` (built from a copy, the owner's dev server running). The owner merges
  `feat/crm-foundations` once the CRM is final.

## Definition of Done

- [ ] Code merged to `dev` in backend and admin
- [x] EN + AR translations in the same commit
- [x] Quality gate green (backend `composer qa`; admin `yarn type-check` + `yarn build` + `yarn check:rbac`)
- [x] The cases above covered by backend tests, through HTTP
- [ ] Docs updated (this TASK.md, the index row)
- [x] Mobile contract checked (admin routes only)
- [x] Seen working in a browser, by the owner
