"""Reviewer-built probe (not the finder's): edges of the new clamp in _feedback_bounds."""
import sys, os
sys.path.insert(0, os.environ["HARN"])
import r10_water_setpoint_feedback as h
from heatpump_optimizer import pump_arbiter as pa
from datetime import timedelta
up = {"plan_kw": [0.53] * 8 + [1.2] * 16}
def gate(unit, step=0.1):
    return pa._gate_c(h.Coord(unit=unit, step=step).arbiter_inputs())
# 1. direct bounds, every source x edge
for unit in ("return", "flow"):
  for step in (0.1, 0.5, 1.0):
    g = gate(unit, step)
    for src in ("sensor", "cut", "both"):
      for off in (-25.0, -5.0, -step, 0.0, 0.005, 0.01, step/2, step - 0.001, step, step + 0.001, 2*step):
        lim = round(g + off, 4)
        c = h.Coord(unit=unit, step=step, limits=(None, lim if src in ("sensor","both") else None))
        inp = c.arbiter_inputs(); held = pa.state_for(c)
        rec = pa.FeedbackRun(start=h.T0, w_c=30.0, seen=h.T0, cut_hi_c=lim if src in ("cut","both") else None)
        lo, hi = pa._feedback_bounds(held, rec, inp, 26.0)
        rec.w_c = min(max(30.0, lo), hi)
        w = pa._bounded(inp, "space_setpoint", rec.w_c, lo=lo, hi=hi)
        print(f"BOUNDS {unit:6s} step {step} gate {g:.1f} src {src:6s} limit {lim:8.3f} lo {lo:.2f} hi {hi:.2f} write {w} above-gate {w is not None and w > g}")
# 2. placeholder sensor states
for st in ("unavailable", "unknown", "", "nan", "0", "-20", "-20.1", "100", "100.1", "inf"):
    r = h.sim(limits=(None, st), **up)
    s = [w[1] for w in r["writes"]]
    print(f"PLACEHOLDER high {st!r:14s} writes {len(s)} lowest {min(s):.1f} highest {max(s):.1f} at<=gate {sum(v<=20.0 for v in s)}")
# 3. controller clamp maximum under / at / just over the gate (cut path, no sensor)
for cmax in (18.0, 20.0, 20.1, 21.0):
    r = h.sim(clamp=(10.0, cmax), **up)
    s = [w[1] for w in r["writes"]]
    print(f"CLAMPMAX {cmax}: writes {len(s)} lowest {min(s):.1f} at<=gate {sum(v<=20.0 for v in s)} retry-passes {len(r['issues'])}")
# 4. unset space_setpoint entity state
c = h.Coord(limits=(None, 20.0)); c.hass.states._states.pop(h.SET, None) if hasattr(c.hass.states, "_states") else None
inp = c.arbiter_inputs(); held = pa.state_for(c)
rec = pa.FeedbackRun(start=h.T0, w_c=30.0, seen=h.T0)
try:
    lo, hi = pa._feedback_bounds(held, rec, inp, 26.0)
    print(f"UNSET-SLOT state {c.hass.states.get(h.SET)} bounds {lo:.2f} {hi:.2f} write {pa._bounded(inp, 'space_setpoint', min(max(30.0, lo), hi), lo=lo, hi=hi)}")
except Exception as e:
    print("UNSET-SLOT raised", type(e).__name__, e)
