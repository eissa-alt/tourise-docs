# Fork port-back — findings and TODO

**Date:** 2026-08-06
**Scope:** what we should copy back into `alt-static-basecode` from three clone projects
**Status:** analysis done, nothing ported yet

---

## 1. What this is

We cloned this baseline three times. Each clone found and fixed bugs. Those fixes stayed in the
clone. This document lists what is worth copying back, so the next clone starts from a better place.

The three clones:

| Project | What it is | Fork point | Its own commits |
|---|---|---|---|
| `122-gfeai-v2` | UNESCO Global Forum on Ethics of AI | 2026-07-08 | 220 backend / 173 admin / 100 frontend |
| `123-pif-pep-v2` | PIF Private Events Platform | 2026-07-28 | 10 / 11 / 4 / 2 seating |
| `124-ewc-2026-v2` | EWC 2026 | 2026-07-28 | 2 / 4 / 7 |

**Out of scope on purpose:** branding, colours, logos, fonts, SEO images, copy changes, and each
project's own form shapes. We only want fixes and features that any clone would benefit from.

---

## 2. How we checked

Three passes, 34 agents. Each pass fixed a mistake in the one before it.

1. **Pass 1 — commit by commit.** Read every commit in every fork. Then a second set of agents tried
   to *disprove* each finding by reading the baseline's own source. Two agents crashed mid-run and
   left gaps.
2. **Pass 2 — fill the gaps.** Read the 166 commits nobody had read. Also challenged the pep and ewc
   findings, which pass 1 had never checked.
3. **Pass 3 — file by file, not commit by commit.** Compared every shared component file directly
   between the baseline and each fork.

**Pass 3 mattered most.** Reading commits misses things, because a shared-component fix can hide
inside a commit whose title says "feat: rebrand". Comparing files directly found bugs that three
passes of commit-reading had walked past — including two that break the public registration form.

Every item below was checked against the baseline's actual source code, with a file and line number.
Nothing here is "the commit message said so".

---

## 3. What we found

**About 60 items worth porting.** Roughly a third are one-line fixes.

| Size of job | Count |
|---|---|
| One line | 17 |
| Small (one file, an hour or two) | 20 |
| Medium (a few files, half a day) | 8 |
| Large (needs planning) | 5 |

We also found **problems in the baseline that no fork fixes**. No amount of comparing forks would
have found these — they only turned up because agents audited the baseline directly. They are in
section 8.

### Three things to know first

**1. The invitation link dies after one use.**
A multi-use invitation for 50 people stops working after the first person registers. Worse: the
check is not scoped to the invitation, so if that email address ever registered anywhere else on the
site, the link never opens at all — not even once.

**2. The "complete your data" email link creates a duplicate guest.**
The guest clicks the link, fills the form, hits Submit. Instead of updating their record, it creates
a second one. This is a link we email to real registrants.

**3. One admin endpoint returns a 500 error on every single call.**
`GET /admin/guest-data-offline` filters on a database column that does not exist. The code's own
comment already says the column is missing. It has never worked.

---

## 4. Do these first — the quick wins

All one-line or near-one-line. All verified twice. None depend on each other. Together they close
most of the high-severity list.

- [ ] **Fix the invitation link.** Move the "already submitted" check so it only runs when no uses
      remain. `InvitationsController.php:467` runs before the `remaining === 0` gate at `:475`.
      Copy from **ewc `e647bb9`** — it is the same fix plus a 127-line test.
- [ ] **Fix the endpoint that always 500s.** `GuestsController.php:3615` does
      `Guest::where('dinner_invite', 'yes')`. No migration creates that column. Remove the filter.
      Same phantom column is also used as a listing filter at `:216-221`.
- [ ] **Make gate check-in write `checked_in_at`.** `attend()` at `GuestsController.php:3585-3611`
      writes four other fields but not this one, so the Seating Manager and the admin both think
      nobody has checked in. From pep `976ae89`.
- [ ] **Fix the two upload paths.** `custom-file-input.tsx:212` posts to `/upload`,
      `custom-file-input-3.tsx:104` posts to `/upload-document`. Neither route exists under the
      admin API base. Real routes are `/admin/guests/upload` and `/admin/guests/upload-document`.
      Copy from pep `fd41aed` (fixes both) — gfeai only fixed one.
      **Also remove the fallback on the next line of each file.** It builds a public URL for a file
      stored on the private disk, so the preview breaks even after the path is fixed.
