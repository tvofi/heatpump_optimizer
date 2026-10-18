"""Reviewer's own re-derivation: non-merge commits on a ref adding an inert_reads pair."""
import json, subprocess, sys
repo, ref = sys.argv[1], sys.argv[2]
def g(*a): return subprocess.run(["git","-C",repo,*a],capture_output=True,text=True).stdout
def pairs(sha):
    s = g("show", f"{sha}:tests/closures.json")
    try: d = json.loads(s)
    except Exception: return set()
    ir = d.get("inert_reads", {}) or {}
    return {(k, f) for k, v in ir.items() for f in v}
rows = g("log","--no-merges","--format=%H|%P|%an|%cI|%s",ref,"--","tests/closures.json").splitlines()
out=[]
for r in rows:
    sha, par, an, date, subj = r.split("|",4)
    p = par.split()[0] if par else None
    added = pairs(sha) - (pairs(p) if p else set())
    if added:
        bot = subj.startswith("ci: re-record closures") or "[bot]" in an
        out.append((date, sha[:9], "bot" if bot else "hand", an, len(added), subj[:60], sorted(added)))
for o in sorted(out): print(o[0],o[1],o[2],o[3],o[4],o[5]," ; ".join(f"{a}<-{b}" for a,b in o[6][:3]))
print("TOTAL", len(out), "bot", sum(o[2]=="bot" for o in out), "hand", sum(o[2]=="hand" for o in out))
