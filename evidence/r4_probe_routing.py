"""R10-CEILING-PROBE final-note review probe: where the routing predicate reads.

Run: <seat python> -I probe_routing.py <worktree-at-6fe5170cd>

The note's re-cut B routes an interval to the `ceiling` deque when
``_current_action["mode"] == "system_identification"``.  Re-cut A proves that
every read made at the fold (``_commanded_split``, ``pump_arbiter.flow_command``
-> ``_current_action``) describes the NEXT interval, and its fix is a capture
of the interval's own pair.  The note's captured "pair" is the ask and the
command; the interval's KIND is not in it, and the routing sentence names
``_current_action`` -- so a fixer implementing the note literally reads the
kind at the fold, one interval late.

This probe measures both readings.  The window path is the real
``draw_range.fold``; only the routing decision and the store append are
modelled (the store is not on main).  Draws are realistic: the plan's own
p_max interval draws the pump's real maximum, the same as the probe's, so the
probe can only be told apart by WHICH interval is routed, not by its value.
"""
import sys

WT = sys.argv[1]
sys.path.insert(0, WT + "/tests/hastub")
sys.path.insert(0, WT)

from custom_components.heatpump_optimizer.draw_range import (  # noqa: E402
    CEILING_TOLERANCE_K, DrawRange, fold, is_running_space,
)

CFG = (1.0, 5.0)
HEAT, GATE = 55.0, 35.0
CMD_CEIL = (HEAT, HEAT)
CMD_PLAN = (42.0, HEAT)
P_MAX, REAL_MAX, PLAN_KW = 5.0, 3.0, 1.5
CEILING_TOL = CEILING_TOLERANCE_K


class Params:
    min_electrical_power = 1.0
    max_electrical_power = 5.0


class Cmd:
    def __init__(self, c):
        self.written_c, self.gate_c, self.ceiling_c = c[0], GATE, HEAT


def run(cycles, settling_at_pmax=False):
    """settling, `cycles` probe steps, one relax; each row: (drawn, asked, cmd, probe).

    ``settling_at_pmax`` is F6's own premise -- a plan interval that writes the
    ceiling at p_max -- and draws the pump's mild-weather ceiling draw (2.6 kW).
    """
    settle = ((2.6, P_MAX, CMD_CEIL, False) if settling_at_pmax
              else (PLAN_KW, PLAN_KW, CMD_PLAN, False))
    rows = [settle]
    rows += [(REAL_MAX, P_MAX, CMD_CEIL, True)] * cycles
    rows += [(PLAN_KW, PLAN_KW, CMD_PLAN, False)]
    return rows


def routed(rows, by_next):
    draw = DrawRange()
    store = []
    for i, (drawn, asked, cmd, probe) in enumerate(rows):
        kind = rows[i + 1][3] if (by_next and i + 1 < len(rows)) else probe
        full = cmd[0] >= cmd[1] - CEILING_TOL
        running = is_running_space(drawn, asked, 0.0, frozen=False,
                                   distorted=False, defrost=False)
        if kind and full and running:
            store.append(drawn)
            continue
        fold(draw, drawn, (asked, 0.0), Params(), frozen=False, distorted=False,
             defrost=False, command=Cmd(cmd))
    return len(draw.samples), store


print("## the note as written: the kind read at the fold (the NEXT interval's action)")
for cycles, label in ((4, "2.0 h step"), (2, "1.0 h step")):
    n, store = routed(run(cycles), by_next=True)
    print(f"  {label}: store={len(store)} samples {store}; window={n} samples")
print("  per twelve store samples: "
      f"{12 // 3} runs at 2.0 h, {12 // 1} runs at 1.0 h")
print("  the note's Evidence plan states: four samples for a 2.0 h step, two for a 1.0 h step")

print()
print("## control: the kind carried with the captured pair (THIS interval's action)")
for cycles, label in ((4, "2.0 h step"), (2, "1.0 h step")):
    n, store = routed(run(cycles), by_next=False)
    print(f"  {label}: store={len(store)} samples {store}; window={n} samples")
print("  per twelve store samples: "
      f"{12 // 4} runs at 2.0 h, {12 // 2} runs at 1.0 h")
print("  the note's Evidence plan states: four samples for a 2.0 h step, two for a 1.0 h step")

print()
print("## what moves: the kind read one interval late drops each run's LAST step")
print("## interval out of the store and into the window (one probe sample per run")
print("## reaches `observe`, which re-cut B says cannot happen), so the store gets")
print("## 3 and 1 samples per run, not the note's 4 and 2.")

print()
print("## F6's premise: the settling interval is a plan at p_max (cmd = ceiling, 2.6 kW)")
for cycles, label in ((4, "2.0 h step"), (2, "1.0 h step")):
    n, store = routed(run(cycles, settling_at_pmax=True), by_next=True)
    print(f"  read at the fold: store={store}; window={n} samples")
    n, store = routed(run(cycles, settling_at_pmax=True), by_next=False)
    print(f"  control (kind captured): store={store}; window={n} samples")
