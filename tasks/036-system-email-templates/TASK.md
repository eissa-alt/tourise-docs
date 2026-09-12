# Task 036 — System emails become builder templates

- **Status:** `done (code)` — deploy + prod re-save + browser QA pending
- **Opened:** 2026-09-12
- **Owner:** Eissa
- **Sub-app(s):** backend, admin
- **Branch(es):** `dev`

## Goal

The client asked for the guest-OTP and admin-OTP emails to carry the same footer the email editor
produces. They could not: those emails were hardcoded blades, so the event's branding only reached
them through a developer. Instead of porting the footer markup by hand, the five system emails
became rows in `email_templates` and open in the same Waypoint builder as every other template.

## Scope

- **In:** `type` + `system_key` on `email_templates`; the five system templates seeded from the
  invitation template's own header/footer blocks; `SystemEmail::render()`; `resolveSystem()`;
  all five senders switched; 14 blade views deleted; a System templates tab; the builder opened in
  a modal with language + template switchers; the variable palette scoped and grouped; the
  header/footer/social/cta_color controls removed from the config screen.
- **Out:** retiring the now-unread `email_configs` columns (needs its own migration); a per-block
  text-direction control for mixed-language content; grouping the 15-chip guest variable list.

## Log

- 2026-09-12 — opened. Started as "fix the duplicate footer + make social icons uploadable"; the
  owner redirected to system-templates-in-the-builder, which retires that whole mechanism instead
  of improving it. The social-icon upload and arrow-reordering work built that morning was backed
  out deliberately, not lost to a mistake — see Decisions #1.
- 2026-09-12 — backend `c92ab56`, admin `1f0ee8e`. Both committed on `dev`, **not pushed**.
  Backend was re-committed after pulling a teammate's `f6e49ac` (equipment Word form); zero file
  overlap, gates re-run on the merged tree.

## Decisions

1. **The social-links feature was NOT improved — it was made redundant.** Icons live in the builder
   as image blocks now. `social_media_links` / `social_media_links_per_temp`, their controllers,
   routes and the per-template `override_social_links` switch are all still present but read by
   nothing. Left in place: removing routes touches the mobile contract, and the tables want their
   own cleanup task.
2. **One table, not two.** The builder, `content_{lang}` / `editor_json_{lang}`, the editor's
   load/save endpoints, send-test, attachments and clone already work against `email_templates`.
3. **`content_*` cannot be generated server-side.** The builder renders in the BROWSER
   (`handleSave` in `email-editor-waypoint.tsx`) and posts pre-rendered HTML; the backend never
   parses `editor_json_*`. So the seeder writes both columns, and the hand-written `content_*` is
   superseded the first time anyone opens a template and saves.
4. **The plain-text OTP twin stays a blade.** The builder emits HTML only, and dropping the text
   alternative of an OTP costs deliverability. It needs the code alone.

**Promoted to the ledger:** D48 (system templates), D49 (builder direction + link colour).

## Definition of Done

- [x] Code committed to `dev` in both sub-apps
- [x] EN + AR translations in the same commit (10 keys each, admin)
- [x] Quality gate green — backend `pint --test` + 641 tests on the merged tree (phpstan unchanged:
      the same 5 pre-existing larastan false positives, verified against a pristine worktree);
      admin `yarn type-check` + `yarn build` + `yarn check:rbac` + eslint
- [x] Docs updated (this TASK.md, index row, ledger D48 + D49)
- [x] Mobile contract checked — no route added, removed or renamed; `type` is a query param on an
      existing `/admin/*` listing
- [ ] Push all three repos
- [ ] `php artisan migrate` + `db:seed --class=SystemEmailTemplatesSeeder` on every environment
- [ ] **Open the production invitation template in the editor and save it once per language** — the
      RTL and link-colour fixes apply on save, so templates authored before this keep the blue
      auto-linked `TOURISE.COM` until re-saved. Local templates are ~1KB stubs and unaffected; the
      15KB template in the screenshot is production-only.
- [ ] Browser QA: send-test each of the five system templates in EN and AR; confirm one footer, the
      code substituting, Arabic reading right-to-left, and the footer link white rather than blue
