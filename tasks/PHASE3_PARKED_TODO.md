# Phase 3 — parked "later / opportunistic" cleanups — ✅ CLOSED 2026-07-19

**Parked:** 2026-07-07 (user chose to park these and move on to new work).
**Closed:** 2026-07-19 — re-checked against the code; items 1 + 2 are **done** (landed via later
sessions, not tracked here at the time), item 3 was promoted to task 009 and closed. Nothing left in
this bucket except the *optional* drift-check script (see item 1). File kept for the record.
**Source:** the admin+frontend code-quality audit whose "fix first" and "cheap cleanups" phases are
now complete (see `HANDOFF.md`, ledger **D5/D9**).

---

## 1. Cross-repo drift check — `utils/cont-list.ts` — ✅ DONE (core), optional script not built

The admin and frontend apps keep ~26 byte-identical "plumbing" files in sync **by hand-copying**, so
they silently drift. As of 2026-07-07, `utils/cont-list.ts` differed between the two apps — a latent
data bug.

- **Do first — ✅ DONE:** `utils/cont-list.ts` is now **byte-identical** between admin and frontend
  (verified 2026-07-19 with `diff` — clean). The country-list drift is reconciled.
- **Then (optional) — not done:** the read-only drift-check bash script (`diff`/`cmp` over the ~26
  should-be-identical files) was never built. Still optional; pick up only if drift recurs.

## 2. Bundle-size wins — dynamic imports — ✅ DONE

- **`xlsx`** (~400 KB, SheetJS) is now **dynamically** imported — `await import('xlsx')` inside the
  file-change handler at `custom-excel-import.tsx` (~line 109), so it stays out of the invitations
  create/edit page bundles until a user actually picks a file.
- **chart.js + chartjs-plugin-datalabels** no longer load eagerly. All five dashboard widgets are
  wrapped in `next/dynamic` with `{ ssr: false }` (`components/admin-modules/dashbaord/index.tsx`), and
  `ChartCanvas.tsx` does `await import('chart.js/auto')` + the datalabels plugin at runtime — chart.js
  is fully out of the dashboard's initial bundle.

## 3. `useFetch` adoption (opportunistic, do NOT sweep) — **moved to `tasks/009-usefetch-adoption/`**

Promoted out of this parked bucket into its own standing-convention task on 2026-07-18. See
[`tasks/009-usefetch-adoption/TASK.md`](009-usefetch-adoption/TASK.md) for the rule, the candidate
checklist, and the known `refetch` gap. The convention note now also lives at the top of
`admin/hooks/useFetch.ts` where devs see it.

---

## Explicitly NOT doing (decided, not "parked")

- **Remove `zod`** — it's load-bearing (runtime peer dep of the email-template editor); removing it
  crashes the editor.
- **Flip `@typescript-eslint/no-explicit-any` on** — stays off globally by decision; typing was burned
  down where it mattered (ledger D9) without the rule flip.
- **CI quality-gate workflow** — dropped; Vercel already fails deploys on build/type errors.
