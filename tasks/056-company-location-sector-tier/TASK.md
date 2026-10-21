# Task 056: Company Location, Sector and Tier on the guest

- **Status:** `in-progress`: built on `feat/crm-foundations` in all three apps, committed locally, not
  pushed, not seen in a browser yet (2026-10-20). See *Log*.
- **Opened:** 2026-10-20
- **Owner:** unassigned
- **Sub-app(s):** backend + admin + frontend (the public forms)
- **Branch(es):** `feat/crm-foundations`, the Task 055 branch, in `tourise-backend` and `tourise-admin`
  (owner, 2026-10-20: same branch); a branch of that name off `dev` (`--no-track`) in `tourise-frontend`

## Goal

Three fields the client's sheets ask for and the system does not hold (the gaps after Task 055):

- **Company Location** (Local / International) and **Sector** (Public / Private): on every registration
  form, "added at Fahad's request 5th of Oct, to support reporting on market" (Master 07.10, all 10 form
  sheets, in [`client/CRM_PLAN_V2/`](../../client/CRM_PLAN_V2/)).
- **Tier** (Tier 1 / 2 / 3): the client's "approved master list" signed off by Fahad, admin only, never
  guest-facing (v4.1 Field List).

None of the three is CRM-only (owner, 2026-10-20): they live on the guest, and the CRM (Task 054) uses the
same fields.

## Decisions

All 2026-10-20, with the owner.

| # | Decision |
|---|---|
| 1 | **On the guest, not CRM-only.** Plan V1 had Company Location and Tier in the CRM only, and took Sector as already on the guest; it is on no form in use (only the unused four-step form). |
| 2 | **Values.** Company Location: `local` / `international`. Sector: **Public / Private only**, the two keys the list already has (`public_sector`, `private_sector`); the other three go from the list. No guest holds a sector today, so nothing to convert. Tier: `tier_1` / `tier_2` / `tier_3`. |
| 3 | **Which forms.** Company Location and Sector go on the 10 registration forms the categories use (General Registration, Media, Dignitary, Dignitary Delegation, Security, Protocol, VIP, Sponsor, Speaker, Moderator) and their admin add / edit forms. **Not** on Request an Invitation. The unused shapes stay as they are for now (Default, One Step RSVP, Tourise Private, Four Steps); the four-step form keeps its sector field, with the two values. |
| 4 | **Mandatory is the category's choice.** Neither is hard-coded as required: both become options in the category's mandatory-fields pickers (`data/mandatory-fields-by-form-shape.tsx`), user side and admin side, and each form reads them as it reads every other field. |
| 5 | **Labels.** "Company Location" / "Sector"; on the Media form "Organization Location", as the client's Media sheet says. Tier in Arabic: **"تير"** (owner), values "تير 1 / 2 / 3". |
| 6 | **Position.** The client's order: Company Location right after Company, Sector right after Mobile. |
| 7 | **Reporting.** A column and a filter on the guest list; the last column in the guest exports (the house rule); Local / International and Public / Private on the dashboard. |
| 8 | **Tier has its own box, "View tier"** (`guests_listing`, `view_tier`). Without it an admin sees no tier anywhere (column, filter, form field, export column, dashboard), and the backend ignores a tier filter or a tier value they send, so a tier cannot be read by filtering. Roles start unticked: Super Admins see it. |
| 9 | **Where Tier is set.** The admin guest add / edit form (one field in the shared wrapper, as the System Category); the collection (copied to each invitation it makes), changed per invitation (single edit, Update bulk); a registration through an invitation carries it to the guest. Never on a public form. |
| 10 | **Automations need nothing of their own.** Their guest picker is the guest list's filter panel and backend (`SearchGuestsBySuper`, `applyFilters`, `select-ids`), so the tier filter works there as it is. No "set tier" action. |
| 11 | **Dashboard per tier**, behind the box. |
| 12 | **Left for the CRM:** "Tier 1 declines escalate the same day" (a notification to owners). |

## Build order

Each step merges on its own.

