"""D2-s1-51: without an outdoor thermometer the DHW setpoint advisor prices every candidate at the
5.0 degC ThermalState constructor default, not the forecast the plan uses.

Metric: on a DHW install with no outdoor thermometer and a flat forecast of F degC, count the 7
candidates of HeatPumpOptimizerCoordinator._dhw_setpoint_sweep whose published cost_per_day differs
by more than 5 % from the same sweep priced at the forecast's current step
(forecast_outdoor_now); report the worst relative error, over F in {-15, -5, 5}.
Count key: the sweep's own published cost_per_day.
Command: PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D2/leads/dhw_sweep_outdoor.py [--forecast]
Expected: F=-15 -> 7 of 7 off (tens of %); F=5 -> 0 of 7 (null control: forecast equals the default);
--forecast (perturbation: the sweep reads forecast_outdoor_now, the fix's input) -> 0 in every cell.
The recommended setpoint is unchanged (cost is monotone in the candidate either way): the wrong
numbers are the published cost_per_day attributes.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine B10 cloud container.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "D1", "leads"))
import _rig  # noqa: E402
import asyncio
from heatpump_optimizer import const, coordinator as cm

FORECAST = "--forecast" in sys.argv


def cell(f):
    _rig.freeze()
    cfg = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor", const.CONF_DHW_TANK_VOLUME: 180.0}
    hass, entry, coord = _rig.make_coord(cfg)
    for row in coord._weather_forecast:
        row["temperature"] = f
    asyncio.run(coord._update_current_state())
    state = coord._ctx._current_state if hasattr(coord, "_ctx") else coord._current_state
    default_outdoor = state.outdoor_temperature
    fc = cm.forecast_outdoor_now(coord._weather_forecast, _rig.NOW)
    if FORECAST:
        state.outdoor_temperature = fc
    pub = coord._dhw_setpoint_sweep()
    state.outdoor_temperature = fc
    ref = coord._dhw_setpoint_sweep()
    state.outdoor_temperature = default_outdoor
    errs = [abs(a["cost_per_day"] - b["cost_per_day"]) / b["cost_per_day"]
            for a, b in zip(pub["candidates"], ref["candidates"])]
    off = sum(e > 0.05 for e in errs)
    same_rec = pub["recommended_setpoint"] == ref["recommended_setpoint"]
    return off, max(errs), default_outdoor, fc, same_rec


tot = 0
for f in (-15.0, -5.0, 5.0):
    off, worst, d, fc, same = cell(f)
    tot += off if f != 5.0 else 0
    print(f"RESULT F{f:+.0f}: off={off} of_7 worst_rel_err={worst:.3f} priced_at={d} forecast_now={fc} same_recommendation={int(same)}")
print(f"RESULT off_total_cold={tot} of_14")
_rig.tail()
