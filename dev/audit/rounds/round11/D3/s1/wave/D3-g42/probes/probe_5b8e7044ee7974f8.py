#!/usr/bin/env python3
# Metric: wood_tank_temperature after apply_dhw_coil with the wood tank below the DHW inlet reference (q_coil == 0).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g42/probes/probe_5b8e7044ee7974f8.py
# Expected: wood_after baseline = unchanged (below inlet), mutant = raised to inlet => moved=1: candidate. Reads RESULT <metric>_baseline / _mutant per metric, then RESULT metrics_moved=<n>.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g42 (see wave/D3-g42/MACHINE.txt); exact arithmetic, no timing.
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel.apply_dhw_coil, line 5012.
# Perturbation: production line 5012 `q_coil > 0.0` -> `q_coil >= 0.0` (key 5b8e7044ee7974f8), applied to a scratch copy of custom_components (never the gate tree);
#   the baseline arm runs the untouched tree. Direction: see Expected.
# Null control: the metrics_moved count over inputs the line cannot distinguish (listed in the metric names); a gate at the comment-only marker (fullgate.py null) leaves the suite green.
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import main, hits
def _with_ua(p, ua):
    """Params whose dhw_tank_heat_loss_coefficient reads exactly `ua`: the property is memoised on
    (dhw_cooling_rate, dhw_tank_volume), so the cache is primed with the forced value (forced, not config-reachable)."""
    import dataclasses
    q = dataclasses.replace(p)
    q._dhw_ua_cache = ((q.dhw_cooling_rate, q.dhw_tank_volume), ua)
    return q
def _zero_ua(p): return _with_ua(p, 0.0)
def measure(mod):
    from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
    p=ThermalParameters(); m=ThermalModel(p)
    inlet=p.dhw_inlet_reference
    out=[("inlet",inlet)]
    for wood in (inlet-8.0, inlet-0.5, inlet, inlet+0.5, inlet+20.0):
        s=ThermalState(wood_tank_temperature=wood)
        d=m.apply_dhw_coil(s, 3.0, 50.0, 0.25)
        out.append((f"wood_after_from_{wood:.1f}",repr(s.wood_tank_temperature)))
        out.append((f"draw_from_{wood:.1f}",repr(d)))
    return out
if __name__ == "__main__":
    main("5b8e7044ee7974f8", measure, __file__)
