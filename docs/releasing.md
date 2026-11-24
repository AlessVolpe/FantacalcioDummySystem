# Application releases

`pyproject.toml` is the version source of truth. For a release PR, increase
`project.version`, run `uv lock` without `--upgrade`, and add a matching
`## [X.Y.Z]` section to [CHANGELOG.md](../CHANGELOG.md). Merge using a scoped
Conventional Commit. Application versions are independent of CRD releases.

The [release workflow](../.github/workflows/release.yml) validates metadata on
PRs and pushes. A version increase merged to `main` (starting at 0.1.1) triggers
publication only after the reusable Linux/Windows quality and security workflows
and commit-policy workflow pass for that exact commit. Existing standalone
workflows and required checks remain unchanged. Routine pushes with the same
version do not publish. PRs never publish. The publish job alone receives
`contents: write`; no personal access token or deployment secret is needed.

The workflow creates a lightweight `vX.Y.Z` tag on the verified commit and a
GitHub source release with generated notes. All 0.x versions are GitHub
pre-releases; 1.x and later are ordinary releases. No PyPI upload, wheel,
container or deployment is performed at this stage. Do not manually create the
release tag before the workflow runs. Enable GitHub Actions and ensure any tag
ruleset permits the workflow to create the release tag.

If a verification or publishing step fails, fix the issue where possible and
rerun the original version-bump workflow (all jobs if needed). If a source fix
must be merged, use a new version bump instead of releasing the failed revision.
A rerun skips an existing published release on the same commit and can resume
an orphan tag on that commit. A tag on a different commit, an existing draft,
or a newer release tag requires explicit maintainer review. Never force-move a
release tag. A routine subsequent merge without a version bump is not a retry.

Publication uses `GITHUB_TOKEN`; tag creation and release creation happen in the
same workflow. Do not depend on a separate tag-triggered workflow to run as a
side effect of that token's operations.
