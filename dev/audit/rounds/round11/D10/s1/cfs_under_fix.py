#!/usr/bin/env python3
"""D10.M1 companion to opt_two_zone.py: tests/config_flow_steps.py's failing checks, bare and with the fix shape.

Metric: count of FAIL lines tests/config_flow_steps.py prints, (a) bare and
(b) with ThermalParameters.from_config recompiled in memory with the mode
test ``two_zone_mode == const.TWO_ZONE_MODE_ON`` (the D10-s1-04 fix shape).
If (b) is 0, every failing check comes from that one predicate.
Instrumented symbol: thermal_model:ThermalParameters.from_config.
Perturbation: the arm itself (``--fix``); the FAIL count must fall (down).

Run (from the export root):
  PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python3 \
      dev/audit/rounds/round11/D10/s1/cfs_under_fix.py [--fix]
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (the round's export tree). Machine: macOS arm64, venv-ci Python 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import contextlib
import inspect
import io
import runpy
import sys
import tempfile
import textwrap

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
os.environ.setdefault("HPO_PLANDATA", os.path.join(tempfile.mkdtemp(prefix="d10s1."), "plandata.json"))

if "--fix" in sys.argv:
    from heatpump_optimizer import thermal_model as tm
    src = textwrap.dedent(inspect.getsource(tm.ThermalParameters.from_config.__func__))
    old = "two_zone_mode in (const.TWO_ZONE_MODE_ON, const.DEFAULT_TWO_ZONE_MODE)"
    assert old in src
    src = src.replace(old, "two_zone_mode == const.TWO_ZONE_MODE_ON").replace("@classmethod\n", "")
    ns = {}
    exec(compile(src, tm.__file__, "exec"), tm.__dict__, ns)
    tm.ThermalParameters.from_config = classmethod(ns["from_config"])

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    try:
        runpy.run_path("tests/config_flow_steps.py", run_name="__main__")
    except SystemExit:
        pass
fails = [ln.strip() for ln in buf.getvalue().splitlines() if ln.strip().startswith("FAIL ")]
for f in fails:
    print("CHECK", f[:160])
print(f"RESULT arm={'fix' if '--fix' in sys.argv else 'bare'}")
print(f"RESULT config_flow_steps_fails={len(fails)} count")
print("RESULT thread_factor=1.0")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
