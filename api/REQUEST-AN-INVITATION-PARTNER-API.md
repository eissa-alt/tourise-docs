# Request an Invitation — partner API

For a website that is not ours. They build the form; we take the request.

A request filed this way lands in the same admin review queue as one filed on
our own form, under the category named in the URL.

## Getting a key

Admin → **Invitations → API keys** → *Issue a key*, named for the site it is
for. The token is shown **once**, on that screen. It is stored hashed, so it
cannot be shown again — a lost key is replaced by issuing a new one, which is
also how one is rotated.

One key per site. Revoking a key stops that site and no other.

## The category

The address is the category's slug, the same one in its public form URL:

```
https://register.tourise.com/en/request-an-invitation/press
                                                      ^^^^^ slug
```

Categories are created in Admin → Invitations → Invitation requests →
Categories. A category that is switched off stops accepting posts.

## 1. Read the field list

```http
GET /api/request-an-invitation/{slug}
```

Public, no key needed. Tells the partner what to render and what to require.

```json
{
  "status": "success",
  "data": {
    "slug": "press",
    "name_en": "Press",
    "mandatory_fields": ["first_name", "company"],
    "optional_fields": ["phone"]
  }
}
```

`mandatory_fields` / `optional_fields` are `null` when the category has not been
configured — meaning nothing extra is required beyond `email`.

## 2. File a request

```http
POST /api/request-an-invitation/{slug}
X-Api-Key: tri_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Content-Type: application/json
```

`Authorization: Bearer <key>` is accepted as the same credential, for clients
where that header is easier.

```json
{
  "email": "sara@example.com",
  "first_name": "Sara",
  "last_name": "Idris",
  "company": "Partner Co",
  "job_title": "Editor",
  "phone": "+966500000000",
  "industry": "Media & Content Creators",
  "country_of_residence": "<country uuid>",
  "nationality": "<country uuid>",
  "social_media_channel_1": "https://...",
  "social_media_channel_2": "https://...",
  "lang": "en",
  "subscribe_newsletter": true
}
```

`email` is always required. Everything else is required only if the category
says so. No other fields are accepted — anything not on this list is ignored.

`country_of_residence` and `nationality` are country UUIDs from
`GET /api/countries`, not names.

### Responses

| Code | Meaning |
|---|---|
| `201` | Filed. `{"data": {"id": "...", "duplicate": false}}` |
| `200` | That address already has a request pending. `duplicate: true`, nothing new created. |
| `401` | Key missing, unknown, or revoked. |
| `404` | No category at that slug. |
| `410` | The category exists but is closed. |
| `422` | Validation failed — `errors` names the fields. |
| `429` | Rate limited (60/min per key). |

`duplicate: true` is a success, not an error — show the same thank-you. It
exists so a double submit does not put the same person in the queue twice.

## Notes

- **No reCAPTCHA on this route.** The key is the credential; a server has no
  browser to run a challenge in. Our own form still uses reCAPTCHA.
- **`source` is set by us, not by the caller.** Anything filed with a key is
  recorded as coming from that site, and admin can see which.
- **CORS**: if the form posts from the browser, the partner's origin must be in
  `CORS_ALLOWED_ORIGINS` on the API. Posting from their server needs nothing.
- Rate limit is per key, so one partner cannot exhaust another's budget.
