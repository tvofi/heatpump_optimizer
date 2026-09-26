"""L4 lead (raised by D2-s1) for D1-s5 / D1.M6 -- can a non-finite value reach the free-heat forecast?

Metric (one line): nonfinite_forecast_cells = fuzz cells whose ExternalHeatDetector.forecast_free_heat
  output (96 steps x 0.25 h, what coordinator._external_heat_forecast hands the optimizer) holds any
  non-finite value, over every numeric observation field x {nan, inf, -inf}, fire active (override on).
  Count key: the forecast list production returns.
  Second number: the reachability of those inputs -- coordinator._space_demand_kw on a coordinator
  whose room/outdoor come from the stale-aware reader (D1-s5's parsers_sweep.py already shows
  InputReader delivers 0 non-finite of 102 hostile states); here _space_demand_kw is driven with
  non-finite ThermalParameters/ThermalState fields to show what it can deliver itself.
Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/leads/l4_free_heat_nan.py [--perturb]
Perturbation (--perturb): external_heat's clamp `min(1.0, max(0.0, fraction))` swapped in memory for
  the NaN-propagating numpy form (np.clip), i.e. the scalar max() that silently eats NaN is removed.
  Expected: nonfinite_forecast_cells up.
Expected: nonfinite_forecast_cells=0 of 27, space_demand_nonfinite=2 of 6; --perturb 1. Exact.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; box: 4-vCPU Linux container.
Instrumented: external_heat:ExternalHeatDetector.update/_update_displacement/forecast_free_heat,
  coordinator:HeatPumpOptimizerCoordinator._space_demand_kw.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import math
import sys
import time
from dataclasses import replace
from datetime import datetime, timedelta
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
from heatpump_optimizer import external_heat as eh  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters, ThermalState  # noqa: E402

PERTURB = "--perturb" in sys.argv
if PERTURB:
    _src_min, _src_max = min, max

    class _NpMax:
        def __call__(self, *a):
            if len(a) == 2 and all(isinstance(v, float) for v in a):
                return float(np.maximum(a[0], a[1]))
            return _src_max(*a)

    eh.max = _NpMax()  # module-global shadow: _update_displacement's max() now propagates NaN

FIELDS = ["outlet_temp", "wood_top", "wood_bottom", "hp_tank_temp", "space_demand_kw",
          "dhw_temp", "buffer_temp", "commanded_power_kw", "measured_power_kw"]
HEALTHY = dict(outlet_temp=45.0, wood_top=70.0, wood_bottom=60.0, hp_tank_temp=40.0,
               space_demand_kw=5.0, dhw_temp=50.0, buffer_temp=40.0, commanded_power_kw=0.0,
               measured_power_kw=0.0)


def cell(field, bad):
    det = eh.ExternalHeatDetector(eh.ExternalHeatConfig(enabled=True))
    now = datetime(2026, 1, 15, 12, 0)
    obs = eh.ExternalHeatObservation(now=now, override=True, **HEALTHY)
    det.update(obs)
    det.update(replace(obs, now=now + timedelta(minutes=30), **{field: bad}))
    fc = det.forecast_free_heat(96, 0.25)
    return any(not math.isfinite(v) for v in fc), det.state.free_heat_kw


def main():
    t0, th0 = time.process_time(), time.thread_time()
    bad_cells, total = 0, 0
    for f in FIELDS:
        for bad in (float("nan"), float("inf"), float("-inf")):
            nonfin, fh = cell(f, bad)
            total += 1
            bad_cells += int(nonfin)
            if nonfin:
                print(f"NONFINITE {f}={bad} free_heat_kw={fh}")
    healthy_nonfin, healthy_fh = cell("outlet_temp", 45.0)
    # What _space_demand_kw itself can deliver from non-finite state/params.
    coord = object.__new__(cm.HeatPumpOptimizerCoordinator)
    sd_bad = 0
    sd_total = 0
    for fld in ("room_temperature", "outdoor_temperature"):
        for bad in (float("nan"), float("inf"), float("-inf")):
            coord._thermal_params = ThermalParameters()
            coord._current_state = replace(ThermalState(), **{fld: bad})
            v = coord._space_demand_kw()
            sd_total += 1
            sd_bad += int(not math.isfinite(v))
            if not math.isfinite(v):
                print(f"SPACE_DEMAND_NONFINITE {fld}={bad} -> {v}")
    print(f"RESULT fuzz_cells={total} count")
    print(f"RESULT nonfinite_forecast_cells={bad_cells} count")
    print(f"RESULT healthy_free_heat_kw={healthy_fh:.3f} kW (the fire is active and displacing)")
    print(f"RESULT space_demand_nonfinite={sd_bad} of {sd_total}")
    print(f"RESULT perturbed={int(PERTURB)}")
    print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "n/a"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
