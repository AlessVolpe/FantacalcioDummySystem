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

The application is still a scaffold. Automated linting, typing, testing and
commit validation will be established separately; this policy does not claim
that those checks already exist. Avoid unrelated reformatting or generated files.

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

Use the appropriate type (`feat`, `fix`, `docs`, `style`, `refactor`, `perf`,
`test`, `build`, `ci`, `chore`, `revert`). Initial scopes include `repo`,
`readme`, `license`, `contributing`, `security`, `tooling`, `deps`, `actions`,
`architecture`, `competition`, `integration`, `experiments`, `api`, `frontend`
and `deployment`. This list is illustrative until the automated policy is
introduced. Existing historical commits are not subject to retroactive rewriting.

Pull requests use squash merging only; the squash commit subject must use the
scoped pull request title. Review and correct the generated subject before
merging if needed. Required status checks and branch rules will be introduced
with CI. Do not merge unverified changes.

## Security reports

Do not report vulnerabilities in public issues or pull requests. Follow
[SECURITY.md](SECURITY.md) instead.
