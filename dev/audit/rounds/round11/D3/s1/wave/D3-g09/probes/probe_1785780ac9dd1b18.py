#!/usr/bin/env python3
# Metric: summary.get("measured_production_kw") from HeatPumpOptimizerCoordinator._pv_forecast(solar, 8) with a
#   6 kWp array and a production meter reading 3.0 kW (None when the key is absent).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_1785780ac9dd1b18.py
# EXPECTED RESULT measured_production_kw_baseline=3.0, measured_production_kw_mutant=None; null control: no meter,
#   both None.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g09 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._pv_forecast
#   (coordinator.py:9836 `if self._pv_production is not None:`).
# Perturbation: mutant 1785780ac9dd1b18, the guard -> `if False:`, in memory. Direction: the key disappears from
#   the PV summary (self._pv_summary, what the payload publishes).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402
import _pv_common as V  # noqa: E402

OLD = "if self._pv_production is not None:"
NEW = "if False:"
MUT = L.mutant(V.C, "_pv_forecast", OLD, NEW)
for label, meter in (("meter", 3.0), ("nometer", None)):
    for name, fn in (("baseline", None), ("mutant", MUT)):
        c = V.make(6.0, meter)
        s, summ = V.run(c, "_pv_forecast", fn)
        print(f"RESULT measured_production_kw_{label}_{name}={summ.get('measured_production_kw')} "
              f"stored_summary_has_key={'measured_production_kw' in c._pv_summary}")
L.trailer()
