#!/usr/bin/env python3
"""Set-point-to-draw linearity and the ask judgement (#3106 item 4, R10-DRAW-MAP-EVIDENCE).

The measurement a local seat ran on one owner diagnostics download, ported to
run on a synthetic fixture this script generates (no row of that download is
in the tree), and on a seat's own bundle where one is handed to it. It asks
whether the metered draw follows the electrical level the code maps to a flow
set-point, and reads every answer beside the control that would have read the
same if it were false.

  map       the code's own map (``thermal_model.flow_setpoint_for_level``,
            inverted on a grid, floor from ``modulation_floor_flow_c``),
            no fitted parameter: residual draw by model fraction over steady
            heating minutes, and how many minutes the band's middle (0.25 to
            1.0) held
  fit       draw on held set-point over the minutes, linear; NULL: held
            set-points shuffled across segments (1000 permutations)
  store     the ``DrawRange`` rows (drawn, asked, written, ceiling): draw on
            written set-point, linear; NULL: written set-points shuffled
            across rows; PERTURBATION: a planted mid-band bump ``c*4u(1-u)``
            on the linear fit plus resampled residuals, counting the runs
            (of 50) where a quadratic beats the line on leave-one-out error
  ask       the run-asked rows judged by ``draw_range.ask_evidence`` (the
            production judgement), with their log-log slope, drawn over asked
            summed, and the factor the fitted level moves across the asks'
            span; NULL: the same asks drawn at one ratio (the summed level),
            which must follow
  steps     the draw's response to each set-point step, before against
            after (closed-loop levels are confounded: the feedback loop
            lowers the set-point because the draw is high); NULL: step sizes
            shuffled across events; PERTURBATION: a planted gain recovered
  ceiling   the ceiling store's gates (``draw_range.fold``): rows written at
            the ceiling, ceiling-store rows, and (bundle only) cycles whose
            action ran the system-identification experiment, the only
            intervals the store takes

Inputs. Default: the synthetic fixture, seeded, shaped like the measured
install (a 0.5 to 4.0 kW band, asks piled at the floor, drawn 1.75 x
ask**0.7, a shallow closed-loop draw on set-point). ``--bundle PATH``: a
diagnostics download's store rows and cycle rows only (no entity id is read);
``--minutes CSV`` adds minute rows ``setpoint_c,draw_kw,inlet_c,ok`` a seat
extracted from the bundle's replay out of tree (``ok`` 1 for a steady
heating minute, no booster, defrost or hot-water charge).

  PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/draw_map_linearity.py
  ... --bundle diag.json [--minutes minutes.csv]

Synthetic, at R10-DRAW-MAP-EVIDENCE's head: RESULT ask_evidence=does_not_follow
and RESULT ask_null_proportional=follows; at its base both read follows.
"""
from __future__ import annotations

import csv
import json
import sys

import numpy as np

from heatpump_optimizer import draw_range as dr
from heatpump_optimizer.pump_arbiter import FLOW_GATE_C
from heatpump_optimizer.thermal_model import flow_setpoint_for_level, modulation_floor_flow_c

SEED = 3106


def expected_kw(sp, inlet, p_min, p_max, heat_c, lift):
    """The draw the code books for a held set-point: its own map, inverted."""
    floor = modulation_floor_flow_c(inlet, FLOW_GATE_C, lift)
    levels = np.linspace(p_min, p_max, 351)
    sps = np.array([flow_setpoint_for_level(p, p_min, p_max, heat_c, floor) for p in levels])
    frac = (sp - floor) / (heat_c - floor) if heat_c > floor else float("nan")
    return float(np.interp(sp, sps, levels)), frac


def linfit(x, y):
    b = np.polyfit(x, y, 1)
    yh = np.polyval(b, x)
    return b, 1.0 - np.sum((y - yh) ** 2) / np.sum((y - y.mean()) ** 2)


def loo_rmse(x, y, deg):
    e = [y[i] - np.polyval(np.polyfit(np.delete(x, i), np.delete(y, i), deg), x[i]) for i in range(len(x))]
    return float(np.sqrt(np.mean(np.square(e))))


