# Task 070: the will_attend fill becomes a command; the London copy is dropped

- **Status:** `merged`: into `testing` (PR #162, `0f9be81`) and `main` (PR #163, `551d13e`) 2026-11-05 20:29;
  the server steps below are next.
- **Opened:** 2026-11-05
- **Owner:** Eissa
- **Sub-app(s):** backend
- **Branch(es):** `tourise-backend`, both `--no-track`, the same commit on each:
  - `fix/will-attend-fill-command` from `testing` `4b18283`: `c041887` (into `testing`).
  - `fix/will-attend-fill-command-main` from `main` `27a1738`: `564a452` (into `main`).
  The six files it touches were identical on `main` and `testing`, so the commit went onto both cleanly; a merge of
  the `main` branch into `testing` would have carried 53 commits only `main` has.

## The request (owner, 2026-11-05)

1. Delete migration `2026_11_05_000002_london_will_attend_follows_its_answer`: the existing London Reception
   registrations are not filled from their London answer.
2. Replace migration `2026_11_05_000001_set_will_attend_for_invitation_registrations` with a command that has a
   `--dry-run`, to see the guests it changes before changing them.
3. Leave the public registration as Imtinan wrote it (London registration is closed, so its London line runs for
   nobody today).

## Background

Imtinan's work of 2026-11-05 made accepting an invitation the guest's yes (`will_attend = yes`, commit `141db87`),
with `000001` filling the registrations already made. On production it failed (MySQL 8.4 error 1093); she fixed that
(main PR #158, testing PR #159), then made London registrations take their London answer, with `000002` copying it
onto the registrations already made (main PR #160, testing PR #161).

Checked on the production dump of 2026-11-05 11:55: the two migrations together would have set 180 guests to yes and
16 to no, 188 of them London Reception guests (175 yes, 13 no), and the CRM dashboard's Declined tile would have gone
from 3 to 16. The owner pulled `main` `27a1738` on production and did not run `migrate`.

## What changed

- Both migrations deleted. On production they never ran, so nothing is pending there any more.
- New command `php artisan guests:fill-will-attend [--dry-run]` (`app/Console/Commands/FillWillAttendFromInvitations.php`),
  the rule of `000001`: a website registration made through an invitation, still unanswered, not a partner named on
  someone's registration. Not the London Reception, and not anyone who came through a London invitation and was moved
  to another category since (4 guests now in Test; the team will delete them). `--dry-run` lists the guests (name,
  email, category, collection) and the count and changes nothing; without it, it sets them to yes and prints the
  count; run again, it changes nothing. Ids first, then the update (MySQL 1093).
- Tests: `WillAttendFromInvitationTest` runs the command (and a new dry-run test); `LondonWillAttendTest` as on
  `main`, its London check running the command, its `000002` test removed. The moved-to-another-category case has
  no test of its own.

## Production, after the merge

1. `git pull` (no `migrate` needed for this).
2. `php artisan guests:fill-will-attend --dry-run`: on the 11:55 dump it lists 1 guest (a personal invitation,
   registered before the live rule).
3. `php artisan guests:fill-will-attend`.

## Where the migrations already ran

`000002`: nowhere that matters (not production, not the testing server, not the owner's local database; probably
Imtinan's local one). `000001`: the owner's local database ran its first version (rolled back 2026-11-05 on the
owner's yes, record only: its `down` was empty, the yes values stay); the testing server may have run it too, which
leaves only a record there.

## Next

- Merged 2026-11-05 (testing PR #162, main PR #163). Next: production as above; on the testing server, `git pull`
  and the dry run (no `migrate` for this).

## Quality gate

`composer qa` green 2026-11-05 on both branches: Pint, PHPStan, 1,782 tests (`main` branch), 1,790 (`testing`
branch). Dry run checked on the owner's local database (0 there: its first `000001` had already set them).
