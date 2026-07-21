# Mobile notice — category `with_otp` renamed to `with_email_otp`

**Date:** 2026-07-21
**Severity:** Breaking field rename on category payloads (plus two additive fields)
**Affects:** Any Flutter screen that reads the category OTP flag from an **invitation** payload.

## What changed

The category boolean previously exposed as **`with_otp`** is renamed to **`with_email_otp`** — for
symmetry with the already-existing `with_sms_otp`. The value/meaning is unchanged: *this category
requires an email OTP step during registration.*

Two additive per-category flags were also introduced:

| Field | Type | Meaning |
|---|---|---|
| `with_email` | bool | Master switch: the category may send **email** at all (notifications + email OTP). |
| `with_sms` | bool | Master switch: the category may send **SMS** at all (notifications + phone OTP). |

Server-side, when a master flag is `false` the backend will **not** send on that channel regardless of
per-event settings (enforced centrally in `Category::getNotificationTemplate`). Existing categories were
backfilled so already-configured data keeps working.

## Endpoints that carry the renamed field

Both invitation-verification responses in `InvitationsController` now return `with_email_otp`
(previously `with_otp`):

- `GET` invitation verify by token — the `{ "status": "valid", …, "with_email_otp": bool, "with_sms_otp": bool, … }` body.
- `GET` invitation category info — the `{ "status": "valid", "category": …, "with_email_otp": bool, "with_sms_otp": bool, … }` body.

The admin `CategoriesResources` (admin CMS, not the mobile app) also renamed the key and added
`with_email` / `with_sms`.

## Mobile action required

- Read **`with_email_otp`** instead of `with_otp` from the invitation payloads above.
- No action needed for `with_email` / `with_sms` unless you want to reflect channel availability; they are
  additive and default to the backfilled value.

**Routes are unchanged** — this is a payload field rename only (`git diff routes/api.php` stays empty).
