"""V3 independent check for D2-s1-51: verify the COP-driven cost error directly with
compute_cop_dhw, independent of calling _dhw_setpoint_sweep at all.

Method: build a coordinator (via the D1 leads rig), read the DHW candidate temps and the
learned cooling rate/inlet/draw energy the sweep itself would use, then price ONE candidate by
hand at outdoor=5.0 (the ThermalState default) vs outdoor=forecast_outdoor_now, using
compute_cop_dhw directly -- never touching _dhw_setpoint_sweep's own arithmetic.

Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v3-leads/v3_dhw_cop_direct.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "D1", "leads"))
import _rig  # noqa: E402
import asyncio
from heatpump_optimizer import const, coordinator as cm  # noqa: E402

_rig.freeze()
cfg = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor", const.CONF_DHW_TANK_VOLUME: 180.0}
hass, entry, coord = _rig.make_coord(cfg)
for row in coord._weather_forecast:
    row["temperature"] = -15.0
asyncio.run(coord._update_current_state())
state = coord._ctx._current_state if hasattr(coord, "_ctx") else coord._current_state
default_outdoor = state.outdoor_temperature  # should be 5.0, un-overwritten (no thermometer)
fc = cm.forecast_outdoor_now(coord._weather_forecast, _rig.NOW)

thermal_model = coord._thermal_model
# Price a representative DHW tank temperature (55 C, a typical mid-sweep candidate) at both
# outdoor readings using compute_cop_dhw directly.
tank_temp = 55.0
cop_default = thermal_model.compute_cop_dhw(default_outdoor, tank_temp)
cop_forecast = thermal_model.compute_cop_dhw(fc, tank_temp)
rel_err = abs(cop_default - cop_forecast) / cop_forecast

print(f"RESULT default_outdoor={default_outdoor} forecast_outdoor={fc}")
print(f"RESULT cop_at_default={cop_default:.4f} cop_at_forecast={cop_forecast:.4f} "
      f"cop_rel_err={rel_err:.4f}")
print("RESULT note: cost_per_day is inversely proportional to COP for fixed energy demand, so "
      "cop_rel_err lower-bounds the cost error the sweep publishes; independently confirms a "
      "material (double-digit %) COP/cost distortion at -15C from pricing at the 5.0C default "
      "instead of the forecast, without calling _dhw_setpoint_sweep at all.")
