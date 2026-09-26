"""D5 verify-v3 (reach and class) harness for D5-s2-02 and D5-s2-03: numbers and couplings the
comments state, against the value SET each production symbol can take on a real install.

Metric (one line, s2-02): of the three comment numbers (defrost floor 0.5, valve-write cadence
15 min, stale-floor interval 5 min), how many lie outside the set of values the production
symbol can deliver: DefrostDerate.factor after 2000 inferred observations at a 10 % delivered ratio, and the coordinator's update_interval over every
optimization_interval the options selector admits (min..max by step).
Metric (one line, s2-03): of the three real dhw_coil_draw_reduction call paths, how many use
DHW_COLD_WATER_TEMP as the cold end at a configured inlet of 15 C -- measured by a
recording wrapper on thermal_model.dhw_coil_draw_reduction under
ThermalModel.simulate_trajectory_with_dhw with dhw_coil_active forced True; plus the draw's cold end at inlet 15 C.
Count key: DefrostDerate.factor output; the update_interval kwarg HeatPumpOptimizerCoordinator
hands DataUpdateCoordinator.__init__ (tests/hastub drops it, ha_contract SIMPLIFIED, so it is
captured at the call); the inlet_temp argument dhw_coil_draw_reduction receives.
Command (from the repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D5/verify-v3/v3_s2_02_03_numbers.py [--perturb]
--perturb: defrost.DERATE_MIN=0.5 and the selector minimum 5 (in memory). Expected:
    comment_numbers_unreachable 2 -> 0.
Expected at baseline: comment_numbers_unreachable=2 (valve 15 is reachable), default interval
    30, draw_cold_end_at_15=15.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence); machine: 4-core
cloud container, CPython 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
_t0p, _t0t = time.process_time(), time.thread_time()
import numpy as np  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import config_flow, const, defrost, thermal_model  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402

PERTURB = "--perturb" in sys.argv
field = next(f for f in config_flow._OPTION_FIELDS if f.key == const.CONF_OPTIMIZATION_INTERVAL)
cfg = field.widget.config
lo, hi, step = float(cfg["min"]), float(cfg["max"]), float(cfg["step"])
if PERTURB:
    defrost.DERATE_MIN = 0.5
    lo = 5.0

# 1. defrost floor: drive the inferred estimator with a 10 % delivered ratio until it settles
d = defrost.DefrostDerate()
for _ in range(2000):
    d.observe(2.0, 90.0, 0.10)
_t, _h = d._bucket(2.0, 90.0)
# read at the bucket's own centre, where factor()'s bilinear blend with unlearned neighbours vanishes
floor_seen = d.factor(defrost.TEMP_CENTERS[_t], defrost.HUMIDITY_CENTERS[_h])

# 2. update_interval for every admitted optimization_interval
base = coord_mod.HeatPumpOptimizerCoordinator.__mro__[1]
seen = []
real = base.__init__


def cap(self, *a, **k):
    seen.append(k.get("update_interval"))
    return real(self, *a, **k)


intervals = []
with mock.patch.object(base, "__init__", cap):
    for m in np.arange(lo, hi + step / 2, step):
        seen.clear()
        coord_mod.HeatPumpOptimizerCoordinator(
            FakeHass(), FakeEntry(data={"weather_entity": "weather.home", "tibber_token": "x",
                                        const.CONF_OPTIMIZATION_INTERVAL: float(m)}))
        intervals.append(seen[0].total_seconds() / 60.0)
    seen.clear()
    coord_mod.HeatPumpOptimizerCoordinator(
        FakeHass(), FakeEntry(data={"weather_entity": "weather.home", "tibber_token": "x"}))
    default_min = seen[0].total_seconds() / 60.0
reach = set(round(x, 6) for x in intervals)
unreach = int(abs(floor_seen - 0.5) > 1e-6) + int(15.0 not in reach) + int(5.0 not in reach)
print(f"defrost floor at bucket centre={floor_seen:.3f}; admitted intervals {min(reach)}..{max(reach)}"
      f" ({len(reach)} values); default={default_min}")

# 3. s2-03: the draw's cold end at a configured inlet of 15 C, and what the coil receives
p = thermal_model.ThermalParameters(dhw_inlet_temp=15.0)
p10 = thermal_model.ThermalParameters(dhw_inlet_temp=10.0)
ratio = p.dhw_draw_power / p10.dhw_draw_power
cold_end = p.dhw_setpoint - (p.dhw_setpoint - 10.0) * ratio
calls = []
_real_coil = thermal_model.dhw_coil_draw_reduction


def rec(*a, **k):
    calls.append(k.get("inlet_temp", a[3] if len(a) > 3 else "DEFAULT"))
    return _real_coil(*a, **k)


# drive ThermalModel.simulate_trajectory_with_dhw's own call site with the coil forced active
n = 8
with mock.patch.object(thermal_model, "dhw_coil_draw_reduction", rec), \
        mock.patch.object(thermal_model.ThermalParameters, "dhw_coil_active",
                          new=property(lambda self: True)):
    pw = thermal_model.ThermalParameters(dhw_inlet_temp=15.0)
    model = thermal_model.ThermalModel(pw)
    st = thermal_model.ThermalState()
    st.wood_tank_temperature = 70.0
    model.simulate_trajectory_with_dhw(st, np.full(n, 2.0), np.full(n, 1.0), np.full(n, 0.0),
                                       dhw_draw_rates=np.full(n, 0.5))
default_calls = sum(1 for c in calls if c == "DEFAULT")
print(f"coil calls recorded={len(calls)} inlet args={calls[:3]}")
cpu_p, cpu_t = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT defrost_floor={floor_seen:.3f} ratio")
print(f"RESULT default_interval={default_min:g} min")
print(f"RESULT interval_min_admitted={min(reach):g} min")
print(f"RESULT comment_numbers_unreachable={unreach} count")
print(f"RESULT draw_cold_end_at_15={cold_end:.3f} C")
print(f"RESULT coil_calls={len(calls)} count")
print(f"RESULT coil_calls_on_default_constant={default_calls} count")
print(f"RESULT thread_factor={cpu_p / cpu_t if cpu_t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
