import sys, subprocess, importlib.util
spec = importlib.util.spec_from_file_location("cd", "/Users/timmalmstrom/hpo-seats/r10s6/orch-wt/tools/audit/seat/cloud_dispatch.py")
cd = importlib.util.module_from_spec(spec); sys.modules["cd"] = cd; spec.loader.exec_module(cd)
pool, newref, drop = sys.argv[1], sys.argv[2], sys.argv[3:]
cur = subprocess.run(["git","show",f"origin/dispatch/{pool}:POOL.txt"],capture_output=True,text=True,cwd="/Users/timmalmstrom/hpo-seats/r10s6/orch-wt").stdout.split("\n")
lines=[l for l in cur if l.strip() and l.strip() not in drop and l.strip()!=newref]
if "--top" in sys.argv: pass
lines=([newref]+lines) if "TOP" in __import__("os").environ else lines+[newref]
cd._publish("/Users/timmalmstrom/hpo-seats/r10s6/orch-wt", f"dispatch/{pool}", {"POOL.txt":"\n".join(lines)+"\n"})
