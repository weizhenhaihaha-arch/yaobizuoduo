#!/usr/bin/env python3
"""Fail-closed project-status v2 validator using only the Python standard library."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import os
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATUS = ROOT / "PROJECT_STATUS.yaml"
DEFAULT_SCHEMA = ROOT / "schemas" / "project_status.schema.json"
BOOTSTRAP_TASK = "G0-T01"
BOOTSTRAP_BASELINE = "7aadae13efd45023d19bf8a280f7680667c930fa"
LEDGER_ANCHOR = "fa047696761f235cb1e5cd94bbf1881b49e4bb21"
LEDGER_DIGEST = "9519f9121f043f777473a631e804c074f5e8c62ed407ac6c0060ec4e9c7a78aa"
LEDGER_REPOSITORY = ("weizhenhaihaha-arch", "yaobizuoduo")
SCHEMA_BOOTSTRAP_SUBJECT = "abf310da75676fed15d697786886b57f107854ed"
SCHEMA_BOOTSTRAP_OLD_DIGEST = "f0b1af40eac4adfad78e30cdc9dcb3104ed3c1cfbeac7a506c4128231c5a1693"
SCHEMA_PREAUTHORITY_HISTORY_DIGEST = "0783dfa9d3ec8c281fbd175ae983f23d116edca577d6bf3d3857f5e728c95fa4"
SCHEMA_COMPATIBILITY_RULE = "strict-current-schema-revalidation"
SCHEMA_CONTROL_PATH = "schemas/project_status.schema-migration-control.json"
SCHEMA_CONTROL_VERSION = "schema-migration-control.v1"
SCHEMA_CONTROL_PURPOSE = "project-status-schema-migration"
SCHEMA_CONTROL_BOOTSTRAP_PARENT = "3128dd4a5c767d1a8b292a68c3418299e9d89ac3"
MANDATORY_DOCUMENTS = {
    "AGENTS.md",
    "DEVELOPMENT_WORKFLOW.md",
    "AG_WORK_LOOP.md",
    "DESIGN.md",
    "CURRENT_TASK.md",
    "PROJECT_MEMORY.md",
}

TRANSITIONS = {
    "planned": {"authorized"},
    "authorized": {"in_progress"},
    "in_progress": {"awaiting_review", "blocked"},
    "awaiting_review": {"returned", "blocked", "accepted_pending_merge"},
    "returned": {"in_progress", "blocked"},
    "blocked": set(),
    "accepted_pending_merge": {"merged_verified"},
    "merged_verified": {"closed"},
    "closed": {"authorized"},
}
MATURITY = {"OFFLINE_EVIDENCE_ACCEPTED": 0, "INTEGRATION_ACCEPTED": 1, "PAPER_VALIDATED": 2, "RELEASE_READY": 3}
GATE_CEILING = {**{f"G{i}": 0 for i in range(6)}, "G6": 1, "G7": 1, "G8": 2, "G9": 3}
FORBIDDEN_CURRENT_MIRROR = re.compile(
    r"^\s*(?:[-*]\s*)?(?:gate|task\s+id|status|risk|baseline|maturity|current\s+(?:gate|task|status|state|maturity|stage|milestone)|当前(?:门禁|任务|状态|成熟度|阶段|里程碑))\s*[:：]",
    re.IGNORECASE | re.MULTILINE,
)
STALE_M_CLAIM = re.compile(
    r"(?:当前项目处于\s*M[0-9]|当前里程碑[：:]\s*M[0-9]|当前任务[：:]\s*`?M[0-9]-T[0-9]+|current\s+(?:milestone|stage|task)\s*[:：]\s*`?M[0-9])",
    re.IGNORECASE,
)


def _type_matches(value: Any, expected: str) -> bool:
    return {"object": type(value) is dict, "array": type(value) is list, "string": type(value) is str, "integer": type(value) is int, "null": value is None, "boolean": type(value) is bool}.get(expected, False)


def _typed_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(_typed_equal(left[key], right[key]) for key in left)
    if type(left) in {list, tuple}:
        return len(left) == len(right) and all(_typed_equal(a, b) for a, b in zip(left, right))
    return left == right


def _payload_digest(value: dict[str, Any]) -> str:
    payload = {key: item for key, item in value.items() if key != "payload_sha256"}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


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
    if "const" in rule and not _typed_equal(value, rule["const"]):
        errors.append(f"{path}: value does not match required constant")
    if "enum" in rule and not any(_typed_equal(value, item) for item in rule["enum"]):
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
        if rule.get("uniqueItems") is True:
            serialized = [json.dumps(item, sort_keys=True, separators=(",", ":")) for item in value]
            if len(serialized) != len(set(serialized)):
                errors.append(f"{path}: duplicate items are forbidden")
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
    if status in {"pending", "success", "failure"} and ci.get("url") is not None:
        url_run = re.search(r"/actions/runs/([1-9][0-9]*)$", ci["url"])
        if url_run is None or url_run.group(1) != ci.get("run_id"):
            errors.append(f"{path}: CI URL run number must equal run_id")
    return errors


def _governed_list_errors(documents: list[str]) -> list[str]:
    errors: list[str] = []
    if not MANDATORY_DOCUMENTS.issubset(set(documents)):
        errors.append("$.governed_documents: mandatory canonical documents are missing")
    normalized: list[str] = []
    for item in documents:
        pure = PurePosixPath(item)
        canonical = pure.as_posix()
        if canonical != item or item.startswith("/") or ".." in pure.parts or "." in pure.parts:
            errors.append("$.governed_documents: document paths must be canonical repository-relative identities")
        normalized.append(canonical)
    if len(normalized) != len(set(normalized)):
        errors.append("$.governed_documents: duplicate or aliased document identities are forbidden")
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
    errors.extend(_governed_list_errors(status["governed_documents"]))
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
    if state == "in_progress" and status["blockers"]:
        errors.append("$.blockers: in_progress state must not retain blockers")

    if state == "in_progress" and transition["from"] == "returned":
        if task["candidate_generation"] < 2:
            errors.append("$.active_tasks[0].candidate_generation: returned repair must increment generation")
        if any(ci["subject_sha"] is not None or ci["run_id"] is not None or ci["url"] is not None for _, ci in _all_ci(evidence)):
            errors.append("$: returned repair must atomically clear all CI identities")

    exception = status["bootstrap_exception"]
    exception_consumed = exception is not None and exception["status"] == "consumed" and _typed_equal(exception["uses"], 1)
    if exception is not None:
        if task_id != BOOTSTRAP_TASK or evidence["authorization_baseline_sha"] != BOOTSTRAP_BASELINE:
            errors.append("$.bootstrap_exception: exception is restricted to the authorized G0-T01 baseline")
        expected_status = "consumed" if state in accepted_states else "available"
        expected_uses = 1 if state in accepted_states else 0
        if not _typed_equal(exception["status"], expected_status) or not _typed_equal(exception["uses"], expected_uses):
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
        if current_gate != "G9" or state != "closed" or status["release"]["product_owner_approval"] is None or status["release"]["release_manifest"] is None:
            errors.append("$.capability.maturity: RELEASE_READY requires closed G9 and traceable approval/manifest identities")
    if current_gate != "G9" and any(value is not None for value in status["release"].values()):
        errors.append("$.release: release identities are forbidden before G9")

    next_auth = status["next_authorization"]
    next_gate = next_auth["gate"]
    if next_auth["task_id"].split("-", 1)[0] != next_gate:
        errors.append("$.next_authorization.task_id: task prefix must match next authorization gate")
    current_index, next_index = int(current_gate[1:]), int(next_gate[1:])
    if next_index not in {current_index, min(current_index + 1, 9)}:
        errors.append("$.next_authorization.gate: next authorization may only stay in gate or advance one gate")
    if next_auth["task_id"] == task_id:
        errors.append("$.next_authorization.task_id: next authorization cannot repeat the active task")
    if next_gate == current_gate:
        current_task_number = int(task_id.rsplit("T", 1)[1])
        next_task_number = int(next_auth["task_id"].rsplit("T", 1)[1])
        if next_task_number <= current_task_number:
            errors.append("$.next_authorization.task_id: same-gate task sequence must move forward")
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
    resolved_identities: set[Path] = set()
    for relative in status["governed_documents"]:
        unresolved = root / relative
        cursor = root
        for component in PurePosixPath(relative).parts:
            cursor /= component
            if os.path.islink(cursor):
                errors.append(f"$.governed_documents: symlink path component is forbidden: {relative}")
                break
        path = unresolved.resolve()
        try:
            path.relative_to(root)
        except ValueError:
            errors.append(f"$.governed_documents: path escapes repository: {relative}")
            continue
        if path in resolved_identities:
            errors.append("$.governed_documents: duplicate or aliased resolved document identities are forbidden")
        else:
            resolved_identities.add(path)
        if not path.is_file():
            errors.append(f"$.governed_documents: missing document: {relative}")
            continue
        ok, tree_entry = _git(root, "ls-tree", "HEAD", "--", relative)
        fields = tree_entry.split(None, 3) if ok else []
        if len(fields) != 4 or fields[0] not in {"100644", "100755"} or fields[1] != "blob":
            errors.append(f"$.governed_documents: path must be a regular Git blob: {relative}")
        parent = PurePosixPath(relative).parent
        if parent.as_posix() != ".":
            accumulated: list[str] = []
            for component in parent.parts:
                accumulated.append(component)
                ok, kind = _git(root, "cat-file", "-t", f"HEAD:{'/'.join(accumulated)}")
                if not ok or kind != "tree":
                    errors.append(f"$.governed_documents: parent must be a regular Git tree: {relative}")
                    break
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
                matches = re.findall(pattern, text, re.MULTILINE)
                if len(matches) != 1 or matches[0] != expected:
                    errors.append(f"$.governed_documents: CURRENT_TASK {label} conflicts with canonical status")
            extra_current = re.sub(r"^- (?:Task ID|Gate|Risk|Status|Baseline):.*$", "", text, flags=re.MULTILINE)
            if FORBIDDEN_CURRENT_MIRROR.search(extra_current):
                errors.append("$.governed_documents: CURRENT_TASK contains an unsupported current-state mirror")
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


def _git_bytes(root: Path, *args: str) -> tuple[bool, bytes]:
    try:
        result = subprocess.run(["git", *args], cwd=root, capture_output=True, check=False)
    except OSError:
        return False, b""
    return result.returncode == 0, result.stdout


def _github_repository_identity(remote_url: str) -> tuple[str, str] | None:
    match = re.fullmatch(r"https://github\.com/([^/]+)/([^/]+?)(?:\.git)?", remote_url)
    if match is None:
        match = re.fullmatch(r"git@github\.com:([^/]+)/([^/]+?)(?:\.git)?", remote_url)
    if match is None:
        return None
    return match.group(1).lower(), match.group(2).lower()


def _ci_repository_errors(evidence: dict[str, Any], repository: tuple[str, str] | None) -> list[str]:
    errors: list[str] = []
    for path, ci in _all_ci(evidence):
        if ci["status"] not in {"pending", "success", "failure"}:
            continue
        match = re.fullmatch(r"https://github\.com/([^/]+)/([^/]+)/actions/runs/([1-9][0-9]*)", ci["url"])
        if repository is None or match is None or (match.group(1).lower(), match.group(2).lower()) != repository:
            errors.append(f"{path}: CI URL repository must match canonical origin")
        elif match.group(3) != ci["run_id"]:
            errors.append(f"{path}: CI URL run number must equal run_id")
    return errors


def _release_identity_errors(status: dict[str, Any], root: Path, main_ref: str) -> list[str]:
    errors: list[str] = []
    release = status["release"]
    resolved: dict[str, dict[str, Any]] = {}
    for name in ("product_owner_approval", "release_manifest"):
        identity = release[name]
        if identity is None:
            continue
        commit_sha, path, expected_digest = identity["commit_sha"], identity["path"], identity["sha256"]
        pure_path = PurePosixPath(path)
        if pure_path.as_posix() != path or path.startswith("/") or "." in pure_path.parts or ".." in pure_path.parts:
            errors.append(f"$.release.{name}.path: artifact path must be canonical and repository-relative")
            continue
        if not _commit_exists(root, commit_sha):
            errors.append(f"$.release.{name}.commit_sha: Git commit does not exist")
            continue
        if not _is_ancestor(root, commit_sha, main_ref):
            errors.append(f"$.release.{name}.commit_sha: evidence is not reachable from authoritative main")
        ok, payload = _git_bytes(root, "show", f"{commit_sha}:{path}")
        if not ok or hashlib.sha256(payload).hexdigest() != expected_digest:
            errors.append(f"$.release.{name}: immutable artifact content does not match sha256")
            continue
        try:
            value = json.loads(payload.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
        except (UnicodeError, json.JSONDecodeError, ValueError):
            errors.append(f"$.release.{name}: immutable artifact is not valid canonical JSON evidence")
            continue
        if type(value) is not dict or value.get("project") != status["project"]:
            errors.append(f"$.release.{name}: immutable artifact project identity mismatch")
            continue
        resolved[name] = value
    approval = resolved.get("product_owner_approval")
    manifest = resolved.get("release_manifest")
    manifest_identity = release.get("release_manifest")
    approval_keys = {"schema_version", "project", "decision", "approving_authority", "authorization_id", "release_manifest_sha256"}
    if approval is not None and (
        set(approval) != approval_keys
        or approval.get("schema_version") != "product-owner-approval.v1"
        or approval.get("decision") != "go"
        or type(approval.get("approving_authority")) is not str
        or not approval["approving_authority"].strip()
        or type(approval.get("authorization_id")) is not str
        or re.fullmatch(r"AUTH-[A-Za-z0-9._-]+", approval["authorization_id"]) is None
        or manifest_identity is None
        or approval.get("release_manifest_sha256") != manifest_identity["sha256"]
    ):
        errors.append("$.release.product_owner_approval: artifact is not an explicit go bound to the release manifest")
    evidence_map: dict[str, str] = {}
    manifest_evidence = manifest.get("evidence") if manifest is not None else None
    if type(manifest_evidence) is list:
        for item in manifest_evidence:
            if type(item) is dict and set(item) == {"phase", "subject_sha"} and type(item.get("phase")) is str and type(item.get("subject_sha")) is str:
                evidence_map[item["phase"]] = item["subject_sha"]
    bad_manifest_shape = (
        manifest is not None
        and (
            set(manifest) != {"schema_version", "project", "release_sha", "evidence"}
            or manifest.get("schema_version") != "release-evidence.v1"
            or re.fullmatch(r"[0-9a-f]{40}", str(manifest.get("release_sha", ""))) is None
            or type(manifest_evidence) is not list
            or len(manifest_evidence) != 4
            or set(evidence_map) != {"candidate", "closure", "merged_main", "finalization"}
        )
    )
    if bad_manifest_shape:
        errors.append("$.release.release_manifest: artifact does not prove complete immutable release evidence")
    elif manifest is not None:
        release_sha = manifest["release_sha"]
        expected = {
            "candidate": status["evidence"]["candidate"]["commit_sha"],
            "closure": status["evidence"]["closure"]["commit_sha"],
            "merged_main": status["evidence"]["merged_main"]["commit_sha"],
            "finalization": status["evidence"]["finalization"]["commit_sha"],
        }
        if release_sha != expected["finalization"] or evidence_map != expected:
            errors.append("$.release.release_manifest: release_sha and evidence must bind the exact finalization chain")
        elif not _commit_exists(root, release_sha) or not _is_first_parent_ancestor(root, release_sha, main_ref):
            errors.append("$.release.release_manifest: release_sha is not on authoritative main first-parent history")
    return errors


def _commit_exists(root: Path, sha: str) -> bool:
    return _git(root, "cat-file", "-e", f"{sha}^{{commit}}")[0]


def _is_ancestor(root: Path, older: str, newer: str) -> bool:
    return _git(root, "merge-base", "--is-ancestor", older, newer)[0]


def _is_first_parent_ancestor(root: Path, older: str, newer: str) -> bool:
    ok, history = _git(root, "rev-list", "--first-parent", newer)
    return ok and older in history.splitlines()


def _status_at(root: Path, sha: str) -> dict[str, Any] | None:
    ok, text = _git(root, "show", f"{sha}:PROJECT_STATUS.yaml")
    if not ok:
        return None
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except (json.JSONDecodeError, ValueError):
        return None
    return value if type(value) is dict else None


def _schema_at(root: Path, sha: str) -> dict[str, Any] | None:
    ok, text = _git(root, "show", f"{sha}:schemas/project_status.schema.json")
    if not ok:
        return None
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except (json.JSONDecodeError, ValueError):
        return None
    return value if type(value) is dict else None


def _schema_digest_at(root: Path, sha: str) -> str | None:
    ok, payload = _git_bytes(root, "show", f"{sha}:schemas/project_status.schema.json")
    return hashlib.sha256(payload).hexdigest() if ok else None


def _schema_control_from_bytes(payload: bytes) -> dict[str, Any] | None:
    try:
        value = json.loads(payload.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
    except (UnicodeError, json.JSONDecodeError, ValueError):
        return None
    return value if type(value) is dict else None


def _schema_control_at(root: Path, sha: str) -> dict[str, Any] | None:
    ok, payload = _git_bytes(root, "show", f"{sha}:{SCHEMA_CONTROL_PATH}")
    return _schema_control_from_bytes(payload) if ok else None


def _schema_control_errors(control: Any, status: dict[str, Any]) -> list[str]:
    if type(control) is not dict:
        return ["$.schema_migration_control: required canonical control artifact is unreadable"]
    common = {"schema_version", "project", "decision", "payload_sha256"}
    no_migration_keys = common | {"current_revision", "current_sha256"}
    authorization_keys = common | {
        "task_id", "gate", "purpose", "from_revision", "from_sha256",
        "to_revision", "to_sha256", "compatibility_rule",
    }
    decision = control.get("decision")
    expected_keys = no_migration_keys if decision == "no_migration" else authorization_keys if decision == "authorize_migration" else set()
    if not expected_keys or set(control) != expected_keys:
        return ["$.schema_migration_control: invalid control artifact shape or decision"]
    if (
        type(control.get("schema_version")) is not str
        or type(control.get("project")) is not str
        or type(control.get("payload_sha256")) is not str
        or control["schema_version"] != SCHEMA_CONTROL_VERSION
        or control["project"] != "yaobizuoduo"
        or re.fullmatch(r"[0-9a-f]{64}", control["payload_sha256"]) is None
        or not _typed_equal(control["payload_sha256"], _payload_digest(control))
    ):
        return ["$.schema_migration_control: identity or payload digest mismatch"]
    authority = status.get("schema_authority")
    task = status["active_tasks"][0]
    if decision == "no_migration":
        valid = (
            type(control.get("current_revision")) is int
            and type(control.get("current_sha256")) is str
            and _typed_equal(control["current_revision"], authority.get("revision"))
            and _typed_equal(control["current_sha256"], authority.get("sha256"))
        )
        return [] if valid else ["$.schema_migration_control: explicit no-migration decision must bind current schema authority"]
    exact_types = (
        type(control.get("task_id")) is str
        and type(control.get("gate")) is str
        and type(control.get("purpose")) is str
        and type(control.get("from_revision")) is int
        and type(control.get("from_sha256")) is str
        and type(control.get("to_revision")) is int
        and type(control.get("to_sha256")) is str
        and type(control.get("compatibility_rule")) is str
    )
    if not exact_types:
        return ["$.schema_migration_control: authorization fields require exact canonical types"]
    valid = (
        task["state"] == "authorized"
        and _typed_equal(control["task_id"], task["task_id"])
        and _typed_equal(control["gate"], status["current_gate"])
        and control["purpose"] == SCHEMA_CONTROL_PURPOSE
        and _typed_equal(control["from_revision"], authority.get("revision"))
        and _typed_equal(control["from_sha256"], authority.get("sha256"))
        and _typed_equal(control["to_revision"], authority.get("revision") + 1)
        and re.fullmatch(r"[0-9a-f]{64}", control["to_sha256"]) is not None
        and not _typed_equal(control["to_sha256"], authority.get("sha256"))
        and control["compatibility_rule"] == SCHEMA_COMPATIBILITY_RULE
    )
    return [] if valid else ["$.schema_migration_control: authorization must pre-bind task, gate, purpose, compatibility, and exact schema transition"]


def _schema_control_document_errors(status: dict[str, Any], schema_path: Path) -> list[str]:
    if type(status.get("transition_ledger")) is not dict:
        return []
    path = schema_path.parent / Path(SCHEMA_CONTROL_PATH).name
    try:
        control = _schema_control_from_bytes(path.read_bytes())
    except OSError:
        control = None
    return _schema_control_errors(control, status)


def _repository_visible_commits(root: Path) -> list[str] | None:
    # Git cannot enumerate absent or unreachable objects. The enforceable boundary is every
    # commit reachable from a repository-visible local branch or fetched remote-tracking ref.
    ok, refs_text = _git(root, "for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes")
    refs = refs_text.splitlines() if ok else []
    if not refs:
        return None
    ok, commits_text = _git(root, "rev-list", "--topo-order", *refs)
    return commits_text.splitlines() if ok else None


def _schema_migration_consumers(root: Path, authorization_sha: str) -> set[str] | None:
    commits = _repository_visible_commits(root)
    if commits is None:
        return None
    consumers: set[str] = set()
    for sha in commits:
        node = _status_at(root, sha)
        authority = node.get("schema_authority") if type(node) is dict else None
        migration = authority.get("migration") if type(authority) is dict else None
        if type(migration) is not dict or not _typed_equal(migration.get("authorization_sha"), authorization_sha):
            continue
        ok, parents_text = _git(root, "rev-list", "--parents", "-n", "1", sha)
        parts = parents_text.split() if ok else []
        parent = _status_at(root, parts[1]) if len(parts) >= 2 else None
        parent_authority = parent.get("schema_authority") if type(parent) is dict else None
        if not _typed_equal(authority, parent_authority):
            consumers.add(sha)
    return consumers


def _schema_digest_history_errors(root: Path, candidate_sha: str) -> list[str]:
    ok, commits_text = _git(root, "rev-list", "--first-parent", candidate_sha)
    if not ok:
        return ["$.schema_authority: immutable schema digest history is unavailable"]
    revisions: dict[int, str] = {}
    digests: dict[str, int] = {}
    for sha in reversed(commits_text.splitlines()):
        node = _status_at(root, sha)
        authority = node.get("schema_authority") if type(node) is dict else None
        if type(authority) is not dict:
            continue
        pairs: list[tuple[Any, Any]] = [(authority.get("revision"), authority.get("sha256"))]
        migration = authority.get("migration")
        if type(migration) is dict:
            pairs.append((migration.get("from_revision"), migration.get("from_sha256")))
        for revision, digest in pairs:
            if type(revision) is not int or type(digest) is not str:
                continue
            if revision in revisions and not _typed_equal(revisions[revision], digest):
                return ["$.schema_authority: one revision cannot have multiple immutable schema digests"]
            if digest in digests and not _typed_equal(digests[digest], revision):
                return ["$.schema_authority: higher revision cannot reuse an earlier schema digest"]
            revisions[revision] = digest
            digests[digest] = revision
    return []


def _schema_authorization_reuse_errors(root: Path, authorization_sha: str, candidate_sha: str) -> list[str]:
    consumers = _schema_migration_consumers(root, authorization_sha)
    if consumers is None:
        return ["$.schema_authority: repository-visible migration consumption set is unavailable"]
    if consumers != {candidate_sha}:
        return ["$.schema_authority: migration authorization must have exactly one repository-visible consumer"]
    ok, remote_main = _git(root, "rev-parse", "--verify", "refs/remotes/origin/main")
    if not ok or not _is_first_parent_ancestor(root, candidate_sha, remote_main):
        return ["$.schema_authority: migration consumption must be on canonical origin/main first-parent history"]
    return []


def _schema_authorization_reused(root: Path, candidate_sha: str, authorization_sha: str) -> bool:
    return bool(_schema_authorization_reuse_errors(root, authorization_sha, candidate_sha))


def _schema_authority_document_errors(status: dict[str, Any], schema_path: Path) -> list[str]:
    if type(status.get("transition_ledger")) is not dict:
        return []
    authority = status.get("schema_authority")
    if type(authority) is not dict:
        return ["$.schema_authority: canonical ledger status requires schema authority"]
    if set(authority) != {"revision", "sha256", "migration"}:
        return ["$.schema_authority: invalid authority shape"]
    revision, digest, migration = authority["revision"], authority["sha256"], authority["migration"]
    if type(revision) is not int or revision < 1 or type(digest) is not str or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        return ["$.schema_authority: revision and digest require exact canonical types"]
    try:
        actual_digest = hashlib.sha256(schema_path.read_bytes()).hexdigest()
    except OSError:
        return ["$.schema_authority: canonical schema bytes are unreadable"]
    errors: list[str] = []
    if digest != actual_digest:
        errors.append("$.schema_authority.sha256: canonical schema content digest mismatch")
    migration_keys = {"from_revision", "from_sha256", "to_revision", "to_sha256", "authorization_sha", "compatibility_rule", "preauthority_history_sha256"}
    if type(migration) is not dict or set(migration) != migration_keys:
        errors.append("$.schema_authority.migration: explicit migration identity is required")
        return errors
    from_revision, to_revision = migration["from_revision"], migration["to_revision"]
    from_digest, to_digest = migration["from_sha256"], migration["to_sha256"]
    authorization_sha, compatibility = migration["authorization_sha"], migration["compatibility_rule"]
    preauthority_digest = migration["preauthority_history_sha256"]
    if (
        type(from_revision) is not int
        or type(to_revision) is not int
        or type(from_digest) is not str
        or type(to_digest) is not str
        or type(authorization_sha) is not str
        or type(compatibility) is not str
        or (preauthority_digest is not None and type(preauthority_digest) is not str)
    ):
        errors.append("$.schema_authority.migration: migration fields require exact canonical types")
        return errors
    if not _typed_equal(to_revision, from_revision + 1) or not _typed_equal(to_revision, revision):
        errors.append("$.schema_authority.migration: schema revision must advance exactly one step")
    if to_digest != digest or compatibility != SCHEMA_COMPATIBILITY_RULE:
        errors.append("$.schema_authority.migration: target digest and compatibility rule must bind the current schema")
    if re.fullmatch(r"[0-9a-f]{64}", from_digest) is None or re.fullmatch(r"[0-9a-f]{64}", to_digest) is None or re.fullmatch(r"[0-9a-f]{40}", authorization_sha) is None:
        errors.append("$.schema_authority.migration: migration identities have invalid format")
    if revision == 1:
        if preauthority_digest != SCHEMA_PREAUTHORITY_HISTORY_DIGEST:
            errors.append("$.schema_authority.migration: bootstrap must bind the sealed pre-authority schema history")
    elif preauthority_digest is not None:
        errors.append("$.schema_authority.migration: later migrations must not reuse the bootstrap history seal")
    return errors


def _schema_authority_continuity_errors(
    status: dict[str, Any], parent: dict[str, Any], parent_sha: str, root: Path, child_sha: str | None = None
) -> list[str]:
    current = status.get("schema_authority")
    previous = parent.get("schema_authority")
    if current is None and previous is None:
        return []
    if previous is None:
        projected = dict(status)
        projected.pop("schema_authority", None)
        migration = current.get("migration") if type(current) is dict else None
        expected_bootstrap = (
            type(current) is dict
            and _typed_equal(current.get("revision"), 1)
            and type(migration) is dict
            and _typed_equal(migration.get("from_revision"), 0)
            and migration.get("from_sha256") == SCHEMA_BOOTSTRAP_OLD_DIGEST
            and migration.get("authorization_sha") == SCHEMA_BOOTSTRAP_SUBJECT
            and migration.get("preauthority_history_sha256") == SCHEMA_PREAUTHORITY_HISTORY_DIGEST
            and parent_sha == SCHEMA_BOOTSTRAP_SUBJECT
            and status["project"] == "yaobizuoduo"
            and status["active_tasks"][0]["task_id"] == BOOTSTRAP_TASK
            and status["evidence"]["authorization_baseline_sha"] == BOOTSTRAP_BASELINE
            and _typed_equal(projected, parent)
            and _schema_digest_at(root, parent_sha) == SCHEMA_BOOTSTRAP_OLD_DIGEST
        )
        return [] if expected_bootstrap else ["$.schema_authority: first authority creation must be the exact generation-6 bootstrap migration"]
    current_control = _schema_control_at(root, child_sha) if child_sha is not None else _schema_control_from_bytes((root / SCHEMA_CONTROL_PATH).read_bytes()) if (root / SCHEMA_CONTROL_PATH).is_file() else None
    parent_control = _schema_control_at(root, parent_sha)
    if _typed_equal(current, previous):
        if current_control is None and parent_control is None:
            return []
        if parent_control is None:
            bootstrap = (
                parent_sha == SCHEMA_CONTROL_BOOTSTRAP_PARENT
                and type(current_control) is dict
                and current_control.get("decision") == "no_migration"
                and status["project"] == "yaobizuoduo"
                and status["active_tasks"][0]["task_id"] == BOOTSTRAP_TASK
                and status["active_tasks"][0]["state"] == "in_progress"
                and not _schema_control_errors(current_control, status)
            )
            return [] if bootstrap else ["$.schema_migration_control: first control creation is not the authorized generation-7 bootstrap"]
        if _typed_equal(current_control, parent_control):
            return []
        if type(current_control) is dict and current_control.get("decision") == "authorize_migration":
            parent_task, current_task = parent["active_tasks"][0], status["active_tasks"][0]
            remote_ok, remote_main = _git(root, "rev-parse", "--verify", "refs/remotes/origin/" + status["authoritative_main_ref"].removeprefix("refs/heads/"))
            authorized = (
                type(parent_control) is dict
                and parent_control.get("decision") == "no_migration"
                and parent_task["state"] == "closed"
                and current_task["state"] == "authorized"
                and current_task["transition"] == {"from": "closed", "to": "authorized"}
                and _typed_equal(status["evidence"]["authorization_baseline_sha"], parent_sha)
                and remote_ok
                and _is_first_parent_ancestor(root, parent_sha, remote_main)
                and not _schema_control_errors(current_control, status)
            )
            return [] if authorized else ["$.schema_migration_control: migration authorization must be an authorized handoff from authoritative main"]
        return ["$.schema_migration_control: authorization cannot be changed, discarded, or consumed without its exact migration"]
    migration = current.get("migration") if type(current) is dict else None
    parent_task, current_task = parent["active_tasks"][0], status["active_tasks"][0]
    control_valid = (
        type(parent_control) is dict
        and parent_control.get("decision") == "authorize_migration"
        and not _schema_control_errors(parent_control, parent)
        and type(current_control) is dict
        and current_control.get("decision") == "no_migration"
        and not _schema_control_errors(current_control, status)
    )
    remote_ok, remote_main = _git(root, "rev-parse", "--verify", "refs/remotes/origin/" + status["authoritative_main_ref"].removeprefix("refs/heads/"))
    authorization_baseline = parent["evidence"]["authorization_baseline_sha"]
    valid = (
        type(current) is dict
        and type(previous) is dict
        and type(migration) is dict
        and control_valid
        and parent_task["state"] == "authorized"
        and current_task["state"] == "in_progress"
        and current_task["transition"] == {"from": "authorized", "to": "in_progress"}
        and _typed_equal(current_task["task_id"], parent_task["task_id"])
        and _typed_equal(status["current_gate"], parent["current_gate"])
        and _typed_equal(current_task["candidate_generation"], parent_task["candidate_generation"])
        and _typed_equal(migration.get("from_revision"), previous.get("revision"))
        and _typed_equal(migration.get("from_sha256"), previous.get("sha256"))
        and _typed_equal(migration.get("to_revision"), current.get("revision"))
        and _typed_equal(migration.get("to_sha256"), current.get("sha256"))
        and _typed_equal(migration.get("authorization_sha"), parent_sha)
        and _typed_equal(migration.get("compatibility_rule"), SCHEMA_COMPATIBILITY_RULE)
        and migration.get("preauthority_history_sha256") is None
        and _schema_digest_at(root, parent_sha) == previous.get("sha256")
        and _typed_equal(parent_control.get("from_revision"), previous.get("revision"))
        and _typed_equal(parent_control.get("from_sha256"), previous.get("sha256"))
        and _typed_equal(parent_control.get("to_revision"), current.get("revision"))
        and _typed_equal(parent_control.get("to_sha256"), current.get("sha256"))
        and _typed_equal(parent_control.get("task_id"), current_task["task_id"])
        and _typed_equal(parent_control.get("gate"), status["current_gate"])
        and _typed_equal(parent_control.get("purpose"), SCHEMA_CONTROL_PURPOSE)
        and remote_ok
        and _is_first_parent_ancestor(root, authorization_baseline, remote_main)
    )
    if not valid:
        return ["$.schema_authority: schema migration is unauthorized or discontinuous"]
    if child_sha is None:
        ok, resolved_child = _git(root, "rev-parse", "HEAD")
        if not ok:
            return ["$.schema_authority: migration consumer identity is unavailable"]
        child_sha = resolved_child
    errors = _schema_authorization_reuse_errors(root, parent_sha, child_sha)
    errors.extend(_schema_digest_history_errors(root, child_sha))
    return errors


def _committed_status_errors(root: Path, sha: str, current_schema: dict[str, Any], use_current_schema: bool = False) -> tuple[dict[str, Any] | None, list[str]]:
    status = _status_at(root, sha)
    if status is None:
        return None, [f"$: first-parent status at {sha[:12]} is unreadable"]
    schema = current_schema if use_current_schema else (_schema_at(root, sha) or current_schema)
    if schema is None:
        return status, [f"$: first-parent status at {sha[:12]} has no readable schema"]
    try:
        errors = _schema_errors(status, schema, schema)
    except (KeyError, TypeError, ValueError):
        errors = ["schema is malformed or unsupported"]
    return status, [f"$: first-parent status at {sha[:12]} fails schema validation: {item}" for item in errors]


def _bootstrap_identity(value: Any) -> tuple[Any, Any, Any] | None:
    if type(value) is not dict:
        return None
    return (value.get("exception_id"), value.get("task_id"), value.get("authorization_baseline_sha"))


def _ci_continuity_errors(status: dict[str, Any], parent: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for (path, current), (_, previous) in zip(_all_ci(status["evidence"]), _all_ci(parent["evidence"])):
        old_state, new_state = previous["status"], current["status"]
        old_identity = (previous["subject_sha"], previous["run_id"], previous["url"])
        new_identity = (current["subject_sha"], current["run_id"], current["url"])
        if old_state in {"success", "failure"} and not _typed_equal(current, previous):
            errors.append(f"{path}: terminal CI evidence is immutable")
        elif old_state == "pending":
            if new_state not in {"pending", "success", "failure"} or not _typed_equal(new_identity, old_identity):
                errors.append(f"{path}: pending CI may only become terminal for the same immutable run")
        elif old_state in {"not_established", "not_run"} and new_state in {"not_established", "not_run"} and not _typed_equal(current, previous):
            errors.append(f"{path}: inactive CI state cannot be relabelled")
    return errors


def _cleared_handoff(status: dict[str, Any]) -> bool:
    evidence = status["evidence"]
    empty_ci = all(ci["status"] in {"not_established", "not_run"} and ci["subject_sha"] is None and ci["run_id"] is None and ci["url"] is None for _, ci in _all_ci(evidence))
    return (
        evidence["implementation_sha"] is None
        and all(evidence[name]["commit_sha"] is None for name in ("candidate", "closure", "merged_main", "finalization"))
        and evidence["candidate"]["local_verification"] == {"status": "pending", "subject": "delivery_head"}
        and empty_ci
        and status["review"] == {"code_security": "pending", "architecture": "pending", "reviewed_candidate_sha": None}
        and status["blockers"] == []
        and status["bootstrap_exception"] is None
    )


def _maturity_upgrade_allowed(status: dict[str, Any], previous: str, current: str) -> bool:
    gate_rules = {
        ("OFFLINE_EVIDENCE_ACCEPTED", "INTEGRATION_ACCEPTED"): ("G6", "G7"),
        ("INTEGRATION_ACCEPTED", "PAPER_VALIDATED"): ("G8", "G9"),
        ("PAPER_VALIDATED", "RELEASE_READY"): ("G9", "G9"),
    }
    rule = gate_rules.get((previous, current))
    if rule is None:
        return False
    task = status["active_tasks"][0]
    evidence = status["evidence"]
    candidate = evidence["candidate"]
    all_phase_shas = [candidate["commit_sha"], evidence["closure"]["commit_sha"], evidence["merged_main"]["commit_sha"], evidence["finalization"]["commit_sha"]]
    all_ci_success = all(ci["status"] == "success" for _, ci in _all_ci(evidence))
    release_ready = current != "RELEASE_READY" or all(value is not None for value in status["release"].values())
    return (
        (status["current_gate"], status["next_authorization"]["gate"]) == rule
        and task["state"] == "closed"
        and task["transition"] == {"from": "merged_verified", "to": "closed"}
        and all(sha is not None for sha in all_phase_shas)
        and status["review"] == {"code_security": "approve", "architecture": "clear", "reviewed_candidate_sha": candidate["commit_sha"]}
        and candidate["local_verification"] == {"status": "success", "subject": "delivery_head"}
        and all_ci_success
        and release_ready
    )


def _maturity_continuity_errors(status: dict[str, Any], parent: dict[str, Any]) -> list[str]:
    previous = parent["capability"]["maturity"]
    current = status["capability"]["maturity"]
    old_rank, new_rank = MATURITY[previous], MATURITY[current]
    if new_rank < old_rank:
        return ["$.capability.maturity: maturity rollback is forbidden"]
    if new_rank == old_rank:
        return []
    if new_rank != old_rank + 1:
        return ["$.capability.maturity: maturity upgrades must advance exactly one level"]
    if not _maturity_upgrade_allowed(status, previous, current):
        return ["$.capability.maturity: upgrade requires the exact qualifying closed gate-exit evidence transition"]
    return []


def _parent_status_errors(status: dict[str, Any], parent: dict[str, Any] | None, parent_sha: str | None = None) -> list[str]:
    if parent is None:
        return ["$: direct first parent has no readable canonical project status"]
    errors: list[str] = []
    current_task = status["active_tasks"][0]
    try:
        parent_task = parent["active_tasks"][0]
        immutable = [
            ("project", status["project"], parent["project"]),
            ("authoritative_main_ref", status["authoritative_main_ref"], parent["authoritative_main_ref"]),
            ("current_gate", status["current_gate"], parent["current_gate"]),
            ("task_id", current_task["task_id"], parent_task["task_id"]),
            ("risk", current_task["risk"], parent_task["risk"]),
            ("authorization_baseline_sha", status["evidence"]["authorization_baseline_sha"], parent["evidence"]["authorization_baseline_sha"]),
        ]
    except (KeyError, IndexError, TypeError):
        return ["$: direct first parent canonical status is structurally incompatible"]
    parent_state = parent_task["state"]
    if _typed_equal(parent, status):
        if current_task["state"] != "in_progress":
            errors.append(f"$: same-status commits are restricted to byte-equivalent in_progress implementation work after {parent_sha[:12] if parent_sha else 'unknown'}")
        return errors
    if "transition_ledger" not in parent and "transition_ledger" in status:
        projected = dict(status)
        projected.pop("transition_ledger", None)
        if _typed_equal(projected, parent) and current_task["state"] == "in_progress":
            return errors
    if "schema_authority" not in parent and "schema_authority" in status:
        projected = dict(status)
        projected.pop("schema_authority", None)
        if _typed_equal(projected, parent) and current_task["state"] == "in_progress":
            return errors
    handoff = parent_state == "closed" and current_task["state"] == "authorized" and current_task["transition"] == {"from": "closed", "to": "authorized"}
    if handoff:
        next_auth = parent.get("next_authorization")
        if type(next_auth) is not dict or not _typed_equal((current_task["task_id"], status["current_gate"]), (next_auth.get("task_id"), next_auth.get("gate"))):
            errors.append("$: inter-task handoff must match the exact prior next authorization")
        if not _typed_equal(current_task["candidate_generation"], 1):
            errors.append("$.active_tasks[0].candidate_generation: inter-task handoff must reset generation to one")
        if parent_sha is None or not _typed_equal(status["evidence"]["authorization_baseline_sha"], parent_sha):
            errors.append("$.evidence.authorization_baseline_sha: inter-task handoff baseline must equal the prior close commit")
        if not _cleared_handoff(status):
            errors.append("$: inter-task handoff must clear prior evidence, review, CI, blockers, and bootstrap exception")
        if not _typed_equal(status["capability"]["maturity"], parent["capability"]["maturity"]):
            errors.append("$.capability.maturity: inter-task handoff must preserve maturity")
        if not _typed_equal(status.get("transition_ledger"), parent.get("transition_ledger")):
            errors.append("$.transition_ledger: inter-task handoff must preserve the canonical ledger")
        parent_exception = parent.get("bootstrap_exception")
        if type(parent_exception) is dict and not _typed_equal((parent_exception.get("status"), parent_exception.get("uses")), ("consumed", 1)):
            errors.append("$.bootstrap_exception: inter-task handoff may retire only a consumed exception")
        return errors
    if parent.get("transition_ledger") is not None and not _typed_equal(status.get("transition_ledger"), parent.get("transition_ledger")):
        errors.append("$.transition_ledger: sealed history identity is immutable outside an inter-task handoff")
    for label, current, previous in immutable:
        if not _typed_equal(current, previous):
            errors.append(f"$: immutable {label} changed from direct first parent")
    if not _typed_equal(current_task["transition"]["from"], parent_state):
        errors.append("$.active_tasks[0].transition.from: must equal direct first parent state")
    current_generation = current_task["candidate_generation"]
    parent_generation = parent_task["candidate_generation"]
    if type(current_generation) is not int or type(parent_generation) is not int:
        errors.append("$.active_tasks[0].candidate_generation: continuity requires exact integers")
    elif parent_state == "returned" and current_task["state"] == "in_progress":
        if not _typed_equal(current_generation, parent_generation + 1):
            errors.append("$.active_tasks[0].candidate_generation: returned repair must be exactly parent generation plus one")
    elif not _typed_equal(current_generation, parent_generation):
        errors.append("$.active_tasks[0].candidate_generation: ordinary transition must preserve parent generation")

    parent_exception = parent.get("bootstrap_exception")
    current_exception = status.get("bootstrap_exception")
    if not _typed_equal(_bootstrap_identity(current_exception), _bootstrap_identity(parent_exception)):
        errors.append("$.bootstrap_exception: immutable identity changed or reappeared across direct parent")
    if type(parent_exception) is dict:
        previous_pair = (parent_exception.get("status"), parent_exception.get("uses"))
        current_pair = (current_exception.get("status"), current_exception.get("uses")) if type(current_exception) is dict else None
        if type(parent_exception.get("uses")) is not int or type(current_exception) is not dict or type(current_exception.get("uses")) is not int:
            errors.append("$.bootstrap_exception.uses: continuity requires exact integers")
        if _typed_equal(previous_pair, ("consumed", 1)) and not _typed_equal(current_pair, ("consumed", 1)):
            errors.append("$.bootstrap_exception: consumed exception cannot roll back or disappear")
        if _typed_equal(previous_pair, ("available", 0)) and not any(_typed_equal(current_pair, allowed) for allowed in (("available", 0), ("consumed", 1))):
            errors.append("$.bootstrap_exception: exception consumption must be monotonic")
        if _typed_equal(current_pair, ("consumed", 1)) and current_task["state"] not in {"accepted_pending_merge", "merged_verified", "closed"}:
            errors.append("$.bootstrap_exception: exception may be consumed only on an accepted transition")

    if not (parent_state == "returned" and current_task["state"] == "in_progress"):
        parent_evidence = parent["evidence"]
        for phase in ("candidate", "closure", "merged_main", "finalization"):
            old_sha = parent_evidence[phase].get("commit_sha")
            new_sha = status["evidence"][phase].get("commit_sha")
            if old_sha is not None and not _typed_equal(new_sha, old_sha):
                errors.append(f"$.evidence.{phase}.commit_sha: immutable phase identity changed across direct parent")
        old_implementation = parent_evidence.get("implementation_sha")
        if old_implementation is not None and not _typed_equal(status["evidence"].get("implementation_sha"), old_implementation):
            errors.append("$.evidence.implementation_sha: immutable implementation identity changed across direct parent")

    if current_task["state"] != "returned" and not (parent_state == "returned" and current_task["state"] == "in_progress"):
        errors.extend(_ci_continuity_errors(status, parent))
    errors.extend(_maturity_continuity_errors(status, parent))

    parent_release = parent.get("release", {})
    current_release = status.get("release", {})
    for key in ("product_owner_approval", "release_manifest"):
        old_identity = parent_release.get(key) if type(parent_release) is dict else None
        if old_identity is not None and not _typed_equal(current_release.get(key), old_identity):
            errors.append(f"$.release.{key}: immutable release identity changed across direct parent")
    return errors


def _history_errors(root: Path, head: str, baseline: str, current_schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    current = _status_at(root, head)
    ledger = current.get("transition_ledger") if type(current) is dict else None
    if type(ledger) is not dict:
        ok, full_text = _git(root, "rev-list", "--first-parent", f"{baseline}..{head}")
        if not ok:
            return ["$: authorization baseline is not on the repository HEAD first-parent chain"]
        commits = full_text.splitlines()
        statuses: list[tuple[str, dict[str, Any], bool]] = []
        for sha in commits:
            node, node_errors = _committed_status_errors(root, sha, current_schema)
            if node is None:
                if statuses:
                    break
                errors.extend(node_errors)
                continue
            current_errors = _schema_errors(node, current_schema, current_schema)
            if current_errors:
                errors.append("$.transition_ledger: legacy history requires a sealed content-addressed ledger")
                return errors
            statuses.append((sha, node, not current_errors and not node_errors))
        for index, ((child_sha, child, child_valid), (parent_sha, parent, parent_valid)) in enumerate(zip(statuses, statuses[1:])):
            if not child_valid or not parent_valid:
                continue
            inherited_merge_bridge = False
            if child == parent and child["active_tasks"][0]["state"] == "accepted_pending_merge" and index > 0:
                newer = statuses[index - 1][1]
                inherited_merge_bridge = (
                    newer["active_tasks"][0]["state"] == "merged_verified"
                    and newer["evidence"]["merged_main"]["commit_sha"] == child_sha
                )
            if not inherited_merge_bridge:
                errors.extend(_parent_status_errors(child, parent, parent_sha))
        return errors
    expected_ledger = {
        "authorization_baseline_sha": BOOTSTRAP_BASELINE,
        "sealed_through_sha": LEDGER_ANCHOR,
        "first_parent_chain_sha256": LEDGER_DIGEST,
    }
    ok, origin_url = _git(root, "remote", "get-url", "origin")
    if not ok or _github_repository_identity(origin_url) != LEDGER_REPOSITORY:
        errors.append("$.transition_ledger: ledger migration is restricted to the canonical yaobizuoduo repository")
    if ledger != expected_ledger:
        errors.append("$.transition_ledger: ledger identity must equal the one-time authorized G0-T01 migration")
    anchor = ledger.get("sealed_through_sha")
    if type(anchor) is not str or not _is_first_parent_ancestor(root, anchor, head):
        return errors + ["$.transition_ledger.sealed_through_sha: must be on the repository HEAD first-parent chain"]
    ok, sealed_text = _git(root, "rev-list", "--first-parent", f"{BOOTSTRAP_BASELINE}..{anchor}")
    if not ok:
        return errors + ["$.transition_ledger: sealed authorization history is unavailable"]
    rows: list[str] = []
    for sha in sealed_text.splitlines():
        ok, blob = _git(root, "rev-parse", f"{sha}:PROJECT_STATUS.yaml")
        if ok:
            rows.append(f"{sha} {blob}")
    payload = (("\n".join(rows) + "\n") if rows else "").encode("ascii")
    if hashlib.sha256(payload).hexdigest() != ledger.get("first_parent_chain_sha256"):
        errors.append("$.transition_ledger.first_parent_chain_sha256: sealed first-parent history digest mismatch")
    authority = current.get("schema_authority") if type(current) is dict else None
    migration = authority.get("migration") if type(authority) is dict else None
    if type(authority) is dict and authority.get("revision") == 1:
        ok, schema_history_text = _git(root, "rev-list", "--first-parent", f"{LEDGER_ANCHOR}..{SCHEMA_BOOTSTRAP_SUBJECT}")
        schema_rows: list[str] = []
        if ok:
            for sha in schema_history_text.splitlines() + [LEDGER_ANCHOR]:
                ok_blob, blob = _git(root, "rev-parse", f"{sha}:schemas/project_status.schema.json")
                if ok_blob:
                    schema_rows.append(f"{sha} {blob}")
        schema_payload = (("\n".join(schema_rows) + "\n") if schema_rows else "").encode("ascii")
        if (
            not ok
            or not _is_first_parent_ancestor(root, SCHEMA_BOOTSTRAP_SUBJECT, head)
            or hashlib.sha256(schema_payload).hexdigest() != SCHEMA_PREAUTHORITY_HISTORY_DIGEST
            or type(migration) is not dict
            or migration.get("preauthority_history_sha256") != SCHEMA_PREAUTHORITY_HISTORY_DIGEST
        ):
            errors.append("$.schema_authority.migration: sealed pre-authority schema history mismatch")
    ok, commits_text = _git(root, "rev-list", "--first-parent", f"{anchor}..{head}")
    if not ok:
        return errors + ["$: post-ledger first-parent history is unavailable"]
    commits = commits_text.splitlines() + [anchor]
    statuses: list[tuple[str, dict[str, Any], bool]] = []
    for sha in commits:
        status, status_errors = _committed_status_errors(root, sha, current_schema, use_current_schema=True)
        if status is None:
            # Commits before status authorization are allowed only after the last status-bearing commit.
            if statuses:
                break
            errors.extend(status_errors)
            continue
        errors.extend(status_errors)
        valid = not status_errors
        if valid:
            committed_digest = _schema_digest_at(root, sha)
            authority = status.get("schema_authority")
            expected_digest = authority.get("sha256") if type(authority) is dict else None
            if expected_digest is not None and committed_digest != expected_digest:
                errors.append(f"$: first-parent status at {sha[:12]} schema bytes do not match its authority digest")
                valid = False
        statuses.append((sha, status, valid))
    ledger_nodes = [(sha, node) for sha, node, valid in statuses if valid and type(node.get("transition_ledger")) is dict]
    if not ledger_nodes:
        errors.append("$.transition_ledger: authorized migration commit is absent after the sealed anchor")
    else:
        first_ledger_sha, first_ledger = ledger_nodes[-1]
        ok, first_parents = _git(root, "rev-list", "--parents", "-n", "1", first_ledger_sha)
        parts = first_parents.split() if ok else []
        anchor_status = _status_at(root, anchor)
        projected = dict(first_ledger)
        projected.pop("transition_ledger", None)
        first_task = first_ledger["active_tasks"][0]
        if (
            len(parts) < 2
            or parts[1] != LEDGER_ANCHOR
            or anchor_status is None
            or projected != anchor_status
            or first_ledger.get("project") != "yaobizuoduo"
            or first_task.get("task_id") != BOOTSTRAP_TASK
            or first_ledger["evidence"].get("authorization_baseline_sha") != BOOTSTRAP_BASELINE
        ):
            errors.append("$.transition_ledger: first creation must be the exact authorized one-time migration immediately after fa04769")
    for index, ((child_sha, child, child_valid), (parent_sha, parent, parent_valid)) in enumerate(zip(statuses, statuses[1:])):
        if not child_valid or not parent_valid:
            continue
        inherited_merge_bridge = False
        if child == parent and child["active_tasks"][0]["state"] == "accepted_pending_merge" and index > 0:
            newer = statuses[index - 1][1]
            inherited_merge_bridge = (
                newer["active_tasks"][0]["state"] == "merged_verified"
                and newer["evidence"]["merged_main"]["commit_sha"] == child_sha
            )
        if not inherited_merge_bridge:
            errors.extend(_parent_status_errors(child, parent, parent_sha))
            errors.extend(_schema_authority_continuity_errors(child, parent, parent_sha, root, child_sha))
    return errors


def _subject_status_matches(status: dict[str, Any], subject: dict[str, Any] | None, expected_state: str) -> bool:
    if subject is None:
        return False
    try:
        return (
            _typed_equal(subject["schema_version"], "project-status.v2")
            and _typed_equal(subject["project"], status["project"])
            and _typed_equal(subject["authoritative_main_ref"], status["authoritative_main_ref"])
            and _typed_equal(subject["current_gate"], status["current_gate"])
            and _typed_equal(subject["active_tasks"][0]["task_id"], status["active_tasks"][0]["task_id"])
            and _typed_equal(subject["active_tasks"][0]["risk"], status["active_tasks"][0]["risk"])
            and _typed_equal(subject["active_tasks"][0]["candidate_generation"], status["active_tasks"][0]["candidate_generation"])
            and _typed_equal(subject["active_tasks"][0]["state"], expected_state)
            and _typed_equal(subject["evidence"]["authorization_baseline_sha"], status["evidence"]["authorization_baseline_sha"])
            and _typed_equal(subject["evidence"]["implementation_sha"], status["evidence"]["implementation_sha"])
            and _typed_equal(_bootstrap_identity(subject.get("bootstrap_exception")), _bootstrap_identity(status.get("bootstrap_exception")))
            and _typed_equal(subject.get("schema_authority"), status.get("schema_authority"))
            and _typed_equal(subject.get("transition_ledger"), status.get("transition_ledger"))
        )
    except (KeyError, IndexError, TypeError):
        return False


def _repository_errors(status: dict[str, Any], status_path: Path, repo_root: Path, schema: dict[str, Any]) -> list[str]:
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
    ok, parents = _git(root, "rev-list", "--parents", "-n", "1", head)
    parent_parts = parents.split() if ok else []
    if len(parent_parts) < 2:
        errors.append("$: repository HEAD has no direct first parent canonical history")
    else:
        parent_status, parent_schema_errors = _committed_status_errors(root, parent_parts[1], schema, use_current_schema=True)
        errors.extend(parent_schema_errors)
        if not parent_schema_errors and parent_status is not None:
            errors.extend(_parent_status_errors(status, parent_status, parent_parts[1]))
            errors.extend(_schema_authority_continuity_errors(status, parent_status, parent_parts[1], root))
    if type(status.get("transition_ledger")) is dict:
        control_path = root / SCHEMA_CONTROL_PATH
        ok, tree_entry = _git(root, "ls-tree", "HEAD", "--", SCHEMA_CONTROL_PATH)
        fields = tree_entry.split(None, 3) if ok else []
        if control_path.is_symlink() or len(fields) != 4 or fields[0] not in {"100644", "100755"} or fields[1] != "blob":
            errors.append("$.schema_migration_control: canonical control must be a committed regular Git blob")
    errors.extend(_history_errors(root, head, baseline, schema))

    main_ref = status["authoritative_main_ref"]
    ok, main_sha = _git(root, "rev-parse", "--verify", main_ref)
    if not ok:
        errors.append("$.authoritative_main_ref: authoritative main ref does not exist")
        main_sha = ""
    remote_main_ref = "refs/remotes/origin/" + main_ref.removeprefix("refs/heads/")
    remote_main_ok, remote_main_sha = _git(root, "rev-parse", "--verify", remote_main_ref)
    ok, origin_url = _git(root, "remote", "get-url", "origin")
    repository_identity = _github_repository_identity(origin_url) if ok else None
    if repository_identity is None:
        errors.append("$: canonical GitHub origin repository identity is unavailable")
    errors.extend(_ci_repository_errors(evidence, repository_identity))
    canonical_path = root / "PROJECT_STATUS.yaml"
    if status_path.resolve() == canonical_path.resolve() and task_state in {"awaiting_review", "accepted_pending_merge", "merged_verified", "closed"}:
        ok, committed = _git(root, "show", "HEAD:PROJECT_STATUS.yaml")
        try:
            working = canonical_path.read_text(encoding="utf-8").rstrip("\n")
        except (OSError, UnicodeError):
            working = ""
        if not ok or committed != working:
            errors.append("$: phase subject must be the exact committed repository HEAD")
        clean, porcelain = _git(root, "status", "--porcelain", "--untracked-files=all")
        if not clean or porcelain:
            errors.append("$: phase subject requires a clean worktree")

    implementation = evidence["implementation_sha"]
    candidate = evidence["candidate"]["commit_sha"]
    closure = evidence["closure"]["commit_sha"]
    merged = evidence["merged_main"]["commit_sha"]
    finalization = evidence["finalization"]["commit_sha"]
    def phase_status_matches(sha: str, expected_state: str) -> bool:
        subject, subject_errors = _committed_status_errors(root, sha, schema, use_current_schema=True)
        errors.extend(subject_errors)
        return not subject_errors and _subject_status_matches(status, subject, expected_state)

    implicit_candidate = head if task_state == "awaiting_review" else candidate
    if implementation is not None and implicit_candidate is not None:
        if not _is_ancestor(root, baseline, implementation) or not _is_ancestor(root, implementation, implicit_candidate):
            errors.append("$.evidence: baseline -> implementation -> candidate ancestry is invalid")
    if candidate is not None:
        if not phase_status_matches(candidate, "awaiting_review"):
            errors.append("$.evidence.candidate.commit_sha: commit is not the matching delivered candidate phase")
        if not _is_ancestor(root, candidate, head):
            errors.append("$.evidence.candidate.commit_sha: candidate is unrelated to current HEAD")
    implicit_closure = head if task_state == "accepted_pending_merge" else closure
    if implicit_closure is not None and candidate is not None and not _is_ancestor(root, candidate, implicit_closure):
        errors.append("$.evidence.closure.commit_sha: candidate is not an ancestor of closure")
    if closure is not None and not phase_status_matches(closure, "accepted_pending_merge"):
        errors.append("$.evidence.closure.commit_sha: commit is not the matching closure phase")
    if merged is not None:
        if closure is None or not _is_ancestor(root, closure, merged):
            errors.append("$.evidence.merged_main.commit_sha: closure is not an ancestor of merged-main")
        ok, parents = _git(root, "rev-list", "--parents", "-n", "1", merged)
        if not ok or len(parents.split()) < 3:
            errors.append("$.evidence.merged_main.commit_sha: merged-main subject is not a merge commit")
        if not remote_main_ok:
            errors.append("$.evidence.merged_main.commit_sha: fetched origin/main evidence is unavailable")
        elif main_sha != remote_main_sha:
            errors.append("$.authoritative_main_ref: local main must equal fetched origin/main")
        elif not _is_first_parent_ancestor(root, merged, remote_main_sha):
            errors.append("$.evidence.merged_main.commit_sha: merge is not on the authoritative remote-main first-parent chain")
    task = status["active_tasks"][0]
    if task["transition"] == {"from": "closed", "to": "authorized"}:
        direct_parent = parent_parts[1] if len(parent_parts) >= 2 else None
        if not remote_main_ok or main_sha != remote_main_sha or direct_parent != remote_main_sha:
            errors.append("$: inter-task handoff must start from the exact fetched authoritative main close")
    if finalization is not None:
        if merged is None or not _is_ancestor(root, merged, finalization):
            errors.append("$.evidence.finalization.commit_sha: merged-main is not an ancestor of finalization")
        if not phase_status_matches(finalization, "merged_verified"):
            errors.append("$.evidence.finalization.commit_sha: commit is not the matching finalization phase")
    errors.extend(_release_identity_errors(status, root, main_ref))
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
    authority_errors = _schema_authority_document_errors(status, schema_path)
    if authority_errors:
        return sorted(set(authority_errors))
    control_errors = _schema_control_document_errors(status, schema_path)
    if control_errors:
        return sorted(set(control_errors))
    try:
        errors = _schema_errors(status, schema, schema)
    except (KeyError, TypeError, ValueError):
        return ["$: schema is malformed or unsupported"]
    if not errors:
        errors.extend(_semantic_errors(status))
        if repo_root is not None:
            errors.extend(_document_errors(status, repo_root))
            errors.extend(_repository_errors(status, status_path, repo_root, schema))
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
