# REST API foundations

**Status:** implementation in PR 5 of milestone 0.2.0. The application package
remains at version 0.1.1. API version `v1` is independent of application and native
wire versions. See [ADR 0008](../adr/0008-rest-api.md) and the [authentication
contract](authentication.md).

## Resource conventions

All application API paths start with `/api/v1/`, use trailing slashes and are
same-origin in production. Unknown paths (including missing trailing slashes)
return a JSON 404 instead of redirecting unsafe requests. New resources use
DRF serializers and views with JSON-only parsing and rendering, Django session
authentication and authenticated-by-default permissions. Public endpoints
require an explicit permission exception. For new anonymous unsafe views,
explicitly enforce Django CSRF protection; DRF SessionAuthentication alone does
not protect anonymous requests. Preserve the existing Django auth views and
CSRF middleware rather than convert the account lifecycle to DRF.

The strict DRF JSON parser accepts UTF-8, rejects duplicate object members and
nonstandard JSON constants, and bounds input at 16 KiB. Future large import
endpoints must choose a separate documented bounded parser. Django's legacy
authentication parser retains its established 400 response for invalid bodies,
including unsupported content types. DRF distinguishes 400 (invalid JSON or
fields), 413 (oversized JSON) and 415 (unsupported media type). DRF resources
return 406 when the requested representation is unavailable. Accept
`application/json` (or `*/*`) for normal resource responses; errors use
`application/problem+json`. No browsable API, CORS or bearer credentials are
introduced.

## Problem Details (RFC 9457)

Error responses contain the standard RFC 9457 members and a stable FDS `code`
extension. For example, an unauthenticated identity request returns HTTP 403:

```json
{
  "type": "about:blank",
  "title": "Forbidden",
  "status": 403,
  "detail": "Authentication is required.",
  "code": "authentication_required"
}
```

The media type is `application/problem+json`. `about:blank` uses the HTTP status
phrase as the title; clients should use the HTTP status and stable FDS `code`
for program logic, not the human-readable detail. The nested PR 4 envelope is
replaced intentionally before the first public application release. Existing
authentication identifiers and status codes are preserved. Raw exception
messages, validation values, arbitrary unknown field names, SQL, tokens and
internal addresses are never returned. Validation uses a generic `validation_error`
code for DRF; field-level problem extensions can be added compatibly later using
explicitly safe names and messages. There is no instance URI containing request
data. Error responses retain `Allow`, `Retry-After` or authentication challenges
when applicable; unexpected exceptions still use Django's logging and rollback.

| HTTP status | Representative codes |
| --- | --- |
| 400 | `invalid_input`, `validation_error`, `invalid_token` |
| 403 | `authentication_required`, `invalid_credentials`, `csrf_failed`, `permission_denied` |
| 404 | `not_found` |
| 405 | `method_not_allowed` |
| 406 | `not_acceptable` |
| 409 | `conflict` |
| 413 | `payload_too_large` |
| 415 | `unsupported_media_type` |
| 429 | `rate_limited` |
| 500 | `internal_error` |
| 503 | `service_unavailable`, `email_flow_unavailable` |

Session-based authentication returns 403 for anonymous protected requests.
Future private objects must be looked up through authorized querysets and
normally return 404 if inaccessible. `Cache-Control: no-store` applies to all
initial API responses. Do not log request bodies or sensitive exception data.

## Own identity

`GET /api/v1/auth/me/` preserves the existing Django view. `PATCH` at the same
route dispatches to a DRF view with session authentication and CSRF protection
at both the Django and DRF boundaries. Fetch `GET /api/v1/auth/csrf/` first,
keep cookies and pass the returned `csrfToken` as `X-CSRFToken`. The request must
be exactly one JSON object with a `display_name` string (1–150 characters after
trimming). Blank names, unknown fields, non-string values and invalid Unicode
are rejected. Only the authenticated user's display name is updated, not
email, password, verification, UUID, privileges or another user's account.

