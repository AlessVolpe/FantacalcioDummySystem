# ADR 0003: Persistence and immutable revisions

**Status:** Accepted principles; PostgreSQL confirmed by
[ADR 0006](0006-backend-stack.md). The historical proposal below records the
original context; detailed persistence invariants remain applicable.

## Context

Users need editable competition data, while experiments must retain their
historical inputs and results. The native engine must not query a database.

## Decision

Use relational persistence owned by the application. Freeze a complete revision
before dispatching a job; later edits cannot modify that revision. Persist
experiments, execution attempts and validated results with explicit ownership
and authorization checks. Keep imported data provenance and distinguish pending
scores from finalized zero. Use transactions for revision and result publication.

PostgreSQL is the proposed production database, subject to confirmation at the
backend milestone. Local testing should not assume SQLite is behaviorally
equivalent for transactions, constraints or concurrency. Exact normalization,
access roles, retention, deletion and migration policies remain open.

## Consequences

Immutable revisions consume storage but prevent historical results from drifting.
A database transaction does not make broker delivery atomic; dispatch and recovery
need a documented strategy. Database constraints complement, not replace,
native semantic validation. No database or ORM dependency is added in this PR.
