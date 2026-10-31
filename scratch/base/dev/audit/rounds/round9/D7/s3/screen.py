#!/usr/bin/env python3
"""D7.M6 instrument check -- what tests/structure.py's dead-member screen reports
against the reachability census, and which of its two rules hides the gap.

Metric: structure.measure()['metrics']['dead_methods'] (the ratchet's budgeted
count, 0 at baseline) beside the number of members in reach.py's dead list the
screen misses.  Count key: the (class, member) the production screen lists.
Two perturbations, each an in-memory edit of the instrument (mock.patch):
  --no-property-exclusion   structure.is_property_getter -> always False
                            (the screen stops skipping @property getters)
  --attribute-only          structure.module_references counts only
                            Attribute loads and getattr literals, not bare
                            Name loads / import names (a method is reached by
                            `x.m`, never by a local variable named `m`)
Each must RAISE dead_methods; both together list every reach.py member.
Command (repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D7/s3/screen.py [--no-property-exclusion] [--attribute-only]
Expected at 1936d5ca: dead_methods=0 (baseline), 5 (--no-property-exclusion),
1 (--attribute-only), 11 (both: reach.py's 9 plus climate hvac_mode and
preset_mode, two HA-read properties HA_CONVENTION_METHODS does not list) +- 0.  Machine: B5 cloud container. Baseline 1936d5ca72a0.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import ast
import contextlib
import io
import sys
import time
from unittest import mock

sys.path.insert(0, "tests")
import structure as S  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--no-property-exclusion", action="store_true")
ap.add_argument("--attribute-only", action="store_true")
a = ap.parse_args()
t0, tt0 = time.process_time(), time.thread_time()


def attribute_only_refs(tree):
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Attribute):
            out.add(n.attr)
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                and n.func.id in ("getattr", "hasattr", "setattr") and len(n.args) >= 2 \
                and isinstance(n.args[1], ast.Constant) and isinstance(n.args[1].value, str):
            out.add(n.args[1].value)
    return out


patches = []
if a.no_property_exclusion:
    patches.append(mock.patch.object(S, "is_property_getter", lambda node: False))
if a.attribute_only:
    # module_references also feeds the top-level screen through other paths;
    # only the method screen consumes the name set, so patch its producer.
    patches.append(mock.patch.object(S, "module_references", attribute_only_refs))

with contextlib.ExitStack() as st:
    for p in patches:
        st.enter_context(p)
    with contextlib.redirect_stdout(io.StringIO()):
        res = S.measure()
m = res["metrics"] if "metrics" in res else res
tables = res.get("tables", {})
dm = tables.get("dead_methods", [])
for row in dm:
    print("LISTED", *row)
print(f"RESULT dead_methods={m['dead_methods']} count")
print(f"RESULT dead_top_level_symbols={m['dead_top_level_symbols']} count")
cpu, th = time.process_time() - t0, time.thread_time() - tt0
print(f"RESULT thread_factor={cpu / th if th else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
except Exception:  # noqa: BLE001
    sw = "na"
print(f"RESULT swapins={sw}")
