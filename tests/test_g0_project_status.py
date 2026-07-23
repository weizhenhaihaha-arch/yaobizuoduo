from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
G0_T01_CLOSE_RECORD = "94892d79b8d39ac1726cf657fac0ae76a0e27b37"
G0_T02_CLOSED_MAIN = "09bfbd23d898198fe694a3a94f77663759dd89d8"
G0_T02_GENERATION1_IMPLEMENTATION = "5f3a6e93b69947b73e21e51c7e0218c0c283f6de"
G0_T02_GENERATION1_BLOCKED = "925fa94c22dfabc8ccd2dbe99fde74ca0c88a12f"
G0_T02_GENERATION2_AUTHORIZATION = "f69e6abd379e74d1af1c507a4a9b15395d077f90"
G0_T02_ACCEPTED_RECORD = "41868a5eff635d9f83dccaba4ad3e6e38433822c"
G0_T02_FAILED_MAIN = "608800462fbf9f3b97277484fa906a691b8b8b98"
G0_T02_RECOVERY_MAIN = "c5a488482fffb7183790f36701411d91b2a2bba0"
G0_T02_FINALIZATION = "0a8048df7197ece027287c3397783f37630ff0e6"
G0_T02_CLOSED_RECORD = "231d3d0e4756889e8fa3fc5803df6701088556e8"
G0_T02_FINAL_CLOSE_MERGE = "d0dcc837715ea29c7b08f9ef6a7212894e4098bb"
G0_T03_FAILED_MAIN = "08d6a3ea8d1898dbe47c7eaf9c82cb7adf1db68f"
G0_T03_ACCEPTED_RECORD = "85509b6dc1b156d3347b6b21ff952d8e55ac18d3"
G0_T03_CANDIDATE = "6ca1ace6af66f874eed38f644104f59bbc4009ad"
G0_T03_AUTHORIZATION = "c1e3ebacefc8839bc6f4c32f3bc2c31cc890d398"
G0_T03_BLOCKED = "3046d8bb023e169d3b64bfbe7093eee3ec52f722"
G0_T03_RECOVERY_CANDIDATE = "a0885c16582e75613bb203be3a2ecefb01637d37"
G0_T03_RECOVERY_ACCEPTED_RECORD = "0b5279b69b70b70500f22753cb6ae3a542b196c7"
G0_T03_RECOVERY_MERGE = "bea5cf840ddf45ec4425796861d8956f682ab564"
G0_T03_RECOVERY_CLOSURE = "3263cf207cecac1e3fb019df2fbd6c2a6435d5bd"
G0_T03_MERGED_MAIN = "a98dada059c91dc70714119f333d0d03ab1cb9f1"
G0_T03_FINALIZATION = "e4fd7ae620955867ac0c6914aff2c913420c3ba2"
G0_T03_CLOSED_RECORD = "cf15b25533769c7f589dd5dad275627802d9ae7d"
G0_T03_FINAL_CLOSE_MERGE = "b1544c168cf3acf9e0ce0c1c7e3785041c02e87c"
G0_T03_RECOVERED_MAIN = "02e05d1f2d68a9a1c89fda9c8636e2263fc48053"
G0_T03_PLANNING_HANDOFF = "e1d251c35bbfc128990be4f9e3d1b851a3146f12"
G0_T03_PLANNING_HEAD = "b8f04c9bbc3f86b6ef643cdd097ec7dc46c16e5b"
G0_T03_STATUS_RECONCILIATION_BASE = "c11eae14986de8bb5f387e3064680ce48d2c284b"
G0_T04_FAILED_MAIN = "11040ca0d8ea17ba1bc47641705aa95c2cba6a75"
G0_T04_CLOSURE = "bdf6fbca71b29da79801c1be7a4cdd14f103ce52"
G0_T04_ANOMALY_MAIN = "4f358cf42b9a8e0f741563425fc26cf532df98fb"
G0_T04_ANOMALY_IMPLEMENTATION = "69c045de1e80bcb90c1b5ce5a49b640e48047d32"
G0_T04_ANOMALY_CANDIDATE = "6541189bbdacc870de5691d07991b9103ee2c763"
PACKAGE_A_MANIFEST = ROOT / "governance" / "packages" / "package-a.manifest.json"
PACKAGE_A_SCHEMA = ROOT / "schemas" / "package_a_manifest.schema.json"
SCRIPT = ROOT / "scripts" / "validate_project_status.py"
SCHEMA = ROOT / "schemas" / "project_status.schema.json"
SCHEMA_CONTROL = ROOT / "schemas" / "project_status.schema-migration-control.json"
FIXTURES = ROOT / "fixtures" / "g0"
SPEC = importlib.util.spec_from_file_location("project_status_validator", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def run_validator(path: Path, repo_root: Path | None = None, schema_path: Path = SCHEMA) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT), str(path), "--schema", str(schema_path)]
    if repo_root is not None:
        command.extend(["--repo-root", str(repo_root)])
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)


def load_valid() -> dict:
    return json.loads((FIXTURES / "valid_awaiting_review.json").read_text())


def write_status(path: Path, status: dict) -> None:
    path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")


def write_digest_json(path: Path, value: dict) -> None:
    payload = {key: item for key, item in value.items() if key != "payload_sha256"}
    value["payload_sha256"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def migration_control(decision: str, authority: dict, **overrides: object) -> dict:
    if decision == "no_migration":
        control = {
            "schema_version": "schema-migration-control.v1",
            "project": "yaobizuoduo",
            "decision": decision,
            "current_revision": authority["revision"],
            "current_sha256": authority["sha256"],
        }
    else:
        control = {
            "schema_version": "schema-migration-control.v1",
            "project": "yaobizuoduo",
            "decision": "authorize_migration",
            "task_id": "G1-T01",
            "gate": "G1",
            "purpose": "project-status-schema-migration",
            "from_revision": authority["revision"],
            "from_sha256": authority["sha256"],
            "to_revision": authority["revision"] + 1,
            "to_sha256": "f" * 64,
            "compatibility_rule": "strict-current-schema-revalidation",
        }
    control.update(overrides)
    control["payload_sha256"] = VALIDATOR._payload_digest(control)
    return control


def ci(status: str = "not_established", subject: str | None = None, run: str | None = None) -> dict:
    return {
        "status": status,
        "subject_sha": subject,
        "run_id": run,
        "url": None if run is None else f"https://github.com/a/b/actions/runs/{run}",
    }


def phase_ci(status: dict, phase: str) -> dict:
    return status["evidence"][phase]["d0_ci" if phase == "finalization" else "ci"]


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
    assert "traceable approval/manifest identities" in result.stdout
    status["release"] = {"product_owner_go": True, "release_evidence_complete": True}
    write_status(path, status)
    result = run_validator(path)
    assert result.returncode == 1
    assert "unknown field" in result.stdout
    assert "required field is missing" in result.stdout


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
    status["governed_documents"].append("GOVERNANCE.md")
    path = tmp_path / "status.json"
    write_status(path, status)
    (tmp_path / "GOVERNANCE.md").write_text("- Current Gate: G9\n", encoding="utf-8")
    (tmp_path / "CURRENT_TASK.md").write_text("- Task ID: `G0-T02`\n- Gate: G9 release\n- Risk: `D2`\n- Status: `closed`\n- Status: `awaiting_review`\n- Baseline: `" + "9" * 40 + "`\n- Current Maturity: RELEASE_READY\n", encoding="utf-8")
    (tmp_path / "PROJECT_MEMORY.md").write_text("- Current Maturity: RELEASE_READY\n", encoding="utf-8")
    for name in ("AGENTS.md", "DEVELOPMENT_WORKFLOW.md", "AG_WORK_LOOP.md", "DESIGN.md"):
        (tmp_path / name).write_text(f"# {name}\n", encoding="utf-8")
    result = run_validator(path, tmp_path)
    assert result.returncode == 1
    for diagnostic in ("forbidden current-state mirror", "CURRENT_TASK task_id conflicts", "CURRENT_TASK gate conflicts", "CURRENT_TASK state conflicts", "unsupported current-state mirror", "PROJECT_MEMORY must declare historical-only authority"):
        assert diagnostic in result.stdout


def test_invalid_utf8_governed_document_is_sanitized(tmp_path: Path) -> None:
    status = load_valid()
    status["governed_documents"].append("BAD.md")
    path = tmp_path / "status.json"
    write_status(path, status)
    (tmp_path / "BAD.md").write_bytes(b"\xff\xfe")
    (tmp_path / "CURRENT_TASK.md").write_text("- Task ID: `G0-T01`\n- Gate: G0 test\n- Risk: `D0`\n- Status: `awaiting_review`\n- Baseline: `7aadae13efd45023d19bf8a280f7680667c930fa`\n", encoding="utf-8")
    (tmp_path / "PROJECT_MEMORY.md").write_text("Historical record; not the current machine-state authority.\n", encoding="utf-8")
    for name in ("AGENTS.md", "DEVELOPMENT_WORKFLOW.md", "AG_WORK_LOOP.md", "DESIGN.md"):
        (tmp_path / name).write_text(f"# {name}\n", encoding="utf-8")
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
    for name in ("AGENTS.md", "DEVELOPMENT_WORKFLOW.md", "AG_WORK_LOOP.md", "DESIGN.md"):
        (repo / name).write_text(f"# {name}\n", encoding="utf-8")


def make_delivery_repo(tmp_path: Path, gate: str = "G1", maturity: str = "OFFLINE_EVIDENCE_ACCEPTED") -> tuple[Path, dict, str, str, str]:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "remote", "add", "origin", "https://github.com/a/b.git")
    (repo / "README.md").write_text("baseline\n")
    baseline = commit(repo, "baseline")
    status = load_valid()
    status["current_gate"] = gate
    status["active_tasks"][0].update(task_id=f"{gate}-T01", state="in_progress", transition={"from": "authorized", "to": "in_progress"}, candidate_generation=1)
    status["evidence"]["authorization_baseline_sha"] = baseline
    status["evidence"]["implementation_sha"] = None
    status["evidence"]["candidate"]["local_verification"]["status"] = "pending"
    status["bootstrap_exception"] = None
    status["capability"]["maturity"] = maturity
    status["next_authorization"].update(gate=gate, task_id=f"{gate}-T02")
    write_governed(repo, status)
    commit(repo, "start task")
    (repo / "implementation.txt").write_text("implementation\n")
    implementation = commit(repo, "implementation")
    status["active_tasks"][0].update(state="awaiting_review", transition={"from": "in_progress", "to": "awaiting_review"})
    status["evidence"]["implementation_sha"] = implementation
    status["evidence"]["candidate"]["local_verification"]["status"] = "success"
    write_governed(repo, status)
    candidate = commit(repo, "candidate delivery")
    return repo, status, baseline, implementation, candidate


def clone_with_ledger_migration(tmp_path: Path) -> tuple[Path, dict]:
    repo = tmp_path / "history"
    git(tmp_path, "clone", "--quiet", str(ROOT), str(repo))
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "remote", "set-url", "origin", "https://github.com/weizhenhaihaha-arch/yaobizuoduo.git")
    git(repo, "update-ref", "refs/heads/main", "refs/remotes/origin/main")
    status = json.loads((ROOT / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    write_governed(repo, status)
    (repo / "schemas" / "project_status.schema.json").write_text(SCHEMA.read_text(encoding="utf-8"), encoding="utf-8")
    commit(repo, "install sealed transition ledger")
    return repo, status


def make_closed_repo(
    tmp_path: Path,
    gate: str = "G1",
    maturity: str = "OFFLINE_EVIDENCE_ACCEPTED",
    next_gate: str | None = None,
    close_maturity: str | None = None,
) -> tuple[Path, dict, str]:
    repo, status, _, _, candidate = make_delivery_repo(tmp_path, gate=gate, maturity=maturity)
    if next_gate is not None:
        status["next_authorization"].update(gate=next_gate, task_id=f"{next_gate}-T01")
    status["active_tasks"][0].update(state="accepted_pending_merge", transition={"from": "awaiting_review", "to": "accepted_pending_merge"})
    status["evidence"]["candidate"].update(commit_sha=candidate, ci=ci("success", candidate, "1"))
    status["review"] = {"code_security": "approve", "architecture": "clear", "reviewed_candidate_sha": candidate}
    write_governed(repo, status)
    closure = commit(repo, "closure")
    git(repo, "switch", "-c", "merge-side")
    (repo / "side.txt").write_text("side\n", encoding="utf-8")
    commit(repo, "side")
    git(repo, "switch", "main")
    git(repo, "merge", "--no-ff", "merge-side", "-m", "implementation merge")
    merged = git(repo, "rev-parse", "HEAD")
    status["active_tasks"][0].update(state="merged_verified", transition={"from": "accepted_pending_merge", "to": "merged_verified"})
    status["evidence"]["closure"].update(commit_sha=closure, ci=ci("success", closure, "2"))
    status["evidence"]["merged_main"].update(commit_sha=merged, ci=ci("success", merged, "3"))
    write_governed(repo, status)
    finalization = commit(repo, "finalization")
    status["active_tasks"][0].update(state="closed", transition={"from": "merged_verified", "to": "closed"})
    if close_maturity is not None:
        status["capability"]["maturity"] = close_maturity
    status["evidence"]["finalization"].update(commit_sha=finalization, d0_ci=ci("success", finalization, "4"))
    write_governed(repo, status)
    close_record = commit(repo, "close record")
    git(repo, "update-ref", "refs/remotes/origin/main", close_record)
    return repo, status, close_record


def handoff_status(status: dict, close_record: str, gate: str, task_id: str, maturity: str) -> dict:
    result = copy.deepcopy(status)
    result["current_gate"] = gate
    result["active_tasks"][0] = {
        "task_id": task_id, "risk": "D0", "state": "authorized",
        "transition": {"from": "closed", "to": "authorized"}, "candidate_generation": 1,
    }
    result["evidence"] = copy.deepcopy(load_valid()["evidence"])
    result["evidence"]["authorization_baseline_sha"] = close_record
    result["evidence"]["implementation_sha"] = None
    result["evidence"]["candidate"]["local_verification"]["status"] = "pending"
    result["review"] = {"code_security": "pending", "architecture": "pending", "reviewed_candidate_sha": None}
    result["bootstrap_exception"] = None
    result["capability"]["maturity"] = maturity
    result["blockers"] = []
    result["release"] = {"product_owner_approval": None, "release_manifest": None}
    result["next_authorization"] = {"gate": gate, "task_id": f"{gate}-T02", "state": "not_authorized"}
    return result


def make_blocked_reauthorization_repo(tmp_path: Path) -> tuple[Path, dict, str, str, str]:
    repo, closed, close_record = make_closed_repo(tmp_path, gate="G1")
    git(repo, "switch", "-c", "generation-1", close_record)
    (repo / "schemas").mkdir(exist_ok=True)
    (repo / "schemas" / "project_status.schema.json").write_text(SCHEMA.read_text(encoding="utf-8"), encoding="utf-8")
    generation1 = handoff_status(closed, close_record, "G1", "G1-T02", "OFFLINE_EVIDENCE_ACCEPTED")
    generation1["next_authorization"]["task_id"] = "G1-T03"
    write_governed(repo, generation1)
    commit(repo, "authorize generation 1")
    generation1["active_tasks"][0].update(state="in_progress", transition={"from": "authorized", "to": "in_progress"})
    write_governed(repo, generation1)
    commit(repo, "start generation 1")
    generation1["active_tasks"][0].update(state="blocked", transition={"from": "in_progress", "to": "blocked"})
    generation1["blockers"] = ["external authorization unavailable"]
    write_governed(repo, generation1)
    blocked = commit(repo, "block generation 1")

    git(repo, "switch", "-c", "generation-2", close_record)
    git(repo, "merge", "--no-ff", "--no-commit", blocked)
    generation2 = handoff_status(closed, close_record, "G1", "G1-T02", "OFFLINE_EVIDENCE_ACCEPTED")
    generation2["active_tasks"][0]["candidate_generation"] = 2
    generation2["next_authorization"]["task_id"] = "G1-T03"
    write_governed(repo, generation2)
    authorized = commit(repo, "authorize generation 2 from terminal block")
    return repo, generation2, close_record, blocked, authorized


def test_blocked_reauthorization_requires_exact_two_parent_generation_record(tmp_path: Path) -> None:
    repo, _, close_record, blocked, authorized = make_blocked_reauthorization_repo(tmp_path)
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout
    assert git(repo, "rev-list", "--parents", "-n", "1", authorized).split() == [authorized, close_record, blocked]
    assert git(repo, "rev-parse", "generation-1") == blocked
    assert VALIDATOR.TRANSITIONS["blocked"] == set()


@pytest.mark.parametrize("mutation", ["missing", "wrong", "swapped"])
def test_blocked_reauthorization_rejects_parent_substitution(tmp_path: Path, mutation: str) -> None:
    repo, generation2, close_record, blocked, authorized = make_blocked_reauthorization_repo(tmp_path)
    tree = git(repo, "rev-parse", f"{authorized}^{{tree}}")
    if mutation == "missing":
        forged = git(repo, "commit-tree", tree, "-p", close_record, "-m", "missing blocked parent")
    elif mutation == "wrong":
        wrong = git(repo, "rev-parse", f"{blocked}^1")
        forged = git(repo, "commit-tree", tree, "-p", close_record, "-p", wrong, "-m", "wrong blocked parent")
    else:
        forged = git(repo, "commit-tree", tree, "-p", blocked, "-p", close_record, "-m", "swapped parents")
    git(repo, "update-ref", "refs/heads/generation-2", forged)
    write_governed(repo, generation2)
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert any(
        message in result.stdout
        for message in (
            "repeated authorization must be an exact two-parent record",
            "repeated authorization must bind the exact prior-generation terminal blocked record",
            "transition.from: must equal direct first parent state",
        )
    )


def test_g0_t02_reauthorization_record_preserves_generation1_core_implementation() -> None:
    paths = [
        ".github/workflows/g0-exact-head.yml",
        "scripts/verify_exact_head_ci.py",
        "tests/test_g0_exact_head_ci.py",
    ]
    for path in paths:
        assert git(ROOT, "rev-parse", f"{G0_T02_GENERATION1_IMPLEMENTATION}:{path}") == git(
            ROOT, "rev-parse", f"{G0_T02_GENERATION2_AUTHORIZATION}:{path}"
        )
    assert git(ROOT, "rev-parse", "origin/codex/g0-t02-minimal-ci") == G0_T02_GENERATION1_BLOCKED


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


def clone_canonical_g0_merge(tmp_path: Path) -> Path:
    repo = tmp_path / "canonical-merge"
    git(tmp_path, "clone", "--quiet", str(ROOT), str(repo))
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "remote", "set-url", "origin", "https://github.com/weizhenhaihaha-arch/yaobizuoduo.git")
    git(repo, "switch", "--detach", G0_T01_CLOSE_RECORD)
    git(repo, "update-ref", "refs/heads/main", G0_T01_CLOSE_RECORD)
    git(repo, "update-ref", "refs/remotes/origin/main", G0_T01_CLOSE_RECORD)
    return repo


def clone_g0_t02_failed_main(tmp_path: Path) -> Path:
    repo = tmp_path / "g0-t02-failed-main"
    git(tmp_path, "clone", "--quiet", str(ROOT), str(repo))
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "remote", "set-url", "origin", "https://github.com/weizhenhaihaha-arch/yaobizuoduo.git")
    git(repo, "switch", "--detach", G0_T02_FAILED_MAIN)
    git(repo, "update-ref", "refs/heads/main", G0_T02_FAILED_MAIN)
    git(repo, "update-ref", "refs/remotes/origin/main", G0_T02_FAILED_MAIN)
    return repo


def clone_g0_t02_final_close(tmp_path: Path) -> Path:
    repo = tmp_path / "g0-t02-final-close"
    git(tmp_path, "clone", "--quiet", str(ROOT), str(repo))
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "remote", "set-url", "origin", "https://github.com/weizhenhaihaha-arch/yaobizuoduo.git")
    git(repo, "switch", "--detach", G0_T02_FINAL_CLOSE_MERGE)
    git(repo, "update-ref", "refs/heads/main", G0_T02_FINAL_CLOSE_MERGE)
    git(repo, "update-ref", "refs/remotes/origin/main", G0_T02_FINAL_CLOSE_MERGE)
    return repo


def clone_g0_t03_failed_main(tmp_path: Path) -> Path:
    repo = tmp_path / "g0-t03-failed-main"
    git(tmp_path, "clone", "--quiet", str(ROOT), str(repo))
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "remote", "set-url", "origin", "https://github.com/weizhenhaihaha-arch/yaobizuoduo.git")
    git(repo, "switch", "--detach", G0_T03_FAILED_MAIN)
    git(repo, "update-ref", "refs/heads/main", G0_T03_FAILED_MAIN)
    git(repo, "update-ref", "refs/remotes/origin/main", G0_T03_FAILED_MAIN)
    return repo


def clone_g0_t03_failed_recovery_merge(tmp_path: Path) -> Path:
    repo = tmp_path / "g0-t03-failed-recovery-merge"
    git(tmp_path, "clone", "--quiet", str(ROOT), str(repo))
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "remote", "set-url", "origin", "https://github.com/weizhenhaihaha-arch/yaobizuoduo.git")
    git(repo, "switch", "--detach", G0_T03_RECOVERY_MERGE)
    git(repo, "update-ref", "refs/heads/main", G0_T03_RECOVERY_MERGE)
    git(repo, "update-ref", "refs/remotes/origin/main", G0_T03_RECOVERY_MERGE)
    return repo


