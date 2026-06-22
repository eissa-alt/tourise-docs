# Countdown Hook Replacement Playbook (portable)

> **Reusable across the ALT project family** (Next.js pages-router apps). Recipe to **drop `reactjs-countdown-hook`** — whose `react@^16.9.0` peer dependency emits an install warning on our React 18 lineage — by swapping it for a tiny, dependency-free local `useTimer` hook (`components/home/use-timer.ts`).
>
> Executed on **alt-static-basecode** (2026-06-22, frontend `17f3451` · landing `d4dbd74`). This doc is the *method + the copy-paste source* so the same change can be replayed onto **cyan-basecode** (and any other clone) later.
>
> **Scope:** one self-contained dev-ergonomics/hygiene change — remove a single unmaintained dep with one call site per app. Honors the **no-framework-bump** rule (React stays 18). Pairs with [`DEPENDENCY_HYGIENE_PLAYBOOK.md`](DEPENDENCY_HYGIENE_PLAYBOOK.md) (the general method); this is the concrete recipe for this one package.

---

## 0. The symptom

`yarn install` prints:

```
warning "reactjs-countdown-hook@1.0.5" has incorrect peer dependency "react@^16.9.0".
```

The hook **works fine on React 18** — this is console-only — but it is an unmaintained single-purpose dep with exactly one call site per app (`components/home/timer.tsx`), so a local reimplementation is cheaper to own than the dependency.

---

## 1. What the package actually does

`useTimer(count, onFinish?)` counts `count` seconds down to zero on a 1-second `setInterval` and returns:

| Field | Type | Notes |
|---|---|---|
| `isActive` | `boolean` | false once it hits zero |
| `counter` | `number` | remaining seconds |
| `seconds` / `minutes` / `hours` / `days` | `string` | **zero-padded** (e.g. `"05"`); **empty `""` until the first tick** (~1s) |
| `pause` / `resume` / `reset` | `() => void` | controls |

Two faithful-port nuances to preserve so the UI is byte-identical:

1. **Empty-until-first-tick:** the four display fields start as `""` and only populate after the first 1s interval — the original computes them inside the interval, not on mount.
2. **One-tick display lag:** the original computes the display from `counter.count` *before* the decrement is applied. Cosmetic for a countdown; the local hook mirrors it by computing from the current `counter.count` each tick.

`timer.tsx` only consumes `{ seconds, minutes, hours, days }`, but the local hook keeps the full return shape so it is a true drop-in.

---

## 2. The local replacement — copy this verbatim

Create `components/home/use-timer.ts` (3-space indent matches the repo):

```ts
import { useEffect, useState } from 'react';

type TimerState = {
   count: number;
   seconds: string;
   minutes: string;
   hours: string;
   days: string;
};

type UseTimerReturn = {
   isActive: boolean;
   counter: number;
   seconds: string;
   minutes: string;
   hours: string;
   days: string;
   pause: () => void;
   resume: () => void;
   reset: () => void;
};

const pad = (value: number): string => (String(value).length === 1 ? `0${value}` : `${value}`);

/**
 * Local countdown timer hook — drop-in replacement for `reactjs-countdown-hook`'s
 * `useTimer`, dropped to clear its React 16 peer-dependency warning. Counts `count`
 * seconds down to zero, exposing zero-padded days/hours/minutes/seconds.
 */
export const useTimer = (count: number, onFinish?: () => void): UseTimerReturn => {
   const [isActive, setIsActive] = useState(true);
   const [counter, setCounter] = useState<TimerState>({
      count,
      seconds: '',
      minutes: '',
      hours: '',
      days: '',
   });

   useEffect(() => {
      let intervalId: ReturnType<typeof setInterval>;

      if (isActive) {
         intervalId = setInterval(() => {
            if (counter.count >= 1) {
               setCounter(prev => ({ ...prev, count: prev.count - 1 }));
            } else {
               setIsActive(false);
               onFinish?.();
            }

            const secondCounter = counter.count % 60;
            const minuteCounter = Math.floor((counter.count % 3600) / 60);
            const hourCounter = Math.floor((counter.count % (3600 * 24)) / 3600);
            const daysCounter = Math.floor(counter.count / (3600 * 24));

            setCounter(prev => ({
               ...prev,
               seconds: pad(secondCounter),
               minutes: pad(minuteCounter),
               hours: pad(hourCounter),
               days: pad(daysCounter),
            }));
         }, 1000);
      }

      return () => clearInterval(intervalId);
   }, [isActive, counter.count, onFinish]);

   const pause = () => setIsActive(false);
   const resume = () => setIsActive(true);
   const reset = () => {
      setCounter({ count, seconds: '00', minutes: '00', hours: '00', days: '00' });
      setIsActive(true);
   };

   return {
      isActive,
      counter: counter.count,
      seconds: counter.seconds,
      minutes: counter.minutes,
      hours: counter.hours,
      days: counter.days,
      pause,
      resume,
      reset,
   };
};
```