- [ ] **Delete two test backdoors.** `GuestsController.php:3732` throws a 500 when the token is
      `IUFRP3GYZ4ISPUEU`. `InvitationsController.php:441` does the same for `RWYI82IWDG`. Both are on
      public, unauthenticated routes. Both marked `// TODO: remove this test hook`.
- [ ] **Delete the `dd()` in committed code.** `GuestsController.php:2638`. Breaks our own rule 8.
      The method is not routed today, but it ships in every clone.
- [ ] **Un-comment the sidebar links.** `data/sidebar-links.tsx:437-444` hides `/conference`. The
      same block also hides `event_days` and `sessions`. All three pages exist, all three have
      routes and feature ids — they are just unreachable. Three dead features, one comment block.
- [ ] **Add a plain `build` script** to admin and frontend `package.json`. Today there are only
      `env-cmd`-wrapped variants, so neither app builds on Vercel or in CI. From ewc `557228b` /
      `28c79ee`.
- [ ] **Add a null guard to reCAPTCHA.** `app/Rules/ReCaptcha.php:36` is
      `return $response->json()['success'];`. If Google returns a non-JSON body or the network
      fails, `json()` is null and this throws — turning a bot-check failure into a 500 on admin
      login *and* public registration. From gfeai `eafd3e4`.
- [ ] **Raise the API rate limit.** `RouteServiceProvider.php:49` is still `perMinute(200)`. gfeai
      went to 300, then 500, under real load. Multi-step registration forms burst past 200.

---

## 5. TODO — 122-gfeai-v2

### Broken things users hit

- [ ] **Super Admins see no invitation collections and export empty files.**
      `InvitationsCollectionController.php:33/176/192` turn `null` into `[]`, then treat `[]` as "no
      access". A Super Admin has no category list, so they get nothing. There is no `is_super`
      bypass here, unlike `GuestsController::applyAdminGuestAccessFilter:368`.
      **The fork's fix is incomplete.** The same bug is in `InvitationsController::index`,
      `::getAllInvitations` and `::export`. Fix all four. From gfeai `7ce4225`.

- [ ] **The guests listing loses 9 filters when you turn the page.**
      Filter the list, click page 2, and page 2 comes back unfiltered while the filter chips still
      show. `guests-listing.tsx:247-292` rebuilds the URL from a hand-written list of 36 keys, but
      the search form pushes 43. The fix is one line — `searchQueries` on line 245 already holds
      the whole query. From gfeai `a4dab7a`.
      **Same file, related:** `print-logs.tsx` has the same pattern.

- [ ] **The "Reconfirmation" filter does nothing at all.**
      Pick Yes or No, hit Search, the URL changes, the results do not.
      `search-guests-by-super.tsx:216` pushes `reconfirmed_will_attend` into the URL, but
      `fetch-data-url.ts:83-126` has no parameter for it, so it never reaches the API.
      **9 keys total** are pushed but never forwarded. From gfeai `9ea56fd`.

- [ ] **Every email log row says "No".**
      Sent, Delivered, Opened, Clicked all show a grey "No" badge forever — including for messages
      that were definitely delivered. The backend now sends real booleans; the admin still compares
      against the string `'yes'`. **4 files, 14 comparison sites.** The correct helper already
      exists at `guest-sms-logs-listing.tsx:26`. From gfeai `7eff9cc` + `af620c0`.

- [ ] **Three columns are permanently blank.**
      React renders `true` and `false` as nothing, so you cannot tell the two apart. In the
      invitations listing (`:252` `render: row => row.is_sent`) and two badge/verified chips.
      Found by checking all 84 boolean columns against both apps.

- [ ] **Every dropdown in the admin freezes the page.**
      Open any select, action menu, export menu or filter, and the page will not scroll — and
      clicks outside the panel are swallowed, because the rest of the page goes inert.
      Headless UI 2.2.10 defaults `modal` to `true`; we never pass `modal={false}`.
      **14 sites across 13 files.** `ui-select.tsx` is the main one —
      `custom-select.tsx` is just a re-export of it, and 39 admin files import that.
      **Two fixes must land together:** `anchor="bottom start"` (gfeai `cd0a861`) stops the panel
      being clipped, `modal={false}` (gfeai `60c0e26`) stops the freeze. Porting `anchor` alone
      would likely *introduce* the freeze.

