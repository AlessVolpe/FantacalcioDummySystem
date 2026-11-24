# Development roadmap

This ledger records the proposed application milestones, independently of CRD's
version sequence. Version targets are planning labels, not release promises.

## 0.1.x: Repository foundations

| PR | Deliverable | Status at PR 4 |
| --- | --- | --- |
| 1 | Governance, AGPL licensing and contribution policy | Merged |
| 2 | uv development group, Ruff, mypy, pytest and local hooks | Merged |
| 3 | CI, scoped commit policy and security audit | Merged (workflow files) |
| 4 | Architectural documentation, ADRs and roadmap | This PR |

Exit: documentation reviewed, workflow checks passing, repository ruleset
configured by maintainer. Repository administration is not inferred from files.
The current package version remains 0.1.0 in this documentation-only PR;
consider 0.1.1 after foundation acceptance.

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

## Before implementation

Resolve database and authentication specifics in 0.2.0; competition lifecycle,
access roles and authorized import formats in 0.3.0; supported native artifact
and schema compatibility in 0.4.0; broker, retries, quotas and retention in
0.5.0. Publication and anonymization requirements must be considered in the
data model early, even if public endpoints are deferred. Do not install all
future dependencies in the foundation PR.

Maintain the [ADR register](adr/README.md) and [system architecture](architecture/system.md)
as each milestone progresses. Record actual verification evidence separately from
planned exit criteria.
