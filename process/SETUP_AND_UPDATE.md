# ALT Static Basecode — Setup & Update Runbook

How to get the project running on a machine — **two scenarios**:

- **[A. First-time setup](#a-first-time-setup-fresh-machine--fresh-clone)** — nothing installed yet (fresh clone).
- **[B. Update after a pull](#b-update-after-a-pull-already-installed--older-version)** — you already had it running and just pulled `dev`.

> ⚠️ **Read this first — the lockfiles are gitignored.**
> `yarn.lock`, `package-lock.json`, and `composer.lock` are **not committed**. So after a pull, your *local* lockfile is stale and a plain `install` can silently keep removed/old packages. That's why **Scenario B uses a clean reinstall + cache clear**, and why the backend uses `composer update` (not `install`).
> Recent changes that make this matter: Tailwind v3→v4, Next 12→15, React 17→18, Laravel 11→12, and the `babel.config.js`→SWC swap.

---

## Prerequisites (both scenarios)

| Tool | Version |
|---|---|
| Node.js | 20 LTS (Next 15 needs ≥18.18) |
| Yarn | 1.x (`npm i -g yarn`) |
| PHP | 8.2 |
| Composer | 2.x |
| MySQL | running locally (backend default `DB_CONNECTION=mysql`) |

**Repos** (three separate git repos, cloned side-by-side under one parent folder — no monorepo):

```
alt-static-basecode-repos/
├── alt-static-basecode-backend/    # Laravel 12 API (serves admin, frontend + mobile)
├── alt-static-basecode-admin/      # Next 15 CMS
└── alt-static-basecode-frontend/   # Next 15 registration site
```

---

## A. First-time setup (fresh machine / fresh clone)

### 1. Clone the three repos side-by-side

```bash
mkdir -p alt-static-basecode-repos && cd alt-static-basecode-repos
git clone https://github.com/eissa-alt/alt-static-basecode-backend.git
git clone https://github.com/eissa-alt/alt-static-basecode-admin.git
git clone https://github.com/eissa-alt/alt-static-basecode-frontend.git
# default working branch is `dev`:
for r in backend admin frontend; do (cd alt-static-basecode-$r && git checkout dev); done
```

### 2. Backend — `alt-static-basecode-backend/`

```bash
cd alt-static-basecode-backend
composer install                 # no lock present yet → resolves from composer.json
cp .env.example .env             # then fill in DB + secrets (see note below)
php artisan key:generate
php artisan storage:link         # public file/media access (badges, images)
php artisan migrate              # create schema  (add --seed if you have seeders to run)
php artisan serve                # http://127.0.0.1:8000
# Optional (chat / realtime / push features): in a second terminal
# php artisan reverb:start
```

> **Background processes (run in their own terminals).** The API alone doesn't *send* or *fire* anything:
> - `php artisan queue:work` — processes queued sends (automation / invitation / notification email · SMS · WhatsApp · poster generation). Prod runs this under **supervisor**. Without it, nothing is actually sent.
> - `php artisan schedule:work` — the Laravel scheduler; fires **scheduled automations** (runs `automations:dispatch-scheduled` every minute — **new in ledger D39**). Prod uses a cron `* * * * * php artisan schedule:run` **or** a supervisor `schedule:work` program. Without it, *immediate* automations still send (dispatched on create), but *scheduled* ones sit in `send_status = scheduled` forever.

> **`.env` secrets:** `.env` is gitignored. After `cp .env.example .env`, set your local `DB_DATABASE` / `DB_USERNAME` / `DB_PASSWORD`, mail, Firebase (push), and any API keys — get real values from a teammate / the secrets store.

> **Quality gate + pre-commit hook (backend).** `composer install` auto-installs the Pint pre-commit
> hook (via a `post-autoload-dump` script that sets `git config core.hooksPath .githooks`). From then on,
> committing formats staged `*.php` with Pint automatically (it graceful-skips if Pint isn't installed).
> The full gate before a push is **`composer qa`** = `pint --test` (`composer lint`) + `phpstan analyse`
> (`composer analyse`) + `php artisan test`. The repo is Pint-clean (ledger D10), so use `pint --test`,
> not the old `pint --dirty`. Larastan starts at **level 0** with a baseline in `phpstan-baseline.neon`
> — see `tasks/003-backend-tooling-chain/TASK.md` for the ratchet plan.

### 3. Admin / Frontend (same steps, per app)

```bash
cd alt-static-basecode-admin        # repeat for -frontend
yarn install
# .env.local is gitignored and has NO committed example → get it from a teammate:
#   place .env.local (and .env.production) in the app root before running.
yarn local                               # dev server
```

> **JS env files:** unlike the backend, the JS apps have **no `.env.example`**. You must obtain `.env.local` (and `.env.production` for prod builds) from a teammate / secrets store — they hold the API base URL and keys.

### 4. Verify a build (optional but recommended)

```bash
# in each JS app:
yarn type-check && yarn production
# admin only — sidebar featureId ↔ inferFeatureId parity (D33/D34); NOT covered by the above:
(cd alt-static-basecode-admin && yarn check:rbac)
# backend (full gate):
composer qa            # = pint --test + phpstan analyse + php artisan test
```

> **Running `yarn production` without a `.env.production`.** The `production` script is
> `env-cmd -f .env.production next build`, so it errors (`Failed to find .env file`) if you only have
> `.env.local` (dev) — common now that envs are split across a dedicated server + Vercel. To run the
> **build gate** anyway, use a **throwaway copy** and delete it right after:
>
> ```bash
> cp .env.local .env.production && yarn production; rm -f .env.production
> ```
>
> Safe because: `.env.production` is **gitignored** (never committed), and this build is a **compile
> check only** — the dev API URL gets baked in, so **discard the output, don't deploy it**. Always
> `rm` the temp file when done (the trailing `rm` runs even if the build fails).

---

## B. Update after a pull (already installed / older version)

Run **after** `git pull origin dev` in each repo. Because lockfiles are gitignored and recent days changed frameworks + the build compiler, do a **clean reinstall**, not an incremental one.

### Backend — `alt-static-basecode-backend/`

```bash
cd alt-static-basecode-backend
git pull origin dev
composer update              # NOT `composer install` — your local lock is stale; update re-resolves from composer.json
php artisan optimize:clear   # clear stale config/route/view/compiled cache (Laravel 11→12)
php artisan migrate          # REQUIRED after P24.25 — adds 2026_07_25_000002 (automation scheduling columns)
# Restart any running background workers so they pick up the new code:
#   php artisan queue:work   (sends)  ·  php artisan schedule:work  (fires scheduled automations — new)
```

### Admin / Frontend (per app)

```bash
cd alt-static-basecode-admin        # repeat for -frontend
git pull origin dev
rm -rf node_modules .next yarn.lock package-lock.json   # drop stale lock + old Babel/SWC + Tailwind-v3 build cache
yarn install
yarn local                               # or: yarn type-check && yarn production
```

### Why clean (not just `install`)

| Step | Reason |
|---|---|
| `composer update` (not `install`) | composer.lock is gitignored; a stale local lock makes `composer install` **warn and install old deps**. `update` re-resolves from the new `composer.json`. |
| `rm -rf yarn.lock package-lock.json` | gitignored → your local lock is stale. Deleting forces a fresh resolve from the new `package.json` (the removals + floor-bumps). |
| `rm -rf .next` | today's `babel.config.js` removal switched the compiler to **SWC**; stale `.next` artifacts (Babel-era + Tailwind v3) can cause build/runtime errors. |
| `php artisan optimize:clear` | the Laravel 11→12 upgrade can leave stale cached config/routes/compiled services. |

---

## Caveats / troubleshooting

- **`.env*` are gitignored.** If new env keys were added recently, nothing in git will tell you — add them to your local `.env` / `.env.local` / `.env.production` manually (ask a teammate).
- **Backend resolution oddities:** nuclear option → `rm -f composer.lock && composer install`.
- **JS resolution oddities / native module errors:** ensure you removed `node_modules` *and* the lockfiles before `yarn install` (the clean step above).
- **Reproducibility note:** because lockfiles aren't committed, every clean install floats to the latest in-range versions. That's by design for this project — expect minor version drift between machines.
