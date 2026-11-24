# ADR 0004: Background experiment execution

**Status:** Accepted direction; broker and recovery design proposed.

## Context

Simulation durations and resource consumption vary. Native execution must not
block an HTTP request or depend on the browser staying connected.

## Decision

Use Celery workers to execute persistent experiment jobs asynchronously. The
relational database is authoritative for application-visible lifecycle state;
a broker transports job references. Redis is a proposed initial broker, not a
final dependency selection. Dispatch only after the database transaction commits;
provide a recovery path for persisted jobs that were not successfully dispatched.
Use explicit attempt identities, atomic claiming/finalization and idempotent job
handling to tolerate duplicate delivery. Bound runtime, memory and concurrency;
apply cooperative cancellation with a forced-stop fallback. Never publish a
partial response as a complete result.

## Consequences

Worker and web processes share application contracts but have separate operational
limits. Retry policy, queue selection, cancellation transport, reconciliation
mechanism and quota values must be specified and tested before production.
The broker is not a permanent results store. See [lifecycle](../architecture/data-flow.md).
