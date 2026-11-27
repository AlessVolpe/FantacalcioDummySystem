# ADR 0009: Secret isolation and database access control

**Status:** Accepted 2026-11-24; local settings and scanning introduced;
real PostgreSQL and production privilege verification pending.

## Context

FDS is a public repository. Published defaults for local authentication can
become real credentials when copied into an installation. Static analysis and
unit tests must remain usable without access to any private database.

## Decision

- No operational credentials, including development defaults, are committed.
  Database names, roles, passwords, hosts and ports are supplied at runtime;
  persistent Django signing keys are independently generated and private.
- Local secrets live in ignored files, explicitly loaded via `uv run --env-file`.
  Checked-in templates contain only variable names and empty values. Do not
  load production configuration into local profiles or use shared passwords.
- The static profile uses Django's dummy database backend and a process-local
  random signing key. It is not an alternative database or serving profile.
  Real tests explicitly select the PostgreSQL testing profile and use isolated
  credentials. Testing signing keys and synthetic fixture passwords are random.
- Support native PostgreSQL and local Docker Compose equally. Docker publishes
  only to loopback and uses a private bootstrap password file. Django never
  uses the bootstrap or PostgreSQL administrator role.
- Development and testing roles are independent and own only their dedicated
  databases. Neither has superuser, role-creation, replication or database-
  creation privileges. Use an explicitly marked, pre-provisioned test database
  with a restricted owner. The integration suite migrates it in place and
  never creates or drops databases. CI creates a fresh isolated cluster per
  job with the same restricted application role. Never use production data.
- Production migrations use a separate controlled migration role. The runtime
  role has only the database/schema access and DML needed by the application,
  not ownership or schema modification. Grant future object privileges using
  the migration owner and verify privileges on real PostgreSQL before deployment.
- When real database CI tests are introduced, generate independent disposable
  credentials per job, mask them before use, avoid command/output leakage,
  and destroy the database at job end. Never supply long-lived repository,
  development or production database credentials to PR workflows.
- Production secrets come from private server-side storage or an external secret
  manager, injected into the process environment; no committed production file.
- Use a local pre-commit scanner and a required GitHub Actions secret scan.
  Reject tracked private configuration files and nonempty templates independently
  of scanner heuristics.
  Scan tracked source without online secret verification or blanket allowlists.

## Consequences

A fresh clone can run unit tests and mypy without any credentials. Database
commands fail closed until configured. Native and Compose setups need an
administrator for one-time provisioning; separate runtime privileges are an
explicit production acceptance requirement. See [local PostgreSQL setup](../local-postgresql.md).

Scanners are defense in depth, not proof of absence. The configured scan checks
staged/tracked content, not every historical commit, and may produce false
positives. Review specific findings before any narrow exception. Rotate any
actual exposed credential immediately; deleting it from a branch does not erase
Git history, pull request diffs, caches or clones. Never reuse published defaults.
