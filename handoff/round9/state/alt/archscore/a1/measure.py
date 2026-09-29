#!/usr/bin/env python3
"""Import tests/structure.py from a worktree and print measure()['metrics'] as JSON."""
import importlib.util, json, sys, io, contextlib
wt = sys.argv[1]
spec = importlib.util.spec_from_file_location("structure_m", f"{wt}/tests/structure.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
res = m.measure()
out = dict(res["metrics"])
if len(sys.argv) > 2 and sys.argv[2] == "--tables":
    t = res["tables"]
    out["_dup"] = t["duplication"]; out["_dead_methods"] = t["dead_methods"]; out["_dead_symbols"]=t["dead_symbols"]
print(json.dumps(out, sort_keys=True, default=str))
