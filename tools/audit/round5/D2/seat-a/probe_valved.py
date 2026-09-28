"""Root-cause probe for R5-D2-02 (#1307): the 35 L valved buffer's non-monotone
response to commanded power.

Measures the bump scaling of the buffer trough (min T_buf over the tail after a
bump at step i) for the shipped 35 L valved config, and ablations:
  - as-shipped (cop_flow_carnot on)
  - cop_flow_carnot off
  - 100 L / 750 L tanks
and prints the per-step internals (cop, thermal_power, drawn, available, scale,
new_buf) around a reproducing bump.

Run from the repo root: PYTHONPATH=tests/hastub python3 <this file>
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np
from dataclasses import replace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d2a_common as C


def _build(volume=35.0, carnot=None):
    from tests.golden import make
    b = make(
        two_zone=True, dhw=False,
        config_overrides={
            "mixing_valve_mode": "manual", "buffer_tank_volume": volume,
            "buffer_max_temperature": 70.0,
        },
        state_overrides={"buffer_tank_temperature": 32.0},
    )
    if carnot is not None:
        b["optimizer"].model.params.cop_flow_carnot = carnot
    return b


def _run(b, sched, n):
    return b["optimizer"].model.simulate_trajectory_with_dhw(
        replace(b["state"]), sched, np.zeros(n), b["outdoor"], b["wind"],
        b["rain"], b["solar"],
        dt_hours=0.25, external_heat_kw=C.ext_forecast(n), humidity=np.full(n, 55.0),
        start_hour=6.5,
    )


def bump_scan(b, n=96, bumps=(1e-3, 1.0), seed=99, step=3):
    rng = np.random.default_rng(seed)
    base = rng.uniform(0, b["optimizer"].model.params.max_electrical_power, n)
    r0 = _run(b, base, n)
    buf0 = np.asarray(r0[5], dtype=float)  # index 5 == buffer_temps
    out = []
    for bump in bumps:
        worst = 0.0
        at = None
        for i in range(0, n, step):
            s = base.copy()
            s[i] += bump
            r1 = _run(b, s, n)
            buf1 = np.asarray(r1[5], dtype=float)
            d = buf1[i + 1:] - buf0[i + 1:]
            mn = float(d.min())
            if mn < worst:
                worst, at = mn, i
        out.append((bump, worst, at))
    return base, buf0, out


def internals(b, sched, i, n=96):
    """Step-by-step internals for a single bump at step i: returns dict."""
    model = b["optimizer"].model
    p = model.params
    st = replace(b["state"])
    kw = dict(dt_hours=0.25, external_heat_kw=C.ext_forecast(n),
              humidity=np.full(n, 55.0), start_hour=6.5)
    r0 = _run(b, sched, n)
    s2 = sched.copy()
    s2[i] += 1e-3
    r1 = _run(b, s2, n)
    return r0, r1


def main():
    print("== bump scan: as-shipped 35 L (carnot on) ==")
    b = _build(35.0)
    base, buf0, out = bump_scan(b)
    for bump, w, at in out:
        print("RESULT as_shipped bump=%g worst_cool_K=%.4e at_step=%s" % (bump, w, at))

    print("== ablation: cop_flow_carnot OFF (35 L) ==")
    b2 = _build(35.0, carnot=False)
    _, _, out2 = bump_scan(b2)
    for bump, w, at in out2:
        print("RESULT carnot_off bump=%g worst_cool_K=%.4e at_step=%s" % (bump, w, at))

    for vol in (100.0, 750.0):
        b3 = _build(vol)
        _, _, out3 = bump_scan(b3)
        for bump, w, at in out3:
            print("RESULT vol_%g bump=%g worst_cool_K=%.4e at_step=%s" % (vol, bump, w, at))

    # internals around a strong reproduction (bump 1.0 at step 33)
    print("== internals: bump +1.0 kW at step 33 (as-shipped 35 L) ==")
    b1 = _build(35.0)
    r0, r1 = internals(b1, base, 33)
    b0 = np.asarray(r0[5], dtype=float)
    b1a = np.asarray(r1[5], dtype=float)
    for j in range(30, 44):
        print("t=%2d  base=%9.4f  bump=%9.4f  d=%9.4f" % (j, b0[j], b1a[j], b1a[j] - b0[j]))

    for bump in (1e-3, 1.0):
        r0, r1 = internals(b1, base, 33)
        b0 = np.asarray(r0[5], dtype=float)
        b1a = np.asarray(r1[5], dtype=float)
        d = b1a - b0
        j = int(np.argmin(d))
        print("== worst for bump=%g at step %d (d=%.5f) ==" % (bump, j, d[j]))
        for jj in range(max(0, j - 3), min(96, j + 4)):
            print("t=%2d  base=%9.4f  bump=%9.4f  d=%9.5f" % (jj, b0[jj], b1a[jj], d[jj]))


if __name__ == "__main__":
    main()
