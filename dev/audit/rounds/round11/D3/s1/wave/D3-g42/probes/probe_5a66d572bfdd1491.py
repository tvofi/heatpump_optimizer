#!/usr/bin/env python3
# Metric: two-zone buffer step outputs (new buffer temp, refused heat) over a grid of buffer temperatures incl. the cap tie, and the hit count of line 4020.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g42/probes/probe_5a66d572bfdd1491.py
# Expected: metrics_moved=0 (at equality refused=(dT_buf-dT_cap)*C=0 and dT_buf=dT_cap: both branches write identical values) => equivalent-candidate. Reads RESULT <metric>_baseline / _mutant per metric, then RESULT metrics_moved=<n>.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g42 (see wave/D3-g42/MACHINE.txt); exact arithmetic, no timing.
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:ThermalModel._simulate_step_two_zone, line 4020.
# Perturbation: production line 4020 `dT_buf > dT_cap` -> `dT_buf >= dT_cap` (key 5a66d572bfdd1491), applied to a scratch copy of custom_components (never the gate tree);
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
    out=[]
    p=ThermalParameters(two_zone_enabled=True, mixing_valve_mode="manual")
    m=ThermalModel(p)
    cap=p.buffer_max_temp
    res=[]
    def run():
        for tb in (cap-5, cap-0.5, cap-0.01, cap, cap+0.01, cap+3):
            for pw in (0.0, 0.5, 2.0, 6.0, 12.0):
                for dt in (0.0625, 0.25, 1.0):
                    s=ThermalState(buffer_tank_temperature=tb)
                    n=m.simulate_step(s, pw, 2.0, dt_hours=dt)
                    res.append((tb,pw,dt,repr(n.buffer_tank_temperature),repr(m._step_buffer_refused)))
    h=hits(mod,"thermal_model.py",4020,run)
    out.append(("line_4020_hits",h)); out.append(("grid_cells",len(res)))
    out.append(("grid_digest",hash(tuple(res))%10**9 if False else __import__("hashlib").md5(repr(res).encode()).hexdigest()))
    out.append(("refused_nonzero_cells",sum(1 for r in res if float(r[4])!=0.0)))
    return out
if __name__ == "__main__":
    main("5a66d572bfdd1491", measure, __file__)