- [ ] **The public registration form has the same freeze.**
      No fork ever fixed this side. Three components —
      `countries-select-new.tsx:224`, `titles-select-new.tsx:165`, and the static select — back
      every dropdown a registrant touches. On a phone, tapping Country freezes the page.

- [ ] **Invitations form hides the real error.**
      A duplicate collection name comes back as a clear 422 message, but `invitations-form.tsx:469`
      logs it to the console and shows a generic "something went wrong" toast. Next 15's dev overlay
      then reports it as a crash. From gfeai `0be14a0`.

- [ ] **Invitations can be created for people who already registered.**
      These can never be redeemed — the register endpoint rejects duplicate emails and
      `guests.email` is unique. Needs the check server-side *and* in both admin fill modes (Excel
      and manual). From gfeai `4d4fed0` + `ec316cc`.

- [ ] **Invitation create writes NULL into three NOT NULL columns.**
      `prefilldata`, `lock_data`, `with_from`. Same bug we already fixed for `is_sent` in
      `1f3839d` — it missed these three. From gfeai `4d4fed0`.

- [ ] **Saving a title with Arabic gender names throws a 500.**
      `normalizeGenderSpecific` returns an array, the column is untyped `text`, and
      `TitlesResources` reads it back with `json_decode`. Needs `json_encode()` in **both**
      `TitlesController.php:88` (store) and `:149` (update).
      *Note: we previously believed P029.1 fixed this. It only fixed half.*
      Also add `?? 0` on `order` in update, and the 62-line test — we have **zero** title tests.

- [ ] **Export column letters point at the wrong columns.**
      Not "fragile" — already wrong. `GuestsExport.php:36-39` has `DATE_COLS = ['S','W']` labelled
      "Printed At / Created At", but S is *Source* and W is *Reconfirmed Will Attend*. The real date
      columns are M, Q, X. Same in `GuestsExportGuestView.php`, `GuestsExportView.php`, and
      `InvitationsCollectionsWithInvitationsExport.php` (where `COL_TITLE_FROM='Z'` runs the title
      converter over *genders*, blanking them).
      **28 classes in `app/Exports/` all use hardcoded letters. None use a lookup.**
      **Port the mechanism, not corrected letters** — a headings-based lookup (gfeai `5c39fd8` /
      `7ce4225`), plus the alignment test (gfeai `741ad17`). We have **zero** export tests today.

- [ ] **"Send test" is clickable while creating a template** and posts to
      `/email-templates/send-test/undefined`. From gfeai `b194523`.

- [ ] **Date fields say "required" when they clearly contain a date.**
      Type a real date that falls outside min/max and `masked-date-input.tsx:124-134` reports it as
      missing instead of out of range. 8 files, ~14 call sites. From gfeai `daee938`.

- [ ] **Download errors always show the generic 500 toast.**
      On a `responseType: 'blob'` request the real message ("no default SMTP config") is inside the
      Blob and never read. **7 call sites.**

- [ ] **Social-media modal sends bad data.** `order` goes as a string (backend wants an integer,
      422), `link` has no URL validation, and every platform tile draws a check mark, not just the
      selected one. From gfeai `b194523`.

- [ ] **Admin CSP blocks 8 social icons.** `soical-media-modal.tsx:43+` hardcodes them on
      **another ALT client's bucket** (`emails-alt.eu-central-1.linodeobjects.com`). It is never
      derived from env, so the CSP at `next.config.js:54` cannot cover it and all 8 render broken.
      **Do not copy gfeai's fix** — it widens the CSP to a wildcard bucket host, which undoes our
      env-derived design. Move the icons to the project's own storage instead.

### Missing features

- [ ] **Add an `is_sent` filter** to the invitations listing (backend + admin). gfeai `12f6a62` /
      `7effa14`.
- [ ] **E-visa bulk download** — selected / filtered / all pages / in-progress only, as one zip.
      Today "Download all" fires one browser download per guest and browsers block the burst.
      Paired backend + admin job. gfeai `01582a2`, `2f917ec`, `48b8578`, `528c977`, `b6b84b9`.
