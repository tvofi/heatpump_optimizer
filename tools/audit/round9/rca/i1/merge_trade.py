"""Unpinned count and new-unpinned anchors across one PR merge (merge^1 -> merge),
computed with each ref's OWN mutation_table.py and ledger, as the ratchet did."""
import subprocess, sys, tempfile, json, os
REPO = "/home/claude/heatpump_optimizer"
def at(ref):
    d = tempfile.mkdtemp(prefix="i1ref-")
    want = ["custom_components","tests/mutation_table.py","tests/mutation_budgets.json","tests/mutation_ledger","tests/closures.json"]
    have = [p for p in want if subprocess.run(["git","-C",REPO,"cat-file","-e",f"{ref}:{p}"]).returncode == 0]
    subprocess.run(f"git -C {REPO} archive {ref} {' '.join(have)} | tar -x -C {d}", shell=True, check=True)
    code = f"""
import sys,json; sys.path.insert(0,'tests'); import mutation_table as mt
b=mt.load_budgets() if hasattr(mt,'load_budgets') else json.load(open('tests/mutation_budgets.json'))
inv=mt.inventory(); u=mt.unpinned_sites(b,inv)
print(json.dumps(dict(n=len(u), rec=b.get('unpinned_sites'), anchors=sorted(s['file']+' '+s['kind']+' '+s['old'].strip() for s in u))))"""
    out = subprocess.run([sys.executable, "-c", code], cwd=d, capture_output=True, text=True, env=dict(os.environ, PYTHONPATH="tests/hastub"))
    if out.returncode: return None
    return json.loads(out.stdout.strip().splitlines()[-1])
m = sys.argv[1]
a, b = at(m + "^1"), at(m)
if a is None or b is None: print(m, "UNREADABLE"); sys.exit()
from collections import Counter
new = sorted((Counter(b["anchors"]) - Counter(a["anchors"])).elements()); gone = list((Counter(a["anchors"]) - Counter(b["anchors"])).elements())
print(f"{m} base={a['n']} head={b['n']} delta={b['n']-a['n']} new_unpinned={len(new)} removed_unpinned={len(gone)} refused_vs_base={int(b['n']>a['n'])} record_at_head={b['rec']} refused_vs_record={int(b['rec'] is not None and b['n']>b['rec'])}")
for x in new: print("   NEW", x)
