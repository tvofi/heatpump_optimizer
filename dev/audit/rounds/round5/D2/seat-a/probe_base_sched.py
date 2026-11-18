"""At the merge base (fix deleted), find schedules/params that reproduce the
R5-D2-02 non-monotone buffer, to pin the regression test on a real failure.

Run from the worktree root: PYTHONPATH=tests/hastub python3 <this>
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

sys.path.insert(0, os.path.abspath(os.getcwd()))
sys.path.insert(0, os.path.join(os.path.abspath(os.getcwd()), "custom_components"))

import numpy as np  # noqa: E402
from heatpump_optimizer import mixing_valve as MV  # noqa: E402
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState,
)


def build(mp):
    return ThermalModel(ThermalParameters(
        two_zone_enabled=True, buffer_tank_volume=35.0,
        mixing_valve_mode=MV.MODE_MANUAL, mixing_valve_target=21.0,
        cop_flow_carnot=True, max_electrical_power=mp,
    ))


def tail(m, sched, bump, at):
    st = ThermalState(
        room_temperature=21.0, upper_floor_temperature=21.0,
        lower_floor_temperature=20.5, slab_temperature=25.0,
        buffer_tank_temperature=32.0, outdoor_temperature=-5.0,
    )
    out = []
    for k, p in enumerate(sched):
        st = m.simulate_step(st, float(p + (bump if k == at else 0.0)), -5.0,
                             dt_hours=0.25)
        out.append(st.buffer_tank_temperature)
    return np.asarray(out)


def scan(m, base, bumps=(1e-3, 0.1, 1.0)):
    b0 = tail(m, base, 0.0, -1)
    res = []
    for bump in bumps:
        worst, at = 0.0, None
        for i in range(len(base)):
            d = tail(m, base, bump, i)[i:] - b0[i:]
            mn = float(d.min())
            if mn < worst:
                worst, at = mn, i
        res.append((bump, worst, at))
    return res


def main():
    n = 48
    for mp in (5.0, 6.0):
        scheds = {}
        for seed in (99, 7, 1, 3):
            scheds["rand%d" % seed] = np.random.default_rng(seed).uniform(0.0, mp, n)
        scheds["half"] = np.full(n, mp * 0.5)
        scheds["pulse"] = np.array([mp if k % 2 == 0 else 0.0 for k in range(n)])
        scheds["ramp"] = np.linspace(0.0, mp, n)
        scheds["step_mid"] = np.array([0.0] * (n // 2) + [mp] * (n - n // 2))
        for name, base in scheds.items():
            m = build(mp)
            res = scan(m, base)
            worst = min(r[1] for r in res)
            print("RESULT mp=%.1f %-9s n_sub=%d worst=%.4e  %s" % (
                mp, name, m._stability_substeps(0.0, 0.0, 0.25), worst,
                " ".join("b=%g:%.4e@%s" % r for r in res)), flush=True)


if __name__ == "__main__":
    main()
