#!/usr/bin/env python3
# Metric: HeatPumpOptimizerCoordinator._max_pump_rise(tank) return value (degC/h, or None, or the exception
#   type it raises) for a tank whose capacity (kWh/degC) sits at or below the 1e-6 guard; key = the value returned.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g08/probes/probe_15456e64946920b5.py
# Expected: see the RESULT lines printed (baseline arm vs mutant arm per input); exact, no tolerance (deterministic).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g08 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._max_pump_rise
#   (coordinator.py:5108), read by the external-heat observation at coordinator.py:5223-5224.
# Perturbation: mutant 15456e64946920b5 (GUARD_OFF) '       if capacity <= 1e-6:' -> '       if False:', compiled in memory from the method's source.
# Inputs: real ThermalParameters (default build, the real ThermalModel for compute_cop at 0 degC outdoor) with the
#   capacity forced through a params proxy to each value in CAPS for both tanks ('dhw' and 'buffer').
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path.cwd()))
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402

CLS = co.HeatPumpOptimizerCoordinator
OLD, NEW = (s.strip() for s in ("       if capacity <= 1e-6:", "       if False:"))


def mutant(fn):
    src = textwrap.dedent(inspect.getsource(fn))
    assert src.count(OLD) == 1, "anchor line moved"
    ns = dict(co.__dict__)
    exec(compile(src.replace(OLD, NEW, 1), co.__file__, "exec"), ns)
    return ns[fn.__name__]


MUT = mutant(CLS._max_pump_rise)
REAL = ThermalParameters()


def call(fn, tank, cap):
    params = SimpleNamespace(max_electrical_power=REAL.max_electrical_power,
                             buffer_tank_thermal_mass=cap,
                             dhw_store=SimpleNamespace(capacity_kwh_per_c=cap))
    me = SimpleNamespace(_thermal_params=params, _thermal_model=ThermalModel(REAL),
                         _current_state=SimpleNamespace(outdoor_temperature=0.0))
    try:
        v = fn(me, tank)
        return "None" if v is None else f"{v:.6g}"
    except Exception as exc:  # the mutant's division can raise
        return f"raises {type(exc).__name__}"


CAPS = (0.0, 5e-7, 1e-6, 1.0000001e-6, REAL.buffer_tank_thermal_mass, REAL.dhw_tank_thermal_mass)
moved = 0
for tank in ("dhw", "buffer"):
    for cap in CAPS:
        b, m = call(CLS._max_pump_rise, tank, cap), call(MUT, tank, cap)
        moved += int(b != m)
        print(f"RESULT {tank}_cap={cap!r}_baseline={b}")
        print(f"RESULT {tank}_cap={cap!r}_mutant={m}")
print(f"RESULT inputs_moved={moved} count of {2 * len(CAPS)}")
# real-volume reach: the smallest store the config flow accepts (buffer 10 L, dhw 50 L) is far above the guard
print(f"RESULT min_config_capacity_buffer={ThermalParameters(buffer_tank_volume=10.0).buffer_tank_thermal_mass:.6g} kWh/degC")
print(f"RESULT min_config_capacity_dhw={ThermalParameters(dhw_tank_volume=50.0).dhw_tank_thermal_mass:.6g} kWh/degC")

# Downstream arm: the only reader, ExternalHeatDetector._collect_evidence (external_heat.py:300-316), with the
# compressor running (commanded 3 kW, metered 3 kW) and a DHW/buffer rise RATE in degC/h; key = evidence lines.
from datetime import datetime, timezone  # noqa: E402
from custom_components.heatpump_optimizer.external_heat import ExternalHeatDetector, ExternalHeatObservation  # noqa: E402

det = ExternalHeatDetector()
RATES = (2.0, 50.0, 1000.0, 1e6)
ev_moved, ev_cells = 0, 0
for cap in CAPS[:4]:
    for rate in RATES:
        arms = []
        for fn in (CLS._max_pump_rise, MUT):
            ceil = call(fn, "buffer", cap)
            if ceil.startswith("raises"):
                arms.append(ceil)
                continue
            obs = ExternalHeatObservation(now=datetime(2026, 1, 10, 12, tzinfo=timezone.utc), commanded_power_kw=3.0,
                                          measured_power_kw=3.0,
                                          buffer_max_rise_c_per_h=None if ceil == "None" else float(ceil),
                                          dhw_max_rise_c_per_h=None if ceil == "None" else float(ceil))
            arms.append(len(det._collect_evidence(obs, rate, rate)))
        ev_cells += 1
        ev_moved += int(arms[0] != arms[1])
        print(f"RESULT evidence_cap={cap!r}_rate={rate}_baseline={arms[0]} mutant={arms[1]}")
print(f"RESULT evidence_moved={ev_moved} count of {ev_cells}")
