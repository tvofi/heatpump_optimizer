#!/usr/bin/env python3
"""V3 perturbation for D6-s2-05 that moves the FINDING's own number.

METRIC: schema-only keys the finder's services_claims.py reports on the
simulate_plan prose row (configuration.md:951), with the five wood_* keys removed
from services.SERVICE_SCHEMA_SIMULATE_PLAN in memory before the finder's harness runs.
RUN: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/verify-v3/s2_05_own_perturb.py
EXPECTED: RESULT simulate_plan_schema_only=0 (baseline, unperturbed finder harness: 5).
BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. MACHINE: 4-CPU linux container.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import contextlib, io, re, runpy, sys, time
from pathlib import Path
import voluptuous as vol
_T0P, _T0T = time.process_time(), time.thread_time()
sys.path[:0] = [str(Path.cwd() / "tests"), str(Path.cwd() / "custom_components")]
from heatpump_optimizer import services  # noqa: E402
s = services.SERVICE_SCHEMA_SIMULATE_PLAN
services.SERVICE_SCHEMA_SIMULATE_PLAN = vol.Schema(
    {k: v for k, v in s.schema.items() if not str(getattr(k, "schema", k)).startswith("wood_")})
buf = io.StringIO()
sys.argv = ["services_claims.py"]
with contextlib.redirect_stdout(buf):
    try:
        runpy.run_path("tools/audit/round9/D6/s2/services_claims.py", run_name="__main__")
    except SystemExit:
        pass
out = buf.getvalue()
row = next((l for l in out.splitlines() if "simulate_plan: prose" in l), "")
m = re.search(r"schema-only \[(.*?)\]", row)
n = len([x for x in m.group(1).split(",") if x.strip()]) if m else 0
print(row[:200])
print(f"RESULT simulate_plan_schema_only={n} count")
print(f"RESULT thread_factor={(time.process_time()-_T0P)/max(time.thread_time()-_T0T,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _sw = int(next(l.split()[1] for l in open("/proc/vmstat") if l.startswith("pswpin")))
except Exception:
    _sw = -1
print(f"RESULT swapins={_sw}")
