from __future__ import annotations

import importlib.util
import re
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "g0-exact-head.yml"
SCRIPT = ROOT / "scripts" / "verify_exact_head_ci.py"
SPEC = importlib.util.spec_from_file_location("verify_exact_head_ci", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, check=True)
    return result.stdout.strip()


def make_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    (repo / "README.md").write_text("exact head\n", encoding="utf-8")
    git(repo, "add", "README.md")
    git(repo, "commit", "-m", "subject")
    return repo, git(repo, "rev-parse", "HEAD")


def environment(subject: str, event: str = "push") -> dict[str, str]:
    return {
        "CI_EXPECTED_SHA": subject,
        "CI_PR_HEAD_SHA": subject if event == "pull_request" else "",
        "GITHUB_EVENT_NAME": event,
        "GITHUB_REPOSITORY": "weizhenhaihaha-arch/yaobizuoduo",
        "GITHUB_RUN_ID": "12345",
        "GITHUB_SERVER_URL": "https://github.com",
        "GITHUB_SHA": subject,
    }


def test_workflow_freezes_read_only_secret_free_exact_head_contract() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "name: G0 / exact-head" in text
    assert "permissions:\n  contents: read" in text
    assert "persist-credentials: false" in text
    assert "github.event.pull_request.head.sha" in text
    assert "github.sha" in text
    assert "pull_request:" in text and "push:" in text
    assert "secrets." not in text
    assert "continue-on-error" not in text
    action_uses = re.findall(r"^\s*uses:\s*([^\s]+)$", text, re.MULTILINE)
    assert action_uses
    assert all(re.fullmatch(r"[^@\s]+@[0-9a-f]{40}", item) for item in action_uses)


@pytest.mark.parametrize("event", ["push", "pull_request"])
def test_verifier_accepts_exact_push_and_pr_head(tmp_path: Path, event: str) -> None:
    repo, subject = make_repo(tmp_path)
    evidence = VERIFIER.verify(repo, environment(subject, event))
    assert evidence == {
        "event": event,
        "repository": "weizhenhaihaha-arch/yaobizuoduo",
        "run_id": "12345",
        "run_url": "https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/12345",
        "subject_sha": subject,
    }


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("CI_EXPECTED_SHA", "f" * 40, "checked-out HEAD"),
        ("CI_PR_HEAD_SHA", "e" * 40, "pull request subject"),
        ("GITHUB_SHA", "e" * 40, "push subject"),
        ("GITHUB_EVENT_NAME", "workflow_dispatch", "only pull_request and push"),
        ("GITHUB_REPOSITORY", "attacker/fork", "canonical repository"),
        ("GITHUB_RUN_ID", "0", "positive integer"),
    ],
)
def test_verifier_fails_closed_on_stale_or_mismatched_identity(
    tmp_path: Path, field: str, value: str, message: str
) -> None:
    repo, subject = make_repo(tmp_path)
    environ = environment(subject, "pull_request" if field == "CI_PR_HEAD_SHA" else "push")
    environ[field] = value
    if field == "CI_EXPECTED_SHA":
        environ["GITHUB_SHA"] = value
    with pytest.raises(ValueError, match=message):
        VERIFIER.verify(repo, environ)
