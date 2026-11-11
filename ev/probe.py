import sys; sys.path.insert(0, "/tmp/tmp.ZVonrdRvqq/fh")
import r10_water_setpoint_feedback as h
up = {"plan_kw": [0.53] * 8 + [1.2] * 16}
for label, limits, kw in (
  ("low limit 40 above ceiling 32", (40.0, None), dict(up, ceiling=32.0)),
  ("low limit 31.9 just under ceiling 32", (31.9, None), dict(up, ceiling=32.0)),
  ("high limit 20 below gate+clear", (None, 20.0), dict(up)),
  ("high limit 24 below inlet-DOWN?", (None, 24.0), dict(up)),
  ("none", (None, None), dict(up)),
):
    r = h.sim(limits=limits, **kw)
    s = [w[1] for w in r["writes"]]
    print(f"PROBE {label:40s} writes {len(s)} lowest {min(s):.1f} highest {max(s):.1f} loop-writes>32 {sum(v>32.0 for v in s)} issues {r['issues'][:2]}")
