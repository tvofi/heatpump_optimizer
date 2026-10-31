"""Shared plumbing for the round-3 D2 (mathematical/physical sanity) harnesses.

Not a harness itself; it prints nothing.  Every harness in this directory
imports it as its FIRST import so the BLAS thread pin lands before numpy.

    import d2lib   # noqa: F401  -- must precede any numpy import

Provides: the thread pin, `sys.path` wiring identical to `tests/golden.py`,
a `result(name, value, unit)` printer, and `env_footer()` which prints
`thread_factor`, `load1`, `swapins` and the concurrent-agent process count
the round-3 seat block requires beside every RESULT block.
"""
from __future__ import annotations

import os

# --- BLAS thread pin, copied from tests/stress.py, BEFORE numpy ------------
for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

# Same two insertions tests/golden.py makes, so `import golden`/`import
# profiles` and `from heatpump_optimizer...` both work from the repo root.
for _p in ("tests", "custom_components", "tests/hastub"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np  # noqa: E402


def result(name: str, value, unit: str = "") -> None:
    """Print one `RESULT name=value unit` line."""
    if isinstance(value, float):
        value = repr(value)
    print(f"RESULT {name}={value}" + (f" {unit}" if unit else ""))


def _load1() -> float:
    try:
        return os.getloadavg()[0]
    except OSError:  # pragma: no cover - not on darwin/linux
        return float("nan")


def _swapins() -> int:
    try:
        out = subprocess.run(
            ["sysctl", "-n", "vm.swapusage"], capture_output=True, text=True, timeout=5
        ).stdout
        return int(float(out.split("used =")[1].split("M")[0]))
    except Exception:
        return -1


def _concurrent() -> int:
    try:
        out = subprocess.run(
            ["ps", "axo", "command"], capture_output=True, text=True, timeout=10
        ).stdout
    except Exception:
        return -1
    return sum(1 for ln in out.splitlines() if "claude" in ln.lower())


def thread_factor() -> float:
    """process_time / (wall * 1) over a small BLAS matmul.

    1.0 means the pin took.  The audit README rejects a timing RESULT whose
    factor exceeds 1.05.
    """
    a = np.random.default_rng(0).standard_normal((400, 400))
    t0, c0 = time.perf_counter(), time.process_time()
    for _ in range(6):
        a @ a
    wall = time.perf_counter() - t0
    cpu = time.process_time() - c0
    return cpu / wall if wall > 0 else float("nan")


def env_footer() -> None:
    result("thread_factor", round(thread_factor(), 4))
    result("load1", round(_load1(), 2))
    result("swapins", _swapins(), "MB_swap_used")
    result("concurrent_claude_procs", _concurrent())


BASELINE_SHA = "ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1"
MACHINE = "8-core Apple M1, 8 GB, macOS 25.6.0, python 3.11.5, numpy 2.4.6, scipy 1.17.1 (OpenBLAS)"


def repo_root_ok() -> None:
    """Refuse to run from anywhere but the export root."""
    if not Path("tests/golden.py").exists() or not Path(
        "custom_components/heatpump_optimizer/thermal_model.py"
    ).exists():
        raise SystemExit(
            "run me from the repository root: PYTHONPATH=tests/hastub "
            "python3 tools/audit/round3/D2/<harness>.py"
        )
