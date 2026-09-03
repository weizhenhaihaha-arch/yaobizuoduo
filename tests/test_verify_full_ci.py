from __future__ import annotations

from collections import Counter
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

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


def freeze_fixture_repository(root: Path, relative: str) -> None:
    for command in (
        ["git", "init", "--quiet"],
        ["git", "config", "core.autocrlf", "false"],
        ["git", "config", "user.name", "Fixture Test"],
        ["git", "config", "user.email", "fixture@example.invalid"],
        ["git", "add", relative],
        ["git", "commit", "--quiet", "-m", "freeze fixture"],
    ):
        subprocess.run(command, cwd=root, check=True, capture_output=True)
    assert not subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


@pytest.mark.parametrize("newline", [b"\n", b"\r\n"])
def test_text_fixture_digest_accepts_clean_lf_and_crlf(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    newline: bytes,
) -> None:
    relative = "fixtures/example.json"
    fixture = tmp_path / relative
    fixture.parent.mkdir(parents=True)
    fixture.write_bytes('{"value": "中文"}'.encode("utf-8") + newline)
    freeze_fixture_repository(tmp_path, relative)
    monkeypatch.setattr(VERIFY, "ROOT", tmp_path)
    monkeypatch.setattr(
        VERIFY,
        "FIXTURE_DIGESTS",
        {relative: "dda00999e6a5c839ac6eed03f75c9e9b93c9eb1a9c5514a3eaddb9ee4ba36746"},
    )

    VERIFY.validate_fixture_digests()


def test_dirty_text_fixture_content_tampering_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    relative = "fixtures/example.json"
    fixture = tmp_path / relative
    fixture.parent.mkdir(parents=True)
    fixture.write_bytes(b'{"value": 1}\n')
    freeze_fixture_repository(tmp_path, relative)
    monkeypatch.setattr(VERIFY, "ROOT", tmp_path)
    monkeypatch.setattr(
        VERIFY,
        "FIXTURE_DIGESTS",
        {relative: "dbbd9c92f0a9fc8ec5968c1d825d1f3779567052b3286c91ed34f060ebe2f466"},
    )
    VERIFY.validate_fixture_digests()

    fixture.write_bytes(b'{"value": 2}\n')

    assert subprocess.run(
        ["git", "status", "--porcelain", "--", relative],
        cwd=tmp_path,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    with pytest.raises(VERIFY.VerificationError, match="fixture digest drifted"):
        VERIFY.validate_fixture_digests()


def test_invalid_utf8_fixture_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    relative = "fixtures/example.json"
    fixture = tmp_path / relative
    fixture.parent.mkdir(parents=True)
    fixture.write_bytes(b"\xff\xfe")
    monkeypatch.setattr(VERIFY, "ROOT", tmp_path)
    monkeypatch.setattr(VERIFY, "FIXTURE_DIGESTS", {relative: "0" * 64})

    with pytest.raises(VERIFY.VerificationError, match="valid UTF-8"):
        VERIFY.validate_fixture_digests()


@pytest.mark.parametrize("mutation", ["added", "deleted"])
def test_fixture_inventory_addition_or_deletion_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    relative = "fixtures/example.json"
    fixture = tmp_path / relative
    fixture.parent.mkdir(parents=True)
    fixture.write_bytes(b'{"value": 1}\n')
    monkeypatch.setattr(VERIFY, "ROOT", tmp_path)
    monkeypatch.setattr(
        VERIFY,
        "FIXTURE_DIGESTS",
        {relative: "dbbd9c92f0a9fc8ec5968c1d825d1f3779567052b3286c91ed34f060ebe2f466"},
    )
    if mutation == "added":
        (fixture.parent / "extra.json").write_text("{}\n", encoding="utf-8")
    else:
        fixture.unlink()

    with pytest.raises(VERIFY.VerificationError, match="fixture inventory drifted"):
        VERIFY.validate_fixture_digests()


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


def test_offline_guard_preserves_outer_shard_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("G1_CI_SHARD_COUNT", "4")
    monkeypatch.setenv("G1_CI_SHARD_INDEX", "3")
    env = VERIFY.offline_environment(tmp_path)
    guard = (tmp_path / "sitecustomize.py").read_text(encoding="utf-8")
    assert "offline verification forbids network access" in guard
    assert env["G1_CI_WORKERS"] == "4"
    assert env["G1_CI_SHARD_COUNT"] == "4"
    assert env["G1_CI_SHARD_INDEX"] == "3"
    assert env["PIP_NO_INDEX"] == "1"
    assert env["npm_config_offline"] == "true"


def test_offline_guard_defaults_to_one_complete_local_shard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("G1_CI_SHARD_COUNT", raising=False)
    monkeypatch.delenv("G1_CI_SHARD_INDEX", raising=False)

    env = VERIFY.offline_environment(tmp_path)

    assert env["G1_CI_SHARD_COUNT"] == "1"
    assert env["G1_CI_SHARD_INDEX"] == "0"


def execute_offline_guard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    socket_module: SimpleNamespace,
) -> None:
    VERIFY.offline_environment(tmp_path)
    monkeypatch.setitem(sys.modules, "socket", socket_module)
    guard = (tmp_path / "sitecustomize.py").read_text(encoding="utf-8")
    exec(compile(guard, str(tmp_path / "sitecustomize.py"), "exec"), {})


