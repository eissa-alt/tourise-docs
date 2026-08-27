# Tourise 2027 — theme & component reference

How to build a **new form** (or any new screen) so it matches the rest without
re-deriving anything. Everything here is in the frontend repo and already in use
by the four registration shapes.

Source of truth for values: the Figma file `2H2r4RLTgO2LWvWZg9zq4M`. Read frames
through the Figma MCP server (`get_design_context`) rather than eyeballing.

---

## 1. Tokens — `tourise-frontend/tailwind.config.js`

Never hardcode a hex. Every value below is a Tailwind token.

### Colour (`theme.extend.colors.tourise`)

| Token | Value | Used for |
|---|---|---|
| `tourise-blue` | `#3C0DEB` | page ground, buttons, progress, links, checkboxes, focus |
| `tourise-black` | `#000000` | headings and field values |
| `tourise-ink` | `#212121` | body copy that is not pure black (Figma calls it `--primary`) |
| `tourise-muted` | `#7F8694` | placeholders, floating labels at rest |
| `tourise-border` | `#D3DBE5` | the 2px field outline, 1px icon-button border |
| `tourise-grey-light` / `tourise-panel` | `#E7EEF7` | summary panels, prefix chips, the upload bar, inactive progress |
| `tourise-white` | `#FFFFFF` | cards |
| `tourise-graphic-*` | red `#FF0A5A` · green `#1EC8A0` · yellow `#FF9B3C` · blue `#3C00EB` · ink · paper | the footer property band only |

`primary` and `accent` in the legacy palette also resolve to the brand purple, so
old `text-primary` / `ring-accent` usages stay on-brand. `secondary` keeps
`#1EC8A0` because it is the band's green.

### Type (`theme.extend.fontSize`) — names match the Figma styles

| Token | px | Figma style |
|---|---|---|
| `text-display` | 40 / 48 | H3 · Bold · Caps |
| `text-body-xl` | 24 / 32 | Body XL · Bold · Caps — section headings |
| `text-body-l` | 20 / 28 | Body L / Label L — panel titles, buttons |
| `text-body-m` | 18 / 24 | Body M — field values, body copy |
| `text-body-s` | 16 / 22 | Body S · Light — helper text |
| `text-body-xs` | 14 / 20 | Body XS · Bold — footer links |

Font family is `font-akhand`; the app-wide `en`/`ar` families already lead with
Akhand, so you rarely set it.

### Radius (`theme.extend.borderRadius`)

`rounded-card` 32 · `rounded-panel` 16 · `rounded-field` 12 · `rounded-chip` 10 ·
`rounded-pill` 100 · `rounded-pill-lg` 120. Icon buttons use `rounded-pill`.

---

## 2. Field anatomy — the part most easily got wrong

A field is **56px** tall, `px-4`, with a **2px** `tourise-border` outline and
`rounded-field`. Inside it a floating label:

```
6px  top padding
16px label      text-sm  leading-4  text-tourise-muted
4px  gap
24px value      text-body-m         text-tourise-black
6px  bottom padding
= 56
```

- At rest the label sits centred and reads as the placeholder; it rises on focus
  or once the field has a value. Driven by `:placeholder-shown`, so the input
  needs `placeholder=" "` whenever it has a label.
- The **caret** is blue (`caret-tourise-blue`). The typed value stays black —
  the blue `|` in the Active frame is the cursor, not the text.
- Errors render **in flow** (`mt-1 text-xs leading-4 text-error`). Absolutely
  positioned errors escape their grid cell and land on the row below.
- Focus ring belongs to the field, never to an inner control.

Prefix chips (Title, dial code) are **40px** inside the 56px field — the field
uses `py-2` so `8 + 40 + 8 = 56`. The frame's `py-2.5` overflows a real border.

---

## 3. Layout

```
PageShell               mosaic ground + header + footer
└─ ThemeCard            800px max, rounded-card, p-8, gap-6
   ├─ title row         back IconButton + text-display, pr-14 to balance
   ├─ StepProgress      4 rails, gap-2.5
   ├─ <section> …       gap-4: heading (body-xl) + grid
   │   └─ grid gap-4 md:grid-cols-2 md:items-start
   └─ primary button    ThemeButton block
```

