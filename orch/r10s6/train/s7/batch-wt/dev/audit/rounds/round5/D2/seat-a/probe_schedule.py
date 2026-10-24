"""Find a `simulate_step`-loop schedule that reproduces R5-D2-02 on the shipped
35 L valved config, so the regression test can pin it without the trajectory
API's external-heat/start-hour machinery.

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


def model(vol=35.0):
    return ThermalModel(ThermalParameters(
        two_zone_enabled=True, buffer_tank_volume=vol,
        mixing_valve_mode=MV.MODE_MANUAL, mixing_valve_target=21.0,
        cop_flow_carnot=True,
    ))


def state():
    return ThermalState(
        room_temperature=21.0, upper_floor_temperature=21.0,
        lower_floor_temperature=20.5, slab_temperature=25.0,
        buffer_tank_temperature=32.0, outdoor_temperature=-5.0,
    )


def tail(m, sched, i):
    ts = sched[0].copy()
    ts[i] += sched[1]
    out = []
    st = state()
    for k in range(len(sched[0])):
        st = m.simulate_step(st, float(ts[k]), -5.0, dt_hours=0.25)
        out.append(st.buffer_tank_temperature)
    return np.asarray(out)


def scan(m, base, bumps, step=1):
    b0 = tail(m, (base, 0.0), 0)
    res = []
    for bump in bumps:
        worst, at = 0.0, None
        for i in range(0, len(base), step):
            d = tail(m, (base, bump), i)[i:] - b0[i:]
            mn = float(d.min())
            if mn < worst:
                worst, at = mn, i
        res.append((bump, worst, at))
    return res


def main():
    n = 48
    mp = model().params.max_electrical_power
    cands = {
        "rand99": np.random.default_rng(99).uniform(0.0, mp, n),
        "const_half": np.full(n, mp * 0.5),
        "pulse": np.array([mp if k % 4 == 0 else 0.0 for k in range(n)]),
        "ramp": np.linspace(0.0, mp, n),
    }
    for name, base in cands.items():
        for label, fixed in (("fix", False), ("base", True)):
            if fixed:
                _orig = ThermalModel._stability_substeps
                ThermalModel._stability_substeps = lambda self, w, p, dt: 1
            m = model()
            res = scan(m, base, (1e-3, 0.1, 1.0))
            if fixed:
                ThermalModel._stability_substeps = _orig
            print("RESULT 35L %-10s n_sub=%d %-5s %s" % (
                name, m._stability_substeps(0.0, 0.0, 0.25) if not fixed else 1,
                label, " ".join("b=%g:%.4e@%s" % r for r in res)), flush=True)


if __name__ == "__main__":
    main()
