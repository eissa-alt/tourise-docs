# Task 061: London Reception

- **Status:** `done` (Imtinan): on `main` from 2026-10-26 to 2026-10-28 and live on production at the latest with
  the 2026-10-29 release. Written on 2026-11-02 from her commits; **to check by Imtinan**. The RSVP dashboard page
  is marked temporary in the code, for easy removal.
- **Opened:** 2026-10-26
- **Owner:** Imtinan
- **Sub-app(s):** backend + admin + frontend
- **Branch(es):** `feat/london-reception` (backend PR #81, admin #76, frontend #23), `feat/london-reception-rsvp`
  (frontend #24, #25), `feat/london-reception-details` (frontend #26), `feat/london-reception-dashboard` (backend
  #97, admin #93), `fix/london-rsvp-page-simpler` (admin #96), `fix/london-page-no-latest-no-open` (admin #98),
  `fix/london-only-role` (admin #104) and `test/london-only-role` (backend #104)

## Goal

An RSVP for the TOURISE London Reception: its own category and form, the guest's yes or no kept apart from the
event's attendance, and a page for the team to follow the answers.

## How it works

- **Category:** London Reception (slug `london-reception`, shape `default-london-reception`, public), made by a
  migration if missing and seeded on a fresh database. Mandatory: first name, last name, email and the question.
- **The question:** "Would you like to attend TOURISE London Reception?" (EN + AR), kept in its own guest column
  `attend_london_reception` (yes or no). It is not `will_attend`: on the public form a `no` there would decline the
  registration and count against the event's attendance.
- **Public form (frontend):** titled RSVP, with the event's details in a card under the title; the success page says
  "Thank you for your response!" and has no Back to homepage.
- **Admin:** the shape in the category form, its Add and Edit form, its mandatory-field options, See more showing
  Yes or No; the answer is the last column of the guest exports.
- **RSVP dashboard (temporary):** Dashboard > London Reception, behind its own Roles box (London Reception
  dashboard): the Yes and No figures, a donut and the responses per day, Export PDF. The funnel, No answer, Open in
  Guests and Latest responses were taken off on 2026-10-28. A role with only that box can open it; the Dashboard
  link is hidden for it.
- **Migrations:** `2026_10_26_000001_add_attend_london_reception_to_guests_table`,
  `2026_10_26_000002_create_london_reception_category`.

## Log

- 2026-10-26: category, question, admin and public form, details card (PRs above, Imtinan).
- 2026-10-28: the RSVP dashboard page, then trimmed; the London-only role (Imtinan).
- 2026-11-01: a London Reception import came with the sub-events branch ([Task 060](../060-sub-events/TASK.md)),
  not merged.
- 2026-11-02: this record written from the commits (Eissa), for Imtinan to check.

## Open

- **For Imtinan:** whether the temporary dashboard page stays or goes, now that sub-events (Task 060) will hold the
  London Reception's RSVPs.
