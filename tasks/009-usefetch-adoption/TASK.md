# Task 009 — `useFetch` adoption (opportunistic, NOT a sweep)

- **Status:** `todo` (standing convention — no milestone)
- **Opened:** 2026-07-17
- **Owner:** AI agent
- **Sub-app(s):** admin
- **Branch(es):** `dev`
- **Supersedes:** `PHASE3_PARKED_TODO.md` item 3 (remove that line once this task exists).

## Goal

Reduce hand-rolled fetch boilerplate by adopting the existing `useFetch` hook — **opportunistically,
never as a batch migration**. Split out of the original task-008 (now guest-drafts-only).

## Current state (verified 2026-07-17)

- **Hook:** `admin/hooks/useFetch.ts` — `useFetch<T>(url)` → `{ data, loading, error }`. Fetches once on
  mount (and when `url` changes), `Accept: application/json`, unmount-guarded. **No `refetch`, no manual
  trigger, no extra deps.**
- **Adopters: 5**, all on the dashboard (`over-all`, `charts`, `other-status`, `categories-status`,
  `Invitations-categories-status`).
- **Hand-rolled: ~74 files** carry `useState(loading)` + `Axios.get` in `useEffect` (the 2026-07-07
  audit counted ~64).

## The rule (do NOT batch-migrate)

Migrate a file **only when already editing it** for another reason, highest-traffic screens first. A
file is a candidate **only if all** hold:

- ✅ Single `GET` whose result is rendered once (dashboard-widget shape).
- ❌ NOT a paginated / filtered listing → those stay on `use-listing-state`.
- ❌ NOT a multi-request or form screen → leave alone.
- ❌ Does NOT need `refetch` / manual re-trigger → the hook can't do it (see gap).

## Known gap to weigh before wider use

`useFetch` has **no `refetch`**. Sites that re-fetch after an action (delete/toggle/save) are **not**
candidates as-is. **Decision when a real candidate needs it:** extend the hook with `refetch()` (and
maybe `deps`/`enabled`) in that same PR. Default recommendation: **keep it minimal**; add `refetch` only
on first need, not speculatively.

## Definition of done

No "done" — it's a standing convention. Success = new/edited fetch-once screens use `useFetch`, and the
count creeps up over time without a dedicated sweep.

## Todo

- [x] Add a one-line convention note where devs see it — done 2026-07-18: JSDoc at the top of
      `admin/hooks/useFetch.ts`.
- [ ] (Ongoing) When editing a hand-rolled fetch-once file, convert it in the same change.
- [ ] (On first need) Extend `useFetch` with `refetch()`; document the new shape.
- [x] Remove the `useFetch` line from `PHASE3_PARKED_TODO.md` — done 2026-07-18 (item 3 now points here).

## Log

- 2026-07-17 — split out of task-008 so 008 can focus solely on the guest-drafts port.
- 2026-07-18 — one-time setup done: convention note added atop `admin/hooks/useFetch.ts`;
  `PHASE3_PARKED_TODO.md` item 3 retired → points here. Task is now a live standing convention
  (adopt opportunistically; extend with `refetch()` on first real need).
