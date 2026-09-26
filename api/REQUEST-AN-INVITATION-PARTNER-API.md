# TOURISE 2027 — partner API

Two endpoints, one key: file an invitation request, and subscribe someone to
the newsletter.

For a website that is not ours. They build the form; we take the request.

A request filed this way lands in the same admin review queue as one filed on
our own form, under the category named in the URL.

> The partner-facing version of this file is
> [`TOURISE-2027-Request-an-Invitation-API.pdf`](TOURISE-2027-Request-an-Invitation-API.pdf),
> whose source is [`TOURISE-2027-Request-an-Invitation-API.html`](TOURISE-2027-Request-an-Invitation-API.html)
> (printed to PDF through headless Chrome). Keep the two in step.

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

## No backend of your own

Four ways in, from no code at all to a key in the browser.

| | How | Key | CORS |
|---|---|---|---|
| **A** | **Link to our form** at `https://register.tourise.com/{lang}/request-an-invitation/{slug}` — we handle required fields, the email code, reCAPTCHA and the reply | none | none |
| **B** | Their **server-side function** adds the key and forwards (recommended for their own form) | server-side | none |
| **C** | **Key in browser JavaScript** — public, and understood as such | exposed | their origin must be allow-listed |
| **D** | **Newsletter only**: `POST /api/newsletter/subscribe` takes a reCAPTCHA token instead of a key | none | their origin |

Two things worth saying out loud when a partner asks:

- **Option A cannot be an iframe.** The public site sends
  `frame-ancestors 'none'` and `X-Frame-Options`, so an embedded window stays
  blank. Link or redirect.
- **There is no keyless route for invitation requests.** `POST
  /api/request-an-invitation/{slug}` sits behind `request-api-key`; only the
  newsletter endpoint resolves either credential (`NewsletterController@subscribe`).

What a leaked browser key can do: file a pending request, 60/min, nothing else.
It cannot read, list, edit, accept or reject anything.

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
    "with_email_otp": true,
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

## 3. Email OTP

A request category can ask the applicant to type back a code emailed to the
address they entered (`with_email_otp`, set per category in the admin and
reported by the field list).

**It applies to our own form only.** `InvitationRequestsController@createRequest`
checks the code when `with_email_otp && ! $fromPartner` — a request carrying a
key skips it, whatever the category says, and an `otp_token` sent with a key is
ignored. The key is the trust; a partner's server has no inbox of the
applicant's to read.

On our form:

1. `POST /api/guests/email-verification` — `{email, recaptcha}` emails an
   8-character code and replaces any live code for that address.
2. `POST /api/guests/email-confirmation` — `{token, recaptcha}` answers
   `200 {status: success, token}` or `404 {error: "wrong token"}`.
3. The request is posted with `otp_token`, checked against **the address it was
   sent to**, so a code obtained for one address cannot file under another.
4. Filing spends every code for that address (`email_verifications` row
   deleted). A second request needs a fresh code.

Both OTP calls require reCAPTCHA and share the site-wide `sensitive-api`
ceiling of 300/min. A partner who wants the same proof on their own form needs
a reCAPTCHA site key registered for their domain — ours is not.

## 4. After the request is filed

Who talks to the applicant, and what each side keeps — the question every
partner asks second.

| Moment | What we send | When nothing goes out |
|---|---|---|
| Filed (`201`) | The holding email — it arrived, a decision is coming | Only if the request category names `submitted_email_template_id`. Otherwise silence. |
| Duplicate (`200`) | Nothing; the earlier request stands | Always — a second submit sends no second email |
| Accepted | The invitation itself, with the registration link, on that collection's channel (`SendInvitationEvent` / SMS / WhatsApp) | — |
| Rejected | A rejection email | Only if the category names `rejection_email_template_id`. Rejecting used to be silent; it still is without one. |

So the honest answer to "will my applicant hear from you?" is **it depends on
the category's templates** — check which are set before a partner words their
thank-you page.

What we keep: the request row (the fields sent, language, the partner site it
came from, status, handled_by / handled_at, note). A newsletter opt-in is a
separate subscriber row, attributed the same way. Nothing else about their
visitor reaches us.

What they keep: their business. The queue is our record; they cannot delete
through this API, so a removal request comes to us.

## Notes

- **No reCAPTCHA on the partner route.** The key is the credential; a server has
  no browser to run a challenge in. Our own form still uses reCAPTCHA.
- **`source` is set by us, not by the caller.** Anything filed with a key is
  recorded as coming from that site, and admin can see which.
- **CORS**: if the form posts from the browser, the partner's origin must be in
  `CORS_ALLOWED_ORIGINS` on the API. Posting from their server needs nothing.
- Rate limit is per key, so one partner cannot exhaust another's budget.


---

# Newsletter signup

The same key, for a signup box on a partner site.

```http
POST /api/newsletter/subscribe
X-Api-Key: tri_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Content-Type: application/json
```

```json
{
  "email": "sara@example.com",
  "first_name": "Sara",
  "last_name": "Idris",
  "company": "Partner Co",
  "lang": "en"
}
```

Only `email` is required. New subscribers join the default list.

A page that can hold no secret may send `recaptcha` instead of the key. A
**wrong** key is still refused — there is no order in which a bad key falls
through to the softer check.

### Responses

Always `201` on success. Read `state` to say the right thing:

| `state` | Meaning | Say |
|---|---|---|
| `subscribed` | New — they are now on the list | "Thanks for subscribing" |
| `already_subscribed` | Was already on the list | "You are already subscribed" |
| `resubscribed` | Had unsubscribed, now back | "Welcome back" |

`401` for a missing, unknown or revoked key. `422` if the address is not valid.

### About `token`

`token` is returned **only** when `state` is `subscribed` — a genuinely new
address. It is a bearer credential: whoever holds it can read that subscriber
and unsubscribe them, so it is never returned for an address that already
existed, where the caller may know the address without owning it.

Do not build a flow that depends on getting it back for an existing subscriber.

### Attribution

TOURISE records which partner site each subscriber came from, taken from the
key rather than anything you send. The first site to subscribe an address keeps
the attribution — a later signup elsewhere does not rewrite where they
originally came from.
