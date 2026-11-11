#!/usr/bin/env python3
"""Refute #1293's stop-rule tightening, reproducibly, at this branch's head.

The branch does NOT carry #1293 (the L-BFGS-B stop rule, ``ftol`` 1e-6 ->
1e-9). It was reverted because the tightening buys money on most cells and
loses badly on one, and this script is the measurement: it re-applies the
reverted hunk to a checkout of this branch, drives the gate's own backtest and
a five-cell money table in both trees, and restores the file.

COMMAND (from the tree root):
  PYTHONPATH=tests/hastub python3 \
      tools/audit/round5/D0/seat-c/refute_1293.py <checkout>

``<checkout>`` must be a git worktree of THIS branch (a clean one: the script
edits ``custom_components/heatpump_optimizer/optimizer.py`` in place and
restores it, byte-compared, in a ``finally``).  A backup is written under
$TMPDIR first, so a crash leaves a recoverable copy and the restore line says
where it is.

THE RE-APPLICATION IT APPLIES is the whole of #1293, three substitutions:

  1. ``_LBFGSB_FTOL = 1e-9`` is inserted before ``def _lbfgsb_restart(``;
  2. and 3. both ``options={"maxiter": maxiter, "ftol": 1e-6, "eps": 1e-4},``
     literals (the restart's and the multi-start's) become
     ``"ftol": _LBFGSB_FTOL``.

WHAT IT PRINTS, and what this seat measured at the head:

  backtest, this head        ALL 25 BACKTEST CHECKS PASSED; shoulder-season
                             optimizer 4.44 against the night tariff's 4.48
  backtest, re-applied       FAIL ... [4.72 vs 4.48]; 1 of 25 failed
  the shoulder cell          every ftol 1e-6 shape reads 4.44 / 8.30 kWh and
                             every ftol 1e-9 shape reads 4.72 / 8.60 kWh --
                             the cut and the seeds do not move it either way,
                             so the regression is the stop rule's alone
  money across five cells    1e-6 -> 1e-9: D0 grid -0.816%, D0 cell 2 -0.334%,
                             winter single +0.000%, winter two -1.909%,
                             backtest shoulder +6.423% -- a large win on four
                             cells and a large loss on the fifth, while the
                             solve's own objective IMPROVES on that fifth
                             (-0.332%): the objective cannot see this trade,
                             which is why tests/backtest.py is the detector.
"""
import os
import subprocess
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

REL = os.path.join("custom_components", "heatpump_optimizer", "optimizer.py")
CONST = "_LBFGSB_FTOL = 1e-9"
ANCHOR = "def _lbfgsb_restart("
DICTS = 'options={"maxiter": maxiter, "ftol": 1e-6, "eps": 1e-4},'


def reapply(text):
    """The whole of #1293, count-asserted, so a moved anchor refuses."""
    assert text.count(ANCHOR) == 1, "the restart anchor moved"
    assert text.count(DICTS) == 2, f"{text.count(DICTS)} options dicts found"
    text = text.replace(ANCHOR, CONST + "\n\n\n" + ANCHOR)
    return text.replace(DICTS, DICTS.replace("1e-6", "_LBFGSB_FTOL"))


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: refute_1293.py <checkout>")
    root = os.path.abspath(sys.argv[1])
    path = os.path.join(root, REL)
    if not os.path.isdir(os.path.join(root, "custom_components")):
        raise SystemExit(f"{root} is not a checkout root")
    src = open(path).read()
    if "_LBFGSB_FTOL" in src:
        raise SystemExit(f"{root} already carries #1293; this script needs the "
                         f"reduced tree (the constant is absent there)")
    backup = os.path.join(os.environ.get("TMPDIR", "/tmp"),
                          "refute_1293_optimizer.py.bak")
    with open(backup, "w") as handle:
        handle.write(src)
    print(f"backup: {backup}")

    try:
        print("===== backtest, this head (no #1293)")
        rc, out = backtest(root)
        report(out)
        print(f"exit={rc}")

        with open(path, "w") as handle:
            handle.write(reapply(src))
        print("\n===== backtest, #1293 re-applied")
        rc, out = backtest(root)
        report(out)
        print(f"exit={rc}")

        print("\n===== the shoulder-season cell, arm by arm (re-applied tree)")
        shoulder_arms(root)

        print("\n===== five cells, money and objective, 1e-6 -> 1e-9")
        money(root)
    finally:
        with open(path, "w") as handle:
            handle.write(src)
        ok = open(path).read() == src
        print(f"\nrestored {path}: byte-identical={ok} (backup {backup})")


def backtest(root):
    env = dict(os.environ,
               PYTHONPATH=os.path.join(root, "tests", "hastub"))
    proc = subprocess.run([sys.executable, "tests/backtest.py"], cwd=root,
                          env=env, capture_output=True, text=True)
    return proc.returncode, proc.stdout


