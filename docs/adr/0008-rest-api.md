# ADR 0008: RESTful API and HTTP conventions

**Status:** Accepted 2026-11-24; API foundations in implementation (PR 5).
See the [REST API reference](../architecture/rest-api.md) for RFC 9457 Problem
Details, OpenAPI 3.1, bounded page-number pagination and the health contract.

## Context

React will consume the backend in a later milestone. Resource contracts must
remain independent of the native JSON CLI and the ORM's internal structure.

## Decision

Use Django REST Framework with a JSON, resource-oriented HTTP API rooted at
`/api/v1/` and a versioned OpenAPI description. The browser and API share the
same production origin; a reverse proxy routes API requests to Django and
serves the frontend. Preserve standard HTTP semantics rather than implementing
RPC endpoints for ordinary CRUD operations.

- Use plural resource nouns, stable UUID identifiers where applicable, and a
  consistent trailing slash convention. Use GET for safe reads, POST for
  creation, PATCH for partial updates, PUT for complete replacement where
  supported, and DELETE where domain policy permits. GET must not mutate state.
- Use 201 with Location for created resources, 202 for accepted asynchronous
  work not yet completed, 204 for successful empty responses, and appropriate
  4xx/5xx status codes for errors. Do not wrap failures in HTTP 200 responses.
- Represent asynchronous experiments as resources with readable status and
  results. Model cancellation and other non-CRUD transitions explicitly when
  needed; define their semantics in the experiment milestone.
- Default to authenticated and authorized access; allow anonymous access only
  for deliberately public resources or account bootstrap endpoints. Enforce
  permissions on object lookup and collection querysets, not just views.
- Document request/response shapes, validation, authentication, pagination,
  ordering and filtering in OpenAPI. Use bounded pagination for lists and
  deterministic ordering. Do not serialize raw model fields implicitly.
- Use a consistent machine-readable error format with stable codes and field
  details where appropriate; the exact schema and pagination contract are
  defined and tested during API foundations. Honor DRF session authentication's
  actual unauthenticated/forbidden behavior and document it rather than
  promising a 401 without an applicable authentication challenge.
- Use additive compatible changes within v1; introduce a separately documented
  version for breaking public contracts. Never expose native pointers, raw
  subprocess diagnostics, secrets or private competition snapshots as errors.

Browser session authentication is specified in [ADR 0007](0007-identity-and-authentication.md).
REST interface statelessness is not claimed: the selected browser authentication
uses server-side sessions. Resource-oriented HTTP semantics remain the design goal.
The native wire schema `1.0` and public HTTP API `v1` are independent versions.

## Consequences

A stable resource interface permits independent frontend development without
coupling clients to database models or native serialization. Same-origin
routing reduces CORS complexity. OpenAPI and contract tests must evolve with
implementation; this record is not a published endpoint specification.
