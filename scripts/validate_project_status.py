#!/usr/bin/env python3
"""Fail-closed project-status v2 validator using only the Python standard library."""

from __future__ import annotations

import argparse
import copy
import functools
import hashlib
import json
import re
import shlex
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
G0_GOVERNED_PARENT_SHA = "48904701f31ad12b08d0d224c25bd65003356230"
G0_T02_FAILED_MAIN_SHA = "608800462fbf9f3b97277484fa906a691b8b8b98"
G0_T02_FAILED_MAIN_RUN = "29884710636"
G0_T02_FAILED_MAIN_URL = "https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/29884710636"
G0_T02_RECOVERY_MAIN_SHA = "c5a488482fffb7183790f36701411d91b2a2bba0"
G0_T02_CLOSURE_SHA = "41868a5eff635d9f83dccaba4ad3e6e38433822c"
G0_T02_CLOSURE_RUN = "29884474658"
G0_T02_FINALIZATION_SHA = "0a8048df7197ece027287c3397783f37630ff0e6"
G0_T02_FINALIZATION_RUN = "29888131234"
G0_T02_CLOSED_RECORD_SHA = "231d3d0e4756889e8fa3fc5803df6701088556e8"
G0_T02_FINAL_CLOSE_MERGE_SHA = "d0dcc837715ea29c7b08f9ef6a7212894e4098bb"
G0_T02_RECOVERY_BLOCKER = (
    "post_merge_ci_failure repository=weizhenhaihaha-arch/yaobizuoduo event=push "
    f"ref=refs/heads/main subject_sha={G0_T02_FAILED_MAIN_SHA} run_id={G0_T02_FAILED_MAIN_RUN} "
    f"url={G0_T02_FAILED_MAIN_URL} conclusion=failure"
)
G0_T03_FAILED_MAIN_SHA = "08d6a3ea8d1898dbe47c7eaf9c82cb7adf1db68f"
G0_T03_FAILED_MAIN_RUN = "29894526319"
G0_T03_FAILED_MAIN_URL = "https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/29894526319"
G0_T03_ACCEPTED_RECORD_SHA = "85509b6dc1b156d3347b6b21ff952d8e55ac18d3"
G0_T03_CANDIDATE_SHA = "6ca1ace6af66f874eed38f644104f59bbc4009ad"
G0_T03_IMPLEMENTATION_SHA = "a247cd33e5e31dc4889fa611192c9a8f7c043b04"
G0_T03_AUTHORIZATION_SHA = "c1e3ebacefc8839bc6f4c32f3bc2c31cc890d398"
G0_T03_BLOCKED_SHA = "3046d8bb023e169d3b64bfbe7093eee3ec52f722"
G0_T03_ACCEPTED_STATUS_DIGEST = "0efcdc4909d2f646bcfe3b41ab6e4b01e3f89aba110cc90b405ac4d99d4843bf"
G0_T03_RECOVERY_BLOCKER = (
    "post_merge_ci_failure repository=weizhenhaihaha-arch/yaobizuoduo event=push "
    f"ref=refs/heads/main subject_sha={G0_T03_FAILED_MAIN_SHA} run_id={G0_T03_FAILED_MAIN_RUN} "
    f"url={G0_T03_FAILED_MAIN_URL} conclusion=failure"
)
G0_T03_RECOVERY_CANDIDATE_SHA = "a0885c16582e75613bb203be3a2ecefb01637d37"
G0_T03_RECOVERY_CANDIDATE_RUN = "29896682124"
G0_T03_RECOVERY_ACCEPTED_RECORD_SHA = "0b5279b69b70b70500f22753cb6ae3a542b196c7"
G0_T03_RECOVERY_MERGE_SHA = "bea5cf840ddf45ec4425796861d8956f682ab564"
G0_T03_RECOVERY_MERGE_RUN = "29898504840"
G0_T03_RECOVERY_STATUS_DIGEST = "99e9f5bfdaa17955555e116464ae8f54eb664f7ac4709c22db465ccb0b6543ca"
G0_T03_RECOVERY_MERGE_BLOCKER = (
    "post_merge_ci_failure repository=weizhenhaihaha-arch/yaobizuoduo event=push "
    f"ref=refs/heads/main subject_sha={G0_T03_RECOVERY_MERGE_SHA} run_id={G0_T03_RECOVERY_MERGE_RUN} "
    "url=https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/29898504840 conclusion=failure"
)
G0_T03_RECOVERY_CLOSURE_RECEIPT_PATH = "evidence/g0-t03/recovery-merge-closure-acceptance.json"
G0_T03_RECOVERY_CLOSURE_RECEIPT_VERSION = "g0-t03-recovery-merge-closure.v1"
G0_T03_FINALIZATION_SHA = "e4fd7ae620955867ac0c6914aff2c913420c3ba2"
G0_T03_FINALIZATION_RUN = "29906677035"
G0_T03_CLOSED_RECORD_SHA = "cf15b25533769c7f589dd5dad275627802d9ae7d"
G0_T03_CLOSED_RECORD_RUN = "29907836986"
G0_T03_FINAL_CLOSE_MERGE_SHA = "b1544c168cf3acf9e0ce0c1c7e3785041c02e87c"
G0_T03_FINAL_CLOSE_MERGE_RUN = "29909220290"
G0_T03_FINAL_CLOSE_BLOCKER = (
    "post_merge_ci_failure repository=weizhenhaihaha-arch/yaobizuoduo event=push "
    f"ref=refs/heads/main subject_sha={G0_T03_FINAL_CLOSE_MERGE_SHA} "
    f"run_id={G0_T03_FINAL_CLOSE_MERGE_RUN} "
    f"url=https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/{G0_T03_FINAL_CLOSE_MERGE_RUN} "
    "conclusion=failure"
)
G0_T03_FINAL_CLOSE_RECEIPT_PATH = "evidence/g0-t03/final-close-recovery-acceptance.json"
G0_T03_FINAL_CLOSE_RECEIPT_VERSION = "g0-t03-final-close-recovery.v1"
G0_T03_FINAL_CLOSE_BINDING_PATH = "evidence/g0-t03/final-close-reviewed-run-binding.json"
G0_T03_FINAL_CLOSE_BINDING_VERSION = "g0-t03-final-close-reviewed-run-binding.v1"
G0_T03_RECOVERED_MAIN_SHA = "02e05d1f2d68a9a1c89fda9c8636e2263fc48053"
G0_T03_RECOVERED_MAIN_RUN = "29929973216"
G0_T03_PLANNING_HANDOFF_SHA = "e1d251c35bbfc128990be4f9e3d1b851a3146f12"
G0_T03_PLANNING_HANDOFF_FIRST_PARENT = G0_T03_RECOVERED_MAIN_SHA
G0_T03_PLANNING_HANDOFF_SECOND_PARENT = "b8f04c9bbc3f86b6ef643cdd097ec7dc46c16e5b"
G0_T03_PLANNING_HANDOFF_TREE = "5f0fbfe0f5ec19a6a8c2c7b59f5c07ab5d3f91bc"
G0_T03_PLANNING_HANDOFF_PR_RUN = "29932171250"
G0_T03_PLANNING_HANDOFF_MAIN_RUN = "29933844415"
G0_T03_STATUS_RECONCILIATION_BASE_SHA = "c11eae14986de8bb5f387e3064680ce48d2c284b"
G0_T03_STATUS_RECONCILIATION_BASE_RUN = "29956605323"
G0_T03_STATUS_RECONCILIATION_FIRST_PARENT = G0_T03_PLANNING_HANDOFF_SHA
G0_T03_STATUS_RECONCILIATION_SECOND_PARENT = "7bbe1e291833010f01e35ac4c46d6dc512b1f2c6"
G0_T03_STATUS_RECONCILIATION_TREE = "d9f639b5d3261a8621c26a212108884a92dbbffc"
G0_T03_STATUS_RECONCILIATION_PR_RUN = "29936794730"
G0_T03_STATUS_RECONCILIATION_PATH = "evidence/g0-t03/post-recovery-status-reconciliation.json"
G0_T03_STATUS_RECONCILIATION_VERSION = "g0-t03-post-recovery-status-reconciliation.v1"
G0_T03_RULESET_ID = 19526291
G0_T03_RULESET_EVIDENCE_DIGEST = "73aa3644a4c571c7101b0ac36547bd1be2edc306846045d2d36ad07ac86c5bb1"
G0_T04_CANDIDATE_SHA = "be45d7fee1f5e4a34b14bd035539d5a3a462dad8"
G0_T04_CANDIDATE_RUN = "29987891035"
G0_T04_CLOSURE_SHA = "bdf6fbca71b29da79801c1be7a4cdd14f103ce52"
G0_T04_CLOSURE_RUN = "29988100257"
G0_T04_FAILED_MAIN_SHA = "11040ca0d8ea17ba1bc47641705aa95c2cba6a75"
G0_T04_FAILED_MAIN_RUN = "29988167026"
G0_T04_FAILED_MAIN_FIRST_PARENT = "1671568fd5bb33d1e316f8cbe8e9708d7d4d5d1f"
G0_T04_FAILED_MAIN_SECOND_PARENT = G0_T04_CLOSURE_SHA
G0_T04_FAILED_MAIN_TREE = "12d85f91119ee802d3f92405ceb619ed18534e4d"
G0_T04_ACCEPTED_STATUS_DIGEST = "77d3f6a041a9342b38faa811d6d9f5e01a8afb003dea882ed2f93a08f0a0a51d"
G0_T04_RECOVERY_RECEIPT_PATH = "evidence/g0-t04/merged-main-recovery.json"
G0_T04_RECOVERY_RECEIPT_VERSION = "g0-t04-merged-main-recovery.v1"
G0_T04_RECOVERY_BLOCKER = (
    "post_merge_ci_failure repository=weizhenhaihaha-arch/yaobizuoduo event=push "
    f"ref=refs/heads/main subject_sha={G0_T04_FAILED_MAIN_SHA} "
    f"run_id={G0_T04_FAILED_MAIN_RUN} "
    f"url=https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/{G0_T04_FAILED_MAIN_RUN} "
    "conclusion=failure"
)
G0_T04_RECOVERY_ALLOWED_PATHS = frozenset(
    {
        "PROJECT_STATUS.yaml",
        "CURRENT_TASK.md",
        "PROJECT_MEMORY.md",
        G0_T04_RECOVERY_RECEIPT_PATH,
        "scripts/validate_project_status.py",
        "tests/test_g0_project_status.py",
    }
)
G0_T04_RECOVERY_REQUIRED_PATHS = frozenset(
    {
        "PROJECT_STATUS.yaml",
        G0_T04_RECOVERY_RECEIPT_PATH,
        "scripts/validate_project_status.py",
        "tests/test_g0_project_status.py",
    }
)
PACKAGE_A_MANIFEST_PATH = "governance/packages/package-a.manifest.json"
PACKAGE_A_SCHEMA_PATH = "schemas/package_a_manifest.schema.json"
PACKAGE_A_SCHEMA_VERSION = "package-a-manifest.v2"
PACKAGE_A_BASELINE_SHA = "1671568fd5bb33d1e316f8cbe8e9708d7d4d5d1f"
PACKAGE_A_SCHEMA_SHA256 = "5ebc757f76c58424e88fa6618c806c1bb73ad9dfa9bc09302481e5206c94ceda"
PACKAGE_A_PAYLOAD_SHA256 = "815a40dc1fb47b367e1fe5707c16911862feeb929b0356aff769d0544500ca27"
PACKAGE_A_SUPERSEDED_PAYLOAD_SHA256 = "a7f69d3aacfecb9511e602ce649c80cc4e5a53409928a773abb6ff1eb16d41ff"
PACKAGE_A_ACTIVATION_PATH = "evidence/g0-t05/package-a-activation.json"
PACKAGE_A_ACTIVATION_VERSION = "package-a-activation.v1"
PACKAGE_A_ORDERED_TASKS = ["G0-T05", "G1-T01"]
G0_T04_ANOMALY_MAIN = "4f358cf42b9a8e0f741563425fc26cf532df98fb"
G0_T04_ANOMALY_ORIGIN = "8f3cfc2ba8c7ba533c8e7d065c0f7e5c27a3e373"
G0_T04_ANOMALY_IMPLEMENTATION = "69c045de1e80bcb90c1b5ce5a49b640e48047d32"
G0_T04_ANOMALY_CANDIDATE = "6541189bbdacc870de5691d07991b9103ee2c763"
G0_T04_ANOMALY_SEAL = "50a801f2f81c9c6f5eaea99444529fcbeb5933c2"
G0_T04_ANOMALY_MERGE = "a88b4f9e5fa7d498aeb338ec9e8bbbe198241a87"
G0_T04_ANOMALY_RECEIPT_PATH = "evidence/g0-t04/pr15-pr22-review-chain.json"
G0_T04_ANOMALY_SEAL_PATH = "evidence/g0-t04/pr15-pr22-recovery-seal.json"
G0_T04_ANOMALY_SEAL_VERSION = "g0-t04-pr15-pr22-recovery-seal.v1"
G0_T04_ANOMALY_BLOCKER = (
    "governance_anomaly current_main=4f358cf42b9a8e0f741563425fc26cf532df98fb "
    "pr15_pr17_pr19_reviews=empty pr20_pr21_pr22_reviews=empty "
    "false_owner_confirmation=true g0_t05=not_authorized g1=not_authorized "
    "code_security=request_changes architecture=block"
)
G0_T04_ANOMALY_ALLOWED = {
    "PROJECT_STATUS.yaml",
    "CURRENT_TASK.md",
    "PROJECT_MEMORY.md",
    "docs/NEXT_WORKFLOW.md",
    G0_T04_ANOMALY_RECEIPT_PATH,
    PACKAGE_A_ACTIVATION_PATH,
    "scripts/validate_project_status.py",
    "tests/test_g0_project_status.py",
}
G0_T04_ANOMALY_REQUIRED = frozenset(G0_T04_ANOMALY_ALLOWED)
G0_T04_ANOMALY_SEAL_ALLOWED = frozenset(
    {
        "PROJECT_STATUS.yaml",
        "CURRENT_TASK.md",
        "PROJECT_MEMORY.md",
        "docs/NEXT_WORKFLOW.md",
        G0_T04_ANOMALY_SEAL_PATH,
        "scripts/validate_project_status.py",
        "tests/test_g0_project_status.py",
    }
)
G0_T04_ANOMALY_POST_MERGE_REPAIR_ALLOWED = frozenset(
    {
        "PROJECT_MEMORY.md",
        "scripts/validate_project_status.py",
        "tests/test_g0_project_status.py",
    }
)
G0_T04_G4_AUTHORIZATION = "376aa67c5abf81aaf037b21fd833474bf704395d"
G0_T04_G4_START = "39a50d9ea1d97e2fe3925ffa355eb787165bc1d6"
G0_T04_G4_BLOCKED_MAIN = "414fa392026c71b01378c64cbf62cb6b304b2eed"
G0_T04_G4_BASELINE = "1671568fd5bb33d1e316f8cbe8e9708d7d4d5d1f"
G0_T04_G4_PR24_HEAD = "db507f75f46196a03a9d87725be5946e6f05575c"
G0_T04_G4_PR24_RUN = "30014856791"
G0_T04_G4_ABANDONED_AUTH = "de070276e53ec75f0cfd864a02d6d05236784eb8"
G0_T04_G4_ABANDONED_START = "c7be2b2f07ef171e9d1535e29d93aa6beadf348a"
G0_T04_G4_ABANDONED_CANDIDATE = "45e714f9e099774ac0c4885f77523fb73c2d313d"
G0_T04_G4_COMPETING_AUTH = "046414bea45316f01e3d3e7b556b4c06d489c03b"
G0_T04_G4_COMPETING_START = "906cb1124f60f83c4bcdeaf0d2a47e1c6d4332d7"
G0_T04_G4_EXCLUDED_ROUTE_NODES = (
    G0_T04_G4_ABANDONED_AUTH,
    G0_T04_G4_ABANDONED_START,
    G0_T04_G4_ABANDONED_CANDIDATE,
    G0_T04_G4_COMPETING_AUTH,
    G0_T04_G4_COMPETING_START,
)
G0_T04_G4_ROUTE_SEAL_PATH = (
    "evidence/g0-t04/generation-4-main-drift-seal.json"
)
G0_T04_G4_ROUTE_SEAL_VERSION = "g0-t04-generation-4-main-drift-seal.v1"
G0_T04_G4_ROUTE_SEAL_PAYLOAD = (
    "87b9b2b0ab285de6ef7d9850203b083315a630efae23427b23a4b08e5ce71146"
)
G0_T04_G4_G1_BLOCKED = "3a27f530b338ece78ae90ffd895787e5a10616fc"
G0_T04_G4_G1_MERGE_BASE = "4f358cf42b9a8e0f741563425fc26cf532df98fb"
G0_T04_G4_PREMATURE_MAIN = "8a7b8aca2b59a5598f0e721f557c06a008f362e0"
G0_T04_G4_PREMATURE_MAIN_FIRST_PARENT = G0_T04_G4_BLOCKED_MAIN
G0_T04_G4_PREMATURE_MAIN_SECOND_PARENT = (
    "c22bc286b2ee30a0cdaf40a82223bc6f15133af5"
)
G0_T04_G4_PREMATURE_MAIN_TREE = "930c41200f0f94fb64e40aa19d3adc4323f8276c"
G0_T04_G4_PREMATURE_MAIN_STATUS_BLOB = (
    "a0c097ed92896b0d8b6b958e19655b5a1e8d110d"
)
G0_T04_G4_PREMATURE_MAIN_STATUS_DIGEST = (
    "2b988b6a14c64c507b3dcbed33eba27e28ac13f371c85a665ead2c222661dc52"
)
G0_T04_G4_PREMATURE_PR = 26
G0_T04_G4_PREMATURE_PR_RUN = "30028693653"
G0_T04_G4_PREMATURE_MAIN_RUN = "30028739788"
G0_T04_G4_PREMATURE_RECEIPT_PATH = (
    "evidence/g0-t04/generation-4-premature-merge-recovery.json"
)
G0_T04_G4_PREMATURE_RECEIPT_VERSION = (
    "g0-t04-generation-4-premature-merge-recovery.v1"
)
G0_T04_G4_MERGED_VERIFICATION_RECEIPT_VERSION = (
    "g0-t04-generation-4-premature-merge-recovery.v2"
)
G0_T04_G4_FINALIZATION_CLOSE_RECEIPT_VERSION = (
    "g0-t04-generation-4-premature-merge-recovery.v3"
)
G0_T04_G4_RECOVERY_CANDIDATE = (
    "388a75b18f37ddd970a37938dba8b955dc95e719"
)
G0_T04_G4_RECOVERY_CANDIDATE_RUN = "30036514625"
G0_T04_G4_RECOVERY_ACCEPTANCE = (
    "9652fabb655b1d678ef7677f173c2f15d65f881d"
)
G0_T04_G4_RECOVERY_ACCEPTANCE_RUN = "30037270342"
G0_T04_G4_RECOVERY_MERGED_MAIN = (
    "1419f7c77ff102fd68eb9583f5ec5c3b196ae4be"
)
G0_T04_G4_RECOVERY_MERGED_MAIN_RUN = "30037311721"
G0_T04_G4_RECOVERY_ACCEPTED_TREE = (
    "1746a81c49d6dd4164925c04b476808e22b66ccc"
)
G0_T04_G4_RECOVERY_BRANCH_REF = (
    "refs/heads/codex/g0-t04-g4-premature-merge-recovery"
)
G0_T04_G4_MERGED_VERIFICATION = (
    "80effc864ce6788ebf6be8485ca1273ae52de538"
)
G0_T04_G4_MERGED_VERIFICATION_RUN = "30039415469"
G0_T04_G4_MERGED_VERIFICATION_BRANCH_REF = (
    "refs/heads/codex/g0-t04-g4-merged-verification"
)
G0_T04_G4_PREMATURE_BLOCKER = (
    "premature_merge_main_ci_failure "
    "repository=weizhenhaihaha-arch/yaobizuoduo event=push "
    "ref=refs/heads/main "
    f"subject_sha={G0_T04_G4_PREMATURE_MAIN} "
    f"run_id={G0_T04_G4_PREMATURE_MAIN_RUN} "
    "url=https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/"
    f"{G0_T04_G4_PREMATURE_MAIN_RUN} conclusion=failure"
)
G0_T04_G4_PREMATURE_ALLOWED = frozenset(
    {
        "PROJECT_STATUS.yaml",
        "CURRENT_TASK.md",
        "PROJECT_MEMORY.md",
        "docs/NEXT_WORKFLOW.md",
        G0_T04_G4_PREMATURE_RECEIPT_PATH,
        "scripts/validate_project_status.py",
        "tests/test_g0_project_status.py",
    }
)
G0_T04_G4_PREMATURE_REQUIRED = frozenset(
    {
        "PROJECT_STATUS.yaml",
        "CURRENT_TASK.md",
        "PROJECT_MEMORY.md",
        "docs/NEXT_WORKFLOW.md",
        G0_T04_G4_PREMATURE_RECEIPT_PATH,
        "scripts/validate_project_status.py",
        "tests/test_g0_project_status.py",
    }
)
G0_T04_G4_ALLOWED = frozenset(
    {
        "PROJECT_STATUS.yaml",
        "CURRENT_TASK.md",
        "PROJECT_MEMORY.md",
        "docs/NEXT_WORKFLOW.md",
        G0_T04_G4_ROUTE_SEAL_PATH,
        "scripts/validate_project_status.py",
        "tests/test_g0_project_status.py",
    }
)
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


def _package_a_manifest_errors(
    root: Path, subject_sha: str | None = None
) -> list[str]:
    """Validate the immutable, still-inactive Package A planning artifact."""

    subject = subject_sha or "HEAD"

    def read_regular_blob(relative: str) -> tuple[bool, bytes]:
        ok_entry, entry = _git(root, "ls-tree", subject, "--", relative)
        fields = entry.split(None, 3) if ok_entry else []
        if (
            len(fields) != 4
            or fields[0] != "100644"
            or fields[1] != "blob"
            or fields[3] != relative
        ):
            return False, b""
        return _git_bytes(root, "show", f"{subject}:{relative}")

    ok_manifest, manifest_bytes = read_regular_blob(PACKAGE_A_MANIFEST_PATH)
    ok_schema, schema_bytes = read_regular_blob(PACKAGE_A_SCHEMA_PATH)
    if not ok_manifest or not ok_schema:
        return [
            "$: Package A manifest and schema must be exact committed 100644 Git blobs"
        ]
    try:
        manifest_text = manifest_bytes.decode("utf-8")
        schema_text = schema_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return ["$: Package A manifest or schema is not UTF-8"]
    try:
        manifest = json.loads(
            manifest_text, object_pairs_hook=_reject_duplicate_keys
        )
        manifest_schema = json.loads(
            schema_text, object_pairs_hook=_reject_duplicate_keys
        )
    except (json.JSONDecodeError, TypeError, ValueError):
        return ["$: Package A manifest or schema is not canonical JSON"]
    if type(manifest) is not dict or type(manifest_schema) is not dict:
        return ["$: Package A manifest and schema roots must be objects"]

    errors = [
        f"$.package_a{item[1:]}"
        for item in _schema_errors(
            manifest, manifest_schema, manifest_schema
        )
    ]
    schema_digest = hashlib.sha256(schema_bytes).hexdigest()
    if (
        schema_digest != PACKAGE_A_SCHEMA_SHA256
        or manifest.get("schema_sha256") != PACKAGE_A_SCHEMA_SHA256
    ):
        errors.append("$.package_a.schema_sha256: immutable schema bytes drifted")
    if manifest.get("payload_sha256") != _payload_digest(manifest):
        errors.append("$.package_a.payload_sha256: normalized payload digest mismatch")
    if manifest.get("payload_sha256") != PACKAGE_A_PAYLOAD_SHA256:
        errors.append("$.package_a.payload_sha256: immutable accepted planning payload drifted")
    if manifest.get("payload_sha256") == PACKAGE_A_SUPERSEDED_PAYLOAD_SHA256:
        errors.append("$.package_a.payload_sha256: superseded generation-1 digest is forbidden")

    cards = manifest.get("cards")
    ordered = manifest.get("ordered_task_ids")
    expected_identity = {
        "schema_version": PACKAGE_A_SCHEMA_VERSION,
        "package_id": "PACKAGE-A",
        "package_state": "not_authorized",
        "manifest_path": PACKAGE_A_MANIFEST_PATH,
        "schema_path": PACKAGE_A_SCHEMA_PATH,
        "generation": 2,
        "supersedes_payload_sha256": PACKAGE_A_SUPERSEDED_PAYLOAD_SHA256,
        "authoritative_baseline_sha": PACKAGE_A_BASELINE_SHA,
        "canonical_serialization": "utf8-json-sort-keys-compact-excluding-payload_sha256.v1",
        "first_task_id": PACKAGE_A_ORDERED_TASKS[0],
        "last_task_id": PACKAGE_A_ORDERED_TASKS[-1],
        "ordered_task_ids": PACKAGE_A_ORDERED_TASKS,
    }
    for key, value in expected_identity.items():
        if not _typed_equal(manifest.get(key), value):
            errors.append(f"$.package_a.{key}: immutable identity drifted")

    if type(cards) is not list or [card.get("task_id") for card in cards if type(card) is dict] != PACKAGE_A_ORDERED_TASKS:
        errors.append("$.package_a.cards: cards must exactly match the ordered unique task list")
    elif type(ordered) is list:
        for index, card in enumerate(cards):
            task_id = card["task_id"]
            gate = card["gate"]
            review = card["independent_review"]
            continuation = card["automatic_continuation"]
            if task_id == "G0-T04" or task_id.split("-", 1)[0] != gate:
                errors.append("$.package_a.cards: planning task reuse or gate mismatch is forbidden")
            if review != {"code_security": "APPROVE", "architecture_route": "CLEAR"}:
                errors.append(f"$.package_a.cards[{index}]: independent dual review is mandatory")
            expected_next = ordered[index + 1] if index + 1 < len(ordered) else None
            if continuation.get("next_task_id") != expected_next:
                errors.append(f"$.package_a.cards[{index}]: continuation is not strictly serial")
            if continuation.get("allowed") is not (expected_next is not None):
                errors.append(f"$.package_a.cards[{index}]: continuation permission is inconsistent")
            if continuation.get("requires_same_package") is not True:
                errors.append(f"$.package_a.cards[{index}]: cross-package continuation is forbidden")
            for command in card["acceptance_commands"]:
                try:
                    tokens = shlex.split(command)
                except ValueError:
                    errors.append(f"$.package_a.cards[{index}]: acceptance command is not parseable")
                    continue
                test_paths: set[str] = set()
                for token in tokens:
                    if token.startswith("--ignore="):
                        test_paths.add(token.removeprefix("--ignore="))
                    elif token.startswith("tests/") and token.endswith(".py"):
                        test_paths.add(token)
                for test_path in test_paths:
                    ok_test, test_entry = _git(
                        root, "ls-tree", subject, "--", test_path
                    )
                    test_fields = test_entry.split(None, 3) if ok_test else []
                    if (
                        len(test_fields) != 4
                        or test_fields[0] not in {"100644", "100755"}
                        or test_fields[1] != "blob"
                        or test_fields[3] != test_path
                    ):
                        errors.append(
                            f"$.package_a.cards[{index}]: acceptance test path does not exist: {test_path}"
                        )

    activation = manifest.get("activation")
    if activation != {
        "product_owner_digest_confirmation_required": True,
        "confirmed_payload_sha256": None,
        "first_task_state": "not_authorized",
        "activation_record_path": PACKAGE_A_ACTIVATION_PATH,
        "automatic_cross_package_continuation": False,
    }:
        errors.append("$.package_a.activation: Package A must remain explicitly inactive")
    return errors


def _g0_t04_package_a_changed_path_errors(
    root: Path, subject_sha: str
) -> list[str]:
    ok, text = _git(
        root, "diff", "--name-only", PACKAGE_A_BASELINE_SHA, subject_sha
    )
    if not ok:
        return ["$: G0-T04 changed-path proof is unavailable"]
    changed = {line for line in text.splitlines() if line}
    allowed = {
        "PROJECT_STATUS.yaml",
        "CURRENT_TASK.md",
        "PROJECT_MEMORY.md",
        "README.md",
        "DEVELOPMENT_WORKFLOW.md",
        "AG_WORK_LOOP.md",
        "docs/NEXT_WORKFLOW.md",
        PACKAGE_A_MANIFEST_PATH,
        PACKAGE_A_SCHEMA_PATH,
        "scripts/validate_project_status.py",
        "tests/test_g0_project_status.py",
    }
    required = {
        "PROJECT_STATUS.yaml",
        "CURRENT_TASK.md",
        "PROJECT_MEMORY.md",
        "README.md",
        "docs/NEXT_WORKFLOW.md",
        PACKAGE_A_MANIFEST_PATH,
        PACKAGE_A_SCHEMA_PATH,
        "scripts/validate_project_status.py",
        "tests/test_g0_project_status.py",
    }
    errors: list[str] = []
    if not required.issubset(changed) or not changed.issubset(allowed):
        errors.append("$: G0-T04 changed paths violate the frozen planning-only allowlist")
    for relative in (PACKAGE_A_MANIFEST_PATH, PACKAGE_A_SCHEMA_PATH):
        ok_prior, _ = _git(
            root, "cat-file", "-e", f"{PACKAGE_A_BASELINE_SHA}:{relative}"
        )
        if ok_prior:
            errors.append(f"$: G0-T04 immutable artifact must be newly introduced: {relative}")
    return errors


def _package_a_activation_errors(
    status: dict[str, Any], root: Path, subject_sha: str
) -> list[str]:
    ok_entry, entry = _git(
        root, "ls-tree", subject_sha, "--", PACKAGE_A_ACTIVATION_PATH
    )
    fields = entry.split(None, 3) if ok_entry else []
    if (
        len(fields) != 4
        or fields[0] != "100644"
        or fields[1] != "blob"
        or fields[3] != PACKAGE_A_ACTIVATION_PATH
    ):
        return ["$: Package A activation must be an exact committed 100644 Git blob"]
    ok_blob, payload = _git_bytes(
        root, "show", f"{subject_sha}:{PACKAGE_A_ACTIVATION_PATH}"
    )
    try:
        activation = json.loads(
            payload.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys
        ) if ok_blob else None
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        activation = None
    if type(activation) is not dict:
        return ["$: Package A activation evidence is not canonical JSON"]
    expected_keys = {
        "schema_version",
        "package_id",
        "package_generation",
        "manifest_path",
        "schema_path",
        "manifest_payload_sha256",
        "first_task_id",
        "package_state",
        "product_owner_confirmation",
        "g0_t04_closed_sha",
        "payload_sha256",
    }
    errors: list[str] = []
    if set(activation) != expected_keys:
        errors.append("$.package_a_activation: inexact field set")
    expected = {
        "schema_version": PACKAGE_A_ACTIVATION_VERSION,
        "package_id": "PACKAGE-A",
        "package_generation": 2,
        "manifest_path": PACKAGE_A_MANIFEST_PATH,
        "schema_path": PACKAGE_A_SCHEMA_PATH,
        "manifest_payload_sha256": PACKAGE_A_PAYLOAD_SHA256,
        "first_task_id": PACKAGE_A_ORDERED_TASKS[0],
        "package_state": "authorized",
        "product_owner_confirmation": "exact_payload_digest_confirmed",
    }
    for key, value in expected.items():
        if not _typed_equal(activation.get(key), value):
            errors.append(f"$.package_a_activation.{key}: activation identity drifted")
    if activation.get("payload_sha256") != _payload_digest(activation):
        errors.append("$.package_a_activation.payload_sha256: digest mismatch")
    closed_sha = activation.get("g0_t04_closed_sha")
    closed_status = (
        _status_at(root, closed_sha)
        if type(closed_sha) is str and re.fullmatch(r"[0-9a-f]{40}", closed_sha)
        else None
    )
    try:
        valid_closed = (
            type(closed_status) is dict
            and closed_status["active_tasks"][0].get("task_id") == "G0-T04"
            and closed_status["active_tasks"][0].get("state") == "closed"
            and _is_ancestor(root, closed_sha, subject_sha)
        )
    except (KeyError, IndexError, TypeError):
        valid_closed = False
    if not valid_closed:
        errors.append("$.package_a_activation.g0_t04_closed_sha: must bind an ancestor closed G0-T04")
    if status["active_tasks"][0]["task_id"] == "G0-T05" and closed_sha != status["evidence"]["authorization_baseline_sha"]:
        errors.append("$.package_a_activation.g0_t04_closed_sha: G0-T05 must start from the bound close")
    return errors


