"""D2-s2 / D2.M3 -- plan-level consequence of the unscaled slab settlement cap.

Metric (one line): per golden scenario with house_heat_loss_scale = S (param override), the
  plan's end-of-horizon slab temperature, its predicted_savings, and its deferred_energy_cost,
  production (cap ignores S) vs the one-factor fix (cap computed at losses x S). Reported as
  deltas fix - production. Null control: S = 1 (deltas exactly 0).
  count key: OptimizationResult.slab_temp_trajectory[-1] / predicted_savings (production seam).
Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D2/s2/slab_cap_plan.py [S]
Expect (baseline 1936d5ca, box B5): see REPORT.
Perturbation: the fix arm IS the perturbation (optimizer.slab_settlement_cap and
  optimizer.hold_demand_kw fed losses x house_heat_loss_scale, in memory); at S=2 the end slab
  must rise (direction: up); at S=1 nothing moves.
Instrumented: optimizer:slab_settlement_cap, optimizer:HeatPumpOptimizer.optimize
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import copy
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer import optimizer as optmod  # noqa: E402

S = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0
SCEN = ["winter_single_no_dhw", "winter_two_zone_no_dhw", "shoulder", "flat_prices",
        "extreme_prices", "winter_single_dhw"]
_cap = optmod.slab_settlement_cap
_hold = optmod.hold_demand_kw


def _scaled(params):
    q = copy.copy(params)
    s = params.house_heat_loss_scale
    q.heat_loss_coefficient *= s
    q.upper_floor_heat_loss *= s
    q.lower_floor_heat_loss *= s
    return q


_orig_opt = optmod.HeatPumpOptimizer.optimize
last = {}


def opt_wrap(self, *a, **k):
    res = _orig_opt(self, *a, **k)
    last["res"] = res
    return res


optmod.HeatPumpOptimizer.optimize = opt_wrap


def run(name, fixed):
    optmod.slab_settlement_cap = (lambda p, t, o: _cap(_scaled(p), t, o)) if fixed else _cap
    optmod.hold_demand_kw = (lambda p, t, o, s=0.0: _hold(_scaled(p), t, o, s)) if fixed else _hold
    spec = copy.deepcopy(golden.SCENARIOS[name])
    po = dict(spec.get("param_overrides") or {})
    po["house_heat_loss_scale"] = S
    spec["param_overrides"] = po
    try:
        golden.capture(name, spec)
    except AssertionError as e:
        print(f"# {name}: invariant {e}")
    r = last["res"]
    return r.slab_temp_trajectory[-1], r.predicted_savings, r.deferred_energy_cost, r.predicted_cost, min(r.room_temp_trajectory[-17:])


t0 = time.process_time(); tt0 = time.thread_time()
d_slab = []; d_sav = []
for name in SCEN:
    a = run(name, False); b = run(name, True)
    d_slab.append(b[0] - a[0]); d_sav.append(b[1] - a[1])
    print(f"# {name:24s} S={S} end_slab {a[0]:.3f}->{b[0]:.3f}  savings {a[1]:.3f}->{b[1]:.3f}  deferred {a[2]:.3f}->{b[2]:.3f}  cost {a[3]:.3f}->{b[3]:.3f} min_room_last4h {a[4]:.3f}->{b[4]:.3f}")
cpu = time.process_time() - t0; tcpu = time.thread_time() - tt0
print(f"RESULT scale={S}")
print(f"RESULT cells={len(SCEN)} count")
print(f"RESULT end_slab_delta_max_K={max(d_slab):.3f}")
print(f"RESULT end_slab_delta_min_K={min(d_slab):.3f}")
print(f"RESULT savings_delta_min={min(d_sav):.3f} currency")
print(f"RESULT savings_delta_max={max(d_sav):.3f} currency")
print(f"RESULT thread_factor={cpu / max(tcpu, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
