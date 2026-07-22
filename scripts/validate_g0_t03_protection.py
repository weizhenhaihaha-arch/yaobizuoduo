from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


EXACT_CONTEXT = "G0 / exact-head"
EXACT_REPOSITORY = "weizhenhaihaha-arch/yaobizuoduo"
EXACT_MAIN_SHA = "09bfbd23d898198fe694a3a94f77663759dd89d8"
EXACT_RULE_ID = 19526291
EXACT_CREATED_AT = "2026-07-22T12:48:34.433+08:00"
EXACT_UPDATED_AT = "2026-07-22T12:48:34.463+08:00"
EXACT_RUN_ID = "29890931290"
EXACT_BEFORE_DIGEST = "c853932335770382ae0a515a2a0d1c52bfccabe84e060c5ce4b68db7000980de"
EXACT_AFTER_DIGEST = "73aa3644a4c571c7101b0ac36547bd1be2edc306846045d2d36ad07ac86c5bb1"

ROOT_KEYS = {
    "schema_version", "phase", "observed_at_utc", "before", "before_sha256",
    "desired_ruleset", "readback", "after_sha256", "rollback", "remote_mutation_performed",
}
BEFORE_KEYS = {
    "repository", "visibility", "default_branch", "main_head_sha", "rulesets",
    "classic_protection", "required_check_observation",
}
DESIRED_KEYS = {"name", "target", "enforcement", "bypass_actors", "conditions", "rules"}
READBACK_KEYS = DESIRED_KEYS | {"id", "source_type", "source", "created_at", "updated_at"}
PULL_REQUEST_PARAMETER_KEYS = {
    "dismiss_stale_reviews_on_push", "require_code_owner_review", "require_last_push_approval",
    "required_approving_review_count", "required_review_thread_resolution",
}
READBACK_PULL_REQUEST_PARAMETER_KEYS = PULL_REQUEST_PARAMETER_KEYS | {"required_reviewers", "allowed_merge_methods"}
STATUS_PARAMETER_KEYS = {"do_not_enforce_on_create", "required_status_checks", "strict_required_status_checks_policy"}


def digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def exact_keys(value: object, expected: set[str]) -> bool:
    return type(value) is dict and set(value) == expected


def strict_check_success(context: object, conclusion: object) -> bool:
    return type(context) is str and context == EXACT_CONTEXT and type(conclusion) is str and conclusion == "success"


def expected_conditions() -> dict[str, Any]:
    return {"ref_name": {"include": ["refs/heads/main"], "exclude": []}}


def expected_desired_rules() -> list[dict[str, Any]]:
    return [
        {"type": "deletion"},
        {"type": "non_fast_forward"},
        {
            "type": "pull_request",
            "parameters": {
                "dismiss_stale_reviews_on_push": False,
                "require_code_owner_review": False,
                "require_last_push_approval": False,
                "required_approving_review_count": 0,
                "required_review_thread_resolution": False,
            },
        },
        {
            "type": "required_status_checks",
            "parameters": {
                "do_not_enforce_on_create": False,
                "required_status_checks": [{"context": EXACT_CONTEXT}],
                "strict_required_status_checks_policy": False,
            },
        },
    ]


def expected_readback_rules() -> list[dict[str, Any]]:
    rules = expected_desired_rules()
    pull = rules[2]["parameters"]
    pull["required_reviewers"] = []
    pull["allowed_merge_methods"] = ["merge", "squash", "rebase"]
    return rules


def valid_rules(rules: object, *, readback: bool) -> bool:
    expected = expected_readback_rules() if readback else expected_desired_rules()
    if type(rules) is not list or rules != expected:
        return False
    if not all(exact_keys(rule, {"type"} if index < 2 else {"type", "parameters"}) for index, rule in enumerate(rules)):
        return False
    pull_keys = READBACK_PULL_REQUEST_PARAMETER_KEYS if readback else PULL_REQUEST_PARAMETER_KEYS
    return (
        exact_keys(rules[2]["parameters"], pull_keys)
        and exact_keys(rules[3]["parameters"], STATUS_PARAMETER_KEYS)
        and exact_keys(rules[3]["parameters"]["required_status_checks"][0], {"context"})
    )


def validate_before(before: object, claimed_digest: object) -> list[str]:
    if not exact_keys(before, BEFORE_KEYS):
        return ["before snapshot field set is not exact"]
    assert type(before) is dict
    errors: list[str] = []
    if claimed_digest != EXACT_BEFORE_DIGEST or digest(before) != EXACT_BEFORE_DIGEST:
        errors.append("before snapshot digest mismatch")
    if before["repository"] != EXACT_REPOSITORY or before["visibility"] != "PUBLIC":
        errors.append("before repository identity is not exact")
    if before["default_branch"] != "main" or before["main_head_sha"] != EXACT_MAIN_SHA:
        errors.append("before main identity is not exact")
    if before["rulesets"] != []:
        errors.append("before rulesets must be exactly empty")
    if before["classic_protection"] != {"http_status": 404, "protected": False} or not exact_keys(before["classic_protection"], {"http_status", "protected"}):
        errors.append("before classic protection identity is not exact")
    check = before["required_check_observation"]
    expected_check = {
        "context": EXACT_CONTEXT, "app_slug": "github-actions", "head_sha": EXACT_MAIN_SHA,
        "status": "completed", "conclusion": "success", "run_id": EXACT_RUN_ID,
    }
    if not exact_keys(check, set(expected_check)) or check != expected_check or not strict_check_success(check.get("context") if type(check) is dict else None, check.get("conclusion") if type(check) is dict else None):
        errors.append("before required check identity is not exact strict success")
    if type(check) is dict and (type(check.get("run_id")) is not str or re.fullmatch(r"[1-9][0-9]*", check["run_id"]) is None):
        errors.append("before required check run ID must be a positive integer string")
    return errors


