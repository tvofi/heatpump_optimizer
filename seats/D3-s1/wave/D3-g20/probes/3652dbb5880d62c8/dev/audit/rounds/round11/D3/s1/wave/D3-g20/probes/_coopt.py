"""Shared body of the two _co_optimize probes (line 3969, the `pinned` mask).

Drives the production HeatPumpOptimizer._co_optimize (and through it the production _dhw_build and
duty_legs.space_headroom) with a recording DHW planner stand-in: _dhw_coil_wood_forecast -> None (no
wood coil), _build_dhw_requirements records the `space_demand` the re-plan is handed and returns a
schedule 0.5 kW off the incumbent; solve_space returns a candidate scoring 1.0 below best_score, so
whenever the pinned mask is non-empty the re-plan is adopted. draw_rates None (no combi store).
"""
from types import SimpleNamespace
import numpy as np
from _mutant import build, mutated, outcome, tail

OPT = build()
OPT._space_avail = None  # space_headroom = max(0, p_max - dhw)
P_MAX = 5.0


class Planner:
    def __init__(self):
        self.demands = []

    def _dhw_coil_wood_forecast(self, h, space, dhw):
        return None

    def _build_dhw_requirements(self, h, **kw):
        self.demands.append(np.asarray(kw["space_demand"], dtype=float).copy())
        return SimpleNamespace(schedule=np.asarray(self._dhw, dtype=float) + 0.5), np.zeros(len(self._dhw))


def call(space, dhw):
    pl = Planner()
    pl._dhw = dhw
    h = SimpleNamespace(power_caps_extra=None, dhw_blocked=False, off_steps=None,
                        step_hours=np.arange(len(dhw)) * 0.25)
    res = OPT._co_optimize(
        h, space_power=np.asarray(space, dtype=float), dhw_power=np.asarray(dhw, dtype=float), status="ok",
        best_score=10.0, solve_space=lambda dhw2, space0: (np.asarray(space0) + 1.0, "replanned", 9.0),
        p_max=P_MAX, planner=pl, draw_rates=None)
    pinned = int(np.sum(pl.demands[0] == P_MAX)) if pl.demands else 0
    return (res[2], pinned)


def cases():
    out = []
    for d in (0.0, 1e-6, float(np.nextafter(1e-6, 1)), float(np.nextafter(1e-6, 0)), 1.0, 4.0, 5.0):
        head = max(0.0, P_MAX - d)
        for lbl, s in (("head-2e-3", head - 2e-3), ("tie head-1e-3", head - 1e-3),
                       ("below tie", float(np.nextafter(head - 1e-3, -np.inf))),
                       ("above tie", float(np.nextafter(head - 1e-3, np.inf))), ("head", head), ("0", 0.0)):
            out.append((f"dhw={d!r} space={lbl} ({s!r})", [s], [d]))
    return out


def run(old, new, focus):
    moved, rows, frow = 0, [], None
    cs = cases()
    for label, s, d in cs:
        b = outcome(lambda: call(s, d))
        with mutated("_co_optimize", old, new):
            m = outcome(lambda: call(s, d))
        if b != m:
            moved += 1
            rows.append((label, b, m))
        if label.startswith(focus) and frow is None:
            frow = (label, b, m)
    print(f"RESULT inputs_tried={len(cs)} count")
    print(f"RESULT inputs_moved={moved} count")
    for label, b, m in rows[:4]:
        print(f"RESULT moved {label}: baseline(status,pinned)={b!r} mutant={m!r}")
    if frow:
        print(f"RESULT focus {frow[0]}: baseline(status,pinned)={frow[1]!r} mutant={frow[2]!r}")
    b = call([1.0], [1.0])
    with mutated("_co_optimize", old, new):
        m = call([1.0], [1.0])
    print(f"RESULT null_delta={0 if b == m else 1} count (dhw=1.0 space=1.0: far from both edges)")
    tail()
