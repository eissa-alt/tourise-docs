# Task 067: CRM Speakers import, the team's new template and sessions in CRM Settings

- **Status:** `in-progress`: every question answered (2026-11-03 to 2026-11-04); **built 2026-11-04** on
  `feat/crm-speakers-import`, quality gates green, **committed and pushed** (backend `8407580`, admin `422c95c`);
  the three migrations run on the owner's local database. Next: the owner's browser check and the PRs into
  `testing`.
- **Opened:** 2026-11-03
- **Owner:** Eissa
- **Sub-app(s):** backend + admin
- **Branch(es):** `feat/crm-speakers-import` in `tourise-backend` (from `testing` `f0ca2df`) and `tourise-admin`
  (from `testing` `946bb7c`), `--no-track`

## Goal

The Speakers import follows the team's new template, and sessions become a list the team keeps in CRM Settings, so a
speaker can be in several sessions. The Contacts import is the reference for everything the two share (owner,
2026-11-03).

## Source

- The team's `Speakers_Import_Template.xlsx`, tab "Speaker Program V20": 32 headings, no rows, no dropdowns. Red =
  required, grey = optional (the team's note). Kept outside git, in `~/Projects/ALT/127-tourise/crm_updates_3_nov/`.
- The file also has a hidden tab, "Speaker Program (V13)": the old programme, 544 real rows, passport numbers and
  headshots included. **Not used, not uploaded** (decision 11).
- Builds on [Task 059](../059-crm-speakers-and-dashboards/TASK.md) (the Speakers tab and import), Imtinan's 2026-10-27
  change (speakers are Speaker-category contacts, their own fields in `crm_speaker_details`) and the Contacts import of
  [Task 054](../054-prospects/TASK.md) (decisions 58, 61 to 64, 70).

## Decisions (the team and the owner, 2026-11-03 to 2026-11-04)

| # | Topic | Decision |
|---|---|---|
| 1 | Speaker column | Kept: the **media name**, which may differ from the real name (the client). Text, required. First Name and Last Name stay the real name, used by the invitation and the registration. |
| 2 | Tier | The contacts' **Tier 1 / 2 / 3**, required, with the contacts' View tier rules: an admin without View tier is not asked for it, and the import does not read it. |
| 3 | Passport | A **Passport Number** column in the speakers' sample (the team's "Passport" heading read as it). **The CRM saves it.** This reverses Task 059 decision 7 for speakers only: the Contacts file still refuses passport columns. |
| 3b | Who sees it | **Every admin who can open the CRM** (speakers): form, See more, table, Export, History. |
| 4 | Status columns | Status works **the same as contacts** (Tracking). Status, Invitation Status, Save the Date Invitations, Save the Date Status and Follow Up Status leave the template. An old file's cells stay with the row only, as today. |
| 5 | Follow up | Stays **Yes / No**. The team's "Follow Up Call/Text by" heading is read as Follow up. |
| 6 | Lists | Day, Pillar, Type and Continent stay the fixed lists we have, kept in code. Session moves to CRM Settings (decision 7). |
| 7 | Sessions | **Sessions are a list the team keeps in CRM Settings.** Each session has its own Day, Pillar and Keyword. **A session's name is unique** (case and extra spaces aside). A speaker has **one or more session lines**, each **Session + Type + Option #** (the team chose C). |
| 7b | Sessions in the import | The import takes **Session, Type and Option #**, all **required**, for one session line. **Each speaker once per file**, with exactly one session; a repeated email is refused. More sessions are added in Edit speaker. |
| 8 | Speaker Email | Required, the **speaker's own**. An office or assistant email goes in Contact Email. |
| 9 | Country | Files use the **CRM's country names** (the sample's dropdown). "USA", "UK", "KSA" are refused. |
| 10 | CRM ID | **Like contacts:** no CRM ID in the speakers' file, which **only adds**. A person already in the CRM is refused with "already exists, added by X". Updates go through **Export, then Update import**, which gains a Speakers mode and its own box. Point of Contact stays an optional column. |
| 11 | Hidden V13 tab | Not uploaded. |
| 12 | Add / Edit form | **The form follows the file**, as for contacts: one list of required fields. |
| - | Heading colours | Red = required, grey = optional (the team's note). |

## The speakers' file after this task

The team's V20 order, without Day, Pillar and Keyword (now on the session), the five status columns (decision 4) and
CRM ID (decision 10). Point of Contact stays beside the Relationship Owner, as today.

| # | Heading | Kind | Required |
|---|---|---|---|
| 1 | Session | a session in CRM Settings | yes |
| 2 | Type | fixed list (Panelist, Moderator, Presentation, Presenter, FE) | yes |
| 3 | Option # | whole number from 1 | yes |
| 4 | Speaker | text (media name) | yes |
| 5 | First Name | text | yes |
| 6 | Last Name | text | yes |
| 7 | Gender | the system's list | yes |
| 8 | Tier | Tier 1 / 2 / 3 | yes (with View tier) |
| 9 | Title | text (job title) | yes |
| 10 | Organization | text | yes |
| 11 | Country | the system's countries | |
| 12 | Continent | fixed list | |
| 13 | Notes | text | |
| 14 | Program Team Relationship Owner | text | |
| 15 | Point of Contact | an admin (name or email) | |
| 16 | Network to leverage | text | |
| 17 | Speaker Email | email, one person in the CRM | yes |
| 18 | Contact Person | text | |
| 19 | Official invite to be sent by | the system's Titles | |
| 20 | Contact Email | email | |
| 21 | Invitation Sent by | text | |
| 22 | Follow up | Yes / No | |
| 23 | Bio | text | |
| 24 | Passport Number | text | |
| 25 | Social Handles | text | |

Still refused in every CRM file (PDPL): national ID, ID number, iqama, date of birth, photo, picture, headshot.

## Build plan

### Backend

1. **Sessions in CRM Settings:** a new table `crm_sessions` (name, Arabic name, Day, Pillar, Keyword, on/off), with
   the name unique by its match key. Model `CrmSession` (not the website's agenda Session). Routes under
   `/admin/crm/sessions`: read with any CRM box, add / edit / switch off with `settings`, as the Settings lists.
2. **Session lines:** a new table `crm_speaker_sessions` (speaker, session, Type, Option #), one line per speaker and
   session. Read and written through the speaker, so each change is in the speaker's History.
3. **Data move (one migration):** the 57 sessions of `CrmFixedLists::SESSION` become CRM Settings sessions (English
   and Arabic names as today, Day / Pillar / Keyword empty for the team to fill). Each speaker's Session, Type and
   Option # become its first line. `down()` puts them back.
4. **New speaker fields** on `crm_speaker_details`: `speaker_name` (Speaker) and `passport_number`. Tier uses the
   contact's own Tier column (speakers are contact rows).
5. **The speakers' columns** (`CrmImportColumns::SPEAKER_COLUMNS`): the 25 above, the 11 required. The save rules,
   the form's markers, the template and the import read them, as for contacts.
6. **The import:** add-only, as contacts (an email already in the CRM: "already exists, added by X"); the session
   line from Session + Type + Option #; Passport Number allowed in the speakers' file only; Tier read only with View
   tier. This also ends the bug found on 2026-11-03 (below).
7. **The Update import** takes speakers: its own box `speakers_update_import`, the speakers' Export columns (CRM ID
   first), an empty cell changes nothing.
8. **Export, dashboard, filters:** sessions read through the lines (see defaults e to g); Tier and Passport Number
   added.
9. **The sample:** the 25 headings in red / grey, dropdowns for Session (switched-on sessions), Type, Gender, Tier,
   Country, Continent, Official invite, Follow up and Point of Contact.
10. **Texts, EN + AR:** the server messages for sessions, and the Bring back message saying "archived speaker" for a
    speaker.

### Admin

1. **CRM Settings:** a Sessions section: the list (name, Arabic name, Day, Pillar, Keyword, speakers in it), Add,
   Edit, switch off.
2. **Edit / Add speaker:** a Sessions card with lines (Session, Type, Option #; add and remove; at least one); the
   Speaker field; Tier (View tier only); Passport Number.
3. **See more:** the session lines, each with its session's Day, Pillar and Keyword; Speaker, Tier, Passport Number.
4. **Speakers table:** a Sessions column, Speaker, Tier (View tier), Passport Number; the Session / Day / Pillar /
   Type filters through the lines; a Tier filter.
5. **Import page (Speakers):** an Update speakers mode beside Add (with its box); the notes rewritten for the new rules
   (the old ones say "every column is required" and "an email already in the CRM is refused", both wrong now); the
   popup before the sample download in red / grey.
6. **Roles:** the new box's label. EN + AR in the same commit.

### Tests and test files

- Backend: `CrmSpeakersTest` and the import, export, dashboard and update-import tests for the new rules; the data
  move; Passport Number allowed for speakers and still refused for contacts; Tier with and without View tier; a
  speakers row meeting an ordinary contact refused. Today's CRM tests stay green.
- New speakers test files for Eissa, Rawand and Imtinan in
  `~/Projects/ALT/127-tourise/crm_imports_test/crm_speakers_tests/`, made by scripts in its `tools/`, checked through
  the API. The 25 Oct sets in `crm_import_tests/*-speakers` are retired (their file 01 fails since Follow up became
  Yes / No).

### Quality gate

Backend `composer qa`; admin `yarn type-check`, `yarn lint`, `yarn check:rbac`, `yarn build` (from a copy if the
owner's dev server is running).

## My defaults, to correct

| # | Default |
|---|---|
| a | A session's **Day, Pillar and Keyword are optional** in CRM Settings, so the 57 can start empty and the team fills them in. |
| b | **Sessions can be renamed** (the name stays unique). **Switched off only while no speaker is in them**, never deleted, as Invitation Channel. |
| c | The speakers' **old Day, Pillar and Keyword** (per speaker) stay in the database, unused and not shown; History keeps them. Nothing is copied into the sessions (no silent data edits). |
| d | **Export:** one row per speaker; the Session, Type and Option # cells list each line, separated by " \| ". |
| e | **The Update import does not change sessions:** sessions are changed in Edit speaker. Its session cells stay with the row. |
| f | **Dashboard:** Day, Pillar, Session and Type count speakers through their lines (a speaker in two sessions counts in each); the Pillar by Day table reads the sessions; a Tier card for View tier. |
| g | **Filters:** a speaker matches Session, Day, Pillar or Type when any of its lines does. |
| h | **Bulk edit** of speakers no longer offers Session, Day, Pillar or Type (lines are per speaker); Tier is offered, with View tier. |
| i | The sample's heading is **"Follow up"** (Yes / No); the team's "Follow Up Call/Text by" is still read as it. |
| j | **Passport Number** shows in the table like the other columns, and Columns hides it. Changed while building: the table remembers only what each admin hides, so "hidden by default" would have needed a new mechanism. |
| k | Colours: the contacts' red for required, the team's grey (`D9D9D9`) for optional. |
| l | The Arabic label for Speaker: "الاسم الإعلامي" (a draft for the team to check). |

## Found while checking (2026-11-03, run on the test database)

- **A speakers row whose email is an ordinary contact's** (a VIP, say) updates that contact's name, job title,
  company and notes, keeps it a contact, and drops the speaker fields the preview listed. Live on production. Ends
  with decision 10 (the file only adds).
- **The speakers' import page says** "an email already on a contact or a speaker is refused" (EN + AR): wrong today,
  the file updates that person. Rewritten in this task.

## Not touched

The website's Speakers, Sessions and agenda modules; mobile (every route here is under `/admin/crm`); the frontend;
the Contacts import's rules; Tracking and Invite (one invitation per person, not per session).

## Deploy (when it reaches a server)

`migrate` (the two new tables, the data move, the two new columns), `config:cache`, `route:cache`, `queue:restart`;
admin build and restart. Tick the new **Update speakers by import** box in Roles. The team checks the 57 sessions in
CRM Settings and fills in their Day, Pillar and Keyword.

## Log

- 2026-11-03: opened from the team's `Speakers_Import_Template.xlsx`. The Speakers import, the Contacts import (Task
  054 decisions and the git history) and the team's file compared; a bug and two wrong page texts found by running the
  import on the test database. Questions 1 to 12 sent to the team.
- 2026-11-04: every question answered; sessions move to CRM Settings with lines per speaker (the owner's flow, adjusted
  by the team). This plan written; the owner said to start building.
- 2026-11-04: **built** on `feat/crm-speakers-import`; committed and pushed on the owner's word (backend `8407580`,
  admin `422c95c`); the three migrations run on the owner's local database (batch 50, 57 sessions, no speaker to
  move).
  - Backend: migrations `2026_11_04_000001` (`crm_sessions`, the 57 seeded), `000002` (`crm_speaker_sessions`, each
    speaker's session moved to its first line) and `000003` (`speaker_name`, `passport_number`); `CrmSession`,
    `CrmSpeakerSession`, `CrmSpeakerSessions`; the speaker's `sessions` saved with it and said in History in words;
    the 25 columns; add-only import; the speakers' update import (box `speakers_update_import`); sessions in CRM
    Settings (`/admin/crm/sessions`); Export, filters, dashboard; EN + AR messages. `composer qa` green: Pint, PHPStan,
    1,744 tests (`CrmSpeakersTest` rewritten, 26).
  - Admin: the Sessions card in Add / Edit speaker (lines, add and remove), Speaker, Tier, Passport Number; See more's
    session lines; the table's Sessions column and Tier filter; CRM Settings' Speakers' sessions section; the import
    page's Update speakers mode, rewritten notes, red / grey colours, and the browser's passport check skipping the
    speakers' own column; the new box's Roles label; EN + AR. Type-check, ESLint, Prettier, `yarn build`,
    `check:rbac` green.
  - Test files: three sets of 8 files and Steps S, E, U, built and replayed through the API (every result as their
    README says), PDFs, the two zips.

## Definition of Done

- [x] Plan approved by the owner (the owner said to start; defaults as written, j changed while building)
- [x] Code on the task branch in backend and admin, committed and pushed on the owner's word
- [x] EN + AR translations in the same commit (in the change, to commit together)
- [x] Quality gate green
- [x] New speakers test files for the three testers, built and checked
- [ ] Browser check by the owner (the three migrations run locally 2026-11-04)
- [ ] Merged into `testing`; `migrate` on the testing server; the new box ticked in Roles
- [ ] Docs updated (this TASK.md, the index row, a HANDOFF line)
