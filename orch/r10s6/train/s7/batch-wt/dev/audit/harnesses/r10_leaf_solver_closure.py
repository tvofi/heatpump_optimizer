#!/usr/bin/env python3
"""R10-LEAF-IMPORTS (#2247, ARCH2-s4 P1 and ARCH3-s6 P4): which package modules load the solver.

Metric: over every module of custom_components/heatpump_optimizer at REF except ``__init__``,
each imported alone in a fresh interpreter (tests/hastub first on the path), `solver_in` counts
the modules after whose import ``heatpump_optimizer.optimizer`` is in ``sys.modules``, `scipy_in`
those after which ``scipy`` is, and `import_failures` those that did not import. A census that
imported nothing cannot read as "every module is free of the solver": `modules` is printed, and
the harness exits 1 on any import failure or an empty package. One line per module names it.

Command (from the repository root, PYTHONPATH as the gate sets it):
    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_leaf_solver_closure.py REF

Perturbation: REF itself. At a merge base before the fix the seven leaves (early_cutoff,
legionella, pump_arbiter, quiet_windows, repairs, setpoint_check, silent_mode) read IN; at the
fix head they read out. The control is that no module flips the other way.

Expected (exact; static import graph, no timing):
    at merge base e5f7e169d64b93d4ae117eb07c68ecef6d47aea6:
        modules=76 solver_in=17 scipy_in=18 import_failures=0
    at the R10-LEAF-IMPORTS head:
    EXPECTED RESULT modules=76
    EXPECTED RESULT solver_in=10
    EXPECTED RESULT scipy_in=11
    EXPECTED RESULT import_failures=0

Baseline: e5f7e169d64b93d4ae117eb07c68ecef6d47aea6. Machine: Apple M1, darwin, CI venv 3.14; the
counts are machine-independent. Not a live-header harness: its 76 interpreters cost minutes on a
loaded seat, so harness_headers.py does not execute it.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import io  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tarfile  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


REPO = repo_root(__file__)
PKG = "heatpump_optimizer"


def census(ref: str) -> int:
    t_cpu, t_thr = time.process_time(), time.thread_time()
    hastub = REPO / "tests" / "hastub"
    with tempfile.TemporaryDirectory(prefix="leaf-closure-") as tmp:
        arc = subprocess.run(["git", "-C", str(REPO), "archive", ref, "custom_components"],
                             capture_output=True, check=True).stdout
        tarfile.open(fileobj=io.BytesIO(arc)).extractall(tmp, filter="data")
        root = Path(tmp) / "custom_components"
        env = {**os.environ, "PYTHONPATH": os.pathsep.join([str(hastub), str(root)])}
        mods = sorted(p.stem for p in (root / PKG).glob("*.py") if p.stem != "__init__")
        fail = solver = scipy = 0
        for m in mods:
            r = subprocess.run(
                [sys.executable, "-c",
                 f"import sys, {PKG}.{m}; "
                 f"print('IN' if '{PKG}.optimizer' in sys.modules else 'out', "
                 "'scipy' if 'scipy' in sys.modules else '-')"],
                capture_output=True, text=True, env=env)
            if r.returncode:
                fail += 1
                print(f"{m} IMPORT-FAILED {(r.stderr.strip().splitlines() or [''])[-1][:120]}")
                continue
            solver += r.stdout.startswith("IN")
            scipy += "scipy" in r.stdout
            print(m, r.stdout.strip())
    print(f"RESULT modules={len(mods)} count")
    print(f"RESULT solver_in={solver} count")
    print(f"RESULT scipy_in={scipy} count")
    print(f"RESULT import_failures={fail} count")
    cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 1 if fail or not mods else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    raise SystemExit(census(sys.argv[1]))
