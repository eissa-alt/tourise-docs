# Queue setup — production (API box)

> For DevOps. Backend server only: `/var/www/alt-static-basecode-backend`.
> Two processes. Both required — one sends, one fires scheduled automations.

`QUEUE_CONNECTION=database` (the `jobs` table comes from migrations — run `php artisan migrate` first).

---

## 1. Queue worker — sends everything

Without it, **nothing is delivered**: automation / invitation / notification email · SMS · WhatsApp,
plus poster generation. Jobs just pile up in `jobs`.

`/etc/supervisor/conf.d/alt-static-basecode-queue.conf`

```ini
[program:alt-static-basecode-queue]
process_name=%(program_name)s_%(process_num)02d
command=php /var/www/alt-static-basecode-backend/artisan queue:work --sleep=3 --tries=3 --max-time=3600
user=www-data
numprocs=2
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stopwaitsecs=3600
redirect_stderr=true
stdout_logfile=/var/log/supervisor/alt-static-basecode-queue.log
```

---

## 2. Scheduler — fires scheduled automations

`app/Console/Kernel.php` runs `automations:dispatch-scheduled` every minute. Without it, *immediate*
automations still send, but anything set to **Schedule for later** sits at `send_status = scheduled`
forever, with no error anywhere.

**Cron (recommended):**

```
* * * * * cd /var/www/alt-static-basecode-backend && php artisan schedule:run >> /dev/null 2>&1
```

**Or supervisor** — `numprocs=1`, never more:

```ini
[program:alt-static-basecode-scheduler]
command=php /var/www/alt-static-basecode-backend/artisan schedule:work
user=www-data
numprocs=1
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/alt-static-basecode-scheduler.log
```

---

## 3. Apply

```bash
sudo supervisorctl reread && sudo supervisorctl update
sudo supervisorctl status
```

---

## 4. After every deploy

```bash
php artisan queue:restart
```

PHP workers hold code in memory — without this they keep running the **previous release** and fail on
new classes. Supervisor respawns them automatically.

---

## 5. Verify

```bash
sudo supervisorctl status          # queue workers RUNNING
php artisan schedule:list          # automations:dispatch-scheduled listed, every minute
php artisan queue:failed           # should stay empty
```

Then send a test automation and confirm the `jobs` table drains; schedule one for +2 minutes and
confirm `send_status` leaves `scheduled` on its own.