---

## 3. The recipe (per app that uses the hook)

1. **Add** `components/home/use-timer.ts` (§2).
2. **Repoint the import** in `components/home/timer.tsx` — the only change to that file:

   ```diff
   - import { useTimer } from 'reactjs-countdown-hook';
   + import { useTimer } from './use-timer';
   ```

3. **Delete the dead ambient shim** `reactjs-countdown-hook.d.ts` at the app root (it only contained `declare module 'reactjs-countdown-hook';` — useless once nothing imports the module).
4. **Drop the dependency** from `package.json` (remove the `"reactjs-countdown-hook": "^1.0.5",` line). `yarn.lock` is gitignored, so the install prunes it on the next clean install — re-run `yarn install` to confirm.
5. **Verify** no stray references remain:

   ```bash
   rg -n --glob '!node_modules' --glob '!.next' "reactjs-countdown-hook" .
   ```

   Expect only the doc-comment mention inside `use-timer.ts`.

---

## 4. Find every call site first

```bash
rg -n --glob '!node_modules' --glob '!.next' "reactjs-countdown-hook|useTimer" .
```

On **alt-static-basecode** this was `components/home/timer.tsx` (+ the `reactjs-countdown-hook.d.ts` shim + the `package.json` line) in **both** `-frontend` and `-landing`; `-admin` never used it.

> 🔶 **CYAN DELTA.** cyan-basecode **kept** this dependency (it deferred the warning as low-priority). cyan has **only `cyan-frontend`** using it — `cyan-frontend/components/home/timer.tsx`, `cyan-frontend/reactjs-countdown-hook.d.ts`, and the `cyan-frontend/package.json` line. **cyan has no `-landing` app**, so this is a single-app change there. Re-run the `rg` scan in cyan before acting in case a second call site appears.

---

## 5. Quality gate

Per app, both must be green (the hygiene gate):

```bash
yarn type-check     # tsc — catches the removed module symbol if a call site was missed
yarn production     # the real Next build
```

A removed dep with a faithful drop-in has **zero runtime change**; the gate plus the §3.5 grep is the safety net. For full confidence, smoke the homepage countdown once (it renders empty for ~1s, then ticks).

---

## 6. Git / tracking

- One branch per repo off `dev`; commit `chore(deps): replace reactjs-countdown-hook with local useTimer hook`.
- Stage `package.json` + `components/home/` + the `reactjs-countdown-hook.d.ts` deletion. (`yarn.lock` gitignored → manifest-only diff.)
- alt-static-basecode SHAs for cross-cite: **frontend `17f3451`**, **landing `d4dbd74`** (both off the spinner-cleanup commits `545aa8a` / `790f5fd`).
- **Don't push without instruction.**

---

## 7. Pitfalls checklist (TL;DR)

| Pitfall | Guard |
|---|---|
| forgot a call site | `rg "reactjs-countdown-hook\|useTimer"` BEFORE editing; `type-check` catches a missed import |
| dropped the empty-until-first-tick behavior | keep the display computed *inside* the interval, fields init `''` |
| left the `.d.ts` shim | delete `reactjs-countdown-hook.d.ts` — it's dead once the module isn't imported |
| bump-has-no-diff confusion | `yarn.lock` is gitignored; the `package.json` line removal IS the diff — re-install to prune |
| forgot the landing app (alt) | alt has `-frontend` **and** `-landing`; 🔶 cyan has frontend only |
| assumed cyan already removed it | cyan **kept** the dep — this playbook is the not-yet-done port for cyan |
