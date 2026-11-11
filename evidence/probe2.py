import sys; sys.path.insert(0, "dev/audit/harnesses")
import r10_water_setpoint_feedback as h
from heatpump_optimizer import pump_arbiter as pa
print("FEEDBACK_GATE_CLEAR_K", pa.FEEDBACK_GATE_CLEAR_K, "FEEDBACK_DOWN_K", pa.FEEDBACK_DOWN_K)
c = h.Coord(); print("gate floor (return unit)", pa._gate_floor_c(c.config if hasattr(c,'config') else c.entry.options) if False else "see writes")
up = {"plan_kw": [0.53] * 8 + [1.2] * 16}
for hl in (5.0, 15.0, 20.0, 21.0, 22.0, None):
    r = h.sim(limits=(None, hl), **up)
    s = [round(w[1],1) for w in r["writes"]]
    print(f"PROBE2 high-limit {hl}: writes {len(s)} at<=20.0 {sum(v<=20.0 for v in s)} lowest {min(s)} first5 {s[:5]} last3 {s[-3:]}")
