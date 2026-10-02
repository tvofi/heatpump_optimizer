"""Reviewer's own sweep (not the finder's harness): every tests/golden.py scenario,
DHW mode-blocked, prices shifted by DELTA in {-2,-3}. Reports DHW heat shipped while
blocked and the kwarg each _build_dhw_requirements call received for `blocked`.
Run from the repo root: PYTHONPATH=tests/hastub:custom_components:tests python3 b8_class_sweep.py"""
import sys, numpy as np
sys.argv = [sys.argv[0]]
import golden as G
from heatpump_optimizer.optimizer import HeatPumpOptimizer
orig = HeatPumpOptimizer._build_dhw_requirements
calls = []
def spy(self, *a, **k):
    calls.append(k.get("blocked", "<omitted>")); return orig(self, *a, **k)
HeatPumpOptimizer._build_dhw_requirements = spy
bad = 0; tot = 0
for name, spec in G.SCENARIOS.items():
    for d in (-2.0, -3.0):
        b = G.make(**spec); opt = b["optimizer"]; n = len(b["prices"])
        ext = G.external_heat_for(n) if name in G.EXTERNAL_HEAT_SCENARIOS else None
        calls.clear()
        try:
            res = opt.optimize(b["state"], np.asarray(b["prices"]) + d, b["outdoor"], b["wind"], b["rain"], b["solar"], G.START,
                               None, None, external_heat_kw=ext, dhw_blocked=True)
        except Exception as e:
            print(f"{name:28s} delta={d:+.1f} ERROR {type(e).__name__}: {e}"); continue
        dhw = np.asarray(res.dhw_power_schedule if res.dhw_power_schedule is not None else [0.0], dtype=float)
        kwh = float(dhw.sum() * opt.config.dt_hours); tot += 1
        bad += kwh > 1e-6
        print(f"{name:28s} delta={d:+.1f} shipped_dhw_kwh={kwh:.2f} calls={calls}")
print(f"RESULT runs={tot} shipped_while_blocked={bad}")
