# SPDX-License-Identifier: AGPL-3.0-only
"""Validate scoped Conventional Commit subjects in selected Git revisions."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

POLICY_FILE = Path(__file__).with_name("commit_policy.json")
SUBJECT_PATTERN = re.compile(
    r"(?P<type>[a-z][a-z-]*)\((?P<scope>[a-z][a-z0-9-]*)\)"
    r"(?P<breaking>!)?: (?P<description>\S(?:[^\r\n]*\S)?)"
)


class Commit(NamedTuple):
    sha: str
    subject: str


def _entries(value: object, pattern: str) -> frozenset[str]:
    if not isinstance(value, list) or not value:
        raise ValueError("policy entries must be a nonempty list")
    entries: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not re.fullmatch(pattern, item):
            raise ValueError("invalid commit policy entry")
        if item in entries:
            raise ValueError("duplicate commit policy entry")
        entries.add(item)
    return frozenset(entries)


def load_policy(path: Path = POLICY_FILE) -> tuple[frozenset[str], frozenset[str]]:
    data: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"types", "scopes"}:
        raise ValueError("policy must contain types and scopes")
    return (
        _entries(data["types"], r"[a-z][a-z-]*"),
        _entries(data["scopes"], r"[a-z][a-z0-9-]*"),
    )


def validate_subject(
    subject: str, types: frozenset[str], scopes: frozenset[str]
) -> str | None:
    match = SUBJECT_PATTERN.fullmatch(subject)
    if match is None:
        return "expected type(scope): description or type(scope)!: description"
    if match["type"] not in types:
        return f"unknown type '{match['type']}' (allowed: {', '.join(sorted(types))})"
    if match["scope"] not in scopes:
        allowed = ", ".join(sorted(scopes))
        return f"unknown scope '{match['scope']}' (allowed: {allowed})"
    return None


def _resolve_commit(ref: str, cwd: Path | None) -> str:
    if not ref or ref.startswith("-") or ".." in ref:
        raise ValueError("expected a single commit reference")
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}"],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    sha = result.stdout.strip()
    if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", sha):
        raise ValueError("unexpected Git object ID")
    return sha


def git_commits(
    revision: str, *, single: bool = False, cwd: Path | None = None
) -> list[Commit]:
    """Read one commit or a two-dot range, skipping only actual merge commits."""
    if single:
        # Select exactly this commit, even if it is a merge; never walk its parents.
        selection = ["-1", _resolve_commit(revision, cwd)]
    else:
        parts = revision.split("..")
        if len(parts) != 2 or any(not part or part.startswith(".") for part in parts):
            raise ValueError("expected a two-dot BASE..HEAD range")
        base, head = (_resolve_commit(part, cwd) for part in parts)
        selection = ["--no-merges", "--reverse", f"{base}..{head}"]
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s", *selection, "--"],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    commits: list[Commit] = []
    for line in result.stdout.split("\n"):
        if not line:
            continue
        sha, tab, subject = line.partition("\t")
        if not tab or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", sha):
            raise ValueError("unexpected Git log format")
        commits.append(Commit(sha, subject))
    return commits


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--range", dest="revision_range", metavar="BASE..HEAD")
    source.add_argument("--commit", metavar="SHA")
    parser.add_argument("--title", help="validate a pull request title")
    args = parser.parse_args(argv)
    if args.revision_range is None and args.commit is None and args.title is None:
        parser.error("provide --title, --range or --commit")

    try:
        types, scopes = load_policy()
        commits: list[Commit] = []
        if args.revision_range is not None:
            commits = git_commits(args.revision_range)
        elif args.commit is not None:
            commits = git_commits(args.commit, single=True)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Commit policy validation failed: {exc}", file=sys.stderr)
        return 2

    records = [Commit("PR title", args.title)] if args.title is not None else []
    records.extend(commits)
    if not records:
        print("Commit policy validation failed: no subjects found", file=sys.stderr)
        return 2

    problems = 0
    for record in records:
        problem = validate_subject(record.subject, types, scopes)
        if problem:
            print(f"FAIL {record.sha}: {record.subject!r}\n     {problem}")
            problems += 1
        else:
            print(f"PASS {record.sha}: {record.subject!r}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
