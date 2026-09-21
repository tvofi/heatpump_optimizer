"""Broader search, at the merge base, for a self-contained regression schedule
that reproduces R5-D2-02 at the shipped 6 kW. Two surfaces: the bare
`simulate_step` loop and the finding's `simulate_trajectory_with_dhw`.

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
from dataclasses import replace  # noqa: E402
from heatpump_optimizer import mixing_valve as MV  # noqa: E402
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState,
)

MP = 6.0


def model():
    return ThermalModel(ThermalParameters(
        two_zone_enabled=True, buffer_tank_volume=35.0,
        mixing_valve_mode=MV.MODE_MANUAL, mixing_valve_target=21.0,
        cop_flow_carnot=True, max_electrical_power=MP,
        buffer_max_temp=70.0,
    ))


def state():
    return ThermalState(
        room_temperature=21.0, upper_floor_temperature=21.0,
        lower_floor_temperature=20.5, slab_temperature=25.0,
        buffer_tank_temperature=32.0, outdoor_temperature=-5.0,
    )


def step_tail(m, base, bump, at):
    st = state()
    out = []
    for k, p in enumerate(base):
        st = m.simulate_step(st, float(p + (bump if k == at else 0.0)), -5.0,
                             dt_hours=0.25)
        out.append(st.buffer_tank_temperature)
    return np.asarray(out)


def traj_tail(m, base, bump, at, ext):
    n = len(base)
    out = []
    st = state()
    sched = base.copy()
    sched[at] += bump
    res = m.simulate_trajectory_with_dhw(
        st, sched, np.zeros(n), np.full(n, -5.0), np.zeros(n), np.zeros(n),
        np.zeros(n), dt_hours=0.25,
        external_heat_kw=ext, humidity=np.full(n, 55.0), start_hour=6.5,
    )
    return np.asarray(res[5], dtype=float)


def scan(fn, m, base, extra):
    b0 = np.asarray(fn(m, base, 0.0, -1, *extra), dtype=float)
    res = []
    for bump in (1e-3, 0.1, 1.0):
        worst, at = 0.0, None
        for i in range(len(base)):
            d = np.asarray(fn(m, base, bump, i, *extra), dtype=float)[i:] - b0[i:]
            mn = float(d.min())
            if mn < worst:
                worst, at = mn, i
        res.append((bump, worst, at))
    return res


def main():
    n = 48
    cands = {
        "ramp": np.linspace(0.0, MP, n),
        "ramp_rev": np.linspace(MP, 0.0, n),
        "sine": MP * (1.0 + np.sin(np.linspace(0, 6.0, n))) / 2.0,
        "blocks8": np.array([MP if (k // 8) % 2 == 0 else 0.0 for k in range(n)]),
        "blocks4": np.array([MP if (k // 4) % 2 == 0 else 0.0 for k in range(n)]),
        "saw": np.array([MP * ((k % 12) / 12.0) for k in range(n)]),
    }
    for seed in (99, 5, 11, 42, 101, 202):
        cands["rand%d" % seed] = np.random.default_rng(seed).uniform(0.0, MP, n)
    ext = np.zeros(n)
    ext[:8] = [MP * (1.0 - i / 8.0) for i in range(8)]
    for name, base in cands.items():
        m = model()
        res = scan(step_tail, m, base, ())
        print("STEP  %-9s n_sub=%d worst=%.4e  %s" % (
            name, m._stability_substeps(0.0, 0.0, 0.25), min(r[1] for r in res),
            " ".join("b=%g:%.4e@%s" % r for r in res)), flush=True)
    n = 96
    cands2 = {
        "rand99_96": np.random.default_rng(99).uniform(0.0, MP, n),
        "ramp_96": np.linspace(0.0, MP, n),
    }
    for name, base in cands2.items():
        for lbl, e in (("noext", np.zeros(n)), ("ext", np.concatenate([ext[:8], np.zeros(n - 8)]))):
            m = model()
            res = scan(traj_tail, m, base, (e,))
            print("TRAJ  %-9s %-6s n_sub=%d worst=%.4e  %s" % (
                name, lbl, m._stability_substeps(0.0, 0.0, 0.25),
                min(r[1] for r in res),
                " ".join("b=%g:%.4e@%s" % r for r in res)), flush=True)


if __name__ == "__main__":
    main()
