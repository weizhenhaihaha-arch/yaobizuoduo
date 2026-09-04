#!/usr/bin/env python3
"""Run the one fail-closed, offline G1-T01 backend/frontend verification entrypoint."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[1]
PYTHON_PIN = ROOT / ".python-version"
NODE_PIN = ROOT / ".nvmrc"
API_LOCK = ROOT / "requirements-api.txt"
DEV_LOCK = ROOT / "requirements-dev.txt"
PACKAGE_JSON = ROOT / "frontend" / "package.json"
PACKAGE_LOCK = ROOT / "frontend" / "package-lock.json"
MANIFEST = ROOT / "governance" / "packages" / "package-a.manifest.json"
STATUS = ROOT / "PROJECT_STATUS.yaml"
TRANSPORT_TEST = "tests/test_m5_transport.py"
FULL_CI_TIMEOUT_SECONDS = 870
PROCESS_TERM_GRACE_SECONDS = 1
PROCESS_CLEANUP_TIMEOUT_SECONDS = 5
WINDOWS_JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
WINDOWS_JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
WINDOWS_JOB_LAUNCHER = """\
import json
from pathlib import Path
import subprocess
import sys
import time

gate = Path(sys.argv[1])
deadline = time.monotonic() + 30
while not gate.exists():
    if time.monotonic() >= deadline:
        raise SystemExit(125)
    time.sleep(0.01)