def clone_g0_t03_failed_final_close(tmp_path: Path) -> Path:
    repo = tmp_path / "g0-t03-failed-final-close"
    git(tmp_path, "clone", "--quiet", str(ROOT), str(repo))
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "remote", "set-url", "origin", "https://github.com/weizhenhaihaha-arch/yaobizuoduo.git")
    git(repo, "switch", "--detach", G0_T03_FINAL_CLOSE_MERGE)
    git(repo, "update-ref", "refs/heads/main", G0_T03_FINAL_CLOSE_MERGE)
    git(repo, "update-ref", "refs/remotes/origin/main", G0_T03_FINAL_CLOSE_MERGE)
    frozen = {
        "refs/remotes/origin/codex/g0-t03-main-protection": G0_T03_BLOCKED,
        "refs/remotes/origin/codex/g0-t03-merge-recovery": G0_T03_RECOVERY_ACCEPTED_RECORD,
        "refs/remotes/origin/codex/g0-t03-recovery-merge-recovery": G0_T03_RECOVERY_CLOSURE,
        "refs/remotes/origin/codex/g0-t03-finalize": G0_T03_CLOSED_RECORD,
    }
    for ref, sha in frozen.items():
        git(repo, "update-ref", ref, sha)
    return repo


def clone_g0_t03_planning_handoff(tmp_path: Path) -> Path:
    repo = tmp_path / "g0-t03-planning-handoff"
    git(tmp_path, "clone", "--quiet", str(ROOT), str(repo))
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "remote", "set-url", "origin", "https://github.com/weizhenhaihaha-arch/yaobizuoduo.git")
    git(repo, "switch", "--detach", G0_T03_PLANNING_HANDOFF)
    git(repo, "update-ref", "refs/heads/main", G0_T03_PLANNING_HANDOFF)
    git(repo, "update-ref", "refs/remotes/origin/main", G0_T03_PLANNING_HANDOFF)
    frozen = {
        "refs/remotes/origin/codex/g0-t03-main-protection": G0_T03_BLOCKED,
        "refs/remotes/origin/codex/g0-t03-merge-recovery": G0_T03_RECOVERY_ACCEPTED_RECORD,
        "refs/remotes/origin/codex/g0-t03-recovery-merge-recovery": G0_T03_RECOVERY_CLOSURE,
        "refs/remotes/origin/codex/g0-t03-finalize": G0_T03_CLOSED_RECORD,
    }
    for ref, sha in frozen.items():
        git(repo, "update-ref", ref, sha)
    return repo


def clone_g0_t04_failed_main(tmp_path: Path) -> Path:
    repo = tmp_path / "g0-t04-failed-main"
    git(tmp_path, "clone", "--quiet", str(ROOT), str(repo))
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    git(
        repo,
        "remote",
        "set-url",
        "origin",
        "https://github.com/weizhenhaihaha-arch/yaobizuoduo.git",
    )
    git(repo, "switch", "--detach", G0_T04_FAILED_MAIN)
    git(repo, "update-ref", "refs/heads/main", G0_T04_FAILED_MAIN)
    git(repo, "update-ref", "refs/remotes/origin/main", G0_T04_FAILED_MAIN)
    return repo


def install_g0_t03_frozen_refs(repo: Path) -> None:
    frozen = {
        "refs/remotes/origin/codex/g0-t03-main-protection": G0_T03_BLOCKED,
        "refs/remotes/origin/codex/g0-t03-merge-recovery": (
            G0_T03_RECOVERY_ACCEPTED_RECORD
        ),
        "refs/remotes/origin/codex/g0-t03-recovery-merge-recovery": (
            G0_T03_RECOVERY_CLOSURE
        ),
        "refs/remotes/origin/codex/g0-t03-finalize": G0_T03_CLOSED_RECORD,
    }
    for ref, sha in frozen.items():
        git(repo, "update-ref", ref, sha)


def make_g0_t04_anomaly_recovery(
    tmp_path: Path, mutation: str | None = None
) -> tuple[Path, dict, str, str]:
    repo = tmp_path / "g0-t04-anomaly-recovery"
    git(tmp_path, "clone", "--quiet", str(ROOT), str(repo))
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "remote", "set-url", "origin", "https://github.com/weizhenhaihaha-arch/yaobizuoduo.git")
    git(
        repo,
        "switch",
        "-c",
        "g0-t04-anomaly-recovery",
        G0_T04_ANOMALY_IMPLEMENTATION,
    )
    git(repo, "update-ref", "refs/heads/main", G0_T04_ANOMALY_MAIN)
    git(repo, "update-ref", "refs/remotes/origin/main", G0_T04_ANOMALY_MAIN)
    install_g0_t03_frozen_refs(repo)
    implementation = G0_T04_ANOMALY_IMPLEMENTATION

    status = VALIDATOR._g0_t04_anomaly_status(repo)
    write_status(repo / "PROJECT_STATUS.yaml", status)
    receipt = VALIDATOR._g0_t04_anomaly_receipt()
    if mutation == "receipt":
        receipt["pr22"]["push_run"] = "29998455190"
    receipt_path = repo / VALIDATOR.G0_T04_ANOMALY_RECEIPT_PATH
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
    task = status["active_tasks"][0]
    (repo / "CURRENT_TASK.md").write_text(
        "# G0-T04 anomaly recovery\n\n"
        f"- Task ID: `{task['task_id']}`\n"
        f"- Gate: {status['current_gate']} governance recovery\n"
        f"- Risk: `{task['risk']}`\n"
        f"- Status: `{task['state']}`\n"
        f"- Baseline: `{status['evidence']['authorization_baseline_sha']}`\n",
        encoding="utf-8",
    )
    (repo / "PROJECT_MEMORY.md").write_text(
        (repo / "PROJECT_MEMORY.md").read_text(encoding="utf-8")
        + "\n- PR15-PR22 anomaly recovery remains the only active G0-T04 slice.\n",
        encoding="utf-8",
    )
    (repo / "docs" / "NEXT_WORKFLOW.md").write_text(
        "# Next workflow\n\nG0-T05 and G1 remain not authorized.\n",
        encoding="utf-8",
    )
    activation = repo / VALIDATOR.PACKAGE_A_ACTIVATION_PATH
    if mutation != "activation":
        activation.unlink()
    if mutation == "ordinary":
        (repo / "ordinary.txt").write_text("scope escape\n", encoding="utf-8")
    delivery = commit(repo, "record exact G0-T04 anomaly recovery")
    return repo, status, implementation, delivery


def make_g0_t04_anomaly_seal(
    tmp_path: Path, mutation: str | None = None
) -> tuple[Path, dict, str]:
    repo = tmp_path / f"g0-t04-anomaly-seal-{mutation or 'valid'}"
    git(tmp_path, "clone", "--quiet", str(ROOT), str(repo))
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    git(
        repo,
        "remote",
        "set-url",
        "origin",
        "https://github.com/weizhenhaihaha-arch/yaobizuoduo.git",
    )
    git(repo, "switch", "-c", "g0-t04-anomaly-seal", G0_T04_ANOMALY_CANDIDATE)
    git(repo, "update-ref", "refs/heads/main", G0_T04_ANOMALY_MAIN)
    git(repo, "update-ref", "refs/remotes/origin/main", G0_T04_ANOMALY_MAIN)
    install_g0_t03_frozen_refs(repo)
    status = VALIDATOR._g0_t04_anomaly_seal_status(repo)
    write_status(repo / "PROJECT_STATUS.yaml", status)
    seal = VALIDATOR._g0_t04_anomaly_seal()
    if mutation == "receipt":
        seal["anomaly_receipt"]["payload_sha256"] = "0" * 64
        seal["payload_sha256"] = VALIDATOR._payload_digest(seal)
    elif mutation == "ci":
        seal["candidate"]["ci"]["run_id"] = "30005396034"
        seal["candidate"]["ci"]["url"] = (
            "https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/30005396034"
        )
        seal["payload_sha256"] = VALIDATOR._payload_digest(seal)
    elif mutation == "review":
        seal["review"]["architecture"]["decision"] = "watch"
        seal["payload_sha256"] = VALIDATOR._payload_digest(seal)
    seal_path = repo / VALIDATOR.G0_T04_ANOMALY_SEAL_PATH
    seal_path.parent.mkdir(parents=True, exist_ok=True)
    seal_path.write_text(json.dumps(seal, indent=2, ensure_ascii=False) + "\n")
    shutil.copy2(SCRIPT, repo / "scripts/validate_project_status.py")
    shutil.copy2(ROOT / "tests/test_g0_project_status.py", repo / "tests/test_g0_project_status.py")
    shutil.copy2(ROOT / "CURRENT_TASK.md", repo / "CURRENT_TASK.md")
    shutil.copy2(ROOT / "PROJECT_MEMORY.md", repo / "PROJECT_MEMORY.md")
    shutil.copy2(ROOT / "docs/NEXT_WORKFLOW.md", repo / "docs/NEXT_WORKFLOW.md")
    if mutation == "package":
        with (repo / "governance/packages/package-a.manifest.json").open("a") as handle:
            handle.write("\n")
    elif mutation == "activation":
        activation = repo / VALIDATOR.PACKAGE_A_ACTIVATION_PATH
        activation.parent.mkdir(parents=True, exist_ok=True)
        activation.write_text("{}\n")
    elif mutation == "allowlist":
        (repo / "forbidden-seal-change.txt").write_text("scope escape\n")
    seal_sha = commit(repo, "seal exact reviewed G0-T04 anomaly candidate")
    if mutation == "parent":
        seal_sha = git(
            repo,
            "commit-tree",
            git(repo, "rev-parse", f"{seal_sha}^{{tree}}"),
            "-p",
            G0_T04_ANOMALY_MAIN,
            "-m",
            "forge seal parent",
        )
    return repo, status, seal_sha


def make_g0_t04_recovery(
    tmp_path: Path,
    *,
    receipt_run_drift: bool = False,
    ordinary_path: bool = False,
) -> tuple[Path, dict, str]:
    repo = clone_g0_t04_failed_main(tmp_path)
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    status["active_tasks"][0]["transition"] = {
        "from": "accepted_pending_merge",
        "to": "accepted_pending_merge",
    }
    status["blockers"] = [VALIDATOR.G0_T04_RECOVERY_BLOCKER]
    write_status(repo / "PROJECT_STATUS.yaml", status)
    receipt = VALIDATOR._g0_t04_recovery_receipt()
    if receipt_run_drift:
        receipt["failed_main"]["ci"]["run_id"] = "29988167027"
        receipt["failed_main"]["ci"]["url"] = (
            "https://github.com/weizhenhaihaha-arch/yaobizuoduo/"
            "actions/runs/29988167027"
        )
        receipt["payload_sha256"] = VALIDATOR._payload_digest(receipt)
    receipt_path = repo / VALIDATOR.G0_T04_RECOVERY_RECEIPT_PATH
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    for relative in (
        "scripts/validate_project_status.py",
        "tests/test_g0_project_status.py",
    ):
        path = repo / relative
        path.write_text(
            path.read_text(encoding="utf-8") + "\n# G0-T04 bounded recovery fixture\n",
            encoding="utf-8",
        )
    if ordinary_path:
        (repo / "ordinary.txt").write_text("out of scope\n", encoding="utf-8")
    recovery = commit(repo, "record exact G0-T04 merged-main recovery")
    return repo, status, recovery


def make_g0_t03_planning_handoff_recovery(
    repo: Path,
    mutation: str | None = None,
) -> tuple[dict, str, str]:
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    git(repo, "switch", "-c", "planning-repair", G0_T03_PLANNING_HANDOFF)
    if mutation == "ordinary_docs":
        with (repo / "PROJECT_MEMORY.md").open("a", encoding="utf-8") as handle:
            handle.write("\n- ordinary docs-only merge\n")
    else:
        with (repo / "scripts" / "validate_project_status.py").open("a", encoding="utf-8") as handle:
            handle.write("\n# bounded planning-handoff bridge repair\n")
        with (repo / "tests" / "test_g0_project_status.py").open("a", encoding="utf-8") as handle:
            handle.write("\n# bounded planning-handoff bridge regression\n")
    if mutation == "status_drift":
        status["review"]["architecture"] = "watch"
        write_status(repo / "PROJECT_STATUS.yaml", status)
    elif mutation == "generation_drift":
        status["active_tasks"][0]["candidate_generation"] += 1
        write_status(repo / "PROJECT_STATUS.yaml", status)
    repair = commit(repo, "repair exact planning-handoff bridge")
    first = G0_T03_PLANNING_HANDOFF
    second = repair
    tree = git(repo, "rev-parse", f"{repair}^{{tree}}")
    if mutation == "wrong_first":
        first = G0_T03_RECOVERED_MAIN
    elif mutation == "wrong_second":
        second = G0_T03_PLANNING_HEAD
    elif mutation == "swapped":
        first, second = second, first
    elif mutation == "wrong_tree":
        tree = git(repo, "rev-parse", f"{G0_T03_PLANNING_HANDOFF}^{{tree}}")
    merged = git(
        repo,
        "commit-tree",
        tree,
        "-p",
        first,
        "-p",
        second,
        "-m",
        "merge bounded planning-handoff repair",
    )
    git(repo, "update-ref", "refs/heads/main", merged)
    git(repo, "update-ref", "refs/remotes/origin/main", merged)
    git(repo, "switch", "--detach", merged)
    return status, repair, merged


def write_g0_t03_recovery(repo: Path) -> dict:
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    status["active_tasks"][0]["transition"] = {
        "from": "accepted_pending_merge",
        "to": "accepted_pending_merge",
    }
    status["blockers"] = [VALIDATOR.G0_T03_RECOVERY_BLOCKER]
    write_status(repo / "PROJECT_STATUS.yaml", status)
    return status


def write_g0_t03_recovery_merge_recovery(repo: Path) -> dict:
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    status["blockers"] = [
        VALIDATOR.G0_T03_RECOVERY_BLOCKER,
        VALIDATOR.G0_T03_RECOVERY_MERGE_BLOCKER,
    ]
    write_status(repo / "PROJECT_STATUS.yaml", status)
    return status


def write_g0_t03_final_close_recovery(repo: Path) -> dict:
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    status["active_tasks"][0]["transition"] = {"from": "closed", "to": "closed"}
    status["blockers"] = [VALIDATOR.G0_T03_FINAL_CLOSE_BLOCKER]
    write_status(repo / "PROJECT_STATUS.yaml", status)
    return status


def make_g0_t03_final_close_recovery(
    repo: Path,
    *,
    receipt_mutation: str | None = None,
    binding_mutation: str | None = None,
    topology_mutation: str | None = None,
    status_mutation: str | None = None,
    candidate_override: str | None = None,
) -> tuple[dict, str, str, str, str]:
    if candidate_override is not None:
        git(repo, "switch", "--detach", candidate_override)
    status = write_g0_t03_final_close_recovery(repo)
    if status_mutation == "wrong_task":
        status["active_tasks"][0]["task_id"] = "G0-T04"
        write_status(repo / "PROJECT_STATUS.yaml", status)
    elif status_mutation == "wrong_generation":
        status["active_tasks"][0]["candidate_generation"] = 4
        write_status(repo / "PROJECT_STATUS.yaml", status)
    if candidate_override is None:
        (repo / "final-close-recovery-note.txt").write_text(
            "strict non-self-referential final-close recovery\n", encoding="utf-8"
        )
        candidate = commit(repo, "repair G0-T03 final-close bridge")
    else:
        candidate = candidate_override
        status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    candidate_ci = {
        "repository": "weizhenhaihaha-arch/yaobizuoduo",
        "event": "pull_request",
        "subject_sha": candidate,
        "run_id": "30000000010",
        "url": "https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/30000000010",
        "check": "G0 / exact-head",
        "status": "completed",
        "conclusion": "success",
    }
    binding = {
        "schema_version": VALIDATOR.G0_T03_FINAL_CLOSE_BINDING_VERSION,
        "project": "yaobizuoduo",
        "task_id": "G0-T03",
        "candidate_generation": 3,
        "recovery_generation": 3,
        "candidate_sha": candidate,
        "ci": dict(candidate_ci),
        "history": {
            "repair_candidate_sha": "d259f75cb13a56b7256779ad87115120c005ddec",
            "repair_candidate_run_id": "29904268309",
            "repair_acceptance_sha": G0_T03_RECOVERY_CLOSURE,
            "repair_acceptance_run_id": "29905690883",
            "merged_main_sha": G0_T03_MERGED_MAIN,
            "merged_main_run_id": "29906115287",
            "finalization_sha": G0_T03_FINALIZATION,
            "finalization_run_id": "29906677035",
            "closed_record_sha": G0_T03_CLOSED_RECORD,
            "closed_record_run_id": "29907836986",
            "blocked_record_sha": G0_T03_BLOCKED,
            "recovery_record_sha": G0_T03_RECOVERY_ACCEPTED_RECORD,
        },
        "review": {"code_security": "approve", "architecture": "clear"},
        "ruleset": {
            "id": 19526291,
            "evidence_sha256": "73aa3644a4c571c7101b0ac36547bd1be2edc306846045d2d36ad07ac86c5bb1",
        },
    }
    if binding_mutation == "wrong_candidate":
        binding["candidate_sha"] = G0_T03_CLOSED_RECORD
    elif binding_mutation == "wrong_subject":
        binding["ci"]["subject_sha"] = G0_T03_CLOSED_RECORD
    elif binding_mutation == "wrong_run":
        binding["ci"]["run_id"] = "39999999999"
        binding["ci"]["url"] = "https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/39999999999"
    elif binding_mutation == "wrong_history":
        binding["history"]["closed_record_sha"] = G0_T03_FINALIZATION
    elif binding_mutation == "wrong_review":
        binding["review"]["architecture"] = "watch"
    elif binding_mutation == "wrong_ruleset":
        binding["ruleset"]["id"] = 19526292
    binding["payload_sha256"] = VALIDATOR._payload_digest(binding)
    if binding_mutation == "wrong_digest":
        binding["payload_sha256"] = "0" * 64
    binding_path = repo / VALIDATOR.G0_T03_FINAL_CLOSE_BINDING_PATH
    binding_path.parent.mkdir(parents=True, exist_ok=True)
    binding_path.write_text(json.dumps(binding, indent=2) + "\n", encoding="utf-8")
    if binding_mutation == "extra_file":
        (repo / "forbidden-binding-change.txt").write_text("not binding only\n", encoding="utf-8")
    elif binding_mutation == "validator_change":
        with (repo / "scripts" / "validate_project_status.py").open("a", encoding="utf-8") as handle:
            handle.write("\n# forbidden B validator change\n")
    elif binding_mutation == "status_drift":
        with (repo / "PROJECT_STATUS.yaml").open("a", encoding="utf-8") as handle:
            handle.write("\n")
    elif binding_mutation == "receipt_defined":
        receipt_in_b = repo / VALIDATOR.G0_T03_FINAL_CLOSE_RECEIPT_PATH
        receipt_in_b.parent.mkdir(parents=True, exist_ok=True)
        receipt_in_b.write_text("{}\n", encoding="utf-8")
    binding_record = commit(repo, "seal exact reviewed run for G0-T03 repair candidate")
    if topology_mutation == "binding_wrong_parent":
        binding_record = git(
            repo,
            "commit-tree",
            git(repo, "rev-parse", f"{binding_record}^{{tree}}"),
            "-p",
            G0_T03_FINAL_CLOSE_MERGE,
            "-m",
            "forge run seal parent",
        )
        git(repo, "switch", "--detach", binding_record)
    elif topology_mutation == "acceptance_bypasses_binding":
        git(repo, "switch", "--detach", candidate)
    receipt = {
        "schema_version": VALIDATOR.G0_T03_FINAL_CLOSE_RECEIPT_VERSION,
        "project": "yaobizuoduo",
        "task_id": "G0-T03",
        "candidate_generation": 3,
        "recovery_generation": 3,
        "failed_merge": {
            "commit_sha": G0_T03_FINAL_CLOSE_MERGE,
            "run_id": "29909220290",
            "url": "https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/29909220290",
            "conclusion": "failure",
        },
        "history": {
            **binding["history"],
        },
        "candidate": {
            "commit_sha": candidate,
            "ci": dict(candidate_ci),
        },
        "review": dict(binding["review"]),
        "ruleset": dict(binding["ruleset"]),
    }
    if receipt_mutation == "wrong_candidate":
        receipt["candidate"]["commit_sha"] = G0_T03_CLOSED_RECORD
    elif receipt_mutation == "wrong_run":
        receipt["candidate"]["ci"]["subject_sha"] = G0_T03_CLOSED_RECORD
    elif receipt_mutation == "synchronized_run_substitution":
        receipt["candidate"]["ci"]["run_id"] = "39999999999"
        receipt["candidate"]["ci"]["url"] = (
            "https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/39999999999"
        )
    elif receipt_mutation == "nonexistent_run":
        receipt["candidate"]["ci"]["run_id"] = "999999999999"
        receipt["candidate"]["ci"]["url"] = (
            "https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/999999999999"
        )
    elif receipt_mutation == "unrelated_run":
        receipt["candidate"]["ci"]["run_id"] = "29909220290"
        receipt["candidate"]["ci"]["url"] = (
            "https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/29909220290"
        )
    elif receipt_mutation == "wrong_closure_history":
        receipt["history"]["repair_acceptance_sha"] = G0_T03_RECOVERY_ACCEPTED_RECORD
    elif receipt_mutation == "wrong_finalization_history":
        receipt["history"]["finalization_sha"] = G0_T03_CLOSED_RECORD
    elif receipt_mutation == "wrong_blocked_history":
        receipt["history"]["blocked_record_sha"] = G0_T03_RECOVERY_ACCEPTED_RECORD
    elif receipt_mutation == "wrong_review":
        receipt["review"]["code_security"] = "request_changes"
    elif receipt_mutation == "wrong_ruleset":
        receipt["ruleset"]["id"] = 19526292
    receipt["payload_sha256"] = VALIDATOR._payload_digest(receipt)
    if receipt_mutation == "wrong_digest":
        receipt["payload_sha256"] = "0" * 64
    receipt_path = repo / VALIDATOR.G0_T03_FINAL_CLOSE_RECEIPT_PATH
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    if receipt_mutation == "extra_file":
        (repo / "forbidden-acceptance-change.txt").write_text("not receipt only\n", encoding="utf-8")
    elif receipt_mutation == "binding_change":
        with binding_path.open("a", encoding="utf-8") as handle:
            handle.write("\n")
    elif receipt_mutation == "validator_change":
        with (repo / "scripts" / "validate_project_status.py").open("a", encoding="utf-8") as handle:
            handle.write("\n# forbidden A validator change\n")
    elif receipt_mutation == "status_drift":
        with (repo / "PROJECT_STATUS.yaml").open("a", encoding="utf-8") as handle:
            handle.write("\n")
    accepted_record = commit(repo, "accept exact G0-T03 final-close recovery")
    first = G0_T03_FINAL_CLOSE_MERGE
    second = accepted_record
    tree = git(repo, "rev-parse", f"{accepted_record}^{{tree}}")
    if topology_mutation == "wrong_first":
        first = G0_T03_CLOSED_RECORD
    elif topology_mutation == "wrong_second":
        second = binding_record
    elif topology_mutation == "swapped":
        first, second = second, first
    elif topology_mutation == "wrong_tree":
        tree = git(repo, "rev-parse", f"{candidate}^{{tree}}")
    merged = git(
        repo, "commit-tree", tree, "-p", first, "-p", second,
        "-m", "merge exact G0-T03 final-close recovery",
    )
    git(repo, "update-ref", "refs/heads/main", merged)
    git(repo, "update-ref", "refs/remotes/origin/main", merged)
    git(repo, "switch", "--detach", merged)
    return status, candidate, binding_record, accepted_record, merged


