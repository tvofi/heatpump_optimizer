#!/usr/bin/env python3
# Metric: surplus[0] kW from HeatPumpOptimizerCoordinator._pv_forecast(solar, 8) with a 6 kWp array whose
#   irradiance at step 0 is 0 W/m2 and whose production meter (pv_production_entity) reads 3.0 kW.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_002980a15ae8b9a9.py
# EXPECTED RESULT surplus0_meter_baseline > 0 (the meter's 3.0 kW less the baseline house load),
#   surplus0_meter_mutant = 0.0 (the irradiance model's dark step); null control: no meter configured, both 0.0.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g09 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._pv_forecast
#   (coordinator.py:9827 `if self._pv_production is not None and len(production):`).
# Perturbation: mutant 002980a15ae8b9a9, the guard -> `if False:`, in memory. Direction: surplus[0] down to the
#   model's value (the measured override of the step being acted on is lost).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402
import _pv_common as V  # noqa: E402

OLD = "if self._pv_production is not None and len(production):"
NEW = "if False:"
MUT = L.mutant(V.C, "_pv_forecast", OLD, NEW)
for label, meter in (("meter", 3.0), ("meter_over_peak", 9.0), ("nometer", None)):
    for name, fn in (("baseline", None), ("mutant", MUT)):
        s, summ = V.run(V.make(6.0, meter), "_pv_forecast", fn)
        print(f"RESULT surplus0_{label}_{name}={s[0]:.4f} kW  surplus_sum={sum(s):.4f} "
              f"forecast_production_kwh={summ.get('forecast_production_kwh')}")
L.trailer()