command = json.loads(sys.argv[2])
raise SystemExit(subprocess.run(command, check=False).returncode)
"""
FIXTURE_DIGESTS = {
    "fixtures/g0/adversarial_mutations.json": "936890388414d8a2acfb839e33147c96a2cdc97c4b874f07aecc235e5f5c51e9",
    "fixtures/g0/valid_awaiting_review.json": "56623d63602464b66a439827f22e6f0a98f718671dc531b934164a9671786684",
    "fixtures/m1/binance_cases.json": "bf71c1a5478aab2c7ccbe289f517c408aa9a3669c313cf7d434200db4098634d",
    "fixtures/m1/okx_cases.json": "4bc22f128046851a8f336dacc333ef8cf3b3552edaf8862082c219489237a781",
    "fixtures/m3/lifecycle_cases.json": "c5de9f1b12ebe7769c93e235080d40f135c68832a1b069d5367bbaa044d765d0",
    "fixtures/m4/replay_cases.json": "2a7c6251c3169a7ad938eb09af52aae555e73703f77281c9c199cb029202955f",
    "fixtures/m7/notification_cases.json": "47c6e48454f03fef4b902ce12a1b94fc7ecfe3e883d011e5b6a3809a203e2429",
    "fixtures/m7/operational_health_cases.json": "12da0c5249b0fc8d7976831ae9f3b94c176175bea60dd5979b6880bf186a6de2",
}
SECRET_PATTERNS = (
    re.compile(rb"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
    re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    re.compile(rb"\bsk-[A-Za-z0-9]{32,}\b"),
    re.compile(rb"\beyJ[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}\b"),
    re.compile(
        rb"(?i)\b(?:api[_-]?key|access[_-]?token|secret|password)\b"
        rb"\s*[:=]\s*['\"][A-Za-z0-9_./+=-]{16,}['\"]"
    ),
)
REQUIREMENT_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9_.-]+)==(?P<version>[^\s]+)"
    r"(?P<hashes>(?:\s+--hash=sha256:[0-9a-f]{64})+)$"
)
# Coarse relative costs from the exact Generation 9 collection sampled with the
# pinned pytest/xdist stack.  Prefixes intentionally cover parametrized cases;
# unlisted and newly added tests retain cost 1 and can never be omitted.
SHARD_COST_HINTS = (
    ("tests/test_g0_project_status.py::test_canonical_status_and_documents_are_valid", 8),
    ("tests/test_g0_project_status.py::test_package_a_g0_t05_g3_full_lifecycle_is_reachable", 8),
    ("tests/test_g0_project_status.py::test_fresh_clone_of_exact_head_remains_valid", 8),
    ("tests/test_g0_project_status.py::test_g0_t03_recovery_closure_can_reach_merged_verified_and_closed_without_third_recovery", 8),
    ("tests/test_g0_project_status.py::test_package_a_g0_t05_g3_pr29_main_ci_recovery_and_future_merge_are_canonical", 8),
    ("tests/test_g0_project_status.py::test_g0_t04_post_merge_repair_merge_rejects_substitutions", 8),
    ("tests/test_g0_project_status.py::test_g0_t04_post_merge_repair_merge_is_canonical", 8),
    ("tests/test_g0_project_status.py::test_g0_t03_status_reconciliation_candidate_and_future_merge_validate", 8),
    ("tests/test_g0_project_status.py::test_g0_t04_post_merge_repair_rejects_scope_and_authority_drift", 8),
    ("tests/test_g0_project_status.py::test_g0_t04_generation4_terminal_main_hostiles_fail_full_validator", 8),
    ("tests/test_g0_project_status.py::test_transition_ledger_rejects_tamper_truncate_rollback_and_wrong_anchor", 8),
    ("tests/test_g0_project_status.py::test_crlf_checkout_is_portable_but_content_tampering_still_fails", 8),
    ("tests/test_g0_project_status.py::test_g0_t04_generation4_terminal_main_passes_full_canonical_validator", 8),
    ("tests/test_g0_project_status.py::test_package_a_g0_t05_g3_future_merge_passes_full_validator", 8),
    ("tests/test_g0_project_status.py::test_malformed_two_parent_status_is_rejected_without_traceback", 8),
    ("tests/test_g0_project_status.py::test_package_a_g0_t05_g3_exact_authorization_passes_route", 8),
    ("tests/test_g0_project_status.py::test_committed_schema_weakening_cannot_be_hidden_by_restore", 8),
    ("tests/test_g0_project_status.py::test_g0_t04_recovery_rejects_topology_and_evidence_substitution", 8),
    ("tests/test_g0_project_status.py::test_post_anchor_weakened_schema_float_generation_is_fatal_after_restore", 8),
    ("tests/test_g0_project_status.py::test_g0_t04_recovery_descendant_rejects_out_of_scope_path", 4),
    ("tests/test_g0_project_status.py::test_post_ledger_forged_intermediate_generation_cannot_be_laundered", 4),
    ("tests/test_g0_project_status.py::test_future_g0_t03_planning_handoff_two_parent_recovery_is_accepted", 4),
    ("tests/test_g0_project_status.py::test_exact_g0_t04_failed_main_and_recovery_record_are_accepted", 4),
    ("tests/test_g0_project_status.py::test_g0_t04_exact_merge_post_merge_repair_is_canonical", 4),
    ("tests/test_g0_project_status.py::test_g0_t03_status_reconciliation_rejects_ordinary_descendant_and_merge_drift", 4),
    ("tests/test_g0_project_status.py::test_g0_t04_pr15_pr22_stage2_seal_and_future_bridge_are_canonical", 4),
    ("tests/test_g0_project_status.py::test_exact_g0_t03_final_close_failure_record_is_accepted", 4),
    ("tests/test_g0_project_status.py::test_exact_g0_t03_recovery_merge_failure_record_is_accepted", 4),
    ("tests/test_g0_project_status.py::test_invalid_post_anchor_maturity_shape_is_terminal_after_restore", 4),
    ("tests/test_g0_project_status.py::test_exact_g0_t03_recovery_merge_bridge_is_accepted_before_generic_paths", 4),
    ("tests/test_g0_project_status.py::test_g0_t03_recovery_merge_recovery_rejects_inexact_evidence", 4),
    ("tests/test_g0_project_status.py::test_package_a_g0_t05_g3_pr29_recovery_and_future_merge_are_canonical", 4),
    ("tests/test_g0_project_status.py::test_exact_g0_t03_merge_bridge_and_detached_checkout_history_are_accepted", 4),
    ("tests/test_g0_project_status.py::test_g0_t03_failed_main_recovery_rejects_inexact_trigger", 4),
    ("tests/test_g0_project_status.py::test_exact_g0_t03_failed_main_recovery_record_is_accepted", 4),
    ("tests/test_g0_project_status.py::test_exact_failed_main_recovery_record_and_recovery_merge_are_accepted", 4),
    ("tests/test_g0_project_status.py::test_exact_g0_t04_recovery_merge_is_accepted", 4),
    ("tests/test_g0_project_status.py::test_every_intermediate_parent_status_uses_exact_current_schema_types", 4),
    ("tests/test_g0_project_status.py::test_future_g0_t03_final_close_recovery_merge_and_main_validation_succeed", 4),
    ("tests/test_g0_project_status.py::test_g0_t04_pr15_pr22_anomaly_two_stage_is_canonical", 4),
    ("tests/test_g0_project_status.py::test_exact_g0_t03_planning_handoff_merge_is_accepted_before_r_b_a_paths", 4),
    ("tests/test_g0_project_status.py::test_exact_g0_t03_recovery_closure_bridge_is_accepted_before_generic_paths", 2),
    ("tests/test_g0_project_status.py::test_g0_t02_final_close_accepts_only_strict_repair_merge", 2),
    ("tests/test_g0_project_status.py::test_exact_g0_t02_final_close_bridge_is_accepted", 2),
    ("tests/test_g0_project_status.py::test_failed_main_recovery_rejects_inexact_trigger", 2),
)
SHARD_PLUGIN = """\
import os
from scripts.verify_full_ci import balanced_shard_assignments, shard_cost

