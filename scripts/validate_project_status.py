#!/usr/bin/env python3
"""Fail-closed project-status v2 validator using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATUS = ROOT / "PROJECT_STATUS.yaml"
DEFAULT_SCHEMA = ROOT / "schemas" / "project_status.schema.json"
BOOTSTRAP_TASK = "G0-T01"
BOOTSTRAP_BASELINE = "7aadae13efd45023d19bf8a280f7680667c930fa"

TRANSITIONS = {
    "planned": {"authorized"},
    "authorized": {"in_progress"},
    "in_progress": {"awaiting_review", "blocked"},
    "awaiting_review": {"returned", "blocked", "accepted_pending_merge"},
    "returned": {"in_progress", "blocked"},
    "blocked": set(),
    "accepted_pending_merge": {"merged_verified"},
    "merged_verified": {"closed"},
    "closed": set(),
}
MATURITY = {"OFFLINE_EVIDENCE_ACCEPTED": 0, "INTEGRATION_ACCEPTED": 1, "PAPER_VALIDATED": 2, "RELEASE_READY": 3}
GATE_CEILING = {**{f"G{i}": 0 for i in range(6)}, "G6": 1, "G7": 1, "G8": 2, "G9": 3}
FORBIDDEN_CURRENT_MIRROR = re.compile(
    r"^\s*(?:[-*]\s*)?(?:current\s+(?:gate|task|status|state|maturity)|当前(?:门禁|任务|状态|成熟度))\s*[:：]",
    re.IGNORECASE | re.MULTILINE,
)
STALE_M_CLAIM = re.compile(
    r"(?:当前项目处于\s*M[0-9]|当前里程碑[：:]\s*M[0-9]|当前任务[：:]\s*`?M[0-9]-T[0-9]+|current\s+(?:milestone|stage|task)\s*[:：]\s*`?M[0-9])",
    re.IGNORECASE,
)


def _type_matches(value: Any, expected: str) -> bool:
    return {"object": type(value) is dict, "array": type(value) is list, "string": type(value) is str, "integer": type(value) is int, "null": value is None, "boolean": type(value) is bool}.get(expected, False)


def _resolve_ref(schema: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError("unsupported schema reference")
    node: Any = schema
    for component in ref[2:].split("/"):
        node = node[component.replace("~1", "/").replace("~0", "~")]
    if type(node) is not dict:
        raise ValueError("invalid schema reference")
    return node


def _schema_errors(value: Any, rule: dict[str, Any], schema: dict[str, Any], path: str = "$") -> list[str]:
    if "$ref" in rule:
        return _schema_errors(value, _resolve_ref(schema, rule["$ref"]), schema, path)
    errors: list[str] = []
    if "const" in rule and value != rule["const"]:
        errors.append(f"{path}: value does not match required constant")
    if "enum" in rule and value not in rule["enum"]:
        errors.append(f"{path}: value is not in the allowed set")
    expected = rule.get("type")
    if expected is not None:
        allowed = expected if type(expected) is list else [expected]
        if not any(_type_matches(value, item) for item in allowed):
            errors.append(f"{path}: invalid type")
            return errors
    if type(value) is dict:
        properties = rule.get("properties", {})
        for key in rule.get("required", []):
            if key not in value:
                errors.append(f"{path}.{key}: required field is missing")
        if rule.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    errors.append(f"{path}.{key}: unknown field")
        for key, child in value.items():
            if key in properties:
                errors.extend(_schema_errors(child, properties[key], schema, f"{path}.{key}"))
    if type(value) is list:
        if len(value) < rule.get("minItems", 0):
            errors.append(f"{path}: too few items")
        if "maxItems" in rule and len(value) > rule["maxItems"]:
            errors.append(f"{path}: too many items")
        if "items" in rule:
            for index, child in enumerate(value):
                errors.extend(_schema_errors(child, rule["items"], schema, f"{path}[{index}]"))
    if type(value) is str:
        if len(value) < rule.get("minLength", 0):
            errors.append(f"{path}: string is too short")
        if "pattern" in rule and re.fullmatch(rule["pattern"], value) is None:
            errors.append(f"{path}: string has invalid format")
    if type(value) is int:
        if "minimum" in rule and value < rule["minimum"]:
            errors.append(f"{path}: integer is below minimum")
        if "maximum" in rule and value > rule["maximum"]:
            errors.append(f"{path}: integer is above maximum")
    return errors


def _ci_errors(ci: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    status = ci.get("status")
    identities = (ci.get("subject_sha"), ci.get("run_id"), ci.get("url"))
    if status in {"not_established", "not_run"} and any(item is not None for item in identities):
        errors.append(f"{path}: inactive CI must not carry subject or run identity")
    if status in {"pending", "success", "failure"} and any(item is None for item in identities):
        errors.append(f"{path}: active CI requires subject, run, and URL identity")
    return errors


def _all_ci(evidence: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    return [
        ("$.evidence.candidate.ci", evidence["candidate"]["ci"]),
        ("$.evidence.closure.ci", evidence["closure"]["ci"]),
        ("$.evidence.merged_main.ci", evidence["merged_main"]["ci"]),
        ("$.evidence.finalization.d0_ci", evidence["finalization"]["d0_ci"]),
    ]


def _phase_identity_errors(evidence: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    mapping = [
        ("candidate", evidence["candidate"]["commit_sha"], evidence["candidate"]["ci"]),
        ("closure", evidence["closure"]["commit_sha"], evidence["closure"]["ci"]),
        ("merged_main", evidence["merged_main"]["commit_sha"], evidence["merged_main"]["ci"]),
        ("finalization", evidence["finalization"]["commit_sha"], evidence["finalization"]["d0_ci"]),
    ]
    for name, commit_sha, ci in mapping:
        if ci.get("status") in {"pending", "success", "failure"} and ci.get("subject_sha") != commit_sha:
            errors.append(f"$.evidence.{name}: CI subject must equal the recorded phase commit")
    return errors


def _semantic_errors(status: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    task = status["active_tasks"][0]
    task_id, state = task["task_id"], task["state"]
    transition = task["transition"]
    current_gate = status["current_gate"]
    if task_id.split("-", 1)[0] != current_gate:
        errors.append("$.active_tasks[0].task_id: task gate must match current_gate")
    if transition["to"] != state:
        errors.append("$.active_tasks[0].transition.to: must equal current task state")
    if transition["to"] not in TRANSITIONS.get(transition["from"], set()):
        errors.append("$.active_tasks[0].transition: illegal lifecycle transition")

    evidence = status["evidence"]
    candidate = evidence["candidate"]
    phases = (candidate, evidence["closure"], evidence["merged_main"], evidence["finalization"])
    review = status["review"]
    for path, ci in _all_ci(evidence):
        errors.extend(_ci_errors(ci, path))
    errors.extend(_phase_identity_errors(evidence))

    if state in {"planned", "authorized", "in_progress"}:
        if evidence["implementation_sha"] is not None or any(phase["commit_sha"] is not None for phase in phases):
            errors.append("$.evidence: undelivered state must clear implementation and phase commit identities")
        if candidate["local_verification"]["status"] != "pending":
            errors.append("$.evidence.candidate.local_verification: undelivered state must be pending")
        if review != {"code_security": "pending", "architecture": "pending", "reviewed_candidate_sha": None}:
            errors.append("$.review: undelivered state must clear reviewer identity")
        if any(ci["status"] not in {"not_established", "not_run"} for _, ci in _all_ci(evidence)):
            errors.append("$.evidence: undelivered state must clear CI results")

    if state == "awaiting_review":
        if evidence["implementation_sha"] is None:
            errors.append("$.evidence.implementation_sha: required at delivery")
        if candidate["commit_sha"] is not None:
            errors.append("$.evidence.candidate.commit_sha: delivery HEAD is recorded only by a later review commit")
        if candidate["local_verification"]["status"] != "success":
            errors.append("$.evidence.candidate.local_verification: successful local evidence is required at delivery")
        if any(phase["commit_sha"] is not None for phase in phases[1:]):
            errors.append("$.evidence: later phase commits are forbidden while awaiting review")
        if review != {"code_security": "pending", "architecture": "pending", "reviewed_candidate_sha": None}:
            errors.append("$.review: awaiting review must not carry a reviewer verdict")

    if state == "returned":
        returned_sha = candidate["commit_sha"]
        if evidence["implementation_sha"] is None:
            errors.append("$.evidence.implementation_sha: returned state must retain implementation identity")
        if returned_sha is None or review["reviewed_candidate_sha"] != returned_sha:
            errors.append("$.review: returned verdict must bind the exact returned candidate")
        if review["code_security"] == "pending" or review["architecture"] == "pending":
            errors.append("$.review: returned verdict cannot contain pending reviewers")
        negative = review["code_security"] in {"request_changes", "blocked"} or review["architecture"] in {"watch", "block"}
        if not negative:
            errors.append("$.review: returned state requires a negative review verdict")
        if candidate["ci"]["status"] == "success":
            errors.append("$.evidence.candidate.ci: returned state cannot retain successful CI")
        if candidate["local_verification"]["status"] != "success":
            errors.append("$.evidence.candidate.local_verification: returned evidence must identify a delivered candidate")
        if any(phase["commit_sha"] is not None for phase in phases[1:]) or any(ci["status"] not in {"not_established", "not_run"} for _, ci in _all_ci(evidence)[1:]):
            errors.append("$.evidence: returned state cannot carry closure or later-phase evidence")

    accepted_states = {"accepted_pending_merge", "merged_verified", "closed"}
    if state in accepted_states:
        candidate_sha = candidate["commit_sha"]
        if candidate_sha is None or review["reviewed_candidate_sha"] != candidate_sha:
            errors.append("$.review: accepted states must bind the exact delivered candidate")
        if review["code_security"] != "approve" or review["architecture"] != "clear":
            errors.append("$.review: accepted states require code/security approve and architecture clear")
        if candidate["local_verification"]["status"] != "success":
            errors.append("$.evidence.candidate.local_verification: accepted states require successful local evidence")
    if state == "accepted_pending_merge" and evidence["closure"]["commit_sha"] is not None:
        errors.append("$.evidence.closure.commit_sha: closure HEAD is recorded only by a later phase")
    if state == "accepted_pending_merge" and (evidence["merged_main"]["commit_sha"] is not None or evidence["finalization"]["commit_sha"] is not None):
        errors.append("$.evidence: accepted-pending-merge cannot carry merged-main or finalization commits")
    if state in {"merged_verified", "closed"}:
        if evidence["closure"]["commit_sha"] is None or evidence["merged_main"]["commit_sha"] is None:
            errors.append("$.evidence: merged verification requires closure and merged-main commits")
    if state == "merged_verified" and evidence["finalization"]["commit_sha"] is not None:
        errors.append("$.evidence.finalization.commit_sha: finalization HEAD is recorded only by the close record")
    if state == "closed" and evidence["finalization"]["commit_sha"] is None:
        errors.append("$.evidence.finalization.commit_sha: required when closed")
    if state == "blocked" and not status["blockers"]:
        errors.append("$.blockers: blocked state requires a recorded blocker")

    if state == "in_progress" and transition["from"] == "returned":
        if task["candidate_generation"] < 2:
            errors.append("$.active_tasks[0].candidate_generation: returned repair must increment generation")
        if any(ci["subject_sha"] is not None or ci["run_id"] is not None or ci["url"] is not None for _, ci in _all_ci(evidence)):
            errors.append("$: returned repair must atomically clear all CI identities")

    exception = status["bootstrap_exception"]
    exception_consumed = exception is not None and exception["status"] == "consumed" and exception["uses"] == 1
    if exception is not None:
        if task_id != BOOTSTRAP_TASK or evidence["authorization_baseline_sha"] != BOOTSTRAP_BASELINE:
            errors.append("$.bootstrap_exception: exception is restricted to the authorized G0-T01 baseline")
        expected_status = "consumed" if state in accepted_states else "available"
        expected_uses = 1 if state in accepted_states else 0
        if exception["status"] != expected_status or exception["uses"] != expected_uses:
            errors.append("$.bootstrap_exception: availability/consumption does not match task state")
        if status["capability"]["maturity"] != "OFFLINE_EVIDENCE_ACCEPTED":
            errors.append("$.bootstrap_exception: bootstrap exception is offline-evidence only")
        if exception_consumed:
            if review["code_security"] != "approve" or review["architecture"] != "clear" or candidate["local_verification"]["status"] != "success":
                errors.append("$.bootstrap_exception: consumption requires dual clear local review evidence")
            if any(ci["status"] != "not_established" for _, ci in _all_ci(evidence)):
                errors.append("$.bootstrap_exception: no-CI exception cannot coexist with CI claims")
    elif state in accepted_states:
        required = [candidate["ci"]]
        if state in {"merged_verified", "closed"}:
            required.extend([evidence["closure"]["ci"], evidence["merged_main"]["ci"]])
        if state == "closed":
            required.append(evidence["finalization"]["d0_ci"])
        if any(ci["status"] != "success" for ci in required):
            errors.append("$.evidence: normal accepted phases require successful phase-specific CI")

    maturity = status["capability"]["maturity"]
    if MATURITY[maturity] > GATE_CEILING[current_gate]:
        errors.append("$.capability.maturity: maturity exceeds current gate ceiling")
    if maturity == "RELEASE_READY":
        if current_gate != "G9" or state != "closed" or not status["release"]["product_owner_go"] or not status["release"]["release_evidence_complete"]:
            errors.append("$.capability.maturity: RELEASE_READY requires closed G9, explicit owner go, and complete release evidence")

    next_auth = status["next_authorization"]
    next_gate = next_auth["gate"]
    if next_auth["task_id"].split("-", 1)[0] != next_gate:
        errors.append("$.next_authorization.task_id: task prefix must match next authorization gate")
    current_index, next_index = int(current_gate[1:]), int(next_gate[1:])
    if next_index not in {current_index, min(current_index + 1, 9)}:
        errors.append("$.next_authorization.gate: next authorization may only stay in gate or advance one gate")
    if next_auth["task_id"] == task_id:
        errors.append("$.next_authorization.task_id: next authorization cannot repeat the active task")
    return errors


def _read_document(path: Path, relative: str) -> tuple[str | None, str | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except (OSError, UnicodeError):
        return None, f"$.governed_documents: unreadable governed document: {relative}"


def _document_errors(status: dict[str, Any], repo_root: Path) -> list[str]:
    errors: list[str] = []
    root = repo_root.resolve()
    task = status["active_tasks"][0]
    for relative in status["governed_documents"]:
        path = (root / relative).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            errors.append(f"$.governed_documents: path escapes repository: {relative}")
            continue
        if not path.is_file():
            errors.append(f"$.governed_documents: missing document: {relative}")
            continue
        text, read_error = _read_document(path, relative)
        if read_error:
            errors.append(read_error)
            continue
        assert text is not None
        if relative == "CURRENT_TASK.md":
            mirrors = {
                "task_id": (r"^- Task ID: `([^`]+)`$", task["task_id"]),
                "gate": (r"^- Gate: (G[0-9])(?:\s|$)", status["current_gate"]),
                "risk": (r"^- Risk: `([^`]+)`$", task["risk"]),
                "state": (r"^- Status: `([^`]+)`$", task["state"]),
                "baseline": (r"^- Baseline: `([^`]+)`$", status["evidence"]["authorization_baseline_sha"]),
            }
            for label, (pattern, expected) in mirrors.items():
                match = re.search(pattern, text, re.MULTILINE)
                if match is None or match.group(1) != expected:
                    errors.append(f"$.governed_documents: CURRENT_TASK {label} conflicts with canonical status")
        elif relative == "PROJECT_MEMORY.md":
            if "not the current machine-state authority" not in text:
                errors.append("$.governed_documents: PROJECT_MEMORY must declare historical-only authority")
            if FORBIDDEN_CURRENT_MIRROR.search(text):
                errors.append("$.governed_documents: PROJECT_MEMORY contains a forbidden current-state mirror")
        elif FORBIDDEN_CURRENT_MIRROR.search(text):
            errors.append(f"$.governed_documents: forbidden current-state mirror in {relative}")
        if STALE_M_CLAIM.search(text):
            errors.append(f"$.governed_documents: stale current-state claim in {relative}")
    return errors


def _git(root: Path, *args: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    except (OSError, UnicodeError):
        return False, ""
    return result.returncode == 0, result.stdout.strip()


def _commit_exists(root: Path, sha: str) -> bool:
    return _git(root, "cat-file", "-e", f"{sha}^{{commit}}")[0]


def _is_ancestor(root: Path, older: str, newer: str) -> bool:
    return _git(root, "merge-base", "--is-ancestor", older, newer)[0]


def _status_at(root: Path, sha: str) -> dict[str, Any] | None:
    ok, text = _git(root, "show", f"{sha}:PROJECT_STATUS.yaml")
    if not ok:
        return None
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except (json.JSONDecodeError, ValueError):
        return None
    return value if type(value) is dict else None


def _subject_status_matches(status: dict[str, Any], subject: dict[str, Any] | None, expected_state: str) -> bool:
    if subject is None:
        return False
    try:
        return (
            subject["schema_version"] == "project-status.v2"
            and subject["active_tasks"][0]["task_id"] == status["active_tasks"][0]["task_id"]
            and subject["active_tasks"][0]["candidate_generation"] == status["active_tasks"][0]["candidate_generation"]
            and subject["active_tasks"][0]["state"] == expected_state
            and subject["evidence"]["authorization_baseline_sha"] == status["evidence"]["authorization_baseline_sha"]
        )
    except (KeyError, IndexError, TypeError):
        return False


def _repository_errors(status: dict[str, Any], status_path: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []
    root = repo_root.resolve()
    ok, top = _git(root, "rev-parse", "--show-toplevel")
    if not ok or Path(top).resolve() != root:
        return ["$: repository checks require the exact Git worktree root"]
    evidence = status["evidence"]
    baseline = evidence["authorization_baseline_sha"]
    if not _commit_exists(root, baseline):
        errors.append("$.evidence.authorization_baseline_sha: Git commit does not exist")
    for name, sha in [
        ("implementation_sha", evidence["implementation_sha"]),
        ("candidate.commit_sha", evidence["candidate"]["commit_sha"]),
        ("closure.commit_sha", evidence["closure"]["commit_sha"]),
        ("merged_main.commit_sha", evidence["merged_main"]["commit_sha"]),
        ("finalization.commit_sha", evidence["finalization"]["commit_sha"]),
    ]:
        if sha is not None and not _commit_exists(root, sha):
            errors.append(f"$.evidence.{name}: Git commit does not exist")
    task_state = status["active_tasks"][0]["state"]
    ok, head = _git(root, "rev-parse", "HEAD")
    if not ok:
        return ["$: repository HEAD is unavailable"]
    canonical_path = root / "PROJECT_STATUS.yaml"
    if status_path.resolve() == canonical_path.resolve() and task_state in {"awaiting_review", "accepted_pending_merge", "merged_verified", "closed"}:
        ok, committed = _git(root, "show", "HEAD:PROJECT_STATUS.yaml")
        try:
            working = canonical_path.read_text(encoding="utf-8").rstrip("\n")
        except (OSError, UnicodeError):
            working = ""
        if not ok or committed != working:
            errors.append("$: phase subject must be the exact committed repository HEAD")

    implementation = evidence["implementation_sha"]
    candidate = evidence["candidate"]["commit_sha"]
    closure = evidence["closure"]["commit_sha"]
    merged = evidence["merged_main"]["commit_sha"]
    finalization = evidence["finalization"]["commit_sha"]
    implicit_candidate = head if task_state == "awaiting_review" else candidate
    if implementation is not None and implicit_candidate is not None:
        if not _is_ancestor(root, baseline, implementation) or not _is_ancestor(root, implementation, implicit_candidate):
            errors.append("$.evidence: baseline -> implementation -> candidate ancestry is invalid")
    if candidate is not None:
        if not _subject_status_matches(status, _status_at(root, candidate), "awaiting_review"):
            errors.append("$.evidence.candidate.commit_sha: commit is not the matching delivered candidate phase")
        if not _is_ancestor(root, candidate, head):
            errors.append("$.evidence.candidate.commit_sha: candidate is unrelated to current HEAD")
    implicit_closure = head if task_state == "accepted_pending_merge" else closure
    if implicit_closure is not None and candidate is not None and not _is_ancestor(root, candidate, implicit_closure):
        errors.append("$.evidence.closure.commit_sha: candidate is not an ancestor of closure")
    if closure is not None and not _subject_status_matches(status, _status_at(root, closure), "accepted_pending_merge"):
        errors.append("$.evidence.closure.commit_sha: commit is not the matching closure phase")
    if merged is not None:
        if closure is None or not _is_ancestor(root, closure, merged):
            errors.append("$.evidence.merged_main.commit_sha: closure is not an ancestor of merged-main")
        ok, parents = _git(root, "rev-list", "--parents", "-n", "1", merged)
        if not ok or len(parents.split()) < 3:
            errors.append("$.evidence.merged_main.commit_sha: merged-main subject is not a merge commit")
    if finalization is not None:
        if merged is None or not _is_ancestor(root, merged, finalization):
            errors.append("$.evidence.finalization.commit_sha: merged-main is not an ancestor of finalization")
        if not _subject_status_matches(status, _status_at(root, finalization), "merged_verified"):
            errors.append("$.evidence.finalization.commit_sha: commit is not the matching finalization phase")
    return errors


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def validate(status_path: Path, schema_path: Path, repo_root: Path | None) -> list[str]:
    try:
        status = json.loads(status_path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys)
        schema = json.loads(schema_path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return [f"$: unreadable JSON-compatible status/schema: {type(exc).__name__}"]
    if type(status) is not dict or type(schema) is not dict:
        return ["$: status and schema roots must be objects"]
    try:
        errors = _schema_errors(status, schema, schema)
    except (KeyError, TypeError, ValueError):
        return ["$: schema is malformed or unsupported"]
    if not errors:
        errors.extend(_semantic_errors(status))
        if repo_root is not None:
            errors.extend(_document_errors(status, repo_root))
            errors.extend(_repository_errors(status, status_path, repo_root))
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("status", nargs="?", type=Path, default=DEFAULT_STATUS)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--repo-root", type=Path, default=None, help="check documents and Git phase identity")
    args = parser.parse_args()
    errors = validate(args.status, args.schema, args.repo_root)
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        return 1
    print(f"OK {args.status}: project-status.v2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
