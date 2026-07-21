from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_project_status.py"
SCHEMA = ROOT / "schemas" / "project_status.schema.json"
FIXTURES = ROOT / "fixtures" / "g0"


def run_validator(path: Path, repo_root: Path | None = None) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT), str(path), "--schema", str(SCHEMA)]
    if repo_root is not None:
        command.extend(["--repo-root", str(repo_root)])
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)


def test_canonical_status_and_documents_are_valid() -> None:
    result = run_validator(ROOT / "PROJECT_STATUS.yaml", ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == f"OK {ROOT / 'PROJECT_STATUS.yaml'}: project-status.v1\n"


def test_valid_awaiting_review_fixture_is_accepted() -> None:
    result = run_validator(FIXTURES / "valid_awaiting_review.json")
    assert result.returncode == 0


@pytest.mark.parametrize(
    ("name", "diagnostic"),
    [
        ("invalid_unknown_state.json", "value is not in the allowed set"),
        ("invalid_illegal_transition.json", "illegal lifecycle transition"),
        ("invalid_multiple_active_tasks.json", "too many items"),
        ("invalid_malformed_sha.json", "string has invalid format"),
        ("invalid_missing_review_ci.json", "accepted states require"),
        ("invalid_maturity_upgrade.json", "maturity exceeds evidence"),
        ("invalid_unknown_key.json", "unknown field"),
    ],
)
def test_adversarial_fixtures_fail_closed(name: str, diagnostic: str) -> None:
    result = run_validator(FIXTURES / name)
    assert result.returncode == 1
    assert diagnostic in result.stdout
    assert result.stderr == ""


def test_coercible_values_and_nested_unknown_keys_fail_closed(tmp_path: Path) -> None:
    status = json.loads((FIXTURES / "valid_awaiting_review.json").read_text())
    status["active_tasks"][0]["candidate_generation"] = "1"
    status["review"]["extra"] = False
    path = tmp_path / "status.json"
    path.write_text(json.dumps(status), encoding="utf-8")
    result = run_validator(path)
    assert result.returncode == 1
    assert "invalid type" in result.stdout
    assert "unknown field" in result.stdout


def test_duplicate_json_keys_fail_closed(tmp_path: Path) -> None:
    original = (FIXTURES / "valid_awaiting_review.json").read_text()
    path = tmp_path / "status.json"
    path.write_text(original.replace('"project": "yaobizuoduo",', '"project": "yaobizuoduo", "project": "other",', 1), encoding="utf-8")
    result = run_validator(path)
    assert result.returncode == 1
    assert "unreadable JSON-compatible status/schema: ValueError" in result.stdout


def test_stale_current_stage_claim_is_rejected(tmp_path: Path) -> None:
    status = json.loads((FIXTURES / "valid_awaiting_review.json").read_text())
    status["governed_documents"] = ["GOVERNANCE.md"]
    status_path = tmp_path / "status.json"
    status_path.write_text(json.dumps(status), encoding="utf-8")
    (tmp_path / "GOVERNANCE.md").write_text("当前项目处于 M7。\n", encoding="utf-8")
    result = run_validator(status_path, tmp_path)
    assert result.returncode == 1
    assert result.stdout == "ERROR $.governed_documents: stale current-state claim in GOVERNANCE.md\n"


def test_current_task_mirror_conflict_is_rejected(tmp_path: Path) -> None:
    status = json.loads((FIXTURES / "valid_awaiting_review.json").read_text())
    status["governed_documents"] = ["CURRENT_TASK.md"]
    status_path = tmp_path / "status.json"
    status_path.write_text(json.dumps(status), encoding="utf-8")
    (tmp_path / "CURRENT_TASK.md").write_text("- Task ID: `G0-T02`\n- Status: `in_progress`\n", encoding="utf-8")
    result = run_validator(status_path, tmp_path)
    assert result.returncode == 1
    assert "CURRENT_TASK task_id conflicts" in result.stdout
    assert "CURRENT_TASK state conflicts" in result.stdout


def test_returned_repair_invalidates_old_candidate_review_and_ci(tmp_path: Path) -> None:
    status = json.loads((FIXTURES / "valid_awaiting_review.json").read_text())
    status["active_tasks"][0].update(state="in_progress", transition={"from": "returned", "to": "in_progress"}, candidate_generation=2)
    status["review"] = {"code_security": "pending", "architecture": "pending", "reviewed_candidate_sha": "1" * 40}
    path = tmp_path / "status.json"
    path.write_text(json.dumps(status), encoding="utf-8")
    result = run_validator(path)
    assert result.returncode == 1
    assert "invalidate prior candidate, review, and CI identity" in result.stdout
