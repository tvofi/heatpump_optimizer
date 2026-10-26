"""Reviewer probe for R10-CEILING-PROBE rev 3: the probe store's feed and the
learned top's reader.  Run: python3 -I probe_store.py <wt-main>

The fold's inputs are modelled at origin/main 6fe5170cd: _record_accuracy
(coordinator.py:5861) runs after async_run_optimization (5826), and
_commanded_split (coordinator.py:4695) reads _current_action, which the solve
or the sysid override has just adopted (coordinator.py:3678,
boost.py:235).  So the ask and the command a closed interval is folded with
are the NEXT interval's.
"""
import sys
WT = sys.argv[1]
sys.path.insert(0, WT + "/tests/hastub")
sys.path.insert(0, WT)
import numpy as np
from custom_components.heatpump_optimizer.draw_range import DrawRange, is_running_space

CFG = (1.0, 5.0)
HEAT, GATE = 55.0, 35.0
CMD_FULL = (HEAT, HEAT)          # flow_command after the ceiling write
P_MAX, REAL_MAX, PLAN_LEVEL = 5.0, 3.0, 1.5
TOL = 0.15


def folds(step_cycles, pre_probe_draw=PLAN_LEVEL):
    """(drawn, asked, command) per interval, in the order fold sees them."""
    rows = []
    # the interval before the step: the plan runs, the step action is adopted
    rows.append((pre_probe_draw, P_MAX, CMD_FULL))
    for i in range(step_cycles):
        nxt = P_MAX if i < step_cycles - 1 else 0.0   # last step -> relax 0.0
        rows.append((REAL_MAX, nxt, CMD_FULL))
    return rows


def stored(rows):
    return [d for d, a, c in rows
            if is_running_space(d, a, 0.0, frozen=False, distorted=False, defrost=False)]


def probe_top(rows):
    got = stored(rows)
    if len(got) < 12:
        return None, len(got)
    med = float(np.median(got))
    return (med if med < (1.0 - TOL) * P_MAX else None), len(got)


print("## R1: what one probe run puts in the store (note's F2 arms)")
for label, cycles in (("2.0 h step (F2 leaky, 4 cycles)", 4),
                      ("1.0 h step (F2 tight, 2 cycles)", 2)):
    rows = folds(cycles)
    got = stored(rows)
    true = sum(1 for d, a, c in rows if d == REAL_MAX and a == P_MAX)
    print(f"  {label}: folded={len(rows)} stored={len(got)} true={true} "
          f"plan-draw={len(got)-true} values={[round(v,2) for v in got]}")

print("  null control: the interval before the step is idle (drawn 0.0)")
for label, cycles in (("2.0 h", 4), ("1.0 h", 2)):
    got = stored(folds(cycles, pre_probe_draw=0.0))
    print(f"    {label}: stored={len(got)} (no plan draw enters)")

print()
print("## R1b: the top of twelve with the per-run composition above")
for label, cycles in (("2.0 h", 4), ("1.0 h", 2)):
    per = stored(folds(cycles))
    got = per * (12 // len(per))
    top, n = probe_top([(v, P_MAX, CMD_FULL) for v in got])
    print(f"  {label}: 12 samples from {12//len(per)} runs "
          f"(true {(per.count(REAL_MAX))*(12//len(per))}) -> median {top}")
print("  control: twelve true ceiling draws -> median",
      float(np.median([REAL_MAX]*12)),
      "| adopted:", float(np.median([REAL_MAX]*12)) < (1-TOL)*P_MAX)
print("  control: twelve draws 4.5 kW (90% of configured) -> adopted:",
      4.5 < (1-TOL)*P_MAX)

print()
print("## R2: the reader. observed()/planned() with probe samples folded by observe")
def built(window, probe, probe_last):
    d = DrawRange(); d.config = CFG; d.commands_known = True
    for i in range(window):
        p = (i >= window - probe) if probe_last else (i < probe)
        d.observe(REAL_MAX if p else 1.5, P_MAX if p else 1.5, 1.0, 5.0,
                  CMD_FULL if p else (40.0, HEAT))
    return d

for label, window, probe, last in (
    ("note's case: full window, probe last", 336, 48, True),
    ("young window, probe first", 336, 48, False),
    ("twelve stored samples, full window", 336, 12, True),
):
    d = built(window, probe, last)
    print(f"  {label}: engaged={d.engaged} planned={d.planned(*CFG)} "
          f"observed={d.observed()} summary.observed_max_kw={d.summary()['observed_max_kw']}")
d = built(336, 0, True)
print("  null control: no probe samples -> engaged=%s planned=%s observed=%s"
      % (d.engaged, d.planned(*CFG), d.observed()))
