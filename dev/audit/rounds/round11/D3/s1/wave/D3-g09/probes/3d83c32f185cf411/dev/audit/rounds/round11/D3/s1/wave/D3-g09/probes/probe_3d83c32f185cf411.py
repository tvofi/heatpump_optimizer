#!/usr/bin/env python3
# Metric: len(summary) of HeatPumpOptimizerCoordinator._pv_forecast(solar, 8) and sum(surplus) kW, PV enabled with
#   pv_peak_kw = 0 (the config flow's own minimum, config_flow.py:1933 _number(0, 100, ...)), and at peak 6 / -1.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_3d83c32f185cf411.py
# EXPECTED RESULT summary_keys_peak0_baseline=0 (the disabled-PV {}), summary_keys_peak0_mutant > 0 (a PV summary
#   published for a 0 kWp array); surplus sums equal (0 kW: production is scaled by peak 0) -- the null control is
#   peak 6, where both arms are identical.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g09 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._pv_forecast
#   (coordinator.py:9819 `if not config.enabled or config.peak_kw <= 0:`).
# Perturbation: mutant 3d83c32f185cf411, `<= 0` -> `< 0`, in memory. Direction: the summary goes from {} to a
#   populated dict at peak 0 (what the payload's pv block and the PV sensors read).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402
import _pv_common as V  # noqa: E402

OLD = "if not config.enabled or config.peak_kw <= 0:"
NEW = "if not config.enabled or config.peak_kw < 0:"
MUT = L.mutant(V.C, "_pv_forecast", OLD, NEW)
for label, peak in (("peak0", 0.0), ("peak6", 6.0), ("peakneg", -1.0)):
    for name, fn in (("baseline", None), ("mutant", MUT)):
        r = V.run(V.make(peak), "_pv_forecast", fn)
        if isinstance(r, str):
            print(f"RESULT {label}_{name}: {r}")
            continue
        s, summ = r
        print(f"RESULT summary_keys_{label}_{name}={len(summ)} surplus_sum_kw={sum(s):.4f}")
        if label == "peak0":
            print(f"RESULT summary_{label}_{name}={summ}")
L.trailer()
