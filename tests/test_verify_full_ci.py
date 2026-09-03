from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location(
    "verify_full_ci",
    ROOT / "scripts" / "verify_full_ci.py",
)
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


def test_python_runtime_is_exact_cross_platform_published_identity() -> None:
    assert (ROOT / ".python-version").read_text(encoding="utf-8").strip() == "3.12.10"


def test_python_dependency_files_are_recursive_exact_locks() -> None:
    locked = VERIFY.exact_requirements(ROOT / "requirements-dev.txt")
    assert locked["fastapi"] == "0.116.1"
    assert locked["httpx"] == "0.28.1"
    assert locked["pytest"] == "8.4.2"
    assert locked["pytest-xdist"] == "3.8.0"
    assert locked["uvicorn"] == "0.35.0"
    assert len(locked) == 24


@pytest.mark.parametrize(
    "line",
    [
        "example>=1",
        "example",
        "example==1==2",
        "example~=1",
        "example==1",
        "example==1 --hash=sha256:not-a-digest",
    ],
)
def test_floating_or_malformed_python_dependency_fails_closed(
    tmp_path: Path,
    line: str,
) -> None:
    lock = tmp_path / "requirements.txt"
    lock.write_text(line + "\n", encoding="utf-8")
    with pytest.raises(VERIFY.VerificationError):
        VERIFY.exact_requirements(lock)


def test_frontend_lock_uses_only_official_registry_and_integrity() -> None:
    lock = json.loads(
        (ROOT / "frontend" / "package-lock.json").read_text(encoding="utf-8")
    )
    resolved = [
        record
        for identity, record in lock["packages"].items()
        if identity and record.get("resolved")
    ]
    assert resolved
    assert all(
        record["resolved"].startswith("https://registry.npmjs.org/")
        and record.get("integrity")
        for record in resolved
    )


def test_fixture_inventory_and_digests_are_frozen() -> None:
    VERIFY.validate_fixtures_scope_and_secrets()


@pytest.mark.parametrize(
    "secret",
    [
        b"-----BEGIN " + b"PRIVATE KEY-----",
        b"access_" + b'token="abcdefghijklmnop"',
        b"eyJabcdefghijklmnop."
        + b"qrstuvwxyzABCDEF."
        + b"ghijklmnopqrstuv",
    ],
)
def test_secret_patterns_cover_private_keys_assignments_and_jwts(
    secret: bytes,
) -> None:
    assert any(pattern.search(secret) for pattern in VERIFY.SECRET_PATTERNS)


def test_offline_guard_rejects_non_loopback_network(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("G1_CI_SHARD_COUNT", "4")
    monkeypatch.setenv("G1_CI_SHARD_INDEX", "3")
    env = VERIFY.offline_environment(tmp_path)
    guard = (tmp_path / "sitecustomize.py").read_text(encoding="utf-8")
    assert "offline verification forbids network access" in guard
    assert env["G1_CI_WORKERS"] == "4"
    assert env["G1_CI_SHARD_COUNT"] == "1"
    assert env["G1_CI_SHARD_INDEX"] == "0"
    assert env["PIP_NO_INDEX"] == "1"
    assert env["npm_config_offline"] == "true"


def test_ci_requires_mechanically_probed_os_isolation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CI", "true")
    monkeypatch.delenv("G1_OS_EGRESS_ISOLATED", raising=False)
    with pytest.raises(
        VERIFY.VerificationError,
        match="mechanically probed OS egress isolation",
    ):
        VERIFY.validate_runtime_and_dependencies()


def test_parallel_full_suite_is_bounded_and_complete(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("G1_CI_WORKERS", "4")
    monkeypatch.setenv("G1_CI_SHARD_COUNT", "4")
    monkeypatch.setenv("G1_CI_SHARD_INDEX", "2")
    assert VERIFY.pytest_parallel_args() == [
        "-n",
        "4",
        "--dist",
        "worksteal",
        "-p",
        "g1_shard_plugin",
    ]
    monkeypatch.setenv("G1_CI_WORKERS", "9")
    with pytest.raises(VERIFY.VerificationError):
        VERIFY.pytest_parallel_args()


def test_four_deterministic_shards_are_disjoint_and_complete() -> None:
    nodeids = [f"tests/test_example.py::test_case_{number}" for number in range(100)]
    shards = [
        {nodeid for nodeid in nodeids if VERIFY.shard_index(nodeid, 4) == index}
        for index in range(4)
    ]
    assert set().union(*shards) == set(nodeids)
    assert sum(len(shard) for shard in shards) == len(nodeids)
    assert all(shards)


def test_all_fail_closed_flags_are_mandatory(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["verify_full_ci.py", "--offline"])
    with pytest.raises(SystemExit):
        VERIFY.parse_args()


def test_workflow_has_cross_platform_workers_and_stable_aggregate() -> None:
    workflow = (
        ROOT / ".github" / "workflows" / "g0-exact-head.yml"
    ).read_text(encoding="utf-8")
    assert "ubuntu-24.04" in workflow
    assert "windows-2022" in workflow
    assert "timeout-minutes: 20" in workflow
    assert "timeout-minutes: 15" in workflow
    assert "name: G0 / exact-head" in workflow
    assert "needs:\n      - full-ci" in workflow
    assert "verify_full_ci.py --offline --fail-closed --require-transport" in workflow
    assert "--require-hashes" in workflow
    assert "G1_OS_EGRESS_ISOLATED: \"1\"" in workflow
    assert "G1_CI_SHARD_COUNT: \"4\"" in workflow
    assert "G1_CI_SHARD_INDEX: ${{ matrix.shard }}" in workflow
    assert "shard-${{ matrix.shard }}" in workflow
    assert 'sudo "$tool" -I OUTPUT 1 -j G1T01_OUT' in workflow
    assert "Set-NetFirewallProfile" in workflow
    assert "Python egress probe unexpectedly connected" in workflow
    assert "node -e" in workflow
    assert "curl child-process egress probe unexpectedly connected" in workflow
    assert "always() && runner.os == 'Linux'" in workflow
    assert "always() && runner.os == 'Windows'" in workflow
    assert workflow.index("Install exact Python runtime") < workflow.index(
        "Verify exact subject and run identity"
    )
    assert "secrets." not in workflow
