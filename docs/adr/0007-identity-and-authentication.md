# ADR 0007: Identity and browser authentication

**Status:** Accepted 2026-11-24; authentication in implementation (PR 4).
See the [authentication reference](../architecture/authentication.md) for the
selected email-first flow, token, session, password and throttle contracts.

## Context

The eventual public application must authenticate users, protect private
competition data and support explicit publication. Replacing Django's default
user model after initial migrations is expensive and risky.

## Decision

Use a custom `accounts.User` model from the first migration, configured as
`AUTH_USER_MODEL` before any database initialization. Its primary key is a UUID
(generated server-side); email is the login identifier, with a separate,
non-unique display name. Do not require a username. References to users must
use the configured user model rather than Django's default concrete class.

The public account lifecycle includes registration, email verification,
login, logout and password recovery. Unverified accounts must not receive an
authenticated application session. Treat verification and administrative
disablement as distinct concepts. Keep email private unless an explicitly
authorized account-management operation requires it.

Use Django password hashing, validators and session authentication, not custom
password storage, JWTs or external identity providers in 0.2.0. The frontend
and API share one HTTPS origin in production. Use Django CSRF protection for
unsafe browser requests, including login and other anonymous state-changing
account operations. DRF SessionAuthentication alone is insufficient for
anonymous login CSRF protection. Rotate sessions on login, invalidate them on
logout, use secure HttpOnly session cookies in production, and keep CORS
closed by default. Protect state-changing operations from cross-site requests.

## Implementation requirements

- Adopt a consistent case-insensitive email identity policy: normalize before
  lookup and enforce uniqueness at the database boundary, including concurrent
  registration. Do not apply provider-specific alias rewriting. The
  initialization PR selects ASCII canonical email storage and PostgreSQL
  constraints; see the [backend reference](../architecture/backend.md#django-initialization).
  Internationalized email support remains subject to review before registration.
- Use expiring, purpose-bound, single-use verification and reset tokens;
  do not log or expose tokens in public API responses. Provide a safe resend
  path, and invalidate old tokens when appropriate.
- Avoid account enumeration through registration, verification resend and
  password recovery responses. Apply rate limits before public availability.
- Test session rotation, CSRF rejection (including login), verification,
  duplicate email handling, disabled users, and object-level authorization.
- Keep the user model focused on identity; competition roles and membership
  belong to the competition domain. A UUID is an identifier, not authorization.

Exact model fields, token storage, expiration durations, mail provider,
rate-limit configuration and account deletion/retention policy are implementation
choices to document before the relevant feature is exposed. Do not enable public
registration in production until verification and abuse controls are operational.

## Consequences

The custom identity model must precede all migrations. Same-origin sessions
simplify browser credential management but require explicit CSRF protection.
Public registration requires reliable email delivery and abuse controls.
Use Django's [custom user model guidance](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/)
and DRF's [authentication guidance](https://www.django-rest-framework.org/api-guide/authentication/).
