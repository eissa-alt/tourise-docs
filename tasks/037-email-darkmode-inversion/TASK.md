# Task 037 — Email dark mode: stop clients inverting the black footer

- **Status:** `in-progress`
- **Opened:** 2026-09-16
- **Owner:** Eissa
- **Sub-app(s):** admin
- **Branch(es):** `dev`

## Goal

Mail clients that force dark mode were inverting the black footer band to white. The social
icons are images, are never inverted, and so stayed white glyphs on a now-white band —
invisible. Make the footer survive forced dark mode in the clients the event actually sends to.

## Scope

- In: the HTML `handleSave` emits in `email-editor-waypoint.tsx` (admin), and the social icon
  assets shared by every template.
- Out — **the newsletter editor**. The pull on 2026-09-16 brought in
  `newsletter-template-editor.tsx` and `newsletter-html-version-editor.tsx`, which do **not**
  use `renderToStaticMarkup` and carry no dark-mode handling at all. If a newsletter has a dark
  footer it will invert exactly as the email templates did. Same bug, separate code path, not
  covered by this task's commit. Parked deliberately — see Follow-ups.
- Out: Arabic templates not yet verified. Same footer, same code path, untested.
- Out: Zoho's band colour (see Decisions).

## Log

- 2026-09-16 — opened. Reproduced in Gmail iOS dark: black footer rendered white, icons gone.
- 2026-09-16 — found the emitted HTML has **no `<head>` at all** — no `color-scheme`, no
  `supported-color-schemes`, no `<style>`. A client that cannot tell whether a message handles
  dark mode gives itself permission to invert it.
- 2026-09-16 — added the `<head>` + colour-scheme meta. **Gmail ignores it** — verified by test,
  it inverted anyway with the meta present in the saved HTML. Kept: Apple Mail and Outlook do
  honour it, so it is correct, just not sufficient.
- 2026-09-16 — painted a `linear-gradient` over dark fills. A gradient is a background-IMAGE, not
  a colour, and the inverter rewrites colours — so the band **held black in Gmail**.
- 2026-09-16 — text still darkened. Dropped `background-color` on the theory that Gmail darkens
  footer text because it reads the background as light: **changed nothing**, and it broke Outlook
  web and the Outlook app outright — neither renders a CSS gradient, so the band lost its fill.
  Colour restored underneath the gradient. Conclusion: text inversion is **independent** of the
  background declaration.
- 2026-09-16 — text fixed by authoring, not code: pure `#ffffff` inverts darkest, `#b9b9b9`
  survives. Proved in one message — the `#b9b9b9` legal line was readable while the `#ffffff`
  heading directly above it was not.
- 2026-09-16 — **committed** admin `50c4282`. Verified green in Gmail (iOS), Outlook (web, app,
  classic) and Yahoo, light and dark.
- 2026-09-16 — Zoho dark still inverts. Tried `bgcolor` attribute (no effect) and a hosted black
  PNG as `background-image:url(...)` (abandoned mid-test). Both reverted; working tree returned
  to `50c4282`.
- 2026-09-16 — a `<td>`-scoped transform silently matched nothing for several rounds because the
  footer is still a `<div>` at that point in `handleSave` and only becomes a `<td>` later, in
  `convertPaddedDivsToTables`. Cost ~4 invalid test sends. **Tell: `updated_at` not moving means
  the generated HTML was byte-identical, i.e. the transform did not match — not a stale bundle.**

## Decisions

- **Zoho's band is not winnable with declarations.** It strips `linear-gradient`, and inverts
  `background-color` and `bgcolor` alike. All three tested. Stop chasing it.
- **Fix the icons instead, and let the band be.** In Zoho dark the text is still legible — the
  only real failure is the invisible icons. Social icons rebuilt as white glyphs on a baked-in
  black disc (256×256, in `emails-darkmode-check/icons-darkmode-safe/`). Images are never
  inverted, so they read on a black band *and* a light one. This also hardens every other client
  against inverters we have not met.
- **Footer text is authored near `#b9b9b9`, not `#ffffff`.** Counter-intuitive and worth
  remembering: to get *brighter* text in Gmail dark, pick a *darker* source colour.
- **New icon assets get new filenames.** The existing six URLs are shared by every template in
  the database, so overwriting them would change every template and every already-delivered
  email at once.

## Follow-ups

- **Newsletter dark mode** — parked. Decide whether `newsletter-template-editor.tsx` needs the
  same `<head>` + gradient treatment, or builds its HTML differently enough not to.
- Upload the six icons, swap `iconUrl` on the Social block, verify Zoho dark + Gmail dark.
- Verify an Arabic template renders the same.

## Definition of Done

- [x] Code merged to `dev` in the relevant sub-app(s) — admin `50c4282`
- [ ] EN + AR translations in the same commit (if any user-facing strings) — n/a, no strings
- [ ] Quality gate green — `yarn type-check` + `check:rbac` green; **`yarn build` not yet run**
- [ ] Docs updated (this TASK.md set to `done`; index row updated; any drift fixed)
- [ ] Mobile contract checked if `routes/api.php` touched — n/a
