"""D2.M2 cell priced-inputs-surface: space_setpoint_unit x compressor_modulation.

Metric:
  clamp_mismatch  = per cell, 1 when OptimizationConfig.from_mapping(cfg).clamp_planned_levels
                    (the plan's level law, derived by thermal_model.declared_modulation from the
                    device's declared compressor) differs from the declaration: on_off -> clamped
                    (levels in {0} U [p_min, p_max]), modulating -> not clamped, auto -> the
                    install probe's answer for the same surface without the key.
                    KEY: the flag the production config delivers.
  sub_pmin_steps  = per cell, steps of a real solve (tests/golden.py winter_single_no_dhw,
                    96 x 15 min, p_min 1.0 kW) whose planned space power lies in (0, p_min):
                    a level a declared on/off compressor cannot run, priced as if it could.
Command (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D2/s2/m2_priced_surface.py [--perturb]
--perturb: thermal_model.py `True if mode == const.COMPRESSOR_MODULATION_ON_OFF` ->
  `False if mode == const.COMPRESSOR_MODULATION_ON_OFF` (the docstring's on_off -> False) in a
  private copy; expected clamp_mismatch 3 -> 0 and the on_off cells' sub_pmin_steps -> 0.
Expected at baseline: clamp_mismatch=1 on each on_off cell (3 total, exact); every other cell 0.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B5 (shared, counts only).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C

EDITS = [("thermal_model.py", "True if mode == const.COMPRESSOR_MODULATION_ON_OFF",
          "False if mode == const.COMPRESSOR_MODULATION_ON_OFF")]
C.setup_paths(EDITS if "--perturb" in sys.argv else None)

import numpy as np
from heatpump_optimizer import const
from heatpump_optimizer.optimizer import OptimizationConfig
from heatpump_optimizer.thermal_model import declared_modulation, probe_install
import golden

UNITS = const.SPACE_SETPOINT_UNITS
MODS = const.COMPRESSOR_MODULATIONS
SURFACE = {const.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.hp",
           const.CONF_SPACE_SETPOINT_ENTITY: "number.space"}


def solve(clamped):
    built = golden.make(dhw=False)
    opt = built["optimizer"]
    opt.config.clamp_planned_levels = clamped
    res = opt.optimize(inputs=golden.solve_inputs(
        initial_state=built["state"], prices=built["prices"], outdoor_temps=built["outdoor"],
        wind_speeds=built["wind"], precipitation=built["rain"], solar_radiation=built["solar"],
        start_time=golden.START))
    p = np.asarray(res.power_schedule, dtype=float)
    pmin = opt.model.params.min_electrical_power
    return int(np.sum((p > 1e-6) & (p < pmin - 1e-6)))


cache = {}
total = 0
for unit in UNITS:
    for mod in MODS:
        cfg = {**SURFACE, const.CONF_SPACE_SETPOINT_UNIT: unit, const.CONF_COMPRESSOR_MODULATION: mod}
        clamp = OptimizationConfig.from_mapping(cfg).clamp_planned_levels
        bare = {k: v for k, v in cfg.items() if k != const.CONF_COMPRESSOR_MODULATION}
        expected = {"on_off": True, "modulating": False}.get(
            mod, OptimizationConfig.from_mapping(bare).clamp_planned_levels)
        mismatch = int(bool(clamp) != bool(expected))
        if clamp not in cache:
            cache[clamp] = solve(clamp)
        cell = f"unit={unit},mod={mod}"
        C.result(f"{cell}.declared_modulation", declared_modulation(cfg))
        C.result(f"{cell}.probe_on_off", probe_install(cfg).on_off)
        C.result(f"{cell}.clamp", clamp)
        C.result(f"{cell}.clamp_mismatch", mismatch, "count")
        C.result(f"{cell}.sub_pmin_steps", cache[clamp], "count")
        total += mismatch
C.result("total.clamp_mismatch", total, "count")
C.trailer()
