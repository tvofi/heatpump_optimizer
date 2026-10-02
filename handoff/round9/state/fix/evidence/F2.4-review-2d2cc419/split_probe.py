"""Reviewer's own probe (not the finder's): over every golden scenario at the
tree in cwd, count plan steps where the new on schedule (space+dhw > 0.1) says
ON but pump_arbiter.step_duty's per-circuit split says 'idle' (each circuit
<= 0.1), plus steps where 0 < dhw <= 0.1 and 0 < space <= 0.1."""
import sys
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
import numpy as np
import golden
tot_steps = tot_split = tot_on = 0
per = []
for name, spec in golden.SCENARIOS.items():
    try:
        cap = golden.capture(name, dict(spec))
    except Exception as e:
        print("ERR", name, type(e).__name__, e); continue
    sp = np.asarray(cap.get("power_schedule") or [], float)
    dh = np.asarray(cap.get("dhw_power_schedule") or np.zeros_like(sp), float)
    if dh.size != sp.size: dh = np.zeros_like(sp)
    on = cap.get("heat_pump_on_schedule") or []
    split = int(((sp + dh) > 0.1) .__and__((sp <= 0.1) & (dh <= 0.1)).sum())
    trickle_dhw = int(((dh > 0) & (dh <= 0.1)).sum())
    tot_steps += sp.size; tot_split += split; tot_on += sum(1 for x in on if x)
    if split or trickle_dhw:
        per.append((name, split, trickle_dhw))
    print(f"{name:32s} steps={sp.size} on={sum(1 for x in on if x)} on_but_duty_idle={split} dhw_in_(0,0.1]={trickle_dhw}", flush=True)
print(f"RESULT scenarios={len(golden.SCENARIOS)} steps={tot_steps} on={tot_on} on_but_duty_idle={tot_split}")
print("RESULT nonzero", per)
