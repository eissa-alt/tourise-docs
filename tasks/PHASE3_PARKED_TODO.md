# Phase 3 — parked "later / opportunistic" cleanups

**Parked:** 2026-07-07 (user chose to park these and move on to new work).
**Source:** the admin+frontend code-quality audit whose "fix first" and "cheap cleanups" phases are
now complete (see `HANDOFF.md`, ledger **D5/D9**). This file holds the third bucket — flagged, not
scheduled. Pick up any item independently when it becomes convenient; none is urgent.

---

## 1. Cross-repo drift check — `utils/cont-list.ts` (has a real bug behind it)

The admin and frontend apps keep ~26 byte-identical "plumbing" files in sync **by hand-copying**, so
they silently drift. As of 2026-07-07, `utils/cont-list.ts` **already differs** between the two apps —
the two country lists are out of sync, which is a latent data bug, not just cosmetic.

- **Do first:** reconcile `utils/cont-list.ts` between admin and frontend (decide the canonical list,
  make both identical) in one paired change.
- **Then (optional):** add a read-only drift-check script (plain bash `diff`/`cmp` over an explicit
  file list of the ~26 should-be-identical files) so future drift is caught. No monorepo, no tooling —
  just a script. The audit also found ~8 more files that differ by only 2–8 lines (accidental drift)
  worth folding into the same list.

## 2. Bundle-size wins — dynamic imports (perf only, no correctness issue)

- **`xlsx`** (~400 KB, SheetJS) is **statically** imported at
  `alt-static-basecode-admin/components/shared/forms/custom-file-input-2/custom-excel-import.tsx:10`,
  which pulls it into the invitations create/edit page bundles even though it only runs after a user
  picks an Excel file. Convert to a dynamic `await import('xlsx')` inside the file-change handler, or
  `next/dynamic` the component. (Mirrors the existing dynamic pattern used for print-js / the email
  editor.)
- **chart.js + chartjs-plugin-datalabels** load eagerly on the dashboard
  (`components/admin-modules/dashbaord/charts.tsx`, imported by the dashboard root). Wrap the chart
  components in `next/dynamic` with `{ ssr: false }` so chart.js loads only when the dashboard renders.

## 3. `useFetch` adoption (opportunistic, do NOT sweep)

Admin has a shared `hooks/useFetch.ts` but only **5** call sites, while **~64** files still hand-roll
the `loading` / `hasError` / `Axios.get`-in-`useEffect` pattern. The audit's own guidance: migrate the
single-GET-then-render cases onto `useFetch` **opportunistically when you're already editing that file**,
highest-traffic screens first. Leave paginated screens on `use-listing-state` and multi-request forms
alone. Not a batch job.

---

## Explicitly NOT doing (decided, not "parked")

- **Remove `zod`** — it's load-bearing (runtime peer dep of the email-template editor); removing it
  crashes the editor.
- **Flip `@typescript-eslint/no-explicit-any` on** — stays off globally by decision; typing was burned
  down where it mattered (ledger D9) without the rule flip.
- **CI quality-gate workflow** — dropped; Vercel already fails deploys on build/type errors.
