# Authentication and account lifecycle

**Status:** implementation in the fourth PR of 0.2.0; acceptance requires
local verification and both PostgreSQL CI jobs. See [ADR 0007](../adr/0007-identity-and-authentication.md).

## Identity and registration

Email-first registration accepts a canonical ASCII email address, then sends an
expiring registration link. No user, password or display name is created until
its bearer token is submitted with a password and display name. A successful
completion creates an active, verified, non-staff user. Existing accounts are
never overwritten by registration. Pre-existing unverified accounts created by
trusted internal code require administrator intervention; they are not part of
the public email-first flow. Login is explicit after registration and recovery.

Passwords must be 12–128 Unicode characters (no stripping or silent truncation).
Django's common-password, entirely numeric and user-attribute similarity
validators remain enabled. There are no mixed-case, symbol or digit quotas.
The default Django PBKDF2 hasher remains in use. Browser forms permit paste and
use `autocomplete="new-password"`; password managers and unique generated
passwords are encouraged. The eventual login form should use
`autocomplete="username"` and `autocomplete="current-password"`.

## HTTP contract

All routes below use `/api/v1/auth/` and require a trailing slash. Unsafe
requests require Django CSRF protection even when anonymous. Fetch `csrf/`
first, keep the session and CSRF cookies, and send `X-CSRFToken` with the returned
`csrfToken` on subsequent POST requests. Login rotates both session and CSRF
state; fetch a new token after login. POST bodies with fields are UTF-8 JSON
objects with exactly the listed string fields; bodies are bounded at 16 KiB.
No CORS exception or bearer authentication is introduced. Responses use
`Cache-Control: no-store`; the general API error contract is deferred to PR 5.

| Method | Route | JSON fields | Success |
| --- | --- | --- | --- |
| GET | `csrf/` | — | 200, `csrfToken` |
| POST | `register/` | `email` | 202, generic acceptance |
| POST | `resend/` | `email` | 202, generic acceptance |
| POST | `verify/` | `token`, `display_name`, `password` | 201, empty |
| POST | `login/` | `email`, `password` | 204 |
| POST | `logout/` | — | 204 (also anonymous) |
| POST | `password/reset/` | `email` | 202, generic acceptance |
| POST | `password/confirm/` | `token`, `password` | 204 |
| POST | `password/change/` | `current_password`, `password` | 204 |
| GET | `me/` | — | 200, own `id`, `email`, `display_name` |

Registration completion deliberately does not return the user UUID or a
Location until the client authenticates. The identity resource is private.
Errors have the form `{"error":{"code":"invalid_input"}}`. Invalid input or
invalid/expired tokens return 400, invalid credentials or missing authorization
and CSRF failures return 403, disallowed methods return 405, throttled requests
return 429, and disabled email flows return 503. Registration/resend/recovery
return the same 202 body for eligible, ineligible, email-throttled or failed
mail delivery cases. No account existence or raw token is returned. The IP
limit is independent of account existence. Synchronous SMTP can still create
observable timing differences; this is not a claim of timing indistinguishability.
Review timing leakage and delivery availability before public activation.

Email links use a configured origin and a URL fragment, not a query parameter.
The small Django link-completion pages at `/auth/register/` and
`/auth/reset-password/` read the fragment in memory, remove it from browser
history and POST JSON using CSRF protection. Their restrictive CSP prevents
third-party resources. Opening a link alone never consumes the token. The
pages are temporary, not the React frontend; login and account management are
available via the API and Django admin. Future frontend replacements must
preserve the fragment, no-referrer and CSRF guarantees.

## Token and session storage

`AccountToken` holds SHA-256 digests of random 256-bit tokens, canonical email,
purpose, expiry and (for recovery) a fingerprint of the password hash and
session generation. Registration links expire after 24 hours; recovery links
after 30 minutes. Each email/purpose has at most one outstanding token. Resends
replace it. An email-scoped PostgreSQL transaction advisory lock serializes
issuance and consumption, followed by a row lock and expiry check. A successful
consumption deletes the token in the same transaction as the account change.
Invalid attempts do not consume a valid token; purpose substitution fails.
Recovery is available only to active verified accounts. Password changes and
administrative generation changes invalidate old reset tokens.