```json
{"display_name": "New display name"}
```

Success: 200 with the existing own-identity fields `id`, `email`, `display_name`.
There is no user listing or public account lookup endpoint.

## Pagination

All future collection views must use the bounded page-number paginator and
explicitly order their authorized querysets, using a unique tiebreaker where
needed. Default `page=1`, `page_size=25`; permitted sizes are 1–100. Invalid,
repeated or oversized parameters return 400; a nonexistent page returns 404.
`last` and unlimited results are not supported. Responses have `count`, `next`,
`previous` and `results`. Count and offset pagination are not a snapshot
consistency guarantee under concurrent writes. Cursor pagination can be
introduced for large experiment collections later. No competition collection
is implemented in this milestone.

## Health

| Method | Route | Meaning |
| --- | --- | --- |
| GET | `/api/v1/health/live/` | Process responds; no database operation |
| GET | `/api/v1/health/ready/` | Read-only PostgreSQL `SELECT 1` succeeds |

Both are deliberately anonymous; probes should send no cookies or credentials.
Success is 200 with `{"status":"ok"}`. Readiness returns generic 503 Problem
Details on database errors without exposing diagnostic data. It does not
migrate, write, or claim to verify full schema integrity. Use a bounded external
probe timeout; the connection profile already sets a five-second connect
timeout, but that does not bound all network or SQL waits. Database readiness
does not imply SMTP or future background workers are ready.

## OpenAPI 3.1

The schema is generated by drf-spectacular. A postprocessing hook provides the
explicit initial Django authentication/DRF health contract while preserving
normal auto-generated future DRF operations. Schema security requirements
include session cookies for protected operations and a CSRF request header for
unsafe operations. No secret or generated token appears in examples. The schema
and documentation routes themselves are developer tooling, not domain resources.

Development exposes:

- `/api/v1/schema/` — OpenAPI document.
- `/api/v1/docs/` — Swagger UI.
- `/api/v1/redoc/` — ReDoc.

Swagger UI and ReDoc assets are served through the installed sidecar package,
not a third-party CDN. Production and other non-development profiles disable
these routes by default. Swagger UI fetches a fresh CSRF token immediately
before every unsafe same-origin v1 API request and supplies `X-CSRFToken`
with browser cookies. No token needs to be entered in the Authorize dialog.
The OpenAPI header security scheme `csrfToken` describes CSRF protection, not
an alternative authentication mechanism. Protected unsafe operations require
both `cookieAuth` and `csrfToken`; login and registration require CSRF only.
Other clients must acquire and submit the token themselves. Swagger disables
persistent authorization and the external schema validator. Cross-origin requests
are rejected by the interceptor; server-side CSRF and permission checks are
unchanged. Use development test credentials only: Swagger displays request
bodies and does not act as a password manager.

Generate and commit the canonical schema after resolving dependencies:

```sh
uv run --locked python manage.py spectacular --settings=fantacalciodummysystem.config.settings.static --validate --fail-on-warn --file docs/openapi-v1.yaml
uv run --locked python -m scripts.check_openapi
```

The schema check runs the same generator with the static profile and compares
normalized file contents. A missing or stale schema fails CI on both platforms
and in the reusable release quality workflow. Changes to published operations
must update the schema in the same PR. The initial schema is generated locally
against the resolved lockfile, rather than hand-authoring generator output.

## Scope and verification

No new database models or migrations are introduced. Authentication lifecycle
regression tests must continue passing. Run database-free tests for parser,
serializer, permissions, error responses, pagination and schema contracts;
run the guarded PostgreSQL suite for authenticated profile updates and readiness.
Run Ruff, strict mypy, Django checks, schema validation/drift and dependency
security checks before merging. Competition permissions and collections, native
integration, React, background processing and operational readiness beyond
PostgreSQL remain future milestones. Production email flow activation and
operational security remain deferred.