def pytest_collection_modifyitems(config, items):
    count = int(os.environ["G1_CI_SHARD_COUNT"])
    index = int(os.environ["G1_CI_SHARD_INDEX"])
    assignments = balanced_shard_assignments(
        [item.nodeid for item in items],
        count,
    )
    selected = [
        item for item in items
        if assignments[item.nodeid] == index
    ]
    if count == 1:
        selected.sort(key=lambda item: (-shard_cost(item.nodeid), item.nodeid))
    deselected = [item for item in items if item not in selected]
    if deselected:
        config.hook.pytest_deselected(items=deselected)
    items[:] = selected
"""


class VerificationError(RuntimeError):
    pass


def write_utf8(stream: object, text: str) -> None:
    """Write verifier output as strict UTF-8, independent of the host code page."""
    try:
        payload = text.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise VerificationError("verifier output cannot be encoded as UTF-8") from exc
    binary_stream = getattr(stream, "buffer", None)
    if binary_stream is not None:
        binary_stream.write(payload)
        binary_stream.flush()
        return
    try:
        stream.write(payload.decode("utf-8", errors="strict"))
        stream.flush()
    except (UnicodeDecodeError, UnicodeEncodeError) as exc:
        raise VerificationError("verifier output cannot be written as UTF-8") from exc


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if type(value) is not dict:
        raise VerificationError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def exact_requirements(path: Path) -> dict[str, str]:
    locked: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-r "):
            nested = (path.parent / line[3:].strip()).resolve()
            if nested.parent != ROOT or nested not in {API_LOCK.resolve(), DEV_LOCK.resolve()}:
                raise VerificationError(f"{path.name}: requirement include escapes the frozen locks")
            locked.update(exact_requirements(nested))
            continue
        match = REQUIREMENT_RE.fullmatch(line)
        if match is None:
            raise VerificationError(
                f"{path.name}: every dependency needs one exact == pin and SHA-256 artifact hash"
            )
        name, version = match.group("name"), match.group("version")
        key = name.lower().replace("_", "-")
        if not name or not version or key in locked:
            raise VerificationError(f"{path.name}: invalid or duplicate dependency pin")
        locked[key] = version
    return locked


def new_deadline() -> float:
    return time.monotonic() + FULL_CI_TIMEOUT_SECONDS


def remaining_seconds(deadline: float) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise VerificationError(
            f"full verification exceeded {FULL_CI_TIMEOUT_SECONDS}s limit"
        )
    return remaining


def validate_runtime_and_dependencies(deadline: float | None = None) -> None:
    deadline = new_deadline() if deadline is None else deadline
    if (
        os.environ.get("CI", "").lower() == "true"
        and os.environ.get("G1_OS_EGRESS_ISOLATED") != "1"
    ):
        raise VerificationError(
            "CI full verification requires mechanically probed OS egress isolation"
        )
    python_pin = PYTHON_PIN.read_text(encoding="utf-8").strip()
    actual_python = ".".join(str(part) for part in sys.version_info[:3])
    if actual_python != python_pin:
        raise VerificationError(f"Python runtime drift: expected {python_pin}, got {actual_python}")

    node = shutil.which("node")
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if node is None or npm is None:
        raise VerificationError("pinned Node/npm runtime is unavailable")
    node_version = run([node, "--version"], os.environ.copy(), deadline).strip().removeprefix("v")
    node_pin = NODE_PIN.read_text(encoding="utf-8").strip()
    if node_version != node_pin:
        raise VerificationError(f"Node runtime drift: expected {node_pin}, got {node_version}")

    package = read_json(PACKAGE_JSON)
    npm_pin = package.get("packageManager")
    npm_version = run([npm, "--version"], os.environ.copy(), deadline).strip()
    if npm_pin != f"npm@{npm_version}":
        raise VerificationError("npm runtime does not match packageManager identity")
    if package.get("engines") != {"node": node_pin, "npm": npm_version}:
        raise VerificationError("frontend runtime engines are not exact")
    for section in ("dependencies", "devDependencies"):
        values = package.get(section)
        if type(values) is not dict or any(
            type(version) is not str
            or version.startswith(("^", "~", ">", "<", "*"))
            for version in values.values()
        ):
            raise VerificationError(f"frontend {section} contains a floating dependency")

    locked = exact_requirements(DEV_LOCK)
    if not {"fastapi", "httpx", "pytest", "pytest-xdist", "uvicorn"}.issubset(locked):
        raise VerificationError("Python lock omits a mandatory API/test dependency")
    for name, expected in locked.items():
        try:
            actual = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError as exc:
            raise VerificationError(f"locked Python dependency is not installed: {name}") from exc
        if actual != expected:
            raise VerificationError(
                f"Python dependency drift for {name}: expected {expected}, got {actual}"
            )

    package_lock = read_json(PACKAGE_LOCK)
    if package_lock.get("lockfileVersion") != 3:
        raise VerificationError("frontend package-lock must use lockfileVersion 3")
    for identity, record in package_lock.get("packages", {}).items():
        if type(record) is not dict:
            raise VerificationError(f"invalid package-lock record: {identity}")
        resolved = record.get("resolved")
        if resolved is not None and (
            type(resolved) is not str
            or not resolved.startswith("https://registry.npmjs.org/")
        ):
            raise VerificationError(f"non-official npm registry identity: {identity}")
        if identity and resolved is not None and not record.get("integrity"):
            raise VerificationError(f"npm lock record lacks integrity: {identity}")


def canonical_text_digest(payload: bytes) -> str:
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise VerificationError("fixture must contain valid UTF-8 text") from exc
    canonical = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_fixture_digests() -> None:
    actual_fixtures = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "fixtures").rglob("*")
        if path.is_file()
    }
    if actual_fixtures != set(FIXTURE_DIGESTS):
        raise VerificationError("fixture inventory drifted")
    for relative, expected in FIXTURE_DIGESTS.items():
        actual = canonical_text_digest((ROOT / relative).read_bytes())
        if actual != expected:
            raise VerificationError(f"fixture digest drifted: {relative}")


def validate_fixtures_scope_and_secrets(deadline: float | None = None) -> None:
    deadline = new_deadline() if deadline is None else deadline
    validate_fixture_digests()
    status = read_json(STATUS)
    manifest = read_json(MANIFEST)
    task = status["active_tasks"][0]
    if task.get("task_id") != "G1-T01" or task.get("risk") != "D1":
        raise VerificationError("full CI is restricted to the frozen G1-T01 D1 card")
    card = next(
        item for item in manifest["cards"] if item.get("task_id") == "G1-T01"
    )
    baseline = status["evidence"]["authorization_baseline_sha"]
    diff = run(
        ["git", "diff", "--name-only", baseline, "--"],
        os.environ.copy(),
        deadline,
    ).splitlines()
    outside = sorted(set(diff) - set(card["allowed_paths"]))
    if outside:
        raise VerificationError("forbidden-scope paths changed: " + ", ".join(outside))
    patch = run(
        ["git", "diff", "--binary", baseline, "--"],
        os.environ.copy(),
        deadline,
    ).encode("utf-8")
    if any(pattern.search(patch) for pattern in SECRET_PATTERNS):
        raise VerificationError("candidate diff contains a secret-shaped value")


def offline_environment(directory: Path) -> dict[str, str]:
    guard = directory / "sitecustomize.py"
    guard.write_text(
        "import socket\n"
        "_original_connect = socket.socket.connect\n"
        "_af_unix = getattr(socket, 'AF_UNIX', None)\n"
        "def _offline_connect(self, address):\n"
        "    if _af_unix is not None and self.family == _af_unix:\n"
        "        return _original_connect(self, address)\n"
        "    host = address[0] if isinstance(address, tuple) and address else ''\n"
        "    if host in {'127.0.0.1', '::1', 'localhost'}:\n"
        "        return _original_connect(self, address)\n"
        "    raise OSError('offline verification forbids network access')\n"
        "socket.socket.connect = _offline_connect\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env.setdefault("G1_CI_SHARD_COUNT", "1")
    env.setdefault("G1_CI_SHARD_INDEX", "0")
    env.setdefault(
        "G1_CI_WORKERS",
        "8" if env["G1_CI_SHARD_COUNT"] == "1" else "4",
    )
    env.update(
        {
            "CI": "true",
            "NO_PROXY": "*",
            "no_proxy": "*",
            "PIP_NO_INDEX": "1",
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "npm_config_offline": "true",
            "npm_config_audit": "false",
            "npm_config_fund": "false",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPATH": os.pathsep.join(
                [str(directory), str(ROOT), env.get("PYTHONPATH", "")]
            ).rstrip(os.pathsep),
        }
    )
    return env


class WindowsKillJob:
    def __init__(self, kernel32: object, handle: object) -> None:
        self.kernel32 = kernel32
        self.handle = handle
        self.closed = False

    def assign(self, process: subprocess.Popen[bytes]) -> None:
        if not self.kernel32.AssignProcessToJobObject(
            self.handle,
            process._handle,
        ):
            raise VerificationError("Windows process could not be bound to kill-on-close job")

    def close(self) -> None:
        if self.closed:
            return
        if not self.kernel32.CloseHandle(self.handle):
            raise VerificationError("Windows kill-on-close job handle could not be closed")
        self.closed = True


def create_windows_kill_job(kernel32: object | None = None) -> WindowsKillJob:
    import ctypes
    from ctypes import wintypes

    class BasicLimitInformation(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_longlong),
            ("PerJobUserTimeLimit", ctypes.c_longlong),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class IoCounters(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_ulonglong),
            ("WriteOperationCount", ctypes.c_ulonglong),
            ("OtherOperationCount", ctypes.c_ulonglong),
            ("ReadTransferCount", ctypes.c_ulonglong),
            ("WriteTransferCount", ctypes.c_ulonglong),
            ("OtherTransferCount", ctypes.c_ulonglong),
        ]

    class ExtendedLimitInformation(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", BasicLimitInformation),
            ("IoInfo", IoCounters),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    if kernel32 is None:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
        kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        kernel32.SetInformationJobObject.argtypes = [
            wintypes.HANDLE,
            ctypes.c_int,
            wintypes.LPVOID,
            wintypes.DWORD,
        ]
        kernel32.SetInformationJobObject.restype = wintypes.BOOL
        kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL
    handle = kernel32.CreateJobObjectW(None, None)
    if not handle:
        raise VerificationError("Windows kill-on-close job could not be created")
    information = ExtendedLimitInformation()
    information.BasicLimitInformation.LimitFlags = (
        WINDOWS_JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    )
    if not kernel32.SetInformationJobObject(
        handle,
        WINDOWS_JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
        ctypes.byref(information),
        ctypes.sizeof(information),
    ):
        kernel32.CloseHandle(handle)
        raise VerificationError("Windows kill-on-close job could not be configured")
    return WindowsKillJob(kernel32, handle)


def terminate_process_tree(
    process: subprocess.Popen[bytes],
    platform: str | None = None,
    windows_job: WindowsKillJob | None = None,
) -> None:
    platform = os.name if platform is None else platform
    cleanup_deadline = time.monotonic() + PROCESS_CLEANUP_TIMEOUT_SECONDS

    def cleanup_remaining() -> float:
        remaining = cleanup_deadline - time.monotonic()
        if remaining <= 0:
            raise VerificationError("process-tree cleanup exceeded its deadline")
        return remaining

    def bounded_communicate() -> None:
        try:
            process.communicate(timeout=cleanup_remaining())
        except subprocess.TimeoutExpired as exc:
            raise VerificationError(
                "process-tree cleanup could not reap every inherited pipe"
            ) from exc

    if platform == "nt":
        if windows_job is not None:
            try:
                windows_job.close()
            except VerificationError:
                if process.poll() is None:
                    process.kill()
                bounded_communicate()
                raise
            bounded_communicate()
            if process.poll() is None:
                raise VerificationError("Windows process-tree cleanup did not reap the root")
            return
        try:
            result = subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=cleanup_remaining(),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            if process.poll() is None:
                process.kill()
            bounded_communicate()
            raise VerificationError("Windows recursive process-tree cleanup failed") from exc
        if result.returncode != 0:
            if process.poll() is None:
                process.kill()
            bounded_communicate()
            raise VerificationError(
                f"Windows recursive process-tree cleanup exited {result.returncode}"
            )
        bounded_communicate()
        if process.poll() is None:
            raise VerificationError("Windows process-tree cleanup did not reap the root")
        return

    process_group = process.pid

    def group_exists() -> bool:
        try:
            os.killpg(process_group, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        return True

    try:
        os.killpg(process_group, signal.SIGTERM)
    except ProcessLookupError:
        pass
    term_deadline = min(
        cleanup_deadline,
        time.monotonic() + PROCESS_TERM_GRACE_SECONDS,
    )
    while group_exists() and time.monotonic() < term_deadline:
        process.poll()
        time.sleep(0.01)
    if group_exists():
        try:
            os.killpg(process_group, signal.SIGKILL)
        except ProcessLookupError:
            pass
    bounded_communicate()
    while group_exists() and time.monotonic() < cleanup_deadline:
        process.poll()
        time.sleep(0.01)
    if group_exists():
        raise VerificationError("POSIX process group survived SIGKILL cleanup")


def run(command: list[str], env: dict[str, str], deadline: float | None = None) -> str:
    deadline = new_deadline() if deadline is None else deadline
    write_utf8(sys.stdout, "+ " + " ".join(command) + "\n")
    popen_options: dict[str, object] = {}
    windows_job: WindowsKillJob | None = None
    windows_job_assigned = False
    gate_directory: tempfile.TemporaryDirectory[str] | None = None
    if os.name == "nt":
        popen_options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        windows_job = create_windows_kill_job()
        gate_directory = tempfile.TemporaryDirectory(prefix="yaobizuoduo-job-gate-")
        gate = Path(gate_directory.name) / "assigned"
        child_command = command
        command = [
            sys.executable,
            "-c",
            WINDOWS_JOB_LAUNCHER,
            str(gate),
            json.dumps(child_command),
        ]
    else:
        popen_options["start_new_session"] = True
    try:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            **popen_options,
        )
        if windows_job is not None:
            windows_job.assign(process)
            windows_job_assigned = True
            gate.write_text("assigned", encoding="ascii")
    except BaseException:
        try:
            if "process" in locals():
                terminate_process_tree(
                    process,
                    platform=os.name,
                    windows_job=windows_job if windows_job_assigned else None,
                )
        finally:
            if windows_job is not None and not windows_job.closed:
                windows_job.close()
            if gate_directory is not None:
                gate_directory.cleanup()
        raise
    try:
        stdout, _ = process.communicate(timeout=remaining_seconds(deadline))
    except subprocess.TimeoutExpired as exc:
        terminate_process_tree(process, windows_job=windows_job)
        raise VerificationError(
            f"command exceeded full verification deadline: {' '.join(command)}"
        ) from exc
    except BaseException:
        terminate_process_tree(process, windows_job=windows_job)
        raise
    finally:
        if gate_directory is not None:
            gate_directory.cleanup()
    if windows_job is not None:
        windows_job.close()
    try:
        output = stdout.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise VerificationError(
            f"command output is not valid UTF-8: {' '.join(command)}"
        ) from exc
    write_utf8(sys.stdout, output)
    if process.returncode:
        raise VerificationError(
            f"command failed with exit {process.returncode}: {' '.join(command)}"
        )
    return output


def shard_cost(nodeid: str) -> int:
    return next(
        (cost for prefix, cost in SHARD_COST_HINTS if nodeid.startswith(prefix)),
        1,
    )


def balanced_shard_assignments(nodeids: list[str], count: int) -> dict[str, int]:
    """Deterministically spread collected tests by coarse execution cost."""
    if not 1 <= count <= 8:
        raise VerificationError("CI shard count must be an integer from 1 through 8")
    if len(nodeids) != len(set(nodeids)):
        raise VerificationError("pytest collection contains duplicate node IDs")
    assignments: dict[str, int] = {}
    loads = [0] * count
    item_counts = [0] * count
    for nodeid in sorted(nodeids, key=lambda value: (-shard_cost(value), value)):
        index = min(range(count), key=lambda value: (loads[value], item_counts[value], value))
        assignments[nodeid] = index
        loads[index] += shard_cost(nodeid)
        item_counts[index] += 1
    return assignments


def pytest_parallel_args(environment: dict[str, str] | None = None) -> list[str]:
    environment = os.environ if environment is None else environment
    workers = environment.get("G1_CI_WORKERS", "8")
    if not workers.isdigit() or not 2 <= int(workers) <= 8:
        raise VerificationError("G1_CI_WORKERS must be an integer from 2 through 8")
    count = environment.get("G1_CI_SHARD_COUNT", "1")
    index = environment.get("G1_CI_SHARD_INDEX", "0")
    if (
        not count.isdigit()
        or not index.isdigit()
        or not 1 <= int(count) <= 8
        or not 0 <= int(index) < int(count)
    ):
        raise VerificationError("CI shard identity must satisfy 1 <= count <= 8 and 0 <= index < count")
    return [
        "-n",
        workers,
        "--dist",
        "worksteal",
        "-p",
        "g1_shard_plugin",
    ]


def run_complete_suite(deadline: float | None = None) -> None:
    deadline = new_deadline() if deadline is None else deadline
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    assert npm is not None
    with tempfile.TemporaryDirectory(prefix="yaobizuoduo-offline-") as directory:
        directory_path = Path(directory)
        (directory_path / "g1_shard_plugin.py").write_text(
            SHARD_PLUGIN,
            encoding="utf-8",
        )
        env = offline_environment(directory_path)
        run([sys.executable, "scripts/validate_project_status.py", "--repo-root", "."], env, deadline)
        collected = run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", TRANSPORT_TEST],
            env,
            deadline,
        )
        if "6 tests collected" not in collected:
            raise VerificationError("transport suite was not completely collected")
        run([sys.executable, "-m", "pytest", "-q", TRANSPORT_TEST], env, deadline)
        run(
            [sys.executable, "-m", "pytest", "-q", *pytest_parallel_args(env)],
            env,
            deadline,
        )
        run([sys.executable, "-m", "pip", "check"], env, deadline)
        run([npm, "--prefix", "frontend", "ls", "--all", "--offline"], env, deadline)
        run([npm, "--prefix", "frontend", "test", "--", "--run"], env, deadline)
        run([npm, "--prefix", "frontend", "run", "build"], env, deadline)
        run([sys.executable, "-m", "compileall", "-q", "scripts", "tests"], env, deadline)
        run(["git", "diff", "--check"], env, deadline)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--fail-closed", action="store_true")
    parser.add_argument("--require-transport", action="store_true")
    args = parser.parse_args()
    if not (args.offline and args.fail_closed and args.require_transport):
        parser.error("--offline --fail-closed --require-transport are all mandatory")
    return args


def main() -> int:
    parse_args()
    deadline = new_deadline()
    try:
        validate_runtime_and_dependencies(deadline)
        validate_fixtures_scope_and_secrets(deadline)
        run_complete_suite(deadline)
    except (OSError, subprocess.SubprocessError, VerificationError, ValueError) as exc:
        write_utf8(sys.stderr, f"FULL_CI_FAILED: {exc}\n")
        return 1
    write_utf8(sys.stdout, "FULL_CI_OK: G1-T01 complete offline verification passed\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
