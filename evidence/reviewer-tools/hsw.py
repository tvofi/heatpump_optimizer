import sys, json
from pathlib import Path
root = Path(sys.argv[1]); ab = set(sys.argv[2].split(",")) if len(sys.argv) > 2 and sys.argv[2] else set()
sys.path.insert(0, str(Path(sys.argv[3] if len(sys.argv)>3 else root) / "tools/audit"))
from archscore.metrics import common as C, hub_solve_writes as H
if hasattr(C, "FOLLOW_RETURNS"): C.FOLLOW_RETURNS = "C15" not in ab
if hasattr(H, "EVENT_ROOTS"): H.EVENT_ROOTS = "C16" not in ab
m = H.measure(root)
print("RESULT hub_solve_writes", m["value"], "ablate=" + (",".join(sorted(ab)) or "none"))
d = m.get("details", {})
print(json.dumps({k: v for k, v in d.items() if k in ("per_root",)}, default=str))
if len(sys.argv) > 4:
    pkg = C.load(root); eng = C.engine(pkg)
    for q in H.roots(pkg) if hasattr(H, "roots") else []:
        for x in sorted(H._sites(eng, q)): print("SITE", q.rsplit(".",1)[-1], x[:4])
