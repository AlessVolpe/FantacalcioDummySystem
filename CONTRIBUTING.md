# Contributing to Fantacalcio Dummy System

Contributions must preserve the separation between application responsibilities
and native computation, the integrity of competition data, and the
reproducibility of experiments. GitHub Markdown is the canonical documentation.
Participation is subject to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Development workflow

1. Discuss substantial changes in an issue before implementing them.
2. Branch from an up-to-date `main` using `type/short-description` (for example,
   `feat/competition-model`). Use a fork if you do not have write access.
3. Install Python 3.13 and [uv](https://docs.astral.sh/uv/), then run
   `uv sync --locked` and `uv run --locked fantacalciodummysystem`.
4. Make focused changes, add regression tests for behavioral changes, and update
   the relevant documentation. Run the checks available in the repository.
5. Open a pull request against `main`, describing the motivation, verification,
   limitations and any compatibility or migration implications.

The Django project is initialized; the public application and PostgreSQL
integration verification remains pending. See [local PostgreSQL setup](docs/local-postgresql.md)
for native and Compose setup. Local quality checks are configured.
GitHub Actions verifies the same checks on Linux and Windows. Avoid unrelated
reformatting or generated files.

## Local quality checks

The `dev` dependency group contains Ruff, mypy, pytest, pytest-cov, pre-commit,
pytest-django and django-stubs. See the [backend reference](docs/architecture/backend.md#django-initialization)
for database-free checks and the pending real-database verification.
`uv sync --locked` installs this group by default. To install only runtime
dependencies, use `uv sync --locked --no-dev`.

Run from the repository root on Python 3.13:

```sh
uv lock --check
uv sync --locked
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked mypy
uv run --locked python manage.py check --settings=fantacalciodummysystem.config.settings.static
uv run --locked pytest --cov --cov-report=term-missing
```

Ruff checks imports, common errors and selected modernization and simplification
rules. Use `uv run --locked ruff check --fix .` and
`uv run --locked ruff format .` to apply safe fixes and formatting; review the
resulting diff. Mypy checks source, repository scripts and tests in strict mode. Add explicit types
and narrow, justified suppressions instead of disabling checks globally.

Pytest collects tests from `tests/` against the installed `src/` package. New
behavior requires tests; prefer deterministic fixtures and regression cases.
Coverage includes branches as well as statements. There is no numerical
coverage gate yet: establish one when substantive domain code exists, rather
than treating the scaffold's coverage as a meaningful quality target.

Install optional local Git hooks once per clone:

```sh
uv run --locked pre-commit install --config pre-commit/.pre-commit-config.yaml --hook-type pre-commit --hook-type pre-push
uv run --locked pre-commit run --config pre-commit/.pre-commit-config.yaml --all-files
uv run --locked pre-commit run --config pre-commit/.pre-commit-config.yaml --hook-stage pre-push --all-files
```

The pre-commit stage rejects private configuration files, scans for secrets,
checks formatting, lint and types; pre-push runs tests and coverage. Python
quality hooks use the project's locked `uv` environment; the pinned secret
scanner uses its own pre-commit environment. Hooks do not edit files automatically.
Ensure `uv` is on PATH when Git invokes the hooks. Local hooks supplement required CI checks; they do not
replace them.

Run the security hooks against all tracked files before opening a PR:

```sh
uv run --locked pre-commit run --config pre-commit/.pre-commit-config.yaml forbid-private-config --all-files
uv run --locked pre-commit run --config pre-commit/.pre-commit-config.yaml blank-config-templates --all-files
uv run --locked pre-commit run --config pre-commit/.pre-commit-config.yaml detect-secrets --all-files
```

Never load private `.env` files for database-free checks. Scanner findings
require review; never add a broad exclusion or a baseline of unreviewed secrets.
The scan covers tracked content, not every historical commit.

When changing dependencies, run `uv lock`, then `uv sync --locked` and the
quality checks above. Commit `pyproject.toml` and `uv.lock` together. Do not
update the lockfile simply to run routine checks.

## Code and documentation

- Use English for source identifiers, documentation, comments and repository
  discussions. Prefer clear names, explicit types and small, cohesive modules.
- Keep `pyproject.toml` and `uv.lock` consistent when dependencies change.
- Keep database, HTTP and job orchestration concerns in the application; use
  the documented [CRD JSON CLI v1 contract](https://github.com/AlessVolpe/CentralRankingDogma/blob/master/docs/integration/json-cli-v1.md)
  for native computations rather than duplicating the engine's algorithms.
- Document changes to data models, public APIs, error handling and configuration.
- Preserve authorship, third-party licensing notices and source provenance.
  New original source is contributed under AGPL-3.0-only; do not introduce code
  or datasets without compatible permissions.
- Do not commit credentials, private league data, personal information, local
  databases, generated builds or temporary patch files.

Update the [current architectural references](docs/index.md), [roadmap](docs/roadmap.md)
and relevant [ADR](docs/adr/README.md) when changing system boundaries or
scientific contracts. Distinguish proposed, accepted and implemented behavior.
Supersede accepted decisions rather than silently rewriting them.

## Scientific integrity

Changes affecting experiment results should document input revisions, engine
versions, seeds, simulation settings, relevant assumptions and limitations.
Test the same inputs against expected outputs where feasible. Distinguish
historical observations, reproducible simulated outcomes and statistical
inference. Do not claim uniform calendar sampling without supporting evidence.
Do not publish real competition data without appropriate authorization.

## Commit and pull request naming

**Every new commit subject and pull request title must contain a scope.** Use
Conventional Commits: `type(scope): imperative description`, or
`type(scope)!: imperative description` for a breaking change. Add a
`BREAKING CHANGE:` footer when needed to explain migration requirements.
Use lowercase, component-specific scopes and concise imperative descriptions.

Examples:

```text
feat(competition): introduce competition snapshots
fix(integration): reject malformed native engine responses
test(experiments): verify deterministic replay
docs(readme): describe application architecture
ci(actions): configure automated checks
build(deps): update development dependencies
chore(repo): establish repository governance
```

The canonical type and scope allowlists are maintained in
[`scripts/commit_policy.json`](scripts/commit_policy.json). Use lowercase,
component-specific scopes. The application policy is independent of CRD's native
scope vocabulary. Update the policy, tests and this guide together when adding
new scope families. Historical commits are not subject to retroactive rewriting.

Run the validator locally (Git must be installed):

```sh
uv run --locked python scripts/check_commit_messages.py --title "docs(readme): update project overview"
uv run --locked python scripts/check_commit_messages.py --range origin/main..HEAD
uv run --locked python scripts/check_commit_messages.py --commit HEAD
uv run --locked pytest tests/tooling
```

PR checks validate the title and each introduced non-merge commit, not the
historical base branch or GitHub's synthetic merge commit. Actual merge commits
in the topic branch are excluded by topology; ordinary invalid subjects are not.
The `--commit` option checks exactly one specified commit, including a merge if
explicitly selected. The policy checks subject syntax and allowlists, not grammar
or the semantics of the change. The push workflow rechecks new commits on `main`.

Pull requests use squash merging only; the squash commit subject must use the
scoped pull request title. Review and correct the generated subject before
merging if needed. Do not merge unverified changes.

## Continuous integration

The [quality workflow](.github/workflows/ci.yml) runs locked installation,
formatting, linting, strict typing and pytest with coverage on Linux and Windows
using Python 3.13. The [commit policy workflow](.github/workflows/commit-messages.yml)
checks PR titles and Git subjects. The [security workflow](.github/workflows/security.yml)
audits locked runtime and development dependencies on both platforms against
known vulnerabilities using pip-audit and scans tracked files for secrets in
a separate Linux job. It also runs weekly and on demand.
Audit coverage is limited to the selected Python version and runner platforms;
it does not inspect application logic, future environments, build-system
requirements, or the native engine. No numerical coverage threshold is imposed.

For local audit reproduction (the audit tool is isolated from the project):

```sh
uv export --locked --all-groups --no-emit-project --no-hashes --format requirements-txt --output-file audit-requirements.txt
uvx --python 3.13 pip-audit==2.10.1 --strict --no-deps --disable-pip -r audit-requirements.txt
```

Remove the generated requirements file after use. Dependabot proposes weekly
`uv` dependency and GitHub Actions updates with scoped commit prefixes.

After the first successful workflow runs, configure a branch ruleset targeting
`main`: require pull requests and the seven checks below, require the branch to
be up to date, require linear history, and block force pushes and deletion.
Keep squash merging as the only allowed merge method. A solo maintainer should
not require an independent approval until a second reviewer is available.

- `Python quality (ubuntu-latest)`
- `Python quality (windows-latest)`
- `Validate scoped commits`
- `Dependency audit (ubuntu-latest)`
- `Dependency audit (windows-latest)`
- `Automatic application release / Validate release metadata`
- `Secret scanning`

Select the actual GitHub Actions checks in the ruleset UI. No workflow file
alone configures repository protection; maintainers must enable the ruleset.

## Security reports

Do not report vulnerabilities in public issues or pull requests. Follow
[SECURITY.md](SECURITY.md) instead.
