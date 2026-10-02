"""ELIGIBLE count of tools/audit/merge_fastpath.py over main's last 30 PR merges.
Pair k: head = M^2, main = M^1 (what the fast path would have been asked just
before merge M). INJECT=1 overlays this branch's inert_reads on both tables
(history has none); INJECT=0 is the baseline predicate. Prints a per-pair class list."""
import re, json, os, subprocess, sys, io, contextlib
sys.path.insert(0, "tools/audit")
import merge_fastpath as m
inject = os.environ.get("INJECT") == "1"
reads = json.loads(open("tests/closures.json").read()).get("inert_reads", {})
orig = m._git
def git(*a):
    out = orig(*a)
    if inject and a[0] == "show" and a[1].endswith(":tests/closures.json"):
        t = json.loads(out); t["inert_reads"] = reads; return json.dumps(t)
    return out
m._git = git
merges = subprocess.run(["git","rev-list","--first-parent","--merges","-n",os.environ.get("N","30"),"origin/main"],
        capture_output=True,text=True).stdout.split()
elig = 0; rows = []
for M in merges:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try: rc = m.run(M + "^2", M + "^1", None)
        except Exception as e: rc = 9
    cls = sorted({l.split()[1].rstrip(":") for l in buf.getvalue().splitlines() if l.startswith("REFUSE")})
    mv = re.search(r"main changed (\d+) since", buf.getvalue())
    moved = int(mv.group(1)) if mv else 0
    elig += rc == 0 and moved > 0
    cls = (f"moved={moved} " + ",".join(cls)).strip()
    rows.append((M[:8], rc, cls))
for r in rows: print(*r)
print("ELIGIBLE (main moved, no refusal)", elig, "of", len(merges))