1. **Backend.** Migration: `company_location` and `tier` on `guests`, `tier` on `invitations` and
   `invitation_collections` (all nullable). The value lists checked on every write. Company Location and
   Sector saved by public registration and the admin create / update; Tier by the admin forms, the
   collection and invitation paths (create, edit, Add people, Update bulk; Move and Extract keep each
   invitation's own) and inherited at registration and decline. The `view_tier` box: resources leave tier
   out, filters ignore it, exports drop its column, writes ignore it, for an admin without the box. Guest
   filters for all three; the export columns; dashboard counts. Tests through HTTP.
2. **Public forms (frontend).** The two fields on the 10 forms, in the client's position, required when the
   category marks them; the Media label; `sector-types-select` to the two values (frontend and admin
   copies). EN + AR.
3. **Admin.** The mandatory-fields catalogue for the 10 shapes; the two fields on the 10 admin forms and
   their See more panels; Tier in the guest create / edit wrapper; the list columns and filters; Tier on the
   collection form, single edit, Update bulk and the invitation listings; the "View tier" label in Roles;
   the dashboard filters and counts. All of Tier behind the box. EN + AR.
4. **Docs.**

## Cases (backend tests, through HTTP)

1. Registration saves Company Location and Sector; a value outside the list is refused.
2. A registration through an invitation takes the invitation's tier; a public form's tier is not read.
3. An admin with the box sets and reads a guest's tier; one without sees no tier in the guest, the list or
   the export, and a tier filter or value they send is ignored.
4. A collection's tier is copied to each invitation; Add people takes it; Update bulk sets it; Move and
   Extract keep each invitation's own.
5. The guest list filters by Company Location, Sector and Tier (the last only with the box).
6. The exports end with the new columns; the tier column only for an admin with the box.

## Deploy

- `php artisan migrate`.
- Tick "View tier" on the roles that need it (it starts unticked); tell the team.
- Each category marks the two fields mandatory or not in its settings, if wanted.

## Log

- 2026-10-20: opened, with the owner's decisions 1 to 12. Approved; built on the Task 055 branch.
- 2026-10-20: built, each step committed locally. Gates green: backend `composer qa` (1315 tests), admin
  and frontend `tsc` + `eslint` + `yarn build` (+ `check:rbac` on admin).
  - **Step 1** (backend `ede2db5`): migration `2026_10_20_000004`; `App\Support\GuestFieldValues` (the
    lists, `tierVisibleTo()`, the export columns); every write path; the `view_tier` box in resources,
    filters (the generic has / has no / duplicate filters too), exports and the dashboard.
  - **Step 2** (frontend `679f45a`): the two fields on the five form files behind the ten in use; the
    sector list to two values.
  - **Step 3** (admin `c052749`): mandatory-fields options, the five admin forms and See more, Tier in the
    guest wrapper, collection form, collection edit, single edit, Update bulk, list columns and filters,
    the dashboard breakdown (Sector shown for the first time), the Roles label.
  - **Where the build differs from the plan:** the exports write the stored keys (`international`,
    `public_sector`, `tier_2`), as they write gender and industry; the data coverage test expects it.
    Five form files carry the ten forms (VIP, the three dignitary attendants and Moderator wrap another).
- 2026-10-20: branch renamed `feat/system-categories` to `feat/crm-foundations` in all three apps (owner), before
  the first push: the branch stays open for the CRM requirements as they close, merged with `dev` as it goes.

- 2026-10-21: found while building Task 054: a tier change shows in a guest's History and in the invitations' (and
  now the CRM's) audit trails to any admin who can open them, with or without View tier. The owner chose to leave
  it as it is.

## Definition of Done

- [ ] Code merged to `dev` in backend, admin and frontend
- [x] EN + AR translations in the same commit
- [x] Quality gate green (backend `composer qa`; admin `yarn type-check` + `yarn build` + `yarn check:rbac`;
      frontend `yarn type-check` + `yarn build`)
- [x] The cases above covered by backend tests, through HTTP
- [ ] Docs updated (this TASK.md, the index row)
- [x] Mobile contract checked (nothing exposed)
- [ ] Seen working in a browser, by the owner