- [ ] **Clone an email template** (with its attachments). We already clone categories, SMTP configs
      and badges — templates are the gap. Paired backend + admin. gfeai `1a423f5` / `3f97f70`.
- [ ] **Bulk missing-data notify** — `POST /admin/guests/notify-bulk` with a sent/skipped tally.
      Hidden inside a commit titled "feat: rebrand". gfeai `4c6187e`.
- [ ] **Harden base64 uploads.** `UploadService.php:61` takes the file extension from whatever mime
      the caller declares, with no allow-list — `data:x/phtml;base64,…` writes a `.phtml` file to
      the **public** disk. There is also no size limit. 4 call sites are affected.
- [ ] **Skip reCAPTCHA outside production** (opt back in with `RECAPTCHA_ENFORCE`). Local dev
      currently cannot log in or register. gfeai `eafd3e4`.
      ⚠️ That commit also reports that the backend's Google secret is Google's **test** secret and
      does not match the site key the apps use. We could not verify this (we do not read `.env`) —
      **please check before enforcing reCAPTCHA in production.**
- [ ] **Multi-file upload input** with in-browser image downscaling. gfeai `df4c152`.
- [ ] **Searchable guest-type picker** instead of an unbounded card list. gfeai `c127e36`.
- [ ] **Per-option help text on radio groups** — `custom-radio-input.tsx` can only show one shared
      label and only lays out horizontally. gfeai `03d2411`.
- [ ] **Scroll hint on listing tables.** Every listing is a fixed 1120px table; on a laptop the
      Actions column (Edit/Delete) is off-screen with nothing indicating it. **46 components import
      `ListingTable`** — one edit fixes all of them. gfeai `cd0a861`.
- [ ] **Show consumed uses / limit** on the invitations listing instead of a raw send count.
      gfeai `5520a33`.
- [ ] **Bulk guest hard-delete by email list**, with preview and a workbook export. Operator tool.
      gfeai `e1273d4`, `c4dfcbc`, `382b13d`.
- [ ] **Tests we do not have:** first coverage for the invitation store endpoint and the guest
      listing filters. gfeai `4d4fed0`, `6622fcc`.

### Public registration form (frontend)

- [ ] **The complete-data link creates a duplicate guest.**
      `complete-data/[category]/[token].tsx:57` passes `onCustomSubmit`, and
      `renderFormSteps.tsx` forwards it at `:155` and `:217` — but only
      `one-step-rsvp/step-1.tsx` actually uses it. `one-step/step-1.tsx:204` and
      `fours-steps/step-4.tsx:90` just POST to `guests`. **2 of our 3 form shapes.**
      From gfeai `6b15463`.

- [ ] **Prefilled forms reject the guest's own email.**
      `isUniqueAttribute(...)` is called with the mode hardcoded to `'create'`, so the check matches
      the guest's own row and blocks submit. The guest id is already being passed — only the mode is
      wrong. 3 call sites. From gfeai `3499a55`.

- [ ] **The completion page marks every field required**, because it passes no optional/mandatory
      lists. From gfeai `3499a55`.

- [ ] **The country dropdown silently wipes a saved country** that is no longer in the list — on
      the prefilled complete-data form, which is exactly where it hurts.

- [ ] **Two-step form shapes strand the user.** `renderFormSteps` step-2 branch is not
      last-step aware, so the guest submits, the record is created, and nothing happens next.
      **Fixed independently in both gfeai and ewc** — two forks hitting it is a strong signal.

- [ ] **Admin-controllable privacy consent** — today the consent checkbox is hardcoded per shape,
      one shape has none, and one records consent silently. gfeai `bfebdfc` / `0bef709`.

### Big jobs — decide before starting

- [ ] **DB-driven mandatory-field catalogue (`form_shape_fields`).**
      Today the field lists are hardcoded in the admin and frontend bundles. gfeai moves them into a
      table, serves them over the API, and enforces them server-side.
      **This sits right on the "no forms business logic" line.** The catalogue and the enforcement
      are architecture; the per-shape field lists are project data. Worth its own task.
- [ ] **Split the completion flow into purpose-scoped tokens (`completion_tokens`).**
      Replaces one-row-per-email token tables. Only relevant if we keep logistics.
      ⚠️ Related bug found on the way: sending a test email **silently invalidates the completion
      link already sitting in a guest's inbox**.

