# Task 010 — RESTful rename map (Tier 2/3 cutover)

**Status:** PROPOSED — awaiting review before execution. Tier 0+1 (dead-code cleanup) already landed
(backend `4cf7036`). This map drives the **hard cutover**: backend `routes/api.php` + admin API client
(+ frontend/mobile if a consumed URI changes) move together.

All paths below are under the `api/admin/` prefix unless noted. `{id}` gains `->whereUuid('id')`.

---

## A. Pattern rules (apply to every matching resource)

| # | Old pattern | New pattern | Rationale |
|---|---|---|---|
| P1 | `/<res>-select` | `/<res>/select` | select is a sub-resource, not a sibling |
| P2 | `PATCH /<res>/block/{id}` + `PATCH /<res>/activate/{id}` | **`PATCH /<res>/{id}/toggle-status`** (replaces both) | per your call — consolidate, no legacy pair |
| P3 | `/<res>/{id}` verbs unchanged (`GET index`, `POST store`, `GET/{id} show`, `PUT/{id} update`, `DELETE/{id} destroy`) | same, + `whereUuid` | already RESTful |

**P1 targets:** admins, areas, badges, categories, countries, gates, guest-statuses, speakers, sponsors,
speaker-labels, sponsor-labels, sms-templates, email-templates, titles (`titles-select-all` →
`titles/select-all`; `titles-select/{category}` → `titles/select/{category}`).

**P2 targets (block+activate → toggle-status):** admins, areas, badges, categories, gates,
guest-statuses, email-templates, speakers, sponsors, speaker-labels, sponsor-labels, titles,
sms-templates. (SMTP-configs already uses `toggle-active`/`make-default` — leave as-is, cyan does too.)

---

## B. Resource-specific renames (non-pattern)

### Guests
| Old | New |
|---|---|
| `POST /guests-new` | `POST /guests` |
| `PUT /guests-update/{id}` | `PUT /guests/{id}` |
| `POST /guests-update-cat/{id}` | `PATCH /guests/{id}/category` |
| `POST /guests-regenerate-smp/{id}` | `POST /guests/{id}/regenerate-smp` |
| `POST /guests-upload-zip` | `POST /guests/upload-zip` |
| `GET /guests-printed-since` | `GET /guests/printed-since` |
| `POST /match-guests-images` | `POST /guests/match-images` |
| `POST /import-guests-excel` | `POST /guests/import-excel` |
| `POST /upload` (uploadAdmin) | `POST /guests/upload` |
| `POST /upload-document` (uploadDocumentAdmin) | `POST /guests/upload-document` |
| `GET /guest-data-offline` | `GET /guests/data-offline` |
| `POST /guest-data-sync` | `POST /guests/data-sync` |

### Categories
| `GET /categories-by-slug/{slug}` | `GET /categories/slug/{slug}` |

### Gates  *(⚠ naming choices — see open questions)*
| Old | New (proposed) |
|---|---|
| `GET /gates-select` | `GET /gates/select` |
| `GET /gates-show/{id}` (showAgentSide) | `GET /gates/{id}/agent-view` |
| `PUT /setup-gate/{id}` | `PUT /gates/{id}/setup` |
| `PUT /gates-start-scanning/{id}` | `PUT /gates/{id}/start-scanning` |
| `PUT /gates-pause-scanning/{id}` | `PUT /gates/{id}/pause-scanning` |
| `PUT /gates-scan/{id}` | `PUT /gates/{id}/scan` |
| `POST /gates-search-guests-by-name` | `POST /gates/search-guests` |
| `POST /gates-upload-scan-image/{scanId}` | `POST /gates/scans/{scanId}/image` |
| `PUT /gates-update-scan-guest/{scanId}` | `PUT /gates/scans/{scanId}/guest` |

**Also the non-`/admin` agent-app variants** (same handlers, no `admin` prefix):
`gates-scan/{id}`, `gates-search-guests-by-name`, `gates-upload-scan-image/{scanId}`,
`gates-update-scan-guest/{scanId}` → mirror under a `scan/` prefix, e.g. `PUT /scan/gates/{id}/scan`, etc.
⚠ **These are consumed by the scanner/agent app** — confirm that client is in scope for the cutover.

### Invitations
| Old | New |
|---|---|
| `GET /invitations-list/{id}` | `GET /invitations/{id}/list` |
| `POST /invitations-send-bulk/{id}` | `POST /invitations/{id}/send-bulk` |
| `GET /invitation-details/{id}` | `GET /invitations/{id}/details` |
| `PUT /invitation-details/{id}` | `PUT /invitations/{id}/details` |
| `PUT /invitation-modify-upto/{id}` | `PUT /invitations/{id}/modify-upto` |
| `POST /invitations-update-cat/{id}` | `PATCH /invitations/{id}/category` |
| `POST /invitations-update-cat-bulk/{id}` | `PATCH /invitations/{id}/category-bulk` |
| `POST /invitations-extract-bulk/{id}` | `POST /invitations/{id}/extract-bulk` |
| `PATCH /invitations/block/{id}` + `activate/{id}` | `PATCH /invitations/{id}/toggle-status` (P2) |
| `PATCH /invitations/invite/{id}` | `PATCH /invitations/{id}/invite` (kept — not a status toggle) |

### Social-media-links-per-temp
| `GET /social-media-links-per-temp-all/{template_id}` | `GET /social-media-links-per-temp/all/{template_id}` |

### Countries
`countries` has no block/activate (removed in Tier 1); `countries-select` → `countries/select` (P1).

---

## C. Frozen (do NOT rename)
- All `mobile/*` — mobile contract, already RESTful.
- `Route::middleware('signed')` `files/guest-doc/...` — signed-URL contract (D14).
- Dashboard (`admin/dashboard/...`), event-days, sessions, workshops, publications, media-*,
  meeting-rooms, notifications, roles, smtp-configs, sms-provider-configs, export-templates,
  guest-drafts, guest-import-runs — **already RESTful** (the ported/newer modules). No change.

---

## D. Open naming decisions (need your call before I execute)

1. **Gates action verbs** — `gates/{id}/agent-view` vs `gates/{id}/show-agent`? and
   `gates/scans/{scanId}/image` vs `gates/{scanId}/upload-scan-image`? (I proposed the cleaner forms.)
2. **Scanner/agent app** — are the non-`/admin` `gates-*` agent routes in scope? If that client can't be
   updated in lockstep, we keep those 4 URIs frozen and only rename the `/admin` ones.
3. **`/admin/upload` + `/admin/upload-document`** (guest admin uploads) → fold under `/guests/`? (proposed yes.)

## E. Execution order once approved
1. Backend: rewrite `routes/api.php` admin block into `prefix()->group()` + new URIs + `whereUuid` + `toggle-status` (add `toggleStatus()` to controllers lacking it; remove `block`/`activate` where consolidated).
2. `php artisan route:list` → confirm every new URI present, old ones gone.
3. Admin repo: repoint the API client / callers (grep each old path); block/activate buttons → toggle-status.
4. Frontend: update any renamed public/admin call.
5. Gates: backend + phpstan + tests; admin/frontend type-check + build. Dead-link gate (grep old paths = 0).
6. Tier 4 (separate): `admin.can:` gating rollout.
