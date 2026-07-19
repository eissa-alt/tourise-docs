# Mobile response-shape deltas — Task 007 (response unification)

**Date:** 2026-07-19
**Severity:** Breaking response-shape change (payload moves under `data`; control fields added)
**Affects:** The Flutter app — **every** `mobile/*` endpoint plus `/app-config`.
**Reference:** [`../upgrades/cleanup-hardening/CONTROLLER_REFACTOR_PLAN.md`](../upgrades/cleanup-hardening/CONTROLLER_REFACTOR_PLAN.md), [`../upgrades/cleanup-hardening/BASE_API_CONTROLLER_PLAN.md`](../upgrades/cleanup-hardening/BASE_API_CONTROLLER_PLAN.md), `BACKEND_INCOMING_CHANGES_FOR_MOBILE.html`
**Status:** **IMPLEMENTED (backend `dev`) — 2026-07-19.** Every `mobile/*` controller below is migrated to the standard envelope and its feature tests updated (`composer qa` green apart from 3 pre-existing D14 signed-avatar/env failures). `/app-config` is intentionally left unwrapped (§18). This doc is the hand-off the mobile team consumes to adapt the Flutter client; the change is live on backend `dev` awaiting the mobile ack before `dev` → `main`.

> This is the "adapt later" artifact required by the locked Task 007 formula (point 2): *breaking the mobile contract is accepted, but a per-endpoint delta is generated so the mobile team can adapt.* The rows below now describe the shipped `dev` behaviour, not a future spec.

---

## 1. The target envelope

Every JSON response becomes the standard envelope (from the 006 `ApiResponse` trait):

```jsonc
// success
{ "success": true,  "status": "success", "message": "success", "data": <payload>, "meta": { ... } /* optional */ }
// error
{ "success": false, "status": "failed",  "message": "<reason>", "error": "<reason>", "data": <reason|errors>, "errors": { ... } /* optional */ }
```