---

## 6. TODO — 123-pif-pep-v2

- [ ] **Fix the always-500 offline scanner endpoint** and the dead dinner filter — see section 4.
- [ ] **Write `checked_in_at` on gate check-in** — see section 4.
- [ ] **Fix the seating chair overlap.** The seating app draws chairs on top of each other at every
      table corner — 0px apart on U-shape tables, 55.1px apart for a 56px chair on rectangles once
      `headSeats >= 2`. pep `8c39930`.
- [ ] **`GuestSeatingObserver`** — sends seat-assigned, seat-changed and check-in notifications
      across all three channels, with bulk-send suppression and previous-seat capture in the same
      UPDATE. Needs a `guests.previous_seat` column. pep `c941802`. *(Large.)*
- [ ] **Per-admin filter visibility.** One button on the filter row opens a picker; each admin hides
      the filters they never use. Stored on `admins.preferences`, keyed by route, so it follows them
      to another device. Saves *hidden* keys, so filters added later stay visible by default.
      **`ListingFilters` is used by 44 listings**, so they all get it with no call-site changes.
      The guests listing needed extra work — `FilterSlot` self-registers so its 24 hand-written
      filters appear in the picker too. pep `fd41aed`. *(Large.)*
- [ ] **`admins.preferences` column + `GET/PUT /admin/me/preferences`.**
      ⚠️ **pep's routes have no `auth.admin` middleware**, so a mobile guest token can reach an
      admin write. Add it when porting.
- [ ] **Fix the offline-sync foreign key bug.** The round-trip writes an email string back into
      `scanned_by`, which is a UUID foreign key. pep touches this method without fixing it.
- [ ] **`withoutNotifications` wrapper** for bulk drains — generic suppression so a bulk sync does
      not fire a notification per row. pep `c941802`.
- [ ] **WhatsApp: full set — see section 7.**
- [ ] **`NotificationEventFields`** — renders one notification event's three channels (email, SMS,
      WhatsApp) as a reusable block. Today `categories-form.tsx` hand-writes ~500 lines for three
      events; adding a fourth means copying it all again. pep `fd41aed`.
- [ ] **`admins.is_vip` flag** — independent of role. Small migration + form toggle + a live-resolved
      `actor_is_vip` on the seating audit log, highlighted in the seating app's notification panel.
- [ ] **Seat/table number in the default see-more panel** — present only on the RSVP shape today.
- [ ] **Favicon components reference three assets that are not in `public/`**, while the real ones
      go unreferenced.

### ⚠️ One pep change is NOT safe to port as-is

**`PUT /admin/guests/attend` single check-in rewrite.** `attend()` returns the whole Guest model, so
changing it changes what the **out-of-repo iPad scanner** receives. This is not the Flutter app.
Check `docs/mobile/BACKEND_INCOMING_CHANGES_FOR_MOBILE.pdf` and get owner sign-off first.
(Adding `checked_in_at` is additive and safe; the wider rewrite is not.)

---

## 7. WhatsApp — the full pep list

pep did **not** change the WhatsApp integration. The sender, webhook, OTP, listeners, logs, provider
configs and routes are byte-identical to ours. What pep improved is the **template layer**.

That is because pep forked *after* we built the whole WhatsApp stack ourselves (P24.1–P24.27). It
inherited a complete integration and had nothing to fix in it.

**11 files across 5 commits** (`9b71528`, `976ae89`, `c941802`, `4633938`, `57218c4`, `fd41aed`):

**Backend**

- [ ] **`WhatsAppTemplateRenderer.php` (+111 lines)** — adds 11 new variables:
      - `app_name` — reads `app_name_en` / `app_name_ar` from the `conferences` row, falls back to
        `config('app.name')`. Memoised. Resolves for real even in a test send, so an admin checking
        credentials sees the actual name.
      - `event_name`, `event_date`, `event_start_date`, `event_end_date`, `event_datetime`,
        `venue`, `venue_url` — from the same `conferences` row. Dates render in the target language,
        so Arabic sends get Arabic month names. Multi-day collapses to a `start - end` range.
        **An empty row gives empty strings, not the raw variable name** — a blank slot reads better
        than "event_date" in a live message.
      - `seat_number`, `table_number`, `checkin_time` — from the guest row. `checkin_time` prefers
        `checked_in_at` and falls back to `check_in_time`.
      - All merged into **both** the invitation and guest send paths.
