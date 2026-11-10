import sys
sys.path.insert(0, sys.argv[1])
KW = eval(sys.argv[2]) if len(sys.argv) > 2 else {}
import r10_water_setpoint_feedback as h
for lo in (26.0, 26.4, 26.8, 27.2):
    r = h.sim(clamp=(lo, 50.0), **KW)
    tail = r["trace"][-30:]
    mean = sum(x[2] for x in tail)/len(tail)
    print(f"min-return clamp {lo}: writes {len(r['writes'])} issues {len(r['issues'])} mean {mean:.3f} kW starts {r['starts']} cut_lo {getattr(r['held'].feedback,'cut_lo_c',None)}")
