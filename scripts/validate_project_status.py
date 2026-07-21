#!/usr/bin/env python3
"""Validate the canonical project status using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATUS = ROOT / "PROJECT_STATUS.yaml"
DEFAULT_SCHEMA = ROOT / "schemas" / "project_status.schema.json"

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
MATURITY = {
    "OFFLINE_EVIDENCE_ACCEPTED": 0,
    "INTEGRATION_ACCEPTED": 1,
    "PAPER_VALIDATED": 2,
    "RELEASE_READY": 3,
}
STALE_CURRENT_CLAIMS = (
    re.compile(r"当前项目处于\s*M[0-9]"),
    re.compile(r"当前里程碑[：:]\s*M[0-9]"),
    re.compile(r"当前任务[：:]\s*`?M[0-9]-T[0-9]+"),
    re.compile(r"current\s+(?:milestone|stage|task)\s*[:：]\s*`?M[0-9]", re.IGNORECASE),
)


def _type_matches(value: Any, expected: str) -> bool:
    return {
        "object": type(value) is dict,
        "array": type(value) is list,
        "string": type(value) is str,
        "integer": type(value) is int,
        "null": value is None,
        "boolean": type(value) is bool,
    }.get(expected, False)


def _resolve_ref(schema: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError("only local schema references are supported")
    node: Any = schema
    for component in ref[2:].split("/"):
        node = node[component.replace("~1", "/").replace("~0", "~")]
    if type(node) is not dict:
        raise ValueError("schema reference does not resolve to an object")
    return node


def _schema_errors(value: Any, rule: dict[str, Any], schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    if "$ref" in rule:
        return _schema_errors(value, _resolve_ref(schema, rule["$ref"]), schema, path)
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
    if type(value) is int and "minimum" in rule and value < rule["minimum"]:
        errors.append(f"{path}: integer is below minimum")
    return errors


def _semantic_errors(status: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    tasks = status.get("active_tasks")
    if type(tasks) is not list or len(tasks) != 1 or type(tasks[0]) is not dict:
        return errors
    task = tasks[0]
    state = task.get("state")
    task_id = task.get("task_id")
    if type(task_id) is str and not task_id.startswith(f"{status.get('current_gate')}-"):
        errors.append("$.active_tasks[0].task_id: task gate must match current_gate")
    transition = task.get("transition")
    if type(transition) is dict:
        before, after = transition.get("from"), transition.get("to")
        if after != state:
            errors.append("$.active_tasks[0].transition.to: must equal current task state")
        if before not in TRANSITIONS or after not in TRANSITIONS.get(before, set()):
            errors.append("$.active_tasks[0].transition: illegal lifecycle transition")

    evidence = status.get("evidence", {})
    review = status.get("review", {})
    ci = status.get("ci", {})
    candidate = evidence.get("candidate_sha")
    if state in {"planned", "authorized", "in_progress"}:
        if any(evidence.get(key) is not None for key in ("candidate_sha", "closure_sha", "implementation_merge_sha", "finalization_sha")):
            errors.append("$.evidence: undelivered task state cannot carry later-stage SHA evidence")
        if review.get("code_security") != "pending" or review.get("architecture") != "pending" or review.get("reviewed_candidate_sha") is not None:
            errors.append("$.review: undelivered task state must not carry reviewer identity")
        if ci.get("status") not in {"not_established", "not_run"} or ci.get("head_sha") is not None or ci.get("run_id") is not None or ci.get("url") is not None:
            errors.append("$.ci: undelivered task state must not carry CI identity")
    if state in {"awaiting_review", "returned", "accepted_pending_merge", "merged_verified", "closed"} and candidate is None:
        errors.append("$.evidence.candidate_sha: required for delivered task state")
    if state == "awaiting_review":
        if review.get("code_security") != "pending" or review.get("architecture") != "pending" or review.get("reviewed_candidate_sha") is not None:
            errors.append("$.review: awaiting review must not carry a prior verdict identity")
        if ci.get("status") not in {"not_established", "not_run", "pending"}:
            errors.append("$.ci: awaiting review cannot claim successful or failed candidate CI")
    if state in {"accepted_pending_merge", "merged_verified", "closed"}:
        if review.get("code_security") != "approve" or review.get("architecture") != "clear":
            errors.append("$.review: accepted states require code/security approve and architecture clear")
        if review.get("reviewed_candidate_sha") != candidate:
            errors.append("$.review.reviewed_candidate_sha: must identify the candidate")
        if ci.get("status") != "success" or ci.get("head_sha") != candidate or ci.get("run_id") is None or ci.get("url") is None:
            errors.append("$.ci: accepted states require successful exact-candidate CI evidence")
        if evidence.get("closure_sha") is None:
            errors.append("$.evidence.closure_sha: required for accepted state")
    if state in {"merged_verified", "closed"} and evidence.get("implementation_merge_sha") is None:
        errors.append("$.evidence.implementation_merge_sha: required after merge verification")
    if state == "closed" and evidence.get("finalization_sha") is None:
        errors.append("$.evidence.finalization_sha: required when closed")
    if state == "blocked" and not status.get("blockers"):
        errors.append("$.blockers: blocked state requires a recorded blocker")
    if state == "in_progress" and transition.get("from") == "returned":
        if candidate is not None or review.get("reviewed_candidate_sha") is not None or ci.get("head_sha") is not None:
            errors.append("$: a returned-task repair must invalidate prior candidate, review, and CI identity")
    capability = status.get("capability", {})
    maturity = capability.get("maturity")
    if status.get("current_gate") in {"G0", "G1", "G2"} and MATURITY.get(maturity, 99) > MATURITY["OFFLINE_EVIDENCE_ACCEPTED"]:
        errors.append("$.capability.maturity: maturity exceeds evidence available at this gate")
    return errors


def _document_errors(status: dict[str, Any], repo_root: Path) -> list[str]:
    errors: list[str] = []
    documents = status.get("governed_documents", [])
    if type(documents) is not list:
        return errors
    resolved_root = repo_root.resolve()
    for relative in documents:
        if type(relative) is not str:
            continue
        path = (resolved_root / relative).resolve()
        try:
            path.relative_to(resolved_root)
        except ValueError:
            errors.append(f"$.governed_documents: path escapes repository: {relative}")
            continue
        if not path.is_file():
            errors.append(f"$.governed_documents: missing document: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        if relative == "CURRENT_TASK.md":
            expected_task = status["active_tasks"][0]["task_id"]
            expected_state = status["active_tasks"][0]["state"]
            task_match = re.search(r"^- Task ID: `([^`]+)`$", text, re.MULTILINE)
            state_match = re.search(r"^- Status: `([^`]+)`$", text, re.MULTILINE)
            if task_match is None or task_match.group(1) != expected_task:
                errors.append("$.governed_documents: CURRENT_TASK task_id conflicts with canonical status")
            if state_match is None or state_match.group(1) != expected_state:
                errors.append("$.governed_documents: CURRENT_TASK state conflicts with canonical status")
        for pattern in STALE_CURRENT_CLAIMS:
            if pattern.search(text):
                errors.append(f"$.governed_documents: stale current-state claim in {relative}")
                break
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
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("status", nargs="?", type=Path, default=DEFAULT_STATUS)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--repo-root", type=Path, default=None, help="also check governed documents")
    args = parser.parse_args()
    errors = validate(args.status, args.schema, args.repo_root)
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        return 1
    print(f"OK {args.status}: project-status.v1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
