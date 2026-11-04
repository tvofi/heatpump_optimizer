"""Reviewer probe for R10-CEILING-PROBE rev 3, point 3/4: where the probe
store's median can be read, and whether the latch's static-share arithmetic
bounds it.  Run: python3 -I probe_reader.py <wt-main>

DrawRange and planned_range are imported from the worktree at origin/main
6fe5170cd; nothing is modified.
"""
import sys
WT = sys.argv[1]
sys.path.insert(0, WT + "/tests/hastub")
sys.path.insert(0, WT)
from custom_components.heatpump_optimizer.draw_range import DrawRange, planned_range

CFG = (1.0, 5.0)
HEAT, GATE = 55.0, 35.0
FULL = (HEAT, HEAT)          # flow_command once the ceiling is written
PLAIN = (40.0, HEAT)         # ordinary plan set-point: not full
REAL_MAX, PLAN_LEVEL, P_MAX = 3.0, 1.5, 5.0


class Cap:
    def plan_writes_power(self):
        return False

    def can_duty_cycle(self):
        return True


class Params:
    min_electrical_power = CFG[0]
    max_electrical_power = CFG[1]


def build(order, n_normal=288, n_probe=48):
    d = DrawRange()
    d.config = CFG
    d.commands_known = True
    for kind in order:
        if kind == "probe":
            for _ in range(n_probe):
                d.observe(REAL_MAX, P_MAX, *CFG, FULL)
        else:
            for _ in range(n_normal):
                d.observe(PLAN_LEVEL, PLAN_LEVEL, *CFG, PLAIN)
    return d


print("## R3: the latch under incremental evaluation (sticky, after every append)")
for label, order in (("probe first, ordinary after", ["probe", "normal"]),
                     ("ordinary first, probe last", ["normal", "probe"])):
    d = build(order)
    print(f"  {label}: engaged={d.engaged} samples={len(d.samples)} "
          f"final share=48/336=0.1429")

# the transient: 48 ceiling samples on an otherwise empty window
d = DrawRange()
d.config = CFG
d.commands_known = True
flip = None
for i in range(48):
    d.observe(REAL_MAX, P_MAX, *CFG, FULL)
    if flip is None and d.engaged:
        flip = i + 1
print(f"  first 48 ceiling appends on an empty window: engaged flips at append {flip}")

print()
print("## R4: the diagnostics value the note names as its consumer")
for label, order in (("F6 case: 48 ceiling, full window", ["normal", "probe"]),
                     ("twelve ceiling in the window", ["normal", "probe"])):
    d = build(order, n_probe=48 if label.startswith("F6") else 12)
    metered = d.planned(*CFG)
    pr = planned_range(d, Params(), Cap())
    obs = d.observed()
    summ = d.summary()
    print(f"  {label}: observed={obs} engaged={d.engaged} planned={metered}")
    print(f"    summary.observed_max_kw={summ['observed_max_kw']} "
          f"planned_range={pr} effective_max_kw="
          f"{None if pr is None else round(pr[1], 3)}")

# store-only: the median lives on the DrawRange but not in self.samples
d = build(["normal"])
print(f"  store-only median (12 samples, no window entries): observed={d.observed()} "
      f"engaged={d.engaged} planned={d.planned(*CFG)} "
      f"effective_max_kw=None (planned_range={planned_range(d, Params(), Cap())})")
