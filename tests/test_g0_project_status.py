from __future__ import annotations

import copy
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


def load_valid() -> dict:
    return json.loads((FIXTURES / "valid_awaiting_review.json").read_text())


def write_status(path: Path, status: dict) -> None:
    path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")


def ci(status: str = "not_established", subject: str | None = None, run: str | None = None) -> dict:
    return {
        "status": status,
        "subject_sha": subject,
        "run_id": run,
        "url": None if run is None else f"https://github.com/a/b/actions/runs/{run}",
    }


def accepted_status() -> dict:
    status = load_valid()
    candidate = "2" * 40
    status["active_tasks"][0].update(state="accepted_pending_merge", transition={"from": "awaiting_review", "to": "accepted_pending_merge"})
    status["evidence"]["candidate"]["commit_sha"] = candidate
    status["evidence"]["candidate"]["ci"] = ci("success", candidate, "1")
    status["review"] = {"code_security": "approve", "architecture": "clear", "reviewed_candidate_sha": candidate}
    status["bootstrap_exception"] = None
    return status


def returned_status() -> dict:
    status = load_valid()
    candidate = "2" * 40
    status["active_tasks"][0].update(state="returned", transition={"from": "awaiting_review", "to": "returned"})
    status["evidence"]["candidate"]["commit_sha"] = candidate
    status["review"] = {"code_security": "request_changes", "architecture": "clear", "reviewed_candidate_sha": candidate}
    return status


def mutate(case_id: str) -> dict:
    status = load_valid()
    task = status["active_tasks"][0]
    if case_id == "unknown_state":
        task.update(state="done", transition={"from": "in_progress", "to": "done"})
    elif case_id == "illegal_transition":
        task.update(state="closed", transition={"from": "awaiting_review", "to": "closed"})
    elif case_id == "multiple_active_tasks":
        status["active_tasks"].append(copy.deepcopy(task))
    elif case_id == "malformed_sha":
        status["evidence"]["implementation_sha"] = "not-a-sha"
    elif case_id == "missing_review_ci":
        status = accepted_status()
        status["evidence"]["candidate"]["ci"] = ci("not_run")
    elif case_id == "maturity_ceiling":
        status["capability"]["maturity"] = "INTEGRATION_ACCEPTED"
    elif case_id == "unknown_key":
        status["surprise"] = True
    elif case_id == "returned_pending_review":
        status = returned_status()
        status["review"]["architecture"] = "pending"
    elif case_id == "returned_success_ci":
        status = returned_status()
        candidate = status["evidence"]["candidate"]["commit_sha"]
        status["evidence"]["candidate"]["ci"] = ci("success", candidate, "1")
    elif case_id == "watch_non_mergeable":
        status = accepted_status()
        status["review"]["architecture"] = "watch"
    elif case_id == "next_gate_prefix":
        status["next_authorization"].update(gate="G1", task_id="G0-T02")
    elif case_id == "next_gate_skip":
        status["next_authorization"].update(gate="G2", task_id="G2-T01")
    elif case_id == "bootstrap_reuse":
        status["bootstrap_exception"]["uses"] = 2
    else:
        raise AssertionError(case_id)
    return status