def validate_desired(desired: object) -> list[str]:
    if not exact_keys(desired, DESIRED_KEYS):
        return ["desired ruleset field set is not exact"]
    assert type(desired) is dict
    errors: list[str] = []
    if (desired["name"], desired["target"], desired["enforcement"]) != ("G0-T03 main protection", "branch", "active"):
        errors.append("desired ruleset identity is not exact")
    if desired["bypass_actors"] != [] or desired["conditions"] != expected_conditions():
        errors.append("desired target or bypass scope is not exact")
    if not exact_keys(desired["conditions"], {"ref_name"}) or not exact_keys(desired["conditions"].get("ref_name"), {"include", "exclude"}):
        errors.append("desired condition field set is not exact")
    if not valid_rules(desired["rules"], readback=False):
        errors.append("desired rules and parameters are not exact")
    return errors


def validate_readback(readback: object, claimed_digest: object) -> list[str]:
    if not exact_keys(readback, READBACK_KEYS):
        return ["readback field set is not exact"]
    assert type(readback) is dict
    errors: list[str] = []
    if claimed_digest != EXACT_AFTER_DIGEST or digest(readback) != EXACT_AFTER_DIGEST:
        errors.append("readback digest mismatch")
    if type(readback["id"]) is not int or readback["id"] != EXACT_RULE_ID or readback["id"] <= 0:
        errors.append("readback rule ID is not the exact positive integer")
    expected_identity = {
        "name": "G0-T03 main protection", "target": "branch", "source_type": "Repository",
        "source": EXACT_REPOSITORY, "enforcement": "active", "bypass_actors": [],
        "conditions": expected_conditions(), "created_at": EXACT_CREATED_AT, "updated_at": EXACT_UPDATED_AT,
    }
    if any(readback[key] != value for key, value in expected_identity.items()):
        errors.append("readback identity or target is not exact")
    if not exact_keys(readback["conditions"], {"ref_name"}) or not exact_keys(readback["conditions"].get("ref_name"), {"include", "exclude"}):
        errors.append("readback condition field set is not exact")
    if not valid_rules(readback["rules"], readback=True):
        errors.append("readback rules and server defaults are not exact")
    return errors


def validate_rollback(rollback: object, readback: object) -> list[str]:
    expected_keys = {"method", "endpoint_template", "created_rule_id", "success_verification"}
    if not exact_keys(rollback, expected_keys):
        return ["rollback field set is not exact"]
    assert type(rollback) is dict
    success = rollback["success_verification"]
    expected_success = {"rulesets": [], "classic_protection_http_status": 404, "protected": False}
    errors: list[str] = []
    if rollback["method"] != "DELETE" or rollback["endpoint_template"] != f"/repos/{EXACT_REPOSITORY}/rulesets/{{created_rule_id}}":
        errors.append("rollback method or endpoint is not exact")
    readback_id = readback.get("id") if type(readback) is dict else None
    if type(rollback["created_rule_id"]) is not int or rollback["created_rule_id"] <= 0 or rollback["created_rule_id"] != EXACT_RULE_ID or rollback["created_rule_id"] != readback_id:
        errors.append("rollback rule ID does not bind the exact readback")
    if not exact_keys(success, set(expected_success)) or success != expected_success:
        errors.append("rollback success verification is not exact")
    return errors


def validate(document: dict[str, Any]) -> list[str]:
    if not exact_keys(document, ROOT_KEYS):
        return ["evidence root field set is not exact"]
    errors: list[str] = []
    if document["schema_version"] != "g0-t03-main-protection.v1" or document["phase"] != "applied":
        errors.append("evidence schema or phase is not exact")
    if document["observed_at_utc"] != "2026-07-22T04:46:04Z":
        errors.append("evidence observation timestamp is not exact")
    errors.extend(validate_before(document["before"], document["before_sha256"]))
    errors.extend(validate_desired(document["desired_ruleset"]))
    errors.extend(validate_readback(document["readback"], document["after_sha256"]))
    errors.extend(validate_rollback(document["rollback"], document["readback"]))
    if document["remote_mutation_performed"] is not True:
        errors.append("applied evidence must record the remote mutation")
    return errors


def main() -> int:
    path = Path(sys.argv[1])
    try:
        document = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR unreadable evidence: {type(exc).__name__}")
        return 1
    errors = validate(document) if type(document) is dict else ["evidence root must be an object"]
    for error in errors:
        print(f"ERROR {error}")
    if errors:
        return 1
    print(f"OK {path}")
    return 0


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


if __name__ == "__main__":
    raise SystemExit(main())
