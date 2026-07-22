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


def test_preflight_evidence_is_valid_and_digest_bound() -> None:
    assert MODULE.validate(load()) == []


@pytest.mark.parametrize("conclusion", ["failure", "cancelled", "skipped", "neutral", "stale", None])
def test_only_exact_strict_success_satisfies_required_check(conclusion: object) -> None:
    assert not MODULE.strict_check_success("G0 / exact-head", conclusion)
    assert MODULE.strict_check_success("G0 / exact-head", "success")
    assert not MODULE.strict_check_success("G0 / exact-head ", "success")


def test_forged_snapshot_digest_fails_closed() -> None:
    document = load()
    document["before"]["rulesets"] = [{"id": 1}]
    assert "before snapshot digest mismatch" in MODULE.validate(document)


def test_unknown_or_extra_rule_fails_closed() -> None:
    document = load()
    document["desired_ruleset"]["rules"].append({"type": "required_signatures"})
    assert "ruleset must contain exactly the four frozen rule types" in MODULE.validate(document)


def test_approval_or_check_name_drift_fails_closed() -> None:
    approval = load()
    next(rule for rule in approval["desired_ruleset"]["rules"] if rule["type"] == "pull_request")["parameters"]["required_approving_review_count"] = 1
    assert "pull request rule must not require approvals" in MODULE.validate(approval)
    context = load()
    next(rule for rule in context["desired_ruleset"]["rules"] if rule["type"] == "required_status_checks")["parameters"]["required_status_checks"][0]["context"] = "G0 / exact-head "
    assert "required check context is not exact" in MODULE.validate(context)


def test_applied_readback_and_rollback_must_bind_same_rule() -> None:
    document = load()
    document["phase"] = "applied"
    document["readback"] = {"id": 7, **copy.deepcopy(document["desired_ruleset"])}
    document["after_sha256"] = MODULE.digest(document["readback"])
    document["rollback"]["created_rule_id"] = 8
    document["remote_mutation_performed"] = True
    assert "rollback does not bind the created rule ID" in MODULE.validate(document)
