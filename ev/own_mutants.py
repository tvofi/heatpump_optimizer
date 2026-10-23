import subprocess, sys
from pathlib import Path
wt = Path(sys.argv[1])
M = [
 ("c1-queue-dropped","ci_critpath.py","s = max((new[x] for x in kept), default=start) + q","s = max((new[x] for x in kept), default=start)"),
 ("c2-p90-rank","ci_critpath.py","return sorted(xs)[math.ceil(0.9 * len(xs)) - 1]","return sorted(xs)[int(0.9 * len(xs))]"),
 ("c3-field-reset","ci_critpath.py",'        if not line.startswith("     "):\n            field = None','        if False:\n            field = None'),
 ("c4-jobs-paging","ci_critpath.py",'if len(d["jobs"]) < PAGE or len(out) >= d.get("total_count", 0):','if True:'),
 ("c5-runs-paging","ci_critpath.py",'if len(d["workflow_runs"]) < PAGE:','if True:'),
 ("c6-matrix-map","ci_critpath.py",'(m and (by_name.get(m[1]) or (m[1] if m[1] in needs else None)))','None'),
 ("c7-cycle-guard","ci_critpath.py",'        if n in path:\n','        if False:\n'),
 ("c8-expr-name","ci_critpath.py",'val.split(" (${{")[0] if val.endswith(")")','val if val.endswith(")")'),
 ("c9-git-first","ci_critpath.py",'p.stdout if p.returncode == 0','p.stdout if False'),
 ("c10-event-branch-q","ci_critpath.py",'q = "".join(f"&{k}={v}" for k, v in (("event", event), ("branch", branch)) if v)','q = ""'),
 ("c11-cf-path","ci_critpath.py",'cf_path=None if new is None else critical_path({n: g[n] for n in new}, new))','cf_path=None if new is None else critical_path(g, ends))'),
 ("f1-first-verdict","flow_metrics.py",'first.setdefault(v["pr"], v)','first[v["pr"]] = v'),
 ("f2-merge-window","flow_metrics.py",'if m and len(parents.split()) == 2 and a <= rs.when(t) < b:','if m and len(parents.split()) == 2:'),
 ("f3-roster-window","flow_metrics.py",'        if not a <= rs.when(t) < b:\n            continue','        if False:\n            continue'),
 ("f4-patchid","flow_metrics.py",'elif p["head"] == v["head"] or pr_patch(repo, tree, p["head"]) == pr_patch(repo, tree, v["head"]):','elif p["head"] == v["head"]:'),
 ("f5-unresolved","flow_metrics.py",'if not (has(repo, p["head"]) and has(repo, v["head"])):','if False:'),
 ("f6-prev-merge-kind","flow_metrics.py",'if not (p and p["kind"] == "merge" and a <= v["t"] < b):','if not (p and a <= v["t"] < b):'),
 ("f7-unjudged","flow_metrics.py",'unjudged=len(fixes) - len(judged)','unjudged=0'),
]
for mid, f, old, new in M:
    p = wt/"tools/audit/seat"/f
    src = p.read_text()
    n = src.count(old)
    if n != 1:
        print(f"{mid}: NOT APPLIED (pattern found {n} times)"); continue
    p.write_text(src.replace(old, new))
    try:
        r = subprocess.run([sys.executable, "-I", str(p), "--self-test"], capture_output=True, text=True, timeout=600)
        last = (r.stdout.strip().splitlines() or [""])[-1] if "self-test:" in r.stdout else (r.stderr.strip().splitlines() or ["?"])[-1]
        print(f"{mid}: {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} | {last}")
    except subprocess.TimeoutExpired:
        print(f"{mid}: KILLED (timeout)")
    finally:
        p.write_text(src)
