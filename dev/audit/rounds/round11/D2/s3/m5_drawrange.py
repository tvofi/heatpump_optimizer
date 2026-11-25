"""D2.M5 draw-range-censored: a draw range learned from censored samples must not
narrow below the draw it could not observe.

Drives the production fold (draw_range.fold -> DrawRange.observe /
observe_ceiling) and reads the production bands: draw_range.solve_band (the
max/min a SOLVE books, from the ceiling store) and draw_range.planned_range
(the latched window's range, published as diagnostics effective_max_kw).

Pump: configured 1.0..6.0 kW electrical; its true running floor 1.5 kW.
  samples=uncensored            : the house load spans the range; 60 run
                                  samples asked 1.0..6.0 drawing max(ask, 1.5);
                                  14 system-identification intervals at the
                                  ceiling set-point drawing the true top.
                                  Two truths: top 5.6 (agrees) and top 4.0
                                  (a real over-statement the band must learn).
  samples=censored_at_minimum_power: mild weather; 60 run samples asked
                                  1.0..1.4 drawing 1.5 (the floor); 14 ceiling
                                  intervals where the load is under the pump's
                                  minimum, so it runs its floor: drawn 1.5.
                                  Truth top 5.6: nothing ever observed it.
Metric (one line): narrowing_kw = true top - solve_band(...).max_kw, the plan's
top booked below a draw the pump does deliver; identity <= 0.15*cfg_max where the
truth agrees, = 0 kW where it was never observed. Count key: the SolveBand the
coordinator stamps on a solve.
Also printed: planned_range high (diagnostics) and power_floor_kw.
Run:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D2/s3/m5_drawrange.py
      --perturb-floor : fold refuses a ceiling sample whose draw is within
      AGREE_TOLERANCE of the window's metered running floor
      (DrawRange.observed()[0]): censored narrowing_kw must go to_zero while
      the uncensored top-4.0 cell keeps its learned 4.0.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B6 (shared).
"""
import _common  # noqa: F401
from _common import footer, np

import argparse
import sys
from dataclasses import replace
from types import SimpleNamespace

sys.path.insert(0, "custom_components")
import harness  # noqa: F401,E402
from heatpump_optimizer import draw_range  # noqa: E402
from heatpump_optimizer.thermal_model import InstallCapability, ThermalParameters  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--perturb-floor", action="store_true")
A = ap.parse_args()

if A.perturb_floor:
    _orig_takes = draw_range.DrawRange.takes_ceiling

    def _takes(self, drawn_kw, command):
        seen = self.observed()
        if seen is not None and drawn_kw <= (1.0 + draw_range.AGREE_TOLERANCE) * seen[0]:
            return False
        return _orig_takes(self, drawn_kw, command)

    draw_range.DrawRange.takes_ceiling = _takes
    _orig_fold = draw_range.fold

    def _fold(draw, drawn_kw, split, params, **kw):
        if kw.get("experiment_s") is not None and not draw.takes_ceiling(drawn_kw, kw.get("command")):
            return None  # refused store evidence is not window evidence either
        return _orig_fold(draw, drawn_kw, split, params, **kw)

    draw_range.fold = _fold

P = replace(ThermalParameters(), min_electrical_power=1.0, max_electrical_power=6.0)
CAP = InstallCapability(writes=frozenset({"setpoint"}), measured_power=True, frequency=True)
CEIL = SimpleNamespace(written_c=55.0, gate_c=20.0, ceiling_c=55.0)
T0 = 1_800_000_000.0
rng = np.random.default_rng(11)


def run(cell, top):
    d = draw_range.DrawRange()
    t = T0
    for k in range(60):
        ask = rng.uniform(1.0, 6.0) if cell == "uncensored" else rng.uniform(1.0, 1.4)
        drawn = max(ask, 1.5) if cell == "uncensored" else 1.5
        drawn = min(drawn, top)
        draw_range.fold(d, drawn, (ask, 0.0), P, frozen=False, distorted=False, defrost=False,
                        command=None, experiment_s=None)
        t += 1800.0
    for k in range(14):
        drawn = top if cell == "uncensored" else 1.5
        draw_range.fold(d, drawn, (6.0, 0.0), P, frozen=False, distorted=False, defrost=False,
                        command=CEIL, experiment_s=t)
        t += 1800.0
    band = draw_range.solve_band(d, P, CAP, t)
    pr = draw_range.planned_range(d, P, CAP)
    floor = draw_range.power_floor_kw(d, P)
    return band, pr, floor


worst_censored = 0.0
worst_agree = 0.0
learned_4 = None
for cell, tops in (("censored_at_minimum_power", (5.6,)), ("uncensored", (5.6, 4.0))):
    parts = []
    for top in tops:
        band, pr, floor = run(cell, top)
        narrowing = top - band.max_kw
        parts.append(f"top={top}:solve_max={band.max_kw:.3f}({band.reason}) narrowing_kw={narrowing:+.3f} "
                     f"planned_range={None if pr is None else tuple(round(x, 3) for x in pr)} power_floor={floor:.3f}")
        if cell.startswith("censored"):
            worst_censored = max(worst_censored, narrowing)
        elif top == 5.6:
            worst_agree = max(worst_agree, narrowing)
        else:
            learned_4 = band.max_kw
    print(f"CELL draw-range-censored samples={cell} " + " | ".join(parts))
print(f"RESULT narrowing_censored_kw={worst_censored:.3f} kW")
print(f"RESULT narrowing_uncensored_agree_kw={worst_agree:.3f} kW")
print(f"RESULT uncensored_overstated_learned_max_kw={learned_4:.3f} kW")
footer()
