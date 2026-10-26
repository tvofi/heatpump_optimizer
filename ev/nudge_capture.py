"""Capture named golden scenarios at each census price nudge (the band census's own _nudged_make), from cwd's tree."""
import sys, os, json
sys.path.insert(0, os.path.join(os.getcwd(), "tests")); sys.path.insert(0, os.path.join(os.getcwd(), "custom_components"))
import numpy as np, golden
EPS = (0.0, 1e-15, 1e-12, 1e-9)
_make = golden.make; st = {"eps": 0.0}
def nm(**kw):
    b = _make(**kw); p = np.array(b["prices"], dtype=float); k = len(p) // 3
    p[k] = p[k] * (1.0 + st["eps"]) if p[k] else st["eps"]; b["prices"] = p; return b
golden.make = nm
out = {}
for name in sys.argv[2:]:
    for e in EPS:
        st["eps"] = e
        out[f"{name}@{e}"] = json.loads(json.dumps(golden.capture(name, golden.SCENARIOS[name])))
        print(name, e, flush=True)
json.dump(out, open(sys.argv[1], "w"))
