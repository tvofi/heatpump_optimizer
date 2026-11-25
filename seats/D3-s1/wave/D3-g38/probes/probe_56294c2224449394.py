#!/usr/bin/env python3
# Metric: _valve_regulates(plant behind a throttling valve, observed 20.5 C, outdoor 0 C) as 1/0 with the held state's tank temperature set relative to the valve's flow target; inputs_differing counts tank offsets whose outcome differs.
# Command: HPO_PROBE_ROOT=<clean baseline checkout> PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g38/probes/probe_56294c2224449394.py
# EXPECTED inputs_differing=1 of 4 (tank == flow - 0.01 exactly: baseline 1 (regulates, step refused by VALVE_REGULATES_REASON), mutant 0)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g38 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:_valve_regulates, sysid.py:266 `return _held_state(...).buffer_tank_temperature >= flow - 0.01`
# Perturbation: key 56294c2224449394, CMP_BOUND `>= flow - 0.01` -> `> flow - 0.01`. The tie needs a tank temperature equal to flow - 0.01 to the bit, so the held state is supplied by a stub of sysid._held_state in BOTH arms (the stub returns tank = flow + offset); the unstubbed real _held_state is a fourth input, applied in memory (function re-compiled from the baseline source with the
#   one line replaced); the baseline arm is the same source re-compiled unchanged.
# Null control: offsets 0.0 and -1.0, and the real _held_state (same value in both arms)
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent))
import _mutlib as L
import dataclasses
from types import SimpleNamespace
m = L.module(); tm = L.module("thermal_model"); mv = L.module("mixing_valve")
mode = sorted(mv.THROTTLING_MODES)[0]
plant = dataclasses.replace(tm.ThermalParameters(), mixing_valve_mode=mode, mixing_valve_target=21.0)
observed, outdoor = 20.5, 0.0
flow = m.ThermalModel(plant).flow_target_for_indoor(plant.mixing_valve_target or plant.comfort_ceiling, outdoor)
OLD = "    return _held_state(model, observed, outdoor).buffer_tank_temperature >= flow - 0.01"
NEW = "    return _held_state(model, observed, outdoor).buffer_tank_temperature > flow - 0.01"
diff = 0
for name, tank in (("tie_flow-0.01", flow - 0.01), ("null_flow", flow), ("null_flow-1", flow - 1.0), ("real_held_state", None)):
    ov = None if tank is None else {"_held_state": lambda model, o, out, t=tank: SimpleNamespace(buffer_tank_temperature=t)}
    base, mut = L.mutant(m, "_valve_regulates", OLD, NEW, ov)
    b, x = int(base(plant, observed, outdoor)), int(mut(plant, observed, outdoor))
    diff += b != x
    print(f"RESULT regulates[{name}] baseline={b} mutant={x}")
print(f"RESULT inputs_differing={diff} of 4 (mode {mode!r}, flow {flow!r} C)")
