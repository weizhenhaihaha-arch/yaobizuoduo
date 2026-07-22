#!/usr/bin/env python3
"""Fail closed unless GitHub Actions checked out the exact canonical event subject."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path


EXPECTED_REPOSITORY = "weizhenhaihaha-arch/yaobizuoduo"
EXPECTED_SERVER_URL = "https://github.com"
SHA_PATTERN = re.compile(r"[0-9a-f]{40}")
RUN_ID_PATTERN = re.compile(r"[1-9][0-9]*")


def fail(message: str) -> None:
    raise ValueError(message)


def exact_env(environ: dict[str, str], name: str) -> str:
    value = environ.get(name)
    if type(value) is not str or not value:
        fail(f"{name} is required")
    return value


def git_head(repo: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        fail("unable to resolve checked-out HEAD")
    return result.stdout.strip()


def verify(repo: Path, environ: dict[str, str]) -> dict[str, str]:
    event = exact_env(environ, "GITHUB_EVENT_NAME")
    expected_sha = exact_env(environ, "CI_EXPECTED_SHA")
    github_sha = exact_env(environ, "GITHUB_SHA")
    repository = exact_env(environ, "GITHUB_REPOSITORY")
    run_id = exact_env(environ, "GITHUB_RUN_ID")
    server_url = exact_env(environ, "GITHUB_SERVER_URL")

    if SHA_PATTERN.fullmatch(expected_sha) is None:
        fail("CI_EXPECTED_SHA must be a lowercase full commit SHA")
    if SHA_PATTERN.fullmatch(github_sha) is None:
        fail("GITHUB_SHA must be a lowercase full commit SHA")
    if repository != EXPECTED_REPOSITORY:
        fail("workflow repository does not match the canonical repository")
    if server_url != EXPECTED_SERVER_URL:
        fail("workflow server does not match canonical GitHub")
    if RUN_ID_PATTERN.fullmatch(run_id) is None:
        fail("GITHUB_RUN_ID must be a positive integer")

    if event == "pull_request":
        pr_head = exact_env(environ, "CI_PR_HEAD_SHA")
        if pr_head != expected_sha:
            fail("pull request subject must equal github.event.pull_request.head.sha")
    elif event == "push":
        if expected_sha != github_sha:
            fail("push subject must equal github.sha")
    else:
        fail("only pull_request and push events are accepted")

    actual_sha = git_head(repo)
    if actual_sha != expected_sha:
        fail("checked-out HEAD does not equal the exact event subject")

    run_url = f"{server_url}/{repository}/actions/runs/{run_id}"
    return {
        "event": event,
        "repository": repository,
        "run_id": run_id,
        "run_url": run_url,
        "subject_sha": actual_sha,
    }


def write_summary(evidence: dict[str, str], environ: dict[str, str]) -> None:
    summary_path = environ.get("GITHUB_STEP_SUMMARY")
    if type(summary_path) is not str or not summary_path:
        return
    lines = [
        "## G0 exact-head evidence",
        "",
        "```json",
        json.dumps(evidence, sort_keys=True),
        "```",
        "",
    ]
    with Path(summary_path).open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def main() -> int:
    try:
        evidence = verify(Path.cwd(), dict(os.environ))
        write_summary(evidence, dict(os.environ))
    except (OSError, ValueError) as exc:
        print(f"ERROR {exc}")
        return 1
    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
