# Development roadmap

This ledger records the proposed application milestones, independently of CRD's
version sequence. Version targets are planning labels, not release promises.

## 0.1.x: Repository foundations

**Status:** completed in the 0.1.1 foundation baseline.

| GitHub PR | Deliverable | Status |
| --- | --- | --- |
| [#1](https://github.com/AlessVolpe/FantacalcioDummySystem/pull/1) | Governance, AGPL licensing and contribution policy | Merged |
| [#2](https://github.com/AlessVolpe/FantacalcioDummySystem/pull/2) | uv development group, Ruff, mypy, pytest and local hooks | Merged |
| [#3](https://github.com/AlessVolpe/FantacalcioDummySystem/pull/3) | CI, scoped commit policy and security audit | Merged |
| [#6](https://github.com/AlessVolpe/FantacalcioDummySystem/pull/6) | Architectural documentation, ADRs and roadmap | Merged |

Routine GitHub Actions dependency maintenance also landed in
[#4](https://github.com/AlessVolpe/FantacalcioDummySystem/pull/4)
(`actions/setup-python` 7.0.0 to 7.1.0) and
[#5](https://github.com/AlessVolpe/FantacalcioDummySystem/pull/5)
(`astral-sh/setup-uv` 10.3.3 to 10.4.0).

### Foundation acceptance

- Documentation and architectural decisions merged in #6.
- Repository ruleset recorded as enabled in the [maintained README](../README.md#development-status); administrative configuration remains the maintainer's responsibility.
- Successful main-branch workflow runs on the pre-closure commit
  [`e4c9944`](https://github.com/AlessVolpe/FantacalcioDummySystem/commit/e4c994448ed4c38fa92ec869a4d2cd388f615efa):
  [Python quality](https://github.com/AlessVolpe/FantacalcioDummySystem/actions/runs/45402187780),
  [commit policy](https://github.com/AlessVolpe/FantacalcioDummySystem/actions/runs/45402187785),
  [dependency security](https://github.com/AlessVolpe/FantacalcioDummySystem/actions/runs/45402187873).
- The closure PR must pass the required checks before merging. Tag `v0.1.1`
  only after successful verification of the merged release commit.

The current implementation milestone is **0.2.0: Backend foundations**.
See the [changelog](../CHANGELOG.md) for the foundation release record.

## Implementation milestones

| Target | Milestone | Exit criteria |
| --- | --- | --- |
| 0.2.0 | Backend foundations | Django configuration, selected DB, migrations, authentication/access foundation and API/error conventions verified locally and in CI |
| 0.3.0 | Competition management | Authorized creation/editing of competitions, stable team UUIDs, original calendar, scores and rules; immutable revision and import validation tests |
| 0.4.0 | Native integration | Pinned CRD artifact; JSON CLI v1 adapter; real executable tests for validation, resolution, simulation, errors, timeouts and replay |
| 0.5.0 | Experiment lifecycle | Persistent jobs, duplicate-safe dispatch/recovery, cancellation, bounded resources, validated results and provenance |
| 0.6.0 | Frontend foundations | React/TypeScript build, routes, access flows, API integration and frontend CI |
| 0.7.0 | Research interface | Basic and advanced results, baseline comparisons, explicit partial status and bounded example inspection |
| 0.8.0 | Publication and sharing | Authorized public projections, consistent anonymization and exports with provenance; privacy regression tests |
| 0.9.0 | Deployment and validation | Reproducible Docker Compose deployment, Linux integration, backups/restores, operational limits and end-to-end tests |
| 1.0.0 | First stable release | Documented independently deployable research application; supported versions and limitations, reproducibility and security review |

## 0.2.0: Backend foundations

**Status:** in progress; architecture selected; Django initialized; PostgreSQL
persistence implementation and verification in PR 3.

| PR (milestone sequence) | Deliverable | Acceptance criteria |
| --- | --- | --- |
| 1 | Architecture | ADRs 0006–0008 reviewed and merged |
| 2 | Django initialization | Django 5.2 LTS, settings, management commands, custom email/UUID user model and initial migration; database-free checks; real PostgreSQL migration verification in PR 3 |
| 3 | Persistence | PostgreSQL Compose, host uv workflow, migration and real database tests; CI and reusable release workflows provision PostgreSQL on supported runners |
| 4 | Authentication | Public registration, verification, recovery, login/logout, session and CSRF checks, access controls and abuse protection |
| 5 | API foundations | Versioned REST resources, OpenAPI, consistent errors, bounded pagination, health checks and explicit permissions |
| 6 | Backend verification | Fresh database migrations, migration drift checks, strict typing, security settings, integration tests on Linux and Windows, updated documentation |
| Closure | Release | Changelog, acceptance evidence, version bump and automatic v0.2.0 release |

Keep version 0.1.1 until milestone closure. Coordinate the database-dependent
checks in PRs 2 and 3 so no intermediate merge breaks the existing CI gates:
introduce required PostgreSQL provisioning before enabling tests that need it.
Track the Django 6.2 LTS upgrade as a priority when stable and compatible,
independent of the milestone sequence ([ADR 0006](adr/0006-backend-stack.md)).

## Before implementation

Resolve remaining identity implementation details in 0.2.0; competition lifecycle,
access roles and authorized import formats in 0.3.0; supported native artifact
and schema compatibility in 0.4.0; broker, retries, quotas and retention in
0.5.0. Publication and anonymization requirements must be considered in the
data model early, even if public endpoints are deferred. Do not install all
future dependencies in the foundation PR.

Maintain the [ADR register](adr/README.md) and [system architecture](architecture/system.md)
as each milestone progresses. Record actual verification evidence separately from
planned exit criteria.
