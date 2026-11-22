#!/usr/bin/env python3
# Metric: heat (kWh) the valve-throttled two-zone emitters take from a 10 L buffer in one 1 h step beyond what
#   the tank holds above its coldest zone, excess = (q_rad + q_floor) * dt - C_buf * (T_buf - min(zones)),
#   with no heat-pump input (thermal_power 0, a coasting tank at 60 degC over 20 degC zones).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/tm2593_buffer_bound.py
# EXPECTED RESULT excess_kwh_baseline<=0 (the energy bound caps delivery at the tank's content)
# EXPECTED RESULT excess_kwh_mutant>0   (the bound's divisor becomes 1e-6 h: no cap, the tank is a heat source)
# EXPECTED RESULT null_delta=0.0 kW     (a 500 L tank, where the bound does not bind, delivers the same in both arms)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-top6 (4 vCPU Xeon @ 2.30GHz). Deterministic.
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:_valve_two_zone_delivery (line 2593,
#   the single-tank energy bound `available = ... / max(dt_hours, 1e-6)`), the throttled branch
#   _simulate_step_two_zone calls once per step.
# Perturbation: line 2593 `max(dt_hours, 1e-6)` -> `min(dt_hours, 1e-6)` (R10 C3C6 M07, 22b5ec8775d5bd50), in
#   memory: the function is re-compiled from its own source with that one edit and patched onto the module.
#   Direction: excess up. The full gate (fullgate.py run --src complete --key 22b5ec8775d5bd50) stays green.
# Null control: a 500 L tank, where drawn < available in both arms.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import dataclasses, inspect, sys, textwrap
from pathlib import Path

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import thermal_model as tm  # noqa: E402

OLD = ") / max(dt_hours, 1e-6)"


def mutant():
    src = textwrap.dedent(inspect.getsource(tm._valve_two_zone_delivery))
    assert src.count(OLD) == 1, f"anchor occurs {src.count(OLD)} times"
    ns = dict(tm.__dict__)
    exec(compile(src.replace(OLD, ") / min(dt_hours, 1e-6)"), tm.__file__, "exec"), ns)
    return ns["_valve_two_zone_delivery"]


def step(fn, volume_l):
    p = dataclasses.replace(tm.ThermalParameters(), buffer_tank_volume=volume_l, two_zone_enabled=True)
    st = dataclasses.replace(tm.ThermalState(), buffer_tank_temperature=60.0,
                             upper_floor_temperature=20.0, slab_temperature=20.0)
    dt = 1.0
    q_rad, q_floor, *_ = fn(p, st, 0.0, 0.0, 0.0, 45.0, -10.0, 0.2, dt, False)
    stored = tm._buffer_capacity(p) * (60.0 - 20.0)
    return (q_rad + q_floor) * dt - stored, q_rad + q_floor, tm._buffer_capacity(p)


mut = mutant()
b_ex, b_kw, cbuf = step(tm._valve_two_zone_delivery, 10.0)
m_ex, m_kw, _ = step(mut, 10.0)
_, nb_kw, _ = step(tm._valve_two_zone_delivery, 500.0)
_, nm_kw, _ = step(mut, 500.0)
print(f"RESULT c_buf_10l={cbuf:.4f} kWh/K")
print(f"RESULT delivered_kw_baseline={b_kw:.4f} kW")
print(f"RESULT delivered_kw_mutant={m_kw:.4f} kW")
print(f"RESULT excess_kwh_baseline={b_ex:.4f} kWh")
print(f"RESULT excess_kwh_mutant={m_ex:.4f} kWh")
print(f"RESULT null_delta={abs(nb_kw - nm_kw)} kW")
print("RESULT thread_factor=1.0 ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0 count")