def test_canonical_status_and_documents_are_valid() -> None:
    result = run_validator(ROOT / "PROJECT_STATUS.yaml", ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.endswith("project-status.v2\n")


def test_valid_awaiting_review_fixture_is_accepted() -> None:
    assert run_validator(FIXTURES / "valid_awaiting_review.json").returncode == 0


@pytest.mark.parametrize("case", json.loads((FIXTURES / "adversarial_mutations.json").read_text())["cases"])
def test_adversarial_mutations_fail_closed(case: dict, tmp_path: Path) -> None:
    path = tmp_path / "status.json"
    write_status(path, mutate(case["id"]))
    result = run_validator(path)
    assert result.returncode == 1
    assert case["expected"] in result.stdout
    assert result.stderr == ""


def test_coercible_nested_unknown_and_duplicate_keys_fail_closed(tmp_path: Path) -> None:
    status = load_valid()
    status["active_tasks"][0]["candidate_generation"] = "2"
    status["review"]["extra"] = False
    path = tmp_path / "status.json"
    write_status(path, status)
    result = run_validator(path)
    assert result.returncode == 1
    assert "invalid type" in result.stdout and "unknown field" in result.stdout
    path.write_text((FIXTURES / "valid_awaiting_review.json").read_text().replace('"project": "yaobizuoduo",', '"project": "yaobizuoduo", "project": "other",', 1))
    result = run_validator(path)
    assert result.returncode == 1
    assert "ValueError" in result.stdout


def test_returned_repair_must_clear_all_identities_and_increment_generation(tmp_path: Path) -> None:
    status = returned_status()
    status["active_tasks"][0].update(state="in_progress", transition={"from": "returned", "to": "in_progress"}, candidate_generation=1)
    path = tmp_path / "status.json"
    write_status(path, status)
    result = run_validator(path)
    assert result.returncode == 1
    assert "returned repair must increment generation" in result.stdout
    assert "undelivered state must clear" in result.stdout
    status["active_tasks"][0]["candidate_generation"] = 2
    status["evidence"]["implementation_sha"] = None
    status["evidence"]["candidate"] = {"commit_sha": None, "local_verification": {"status": "pending", "subject": "delivery_head"}, "ci": ci()}
    status["review"] = {"code_security": "pending", "architecture": "pending", "reviewed_candidate_sha": None}
    write_status(path, status)
    assert run_validator(path).returncode == 0


@pytest.mark.parametrize(
    ("gate", "maturity"),
    [("G0", "INTEGRATION_ACCEPTED"), ("G3", "INTEGRATION_ACCEPTED"), ("G5", "INTEGRATION_ACCEPTED"), ("G6", "PAPER_VALIDATED"), ("G7", "PAPER_VALIDATED"), ("G8", "RELEASE_READY")],
)
def test_all_gate_maturity_ceilings(gate: str, maturity: str, tmp_path: Path) -> None:
    status = load_valid()
    number = gate[1:]
    status["current_gate"] = gate
    status["active_tasks"][0].update(task_id=f"{gate}-T01", state="in_progress", transition={"from": "authorized", "to": "in_progress"}, candidate_generation=1)
    status["evidence"]["implementation_sha"] = None
    status["evidence"]["candidate"]["local_verification"]["status"] = "pending"
    status["bootstrap_exception"] = None
    status["capability"]["maturity"] = maturity
    status["next_authorization"].update(gate=gate, task_id=f"G{number}-T02")
    path = tmp_path / "status.json"
    write_status(path, status)
    result = run_validator(path)
    assert result.returncode == 1
    assert "maturity exceeds current gate ceiling" in result.stdout


def test_g9_release_ready_requires_owner_go_complete_evidence_and_closed_state(tmp_path: Path) -> None:
    status = load_valid()
    status["current_gate"] = "G9"
    status["active_tasks"][0].update(task_id="G9-T01", state="in_progress", transition={"from": "authorized", "to": "in_progress"}, candidate_generation=1)
    status["evidence"]["implementation_sha"] = None
    status["evidence"]["candidate"]["local_verification"]["status"] = "pending"
    status["bootstrap_exception"] = None
    status["capability"]["maturity"] = "RELEASE_READY"
    status["next_authorization"].update(gate="G9", task_id="G9-T02")
    path = tmp_path / "status.json"
    write_status(path, status)
    result = run_validator(path)
    assert result.returncode == 1
    assert "explicit owner go" in result.stdout


def test_bootstrap_exception_is_exact_single_use_and_dual_review_bound(tmp_path: Path) -> None:
    status = accepted_status()
    status["bootstrap_exception"] = load_valid()["bootstrap_exception"]
    status["bootstrap_exception"].update(status="consumed", uses=1)
    status["evidence"]["candidate"]["ci"] = ci()
    path = tmp_path / "status.json"
    write_status(path, status)
    assert run_validator(path).returncode == 0
    status["active_tasks"][0]["task_id"] = "G0-T02"
    status["next_authorization"]["task_id"] = "G0-T03"
    write_status(path, status)
    result = run_validator(path)
    assert result.returncode == 1
    assert "restricted to the authorized G0-T01 baseline" in result.stdout


def test_bootstrap_exception_rejects_ci_claim_and_watch(tmp_path: Path) -> None:
    status = accepted_status()
    status["bootstrap_exception"] = load_valid()["bootstrap_exception"]
    status["bootstrap_exception"].update(status="consumed", uses=1)
    status["review"]["architecture"] = "watch"
    path = tmp_path / "status.json"
    write_status(path, status)
    result = run_validator(path)
    assert result.returncode == 1
    assert "dual clear local review evidence" in result.stdout
    assert "cannot coexist with CI claims" in result.stdout


def test_phase_ci_subject_must_match_exact_phase_commit(tmp_path: Path) -> None:
    status = accepted_status()
    status["evidence"]["candidate"]["ci"]["subject_sha"] = "3" * 40
    path = tmp_path / "status.json"
    write_status(path, status)
    result = run_validator(path)
    assert result.returncode == 1
    assert "CI subject must equal the recorded phase commit" in result.stdout


def test_structural_document_conflicts_and_memory_authority_fail_closed(tmp_path: Path) -> None:
    status = load_valid()
    status["governed_documents"] = ["GOVERNANCE.md", "CURRENT_TASK.md", "PROJECT_MEMORY.md"]
    path = tmp_path / "status.json"
    write_status(path, status)
    (tmp_path / "GOVERNANCE.md").write_text("- Current Gate: G9\n", encoding="utf-8")
    (tmp_path / "CURRENT_TASK.md").write_text("- Task ID: `G0-T02`\n- Gate: G9 release\n- Risk: `D2`\n- Status: `closed`\n- Baseline: `" + "9" * 40 + "`\n", encoding="utf-8")
    (tmp_path / "PROJECT_MEMORY.md").write_text("- Current Maturity: RELEASE_READY\n", encoding="utf-8")
    result = run_validator(path, tmp_path)
    assert result.returncode == 1
    for diagnostic in ("forbidden current-state mirror", "CURRENT_TASK task_id conflicts", "CURRENT_TASK gate conflicts", "CURRENT_TASK state conflicts", "PROJECT_MEMORY must declare historical-only authority"):
        assert diagnostic in result.stdout


def test_invalid_utf8_governed_document_is_sanitized(tmp_path: Path) -> None:
    status = load_valid()
    status["governed_documents"] = ["BAD.md"]
    path = tmp_path / "status.json"
    write_status(path, status)
    (tmp_path / "BAD.md").write_bytes(b"\xff\xfe")
    result = run_validator(path, tmp_path)
    assert result.returncode == 1
    assert "unreadable governed document: BAD.md" in result.stdout
    assert "Traceback" not in result.stdout + result.stderr


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, check=True)
    return result.stdout.strip()


