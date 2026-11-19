#!/usr/bin/env python3
"""D16.M3 cell ``disinfection`` x ``coordinator.py:3432 _disinfection_switch``: when the pump's
disinfection switch is on, against the steps the plan books the anti-legionella cycle on.

Metric (one line): on_in_window = minutes the switch entity reads on (after the production write,
the device stub applying it) inside the steps whose ``dhw_reasons[k]`` is ``legionella``, read by
plain indexing of the plan; on_outside = minutes it reads on outside them; also the mode in force
and the tank (pump model, effect.py) over the window.

Command:  PYTHONPATH=tests/hastub ~/venv-ci/bin/python3 dev/audit/rounds/round11/D16/s2/disinfect.py
          [--perturb track-after-adopt]
Expected (baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692): window steps 2-3 (06:30-07:00),
cycles at :01/:31: on_in_window=0, on_outside=30 (exact). Perturbation ``track-after-adopt`` (the
legionella cycle follower run again right after the solve adopts its action, the production
``LegionellaGuard.async_track_cycle``): on_in_window rises to 29. Null control: a window of six
steps (06:30-08:00) shows the same one-interval shift (on from 07:01 to 08:31, 59 of 90 minutes in
the window). Null control: no step booked, the switch is never on (null_on_minutes=0).
Machine: box B11 (shared); counts only.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import sys
import time
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cells  # noqa: E402
import rig  # noqa: E402
import timing  # noqa: E402


def run(window, total_steps, perturb=None):
    kinds = ["idle", "partial"] + ["partial"] * (total_steps - 2)
    r = cells.Run("disinfection", kinds, [])
    reasons = [("legionella" if k in window else None) for k in range(total_steps)]
    r.plan = rig.plan(timing.rows_for(kinds, r.f, r.P), dhw_reasons=reasons)
    c = r.sim.coord
    if perturb == "track-after-adopt":
        real_adopt = r.sim.adopt

        def adopt(result):
            real_adopt(result)
            tank = cells._num(r.sim.hass.states.get("sensor.tank").state)
            r.sim.run(c._legionella.async_track_cycle(tank))
        r.sim.adopt = adopt
    for m in range(total_steps * 15 + 15):
        r.minute(m)
    sw = [((wt - rig.T0).total_seconds() / 60, s_) for (wt, d, s_, dd) in r.sim.dev.log
          if dd.get("entity_id") == "switch.hp_disinfect"]
    booked = {m for k in window for m in range(k * 15, k * 15 + 15)}
    on, state, idx = set(), "off", 0
    for m in range(total_steps * 15 + 15):
        while idx < len(sw) and sw[idx][0] <= m:
            state = "on" if sw[idx][1] == "turn_on" else "off"
            idx += 1
        if state == "on":
            on.add(m)
    in_win = [s for s in r.samples if s[0] in booked]
    return {"switch_writes": sw, "on_in_window": len(on & booked), "on_outside": len(on - booked),
            "window_minutes": len(booked),
            "mode_hdhw_minutes_in_window": sum(1 for s in in_win if s[3] == "Heating + DHW"),
            "dhw_setpoint_at_target_minutes_in_window": sum(
                1 for s in in_win if (cells._num(s[5]) or 0) >= float(c._ctx._thermal_params.dhw_legionella_temp) - 0.5),
            "tank_end_of_run": round(r.pump.tank, 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", default=None)
    a = ap.parse_args()
    c0, t0 = time.process_time(), time.thread_time()
    short = run({2, 3}, 6, a.perturb)
    print(f"window steps 2-3: {short}")
    print(f"RESULT on_in_window={short['on_in_window']} minutes (of {short['window_minutes']})")
    print(f"RESULT on_outside={short['on_outside']} minutes")
    print(f"RESULT mode_hdhw_minutes_in_window={short['mode_hdhw_minutes_in_window']} minutes")
    null = run(set(), 6, a.perturb)
    print(f"no window booked (null control): {null}")
    print(f"RESULT null_on_minutes={null['on_in_window'] + null['on_outside']} minutes")
    long = run({2, 3, 4, 5, 6, 7}, 10, a.perturb)
    print(f"window steps 2-7: {long}")
    print(f"RESULT long_on_in_window={long['on_in_window']} minutes (of {long['window_minutes']})")
    print(f"RESULT long_on_outside={long['on_outside']} minutes")
    pc, tc = time.process_time() - c0, time.thread_time() - t0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