def _package_a_persistence_errors(
    status: dict[str, Any], root: Path, head: str
) -> list[str]:
    """Keep accepted Package A blobs and card scopes frozen after G0-T04."""

    task = status["active_tasks"][0]
    task_id = task["task_id"]
    if task_id == "G0-T04":
        return _package_a_manifest_errors(root, head)
    if task_id not in PACKAGE_A_ORDERED_TASKS:
        return []

    baseline = status["evidence"]["authorization_baseline_sha"]
    head_has_package = _git(
        root, "cat-file", "-e", f"{head}:{PACKAGE_A_MANIFEST_PATH}"
    )[0]
    baseline_has_package = _git(
        root, "cat-file", "-e", f"{baseline}:{PACKAGE_A_MANIFEST_PATH}"
    )[0]
    # Legacy or unrelated fixtures using the same task IDs predate Package A.
    # A real Package A transition is permanently in scope once either the
    # accepted baseline or current tree carries its manifest.
    if not head_has_package and not baseline_has_package:
        return []

    errors = _package_a_manifest_errors(root, head)
    errors.extend(_package_a_manifest_errors(root, baseline))
    expected_previous = "G0-T04" if task_id == "G0-T05" else "G0-T05"
    baseline_status = _status_at(root, baseline)
    try:
        valid_baseline = (
            type(baseline_status) is dict
            and baseline_status["active_tasks"][0].get("task_id") == expected_previous
            and baseline_status["active_tasks"][0].get("state") == "closed"
        )
    except (KeyError, IndexError, TypeError):
        valid_baseline = False
    if not valid_baseline:
        errors.append(
            f"$.package_a: {task_id} baseline must be the exact closed {expected_previous}"
        )
    for relative in (PACKAGE_A_MANIFEST_PATH, PACKAGE_A_SCHEMA_PATH):
        ok_current, current_blob = _git(root, "rev-parse", f"{head}:{relative}")
        ok_base, base_blob = _git(root, "rev-parse", f"{baseline}:{relative}")
        if not ok_current or not ok_base or current_blob != base_blob:
            errors.append(f"$.package_a: immutable blob drifted after accepted baseline: {relative}")

    errors.extend(_package_a_activation_errors(status, root, head))
    if task_id == "G1-T01":
        ok_current, current_activation = _git(
            root, "rev-parse", f"{head}:{PACKAGE_A_ACTIVATION_PATH}"
        )
        ok_base, base_activation = _git(
            root, "rev-parse", f"{baseline}:{PACKAGE_A_ACTIVATION_PATH}"
        )
        if not ok_current or not ok_base or current_activation != base_activation:
            errors.append("$.package_a_activation: immutable activation drifted after G0-T05 close")

    ok_manifest, manifest_bytes = _git_bytes(
        root, "show", f"{baseline}:{PACKAGE_A_MANIFEST_PATH}"
    )
    try:
        manifest = json.loads(
            manifest_bytes.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        ) if ok_manifest else None
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        manifest = None
    cards = manifest.get("cards") if type(manifest) is dict else None
    card = next(
        (
            item
            for item in cards
            if type(item) is dict and item.get("task_id") == task_id
        ),
        None,
    ) if type(cards) is list else None
    ok_diff, changed_text = _git(root, "diff", "--name-only", baseline, head)
    changed = {line for line in changed_text.splitlines() if line} if ok_diff else None
    allowed_paths = set(card.get("allowed_paths", [])) if type(card) is dict else set()
    if changed is None or not changed.issubset(allowed_paths):
        errors.append(f"$.package_a.cards: {task_id} changed paths exceed its immutable allowlist")
    return errors


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
    recovery_transition = (
        _is_g0_t04_anomaly_status(status)
        or _is_g0_t04_anomaly_seal_status(status)
        or _is_g0_t04_post_merge_recovery_status(status)
        or _is_g0_t02_post_merge_recovery_status(status)
        or _is_g0_t03_post_merge_recovery_status(status)
        or _is_g0_t03_recovery_merge_recovery_status(status)
        or _is_g0_t03_final_close_recovery_status(status)
        or _is_g0_t03_status_reconciled(status)
    )
    if transition["to"] not in TRANSITIONS.get(transition["from"], set()) and not recovery_transition:
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
    # Git cannot enumerate absent or unreachable objects. The complete enforceable visible-ref
    # policy is every commit reachable from local branches, fetched remote-tracking refs, or tags.
    ok, refs_text = _git(root, "for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes", "refs/tags")
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
        if len(parts) < 2:
            return None
        parent = _status_at(root, parts[1])
        parent_authority = parent.get("schema_authority") if type(parent) is dict else None
        task = node["active_tasks"][0] if type(node) is dict and type(node.get("active_tasks")) is list and node["active_tasks"] else None
        if (
            not _typed_equal(authority, parent_authority)
            and type(task) is dict
            and task.get("state") == "in_progress"
            and task.get("transition") == {"from": "authorized", "to": "in_progress"}
            and _typed_equal(parts[1], authorization_sha)
        ):
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
    return []


def _schema_migration_final_route_errors(status: dict[str, Any], root: Path) -> list[str]:
    task_state = status["active_tasks"][0]["state"]
    authority = status.get("schema_authority")
    migration = authority.get("migration") if type(authority) is dict else None
    if task_state not in {"merged_verified", "closed"} or type(authority) is not dict or authority.get("revision") == 1 or type(migration) is not dict:
        return []
    authorization_sha = migration.get("authorization_sha")
    if type(authorization_sha) is not str:
        return ["$.schema_authority: final migration authorization identity is unavailable"]
    consumers = _schema_migration_consumers(root, authorization_sha)
    if consumers is None or len(consumers) != 1:
        return ["$.schema_authority: final state requires one repository-visible migration consumer"]
    consumer = next(iter(consumers))
    merged = status["evidence"]["merged_main"]["commit_sha"]
    ok, remote_main = _git(root, "rev-parse", "--verify", "refs/remotes/origin/main")
    if type(merged) is not str or not ok or not _is_first_parent_ancestor(root, merged, remote_main) or not _is_ancestor(root, consumer, merged):
        return ["$.schema_authority: final migration consumption must be on canonical origin/main first-parent history"]
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


def _blocked_reauthorization_errors(
    status: dict[str, Any],
    parent_sha: str | None,
    root: Path | None,
    child_sha: str | None,
) -> list[str]:
    """Validate a new-generation authorization without reopening a blocked node."""
    if root is None or child_sha is None or parent_sha is None:
        return ["$.active_tasks[0].candidate_generation: repeated authorization requires repository-bound blocked evidence"]
    ok, parents_text = _git(root, "rev-list", "--parents", "-n", "1", child_sha)
    parts = parents_text.split() if ok else []
    if len(parts) != 3 or parts[1] != parent_sha:
        return ["$: repeated authorization must be an exact two-parent record rooted at the authoritative close"]
    blocked_sha = parts[2]
    blocked = _status_at(root, blocked_sha)
    schema = _schema_at(root, child_sha)
    if type(blocked) is not dict or type(schema) is not dict:
        return ["$: repeated authorization blocked evidence is unreadable"]
    try:
        structural = _schema_errors(blocked, schema, schema)
    except (KeyError, TypeError, ValueError):
        structural = ["malformed blocked evidence"]
    if structural:
        return [f"$: repeated authorization blocked evidence fails schema validation: {item}" for item in structural]

    current_task = status["active_tasks"][0]
    blocked_task = blocked["active_tasks"][0]
    expected_generation = current_task["candidate_generation"] - 1
    identity_matches = (
        blocked.get("project") == status.get("project")
        and blocked.get("authoritative_main_ref") == status.get("authoritative_main_ref")
        and blocked.get("current_gate") == status.get("current_gate")
        and blocked_task.get("task_id") == current_task.get("task_id")
        and blocked_task.get("risk") == current_task.get("risk")
        and blocked_task.get("candidate_generation") == expected_generation
        and blocked_task.get("state") == "blocked"
        and blocked_task.get("transition", {}).get("to") == "blocked"
        and blocked.get("evidence", {}).get("authorization_baseline_sha") == parent_sha
        and type(blocked.get("blockers")) is list
        and bool(blocked["blockers"])
    )
    errors: list[str] = []
    if not identity_matches:
        errors.append("$: repeated authorization must bind the exact prior-generation terminal blocked record")
    if not _is_ancestor(root, parent_sha, blocked_sha):
        errors.append("$: repeated authorization blocked record must descend from the authoritative close")
    if _history_errors(root, blocked_sha, parent_sha, schema):
        errors.append("$: repeated authorization blocked history must independently validate")
    return errors


def _is_g0_t04_g4_status(status: dict[str, Any]) -> bool:
    try:
        task = status["active_tasks"][0]
        return (
            status["current_gate"] == "G0"
            and task["task_id"] == "G0-T04"
            and task["risk"] == "D0"
            and task["candidate_generation"] == 4
            and status["evidence"]["authorization_baseline_sha"]
            == G0_T04_G4_BASELINE
            and status["next_authorization"]
            == {"gate": "G0", "task_id": "G0-T05", "state": "not_authorized"}
        )
    except (KeyError, IndexError, TypeError):
        return False


def _git_blob_oid(root: Path, subject: str, path: str) -> str | None:
    ok, entry = _git(root, "ls-tree", subject, "--", path)
    fields = entry.split(None, 3) if ok else []
    if (
        len(fields) != 4
        or fields[0] != "100644"
        or fields[1] != "blob"
        or fields[3] != path
    ):
        return None
    return fields[2]


def _g0_t04_g4_authorization_parent_errors(
    status: dict[str, Any],
    parent_sha: str | None,
    root: Path | None,
    child_sha: str | None,
    *,
    require_current_main: bool,
) -> list[str] | None:
    task = status.get("active_tasks", [{}])[0]
    if not (
        _is_g0_t04_g4_status(status)
        and task.get("state") == "authorized"
        and task.get("transition") == {"from": "closed", "to": "authorized"}
    ):
        return None
    if root is None or child_sha is None:
        return ["$: G0-T04 generation-4 authorization requires repository lineage"]
    errors: list[str] = []
    ok, parents_text = _git(root, "rev-list", "--parents", "-n", "1", child_sha)
    if (parents_text.split() if ok else []) != [
        child_sha,
        G0_T04_G4_BASELINE,
        G0_T04_G4_BLOCKED_MAIN,
    ]:
        errors.append("$: G0-T04 generation-4 authorization parents drifted")
    if child_sha != G0_T04_G4_AUTHORIZATION or parent_sha != G0_T04_G4_BASELINE:
        errors.append("$: G0-T04 generation-4 authorization identity drifted")
    blocked = _status_at(root, G0_T04_G4_BLOCKED_MAIN)
    try:
        blocked_task = blocked["active_tasks"][0] if type(blocked) is dict else {}
        blocked_identity = (
            blocked_task
            == {
                "task_id": "G0-T04",
                "risk": "D0",
                "state": "blocked",
                "transition": {"from": "blocked", "to": "blocked"},
                "candidate_generation": 3,
            }
            and blocked["evidence"]["authorization_baseline_sha"]
            == G0_T04_G4_BASELINE
            and bool(blocked["blockers"])
        )
    except (KeyError, IndexError, TypeError):
        blocked_identity = False
    if not blocked_identity:
        errors.append("$: G0-T04 generation-4 terminal blocked record drifted")
    if not _cleared_handoff(status):
        errors.append("$: G0-T04 generation-4 authorization must clear all evidence")
    changed = _g0_t03_commit_changed_paths(
        root, G0_T04_G4_BLOCKED_MAIN, child_sha
    )
    if changed != {
        "PROJECT_STATUS.yaml",
        "CURRENT_TASK.md",
        "PROJECT_MEMORY.md",
        "docs/NEXT_WORKFLOW.md",
    }:
        errors.append("$: G0-T04 generation-4 authorization scope drifted")
    for path in (
        G0_T04_ANOMALY_RECEIPT_PATH,
        G0_T04_ANOMALY_SEAL_PATH,
        PACKAGE_A_MANIFEST_PATH,
        PACKAGE_A_SCHEMA_PATH,
    ):
        if _git_blob_oid(root, child_sha, path) != _git_blob_oid(
            root, G0_T04_G4_BLOCKED_MAIN, path
        ):
            errors.append(
                f"$: G0-T04 generation-4 immutable blocked-main blob drifted: {path}"
            )
    if _git_blob_oid(root, child_sha, PACKAGE_A_ACTIVATION_PATH) is not None:
        errors.append("$: G0-T04 generation-4 authorization resurrected activation")
    if require_current_main:
        ok_main, main = _git(
            root, "rev-parse", "--verify", status["authoritative_main_ref"]
        )
        ok_remote, remote = _git(
            root, "rev-parse", "--verify", "refs/remotes/origin/main"
        )
        if (
            not ok_main
            or not ok_remote
            or main != G0_T04_G4_BLOCKED_MAIN
            or remote != G0_T04_G4_BLOCKED_MAIN
        ):
            errors.append(
                "$: G0-T04 generation-4 authorization requires exact terminal blocked main"
            )
    return errors


def _g0_t04_g4_premature_recovery_receipt() -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema_version": G0_T04_G4_PREMATURE_RECEIPT_VERSION,
        "project": "yaobizuoduo",
        "task_id": "G0-T04",
        "candidate_generation": 4,
        "purpose": "premature_in_progress_main_merge_recovery",
        "premature_main": {
            "commit_sha": G0_T04_G4_PREMATURE_MAIN,
            "ordered_parents": [
                G0_T04_G4_PREMATURE_MAIN_FIRST_PARENT,
                G0_T04_G4_PREMATURE_MAIN_SECOND_PARENT,
            ],
            "tree_sha": G0_T04_G4_PREMATURE_MAIN_TREE,
            "pull_request": G0_T04_G4_PREMATURE_PR,
            "pull_request_head": G0_T04_G4_PREMATURE_MAIN_SECOND_PARENT,
            "reviews": {
                "state": "empty",
                "count": 0,
            },
            "project_status": {
                "blob_sha": G0_T04_G4_PREMATURE_MAIN_STATUS_BLOB,
                "canonical_sha256": G0_T04_G4_PREMATURE_MAIN_STATUS_DIGEST,
            },
            "pull_request_ci": {
                "repository": "weizhenhaihaha-arch/yaobizuoduo",
                "event": "pull_request",
                "check": "G0 / exact-head",
                "subject_sha": G0_T04_G4_PREMATURE_MAIN_SECOND_PARENT,
                "run_id": G0_T04_G4_PREMATURE_PR_RUN,
                "url": (
                    "https://github.com/weizhenhaihaha-arch/yaobizuoduo/"
                    f"actions/runs/{G0_T04_G4_PREMATURE_PR_RUN}"
                ),
                "status": "completed",
                "conclusion": "success",
                "authority": "anomaly_history_only",
            },
            "main_ci": {
                "repository": "weizhenhaihaha-arch/yaobizuoduo",
                "event": "push",
                "ref": "refs/heads/main",
                "check": "G0 / exact-head",
                "subject_sha": G0_T04_G4_PREMATURE_MAIN,
                "run_id": G0_T04_G4_PREMATURE_MAIN_RUN,
                "url": (
                    "https://github.com/weizhenhaihaha-arch/yaobizuoduo/"
                    f"actions/runs/{G0_T04_G4_PREMATURE_MAIN_RUN}"
                ),
                "status": "completed",
                "conclusion": "failure",
            },
        },
        "recovery_route": {
            "base_sha": G0_T04_G4_PREMATURE_MAIN,
            "lineage_rule": "strict_single_parent_only",
            "ordinary_in_progress_merge_authority": False,
            "future_bridge": {
                "first_parent": G0_T04_G4_PREMATURE_MAIN,
                "second_parent_role": "accepted_generation_4_recovery",
                "tree_rule": "merge_tree_equals_second_parent_tree",
            },
            "allowed_paths": sorted(G0_T04_G4_PREMATURE_ALLOWED),
        },
        "scope": {
            "g0_t05_authorized": False,
            "g1_authorized": False,
            "g2_authorized": False,
            "product_or_network_change_authorized": False,
        },
    }
    receipt["payload_sha256"] = _payload_digest(receipt)
    return receipt


def _g0_t04_g4_success_ci_record(
    *,
    event: str,
    ref: str,
    subject_sha: str,
    run_id: str,
) -> dict[str, Any]:
    return {
        "repository": "weizhenhaihaha-arch/yaobizuoduo",
        "event": event,
        "ref": ref,
        "check": "G0 / exact-head",
        "subject_sha": subject_sha,
        "run_id": run_id,
        "url": (
            "https://github.com/weizhenhaihaha-arch/yaobizuoduo/"
            f"actions/runs/{run_id}"
        ),
        "status": "completed",
        "conclusion": "success",
    }


def _g0_t04_g4_merged_verification_receipt() -> dict[str, Any]:
    receipt = copy.deepcopy(_g0_t04_g4_premature_recovery_receipt())
    receipt["schema_version"] = G0_T04_G4_MERGED_VERIFICATION_RECEIPT_VERSION
    receipt["merged_verification"] = {
        "candidate": {
            "commit_sha": G0_T04_G4_RECOVERY_CANDIDATE,
            "ci": _g0_t04_g4_success_ci_record(
                event="pull_request",
                ref=G0_T04_G4_RECOVERY_BRANCH_REF,
                subject_sha=G0_T04_G4_RECOVERY_CANDIDATE,
                run_id=G0_T04_G4_RECOVERY_CANDIDATE_RUN,
            ),
            "review": {
                "code_security": "approve",
                "architecture": "clear",
                "reviewed_candidate_sha": G0_T04_G4_RECOVERY_CANDIDATE,
            },
        },
        "acceptance": {
            "commit_sha": G0_T04_G4_RECOVERY_ACCEPTANCE,
            "ordered_parents": [G0_T04_G4_RECOVERY_CANDIDATE],
            "tree_sha": G0_T04_G4_RECOVERY_ACCEPTED_TREE,
            "ci": _g0_t04_g4_success_ci_record(
                event="pull_request",
                ref=G0_T04_G4_RECOVERY_BRANCH_REF,
                subject_sha=G0_T04_G4_RECOVERY_ACCEPTANCE,
                run_id=G0_T04_G4_RECOVERY_ACCEPTANCE_RUN,
            ),
        },
        "merged_main": {
            "commit_sha": G0_T04_G4_RECOVERY_MERGED_MAIN,
            "ordered_parents": [
                G0_T04_G4_PREMATURE_MAIN,
                G0_T04_G4_RECOVERY_ACCEPTANCE,
            ],
            "tree_sha": G0_T04_G4_RECOVERY_ACCEPTED_TREE,
            "ci": _g0_t04_g4_success_ci_record(
                event="push",
                ref="refs/heads/main",
                subject_sha=G0_T04_G4_RECOVERY_MERGED_MAIN,
                run_id=G0_T04_G4_RECOVERY_MERGED_MAIN_RUN,
            ),
        },
        "blocker_transition": {
            "before": [G0_T04_G4_PREMATURE_BLOCKER],
            "after": [],
            "clearing_authority": (
                "exact_acceptance_and_ordered_main_bridge_and_three_success_cis"
            ),
        },
        "finalization": {
            "commit_sha": None,
            "ci_status": "not_run",
            "authority": "not_created",
        },
    }
    receipt.pop("payload_sha256")
    receipt["payload_sha256"] = _payload_digest(receipt)
    return receipt


def _g0_t04_g4_finalization_close_receipt() -> dict[str, Any]:
    receipt = copy.deepcopy(_g0_t04_g4_merged_verification_receipt())
    receipt["schema_version"] = G0_T04_G4_FINALIZATION_CLOSE_RECEIPT_VERSION
    receipt["finalization_close"] = {
        "finalization_subject": {
            "commit_sha": G0_T04_G4_MERGED_VERIFICATION,
            "ci": _g0_t04_g4_success_ci_record(
                event="pull_request",
                ref=G0_T04_G4_MERGED_VERIFICATION_BRANCH_REF,
                subject_sha=G0_T04_G4_MERGED_VERIFICATION,
                run_id=G0_T04_G4_MERGED_VERIFICATION_RUN,
            ),
        },
        "close_record": {
            "parent_sha": G0_T04_G4_MERGED_VERIFICATION,
            "state": "closed",
            "transition": {
                "from": "merged_verified",
                "to": "closed",
            },
            "changed_paths": sorted(G0_T04_G4_PREMATURE_ALLOWED),
        },
        "future_terminal_bridge": {
            "ordered_parents": [
                G0_T04_G4_RECOVERY_MERGED_MAIN,
                "exact_finalization_close_record",
            ],
            "tree_rule": "merge_tree_equals_exact_close_record_tree",
            "generic_closed_merge_authority": False,
        },
        "scope": {
            "package_activation_authorized": False,
            "g0_t05_authorized": False,
            "g1_authorized": False,
            "g2_authorized": False,
            "product_or_network_change_authorized": False,
        },
    }
    receipt.pop("payload_sha256")
    receipt["payload_sha256"] = _payload_digest(receipt)
    return receipt