def test_pr10_direct_acceptance_cannot_self_attest_from_process_binding(tmp_path: Path) -> None:
    repo = clone_g0_t03_failed_final_close(tmp_path)
    candidate = "8048455a8d0d827d7f99af67716d111336df7b07"
    status, actual_candidate, _, _, merged = make_g0_t03_final_close_recovery(
        repo, candidate_override=candidate
    )
    assert actual_candidate == candidate
    schema = json.loads((repo / "schemas" / "project_status.schema.json").read_text(encoding="utf-8"))
    governed, errors = VALIDATOR._canonical_g0_t03_final_close_bridge(
        status, repo, merged, schema, require_canonical_main=True
    )
    assert governed is None
    assert errors


def make_g0_t03_recovery_closure(
    repo: Path,
    *,
    receipt_mutation: str | None = None,
    topology_mutation: str | None = None,
) -> tuple[dict, str, str, str]:
    status = write_g0_t03_recovery_merge_recovery(repo)
    (repo / "recovery-closure-note.txt").write_text(
        "strict non-self-referential recovery closure\n", encoding="utf-8"
    )
    candidate = commit(repo, "repair G0-T03 recovery closure bridge")
    receipt = {
        "schema_version": VALIDATOR.G0_T03_RECOVERY_CLOSURE_RECEIPT_VERSION,
        "project": "yaobizuoduo",
        "task_id": "G0-T03",
        "candidate_generation": 3,
        "recovery_generation": 2,
        "prior_rejected_candidate_sha": "05597ef837031bb6a4aeb6eefb21aa4cecd7ff30",
        "prior_rejected_run_id": "29900351726",
        "prior_review": {"code_security": "request_changes", "architecture": "block"},
        "candidate": {
            "commit_sha": candidate,
            "ci": {
                "repository": "weizhenhaihaha-arch/yaobizuoduo",
                "event": "pull_request",
                "subject_sha": candidate,
                "run_id": "29999999999",
                "url": "https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/29999999999",
                "check": "G0 / exact-head",
                "status": "completed",
                "conclusion": "success",
            },
        },
        "review": {"code_security": "approve", "architecture": "clear"},
        "ruleset": {
            "id": 19526291,
            "evidence_sha256": "73aa3644a4c571c7101b0ac36547bd1be2edc306846045d2d36ad07ac86c5bb1",
        },
    }
    if receipt_mutation == "wrong_candidate":
        receipt["candidate"]["commit_sha"] = G0_T03_RECOVERY_CANDIDATE
    elif receipt_mutation == "wrong_run":
        receipt["candidate"]["ci"]["subject_sha"] = G0_T03_RECOVERY_CANDIDATE
    elif receipt_mutation == "wrong_review":
        receipt["review"]["architecture"] = "watch"
    elif receipt_mutation == "wrong_ruleset":
        receipt["ruleset"]["id"] = 19526292
    receipt["payload_sha256"] = VALIDATOR._payload_digest(receipt)
    if receipt_mutation == "wrong_digest":
        receipt["payload_sha256"] = "0" * 64
    receipt_path = repo / VALIDATOR.G0_T03_RECOVERY_CLOSURE_RECEIPT_PATH
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    accepted_record = commit(repo, "accept exact G0-T03 recovery closure candidate")
    first = G0_T03_RECOVERY_MERGE
    second = accepted_record
    tree = git(repo, "rev-parse", f"{accepted_record}^{{tree}}")
    if topology_mutation == "wrong_first":
        first = G0_T03_FAILED_MAIN
    elif topology_mutation == "wrong_second":
        second = candidate
    elif topology_mutation == "swapped":
        first, second = second, first
    elif topology_mutation == "wrong_tree":
        tree = git(repo, "rev-parse", f"{candidate}^{{tree}}")
    merged = git(
        repo,
        "commit-tree",
        tree,
        "-p",
        first,
        "-p",
        second,
        "-m",
        "merge exact G0-T03 recovery closure",
    )
    git(repo, "update-ref", "refs/heads/main", merged)
    git(repo, "update-ref", "refs/remotes/origin/main", merged)
    git(repo, "switch", "--detach", merged)
    return status, candidate, accepted_record, merged


def write_g0_t02_recovery(repo: Path) -> dict:
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    status["active_tasks"][0]["transition"] = {
        "from": "accepted_pending_merge",
        "to": "accepted_pending_merge",
    }
    status["blockers"] = [VALIDATOR.G0_T02_RECOVERY_BLOCKER]
    write_status(repo / "PROJECT_STATUS.yaml", status)
    return status


def test_canonical_github_two_parent_merge_bridge_is_accepted(tmp_path: Path) -> None:
    repo = clone_canonical_g0_merge(tmp_path)
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo, repo / "schemas" / "project_status.schema.json")
    assert result.returncode == 0, result.stdout


def test_g0_t02_exact_608_parent_chain_merge_bridge_is_accepted(tmp_path: Path) -> None:
    repo = clone_g0_t02_failed_main(tmp_path)
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    schema = json.loads((repo / "schemas" / "project_status.schema.json").read_text(encoding="utf-8"))
    governed, errors = VALIDATOR._canonical_g0_merge_bridge(status, repo, G0_T02_FAILED_MAIN, schema)
    assert governed == G0_T02_ACCEPTED_RECORD
    assert errors == []
    assert run_validator(repo / "PROJECT_STATUS.yaml", repo).returncode == 0


def test_exact_g0_t03_merge_bridge_and_detached_checkout_history_are_accepted(tmp_path: Path) -> None:
    repo = clone_g0_t03_failed_main(tmp_path)
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    schema = json.loads((repo / "schemas" / "project_status.schema.json").read_text(encoding="utf-8"))
    governed, errors = VALIDATOR._canonical_g0_t03_merge_bridge(status, repo, G0_T03_FAILED_MAIN)
    assert governed == G0_T03_ACCEPTED_RECORD
    assert errors == []
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize(
    "mutation",
    ["wrong_first", "wrong_second", "swapped", "wrong_tree", "wrong_status", "wrong_candidate"],
)
def test_g0_t03_merge_bridge_rejects_identity_substitution(tmp_path: Path, mutation: str) -> None:
    repo = clone_g0_t03_failed_main(tmp_path)
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    first, second = G0_T02_CLOSED_MAIN, G0_T03_ACCEPTED_RECORD
    tree = git(repo, "rev-parse", f"{second}^{{tree}}")
    if mutation == "wrong_first":
        first = git(repo, "rev-parse", f"{first}^1")
    elif mutation == "wrong_second":
        second = G0_T03_CANDIDATE
    elif mutation == "swapped":
        first, second = second, first
    elif mutation == "wrong_tree":
        tree = git(repo, "rev-parse", f"{first}^{{tree}}")
    elif mutation == "wrong_status":
        status["active_tasks"][0]["candidate_generation"] = 4
    else:
        status["evidence"]["candidate"]["commit_sha"] = G0_T03_AUTHORIZATION
        status["review"]["reviewed_candidate_sha"] = G0_T03_AUTHORIZATION
    forged = git(repo, "commit-tree", tree, "-p", first, "-p", second, "-m", f"forged {mutation}")
    git(repo, "update-ref", "refs/heads/main", forged)
    git(repo, "update-ref", "refs/remotes/origin/main", forged)
    governed, errors = VALIDATOR._canonical_g0_t03_merge_bridge(status, repo, forged)
    assert governed is None
    assert errors or not VALIDATOR._is_g0_t03_accepted_status(status)


@pytest.mark.parametrize("mutation", ["wrong_auth_parent", "moved_blocked_ref", "fake_blocked_descendant"])
def test_g0_t03_merge_bridge_rejects_authorization_and_blocked_forgery(
    tmp_path: Path, mutation: str
) -> None:
    repo = clone_g0_t03_failed_main(tmp_path)
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    if mutation == "moved_blocked_ref":
        git(repo, "update-ref", "refs/remotes/origin/codex/g0-t03-main-protection", G0_T03_CANDIDATE)
    else:
        tree = git(repo, "rev-parse", f"{G0_T03_AUTHORIZATION}^{{tree}}")
        blocked = G0_T03_CANDIDATE if mutation == "wrong_auth_parent" else git(
            repo, "commit-tree", git(repo, "rev-parse", f"{G0_T03_BLOCKED}^{{tree}}"), "-p", G0_T03_BLOCKED, "-m", "fake blocked descendant"
        )
        forged_auth = git(repo, "commit-tree", tree, "-p", G0_T02_CLOSED_MAIN, "-p", blocked, "-m", "forged authorization")
        original = VALIDATOR.G0_T03_AUTHORIZATION_SHA
        VALIDATOR.G0_T03_AUTHORIZATION_SHA = forged_auth
        try:
            governed, errors = VALIDATOR._canonical_g0_t03_merge_bridge(status, repo, G0_T03_FAILED_MAIN)
        finally:
            VALIDATOR.G0_T03_AUTHORIZATION_SHA = original
        assert governed is None
        assert errors
        return
    governed, errors = VALIDATOR._canonical_g0_t03_merge_bridge(status, repo, G0_T03_FAILED_MAIN)
    assert governed is None
    assert errors


def test_exact_g0_t03_failed_main_recovery_record_is_accepted(tmp_path: Path) -> None:
    repo = clone_g0_t03_failed_main(tmp_path)
    write_g0_t03_recovery(repo)
    recovery = commit(repo, "record exact G0-T03 failed-main recovery")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout
    assert git(repo, "rev-parse", "refs/remotes/origin/codex/g0-t03-main-protection") == G0_T03_BLOCKED
    assert git(repo, "rev-parse", f"{G0_T03_FAILED_MAIN}^1") == G0_T02_CLOSED_MAIN
    assert git(repo, "rev-parse", f"{G0_T03_FAILED_MAIN}^2") == G0_T03_ACCEPTED_RECORD
    assert git(repo, "rev-parse", f"{G0_T03_FAILED_MAIN}^{{tree}}") == git(
        repo, "rev-parse", f"{G0_T03_ACCEPTED_RECORD}^{{tree}}"
    )
    assert git(repo, "merge-base", "--is-ancestor", recovery, "HEAD") == ""


@pytest.mark.parametrize("mutation", ["fake_run", "success_run", "wrong_subject", "wrong_task", "wrong_generation"])
def test_g0_t03_failed_main_recovery_rejects_inexact_trigger(tmp_path: Path, mutation: str) -> None:
    repo = clone_g0_t03_failed_main(tmp_path)
    status = write_g0_t03_recovery(repo)
    if mutation == "fake_run":
        status["blockers"][0] = status["blockers"][0].replace("29894526319", "29894526320")
    elif mutation == "success_run":
        status["blockers"][0] = status["blockers"][0].replace("conclusion=failure", "conclusion=success")
    elif mutation == "wrong_subject":
        status["blockers"][0] = status["blockers"][0].replace(G0_T03_FAILED_MAIN, G0_T03_ACCEPTED_RECORD)
    elif mutation == "wrong_task":
        status["active_tasks"][0]["task_id"] = "G0-T04"
        status["next_authorization"]["task_id"] = "G0-T05"
    else:
        status["active_tasks"][0]["candidate_generation"] = 4
    write_status(repo / "PROJECT_STATUS.yaml", status)
    commit(repo, f"invalid G0-T03 recovery {mutation}")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1


def test_exact_g0_t03_recovery_merge_bridge_is_accepted_before_generic_paths(tmp_path: Path) -> None:
    repo = clone_g0_t03_failed_recovery_merge(tmp_path)
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    schema = json.loads((repo / "schemas" / "project_status.schema.json").read_text(encoding="utf-8"))
    governed, errors = VALIDATOR._canonical_g0_t03_recovery_merge_bridge(
        status, repo, G0_T03_RECOVERY_MERGE
    )
    assert governed == G0_T03_RECOVERY_ACCEPTED_RECORD
    assert errors == []
    governed, errors = VALIDATOR._canonical_g0_merge_bridge(
        status, repo, G0_T03_RECOVERY_MERGE, schema
    )
    assert governed == G0_T03_RECOVERY_ACCEPTED_RECORD
    assert errors == []
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize(
    "mutation",
    ["wrong_first", "wrong_second", "swapped", "wrong_tree", "wrong_status", "wrong_task", "wrong_generation", "wrong_sha"],
)
def test_g0_t03_recovery_merge_rejects_topology_and_status_substitution(
    tmp_path: Path, mutation: str
) -> None:
    repo = clone_g0_t03_failed_recovery_merge(tmp_path)
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    first, second = G0_T03_FAILED_MAIN, G0_T03_RECOVERY_ACCEPTED_RECORD
    tree = git(repo, "rev-parse", f"{second}^{{tree}}")
    if mutation == "wrong_first":
        first = G0_T02_CLOSED_MAIN
    elif mutation == "wrong_second":
        second = G0_T03_RECOVERY_CANDIDATE
    elif mutation == "swapped":
        first, second = second, first
    elif mutation == "wrong_tree":
        tree = git(repo, "rev-parse", f"{first}^{{tree}}")
    elif mutation == "wrong_status":
        status["review"]["architecture"] = "watch"
    elif mutation == "wrong_task":
        status["active_tasks"][0]["task_id"] = "G0-T04"
    elif mutation == "wrong_generation":
        status["active_tasks"][0]["candidate_generation"] = 4
    elif mutation == "wrong_sha":
        status["evidence"]["candidate"]["commit_sha"] = G0_T03_RECOVERY_CANDIDATE
    if mutation in {"wrong_status", "wrong_task", "wrong_generation", "wrong_sha"}:
        governed, errors = VALIDATOR._canonical_g0_t03_recovery_merge_bridge(
            status, repo, G0_T03_RECOVERY_MERGE
        )
        assert governed is None
        assert errors == []
        return
    forged = git(repo, "commit-tree", tree, "-p", first, "-p", second, "-m", f"forged {mutation}")
    original = VALIDATOR.G0_T03_RECOVERY_MERGE_SHA
    VALIDATOR.G0_T03_RECOVERY_MERGE_SHA = forged
    try:
        governed, errors = VALIDATOR._canonical_g0_t03_recovery_merge_bridge(status, repo, forged)
    finally:
        VALIDATOR.G0_T03_RECOVERY_MERGE_SHA = original
    assert governed is None
    assert errors


@pytest.mark.parametrize("mutation", ["wrong_run", "success_run", "wrong_subject", "fake_blocked", "ordinary_merge"])
def test_g0_t03_recovery_merge_recovery_rejects_inexact_evidence(
    tmp_path: Path, mutation: str
) -> None:
    repo = clone_g0_t03_failed_recovery_merge(tmp_path)
    status = write_g0_t03_recovery_merge_recovery(repo)
    if mutation == "wrong_run":
        status["blockers"][1] = status["blockers"][1].replace("29898504840", "29898504841")
    elif mutation == "success_run":
        status["blockers"][1] = status["blockers"][1].replace("conclusion=failure", "conclusion=success")
    elif mutation == "wrong_subject":
        status["blockers"][1] = status["blockers"][1].replace(
            G0_T03_RECOVERY_MERGE, G0_T03_RECOVERY_ACCEPTED_RECORD
        )
    elif mutation == "fake_blocked":
        git(repo, "update-ref", "refs/remotes/origin/codex/g0-t03-main-protection", G0_T03_RECOVERY_CANDIDATE)
    else:
        tree = git(repo, "rev-parse", f"{G0_T03_RECOVERY_CANDIDATE}^{{tree}}")
        ordinary = git(
            repo,
            "commit-tree",
            tree,
            "-p",
            G0_T03_RECOVERY_MERGE,
            "-p",
            G0_T03_RECOVERY_CANDIDATE,
            "-m",
            "ordinary cross-state merge",
        )
        git(repo, "switch", "--detach", ordinary)
    write_status(repo / "PROJECT_STATUS.yaml", status)
    commit(repo, f"invalid recovery-merge evidence {mutation}")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1


def test_exact_g0_t03_recovery_merge_failure_record_is_accepted(tmp_path: Path) -> None:
    repo = clone_g0_t03_failed_recovery_merge(tmp_path)
    write_g0_t03_recovery_merge_recovery(repo)
    commit(repo, "record exact G0-T03 recovery-merge failure")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout


def test_exact_g0_t03_recovery_closure_bridge_is_accepted_before_generic_paths(
    tmp_path: Path,
) -> None:
    repo = clone_g0_t03_failed_recovery_merge(tmp_path)
    status, candidate, accepted_record, merged = make_g0_t03_recovery_closure(repo)
    schema = json.loads((repo / "schemas" / "project_status.schema.json").read_text(encoding="utf-8"))
    assert git(repo, "rev-list", "--parents", "-n", "1", accepted_record).split() == [
        accepted_record,
        candidate,
    ]
    governed, errors = VALIDATOR._canonical_g0_t03_recovery_closure_bridge(
        status, repo, merged
    )
    assert governed == accepted_record, errors
    assert errors == []
    governed, errors = VALIDATOR._canonical_g0_merge_bridge(status, repo, merged, schema)
    assert governed == accepted_record
    assert errors == []
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize(
    "mutation",
    [
        "wrong_first",
        "wrong_second",
        "swapped",
        "wrong_tree",
        "wrong_candidate",
        "wrong_run",
        "wrong_review",
        "wrong_ruleset",
        "wrong_digest",
    ],
)
def test_g0_t03_recovery_closure_bridge_rejects_identity_substitution(
    tmp_path: Path, mutation: str
) -> None:
    repo = clone_g0_t03_failed_recovery_merge(tmp_path)
    topology = mutation if mutation in {"wrong_first", "wrong_second", "swapped", "wrong_tree"} else None
    receipt = None if topology else mutation
    status, _, _, merged = make_g0_t03_recovery_closure(
        repo,
        receipt_mutation=receipt,
        topology_mutation=topology,
    )
    governed, errors = VALIDATOR._canonical_g0_t03_recovery_closure_bridge(
        status, repo, merged
    )
    assert governed is None
    assert errors


def test_exact_g0_t03_final_close_bridge_is_accepted_before_generic_paths(
    tmp_path: Path,
) -> None:
    repo = clone_g0_t03_failed_final_close(tmp_path)
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    schema = json.loads((repo / "schemas" / "project_status.schema.json").read_text(encoding="utf-8"))
    governed, errors = VALIDATOR._canonical_g0_t03_final_close_bridge(
        status, repo, G0_T03_FINAL_CLOSE_MERGE, schema, require_canonical_main=True
    )
    assert governed == G0_T03_CLOSED_RECORD
    assert errors == []
    governed, errors = VALIDATOR._canonical_g0_merge_bridge(
        status, repo, G0_T03_FINAL_CLOSE_MERGE, schema
    )
    assert governed == G0_T03_CLOSED_RECORD
    assert errors == []


