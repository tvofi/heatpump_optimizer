import sys, hashlib, json
sys.path.insert(0, sys.argv[1])
import r10_water_setpoint_feedback as h
arms = [
 ("return, no power entity, option default", dict(power_entity=False)),
 ("return, no power entity, option off", dict(power_entity=False, feedback=False)),
 ("flow, no power entity, option default", dict(unit="flow", power_entity=False)),
 ("return, power entity, option off", dict(feedback=False)),
 ("return, power entity, option default (qualifying)", dict()),
]
for label, kw in arms:
    r = h.sim(**kw)
    w = json.dumps(r["writes"])
    tail = r["trace"][-30:]
    mean = sum(x[2] for x in tail)/len(tail)
    print(f"{label:52s} writes {len(r['writes']):4d} sha1 {hashlib.sha1(w.encode()).hexdigest()[:12]} mean {mean:.3f} kW starts {r['starts']}")