def test_offline_guard_without_af_unix_allows_loopback_and_denies_external(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeSocket:
        def __init__(self, family: str) -> None:
            self.family = family
            self.connected: list[object] = []

        def connect(self, address: object) -> str:
            self.connected.append(address)
            return "connected"

    socket_module = SimpleNamespace(socket=FakeSocket)
    execute_offline_guard(tmp_path, monkeypatch, socket_module)
    client = FakeSocket("AF_INET")

    assert client.connect(("127.0.0.1", 8000)) == "connected"
    assert client.connect(("::1", 8000)) == "connected"
    assert client.connect(("localhost", 8000)) == "connected"
    with pytest.raises(OSError, match="offline verification forbids network access"):
        client.connect(("example.com", 443))
    assert client.connected == [
        ("127.0.0.1", 8000),
        ("::1", 8000),
        ("localhost", 8000),
    ]


def test_offline_guard_with_af_unix_allows_unix_and_denies_external(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeSocket:
        def __init__(self, family: str) -> None:
            self.family = family
            self.connected: list[object] = []

        def connect(self, address: object) -> str:
            self.connected.append(address)
            return "connected"

    socket_module = SimpleNamespace(socket=FakeSocket, AF_UNIX="AF_UNIX")
    execute_offline_guard(tmp_path, monkeypatch, socket_module)
    unix_client = FakeSocket("AF_UNIX")
    internet_client = FakeSocket("AF_INET")

    assert unix_client.connect("/tmp/local.sock") == "connected"
    with pytest.raises(OSError, match="offline verification forbids network access"):
        internet_client.connect(("203.0.113.1", 443))
    assert unix_client.connected == ["/tmp/local.sock"]
    assert internet_client.connected == []


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


def test_one_and_four_shard_plugin_selections_are_complete_and_disjoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    nodeids = [
        *[
            f"tests/test_slow_governance.py::test_case_{number:03}"
            for number in range(479)
        ],
        *[
            f"tests/test_other_{number % 11}.py::test_case_{number:03}"
            for number in range(136)
        ],
    ]
    plugin: dict[str, object] = {}
    exec(VERIFY.SHARD_PLUGIN, plugin)
    partition = plugin["pytest_collection_modifyitems"]

    def select(count: int, index: int) -> tuple[list[str], list[str]]:
        monkeypatch.setenv("G1_CI_SHARD_COUNT", str(count))
        monkeypatch.setenv("G1_CI_SHARD_INDEX", str(index))
        items = [SimpleNamespace(nodeid=nodeid) for nodeid in nodeids]
        deselected: list[SimpleNamespace] = []

        partition(
            SimpleNamespace(
                hook=SimpleNamespace(
                    pytest_deselected=lambda items: deselected.extend(items)
                )
            ),
            items,
        )
        return (
            [item.nodeid for item in items],
            [item.nodeid for item in deselected],
        )

    selected, deselected = select(1, 0)
    assert selected == nodeids
    assert deselected == []

    shards: list[list[str]] = []
    assignments = VERIFY.balanced_shard_assignments(nodeids, 4)
    for index in range(4):
        selected, deselected = select(4, index)
        shards.append(selected)
        assert selected
        assert all(assignments[nodeid] == index for nodeid in selected)
        assert len(selected) + len(deselected) == len(nodeids)

    selected_counts = Counter(nodeid for shard in shards for nodeid in shard)
    assert set(selected_counts) == set(nodeids)
    assert set(selected_counts.values()) == {1}
    assert all(
        set(left).isdisjoint(right)
        for index, left in enumerate(shards)
        for right in shards[index + 1 :]
    )
    assert max(map(len, shards)) - min(map(len, shards)) <= 1
    slow_counts = [
        sum(nodeid.startswith("tests/test_slow_governance.py::") for nodeid in shard)
        for shard in shards
    ]
    assert max(slow_counts) - min(slow_counts) <= 1

    reversed_assignments = VERIFY.balanced_shard_assignments(
        list(reversed(nodeids)),
        4,
    )
    assert reversed_assignments == assignments


@pytest.mark.parametrize("count", [0, 9])
def test_balanced_shards_reject_invalid_count(count: int) -> None:
    with pytest.raises(VERIFY.VerificationError, match="shard count"):
        VERIFY.balanced_shard_assignments(["tests/test_example.py::test_one"], count)


def test_balanced_shards_reject_duplicate_nodeids() -> None:
    nodeid = "tests/test_example.py::test_one"
    with pytest.raises(VERIFY.VerificationError, match="duplicate node IDs"):
        VERIFY.balanced_shard_assignments([nodeid, nodeid], 4)


def test_complete_suite_passes_outer_shard_identity_to_every_child(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[list[str], dict[str, str]]] = []
    monkeypatch.setenv("G1_CI_SHARD_COUNT", "4")
    monkeypatch.setenv("G1_CI_SHARD_INDEX", "2")
    monkeypatch.setenv("G1_CI_WORKERS", "3")
    monkeypatch.setattr(VERIFY.shutil, "which", lambda executable: executable)

    def fake_run(command: list[str], env: dict[str, str]) -> str:
        calls.append((command, env))
        if "--collect-only" in command:
            return "6 tests collected"
        return ""

    monkeypatch.setattr(VERIFY, "run", fake_run)

    VERIFY.run_complete_suite()

    assert calls
    assert all(env["G1_CI_SHARD_COUNT"] == "4" for _, env in calls)
    assert all(env["G1_CI_SHARD_INDEX"] == "2" for _, env in calls)
    full_pytest = next(
        command
        for command, _ in calls
        if command[:3] == [VERIFY.sys.executable, "-m", "pytest"]
        and "g1_shard_plugin" in command
    )
    assert full_pytest[-6:] == [
        "-n",
        "3",
        "--dist",
        "worksteal",
        "-p",
        "g1_shard_plugin",
    ]


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