- [ ] **`WhatsAppTemplatesSeeder.php` (new, 245 lines)** — 8 templates keyed on `purpose` via
      `updateOrCreate`, so re-running updates in place. **`is_active` mirrors the template's real
      status at Meta**, so nothing that would fail on send ships switched on. Its docblock also
      warns about a real trap: the webhook picks the post-RSVP follow-up by `purpose='qr'` +
      `latest()`, so two active rows make that a coin flip.
      *Port the structure; drop the `pep_*` rows, they are project content.*
- [ ] **`DatabaseSeeder.php`** — register the seeder.

**Admin**

- [ ] **`whatsapp-variables-select-ordered.tsx` (new, 243 lines)** — an ordered picker. Position
      **is** the Meta `{{n}}` placeholder, which is why it is deliberately not the existing
      `CheckboxDropdown` (that returns values in option order, not selection order, and would
      silently remap the template). Unknown saved names are kept and flagged amber, never dropped.
- [ ] **`data/whatsapp-body-variables.ts` (new)** — catalogue of the 18 names the backend can
      actually resolve, each tagged `scope: both | invitation | guest`.
- [ ] **`whatsapp-templates-form.tsx` (+73)** — replaces the free-text comma list. Today a typo
      ships a literal variable name to Meta with nothing flagging it.
- [ ] **`notification-event-fields.tsx` (new, 128 lines)** — WhatsApp as one of the three channels.
- [ ] **`categories-form.tsx` (+118)** — seating events (`on_check_in`, `on_seat_assigned`,
      `on_seat_changed`), each with `whatsapp: { enabled, whatsapp_template_id }`.
- [ ] **`interfaces/category.tsx` (+38)** — the types.
- [ ] **`data/sidebar-links.tsx` (+20)** — the `/conference` link. The conferences page feeds
      `app_name`, `event_date` and `venue`, so it has to be reachable once the renderer work lands.
- [ ] **Translations EN + AR** — 4 keys: `body_variables_add`, `_empty`, `_custom`, `_unsupported`.

---

## 8. TODO — 124-ewc-2026-v2

- [ ] **Invitation link fix + the 127-line `InvitationLinkTest`** — `e647bb9`. **Take this version,
      not gfeai's.** It keys purely on `remaining`, and it comes with tests. It also documents why
      gfeai's first attempt (`21037e6`) was wrong: gating on `usage_type` still blocked
      number-of-use invitations whose `usage_type` was `single` or unset.
- [ ] **Plain `build` script** — see section 4.
- [ ] **Derive `is_saudi` from the ISO country code**, not the country's display name. Today it
      matches a localized label, so it breaks in Arabic. The shared country select cannot even
      expose the code — that needs adding. `dcee22e` / `38b4209`.
- [ ] **Two-step form dead end** — see the gfeai frontend list; ewc fixed it too.
- [ ] **`DATE_COLS` in the guest export point at the wrong columns** — folded into the export
      mechanism job above.
- [ ] **Favicon tags reference three assets that do not exist** in the repo.

---

## 9. Problems in our own baseline — no fork fixes these

Found by auditing our code directly. No fork comparison could have surfaced them.

- [ ] **Two forced-500 test hooks on public routes** — see section 4.
- [ ] **A `dd()` in committed controller code** — see section 4.
- [ ] **Public, unauthenticated, unthrottled `/pdf/{id}` routes.** `routes/web.php:24-25`. The `web`
      middleware group has no throttle and no auth. Each request runs Imagick + PDF rendering and
      **writes a new file to public storage**. Anyone can call it in a loop.
- [ ] **Five unrouted OTP endpoints that skip reCAPTCHA.** In `AuthController` — one has the
      reCAPTCHA rule commented out. Each mints an email-verification token. Not routed today, so it
      is a latent bypass, not a live one. Delete them or gate them.
- [ ] **Hardcoded buckets belonging to other ALT clients**, on live render paths:
      - `GuestsController.php:3256` — a **devego** bucket, on `POST /generate-static-badges`
      - an **ims** bucket sticker URL on three badge-PDF paths
      - plus tourise, hci-2026, glmc, faf and `sec-emails` in PDF and email templates
      Every clone renders client-facing PDFs pulling images from a different customer's storage.
      **The fix mechanism exists in gfeai `60ba649`** — `config/pdf.php` keys, env-backed,
      defaulting to null. Port the mechanism, then extend it to the buckets gfeai did not cover.