def _g0_t04_g4_premature_recovery_receipt_errors(
    root: Path, subject_sha: str
) -> list[str]:
    ok_entry, entry = _git(
        root,
        "ls-tree",
        subject_sha,
        "--",
        G0_T04_G4_PREMATURE_RECEIPT_PATH,
    )
    fields = entry.split(None, 3) if ok_entry else []
    if (
        len(fields) != 4
        or fields[0] != "100644"
        or fields[1] != "blob"
        or fields[3] != G0_T04_G4_PREMATURE_RECEIPT_PATH
    ):
        return [
            "$: G0-T04 generation-4 premature-merge recovery receipt "
            "must be an exact committed 100644 blob"
        ]
    ok_bytes, actual = _git_bytes(
        root,
        "show",
        f"{subject_sha}:{G0_T04_G4_PREMATURE_RECEIPT_PATH}",
    )
    expected = (
        json.dumps(
            _g0_t04_g4_premature_recovery_receipt(),
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")
    if not ok_bytes or actual != expected:
        return [
            "$: G0-T04 generation-4 premature-merge recovery receipt "
            "bytes or digest drifted"
        ]
    return []


def _g0_t04_g4_merged_verification_receipt_errors(
    root: Path, subject_sha: str
) -> list[str]:
    ok_entry, entry = _git(
        root,
        "ls-tree",
        subject_sha,
        "--",
        G0_T04_G4_PREMATURE_RECEIPT_PATH,
    )
    fields = entry.split(None, 3) if ok_entry else []
    if (
        len(fields) != 4
        or fields[0] != "100644"
        or fields[1] != "blob"
        or fields[3] != G0_T04_G4_PREMATURE_RECEIPT_PATH
    ):
        return [
            "$: G0-T04 generation-4 merged-verification receipt "
            "must be an exact committed 100644 blob"
        ]
    ok_bytes, actual = _git_bytes(
        root,
        "show",
        f"{subject_sha}:{G0_T04_G4_PREMATURE_RECEIPT_PATH}",
    )
    expected = (
        json.dumps(
            _g0_t04_g4_merged_verification_receipt(),
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")
    if not ok_bytes or actual != expected:
        return [
            "$: G0-T04 generation-4 merged-verification receipt "
            "bytes, CI evidence, or digest drifted"
        ]
    return []


def _g0_t04_g4_merged_verification_topology_errors(root: Path) -> list[str]:
    errors: list[str] = []
    ok_a, a_parents = _git(
        root,
        "rev-list",
        "--parents",
        "-n",
        "1",
        G0_T04_G4_RECOVERY_ACCEPTANCE,
    )
    if (a_parents.split() if ok_a else []) != [
        G0_T04_G4_RECOVERY_ACCEPTANCE,
        G0_T04_G4_RECOVERY_CANDIDATE,
    ]:
        errors.append(
            "$: G0-T04 generation-4 acceptance must be the exact "
            "single-parent child of the reviewed candidate"
        )
    ok_m, m_parents = _git(
        root,
        "rev-list",
        "--parents",
        "-n",
        "1",
        G0_T04_G4_RECOVERY_MERGED_MAIN,
    )
    if (m_parents.split() if ok_m else []) != [
        G0_T04_G4_RECOVERY_MERGED_MAIN,
        G0_T04_G4_PREMATURE_MAIN,
        G0_T04_G4_RECOVERY_ACCEPTANCE,
    ]:
        errors.append(
            "$: G0-T04 generation-4 merged-main ordered parents drifted"
        )
    ok_m_tree, m_tree = _git(
        root,
        "rev-parse",
        f"{G0_T04_G4_RECOVERY_MERGED_MAIN}^{{tree}}",
    )
    ok_a_tree, a_tree = _git(
        root,
        "rev-parse",
        f"{G0_T04_G4_RECOVERY_ACCEPTANCE}^{{tree}}",
    )
    if (
        not ok_m_tree
        or not ok_a_tree
        or m_tree != a_tree
        or m_tree != G0_T04_G4_RECOVERY_ACCEPTED_TREE
    ):
        errors.append(
            "$: G0-T04 generation-4 merged-main tree must equal "
            "the exact acceptance tree"
        )
    return errors


def _g0_t04_g4_merged_verification_status_errors(
    status: dict[str, Any],
    candidate_status: dict[str, Any],
    acceptance_status: dict[str, Any],
    merged_status: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    try:
        candidate_task = candidate_status["active_tasks"][0]
        acceptance_task = acceptance_status["active_tasks"][0]
    except (KeyError, IndexError, TypeError):
        return [
            "$: G0-T04 generation-4 merged-verification phase status is malformed"
        ]
    expected_candidate = {
        "commit_sha": G0_T04_G4_RECOVERY_CANDIDATE,
        "local_verification": {
            "status": "success",
            "subject": "delivery_head",
        },
        "ci": {
            "status": "success",
            "subject_sha": G0_T04_G4_RECOVERY_CANDIDATE,
            "run_id": G0_T04_G4_RECOVERY_CANDIDATE_RUN,
            "url": (
                "https://github.com/weizhenhaihaha-arch/yaobizuoduo/"
                f"actions/runs/{G0_T04_G4_RECOVERY_CANDIDATE_RUN}"
            ),
        },
    }
    if (
        candidate_task.get("state") != "awaiting_review"
        or candidate_task.get("transition")
        != {"from": "in_progress", "to": "awaiting_review"}
        or candidate_status.get("blockers")
        != [G0_T04_G4_PREMATURE_BLOCKER]
    ):
        errors.append(
            "$: G0-T04 generation-4 delivered candidate phase identity drifted"
        )
    if (
        acceptance_task.get("state") != "accepted_pending_merge"
        or acceptance_task.get("transition")
        != {"from": "awaiting_review", "to": "accepted_pending_merge"}
        or acceptance_status.get("evidence", {}).get("candidate")
        != expected_candidate
        or acceptance_status.get("review")
        != {
            "code_security": "approve",
            "architecture": "clear",
            "reviewed_candidate_sha": G0_T04_G4_RECOVERY_CANDIDATE,
        }
        or acceptance_status.get("blockers")
        != [G0_T04_G4_PREMATURE_BLOCKER]
    ):
        errors.append(
            "$: G0-T04 generation-4 acceptance evidence or blocker drifted"
        )
    if merged_status != acceptance_status:
        errors.append(
            "$: G0-T04 generation-4 merge tree status must equal acceptance status"
        )
    expected = copy.deepcopy(acceptance_status)
    expected["active_tasks"][0].update(
        state="merged_verified",
        transition={
            "from": "accepted_pending_merge",
            "to": "merged_verified",
        },
    )
    expected["evidence"]["closure"] = {
        "commit_sha": G0_T04_G4_RECOVERY_ACCEPTANCE,
        "ci": {
            "status": "success",
            "subject_sha": G0_T04_G4_RECOVERY_ACCEPTANCE,
            "run_id": G0_T04_G4_RECOVERY_ACCEPTANCE_RUN,
            "url": (
                "https://github.com/weizhenhaihaha-arch/yaobizuoduo/"
                f"actions/runs/{G0_T04_G4_RECOVERY_ACCEPTANCE_RUN}"
            ),
        },
    }
    expected["evidence"]["merged_main"] = {
        "commit_sha": G0_T04_G4_RECOVERY_MERGED_MAIN,
        "ci": {
            "status": "success",
            "subject_sha": G0_T04_G4_RECOVERY_MERGED_MAIN,
            "run_id": G0_T04_G4_RECOVERY_MERGED_MAIN_RUN,
            "url": (
                "https://github.com/weizhenhaihaha-arch/yaobizuoduo/"
                f"actions/runs/{G0_T04_G4_RECOVERY_MERGED_MAIN_RUN}"
            ),
        },
    }
    expected["blockers"] = []
    if status != expected:
        errors.append(
            "$: G0-T04 generation-4 merged-verification status must be "
            "the exact evidence-bound projection of acceptance"
        )
    return errors


def _g0_t04_g4_merged_verification_errors(
    status: dict[str, Any],
    root: Path,
    head: str,
    *,
    require_current_main: bool = True,
) -> list[str]:
    errors: list[str] = []
    ok_head, head_parents = _git(
        root,
        "rev-list",
        "--parents",
        "-n",
        "1",
        head,
    )
    if (head_parents.split() if ok_head else []) != [
        head,
        G0_T04_G4_RECOVERY_MERGED_MAIN,
    ]:
        errors.append(
            "$: G0-T04 generation-4 merged-verification record must be "
            "the strict single-parent child of exact merged main"
        )
    changed = _g0_t03_commit_changed_paths(
        root,
        G0_T04_G4_RECOVERY_MERGED_MAIN,
        head,
    )
    if changed != G0_T04_G4_PREMATURE_ALLOWED:
        errors.append(
            "$: G0-T04 generation-4 merged-verification required "
            "seven-path scope drifted"
        )
    errors.extend(_g0_t04_g4_merged_verification_topology_errors(root))
    candidate_status = _status_at(root, G0_T04_G4_RECOVERY_CANDIDATE)
    acceptance_status = _status_at(root, G0_T04_G4_RECOVERY_ACCEPTANCE)
    merged_status = _status_at(root, G0_T04_G4_RECOVERY_MERGED_MAIN)
    if not all(
        type(item) is dict
        for item in (candidate_status, acceptance_status, merged_status)
    ):
        errors.append(
            "$: G0-T04 generation-4 merged-verification phase status is unavailable"
        )
    else:
        errors.extend(
            _g0_t04_g4_merged_verification_status_errors(
                status,
                candidate_status,
                acceptance_status,
                merged_status,
            )
        )
    errors.extend(
        _g0_t04_g4_merged_verification_receipt_errors(root, head)
    )
    ok_main, main = _git(root, "rev-parse", "--verify", "refs/heads/main")
    ok_remote, remote = _git(
        root,
        "rev-parse",
        "--verify",
        "refs/remotes/origin/main",
    )
    if require_current_main and (
        not ok_main
        or not ok_remote
        or main != G0_T04_G4_RECOVERY_MERGED_MAIN
        or remote != G0_T04_G4_RECOVERY_MERGED_MAIN
    ):
        errors.append(
            "$: G0-T04 generation-4 merged verification requires "
            "exact local and fetched merged main"
        )
    return errors


def _g0_t04_g4_finalization_close_receipt_errors(
    root: Path,
    subject_sha: str,
) -> list[str]:
    ok_entry, entry = _git(
        root,
        "ls-tree",
        subject_sha,
        "--",
        G0_T04_G4_PREMATURE_RECEIPT_PATH,
    )
    fields = entry.split(None, 3) if ok_entry else []
    if (
        len(fields) != 4
        or fields[0] != "100644"
        or fields[1] != "blob"
        or fields[3] != G0_T04_G4_PREMATURE_RECEIPT_PATH
    ):
        return [
            "$: G0-T04 generation-4 finalization-close receipt "
            "must be an exact committed 100644 blob"
        ]
    ok_bytes, actual = _git_bytes(
        root,
        "show",
        f"{subject_sha}:{G0_T04_G4_PREMATURE_RECEIPT_PATH}",
    )
    expected = (
        json.dumps(
            _g0_t04_g4_finalization_close_receipt(),
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")
    if not ok_bytes or actual != expected:
        return [
            "$: G0-T04 generation-4 finalization-close receipt "
            "bytes, CI evidence, or digest drifted"
        ]
    return []


def _g0_t04_g4_finalization_close_status_errors(
    status: dict[str, Any],
    verification_status: dict[str, Any],
) -> list[str]:
    expected = copy.deepcopy(verification_status)
    expected["active_tasks"][0].update(
        state="closed",
        transition={"from": "merged_verified", "to": "closed"},
    )
    expected["evidence"]["finalization"] = {
        "commit_sha": G0_T04_G4_MERGED_VERIFICATION,
        "d0_ci": {
            "status": "success",
            "subject_sha": G0_T04_G4_MERGED_VERIFICATION,
            "run_id": G0_T04_G4_MERGED_VERIFICATION_RUN,
            "url": (
                "https://github.com/weizhenhaihaha-arch/yaobizuoduo/"
                f"actions/runs/{G0_T04_G4_MERGED_VERIFICATION_RUN}"
            ),
        },
    }
    if status != expected:
        return [
            "$: G0-T04 generation-4 finalization-close status must be "
            "the exact evidence-bound projection of merged verification"
        ]
    return []


def _g0_t04_g4_finalization_close_errors(
    status: dict[str, Any],
    root: Path,
    head: str,
    *,
    require_current_main: bool = True,
) -> list[str]:
    errors: list[str] = []
    ok_head, head_parents = _git(
        root,
        "rev-list",
        "--parents",
        "-n",
        "1",
        head,
    )
    if (head_parents.split() if ok_head else []) != [
        head,
        G0_T04_G4_MERGED_VERIFICATION,
    ]:
        errors.append(
            "$: G0-T04 generation-4 finalization-close record must be "
            "the strict single-parent child of exact merged verification"
        )
    changed = _g0_t03_commit_changed_paths(
        root,
        G0_T04_G4_MERGED_VERIFICATION,
        head,
    )
    if changed != G0_T04_G4_PREMATURE_ALLOWED:
        errors.append(
            "$: G0-T04 generation-4 finalization-close required "
            "seven-path scope drifted"
        )
    verification_status = _status_at(
        root,
        G0_T04_G4_MERGED_VERIFICATION,
    )
    if type(verification_status) is not dict:
        errors.append(
            "$: G0-T04 generation-4 merged-verification status is unavailable"
        )
    else:
        errors.extend(
            _g0_t04_g4_merged_verification_errors(
                verification_status,
                root,
                G0_T04_G4_MERGED_VERIFICATION,
                require_current_main=require_current_main,
            )
        )
        errors.extend(
            _g0_t04_g4_finalization_close_status_errors(
                status,
                verification_status,
            )
        )
    errors.extend(_g0_t04_g4_finalization_close_receipt_errors(root, head))
    return errors


def _g0_t04_g4_final_close_bridge_errors(
    root: Path,
    merge_sha: str,
    close_sha: str,
) -> list[str]:
    errors: list[str] = []
    ok_merge, parents = _git(
        root,
        "rev-list",
        "--parents",
        "-n",
        "1",
        merge_sha,
    )
    if (parents.split() if ok_merge else []) != [
        merge_sha,
        G0_T04_G4_RECOVERY_MERGED_MAIN,
        close_sha,
    ]:
        errors.append(
            "$: G0-T04 generation-4 terminal bridge ordered parents drifted"
        )
    ok_merge_tree, merge_tree = _git(
        root,
        "rev-parse",
        f"{merge_sha}^{{tree}}",
    )
    ok_close_tree, close_tree = _git(
        root,
        "rev-parse",
        f"{close_sha}^{{tree}}",
    )
    if (
        not ok_merge_tree
        or not ok_close_tree
        or merge_tree != close_tree
    ):
        errors.append(
            "$: G0-T04 generation-4 terminal bridge tree must equal "
            "the exact close-record tree"
        )
    return errors


def _g0_t04_g4_terminal_bridge_route_errors(
    status: dict[str, Any],
    root: Path,
    head: str,
    close_sha: str,
    *,
    require_canonical_main: bool,
) -> list[str]:
    errors: list[str] = []
    close_status = _status_at(root, close_sha)
    if type(close_status) is not dict or close_status != status:
        errors.append(
            "$: G0-T04 generation-4 terminal bridge status must exactly "
            "equal its close-record second parent"
        )
    else:
        errors.extend(
            _g0_t04_g4_finalization_close_errors(
                close_status,
                root,
                close_sha,
                require_current_main=False,
            )
        )
    errors.extend(
        _g0_t04_g4_final_close_bridge_errors(root, head, close_sha)
    )
    if require_canonical_main:
        ok_main, main = _git(
            root,
            "rev-parse",
            "--verify",
            "refs/heads/main",
        )
        ok_remote, remote = _git(
            root,
            "rev-parse",
            "--verify",
            "refs/remotes/origin/main",
        )
        if (
            not ok_main
            or not ok_remote
            or main != head
            or remote != head
        ):
            errors.append(
                "$: G0-T04 generation-4 terminal bridge requires exact "
                "local and fetched terminal main"
            )
    return errors


def _g0_t04_g4_premature_recovery_status_errors(
    status: dict[str, Any],
) -> list[str]:
    try:
        task = status["active_tasks"][0]
        state = task["state"]
        blockers = status["blockers"]
    except (KeyError, IndexError, TypeError):
        return [
            "$: G0-T04 generation-4 premature-main recovery status is malformed"
        ]
    if state == "in_progress":
        if blockers != []:
            return [
                "$.blockers: G0-T04 generation-4 premature-main in_progress "
                "recovery must retain exact empty blockers"
            ]
        return []
    if state in {"awaiting_review", "accepted_pending_merge"}:
        if blockers != [G0_T04_G4_PREMATURE_BLOCKER]:
            return [
                "$.blockers: G0-T04 generation-4 premature-main recovery "
                "must retain the exact premature-main CI blocker through acceptance"
            ]
        return []
    if state in {"merged_verified", "closed"}:
        return [
            "$.blockers: G0-T04 generation-4 premature-main recovery blocker "
            "cannot clear before a dedicated evidence-bound clearing transition"
        ]
    return []


def _g0_t04_g4_premature_recovery_lineage_errors(
    root: Path,
    governed_head: str,
    *,
    require_current_main: bool,
) -> list[str]:
    errors: list[str] = []
    ok_f, f_parents_text = _git(
        root,
        "rev-list",
        "--parents",
        "-n",
        "1",
        G0_T04_G4_PREMATURE_MAIN,
    )
    ok_f_tree, f_tree = _git(
        root,
        "rev-parse",
        f"{G0_T04_G4_PREMATURE_MAIN}^{{tree}}",
    )
    if (
        (f_parents_text.split() if ok_f else [])
        != [
            G0_T04_G4_PREMATURE_MAIN,
            G0_T04_G4_PREMATURE_MAIN_FIRST_PARENT,
            G0_T04_G4_PREMATURE_MAIN_SECOND_PARENT,
        ]
        or not ok_f_tree
        or f_tree != G0_T04_G4_PREMATURE_MAIN_TREE
    ):
        errors.append(
            "$: G0-T04 generation-4 premature main identity or topology drifted"
        )
    if governed_head == G0_T04_G4_PREMATURE_MAIN or not _is_ancestor(
        root,
        G0_T04_G4_PREMATURE_MAIN,
        governed_head,
    ):
        return errors + [
            "$: G0-T04 generation-4 recovery must descend from exact premature main"
        ]
    ok_lineage, lineage_text = _git(
        root,
        "rev-list",
        "--first-parent",
        f"{G0_T04_G4_PREMATURE_MAIN}..{governed_head}",
    )
    lineage = lineage_text.splitlines() if ok_lineage else []
    expected_parent = G0_T04_G4_PREMATURE_MAIN
    for sha in reversed(lineage):
        ok_parents, parents_text = _git(
            root,
            "rev-list",
            "--parents",
            "-n",
            "1",
            sha,
        )
        if (parents_text.split() if ok_parents else []) != [sha, expected_parent]:
            errors.append(
                "$: G0-T04 generation-4 premature-main recovery lineage "
                "must remain strict single-parent"
            )
            break
        expected_parent = sha
    changed = _g0_t03_commit_changed_paths(
        root,
        G0_T04_G4_PREMATURE_MAIN,
        governed_head,
    )
    if (
        changed is None
        or not changed.issubset(G0_T04_G4_PREMATURE_ALLOWED)
        or not G0_T04_G4_PREMATURE_REQUIRED.issubset(changed)
    ):
        errors.append(
            "$: G0-T04 generation-4 premature-main recovery required scope drifted"
        )
    errors.extend(
        _g0_t04_g4_premature_recovery_receipt_errors(root, governed_head)
    )
    if _git_blob_oid(
        root,
        governed_head,
        G0_T04_G4_ROUTE_SEAL_PATH,
    ) != _git_blob_oid(
        root,
        G0_T04_G4_PREMATURE_MAIN,
        G0_T04_G4_ROUTE_SEAL_PATH,
    ):
        errors.append(
            "$: G0-T04 generation-4 premature-main recovery changed "
            "the immutable main-drift seal"
        )
    if _git_blob_oid(
        root,
        G0_T04_G4_PREMATURE_MAIN,
        "PROJECT_STATUS.yaml",
    ) != G0_T04_G4_PREMATURE_MAIN_STATUS_BLOB:
        errors.append(
            "$: G0-T04 generation-4 premature main status blob drifted"
        )
    premature_status = _status_at(root, G0_T04_G4_PREMATURE_MAIN)
    if (
        type(premature_status) is not dict
        or _canonical_status_digest(premature_status)
        != G0_T04_G4_PREMATURE_MAIN_STATUS_DIGEST
    ):
        errors.append(
            "$: G0-T04 generation-4 premature main canonical status digest drifted"
        )
    if require_current_main:
        ok_main, main = _git(root, "rev-parse", "--verify", "refs/heads/main")
        ok_remote, remote = _git(
            root,
            "rev-parse",
            "--verify",
            "refs/remotes/origin/main",
        )
        if (
            not ok_main
            or not ok_remote
            or main != G0_T04_G4_PREMATURE_MAIN
            or remote != G0_T04_G4_PREMATURE_MAIN
        ):
            errors.append(
                "$: G0-T04 generation-4 premature-main recovery requires "
                "exact local and fetched main"
            )
    return errors


def _g0_t04_g4_route_errors(
    status: dict[str, Any], root: Path, head: str
) -> list[str]:
    try:
        task = status["active_tasks"][0]
        is_generation_4_identity = (
            status["current_gate"] == "G0"
            and task["task_id"] == "G0-T04"
            and task["risk"] == "D0"
            and task["candidate_generation"] == 4
            and status["evidence"]["authorization_baseline_sha"]
            == G0_T04_G4_BASELINE
        )
    except (KeyError, IndexError, TypeError):
        is_generation_4_identity = False
        task = {}
    if (
        is_generation_4_identity
        and task.get("state") == "closed"
        and task.get("transition")
        == {"from": "merged_verified", "to": "closed"}
    ):
        ok_parents, parents_text = _git(
            root,
            "rev-list",
            "--parents",
            "-n",
            "1",
            head,
        )
        parts = parents_text.split() if ok_parents else []
        if len(parts) == 2:
            return _g0_t04_g4_finalization_close_errors(status, root, head)
        if len(parts) == 3:
            return _g0_t04_g4_terminal_bridge_route_errors(
                status,
                root,
                head,
                parts[2],
                require_canonical_main=True,
            )
        return [
            "$: G0-T04 generation-4 closed route must be the exact "
            "single-parent close record or exact two-parent terminal bridge"
        ]
    if (
        is_generation_4_identity
        and task.get("state") == "merged_verified"
        and task.get("transition")
        == {"from": "accepted_pending_merge", "to": "merged_verified"}
    ):
        return _g0_t04_g4_merged_verification_errors(status, root, head)
    if not _is_g0_t04_g4_status(status):
        return []
    errors: list[str] = []
    ok_entry, entry = _git(
        root, "ls-tree", head, "--", G0_T04_G4_ROUTE_SEAL_PATH
    )
    fields = entry.split(None, 3) if ok_entry else []
    if (
        len(fields) != 4
        or fields[0] != "100644"
        or fields[1] != "blob"
        or fields[3] != G0_T04_G4_ROUTE_SEAL_PATH
    ):
        return [
            "$: G0-T04 generation-4 main-drift seal must be a committed 100644 blob"
        ]
    ok_seal, seal_bytes = _git_bytes(
        root, "show", f"{head}:{G0_T04_G4_ROUTE_SEAL_PATH}"
    )
    if not ok_seal:
        return ["$: G0-T04 generation-4 main-drift seal Git blob is unreadable"]
    try:
        seal = json.loads(
            seal_bytes.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (UnicodeError, json.JSONDecodeError, ValueError):
        return errors + ["$: G0-T04 generation-4 main-drift seal is unreadable"]
    canonical_seal_bytes = (
        json.dumps(seal, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    if seal_bytes != canonical_seal_bytes:
        errors.append(
            "$: G0-T04 generation-4 main-drift seal Git blob bytes are noncanonical"
        )
    expected_keys = {
        "schema_version",
        "project",
        "task_id",
        "candidate_generation",
        "authorization",
        "pr24_main_drift",
        "abandoned_off_main_route",
        "discarded_competing_route",
        "canonical_lineage",
        "immutable_history",
        "owner_authority",
        "protected_main_bridge",
        "continuation",
        "allowed_paths",
        "payload_sha256",
    }
    if type(seal) is not dict or set(seal) != expected_keys:
        return errors + ["$: G0-T04 generation-4 main-drift seal fields drifted"]
    supplied_digest = seal.get("payload_sha256")
    digest_input = dict(seal)
    digest_input.pop("payload_sha256", None)
    computed_digest = hashlib.sha256(
        json.dumps(
            digest_input, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()
    if (
        seal.get("schema_version") != G0_T04_G4_ROUTE_SEAL_VERSION
        or seal.get("project") != "yaobizuoduo"
        or seal.get("task_id") != "G0-T04"
        or seal.get("candidate_generation") != 4
        or supplied_digest != G0_T04_G4_ROUTE_SEAL_PAYLOAD
        or computed_digest != G0_T04_G4_ROUTE_SEAL_PAYLOAD
    ):
        errors.append("$: G0-T04 generation-4 main-drift seal identity drifted")
    if seal.get("authorization") != {
        "sha": G0_T04_G4_AUTHORIZATION,
        "ordered_parents": [G0_T04_G4_BASELINE, G0_T04_G4_BLOCKED_MAIN],
        "start_sha": G0_T04_G4_START,
    }:
        errors.append("$: G0-T04 generation-4 authorization seal drifted")
    if seal.get("pr24_main_drift") != {
        "pr": 24,
        "head_sha": G0_T04_G4_PR24_HEAD,
        "exact_head_run_id": G0_T04_G4_PR24_RUN,
        "reviews": "empty",
        "merge_sha": G0_T04_G4_BLOCKED_MAIN,
        "ordered_merge_parents": [G0_T04_ANOMALY_MERGE, G0_T04_G4_PR24_HEAD],
        "merge_tree": "1f5234ed411b7ab00fea8f74e360deeb1f1340a3",
    }:
        errors.append("$: G0-T04 generation-4 PR #24 identity drifted")
    if seal.get("abandoned_off_main_route") != {
        "authorization_sha": G0_T04_G4_ABANDONED_AUTH,
        "authorization_ordered_parents": [
            G0_T04_G4_BASELINE,
            G0_T04_ANOMALY_MERGE,
        ],
        "start_sha": G0_T04_G4_ABANDONED_START,
        "candidate_sha": G0_T04_G4_ABANDONED_CANDIDATE,
        "candidate_state": "awaiting_review",
        "route_seal_blob": "ca7aa3b416024ed44f57ab8cfa8de94f39995f04",
        "pull_request": 25,
        "ci_status": "not_run",
        "reusable": False,
    }:
        errors.append("$: G0-T04 generation-4 abandoned route identity drifted")
    if seal.get("discarded_competing_route") != {
        "state": "tombstoned_non_authoritative",
        "authorization_sha": G0_T04_G4_COMPETING_AUTH,
        "authorization_ordered_parents": [
            G0_T04_G4_BASELINE,
            G0_T04_G4_BLOCKED_MAIN,
        ],
        "authorization_tree": "11098e342e3706e47ff74ddea7f6515475339a89",
        "authorization_message": "Authorize G0-T04 generation 4",
        "start_sha": G0_T04_G4_COMPETING_START,
        "start_parent": G0_T04_G4_COMPETING_AUTH,
        "start_tree": "0296e60d4cb54cbc509dfd13b0ba54809d848b25",
        "start_message": "Start G0-T04 generation 4 implementation",
        "source_clone_object_requirement": False,
        "verification_rule": (
            "both_absent_accept_sealed_identity_if_any_present_require_both_"
            "and_exact_metadata"
        ),
        "governed_parent_eligible": False,
        "import_allowed": False,
    }:
        errors.append("$: G0-T04 generation-4 competing route tombstone drifted")
    if seal.get("canonical_lineage") != {
        "authorization_sha": G0_T04_G4_AUTHORIZATION,
        "start_sha": G0_T04_G4_START,
        "post_authorization_rule": "strict_single_parent_only",
        "merge_imports_allowed": False,
        "excluded_ancestor_or_import_shas": list(
            G0_T04_G4_EXCLUDED_ROUTE_NODES
        ),
    }:
        errors.append("$: G0-T04 generation-4 canonical lineage exclusions drifted")
    if seal.get("immutable_history") != {
        "anomaly_receipt_blob": "c71560939c1b6fd0c6f038c3fe723df178fa2596",
        "anomaly_seal_blob": "382331a1b6293f6174d52102422a10a340cbf077",
        "package_manifest_blob": "f523c793a58d27e8ffd79da01048c8cd93aaa315",
        "package_schema_blob": "132656bcda439c20a2ade78d30116c49706de7b3",
        "package_payload_sha256": PACKAGE_A_PAYLOAD_SHA256,
        "activation_present": False,
    }:
        errors.append("$: G0-T04 generation-4 immutable history seal drifted")
    if seal.get("owner_authority") != {
        "package_payload_sha256": PACKAGE_A_PAYLOAD_SHA256,
        "fresh_activation_only_after_new_g0_t04_close": True,
        "old_activation_reuse_forbidden": True,
    }:
        errors.append("$: G0-T04 generation-4 owner authority drifted")
    if seal.get("protected_main_bridge") != {
        "first_parent": G0_T04_G4_BLOCKED_MAIN,
        "second_parent_role": "accepted_generation_4_closure",
        "tree_rule": "merge_tree_equals_second_parent_tree",
    }:
        errors.append("$: G0-T04 generation-4 protected-main bridge drifted")
    if seal.get("continuation") != {
        "g0_t05_generation_rule": "smallest_unused_integer_strictly_greater_than_all_historical_g0_t05_generations",
        "g1_t01_generation": 2,
        "g1_ordered_parents": [
            "new_g0_t05_closed_authoritative_main",
            G0_T04_G4_G1_BLOCKED,
        ],
        "g1_merge_base": G0_T04_G4_G1_MERGE_BASE,
        "g2_authorized": False,
    }:
        errors.append("$: G0-T04 generation-4 continuation boundary drifted")
    if seal.get("allowed_paths") != sorted(G0_T04_G4_ALLOWED):
        errors.append("$: G0-T04 generation-4 allowlist seal drifted")
    for path, expected_blob in (
        (G0_T04_ANOMALY_RECEIPT_PATH, "c71560939c1b6fd0c6f038c3fe723df178fa2596"),
        (G0_T04_ANOMALY_SEAL_PATH, "382331a1b6293f6174d52102422a10a340cbf077"),
        (PACKAGE_A_MANIFEST_PATH, "f523c793a58d27e8ffd79da01048c8cd93aaa315"),
        (PACKAGE_A_SCHEMA_PATH, "132656bcda439c20a2ade78d30116c49706de7b3"),
    ):
        if _git_blob_oid(root, head, path) != expected_blob:
            errors.append(f"$: G0-T04 generation-4 immutable blob drifted: {path}")
    if _git_blob_oid(root, head, PACKAGE_A_ACTIVATION_PATH) is not None:
        errors.append("$: G0-T04 generation-4 route resurrected activation")
    pr24_ok, pr24_line = _git(
        root, "rev-list", "--parents", "-n", "1", G0_T04_G4_BLOCKED_MAIN
    )
    pr24_tree_ok, pr24_tree = _git(
        root, "rev-parse", f"{G0_T04_G4_BLOCKED_MAIN}^{{tree}}"
    )
    if (
        (pr24_line.split() if pr24_ok else [])
        != [G0_T04_G4_BLOCKED_MAIN, G0_T04_ANOMALY_MERGE, G0_T04_G4_PR24_HEAD]
        or not pr24_tree_ok
        or pr24_tree != "1f5234ed411b7ab00fea8f74e360deeb1f1340a3"
    ):
        errors.append("$: G0-T04 generation-4 PR #24 merge topology drifted")
    abandoned_ok, abandoned_line = _git(
        root, "rev-list", "--parents", "-n", "1", G0_T04_G4_ABANDONED_AUTH
    )
    abandoned_start_ok, abandoned_start_line = _git(
        root, "rev-list", "--parents", "-n", "1", G0_T04_G4_ABANDONED_START
    )
    if (
        (abandoned_line.split() if abandoned_ok else [])
        != [
            G0_T04_G4_ABANDONED_AUTH,
            G0_T04_G4_BASELINE,
            G0_T04_ANOMALY_MERGE,
        ]
        or (abandoned_start_line.split() if abandoned_start_ok else [])
        != [G0_T04_G4_ABANDONED_START, G0_T04_G4_ABANDONED_AUTH]
        or not _is_ancestor(
            root, G0_T04_G4_ABANDONED_START, G0_T04_G4_ABANDONED_CANDIDATE
        )
        or _git_blob_oid(
            root,
            G0_T04_G4_ABANDONED_CANDIDATE,
            "evidence/g0-t04/generation-4-route-seal.json",
        )
        != "ca7aa3b416024ed44f57ab8cfa8de94f39995f04"
    ):
        errors.append("$: G0-T04 generation-4 abandoned route topology drifted")
    competing_auth_present = _git(
        root, "cat-file", "-e", f"{G0_T04_G4_COMPETING_AUTH}^{{commit}}"
    )[0]
    competing_start_present = _git(
        root, "cat-file", "-e", f"{G0_T04_G4_COMPETING_START}^{{commit}}"
    )[0]
    if competing_auth_present != competing_start_present:
        errors.append(
            "$: G0-T04 generation-4 competing route objects are only partially present"
        )
    elif competing_auth_present:
        competing_ok, competing_line = _git(
            root, "rev-list", "--parents", "-n", "1", G0_T04_G4_COMPETING_AUTH
        )
        competing_tree_ok, competing_tree = _git(
            root, "rev-parse", f"{G0_T04_G4_COMPETING_AUTH}^{{tree}}"
        )
        competing_message_ok, competing_message = _git(
            root, "show", "-s", "--format=%B", G0_T04_G4_COMPETING_AUTH
        )
        competing_start_ok, competing_start_line = _git(
            root, "rev-list", "--parents", "-n", "1", G0_T04_G4_COMPETING_START
        )
        competing_start_tree_ok, competing_start_tree = _git(
            root, "rev-parse", f"{G0_T04_G4_COMPETING_START}^{{tree}}"
        )
        competing_start_message_ok, competing_start_message = _git(
            root, "show", "-s", "--format=%B", G0_T04_G4_COMPETING_START
        )
        if (
            (competing_line.split() if competing_ok else [])
            != [
                G0_T04_G4_COMPETING_AUTH,
                G0_T04_G4_BASELINE,
                G0_T04_G4_BLOCKED_MAIN,
            ]
            or not competing_tree_ok
            or competing_tree != "11098e342e3706e47ff74ddea7f6515475339a89"
            or not competing_message_ok
            or competing_message != "Authorize G0-T04 generation 4"
            or (competing_start_line.split() if competing_start_ok else [])
            != [G0_T04_G4_COMPETING_START, G0_T04_G4_COMPETING_AUTH]
            or not competing_start_tree_ok
            or competing_start_tree != "0296e60d4cb54cbc509dfd13b0ba54809d848b25"
            or not competing_start_message_ok
            or competing_start_message
            != "Start G0-T04 generation 4 implementation"
        ):
            errors.append("$: G0-T04 generation-4 competing route topology drifted")
    ok_start, start_parents = _git(
        root, "rev-list", "--parents", "-n", "1", G0_T04_G4_START
    )
    if (start_parents.split() if ok_start else []) != [
        G0_T04_G4_START,
        G0_T04_G4_AUTHORIZATION,
    ]:
        errors.append("$: G0-T04 generation-4 start lineage drifted")
    lineage_subject = head
    ok_head_parents, head_parents_text = _git(
        root, "rev-list", "--parents", "-n", "1", head
    )
    head_parts = head_parents_text.split() if ok_head_parents else []
    recovery_subject: str | None = None
    recovery_is_bridge = (
        len(head_parts) == 3
        and head_parts[1] == G0_T04_G4_PREMATURE_MAIN
    )
    if recovery_is_bridge:
        recovery_subject = head_parts[2]
    elif (
        head != G0_T04_G4_PREMATURE_MAIN
        and _is_ancestor(root, G0_T04_G4_PREMATURE_MAIN, head)
    ):
        recovery_subject = head
    if recovery_subject is not None:
        errors.extend(
            _g0_t04_g4_premature_recovery_lineage_errors(
                root,
                recovery_subject,
                require_current_main=not recovery_is_bridge,
            )
        )
        if recovery_is_bridge:
            governed_status = _status_at(root, recovery_subject)
            if type(governed_status) is not dict:
                errors.append(
                    "$: G0-T04 generation-4 premature-main recovery "
                    "second-parent status is unavailable"
                )
            else:
                errors.extend(
                    _g0_t04_g4_premature_recovery_status_errors(
                        governed_status
                    )
                )
        else:
            errors.extend(
                _g0_t04_g4_premature_recovery_status_errors(status)
            )
        lineage_subject = G0_T04_G4_PREMATURE_MAIN_SECOND_PARENT
    else:
        changed = _g0_t03_commit_changed_paths(
            root,
            G0_T04_G4_AUTHORIZATION,
            head,
        )
        if changed is None or not changed.issubset(G0_T04_G4_ALLOWED):
            errors.append("$: G0-T04 generation-4 cumulative allowlist drifted")
    if len(head_parts) == 3 and head_parts[1] == G0_T04_G4_BLOCKED_MAIN:
        lineage_subject = head_parts[2]
    errors.extend(_g0_t04_g4_canonical_lineage_errors(root, lineage_subject))
    return errors


def _g0_t04_g4_canonical_lineage_errors(root: Path, governed_head: str) -> list[str]:
    """Reject every noncanonical branch import after the exact G4 authorization."""
    errors: list[str] = []
    if not _is_ancestor(root, G0_T04_G4_AUTHORIZATION, governed_head):
        errors.append(
            "$: G0-T04 generation-4 governed head must descend from exact canonical authorization"
        )
        return errors
    for forbidden_sha in G0_T04_G4_EXCLUDED_ROUTE_NODES:
        if _is_ancestor(root, forbidden_sha, governed_head):
            errors.append(
                "$: G0-T04 generation-4 governed lineage imported a tombstoned noncanonical route"
            )
            break
    ok_lineage, lineage_text = _git(
        root,
        "rev-list",
        "--first-parent",
        f"{G0_T04_G4_AUTHORIZATION}..{governed_head}",
    )
    lineage = lineage_text.splitlines() if ok_lineage else []
    if not lineage or lineage[-1] != G0_T04_G4_START:
        errors.append(
            "$: G0-T04 generation-4 governed lineage must begin at exact canonical start"
        )
        return errors
    expected_parent = G0_T04_G4_AUTHORIZATION
    for sha in reversed(lineage):
        ok_parents, parents_text = _git(
            root, "rev-list", "--parents", "-n", "1", sha
        )
        if (parents_text.split() if ok_parents else []) != [
            sha,
            expected_parent,
        ]:
            errors.append(
                "$: G0-T04 generation-4 implementation/delivery lineage must remain strict single-parent"
            )
            break
        expected_parent = sha
    return errors


def _g0_t04_g4_merge_topology_errors(root: Path, head: str) -> list[str]:
    errors: list[str] = []
    ok, parents_text = _git(root, "rev-list", "--parents", "-n", "1", head)
    parts = parents_text.split() if ok else []
    if len(parts) != 3:
        return ["$: G0-T04 generation-4 main bridge must have exactly two parents"]
    first_parent, governed_parent = parts[1], parts[2]
    if first_parent != G0_T04_G4_PREMATURE_MAIN:
        errors.append(
            "$: G0-T04 generation-4 recovery bridge first parent must be "
            "the exact premature main"
        )
    governed_status = _status_at(root, governed_parent)
    try:
        governed_task = governed_status["active_tasks"][0]
    except (KeyError, IndexError, TypeError):
        governed_task = {}
    if (
        governed_task.get("state") != "accepted_pending_merge"
        or governed_task.get("transition")
        != {"from": "awaiting_review", "to": "accepted_pending_merge"}
    ):
        errors.append(
            "$: G0-T04 generation-4 recovery bridge second parent must be "
            "the accepted recovery"
        )
    if type(governed_status) is dict:
        errors.extend(
            _g0_t04_g4_premature_recovery_status_errors(governed_status)
        )
    errors.extend(
        _g0_t04_g4_premature_recovery_lineage_errors(
            root,
            governed_parent,
            require_current_main=False,
        )
    )
    ok_head_tree, head_tree = _git(root, "rev-parse", f"{head}^{{tree}}")
    ok_parent_tree, parent_tree = _git(
        root, "rev-parse", f"{governed_parent}^{{tree}}"
    )
    if not ok_head_tree or not ok_parent_tree or head_tree != parent_tree:
        errors.append(
            "$: G0-T04 generation-4 recovery bridge tree must equal "
            "its second-parent tree"
        )
    return errors


def _parent_status_errors(
    status: dict[str, Any],
    parent: dict[str, Any] | None,
    parent_sha: str | None = None,
    root: Path | None = None,
    child_sha: str | None = None,
    *,
    require_current_main: bool = True,
) -> list[str]:
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
    recovery_errors = _g0_t04_g4_authorization_parent_errors(
        status,
        parent_sha,
        root,
        child_sha,
        require_current_main=require_current_main,
    )
    if recovery_errors is not None:
        return recovery_errors
    recovery_errors = _g0_t04_anomaly_post_merge_repair_parent_errors(
        status,
        parent,
        parent_sha,
        root,
        child_sha,
        require_current_main=require_current_main,
    )
    if recovery_errors is not None:
        return recovery_errors
    recovery_errors = _g0_t04_anomaly_seal_parent_errors(
        status,
        parent,
        parent_sha,
        root,
        child_sha,
        require_current_main=require_current_main,
    )
    if recovery_errors is not None:
        return recovery_errors
    recovery_errors = _g0_t04_anomaly_parent_errors(
        status,
        parent,
        parent_sha,
        root,
        child_sha,
        require_current_main=require_current_main,
    )
    if recovery_errors is not None:
        return recovery_errors
    recovery_errors = _g0_t04_anomaly_implementation_errors(
        status,
        parent,
        parent_sha,
        root,
        child_sha,
        require_current_main=require_current_main,
    )
    if recovery_errors is not None:
        return recovery_errors
    recovery_errors = _g0_t04_recovery_parent_errors(
        status,
        parent,
        parent_sha,
        root,
        child_sha,
        require_current_main=require_current_main,
    )
    if recovery_errors is not None:
        return recovery_errors
    recovery_errors = _g0_t02_recovery_parent_errors(
        status,
        parent,
        parent_sha,
        root,
        child_sha,
        require_failed_main=require_current_main,
    )
    if recovery_errors is not None:
        return recovery_errors
    recovery_errors = _g0_t03_recovery_parent_errors(
        status,
        parent,
        parent_sha,
        root,
        child_sha,
        require_current_main=require_current_main,
    )
    if recovery_errors is not None:
        return recovery_errors
    recovery_errors = _g0_t03_recovery_merge_recovery_parent_errors(
        status,
        parent,
        parent_sha,
        root,
        child_sha,
        require_current_main=require_current_main,
    )
    if recovery_errors is not None:
        return recovery_errors
    reconciliation_errors = _g0_t03_status_reconciliation_parent_errors(
        status,
        parent,
        parent_sha,
        root,
        child_sha,
        require_current_main=require_current_main,
    )
    if reconciliation_errors is not None:
        return reconciliation_errors
    final_close_repair_errors = _g0_t03_final_close_repair_parent_errors(
        status,
        parent,
        parent_sha,
        root,
        child_sha,
        require_current_main=require_current_main,
    )
    if final_close_repair_errors is not None:
        return final_close_repair_errors
    final_close_repair_errors = _g0_t02_final_close_repair_parent_errors(
        status, parent, parent_sha, root, child_sha
    )
    if final_close_repair_errors is not None:
        return final_close_repair_errors
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
        generation = current_task["candidate_generation"]
        if _typed_equal(generation, 1):
            pass
        elif type(generation) is int and generation >= 2:
            errors.extend(_blocked_reauthorization_errors(status, parent_sha, root, child_sha))
        else:
            errors.append("$.active_tasks[0].candidate_generation: initial authorization must use generation one")
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


def _governed_first_parent_chain(root: Path, head: str, current_schema: dict[str, Any]) -> list[str]:
    chain: list[str] = []
    seen: set[str] = set()
    sha = head
    premature_recovery = (
        head != G0_T04_G4_PREMATURE_MAIN
        and _is_ancestor(root, G0_T04_G4_PREMATURE_MAIN, head)
    )
    while sha not in seen:
        seen.add(sha)
        chain.append(sha)
        ok, parents_text = _git(root, "rev-list", "--parents", "-n", "1", sha)
        parts = parents_text.split() if ok else []
        if len(parts) < 2:
            break
        next_sha = parts[1]
        if len(parts) == 3:
            if (
                premature_recovery
                and sha == G0_T04_G4_PREMATURE_MAIN
                and parts
                == [
                    G0_T04_G4_PREMATURE_MAIN,
                    G0_T04_G4_PREMATURE_MAIN_FIRST_PARENT,
                    G0_T04_G4_PREMATURE_MAIN_SECOND_PARENT,
                ]
            ):
                next_sha = G0_T04_G4_PREMATURE_MAIN_SECOND_PARENT
                sha = next_sha
                continue
            node = _status_at(root, sha)
            if type(node) is dict:
                governed_parent, bridge_errors = _canonical_g0_merge_bridge(
                    node, root, sha, current_schema, require_canonical_main=False
                )
                if governed_parent is not None and not bridge_errors:
                    next_sha = governed_parent
        sha = next_sha
    return chain


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
            governed_parent, bridge_errors = _canonical_g0_merge_bridge(
                child, root, child_sha, current_schema, require_canonical_main=False
            )
            if governed_parent == parent_sha and not bridge_errors:
                inherited_merge_bridge = True
            if not inherited_merge_bridge and child == parent and child["active_tasks"][0]["state"] == "accepted_pending_merge" and index > 0:
                _, newer, newer_valid = statuses[index - 1]
                if newer_valid:
                    inherited_merge_bridge = (
                        newer["active_tasks"][0]["state"] == "merged_verified"
                        and newer["evidence"]["merged_main"]["commit_sha"] == child_sha
                    )
            if not inherited_merge_bridge:
                errors.extend(
                    _parent_status_errors(
                        child,
                        parent,
                        parent_sha,
                        root,
                        child_sha,
                        require_current_main=False,
                    )
                )
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
    governed_chain = _governed_first_parent_chain(root, head, current_schema)
    if type(anchor) is not str or anchor not in governed_chain:
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
            or SCHEMA_BOOTSTRAP_SUBJECT not in governed_chain
            or hashlib.sha256(schema_payload).hexdigest() != SCHEMA_PREAUTHORITY_HISTORY_DIGEST
            or type(migration) is not dict
            or migration.get("preauthority_history_sha256") != SCHEMA_PREAUTHORITY_HISTORY_DIGEST
        ):
            errors.append("$.schema_authority.migration: sealed pre-authority schema history mismatch")
    commits = governed_chain[: governed_chain.index(anchor)] + [anchor]
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
        governed_parent, bridge_errors = _canonical_g0_merge_bridge(
            child, root, child_sha, current_schema, require_canonical_main=False
        )
        if governed_parent == parent_sha and not bridge_errors:
            inherited_merge_bridge = True
        if not inherited_merge_bridge and child == parent and child["active_tasks"][0]["state"] == "accepted_pending_merge" and index > 0:
            _, newer, newer_valid = statuses[index - 1]
            if newer_valid:
                inherited_merge_bridge = (
                    newer["active_tasks"][0]["state"] == "merged_verified"
                    and newer["evidence"]["merged_main"]["commit_sha"] == child_sha
                )
        if not inherited_merge_bridge:
            errors.extend(
                _parent_status_errors(
                    child,
                    parent,
                    parent_sha,
                    root,
                    child_sha,
                    require_current_main=False,
                )
            )
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


def _canonical_status_digest(status: dict[str, Any]) -> str:
    canonical = json.dumps(status, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _is_g0_t04_accepted_status(status: dict[str, Any]) -> bool:
    """Match the exact reviewed G0-T04 generation-3 acceptance."""
    try:
        return (
            status["active_tasks"][0]
            == {
                "task_id": "G0-T04",
                "risk": "D0",
                "state": "accepted_pending_merge",
                "transition": {
                    "from": "awaiting_review",
                    "to": "accepted_pending_merge",
                },
                "candidate_generation": 3,
            }
            and status["evidence"]["authorization_baseline_sha"]
            == G0_T04_FAILED_MAIN_FIRST_PARENT
            and status["evidence"]["implementation_sha"]
            == "57d65f47709b4f683e4326051c737ed037b15b83"
            and status["evidence"]["candidate"]
            == {
                "commit_sha": G0_T04_CANDIDATE_SHA,
                "local_verification": {
                    "status": "success",
                    "subject": "delivery_head",
                },
                "ci": {
                    "status": "success",
                    "subject_sha": G0_T04_CANDIDATE_SHA,
                    "run_id": G0_T04_CANDIDATE_RUN,
                    "url": (
                        "https://github.com/weizhenhaihaha-arch/yaobizuoduo/"
                        f"actions/runs/{G0_T04_CANDIDATE_RUN}"
                    ),
                },
            }
            and status["review"]
            == {
                "code_security": "approve",
                "architecture": "clear",
                "reviewed_candidate_sha": G0_T04_CANDIDATE_SHA,
            }
            and status["blockers"] == []
            and status["next_authorization"]
            == {"gate": "G0", "task_id": "G0-T05", "state": "not_authorized"}
            and _canonical_status_digest(status) == G0_T04_ACCEPTED_STATUS_DIGEST
        )
    except (KeyError, IndexError, TypeError, ValueError):
        return False


def _is_g0_t04_post_merge_recovery_status(status: dict[str, Any]) -> bool:
    """Recognize only the exact G0-T04 failed-main recovery state."""
    try:
        if (
            status["active_tasks"][0]["transition"]
            != {
                "from": "accepted_pending_merge",
                "to": "accepted_pending_merge",
            }
            or status["blockers"] != [G0_T04_RECOVERY_BLOCKER]
        ):
            return False
        projected = json.loads(json.dumps(status))
        projected["active_tasks"][0]["transition"] = {
            "from": "awaiting_review",
            "to": "accepted_pending_merge",
        }
        projected["blockers"] = []
        return _is_g0_t04_accepted_status(projected)
    except (KeyError, IndexError, TypeError, ValueError):
        return False


def _g0_t04_recovery_receipt() -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema_version": G0_T04_RECOVERY_RECEIPT_VERSION,
        "project": "yaobizuoduo",
        "task_id": "G0-T04",
        "candidate_generation": 3,
        "purpose": "bounded_merged_main_ci_recovery",
        "candidate": {
            "commit_sha": G0_T04_CANDIDATE_SHA,
            "ci": {
                "repository": "weizhenhaihaha-arch/yaobizuoduo",
                "event": "pull_request",
                "check": "G0 / exact-head",
                "subject_sha": G0_T04_CANDIDATE_SHA,
                "run_id": G0_T04_CANDIDATE_RUN,
                "url": (
                    "https://github.com/weizhenhaihaha-arch/yaobizuoduo/"
                    f"actions/runs/{G0_T04_CANDIDATE_RUN}"
                ),
                "status": "completed",
                "conclusion": "success",
            },
            "review": {
                "code_security": "approve",
                "architecture": "clear",
            },
        },
        "closure": {
            "commit_sha": G0_T04_CLOSURE_SHA,
            "ci": {
                "repository": "weizhenhaihaha-arch/yaobizuoduo",
                "event": "pull_request",
                "check": "G0 / exact-head",
                "subject_sha": G0_T04_CLOSURE_SHA,
                "run_id": G0_T04_CLOSURE_RUN,
                "url": (
                    "https://github.com/weizhenhaihaha-arch/yaobizuoduo/"
                    f"actions/runs/{G0_T04_CLOSURE_RUN}"
                ),
                "status": "completed",
                "conclusion": "success",
            },
        },
        "failed_main": {
            "commit_sha": G0_T04_FAILED_MAIN_SHA,
            "ordered_parents": [
                G0_T04_FAILED_MAIN_FIRST_PARENT,
                G0_T04_FAILED_MAIN_SECOND_PARENT,
            ],
            "tree_sha": G0_T04_FAILED_MAIN_TREE,
            "ci": {
                "repository": "weizhenhaihaha-arch/yaobizuoduo",
                "event": "push",
                "ref": "refs/heads/main",
                "check": "G0 / exact-head",
                "subject_sha": G0_T04_FAILED_MAIN_SHA,
                "run_id": G0_T04_FAILED_MAIN_RUN,
                "url": (
                    "https://github.com/weizhenhaihaha-arch/yaobizuoduo/"
                    f"actions/runs/{G0_T04_FAILED_MAIN_RUN}"
                ),
                "status": "completed",
                "conclusion": "failure",
            },
        },
        "ruleset": {
            "id": G0_T03_RULESET_ID,
            "readback_sha256": G0_T03_RULESET_EVIDENCE_DIGEST,
        },
        "package_a": {
            "manifest_path": PACKAGE_A_MANIFEST_PATH,
            "schema_path": PACKAGE_A_SCHEMA_PATH,
            "schema_sha256": PACKAGE_A_SCHEMA_SHA256,
            "payload_sha256": PACKAGE_A_PAYLOAD_SHA256,
            "ordered_tasks": PACKAGE_A_ORDERED_TASKS,
            "state": "not_authorized",
        },
    }
    receipt["payload_sha256"] = _payload_digest(receipt)
    return receipt


def _g0_t04_recovery_receipt_errors(root: Path, subject_sha: str) -> list[str]:
    ok_entry, entry = _git(
        root, "ls-tree", subject_sha, "--", G0_T04_RECOVERY_RECEIPT_PATH
    )
    fields = entry.split(None, 3) if ok_entry else []
    if len(fields) != 4 or fields[0] != "100644" or fields[1] != "blob":
        return ["$: G0-T04 recovery receipt must be an exact committed 100644 blob"]
    ok_bytes, actual = _git_bytes(
        root, "show", f"{subject_sha}:{G0_T04_RECOVERY_RECEIPT_PATH}"
    )
    expected = (
        json.dumps(_g0_t04_recovery_receipt(), indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    if not ok_bytes or actual != expected:
        return ["$: G0-T04 recovery receipt bytes or immutable evidence drifted"]
    return []


def _g0_t04_anomaly_receipt() -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema_version": "g0-t04-review-chain.v2",
        "task_id": "G0-T04",
        "pr15": {
            "head": "06feb30d43360ef732242f1be4ad02478823f47a",
            "merge": "8d87f58e690a2ea7fac74d432495c8873d5a9d87",
            "parents": [
                "11040ca0d8ea17ba1bc47641705aa95c2cba6a75",
                "06feb30d43360ef732242f1be4ad02478823f47a",
            ],
            "tree": "4b7404240a4f81282764059b63be906fec5da377",
            "reviews": [],
            "pr_run": "29990406421",
            "push_run": "29991346572",
        },
        "pr17": {
            "head": "b7a2e3fa15d09de15293a384e58bf4575e0cdeca",
            "merge": "3e8e286a208ee12c47d06d8300af20f7f784333d",
            "parents": [
                "8d87f58e690a2ea7fac74d432495c8873d5a9d87",
                "b7a2e3fa15d09de15293a384e58bf4575e0cdeca",
            ],
            "tree": "836812adac03a65bf5d540250de4f9f753a50b09",
            "reviews": [],
            "checks": ["29991698100", "29991698097"],
        },
        "pr19": {
            "head": "f3e4d5b83e0ee763c61dba1d399104e38883300c",
            "merge": G0_T04_ANOMALY_ORIGIN,
            "parents": [
                "3e8e286a208ee12c47d06d8300af20f7f784333d",
                "f3e4d5b83e0ee763c61dba1d399104e38883300c",
            ],
            "tree": "8f6005545a3c19f583b6cf18e4380d09fd90686e",
            "reviews": [],
            "checks": [
                "29992496446",
                "29992525232",
                "29992552022",
                "29992604142",
                "29992606714",
            ],
            "push_run": "29992685457",
        },
        "pr20": {
            "head": "1851eff8974a2263152dd1e31b7191712f40b0d3",
            "merge": "12034455e52d70c94a502136661b5bf7500c5f77",
            "parents": [
                G0_T04_ANOMALY_ORIGIN,
                "1851eff8974a2263152dd1e31b7191712f40b0d3",
            ],
            "tree": "474326cdee26fc799d83c4bba316a4d95609cb70",
            "reviews": [],
            "pr_run": "29998102619",
            "push_run": "29998136427",
        },
        "pr21": {
            "head": "d0cbc0fb7068e07925bd2decb18c06940105d79b",
            "merge": "be322ab4c03cff0d1b6600945d463c791433e96a",
            "parents": [
                "12034455e52d70c94a502136661b5bf7500c5f77",
                "d0cbc0fb7068e07925bd2decb18c06940105d79b",
            ],
            "tree": "4990a1fd1f5b8fafc8b1ec1fd2cf07c12020af92",
            "reviews": [],
            "pr_run": "29998286908",
            "push_run": "29998320978",
        },
        "pr22": {
            "head": "d194462439d0c5dd5d01aa226aeceeaac8cec656",
            "merge": G0_T04_ANOMALY_MAIN,
            "parents": [
                "be322ab4c03cff0d1b6600945d463c791433e96a",
                "d194462439d0c5dd5d01aa226aeceeaac8cec656",
            ],
            "tree": "3e8dcb668de2c004f5ee439d8d6fa4e4233359e3",
            "reviews": [],
            "pr_run": "29998431313",
            "push_run": "29998455189",
        },
        "invalid_assertions": {
            "product_owner_confirmation": "not_observed",
            "package_a_activation": "not_authorized",
            "g0_t05": "not_authorized",
            "g1_t01": "not_authorized",
            "activation_path": PACKAGE_A_ACTIVATION_PATH,
            "activation_blob": "c061d55218098fd5957ef75d40cb855635371bb6",
            "activation_sha256": "884afa51508d70f1406646a4743aca1935eeced41f5222fc91e37164db8546a6",
        },
        "independent_review": {
            "code_security": "request_changes",
            "architecture_route": "block",
            "p1": "2_failed_tests_missing_frozen_refs",
        },
        "ruleset": {
            "id": 19526291,
            "readback_sha256": G0_T03_RULESET_EVIDENCE_DIGEST,
            "required_review_count": 0,
            "required_status_check": "G0 / exact-head",
            "bypass_actors": [],
        },
        "package_a": {
            "manifest_blob": "f523c793a58d27e8ffd79da01048c8cd93aaa315",
            "manifest_sha256": "ae99c3ea471402c156c189067a771ca3b903380c9e8b4f64c0bf9e83096050a6",
            "schema_blob": "132656bcda439c20a2ade78d30116c49706de7b3",
            "schema_sha256": PACKAGE_A_SCHEMA_SHA256,
            "payload_sha256": PACKAGE_A_PAYLOAD_SHA256,
            "ordered_task_ids": PACKAGE_A_ORDERED_TASKS,
            "state": "not_authorized",
        },
    }
    receipt["payload_sha256"] = _payload_digest(receipt)
    return receipt


def _g0_t04_anomaly_validation_report() -> dict[str, Any]:
    return {
        "schema_version": "canonical-validation-report.v1",
        "subject_sha": G0_T04_ANOMALY_CANDIDATE,
        "results": {
            "focused_governance": {"passed": 9, "deselected": 264},
            "canonical_validator": {
                "result": "ok",
                "schema_version": "project-status.v2",
            },
            "full_non_transport": {"passed": 380},
            "metamorphic_transport": {"passed": 15},
            "frontend": {"passed": 10},
            "production_build": {"result": "pass"},
        },
    }


def _g0_t04_anomaly_seal() -> dict[str, Any]:
    report = _g0_t04_anomaly_validation_report()
    seal: dict[str, Any] = {
        "schema_version": G0_T04_ANOMALY_SEAL_VERSION,
        "project": "yaobizuoduo",
        "task_id": "G0-T04",
        "candidate_generation": 3,
        "topology": {
            "anomalous_main": {
                "sha": G0_T04_ANOMALY_MAIN,
                "tree": "3e8dcb668de2c004f5ee439d8d6fa4e4233359e3",
            },
            "implementation": {
                "sha": G0_T04_ANOMALY_IMPLEMENTATION,
                "parents": [G0_T04_ANOMALY_MAIN],
                "tree": "c730f2e21d1baad993f49ad833d127b839e0cac0",
                "changed_paths": [
                    "scripts/validate_project_status.py",
                    "tests/test_g0_project_status.py",
                ],
            },
            "candidate": {
                "sha": G0_T04_ANOMALY_CANDIDATE,
                "parents": [G0_T04_ANOMALY_IMPLEMENTATION],
                "tree": "263342bfd2a6c72cbb6765602b515e7e44cd38a5",
                "changed_paths_from_main": sorted(G0_T04_ANOMALY_ALLOWED),
            },
        },
        "candidate": {
            "sha": G0_T04_ANOMALY_CANDIDATE,
            "pull_request": 23,
            "base_sha": G0_T04_ANOMALY_MAIN,
            "ci": {
                "repository": "weizhenhaihaha-arch/yaobizuoduo",
                "event": "pull_request",
                "subject_sha": G0_T04_ANOMALY_CANDIDATE,
                "run_id": "30005396033",
                "url": (
                    "https://github.com/weizhenhaihaha-arch/yaobizuoduo/"
                    "actions/runs/30005396033"
                ),
                "check": "G0 / exact-head",
                "status": "completed",
                "conclusion": "success",
            },
        },
        "main_codex_verification": {
            "subject_sha": G0_T04_ANOMALY_CANDIDATE,
            "validation_report": report,
            "validation_report_sha256": _payload_digest(report),
        },
        "review": {
            "code_security": {
                "reviewer": "/root/workflow_critic/g0_t04_code_lane",
                "subject_sha": G0_T04_ANOMALY_CANDIDATE,
                "decision": "approve",
            },
            "architecture": {
                "reviewer": "/root/workflow_architect",
                "subject_sha": G0_T04_ANOMALY_CANDIDATE,
                "decision": "clear_for_seal",
            },
        },
        "anomaly_receipt": {
            "path": G0_T04_ANOMALY_RECEIPT_PATH,
            "blob": "c71560939c1b6fd0c6f038c3fe723df178fa2596",
            "payload_sha256": (
                "52740d951f85f4a25d30cda2d1787e294c0227c98f4c5c34e66deff75b58e2f8"
            ),
        },
        "false_activation": {
            "path": PACKAGE_A_ACTIVATION_PATH,
            "historical_main": G0_T04_ANOMALY_MAIN,
            "historical_blob": "c061d55218098fd5957ef75d40cb855635371bb6",
            "historical_sha256": (
                "884afa51508d70f1406646a4743aca1935eeced41f5222fc91e37164db8546a6"
            ),
            "present_in_candidate": False,
            "present_in_seal": False,
        },
        "package_a": {
            "manifest_blob": "f523c793a58d27e8ffd79da01048c8cd93aaa315",
            "schema_blob": "132656bcda439c20a2ade78d30116c49706de7b3",
            "payload_sha256": PACKAGE_A_PAYLOAD_SHA256,
            "ordered_task_ids": PACKAGE_A_ORDERED_TASKS,
            "state": "not_authorized",
        },
        "ruleset": {
            "id": G0_T03_RULESET_ID,
            "readback_sha256": G0_T03_RULESET_EVIDENCE_DIGEST,
        },
        "capability": {
            "maturity": "OFFLINE_EVIDENCE_ACCEPTED",
            "g0_t05": "not_authorized",
            "g1_t01": "not_authorized",
        },
        "seal_allowlist": sorted(G0_T04_ANOMALY_SEAL_ALLOWED),
        "same_tree_identity_boundary": "external_ci_and_independent_review",
    }
    seal["payload_sha256"] = _payload_digest(seal)
    return seal


def _g0_t04_anomaly_status(root: Path) -> dict[str, Any]:
    base = _status_at(root, G0_T04_ANOMALY_ORIGIN)
    if type(base) is not dict:
        return {}
    status = json.loads(json.dumps(base))
    status["active_tasks"][0].update(
        task_id="G0-T04",
        risk="D0",
        state="blocked",
        transition={"from": "closed", "to": "blocked"},
        candidate_generation=3,
    )
    status["review"] = {
        "code_security": "pending",
        "architecture": "pending",
        "reviewed_candidate_sha": None,
    }
    status["blockers"] = [G0_T04_ANOMALY_BLOCKER]
    status["next_authorization"] = {
        "gate": "G0",
        "task_id": "G0-T05",
        "state": "not_authorized",
    }
    return status


def _g0_t04_anomaly_seal_status(root: Path) -> dict[str, Any]:
    status = _g0_t04_anomaly_status(root)
    if not status:
        return {}
    status["active_tasks"][0]["transition"] = {"from": "blocked", "to": "blocked"}
    status["review"] = {
        "code_security": "approve",
        "architecture": "clear",
        "reviewed_candidate_sha": G0_T04_ANOMALY_CANDIDATE,
    }
    return status


def _is_g0_t04_anomaly_status(status: dict[str, Any]) -> bool:
    try:
        return (
            status["active_tasks"][0] == {
                "task_id": "G0-T04",
                "risk": "D0",
                "state": "blocked",
                "transition": {"from": "closed", "to": "blocked"},
                "candidate_generation": 3,
            }
            and status["review"]
            == {
                "code_security": "pending",
                "architecture": "pending",
                "reviewed_candidate_sha": None,
            }
            and status["blockers"] == [G0_T04_ANOMALY_BLOCKER]
            and status["next_authorization"]
            == {"gate": "G0", "task_id": "G0-T05", "state": "not_authorized"}
            and status.get("transition_ledger")
            == {
                "authorization_baseline_sha": BOOTSTRAP_BASELINE,
                "sealed_through_sha": LEDGER_ANCHOR,
                "first_parent_chain_sha256": LEDGER_DIGEST,
            }
        )
    except (KeyError, IndexError, TypeError):
        return False


def _is_g0_t04_anomaly_seal_status(status: dict[str, Any]) -> bool:
    try:
        return (
            status["active_tasks"][0]
            == {
                "task_id": "G0-T04",
                "risk": "D0",
                "state": "blocked",
                "transition": {"from": "blocked", "to": "blocked"},
                "candidate_generation": 3,
            }
            and status["review"]
            == {
                "code_security": "approve",
                "architecture": "clear",
                "reviewed_candidate_sha": G0_T04_ANOMALY_CANDIDATE,
            }
            and status["blockers"] == [G0_T04_ANOMALY_BLOCKER]
            and status["next_authorization"]
            == {"gate": "G0", "task_id": "G0-T05", "state": "not_authorized"}
            and status.get("transition_ledger")
            == {
                "authorization_baseline_sha": BOOTSTRAP_BASELINE,
                "sealed_through_sha": LEDGER_ANCHOR,
                "first_parent_chain_sha256": LEDGER_DIGEST,
            }
        )
    except (KeyError, IndexError, TypeError):
        return False


def _g0_t04_anomaly_receipt_errors(root: Path, subject_sha: str) -> list[str]:
    ok_entry, entry = _git(
        root, "ls-tree", subject_sha, "--", G0_T04_ANOMALY_RECEIPT_PATH
    )
    fields = entry.split(None, 3) if ok_entry else []
    ok_data, actual = _git_bytes(
        root, "show", f"{subject_sha}:{G0_T04_ANOMALY_RECEIPT_PATH}"
    )
    expected = (
        json.dumps(_g0_t04_anomaly_receipt(), indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    if (
        len(fields) != 4
        or fields[0] != "100644"
        or fields[1] != "blob"
        or fields[3] != G0_T04_ANOMALY_RECEIPT_PATH
        or not ok_data
        or actual != expected
    ):
        return ["$: G0-T04 anomaly receipt drifted"]
    return []


def _g0_t04_anomaly_topology_errors(root: Path) -> list[str]:
    checks = {
        "8d87f58e690a2ea7fac74d432495c8873d5a9d87": (
            [
                "11040ca0d8ea17ba1bc47641705aa95c2cba6a75",
                "06feb30d43360ef732242f1be4ad02478823f47a",
            ],
            "4b7404240a4f81282764059b63be906fec5da377",
        ),
        "3e8e286a208ee12c47d06d8300af20f7f784333d": (
            [
                "8d87f58e690a2ea7fac74d432495c8873d5a9d87",
                "b7a2e3fa15d09de15293a384e58bf4575e0cdeca",
            ],
            "836812adac03a65bf5d540250de4f9f753a50b09",
        ),
        G0_T04_ANOMALY_ORIGIN: (
            [
                "3e8e286a208ee12c47d06d8300af20f7f784333d",
                "f3e4d5b83e0ee763c61dba1d399104e38883300c",
            ],
            "8f6005545a3c19f583b6cf18e4380d09fd90686e",
        ),
        "12034455e52d70c94a502136661b5bf7500c5f77": (
            [
                G0_T04_ANOMALY_ORIGIN,
                "1851eff8974a2263152dd1e31b7191712f40b0d3",
            ],
            "474326cdee26fc799d83c4bba316a4d95609cb70",
        ),
        "be322ab4c03cff0d1b6600945d463c791433e96a": (
            [
                "12034455e52d70c94a502136661b5bf7500c5f77",
                "d0cbc0fb7068e07925bd2decb18c06940105d79b",
            ],
            "4990a1fd1f5b8fafc8b1ec1fd2cf07c12020af92",
        ),
        G0_T04_ANOMALY_MAIN: (
            [
                "be322ab4c03cff0d1b6600945d463c791433e96a",
                "d194462439d0c5dd5d01aa226aeceeaac8cec656",
            ],
            "3e8dcb668de2c004f5ee439d8d6fa4e4233359e3",
        ),
    }
    errors: list[str] = []
    for sha, (parents, tree) in checks.items():
        ok_line, line = _git(root, "rev-list", "--parents", "-n", "1", sha)
        ok_tree, actual_tree = _git(root, "rev-parse", f"{sha}^{{tree}}")
        if (
            (line.split() if ok_line else []) != [sha, *parents]
            or not ok_tree
            or actual_tree != tree
        ):
            errors.append(f"$: G0-T04 anomaly topology drifted at {sha[:12]}")
    return errors


def _g0_t04_anomaly_delivery_errors(
    status: dict[str, Any],
    root: Path,
    subject_sha: str,
    *,
    require_current_main: bool,
) -> list[str]:
    errors = _g0_t04_anomaly_topology_errors(root)
    expected_status = _g0_t04_anomaly_status(root)
    if not expected_status or not _typed_equal(status, expected_status):
        errors.append("$: G0-T04 anomaly recovery status drifted")
    errors.extend(_g0_t04_anomaly_receipt_errors(root, subject_sha))
    changed = _g0_t03_commit_changed_paths(root, G0_T04_ANOMALY_MAIN, subject_sha)
    if (
        changed is None
        or not G0_T04_ANOMALY_REQUIRED.issubset(changed)
        or not changed.issubset(G0_T04_ANOMALY_ALLOWED)
    ):
        errors.append("$: G0-T04 anomaly recovery allowlist drifted")
    for relative, expected_blob in (
        (PACKAGE_A_MANIFEST_PATH, "f523c793a58d27e8ffd79da01048c8cd93aaa315"),
        (PACKAGE_A_SCHEMA_PATH, "132656bcda439c20a2ade78d30116c49706de7b3"),
    ):
        for sha in (G0_T04_ANOMALY_ORIGIN, G0_T04_ANOMALY_MAIN, subject_sha):
            ok_blob, blob = _git(root, "rev-parse", f"{sha}:{relative}")
            if not ok_blob or blob != expected_blob:
                errors.append(f"$: immutable Package A blob drifted at {sha[:12]}:{relative}")
    ok_activation, activation_blob = _git(
        root, "rev-parse", f"{G0_T04_ANOMALY_MAIN}:{PACKAGE_A_ACTIVATION_PATH}"
    )
    if not ok_activation or activation_blob != "c061d55218098fd5957ef75d40cb855635371bb6":
        errors.append("$: anomalous activation history blob drifted")
    if _git(root, "cat-file", "-e", f"{subject_sha}:{PACKAGE_A_ACTIVATION_PATH}")[0]:
        errors.append("$: false Package A activation assertion must be absent from recovery")
    if require_current_main:
        ok_main, main = _git(
            root, "rev-parse", "--verify", status["authoritative_main_ref"]
        )
        ok_remote, remote = _git(
            root, "rev-parse", "--verify", "refs/remotes/origin/main"
        )
        ok_origin, origin_url = _git(root, "remote", "get-url", "origin")
        if (
            not ok_main
            or not ok_remote
            or main != remote
            or main != G0_T04_ANOMALY_MAIN
            or not ok_origin
            or _github_repository_identity(origin_url) != LEDGER_REPOSITORY
        ):
            errors.append("$: G0-T04 anomaly recovery requires exact current main")
    return errors


def _g0_t04_anomaly_seal_errors(
    status: dict[str, Any],
    root: Path,
    subject_sha: str,
    *,
    require_current_main: bool,
) -> list[str]:
    errors: list[str] = []
    expected_status = _g0_t04_anomaly_seal_status(root)
    if not expected_status or not _typed_equal(status, expected_status):
        errors.append("$: G0-T04 anomaly seal status drifted")
    changed = _g0_t03_commit_changed_paths(
        root, G0_T04_ANOMALY_CANDIDATE, subject_sha
    )
    if changed != set(G0_T04_ANOMALY_SEAL_ALLOWED):
        errors.append("$: G0-T04 anomaly seal allowlist drifted")
    if _git(
        root,
        "cat-file",
        "-e",
        f"{G0_T04_ANOMALY_CANDIDATE}:{G0_T04_ANOMALY_SEAL_PATH}",
    )[0]:
        errors.append("$: reviewed candidate C must not define its own later seal")
    expected_seal = (
        json.dumps(_g0_t04_anomaly_seal(), indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    ok_seal, actual_seal = _git_bytes(
        root, "show", f"{subject_sha}:{G0_T04_ANOMALY_SEAL_PATH}"
    )
    if not ok_seal or actual_seal != expected_seal:
        errors.append("$: G0-T04 anomaly seal bytes or digest drifted")
    for sha in (G0_T04_ANOMALY_CANDIDATE, subject_sha):
        ok_receipt, receipt_blob = _git(
            root, "rev-parse", f"{sha}:{G0_T04_ANOMALY_RECEIPT_PATH}"
        )
        if not ok_receipt or receipt_blob != "c71560939c1b6fd0c6f038c3fe723df178fa2596":
            errors.append(f"$: G0-T04 anomaly receipt blob drifted at {sha[:12]}")
        for relative, expected_blob in (
            (
                PACKAGE_A_MANIFEST_PATH,
                "f523c793a58d27e8ffd79da01048c8cd93aaa315",
            ),
            (
                PACKAGE_A_SCHEMA_PATH,
                "132656bcda439c20a2ade78d30116c49706de7b3",
            ),
        ):
            ok_blob, blob = _git(root, "rev-parse", f"{sha}:{relative}")
            if not ok_blob or blob != expected_blob:
                errors.append(
                    f"$: immutable Package A blob drifted at {sha[:12]}:{relative}"
                )
        if _git(root, "cat-file", "-e", f"{sha}:{PACKAGE_A_ACTIVATION_PATH}")[0]:
            errors.append(
                f"$: false Package A activation reappeared at {sha[:12]}"
            )
    ok_history, history_blob = _git(
        root, "rev-parse", f"{G0_T04_ANOMALY_MAIN}:{PACKAGE_A_ACTIVATION_PATH}"
    )
    if not ok_history or history_blob != "c061d55218098fd5957ef75d40cb855635371bb6":
        errors.append("$: false activation immutable history drifted")
    ok_origin, origin_url = _git(root, "remote", "get-url", "origin")
    if not ok_origin or _github_repository_identity(origin_url) != LEDGER_REPOSITORY:
        errors.append("$: G0-T04 anomaly seal requires canonical repository identity")
    if require_current_main:
        ok_main, main = _git(
            root, "rev-parse", "--verify", status["authoritative_main_ref"]
        )
        ok_remote, remote = _git(
            root, "rev-parse", "--verify", "refs/remotes/origin/main"
        )
        if (
            not ok_main
            or not ok_remote
            or main != remote
            or main != G0_T04_ANOMALY_MAIN
        ):
            errors.append("$: G0-T04 anomaly seal requires exact current main")
    # The seal cannot contain its own future SHA. A same-tree sibling S' is
    # intentionally distinguished only by the subsequent external CI/review gate.
    return errors


def _is_g0_t03_accepted_status(status: dict[str, Any]) -> bool:
    """Match the immutable accepted G0-T03 generation-3 status exactly."""
    try:
        task = status["active_tasks"][0]
        evidence = status["evidence"]
        return (
            task == {
                "task_id": "G0-T03",
                "risk": "D2",
                "state": "accepted_pending_merge",
                "transition": {"from": "awaiting_review", "to": "accepted_pending_merge"},
                "candidate_generation": 3,
            }
            and evidence["authorization_baseline_sha"] == "09bfbd23d898198fe694a3a94f77663759dd89d8"
            and evidence["implementation_sha"] == G0_T03_IMPLEMENTATION_SHA
            and evidence["candidate"]["commit_sha"] == G0_T03_CANDIDATE_SHA
            and evidence["candidate"]["ci"] == {
                "status": "success",
                "subject_sha": G0_T03_CANDIDATE_SHA,
                "run_id": "29893836848",
                "url": "https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/29893836848",
            }
            and status["review"] == {
                "code_security": "approve",
                "architecture": "clear",
                "reviewed_candidate_sha": G0_T03_CANDIDATE_SHA,
            }
            and status["blockers"] == []
            and _canonical_status_digest(status) == G0_T03_ACCEPTED_STATUS_DIGEST
        )
    except (KeyError, IndexError, TypeError, ValueError):
        return False


def _is_g0_t03_post_merge_recovery_status(status: dict[str, Any]) -> bool:
    """Recognize only the exact failed-main recovery for G0-T03 generation 3."""
    try:
        task = status["active_tasks"][0]
        if task != {
            "task_id": "G0-T03",
            "risk": "D2",
            "state": "accepted_pending_merge",
            "transition": {"from": "accepted_pending_merge", "to": "accepted_pending_merge"},
            "candidate_generation": 3,
        } or status["blockers"] != [G0_T03_RECOVERY_BLOCKER]:
            return False
        projected = json.loads(json.dumps(status))
        projected["active_tasks"][0]["transition"] = {
            "from": "awaiting_review",
            "to": "accepted_pending_merge",
        }
        projected["blockers"] = []
        return _is_g0_t03_accepted_status(projected)
    except (KeyError, IndexError, TypeError, ValueError):
        return False


def _is_g0_t03_recovery_merge_recovery_status(status: dict[str, Any]) -> bool:
    """Match only the second recovery record rooted at the exact PR #7 merge failure."""
    try:
        if status["blockers"] != [G0_T03_RECOVERY_BLOCKER, G0_T03_RECOVERY_MERGE_BLOCKER]:
            return False
        projected = json.loads(json.dumps(status))
        projected["blockers"] = [G0_T03_RECOVERY_BLOCKER]
        return (
            _is_g0_t03_post_merge_recovery_status(projected)
            and _canonical_status_digest(projected) == G0_T03_RECOVERY_STATUS_DIGEST
        )
    except (KeyError, TypeError, ValueError):
        return False


def _is_g0_t02_post_merge_recovery_status(status: dict[str, Any]) -> bool:
    """Recognize the one authorized failed-main recovery without widening ordinary transitions."""
    try:
        task = status["active_tasks"][0]
        evidence = status["evidence"]
        return (
            status["project"] == "yaobizuoduo"
            and status["authoritative_main_ref"] == "refs/heads/main"
            and status["current_gate"] == "G0"
            and task == {
                "task_id": "G0-T02",
                "risk": "D2",
                "state": "accepted_pending_merge",
                "transition": {"from": "accepted_pending_merge", "to": "accepted_pending_merge"},
                "candidate_generation": 5,
            }
            and evidence["authorization_baseline_sha"] == "94892d79b8d39ac1726cf657fac0ae76a0e27b37"
            and evidence["implementation_sha"] == "2ec1a50ad513f81cf3637e82501e4e4d74b5bf1f"
            and evidence["candidate"] == {
                "commit_sha": "35b90f87ab42843925065e6d0dafdc25797702e0",
                "local_verification": {"status": "success", "subject": "delivery_head"},
                "ci": {
                    "status": "success",
                    "subject_sha": "35b90f87ab42843925065e6d0dafdc25797702e0",
                    "run_id": "29884205742",
                    "url": "https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/29884205742",
                },
            }
            and evidence["closure"] == {
                "commit_sha": None,
                "ci": {"status": "not_established", "subject_sha": None, "run_id": None, "url": None},
            }
            and evidence["merged_main"] == {
                "commit_sha": None,
                "ci": {"status": "not_established", "subject_sha": None, "run_id": None, "url": None},
            }
            and evidence["finalization"] == {
                "commit_sha": None,
                "d0_ci": {"status": "not_established", "subject_sha": None, "run_id": None, "url": None},
            }
            and status["review"] == {
                "code_security": "approve",
                "architecture": "clear",
                "reviewed_candidate_sha": "35b90f87ab42843925065e6d0dafdc25797702e0",
            }
            and status.get("schema_authority") == {
                "revision": 1,
                "sha256": "192787ae5ad594bf3fce57af75de8bb9db99c83adac93ad1434fc49d63579e5e",
                "migration": {
                    "from_revision": 0,
                    "from_sha256": SCHEMA_BOOTSTRAP_OLD_DIGEST,
                    "to_revision": 1,
                    "to_sha256": "192787ae5ad594bf3fce57af75de8bb9db99c83adac93ad1434fc49d63579e5e",
                    "authorization_sha": SCHEMA_BOOTSTRAP_SUBJECT,
                    "compatibility_rule": SCHEMA_COMPATIBILITY_RULE,
                    "preauthority_history_sha256": SCHEMA_PREAUTHORITY_HISTORY_DIGEST,
                },
            }
            and status.get("transition_ledger") == {
                "authorization_baseline_sha": BOOTSTRAP_BASELINE,
                "sealed_through_sha": LEDGER_ANCHOR,
                "first_parent_chain_sha256": LEDGER_DIGEST,
            }
            and status["bootstrap_exception"] is None
            and status["capability"] == {
                "maturity": "OFFLINE_EVIDENCE_ACCEPTED",
                "legacy_maximum": "OFFLINE_EVIDENCE_ACCEPTED",
            }
            and status["release"] == {"product_owner_approval": None, "release_manifest": None}
            and status["blockers"] == [G0_T02_RECOVERY_BLOCKER]
            and status["next_authorization"] == {"gate": "G0", "task_id": "G0-T03", "state": "not_authorized"}
            and status["governed_documents"] == [
                "AGENTS.md",
                "DEVELOPMENT_WORKFLOW.md",
                "AG_WORK_LOOP.md",
                "DESIGN.md",
                "CURRENT_TASK.md",
                "PROJECT_MEMORY.md",
            ]
        )
    except (KeyError, IndexError, TypeError):
        return False


def _is_g0_t02_final_closed_status(status: dict[str, Any]) -> bool:
    """Match the immutable G0-T02 close record without accepting lookalike descendants."""
    try:
        task = status["active_tasks"][0]
        evidence = status["evidence"]
        return (
            status["project"] == "yaobizuoduo"
            and status["authoritative_main_ref"] == "refs/heads/main"
            and status["current_gate"] == "G0"
            and task == {
                "task_id": "G0-T02",
                "risk": "D2",
                "state": "closed",
                "transition": {"from": "merged_verified", "to": "closed"},
                "candidate_generation": 5,
            }
            and evidence["authorization_baseline_sha"] == "94892d79b8d39ac1726cf657fac0ae76a0e27b37"
            and evidence["implementation_sha"] == "2ec1a50ad513f81cf3637e82501e4e4d74b5bf1f"
            and evidence["candidate"] == {
                "commit_sha": "35b90f87ab42843925065e6d0dafdc25797702e0",
                "local_verification": {"status": "success", "subject": "delivery_head"},
                "ci": {
                    "status": "success",
                    "subject_sha": "35b90f87ab42843925065e6d0dafdc25797702e0",
                    "run_id": "29884205742",
                    "url": "https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/29884205742",
                },
            }
            and evidence["closure"] == {
                "commit_sha": G0_T02_CLOSURE_SHA,
                "ci": {
                    "status": "success",
                    "subject_sha": G0_T02_CLOSURE_SHA,
                    "run_id": G0_T02_CLOSURE_RUN,
                    "url": f"https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/{G0_T02_CLOSURE_RUN}",
                },
            }
            and evidence["merged_main"] == {
                "commit_sha": G0_T02_RECOVERY_MAIN_SHA,
                "ci": {
                    "status": "success",
                    "subject_sha": G0_T02_RECOVERY_MAIN_SHA,
                    "run_id": "29887948168",
                    "url": "https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/29887948168",
                },
            }
            and evidence["finalization"] == {
                "commit_sha": G0_T02_FINALIZATION_SHA,
                "d0_ci": {
                    "status": "success",
                    "subject_sha": G0_T02_FINALIZATION_SHA,
                    "run_id": G0_T02_FINALIZATION_RUN,
                    "url": f"https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/{G0_T02_FINALIZATION_RUN}",
                },
            }
            and status["review"] == {
                "code_security": "approve",
                "architecture": "clear",
                "reviewed_candidate_sha": "35b90f87ab42843925065e6d0dafdc25797702e0",
            }
            and status.get("schema_authority") == {
                "revision": 1,
                "sha256": "192787ae5ad594bf3fce57af75de8bb9db99c83adac93ad1434fc49d63579e5e",
                "migration": {
                    "from_revision": 0,
                    "from_sha256": SCHEMA_BOOTSTRAP_OLD_DIGEST,
                    "to_revision": 1,
                    "to_sha256": "192787ae5ad594bf3fce57af75de8bb9db99c83adac93ad1434fc49d63579e5e",
                    "authorization_sha": SCHEMA_BOOTSTRAP_SUBJECT,
                    "compatibility_rule": SCHEMA_COMPATIBILITY_RULE,
                    "preauthority_history_sha256": SCHEMA_PREAUTHORITY_HISTORY_DIGEST,
                },
            }
            and status.get("transition_ledger") == {
                "authorization_baseline_sha": BOOTSTRAP_BASELINE,
                "sealed_through_sha": LEDGER_ANCHOR,
                "first_parent_chain_sha256": LEDGER_DIGEST,
            }
            and status["bootstrap_exception"] is None
            and status["capability"] == {
                "maturity": "OFFLINE_EVIDENCE_ACCEPTED",
                "legacy_maximum": "OFFLINE_EVIDENCE_ACCEPTED",
            }
            and status["release"] == {"product_owner_approval": None, "release_manifest": None}
            and status["blockers"] == []
            and status["next_authorization"] == {
                "gate": "G0", "task_id": "G0-T03", "state": "not_authorized"
            }
            and status["governed_documents"] == [
                "AGENTS.md", "DEVELOPMENT_WORKFLOW.md", "AG_WORK_LOOP.md", "DESIGN.md",
                "CURRENT_TASK.md", "PROJECT_MEMORY.md",
            ]
        )
    except (KeyError, IndexError, TypeError):
        return False


def _g0_t02_final_close_record_errors(root: Path, schema: dict[str, Any]) -> list[str]:
    """Verify the close record directly consumes the exact successful finalization subject."""
    errors: list[str] = []
    closed, closed_errors = _committed_status_errors(
        root, G0_T02_CLOSED_RECORD_SHA, schema, use_current_schema=True
    )
    finalization, finalization_errors = _committed_status_errors(
        root, G0_T02_FINALIZATION_SHA, schema, use_current_schema=True
    )
    errors.extend(closed_errors)
    errors.extend(finalization_errors)
    if closed is None or not _is_g0_t02_final_closed_status(closed):
        errors.append("$: canonical G0-T02 final-close record identity is invalid")
    ok_closed, closed_parents_text = _git(
        root, "rev-list", "--parents", "-n", "1", G0_T02_CLOSED_RECORD_SHA
    )
    closed_parts = closed_parents_text.split() if ok_closed else []
    if closed_parts != [G0_T02_CLOSED_RECORD_SHA, G0_T02_FINALIZATION_SHA]:
        errors.append("$: canonical G0-T02 close record must directly consume the exact finalization subject")
    if finalization is None or closed is None:
        return errors
    projected = dict(closed)
    projected["active_tasks"] = [dict(closed["active_tasks"][0])]
    projected["active_tasks"][0].update(
        state="merged_verified",
        transition={"from": "accepted_pending_merge", "to": "merged_verified"},
    )
    projected["evidence"] = dict(closed["evidence"])
    projected["evidence"]["finalization"] = {
        "commit_sha": None,
        "d0_ci": {"status": "not_established", "subject_sha": None, "run_id": None, "url": None},
    }
    if not _typed_equal(projected, finalization):
        errors.append("$: canonical G0-T02 finalization subject changed immutable phase evidence")
    ok_finalization, finalization_parents_text = _git(
        root, "rev-list", "--parents", "-n", "1", G0_T02_FINALIZATION_SHA
    )
    if (finalization_parents_text.split() if ok_finalization else []) != [
        G0_T02_FINALIZATION_SHA, G0_T02_RECOVERY_MAIN_SHA
    ]:
        errors.append("$: canonical G0-T02 finalization subject is not rooted at the verified recovery main")
    return errors


def _g0_t02_final_close_repair_parent_errors(
    status: dict[str, Any],
    parent: dict[str, Any],
    parent_sha: str | None,
    root: Path | None,
    child_sha: str | None,
) -> list[str] | None:
    """Allow only a status-identical, single-parent repair line rooted at the failed close merge."""
    if not (_is_g0_t02_final_closed_status(status) and _is_g0_t02_final_closed_status(parent)):
        return None
    if root is None or parent_sha is None or child_sha is None:
        return ["$: G0-T02 final-close repair requires repository-bound lineage"]
    ok, lineage_text = _git(
        root, "rev-list", "--first-parent", f"{G0_T02_FINAL_CLOSE_MERGE_SHA}..{child_sha}"
    )
    lineage = lineage_text.splitlines() if ok else []
    errors: list[str] = []
    if not lineage or lineage[0] != child_sha:
        errors.append("$: G0-T02 final-close repair is not rooted at the exact failed close merge")
        return errors
    for index, repair_sha in enumerate(lineage):
        ok_parents, parents_text = _git(root, "rev-list", "--parents", "-n", "1", repair_sha)
        parts = parents_text.split() if ok_parents else []
        expected_parent = lineage[index + 1] if index + 1 < len(lineage) else G0_T02_FINAL_CLOSE_MERGE_SHA
        if (
            parts != [repair_sha, expected_parent]
            or not _typed_equal(_status_at(root, repair_sha), status)
        ):
            errors.append("$: G0-T02 final-close repair must be a status-identical single-parent lineage")
            break
    return errors


def _canonical_g0_t02_final_close_bridge(
    status: dict[str, Any],
    root: Path,
    head: str,
    schema: dict[str, Any],
    *,
    require_canonical_main: bool,
) -> tuple[str | None, list[str]]:
    """Recognize only the exact final-close merge or its exact repair merge."""
    if not _is_g0_t02_final_closed_status(status):
        return None, []
    ok, parents_text = _git(root, "rev-list", "--parents", "-n", "1", head)
    parts = parents_text.split() if ok else []
    if len(parts) != 3:
        return None, []
    first_parent, governed_parent = parts[1], parts[2]
    errors = _g0_t02_final_close_record_errors(root, schema)
    ok_origin, origin_url = _git(root, "remote", "get-url", "origin")
    if not ok_origin or _github_repository_identity(origin_url) != LEDGER_REPOSITORY:
        errors.append("$: canonical G0-T02 final-close bridge requires the canonical repository")
    if require_canonical_main:
        ok_main, main_sha = _git(root, "rev-parse", "--verify", status["authoritative_main_ref"])
        ok_remote, remote_sha = _git(root, "rev-parse", "--verify", "refs/remotes/origin/main")
        if not ok_main or not ok_remote or main_sha != remote_sha or main_sha != head:
            errors.append("$: canonical G0-T02 final-close bridge requires exact local/fetched main")

    if head == G0_T02_FINAL_CLOSE_MERGE_SHA:
        if (first_parent, governed_parent) != (
            G0_T02_RECOVERY_MAIN_SHA, G0_T02_CLOSED_RECORD_SHA
        ):
            errors.append("$: canonical G0-T02 final-close bridge has substituted or swapped parents")
    else:
        if first_parent != G0_T02_FINAL_CLOSE_MERGE_SHA:
            errors.append("$: G0-T02 final-close recovery merge must use the exact failed close as first parent")
        ok_lineage, lineage_text = _git(
            root,
            "rev-list",
            "--first-parent",
            f"{G0_T02_FINAL_CLOSE_MERGE_SHA}..{governed_parent}",
        )
        lineage = lineage_text.splitlines() if ok_lineage else []
        if not lineage or lineage[0] != governed_parent:
            errors.append("$: G0-T02 final-close recovery second parent is not a strict repair lineage")
        for index, repair_sha in enumerate(lineage):
            ok_parents, repair_parents_text = _git(
                root, "rev-list", "--parents", "-n", "1", repair_sha
            )
            repair_parts = repair_parents_text.split() if ok_parents else []
            expected_parent = (
                lineage[index + 1]
                if index + 1 < len(lineage)
                else G0_T02_FINAL_CLOSE_MERGE_SHA
            )
            if (
                repair_parts != [repair_sha, expected_parent]
                or not _typed_equal(_status_at(root, repair_sha), status)
            ):
                errors.append("$: G0-T02 final-close recovery requires a status-identical single-parent repair lineage")
                break

    governed_status, governed_errors = _committed_status_errors(
        root, governed_parent, schema, use_current_schema=True
    )
    errors.extend(governed_errors)
    if governed_status is None or not _typed_equal(governed_status, status):
        errors.append("$: canonical G0-T02 final-close bridge status must equal its second parent")
    ok_head_tree, head_tree = _git(root, "rev-parse", f"{head}^{{tree}}")
    ok_parent_tree, parent_tree = _git(root, "rev-parse", f"{governed_parent}^{{tree}}")
    if not ok_head_tree or not ok_parent_tree or head_tree != parent_tree:
        errors.append("$: canonical G0-T02 final-close bridge tree must equal its second parent")
    if errors:
        return None, errors
    return governed_parent, []


def _canonical_g0_t03_merge_bridge(
    status: dict[str, Any],
    root: Path,
    head: str,
    *,
    require_canonical_main: bool = True,
) -> tuple[str | None, list[str]]:
    """Validate only the published G0-T03 generation-3 merge topology."""
    if not _is_g0_t03_accepted_status(status):
        return None, []
    errors: list[str] = []
    if head != G0_T03_FAILED_MAIN_SHA:
        errors.append("$: canonical G0-T03 merge bridge subject is not the exact published merge")
    ok_origin, origin_url = _git(root, "remote", "get-url", "origin")
    if not ok_origin or _github_repository_identity(origin_url) != LEDGER_REPOSITORY:
        errors.append("$: canonical G0-T03 merge bridge requires the canonical repository")
    if require_canonical_main:
        ok_main, main_sha = _git(root, "rev-parse", "--verify", status["authoritative_main_ref"])
        ok_remote, remote_sha = _git(root, "rev-parse", "--verify", "refs/remotes/origin/main")
        if not ok_main or not ok_remote or main_sha != remote_sha or main_sha != head:
            errors.append("$: canonical G0-T03 merge bridge requires exact local/fetched main")

    ok_parents, parents_text = _git(root, "rev-list", "--parents", "-n", "1", head)
    parts = parents_text.split() if ok_parents else []
    if parts != [
        G0_T03_FAILED_MAIN_SHA,
        "09bfbd23d898198fe694a3a94f77663759dd89d8",
        G0_T03_ACCEPTED_RECORD_SHA,
    ]:
        errors.append("$: canonical G0-T03 merge bridge has substituted or swapped parents")
    ok_head_tree, head_tree = _git(root, "rev-parse", f"{head}^{{tree}}")
    ok_record_tree, record_tree = _git(root, "rev-parse", f"{G0_T03_ACCEPTED_RECORD_SHA}^{{tree}}")
    if not ok_head_tree or not ok_record_tree or head_tree != record_tree:
        errors.append("$: canonical G0-T03 merge bridge tree must equal the accepted record")
    accepted_status = _status_at(root, G0_T03_ACCEPTED_RECORD_SHA)
    merged_status = _status_at(root, head)
    if not _typed_equal(accepted_status, status) or not _typed_equal(merged_status, status):
        errors.append("$: canonical G0-T03 merge bridge status must equal the exact accepted record")

    ok_record_parents, record_parents_text = _git(
        root, "rev-list", "--parents", "-n", "1", G0_T03_ACCEPTED_RECORD_SHA
    )
    if (record_parents_text.split() if ok_record_parents else []) != [
        G0_T03_ACCEPTED_RECORD_SHA,
        G0_T03_CANDIDATE_SHA,
    ]:
        errors.append("$: canonical G0-T03 accepted record must directly close the exact candidate")
    candidate_status = _status_at(root, G0_T03_CANDIDATE_SHA)
    if not _subject_status_matches(status, candidate_status, "awaiting_review"):
        errors.append("$: canonical G0-T03 candidate status identity is invalid")
    if not _is_first_parent_ancestor(root, G0_T03_AUTHORIZATION_SHA, G0_T03_CANDIDATE_SHA):
        errors.append("$: canonical G0-T03 candidate is not rooted in the exact generation-2 authorization")

    ok_auth, auth_text = _git(root, "rev-list", "--parents", "-n", "1", G0_T03_AUTHORIZATION_SHA)
    if (auth_text.split() if ok_auth else []) != [
        G0_T03_AUTHORIZATION_SHA,
        "09bfbd23d898198fe694a3a94f77663759dd89d8",
        G0_T03_BLOCKED_SHA,
    ]:
        errors.append("$: canonical G0-T03 generation-2 authorization has substituted or swapped parents")
    auth_status = _status_at(root, G0_T03_AUTHORIZATION_SHA)
    blocked_status = _status_at(root, G0_T03_BLOCKED_SHA)
    try:
        auth_task = auth_status["active_tasks"][0] if type(auth_status) is dict else None
        blocked_task = blocked_status["active_tasks"][0] if type(blocked_status) is dict else None
        authorization_exact = (
            auth_task == {
                "task_id": "G0-T03",
                "risk": "D2",
                "state": "authorized",
                "transition": {"from": "closed", "to": "authorized"},
                "candidate_generation": 2,
            }
            and auth_status["evidence"]["authorization_baseline_sha"]
            == "09bfbd23d898198fe694a3a94f77663759dd89d8"
            and blocked_task == {
                "task_id": "G0-T03",
                "risk": "D2",
                "state": "blocked",
                "transition": {"from": "in_progress", "to": "blocked"},
                "candidate_generation": 1,
            }
            and blocked_status["evidence"]["authorization_baseline_sha"]
            == "09bfbd23d898198fe694a3a94f77663759dd89d8"
            and type(blocked_status["blockers"]) is list
            and bool(blocked_status["blockers"])
        )
    except (KeyError, IndexError, TypeError):
        authorization_exact = False
    if not authorization_exact:
        errors.append("$: canonical G0-T03 authorization or terminal blocked record is inexact")
    for ref in (
        "refs/heads/codex/g0-t03-main-protection",
        "refs/remotes/origin/codex/g0-t03-main-protection",
    ):
        ok_ref, ref_sha = _git(root, "rev-parse", "--verify", ref)
        if ok_ref and ref_sha != G0_T03_BLOCKED_SHA:
            errors.append("$: canonical G0-T03 terminal blocked ref moved")
    if errors:
        return None, errors
    return G0_T03_ACCEPTED_RECORD_SHA, []


def _canonical_g0_t03_recovery_merge_bridge(
    status: dict[str, Any],
    root: Path,
    head: str,
    *,
    require_canonical_main: bool = True,
) -> tuple[str | None, list[str]]:
    """Validate only the exact PR #7 recovery merge before generic merge logic."""
    if not _is_g0_t03_post_merge_recovery_status(status):
        return None, []
    errors: list[str] = []
    if head != G0_T03_RECOVERY_MERGE_SHA:
        errors.append("$: canonical G0-T03 recovery merge subject is not the exact published merge")
    ok_origin, origin_url = _git(root, "remote", "get-url", "origin")
    if not ok_origin or _github_repository_identity(origin_url) != LEDGER_REPOSITORY:
        errors.append("$: canonical G0-T03 recovery merge requires the canonical repository")
    if require_canonical_main:
        ok_main, main_sha = _git(root, "rev-parse", "--verify", status["authoritative_main_ref"])
        ok_remote, remote_sha = _git(root, "rev-parse", "--verify", "refs/remotes/origin/main")
        if not ok_main or not ok_remote or main_sha != remote_sha or main_sha != head:
            errors.append("$: canonical G0-T03 recovery merge requires exact local/fetched main")

    ok_parents, parents_text = _git(root, "rev-list", "--parents", "-n", "1", head)
    if (parents_text.split() if ok_parents else []) != [
        G0_T03_RECOVERY_MERGE_SHA,
        G0_T03_FAILED_MAIN_SHA,
        G0_T03_RECOVERY_ACCEPTED_RECORD_SHA,
    ]:
        errors.append("$: canonical G0-T03 recovery merge has substituted or swapped parents")
    ok_head_tree, head_tree = _git(root, "rev-parse", f"{head}^{{tree}}")
    ok_record_tree, record_tree = _git(
        root, "rev-parse", f"{G0_T03_RECOVERY_ACCEPTED_RECORD_SHA}^{{tree}}"
    )
    if not ok_head_tree or not ok_record_tree or head_tree != record_tree:
        errors.append("$: canonical G0-T03 recovery merge tree must equal its accepted record")
    if (
        not _typed_equal(_status_at(root, head), status)
        or not _typed_equal(_status_at(root, G0_T03_RECOVERY_ACCEPTED_RECORD_SHA), status)
    ):
        errors.append("$: canonical G0-T03 recovery merge status must equal the exact accepted recovery record")

    ok_record_parents, record_parents_text = _git(
        root,
        "rev-list",
        "--parents",
        "-n",
        "1",
        G0_T03_RECOVERY_ACCEPTED_RECORD_SHA,
    )
    if (record_parents_text.split() if ok_record_parents else []) != [
        G0_T03_RECOVERY_ACCEPTED_RECORD_SHA,
        G0_T03_RECOVERY_CANDIDATE_SHA,
    ]:
        errors.append("$: canonical G0-T03 recovery accepted record must directly close the exact recovery candidate")
    if not _typed_equal(_status_at(root, G0_T03_RECOVERY_CANDIDATE_SHA), status):
        errors.append("$: canonical G0-T03 recovery candidate status identity is invalid")
    ok_memory, memory_text = _git(
        root,
        "show",
        f"{G0_T03_RECOVERY_ACCEPTED_RECORD_SHA}:PROJECT_MEMORY.md",
    )
    required_review = (
        f"accepted bounded G0-T03 merge-recovery candidate `{G0_T03_RECOVERY_CANDIDATE_SHA}`",
        f"exact-head run `{G0_T03_RECOVERY_CANDIDATE_RUN}` succeeded",
        "code/security returned `APPROVE`",
        "architecture/route returned `CLEAR`",
    )
    if not ok_memory or not all(item in memory_text for item in required_review):
        errors.append("$: canonical G0-T03 recovery acceptance does not bind exact candidate, CI and dual review")

    projected = json.loads(json.dumps(status))
    projected["active_tasks"][0]["transition"] = {
        "from": "awaiting_review",
        "to": "accepted_pending_merge",
    }
    projected["blockers"] = []
    governed, prior_errors = _canonical_g0_t03_merge_bridge(
        projected,
        root,
        G0_T03_FAILED_MAIN_SHA,
        require_canonical_main=False,
    )
    errors.extend(prior_errors)
    if governed != G0_T03_ACCEPTED_RECORD_SHA:
        errors.append("$: canonical G0-T03 recovery merge is not rooted in the exact prior failed merge")
    evidence_path = "evidence/g0-t03/main-protection-generation2.json"
    evidence_blobs: list[str] = []
    for sha in (
        G0_T03_ACCEPTED_RECORD_SHA,
        G0_T03_RECOVERY_CANDIDATE_SHA,
        G0_T03_RECOVERY_ACCEPTED_RECORD_SHA,
        head,
    ):
        ok_blob, blob = _git(root, "rev-parse", f"{sha}:{evidence_path}")
        if not ok_blob:
            errors.append("$: canonical G0-T03 ruleset evidence is missing from recovery topology")
            break
        evidence_blobs.append(blob)
    if evidence_blobs and len(set(evidence_blobs)) != 1:
        errors.append("$: canonical G0-T03 ruleset evidence changed across recovery topology")
    if errors:
        return None, errors
    return G0_T03_RECOVERY_ACCEPTED_RECORD_SHA, []


def _g0_t03_recovery_closure_receipt_errors(
    root: Path, accepted_record: str, candidate: str
) -> list[str]:
    ok, text = _git(
        root,
        "show",
        f"{accepted_record}:{G0_T03_RECOVERY_CLOSURE_RECEIPT_PATH}",
    )
    if not ok:
        return ["$: G0-T03 recovery closure acceptance receipt is missing"]
    try:
        receipt = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return ["$: G0-T03 recovery closure acceptance receipt is not canonical JSON"]
    exact_keys = {
        "schema_version",
        "project",
        "task_id",
        "candidate_generation",
        "recovery_generation",
        "prior_rejected_candidate_sha",
        "prior_rejected_run_id",
        "prior_review",
        "candidate",
        "review",
        "ruleset",
        "payload_sha256",
    }
    errors: list[str] = []
    if type(receipt) is not dict or set(receipt) != exact_keys:
        return ["$: G0-T03 recovery closure acceptance receipt has an inexact field set"]
    nested_keys = {
        "prior_review": {"code_security", "architecture"},
        "candidate": {"commit_sha", "ci"},
        "review": {"code_security", "architecture"},
        "ruleset": {"id", "evidence_sha256"},
    }
    for field, keys in nested_keys.items():
        value = receipt.get(field)
        if type(value) is not dict or set(value) != keys:
            errors.append(f"$: G0-T03 recovery closure acceptance receipt has an inexact {field} field set")
    expected = {
        "schema_version": G0_T03_RECOVERY_CLOSURE_RECEIPT_VERSION,
        "project": "yaobizuoduo",
        "task_id": "G0-T03",
        "candidate_generation": 3,
        "recovery_generation": 2,
        "prior_rejected_candidate_sha": "05597ef837031bb6a4aeb6eefb21aa4cecd7ff30",
        "prior_rejected_run_id": "29900351726",
        "prior_review": {
            "code_security": "request_changes",
            "architecture": "block",
        },
        "candidate": {
            "commit_sha": candidate,
            "ci": {
                "repository": "weizhenhaihaha-arch/yaobizuoduo",
                "event": "pull_request",
                "subject_sha": candidate,
                "run_id": receipt.get("candidate", {}).get("ci", {}).get("run_id")
                if type(receipt.get("candidate")) is dict
                and type(receipt["candidate"].get("ci")) is dict
                else None,
                "url": receipt.get("candidate", {}).get("ci", {}).get("url")
                if type(receipt.get("candidate")) is dict
                and type(receipt["candidate"].get("ci")) is dict
                else None,
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
    payload = {key: value for key, value in receipt.items() if key != "payload_sha256"}
    for key, value in expected.items():
        if not _typed_equal(payload.get(key), value):
            errors.append(f"$: G0-T03 recovery closure acceptance receipt has inexact {key}")
    ci = receipt.get("candidate", {}).get("ci") if type(receipt.get("candidate")) is dict else None
    if type(ci) is not dict or set(ci) != {
        "repository", "event", "subject_sha", "run_id", "url", "check", "status", "conclusion"
    }:
        errors.append("$: G0-T03 recovery closure CI receipt has an inexact field set")
    else:
        run_id = ci["run_id"]
        if type(run_id) is not str or re.fullmatch(r"[1-9][0-9]*", run_id) is None:
            errors.append("$: G0-T03 recovery closure run ID must be a positive decimal string")
        expected_url = f"https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/{run_id}"
        if ci["url"] != expected_url:
            errors.append("$: G0-T03 recovery closure CI URL does not bind its run ID")
    if receipt.get("payload_sha256") != _payload_digest(receipt):
        errors.append("$: G0-T03 recovery closure acceptance receipt digest mismatch")
    ok_candidate_receipt, _ = _git(
        root,
        "cat-file",
        "-e",
        f"{candidate}:{G0_T03_RECOVERY_CLOSURE_RECEIPT_PATH}",
    )
    if ok_candidate_receipt:
        errors.append("$: G0-T03 recovery closure receipt must be created only by the later acceptance record")
    return errors


def _canonical_g0_t03_recovery_closure_bridge(
    status: dict[str, Any],
    root: Path,
    head: str,
    *,
    require_canonical_main: bool = True,
) -> tuple[str | None, list[str]]:
    """Validate a future non-self-referential merge that closes this exact recovery."""
    if not _is_g0_t03_recovery_merge_recovery_status(status):
        return None, []
    errors: list[str] = []
    ok_parents, parents_text = _git(root, "rev-list", "--parents", "-n", "1", head)
    parts = parents_text.split() if ok_parents else []
    if len(parts) != 3:
        return None, []
    first_parent, accepted_record = parts[1], parts[2]
    if first_parent != G0_T03_RECOVERY_MERGE_SHA:
        errors.append("$: G0-T03 recovery closure first parent is not the exact failed recovery merge")
    ok_origin, origin_url = _git(root, "remote", "get-url", "origin")
    if not ok_origin or _github_repository_identity(origin_url) != LEDGER_REPOSITORY:
        errors.append("$: G0-T03 recovery closure requires the canonical repository")
    if require_canonical_main:
        ok_main, main_sha = _git(root, "rev-parse", "--verify", status["authoritative_main_ref"])
        ok_remote, remote_sha = _git(root, "rev-parse", "--verify", "refs/remotes/origin/main")
        if not ok_main or not ok_remote or main_sha != remote_sha or main_sha != head:
            errors.append("$: G0-T03 recovery closure requires exact local/fetched main")
    ok_record_parents, record_parents_text = _git(
        root, "rev-list", "--parents", "-n", "1", accepted_record
    )
    record_parts = record_parents_text.split() if ok_record_parents else []
    candidate = record_parts[1] if len(record_parts) == 2 else ""
    if len(record_parts) != 2 or candidate == "05597ef837031bb6a4aeb6eefb21aa4cecd7ff30":
        errors.append("$: G0-T03 recovery closure second parent must directly accept a new repair candidate")
    if not _is_first_parent_ancestor(root, G0_T03_RECOVERY_MERGE_SHA, candidate):
        errors.append("$: G0-T03 recovery closure candidate is not rooted at the exact failed recovery merge")
    ok_lineage, lineage_text = _git(
        root, "rev-list", "--first-parent", f"{G0_T03_RECOVERY_MERGE_SHA}..{candidate}"
    )
    lineage = lineage_text.splitlines() if ok_lineage else []
    for index, repair_sha in enumerate(lineage):
        ok_repair_parents, repair_parents_text = _git(
            root, "rev-list", "--parents", "-n", "1", repair_sha
        )
        expected_parent = (
            lineage[index + 1] if index + 1 < len(lineage) else G0_T03_RECOVERY_MERGE_SHA
        )
        if (
            (repair_parents_text.split() if ok_repair_parents else []) != [repair_sha, expected_parent]
            or not _typed_equal(_status_at(root, repair_sha), status)
        ):
            errors.append("$: G0-T03 recovery closure requires a status-identical single-parent repair lineage")
            break
    if (
        not _typed_equal(_status_at(root, candidate), status)
        or not _typed_equal(_status_at(root, accepted_record), status)
        or not _typed_equal(_status_at(root, head), status)
    ):
        errors.append("$: G0-T03 recovery closure status must equal candidate, acceptance and merge subjects")
    ok_head_tree, head_tree = _git(root, "rev-parse", f"{head}^{{tree}}")
    ok_record_tree, record_tree = _git(root, "rev-parse", f"{accepted_record}^{{tree}}")
    if not ok_head_tree or not ok_record_tree or head_tree != record_tree:
        errors.append("$: G0-T03 recovery closure merge tree must equal its accepted record")
    errors.extend(_g0_t03_recovery_closure_receipt_errors(root, accepted_record, candidate))
    evidence_path = "evidence/g0-t03/main-protection-generation2.json"
    evidence_blobs: list[str] = []
    for sha in (G0_T03_RECOVERY_MERGE_SHA, candidate, accepted_record, head):
        ok_blob, blob = _git(root, "rev-parse", f"{sha}:{evidence_path}")
        if not ok_blob:
            errors.append("$: G0-T03 ruleset evidence is missing from recovery closure topology")
            break
        evidence_blobs.append(blob)
    if evidence_blobs and len(set(evidence_blobs)) != 1:
        errors.append("$: G0-T03 ruleset evidence changed across recovery closure topology")
    if errors:
        return None, errors
    return accepted_record, []


def _g0_t03_recovery_closure_ancestor(root: Path, main_sha: str) -> str | None:
    """Find the exact closure bridge beneath a single-parent finalization/close tail."""
    ok_lineage, lineage_text = _git(root, "rev-list", "--first-parent", main_sha)
    if not ok_lineage:
        return None
    for sha in lineage_text.splitlines():
        status = _status_at(root, sha)
        if type(status) is not dict:
            return None
        if _is_g0_t03_recovery_merge_recovery_status(status):
            governed, errors = _canonical_g0_t03_recovery_closure_bridge(
                status,
                root,
                sha,
                require_canonical_main=False,
            )
            return sha if governed is not None and not errors else None
        task = status.get("active_tasks", [{}])[0]
        if (
            type(task) is not dict
            or task.get("task_id") != "G0-T03"
            or task.get("state") not in {"merged_verified", "closed"}
            or status.get("blockers") != []
        ):
            return None
        ok_parents, parents_text = _git(root, "rev-list", "--parents", "-n", "1", sha)
        if len(parents_text.split() if ok_parents else []) != 2:
            return None
    return None


def _is_g0_t03_final_closed_status(status: dict[str, Any]) -> bool:
    try:
        projected = json.loads(json.dumps(status))
        task = status["active_tasks"][0]
        evidence = status["evidence"]
        projected["active_tasks"][0].update(
            state="accepted_pending_merge",
            transition={"from": "accepted_pending_merge", "to": "accepted_pending_merge"},
        )
        projected["evidence"]["closure"] = {
            "commit_sha": None,
            "ci": {"status": "not_established", "subject_sha": None, "run_id": None, "url": None},
        }
        projected["evidence"]["merged_main"] = {
            "commit_sha": None,
            "ci": {"status": "not_established", "subject_sha": None, "run_id": None, "url": None},
        }
        projected["evidence"]["finalization"] = {
            "commit_sha": None,
            "d0_ci": {"status": "not_established", "subject_sha": None, "run_id": None, "url": None},
        }
        projected["blockers"] = [G0_T03_RECOVERY_BLOCKER, G0_T03_RECOVERY_MERGE_BLOCKER]
        return (
            _is_g0_t03_recovery_merge_recovery_status(projected)
            and task == {
                "task_id": "G0-T03",
                "risk": "D2",
                "state": "closed",
                "transition": {"from": "merged_verified", "to": "closed"},
                "candidate_generation": 3,
            }
            and evidence["closure"] == {
                "commit_sha": "3263cf207cecac1e3fb019df2fbd6c2a6435d5bd",
                "ci": {
                    "status": "success",
                    "subject_sha": "3263cf207cecac1e3fb019df2fbd6c2a6435d5bd",
                    "run_id": "29905690883",
                    "url": "https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/29905690883",
                },
            }
            and evidence["merged_main"] == {
                "commit_sha": "a98dada059c91dc70714119f333d0d03ab1cb9f1",
                "ci": {
                    "status": "success",
                    "subject_sha": "a98dada059c91dc70714119f333d0d03ab1cb9f1",
                    "run_id": "29906115287",
                    "url": "https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/29906115287",
                },
            }
            and evidence["finalization"] == {
                "commit_sha": G0_T03_FINALIZATION_SHA,
                "d0_ci": {
                    "status": "success",
                    "subject_sha": G0_T03_FINALIZATION_SHA,
                    "run_id": G0_T03_FINALIZATION_RUN,
                    "url": f"https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/{G0_T03_FINALIZATION_RUN}",
                },
            }
            and status["blockers"] == []
        )
    except (KeyError, IndexError, TypeError):
        return False


def _is_g0_t03_final_close_recovery_status(status: dict[str, Any]) -> bool:
    try:
        projected = json.loads(json.dumps(status))
        if status["active_tasks"][0]["transition"] != {"from": "closed", "to": "closed"}:
            return False
        projected["active_tasks"][0]["transition"] = {
            "from": "merged_verified",
            "to": "closed",
        }
        projected["blockers"] = []
        return (
            _is_g0_t03_final_closed_status(projected)
            and status["blockers"] == [G0_T03_FINAL_CLOSE_BLOCKER]
        )
    except (KeyError, TypeError):
        return False


def _is_g0_t03_status_reconciled(status: dict[str, Any]) -> bool:
    try:
        projected = json.loads(json.dumps(status))
        projected["blockers"] = [G0_T03_FINAL_CLOSE_BLOCKER]
        return (
            _is_g0_t03_final_close_recovery_status(projected)
            and status["active_tasks"][0] == {
                "task_id": "G0-T03",
                "risk": "D2",
                "state": "closed",
                "transition": {"from": "closed", "to": "closed"},
                "candidate_generation": 3,
            }
            and status["blockers"] == []
            and status["capability"] == {
                "maturity": "OFFLINE_EVIDENCE_ACCEPTED",
                "legacy_maximum": "OFFLINE_EVIDENCE_ACCEPTED",
            }
            and status["next_authorization"] == {
                "gate": "G0",
                "task_id": "G0-T04",
                "state": "not_authorized",
            }
        )
    except (KeyError, IndexError, TypeError):
        return False


def _g0_t03_status_reconciliation_evidence_errors(
    root: Path, subject_sha: str
) -> list[str]:
    errors: list[str] = []
    ok, text = _git(
        root, "show", f"{subject_sha}:{G0_T03_STATUS_RECONCILIATION_PATH}"
    )
    if not ok:
        return ["$: G0-T03 status reconciliation evidence is missing"]
    try:
        evidence = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except (json.JSONDecodeError, TypeError, ValueError):
        return ["$: G0-T03 status reconciliation evidence is not canonical JSON"]
    expected = {
        "schema_version": G0_T03_STATUS_RECONCILIATION_VERSION,
        "project": "yaobizuoduo",
        "task_id": "G0-T03",
        "candidate_generation": 3,
        "maturity": "OFFLINE_EVIDENCE_ACCEPTED",
        "next_authorization": {
            "gate": "G0",
            "task_id": "G0-T04",
            "state": "not_authorized",
        },
        "historical_failure": {
            "repository": "weizhenhaihaha-arch/yaobizuoduo",
            "event": "push",
            "ref": "refs/heads/main",
            "subject_sha": G0_T03_FINAL_CLOSE_MERGE_SHA,
            "run_id": G0_T03_FINAL_CLOSE_MERGE_RUN,
            "url": f"https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/{G0_T03_FINAL_CLOSE_MERGE_RUN}",
            "status": "completed",
            "conclusion": "failure",
            "retention": "immutable_history",
        },
        "recovered_main": {
            "commit_sha": G0_T03_RECOVERED_MAIN_SHA,
            "ordered_parents": [
                G0_T03_FINAL_CLOSE_MERGE_SHA,
                "ddd69c2c8174837e12d186fd12252ccb6f13b24e",
            ],
            "tree_sha": "2855cb543087a9dbee1f2c1fad5400e3a79b3573",
            "push_run_id": G0_T03_RECOVERED_MAIN_RUN,
            "push_run_url": f"https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/{G0_T03_RECOVERED_MAIN_RUN}",
            "push_conclusion": "success",
            "pull_request": 10,
            "code_security": "approve",
            "architecture": "clear",
        },
        "planning_recovery_main": {
            "commit_sha": G0_T03_STATUS_RECONCILIATION_BASE_SHA,
            "ordered_parents": [
                G0_T03_STATUS_RECONCILIATION_FIRST_PARENT,
                G0_T03_STATUS_RECONCILIATION_SECOND_PARENT,
            ],
            "tree_sha": G0_T03_STATUS_RECONCILIATION_TREE,
            "push_run_id": G0_T03_STATUS_RECONCILIATION_BASE_RUN,
            "push_run_url": f"https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/{G0_T03_STATUS_RECONCILIATION_BASE_RUN}",
            "push_conclusion": "success",
            "recovery_pull_request": 12,
            "recovery_head_sha": G0_T03_STATUS_RECONCILIATION_SECOND_PARENT,
            "recovery_pr_run_id": G0_T03_STATUS_RECONCILIATION_PR_RUN,
            "recovery_pr_conclusion": "success",
        },
        "ruleset": {
            "id": G0_T03_RULESET_ID,
            "readback_sha256": G0_T03_RULESET_EVIDENCE_DIGEST,
        },
        "blocker_reconciliation": {
            "removed_from_current": [G0_T03_FINAL_CLOSE_BLOCKER],
            "current_blockers": [],
            "reason": "exact_recovered_main_and_planning_recovery_push_runs_succeeded",
        },
    }
    if type(evidence) is not dict or set(evidence) != set(expected) | {"payload_sha256"}:
        return ["$: G0-T03 status reconciliation evidence has an inexact field set"]
    for key, value in expected.items():
        if not _typed_equal(evidence.get(key), value):
            errors.append(f"$: G0-T03 status reconciliation evidence drift: {key}")
    if evidence.get("payload_sha256") != _payload_digest(evidence):
        errors.append("$: G0-T03 status reconciliation evidence digest mismatch")

    ok_base, base_parts_text = _git(
        root, "rev-list", "--parents", "-n", "1", G0_T03_STATUS_RECONCILIATION_BASE_SHA
    )
    if (base_parts_text.split() if ok_base else []) != [
        G0_T03_STATUS_RECONCILIATION_BASE_SHA,
        G0_T03_STATUS_RECONCILIATION_FIRST_PARENT,
        G0_T03_STATUS_RECONCILIATION_SECOND_PARENT,
    ]:
        errors.append("$: G0-T03 status reconciliation base has substituted parents")
    ok_tree, tree_sha = _git(
        root, "rev-parse", f"{G0_T03_STATUS_RECONCILIATION_BASE_SHA}^{{tree}}"
    )
    if not ok_tree or tree_sha != G0_T03_STATUS_RECONCILIATION_TREE:
        errors.append("$: G0-T03 status reconciliation base has substituted tree")
    recovered_status = _status_at(root, G0_T03_RECOVERED_MAIN_SHA)
    recovered_schema = _schema_at(root, G0_T03_RECOVERED_MAIN_SHA)
    if type(recovered_status) is not dict or type(recovered_schema) is not dict:
        errors.append("$: G0-T03 recovered-main proof is unreadable")
    else:
        governed, recovery_errors = _canonical_g0_t03_final_close_bridge(
            recovered_status,
            root,
            G0_T03_RECOVERED_MAIN_SHA,
            recovered_schema,
            require_canonical_main=False,
        )
        errors.extend(recovery_errors)
        if governed != "ddd69c2c8174837e12d186fd12252ccb6f13b24e":
            errors.append("$: G0-T03 status reconciliation is not rooted at exact R-B-A recovery")
    ruleset_path = "evidence/g0-t03/main-protection-generation2.json"
    ok_ruleset, ruleset_blob = _git(root, "show", f"{subject_sha}:{ruleset_path}")
    ok_base_ruleset, base_ruleset_blob = _git(
        root, "show", f"{G0_T03_STATUS_RECONCILIATION_BASE_SHA}:{ruleset_path}"
    )
    try:
        ruleset_evidence = json.loads(ruleset_blob) if ok_ruleset else None
    except json.JSONDecodeError:
        ruleset_evidence = None
    if (
        not ok_ruleset
        or not ok_base_ruleset
        or ruleset_blob != base_ruleset_blob
        or type(ruleset_evidence) is not dict
        or ruleset_evidence.get("after_sha256") != G0_T03_RULESET_EVIDENCE_DIGEST
        or ruleset_evidence.get("readback", {}).get("id") != G0_T03_RULESET_ID
    ):
        errors.append("$: G0-T03 status reconciliation ruleset evidence changed")
    return errors


def _g0_t03_status_reconciliation_changed_path_errors(
    root: Path, subject_sha: str
) -> list[str]:
    changed = _g0_t03_commit_changed_paths(
        root, G0_T03_STATUS_RECONCILIATION_BASE_SHA, subject_sha
    )
    allowed = {
        "PROJECT_STATUS.yaml",
        "scripts/validate_project_status.py",
        "tests/test_g0_project_status.py",
        "CURRENT_TASK.md",
        "PROJECT_MEMORY.md",
        G0_T03_STATUS_RECONCILIATION_PATH,
    }
    required = {
        "PROJECT_STATUS.yaml",
        "scripts/validate_project_status.py",
        "tests/test_g0_project_status.py",
        G0_T03_STATUS_RECONCILIATION_PATH,
    }
    if changed is None or not required.issubset(changed) or not changed.issubset(allowed):
        return ["$: G0-T03 status reconciliation changed paths violate the exact allowlist"]
    ok_prior, _ = _git(
        root,
        "cat-file",
        "-e",
        f"{G0_T03_STATUS_RECONCILIATION_BASE_SHA}:{G0_T03_STATUS_RECONCILIATION_PATH}",
    )
    return ["$: G0-T03 status reconciliation evidence must be newly introduced"] if ok_prior else []


def _g0_t03_status_reconciliation_parent_errors(
    status: dict[str, Any],
    parent: dict[str, Any],
    parent_sha: str | None,
    root: Path | None,
    child_sha: str | None,
    *,
    require_current_main: bool = True,
) -> list[str] | None:
    if not _is_g0_t03_status_reconciled(status):
        return None
    if root is None or parent_sha is None or child_sha is None:
        return ["$: G0-T03 status reconciliation requires repository-bound proof"]
    projected = json.loads(json.dumps(status))
    projected["blockers"] = [G0_T03_FINAL_CLOSE_BLOCKER]
    errors: list[str] = []
    if parent_sha != G0_T03_STATUS_RECONCILIATION_BASE_SHA or not _typed_equal(projected, parent):
        errors.append("$: G0-T03 status reconciliation may only clear the exact recovered blocker from authoritative base")
    ok_parents, parents_text = _git(root, "rev-list", "--parents", "-n", "1", child_sha)
    if (parents_text.split() if ok_parents else []) != [
        child_sha,
        G0_T03_STATUS_RECONCILIATION_BASE_SHA,
    ]:
        errors.append("$: G0-T03 status reconciliation must directly follow exact authoritative base")
    if require_current_main:
        ok_main, main_sha = _git(root, "rev-parse", "--verify", status["authoritative_main_ref"])
        ok_remote, remote_sha = _git(root, "rev-parse", "--verify", "refs/remotes/origin/main")
        main_matches = (
            ok_main
            and ok_remote
            and main_sha == remote_sha == G0_T03_STATUS_RECONCILIATION_BASE_SHA
        )
        if ok_main and ok_remote and main_sha == remote_sha and not main_matches:
            main_status = _status_at(root, main_sha)
            if type(main_status) is dict:
                governed, bridge_errors = _canonical_g0_t03_status_reconciliation_bridge(
                    main_status,
                    root,
                    main_sha,
                    require_canonical_main=False,
                )
                main_matches = governed is not None and not bridge_errors
        if not main_matches:
            errors.append("$: G0-T03 status reconciliation requires exact local/fetched authoritative base")
    errors.extend(_g0_t03_status_reconciliation_changed_path_errors(root, child_sha))
    errors.extend(_g0_t03_status_reconciliation_evidence_errors(root, child_sha))
    return errors


def _canonical_g0_t03_status_reconciliation_bridge(
    status: dict[str, Any], root: Path, head: str, *, require_canonical_main: bool
) -> tuple[str | None, list[str]]:
    if not _is_g0_t03_status_reconciled(status):
        return None, []
    ok_parents, parents_text = _git(root, "rev-list", "--parents", "-n", "1", head)
    parts = parents_text.split() if ok_parents else []
    second_parent = parts[2] if len(parts) == 3 else ""
    ok_second, second_parents_text = _git(
        root, "rev-list", "--parents", "-n", "1", second_parent
    )
    second_parts = second_parents_text.split() if ok_second else []
    related = len(parts) == 3 and (
        G0_T03_STATUS_RECONCILIATION_BASE_SHA in parts[1:]
        or second_parts == [second_parent, G0_T03_STATUS_RECONCILIATION_BASE_SHA]
    )
    if not related:
        return None, []
    errors: list[str] = []
    first_parent = parts[1]
    governed_parent = second_parent
    if first_parent != G0_T03_STATUS_RECONCILIATION_BASE_SHA:
        errors.append("$: canonical G0-T03 status reconciliation has wrong first parent")
    governed_status = _status_at(root, governed_parent)
    if type(governed_status) is not dict or not _typed_equal(governed_status, status):
        errors.append("$: canonical G0-T03 status reconciliation status must equal second parent")
    if second_parts != [
        governed_parent,
        G0_T03_STATUS_RECONCILIATION_BASE_SHA,
    ]:
        errors.append("$: canonical G0-T03 status reconciliation second parent is not direct")
    ok_head_tree, head_tree = _git(root, "rev-parse", f"{head}^{{tree}}")
    ok_parent_tree, parent_tree = _git(root, "rev-parse", f"{governed_parent}^{{tree}}")
    if not ok_head_tree or not ok_parent_tree or head_tree != parent_tree:
        errors.append("$: canonical G0-T03 status reconciliation tree must equal second parent")
    if require_canonical_main:
        ok_main, main_sha = _git(root, "rev-parse", "--verify", status["authoritative_main_ref"])
        ok_remote, remote_sha = _git(root, "rev-parse", "--verify", "refs/remotes/origin/main")
        if not ok_main or not ok_remote or main_sha != remote_sha or main_sha != head:
            errors.append("$: canonical G0-T03 status reconciliation requires exact local/fetched main")
    errors.extend(_g0_t03_status_reconciliation_changed_path_errors(root, governed_parent))
    errors.extend(_g0_t03_status_reconciliation_evidence_errors(root, governed_parent))
    return (None, errors) if errors else (governed_parent, [])


def _g0_t03_final_close_record_errors(root: Path, schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    closed = _status_at(root, G0_T03_CLOSED_RECORD_SHA)
    finalization = _status_at(root, G0_T03_FINALIZATION_SHA)
    if type(closed) is not dict or _schema_errors(closed, schema, schema):
        errors.append("$: canonical G0-T03 close record is structurally invalid")
        return errors
    if not _is_g0_t03_final_closed_status(closed):
        errors.append("$: canonical G0-T03 close record identity is invalid")
    ok_closed, closed_parents_text = _git(
        root, "rev-list", "--parents", "-n", "1", G0_T03_CLOSED_RECORD_SHA
    )
    if (closed_parents_text.split() if ok_closed else []) != [
        G0_T03_CLOSED_RECORD_SHA,
        G0_T03_FINALIZATION_SHA,
    ]:
        errors.append("$: canonical G0-T03 close record must directly consume finalization")
    if type(finalization) is not dict or _schema_errors(finalization, schema, schema):
        errors.append("$: canonical G0-T03 finalization subject is structurally invalid")
        return errors
    projected = json.loads(json.dumps(closed))
    projected["active_tasks"][0].update(
        state="merged_verified",
        transition={"from": "accepted_pending_merge", "to": "merged_verified"},
    )
    projected["evidence"]["finalization"] = {
        "commit_sha": None,
        "d0_ci": {"status": "not_established", "subject_sha": None, "run_id": None, "url": None},
    }
    if not _typed_equal(projected, finalization):
        errors.append("$: canonical G0-T03 finalization changed immutable phase evidence")
    ok_finalization, finalization_parents_text = _git(
        root, "rev-list", "--parents", "-n", "1", G0_T03_FINALIZATION_SHA
    )
    if (finalization_parents_text.split() if ok_finalization else []) != [
        G0_T03_FINALIZATION_SHA,
        "a98dada059c91dc70714119f333d0d03ab1cb9f1",
    ]:
        errors.append("$: canonical G0-T03 finalization is not rooted at verified main")
    ok_main_parents, main_parents_text = _git(
        root, "rev-list", "--parents", "-n", "1", "a98dada059c91dc70714119f333d0d03ab1cb9f1"
    )
    if (main_parents_text.split() if ok_main_parents else []) != [
        "a98dada059c91dc70714119f333d0d03ab1cb9f1",
        G0_T03_RECOVERY_MERGE_SHA,
        "3263cf207cecac1e3fb019df2fbd6c2a6435d5bd",
    ]:
        errors.append("$: verified G0-T03 main has substituted acceptance topology")
    errors.extend(
        _g0_t03_recovery_closure_receipt_errors(
            root,
            "3263cf207cecac1e3fb019df2fbd6c2a6435d5bd",
            "d259f75cb13a56b7256779ad87115120c005ddec",
        )
    )
    return errors


def _g0_t03_commit_changed_paths(root: Path, parent: str, child: str) -> set[str] | None:
    ok, text = _git(
        root, "diff-tree", "--no-commit-id", "--name-only", "-r", parent, child
    )
    return set(text.splitlines()) if ok else None


def _g0_t03_final_close_binding_errors(
    root: Path, binding_record: str, candidate: str
) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    changed = _g0_t03_commit_changed_paths(root, candidate, binding_record)
    allowed = {
        G0_T03_FINAL_CLOSE_BINDING_PATH,
        "CURRENT_TASK.md",
        "PROJECT_MEMORY.md",
    }
    if (
        changed is None
        or G0_T03_FINAL_CLOSE_BINDING_PATH not in changed
        or not changed.issubset(allowed)
    ):
        errors.append("$: G0-T03 run seal B must be binding-only relative to candidate R")
    ok_candidate_binding, _ = _git(
        root, "cat-file", "-e", f"{candidate}:{G0_T03_FINAL_CLOSE_BINDING_PATH}"
    )
    if ok_candidate_binding:
        errors.append("$: G0-T03 candidate R must not define its own reviewed-run binding")
    ok, text = _git(root, "show", f"{binding_record}:{G0_T03_FINAL_CLOSE_BINDING_PATH}")
    if not ok:
        return None, errors + ["$: G0-T03 run seal B has no reviewed-run binding"]
    try:
        binding = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None, errors + ["$: G0-T03 reviewed-run binding is not canonical JSON"]
    root_keys = {
        "schema_version", "project", "task_id", "candidate_generation",
        "recovery_generation", "candidate_sha", "ci", "history", "review",
        "ruleset", "payload_sha256",
    }
    if type(binding) is not dict or set(binding) != root_keys:
        return None, errors + ["$: G0-T03 reviewed-run binding has an inexact field set"]
    ci = binding.get("ci")
    if type(ci) is not dict or set(ci) != {
        "repository", "event", "subject_sha", "run_id", "url", "check", "status", "conclusion"
    }:
        errors.append("$: G0-T03 reviewed-run binding CI has an inexact field set")
    history = binding.get("history")
    if type(history) is not dict or set(history) != {
        "repair_candidate_sha", "repair_candidate_run_id", "repair_acceptance_sha",
        "repair_acceptance_run_id", "merged_main_sha", "merged_main_run_id",
        "finalization_sha", "finalization_run_id", "closed_record_sha",
        "closed_record_run_id", "blocked_record_sha", "recovery_record_sha",
    }:
        errors.append("$: G0-T03 reviewed-run binding history has an inexact field set")
    if type(binding.get("review")) is not dict or set(binding["review"]) != {
        "code_security", "architecture"
    }:
        errors.append("$: G0-T03 reviewed-run binding review has an inexact field set")
    if type(binding.get("ruleset")) is not dict or set(binding["ruleset"]) != {
        "id", "evidence_sha256"
    }:
        errors.append("$: G0-T03 reviewed-run binding ruleset has an inexact field set")
    expected_history = {
        "repair_candidate_sha": "d259f75cb13a56b7256779ad87115120c005ddec",
        "repair_candidate_run_id": "29904268309",
        "repair_acceptance_sha": "3263cf207cecac1e3fb019df2fbd6c2a6435d5bd",
        "repair_acceptance_run_id": "29905690883",
        "merged_main_sha": "a98dada059c91dc70714119f333d0d03ab1cb9f1",
        "merged_main_run_id": "29906115287",
        "finalization_sha": G0_T03_FINALIZATION_SHA,
        "finalization_run_id": G0_T03_FINALIZATION_RUN,
        "closed_record_sha": G0_T03_CLOSED_RECORD_SHA,
        "closed_record_run_id": G0_T03_CLOSED_RECORD_RUN,
        "blocked_record_sha": G0_T03_BLOCKED_SHA,
        "recovery_record_sha": G0_T03_RECOVERY_ACCEPTED_RECORD_SHA,
    }
    expected_ruleset = {
        "id": 19526291,
        "evidence_sha256": "73aa3644a4c571c7101b0ac36547bd1be2edc306846045d2d36ad07ac86c5bb1",
    }
    if not _typed_equal(binding.get("schema_version"), G0_T03_FINAL_CLOSE_BINDING_VERSION):
        errors.append("$: G0-T03 reviewed-run binding schema version mismatch")
    if not _typed_equal(binding.get("project"), "yaobizuoduo"):
        errors.append("$: G0-T03 reviewed-run binding project mismatch")
    if not _typed_equal(binding.get("task_id"), "G0-T03"):
        errors.append("$: G0-T03 reviewed-run binding task mismatch")
    if not _typed_equal(binding.get("candidate_generation"), 3) or not _typed_equal(
        binding.get("recovery_generation"), 3
    ):
        errors.append("$: G0-T03 reviewed-run binding generation mismatch")
    if not _typed_equal(binding.get("candidate_sha"), candidate):
        errors.append("$: G0-T03 reviewed-run binding candidate mismatch")
    expected_ci = {
        "repository": "weizhenhaihaha-arch/yaobizuoduo",
        "event": "pull_request",
        "subject_sha": candidate,
        "run_id": ci.get("run_id") if type(ci) is dict else None,
        "url": ci.get("url") if type(ci) is dict else None,
        "check": "G0 / exact-head",
        "status": "completed",
        "conclusion": "success",
    }
    if not _typed_equal(ci, expected_ci):
        errors.append("$: G0-T03 reviewed-run binding has inexact CI identity")
    run_id = ci.get("run_id") if type(ci) is dict else None
    url = ci.get("url") if type(ci) is dict else None
    if type(run_id) is not str or re.fullmatch(r"[1-9][0-9]*", run_id) is None:
        errors.append("$: G0-T03 reviewed-run binding run ID must be positive decimal")
    elif url != f"https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/{run_id}":
        errors.append("$: G0-T03 reviewed-run binding URL does not bind run ID")
    if not _typed_equal(history, expected_history):
        errors.append("$: G0-T03 reviewed-run binding history drift")
    if not _typed_equal(binding.get("review"), {"code_security": "approve", "architecture": "clear"}):
        errors.append("$: G0-T03 reviewed-run binding review drift")
    if not _typed_equal(binding.get("ruleset"), expected_ruleset):
        errors.append("$: G0-T03 reviewed-run binding ruleset drift")
    if binding.get("payload_sha256") != _payload_digest(binding):
        errors.append("$: G0-T03 reviewed-run binding digest mismatch")
    return binding, errors


def _g0_t03_final_close_receipt_errors(
    root: Path, accepted_record: str, binding_record: str, candidate: str,
    binding: dict[str, Any] | None,
) -> list[str]:
    changed = _g0_t03_commit_changed_paths(root, binding_record, accepted_record)
    allowed = {
        G0_T03_FINAL_CLOSE_RECEIPT_PATH,
        "CURRENT_TASK.md",
        "PROJECT_MEMORY.md",
    }
    errors: list[str] = []
    if (
        changed is None
        or G0_T03_FINAL_CLOSE_RECEIPT_PATH not in changed
        or not changed.issubset(allowed)
    ):
        errors.append("$: G0-T03 acceptance A must be receipt-only relative to run seal B")
    ok_binding_receipt, _ = _git(
        root, "cat-file", "-e", f"{binding_record}:{G0_T03_FINAL_CLOSE_RECEIPT_PATH}"
    )
    if ok_binding_receipt:
        errors.append("$: G0-T03 run seal B must not define acceptance receipt")
    ok, text = _git(root, "show", f"{accepted_record}:{G0_T03_FINAL_CLOSE_RECEIPT_PATH}")
    if not ok:
        return errors + ["$: G0-T03 final-close recovery acceptance receipt is missing"]
    try:
        receipt = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return ["$: G0-T03 final-close recovery receipt is not canonical JSON"]
    root_keys = {
        "schema_version", "project", "task_id", "candidate_generation",
        "recovery_generation", "failed_merge", "history", "candidate",
        "review", "ruleset", "payload_sha256",
    }
    if type(receipt) is not dict or set(receipt) != root_keys:
        return errors + ["$: G0-T03 final-close recovery receipt has an inexact field set"]
    nested_keys = {
        "failed_merge": {"commit_sha", "run_id", "url", "conclusion"},
        "history": {
            "repair_candidate_sha", "repair_candidate_run_id", "repair_acceptance_sha",
            "repair_acceptance_run_id", "merged_main_sha", "merged_main_run_id",
            "finalization_sha", "finalization_run_id", "closed_record_sha",
            "closed_record_run_id", "blocked_record_sha", "recovery_record_sha",
        },
        "candidate": {"commit_sha", "ci"},
        "review": {"code_security", "architecture"},
        "ruleset": {"id", "evidence_sha256"},
    }
    for field, keys in nested_keys.items():
        value = receipt.get(field)
        if type(value) is not dict or set(value) != keys:
            errors.append(f"$: G0-T03 final-close recovery receipt has an inexact {field} field set")
    ci = receipt.get("candidate", {}).get("ci") if type(receipt.get("candidate")) is dict else None
    if type(ci) is not dict or set(ci) != {
        "repository", "event", "subject_sha", "run_id", "url", "check", "status", "conclusion"
    }:
        errors.append("$: G0-T03 final-close recovery CI receipt has an inexact field set")
        run_id = None
        url = None
    else:
        run_id = ci["run_id"]
        url = ci["url"]
    if binding is None:
        errors.append("$: G0-T03 final-close candidate has no immutable reviewed-run binding")
        candidate_binding = {
            "repository": None, "event": None, "subject_sha": None,
            "run_id": None, "url": None, "check": None,
            "status": None, "conclusion": None,
        }
        binding_history = None
        binding_review = None
        binding_ruleset = None
    else:
        candidate_binding = binding.get("ci")
        binding_history = binding.get("history")
        binding_review = binding.get("review")
        binding_ruleset = binding.get("ruleset")
    expected = {
        "schema_version": G0_T03_FINAL_CLOSE_RECEIPT_VERSION,
        "project": "yaobizuoduo",
        "task_id": "G0-T03",
        "candidate_generation": 3,
        "recovery_generation": 3,
        "failed_merge": {
            "commit_sha": G0_T03_FINAL_CLOSE_MERGE_SHA,
            "run_id": G0_T03_FINAL_CLOSE_MERGE_RUN,
            "url": f"https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/{G0_T03_FINAL_CLOSE_MERGE_RUN}",
            "conclusion": "failure",
        },
        "history": binding_history,
        "candidate": {
            "commit_sha": candidate,
            "ci": candidate_binding,
        },
        "review": binding_review,
        "ruleset": binding_ruleset,
    }
    payload = {key: value for key, value in receipt.items() if key != "payload_sha256"}
    for key, value in expected.items():
        if not _typed_equal(payload.get(key), value):
            errors.append(f"$: G0-T03 final-close recovery receipt has inexact {key}")
    if type(run_id) is not str or re.fullmatch(r"[1-9][0-9]*", run_id) is None:
        errors.append("$: G0-T03 final-close recovery run ID must be a positive decimal string")
    elif url != f"https://github.com/weizhenhaihaha-arch/yaobizuoduo/actions/runs/{run_id}":
        errors.append("$: G0-T03 final-close recovery CI URL does not bind its run ID")
    if receipt.get("payload_sha256") != _payload_digest(receipt):
        errors.append("$: G0-T03 final-close recovery receipt digest mismatch")
    ok_candidate_receipt, _ = _git(
        root, "cat-file", "-e", f"{candidate}:{G0_T03_FINAL_CLOSE_RECEIPT_PATH}"
    )
    if ok_candidate_receipt:
        errors.append("$: G0-T03 final-close receipt must be created only by later acceptance")
    return errors


def _canonical_g0_t03_final_close_bridge(
    status: dict[str, Any],
    root: Path,
    head: str,
    schema: dict[str, Any],
    *,
    require_canonical_main: bool,
) -> tuple[str | None, list[str]]:
    base_status = _is_g0_t03_final_closed_status(status)
    recovery_status = _is_g0_t03_final_close_recovery_status(status)
    if not (base_status or recovery_status):
        return None, []
    ok, parents_text = _git(root, "rev-list", "--parents", "-n", "1", head)
    parts = parents_text.split() if ok else []
    if len(parts) != 3:
        return None, []
    first_parent, governed_parent = parts[1], parts[2]
    errors = _g0_t03_final_close_record_errors(root, schema)
    ok_origin, origin_url = _git(root, "remote", "get-url", "origin")
    if not ok_origin or _github_repository_identity(origin_url) != LEDGER_REPOSITORY:
        errors.append("$: canonical G0-T03 final-close bridge requires canonical repository")
    if require_canonical_main:
        ok_main, main_sha = _git(root, "rev-parse", "--verify", status["authoritative_main_ref"])
        ok_remote, remote_sha = _git(root, "rev-parse", "--verify", "refs/remotes/origin/main")
        if not ok_main or not ok_remote or main_sha != remote_sha or main_sha != head:
            errors.append("$: canonical G0-T03 final-close bridge requires exact local/fetched main")
    if head == G0_T03_FINAL_CLOSE_MERGE_SHA:
        if not base_status or (first_parent, governed_parent) != (
            "a98dada059c91dc70714119f333d0d03ab1cb9f1",
            G0_T03_CLOSED_RECORD_SHA,
        ):
            errors.append("$: canonical G0-T03 final-close merge has substituted parents or status")
    else:
        if not recovery_status or first_parent != G0_T03_FINAL_CLOSE_MERGE_SHA:
            errors.append("$: G0-T03 final-close recovery must use exact failed merge and recovery status")
        ok_record, record_parents_text = _git(
            root, "rev-list", "--parents", "-n", "1", governed_parent
        )
        record_parts = record_parents_text.split() if ok_record else []
        binding_record = record_parts[1] if len(record_parts) == 2 else ""
        if len(record_parts) != 2:
            errors.append("$: G0-T03 final-close acceptance A must directly consume run seal B")
        ok_binding, binding_parents_text = _git(
            root, "rev-list", "--parents", "-n", "1", binding_record
        )
        binding_parts = binding_parents_text.split() if ok_binding else []
        candidate = binding_parts[1] if len(binding_parts) == 2 else ""
        if len(binding_parts) != 2:
            errors.append("$: G0-T03 run seal B must directly consume candidate R")
        ok_lineage, lineage_text = _git(
            root, "rev-list", "--first-parent", f"{G0_T03_FINAL_CLOSE_MERGE_SHA}..{candidate}"
        )
        lineage = lineage_text.splitlines() if ok_lineage else []
        if not lineage or lineage[0] != candidate:
            errors.append("$: G0-T03 final-close recovery candidate is not rooted at failed merge")
        for index, repair_sha in enumerate(lineage):
            ok_repair, repair_parents_text = _git(
                root, "rev-list", "--parents", "-n", "1", repair_sha
            )
            expected_parent = (
                lineage[index + 1] if index + 1 < len(lineage) else G0_T03_FINAL_CLOSE_MERGE_SHA
            )
            if (
                (repair_parents_text.split() if ok_repair else []) != [repair_sha, expected_parent]
                or not _typed_equal(_status_at(root, repair_sha), status)
            ):
                errors.append("$: G0-T03 final-close recovery requires status-identical single-parent repair")
                break
        if not _typed_equal(_status_at(root, governed_parent), status):
            errors.append("$: G0-T03 final-close recovery acceptance status mismatch")
        if not _typed_equal(_status_at(root, binding_record), status):
            errors.append("$: G0-T03 final-close run seal status mismatch")
        binding, binding_errors = _g0_t03_final_close_binding_errors(
            root, binding_record, candidate
        )
        errors.extend(binding_errors)
        errors.extend(
            _g0_t03_final_close_receipt_errors(
                root, governed_parent, binding_record, candidate, binding
            )
        )
    if not _typed_equal(_status_at(root, governed_parent), status):
        errors.append("$: canonical G0-T03 final-close bridge status must equal second parent")
    ok_head_tree, head_tree = _git(root, "rev-parse", f"{head}^{{tree}}")
    ok_parent_tree, parent_tree = _git(root, "rev-parse", f"{governed_parent}^{{tree}}")
    if not ok_head_tree or not ok_parent_tree or head_tree != parent_tree:
        errors.append("$: canonical G0-T03 final-close bridge tree must equal second parent")
    frozen_refs = {
        "refs/remotes/origin/codex/g0-t03-main-protection": G0_T03_BLOCKED_SHA,
        "refs/remotes/origin/codex/g0-t03-merge-recovery": G0_T03_RECOVERY_ACCEPTED_RECORD_SHA,
        "refs/remotes/origin/codex/g0-t03-recovery-merge-recovery": "3263cf207cecac1e3fb019df2fbd6c2a6435d5bd",
        "refs/remotes/origin/codex/g0-t03-finalize": G0_T03_CLOSED_RECORD_SHA,
    }
    for ref, expected_sha in frozen_refs.items():
        ok_ref, actual_sha = _git(root, "rev-parse", "--verify", ref)
        if not ok_ref or actual_sha != expected_sha:
            errors.append(f"$: G0-T03 final-close recovery frozen ref changed: {ref}")
    if errors:
        return None, errors
    return governed_parent, []


def _g0_t03_planning_handoff_fact_errors() -> list[str]:
    facts = {
        "recovered_main": {
            "commit_sha": G0_T03_RECOVERED_MAIN_SHA,
            "run_id": G0_T03_RECOVERED_MAIN_RUN,
            "event": "push",
            "conclusion": "success",
        },
        "planning_pr": {
            "number": 11,
            "head_sha": G0_T03_PLANNING_HANDOFF_SECOND_PARENT,
            "run_id": G0_T03_PLANNING_HANDOFF_PR_RUN,
            "event": "pull_request",
            "check": "G0 / exact-head",
            "conclusion": "success",
            "code_security": "approve",
            "architecture": "clear",
        },
        "failed_main": {
            "commit_sha": G0_T03_PLANNING_HANDOFF_SHA,
            "run_id": G0_T03_PLANNING_HANDOFF_MAIN_RUN,
            "event": "push",
            "conclusion": "failure",
        },
    }
    expected = {
        "recovered_main": {
            "commit_sha": "02e05d1f2d68a9a1c89fda9c8636e2263fc48053",
            "run_id": "29929973216",
            "event": "push",
            "conclusion": "success",
        },
        "planning_pr": {
            "number": 11,
            "head_sha": "b8f04c9bbc3f86b6ef643cdd097ec7dc46c16e5b",
            "run_id": "29932171250",
            "event": "pull_request",
            "check": "G0 / exact-head",
            "conclusion": "success",
            "code_security": "approve",
            "architecture": "clear",
        },
        "failed_main": {
            "commit_sha": "e1d251c35bbfc128990be4f9e3d1b851a3146f12",
            "run_id": "29933844415",
            "event": "push",
            "conclusion": "failure",
        },
    }
    return [] if _typed_equal(facts, expected) else [
        "$: G0-T03 planning handoff has drifted CI, review, or main identity"
    ]


def _canonical_g0_t03_planning_handoff_bridge(
    status: dict[str, Any],
    root: Path,
    head: str,
    *,
    require_canonical_main: bool,
) -> tuple[str | None, list[str]]:
    """Recognize only the published planning merge or its bounded repair merge."""
    if not _is_g0_t03_final_close_recovery_status(status):
        return None, []
    ok_head, head_parents_text = _git(root, "rev-list", "--parents", "-n", "1", head)
    head_parts = head_parents_text.split() if ok_head else []
    related = head == G0_T03_PLANNING_HANDOFF_SHA or (
        len(head_parts) == 3 and G0_T03_PLANNING_HANDOFF_SHA in head_parts[1:]
    )
    if not related:
        return None, []
    errors = _g0_t03_planning_handoff_fact_errors()
    ok_origin, origin_url = _git(root, "remote", "get-url", "origin")
    if not ok_origin or _github_repository_identity(origin_url) != LEDGER_REPOSITORY:
        errors.append("$: canonical G0-T03 planning handoff requires canonical repository")
    if require_canonical_main:
        ok_main, main_sha = _git(root, "rev-parse", "--verify", status["authoritative_main_ref"])
        ok_remote, remote_sha = _git(root, "rev-parse", "--verify", "refs/remotes/origin/main")
        if not ok_main or not ok_remote or main_sha != remote_sha or main_sha != head:
            errors.append("$: canonical G0-T03 planning handoff requires exact local/fetched main")

    ok_published, published_parents_text = _git(
        root, "rev-list", "--parents", "-n", "1", G0_T03_PLANNING_HANDOFF_SHA
    )
    published_parts = published_parents_text.split() if ok_published else []
    if published_parts != [
        G0_T03_PLANNING_HANDOFF_SHA,
        G0_T03_PLANNING_HANDOFF_FIRST_PARENT,
        G0_T03_PLANNING_HANDOFF_SECOND_PARENT,
    ]:
        errors.append("$: G0-T03 planning handoff has substituted or swapped published parents")
    ok_published_tree, published_tree = _git(
        root, "rev-parse", f"{G0_T03_PLANNING_HANDOFF_SHA}^{{tree}}"
    )
    ok_planning_tree, planning_tree = _git(
        root, "rev-parse", f"{G0_T03_PLANNING_HANDOFF_SECOND_PARENT}^{{tree}}"
    )
    if (
        not ok_published_tree
        or not ok_planning_tree
        or published_tree != G0_T03_PLANNING_HANDOFF_TREE
        or published_tree != planning_tree
    ):
        errors.append("$: G0-T03 planning handoff has substituted published tree")
    if not (
        _typed_equal(_status_at(root, G0_T03_PLANNING_HANDOFF_SHA), status)
        and _typed_equal(_status_at(root, G0_T03_PLANNING_HANDOFF_FIRST_PARENT), status)
        and _typed_equal(_status_at(root, G0_T03_PLANNING_HANDOFF_SECOND_PARENT), status)
    ):
        errors.append("$: G0-T03 planning handoff must preserve exact closed status")
    planning_paths = _g0_t03_commit_changed_paths(
        root, G0_T03_PLANNING_HANDOFF_FIRST_PARENT, G0_T03_PLANNING_HANDOFF_SECOND_PARENT
    )
    if planning_paths != {"docs/NEXT_WORKFLOW.md", "PROJECT_MEMORY.md"}:
        errors.append("$: G0-T03 planning handoff PR must be planning-only")
    ok_planning_parent, planning_parents_text = _git(
        root, "rev-list", "--parents", "-n", "1", G0_T03_PLANNING_HANDOFF_SECOND_PARENT
    )
    if (planning_parents_text.split() if ok_planning_parent else []) != [
        G0_T03_PLANNING_HANDOFF_SECOND_PARENT,
        G0_T03_PLANNING_HANDOFF_FIRST_PARENT,
    ]:
        errors.append("$: G0-T03 planning handoff PR head must directly follow recovered main")
    recovered_status = _status_at(root, G0_T03_RECOVERED_MAIN_SHA)
    recovered_schema = _schema_at(root, G0_T03_RECOVERED_MAIN_SHA)
    if type(recovered_status) is not dict or type(recovered_schema) is not dict:
        errors.append("$: G0-T03 recovered-main status or schema is unreadable")
    else:
        recovered_governed, recovered_errors = _canonical_g0_t03_final_close_bridge(
            recovered_status,
            root,
            G0_T03_RECOVERED_MAIN_SHA,
            recovered_schema,
            require_canonical_main=False,
        )
        errors.extend(recovered_errors)
        if recovered_governed != "ddd69c2c8174837e12d186fd12252ccb6f13b24e":
            errors.append("$: G0-T03 planning handoff is not rooted at exact recovered R-B-A main")

    if head == G0_T03_PLANNING_HANDOFF_SHA:
        governed_parent = G0_T03_PLANNING_HANDOFF_SECOND_PARENT
    else:
        if len(head_parts) != 3 or head_parts[1] != G0_T03_PLANNING_HANDOFF_SHA:
            errors.append("$: G0-T03 planning-handoff recovery must use failed main as first parent")
        governed_parent = head_parts[2] if len(head_parts) == 3 else ""
        ok_lineage, lineage_text = _git(
            root,
            "rev-list",
            "--first-parent",
            f"{G0_T03_PLANNING_HANDOFF_SHA}..{governed_parent}",
        )
        lineage = lineage_text.splitlines() if ok_lineage else []
        if not lineage or lineage[0] != governed_parent:
            errors.append("$: G0-T03 planning-handoff recovery lineage is unavailable")
        for index, repair_sha in enumerate(lineage):
            ok_repair, repair_parents_text = _git(
                root, "rev-list", "--parents", "-n", "1", repair_sha
            )
            expected_parent = (
                lineage[index + 1]
                if index + 1 < len(lineage)
                else G0_T03_PLANNING_HANDOFF_SHA
            )
            if (
                (repair_parents_text.split() if ok_repair else [])
                != [repair_sha, expected_parent]
                or not _typed_equal(_status_at(root, repair_sha), status)
            ):
                errors.append(
                    "$: G0-T03 planning-handoff recovery requires status-identical single-parent repair"
                )
                break
        repair_paths = _g0_t03_commit_changed_paths(
            root, G0_T03_PLANNING_HANDOFF_SHA, governed_parent
        )
        allowed_repair_paths = {
            "scripts/validate_project_status.py",
            "tests/test_g0_project_status.py",
            "CURRENT_TASK.md",
            "PROJECT_MEMORY.md",
        }
        required_repair_paths = {
            "scripts/validate_project_status.py",
            "tests/test_g0_project_status.py",
        }
        if (
            repair_paths is None
            or not required_repair_paths.issubset(repair_paths)
            or not repair_paths.issubset(allowed_repair_paths)
        ):
            errors.append("$: G0-T03 planning-handoff recovery has out-of-scope changes")
        if not _typed_equal(_status_at(root, governed_parent), status):
            errors.append("$: G0-T03 planning-handoff recovery must preserve second-parent status")
        ok_head_tree, head_tree = _git(root, "rev-parse", f"{head}^{{tree}}")
        ok_parent_tree, parent_tree = _git(root, "rev-parse", f"{governed_parent}^{{tree}}")
        if not ok_head_tree or not ok_parent_tree or head_tree != parent_tree:
            errors.append("$: G0-T03 planning-handoff recovery tree must equal second parent")
    if errors:
        return None, errors
    return governed_parent, []


@functools.lru_cache(maxsize=32)
def _g0_t03_final_close_main_matches(root: Path, main_sha: str) -> bool:
    # The published failed merge is content-addressed and is the immutable
    # baseline for this recovery.  Avoid re-walking its full historical proof
    # for every earlier ledger transition.
    if main_sha == G0_T03_FINAL_CLOSE_MERGE_SHA:
        return True
    status = _status_at(root, main_sha)
    schema = _schema_at(root, main_sha)
    if type(status) is not dict or type(schema) is not dict:
        return False
    reconciliation_governed, reconciliation_errors = (
        _canonical_g0_t03_status_reconciliation_bridge(
            status,
            root,
            main_sha,
            require_canonical_main=False,
        )
    )
    if reconciliation_governed is not None or reconciliation_errors:
        return reconciliation_governed is not None and not reconciliation_errors
    planning_governed, planning_errors = _canonical_g0_t03_planning_handoff_bridge(
        status,
        root,
        main_sha,
        require_canonical_main=False,
    )
    if planning_governed is not None or planning_errors:
        return planning_governed is not None and not planning_errors
    if main_sha == G0_T04_FAILED_MAIN_SHA:
        governed, merge_errors = _canonical_g0_merge_bridge(
            status,
            root,
            main_sha,
            schema,
            require_canonical_main=False,
        )
        return governed == G0_T04_CLOSURE_SHA and not merge_errors
    governed, errors = _canonical_g0_t03_final_close_bridge(
        status,
        root,
        main_sha,
        schema,
        require_canonical_main=False,
    )
    return governed is not None and not errors


def _g0_t03_final_close_repair_parent_errors(
    status: dict[str, Any],
    parent: dict[str, Any],
    parent_sha: str | None,
    root: Path | None,
    child_sha: str | None,
    *,
    require_current_main: bool = True,
) -> list[str] | None:
    if not _is_g0_t03_final_close_recovery_status(status):
        return None
    if root is None or parent_sha is None or child_sha is None:
        return ["$: G0-T03 final-close recovery requires repository-bound lineage"]
    schema = _schema_at(root, child_sha)
    if type(schema) is not dict:
        return ["$: G0-T03 final-close recovery schema is unreadable"]
    if _is_g0_t03_final_close_recovery_status(parent):
        ok, parts_text = _git(root, "rev-list", "--parents", "-n", "1", child_sha)
        if (
            not _typed_equal(status, parent)
            or (parts_text.split() if ok else []) != [child_sha, parent_sha]
            or not _is_ancestor(root, G0_T03_FINAL_CLOSE_MERGE_SHA, parent_sha)
        ):
            return ["$: G0-T03 final-close repair must preserve status on single-parent lineage"]
        return []
    if not _is_g0_t03_final_closed_status(parent) or parent_sha != G0_T03_FINAL_CLOSE_MERGE_SHA:
        return ["$: G0-T03 final-close recovery must be rooted at exact failed merge"]
    projected = json.loads(json.dumps(status))
    projected["active_tasks"][0]["transition"] = {
        "from": "merged_verified",
        "to": "closed",
    }
    projected["blockers"] = []
    errors: list[str] = []
    if not _typed_equal(projected, parent):
        errors.append("$: G0-T03 final-close recovery may only add exact failed-run blocker")
    ok_child, child_parents_text = _git(root, "rev-list", "--parents", "-n", "1", child_sha)
    child_parts = child_parents_text.split() if ok_child else []
    if len(child_parts) == 3:
        governed, bridge_errors = _canonical_g0_t03_final_close_bridge(
            status, root, child_sha, schema, require_canonical_main=False
        )
        errors.extend(bridge_errors)
        if governed is None:
            errors.append("$: G0-T03 final-close recovery merge is not canonical")
    elif child_parts != [child_sha, parent_sha]:
        errors.append("$: initial G0-T03 final-close recovery must directly follow failed merge")
    if require_current_main:
        ok_main, main_sha = _git(root, "rev-parse", "--verify", status["authoritative_main_ref"])
        ok_remote, remote_sha = _git(root, "rev-parse", "--verify", "refs/remotes/origin/main")
        main_matches = (
            ok_main
            and ok_remote
            and main_sha == remote_sha
            and _g0_t03_final_close_main_matches(root, main_sha)
        )
        if not main_matches:
            errors.append("$: G0-T03 final-close recovery requires exact failed or recovered main")
    governed_parent, parent_errors = _canonical_g0_t03_final_close_bridge(
        parent, root, parent_sha, schema, require_canonical_main=False
    )
    errors.extend(parent_errors)
    if governed_parent != G0_T03_CLOSED_RECORD_SHA:
        errors.append("$: G0-T03 final-close recovery parent is not exact failed close bridge")
    return errors


def _g0_t03_recovery_parent_errors(
    status: dict[str, Any],
    parent: dict[str, Any],
    parent_sha: str | None,
    root: Path | None,
    child_sha: str | None,
    *,
    require_current_main: bool = True,
) -> list[str] | None:
    if not _is_g0_t03_post_merge_recovery_status(status):
        return None
    if root is None or child_sha is None or parent_sha is None:
        return ["$: G0-T03 post-merge recovery requires repository-bound parent evidence"]
    errors: list[str] = []
    if _is_g0_t03_post_merge_recovery_status(parent):
        ok, parents_text = _git(root, "rev-list", "--parents", "-n", "1", child_sha)
        if (
            not _typed_equal(status, parent)
            or (parents_text.split() if ok else []) != [child_sha, parent_sha]
            or not _is_ancestor(root, G0_T03_FAILED_MAIN_SHA, parent_sha)
        ):
            errors.append("$: G0-T03 post-merge recovery follow-up must preserve exact status on a single-parent lineage")
        return errors
    if parent_sha != G0_T03_FAILED_MAIN_SHA:
        return ["$: G0-T03 post-merge recovery must be rooted at the exact failed main"]
    projected = json.loads(json.dumps(status))
    projected["active_tasks"][0]["transition"] = {
        "from": "awaiting_review",
        "to": "accepted_pending_merge",
    }
    projected["blockers"] = []
    if not _typed_equal(projected, parent):
        errors.append("$: G0-T03 post-merge recovery may only add the exact failure record and transition")
    ok_lineage, lineage_text = _git(root, "rev-list", "--first-parent", f"{parent_sha}..{child_sha}")
    lineage = lineage_text.splitlines() if ok_lineage else []
    for index, recovery_sha in enumerate(lineage):
        ok_parents, recovery_parents_text = _git(root, "rev-list", "--parents", "-n", "1", recovery_sha)
        expected_parent = lineage[index + 1] if index + 1 < len(lineage) else parent_sha
        if (
            (recovery_parents_text.split() if ok_parents else []) != [recovery_sha, expected_parent]
            or not _typed_equal(_status_at(root, recovery_sha), status)
        ):
            errors.append("$: G0-T03 post-merge recovery requires a status-identical single-parent lineage")
            break
    if require_current_main:
        ok_main, main_sha = _git(root, "rev-parse", "--verify", status["authoritative_main_ref"])
        ok_remote, remote_sha = _git(root, "rev-parse", "--verify", "refs/remotes/origin/main")
        main_matches = ok_main and ok_remote and main_sha == remote_sha == G0_T03_FAILED_MAIN_SHA
        if ok_main and ok_remote and main_sha == remote_sha == G0_T03_RECOVERY_MERGE_SHA:
            recovery_merge_status = _status_at(root, main_sha)
            if type(recovery_merge_status) is dict:
                governed_recovery, recovery_merge_errors = _canonical_g0_t03_recovery_merge_bridge(
                    recovery_merge_status,
                    root,
                    main_sha,
                    require_canonical_main=False,
                )
                main_matches = governed_recovery is not None and not recovery_merge_errors
        if ok_main and ok_remote and main_sha == remote_sha and main_sha not in {
            G0_T03_FAILED_MAIN_SHA,
            G0_T03_RECOVERY_MERGE_SHA,
        }:
            closure_status = _status_at(root, main_sha)
            if type(closure_status) is dict:
                governed_closure, closure_errors = _canonical_g0_t03_recovery_closure_bridge(
                    closure_status,
                    root,
                    main_sha,
                    require_canonical_main=False,
                )
                main_matches = governed_closure is not None and not closure_errors
                if not main_matches:
                    main_matches = _g0_t03_recovery_closure_ancestor(root, main_sha) is not None
        if not main_matches and ok_main and ok_remote and main_sha == remote_sha:
            main_matches = _g0_t03_final_close_main_matches(root, main_sha)
        if not main_matches:
            errors.append("$: G0-T03 post-merge recovery requires the exact failed main on local/fetched main")
    governed, bridge_errors = _canonical_g0_t03_merge_bridge(
        parent, root, parent_sha, require_canonical_main=False
    )
    errors.extend(bridge_errors)
    if governed is None:
        errors.append("$: G0-T03 post-merge recovery parent is not the canonical failed merge bridge")
    return errors


def _g0_t03_recovery_merge_recovery_parent_errors(
    status: dict[str, Any],
    parent: dict[str, Any],
    parent_sha: str | None,
    root: Path | None,
    child_sha: str | None,
    *,
    require_current_main: bool = True,
) -> list[str] | None:
    if not _is_g0_t03_recovery_merge_recovery_status(status):
        return None
    if root is None or child_sha is None or parent_sha is None:
        return ["$: G0-T03 recovery-merge recovery requires repository-bound parent evidence"]
    errors: list[str] = []
    if _is_g0_t03_recovery_merge_recovery_status(parent):
        ok, parents_text = _git(root, "rev-list", "--parents", "-n", "1", child_sha)
        if (
            not _typed_equal(status, parent)
            or (parents_text.split() if ok else []) != [child_sha, parent_sha]
            or not _is_ancestor(root, G0_T03_RECOVERY_MERGE_SHA, parent_sha)
        ):
            errors.append("$: G0-T03 recovery-merge follow-up must preserve exact status on a single-parent lineage")
        return errors
    if parent_sha != G0_T03_RECOVERY_MERGE_SHA:
        return ["$: G0-T03 recovery-merge recovery must be rooted at the exact failed recovery merge"]
    projected = json.loads(json.dumps(status))
    projected["blockers"] = [G0_T03_RECOVERY_BLOCKER]
    if not _typed_equal(projected, parent):
        errors.append("$: G0-T03 recovery-merge recovery may only add the exact second failure record")
    ok_lineage, lineage_text = _git(root, "rev-list", "--first-parent", f"{parent_sha}..{child_sha}")
    lineage = lineage_text.splitlines() if ok_lineage else []
    for index, recovery_sha in enumerate(lineage):
        ok_parents, recovery_parents_text = _git(root, "rev-list", "--parents", "-n", "1", recovery_sha)
        expected_parent = lineage[index + 1] if index + 1 < len(lineage) else parent_sha
        if (
            (recovery_parents_text.split() if ok_parents else []) != [recovery_sha, expected_parent]
            or not _typed_equal(_status_at(root, recovery_sha), status)
        ):
            errors.append("$: G0-T03 recovery-merge recovery requires a status-identical single-parent lineage")
            break
    if require_current_main:
        ok_main, main_sha = _git(root, "rev-parse", "--verify", status["authoritative_main_ref"])
        ok_remote, remote_sha = _git(root, "rev-parse", "--verify", "refs/remotes/origin/main")
        main_matches = ok_main and ok_remote and main_sha == remote_sha == G0_T03_RECOVERY_MERGE_SHA
        if ok_main and ok_remote and main_sha == remote_sha and main_sha != G0_T03_RECOVERY_MERGE_SHA:
            closure_status = _status_at(root, main_sha)
            if type(closure_status) is dict:
                governed_closure, closure_errors = _canonical_g0_t03_recovery_closure_bridge(
                    closure_status,
                    root,
                    main_sha,
                    require_canonical_main=False,
                )
                main_matches = governed_closure is not None and not closure_errors
                if not main_matches:
                    main_matches = _g0_t03_recovery_closure_ancestor(root, main_sha) is not None
        if not main_matches and ok_main and ok_remote and main_sha == remote_sha:
            main_matches = _g0_t03_final_close_main_matches(root, main_sha)
        if not main_matches:
            errors.append("$: G0-T03 recovery-merge recovery requires exact failed recovery merge on local/fetched main")
    governed, bridge_errors = _canonical_g0_t03_recovery_merge_bridge(
        parent,
        root,
        parent_sha,
        require_canonical_main=False,
    )
    errors.extend(bridge_errors)
    if governed != G0_T03_RECOVERY_ACCEPTED_RECORD_SHA:
        errors.append("$: G0-T03 recovery-merge parent is not the exact canonical recovery merge")
    return errors


def _g0_t04_anomaly_post_merge_repair_parent_errors(
    status: dict[str, Any],
    parent: dict[str, Any],
    parent_sha: str | None,
    root: Path | None,
    child_sha: str | None,
    *,
    require_current_main: bool,
) -> list[str] | None:
    if _is_g0_t04_g4_status(status):
        return None
    if root is None or child_sha is None or child_sha == G0_T04_ANOMALY_MERGE:
        return None
    if not _is_ancestor(root, G0_T04_ANOMALY_MERGE, child_sha):
        return None
    if not _is_g0_t04_anomaly_seal_status(status):
        return ["$: G0-T04 post-merge repair must preserve exact blocked status"]
    errors: list[str] = []
    merge_status = _status_at(root, G0_T04_ANOMALY_MERGE)
    if (
        type(merge_status) is not dict
        or not _typed_equal(status, merge_status)
        or not _typed_equal(parent, merge_status)
    ):
        errors.append("$: G0-T04 post-merge repair status drifted from exact F")
    ok_child, child_line = _git(
        root, "rev-list", "--parents", "-n", "1", child_sha
    )
    if (
        parent_sha is None
        or (child_line.split() if ok_child else []) != [child_sha, parent_sha]
    ):
        errors.append("$: G0-T04 post-merge repair must be single-parent")
    ok_lineage, lineage_text = _git(
        root,
        "rev-list",
        "--first-parent",
        f"{G0_T04_ANOMALY_MERGE}..{child_sha}",
    )
    lineage = lineage_text.splitlines() if ok_lineage else []
    if not lineage or lineage[0] != child_sha:
        errors.append("$: G0-T04 post-merge repair is not rooted at exact F")
    for index, repair_sha in enumerate(lineage):
        expected_parent = (
            lineage[index + 1]
            if index + 1 < len(lineage)
            else G0_T04_ANOMALY_MERGE
        )
        ok_repair, repair_line = _git(
            root, "rev-list", "--parents", "-n", "1", repair_sha
        )
        if (
            (repair_line.split() if ok_repair else [])
            != [repair_sha, expected_parent]
            or not _typed_equal(_status_at(root, repair_sha), merge_status)
        ):
            errors.append(
                "$: G0-T04 post-merge repair requires status-identical "
                "single-parent lineage from exact F"
            )
            break
    changed = _g0_t03_commit_changed_paths(
        root, G0_T04_ANOMALY_MERGE, child_sha
    )
    if (
        changed is None
        or not changed
        or not changed.issubset(G0_T04_ANOMALY_POST_MERGE_REPAIR_ALLOWED)
    ):
        errors.append("$: G0-T04 post-merge repair cumulative allowlist drifted")
    ok_merge, merge_line = _git(
        root, "rev-list", "--parents", "-n", "1", G0_T04_ANOMALY_MERGE
    )
    ok_merge_tree, merge_tree = _git(
        root, "rev-parse", f"{G0_T04_ANOMALY_MERGE}^{{tree}}"
    )
    ok_seal_tree, seal_tree = _git(
        root, "rev-parse", f"{G0_T04_ANOMALY_SEAL}^{{tree}}"
    )
    if (
        (merge_line.split() if ok_merge else [])
        != [
            G0_T04_ANOMALY_MERGE,
            G0_T04_ANOMALY_MAIN,
            G0_T04_ANOMALY_SEAL,
        ]
        or not ok_merge_tree
        or not ok_seal_tree
        or merge_tree != seal_tree
    ):
        errors.append("$: exact G0-T04 anomaly merge F topology drifted")
    schema = _schema_at(root, child_sha)
    if type(schema) is not dict:
        errors.append("$: G0-T04 post-merge repair schema is unavailable")
    else:
        governed, bridge_errors = _canonical_g0_t04_anomaly_bridge(
            merge_status if type(merge_status) is dict else status,
            root,
            G0_T04_ANOMALY_MERGE,
            schema,
            require_canonical_main=False,
        )
        errors.extend(bridge_errors)
        if governed != G0_T04_ANOMALY_SEAL:
            errors.append("$: exact G0-T04 anomaly merge F is not canonical")
    for relative in (
        G0_T04_ANOMALY_RECEIPT_PATH,
        G0_T04_ANOMALY_SEAL_PATH,
        PACKAGE_A_MANIFEST_PATH,
        PACKAGE_A_SCHEMA_PATH,
    ):
        ok_f, f_blob = _git(
            root, "rev-parse", f"{G0_T04_ANOMALY_MERGE}:{relative}"
        )
        ok_child_blob, child_blob = _git(
            root, "rev-parse", f"{child_sha}:{relative}"
        )
        if not ok_f or not ok_child_blob or child_blob != f_blob:
            errors.append(
                f"$: G0-T04 post-merge repair immutable blob drifted: {relative}"
            )
    if _git(
        root, "cat-file", "-e", f"{child_sha}:{PACKAGE_A_ACTIVATION_PATH}"
    )[0]:
        errors.append("$: false Package A activation reappeared after exact F")
    if require_current_main:
        ok_main, main = _git(
            root, "rev-parse", "--verify", status["authoritative_main_ref"]
        )
        ok_remote, remote = _git(
            root, "rev-parse", "--verify", "refs/remotes/origin/main"
        )
        if (
            not ok_main
            or not ok_remote
            or main != remote
            or main != G0_T04_ANOMALY_MERGE
        ):
            errors.append(
                "$: G0-T04 post-merge repair requires exact authoritative F"
            )
    return errors


def _g0_t04_anomaly_seal_parent_errors(
    status: dict[str, Any],
    parent: dict[str, Any],
    parent_sha: str | None,
    root: Path | None,
    child_sha: str | None,
    *,
    require_current_main: bool,
) -> list[str] | None:
    if not _is_g0_t04_anomaly_seal_status(status):
        return None
    if (
        root is None
        or parent_sha != G0_T04_ANOMALY_CANDIDATE
        or child_sha is None
    ):
        return ["$: G0-T04 anomaly seal requires exact candidate C lineage"]
    errors: list[str] = []
    if not _typed_equal(parent, _g0_t04_anomaly_status(root)):
        errors.append("$: G0-T04 anomaly seal direct-parent status drifted")
    ok_child, child_line = _git(
        root, "rev-list", "--parents", "-n", "1", child_sha
    )
    if (child_line.split() if ok_child else []) != [
        child_sha,
        G0_T04_ANOMALY_CANDIDATE,
    ]:
        errors.append("$: G0-T04 anomaly seal S must directly consume exact C")
    candidate_status = _status_at(root, G0_T04_ANOMALY_CANDIDATE)
    candidate_history_errors = _g0_t04_anomaly_parent_errors(
        _g0_t04_anomaly_status(root),
        _status_at(root, G0_T04_ANOMALY_IMPLEMENTATION) or {},
        G0_T04_ANOMALY_IMPLEMENTATION,
        root,
        G0_T04_ANOMALY_CANDIDATE,
        require_current_main=False,
    )
    if candidate_status is None or not _typed_equal(
        candidate_status, _g0_t04_anomaly_status(root)
    ):
        errors.append("$: exact candidate C status drifted")
    errors.extend(candidate_history_errors or [])
    errors.extend(
        _g0_t04_anomaly_seal_errors(
            status,
            root,
            child_sha,
            require_current_main=require_current_main,
        )
    )
    return errors


def _g0_t04_anomaly_parent_errors(
    status: dict[str, Any],
    parent: dict[str, Any],
    parent_sha: str | None,
    root: Path | None,
    child_sha: str | None,
    *,
    require_current_main: bool,
) -> list[str] | None:
    if not _is_g0_t04_anomaly_status(status):
        return None
    if root is None or parent_sha is None or child_sha is None:
        return ["$: G0-T04 anomaly recovery requires repository lineage"]
    ok_parent, parent_line = _git(
        root, "rev-list", "--parents", "-n", "1", parent_sha
    )
    ok_child, child_line = _git(
        root, "rev-list", "--parents", "-n", "1", child_sha
    )
    errors: list[str] = []
    if (
        parent_sha != G0_T04_ANOMALY_IMPLEMENTATION
        or (parent_line.split() if ok_parent else []) != [
        G0_T04_ANOMALY_IMPLEMENTATION,
        G0_T04_ANOMALY_MAIN,
        ]
    ):
        errors.append("$: G0-T04 anomaly implementation is not direct child of exact main")
    if (child_line.split() if ok_child else []) != [child_sha, parent_sha]:
        errors.append("$: G0-T04 anomaly delivery must directly follow implementation")
    implementation_changed = _g0_t03_commit_changed_paths(
        root, G0_T04_ANOMALY_MAIN, parent_sha
    )
    if implementation_changed != {
        "scripts/validate_project_status.py",
        "tests/test_g0_project_status.py",
    }:
        errors.append("$: G0-T04 anomaly implementation scope drifted")
    errors.extend(
        _g0_t04_anomaly_delivery_errors(
            status,
            root,
            child_sha,
            require_current_main=require_current_main,
        )
    )
    return errors


def _g0_t04_anomaly_implementation_errors(
    status: dict[str, Any],
    parent: dict[str, Any],
    parent_sha: str | None,
    root: Path | None,
    child_sha: str | None,
    *,
    require_current_main: bool,
) -> list[str] | None:
    if (
        root is None
        or parent_sha != G0_T04_ANOMALY_MAIN
        or child_sha is None
        or not _typed_equal(status, parent)
        or not _typed_equal(parent, _status_at(root, G0_T04_ANOMALY_MAIN))
    ):
        return None
    errors: list[str] = []
    if child_sha != G0_T04_ANOMALY_IMPLEMENTATION:
        errors.append("$: G0-T04 anomaly implementation identity drifted")
    changed = _g0_t03_commit_changed_paths(root, G0_T04_ANOMALY_MAIN, child_sha)
    if changed != {
        "scripts/validate_project_status.py",
        "tests/test_g0_project_status.py",
    }:
        errors.append("$: G0-T04 anomaly implementation scope drifted")
    if require_current_main:
        ok_main, main = _git(
            root, "rev-parse", "--verify", status["authoritative_main_ref"]
        )
        ok_remote, remote = _git(
            root, "rev-parse", "--verify", "refs/remotes/origin/main"
        )
        if not ok_main or not ok_remote or main != remote or main != G0_T04_ANOMALY_MAIN:
            errors.append("$: G0-T04 anomaly implementation requires exact current main")
    return errors


def _canonical_g0_t04_anomaly_bridge(
    status: dict[str, Any],
    root: Path,
    head: str,
    schema: dict[str, Any],
    *,
    require_canonical_main: bool,
) -> tuple[str | None, list[str]]:
    base_status = _is_g0_t04_anomaly_status(status)
    seal_status = _is_g0_t04_anomaly_seal_status(status)
    if not (base_status or seal_status):
        return None, []
    ok, line = _git(root, "rev-list", "--parents", "-n", "1", head)
    parts = line.split() if ok else []
    if len(parts) != 3:
        return None, []
    first_parent, governed = parts[1], parts[2]
    if base_status:
        return None, [
            "$: direct [M,C] anomaly merge is obsolete; reviewed candidate C "
            "must first be consumed by the later Stage-2 seal S"
        ]
    governed_parent = _status_at(root, G0_T04_ANOMALY_CANDIDATE)
    parent_errors = _g0_t04_anomaly_seal_parent_errors(
        status,
        governed_parent if governed_parent is not None else {},
        G0_T04_ANOMALY_CANDIDATE,
        root,
        governed,
        require_current_main=False,
    )
    errors = list(parent_errors or [])
    if first_parent != G0_T04_ANOMALY_MAIN:
        errors.append("$: G0-T04 anomaly merge first parent drifted")
    governed_status = _status_at(root, governed)
    if not _typed_equal(governed_status, status):
        errors.append("$: G0-T04 anomaly merge status drifted")
    ok_head_tree, head_tree = _git(root, "rev-parse", f"{head}^{{tree}}")
    ok_governed_tree, governed_tree = _git(
        root, "rev-parse", f"{governed}^{{tree}}"
    )
    if (
        not ok_head_tree
        or not ok_governed_tree
        or head_tree != governed_tree
    ):
        errors.append("$: G0-T04 anomaly merge tree must equal Stage-2 seal S")
    if require_canonical_main:
        ok_main, main = _git(
            root, "rev-parse", "--verify", status["authoritative_main_ref"]
        )
        ok_remote, remote = _git(
            root, "rev-parse", "--verify", "refs/remotes/origin/main"
        )
        if not ok_main or not ok_remote or main != remote or main != head:
            errors.append("$: G0-T04 anomaly merge requires exact current main")
    return (None, errors) if errors else (governed, [])


def _canonical_g0_t04_post_merge_repair_bridge(
    status: dict[str, Any],
    root: Path,
    head: str,
    schema: dict[str, Any],
    *,
    require_canonical_main: bool,
) -> tuple[str | None, list[str]]:
    """Recognize only a standard [exact F, exact F-rooted repair] merge."""
    if not _is_g0_t04_anomaly_seal_status(status) or head == G0_T04_ANOMALY_MERGE:
        return None, []
    ok_head, head_line = _git(root, "rev-list", "--parents", "-n", "1", head)
    head_parts = head_line.split() if ok_head else []
    if len(head_parts) != 3:
        return None, []
    first_parent, repair_parent = head_parts[1], head_parts[2]
    ok_lineage, lineage_text = _git(
        root,
        "rev-list",
        "--first-parent",
        f"{G0_T04_ANOMALY_MERGE}..{repair_parent}",
    )
    lineage = lineage_text.splitlines() if ok_lineage else []
    owns_route = first_parent == G0_T04_ANOMALY_MERGE or (
        bool(lineage) and lineage[0] == repair_parent
    )
    if not owns_route:
        return None, []

    errors: list[str] = []
    if first_parent != G0_T04_ANOMALY_MERGE:
        errors.append(
            "$: G0-T04 post-merge repair merge first parent must be exact F"
        )
    if not lineage or lineage[0] != repair_parent:
        errors.append(
            "$: G0-T04 post-merge repair merge second parent is not rooted at exact F"
        )
    for index, repair_sha in enumerate(lineage):
        expected_parent = (
            lineage[index + 1]
            if index + 1 < len(lineage)
            else G0_T04_ANOMALY_MERGE
        )
        ok_repair, repair_line = _git(
            root, "rev-list", "--parents", "-n", "1", repair_sha
        )
        if (
            (repair_line.split() if ok_repair else [])
            != [repair_sha, expected_parent]
            or not _typed_equal(_status_at(root, repair_sha), status)
        ):
            errors.append(
                "$: G0-T04 post-merge repair merge requires a status-identical "
                "single-parent second-parent lineage"
            )
            break

    changed = _g0_t03_commit_changed_paths(
        root, G0_T04_ANOMALY_MERGE, repair_parent
    )
    if (
        changed is None
        or not changed
        or not changed.issubset(G0_T04_ANOMALY_POST_MERGE_REPAIR_ALLOWED)
    ):
        errors.append(
            "$: G0-T04 post-merge repair merge cumulative allowlist drifted"
        )

    ok_f, f_line = _git(
        root, "rev-list", "--parents", "-n", "1", G0_T04_ANOMALY_MERGE
    )
    ok_f_tree, f_tree = _git(
        root, "rev-parse", f"{G0_T04_ANOMALY_MERGE}^{{tree}}"
    )
    ok_seal_tree, seal_tree = _git(
        root, "rev-parse", f"{G0_T04_ANOMALY_SEAL}^{{tree}}"
    )
    if (
        (f_line.split() if ok_f else [])
        != [
            G0_T04_ANOMALY_MERGE,
            G0_T04_ANOMALY_MAIN,
            G0_T04_ANOMALY_SEAL,
        ]
        or not ok_f_tree
        or not ok_seal_tree
        or f_tree != seal_tree
    ):
        errors.append("$: exact G0-T04 anomaly merge F topology drifted")

    governed_f, f_errors = _canonical_g0_t04_anomaly_bridge(
        status,
        root,
        G0_T04_ANOMALY_MERGE,
        schema,
        require_canonical_main=False,
    )
    errors.extend(f_errors)
    if governed_f != G0_T04_ANOMALY_SEAL:
        errors.append("$: exact G0-T04 anomaly merge F is not canonical")

    for relative in (
        G0_T04_ANOMALY_RECEIPT_PATH,
        G0_T04_ANOMALY_SEAL_PATH,
        PACKAGE_A_MANIFEST_PATH,
        PACKAGE_A_SCHEMA_PATH,
    ):
        ok_f_blob, f_blob = _git(
            root, "rev-parse", f"{G0_T04_ANOMALY_MERGE}:{relative}"
        )
        ok_repair_blob, repair_blob = _git(
            root, "rev-parse", f"{repair_parent}:{relative}"
        )
        if not ok_f_blob or not ok_repair_blob or repair_blob != f_blob:
            errors.append(
                "$: G0-T04 post-merge repair merge immutable blob drifted: "
                f"{relative}"
            )
    if _git(
        root, "cat-file", "-e", f"{repair_parent}:{PACKAGE_A_ACTIVATION_PATH}"
    )[0]:
        errors.append(
            "$: false Package A activation reappeared in repair merge"
        )

    governed_status = _status_at(root, repair_parent)
    if not _typed_equal(governed_status, status):
        errors.append(
            "$: G0-T04 post-merge repair merge status must equal its second parent"
        )
    ok_head_tree, head_tree = _git(root, "rev-parse", f"{head}^{{tree}}")
    ok_repair_tree, repair_tree = _git(
        root, "rev-parse", f"{repair_parent}^{{tree}}"
    )
    if (
        not ok_head_tree
        or not ok_repair_tree
        or head_tree != repair_tree
    ):
        errors.append(
            "$: G0-T04 post-merge repair merge tree must equal its second parent"
        )
    if require_canonical_main:
        ok_main, main = _git(
            root, "rev-parse", "--verify", status["authoritative_main_ref"]
        )
        ok_remote, remote = _git(
            root, "rev-parse", "--verify", "refs/remotes/origin/main"
        )
        if not ok_main or not ok_remote or main != remote or main != head:
            errors.append(
                "$: G0-T04 post-merge repair merge requires exact local/fetched main"
            )
    return (None, errors) if errors else (repair_parent, [])


def _g0_t04_failed_merge_errors(
    root: Path, schema: dict[str, Any]
) -> list[str]:
    """Bind the exact ordinary PR #14 merge before permitting recovery."""
    errors: list[str] = []
    accepted = _status_at(root, G0_T04_CLOSURE_SHA)
    merged = _status_at(root, G0_T04_FAILED_MAIN_SHA)
    if (
        type(accepted) is not dict
        or type(merged) is not dict
        or not _is_g0_t04_accepted_status(accepted)
        or not _typed_equal(merged, accepted)
    ):
        errors.append("$: G0-T04 failed merge status or accepted closure is inexact")
        return errors
    governed, bridge_errors = _canonical_g0_merge_bridge(
        accepted,
        root,
        G0_T04_FAILED_MAIN_SHA,
        schema,
        require_canonical_main=False,
    )
    errors.extend(bridge_errors)
    if governed != G0_T04_CLOSURE_SHA:
        errors.append("$: G0-T04 failed main is not the exact ordinary accepted merge")
    ok_parents, parents_text = _git(
        root, "rev-list", "--parents", "-n", "1", G0_T04_FAILED_MAIN_SHA
    )
    if (parents_text.split() if ok_parents else []) != [
        G0_T04_FAILED_MAIN_SHA,
        G0_T04_FAILED_MAIN_FIRST_PARENT,
        G0_T04_FAILED_MAIN_SECOND_PARENT,
    ]:
        errors.append("$: G0-T04 failed merge has substituted or swapped parents")
    ok_tree, tree = _git(root, "rev-parse", f"{G0_T04_FAILED_MAIN_SHA}^{{tree}}")
    if not ok_tree or tree != G0_T04_FAILED_MAIN_TREE:
        errors.append("$: G0-T04 failed merge tree drifted")
    return errors


def _g0_t04_recovery_parent_errors(
    status: dict[str, Any],
    parent: dict[str, Any],
    parent_sha: str | None,
    root: Path | None,
    child_sha: str | None,
    *,
    require_current_main: bool = True,
) -> list[str] | None:
    if not _is_g0_t04_post_merge_recovery_status(status):
        return None
    if root is None or parent_sha is None or child_sha is None:
        return ["$: G0-T04 merged-main recovery requires repository-bound lineage"]
    errors: list[str] = []
    if _is_g0_t04_post_merge_recovery_status(parent):
        ok_parents, parents_text = _git(
            root, "rev-list", "--parents", "-n", "1", child_sha
        )
        if (
            not _typed_equal(status, parent)
            or (parents_text.split() if ok_parents else [])
            != [child_sha, parent_sha]
            or not _is_ancestor(root, G0_T04_FAILED_MAIN_SHA, parent_sha)
        ):
            errors.append(
                "$: G0-T04 recovery follow-up must preserve exact status on a single-parent lineage"
            )
    else:
        if parent_sha != G0_T04_FAILED_MAIN_SHA:
            return [
                "$: G0-T04 merged-main recovery must be rooted at the exact failed main"
            ]
        projected = json.loads(json.dumps(status))
        projected["active_tasks"][0]["transition"] = {
            "from": "awaiting_review",
            "to": "accepted_pending_merge",
        }
        projected["blockers"] = []
        if not _typed_equal(projected, parent):
            errors.append(
                "$: G0-T04 recovery may only add the exact failed-run blocker and self-transition"
            )
        ok_parents, parents_text = _git(
            root, "rev-list", "--parents", "-n", "1", child_sha
        )
        if (parents_text.split() if ok_parents else []) != [
            child_sha,
            G0_T04_FAILED_MAIN_SHA,
        ]:
            errors.append(
                "$: initial G0-T04 recovery must directly follow the exact failed main"
            )
    schema = _schema_at(root, child_sha)
    if type(schema) is not dict:
        errors.append("$: G0-T04 recovery schema is unreadable")
    else:
        errors.extend(_g0_t04_failed_merge_errors(root, schema))
    errors.extend(_g0_t04_recovery_receipt_errors(root, child_sha))
    changed = _g0_t03_commit_changed_paths(
        root, G0_T04_FAILED_MAIN_SHA, child_sha
    )
    if (
        changed is None
        or not G0_T04_RECOVERY_REQUIRED_PATHS.issubset(changed)
        or not changed.issubset(G0_T04_RECOVERY_ALLOWED_PATHS)
    ):
        errors.append("$: G0-T04 recovery changed paths violate the exact allowlist")
    for path in (PACKAGE_A_MANIFEST_PATH, PACKAGE_A_SCHEMA_PATH):
        ok_failed, failed_blob = _git(
            root, "rev-parse", f"{G0_T04_FAILED_MAIN_SHA}:{path}"
        )
        ok_child, child_blob = _git(root, "rev-parse", f"{child_sha}:{path}")
        if not ok_failed or not ok_child or failed_blob != child_blob:
            errors.append(f"$: G0-T04 recovery changed immutable Package A artifact {path}")
    if require_current_main:
        ok_main, main_sha = _git(
            root, "rev-parse", "--verify", status["authoritative_main_ref"]
        )
        ok_remote, remote_sha = _git(
            root, "rev-parse", "--verify", "refs/remotes/origin/main"
        )
        main_matches = (
            ok_main
            and ok_remote
            and main_sha == remote_sha == G0_T04_FAILED_MAIN_SHA
        )
        if ok_main and ok_remote and main_sha == remote_sha and not main_matches:
            main_status = _status_at(root, main_sha)
            main_schema = _schema_at(root, main_sha)
            if type(main_status) is dict and type(main_schema) is dict:
                governed, bridge_errors = _canonical_g0_t04_recovery_bridge(
                    main_status,
                    root,
                    main_sha,
                    main_schema,
                    require_canonical_main=False,
                )
                main_matches = (
                    governed is not None
                    and not bridge_errors
                    and _is_ancestor(root, child_sha, governed)
                )
        if not main_matches:
            errors.append(
                "$: G0-T04 recovery requires the exact failed main on local/fetched authoritative main"
            )
    return errors


def _canonical_g0_t04_recovery_bridge(
    status: dict[str, Any],
    root: Path,
    head: str,
    schema: dict[str, Any],
    *,
    require_canonical_main: bool,
) -> tuple[str | None, list[str]]:
    """Accept only [failed main, status-identical recovery] with second-parent tree."""
    if not _is_g0_t04_post_merge_recovery_status(status):
        return None, []
    ok_parents, parents_text = _git(root, "rev-list", "--parents", "-n", "1", head)
    parts = parents_text.split() if ok_parents else []
    if len(parts) != 3:
        return None, []
    first_parent, governed_parent = parts[1], parts[2]
    errors: list[str] = []
    if first_parent != G0_T04_FAILED_MAIN_SHA:
        errors.append(
            "$: G0-T04 recovery merge first parent is not the exact failed main"
        )
    ok_origin, origin_url = _git(root, "remote", "get-url", "origin")
    if not ok_origin or _github_repository_identity(origin_url) != LEDGER_REPOSITORY:
        errors.append("$: G0-T04 recovery merge requires the canonical repository")
    if require_canonical_main:
        ok_main, main_sha = _git(
            root, "rev-parse", "--verify", status["authoritative_main_ref"]
        )
        ok_remote, remote_sha = _git(
            root, "rev-parse", "--verify", "refs/remotes/origin/main"
        )
        if (
            not ok_main
            or not ok_remote
            or main_sha != remote_sha
            or main_sha != head
        ):
            errors.append(
                "$: G0-T04 recovery merge requires exact local/fetched main"
            )
    ok_lineage, lineage_text = _git(
        root,
        "rev-list",
        "--first-parent",
        f"{G0_T04_FAILED_MAIN_SHA}..{governed_parent}",
    )
    lineage = lineage_text.splitlines() if ok_lineage else []
    if not lineage or lineage[0] != governed_parent:
        errors.append("$: G0-T04 recovery second parent is not a strict repair lineage")
    for index, repair_sha in enumerate(lineage):
        ok_repair, repair_parents_text = _git(
            root, "rev-list", "--parents", "-n", "1", repair_sha
        )
        expected_parent = (
            lineage[index + 1]
            if index + 1 < len(lineage)
            else G0_T04_FAILED_MAIN_SHA
        )
        if (
            (repair_parents_text.split() if ok_repair else [])
            != [repair_sha, expected_parent]
            or not _typed_equal(_status_at(root, repair_sha), status)
        ):
            errors.append(
                "$: G0-T04 recovery requires status-identical single-parent repair lineage"
            )
            break
    errors.extend(_g0_t04_failed_merge_errors(root, schema))
    errors.extend(_g0_t04_recovery_receipt_errors(root, governed_parent))
    changed = _g0_t03_commit_changed_paths(
        root, G0_T04_FAILED_MAIN_SHA, governed_parent
    )
    if (
        changed is None
        or not G0_T04_RECOVERY_REQUIRED_PATHS.issubset(changed)
        or not changed.issubset(G0_T04_RECOVERY_ALLOWED_PATHS)
    ):
        errors.append("$: G0-T04 recovery changed paths violate the exact allowlist")
    if not _typed_equal(_status_at(root, governed_parent), status):
        errors.append("$: G0-T04 recovery merge status must equal its second parent")
    ok_head_tree, head_tree = _git(root, "rev-parse", f"{head}^{{tree}}")
    ok_parent_tree, parent_tree = _git(root, "rev-parse", f"{governed_parent}^{{tree}}")
    if not ok_head_tree or not ok_parent_tree or head_tree != parent_tree:
        errors.append("$: G0-T04 recovery merge tree must equal its second parent")
    for path in (PACKAGE_A_MANIFEST_PATH, PACKAGE_A_SCHEMA_PATH):
        ok_failed, failed_blob = _git(
            root, "rev-parse", f"{G0_T04_FAILED_MAIN_SHA}:{path}"
        )
        ok_head, head_blob = _git(root, "rev-parse", f"{head}:{path}")
        if not ok_failed or not ok_head or failed_blob != head_blob:
            errors.append(f"$: G0-T04 recovery merge changed immutable Package A artifact {path}")
    if errors:
        return None, errors
    return governed_parent, []


def _g0_t02_recovery_parent_errors(
    status: dict[str, Any],
    parent: dict[str, Any],
    parent_sha: str | None,
    root: Path | None,
    child_sha: str | None,
    *,
    require_failed_main: bool = True,
) -> list[str] | None:
    if not _is_g0_t02_post_merge_recovery_status(status):
        return None
    if root is None or child_sha is None or parent_sha is None:
        return ["$: post-merge CI recovery requires repository-bound parent evidence"]
    errors: list[str] = []
    parent_is_recovery = _is_g0_t02_post_merge_recovery_status(parent)
    if parent_is_recovery:
        ok, parents_text = _git(root, "rev-list", "--parents", "-n", "1", child_sha)
        parts = parents_text.split() if ok else []
        if not _typed_equal(status, parent) or len(parts) != 2 or parts[1] != parent_sha:
            errors.append("$: post-merge CI recovery follow-up must preserve status on a single-parent lineage")
        if not _is_ancestor(root, G0_T02_FAILED_MAIN_SHA, parent_sha):
            errors.append("$: post-merge CI recovery follow-up is not rooted at the exact failed main subject")
        return errors
    if parent_sha != G0_T02_FAILED_MAIN_SHA:
        return ["$: post-merge CI recovery must be rooted at the exact failed authoritative main subject"]
    projected = dict(status)
    projected["active_tasks"] = [dict(status["active_tasks"][0])]
    projected["active_tasks"][0]["transition"] = {"from": "awaiting_review", "to": "accepted_pending_merge"}
    projected["blockers"] = []
    if not _typed_equal(projected, parent):
        errors.append("$: post-merge CI recovery may only add the exact failure record and recovery transition")
    ok_lineage, lineage_text = _git(root, "rev-list", "--first-parent", f"{parent_sha}..{child_sha}")
    lineage = lineage_text.splitlines() if ok_lineage else []
    if not lineage or lineage[0] != child_sha:
        errors.append("$: post-merge CI recovery lineage is unavailable")
    for index, recovery_sha in enumerate(lineage):
        ok_recovery_parents, recovery_parents_text = _git(root, "rev-list", "--parents", "-n", "1", recovery_sha)
        recovery_parts = recovery_parents_text.split() if ok_recovery_parents else []
        expected_parent = lineage[index + 1] if index + 1 < len(lineage) else parent_sha
        if (
            len(recovery_parts) != 2
            or recovery_parts[1] != expected_parent
            or not _typed_equal(_status_at(root, recovery_sha), status)
        ):
            errors.append("$: post-merge CI recovery must be a status-identical single-parent lineage")
            break
    if require_failed_main:
        ok_main, main_sha = _git(root, "rev-parse", "--verify", status["authoritative_main_ref"])
        ok_remote, remote_sha = _git(root, "rev-parse", "--verify", "refs/remotes/origin/main")
        main_matches = ok_main and ok_remote and main_sha == remote_sha == G0_T02_FAILED_MAIN_SHA
        if ok_main and ok_remote and main_sha == remote_sha and main_sha != G0_T02_FAILED_MAIN_SHA:
            ok_main_parents, main_parents_text = _git(root, "rev-list", "--parents", "-n", "1", main_sha)
            main_parts = main_parents_text.split() if ok_main_parents else []
            ok_main_tree, main_tree = _git(root, "rev-parse", f"{main_sha}^{{tree}}")
            recovery_head = main_parts[2] if len(main_parts) == 3 else ""
            ok_recovery_tree, recovery_tree = _git(root, "rev-parse", f"{recovery_head}^{{tree}}")
            main_matches = (
                len(main_parts) == 3
                and main_parts[1] == G0_T02_FAILED_MAIN_SHA
                and _is_ancestor(root, child_sha, recovery_head)
                and ok_main_tree
                and ok_recovery_tree
                and main_tree == recovery_tree
                and _typed_equal(_status_at(root, recovery_head), status)
                and _typed_equal(_status_at(root, main_sha), status)
            )
            if not main_matches:
                final_close_status = _status_at(root, main_sha)
                final_close_schema = _schema_at(root, main_sha)
                if (
                    type(final_close_status) is dict
                    and type(final_close_schema) is dict
                    and _is_ancestor(root, child_sha, G0_T02_RECOVERY_MAIN_SHA)
                ):
                    governed_close, close_errors = _canonical_g0_t02_final_close_bridge(
                        final_close_status,
                        root,
                        main_sha,
                        final_close_schema,
                        require_canonical_main=False,
                    )
                    main_matches = governed_close is not None and not close_errors
            if not main_matches and main_sha == G0_T03_FAILED_MAIN_SHA:
                g0_t03_status = _status_at(root, main_sha)
                if type(g0_t03_status) is dict:
                    governed_g0_t03, g0_t03_errors = _canonical_g0_t03_merge_bridge(
                        g0_t03_status,
                        root,
                        main_sha,
                        require_canonical_main=False,
                    )
                    main_matches = governed_g0_t03 is not None and not g0_t03_errors
            if not main_matches and main_sha == G0_T03_RECOVERY_MERGE_SHA:
                recovery_merge_status = _status_at(root, main_sha)
                if type(recovery_merge_status) is dict:
                    governed_recovery, recovery_merge_errors = _canonical_g0_t03_recovery_merge_bridge(
                        recovery_merge_status,
                        root,
                        main_sha,
                        require_canonical_main=False,
                    )
                    main_matches = governed_recovery is not None and not recovery_merge_errors
            if not main_matches and main_sha not in {
                G0_T02_FAILED_MAIN_SHA,
                G0_T03_FAILED_MAIN_SHA,
                G0_T03_RECOVERY_MERGE_SHA,
            }:
                closure_status = _status_at(root, main_sha)
                if type(closure_status) is dict:
                    governed_closure, closure_errors = _canonical_g0_t03_recovery_closure_bridge(
                        closure_status,
                        root,
                        main_sha,
                        require_canonical_main=False,
                    )
                    main_matches = governed_closure is not None and not closure_errors
                    if not main_matches:
                        main_matches = _g0_t03_recovery_closure_ancestor(root, main_sha) is not None
        if not main_matches and ok_main and ok_remote and main_sha == remote_sha:
            main_matches = _g0_t03_final_close_main_matches(root, main_sha)
        if not main_matches:
            errors.append("$: post-merge CI recovery requires the exact failed main, recovery merge, or canonical final-close recovery on local/fetched main")
    child_schema = _schema_at(root, child_sha)
    if child_schema is None:
        errors.append("$: post-merge CI recovery schema is unreadable")
    else:
        governed, bridge_errors = _canonical_g0_merge_bridge(parent, root, parent_sha, child_schema, require_canonical_main=False)
        errors.extend(bridge_errors)
        if governed is None:
            errors.append("$: post-merge CI recovery parent is not the canonical failed G0 merge bridge")
    return errors


def _canonical_g0_merge_bridge(
    status: dict[str, Any],
    root: Path,
    head: str,
    schema: dict[str, Any],
    *,
    require_canonical_main: bool = True,
) -> tuple[str | None, list[str]]:
    status_errors = _schema_errors(status, schema, schema)
    if status_errors:
        return None, [f"$: canonical G0 merge bridge status fails structural validation: {item}" for item in status_errors]
    task = status["active_tasks"][0]
    if (
        _is_g0_t04_g4_status(status)
        and task["state"] == "closed"
        and task["transition"]
        == {"from": "merged_verified", "to": "closed"}
    ):
        ok_terminal, terminal_parents_text = _git(
            root,
            "rev-list",
            "--parents",
            "-n",
            "1",
            head,
        )
        terminal_parts = (
            terminal_parents_text.split() if ok_terminal else []
        )
        if len(terminal_parts) == 3:
            close_sha = terminal_parts[2]
            terminal_errors = _g0_t04_g4_terminal_bridge_route_errors(
                status,
                root,
                head,
                close_sha,
                require_canonical_main=require_canonical_main,
            )
            if terminal_errors:
                return None, terminal_errors
            return close_sha, []
    repair_governed, repair_errors = (
        _canonical_g0_t04_post_merge_repair_bridge(
            status,
            root,
            head,
            schema,
            require_canonical_main=require_canonical_main,
        )
    )
    if repair_governed is not None or repair_errors:
        return repair_governed, repair_errors
    if _is_g0_t04_anomaly_status(status) or _is_g0_t04_anomaly_seal_status(status):
        governed, anomaly_errors = _canonical_g0_t04_anomaly_bridge(
            status,
            root,
            head,
            schema,
            require_canonical_main=require_canonical_main,
        )
        if governed is not None or anomaly_errors:
            return governed, anomaly_errors
    if _is_g0_t04_post_merge_recovery_status(status):
        governed, recovery_errors = _canonical_g0_t04_recovery_bridge(
            status,
            root,
            head,
            schema,
            require_canonical_main=require_canonical_main,
        )
        if governed is not None or recovery_errors:
            return governed, recovery_errors
    reconciliation_governed, reconciliation_errors = (
        _canonical_g0_t03_status_reconciliation_bridge(
            status,
            root,
            head,
            require_canonical_main=require_canonical_main,
        )
    )
    if reconciliation_governed is not None or reconciliation_errors:
        return reconciliation_governed, reconciliation_errors
    planning_governed, planning_errors = _canonical_g0_t03_planning_handoff_bridge(
        status,
        root,
        head,
        require_canonical_main=require_canonical_main,
    )
    if planning_governed is not None or planning_errors:
        return planning_governed, planning_errors
    if _is_g0_t03_recovery_merge_recovery_status(status):
        ok_parents, parents_text = _git(root, "rev-list", "--parents", "-n", "1", head)
        if len(parents_text.split() if ok_parents else []) == 3:
            return _canonical_g0_t03_recovery_closure_bridge(
                status,
                root,
                head,
                require_canonical_main=require_canonical_main,
            )
    if _is_g0_t03_final_closed_status(status) or _is_g0_t03_final_close_recovery_status(status):
        return _canonical_g0_t03_final_close_bridge(
            status,
            root,
            head,
            schema,
            require_canonical_main=require_canonical_main,
        )
    if _is_g0_t02_final_closed_status(status):
        return _canonical_g0_t02_final_close_bridge(
            status,
            root,
            head,
            schema,
            require_canonical_main=require_canonical_main,
        )
    if _is_g0_t03_post_merge_recovery_status(status) and head == G0_T03_RECOVERY_MERGE_SHA:
        return _canonical_g0_t03_recovery_merge_bridge(
            status,
            root,
            head,
            require_canonical_main=require_canonical_main,
        )
    if _is_g0_t03_accepted_status(status):
        return _canonical_g0_t03_merge_bridge(
            status,
            root,
            head,
            require_canonical_main=require_canonical_main,
        )
    if task["state"] != "accepted_pending_merge" or not task["task_id"].startswith("G0-"):
        return None, []
    ok, parents_text = _git(root, "rev-list", "--parents", "-n", "1", head)
    parts = parents_text.split() if ok else []
    if len(parts) != 3:
        return None, []
    first_parent, governed_parent = parts[1], parts[2]
    ok_main, main_sha = _git(root, "rev-parse", "--verify", status["authoritative_main_ref"])
    ok_remote, remote_main_sha = _git(root, "rev-parse", "--verify", "refs/remotes/origin/main")
    ok_origin, origin_url = _git(root, "remote", "get-url", "origin")
    errors: list[str] = []
    if require_canonical_main and (
        not ok_main
        or not ok_remote
        or not _typed_equal(main_sha, head)
        or not _typed_equal(remote_main_sha, head)
        or not ok_origin
        or _github_repository_identity(origin_url) != LEDGER_REPOSITORY
    ):
        errors.append("$: canonical G0 merge bridge requires exact local/fetched main in the canonical repository")
    elif not require_canonical_main and (not ok_origin or _github_repository_identity(origin_url) != LEDGER_REPOSITORY):
        errors.append("$: canonical G0 merge bridge requires the canonical repository")
    recovery_bridge = _is_g0_t02_post_merge_recovery_status(status)
    g0_t04_g4_bridge = _is_g0_t04_g4_status(status)
    expected_first_parent = (
        G0_T02_FAILED_MAIN_SHA
        if recovery_bridge
        else (
            G0_T04_G4_PREMATURE_MAIN
            if g0_t04_g4_bridge
            else status["evidence"]["authorization_baseline_sha"]
        )
    )
    if not _typed_equal(first_parent, expected_first_parent):
        errors.append("$: canonical G0 merge bridge first parent is not the authoritative prior main")
    if task["task_id"] == BOOTSTRAP_TASK and not _typed_equal(governed_parent, G0_GOVERNED_PARENT_SHA):
        errors.append("$: canonical G0-T01 merge bridge second parent is not the immutable governed task head")
    governed_status, governed_errors = _committed_status_errors(root, governed_parent, schema, use_current_schema=True)
    errors.extend(governed_errors)
    if governed_status is None or not _typed_equal(status, governed_status):
        errors.append("$: canonical G0 merge bridge status must exactly equal its governed second parent")
    if g0_t04_g4_bridge:
        errors.extend(_g0_t04_g4_merge_topology_errors(root, head))
    ok_head_tree, head_tree = _git(root, "rev-parse", f"{head}^{{tree}}")
    ok_parent_tree, parent_tree = _git(root, "rev-parse", f"{governed_parent}^{{tree}}")
    if not ok_head_tree or not ok_parent_tree or not _typed_equal(head_tree, parent_tree):
        errors.append("$: canonical G0 merge bridge tree must exactly equal its governed second parent")
    ok_governed_parents, governed_parents_text = _git(root, "rev-list", "--parents", "-n", "1", governed_parent)
    governed_parts = governed_parents_text.split() if ok_governed_parents else []
    if recovery_bridge:
        failed_status, failed_errors = _committed_status_errors(root, G0_T02_FAILED_MAIN_SHA, schema, use_current_schema=True)
        errors.extend(failed_errors)
        recovery_errors = (
            _g0_t02_recovery_parent_errors(
                status,
                failed_status,
                G0_T02_FAILED_MAIN_SHA,
                root,
                governed_parent,
                require_failed_main=False,
            )
            if failed_status is not None
            else ["$: post-merge CI recovery failed-main status is unreadable"]
        )
        errors.extend(recovery_errors or [])
    else:
        candidate = status["evidence"]["candidate"]["commit_sha"]
        if type(candidate) is not str or len(governed_parts) != 2 or not _typed_equal(governed_parts[1], candidate):
            errors.append("$: canonical G0 merge bridge second parent must directly close the exact reviewed candidate")
        else:
            candidate_status, candidate_errors = _committed_status_errors(root, candidate, schema, use_current_schema=True)
            errors.extend(candidate_errors)
            if candidate_errors or not _subject_status_matches(status, candidate_status, "awaiting_review"):
                errors.append("$: canonical G0 merge bridge candidate identity is invalid")
    if errors:
        return None, errors
    return governed_parent, []


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
    task = status["active_tasks"][0]
    errors.extend(_package_a_persistence_errors(status, root, head))
    errors.extend(_g0_t04_g4_route_errors(status, root, head))
    if (
        task["task_id"] == "G0-T04"
        and task["state"] == "awaiting_review"
        and not _is_g0_t04_g4_status(status)
    ):
        errors.extend(_g0_t04_package_a_changed_path_errors(root, head))
    governed_history_head, bridge_errors = _canonical_g0_merge_bridge(status, root, head, schema)
    errors.extend(bridge_errors)
    ok, parents = _git(root, "rev-list", "--parents", "-n", "1", head)
    parent_parts = parents.split() if ok else []
    if governed_history_head is not None:
        pass
    elif len(parent_parts) < 2:
        errors.append("$: repository HEAD has no direct first parent canonical history")
    else:
        parent_status, parent_schema_errors = _committed_status_errors(root, parent_parts[1], schema, use_current_schema=True)
        errors.extend(parent_schema_errors)
        if not parent_schema_errors and parent_status is not None:
            errors.extend(_parent_status_errors(status, parent_status, parent_parts[1], root, head))
            errors.extend(_schema_authority_continuity_errors(status, parent_status, parent_parts[1], root))
    if type(status.get("transition_ledger")) is dict:
        control_path = root / SCHEMA_CONTROL_PATH
        ok, tree_entry = _git(root, "ls-tree", "HEAD", "--", SCHEMA_CONTROL_PATH)
        fields = tree_entry.split(None, 3) if ok else []
        if control_path.is_symlink() or len(fields) != 4 or fields[0] not in {"100644", "100755"} or fields[1] != "blob":
            errors.append("$.schema_migration_control: canonical control must be a committed regular Git blob")
    errors.extend(_history_errors(root, governed_history_head or head, baseline, schema))

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
    if task["transition"] == {"from": "closed", "to": "authorized"}:
        direct_parent = parent_parts[1] if len(parent_parts) >= 2 else None
        g4_authorization = (
            _is_g0_t04_g4_status(status)
            and head == G0_T04_G4_AUTHORIZATION
            and direct_parent == G0_T04_G4_BASELINE
            and len(parent_parts) == 3
            and parent_parts[2] == G0_T04_G4_BLOCKED_MAIN
            and remote_main_ok
            and main_sha == remote_main_sha == G0_T04_G4_BLOCKED_MAIN
        )
        if not g4_authorization and (
            not remote_main_ok
            or main_sha != remote_main_sha
            or direct_parent != remote_main_sha
        ):
            errors.append("$: inter-task handoff must start from the exact fetched authoritative main close")
    if finalization is not None:
        if merged is None or not _is_ancestor(root, merged, finalization):
            errors.append("$.evidence.finalization.commit_sha: merged-main is not an ancestor of finalization")
        if not phase_status_matches(finalization, "merged_verified"):
            errors.append("$.evidence.finalization.commit_sha: commit is not the matching finalization phase")
    errors.extend(_schema_migration_final_route_errors(status, root))
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