def test_exact_g0_t03_final_close_failure_record_is_accepted(tmp_path: Path) -> None:
    repo = clone_g0_t03_failed_final_close(tmp_path)
    write_g0_t03_final_close_recovery(repo)
    commit(repo, "record exact G0-T03 final-close failure")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout


def test_exact_g0_t03_planning_handoff_merge_is_accepted_before_r_b_a_paths(
    tmp_path: Path,
) -> None:
    repo = clone_g0_t03_planning_handoff(tmp_path)
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    schema = json.loads((repo / "schemas" / "project_status.schema.json").read_text(encoding="utf-8"))
    governed, errors = VALIDATOR._canonical_g0_t03_planning_handoff_bridge(
        status, repo, G0_T03_PLANNING_HANDOFF, require_canonical_main=True
    )
    assert governed == G0_T03_PLANNING_HEAD, errors
    assert errors == []
    governed, errors = VALIDATOR._canonical_g0_merge_bridge(
        status, repo, G0_T03_PLANNING_HANDOFF, schema
    )
    assert governed == G0_T03_PLANNING_HEAD, errors
    assert errors == []
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout


def test_future_g0_t03_planning_handoff_two_parent_recovery_is_accepted(
    tmp_path: Path,
) -> None:
    repo = clone_g0_t03_planning_handoff(tmp_path)
    status, repair, merged = make_g0_t03_planning_handoff_recovery(repo)
    schema = json.loads((repo / "schemas" / "project_status.schema.json").read_text(encoding="utf-8"))
    assert git(repo, "rev-list", "--parents", "-n", "1", merged).split() == [
        merged,
        G0_T03_PLANNING_HANDOFF,
        repair,
    ]
    governed, errors = VALIDATOR._canonical_g0_t03_planning_handoff_bridge(
        status, repo, merged, require_canonical_main=True
    )
    assert governed == repair, errors
    assert errors == []
    governed, errors = VALIDATOR._canonical_g0_merge_bridge(status, repo, merged, schema)
    assert governed == repair, errors
    assert errors == []
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize(
    "mutation",
    [
        "wrong_first",
        "wrong_second",
        "swapped",
        "wrong_tree",
        "status_drift",
        "generation_drift",
        "ordinary_docs",
    ],
)
def test_g0_t03_planning_handoff_recovery_rejects_topology_status_and_scope_drift(
    tmp_path: Path,
    mutation: str,
) -> None:
    repo = clone_g0_t03_planning_handoff(tmp_path)
    status, _, merged = make_g0_t03_planning_handoff_recovery(repo, mutation)
    governed, errors = VALIDATOR._canonical_g0_t03_planning_handoff_bridge(
        status, repo, merged, require_canonical_main=True
    )
    assert governed is None
    if mutation not in {"status_drift", "generation_drift", "wrong_first"}:
        assert errors


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("G0_T03_PLANNING_HANDOFF_PR_RUN", "29932171251"),
        ("G0_T03_PLANNING_HANDOFF_MAIN_RUN", "29933844416"),
        ("G0_T03_RECOVERED_MAIN_RUN", "29929973217"),
        ("G0_T03_PLANNING_HANDOFF_SECOND_PARENT", G0_T03_CLOSED_RECORD),
    ],
)
def test_g0_t03_planning_handoff_rejects_ci_review_and_sha_fact_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: str,
) -> None:
    repo = clone_g0_t03_planning_handoff(tmp_path)
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    monkeypatch.setattr(VALIDATOR, field, value)
    governed, errors = VALIDATOR._canonical_g0_t03_planning_handoff_bridge(
        status, repo, G0_T03_PLANNING_HANDOFF, require_canonical_main=True
    )
    assert governed is None
    assert errors


def test_future_g0_t03_final_close_recovery_merge_and_main_validation_succeed(
    tmp_path: Path,
) -> None:
    repo = clone_g0_t03_failed_final_close(tmp_path)
    status, candidate, binding_record, accepted_record, merged = (
        make_g0_t03_final_close_recovery(repo)
    )
    schema = json.loads((repo / "schemas" / "project_status.schema.json").read_text(encoding="utf-8"))
    assert git(repo, "rev-list", "--parents", "-n", "1", accepted_record).split() == [
        accepted_record,
        binding_record,
    ]
    assert git(repo, "rev-list", "--parents", "-n", "1", binding_record).split() == [
        binding_record,
        candidate,
    ]
    governed, errors = VALIDATOR._canonical_g0_t03_final_close_bridge(
        status, repo, merged, schema, require_canonical_main=True
    )
    assert governed == accepted_record, errors
    assert errors == []
    errors = VALIDATOR.validate(
        repo / "PROJECT_STATUS.yaml", repo / "schemas" / "project_status.schema.json", repo
    )
    assert errors == []


@pytest.mark.parametrize(
    "mutation",
    [
        "wrong_first",
        "wrong_second",
        "swapped",
        "wrong_tree",
        "binding_wrong_parent",
        "acceptance_bypasses_binding",
        "wrong_task",
        "wrong_generation",
        "wrong_candidate",
        "wrong_run",
        "synchronized_run_substitution",
        "nonexistent_run",
        "unrelated_run",
        "wrong_closure_history",
        "wrong_finalization_history",
        "wrong_blocked_history",
        "wrong_review",
        "wrong_ruleset",
        "wrong_digest",
        "binding_wrong_candidate",
        "binding_wrong_subject",
        "binding_wrong_run",
        "binding_wrong_history",
        "binding_wrong_review",
        "binding_wrong_ruleset",
        "binding_wrong_digest",
        "binding_extra_file",
        "binding_validator_change",
        "binding_status_drift",
        "binding_receipt_defined",
        "acceptance_extra_file",
        "acceptance_binding_change",
        "acceptance_validator_change",
        "acceptance_status_drift",
        "ordinary_closed_merge",
    ],
)
def test_g0_t03_final_close_recovery_rejects_substitution_and_ordinary_closed_merge(
    tmp_path: Path, mutation: str
) -> None:
    repo = clone_g0_t03_failed_final_close(tmp_path)
    topology = mutation if mutation in {
        "wrong_first", "wrong_second", "swapped", "wrong_tree",
        "binding_wrong_parent", "acceptance_bypasses_binding",
    } else None
    status_mutation = mutation if mutation in {"wrong_task", "wrong_generation"} else None
    receipt = mutation if mutation in {
        "wrong_candidate", "wrong_run", "synchronized_run_substitution",
        "nonexistent_run", "unrelated_run", "wrong_closure_history",
        "wrong_finalization_history", "wrong_blocked_history", "wrong_review",
        "wrong_ruleset", "wrong_digest",
        "acceptance_extra_file",
    } else None
    binding_mutation = mutation.removeprefix("binding_") if mutation.startswith("binding_") else None
    if mutation.startswith("acceptance_"):
        receipt = mutation.removeprefix("acceptance_")
    status, candidate, binding_record, accepted_record, merged = make_g0_t03_final_close_recovery(
        repo,
        receipt_mutation=receipt,
        binding_mutation=binding_mutation,
        topology_mutation=topology,
        status_mutation=status_mutation,
    )
    if mutation == "ordinary_closed_merge":
        ordinary = git(
            repo,
            "commit-tree",
            git(repo, "rev-parse", f"{accepted_record}^{{tree}}"),
            "-p",
            G0_T03_CLOSED_RECORD,
            "-p",
            accepted_record,
            "-m",
            "ordinary closed merge must not become final-close recovery",
        )
        git(repo, "update-ref", "refs/heads/main", ordinary)
        git(repo, "update-ref", "refs/remotes/origin/main", ordinary)
        git(repo, "switch", "--detach", ordinary)
        merged = ordinary
    schema = json.loads((repo / "schemas" / "project_status.schema.json").read_text(encoding="utf-8"))
    governed, errors = VALIDATOR._canonical_g0_t03_final_close_bridge(
        status, repo, merged, schema, require_canonical_main=True
    )
    assert governed is None
    if mutation not in {"wrong_task", "wrong_generation"}:
        assert errors
    governed, generic_errors = VALIDATOR._canonical_g0_merge_bridge(
        status, repo, merged, schema, require_canonical_main=True
    )
    assert governed is None
    if mutation not in {"wrong_task", "wrong_generation"}:
        assert generic_errors


def test_g0_t03_recovery_closure_can_reach_merged_verified_and_closed_without_third_recovery(
    tmp_path: Path,
) -> None:
    repo = clone_g0_t03_failed_recovery_merge(tmp_path)
    status, _, accepted_record, merged = make_g0_t03_recovery_closure(repo)

    def exact_ci(subject: str, run_id: str) -> dict:
        return {
            "status": "success",
            "subject_sha": subject,
            "run_id": run_id,
            "url": f"https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/{run_id}",
        }

    status["active_tasks"][0].update(
        state="merged_verified",
        transition={"from": "accepted_pending_merge", "to": "merged_verified"},
    )
    status["evidence"]["closure"].update(
        commit_sha=accepted_record,
        ci=exact_ci(accepted_record, "30000000001"),
    )
    status["evidence"]["merged_main"].update(
        commit_sha=merged,
        ci=exact_ci(merged, "30000000002"),
    )
    status["blockers"] = []
    write_governed(repo, status)
    finalization = commit(repo, "finalize verified G0-T03 recovery closure")
    git(repo, "update-ref", "refs/heads/main", finalization)
    git(repo, "update-ref", "refs/remotes/origin/main", finalization)
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout

    status["active_tasks"][0].update(
        state="closed",
        transition={"from": "merged_verified", "to": "closed"},
    )
    status["evidence"]["finalization"].update(
        commit_sha=finalization,
        d0_ci=exact_ci(finalization, "30000000003"),
    )
    write_governed(repo, status)
    close_record = commit(repo, "close G0-T03 after exact recovery merge verification")
    git(repo, "update-ref", "refs/heads/main", close_record)
    git(repo, "update-ref", "refs/remotes/origin/main", close_record)
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize("mutation", ["wrong_parent", "wrong_tree", "wrong_status", "wrong_candidate"])
def test_g0_t02_merge_bridge_rejects_substitution(tmp_path: Path, mutation: str) -> None:
    repo = clone_g0_t02_failed_main(tmp_path)
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    schema = json.loads((repo / "schemas" / "project_status.schema.json").read_text(encoding="utf-8"))
    first = git(repo, "rev-parse", f"{G0_T02_FAILED_MAIN}^1")
    second = git(repo, "rev-parse", f"{G0_T02_FAILED_MAIN}^2")
    tree = git(repo, "rev-parse", f"{second}^{{tree}}")
    if mutation == "wrong_parent":
        first = git(repo, "rev-parse", f"{first}^1")
    elif mutation == "wrong_tree":
        tree = git(repo, "rev-parse", f"{first}^{{tree}}")
    elif mutation == "wrong_status":
        status["active_tasks"][0]["candidate_generation"] = 4
    else:
        status["evidence"]["candidate"]["commit_sha"] = first
        status["review"]["reviewed_candidate_sha"] = first
    forged = git(repo, "commit-tree", tree, "-p", first, "-p", second, "-m", f"forged {mutation}")
    git(repo, "update-ref", "refs/heads/main", forged)
    git(repo, "update-ref", "refs/remotes/origin/main", forged)
    governed, errors = VALIDATOR._canonical_g0_merge_bridge(status, repo, forged, schema)
    assert governed is None
    assert errors


def test_exact_failed_main_recovery_record_and_recovery_merge_are_accepted(tmp_path: Path) -> None:
    repo = clone_g0_t02_failed_main(tmp_path)
    write_g0_t02_recovery(repo)
    recovery = commit(repo, "record exact failed-main recovery")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout

    (repo / "recovery-note.txt").write_text("bounded recovery follow-up\n", encoding="utf-8")
    recovery = commit(repo, "preserve recovery state during implementation")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout

    recovery_tree = git(repo, "rev-parse", f"{recovery}^{{tree}}")
    recovery_merge = git(
        repo,
        "commit-tree",
        recovery_tree,
        "-p",
        G0_T02_FAILED_MAIN,
        "-p",
        recovery,
        "-m",
        "merge recovery record",
    )
    git(repo, "switch", "--detach", recovery_merge)
    git(repo, "update-ref", "refs/heads/main", recovery_merge)
    git(repo, "update-ref", "refs/remotes/origin/main", recovery_merge)
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout


def test_exact_g0_t02_final_close_bridge_is_accepted(tmp_path: Path) -> None:
    repo = clone_g0_t02_final_close(tmp_path)
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    schema = json.loads((repo / "schemas" / "project_status.schema.json").read_text(encoding="utf-8"))
    governed, errors = VALIDATOR._canonical_g0_merge_bridge(
        status, repo, G0_T02_FINAL_CLOSE_MERGE, schema
    )
    assert governed == G0_T02_CLOSED_RECORD
    assert errors == []
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize("mutation", ["wrong_first", "wrong_second", "wrong_tree", "swapped", "ordinary_closed", "forged_descendant"])
def test_g0_t02_final_close_bridge_rejects_parent_tree_and_lineage_substitution(
    tmp_path: Path, mutation: str
) -> None:
    repo = clone_g0_t02_final_close(tmp_path)
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    schema = json.loads((repo / "schemas" / "project_status.schema.json").read_text(encoding="utf-8"))
    first = G0_T02_RECOVERY_MAIN
    second = G0_T02_CLOSED_RECORD
    tree = git(repo, "rev-parse", f"{second}^{{tree}}")
    if mutation == "wrong_first":
        first = G0_T02_FAILED_MAIN
    elif mutation == "wrong_second":
        second = G0_T02_FINALIZATION
    elif mutation == "wrong_tree":
        tree = git(repo, "rev-parse", f"{first}^{{tree}}")
    elif mutation == "swapped":
        first, second = second, first
    else:
        git(repo, "switch", "--detach", G0_T02_RECOVERY_MAIN if mutation == "forged_descendant" else G0_T02_FINAL_CLOSE_MERGE)
        (repo / "forged.txt").write_text(f"{mutation}\n", encoding="utf-8")
        second = commit(repo, mutation)
        tree = git(repo, "rev-parse", f"{second}^{{tree}}")
        first = G0_T02_FINALIZATION if mutation == "ordinary_closed" else G0_T02_FINAL_CLOSE_MERGE
    forged = git(repo, "commit-tree", tree, "-p", first, "-p", second, "-m", f"forged {mutation}")
    git(repo, "update-ref", "refs/heads/main", forged)
    git(repo, "update-ref", "refs/remotes/origin/main", forged)
    governed, errors = VALIDATOR._canonical_g0_merge_bridge(status, repo, forged, schema)
    assert governed is None
    assert errors


@pytest.mark.parametrize("mutation", ["state", "finalization", "run"])
def test_g0_t02_final_close_status_rejects_identity_substitution(mutation: str) -> None:
    status = json.loads(git(ROOT, "show", f"{G0_T02_CLOSED_RECORD}:PROJECT_STATUS.yaml"))
    if mutation == "state":
        status["active_tasks"][0]["transition"]["from"] = "closed"
    elif mutation == "finalization":
        status["evidence"]["finalization"]["commit_sha"] = G0_T02_CLOSED_RECORD
        status["evidence"]["finalization"]["d0_ci"]["subject_sha"] = G0_T02_CLOSED_RECORD
    else:
        status["evidence"]["finalization"]["d0_ci"]["run_id"] = "29888131235"
        status["evidence"]["finalization"]["d0_ci"]["url"] = (
            "https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/29888131235"
        )
    assert not VALIDATOR._is_g0_t02_final_closed_status(status)


def test_g0_t02_final_close_requires_canonical_main(tmp_path: Path) -> None:
    repo = clone_g0_t02_final_close(tmp_path)
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    schema = json.loads((repo / "schemas" / "project_status.schema.json").read_text(encoding="utf-8"))
    git(repo, "update-ref", "refs/heads/main", G0_T02_RECOVERY_MAIN)
    git(repo, "update-ref", "refs/remotes/origin/main", G0_T02_RECOVERY_MAIN)
    governed, errors = VALIDATOR._canonical_g0_merge_bridge(
        status, repo, G0_T02_FINAL_CLOSE_MERGE, schema
    )
    assert governed is None
    assert any("local/fetched main" in error for error in errors)


def test_g0_t02_final_close_accepts_only_strict_repair_merge(tmp_path: Path) -> None:
    repo = clone_g0_t02_final_close(tmp_path)
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    schema = json.loads((repo / "schemas" / "project_status.schema.json").read_text(encoding="utf-8"))
    (repo / "repair.txt").write_text("bounded repair\n", encoding="utf-8")
    repair = commit(repo, "bounded final-close repair")
    tree = git(repo, "rev-parse", f"{repair}^{{tree}}")
    recovery_merge = git(
        repo,
        "commit-tree",
        tree,
        "-p",
        G0_T02_FINAL_CLOSE_MERGE,
        "-p",
        repair,
        "-m",
        "merge bounded final-close repair",
    )
    git(repo, "switch", "--detach", recovery_merge)
    git(repo, "update-ref", "refs/heads/main", recovery_merge)
    git(repo, "update-ref", "refs/remotes/origin/main", recovery_merge)
    governed, errors = VALIDATOR._canonical_g0_merge_bridge(
        status, repo, recovery_merge, schema
    )
    assert governed == repair
    assert errors == []
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize(
    "mutation",
    ["fake_run", "success_run", "wrong_subject", "non_main"],
)
def test_failed_main_recovery_rejects_inexact_trigger(tmp_path: Path, mutation: str) -> None:
    repo = clone_g0_t02_failed_main(tmp_path)
    status = write_g0_t02_recovery(repo)
    if mutation == "fake_run":
        status["blockers"][0] = status["blockers"][0].replace("29884710636", "29884710637")
    elif mutation == "success_run":
        status["blockers"][0] = status["blockers"][0].replace("conclusion=failure", "conclusion=success")
    elif mutation == "wrong_subject":
        status["blockers"][0] = status["blockers"][0].replace(G0_T02_FAILED_MAIN, G0_T02_ACCEPTED_RECORD)
    else:
        git(repo, "update-ref", "refs/heads/main", G0_T02_ACCEPTED_RECORD)
        git(repo, "update-ref", "refs/remotes/origin/main", G0_T02_ACCEPTED_RECORD)
    write_status(repo / "PROJECT_STATUS.yaml", status)
    commit(repo, f"invalid recovery {mutation}")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "post-merge" in result.stdout or "illegal lifecycle transition" in result.stdout


def test_ordinary_accepted_pending_merge_to_returned_remains_rejected() -> None:
    status = accepted_status()
    status["active_tasks"][0].update(
        state="returned",
        transition={"from": "accepted_pending_merge", "to": "returned"},
    )
    assert "$.active_tasks[0].transition: illegal lifecycle transition" in VALIDATOR._semantic_errors(status)


def test_canonical_merge_bridge_does_not_depend_on_remote_task_ref(tmp_path: Path) -> None:
    repo = clone_canonical_g0_merge(tmp_path)
    git(repo, "update-ref", "-d", "refs/remotes/origin/codex/g0-t01-canonical-status")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo, repo / "schemas" / "project_status.schema.json")
    assert result.returncode == 0, result.stdout


def test_malformed_two_parent_status_is_rejected_without_traceback(tmp_path: Path) -> None:
    repo, valid = clone_with_ledger_migration(tmp_path)
    git(repo, "switch", "-c", "malformed-side")
    (repo / "side.txt").write_text("side\n", encoding="utf-8")
    commit(repo, "side parent")
    git(repo, "switch", "main")
    git(repo, "merge", "--no-ff", "--no-commit", "malformed-side")
    write_status(repo / "PROJECT_STATUS.yaml", {})
    commit(repo, "malformed two-parent status")
    write_governed(repo, valid)
    commit(repo, "restore valid status")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "fails schema validation" in result.stdout
    assert "Traceback" not in result.stdout + result.stderr


@pytest.mark.parametrize("mutation", ["forged", "swapped", "unrelated", "tree"])
def test_canonical_merge_bridge_rejects_parent_or_tree_substitution(tmp_path: Path, mutation: str) -> None:
    repo = clone_canonical_g0_merge(tmp_path)
    current = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    original = current["evidence"]["merged_main"]["commit_sha"]
    assert type(original) is str
    status = json.loads(git(repo, "show", f"{original}:PROJECT_STATUS.yaml"))
    schema = json.loads(git(repo, "show", f"{original}:schemas/project_status.schema.json"))
    first = git(repo, "rev-parse", f"{original}^1")
    governed = git(repo, "rev-parse", f"{original}^2")
    candidate = status["evidence"]["candidate"]["commit_sha"]
    governed_tree = git(repo, "rev-parse", f"{governed}^{{tree}}")
    if mutation == "forged":
        substituted = git(repo, "commit-tree", governed_tree, "-p", candidate, "-m", "forged closure with matching tree")
        parents = (first, substituted)
        tree = governed_tree
    elif mutation == "swapped":
        parents = (governed, first)
        tree = governed_tree
    elif mutation == "unrelated":
        parents = (first, candidate)
        tree = governed_tree
    else:
        parents = (first, governed)
        tree = git(repo, "rev-parse", f"{first}^{{tree}}")
    forged_merge = git(repo, "commit-tree", tree, "-p", parents[0], "-p", parents[1], "-m", f"{mutation} merge bridge")
    git(repo, "update-ref", "refs/heads/main", forged_merge)
    git(repo, "update-ref", "refs/remotes/origin/main", forged_merge)
    governed_head, errors = VALIDATOR._canonical_g0_merge_bridge(status, repo, forged_merge, schema)
    assert governed_head is None
    assert errors


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
    git(repo, "update-ref", "refs/remotes/origin/main", finalization)
    assert run_validator(repo / "PROJECT_STATUS.yaml", repo).returncode == 0

    status["active_tasks"][0].update(state="closed", transition={"from": "merged_verified", "to": "closed"})
    status["evidence"]["finalization"].update(commit_sha=finalization, d0_ci=ci("success", finalization, "4"))
    write_governed(repo, status)
    close_record = commit(repo, "close record")
    git(repo, "update-ref", "refs/remotes/origin/main", close_record)
    assert run_validator(repo / "PROJECT_STATUS.yaml", repo).returncode == 0


