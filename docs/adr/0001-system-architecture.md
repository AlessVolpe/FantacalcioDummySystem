# ADR 0001: Application and native engine boundaries

**Status:** Accepted direction; backend choices resolved by
[ADR 0006](0006-backend-stack.md), [ADR 0007](0007-identity-and-authentication.md)
and [ADR 0008](0008-rest-api.md).

## Context

FDS replaces the Java prototype with an application supporting competition
management and reproducible counterfactual experiments. CRD already owns the
mathematical and native execution contracts.

## Decision

Keep FDS and CRD independently versioned. Use one modular application codebase
with separate web and worker processes. The planned stack is Python 3.13,
Django, React with TypeScript, Celery and Docker Compose on a Linux VPS. Confirm
framework versions, API conventions and deployment details before implementation.
The deprecated repository is a behavioral reference only.

## Consequences

Avoid duplicating the C algorithms or building a separate native HTTP service.
Application code owns identity, persistence, orchestration and presentation;
CRD remains stateless and unaware of users and the database. Independent
releases require a deliberate compatibility and artifact-selection policy.
A modular monolith reduces deployment complexity but still requires explicit
module and process boundaries.
