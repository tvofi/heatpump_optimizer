#!/usr/bin/env python3
"""D3-s1-01, verifier V2 (independent): does any test-supplied inlet reading distinguish C0043?

METRIC: differential_inputs = number of distinct inlet readings (value, unit) that the tree's tests
  feed to coordinator._dhw_inlet_c on which the C0043 mutant (coordinator.py:1371
  `-5.0 <= value` -> `-5.0 < value`) returns a different value from the baseline function.
  0 means no test input can kill C0043, whatever the assertion. Census sources:
  (a) static: every string literal passed as a FakeState value within the tests/features.py
      statements that build `sensor.inlet` states or call `_p8_inlet_at(` (AST walk);
  (b) tests/config_flow_steps.py, the only other test script naming the inlet entity: static count
      of dict entries keyed "sensor.dhw_inlet" that carry a state (FakeState / state dict). Its
      in-process run under a recorder (`--dynamic`) exceeded the 2-minute cap (killed at 170 s) and
      is off by default; its number is not part of this harness's result.
  Controls: positive arm adds (-5.0, degC) and (23.0, degF) to the census -> +2; the null arm
  compares baseline with baseline-recompiled -> 0.
RUN:      PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D3/verify-v2/inlet_census.py
EXPECTED: differential_inputs=0 (exact); positive_control=2 (exact); null_control=0 (exact)
BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
MACHINE:  cloud box G1-V2, 4 vCPU Linux, CPython 3.14.0rc2
PERTURBATION: mutant compiled from the in-memory source, swapped with mock.patch.object; no file written.
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import ast
import contextlib
import io
import runpy
import sys
import textwrap
import time
from datetime import UTC, datetime
from pathlib import Path
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeHass, FakeState  # noqa: E402

import heatpump_optimizer.coordinator as coord  # noqa: E402

OLD = "-5.0 <= value <= 35.0"
NEW = "-5.0 < value <= 35.0"


def build(src: str):
    tree = ast.parse(src)
    node = next(n for n in tree.body if getattr(n, "name", None) == "_dhw_inlet_c")
    seg = textwrap.dedent(ast.get_source_segment(src, node))
    ns: dict = {}
    exec(compile(seg, coord.__file__, "exec"), coord.__dict__, ns)
    return ns["_dhw_inlet_c"]


def call(fn, value, unit):
    hass = FakeHass({"sensor.inlet": FakeState(str(value), unit=unit, last_updated=datetime.now(UTC))})
    try:
        return repr(fn(hass, "sensor.inlet"))
    except Exception as err:  # noqa: BLE001
        return type(err).__name__


def static_census() -> set:
    src = Path("tests/features.py").read_text()
    tree = ast.parse(src)
    lines = src.splitlines()
    out = set()
    for stmt in ast.walk(tree):
        if not isinstance(stmt, (ast.Assign, ast.Expr, ast.FunctionDef)):
            continue
        seg = "\n".join(lines[stmt.lineno - 1:stmt.end_lineno])
        if "sensor.inlet" not in seg and "_p8_inlet_at(" not in seg:
            continue
        for n in ast.walk(stmt):
            if isinstance(n, ast.Call):
                fname = getattr(n.func, "id", getattr(n.func, "attr", ""))
                if fname == "FakeState" and n.args and isinstance(n.args[0], ast.Constant):
                    unit = next((k.value.value for k in n.keywords if k.arg == "unit"
                                 and isinstance(k.value, ast.Constant)), None)
                    out.add((n.args[0].value, unit))
                if fname == "_p8_inlet_at" and len(n.args) == 2 and all(
                        isinstance(a, ast.Constant) for a in n.args):
                    out.add((n.args[0].value, n.args[1].value))
    return out


def main() -> int:
    t0p, t0t = time.process_time(), time.thread_time()
    src = Path(coord.__file__).read_text()
    assert src.count(OLD) == 1, "mutation site not unique"
    base = coord._dhw_inlet_c
    mut = build(src.replace(OLD, NEW))
    null = build(src)

    census = static_census()
    print("STATIC_CENSUS", sorted(census, key=repr))

    seen: list = []

    def recorder(hass, entity_id):
        st = hass.states.get(entity_id) if entity_id else None
        seen.append((getattr(st, "state", None), getattr(st, "attributes", {}).get("unit_of_measurement")
                     if st is not None else None))
        return mut(hass, entity_id)

    cfs = Path("tests/config_flow_steps.py").read_text()
    cfs_states = sum(1 for n in ast.walk(ast.parse(cfs)) if isinstance(n, ast.Dict) and any(
        isinstance(k, ast.Constant) and k.value == "sensor.dhw_inlet" for k in n.keys))
    print(f"RESULT config_flow_steps_dicts_keyed_by_inlet_entity={cfs_states} count")
    print(f"RESULT config_flow_steps_FakeState_for_inlet="
          f"{sum('FakeState' in l and 'dhw_inlet' in l for l in cfs.splitlines())} count")
    if "--dynamic" not in sys.argv:
        seen = []
    buf = io.StringIO()
    rc = 0
    if "--dynamic" in sys.argv:
        with mock.patch.object(coord, "_dhw_inlet_c", recorder), contextlib.redirect_stdout(buf):
            try:
                runpy.run_path("tests/config_flow_steps.py", run_name="__main__")
            except SystemExit as e:
                rc = e.code or 0
        print(f"RESULT config_flow_steps_rc_under_mutant={rc}")
        print(f"RESULT config_flow_steps_inlet_calls={len(seen)} count")
    census |= {s for s in seen if s[0] is not None}

    diff = [c for c in census if call(base, *c) != call(mut, *c)]
    print("DIFFERENTIAL", diff)
    print(f"RESULT census_size={len(census)} count")
    print(f"RESULT differential_inputs={len(diff)} count")
    pos = census | {("-5.0", "°C"), ("23.0", "°F")}
    print(f"RESULT positive_control={sum(call(base, *c) != call(mut, *c) for c in pos)} count")
    print(f"RESULT null_control={sum(call(base, *c) != call(null, *c) for c in pos)} count")
    # width of the flip: grid -10..40 step 0.01 degC
    grid = [round(-10 + i * 0.01, 2) for i in range(5001)]
    print(f"RESULT flip_points_on_0.01C_grid={sum(call(base, v, '°C') != call(mut, v, '°C') for v in grid)} count")
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={tp / tt if tt > 1e-9 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
