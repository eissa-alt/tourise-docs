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
- **Adopters: 15** (was 5). The 5 dashboard widgets (`over-all`, `charts`, `other-status`,
  `categories-status`, `Invitations-categories-status`) + 10 converted 2026-07-18: `profile-details`
  and 9 option selects (`admins`, `areas`, `badges-select-multi`, `categories-select-multi`,
  `countries`, `email-template-invitations`, `guest-statuses`, `sms-template`, `titles-select-all`).
- **Hand-rolled: ~64 files** carry `useState(loading)` + `Axios.get` in `useEffect` (was ~74; 10
  converted on 2026-07-18).

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
- 2026-07-18 — first opportunistic batch: converted 10 fetch-once components (admin `1144582`,
  net −192 ln) — `profile-details` + 9 selects. Adopters 5 → 15. Gates green (type-check + `next
  build`). En route: fixed a latent `Item.slug`-required bug (masked by `useState<any>`) in the
  email-template + sms-template selects → made optional. Skipped `badges-select` (`[lang, role]` dep)
  and `categories-select` (post-fetch filter) as non-clean swaps.
