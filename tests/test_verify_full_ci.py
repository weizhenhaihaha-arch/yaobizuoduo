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


def test_python_dependency_files_are_recursive_exact_locks() -> None:
    locked = VERIFY.exact_requirements(ROOT / "requirements-dev.txt")
    assert locked["fastapi"] == "0.116.1"
    assert locked["httpx"] == "0.28.1"
    assert locked["pytest"] == "8.4.2"
    assert locked["uvicorn"] == "0.35.0"
    assert len(locked) == 22


@pytest.mark.parametrize(
    "line",
    ["example>=1", "example", "example==1==2", "example~=1"],
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


def test_offline_guard_rejects_non_loopback_network(tmp_path: Path) -> None:
    env = VERIFY.offline_environment(tmp_path)
    guard = (tmp_path / "sitecustomize.py").read_text(encoding="utf-8")
    assert "offline verification forbids network access" in guard
    assert env["PIP_NO_INDEX"] == "1"
    assert env["npm_config_offline"] == "true"


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
    assert "name: G0 / exact-head" in workflow
    assert "needs:\n      - full-ci" in workflow
    assert "verify_full_ci.py --offline --fail-closed --require-transport" in workflow
    assert "secrets." not in workflow
