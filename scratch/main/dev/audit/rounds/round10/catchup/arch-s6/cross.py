#!/usr/bin/env python3
"""arch-s6 catch-up verifier: perturbation-cross of D7-s6-91 (setpoint_unit.py) and D12-s3-01
(surface_units.py), the duplicate test.

Arm a: run D12-s3-01's harness (surface_units.py) on a tree carrying D7-s6-91's fix (P2, i.e.
       origin/main + f973a8fdd + e1235aa36). P2 deletes setpoint_check._read_setpoint (moved verbatim
       to inputs.read_setpoint), so this wrapper aliases the old name to the new before exec'ing the
       unmodified harness. Metric: misdelivered_cells (degF arm), null_misdelivered_cells.
Arm b: run D7-s6-91's harness (setpoint_unit.py) with D12-s3-01's own perturbation applied in
       memory: pump_arbiter.state_unit falls back to the instance unit for a unit-less state
       (surface_units.py --perturb's rule; the instance unit is taken from the roundtrip's arm).
       Metric: roundtrip_error_defect_K / roundtrip_error_null_K.
Command:  cd TREE && PYTHONPATH=tests/hastub:tests:custom_components:. python3 \
          $CV/dev/audit/rounds/round10/catchup/arch-s6/cross.py a|b HARNESS_PATH
Expected (baseline d749c986d, macOS arm64): a on P2 tree -> 0 / 0; b on main -> 0.000 / 0.000.
Null: a on the main tree reads 2 / 0; b without perturbation reads 42.222 / 0.000 (the finders' own).
"""
import os
import runpy
import sys

arm, harness = sys.argv[1], sys.argv[2]
sys.argv = [harness]
if arm == "a":
    sys.path[:0] = ["tests", "."]
    from custom_components.heatpump_optimizer import inputs, setpoint_check
    if not hasattr(setpoint_check, "_read_setpoint"):
        setpoint_check._read_setpoint = inputs.read_setpoint
        print("NOTE aliased setpoint_check._read_setpoint -> inputs.read_setpoint (P2 tree)")
    runpy.run_path(harness, run_name="__main__")
elif arm == "b":
    sys.path[:0] = ["tests/hastub", "tests", "custom_components"]
    from heatpump_optimizer import pump_arbiter as pa
    _orig = pa.state_unit
    cur = [None]
    pa.state_unit = lambda s: (lambda u: u if u is not None else cur[0])(_orig(s))
    g = runpy.run_path(harness, run_name="not_main")
    rt = g["roundtrip"]

    def wrapped(entity, state, unit):
        cur[0] = unit
        return rt(entity, state, unit)
    g["main"].__globals__["roundtrip"] = wrapped
    print("NOTE perturbation: pump_arbiter.state_unit falls back to the instance unit")
    g["main"]()
