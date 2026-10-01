"""Replay merge_fastpath.decide over consecutive merges on main: PR k verdicted
on main as it stood before merge k-1, and merge k-1 lands first. The roster of
selectable scripts is taken as main's table keys at merge k-1 (the checkout's
roster is today's, which older tables do not describe)."""
import json, subprocess, sys
from collections import Counter
sys.path.insert(0, "tools/audit"); import merge_fastpath as F
g = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout
tip, n = sys.argv[1], int(sys.argv[2])
ms = g("rev-list", "--first-parent", "--merges", f"-{n+1}", tip).split()
tally, rows = Counter(), []
for k in range(n):
    mk, prev = ms[k], ms[k+1]
    h = g("rev-parse", f"{mk}^2").strip()
    fork = g("merge-base", f"{mk}^1", h).strip()
    pr = sorted(set(g("diff", "--no-renames", "--name-only", f"{fork}...{h}").split()))
    M = sorted(set(g("diff", "--no-renames", "--name-only", f"{prev}^1", prev).split()))
    t_main = json.loads(g("show", f"{prev}:tests/closures.json"))
    t_head = json.loads(g("show", f"{h}:tests/closures.json"))
    wf = [g("show", f"{prev}:.github/workflows/{p}") for p in g("ls-tree", "--name-only", f"{prev}:.github/workflows").split()]
    F.closure.selectable_scripts = lambda t=t_main: sorted(t["closures"])
    al = F.always_scripts([g("show", f"{r}:tests/run.sh") for r in (prev, h)]) if len(sys.argv) < 4 else []
    found = F.decide(pr, M, {"main": t_main, "head": t_head}, F.grader_specs(wf), None, al)
    cls = sorted({c for c, _ in found}) or ["ELIGIBLE"]
    tally[cls[0] if len(cls) == 1 else "+".join(cls)] += 1
    rows.append(f"{mk[:8]} after {prev[:8]}: {','.join(cls)}")
print("\n".join(rows)); print(dict(tally))
print(f"eligible {sum(1 for r in rows if r.endswith('ELIGIBLE'))} of {n}")