- `status` keeps its **legacy values** (`"success"` / `"failed"`, or the endpoint's existing custom value) so any superset reader keeps working.
- `success` (bool) and `message` (string) are **new** on every response.
- **`data` holds what is today the top-level body.** This is the breaking part: fields the app reads at the root today move **one level down**, under `data`.

## 2. The transform rule (how to read every row below)

Unless a row says otherwise:

1. **Current body → `data`.** Whatever the endpoint returns today at the root becomes the value of `data`.
2. **Prepend** `success` + `status` + `message`.
3. **Errors** (`4xx`/`5xx`) → the error envelope; the human string goes to `message`; validation bags to `errors`.
4. **HTTP status codes are unchanged** (200/201/204/400/401/403/404/409/422/429/500 stay as-is).
5. **Routes are unchanged** — this is a body refactor only (`git diff routes/api.php` stays empty).

Pagination/counter fields that live at the root today (`currentPage`, `totalPages`, `pagination`, `totalNotifications`, …) move **inside `data`** with everything else (they are *not* hoisted into `meta` — keeping them beside their list is the least-ambiguous transform).

---

## 3. Identity / Auth — `mobile/identity/*` (`MobileAuthController`)

| Method | Path | Current shape | New shape | Note |
|---|---|---|---|---|
| POST | `/check-email` | `{ hasError, message, OTPSent?, registerURL? }` | `{ success, status, message, data: { hasError, OTPSent?, registerURL? } }` | `success` = `!hasError`. `message` unchanged. `hasError` **retained inside `data`** for back-compat during migration. |
| POST | `/verify-otp` | success `{ user, token }`; errors `{ message }` (400/404/429) | `{ success, status, message, data: { user, token } }` | `user`/`token` now under `data`. Errors → error envelope. |
| GET | `/register` | `302` redirect | **unchanged** | Redirect, not JSON. |
| GET | `/register-with-code` | `302` redirect | **unchanged** | Redirect, not JSON. |
| GET | `/logout` | `{ message }` | `{ success, status, message, data: null }` | message-only → `data:null`. |
| GET | `/delete-account` | `{ message }` | `{ success, status, message, data: null }` | |
| POST | `/device-tokens` | success `{ message, user }`; error `{ error }` (400) | `{ success, status, message, data: { user } }` | `user` under `data`; validation error → error envelope. |
| PATCH | `/profile` | success `{ user }`; validation `{ status:'failed', errors }` (422) | `{ success, status, message, data: { user } }` / error envelope | Already carries `status:'failed'` on the 422 — now full envelope. |

## 4. Event Days — `mobile/event-days` (`MobileEventDayController`)

| Method | Path | Current shape | New shape | Note |
|---|---|---|---|---|
| GET | `/fetch` | `{ programs: [...] }` | `{ success, status, message, data: { programs: [...] } }` | Wrapper key `programs` preserved under `data`. |

## 5. Speakers — `mobile/speakers` (`MobileSpeakerController`)

| Method | Path | Current shape | New shape | Note |
|---|---|---|---|---|
| GET | `/` | `{ currentPage, totalPages, totalSpeakers, speakers: [...] }` | `{ success, status, message, data: { currentPage, totalPages, totalSpeakers, speakers } }` | |
| GET | `/{id}` | success `{ speaker }`; 404 `{ message }` | `{ success, status, message, data: { speaker } }` / error envelope | |

## 6. Sponsors — `mobile/sponsors` (`MobileSponsorController`)

| Method | Path | Current shape | New shape | Note |
|---|---|---|---|---|
| GET | `/` | `{ sponsors: [...] }` | `{ success, status, message, data: { sponsors: [...] } }` | |

## 7. Attendees — `mobile/attendees` (`MobileAttendeeController`)

| Method | Path | Current shape | New shape | Note |
|---|---|---|---|---|
| GET | `/` | `{ attendees, currentPage, totalPages, totalItems }` | `{ success, status, message, data: { attendees, currentPage, totalPages, totalItems } }` | |

## 8. Sessions — `mobile/sessions` (`MobileSessionController`)

| Method | Path | Current shape | New shape | Note |
|---|---|---|---|---|
| GET | `/` | `{ sessions, pagination }` | `{ success, status, message, data: { sessions, pagination } }` | |
| GET | `/search` | `{ sessions, pagination }` | `{ success, status, message, data: { sessions, pagination } }` | Empty-keyword branch same shape. |
| GET | `/{id}` | **flat object** (no wrapper); 404 `{ message }` | `{ success, status, message, data: { ...session } }` / error envelope | **Flat → wrapped: high-impact.** Detail fields move under `data`. |
| GET | `/favorite` | **flat array** | `{ success, status, message, data: [...] }` | **Flat array → wrapped.** |
| POST | `/favorite` | `{ message }`; validation `{ message, errors }` (400) | `{ success, status, message, data: null }` / error envelope | |

## 9. Session feedback — `mobile/sessions/{id}/feedback` (`MobileSessionFeedbackController`)

| Method | Path | Current shape | New shape | Note |
|---|---|---|---|---|
| POST | `/{id}/feedback` | `{ message, data }` (201); 404 `{ message }`; 409 `{ message, error }`; 422 `{ message, errors }` | `{ success, status, message, data }` / error envelope | Already has `data`; add `success`/`status`, move `message` to envelope. 409 `error` → `errors`/`message`. |
| GET | `/{id}/feedback` | `{ data: <feedback|null> }` | `{ success, status, message, data: <feedback|null> }` | |

## 10. Workshops — `mobile/workshops` (`MobileWorkshopController`)

| Method | Path | Current shape | New shape | Note |
|---|---|---|---|---|
| GET | `/` | `{ workshops, pagination }` | `{ success, status, message, data: { workshops, pagination } }` | |
| GET | `/search` | `{ workshops, pagination }` | `{ success, status, message, data: { workshops, pagination } }` | |
| GET | `/{id}` | **flat object**; 404 `{ message }` | `{ success, status, message, data: { ...workshop } }` / error envelope | **Flat → wrapped.** |
| GET | `/registered` | **flat array** | `{ success, status, message, data: [...] }` | **Flat array → wrapped.** |
| POST | `/{id}/register` | `{ message, workshop }` (200); 404 `{ message }`; 409 `{ message, error }`; 500 `{ message }` | `{ success, status, message, data: { workshop } }` / error envelope | `workshop` under `data`. |
| DELETE | `/{id}/register` | `204` no body | **unchanged** | 204 stays bodyless. |

## 11. Workshop feedback — `mobile/workshops/{id}/feedback` (`MobileWorkshopFeedbackController`)

Identical shape to Session feedback (§9).

## 12. Publications — `mobile/publications` (`MobilePublicationController`)

| Method | Path | Current shape | New shape | Note |
|---|---|---|---|---|
| GET | `/` | **flat array** | `{ success, status, message, data: [...] }` | **Flat array → wrapped.** Flutter `MediaResponse.fromJson` must read `data`. |

## 13. Media Center — `mobile/media-center` (`MobileMediaCenterController`)

| Method | Path | Current shape | New shape | Note |
|---|---|---|---|---|
| GET | `/` | `{ videos, documents, images }` | `{ success, status, message, data: { videos, documents, images } }` | Grouped object moves under `data`. |

## 14. QR scanner — `mobile/qr` (`MobileQrController`)

| Method | Path | Current shape | New shape | Note |
|---|---|---|---|---|
| POST | `/` | success `{ user }`; 404 `{ message }` | `{ success, status, message, data: { user } }` / error envelope | |

## 15. Meeting rooms — `mobile/rooms` (`MobileRoomController`)

| Method | Path | Current shape | New shape | Note |
|---|---|---|---|---|
| GET | `/` | **flat array** (rooms); `?grouped=true` → **flat array** of `{ date, rooms }`; `?date=` → **flat array** | `{ success, status, message, data: [...] }` | **Flat array → wrapped**, all three variants. |
| GET | `/bookings` | **flat array** | `{ success, status, message, data: [...] }` | **Flat array → wrapped.** |
| GET | `/users` | `{ users, pagination }` | `{ success, status, message, data: { users, pagination } }` | |
| POST | `/book` | **flat slot object** (201); errors `{ error }` (400/404) | `{ success, status, message, data: { ...slot } }` / error envelope | **Flat → wrapped.** `error` string → `message`. |
| DELETE | `/bookings/{slotId}` | `{ message }`; errors `{ error }` (400/403/404) | `{ success, status, message, data: null }` / error envelope | |
| PATCH | `/bookings/{slotId}` | `{ message, slot }`; errors `{ error }` (400/403/404) | `{ success, status, message, data: { slot } }` / error envelope | `slot` under `data`. |

## 16. Notifications — `mobile/notifications` (`MobileNotificationController`)

| Method | Path | Current shape | New shape | Note |
|---|---|---|---|---|
| GET | `/` | `{ notifications, totalNotifications, totalPages, currentPage }` | `{ success, status, message, data: { notifications, totalNotifications, totalPages, currentPage } }` | |
| GET | `/mark-read` | **plain string** `"OK"` | `{ success, status, message, data: "OK" }` | **Scalar → wrapped.** Flutter's `response.data.toString()` will break — must read `data`. |
| GET | `/unread-count` | **plain integer** | `{ success, status, message, data: <int> }` | **Scalar → wrapped.** Flutter's `response.data as int` will break — must read `data`. |
| GET | `/clear` | **plain string** `"OK"` | `{ success, status, message, data: "OK" }` | **Scalar → wrapped.** |

## 17. Chat — `mobile/chat` (`MobileChatController`)

**Already partially enveloped** (`{ success, data: {...} }`). Only additive `status` + `message` are needed — **non-breaking** if the app already reads `data`.

| Method | Path | Current shape | New shape | Note |
|---|---|---|---|---|
| GET | `/rooms` | `{ success, data: { rooms, pagination } }` | `{ success, status, message, data: { rooms, pagination } }` | **Additive only** — `data` unchanged. |
| GET | `/rooms/{roomId}/messages` | `{ success, data: { messages, pagination } }`; 404 `{ success:false, message }` | `{ success, status, message, data: { messages, pagination } }` | **Additive only.** |
| POST | `/messages` | `{ success, data: { roomId, message } }` (200/201); errors `{ success:false, message }` (404/422) | `{ success, status, message, data: { roomId, message } }` | **Additive only.** |
| GET | `/unread-count` | `{ success, data: { unreadCount } }` | `{ success, status, message, data: { unreadCount } }` | **Additive only.** |

## 18. App config — `/app-config`, `/app-config/version` (`AppConfigController`)

Public, unauthenticated, polled by Flutter. **These are configuration documents, not resource responses.**

| Method | Path | Current shape | Recommendation |
|---|---|---|---|
| GET | `/app-config` | **flat config document** (`{ version, theme, conference, content, features, … }`) | **Leave as-is (do NOT wrap).** It is a document the app deserializes wholesale; wrapping under `data` adds churn with no unification value. Confirm with mobile. |
| GET | `/app-config/version` | `{ version }` | **Leave as-is.** Trivial poll payload. |

> Decision flagged for the mobile team: §18 is the one place where wrapping is *not* recommended. If uniformity is preferred over pragmatism, both can be wrapped — but that is a deliberate choice, not the default.

---

## 19. Already-shipped mobile contract change (context, not part of this delta)

- Guest **`avatar`** is now a signed, 24h-expiring URL. Same field/type, different lifetime. See
  [`MOBILE_NOTICE_PRIVATE_AVATAR_SIGNED_URL.md`](MOBILE_NOTICE_PRIVATE_AVATAR_SIGNED_URL.md) (ledger D14).
- Agenda dates are wall-clock. See [`MOBILE_NOTICE_AGENDA_DATE_WALL_CLOCK.md`](MOBILE_NOTICE_AGENDA_DATE_WALL_CLOCK.md).

## 20. Highest-impact rows (read these first)

The transforms most likely to hard-break the Flutter client (flat/scalar → wrapped; the app reads the root today):

- **Flat objects → wrapped:** `sessions/{id}`, `workshops/{id}`, `rooms/book`.
- **Flat arrays → wrapped:** `sessions/favorite`, `workshops/registered`, `publications`, `rooms`, `rooms/bookings`.
- **Scalars → wrapped:** `notifications/mark-read` & `notifications/clear` (`"OK"`), `notifications/unread-count` (int).

Everything else already has an object wrapper, so the app "only" needs to reach one level deeper (into `data`).

## 21. Migration bookkeeping

- **Done on backend `dev`:** all rows above are implemented. Controllers migrated: `MobileAuthController`,
  `MobileEventDayController`, `MobileSpeakerController`, `MobileSponsorController`, `MobileAttendeeController`,
  `MobileSessionController`, `MobileSessionFeedbackController`, `MobileWorkshopController`,
  `MobileWorkshopFeedbackController`, `MobilePublicationController`, `MobileMediaCenterController`,
  `MobileQrController`, `MobileRoomController`, `MobileNotificationController`, `MobileChatController`.
  `AppConfigController` intentionally left unwrapped (§18).
- Backend feature tests (`MobileAuthTest`, `SessionsTest`, `NotificationTest`, `RoomBookingTest`,
  `ChatTest`, `SpeakersTest`, `AttendeeTest`, `ConferenceTest`, `PublicationsTest`, `QrScannerTest`,
  `MediaCenterTest`, `SessionFeedbackTest`, `WorkshopFeedbackTest`, etc.) were updated in lockstep.
- `routes/api.php` did not change (`git diff` empty) — body refactor only.
- **Remaining:** mobile-team acknowledgment of these deltas, then backend `dev` → `main`. When the mobile
  repo is brought into the parent project folder, the Flutter client is updated directly against this doc.
