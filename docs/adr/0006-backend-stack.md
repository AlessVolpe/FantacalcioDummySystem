# ADR 0006: Backend technology and persistence

**Status:** Accepted 2026-11-24; implementation pending.

## Context

[ADR 0001](0001-system-architecture.md) and [ADR 0003](0003-persistence-strategy.md)
left the backend stack and database selection provisional. The 0.2.0 milestone
must establish a testable platform before competition models are introduced.

## Decision

- Retain Python 3.13, uv and the existing installable `src` package. Use Django
  5.2 LTS with current security and bug-fix patches, Django REST Framework (DRF)
  and OpenAPI for the versioned HTTP API.
- Use PostgreSQL in local development, database integration tests and production;
  SQLite is not a supported substitute. Start with PostgreSQL 18 and Psycopg 3
  as the implementation targets, subject to compatibility verification.
- Run PostgreSQL in Docker Compose locally; run Python on the host using uv.
  CI provisions an isolated PostgreSQL instance for database tests on each
  supported runner, not necessarily using the same provisioning mechanism.
- Use versioned migrations, timezone-aware UTC timestamps and transactions.
  Development and test settings must never point at production databases.
- Keep Django settings and application modules in the existing package. Do not
  introduce a second Python project or premature empty domain applications.

Use pytest-django, django-stubs, djangorestframework-stubs and drf-spectacular
as proposed implementation tools; verify their compatibility before locking
versions. Keep strict typing. ASGI is the proposed server interface, with
Uvicorn as a deployment candidate; final server configuration is deferred.

### Django upgrade policy

Django 6.2 LTS is expected in April 2027 according to the upstream
[release schedule](https://www.djangoproject.com/download/). Prioritize moving
from 5.2 to 6.2 as soon as the stable 6.2 release and required dependencies
are compatible. Do not wait for the 5.2 end-of-support deadline. Track
upstream release notes and resolve deprecation warnings during development.
Use the [incremental upgrade procedure](https://docs.djangoproject.com/en/dev/howto/upgrade-version/)
through 6.0 and 6.1 in a dedicated upgrade branch, validating migrations,
authentication, API schema, strict types and both-platform CI at each step.
Update the locked dependencies and record verification before merging. Do not
install a development or prerelease Django version in the supported baseline.
If a dependency blocks the upgrade, record the blocker and revisit promptly.

## Consequences

A single database engine avoids false confidence from SQLite's different
constraint and transaction behavior, at the cost of requiring local and CI
infrastructure. The selected LTS reduces near-term churn without making the
framework version a permanent contract. CRD, Celery, the broker and React
remain separate later milestones. This record resolves the provisional backend
and database choices in ADRs 0001 and 0003 without changing their boundaries
or immutable-revision principles.
