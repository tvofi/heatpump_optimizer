#!/usr/bin/env python3
# Metric: _max_pump_rise("dhw") in degC/h, the fastest the heat pump alone could warm the DHW tank (default parameters:
#   5 kW electrical, outdoor 5 C, a 200 L DHW tank 0.232 kWh/K, buffer 0.0406 kWh/K).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_1ee0ec8960fb9a66.py
# EXPECTED RESULT rise_dhw_baseline=~70 degC/h  (thermal kW over the DHW tank's capacity)
# EXPECTED RESULT rise_dhw_mutant=~400 degC/h  (the DHW tank is sized as the buffer: 5.7x faster)
# EXPECTED RESULT null_baseline=null_mutant  (tank "buffer": the edited branch is not taken)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g07 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB RAM).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._max_pump_rise, line 5104.
# Perturbation: key 1ee0ec8960fb9a66 (GUARD_OFF), line 5104 `if tank == "dhw":` -> `if False:`, in memory.
#   Direction: rise up (the DHW tank's rise computed from the buffer mass).
# Null control: tank "buffer".
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402

BASE = L.baseline("_max_pump_rise")
MUT = L.mutant("_max_pump_rise", 'if tank == "dhw":', "if False:")
c = L.coord(dhw_tank_volume=200.0)
print(f"RESULT dhw_capacity={c._thermal_params.dhw_store.capacity_kwh_per_c:.4f} kWh/K")
print(f"RESULT buffer_capacity={c._thermal_params.buffer_tank_thermal_mass:.4f} kWh/K")
print(f"RESULT rise_dhw_baseline={BASE(c, 'dhw'):.3f} degC/h")
print(f"RESULT rise_dhw_mutant={MUT(c, 'dhw'):.3f} degC/h")
print(f"RESULT null_baseline={BASE(c, 'buffer'):.3f} degC/h")
print(f"RESULT null_mutant={MUT(c, 'buffer'):.3f} degC/h")
L.footer()
