"""Shared scaffolding for the round-2 D9 harnesses. Not a harness itself.

Every harness under tools/audit/round2/D9/ imports this first. It does four
things, all of which the harness contract (tools/audit/README.md) requires:

* pins the BLAS thread count BEFORE numpy is imported (the harness must
  import d9lib before numpy; d9lib imports numpy itself after the pin);
* prints ``RESULT <name>=<value> <unit>`` lines in the one format the judge
  parses, plus the closing ``thread_factor`` / ``load1`` / ``swapins``;
* loads ``tests/stress.py``'s definitions (``reference_solve``,
  ``Calibration``, ``build_case``, ``SEASONS``, ``BUILDINGS``, the budgets)
  WITHOUT running its sweep: the file runs every check at import, so the
  source is executed only up to the ``R.section("Combination sweep")``
  marker. ``reference_solve`` is therefore byte-identical to the ruler the
  gate uses, which is what makes a CPU ratio against it final;
* measures a section's CPU on both clocks so the thread factor is reported.

Runs from the repository root with PYTHONPATH=tests/hastub; never cd's.
"""
from __future__ import annotations

import os
import sys
import time
import subprocess

# The thread pin, copied from tests/stress.py lines 60-64: OpenBLAS reads
# these once at load, so they must be set before numpy is imported anywhere.
for _threads in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_threads, "1")

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "custom_components"))

import numpy as np  # noqa: E402  (after the pin, deliberately)

BASELINE_SHA = "c398fc84eec25fc44b60d74aae05b9a2da205884"
MACHINE = "Apple M1 8-core 8 GB, macOS, numpy on OpenBLAS (audit box)"


def result(name: str, value, unit: str) -> None:
    if isinstance(value, float):
        text = f"{value:.6g}"
    else:
        text = str(value)
    print(f"RESULT {name}={text} {unit}", flush=True)


def swapins() -> int:
    """macOS: vm_stat's 'Swapins' counter; Linux: /proc/vmstat pswpin."""
    try:
        if sys.platform == "darwin":
            out = subprocess.run(["vm_stat"], capture_output=True, text=True,
                                 timeout=5).stdout
            for line in out.splitlines():
                if line.startswith("Swapins"):
                    return int(line.split(":")[1].strip().rstrip("."))
        else:
            with open("/proc/vmstat") as fh:
                for line in fh:
                    if line.startswith("pswpin"):
                        return int(line.split()[1])
    except Exception:  # noqa: BLE001 - reporting only
        pass
    return -1


def closing(thread_factor: float) -> None:
    """The three lines the judge reads before accepting a timing RESULT."""
    result("thread_factor", float(thread_factor), "ratio")
    result("load1", float(os.getloadavg()[0]), "load")
    result("swapins", swapins(), "count")


class Clocks:
    """CPU on both clocks plus wall, for one measured section."""

    def __enter__(self):
        self.wall0 = time.perf_counter()
        self.proc0 = time.process_time()
        self.thr0 = time.thread_time()
        return self

    def __exit__(self, *exc):
        self.wall_ms = (time.perf_counter() - self.wall0) * 1000.0
        self.proc_ms = (time.process_time() - self.proc0) * 1000.0
        self.thread_ms = (time.thread_time() - self.thr0) * 1000.0
        return False

    @property
    def thread_factor(self) -> float:
        return self.proc_ms / self.thread_ms if self.thread_ms > 1e-9 else 1.0


def load_stress_prefix(marker: str = 'R.section("Combination sweep")') -> dict:
    """Execute tests/stress.py up to ``marker``, return its namespace."""
    path = os.path.join(ROOT, "tests", "stress.py")
    with open(path) as fh:
        source = fh.read()
    cut = source.index(marker)
    prefix = source[:cut]
    namespace: dict = {"__name__": "stress_prefix", "__file__": path}
    code = compile(prefix, path, "exec")
    exec(code, namespace)  # noqa: S102 - the audited tree's own test code
    return namespace
