from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


EXACT_CONTEXT = "G0 / exact-head"
ALLOWED_CONCLUSIONS = {"success"}
EXPECTED_RULE_TYPES = {"deletion", "non_fast_forward", "pull_request", "required_status_checks"}


def digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def strict_check_success(context: object, conclusion: object) -> bool:
    return type(context) is str and context == EXACT_CONTEXT and type(conclusion) is str and conclusion in ALLOWED_CONCLUSIONS


def semantic_rules(rules: object) -> list[dict[str, Any]] | None:
    if type(rules) is not list or any(type(rule) is not dict for rule in rules):
        return None
    result: list[dict[str, Any]] = []
    for rule in rules:
        item = {"type": rule.get("type")}
        parameters = rule.get("parameters")
        if rule.get("type") == "pull_request" and type(parameters) is dict:
            allowed_extras = {"required_reviewers": [], "allowed_merge_methods": ["merge", "squash", "rebase"]}
            for key, value in parameters.items():
                if key not in {
                    "dismiss_stale_reviews_on_push",
                    "require_code_owner_review",
                    "require_last_push_approval",
                    "required_approving_review_count",
                    "required_review_thread_resolution",
                    *allowed_extras,
                }:
                    return None
                if key in allowed_extras and value != allowed_extras[key]:
                    return None
            item["parameters"] = {key: parameters.get(key) for key in (
                "dismiss_stale_reviews_on_push",
                "require_code_owner_review",
                "require_last_push_approval",
                "required_approving_review_count",
                "required_review_thread_resolution",
            )}
        elif rule.get("type") == "required_status_checks" and type(parameters) is dict:
            item["parameters"] = parameters
        elif parameters is not None:
            return None
        result.append(item)
    return result


def validate(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    before = document.get("before")
    desired = document.get("desired_ruleset")
    if type(before) is not dict or digest(before) != document.get("before_sha256"):
        errors.append("before snapshot digest mismatch")
    elif before.get("repository") != "weizhenhaihaha-arch/yaobizuoduo" or before.get("rulesets") != []:
        errors.append("before snapshot does not bind the exact empty-ruleset repository")
    if type(desired) is not dict:
        return errors + ["desired ruleset is missing"]
    if desired.get("name") != "G0-T03 main protection" or desired.get("target") != "branch" or desired.get("enforcement") != "active":
        errors.append("ruleset identity is not exact")
    if desired.get("bypass_actors") != [] or desired.get("conditions") != {"ref_name": {"include": ["refs/heads/main"], "exclude": []}}:
        errors.append("ruleset target or bypass scope is not exact")
    rules = desired.get("rules")
    if type(rules) is not list or {rule.get("type") for rule in rules if type(rule) is dict} != EXPECTED_RULE_TYPES or len(rules) != 4:
        errors.append("ruleset must contain exactly the four frozen rule types")
    else:
        by_type = {rule["type"]: rule for rule in rules}
        pull = by_type["pull_request"].get("parameters")
        if type(pull) is not dict or pull.get("required_approving_review_count") != 0:
            errors.append("pull request rule must not require approvals")
        checks = by_type["required_status_checks"].get("parameters")
        if type(checks) is not dict or checks.get("required_status_checks") != [{"context": EXACT_CONTEXT}]:
            errors.append("required check context is not exact")
    phase = document.get("phase")
    readback = document.get("readback")
    rollback = document.get("rollback")
    if phase == "preflight":
        if readback is not None or document.get("after_sha256") is not None or document.get("remote_mutation_performed") is not False:
            errors.append("preflight cannot claim a remote mutation or readback")
    elif phase == "applied":
        if type(readback) is not dict or digest(readback) != document.get("after_sha256"):
            errors.append("readback digest mismatch")
        elif (
            any(readback.get(key) != desired.get(key) for key in ("name", "target", "enforcement", "bypass_actors", "conditions"))
            or semantic_rules(readback.get("rules")) != semantic_rules(desired.get("rules"))
            or readback.get("source_type") != "Repository"
            or readback.get("source") != before.get("repository")
        ):
            errors.append("readback differs from the frozen ruleset")
        if type(rollback) is not dict or type(rollback.get("created_rule_id")) is not int or rollback["created_rule_id"] != readback.get("id"):
            errors.append("rollback does not bind the created rule ID")
        if document.get("remote_mutation_performed") is not True:
            errors.append("applied phase must record the remote mutation")
    else:
        errors.append("unknown evidence phase")
    return errors


def main() -> int:
    path = Path(sys.argv[1])
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"ERROR unreadable evidence: {type(exc).__name__}")
        return 1
    errors = validate(document) if type(document) is dict else ["evidence root must be an object"]
    for error in errors:
        print(f"ERROR {error}")
    if errors:
        return 1
    print(f"OK {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