def test_uncommitted_phase_subject_and_fabricated_object_fail(tmp_path: Path) -> None:
    repo, status, _, _, _ = make_delivery_repo(tmp_path)
    status["evidence"]["implementation_sha"] = "f" * 40
    write_governed(repo, status)
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "Git commit does not exist" in result.stdout
    assert "exact committed repository HEAD" in result.stdout
    assert "phase subject requires a clean worktree" in result.stdout


def test_direct_parent_rejects_fake_state_and_generation_jump(tmp_path: Path) -> None:
    repo, status, _, _, _ = make_delivery_repo(tmp_path)
    status["active_tasks"][0].update(state="authorized", transition={"from": "planned", "to": "authorized"}, candidate_generation=99)
    status["evidence"]["implementation_sha"] = None
    status["evidence"]["candidate"]["local_verification"]["status"] = "pending"
    write_governed(repo, status)
    commit(repo, "attacker state rewrite")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "must equal direct first parent state" in result.stdout
    assert "ordinary transition must preserve parent generation" in result.stdout


def test_returned_repair_requires_exact_parent_plus_one_generation(tmp_path: Path) -> None:
    repo, status, _, _, candidate = make_delivery_repo(tmp_path)
    status["active_tasks"][0].update(state="returned", transition={"from": "awaiting_review", "to": "returned"})
    status["evidence"]["candidate"]["commit_sha"] = candidate
    status["review"] = {"code_security": "request_changes", "architecture": "clear", "reviewed_candidate_sha": candidate}
    write_governed(repo, status)
    commit(repo, "returned")
    status["active_tasks"][0].update(state="in_progress", transition={"from": "returned", "to": "in_progress"})
    status["evidence"]["implementation_sha"] = None
    status["evidence"]["candidate"] = {"commit_sha": None, "local_verification": {"status": "pending", "subject": "delivery_head"}, "ci": ci()}
    status["review"] = {"code_security": "pending", "architecture": "pending", "reviewed_candidate_sha": None}
    write_governed(repo, status)
    commit(repo, "reused generation")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "exactly parent generation plus one" in result.stdout


def test_parent_and_phase_subject_reject_risk_and_implementation_rewrite(tmp_path: Path) -> None:
    repo, status, baseline, _, candidate = make_delivery_repo(tmp_path)
    status["current_gate"] = "G2"
    status["active_tasks"][0].update(task_id="G2-T01", state="returned", transition={"from": "awaiting_review", "to": "returned"}, risk="D2")
    status["next_authorization"].update(gate="G2", task_id="G2-T02")
    status["evidence"]["authorization_baseline_sha"] = candidate
    status["evidence"]["implementation_sha"] = baseline
    status["evidence"]["candidate"]["commit_sha"] = candidate
    status["review"] = {"code_security": "request_changes", "architecture": "clear", "reviewed_candidate_sha": candidate}
    write_governed(repo, status)
    commit(repo, "rewrite phase identity")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "immutable current_gate changed" in result.stdout
    assert "immutable task_id changed" in result.stdout
    assert "immutable risk changed" in result.stdout
    assert "immutable authorization_baseline_sha changed" in result.stdout
    assert "immutable implementation identity changed" in result.stdout
    assert "not the matching delivered candidate phase" in result.stdout


def test_bootstrap_identity_cannot_reappear_across_parent(tmp_path: Path) -> None:
    repo, status, _, _, _ = make_delivery_repo(tmp_path)
    status["bootstrap_exception"] = load_valid()["bootstrap_exception"]
    write_governed(repo, status)
    commit(repo, "reappear bootstrap")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "identity changed or reappeared" in result.stdout


def test_consumed_bootstrap_cannot_roll_back(tmp_path: Path) -> None:
    repo = tmp_path / "bootstrap"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "remote", "add", "origin", "https://github.com/a/b.git")
    status = accepted_status()
    status["bootstrap_exception"] = load_valid()["bootstrap_exception"]
    status["bootstrap_exception"].update(status="consumed", uses=1)
    status["evidence"]["candidate"]["ci"] = ci()
    write_governed(repo, status)
    commit(repo, "consumed bootstrap")
    status["active_tasks"][0].update(state="merged_verified", transition={"from": "accepted_pending_merge", "to": "merged_verified"})
    status["bootstrap_exception"].update(status="available", uses=0)
    write_governed(repo, status)
    commit(repo, "rollback bootstrap")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "consumed exception cannot roll back or disappear" in result.stdout


def test_ci_url_must_match_origin_repository_and_run_id(tmp_path: Path) -> None:
    repo, status, _, _, candidate = make_delivery_repo(tmp_path)
    status["active_tasks"][0].update(state="accepted_pending_merge", transition={"from": "awaiting_review", "to": "accepted_pending_merge"})
    status["evidence"]["candidate"]["commit_sha"] = candidate
    status["evidence"]["candidate"]["ci"] = {"status": "success", "subject_sha": candidate, "run_id": "8", "url": "https://github.com/evil/repo/actions/runs/9"}
    status["review"] = {"code_security": "approve", "architecture": "clear", "reviewed_candidate_sha": candidate}
    write_governed(repo, status)
    commit(repo, "attacker CI")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "CI URL run number must equal run_id" in result.stdout
    assert "CI URL repository must match canonical origin" in result.stdout


def test_off_main_merge_cannot_be_merged_main(tmp_path: Path) -> None:
    repo, status, _, _, candidate = make_delivery_repo(tmp_path)
    status["active_tasks"][0].update(state="accepted_pending_merge", transition={"from": "awaiting_review", "to": "accepted_pending_merge"})
    status["evidence"]["candidate"]["commit_sha"] = candidate
    status["evidence"]["candidate"]["ci"] = ci("success", candidate, "1")
    status["review"] = {"code_security": "approve", "architecture": "clear", "reviewed_candidate_sha": candidate}
    write_governed(repo, status)
    closure = commit(repo, "closure")
    git(repo, "switch", "-c", "side")
    (repo / "side.txt").write_text("side\n")
    commit(repo, "side")
    git(repo, "switch", "-c", "fake", closure)
    git(repo, "merge", "--no-ff", "side", "-m", "off-main merge")
    merged = git(repo, "rev-parse", "HEAD")
    status["active_tasks"][0].update(state="merged_verified", transition={"from": "accepted_pending_merge", "to": "merged_verified"})
    status["evidence"]["closure"].update(commit_sha=closure, ci=ci("success", closure, "2"))
    status["evidence"]["merged_main"].update(commit_sha=merged, ci=ci("success", merged, "3"))
    write_governed(repo, status)
    commit(repo, "false merged verification")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert any(message in result.stdout for message in ("authoritative remote-main first-parent chain", "local main must equal fetched origin/main", "fetched origin/main evidence is unavailable"))


def test_governed_documents_are_mandatory_unique_and_unaliased(tmp_path: Path) -> None:
    status = load_valid()
    path = tmp_path / "status.json"
    status["governed_documents"].remove("DESIGN.md")
    status["governed_documents"].append("OTHER.md")
    write_status(path, status)
    assert "mandatory canonical documents are missing" in run_validator(path).stdout
    status = load_valid()
    status["governed_documents"].append("AGENTS.md")
    write_status(path, status)
    assert "duplicate items are forbidden" in run_validator(path).stdout
    status = load_valid()
    status["governed_documents"].remove("DESIGN.md")
    status["governed_documents"].append("./DESIGN.md")
    write_status(path, status)
    result = run_validator(path)
    assert "canonical repository-relative identities" in result.stdout
    assert "mandatory canonical documents are missing" in result.stdout


def test_governed_document_symlink_alias_is_rejected(tmp_path: Path) -> None:
    repo, status, _, _, _ = make_delivery_repo(tmp_path)
    status["governed_documents"].append("DESIGN_ALIAS.md")
    (repo / "DESIGN_ALIAS.md").symlink_to("DESIGN.md")
    write_governed(repo, status)
    commit(repo, "alias governed document")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "aliased resolved document identities" in result.stdout


def test_same_gate_next_task_must_move_forward(tmp_path: Path) -> None:
    status = load_valid()
    status["current_gate"] = "G1"
    status["active_tasks"][0].update(task_id="G1-T02", state="in_progress", transition={"from": "authorized", "to": "in_progress"}, candidate_generation=1)
    status["evidence"]["implementation_sha"] = None
    status["evidence"]["candidate"]["local_verification"]["status"] = "pending"
    status["bootstrap_exception"] = None
    status["next_authorization"].update(gate="G1", task_id="G1-T01")
    path = tmp_path / "status.json"
    write_status(path, status)
    result = run_validator(path)
    assert result.returncode == 1
    assert "same-gate task sequence must move forward" in result.stdout


def test_in_progress_rejects_leftover_blockers(tmp_path: Path) -> None:
    status = load_valid()
    status["active_tasks"][0].update(state="in_progress", transition={"from": "returned", "to": "in_progress"})
    status["evidence"]["implementation_sha"] = None
    status["evidence"]["candidate"]["local_verification"]["status"] = "pending"
    status["blockers"] = ["old blocker"]
    path = tmp_path / "status.json"
    write_status(path, status)
    result = run_validator(path)
    assert result.returncode == 1
    assert "in_progress state must not retain blockers" in result.stdout


def test_legacy_self_asserted_g9_approval_and_manifest_are_rejected(tmp_path: Path) -> None:
    repo = tmp_path / "g9"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "remote", "add", "origin", "https://github.com/a/b.git")
    (repo / "README.md").write_text("baseline\n")
    baseline = commit(repo, "baseline")
    status = load_valid()
    status["current_gate"] = "G9"
    status["active_tasks"][0].update(task_id="G9-T01", state="in_progress", transition={"from": "authorized", "to": "in_progress"}, candidate_generation=1)
    status["evidence"]["authorization_baseline_sha"] = baseline
    status["evidence"]["implementation_sha"] = None
    status["evidence"]["candidate"]["local_verification"]["status"] = "pending"
    status["bootstrap_exception"] = None
    status["next_authorization"].update(gate="G9", task_id="G9-T02")
    write_governed(repo, status)
    commit(repo, "start G9")

    evidence_dir = repo / "docs" / "release"
    evidence_dir.mkdir(parents=True)
    manifest_payload = (json.dumps({"complete": True, "project": "yaobizuoduo", "release_sha": baseline, "schema_version": "release-evidence.v1"}, sort_keys=True, separators=(",", ":")) + "\n").encode()
    manifest_path = evidence_dir / "manifest.json"
    manifest_path.write_bytes(manifest_payload)
    manifest_commit = commit(repo, "release manifest")
    manifest_digest = hashlib.sha256(manifest_payload).hexdigest()
    approval_payload = (json.dumps({"decision": "go", "project": "yaobizuoduo", "release_manifest_sha256": manifest_digest, "schema_version": "product-owner-approval.v1"}, sort_keys=True, separators=(",", ":")) + "\n").encode()
    approval_path = evidence_dir / "approval.json"
    approval_path.write_bytes(approval_payload)
    implementation = commit(repo, "owner approval")
    approval_digest = hashlib.sha256(approval_payload).hexdigest()

    status["active_tasks"][0].update(state="awaiting_review", transition={"from": "in_progress", "to": "awaiting_review"})
    status["evidence"]["implementation_sha"] = implementation
    status["evidence"]["candidate"]["local_verification"]["status"] = "success"
    status["release"] = {
        "product_owner_approval": {"commit_sha": implementation, "path": "docs/release/approval.json", "sha256": approval_digest},
        "release_manifest": {"commit_sha": manifest_commit, "path": "docs/release/manifest.json", "sha256": manifest_digest},
    }
    write_governed(repo, status)
    commit(repo, "G9 delivery")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "explicit go bound to the release manifest" in result.stdout
    assert "does not prove complete immutable release evidence" in result.stdout
    status["release"]["release_manifest"]["sha256"] = "f" * 64
    write_governed(repo, status)
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "immutable artifact content does not match sha256" in result.stdout


def test_g9_release_artifacts_bind_authority_manifest_and_exact_finalization(tmp_path: Path) -> None:
    repo, status, _, _, candidate = make_delivery_repo(tmp_path, gate="G9", maturity="PAPER_VALIDATED")
    status["active_tasks"][0].update(state="accepted_pending_merge", transition={"from": "awaiting_review", "to": "accepted_pending_merge"})
    status["evidence"]["candidate"].update(commit_sha=candidate, ci=ci("success", candidate, "1"))
    status["review"] = {"code_security": "approve", "architecture": "clear", "reviewed_candidate_sha": candidate}
    write_governed(repo, status)
    closure = commit(repo, "G9 closure")
    git(repo, "switch", "-c", "release-merge")
    (repo / "release.txt").write_text("release\n", encoding="utf-8")
    commit(repo, "release merge side")
    git(repo, "switch", "main")
    git(repo, "merge", "--no-ff", "release-merge", "-m", "G9 implementation merge")
    merged = git(repo, "rev-parse", "HEAD")
    status["active_tasks"][0].update(state="merged_verified", transition={"from": "accepted_pending_merge", "to": "merged_verified"})
    status["evidence"]["closure"].update(commit_sha=closure, ci=ci("success", closure, "2"))
    status["evidence"]["merged_main"].update(commit_sha=merged, ci=ci("success", merged, "3"))
    write_governed(repo, status)
    finalization = commit(repo, "G9 finalization")

    git(repo, "switch", "-c", "release-evidence")
    evidence_dir = repo / "docs" / "release"
    evidence_dir.mkdir(parents=True)
    manifest = {
        "schema_version": "release-evidence.v1",
        "project": "yaobizuoduo",
        "release_sha": finalization,
        "evidence": [
            {"phase": "candidate", "subject_sha": candidate},
            {"phase": "closure", "subject_sha": closure},
            {"phase": "merged_main", "subject_sha": merged},
            {"phase": "finalization", "subject_sha": finalization},
        ],
    }
    manifest_payload = (json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n").encode()
    (evidence_dir / "manifest.json").write_bytes(manifest_payload)
    manifest_commit = commit(repo, "enumerated release manifest")
    manifest_digest = hashlib.sha256(manifest_payload).hexdigest()
    approval = {
        "schema_version": "product-owner-approval.v1",
        "project": "yaobizuoduo",
        "decision": "go",
        "approving_authority": "product-owner",
        "authorization_id": "AUTH-G9-20260721-001",
        "release_manifest_sha256": manifest_digest,
    }
    approval_payload = (json.dumps(approval, sort_keys=True, separators=(",", ":")) + "\n").encode()
    (evidence_dir / "approval.json").write_bytes(approval_payload)
    approval_commit = commit(repo, "durable product owner approval")
    approval_digest = hashlib.sha256(approval_payload).hexdigest()

    git(repo, "switch", "main")
    git(repo, "merge", "--no-ff", "--no-commit", "release-evidence")
    status["active_tasks"][0].update(state="closed", transition={"from": "merged_verified", "to": "closed"})
    status["evidence"]["finalization"].update(commit_sha=finalization, d0_ci=ci("success", finalization, "4"))
    status["capability"]["maturity"] = "RELEASE_READY"
    status["release"] = {
        "product_owner_approval": {"commit_sha": approval_commit, "path": "docs/release/approval.json", "sha256": approval_digest},
        "release_manifest": {"commit_sha": manifest_commit, "path": "docs/release/manifest.json", "sha256": manifest_digest},
    }
    write_governed(repo, status)
    close_record = commit(repo, "close exact G9 release")
    git(repo, "update-ref", "refs/remotes/origin/main", close_record)
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout

    status["release"]["release_manifest"]["sha256"] = "e" * 64
    write_governed(repo, status)
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "immutable artifact content does not match sha256" in result.stdout


@pytest.mark.parametrize("mutation", ["tamper", "reorder", "truncate", "rollback", "wrong_anchor"])
def test_transition_ledger_rejects_tamper_truncate_rollback_and_wrong_anchor(tmp_path: Path, mutation: str) -> None:
    repo, status = clone_with_ledger_migration(tmp_path)
    if mutation == "tamper":
        status["transition_ledger"]["first_parent_chain_sha256"] = "f" * 64
    elif mutation == "reorder":
        baseline = status["transition_ledger"]["authorization_baseline_sha"]
        anchor = status["transition_ledger"]["sealed_through_sha"]
        commits = git(repo, "rev-list", "--first-parent", f"{baseline}..{anchor}").splitlines()
        rows = [f"{sha} {git(repo, 'rev-parse', f'{sha}:PROJECT_STATUS.yaml')}" for sha in reversed(commits)]
        status["transition_ledger"]["first_parent_chain_sha256"] = hashlib.sha256(("\n".join(rows) + "\n").encode()).hexdigest()
    elif mutation == "truncate":
        status["transition_ledger"]["sealed_through_sha"] = "0900d2af59e9f0cd6971a5f24b90aed00f0a6fe5"
    elif mutation == "rollback":
        status.pop("transition_ledger")
    else:
        status["transition_ledger"]["sealed_through_sha"] = "1" * 40
    write_governed(repo, status)
    commit(repo, mutation)
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert any(message in result.stdout for message in ("sealed history identity is immutable", "history digest mismatch", "durable transition history ledger is required", "must be on the repository HEAD first-parent chain"))


def test_post_ledger_forged_intermediate_generation_cannot_be_laundered(tmp_path: Path) -> None:
    repo, valid = clone_with_ledger_migration(tmp_path)
    forged = copy.deepcopy(valid)
    forged["active_tasks"][0].update(transition={"from": "returned", "to": "in_progress"}, candidate_generation=99)
    write_governed(repo, forged)
    commit(repo, "forged intermediate generation")
    write_governed(repo, valid)
    commit(repo, "restore visible status")
    (repo / "implementation.txt").write_text("unchanged status implementation\n", encoding="utf-8")
    commit(repo, "hide forged intermediate behind same-status work")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "ordinary transition must preserve parent generation" in result.stdout or "returned repair must be exactly parent generation plus one" in result.stdout


def test_every_intermediate_parent_status_uses_exact_current_schema_types(tmp_path: Path) -> None:
    repo, valid = clone_with_ledger_migration(tmp_path)
    malformed = copy.deepcopy(valid)
    malformed["active_tasks"][0]["candidate_generation"] = "4"
    write_governed(repo, malformed)
    commit(repo, "malformed intermediate parent")
    write_governed(repo, valid)
    commit(repo, "restore status after malformed parent")
    (repo / "implementation.txt").write_text("work\n", encoding="utf-8")
    commit(repo, "move malformed parent out of direct-parent position")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "fails schema validation" in result.stdout
    assert "invalid type" in result.stdout


def test_non_in_progress_same_status_commit_is_rejected(tmp_path: Path) -> None:
    repo, status, _, _, _ = make_delivery_repo(tmp_path)
    (repo / "post-delivery.txt").write_text("silently moved candidate\n", encoding="utf-8")
    commit(repo, "same awaiting-review status")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "same-status commits are restricted" in result.stdout


def test_terminal_ci_identity_is_immutable_across_phase_transition(tmp_path: Path) -> None:
    repo, status, _, _, candidate = make_delivery_repo(tmp_path)
    status["active_tasks"][0].update(state="accepted_pending_merge", transition={"from": "awaiting_review", "to": "accepted_pending_merge"})
    status["evidence"]["candidate"]["commit_sha"] = candidate
    status["evidence"]["candidate"]["ci"] = ci("success", candidate, "1")
    status["review"] = {"code_security": "approve", "architecture": "clear", "reviewed_candidate_sha": candidate}
    write_governed(repo, status)
    commit(repo, "accepted with terminal CI")
    status["active_tasks"][0].update(state="blocked", transition={"from": "accepted_pending_merge", "to": "blocked"})
    status["blockers"] = ["test blocker"]
    status["evidence"]["candidate"]["ci"] = ci("failure", candidate, "9")
    write_governed(repo, status)
    commit(repo, "replace terminal CI")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "terminal CI evidence is immutable" in result.stdout


@pytest.mark.parametrize("phase", ["candidate", "closure", "merged_main", "finalization"])
def test_every_phase_ci_is_monotonic_and_identity_immutable(phase: str) -> None:
    parent = accepted_status()
    current = copy.deepcopy(parent)
    phase_ci(parent, phase).update(ci("pending", "2" * 40, "7"))
    phase_ci(current, phase).update(ci("success", "2" * 40, "7"))
    assert VALIDATOR._ci_continuity_errors(current, parent) == []

    phase_ci(current, phase).update(ci("success", "3" * 40, "8"))
    assert any("same immutable run" in error for error in VALIDATOR._ci_continuity_errors(current, parent))

    parent = copy.deepcopy(current)
    phase_ci(parent, phase).update(ci("success", "2" * 40, "7"))
    phase_ci(current, phase).update(ci("failure", "2" * 40, "7"))
    assert any("terminal CI evidence is immutable" in error for error in VALIDATOR._ci_continuity_errors(current, parent))


def test_governed_mandatory_path_must_be_regular_git_blob_not_symlink(tmp_path: Path) -> None:
    repo, status, _, _, _ = make_delivery_repo(tmp_path)
    (repo / "DESIGN.md").unlink()
    (repo / "DESIGN.md").symlink_to("AGENTS.md")
    commit(repo, "replace mandatory document with symlink")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "symlink path component is forbidden" in result.stdout
    assert "path must be a regular Git blob" in result.stdout


def test_closed_task_handoff_exactly_authorizes_next_card_and_clears_prior_state(tmp_path: Path) -> None:
    repo, status, close_record = make_closed_repo(tmp_path)
    git(repo, "switch", "-c", "next-task")
    status["current_gate"] = "G1"
    status["active_tasks"][0] = {
        "task_id": "G1-T02", "risk": "D0", "state": "authorized",
        "transition": {"from": "closed", "to": "authorized"}, "candidate_generation": 1,
    }
    status.pop("transition_ledger", None)
    status["evidence"] = copy.deepcopy(load_valid()["evidence"])
    status["evidence"]["authorization_baseline_sha"] = close_record
    status["evidence"]["implementation_sha"] = None
    status["evidence"]["candidate"]["local_verification"]["status"] = "pending"
    status["review"] = {"code_security": "pending", "architecture": "pending", "reviewed_candidate_sha": None}
    status["bootstrap_exception"] = None
    status["blockers"] = []
    status["next_authorization"] = {"gate": "G1", "task_id": "G1-T03", "state": "not_authorized"}
    write_governed(repo, status)
    commit(repo, "authorize exact next task")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout

    git(repo, "switch", "-c", "forged-handoff", close_record)
    status["active_tasks"][0]["task_id"] = "G1-T09"
    write_governed(repo, status)
    commit(repo, "forge handoff target")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "inter-task handoff" in result.stdout


def test_second_parent_only_merge_is_not_authoritative_merged_main(tmp_path: Path) -> None:
    repo, status, _, _, candidate = make_delivery_repo(tmp_path)
    status["active_tasks"][0].update(state="accepted_pending_merge", transition={"from": "awaiting_review", "to": "accepted_pending_merge"})
    status["evidence"]["candidate"].update(commit_sha=candidate, ci=ci("success", candidate, "1"))
    status["review"] = {"code_security": "approve", "architecture": "clear", "reviewed_candidate_sha": candidate}
    write_governed(repo, status)
    closure = commit(repo, "closure")
    git(repo, "switch", "-c", "fake-merge")
    (repo / "fake.txt").write_text("fake\n", encoding="utf-8")
    commit(repo, "fake side")
    git(repo, "switch", "-c", "fake-second", closure)
    (repo / "fake-second.txt").write_text("second\n", encoding="utf-8")
    commit(repo, "fake second side")
    git(repo, "switch", "fake-merge")
    git(repo, "merge", "--no-ff", "fake-second", "-m", "fake merge subject")
    fake_merge = git(repo, "rev-parse", "HEAD")
    git(repo, "switch", "main")
    (repo / "main.txt").write_text("main\n", encoding="utf-8")
    commit(repo, "main first-parent work")
    git(repo, "merge", "--no-ff", "fake-merge", "-m", "merge fake history as second parent")
    status["active_tasks"][0].update(state="merged_verified", transition={"from": "accepted_pending_merge", "to": "merged_verified"})
    status["evidence"]["closure"].update(commit_sha=closure, ci=ci("success", closure, "2"))
    status["evidence"]["merged_main"].update(commit_sha=fake_merge, ci=ci("success", fake_merge, "3"))
    write_governed(repo, status)
    record = commit(repo, "claim second-parent merge")
    git(repo, "update-ref", "refs/remotes/origin/main", record)
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "not on the authoritative remote-main first-parent chain" in result.stdout


def test_fresh_repository_cannot_self_seal_forged_generation_history(tmp_path: Path) -> None:
    repo = tmp_path / "fresh-seal"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "remote", "add", "origin", "https://github.com/weizhenhaihaha-arch/yaobizuoduo.git")
    (repo / "README.md").write_text("fresh baseline\n", encoding="utf-8")
    baseline = commit(repo, "fresh baseline")
    status = load_valid()
    status["current_gate"] = "G1"
    status["active_tasks"][0].update(task_id="G1-T01", state="in_progress", transition={"from": "authorized", "to": "in_progress"}, candidate_generation=1)
    status["evidence"]["authorization_baseline_sha"] = baseline
    status["evidence"]["implementation_sha"] = None
    status["evidence"]["candidate"]["local_verification"]["status"] = "pending"
    status["bootstrap_exception"] = None
    status["next_authorization"].update(gate="G1", task_id="G1-T02")
    write_governed(repo, status)
    commit(repo, "start fresh history")
    status["active_tasks"][0]["candidate_generation"] = 9
    write_governed(repo, status)
    forged_anchor = commit(repo, "forge generation jump")
    commits = git(repo, "rev-list", "--first-parent", f"{baseline}..{forged_anchor}").splitlines()
    rows = [f"{sha} {git(repo, 'rev-parse', f'{sha}:PROJECT_STATUS.yaml')}" for sha in commits]
    status["transition_ledger"] = {
        "authorization_baseline_sha": baseline,
        "sealed_through_sha": forged_anchor,
        "first_parent_chain_sha256": hashlib.sha256(("\n".join(rows) + "\n").encode()).hexdigest(),
    }
    status["active_tasks"][0]["candidate_generation"] = 1
    write_governed(repo, status)
    commit(repo, "self seal forged history")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert any(message in result.stdout for message in ("one-time authorized G0-T01 migration", "canonical ledger status requires schema authority"))


