# SPDX-License-Identifier: AGPL-3.0-only

import subprocess
from pathlib import Path

import pytest

from scripts.check_commit_messages import (
    git_commits,
    load_policy,
    main,
    validate_subject,
)


@pytest.mark.parametrize(
    "subject",
    [
        "ci(actions): establish automated quality and security workflows",
        "build(deps): bump ruff from 0.17.5 to 0.17.6",
        "ci(actions): bump actions/checkout from 7 to 8",
        "feat(api)!: replace snapshot contract",
        "fix(team): x",
        "docs(readme): describe architecture (#3)",
    ],
)
def test_valid_subject(subject: str) -> None:
    assert validate_subject(subject, *load_policy()) is None


@pytest.mark.parametrize(
    "subject",
    [
        "unscoped commit",
        "feat: missing scope",
        "feat(): empty scope",
        "Feat(api): uppercase type",
        "feat(API): uppercase scope",
        "feature(api): unknown type",
        "feat(bostree): native-only scope",
        "fix(api):",
        "fix(api): ",
        "fix(api): trailing space ",
        "fix(api):  leading space",
        "fix(api): multiline\nsubject",
        "Merge pull request #3 from topic",
    ],
)
def test_invalid_subject(subject: str) -> None:
    assert validate_subject(subject, *load_policy()) is not None


@pytest.mark.parametrize(
    "content",
    [
        "[]",
        '{"types": ["fix", "fix"], "scopes": ["api"]}',
        '{"types": ["fix"], "scopes": []}',
        '{"types": [1], "scopes": ["api"]}',
        '{"types": ["fix"], "scopes": ["API"]}',
        '{"types": ["fix"]}',
    ],
)
def test_malformed_policy(tmp_path: Path, content: str) -> None:
    policy = tmp_path / "policy.json"
    policy.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        load_policy(policy)


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.name", "CI Test")
    git(tmp_path, "config", "user.email", "ci@example.invalid")
    git(tmp_path, "config", "commit.gpgsign", "false")
    git(tmp_path, "commit", "--allow-empty", "-qm", "legacy unscoped subject")
    return tmp_path


def test_range_and_single_commit(repo: Path) -> None:
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "commit", "--allow-empty", "-qm", "fix(api): first")
    git(repo, "commit", "--allow-empty", "-qm", "fix(api): second")
    head = git(repo, "rev-parse", "HEAD")
    assert [c.subject for c in git_commits(f"{base}..{head}", cwd=repo)] == [
        "fix(api): first",
        "fix(api): second",
    ]
    assert [c.subject for c in git_commits(head, single=True, cwd=repo)] == [
        "fix(api): second"
    ]


def test_range_excludes_only_real_merges(repo: Path) -> None:
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "switch", "-qc", "topic")
    git(repo, "commit", "--allow-empty", "-qm", "fix(api): topic")
    git(repo, "switch", "-qc", "side", base)
    git(repo, "commit", "--allow-empty", "-qm", "ordinary invalid subject")
    git(repo, "switch", "-q", "topic")
    git(repo, "merge", "--no-ff", "-qm", "Merge side", "side")
    head = git(repo, "rev-parse", "HEAD")
    subjects = {c.subject for c in git_commits(f"{base}..{head}", cwd=repo)}
    assert subjects == {"fix(api): topic", "ordinary invalid subject"}
    assert validate_subject("ordinary invalid subject", *load_policy()) is not None
    assert [c.subject for c in git_commits(head, single=True, cwd=repo)] == [
        "Merge side"
    ]


@pytest.mark.parametrize("revision", ["HEAD", "HEAD...HEAD", "..HEAD", "--all..HEAD"])
def test_invalid_range(repo: Path, revision: str) -> None:
    with pytest.raises(ValueError):
        git_commits(revision, cwd=repo)


def test_title_cli_exit_codes() -> None:
    assert main(["--title", "fix(api): valid"]) == 0
    assert main(["--title", "fix: unscoped"]) == 1
    assert main(["--title", ""]) == 1
