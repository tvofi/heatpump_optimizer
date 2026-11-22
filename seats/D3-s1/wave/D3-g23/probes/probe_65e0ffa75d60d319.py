#!/usr/bin/env python3
# Metric: whether _settlement_caps returns a 'wood' cap (and its value, C) for a two-tank 4-way-valve house; and how many OptimizationResult fields optimize() changes with the wood tank starting at 99 C (a probe reading above the 95 C rating).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g23/probes/probe_65e0ffa75d60d319.py
# EXPECTED RESULT two_tank_modelled=1
# EXPECTED RESULT wood_cap_baseline=95.0
# EXPECTED RESULT wood_cap_mutant=None
# EXPECTED RESULT null_single_tank_delta=0
# EXPECTED RESULT stored_kwh_wood99_baseline=361.7500 kWh
# EXPECTED RESULT stored_kwh_wood99_mutant=364.0700 kWh
# EXPECTED RESULT optimize_two_tank_wood99_24h_differing_fields=0 []
# EXPECTED RESULT optimize_two_tank_wood99_2h_differing_fields=0 []
# EXPECTED RESULT optimize_two_tank_wood99_1h_differing_fields=0 []
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g23 cloud (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux),
#   run from a scratch baseline worktree while the box's full gate ran (counts exact; no timing is claimed).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._settlement_caps, line 6038 (the wood-tank settlement cap).
# Perturbation: key 65e0ffa75d60d319, optimizer.py:6038 `if p.two_tank_modelled:` -> `if False:`, applied in memory
#   (_g23_common.mutated re-compiles HeatPumpOptimizer._settlement_caps with the one line replaced and patches the class);
#   direction: the wood store loses its settlement cap ('wood' key absent).
# Null control: a single-tank house (no wood probe): both arms identical.
# Writes nothing. Helpers: _g23_common.py beside this file.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import _g23_common as c  # noqa: E402
NAN = c.NAN
MUT = ('_settlement_caps', 'if p.two_tank_modelled:', 'if False:')
import numpy as np
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
base_cfg = {"indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor", "upper_floor_thermal_mass": 3.0,
            "lower_floor_thermal_mass": 4.5, "buffer_tank_volume": 750.0, "mixing_valve_mode": "manual"}
def make(wood, hours=24):
    cfg = dict(base_cfg)
    if wood:
        cfg["wood_tank_top_entity"] = "sensor.wood_top"
    p = ThermalParameters.from_config(cfg)
    oc = c.om.OptimizationConfig(horizon_hours=hours, time_step_minutes=15, target_temp=21.0, min_temp=19.0, max_temp=23.0)
    return c.OPT(ThermalModel(p), oc)
outdoor = np.full(96, -5.0)
caps = {}
for arm in ("baseline", "mutant"):
    with (c.mutated(*MUT) if arm == "mutant" else c.contextlib.nullcontext()):
        caps[arm] = (make(True)._settlement_caps(outdoor), make(False)._settlement_caps(outdoor))
print(f"RESULT two_tank_modelled={int(make(True).model.params.two_tank_modelled)}")
print(f"RESULT wood_cap_baseline={caps['baseline'][0].get('wood')}")
print(f"RESULT wood_cap_mutant={caps['mutant'][0].get('wood')}")
print(f"RESULT null_single_tank_delta={int(caps['baseline'][1] != caps['mutant'][1])}")
from profiles import prices, weather, solve_inputs
outd, wind, rain, solar = weather("winter_cold", c.START)
st = dict(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=float(outd[0]), upper_floor_temperature=21.0,
          lower_floor_temperature=21.0, buffer_tank_temperature=45.0)
fields = {f.name for f in __import__("dataclasses").fields(ThermalState)}
for k, v in (("wood_tank_temperature", 99.0), ("wood_tank_top_temperature", 99.0)):
    if k in fields:
        st[k] = v
state = ThermalState(**st)
# the cap's one reader: _stored_thermal_energy(state, caps=...) on a state whose wood tank reads 99 C
e = {arm: make(True)._stored_thermal_energy(state, caps=caps[arm][0]) for arm in ("baseline", "mutant")}
print(f"RESULT stored_kwh_wood99_baseline={e['baseline']:.4f} kWh")
print(f"RESULT stored_kwh_wood99_mutant={e['mutant']:.4f} kWh")
for hours in (24, 2, 1):
    n = int(hours * 4)
    def run():
        return make(True, hours).optimize(inputs=solve_inputs(initial_state=state, prices=prices("winter_typical", c.START)[:n],
                                   outdoor_temps=outd[:n], wind_speeds=wind[:n], precipitation=rain[:n], solar_radiation=solar[:n],
                                   start_time=c.START))
    rb = run()
    with c.mutated(*MUT):
        rm = run()
    d = c.result_diff(rb, rm)
    print(f"RESULT optimize_two_tank_wood99_{hours}h_differing_fields={len(d)} {c.fmt(d[:8])}")
c.tail()
