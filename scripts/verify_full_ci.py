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
import subprocess
import sys
import tempfile


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
SHARD_PLUGIN = """\
import os
from scripts.verify_full_ci import shard_index

def pytest_collection_modifyitems(config, items):
    count = int(os.environ["G1_CI_SHARD_COUNT"])
    index = int(os.environ["G1_CI_SHARD_INDEX"])
    selected = [
        item for item in items
        if shard_index(item.nodeid, count) == index
    ]
    deselected = [item for item in items if item not in selected]
    if deselected:
        config.hook.pytest_deselected(items=deselected)
    items[:] = selected
"""


class VerificationError(RuntimeError):
    pass


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


def validate_runtime_and_dependencies() -> None:
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
    node_version = subprocess.run(
        [node, "--version"], check=True, text=True, capture_output=True
    ).stdout.strip().removeprefix("v")
    node_pin = NODE_PIN.read_text(encoding="utf-8").strip()
    if node_version != node_pin:
        raise VerificationError(f"Node runtime drift: expected {node_pin}, got {node_version}")

    package = read_json(PACKAGE_JSON)
    npm_pin = package.get("packageManager")
    npm_version = subprocess.run(
        [npm, "--version"], check=True, text=True, capture_output=True
    ).stdout.strip()
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


def validate_fixtures_scope_and_secrets() -> None:
    actual_fixtures = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "fixtures").rglob("*")
        if path.is_file()
    }
    if actual_fixtures != set(FIXTURE_DIGESTS):
        raise VerificationError("fixture inventory drifted")
    for relative, expected in FIXTURE_DIGESTS.items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise VerificationError(f"fixture digest drifted: {relative}")

    status = read_json(STATUS)
    manifest = read_json(MANIFEST)
    task = status["active_tasks"][0]
    if task.get("task_id") != "G1-T01" or task.get("risk") != "D1":
        raise VerificationError("full CI is restricted to the frozen G1-T01 D1 card")
    card = next(
        item for item in manifest["cards"] if item.get("task_id") == "G1-T01"
    )
    baseline = status["evidence"]["authorization_baseline_sha"]
    diff = subprocess.run(
        ["git", "diff", "--name-only", baseline, "--"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.splitlines()
    outside = sorted(set(diff) - set(card["allowed_paths"]))
    if outside:
        raise VerificationError("forbidden-scope paths changed: " + ", ".join(outside))
    patch = subprocess.run(
        ["git", "diff", "--binary", baseline, "--"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    if any(pattern.search(patch) for pattern in SECRET_PATTERNS):
        raise VerificationError("candidate diff contains a secret-shaped value")


def offline_environment(directory: Path) -> dict[str, str]:
    guard = directory / "sitecustomize.py"
    guard.write_text(
        "import socket\n"
        "_original_connect = socket.socket.connect\n"
        "def _offline_connect(self, address):\n"
        "    if self.family == socket.AF_UNIX:\n"
        "        return _original_connect(self, address)\n"
        "    host = address[0] if isinstance(address, tuple) and address else ''\n"
        "    if host in {'127.0.0.1', '::1', 'localhost'}:\n"
        "        return _original_connect(self, address)\n"
        "    raise OSError('offline verification forbids network access')\n"
        "socket.socket.connect = _offline_connect\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env.update(
        {
            "CI": "true",
            "G1_CI_WORKERS": env.get("G1_CI_WORKERS", "4"),
            "G1_CI_SHARD_COUNT": env.get("G1_CI_SHARD_COUNT", "1"),
            "G1_CI_SHARD_INDEX": env.get("G1_CI_SHARD_INDEX", "0"),
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


def run(command: list[str], env: dict[str, str]) -> str:
    print("+", " ".join(command), flush=True)
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(result.stdout, end="")
    if result.returncode:
        raise VerificationError(
            f"command failed with exit {result.returncode}: {' '.join(command)}"
        )
    return result.stdout


def shard_index(nodeid: str, count: int) -> int:
    return int(hashlib.sha256(nodeid.encode("utf-8")).hexdigest(), 16) % count


def pytest_parallel_args() -> list[str]:
    workers = os.environ.get("G1_CI_WORKERS", "4")
    if not workers.isdigit() or not 2 <= int(workers) <= 8:
        raise VerificationError("G1_CI_WORKERS must be an integer from 2 through 8")
    count = os.environ.get("G1_CI_SHARD_COUNT", "1")
    index = os.environ.get("G1_CI_SHARD_INDEX", "0")
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


def run_complete_suite() -> None:
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    assert npm is not None
    with tempfile.TemporaryDirectory(prefix="yaobizuoduo-offline-") as directory:
        directory_path = Path(directory)
        (directory_path / "g1_shard_plugin.py").write_text(
            SHARD_PLUGIN,
            encoding="utf-8",
        )
        env = offline_environment(directory_path)
        run([sys.executable, "scripts/validate_project_status.py", "--repo-root", "."], env)
        collected = run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", TRANSPORT_TEST],
            env,
        )
        if "6 tests collected" not in collected:
            raise VerificationError("transport suite was not completely collected")
        run([sys.executable, "-m", "pytest", "-q", TRANSPORT_TEST], env)
        run(
            [sys.executable, "-m", "pytest", "-q", *pytest_parallel_args()],
            env,
        )
        run([sys.executable, "-m", "pip", "check"], env)
        run([npm, "--prefix", "frontend", "ls", "--all", "--offline"], env)
        run([npm, "--prefix", "frontend", "test", "--", "--run"], env)
        run([npm, "--prefix", "frontend", "run", "build"], env)
        run([sys.executable, "-m", "compileall", "-q", "scripts", "tests"], env)
        run(["git", "diff", "--check"], env)


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
    try:
        validate_runtime_and_dependencies()
        validate_fixtures_scope_and_secrets()
        run_complete_suite()
    except (OSError, subprocess.SubprocessError, VerificationError, ValueError) as exc:
        print(f"FULL_CI_FAILED: {exc}", file=sys.stderr)
        return 1
    print("FULL_CI_OK: G1-T01 complete offline verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