def test_post_anchor_weakened_schema_float_generation_is_fatal_after_restore(tmp_path: Path) -> None:
    repo, valid = clone_with_ledger_migration(tmp_path)
    malformed = copy.deepcopy(valid)
    malformed["active_tasks"][0]["candidate_generation"] = 4.0
    weakened = json.loads(SCHEMA.read_text(encoding="utf-8"))
    weakened["$defs"]["task"]["properties"]["candidate_generation"] = {"type": "number", "minimum": 1}
    write_governed(repo, malformed)
    write_status(repo / "schemas" / "project_status.schema.json", weakened)
    commit(repo, "weaken schema and inject floating generation")
    write_governed(repo, valid)
    (repo / "schemas" / "project_status.schema.json").write_text(SCHEMA.read_text(encoding="utf-8"), encoding="utf-8")
    commit(repo, "restore canonical status and schema")
    (repo / "implementation.txt").write_text("delivery after hidden weakened schema\n", encoding="utf-8")
    commit(repo, "move attack behind delivery")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "fails schema validation" in result.stdout
    assert "candidate_generation: invalid type" in result.stdout


def test_g5_closed_offline_to_g6_authorized_cannot_inflate_integration(tmp_path: Path) -> None:
    repo, parent, close_record = make_closed_repo(tmp_path, gate="G5", next_gate="G6")
    git(repo, "switch", "-c", "G6-task")
    status = handoff_status(parent, close_record, "G6", "G6-T01", "INTEGRATION_ACCEPTED")
    write_governed(repo, status)
    commit(repo, "inflate maturity during G6 handoff")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "inter-task handoff must preserve maturity" in result.stdout


@pytest.mark.parametrize("target_state", ["awaiting_review", "returned"])
def test_g6_pre_review_or_return_cannot_inflate_integration(tmp_path: Path, target_state: str) -> None:
    repo, status, _, _, candidate = make_delivery_repo(tmp_path, gate="G6")
    if target_state == "returned":
        status["active_tasks"][0].update(state="returned", transition={"from": "awaiting_review", "to": "returned"})
        status["evidence"]["candidate"]["commit_sha"] = candidate
        status["review"] = {"code_security": "request_changes", "architecture": "clear", "reviewed_candidate_sha": candidate}
    status["capability"]["maturity"] = "INTEGRATION_ACCEPTED"
    write_governed(repo, status)
    commit(repo, f"inflate G6 {target_state}")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "exact qualifying closed gate-exit evidence transition" in result.stdout


def test_g7_to_g8_handoff_cannot_inflate_paper_maturity(tmp_path: Path) -> None:
    repo, parent, close_record = make_closed_repo(tmp_path, gate="G7", maturity="INTEGRATION_ACCEPTED", next_gate="G8")
    git(repo, "switch", "-c", "G8-task")
    status = handoff_status(parent, close_record, "G8", "G8-T01", "PAPER_VALIDATED")
    write_governed(repo, status)
    commit(repo, "inflate paper maturity during G8 handoff")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "inter-task handoff must preserve maturity" in result.stdout


def test_maturity_rollback_is_rejected(tmp_path: Path) -> None:
    repo, status, _, _, candidate = make_delivery_repo(tmp_path, gate="G8", maturity="PAPER_VALIDATED")
    status["active_tasks"][0].update(state="returned", transition={"from": "awaiting_review", "to": "returned"})
    status["evidence"]["candidate"]["commit_sha"] = candidate
    status["review"] = {"code_security": "request_changes", "architecture": "clear", "reviewed_candidate_sha": candidate}
    status["capability"]["maturity"] = "INTEGRATION_ACCEPTED"
    write_governed(repo, status)
    commit(repo, "roll maturity backward")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "maturity rollback is forbidden" in result.stdout


@pytest.mark.parametrize(
    ("gate", "before", "after", "next_gate"),
    [
        ("G6", "OFFLINE_EVIDENCE_ACCEPTED", "INTEGRATION_ACCEPTED", "G7"),
        ("G8", "INTEGRATION_ACCEPTED", "PAPER_VALIDATED", "G9"),
    ],
)
def test_sequential_maturity_upgrade_requires_and_accepts_exact_closed_exit(
    tmp_path: Path, gate: str, before: str, after: str, next_gate: str
) -> None:
    repo, _, _ = make_closed_repo(tmp_path, gate=gate, maturity=before, next_gate=next_gate, close_maturity=after)
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout


def test_current_schema_weakening_and_generation_float_fail_content_address(tmp_path: Path) -> None:
    status = json.loads((ROOT / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    status["active_tasks"][0]["candidate_generation"] = 5.0
    weakened = json.loads(SCHEMA.read_text(encoding="utf-8"))
    weakened["$defs"]["task"]["properties"]["candidate_generation"] = {}
    status_path = tmp_path / "status.json"
    schema_path = tmp_path / "weakened-schema.json"
    write_status(status_path, status)
    write_status(schema_path, weakened)
    result = run_validator(status_path, schema_path=schema_path)
    assert result.returncode == 1
    assert "canonical schema content digest mismatch" in result.stdout
    assert "Traceback" not in result.stdout + result.stderr


def test_typed_identity_equality_distinguishes_numbers_and_booleans() -> None:
    assert not VALIDATOR._typed_equal(5, 5.0)
    assert not VALIDATOR._typed_equal(True, 1)
    assert not VALIDATOR._typed_equal({"value": [5]}, {"value": [5.0]})
    assert not VALIDATOR._typed_equal((1,), (1.0,))
    assert not VALIDATOR._typed_equal(("consumed", True), ("consumed", 1))
    assert VALIDATOR._typed_equal({"value": [5]}, {"value": [5]})


def test_invalid_post_anchor_maturity_shape_is_terminal_after_restore(tmp_path: Path) -> None:
    repo, valid = clone_with_ledger_migration(tmp_path)
    malformed = copy.deepcopy(valid)
    malformed["capability"]["maturity"] = []
    write_governed(repo, malformed)
    commit(repo, "hide invalid maturity shape")
    write_governed(repo, valid)
    commit(repo, "restore maturity shape")
    (repo / "implementation.txt").write_text("delivery after invalid maturity\n", encoding="utf-8")
    commit(repo, "move invalid maturity behind delivery")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "capability.maturity: value is not in the allowed set" in result.stdout
    assert "Traceback" not in result.stdout + result.stderr


def test_invalid_direct_parent_schema_is_terminal_before_continuity(tmp_path: Path) -> None:
    repo, valid, _, _, _ = make_delivery_repo(tmp_path)
    malformed = copy.deepcopy(valid)
    malformed["active_tasks"][0]["candidate_generation"] = []
    write_governed(repo, malformed)
    commit(repo, "invalid direct parent")
    write_governed(repo, valid)
    commit(repo, "valid child of invalid parent")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1
    assert "candidate_generation: invalid type" in result.stdout
    assert "Traceback" not in result.stdout + result.stderr


def test_schema_digest_and_revision_rollback_fail_closed(tmp_path: Path) -> None:
    status = json.loads((ROOT / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    authority = status["schema_authority"]
    authority["revision"] = 1
    authority["sha256"] = authority["migration"]["from_sha256"]
    authority["migration"]["from_revision"] = 1
    authority["migration"]["to_revision"] = 1
    authority["migration"]["to_sha256"] = authority["sha256"]
    path = tmp_path / "rollback.json"
    write_status(path, status)
    result = run_validator(path)
    assert result.returncode == 1
    assert "content digest mismatch" in result.stdout
    assert "revision must advance exactly one step" in result.stdout


def test_unauthorized_schema_migration_is_rejected(tmp_path: Path) -> None:
    repo, status = clone_with_ledger_migration(tmp_path)
    parent_sha = git(repo, "rev-parse", "HEAD")
    schema_path = repo / "schemas" / "project_status.schema.json"
    changed_schema = json.loads(schema_path.read_text(encoding="utf-8"))
    changed_schema["$comment"] = "backward-compatible test migration"
    write_status(schema_path, changed_schema)
    new_digest = hashlib.sha256(schema_path.read_bytes()).hexdigest()
    old_authority = copy.deepcopy(status["schema_authority"])
    status["schema_authority"] = {
        "revision": 2,
        "sha256": new_digest,
        "migration": {
            "from_revision": 1,
            "from_sha256": old_authority["sha256"],
            "to_revision": 2,
            "to_sha256": new_digest,
            "authorization_sha": parent_sha,
            "compatibility_rule": "strict-current-schema-revalidation",
            "preauthority_history_sha256": None,
        },
    }
    write_governed(repo, status)
    commit(repo, "unauthorized in-progress schema migration")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo, schema_path)
    assert result.returncode == 1
    assert "explicit no-migration decision must bind current schema authority" in result.stdout


def test_committed_schema_weakening_cannot_be_hidden_by_restore(tmp_path: Path) -> None:
    repo, valid = clone_with_ledger_migration(tmp_path)
    schema_path = repo / "schemas" / "project_status.schema.json"
    weakened = json.loads(schema_path.read_text(encoding="utf-8"))
    weakened["$defs"]["task"]["properties"]["candidate_generation"] = {}
    write_status(schema_path, weakened)
    commit(repo, "commit weakened schema without authority change")
    schema_path.write_text(SCHEMA.read_text(encoding="utf-8"), encoding="utf-8")
    write_governed(repo, valid)
    commit(repo, "restore schema bytes")
    (repo / "implementation.txt").write_text("delivery after hidden schema weakening\n", encoding="utf-8")
    commit(repo, "move schema weakening behind delivery")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo, schema_path)
    assert result.returncode == 1
    assert "schema bytes do not match its authority digest" in result.stdout


def test_unchanged_content_addressed_schema_remains_valid(tmp_path: Path) -> None:
    repo = tmp_path / "pinned-in-progress"
    git(tmp_path, "clone", "--quiet", str(ROOT), str(repo))
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "remote", "set-url", "origin", "https://github.com/weizhenhaihaha-arch/yaobizuoduo.git")
    git(repo, "switch", "-c", "pinned", VALIDATOR.SCHEMA_CONTROL_BOOTSTRAP_PARENT)
    git(repo, "update-ref", "refs/heads/main", "refs/remotes/origin/main")
    (repo / "schemas" / SCHEMA_CONTROL.name).write_text(SCHEMA_CONTROL.read_text(encoding="utf-8"), encoding="utf-8")
    commit(repo, "install explicit no-migration control")
    (repo / "implementation.txt").write_text("ordinary work with unchanged schema\n", encoding="utf-8")
    commit(repo, "unchanged schema work")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo, repo / "schemas" / "project_status.schema.json")
    assert result.returncode == 0, result.stdout


def test_fresh_clone_of_exact_head_remains_valid(tmp_path: Path) -> None:
    repo = tmp_path / "exact-head"
    git(tmp_path, "clone", "--quiet", str(ROOT), str(repo))
    git(repo, "remote", "set-url", "origin", "https://github.com/weizhenhaihaha-arch/yaobizuoduo.git")
    git(repo, "update-ref", "refs/heads/main", "refs/remotes/origin/main")
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo, repo / "schemas" / "project_status.schema.json")
    assert result.returncode == 0, result.stdout


