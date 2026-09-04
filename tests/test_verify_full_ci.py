from __future__ import annotations

from collections import Counter
import importlib.util
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
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
    monkeypatch.delenv("G1_CI_WORKERS", raising=False)
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
    monkeypatch.delenv("G1_CI_WORKERS", raising=False)

    env = VERIFY.offline_environment(tmp_path)

    assert env["G1_CI_SHARD_COUNT"] == "1"
    assert env["G1_CI_SHARD_INDEX"] == "0"
    assert env["G1_CI_WORKERS"] == "8"
    assert VERIFY.pytest_parallel_args(env)[:2] == ["-n", "8"]


def test_offline_guard_preserves_explicit_local_worker_override(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("G1_CI_SHARD_COUNT", raising=False)
    monkeypatch.delenv("G1_CI_SHARD_INDEX", raising=False)
    monkeypatch.setenv("G1_CI_WORKERS", "2")

    env = VERIFY.offline_environment(tmp_path)

    assert env["G1_CI_SHARD_COUNT"] == "1"
    assert env["G1_CI_WORKERS"] == "2"
    assert VERIFY.pytest_parallel_args(env)[:2] == ["-n", "2"]


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

    assert VERIFY.pytest_parallel_args(
        {
            "G1_CI_WORKERS": "8",
            "G1_CI_SHARD_COUNT": "1",
            "G1_CI_SHARD_INDEX": "0",
        }
    )[:2] == ["-n", "8"]


def test_one_and_four_shard_plugin_selections_are_complete_and_disjoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    nodeids = [
        *[
            f"{prefix}[sample]"
            for prefix, _ in VERIFY.SHARD_COST_HINTS
        ],
        *[
            f"tests/test_other_{number % 11}.py::test_case_{number:03}"
            for number in range(576)
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
    assert selected == sorted(
        nodeids,
        key=lambda nodeid: (-VERIFY.shard_cost(nodeid), nodeid),
    )
    assert deselected == []

    shards: list[list[str]] = []
    assignments = VERIFY.balanced_shard_assignments(nodeids, 4)
    for index in range(4):
        selected, deselected = select(4, index)
        shards.append(selected)
        assert selected
        assert all(assignments[nodeid] == index for nodeid in selected)
        assert selected == [
            nodeid for nodeid in nodeids if assignments[nodeid] == index
        ]
        assert len(selected) + len(deselected) == len(nodeids)

    selected_counts = Counter(nodeid for shard in shards for nodeid in shard)
    assert set(selected_counts) == set(nodeids)
    assert set(selected_counts.values()) == {1}
    assert all(
        set(left).isdisjoint(right)
        for index, left in enumerate(shards)
        for right in shards[index + 1 :]
    )
    weighted_loads = [
        sum(VERIFY.shard_cost(nodeid) for nodeid in shard)
        for shard in shards
    ]
    assert max(weighted_loads) - min(weighted_loads) <= 1
    slow_counts = [
        sum(VERIFY.shard_cost(nodeid) > 1 for nodeid in shard)
        for shard in shards
    ]
    assert max(slow_counts) - min(slow_counts) <= 2

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


def test_actual_collection_spreads_every_slow_governance_cost_hint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--collect-only",
            "-q",
            "tests/test_g0_project_status.py",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    nodeids = [
        line.replace("\\", "/")
        for line in result.stdout.splitlines()
        if line.replace("\\", "/").startswith("tests/") and "::" in line
    ]
    assert len(nodeids) >= 480
    assert len({prefix for prefix, _ in VERIFY.SHARD_COST_HINTS}) == len(
        VERIFY.SHARD_COST_HINTS
    )
    assert {cost for _, cost in VERIFY.SHARD_COST_HINTS} == {2, 4, 8}
    assert all(
        any(nodeid.startswith(prefix) for nodeid in nodeids)
        for prefix, _ in VERIFY.SHARD_COST_HINTS
    )

    plugin: dict[str, object] = {}
    exec(VERIFY.SHARD_PLUGIN, plugin)
    monkeypatch.setenv("G1_CI_SHARD_COUNT", "1")
    monkeypatch.setenv("G1_CI_SHARD_INDEX", "0")
    local_items = [SimpleNamespace(nodeid=nodeid) for nodeid in nodeids]
    plugin["pytest_collection_modifyitems"](
        SimpleNamespace(
            hook=SimpleNamespace(pytest_deselected=lambda items: None)
        ),
        local_items,
    )
    local_nodeids = [item.nodeid for item in local_items]
    assert local_nodeids == sorted(
        nodeids,
        key=lambda nodeid: (-VERIFY.shard_cost(nodeid), nodeid),
    )
    assert {item.nodeid for item in local_items} == set(nodeids)

    assignments = VERIFY.balanced_shard_assignments(nodeids, 4)
    shards = [
        {nodeid for nodeid in nodeids if assignments[nodeid] == index}
        for index in range(4)
    ]
    selected_counts = Counter(nodeid for shard in shards for nodeid in shard)
    assert set(selected_counts) == set(nodeids)
    assert set(selected_counts.values()) == {1}
    assert all(shards)
    assert all(
        left.isdisjoint(right)
        for index, left in enumerate(shards)
        for right in shards[index + 1 :]
    )

    weighted_loads = [
        sum(VERIFY.shard_cost(nodeid) for nodeid in shard)
        for shard in shards
    ]
    slow_loads = [
        sum(
            VERIFY.shard_cost(nodeid)
            for nodeid in shard
            if VERIFY.shard_cost(nodeid) > 1
        )
        for shard in shards
    ]
    assert max(weighted_loads) - min(weighted_loads) <= 1
    assert max(slow_loads) - min(slow_loads) <= 2


def test_complete_suite_passes_outer_shard_identity_to_every_child(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[list[str], dict[str, str], float | None]] = []
    monkeypatch.setenv("G1_CI_SHARD_COUNT", "4")
    monkeypatch.setenv("G1_CI_SHARD_INDEX", "2")
    monkeypatch.setenv("G1_CI_WORKERS", "3")
    monkeypatch.setattr(VERIFY.shutil, "which", lambda executable: executable)

    def fake_run(
        command: list[str],
        env: dict[str, str],
        deadline: float | None = None,
    ) -> str:
        calls.append((command, env, deadline))
        if "--collect-only" in command:
            return "6 tests collected"
        return ""

    monkeypatch.setattr(VERIFY, "run", fake_run)

    VERIFY.run_complete_suite()

    assert calls
    assert all(env["G1_CI_SHARD_COUNT"] == "4" for _, env, _ in calls)
    assert all(env["G1_CI_SHARD_INDEX"] == "2" for _, env, _ in calls)
    deadlines = {deadline for _, _, deadline in calls}
    assert len(deadlines) == 1
    assert None not in deadlines
    full_pytest = next(
        command
        for command, _, _ in calls
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


def test_main_uses_one_deadline_for_the_entire_verifier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: list[float] = []
    monkeypatch.setattr(VERIFY, "parse_args", lambda: None)
    monkeypatch.setattr(VERIFY, "new_deadline", lambda: 123.0)
    monkeypatch.setattr(
        VERIFY,
        "validate_runtime_and_dependencies",
        lambda deadline: observed.append(deadline),
    )
    monkeypatch.setattr(
        VERIFY,
        "validate_fixtures_scope_and_secrets",
        lambda deadline: observed.append(deadline),
    )
    monkeypatch.setattr(
        VERIFY,
        "run_complete_suite",
        lambda deadline: observed.append(deadline),
    )

    assert VERIFY.main() == 0
    assert observed == [123.0, 123.0, 123.0]


def test_full_ci_deadline_is_exactly_870_seconds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    now = [100.0]
    monkeypatch.setattr(VERIFY.time, "monotonic", lambda: now[0])

    deadline = VERIFY.new_deadline()

    assert VERIFY.FULL_CI_TIMEOUT_SECONDS == 870
    assert deadline == 970.0
    assert VERIFY.remaining_seconds(deadline) == 870.0
    now[0] = deadline
    with pytest.raises(VERIFY.VerificationError, match="exceeded 870s limit"):
        VERIFY.remaining_seconds(deadline)


def test_run_rejects_non_utf8_output() -> None:
    with pytest.raises(VERIFY.VerificationError, match="not valid UTF-8"):
        VERIFY.run(
            [sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'\\xff')"],
            os.environ.copy(),
        )


def test_run_emits_chinese_git_diff_as_strict_utf8_under_ascii_code_page(
    tmp_path: Path,
) -> None:
    tracked = tmp_path / "example.txt"
    tracked.write_text("baseline\n", encoding="utf-8")
    freeze_fixture_repository(tmp_path, tracked.name)
    tracked.write_text("中文差异\n", encoding="utf-8")
    driver = (
        "import importlib.util, os, pathlib, sys; "
        "path=pathlib.Path(sys.argv[1]); "
        "spec=importlib.util.spec_from_file_location('verify_full_ci', path); "
        "module=importlib.util.module_from_spec(spec); "
        "spec.loader.exec_module(module); "
        "module.ROOT=pathlib.Path(sys.argv[2]); "
        "module.run(['git', 'diff', '--binary', 'HEAD', '--'], os.environ.copy())"
    )
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "ascii:strict"

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            driver,
            str(ROOT / "scripts" / "verify_full_ci.py"),
            str(tmp_path),
        ],
        env=env,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    output = result.stdout.decode("utf-8", errors="strict")
    assert "+ git diff --binary HEAD --\n" in output
    assert "+中文差异" in output
    assert result.stderr == b""


def test_utf8_output_writer_rejects_unencodable_text() -> None:
    stream = io.TextIOWrapper(io.BytesIO(), encoding="ascii", errors="strict")

    with pytest.raises(
        VERIFY.VerificationError,
        match="cannot be encoded as UTF-8",
    ):
        VERIFY.write_utf8(stream, "\udcff")


@pytest.mark.parametrize("resists_term", [False, True])
def test_timeout_terminates_and_reaps_ready_descendant_process_tree(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    resists_term: bool,
) -> None:
    pid_file = tmp_path / "descendant.pid"
    ready_file = tmp_path / "ready"
    child_code = (
        "import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); "
        "time.sleep(60)"
        if resists_term
        else "import time; time.sleep(60)"
    )
    parent_code = (
        "from pathlib import Path; import subprocess, sys, time; "
        f"child=subprocess.Popen([sys.executable, '-c', {child_code!r}]); "
        f"Path({str(pid_file)!r}).write_text(str(child.pid), encoding='ascii'); "
        f"Path({str(ready_file)!r}).write_text('ready', encoding='ascii'); "
        "time.sleep(60)"
    )

    def timeout_only_after_ready(deadline: float) -> float:
        ready_deadline = time.monotonic() + 5
        while not ready_file.exists() and time.monotonic() < ready_deadline:
            time.sleep(0.01)
        assert ready_file.read_text(encoding="ascii") == "ready"
        return 0.05

    monkeypatch.setattr(VERIFY, "remaining_seconds", timeout_only_after_ready)

    with pytest.raises(VERIFY.VerificationError, match="verification deadline"):
        VERIFY.run(
            [sys.executable, "-c", parent_code],
            os.environ.copy(),
            1.0,
        )

    descendant_pid = int(pid_file.read_text(encoding="ascii"))

    def descendant_is_running() -> bool:
        if os.name == "nt":
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {descendant_pid}", "/FO", "CSV", "/NH"],
                check=False,
                capture_output=True,
            )
            return str(descendant_pid).encode("ascii") in result.stdout
        try:
            os.kill(descendant_pid, 0)
        except ProcessLookupError:
            return False
        return True

    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and descendant_is_running():
        time.sleep(0.05)
    if descendant_is_running():
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(descendant_pid), "/T", "/F"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            os.kill(descendant_pid, signal.SIGKILL)
        pytest.fail("descendant survived process-tree cleanup")


@pytest.mark.skipif(os.name == "nt", reason="POSIX process-group regression")
def test_posix_cleanup_handles_exited_root_with_descendant_holding_pipe(
    tmp_path: Path,
) -> None:
    pid_file = tmp_path / "descendant.pid"
    ready_file = tmp_path / "ready"
    child_code = "import time; time.sleep(60)"
    parent_code = (
        "from pathlib import Path; import subprocess, sys; "
        f"child=subprocess.Popen([sys.executable, '-c', {child_code!r}]); "
        f"Path({str(pid_file)!r}).write_text(str(child.pid), encoding='ascii'); "
        f"Path({str(ready_file)!r}).write_text('ready', encoding='ascii')"
    )
    process = subprocess.Popen(
        [sys.executable, "-c", parent_code],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    ready_deadline = time.monotonic() + 5
    while not ready_file.exists() and time.monotonic() < ready_deadline:
        time.sleep(0.01)
    assert ready_file.read_text(encoding="ascii") == "ready"
    process.wait(timeout=5)
    assert process.poll() == 0

    VERIFY.terminate_process_tree(process, platform="posix")

    descendant_pid = int(pid_file.read_text(encoding="ascii"))
    with pytest.raises(ProcessLookupError):
        os.kill(descendant_pid, 0)


def test_windows_cleanup_requests_recursive_tree_kill(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []

    class FakeProcess:
        pid = 4242
        reaped = False

        def poll(self) -> int | None:
            return 0 if self.reaped else None

        def communicate(self, timeout: float) -> tuple[bytes, None]:
            assert 0 < timeout <= VERIFY.PROCESS_CLEANUP_TIMEOUT_SECONDS
            self.reaped = True
            return b"", None

        def kill(self) -> None:
            pytest.fail("taskkill success must not need root-only fallback")

    def fake_taskkill(command: list[str], **kwargs: object) -> SimpleNamespace:
        calls.append(command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(VERIFY.subprocess, "run", fake_taskkill)
    VERIFY.terminate_process_tree(FakeProcess(), platform="nt")

    assert calls == [["taskkill", "/PID", "4242", "/T", "/F"]]


def test_windows_taskkill_nonzero_is_not_accepted_as_tree_cleanup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeProcess:
        pid = 4242
        killed = False

        def poll(self) -> None:
            return None

        def kill(self) -> None:
            self.killed = True

        def communicate(self, timeout: float) -> tuple[bytes, None]:
            assert self.killed
            assert 0 < timeout <= VERIFY.PROCESS_CLEANUP_TIMEOUT_SECONDS
            return b"", None

    monkeypatch.setattr(
        VERIFY.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=1),
    )
    process = FakeProcess()

    with pytest.raises(VERIFY.VerificationError, match="cleanup exited 1"):
        VERIFY.terminate_process_tree(process, platform="nt")


def test_windows_job_binding_and_close_failures_are_fail_closed() -> None:
    class BindingFailureKernel:
        def AssignProcessToJobObject(self, handle: object, process: object) -> int:
            return 0

        def CloseHandle(self, handle: object) -> int:
            return 1

    class CloseFailureKernel:
        def AssignProcessToJobObject(self, handle: object, process: object) -> int:
            return 1

        def CloseHandle(self, handle: object) -> int:
            return 0

    process = SimpleNamespace(_handle=99)

    with pytest.raises(VERIFY.VerificationError, match="could not be bound"):
        VERIFY.WindowsKillJob(BindingFailureKernel(), 1).assign(process)
    with pytest.raises(VERIFY.VerificationError, match="could not be closed"):
        VERIFY.WindowsKillJob(CloseFailureKernel(), 1).close()


def test_windows_job_is_configured_kill_on_close() -> None:
    observed_flags: list[int] = []

    class FakeKernel:
        def CreateJobObjectW(self, security: object, name: object) -> int:
            return 7

        def SetInformationJobObject(
            self,
            handle: object,
            information_class: int,
            information: object,
            size: int,
        ) -> int:
            assert handle == 7
            assert information_class == VERIFY.WINDOWS_JOB_OBJECT_EXTENDED_LIMIT_INFORMATION
            observed_flags.append(
                information._obj.BasicLimitInformation.LimitFlags
            )
            return 1

        def CloseHandle(self, handle: object) -> int:
            assert handle == 7
            return 1

    job = VERIFY.create_windows_kill_job(FakeKernel())
    job.close()

    assert observed_flags == [VERIFY.WINDOWS_JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE]


@pytest.mark.skipif(os.name != "nt", reason="real Windows Job Object regression")
def test_windows_job_closes_descendant_after_command_root_exits(
    tmp_path: Path,
) -> None:
    pid_file = tmp_path / "independent-descendant.pid"
    ready_file = tmp_path / "independent-ready"
    child_code = "import time; time.sleep(60)"
    parent_code = (
        "from pathlib import Path; import subprocess, sys; "
        f"child=subprocess.Popen([sys.executable, '-c', {child_code!r}], "
        "stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); "
        f"Path({str(pid_file)!r}).write_text(str(child.pid), encoding='ascii'); "
        f"Path({str(ready_file)!r}).write_text('ready', encoding='ascii')"
    )

    VERIFY.run(
        [sys.executable, "-c", parent_code],
        os.environ.copy(),
        time.monotonic() + 10,
    )

    assert ready_file.read_text(encoding="ascii") == "ready"
    descendant_pid = pid_file.read_text(encoding="ascii")
    result = subprocess.run(
        ["tasklist", "/FI", f"PID eq {descendant_pid}", "/FO", "CSV", "/NH"],
        check=False,
        capture_output=True,
    )
    assert descendant_pid.encode("ascii") not in result.stdout


def test_keyboard_interrupt_cleans_process_tree_before_propagating(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cleaned: list[tuple[object, object | None]] = []
    assigned: list[object] = []

    class FakeProcess:
        _handle = 99
        returncode = None

        def communicate(self, timeout: float) -> tuple[bytes, None]:
            raise KeyboardInterrupt

    class FakeWindowsJob:
        closed = False

        def assign(self, target: object) -> None:
            assert target._handle == 99
            assigned.append(target)

        def close(self) -> None:
            self.closed = True

    process = FakeProcess()
    windows_job = FakeWindowsJob()

    def fake_terminate(target: object, **kwargs: object) -> None:
        job = kwargs.get("windows_job")
        cleaned.append((target, job))
        if job is not None:
            job.close()

    monkeypatch.setattr(VERIFY.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(VERIFY, "create_windows_kill_job", lambda: windows_job)
    monkeypatch.setattr(
        VERIFY,
        "terminate_process_tree",
        fake_terminate,
    )

    with pytest.raises(KeyboardInterrupt):
        VERIFY.run(["command"], {}, time.monotonic() + 1)
    expected_job = windows_job if os.name == "nt" else None
    assert cleaned == [(process, expected_job)]
    assert assigned == ([process] if os.name == "nt" else [])
    assert windows_job.closed is (os.name == "nt")


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