def report(out):
    for line in out.splitlines():
        if ("shoulder season" in line or "BACKTEST CHECKS" in line
                or line.strip().startswith("FAIL")):
            print(line)


def _solve(root, tz, dhw, pp, wp, ftol, cut=None, drop_seed=False):
    """One production solve in ``root`` with the stop rule at ``ftol``."""
    sys.path.insert(0, os.path.join(root, "tests"))
    sys.path.insert(0, os.path.join(root, "custom_components"))
    from datetime import datetime
    from unittest import mock
    import numpy as np
    from profiles import DT, house, prices, weather
    from heatpump_optimizer.optimizer import (HeatPumpOptimizer,
                                              OptimizationConfig)
    from heatpump_optimizer.thermal_model import (ThermalModel,
                                                  ThermalParameters,
                                                  ThermalState)
    import heatpump_optimizer.optimizer as om

    cfg = house(two_zone=tz)
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = dhw
    model = ThermalModel(params)
    opt = HeatPumpOptimizer(model, OptimizationConfig(
        horizon_hours=24, time_step_minutes=15, target_temp=21.0,
        min_temp=17.0, max_temp=23.0))
    start = datetime(2026, 1, 15)
    ps = prices(pp, start)
    od, wi, ra, so = weather(wp, start)
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0,
                      outdoor_temperature=float(od[0]),
                      upper_floor_temperature=21.0,
                      lower_floor_temperature=21.0,
                      buffer_tank_temperature=40.0, dhw_temperature=48.0)
    real = om._multi_start_minimize
    keep = om._MULTI_START_SOLVES

    def arm(objective, candidates, bounds, *a, **kw):
        cands = list(candidates)
        if drop_seed and len(cands) >= 5:
            cands = cands[:-1]
        om._MULTI_START_SOLVES = keep if cut is None else cut
        try:
            return real(objective, cands, bounds, *a, **kw)
        finally:
            om._MULTI_START_SOLVES = keep

    with mock.patch.object(om, "_LBFGSB_FTOL", ftol), \
            mock.patch.object(om, "_multi_start_minimize", arm):
        result = opt.optimize(st, ps, od, wi, ra, so, start)
    power = np.asarray(result.power_schedule, dtype=float)
    room, _, upper, lower, _, _, _ = model.simulate_trajectory(
        initial_state=st, power_schedule=power, outdoor_temps=od,
        wind_speeds=wi, precipitation=ra, solar_radiation=so, dt_hours=DT)
    indoor = np.minimum(upper[1:], lower[1:]) if params.two_zone_enabled \
        else room[1:]
    return (float(result.objective_value), float(np.sum(ps * power * DT)),
            float(np.sum(power) * DT), float(np.min(indoor)))


def shoulder_arms(root):
    shapes = [
        ("ftol 1e-9, shipped cut and seeds", 1e-9, None, False),
        ("ftol 1e-6, shipped cut and seeds", 1e-6, None, False),
        ("ftol 1e-6, cut back at 4", 1e-6, 4, False),
        ("ftol 1e-6, appended seed dropped", 1e-6, None, True),
        ("ftol 1e-9, cut back at 4", 1e-9, 4, False),
        ("ftol 1e-9, appended seed dropped", 1e-9, None, True),
    ]
    print(f"{'shape':38s} {'cost':>7s} {'kWh':>7s} {'min':>6s}")
    for label, ftol, cut, drop in shapes:
        obj, cost, kwh, mn = _solve(root, False, False, "shoulder", "shoulder",
                                    ftol, cut, drop)
        print(f"{label:38s} {cost:7.2f} {kwh:7.2f} {mn:6.2f}")


def money(root):
    cells = [
        ("D0 grid cell (tz=1,flat,winter_cold,nodhw)", True, False,
         "flat", "winter_cold"),
        ("D0 cell 2 (tz=1,shoulder,winter_cold,dhw)", True, True,
         "shoulder", "winter_cold"),
        ("backtest winter single (tz=0)", False, False,
         "winter_typical", "winter_cold"),
        ("backtest winter two (tz=1)", True, False,
         "winter_typical", "winter_cold"),
        ("backtest shoulder (tz=0)", False, False, "shoulder", "shoulder"),
    ]
    print(f"{'cell':44s} {'obj%':>8s} {'money%':>9s} {'kWh 1e-6 -> 1e-9':>18s}")
    for label, tz, dhw, pp, wp in cells:
        o1, c1, k1, _ = _solve(root, tz, dhw, pp, wp, 1e-9)
        o0, c0, k0, _ = _solve(root, tz, dhw, pp, wp, 1e-6)
        print(f"{label:44s} {100.0 * (o1 - o0) / abs(o0):+7.3f}% "
              f"{100.0 * (c1 - c0) / abs(c0):+8.3f}% {k0:6.2f} -> {k1:5.2f}")


if __name__ == "__main__":
    main()
