#!/usr/bin/env python3
# Metric: the buffer settlement cap (C) _settlement_caps returns for a 750 L valve tank on a -20 C day (charge ceiling 35 C) when the solve starts with the tank at 60 C (above the charge ceiling); and how many OptimizationResult fields optimize() changes.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g23/probes/probe_7516dd3d9e66d3ef.py
# EXPECTED RESULT charge_ceiling=35.000 C
# EXPECTED RESULT buffer_cap_initial60_baseline=60.000 C
# EXPECTED RESULT buffer_cap_initial60_mutant=35.000 C
# EXPECTED RESULT null_initial30_delta=0.000000 C
# EXPECTED RESULT optimize_tank60_differing_fields=20 ['buffer_temp_trajectory','compressor_starts','deferred_energy_cost','displace_schedule','heat_pump_on_schedule','lower_setpoints','lower_temp_trajectory','objective_value']
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g23 cloud (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux),
#   run from a scratch baseline worktree while the box's full gate ran (counts exact; no timing is claimed).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._settlement_caps, line 6029 (max(ceiling, initial)).
# Perturbation: key 7516dd3d9e66d3ef, optimizer.py:6029 `float(p.buffer_max_temp), max(ceiling, float(initial))` -> `float(p.buffer_max_temp), (ceiling)`, applied in memory
#   (_g23_common.mutated re-compiles HeatPumpOptimizer._settlement_caps with the one line replaced and patches the class);
#   direction: the cap falls from 60 C to the 35 C charge ceiling, so pre-stored heat above it settles at zero.
# Null control: initial tank 30 C (below the ceiling): both arms identical.
# Writes nothing. Helpers: _g23_common.py beside this file.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import _g23_common as c  # noqa: E402
NAN = c.NAN
MUT = ('_settlement_caps', 'float(p.buffer_max_temp), max(ceiling, float(initial))', 'float(p.buffer_max_temp), (ceiling)')
import numpy as np
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState


def make():
    p = ThermalParameters(two_zone_enabled=True, buffer_tank_volume=750.0, mixing_valve_mode="manual", buffer_max_temp=70.0)
    cfg = c.om.OptimizationConfig(horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=19.0, max_temp=23.0)
    return c.OPT(ThermalModel(p), cfg)


outdoor = np.full(96, -20.0)
o = make()
o._initial_buffer_temp = None
ceiling = o._settlement_caps(outdoor)["buffer"]
caps = {}
for arm in ("baseline", "mutant"):
    with (c.mutated(*MUT) if arm == "mutant" else c.contextlib.nullcontext()):
        o._initial_buffer_temp = 60.0
        hot = o._settlement_caps(outdoor)["buffer"]
        o._initial_buffer_temp = 30.0
        cool = o._settlement_caps(outdoor)["buffer"]
        caps[arm] = (hot, cool)
print(f"RESULT charge_ceiling={ceiling:.3f} C")
print(f"RESULT buffer_cap_initial60_baseline={caps['baseline'][0]:.3f} C")
print(f"RESULT buffer_cap_initial60_mutant={caps['mutant'][0]:.3f} C")
print(f"RESULT null_initial30_delta={abs(caps['baseline'][1] - caps['mutant'][1]):.6f} C")
# through optimize(): a valve house, a -20 C day, tank starting at 60 C
from profiles import prices, weather
_o, wind, rain, solar = weather("winter_cold", c.START)
outd = np.full(len(_o), -20.0)
state = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=float(outd[0]),
                     upper_floor_temperature=21.0, lower_floor_temperature=21.0, buffer_tank_temperature=60.0)
from profiles import solve_inputs
def run():
    return make().optimize(inputs=solve_inputs(initial_state=state, prices=prices("winter_typical", c.START),
                           outdoor_temps=outd, wind_speeds=wind, precipitation=rain, solar_radiation=solar, start_time=c.START))
rb = run()
with c.mutated(*MUT):
    rm = run()
d = c.result_diff(rb, rm)
print(f"RESULT optimize_tank60_differing_fields={len(d)} {c.fmt(d[:8])}")
c.tail()
