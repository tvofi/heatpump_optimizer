"""D2-s2 / D2.M3 -- objective and savings identities on every golden scenario.

Metric (one line each):
  cost_err      = max over scenarios |predicted_cost - E(power+dhw)|, E = sum(price*P*dt)
                  minus the PV piecewise credit sum(margin*min(P,surplus))*dt where a surplus exists
  savings_err   = max |predicted_savings - (baseline_cost - predicted_cost - deferred_energy_cost)|
  end_mismatch  = count of (scenario, store) where the optimized end state that
                  _deferred_energy_cost settles differs by > 1e-6 K from the end of the
                  trajectory the same result publishes (room/slab/upper/lower/buffer/wood/dhw)
  count key: the ThermalState HeatPumpOptimizer._deferred_energy_cost receives
             (its optimized_end argument), compared with OptimizationResult's own
             *_trajectory[-1] -- i.e. keyed on what the production seam delivers.

Run:   PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D2/s2/objective_identities.py [--perturb] [--only a,b]
Expect (baseline 1936d5ca, box B5 linux, py3.14 numpy 2.4.6):
  cost_err <= 1e-9 ; savings_err <= 1e-9 ; end_mismatch = see REPORT (exact count)
Perturbation (--perturb): in memory, HeatPumpOptimizer._replay_end_state is swapped for a
  replay through simulate_trajectory_with_dhw (space AND dhw schedules) -- the one-line fix;
  end_mismatch must fall.
Instrumented: optimizer:HeatPumpOptimizer._deferred_energy_cost, optimizer:HeatPumpOptimizer.optimize
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer import optimizer as optmod  # noqa: E402
from heatpump_optimizer import pv  # noqa: E402

PERTURB = "--perturb" in sys.argv
HPO = optmod.HeatPumpOptimizer
_orig_def = HPO._deferred_energy_cost
_orig_opt = HPO.optimize
_orig_replay = HPO._replay_end_state
rec = {}


def def_wrap(self, baseline_end, optimized_end, prices, outdoor, include_dhw=False,
             caps=None, humidity=None):
    val = _orig_def(self, baseline_end, optimized_end, prices, outdoor,
                    include_dhw=include_dhw, caps=caps, humidity=humidity)
    rec.setdefault("deferred", []).append((optimized_end, include_dhw, val))
    rec.setdefault("deferred_args", []).append(
        (baseline_end, prices, outdoor, include_dhw, caps, humidity))
    return val


def opt_wrap(self, *a, **k):
    rec["pv"] = a[8] if len(a) > 8 else k.get("pv_surplus")
    res = _orig_opt(self, *a, **k)
    rec.setdefault("results", []).append((self, res))
    return res


HPO._deferred_energy_cost = def_wrap
HPO.optimize = opt_wrap

if PERTURB:
    # One-line fix candidate: on the DHW path, settle the end state the published
    # trajectory actually reaches.  Implemented by wrapping the DHW simulation so
    # _replay_end_state returns the state at the end of simulate_trajectory_with_dhw.
    from heatpump_optimizer import thermal_model as tm
    _orig_swd = tm.ThermalModel.simulate_trajectory_with_dhw

    def swd_wrap(self, *a, **k):
        out = _orig_swd(self, *a, **k)
        rec["last_swd"] = out
        return out
    tm.ThermalModel.simulate_trajectory_with_dhw = swd_wrap

    def replay_from_traj(self, initial_state, power_schedule, *a, **k):
        st = _orig_replay(self, initial_state, power_schedule, *a, **k)
        out = rec.get("last_swd")
        if out is not None and len(out[0]) == len(power_schedule) + 1:
            room, slab, upper, lower, dhw, buf, wood = out
            st.room_temperature = float(room[-1]); st.slab_temperature = float(slab[-1])
            st.upper_floor_temperature = float(upper[-1])
            st.lower_floor_temperature = float(lower[-1])
            if buf is not None and len(buf):
                st.buffer_tank_temperature = float(buf[-1])
            if wood is not None and len(wood) and st.wood_tank_temperature is not None:
                st.wood_tank_temperature = float(wood[-1])
        return st
    HPO._replay_end_state = replay_from_traj

t0 = time.process_time(); tt0 = time.thread_time()
cost_err = 0.0; sav_err = 0.0; mismatches = []; savings_shift = []; worst_cost = ("", 0.0)
names = list(golden.SCENARIOS)
if "--only" in sys.argv:
    names = sys.argv[sys.argv.index("--only") + 1].split(",")
for name in names:
    rec.clear()
    try:
        golden.capture(name, golden.SCENARIOS[name])
    except AssertionError as e:  # invariants: report, keep going
        print(f"# {name}: invariant {e}")
    opt, res = rec["results"][-1]
    dt = opt.config.dt_hours
    prices = np.asarray(res.prices)
    P = np.asarray(res.power_schedule)
    if res.dhw_power_schedule:
        P = P + np.asarray(res.dhw_power_schedule)
    e = float(np.sum(prices * P) * dt)
    surplus = rec.get("pv")
    if surplus is not None and np.any(np.asarray(surplus)[: len(prices)] > 1e-6):
        s = np.asarray(surplus, dtype=float)[: len(prices)]
        m = pv.import_margin(prices, opt.config.pv_export_price)
        e -= float(np.sum(m * np.minimum(P, s)) * dt)
    ce = abs(res.predicted_cost - e)
    if ce > worst_cost[1]:
        worst_cost = (name, ce)
    cost_err = max(cost_err, ce)
    sav_err = max(sav_err, abs(res.predicted_savings - (res.baseline_cost - res.predicted_cost - res.deferred_energy_cost)))
    end, inc_dhw, _ = rec["deferred"][-1]
    pairs = [("room", end.room_temperature, res.room_temp_trajectory),
             ("slab", end.slab_temperature, res.slab_temp_trajectory)]
    if opt.model.params.two_zone_enabled:
        pairs += [("upper", end.upper_floor_temperature, res.upper_temp_trajectory),
                  ("lower", end.lower_floor_temperature, res.lower_temp_trajectory),
                  ("buffer", end.buffer_tank_temperature, res.buffer_temp_trajectory),
                  ("wood", end.wood_tank_temperature, res.wood_temp_trajectory)]
    if inc_dhw:
        pairs.append(("dhw", end.dhw_temperature, res.dhw_temp_trajectory))
    import copy
    fixed = copy.copy(end)
    attr = {"room": "room_temperature", "slab": "slab_temperature",
            "upper": "upper_floor_temperature", "lower": "lower_floor_temperature",
            "buffer": "buffer_tank_temperature", "wood": "wood_tank_temperature",
            "dhw": "dhw_temperature"}
    hit = False
    for store, v, traj in pairs:
        if v is None or not traj:
            continue
        d = float(v) - float(traj[-1])
        if abs(d) > 1e-6:
            mismatches.append((name, store, d))
            setattr(fixed, attr[store], float(traj[-1]))
            hit = True
    if hit:
        b_end, pr, od, inc, cp, hu = rec["deferred_args"][-1]
        alt = _orig_def(opt, b_end, fixed, pr, od, include_dhw=inc, caps=cp, humidity=hu)
        shift = (res.baseline_cost - res.predicted_cost - alt) - res.predicted_savings
        savings_shift.append((name, shift, res.predicted_savings, res.baseline_cost))
cpu = time.process_time() - t0; tcpu = time.thread_time() - tt0
for m in mismatches:
    print(f"# mismatch {m[0]:32s} {m[1]:7s} end_state - trajectory_end = {m[2]:+.6f} K")
print(f"# worst cost scenario {worst_cost}")
for nm, sh, ps, bc in savings_shift:
    print(f"# {nm}: savings with trajectory-end settlement - published = {sh:+.4f} (published savings {ps:.4f}, baseline {bc:.4f})")
print(f"RESULT savings_overstatement_max={max((-s[1] for s in savings_shift), default=0.0):.4f} currency")
print(f"RESULT savings_overstatement_pct_of_baseline={max((-s[1] / s[3] * 100 for s in savings_shift), default=0.0):.3f} pct")
print(f"RESULT scenarios={len(names)} count")
print(f"RESULT cost_err={cost_err:.3e} currency")
print(f"RESULT savings_err={sav_err:.3e} currency")
print(f"RESULT end_mismatch={len(mismatches)} count")
print(f"RESULT end_mismatch_scenarios={len({m[0] for m in mismatches})} count")
print(f"RESULT end_mismatch_max_abs={max((abs(m[2]) for m in mismatches), default=0.0):.6f} K")
print(f"RESULT perturbed={int(PERTURB)}")
print(f"RESULT thread_factor={cpu / max(tcpu, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