Sessions use Django's database backend. Absolute lifetime is seven days and
inactivity lifetime is 24 hours, independently enforced by middleware on each
authenticated request. Login rotates session identity; logout flushes the
current session. Django's password-derived session authentication hash rejects
previous sessions on their next request after recovery or password change;
password change preserves the current session with a rotated session key.
Concurrent sessions are allowed. No remember-me or automatic login is provided.
A session generation UUID invalidates old sessions even if an administrator
subsequently re-enables an account. Direct internal updates of activation must
also rotate the generation when changing status; the admin path does so.

## Abuse protection

Fixed-duration PostgreSQL counters are keyed by a SHA-256 HMAC of scope and
identity, rather than raw email or IP. Row locking enforces the budget across
workers. Limits are configurable through `FDS_AUTH_LIMITS` in server settings.

| Operation | Per email | Per IP |
| --- | --- | --- |
| Registration and resend (shared) | 3/hour | 10/hour |
| Recovery request | 3/hour | 10/hour |
| Failed login/current-password checks | 5/15 min | 30/15 min |
| Token consumption | — | 30/15 min |

The admin login shares the login budget. Admin password-change form errors are
counted conservatively. Fixed windows can permit bursts at boundaries and
per-email limits can temporarily block legitimate login attempts. The direct
peer address is used; forwarded headers are not trusted. Production proxy
configuration, network-level limits, distributed abuse and reliable email
provider handling remain deployment acceptance tasks. Expired rows no longer
count against limits. Schedule periodic `manage.py cleanup_auth` to remove
expired tokens, counters and sessions before enabling public traffic. Do not
log raw tokens, request bodies, SMTP credentials or email content. Console mail
is intentionally visible to the local developer only.

## Administration and email configuration

The restricted Django admin is at `/admin/`. Create a verified superuser with
Django's existing `createsuperuser` command. Superusers can inspect accounts and
activate/disable other accounts, but cannot create, delete or edit identity,
password or permissions from the account admin. The superuser's own password
can be changed using Django admin's authenticated password-change form. There
are no public user listings or user-object lookup endpoints.

Development uses console mail and the origin `http://localhost:8000`; testing
uses in-memory mail and `http://testserver`. Static settings do not deliver mail.
Production email flows are disabled by default. After operational acceptance,
set `FDS_AUTH_EMAIL_ENABLED=1` and supply private environment variables:

- `FDS_AUTH_ORIGIN`: explicit HTTPS origin with no path, query or fragment, whose
  host is in `FDS_ALLOWED_HOSTS`.
- `FDS_EMAIL_HOST`, `FDS_EMAIL_HOST_USER`, `FDS_EMAIL_HOST_PASSWORD`,
  `FDS_EMAIL_FROM`: authenticated SMTP submission configuration (port 587,
  STARTTLS, 10-second socket timeout).

No actual provider is selected or tested here. TLS proxy handling, sender
verification, email deliverability, retention and delivery/timing defenses need
operational review. Account deletion, email changes, MFA and competition-level
permissions remain out of scope. Display-name editing is planned for PR 5.

## Verification

Use the [existing dedicated PostgreSQL testing profile](../local-postgresql.md).
The migration adds the token/counter tables, a user session generation and the
standard Django admin log table. The integration guard recognizes only these
additional tables and still refuses existing user/session/token/counter/admin
log data. No new database credentials or reprovisioning are required.

```sh
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked mypy
uv run --locked pytest --cov --cov-report=term-missing
uv run --locked --env-file .env.testing pytest -m integration --ds=fantacalciodummysystem.config.settings.testing
```

The dedicated integration fixture checks migration drift before migrating.
Exercise registration, replay, expiration, session rotation/expiration,
recovery and password changes, CSRF, throttles and concurrent token consumption.
Verify both Linux and Windows CI before merging. The application version
remains 0.1.1 until milestone closure.
