"""draw_range evidence: when does the metered-draw latch engage, and what range would it clamp to.

Synthetic samples only. Each shape is fed WINDOW running samples per seed, under one
configured (min, max), and the harness prints, per shape: how many seeds engaged, and the
effective range ``planned_range`` returns on each install surface.

Shapes:
  live        configured 1-14 kW; plan asks U(3, 14), pump draws U(1.9, 2.55) -- the install
  null        the pump draws exactly what it is asked, asks U(min, max)
  mild        a correctly sized 6 kW pump part-loading: asks U(1, 2), draws ask * U(0.9, 1.1)
  mild-indep  the same pump whose draw does not follow the ask: asks U(1, 2), draws U(1, 2)

Run from a worktree root:
  PYTHONPATH=tests/hastub:custom_components python3 tools/audit/harnesses/draw_range_evidence.py [seeds]
"""
from __future__ import annotations

import sys

import numpy as np

from heatpump_optimizer import draw_range as dr
from heatpump_optimizer.thermal_model import InstallCapability, ThermalParameters

SURFACES = {
    "switch+setpoint": InstallCapability(frozenset({"switch", "setpoint"}), True, False),
    "duty-cycling": InstallCapability(frozenset({"setpoint"}), True, False),
    "frequency write": InstallCapability(frozenset({"switch", "frequency"}), True, True),
}
SHAPES = {
    "live": ((1.0, 14.0), lambda r, lo, hi: (r.uniform(3.0, 14.0), r.uniform(1.9, 2.55))),
    "null": ((1.0, 14.0), lambda r, lo, hi: (lambda a: (a, a))(r.uniform(lo, hi))),
    "mild": ((1.0, 6.0), lambda r, lo, hi: (lambda a: (a, a * r.uniform(0.9, 1.1)))(r.uniform(1.0, 2.0))),
    "mild-indep": ((1.0, 6.0), lambda r, lo, hi: (r.uniform(1.0, 2.0), r.uniform(1.0, 2.0))),
}


def run(seeds: int) -> None:
    for name, ((lo, hi), draw) in SHAPES.items():
        params = ThermalParameters()
        params.min_electrical_power, params.max_electrical_power = lo, hi
        engaged = 0
        last = None
        for seed in range(seeds):
            rng = np.random.default_rng(seed)
            d = dr.DrawRange()
            for _ in range(dr.WINDOW):
                asked, drawn = draw(rng, lo, hi)
                d.observe(drawn, asked, lo, hi)
            engaged += d.engaged
            last = d
        ranges = {k: dr.planned_range(last, params, cap) for k, cap in SURFACES.items()}
        print(f"{name:11s} cfg=({lo}, {hi}) engaged {engaged}/{seeds} seeds; "
              f"last seed observed={tuple(round(x, 3) for x in last.observed())} "
              + "; ".join(f"{k}: {None if v is None else tuple(round(x, 3) for x in v)}"
                          for k, v in ranges.items()))


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 20)
