#!/usr/bin/env python3
"""
Markdown to A4-print HTML (and PDF) for the security reports in this folder,
in the TOURISE 2027 theme of the client guides in docs/client/.

Ported from pif-pep-v2's docs/security/md2report.py. The parser is the same
small subset (h2, h3, tables, fenced code, lists, callouts, paragraphs, inline
code, bold, links); the stylesheet is the one ONE_INVITATION_PER_EMAIL.html and
the other client guides use, plus pills for severity and status.

The title block comes from a comment at the top of the markdown, so a report
regenerates from its own file with no flags to remember:

  <!-- report
  eyebrow: Security
  subtitle: One line under the title
  meta: Classification=CONFIDENTIAL / TLP:AMBER|Date=2026-10-13
  footer: Pentest triage
  -->
  # The title

Flags of the same names override it. GitHub hides the comment.

Inline extras:
  [[Medium]]          a pill; the class comes from the word (see PILL in CSS)
  > [!WARNING]        first line of a callout picks its colour: NOTE and TIP
                      purple, WARNING and IMPORTANT orange, CAUTION pink

Escaped pipes matter: `a\\|b` stays one table cell. Cells are split on
unescaped pipes only.

Usage:
  md2report.py IN.md [OUT.html] [--pdf]
OUT defaults to IN with .html. --pdf also prints OUT.pdf with headless Chrome.
See REPORT_GENERATION_WORKFLOW.md.
"""

import argparse
import html as H
import pathlib
import re
import shutil
import subprocess
import sys

CSS = """
@page { size: A4; margin: 16mm 16mm 17mm 16mm;
  @bottom-left { content: "__FOOTER__"; font-family: Arial, sans-serif; font-size: 7.6pt; color: #8A90A0; }
  @bottom-right { content: "Page " counter(page) " of " counter(pages); font-family: Arial, sans-serif; font-size: 7.6pt; color: #8A90A0; }
}
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  color: #212121; font-size: 10.3pt; line-height: 1.55; margin: 0; }
.head { padding-bottom: 2mm; margin-bottom: 6mm; }
.eyebrow { font-size: 8pt; font-weight: 700; letter-spacing: 2.2px; color: #3C0DEB; text-transform: uppercase; }
h1 { font-size: 25pt; line-height: 1.12; margin: 3mm 0 3mm 0; color: #111; letter-spacing: -.5px; font-weight: 800; }
.sub { font-size: 11pt; color: #4A4F5A; margin: 0; }
.meta { font-size: 8.4pt; color: #8A90A0; margin: 2.5mm 0 0 0; }
.meta strong { color: #4A4F5A; }
.band { display: flex; height: 3px; margin-top: 5mm; }
.band i { flex: 1; } .band i:nth-child(1){background:#3C0DEB} .band i:nth-child(2){background:#FF0A5A}
.band i:nth-child(3){background:#1EC8A0} .band i:nth-child(4){background:#FF9B3C}
h2 { font-size: 14.5pt; color: #111; margin: 8mm 0 3mm 0; font-weight: 800; letter-spacing: -.2px;
  border-bottom: 1.2px solid #D3DBE5; padding-bottom: 1.5mm; page-break-after: avoid; }
h3 { font-size: 11.5pt; margin: 6mm 0 2mm 0; font-weight: 700; color: #111; page-break-after: avoid; }
p { margin: 0 0 3mm 0; }
ul, ol { margin: 0 0 3mm 0; padding-left: 6mm; }
li { margin: 0 0 1.4mm 0; }
strong { color: #111; }
a { color: #3C0DEB; text-decoration: none; }
.nw { white-space: nowrap; }
code { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 8.8pt; background: #F1F3F8;
  border: 1px solid #E2E6EE; border-radius: 3px; padding: 0 1.2mm; overflow-wrap: anywhere; }
.ascii { background: #F7F8FB; border: 1px solid #E2E6EE; border-radius: 2mm; padding: 3mm 4mm;
  font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 8.4pt; white-space: pre-wrap;
  color: #212121; margin: 0 0 4mm 0; page-break-inside: avoid; }
.callout { background: #F3F0FF; border-left: 3px solid #3C0DEB; border-radius: 2mm;
  padding: 3mm 4mm; margin: 0 0 4mm 0; page-break-inside: avoid; }
.callout.warn { background: #FFF7ED; border-left-color: #FF9B3C; }
.callout.danger { background: #FFF1F5; border-left-color: #FF0A5A; }
.callout p:last-child { margin-bottom: 0; }
table { width: 100%; border-collapse: collapse; margin: 1mm 0 4mm 0; font-size: 9.2pt; page-break-inside: auto; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th { background: #3C0DEB; color: #fff; text-align: left; font-weight: 700; padding: 2mm 2.4mm; }
td { border-bottom: 1px solid #E2E6EE; padding: 2mm 2.4mm; vertical-align: top; overflow-wrap: break-word; }
tr:nth-child(even) td { background: #FAFBFD; }
.pill { display: inline-block; font-size: 7.2pt; font-weight: 800; letter-spacing: 1px; text-transform: uppercase;
  padding: .5mm 2mm; border-radius: 1mm; white-space: nowrap; background: #F1F3F8; color: #5A606C; }
.pill-critical { background: #FFE3EC; color: #C2003F; }
.pill-high     { background: #FFEBD9; color: #B0560A; }
.pill-medium   { background: #FFF4D6; color: #8A6100; }
.pill-low      { background: #EFF3FF; color: #3C0DEB; }
.pill-open     { background: #FFF1F5; color: #C2003F; }
.pill-decision { background: #FFF7ED; color: #9A5B0A; }
.pill-partial  { background: #FFF4D6; color: #8A6100; }
.pill-fixed, .pill-closed, .pill-verified { background: #E3F8F1; color: #0E7A5F; }
.pill-code, .pill-ops { background: #F3F0FF; color: #3C0DEB; }
"""

