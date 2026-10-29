# CRM guide — 29 October 2026

`TOURISE_CRM_GUIDE.html` is the editable, self-contained source; regenerate
`TOURISE_CRM_GUIDE.pdf` whenever it changes. The guide includes the latest
CRM work merged into `testing`, including Eissa's changes through 29 October.

This revision covers:

- Added for an invitation created but not sent; Sent only after sending.
- Archive, restore and permanent deletion, with the separate access boxes.
- Up to 5,000 import rows; valid rows imported separately from failed rows.
- Editing red cells, removing rows, rechecking and downloading corrected files.
- Add new contacts versus Update contacts from Export, matched by CRM ID.
- Existing-email messages naming who added the contact, and speaker imports.
- The revised required columns, free-text List Provided By, optional channel
  and clearance, and Industry inferred from Sub-industry.
- Up to five activity attachments, 5 MB each, kept private.
- Requests entering the CRM only after acceptance, and public registration
  remaining available for CRM contacts without an invitation send.

Screenshots predate this revision; the guide explicitly identifies this.
Current text and the replacement cases table take precedence over old labels
in screenshots. A new screenshot capture is still needed to refresh the images.

Verified against admin `7ce52e6` and backend `ce6e14e` on `testing`.
The backend change adds three regression tests; no runtime registration change
was needed. The focused suite passed 66 tests / 555 assertions with debug on
and off. Admin type checking, RBAC validation and the production build passed.
The production build ran in a temporary checkout to preserve the local dev server.

## Regenerate the PDF

Use headless Chrome with `--no-pdf-header-footer`, an isolated temporary profile,
and `--print-to-pdf` pointing to the sibling PDF. The HTML supplies A4 dimensions,
print scaling and page footers. Review the resulting pages before committing.
