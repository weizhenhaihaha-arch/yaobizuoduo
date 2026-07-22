from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "g0-t03" / "main-protection-generation2.json"
SPEC = importlib.util.spec_from_file_location("g0_t03", ROOT / "scripts" / "validate_g0_t03_protection.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def load() -> dict:
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def recompute(document: dict, section: str) -> None:
    document["before_sha256" if section == "before" else "after_sha256"] = MODULE.digest(document[section])


def pull(document: dict, section: str) -> dict:
    return next(rule for rule in document[section]["rules"] if rule["type"] == "pull_request")


def checks(document: dict, section: str) -> dict:
    return next(rule for rule in document[section]["rules"] if rule["type"] == "required_status_checks")


def assert_rejected(document: dict, fragment: str) -> None:
    assert any(fragment in error for error in MODULE.validate(document)), MODULE.validate(document)


def test_applied_evidence_is_exact_and_digest_bound() -> None:
    assert MODULE.validate(load()) == []


@pytest.mark.parametrize("conclusion", ["failure", "cancelled", "skipped", "neutral", "stale", None])
def test_only_exact_strict_success_satisfies_required_check(conclusion: object) -> None:
    assert not MODULE.strict_check_success("G0 / exact-head", conclusion)
    assert MODULE.strict_check_success("G0 / exact-head", "success")
    assert not MODULE.strict_check_success("G0 / exact-head ", "success")


@pytest.mark.parametrize(
    ("mutation", "fragment"),
    [
        (lambda d: d["before"].__setitem__("default_branch", "develop"), "before main identity"),
        (lambda d: d["before"].__setitem__("main_head_sha", "f" * 40), "before main identity"),
        (lambda d: d["before"]["classic_protection"].__setitem__("http_status", 200), "classic protection"),
        (lambda d: d["before"]["required_check_observation"].__setitem__("conclusion", "failure"), "required check identity"),
        (lambda d: d["before"]["required_check_observation"].__setitem__("app_slug", "attacker"), "required check identity"),
        (lambda d: d["before"]["required_check_observation"].__setitem__("run_id", "0"), "required check"),
    ],
)
def test_recomputed_before_digest_does_not_replace_semantic_truth(mutation, fragment: str) -> None:
    document = load()
    mutation(document)
    recompute(document, "before")
    assert_rejected(document, fragment)


def test_unknown_before_or_root_field_fails_closed() -> None:
    before = load()
    before["before"]["unknown"] = True
    recompute(before, "before")
    assert_rejected(before, "before snapshot field set")
    root = load()
    root["unknown"] = True
    assert_rejected(root, "root field set")


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: pull(d, "desired_ruleset")["parameters"].__setitem__("require_code_owner_review", True),
        lambda d: pull(d, "desired_ruleset")["parameters"].__setitem__("required_approving_review_count", 1),
        lambda d: checks(d, "desired_ruleset")["parameters"].__setitem__("strict_required_status_checks_policy", True),
        lambda d: checks(d, "desired_ruleset")["parameters"].__setitem__("do_not_enforce_on_create", True),
        lambda d: checks(d, "desired_ruleset")["parameters"]["required_status_checks"].append({"context": "other"}),
        lambda d: pull(d, "desired_ruleset")["parameters"].__setitem__("unknown", False),
        lambda d: d["desired_ruleset"].__setitem__("unknown", False),
    ],
)
def test_desired_rule_or_parameter_drift_fails_closed(mutate) -> None:
    document = load()
    mutate(document)
    assert_rejected(document, "desired")


def test_desired_and_readback_synchronized_drift_still_fails_closed() -> None:
    document = load()
    pull(document, "desired_ruleset")["parameters"]["require_code_owner_review"] = True
    pull(document, "readback")["parameters"]["require_code_owner_review"] = True
    recompute(document, "readback")
    assert_rejected(document, "desired rules")
    assert_rejected(document, "readback rules")


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d["readback"].__setitem__("id", -1),
        lambda d: d["readback"].__setitem__("source", "other/repo"),
        lambda d: d["readback"].__setitem__("unknown", True),
        lambda d: pull(d, "readback")["parameters"].__setitem__("unknown", True),
        lambda d: pull(d, "readback")["parameters"].__setitem__("allowed_merge_methods", ["merge"]),
    ],
)
def test_recomputed_readback_digest_does_not_replace_exact_truth(mutate) -> None:
    document = load()
    mutate(document)
    recompute(document, "readback")
    assert MODULE.validate(document)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d["rollback"].__setitem__("method", "POST"),
        lambda d: d["rollback"].__setitem__("endpoint_template", "/repos/other/repo/rulesets/{created_rule_id}"),
        lambda d: d["rollback"].__setitem__("created_rule_id", 1),
        lambda d: d["rollback"].__setitem__("created_rule_id", -1),
        lambda d: d["rollback"]["success_verification"].__setitem__("protected", True),
        lambda d: d["rollback"]["success_verification"].__setitem__("rulesets", [{"id": 9}]),
        lambda d: d["rollback"].__setitem__("unknown", True),
    ],
)
def test_rollback_method_repository_id_and_recovery_are_exact(mutate) -> None:
    document = load()
    mutate(document)
    assert_rejected(document, "rollback")


def test_none_or_incomplete_desired_and_readback_fail_closed() -> None:
    desired = load()
    desired["desired_ruleset"] = None
    assert_rejected(desired, "desired ruleset field set")
    readback = load()
    readback["readback"] = None
    assert_rejected(readback, "readback field set")


def test_exact_head_workflow_is_fork_safe_and_secret_free() -> None:
    workflow = (ROOT / ".github" / "workflows" / "g0-exact-head.yml").read_text(encoding="utf-8")
    assert "pull_request:" in workflow
    assert "secrets." not in workflow
    assert "persist-credentials: false" in workflow
    assert "contents: read" in workflow