def synthetic(rng):
    """(config, store rows, minute rows, cycle rows) shaped like the measured install."""
    cfg = {"p_min": 0.5, "p_max": 4.0, "heat_c": 55.0, "lift": 10.0}
    asks = ([0.5] * 46 + [0.55 + 0.4 * i / 23 for i in range(24)] + [1.05 + 0.4 * i / 8 for i in range(9)]
            + [1.6, 1.9, 2.2, 2.4, 2.9] + [3.1 + 0.8 * i / 5 for i in range(6)])
    store = []
    for i, a in enumerate(asks):
        inlet = 30.0 + 10.0 * rng.random()
        floor = modulation_floor_flow_c(inlet, FLOW_GATE_C, cfg["lift"])
        written = flow_setpoint_for_level(a, cfg["p_min"], cfg["p_max"], cfg["heat_c"], floor)
        store.append((1.75 * a ** 0.7 * (1.15, 0.87, 1.0)[i % 3], a, written, cfg["heat_c"]))
    store += [(1.46 + 0.2 * rng.standard_normal(), 0.5, FLOW_GATE_C, cfg["heat_c"]) for _ in range(26)]
    minutes, sp = [], 40.0
    while len(minutes) < 1440:
        sp = float(rng.choice([30, 35, 38, 41, 44, 47, 50, 55]))
        inlet = 33.0 + 4.0 * rng.random()
        for _ in range(int(rng.integers(4, 40))):
            draw = 3.2 if sp >= 54.5 else 2.2 + 0.04 * (sp - 40.0)
            minutes.append((sp, draw + 0.35 * rng.standard_normal(), inlet, int(rng.random() > 0.2)))
    return cfg, store, minutes[:1440], None


def from_bundle(path, minutes_csv):
    data = json.load(open(path, encoding="utf-8"))["data"]
    c = data["config"]
    cfg = {"p_min": float(c["heat_pump_min_power"]), "p_max": float(c["heat_pump_max_power"]),
           "heat_c": float(c.get("flow_heat_c") or 55.0), "lift": float(c.get("flow_min_lift_k") or 5.0)}
    acc = next(v for k, v in data["debug"]["stores"].items() if k.endswith("_accuracy"))["accuracy"]["draw"]
    store = [tuple(r[:4]) for r in acc["samples"] if len(r) >= 4]
    cycles = [r.get("action_mode") for r in data["debug"].get("cycle_rows", []) if isinstance(r, dict)]
    minutes = None
    if minutes_csv:
        with open(minutes_csv, encoding="utf-8") as fh:
            minutes = [tuple(float(v) for v in row[:4]) for row in csv.reader(fh) if row and row[0][0].isdigit()]
    return cfg, store, minutes, (cycles, len(acc.get("ceiling", [])), acc)