def make_prior_bound_schema_migration(tmp_path: Path, corrupt_digest: bool = False) -> tuple[Path, dict, dict, str, str]:
    repo = tmp_path / "prior-bound"
    repo.mkdir(parents=True)
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "remote", "add", "origin", "https://github.com/weizhenhaihaha-arch/yaobizuoduo.git")
    (repo / "schemas").mkdir()
    schema_path = repo / "schemas" / "project_status.schema.json"
    schema_path.write_text(SCHEMA.read_text(encoding="utf-8"), encoding="utf-8")
    parent = json.loads((ROOT / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    parent["active_tasks"][0].update(state="closed", transition={"from": "merged_verified", "to": "closed"})
    write_status(repo / "PROJECT_STATUS.yaml", parent)
    write_status(repo / VALIDATOR.SCHEMA_CONTROL_PATH, migration_control("no_migration", parent["schema_authority"]))
    main_sha = commit(repo, "authoritative closed main")
    git(repo, "update-ref", "refs/remotes/origin/main", main_sha)

    changed_schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    changed_schema["$comment"] = "prior-authorized compatible migration"
    target_bytes = (json.dumps(changed_schema, indent=2) + "\n").encode()
    target_digest = hashlib.sha256(target_bytes).hexdigest()
    authorized = copy.deepcopy(parent)
    authorized["current_gate"] = "G1"
    authorized["active_tasks"][0].update(task_id="G1-T01", state="authorized", transition={"from": "closed", "to": "authorized"}, candidate_generation=1)
    authorized["evidence"]["authorization_baseline_sha"] = main_sha
    auth_control = migration_control("authorize_migration", parent["schema_authority"], to_sha256=target_digest)
    if corrupt_digest:
        auth_control["payload_sha256"] = "0" * 64
    write_status(repo / "PROJECT_STATUS.yaml", authorized)
    write_status(repo / VALIDATOR.SCHEMA_CONTROL_PATH, auth_control)
    authorization_sha = commit(repo, "bind exact future schema migration")

    current = copy.deepcopy(authorized)
    current["active_tasks"][0].update(state="in_progress", transition={"from": "authorized", "to": "in_progress"})
    old_digest = parent["schema_authority"]["sha256"]
    current["schema_authority"] = {
        "revision": 2,
        "sha256": target_digest,
        "migration": {
            "from_revision": 1,
            "from_sha256": old_digest,
            "to_revision": 2,
            "to_sha256": target_digest,
            "authorization_sha": authorization_sha,
            "compatibility_rule": "strict-current-schema-revalidation",
            "preauthority_history_sha256": None,
        },
    }
    schema_path.write_bytes(target_bytes)
    write_status(repo / "PROJECT_STATUS.yaml", current)
    write_status(repo / VALIDATOR.SCHEMA_CONTROL_PATH, migration_control("no_migration", current["schema_authority"]))
    migration_sha = commit(repo, "consume prior schema migration authorization")
    return repo, authorized, current, authorization_sha, migration_sha


def test_future_schema_cannot_self_authorize_from_generic_closed_parent(tmp_path: Path) -> None:
    repo, authorized, current, authorization_sha, migration_sha = make_prior_bound_schema_migration(tmp_path)
    closed = copy.deepcopy(authorized)
    closed["active_tasks"][0].update(state="closed", transition={"from": "merged_verified", "to": "closed"})
    write_status(repo / VALIDATOR.SCHEMA_CONTROL_PATH, migration_control("no_migration", closed["schema_authority"]))
    assert VALIDATOR._schema_authority_continuity_errors(current, closed, authorization_sha, repo, migration_sha) != []


def test_valid_prior_bound_schema_migration_is_accepted_on_pre_review_task_branch(tmp_path: Path) -> None:
    repo, authorized, current, authorization_sha, migration_sha = make_prior_bound_schema_migration(tmp_path)
    assert git(repo, "rev-parse", "refs/remotes/origin/main") != migration_sha
    assert VALIDATOR._schema_authority_continuity_errors(current, authorized, authorization_sha, repo, migration_sha) == []


def test_schema_authorization_digest_mismatch_and_reuse_fail_closed(tmp_path: Path) -> None:
    bad_repo, authorized, current, authorization_sha, migration_sha = make_prior_bound_schema_migration(tmp_path / "bad", corrupt_digest=True)
    assert VALIDATOR._schema_authority_continuity_errors(current, authorized, authorization_sha, bad_repo, migration_sha) != []
    good_repo, _, _, good_authorization, good_migration = make_prior_bound_schema_migration(tmp_path / "good")
    assert not VALIDATOR._schema_authorization_reused(good_repo, good_migration, good_authorization)


def test_schema_authorization_reuse_on_sibling_ref_is_rejected(tmp_path: Path) -> None:
    repo, authorized, current, authorization_sha, migration_sha = make_prior_bound_schema_migration(tmp_path)
    schema_text = git(repo, "show", f"{migration_sha}:schemas/project_status.schema.json") + "\n"
    git(repo, "switch", "-c", "sibling-consumer", authorization_sha)
    (repo / "schemas" / "project_status.schema.json").write_text(schema_text, encoding="utf-8")
    write_status(repo / "PROJECT_STATUS.yaml", current)
    write_status(repo / VALIDATOR.SCHEMA_CONTROL_PATH, migration_control("no_migration", current["schema_authority"]))
    sibling_sha = commit(repo, "consume same authorization on sibling ref")
    errors = VALIDATOR._schema_authority_continuity_errors(current, authorized, authorization_sha, repo, sibling_sha)
    assert "$.schema_authority: migration authorization must have exactly one repository-visible consumer" in errors


def test_schema_authorization_reuse_reachable_only_from_tag_is_rejected(tmp_path: Path) -> None:
    repo, authorized, current, authorization_sha, migration_sha = make_prior_bound_schema_migration(tmp_path)
    schema_text = git(repo, "show", f"{migration_sha}:schemas/project_status.schema.json") + "\n"
    git(repo, "switch", "-c", "temporary-sibling", authorization_sha)
    (repo / "schemas" / "project_status.schema.json").write_text(schema_text, encoding="utf-8")
    write_status(repo / "PROJECT_STATUS.yaml", current)
    write_status(repo / VALIDATOR.SCHEMA_CONTROL_PATH, migration_control("no_migration", current["schema_authority"]))
    sibling_sha = commit(repo, "consume authorization retained only by tag")
    git(repo, "tag", "tag-only-consumer", sibling_sha)
    git(repo, "switch", "main")
    git(repo, "branch", "-D", "temporary-sibling")
    errors = VALIDATOR._schema_authority_continuity_errors(current, authorized, authorization_sha, repo, migration_sha)
    assert "$.schema_authority: migration authorization must have exactly one repository-visible consumer" in errors


def test_tag_visible_migration_shaped_root_commit_fails_closed_without_traceback(tmp_path: Path) -> None:
    repo, _, _, authorization_sha, migration_sha = make_prior_bound_schema_migration(tmp_path)
    tree = git(repo, "rev-parse", f"{migration_sha}^{{tree}}")
    root_sha = git(repo, "commit-tree", tree, "-m", "parentless migration-shaped root")
    git(repo, "tag", "parentless-migration", root_sha)
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo, repo / "schemas" / "project_status.schema.json")
    assert result.returncode == 1
    assert "repository-visible migration consumption set is unavailable" in result.stdout
    assert "Traceback" not in result.stdout + result.stderr
    assert VALIDATOR._schema_migration_consumers(repo, authorization_sha) is None


def test_final_schema_migration_state_rejects_consumer_off_origin_main(tmp_path: Path) -> None:
    repo, _, current, _, migration_sha = make_prior_bound_schema_migration(tmp_path)
    final_status = copy.deepcopy(current)
    final_status["active_tasks"][0].update(state="merged_verified", transition={"from": "accepted_pending_merge", "to": "merged_verified"})
    assert git(repo, "rev-parse", "refs/remotes/origin/main") != migration_sha
    errors = VALIDATOR._schema_migration_final_route_errors(final_status, repo)
    assert "$.schema_authority: final migration consumption must be on canonical origin/main first-parent history" in errors


def test_higher_schema_revision_cannot_reuse_earlier_digest(tmp_path: Path) -> None:
    repo, _, current, _, migration_sha = make_prior_bound_schema_migration(tmp_path)
    rollback = copy.deepcopy(current)
    first_digest = current["schema_authority"]["migration"]["from_sha256"]
    rollback["schema_authority"] = {
        "revision": 3,
        "sha256": first_digest,
        "migration": {
            "from_revision": 2,
            "from_sha256": current["schema_authority"]["sha256"],
            "to_revision": 3,
            "to_sha256": first_digest,
            "authorization_sha": migration_sha,
            "compatibility_rule": "strict-current-schema-revalidation",
            "preauthority_history_sha256": None,
        },
    }
    write_status(repo / "PROJECT_STATUS.yaml", rollback)
    rollback_sha = commit(repo, "attempt higher-revision schema digest rollback")
    assert "$.schema_authority: higher revision cannot reuse an earlier schema digest" in VALIDATOR._schema_digest_history_errors(repo, rollback_sha)


def test_bootstrap_and_ci_tuple_identities_reject_bool_integer_aliases() -> None:
    parent = load_valid()
    parent["active_tasks"][0].update(state="in_progress", transition={"from": "authorized", "to": "in_progress"})
    child = copy.deepcopy(parent)
    child["bootstrap_exception"]["uses"] = True
    assert "$.bootstrap_exception.uses: continuity requires exact integers" in VALIDATOR._parent_status_errors(child, parent, "1" * 40)

    previous_ci = copy.deepcopy(parent)
    current_ci = copy.deepcopy(parent)
    for status, run_id in ((previous_ci, 1), (current_ci, True)):
        status["evidence"]["candidate"]["ci"] = {"status": "pending", "subject_sha": "2" * 40, "run_id": run_id, "url": "https://github.com/a/b/actions/runs/1"}
    errors = VALIDATOR._ci_continuity_errors(current_ci, previous_ci)
    assert "pending CI may only become terminal for the same immutable run" in "\n".join(errors)


def test_generation_continuity_rejects_float_and_bool_identities() -> None:
    parent = load_valid()
    parent["active_tasks"][0].update(state="in_progress", transition={"from": "authorized", "to": "in_progress"}, candidate_generation=1)
    for forged in (1.0, True):
        child = copy.deepcopy(parent)
        child["active_tasks"][0]["candidate_generation"] = forged
        errors = VALIDATOR._parent_status_errors(child, parent, "1" * 40)
        assert "$.active_tasks[0].candidate_generation: continuity requires exact integers" in errors


def make_g0_t03_status_reconciliation(
    tmp_path: Path, mutation: str | None = None
) -> tuple[Path, dict, str]:
    repo = tmp_path / f"g0-t03-status-reconciliation-{mutation or 'exact'}"
    git(tmp_path, "clone", "--quiet", str(ROOT), str(repo))
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "remote", "set-url", "origin", "https://github.com/weizhenhaihaha-arch/yaobizuoduo.git")
    git(repo, "switch", "-c", "status-reconciliation", G0_T03_STATUS_RECONCILIATION_BASE)
    git(repo, "update-ref", "refs/heads/main", G0_T03_STATUS_RECONCILIATION_BASE)
    git(repo, "update-ref", "refs/remotes/origin/main", G0_T03_STATUS_RECONCILIATION_BASE)

    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    status["blockers"] = []
    if mutation == "generation":
        status["active_tasks"][0]["candidate_generation"] = 4
    elif mutation == "maturity":
        status["capability"]["maturity"] = "INTEGRATION_ACCEPTED"
    elif mutation == "next_authorization":
        status["next_authorization"]["state"] = "authorized"
    write_status(repo / "PROJECT_STATUS.yaml", status)

    shutil.copy2(SCRIPT, repo / "scripts" / "validate_project_status.py")
    with (repo / "tests" / "test_g0_project_status.py").open("a", encoding="utf-8") as handle:
        handle.write("\n# post-recovery status reconciliation adversarial regression\n")
    evidence_path = repo / VALIDATOR.G0_T03_STATUS_RECONCILIATION_PATH
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence = json.loads(
        (ROOT / VALIDATOR.G0_T03_STATUS_RECONCILIATION_PATH).read_text(encoding="utf-8")
    )
    if mutation == "failed_run":
        evidence["historical_failure"]["run_id"] = "29909220291"
    elif mutation == "recovered_main":
        evidence["recovered_main"]["commit_sha"] = G0_T03_FINAL_CLOSE_MERGE
    elif mutation == "recovered_run":
        evidence["recovered_main"]["push_run_id"] = "29929973217"
    elif mutation == "review":
        evidence["recovered_main"]["code_security"] = "request_changes"
    elif mutation == "planning_main":
        evidence["planning_recovery_main"]["commit_sha"] = G0_T03_PLANNING_HANDOFF
    elif mutation == "planning_run":
        evidence["planning_recovery_main"]["push_run_id"] = "29956605324"
    elif mutation == "ruleset":
        evidence["ruleset"]["id"] = 19526292
    elif mutation == "history_retention":
        evidence["historical_failure"]["retention"] = "discarded"
    elif mutation == "blocker":
        evidence["blocker_reconciliation"]["removed_from_current"] = []
    elif mutation == "unknown_field":
        evidence["unexpected"] = True
    write_digest_json(evidence_path, evidence)
    if mutation == "extra_path":
        (repo / "docs" / "NEXT_WORKFLOW.md").write_text("scope drift\n", encoding="utf-8")
    candidate = commit(repo, "reconcile exact G0-T03 post-recovery status")
    return repo, status, candidate


def test_g0_t03_status_reconciliation_candidate_and_future_merge_validate(
    tmp_path: Path,
) -> None:
    repo, status, candidate = make_g0_t03_status_reconciliation(tmp_path)
    assert run_validator(repo / "PROJECT_STATUS.yaml", repo).returncode == 0
    tree = git(repo, "rev-parse", f"{candidate}^{{tree}}")
    merged = git(
        repo,
        "commit-tree",
        tree,
        "-p",
        G0_T03_STATUS_RECONCILIATION_BASE,
        "-p",
        candidate,
        "-m",
        "merge exact G0-T03 post-recovery status reconciliation",
    )
    git(repo, "update-ref", "refs/heads/main", merged)
    git(repo, "update-ref", "refs/remotes/origin/main", merged)
    git(repo, "switch", "--detach", merged)
    governed, errors = VALIDATOR._canonical_g0_t03_status_reconciliation_bridge(
        status, repo, merged, require_canonical_main=True
    )
    assert governed == candidate
    assert errors == []
    assert run_validator(repo / "PROJECT_STATUS.yaml", repo).returncode == 0


@pytest.mark.parametrize(
    "mutation",
    [
        "failed_run",
        "recovered_main",
        "recovered_run",
        "review",
        "planning_main",
        "planning_run",
        "ruleset",
        "history_retention",
        "blocker",
        "unknown_field",
        "extra_path",
        "generation",
        "maturity",
        "next_authorization",
    ],
)
def test_g0_t03_status_reconciliation_rejects_identity_and_scope_drift(
    tmp_path: Path, mutation: str
) -> None:
    repo, status, candidate = make_g0_t03_status_reconciliation(tmp_path, mutation)
    errors = VALIDATOR._g0_t03_status_reconciliation_evidence_errors(repo, candidate)
    errors.extend(
        VALIDATOR._g0_t03_status_reconciliation_changed_path_errors(repo, candidate)
    )
    if mutation in {"generation", "maturity", "next_authorization"}:
        assert not VALIDATOR._is_g0_t03_status_reconciled(status)
    else:
        assert errors


def test_g0_t03_status_reconciliation_rejects_ordinary_descendant_and_merge_drift(
    tmp_path: Path,
) -> None:
    repo, status, candidate = make_g0_t03_status_reconciliation(tmp_path)
    with (repo / "PROJECT_MEMORY.md").open("a", encoding="utf-8") as handle:
        handle.write("\n- ordinary descendant\n")
    descendant = commit(repo, "ordinary descendant")
    assert run_validator(repo / "PROJECT_STATUS.yaml", repo).returncode == 1

    candidate_tree = git(repo, "rev-parse", f"{candidate}^{{tree}}")
    wrong_first = git(
        repo,
        "commit-tree",
        candidate_tree,
        "-p",
        G0_T03_RECOVERED_MAIN,
        "-p",
        candidate,
        "-m",
        "wrong first parent",
    )
    governed, errors = VALIDATOR._canonical_g0_t03_status_reconciliation_bridge(
        status, repo, wrong_first, require_canonical_main=False
    )
    assert governed is None
    assert errors

    wrong_tree = git(repo, "rev-parse", f"{G0_T03_STATUS_RECONCILIATION_BASE}^{{tree}}")
    drifted = git(
        repo,
        "commit-tree",
        wrong_tree,
        "-p",
        G0_T03_STATUS_RECONCILIATION_BASE,
        "-p",
        candidate,
        "-m",
        "wrong reconciliation tree",
    )
    governed, errors = VALIDATOR._canonical_g0_t03_status_reconciliation_bridge(
        status, repo, drifted, require_canonical_main=False
    )
    assert governed is None
    assert errors
    assert descendant != candidate


def package_a_fixture(tmp_path: Path) -> tuple[Path, dict]:
    root = tmp_path / "package-a"
    manifest_path = root / VALIDATOR.PACKAGE_A_MANIFEST_PATH
    schema_path = root / VALIDATOR.PACKAGE_A_SCHEMA_PATH
    manifest_path.parent.mkdir(parents=True)
    schema_path.parent.mkdir(parents=True)
    shutil.copy2(PACKAGE_A_MANIFEST, manifest_path)
    shutil.copy2(PACKAGE_A_SCHEMA, schema_path)
    tests = root / "tests"
    tests.mkdir()
    (tests / "test_g0_project_status.py").write_text("# fixture\n", encoding="utf-8")
    (tests / "test_m5_transport.py").write_text("# fixture\n", encoding="utf-8")
    git(root, "init", "-q")
    git(root, "config", "user.name", "Test")
    git(root, "config", "user.email", "test@example.invalid")
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", "exact package A")
    return root, json.loads(manifest_path.read_text(encoding="utf-8"))


def write_package_a(root: Path, manifest: dict, *, refresh_digest: bool = True) -> None:
    if refresh_digest:
        manifest["payload_sha256"] = VALIDATOR._payload_digest(manifest)
    (root / VALIDATOR.PACKAGE_A_MANIFEST_PATH).write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    git(root, "add", VALIDATOR.PACKAGE_A_MANIFEST_PATH)
    git(root, "commit", "-q", "-m", "mutate package A")


def test_package_a_exact_manifest_is_valid_and_inactive() -> None:
    assert VALIDATOR._package_a_manifest_errors(ROOT) == []
    manifest = json.loads(PACKAGE_A_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["package_state"] == "not_authorized"
    assert manifest["activation"]["confirmed_payload_sha256"] is None
    assert manifest["ordered_task_ids"] == ["G0-T05", "G1-T01"]


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("unknown_field", "unknown field"),
        ("order", "ordered unique task list"),
        ("digest", "normalized payload digest mismatch"),
        ("baseline", "authoritative_baseline_sha"),
        ("scope", "immutable accepted planning payload drifted"),
        ("nonserial", "strictly serial"),
        ("reviewer", "independent dual review"),
        ("cross_package", "cross-package continuation is forbidden"),
        ("implicit_activation", "must remain explicitly inactive"),
        ("superseded_digest", "superseded generation-1 digest is forbidden"),
        ("missing_test_path", "acceptance test path does not exist"),
    ],
)
def test_package_a_manifest_adversarial_drift_fails_closed(
    tmp_path: Path, mutation: str, expected: str
) -> None:
    root, manifest = package_a_fixture(tmp_path)
    refresh_digest = True
    if mutation == "unknown_field":
        manifest["unexpected"] = True
    elif mutation == "order":
        manifest["cards"].reverse()
    elif mutation == "digest":
        manifest["payload_sha256"] = "0" * 64
        refresh_digest = False
    elif mutation == "baseline":
        manifest["authoritative_baseline_sha"] = "0" * 40
    elif mutation == "scope":
        manifest["cards"][0]["allowed_paths"].append("strategy/live.py")
    elif mutation == "nonserial":
        manifest["cards"][0]["automatic_continuation"]["next_task_id"] = "G1-T02"
    elif mutation == "reviewer":
        manifest["cards"][0]["independent_review"]["code_security"] = "PENDING"
    elif mutation == "cross_package":
        manifest["cards"][0]["automatic_continuation"]["requires_same_package"] = False
    elif mutation == "implicit_activation":
        manifest["package_state"] = "authorized"
        manifest["activation"]["confirmed_payload_sha256"] = manifest["payload_sha256"]
        manifest["activation"]["first_task_state"] = "authorized"
    elif mutation == "superseded_digest":
        manifest["payload_sha256"] = VALIDATOR.PACKAGE_A_SUPERSEDED_PAYLOAD_SHA256
        refresh_digest = False
    elif mutation == "missing_test_path":
        manifest["cards"][0]["acceptance_commands"][2] = (
            "python3 -m pytest -q --ignore=tests/does_not_exist.py"
        )
    else:
        raise AssertionError(mutation)
    write_package_a(root, manifest, refresh_digest=refresh_digest)
    errors = VALIDATOR._package_a_manifest_errors(root)
    assert errors
    assert expected in "\n".join(errors)


@pytest.mark.parametrize("relative", [VALIDATOR.PACKAGE_A_MANIFEST_PATH, VALIDATOR.PACKAGE_A_SCHEMA_PATH])
def test_package_a_symlink_git_entries_are_rejected(
    tmp_path: Path, relative: str
) -> None:
    root, _ = package_a_fixture(tmp_path)
    path = root / relative
    external = tmp_path / ("external-" + path.name)
    external.write_bytes(path.read_bytes())
    path.unlink()
    path.symlink_to(external)
    git(root, "add", relative)
    git(root, "commit", "-q", "-m", "replace immutable artifact with symlink")
    errors = VALIDATOR._package_a_manifest_errors(root)
    assert "exact committed 100644 Git blobs" in "\n".join(errors)


def test_package_a_executable_git_entry_is_rejected(tmp_path: Path) -> None:
    root, _ = package_a_fixture(tmp_path)
    path = root / VALIDATOR.PACKAGE_A_MANIFEST_PATH
    path.chmod(0o755)
    git(root, "add", VALIDATOR.PACKAGE_A_MANIFEST_PATH)
    git(root, "commit", "-q", "-m", "make immutable manifest executable")
    errors = VALIDATOR._package_a_manifest_errors(root)
    assert "exact committed 100644 Git blobs" in "\n".join(errors)


def test_package_a_g1_freezes_complete_transport_backend_ci() -> None:
    manifest = json.loads(PACKAGE_A_MANIFEST.read_text(encoding="utf-8"))
    g1 = manifest["cards"][1]
    rendered = json.dumps(g1, ensure_ascii=False)
    assert "non-transport" not in rendered
    assert "tests/test_m5_transport.py" in rendered
    assert "missing API dependency" in rendered
    assert "uncollected, skipped, or failed transport test" in rendered
    assert "python3 -m pytest -q" in g1["acceptance_commands"]
    g0 = manifest["cards"][0]
    assert "python3 -m pytest -q --ignore=tests/test_m5_transport.py" in g0["acceptance_commands"]
    assert all("test_api_transport.py" not in command for command in g0["acceptance_commands"])


def make_package_a_activation(
    closed_sha: str, **overrides: object
) -> dict:
    activation = {
        "schema_version": VALIDATOR.PACKAGE_A_ACTIVATION_VERSION,
        "package_id": "PACKAGE-A",
        "package_generation": 2,
        "manifest_path": VALIDATOR.PACKAGE_A_MANIFEST_PATH,
        "schema_path": VALIDATOR.PACKAGE_A_SCHEMA_PATH,
        "manifest_payload_sha256": VALIDATOR.PACKAGE_A_PAYLOAD_SHA256,
        "first_task_id": "G0-T05",
        "package_state": "authorized",
        "product_owner_confirmation": "exact_payload_digest_confirmed",
        "g0_t04_closed_sha": closed_sha,
    }
    activation.update(overrides)
    activation["payload_sha256"] = VALIDATOR._payload_digest(activation)
    return activation


def make_post_g0_t04_package_repo(tmp_path: Path) -> tuple[Path, dict, str, str]:
    repo = tmp_path / "post-g0-t04-package"
    git(tmp_path, "clone", "--quiet", str(ROOT), str(repo))
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    shutil.copy2(PACKAGE_A_MANIFEST, repo / VALIDATOR.PACKAGE_A_MANIFEST_PATH)
    shutil.copy2(PACKAGE_A_SCHEMA, repo / VALIDATOR.PACKAGE_A_SCHEMA_PATH)
    status = json.loads((repo / "PROJECT_STATUS.yaml").read_text(encoding="utf-8"))
    status["active_tasks"][0].update(
        task_id="G0-T04",
        risk="D0",
        state="closed",
        transition={"from": "merged_verified", "to": "closed"},
        candidate_generation=2,
    )
    write_status(repo / "PROJECT_STATUS.yaml", status)
    closed_sha = commit(repo, "synthetic closed G0-T04 package anchor")

    status["active_tasks"][0].update(
        task_id="G0-T05",
        state="authorized",
        transition={"from": "closed", "to": "authorized"},
        candidate_generation=1,
    )
    status["evidence"]["authorization_baseline_sha"] = closed_sha
    status["evidence"]["implementation_sha"] = None
    status["evidence"]["candidate"] = {
        "commit_sha": None,
        "local_verification": {"status": "pending", "subject": "delivery_head"},
        "ci": {"status": "not_run", "subject_sha": None, "run_id": None, "url": None},
    }
    for phase in ("closure", "merged_main"):
        status["evidence"][phase] = {
            "commit_sha": None,
            "ci": {"status": "not_run", "subject_sha": None, "run_id": None, "url": None},
        }
    status["evidence"]["finalization"] = {
        "commit_sha": None,
        "d0_ci": {"status": "not_run", "subject_sha": None, "run_id": None, "url": None},
    }
    status["review"] = {
        "code_security": "pending",
        "architecture": "pending",
        "reviewed_candidate_sha": None,
    }
    status["next_authorization"] = {
        "gate": "G1",
        "task_id": "G1-T01",
        "state": "not_authorized",
    }
    write_status(repo / "PROJECT_STATUS.yaml", status)
    activation_path = repo / VALIDATOR.PACKAGE_A_ACTIVATION_PATH
    activation_path.parent.mkdir(parents=True, exist_ok=True)
    write_digest_json(activation_path, make_package_a_activation(closed_sha))
    authorized_sha = commit(repo, "authorize G0-T05 with exact package digest")
    return repo, status, closed_sha, authorized_sha


