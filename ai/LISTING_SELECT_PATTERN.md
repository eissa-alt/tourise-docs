# Listing & "clean select box" pattern

> The reusable table / selection UI used across the admin. **Don't hand-roll a `<table>`** for a
> listing or a pick-guests screen — compose the shared `components/shared/listing/*` primitives so
> every listing reads as the same "clean select box".

## Where it's used

- **Canonical listing:** `admin/components/admin-modules/e-visa/e-visa-listing.tsx` — filters + a
  selection bar + a checkbox column + client-side bulk fan-out.
- **Select → act:** `admin/components/admin-modules/automation/automation-guest-picker.tsx` — filter
  guests, tick rows (or "select all matching" across pages), then run an automation on them.

## The shared primitives (`admin/components/shared/listing/`)

| Component | What it is |
|---|---|
| `ListingTable.tsx` | Generic `<ListingTable<TItem>>` — the clean card table: `rounded-xl border border-gray-200 bg-white shadow-sm`, sticky `bg-gray-50` header, `divide-y divide-gray-100` rows with `hover:bg-gray-50`, a 5-row loading skeleton, and an empty state. Columns drive everything. |
| `ListingFooter.tsx` | The `showing X to Y of Z` footer + pagination (`rounded-b-xl border-t-0 bg-gray-50`). Feed it a `ListingMeta`. |
| `ListingFilters.tsx` | Declarative filter bar (`fields` + `values` + `onApply`/`onReset`). |
| `ConfirmModal.tsx` / `DialogShell.tsx` | Confirm dialogs / modal chrome (Headless UI v2). |
| `RowActions.tsx` | Per-row action menu (the `actions` column is auto-stuck to the inline edge). |

Contracts live in `admin/interfaces/listing.ts` — `ListingColumn<TItem>`, `ListingMeta`, `SortDir`,
`ListingFilterConfig`, `RowAction`.

## `ListingColumn` — how a column is defined

```ts
type ListingColumn<TItem> = {
   key: string;
   label: string;                       // header text (string only — not a node)
   sortable?: boolean;
   sortKey?: string;                    // defaults to key
   className?: string;                  // <td> class
   headerClassName?: string;            // <th> class
   render?: (row: TItem) => React.ReactNode;  // cell; falls back to row[key]
};
```

`ListingTable` requires `data`, `columns`, `rowKey`, `sortBy`, `sortDir`, `onSort`. For a
non-sorted table pass `sortBy=""`, `sortDir="asc"`, `onSort={() => {}}` and leave columns
non-sortable. Pass `attachedFooter` so the table is `rounded-t-xl` and a `ListingFooter` clips onto
the bottom.

## The select column (checkbox) — copy this verbatim

```tsx
{
   key: 'select',
   label: translate({ id: 'web:select' }),
   headerClassName: 'text-center w-12',
   className: 'text-center w-12',
   render: row => (
      <input
         type="checkbox"
         className="h-4 w-4 cursor-pointer rounded border-gray-300 text-primary-600 focus:ring-primary-500"
         checked={selected.has(row.id)}
         onChange={() => toggleRow(row.id)}
         aria-label={translate({ id: 'web:select' })}
      />
   ),
}
```

Selection state is a `Set<string>` (or `string[]`) of row IDs held in the parent. There is **no
header select-all checkbox** — select-all lives in the toolbar button (below), which keeps the
header clean and lets "select all" mean *all matching across pages*, not just the visible page.

## The selection toolbar

A card above the table, mirroring `e-visa-bulk-filters-bar.tsx`:

```tsx
<div className="flex flex-col gap-3 rounded-xl border border-gray-200 bg-white px-4 py-3 shadow-sm lg:flex-row lg:items-center lg:justify-between">
   <div className="text-sm text-gray-600">
      <Translate id="web:total_selected" />: <span className="font-semibold text-gray-800">{selected.size}</span> {translate({ id: 'web:of' })} {meta.total}
   </div>
   <div className="flex flex-wrap items-center gap-2">
      {/* secondary button:  rounded-md border border-gray-300 bg-gray-100 ... hover:bg-gray-200 */}
      {/* clear button:      rounded-md border border-gray-300 bg-white  ... hover:bg-gray-50  */}
      {/* primary action:    rounded-md bg-primary-600 text-white       ... hover:bg-primary-700 */}
   </div>
</div>
```

Every button is `px-4 py-1.5 text-sm font-medium` with `disabled:cursor-not-allowed
disabled:opacity-50`.

### "Select all matching" across pages

Ticking rows only covers the visible page. To select the whole filtered set without paging the UI,
resolve the IDs server-side: add a lightweight `…/select-ids` endpoint that reuses the listing's
exact filters (the automation flow added `GET /admin/guests/select-ids`, which calls the same
`applyFilters` + `applyAdminGuestAccessFilter` as the listing `index`, so the selection is
guaranteed to match what the list shows). See ledger **D38**.

## Adopting it in a new module

1. Fetch the page from the module's listing endpoint; map the Laravel paginator `meta` →
   `ListingMeta` (`{ total, perPage: per_page, currentPage: current_page, lastPage: last_page, from, to }`).
2. Filters: reuse `SearchGuestsBySuper` (guest screens, URL-driven) or `ListingFilters` (declarative).
3. Build `columns: ListingColumn<Row>[]` — add the select column above if you need selection.
4. Render `<ListingTable … attachedFooter />` then `<ListingFooter meta onPageChange />`.
5. Selection → hold a `Set<string>`; add a toolbar with the count + select-all + clear + the
   primary action.

Do **not** re-implement the table, the header/hover styling, the skeleton, or the pagination — the
primitives own them, and matching them by hand is how the UI drifts.
