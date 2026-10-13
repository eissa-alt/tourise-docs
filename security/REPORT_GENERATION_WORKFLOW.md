# Report generation workflow

How a security report in this folder becomes an A4 PDF in the TOURISE 2027 theme. The markdown
is the source; the HTML and the PDF are generated from it and committed beside it.

> Ported from `123-pif-pep-v2/pif-pep-v2-repos/docs/security/REPORT_GENERATION_WORKFLOW.md`
> (itself from saudi-forum-11) on 2026-10-13. Same pipeline and the same converter, restyled with
> the theme of the client guides in [`docs/client/`](../client/) (for example
> `ONE_INVITATION_PER_EMAIL`), so a security report looks like every other document the event team
> receives.

## Pipeline

```
NAME.md    the source, edited by hand
  │  python3 md2report.py NAME.md --pdf
  ▼
NAME.html  self-contained, A4 print-ready (no external CSS, fonts or images)
  │  headless Chrome (run by --pdf)
  ▼
NAME.pdf   what is handed to people outside the team
```

One folder per report, with the three files sharing the folder's name:

```
pentest-2026-09/
  PENTEST_TRIAGE/
    PENTEST_TRIAGE.md
    PENTEST_TRIAGE.html
    PENTEST_TRIAGE.pdf
```

The basename repeats inside the folder on purpose: a PDF sent on its own carries only its file
name, and `PENTEST_TRIAGE.pdf` still says what it is; `report.pdf` would not.

> [!WARNING]
> **A PDF goes stale silently.** It is binary, so a text search for a finding or a SHA never finds
> it. Whenever the `.md` changes, regenerate in the same commit. If the `.md` and the `.pdf` ever
> disagree, the `.md` wins.

## Command

From `docs/security/`:

```bash
python3 md2report.py pentest-2026-09/PENTEST_TRIAGE/PENTEST_TRIAGE.md --pdf
```

This writes `PENTEST_TRIAGE.html` next to the `.md`, then prints `PENTEST_TRIAGE.pdf` with
headless Chrome (`/Applications/Google Chrome.app` on macOS, or `google-chrome` / `chromium` on
the PATH). Without `--pdf` it writes the HTML only. Python 3.10 or later, standard library only.

To print by hand instead:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$PWD/NAME.pdf" "file://$PWD/NAME.html"
```

Keep `--no-pdf-header-footer`. Page size, margins and the footer ("TOURISE 2027 · title" on the
left, "Page X of Y" on the right) come from the stylesheet's `@page` rule, not from Chrome flags.

## Writing the markdown

Start each report with a comment that holds its title block, so it regenerates with no flags:

```markdown
<!-- report
eyebrow: Security · Pentest 2026-09
subtitle: One line under the title
meta: Classification=CONFIDENTIAL / TLP:AMBER|Checked=2026-10-13
footer: Pentest triage, September 2026
-->
# Pentest triage
```

| Field | Shows as |
|---|---|
| `eyebrow` | The small purple capitals above the title (default `Security`) |
| `# ` line | The title (or `title:` in the comment) |
| `subtitle` | The grey line under the title |
| `meta` | `Key=Value` pairs separated by `\|`, in small print under the subtitle |
| `footer` | The left page footer, after `TOURISE 2027 · ` (default: the title) |

GitHub hides the comment, so the `.md` still reads cleanly there. Command line flags of the same
names (`--eyebrow`, `--subtitle`, `--meta`, `--footer`, `--title`) override it.

The converter understands a small subset, enough for these reports:

| Markdown | Result |
|---|---|
| `## ` and `### ` | Section and sub-section headings |
| Paragraphs, `**bold**`, `` `code` ``, `[text](url)` | As usual |
| `- ` and `1. ` lists | Bulleted and numbered lists; indent a line to continue an item |
| Tables | Purple header row, striped body. Write `\|` for a pipe inside a cell |
| Fenced code blocks | A grey box, kept on one page |
| `> ` | A purple callout |
| `> [!WARNING]` or `> [!IMPORTANT]` as the first line | An orange callout |
| `> [!CAUTION]` as the first line | A pink callout |
| `[[Medium]]`, `[[Open]]` | A pill. Coloured: Critical, High, Medium, Low, Open, Fixed, Closed, Verified, Partial, Decision, Code, Ops. Any other word is grey |

IDs such as `M-001` and `CVE-2026-64645` are kept on one line automatically. Anything else
(images, nested lists, italics) is not supported: keep reports to the subset, or extend
`md2report.py` and note it here.

## Theme

The colours and type are those of the client guides, from the TOURISE 2027 brand
([design/THEME.md](../design/THEME.md)): purple `#3C0DEB` for the eyebrow, table headers and
callouts; the four-colour band (`#3C0DEB`, `#FF0A5A`, `#1EC8A0`, `#FF9B3C`) under the title; the
system sans-serif stack; A4 with 16 mm margins. Change the stylesheet in `md2report.py` only, then
regenerate every report in this folder so they stay alike.