ALERTS = {'NOTE': '', 'TIP': '', 'WARNING': ' warn', 'IMPORTANT': ' warn', 'CAUTION': ' danger'}


def inline(s: str) -> str:
    """Escape HTML, then apply inline code, links, pills and bold. Code
    first so markers inside a code span are left alone."""
    out, i = [], 0
    for m in re.finditer(r'`([^`]+)`', s):
        out.append(_marks(H.escape(s[i:m.start()], quote=False)))
        out.append('<code>' + H.escape(m.group(1), quote=False) + '</code>')
        i = m.end()
    out.append(_marks(H.escape(s[i:], quote=False)))
    return ''.join(out)


def _marks(s: str) -> str:
    s = re.sub(r'\[\[([^\]]+)\]\]',
               lambda m: f'<span class="pill pill-{_slug(m.group(1))}">{m.group(1)}</span>', s)
    # Keep IDs such as M-001 or CVE-2026-64645 on one line; not inside a URL.
    s = re.sub(r'(?<![/\w-])([A-Z]{1,4}-\d{2,}(?:-\d+)?)\b', r'<span class="nw">\1</span>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'<a href="\2">\1</a>', s)
    return re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)


def _slug(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def split_cells(row: str) -> list[str]:
    """Split a table row on unescaped pipes, then unescape the rest."""
    r = row.strip()
    if r.startswith('|'):
        r = r[1:]
    if r.endswith('|') and not r.endswith('\\|'):
        r = r[:-1]
    return [c.strip().replace('\\|', '|') for c in re.split(r'(?<!\\)\|', r)]


def front_matter(md: str) -> tuple[dict, str]:
    """Read the leading <!-- report ... --> block, if any."""
    m = re.match(r'\s*<!--\s*report\s*\n(.*?)-->\s*\n', md, re.S)
    if not m:
        return {}, md
    fm = {}
    for line in m.group(1).splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            fm[k.strip()] = v.strip()
    return fm, md[m.end():]


def convert(md: str) -> tuple[str, str]:
    """Return (title, body html). The first `# ` line is the title."""
    lines = md.split('\n')
    title, body, i = '', [], 0
    starts = ('|', '#', '```', '---', '>', '- ')
    while i < len(lines):
        stripped = lines[i].strip()

        if stripped.startswith('# '):
            title = title or stripped[2:]
            i += 1
            continue

        if stripped == '---' or stripped.startswith('<!--'):
            i += 1
            continue

        if stripped.startswith('```'):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith('```'):
                buf.append(H.escape(lines[i], quote=False))
                i += 1
            i += 1
            body.append('<div class="ascii">' + '\n'.join(buf) + '</div>')
            continue

        if stripped.startswith('### '):
            body.append('<h3>' + inline(stripped[4:]) + '</h3>')
            i += 1
            continue

        if stripped.startswith('## '):
            body.append('<h2>' + inline(stripped[3:]) + '</h2>')
            i += 1
            continue

        if stripped.startswith('>'):
            buf = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                buf.append(lines[i].strip()[1:].strip())
                i += 1
            kind = ''
            alert = re.match(r'\[!(\w+)\]$', buf[0]) if buf else None
            if alert:
                kind = ALERTS.get(alert.group(1).upper(), '')
                buf = buf[1:]
            paras = ' '.join(b if b else '\n\n' for b in buf).split('\n\n')
            body.append(f'<div class="callout{kind}">'
                        + ''.join('<p>' + inline(p.strip()) + '</p>' for p in paras if p.strip())
                        + '</div>')
            continue

        if stripped.startswith('- ') or re.match(r'\d+\. ', stripped):
            ordered = not stripped.startswith('- ')
            item = r'\d+\. ' if ordered else r'- '
            items = []
            while i < len(lines) and lines[i].strip():
                s = lines[i].strip()
                if re.match(item, s):
                    items.append(re.sub('^' + item, '', s))
                elif items and lines[i].startswith((' ', '\t')):
                    items[-1] += ' ' + s            # a wrapped continuation line
                else:
                    break
                i += 1
            tag = 'ol' if ordered else 'ul'
            body.append(f'<{tag}>' + ''.join('<li>' + inline(t) + '</li>' for t in items) + f'</{tag}>')
            continue

        if stripped.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append(lines[i])
                i += 1
            head = split_cells(rows[0])
            out = ['<table><thead><tr>']
            out += ['<th>' + inline(c) + '</th>' for c in head]
            out.append('</tr></thead><tbody>')
            for r in rows[2:]:                       # row 1 is the |---| rule
                cells = split_cells(r)
                # Pad or trim so a malformed row can never shift the columns.
                cells = (cells + [''] * len(head))[:len(head)]
                out.append('<tr>' + ''.join('<td>' + inline(c) + '</td>' for c in cells) + '</tr>')
            out.append('</tbody></table>')
            body.append(''.join(out))
            continue

        if not stripped:
            i += 1
            continue

        para = []
        while i < len(lines) and lines[i].strip() and not (
                lines[i].strip().startswith(starts) or re.match(r'\d+\. ', lines[i].strip())):
            para.append(lines[i].strip())
            i += 1
        body.append('<p>' + inline(' '.join(para)) + '</p>')

    return title, '\n'.join(body)


def chrome() -> str | None:
    mac = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    if pathlib.Path(mac).exists():
        return mac
    for name in ('google-chrome', 'chromium', 'chromium-browser'):
        if shutil.which(name):
            return name
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dest', nargs='?')
    ap.add_argument('--eyebrow')
    ap.add_argument('--title')
    ap.add_argument('--subtitle')
    ap.add_argument('--meta', help='pipe separated k=v pairs')
    ap.add_argument('--footer', help='left page footer, after "TOURISE 2027 · "')
    ap.add_argument('--pdf', action='store_true', help='also print the PDF with headless Chrome')
    a = ap.parse_args()

    src = pathlib.Path(a.src).resolve()
    dest = pathlib.Path(a.dest).resolve() if a.dest else src.with_suffix('.html')
    fm, md = front_matter(src.read_text())
    md_title, body = convert(md)

    title = a.title or fm.get('title') or md_title or src.stem
    eyebrow = a.eyebrow or fm.get('eyebrow', 'Security')
    subtitle = a.subtitle or fm.get('subtitle', '')
    meta_raw = a.meta or fm.get('meta', '')
    footer = 'TOURISE 2027 · ' + (a.footer or fm.get('footer') or title)
    meta = ' &nbsp;·&nbsp; '.join(
        f'{H.escape(k.strip())}: <strong>{H.escape(v.strip())}</strong>'
        for k, v in (p.split('=', 1) for p in meta_raw.split('|') if '=' in p)
    )
    css = CSS.replace('__FOOTER__', footer.replace('\\', '\\\\').replace('"', '\\"'))

    doc = (
        '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
        f'<title>TOURISE 2027 · {H.escape(title)}</title><style>{css}</style></head><body>'
        f'<div class="head"><div class="eyebrow">{H.escape(eyebrow)}</div><h1>{inline(title)}</h1>'
        + (f'<p class="sub">{inline(subtitle)}</p>' if subtitle else '')
        + (f'<p class="meta">{meta}</p>' if meta else '')
        + '<div class="band"><i></i><i></i><i></i><i></i></div></div>\n'
        f'{body}\n</body></html>\n'
    )
    dest.write_text(doc)
    print(f'{dest.name}: {len(doc)} bytes')

    if a.pdf:
        exe = chrome()
        if not exe:
            sys.exit('No Chrome or Chromium found; print the PDF by hand (see the workflow doc).')
        pdf = dest.with_suffix('.pdf')
        subprocess.run([exe, '--headless', '--disable-gpu', '--no-pdf-header-footer',
                        f'--print-to-pdf={pdf}', dest.as_uri()],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f'{pdf.name}: {pdf.stat().st_size} bytes')


if __name__ == '__main__':
    main()