def test_package_a_persists_from_g0_t04_close_through_g0_t05(
    tmp_path: Path,
) -> None:
    repo, status, _, authorized_sha = make_post_g0_t04_package_repo(tmp_path)
    assert VALIDATOR._package_a_persistence_errors(status, repo, authorized_sha) == []

    status["active_tasks"][0].update(
        state="in_progress",
        transition={"from": "authorized", "to": "in_progress"},
    )
    write_status(repo / "PROJECT_STATUS.yaml", status)
    in_progress_sha = commit(repo, "start G0-T05")
    assert VALIDATOR._package_a_persistence_errors(status, repo, in_progress_sha) == []

    manifest_path = repo / VALIDATOR.PACKAGE_A_MANIFEST_PATH
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["cards"][0]["goal"] += " drift"
    write_digest_json(manifest_path, manifest)
    drift_sha = commit(repo, "drift accepted package")
    errors = VALIDATOR._package_a_persistence_errors(status, repo, drift_sha)
    assert "immutable blob drifted after accepted baseline" in "\n".join(errors)


def test_package_a_active_card_allowlist_remains_fail_closed(
    tmp_path: Path,
) -> None:
    repo, status, _, authorized_sha = make_post_g0_t04_package_repo(tmp_path)
    assert VALIDATOR._package_a_persistence_errors(status, repo, authorized_sha) == []
    (repo / "strategy" / "package_scope_escape.py").write_text("escape = True\n", encoding="utf-8")
    escaped_sha = commit(repo, "escape frozen G0-T05 allowlist")
    errors = VALIDATOR._package_a_persistence_errors(status, repo, escaped_sha)
    assert "changed paths exceed its immutable allowlist" in "\n".join(errors)


def test_package_a_persistence_skips_legacy_when_head_and_baseline_both_absent(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "legacy-g1-without-package-a"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    status = load_valid()
    status["current_gate"] = "G0"
    status["active_tasks"][0].update(
        task_id="G0-T99",
        state="closed",
        transition={"from": "merged_verified", "to": "closed"},
    )
    write_status(repo / "PROJECT_STATUS.yaml", status)
    baseline = commit(repo, "legacy baseline without Package A")
    status["current_gate"] = "G1"
    status["active_tasks"][0].update(
        task_id="G1-T01",
        state="in_progress",
        transition={"from": "authorized", "to": "in_progress"},
        candidate_generation=1,
    )
    status["evidence"]["authorization_baseline_sha"] = baseline
    write_status(repo / "PROJECT_STATUS.yaml", status)
    head = commit(repo, "legacy G1 without Package A")
    assert VALIDATOR._package_a_persistence_errors(status, repo, head) == []


@pytest.mark.parametrize(
    "relative",
    [VALIDATOR.PACKAGE_A_MANIFEST_PATH, VALIDATOR.PACKAGE_A_SCHEMA_PATH],
)
def test_package_a_baseline_present_artifact_deletion_fails_closed(
    tmp_path: Path, relative: str
) -> None:
    repo, status, _, authorized_sha = make_post_g0_t04_package_repo(tmp_path)
    assert VALIDATOR._package_a_persistence_errors(status, repo, authorized_sha) == []
    (repo / relative).unlink()
    deleted_sha = commit(repo, f"delete accepted {relative}")
    errors = VALIDATOR._package_a_persistence_errors(status, repo, deleted_sha)
    rendered = "\n".join(errors)
    assert "exact committed 100644 Git blobs" in rendered
    assert "immutable blob drifted after accepted baseline" in rendered


def test_exact_g0_t04_failed_main_and_recovery_record_are_accepted(
    tmp_path: Path,
) -> None:
    repo, status, recovery = make_g0_t04_recovery(tmp_path)
    schema = json.loads(
        (repo / "schemas" / "project_status.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert VALIDATOR._g0_t04_failed_merge_errors(repo, schema) == []
    assert VALIDATOR._g0_t04_recovery_receipt_errors(repo, recovery) == []
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout
    assert VALIDATOR._is_g0_t04_post_merge_recovery_status(status)


def test_g0_t04_recovery_historical_validation_ignores_advanced_main(
    tmp_path: Path,
) -> None:
    repo, status, recovery = make_g0_t04_recovery(tmp_path)
    parent = VALIDATOR._status_at(repo, G0_T04_FAILED_MAIN)
    assert isinstance(parent, dict)
    git(repo, "update-ref", "refs/heads/main", G0_T04_CLOSURE)
    git(repo, "update-ref", "refs/remotes/origin/main", G0_T04_CLOSURE)

    live_errors = VALIDATOR._g0_t04_recovery_parent_errors(
        status,
        parent,
        G0_T04_FAILED_MAIN,
        repo,
        recovery,
        require_current_main=True,
    )
    historical_errors = VALIDATOR._g0_t04_recovery_parent_errors(
        status,
        parent,
        G0_T04_FAILED_MAIN,
        repo,
        recovery,
        require_current_main=False,
    )

    assert live_errors is not None
    assert any("authoritative main" in item for item in live_errors)
    assert historical_errors == []


def test_g0_t04_recovery_descendant_rejects_out_of_scope_path(
    tmp_path: Path,
) -> None:
    repo, _, recovery = make_g0_t04_recovery(tmp_path)
    (repo / "ordinary.txt").write_text("out of scope\n", encoding="utf-8")
    forged = commit(repo, "forge out-of-scope G0-T04 recovery descendant")

    assert git(repo, "rev-list", "--parents", "-n", "1", forged).split() == [
        forged,
        recovery,
    ]
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)

    assert result.returncode == 1
    assert "G0-T04 recovery changed paths violate the exact allowlist" in result.stdout


def test_exact_g0_t04_recovery_merge_is_accepted(tmp_path: Path) -> None:
    repo, status, recovery = make_g0_t04_recovery(tmp_path)
    tree = git(repo, "rev-parse", f"{recovery}^{{tree}}")
    merged = git(
        repo,
        "commit-tree",
        tree,
        "-p",
        G0_T04_FAILED_MAIN,
        "-p",
        recovery,
        "-m",
        "merge exact G0-T04 merged-main recovery",
    )
    git(repo, "switch", "--detach", merged)
    git(repo, "update-ref", "refs/heads/main", merged)
    git(repo, "update-ref", "refs/remotes/origin/main", merged)
    schema = json.loads(
        (repo / "schemas" / "project_status.schema.json").read_text(
            encoding="utf-8"
        )
    )
    governed, errors = VALIDATOR._canonical_g0_t04_recovery_bridge(
        status, repo, merged, schema, require_canonical_main=True
    )
    assert governed == recovery
    assert errors == []
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize(
    "mutation",
    [
        "wrong_failed_main",
        "wrong_second_parent",
        "wrong_tree",
        "wrong_failed_run",
        "ordinary_descendant",
    ],
)
def test_g0_t04_recovery_rejects_topology_and_evidence_substitution(
    tmp_path: Path, mutation: str
) -> None:
    repo, status, recovery = make_g0_t04_recovery(
        tmp_path,
        receipt_run_drift=mutation == "wrong_failed_run",
        ordinary_path=mutation == "ordinary_descendant",
    )
    first = G0_T04_FAILED_MAIN
    second = recovery
    tree = git(repo, "rev-parse", f"{recovery}^{{tree}}")
    if mutation == "wrong_failed_main":
        first = VALIDATOR.G0_T04_FAILED_MAIN_FIRST_PARENT
    elif mutation == "wrong_second_parent":
        second = G0_T04_CLOSURE
        tree = git(repo, "rev-parse", f"{second}^{{tree}}")
    elif mutation == "wrong_tree":
        tree = git(repo, "rev-parse", f"{G0_T04_FAILED_MAIN}^{{tree}}")
    merged = git(
        repo,
        "commit-tree",
        tree,
        "-p",
        first,
        "-p",
        second,
        "-m",
        f"forged G0-T04 recovery {mutation}",
    )
    git(repo, "switch", "--detach", merged)
    git(repo, "update-ref", "refs/heads/main", merged)
    git(repo, "update-ref", "refs/remotes/origin/main", merged)
    schema = json.loads(
        (repo / "schemas" / "project_status.schema.json").read_text(
            encoding="utf-8"
        )
    )
    governed, errors = VALIDATOR._canonical_g0_t04_recovery_bridge(
        status, repo, merged, schema, require_canonical_main=True
    )
    assert governed is None
    assert errors
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 1


def test_g0_t04_pr15_pr22_anomaly_two_stage_is_canonical(tmp_path: Path) -> None:
    repo, status, implementation, delivery = make_g0_t04_anomaly_recovery(tmp_path)
    parent = VALIDATOR._status_at(repo, implementation)
    assert parent is not None
    assert VALIDATOR._g0_t04_anomaly_parent_errors(
        status,
        parent,
        implementation,
        repo,
        delivery,
        require_current_main=True,
    ) == []
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout


def test_g0_t04_pr15_pr22_live_main_strict_history_replayable(
    tmp_path: Path,
) -> None:
    repo, status, implementation, delivery = make_g0_t04_anomaly_recovery(tmp_path)
    parent = VALIDATOR._status_at(repo, implementation)
    assert parent is not None
    git(repo, "update-ref", "refs/heads/main", G0_T04_FAILED_MAIN)
    live = VALIDATOR._g0_t04_anomaly_parent_errors(
        status,
        parent,
        implementation,
        repo,
        delivery,
        require_current_main=True,
    )
    history = VALIDATOR._g0_t04_anomaly_parent_errors(
        status,
        parent,
        implementation,
        repo,
        delivery,
        require_current_main=False,
    )
    assert any("exact current main" in error for error in live)
    assert not any("exact current main" in error for error in history)


@pytest.mark.parametrize("mutation", ["receipt", "activation", "ordinary"])
def test_g0_t04_pr15_pr22_rejects_evidence_activation_and_allowlist_drift(
    tmp_path: Path, mutation: str
) -> None:
    repo, status, _, delivery = make_g0_t04_anomaly_recovery(tmp_path, mutation)
    errors = VALIDATOR._g0_t04_anomaly_delivery_errors(
        status, repo, delivery, require_current_main=False
    )
    assert errors


def test_g0_t04_pr15_pr22_merge_bridge_rejects_parent_and_tree_drift(
    tmp_path: Path,
) -> None:
    repo, status, _, delivery = make_g0_t04_anomaly_recovery(tmp_path)
    schema = json.loads((repo / "schemas/project_status.schema.json").read_text())
    delivery_tree = git(repo, "rev-parse", f"{delivery}^{{tree}}")
    obsolete_direct = git(
        repo,
        "commit-tree",
        delivery_tree,
        "-p",
        G0_T04_ANOMALY_MAIN,
        "-p",
        delivery,
        "-m",
        "obsolete direct recovery merge",
    )
    governed, errors = VALIDATOR._canonical_g0_t04_anomaly_bridge(
        status, repo, obsolete_direct, schema, require_canonical_main=False
    )
    assert governed is None
    assert errors

    swapped = git(
        repo,
        "commit-tree",
        delivery_tree,
        "-p",
        delivery,
        "-p",
        G0_T04_ANOMALY_MAIN,
        "-m",
        "swapped recovery merge",
    )
    governed, errors = VALIDATOR._canonical_g0_t04_anomaly_bridge(
        status, repo, swapped, schema, require_canonical_main=False
    )
    assert governed is None
    assert errors


def test_g0_t04_pr15_pr22_merge_rejects_delivery_skipping_exact_implementation(
    tmp_path: Path,
) -> None:
    repo, status, _, delivery = make_g0_t04_anomaly_recovery(tmp_path)
    schema = json.loads((repo / "schemas/project_status.schema.json").read_text())
    delivery_tree = git(repo, "rev-parse", f"{delivery}^{{tree}}")
    skipped = git(
        repo,
        "commit-tree",
        delivery_tree,
        "-p",
        G0_T04_ANOMALY_MAIN,
        "-m",
        "content-identical delivery skipping implementation",
    )
    merged = git(
        repo,
        "commit-tree",
        delivery_tree,
        "-p",
        G0_T04_ANOMALY_MAIN,
        "-p",
        skipped,
        "-m",
        "merge skipped delivery",
    )
    governed, errors = VALIDATOR._canonical_g0_t04_anomaly_bridge(
        status, repo, merged, schema, require_canonical_main=False
    )
    assert governed is None
    assert errors


def test_g0_t04_pr15_pr22_merge_rejects_substituted_implementation_same_tree(
    tmp_path: Path,
) -> None:
    repo, status, implementation, delivery = make_g0_t04_anomaly_recovery(tmp_path)
    schema = json.loads((repo / "schemas/project_status.schema.json").read_text())
    implementation_tree = git(repo, "rev-parse", f"{implementation}^{{tree}}")
    delivery_tree = git(repo, "rev-parse", f"{delivery}^{{tree}}")
    substituted_implementation = git(
        repo,
        "commit-tree",
        implementation_tree,
        "-p",
        G0_T04_ANOMALY_MAIN,
        "-m",
        "substituted implementation with identical tree",
    )
    substituted_delivery = git(
        repo,
        "commit-tree",
        delivery_tree,
        "-p",
        substituted_implementation,
        "-m",
        "delivery from substituted implementation",
    )
    merged = git(
        repo,
        "commit-tree",
        delivery_tree,
        "-p",
        G0_T04_ANOMALY_MAIN,
        "-p",
        substituted_delivery,
        "-m",
        "merge substituted implementation lineage",
    )
    governed, errors = VALIDATOR._canonical_g0_t04_anomaly_bridge(
        status, repo, merged, schema, require_canonical_main=False
    )
    assert governed is None
    assert errors


def test_g0_t04_pr15_pr22_merge_rejects_non_delivery_second_parent_lineage(
    tmp_path: Path,
) -> None:
    repo, status, _, delivery = make_g0_t04_anomaly_recovery(tmp_path)
    schema = json.loads((repo / "schemas/project_status.schema.json").read_text())
    delivery_tree = git(repo, "rev-parse", f"{delivery}^{{tree}}")
    wrapper = git(
        repo,
        "commit-tree",
        delivery_tree,
        "-p",
        delivery,
        "-m",
        "content-identical wrapper after exact delivery",
    )
    merged = git(
        repo,
        "commit-tree",
        delivery_tree,
        "-p",
        G0_T04_ANOMALY_MAIN,
        "-p",
        wrapper,
        "-m",
        "merge non-delivery lineage",
    )
    governed, errors = VALIDATOR._canonical_g0_t04_anomaly_bridge(
        status, repo, merged, schema, require_canonical_main=False
    )
    assert governed is None
    assert errors


def test_g0_t04_pr15_pr22_stage2_seal_and_future_bridge_are_canonical(
    tmp_path: Path,
) -> None:
    repo, status, seal = make_g0_t04_anomaly_seal(tmp_path)
    parent = VALIDATOR._status_at(repo, G0_T04_ANOMALY_CANDIDATE)
    assert parent is not None
    assert VALIDATOR._g0_t04_anomaly_seal_parent_errors(
        status,
        parent,
        G0_T04_ANOMALY_CANDIDATE,
        repo,
        seal,
        require_current_main=True,
    ) == []
    result = run_validator(repo / "PROJECT_STATUS.yaml", repo)
    assert result.returncode == 0, result.stdout
    seal_tree = git(repo, "rev-parse", f"{seal}^{{tree}}")
    merged = git(
        repo,
        "commit-tree",
        seal_tree,
        "-p",
        G0_T04_ANOMALY_MAIN,
        "-p",
        seal,
        "-m",
        "merge exact reviewed anomaly seal",
    )
    schema = json.loads((repo / "schemas/project_status.schema.json").read_text())
    governed, errors = VALIDATOR._canonical_g0_t04_anomaly_bridge(
        status, repo, merged, schema, require_canonical_main=False
    )
    assert governed == seal
    assert errors == []


def test_g0_t04_pr15_pr22_direct_candidate_merge_is_rejected_after_seal_route(
    tmp_path: Path,
) -> None:
    repo, status, _, delivery = make_g0_t04_anomaly_recovery(tmp_path)
    delivery_tree = git(repo, "rev-parse", f"{delivery}^{{tree}}")
    merged = git(
        repo,
        "commit-tree",
        delivery_tree,
        "-p",
        G0_T04_ANOMALY_MAIN,
        "-p",
        delivery,
        "-m",
        "obsolete direct candidate merge",
    )
    schema = json.loads((repo / "schemas/project_status.schema.json").read_text())
    governed, errors = VALIDATOR._canonical_g0_t04_anomaly_bridge(
        status, repo, merged, schema, require_canonical_main=False
    )
    assert governed is None
    assert errors


@pytest.mark.parametrize(
    "mutation",
    ["parent", "receipt", "ci", "review", "package", "activation", "allowlist"],
)
def test_g0_t04_pr15_pr22_stage2_seal_rejects_drift(
    tmp_path: Path, mutation: str
) -> None:
    repo, status, seal = make_g0_t04_anomaly_seal(tmp_path, mutation)
    parent = VALIDATOR._status_at(repo, G0_T04_ANOMALY_CANDIDATE)
    assert parent is not None
    errors = VALIDATOR._g0_t04_anomaly_seal_parent_errors(
        status,
        parent,
        G0_T04_ANOMALY_CANDIDATE,
        repo,
        seal,
        require_current_main=False,
    )
    assert errors


@pytest.mark.parametrize("mutation", ["parents", "tree"])
def test_g0_t04_pr15_pr22_stage2_merge_rejects_topology_drift(
    tmp_path: Path, mutation: str
) -> None:
    repo, status, seal = make_g0_t04_anomaly_seal(tmp_path)
    seal_tree = git(repo, "rev-parse", f"{seal}^{{tree}}")
    if mutation == "parents":
        parents = (seal, G0_T04_ANOMALY_MAIN)
        tree = seal_tree
    else:
        parents = (G0_T04_ANOMALY_MAIN, seal)
        tree = git(repo, "rev-parse", f"{G0_T04_ANOMALY_MAIN}^{{tree}}")
    merged = git(
        repo,
        "commit-tree",
        tree,
        "-p",
        parents[0],
        "-p",
        parents[1],
        "-m",
        "forged stage2 seal merge",
    )
    schema = json.loads((repo / "schemas/project_status.schema.json").read_text())
    governed, errors = VALIDATOR._canonical_g0_t04_anomaly_bridge(
        status, repo, merged, schema, require_canonical_main=False
    )
    assert governed is None
    assert errors


def test_g0_t04_pr15_pr22_stage2_seal_live_main_strict_history_replayable(
    tmp_path: Path,
) -> None:
    repo, status, seal = make_g0_t04_anomaly_seal(tmp_path)
    parent = VALIDATOR._status_at(repo, G0_T04_ANOMALY_CANDIDATE)
    assert parent is not None
    git(repo, "update-ref", "refs/heads/main", G0_T04_ANOMALY_CANDIDATE)
    live = VALIDATOR._g0_t04_anomaly_seal_parent_errors(
        status,
        parent,
        G0_T04_ANOMALY_CANDIDATE,
        repo,
        seal,
        require_current_main=True,
    )
    history = VALIDATOR._g0_t04_anomaly_seal_parent_errors(
        status,
        parent,
        G0_T04_ANOMALY_CANDIDATE,
        repo,
        seal,
        require_current_main=False,
    )
    assert any("exact current main" in error for error in live)
    assert not any("exact current main" in error for error in history)


def test_g0_t04_pr15_pr22_same_tree_seal_identity_is_external_gate(
    tmp_path: Path,
) -> None:
    repo, status, seal = make_g0_t04_anomaly_seal(tmp_path)
    same_tree_seal = git(
        repo,
        "commit-tree",
        git(repo, "rev-parse", f"{seal}^{{tree}}"),
        "-p",
        G0_T04_ANOMALY_CANDIDATE,
        "-m",
        "same-tree seal requiring the same external gate",
    )
    parent = VALIDATOR._status_at(repo, G0_T04_ANOMALY_CANDIDATE)
    assert parent is not None
    # A commit cannot attest its own future SHA. Code binds exact parent/tree/bytes;
    # exact S identity is established only by the later external CI/review gate.
    assert VALIDATOR._g0_t04_anomaly_seal_parent_errors(
        status,
        parent,
        G0_T04_ANOMALY_CANDIDATE,
        repo,
        same_tree_seal,
        require_current_main=False,
    ) == []