- [ ] **`X-Mailer` uses `env()` outside a config file**, so it sends **empty under `config:cache`**
      — i.e. in production.
- [ ] **20 export classes duplicate the same row-number binder** with no shared trait.
- [ ] **`composer.lock` is untracked in all four backend repos.** Every clone's `composer install`
      resolves fresh versions. Non-reproducible builds, and no supply-chain pinning — which sits
      awkwardly next to the OWASP hardening this baseline advertises. *(No fork fixes this either;
      noting it as a decision to make.)*
- [ ] **Admin, frontend and seating have zero automated tests, and there is no CI in any of the 18
      repos.** The backend has 24 feature test files. Most of the bugs in this document are
      client-side, where we have no coverage at all.

---

## 10. What we decided NOT to port

Each of these was checked and rejected with evidence.

| Item | Why not |
|---|---|
| **SMS non-production guard** | We removed this **on purpose** in P23.2 (`28eca40`) on 2026-07-23, *after* gfeai forked. gfeai never added it — it just never got our removal. Porting it would reverse a deliberate decision. **Raise as an owner question, not a port.** |
| **CSP `connect-src` for reCAPTCHA** | Contested — see section 11. |
| **Route shadowing fixes** (`2f21800`, `d4ed8cd`) | Fork-native. An agent wrote a route-table parser, proved it against gfeai's pre-fix file (found exactly the 4 routes gfeai later fixed), then ran it on ours: **0 shadowed across 467 routes.** Note the reason is *declaration order*, not `whereUuid` — 65 of our routes have unconstrained params and are safe only because their literal siblings come first. |
| **Duplicate PUT / guest-edit 500** (`b0f275a`) | **0 duplicate routes** and **0 routes pointing at a missing handler**, across all 467. |
| **Email-log boolean filters, backend half** | We fixed this independently in P23.11 (`7eb1e54`) — five days *before* gfeai did, in both controllers, for all four filters. **The admin half is still broken** (section 5). |
| **`/join` landing page** | The fork's version is a 35-line empty shell. |
| **Most gfeai work before 2026-07-22** | We built the same things in parallel. Reading all 166 unread commits found only 8 real gaps, all listed above. |

---

## 11. Still unanswered

- **Does our CSP block reCAPTCHA on admin login?** Two agents, opposite conclusions, both citing
  source. One proved the wrapper only injects a script (which `script-src` already allows) and makes
  zero `fetch`/`XHR` calls. The other says `connect-src` at `next.config.js:55` cannot contain
  `google.com`, and points at three submit handlers that `await executeRecaptcha`.
  **Settle it in a browser, not from source.** Open admin login with devtools and watch for a CSP
  violation. Adding the two Google hosts is cheap insurance either way.
- **Is the backend's Google reCAPTCHA secret the test one?** We do not read `.env`. Please check.
- **Some scope numbers are single-agent claims.** The audit was stopped before the verifying critic
  ran. The counts of 14 sites / 46 components / 44 listings / 7 blob call sites are probably right
  but unchecked. The findings themselves were all verified.

---

## 12. Notes for whoever does this

- **Order:** section 4 first. They are cheap, independent, and cover most of the high-severity list.
  Then the broken-things lists. Save the five large jobs for last — they need a decision, not a port.
- **Do not copy commits blindly.** Several fork fixes are incomplete or wrong for us:
  the invitation-collections fix misses three methods; gfeai's upload fix covers one of two files;
  gfeai's CSP fix would undo our env-derived design; gfeai's first invitation fix is superseded by
  its own later one.
- **Two ports need a mobile-contract check** before they land — see the warning in section 6 and
  hard rule 4 in `CLAUDE.md`.
- **Prefer porting mechanisms over values.** The export job is the clearest case: fixing the column
  letters leaves 28 classes ready to break again on the next column insert.
- Every claim here has a file and line number. If something looks wrong, open the file — that is
  faster than re-running the analysis.

---

*Analysis: three passes, 34 of 36 agents completed (2 stopped early — see section 11).
Nothing in this document has been ported yet.*
