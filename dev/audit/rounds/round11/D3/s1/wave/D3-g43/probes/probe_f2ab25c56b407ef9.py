#!/usr/bin/env python3
# Metric: ThermalModel.flow_lift_factor(outdoor, flow) over a grid of (cop_flow_reference_temp ref, cop_reference_temp,
#   outdoor, flow) inputs, including the one point where carnot_ref == 1e-9 exactly (the only point `<=` and `<` differ);
#   moved = number of grid points whose returned float differs between baseline and mutant.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes/probe_f2ab25c56b407ef9.py
# Expected: grid_moved=0 over the validated range of ref; exact_tie_moved=1 only with ref set outside the config bounds
#   (ref = -273.15 + 1e-9 bit-exactly), which from_config cannot produce.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g43 (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel.flow_lift_factor, line 3389.
# Perturbation: `if carnot_ref <= 1e-9:` -> `if carnot_ref < 1e-9:`, in a scratch copy of the baseline package.
# Null control: the same grid against an unedited scratch copy (moved 0).
import json, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blib as B

CHILD = r'''
import json, math, sys
sys.path.insert(0, "tests")
from profiles import house
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
out = []
def run(ref, cref, outdoor, flow):
    p = ThermalParameters.from_config(house(two_zone=False))
    p.cop_flow_reference_temp = ref
    p.cop_reference_temp = cref
    return ThermalModel(p).flow_lift_factor(outdoor, flow)
# validated-range grid
for ref in (25.0, 35.0, 45.0, 55.0):
    for cref in (-7.0, 2.0, 7.0, 12.0):
        for outdoor in (-30.0, -7.0, 0.0, 7.0, 15.0, 30.0):
            for flow in (ref - 1, ref, ref + 0.5, ref + 10, 60.0, float("nan")):
                out.append(("grid", ref, cref, outdoor, flow, run(ref, cref, outdoor, flow)))
# the tie: find ref with (ref + 273.15) == 1e-9 bit-exactly, and a cop_reference_temp that keeps the lift denominator at 1.0
import numpy as np
ref = -273.15 + 1e-9
cands = [ref]
x = ref
for _ in range(2000):
    x = float(np.nextafter(x, 1.0)); cands.append(x)
x = ref
for _ in range(2000):
    x = float(np.nextafter(x, -1000.0)); cands.append(x)
tie = [c for c in cands if (c + 273.15) == 1e-9]
for c in tie[:3]:
    for outdoor in (-300.0, c - 5.0, c):
        out.append(("tie", c, c, outdoor, 60.0, run(c, c, outdoor, 60.0)))
print(json.dumps({"rows": out, "tie_refs": tie[:3], "n_tie_refs": len(tie)}))
'''


def run_child(variant):
    env = dict(os.environ, PYTHONPATH=f"{variant}/tests/hastub:{variant}/tests:{variant}")
    r = subprocess.run([sys.executable, "-c", CHILD], cwd=variant, env=env, capture_output=True, text=True, timeout=600)
    if r.returncode:
        raise SystemExit("child failed: " + r.stderr[-500:])
    return json.loads(r.stdout.strip().splitlines()[-1])


if __name__ == "__main__":
    LINE, OLD, NEW = 3389, "carnot_ref <= 1e-9", "carnot_ref < 1e-9"
    b = run_child(B.make_variant(LINE, None, None, "base"))
    n = run_child(B.make_variant(LINE, None, None, "null"))
    m = run_child(B.make_variant(LINE, OLD, NEW, "mut"))
    def moved(x, y, kind):
        return [(a, c) for a, c in zip(x["rows"], y["rows"]) if a[0] == kind and a[5] != c[5]]
    gm, tm_, gn = moved(b, m, "grid"), moved(b, m, "tie"), moved(b, n, "grid")
    print(f"grid_points={sum(1 for r in b['rows'] if r[0]=='grid')} tie_points={sum(1 for r in b['rows'] if r[0]=='tie')} "
          f"tie_refs_found={b['n_tie_refs']}")
    for a, c in tm_[:3]:
        print(f"  tie moved: ref={a[1]!r} outdoor={a[3]} baseline={a[5]!r} mutant={c[5]!r}")
    print(f"RESULT grid_moved={len(gm)}")
    print(f"RESULT null_grid_moved={len(gn)}")
    print(f"RESULT exact_tie_moved={len(tm_)}")