- Fields space themselves below `md` (`mb-4 md:mb-0`) and hand over to the grid
  gap at `md`. Do not rely on the grid alone — mobile is a single column.
- Full-width items inside the grid take `md:col-span-2` (upload, consent, submit).
- Section order in every shape: **Gender → Title → First Name → Last Name → …**,
  and the personal photo is the closing row of Personal details.

---

## 4. Components — `tourise-frontend/components/theme/`

| Component | What it is |
|---|---|
| `PageShell` | mosaic ground + header + footer; for pages that opt out of the global layout (`isBareLayout`) |
| `MosaicGround` | the fixed mosaic-over-purple layer — never a background on a scrolling wrapper |
| `ThemeCard` | the 800px white card |
| `ThemeButton` | brand / outline / ghost × large / small, pill |
| `IconButton` | 48px circular, 1px border — the back and close controls |
| `StepProgress` | the rails |
| `SummaryPanel` | panel title + EDIT + label/value rows (`translateTitle` for i18n ids) |
| `ReviewStep` | the whole review screen; pass `sections` |
| `ConfirmSubmitModal` | yes/no confirm with a photo preview |
| `PhotoDropzone` · `PhotoPreview` · `PhotoGuidelines` · `PhotoCropModal` | the personal-photo step |
| `PrefixField` | field shell with a chip on the leading edge |
| `CheckRow` | consent checkbox — a real `<input type="checkbox">` |
| `SiteHeader` · `SiteFooter` · `PixelStrip` · `SocialRow` | the shell |
| `icons.tsx` | `ArrowLeftIcon` `CloseIcon` `CloseSmallIcon` `CheckIcon` — exported Figma paths, inlined verbatim |

Shared form controls live in `components/shared/forms` and are already themed:
`CustomInput`, the three selects, `PhoneInputV2`, `MaskedDateInput`,
`SingleCheckboxInput`, `CustomRadioInput`, `CustomFileInput2` (`compact` for the
bar + thumbnail).

---

## 5. Traps that cost time — read before debugging

1. **`tsc` green ≠ structure sound.** Moving JSX blocks can unbalance a grid and
   still compile; every field then goes full width. Verify in the render.
2. **Option lists whose labels are `<Translate>` elements** (ten of them in
   `data/`) cannot have their label captured at selection time — it is a React
   element, not a string. Derive the text from the value's own translation key.
3. **`valid_visa` is stored INVERTED** — "Yes, I need assistance" writes `false`.
4. **`ltr:`/`rtl:` variants need an explicit `dir`** on an ancestor and fall back
   to the wrong side without one. Prefer logical utilities (`start-*`, `end-*`).
5. **react-phone-input-2 is controlled**: echo back the value it emitted, or it
   rejects every keystroke. It also re-guesses the country from typed digits
   unless `disableCountryGuess` is set.
6. **Invisible leftovers**: an `<hr className="my-7 border-white/50">` cost 56px
   of blank space above the upload bar for a while. When spacing looks wrong,
   tint the wrapper and look, do not reason.
7. **Two `next dev` on one folder** corrupt `.next` and produce
   `Cannot find module './xxx.js'`. One per project.

---

## 6. Previews

`/[lang]/theme-preview/` — `index` (intro) · `form?shape=<form_shape>&step=<id>`
(any shape or step, no backend needed) · `review` · `photo`. All `noindex`,
unlinked, and marked `isBareLayout`.

---

## 7. Outstanding

- **Akhand licence.** The bundled files are "Free for Personal Use" from
  befonts; the family is Indian Type Foundry's. A commercial licence is needed
  before launch — the kit drops into `public/fonts/Akhand/` unchanged.
- Social glyphs in the footer are hand-drawn stand-ins, not the official marks.
- `favicon.ico` and friends are still the fork's artwork.
- `passport_type` now carries `passport|iqama|national_id` from Tourise and
  `regular|diplomatic` from four-steps; the admin maps only the latter pair.
