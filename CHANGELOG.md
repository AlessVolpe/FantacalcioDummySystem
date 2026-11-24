# Changelog

This file records notable application changes by release. Application versions
are independent of Central Ranking Dogma's version sequence.

## [Unreleased]

Development of 0.2.0 (Backend foundations) follows the foundation baseline.
See the [roadmap](docs/roadmap.md) for the intended exit criteria.

## [0.1.1] - Repository foundations

The first foundation release establishes the development and governance
infrastructure of Fantacalcio Dummy System. It is an installable Python
scaffold, not a usable web application.

### Added

- AGPL-3.0-only licensing, contribution and security policies, code of conduct,
  issue and pull request templates, and default code ownership ([#1][pr1]).
- Locked development tooling with uv, Ruff, strict mypy, pytest, coverage,
  EditorConfig and local Git hooks ([#2][pr2]).
- Linux and Windows CI, scoped Conventional Commit validation and regression
  tests, dependency auditing and Dependabot configuration ([#3][pr3]).
- Canonical architectural documentation, five ADRs, module boundaries, research
  data flow and milestone exit criteria ([#6][pr6]).

### Changed

- Enforced consistent text line endings across platforms ([#3][pr3]).
- Updated `actions/setup-python` from 7.0.0 to 7.1.0 ([#4][pr4]).
- Updated `astral-sh/setup-uv` from 10.3.3 to 10.4.0 ([#5][pr5]).
- Advanced application package metadata to 0.1.1 without changing runtime
  dependencies or application behavior.

### Limitations

Django, persistence, authentication, the frontend, native engine integration
and research workflows remain unimplemented. The entry point still prints the
scaffold greeting. This version does not provide a deployable research service.

## [0.1.0] - Initial scaffold

- Established the Python 3.13 package scaffold and uv project configuration.
- Introduced the project overview and historical context.
- This is a historical package version, not a claimed published GitHub release.

[pr1]: https://github.com/AlessVolpe/FantacalcioDummySystem/pull/1
[pr2]: https://github.com/AlessVolpe/FantacalcioDummySystem/pull/2
[pr3]: https://github.com/AlessVolpe/FantacalcioDummySystem/pull/3
[pr4]: https://github.com/AlessVolpe/FantacalcioDummySystem/pull/4
[pr5]: https://github.com/AlessVolpe/FantacalcioDummySystem/pull/5
[pr6]: https://github.com/AlessVolpe/FantacalcioDummySystem/pull/6
