<!-- report
eyebrow: Process · Production
subtitle: The standard steps for every backend deploy, run as www-data
meta: Server=tourise-v2-backend-prod|Folder=/var/www/tourise-backend|Checked=2026-10-19
footer: Backend deploy
-->
# Backend deploy (production)

> For whoever deploys the backend. Server `tourise-v2-backend-prod`, folder `/var/www/tourise-backend`.
> Written from the owner's own command list on 2026-10-19. A release with its own runbook (for example
> [security/RELEASE_RUNBOOK_WAVE_1](../security/RELEASE_RUNBOOK_WAVE_1/RELEASE_RUNBOOK_WAVE_1.md)) adds its
> steps to this list and says which of the three apps goes first.

## The server (checked 2026-10-19)

| Item | What we found |
|---|---|
| PHP | 8.5.4, both the command line and the website (`php8.5-fpm`). Local machines run 8.2, so the tests run on 8.2. |
| Folder owner | `www-data`. Run every `git`, `composer` and `php artisan` command as `www-data` (`sudo -u www-data ...`). A cache or log file made by another user can't be written by the website, which then fails. It also avoids git's "dubious ownership" stop. |
| Lock file | `composer.lock` is not in git (gitignored). The server keeps its own, from 16 Aug 2026, and `composer install` installs from it. |
| OPcache | Default settings: PHP notices changed files within 2 seconds by itself. The php-fpm reload makes the switch clean. |
| Caches | None on 2026-10-19: `bootstrap/cache/` has no `config.php` and no routes file. |

## Every deploy

```bash
cd /var/www/tourise-backend

# 1. Note where you start, and check nobody changed files by hand
sudo -u www-data git log -1 --format='%h %s'
sudo -u www-data git status

# 2. Pull
sudo -u www-data git pull

# 3. Only if composer.json changed in this pull (see below)
sudo -u www-data composer install --no-dev --optimize-autoloader

# 4. Database (asks "Are you sure?" in production)
sudo -u www-data php artisan migrate

# 5. Caches (read the warning below first)
sudo -u www-data php artisan config:cache
sudo -u www-data php artisan route:cache

# 6. The queue worker picks up the new code
sudo -u www-data php artisan queue:restart

# 7. The website picks up the new code
sudo systemctl reload php8.5-fpm
```

**Did composer.json change?** After step 2:
`sudo -u www-data git diff --stat ORIG_HEAD HEAD -- composer.json`. No output means skip step 3.

> [!WARNING]
> **Step 5 is safe only from backend 5d2b23b on** (PR #69, on `dev` since 2026-10-19). Before it, six
> settings were read with `env()`, which returns nothing once the config is cached: the root admin login alert
> would go to nobody, and automation emails would leave the bulk mailer.

Check before step 5:

```bash
sudo -u www-data git merge-base --is-ancestor 04a0a5e HEAD && echo "safe to cache"
```

If it prints nothing, run `sudo -u www-data php artisan optimize:clear` instead of step 5.

**No clear commands needed.** `config:cache` and `route:cache` delete the old cache before building the new
one, so `config:clear` and `route:clear` add nothing. `cache:clear` empties a different cache (rate limit
counters, the mobile app config) that a deploy does not change; it is under "Only when needed".

**After any .env change**, run steps 5 and 6 again. With a cached config, Laravel does not read `.env`, so a
change does nothing until the cache is rebuilt, and the queue worker keeps the old values until it restarts.

## Check after

```bash
curl -s https://api-register.tourise.com/api/admin/roles/select
# {"status":"error","message":"Unauthenticated."}

sudo -u www-data php artisan config:show app.debug   # false
sudo -u www-data php artisan queue:failed            # nothing new
```

## Only when needed

```bash
# Fresh server: builds vendor/ (then set the permissions below)
sudo -u www-data composer install --no-dev --optimize-autoloader

# Permissions: on a fresh server, or after a file got the wrong owner
sudo chown -R www-data:www-data storage bootstrap/cache
sudo chmod -R 775 storage bootstrap/cache

# Public file links (one time)
sudo -u www-data php artisan storage:link

# A seeder a task asks for
sudo -u www-data php artisan db:seed --class=<Name>

# Empty the data cache (rate limit counters, mobile app config), when a task asks for it
sudo -u www-data php artisan cache:clear

# Edit .env (then steps 5 and 6). Never paste its contents anywhere.
sudo -u www-data nano .env
sudo chown www-data:www-data .env

# git shows every file as changed after a chmod
sudo -u www-data git config core.fileMode false
```