def commit(repo: Path, message: str) -> str:
    git(repo, "add", ".")
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def write_governed(repo: Path, status: dict) -> None:
    task = status["active_tasks"][0]
    write_status(repo / "PROJECT_STATUS.yaml", status)
    (repo / "CURRENT_TASK.md").write_text(
        f"- Task ID: `{task['task_id']}`\n- Gate: {status['current_gate']} test\n- Risk: `{task['risk']}`\n- Status: `{task['state']}`\n- Baseline: `{status['evidence']['authorization_baseline_sha']}`\n",
        encoding="utf-8",
    )
    (repo / "PROJECT_MEMORY.md").write_text("Historical record; not the current machine-state authority.\n", encoding="utf-8")


def make_delivery_repo(tmp_path: Path) -> tuple[Path, dict, str, str, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    (repo / "README.md").write_text("baseline\n")
    baseline = commit(repo, "baseline")
    (repo / "implementation.txt").write_text("implementation\n")
    implementation = commit(repo, "implementation")
    status = load_valid()
    status["current_gate"] = "G1"
    status["active_tasks"][0].update(task_id="G1-T01", candidate_generation=1)
    status["evidence"]["authorization_baseline_sha"] = baseline
    status["evidence"]["implementation_sha"] = implementation
    status["bootstrap_exception"] = None
    status["next_authorization"].update(gate="G1", task_id="G1-T02")
    status["governed_documents"] = ["CURRENT_TASK.md", "PROJECT_MEMORY.md"]
    write_governed(repo, status)
    candidate = commit(repo, "candidate delivery")
    return repo, status, baseline, implementation, candidate


def test_repository_exact_head_and_returned_candidate_identity(tmp_path: Path) -> None:
    repo, status, _, _, candidate = make_delivery_repo(tmp_path)
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout
    status["active_tasks"][0].update(state="returned", transition={"from": "awaiting_review", "to": "returned"})
    status["evidence"]["candidate"]["commit_sha"] = candidate
    status["review"] = {"code_security": "request_changes", "architecture": "clear", "reviewed_candidate_sha": candidate}
    write_governed(repo, status)
    commit(repo, "return candidate")
    assert run_validator(repo / "PROJECT_STATUS.yaml", repo).returncode == 0
    tree = git(repo, "write-tree")
    stray = subprocess.run(["git", "commit-tree", tree], cwd=repo, text=True, input="stray\n", capture_output=True, check=True).stdout.strip()
    status["evidence"]["candidate"]["commit_sha"] = stray
    status["review"]["reviewed_candidate_sha"] = stray
    write_governed(repo, status)
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "not the matching delivered candidate phase" in result.stdout
    assert "unrelated to current HEAD" in result.stdout


def test_repository_phase_objects_ancestry_identity_and_close_chain(tmp_path: Path) -> None:
    repo, status, _, _, candidate = make_delivery_repo(tmp_path)
    status["active_tasks"][0].update(state="accepted_pending_merge", transition={"from": "awaiting_review", "to": "accepted_pending_merge"})
    status["evidence"]["candidate"]["commit_sha"] = candidate
    status["evidence"]["candidate"]["ci"] = ci("success", candidate, "1")
    status["review"] = {"code_security": "approve", "architecture": "clear", "reviewed_candidate_sha": candidate}
    write_governed(repo, status)
    closure = commit(repo, "closure")
    assert run_validator(repo / "PROJECT_STATUS.yaml", repo).returncode == 0

    git(repo, "switch", "-c", "merge-side")
    (repo / "side.txt").write_text("side\n")
    commit(repo, "side")
    git(repo, "switch", "main")
    git(repo, "merge", "--no-ff", "merge-side", "-m", "implementation merge")
    merged = git(repo, "rev-parse", "HEAD")

    status["active_tasks"][0].update(state="merged_verified", transition={"from": "accepted_pending_merge", "to": "merged_verified"})
    status["evidence"]["closure"].update(commit_sha=closure, ci=ci("success", closure, "2"))
    status["evidence"]["merged_main"].update(commit_sha=merged, ci=ci("success", merged, "3"))
    write_governed(repo, status)
    finalization = commit(repo, "finalization")
    assert run_validator(repo / "PROJECT_STATUS.yaml", repo).returncode == 0

    status["active_tasks"][0].update(state="closed", transition={"from": "merged_verified", "to": "closed"})
    status["evidence"]["finalization"].update(commit_sha=finalization, d0_ci=ci("success", finalization, "4"))
    write_governed(repo, status)
    commit(repo, "close record")
    assert run_validator(repo / "PROJECT_STATUS.yaml", repo).returncode == 0


def test_uncommitted_phase_subject_and_fabricated_object_fail(tmp_path: Path) -> None:
    repo, status, _, _, _ = make_delivery_repo(tmp_path)
    status["evidence"]["implementation_sha"] = "f" * 40
    write_governed(repo, status)
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "Git commit does not exist" in result.stdout
    assert "exact committed repository HEAD" in result.stdout