def main(argv):
    rng = np.random.default_rng(SEED)
    if "--bundle" in argv:
        mins = argv[argv.index("--minutes") + 1] if "--minutes" in argv else None
        cfg, store, minutes, extra = from_bundle(argv[argv.index("--bundle") + 1], mins)
    else:
        cfg, store, minutes, extra = synthetic(rng)
    p_min, p_max, heat_c, lift = cfg["p_min"], cfg["p_max"], cfg["heat_c"], cfg["lift"]

    if minutes:
        m = np.array([r for r in minutes if r[3] and r[0] > FLOW_GATE_C + dr.GATE_TOLERANCE_K and r[1] > dr.RUNNING_FLOOR_KW])
        exp = np.array([expected_kw(sp, inlet, p_min, p_max, heat_c, lift) for sp, _, inlet, _ in m])
        res, frac = m[:, 1] - exp[:, 0], np.where(m[:, 0] >= heat_c - dr.CEILING_TOLERANCE_K, 1.0, exp[:, 1])
        print(f"RESULT map_minutes={len(m)}")
        print(f"RESULT map_bias_kw={res.mean():+.3f}")
        print(f"RESULT map_rms_kw={np.sqrt(np.mean(res ** 2)):.3f}")
        print(f"RESULT map_resid_floor_end_kw={res[frac < 0.25].mean():+.3f}")
        print(f"RESULT map_resid_ceiling_kw={res[frac >= 1.0].mean():+.3f}" if (frac >= 1.0).any() else "RESULT map_resid_ceiling_kw=none")
        print(f"RESULT minutes_mid_band={int(np.sum((frac >= 0.25) & (frac < 1.0)))}")
        seg = np.cumsum(np.r_[1, np.diff(m[:, 0]) != 0])
        (b, _), r2 = linfit(m[:, 0], m[:, 1])
        segs = np.unique(seg)
        means = np.array([m[seg == s, 0][0] for s in segs])
        null = []
        for _ in range(1000):
            perm = dict(zip(segs, rng.permutation(means)))
            null.append(linfit(np.array([perm[s] for s in seg]), m[:, 1])[1])
        print(f"RESULT fit_gain_kw_per_k={b:.4f} fit_r2={r2:.3f} fit_null_p95={np.percentile(null, 95):.3f}")
        steps(np.array([r for r in minutes]), rng)
    else:
        print("RESULT map_minutes=none")

    s = np.array([[np.nan if v is None else v for v in r] for r in store], float)
    hs = s[s[:, 2] > FLOW_GATE_C + dr.GATE_TOLERANCE_K]
    xs, ys = hs[:, 2], hs[:, 0]
    (b, a0), r2 = linfit(xs, ys)
    null = np.array([linfit(rng.permutation(xs), ys)[1] for _ in range(1000)])
    print(f"RESULT store_rows={len(s)} store_heating_rows={len(hs)}")
    print(f"RESULT store_gain_kw_per_k={b:.4f} store_r2={r2:.3f} store_null_p95={np.percentile(null, 95):.3f} "
          f"store_null_p={(1 + np.sum(null >= r2)) / (1 + len(null)):.4f}")
    base, u = np.polyval((b, a0), xs), (xs - xs.min()) / max(xs.max() - xs.min(), 1e-9)
    for c in (0.0, 0.35, 1.0):
        wins = sum(loo_rmse(xs, yy, 2) < loo_rmse(xs, yy, 1)
                   for yy in (base + rng.permutation(ys - base) + c * 4 * u * (1 - u) for _ in range(50)))
        print(f"RESULT curvature_c{c:.2f}_wins={wins}/50")

    window = dr.DrawRange()
    for d, asked, w, ceil in s:
        window.observe(d, asked, p_min, p_max, None if np.isnan(w) else (w, ceil))
    pairs = np.array(window._run_asked(), float)
    la, ld = np.log(pairs[:, 1]), np.log(pairs[:, 0])
    slope = float(np.polyfit(la, ld, 1)[0])
    lo, hi = np.percentile(pairs[:, 1], (dr.LOW_PERCENTILE, dr.HIGH_PERCENTILE))
    level = pairs[:, 0].sum() / pairs[:, 1].sum()
    print(f"RESULT ask_pairs={len(pairs)} ask_slope={slope:.3f} ask_level_sum={level:.3f} "
          f"ask_level_moves={(hi / lo) ** abs(1.0 - slope):.3f}")
    print(f"RESULT ask_evidence={dr.ask_evidence(window)}")
    flat = dr.DrawRange()
    for _, asked in pairs:
        flat.observe(level * asked, asked, p_min, p_max)
    print(f"RESULT ask_null_proportional={dr.ask_evidence(flat)}")

    at_ceiling = int(np.sum(s[:, 2] >= s[:, 3] - dr.CEILING_TOLERANCE_K))
    print(f"RESULT store_rows_at_ceiling={at_ceiling}")
    if extra is not None:
        cycles, ceiling_rows, _ = extra
        print(f"RESULT ceiling_store_rows={ceiling_rows} cycles={len(cycles)} "
              f"experiment_cycles={sum(1 for c in cycles if c == 'system_identification')}")
    return 0


def steps(mins, rng, pre=2, lo=1, hi=3):
    """Event study over minute rows: draw after a set-point step minus before."""
    ev = []
    for i in range(pre, len(mins) - hi):
        old, new = mins[i - 1, 0], mins[i, 0]
        if old == new or min(old, new) <= FLOW_GATE_C + dr.GATE_TOLERANCE_K:
            continue
        w = mins[i - pre:i + hi]
        if not w[:, 3].all() or np.any(np.diff(mins[i:i + hi, 0]) != 0) or np.any(np.diff(mins[i - pre:i, 0]) != 0):
            continue
        ev.append((new - old, mins[i + lo:i + hi, 1].mean() - mins[i - pre:i, 1].mean()))
    if len(ev) < 3:
        print(f"RESULT steps_n={len(ev)}")
        return
    x, y = np.array(ev).T
    g = float(np.dot(x, y) / np.dot(x, x))
    null = np.array([np.dot(p := rng.permutation(x), y) / np.dot(p, p) for _ in range(2000)])
    planted = np.median([np.dot(x, 0.27 * x + rng.permutation(y - g * x)) / np.dot(x, x) for _ in range(500)])
    print(f"RESULT steps_n={len(ev)} step_gain_kw_per_k={g:.3f} step_null_p97_5={np.percentile(np.abs(null), 95):.3f} "
          f"step_planted_0.27_recovered={planted:.3f}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
