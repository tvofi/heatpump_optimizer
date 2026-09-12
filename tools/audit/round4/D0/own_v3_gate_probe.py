"""Verifier 3's mutation probe for D0-02's "ftol has no gate" half.

METRIC (one line): the pass/fail outcome of the repository's own solution
quality gate ``tests/optimality.py`` when production's L-BFGS-B ``ftol`` is
degraded 1e-6 -> 1e-3 (a 1000x loosening of the stop rule) in
``optimizer.py:_multi_start_minimize``/``_lbfgsb_restart`` via the options
dict -- forced at ``_scoped_minimize`` so no file is edited -- plus, for
contrast, the same gate when ``maxiter`` is cut to 3 (the degradation
``tests/optimality.py`` challenger 3 exists to catch).

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub \
      /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
      tools/audit/round4/D0/own_v3_gate_probe.py

EXPECTED: the gate passes with ftol degraded (if it fails, name the check --
that check is the ftol gate and the claim weakens); the gate fails with
maxiter starved.

BASELINE SHA: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697 (measured at 3e91f85)
MACHINE: 8-core Apple M1, 8 GB, numpy/OpenBLAS, python 3.11
INSTRUMENTED SYMBOL: optimizer.py:_scoped_minimize (options dict forced).
PERTURBATION: ftol 1e-6 -> 1e-3 must not change the gate's verdict;
maxiter -> 3 must flip it.
CONTENTION: pass/fail and objective ratios only.
"""
from __future__ import annotations

import io
import os

for _v in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import contextlib  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from unittest import mock  # noqa: E402

sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
sys.path.insert(0, os.path.join(os.getcwd(), "custom_components"))

from heatpump_optimizer import optimizer as O  # noqa: E402

_real_scoped = O._scoped_minimize


def emit(name, value, unit=""):
    print(f"RESULT {name}={value} {unit}".rstrip())


def run_gate(ftol=None, maxiter=None, label=""):
    """Import tests/optimality.py with the options forced; return outcome."""
    for mod in [m for m in list(sys.modules) if m == "optimality"]:
        del sys.modules[mod]

    def forced(*a, **kw):
        kw = dict(kw)
        opts = dict(kw.get("options") or {})
        if ftol is not None:
            opts["ftol"] = ftol
        if maxiter is not None:
            opts["maxiter"] = maxiter
        kw["options"] = opts
        return _real_scoped(*a, **kw)

    buf = io.StringIO()
    code = 0
    with mock.patch.object(O, "_scoped_minimize", forced), \
            contextlib.redirect_stdout(buf):
        try:
            import optimality  # noqa: F401  (runs at import, sys.exits)
        except SystemExit as e:
            code = int(e.code or 0)
    out = buf.getvalue()
    fails = [l.strip() for l in out.splitlines() if "FAIL" in l]
    print(f"--- gate {label}: exit={code} failures={len(fails)}")
    for f in fails[:10]:
        print("    ", f)
    return code, fails


def main() -> int:
    code0, _ = run_gate(label="unmodified control")
    code1, fails1 = run_gate(ftol=1e-3, label="ftol degraded 1e-6 -> 1e-3")
    emit("gate_unmodified_exit", code0)
    emit("gate_ftol_1e-3_exit", code1)
    emit("gate_ftol_1e-3_failed_checks", len(fails1))
    # Contrast: the starvation the gate exists to catch. maxiter->3 on every
    # call, like optimality.py's own challenger 3 but from outside.
    code2, fails2 = run_gate(maxiter=3, label="maxiter starved to 3")
    emit("gate_maxiter_3_exit", code2)
    emit("gate_maxiter_3_failed_checks", len(fails2))
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True,
                             timeout=10).stdout
        swapins = next(int(l.split(":")[1].strip().rstrip("."))
                       for l in out.splitlines()
                       if l.strip().startswith("Swapins"))
    except Exception:
        swapins = -1
    emit("load1", round(os.getloadavg()[0], 2))
    emit("swapins", swapins)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
