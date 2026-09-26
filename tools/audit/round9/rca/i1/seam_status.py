"""RCA I1: for each round-9 I1 production seam at baseline, is it in the
mutation ratchet's inventory, is it pinned, and was it born before or after
the ratchet (#1426, 43dd4c34) landed?"""
import subprocess, sys, json
from pathlib import Path
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as mt
SEAMS = [("D3-s1-01","coordinator.py",1371),("D3-s1-91","coordinator.py",8112),
 ("D3-s1-91","coordinator.py",8384),("D3-s2-01","flow_lift.py",210),
 ("D3-s2-01","tariff.py",402),("D3-s2-01","price_model.py",324),
 ("D3-s2-01","price_model.py",349),("D3-s2-02","price_model.py",368),
 ("D3-s3-01","open_meteo.py",209),("D3-s3-02","dhw_draws.py",136),
 ("D3-s3-03","ledger.py",117),("D3-s3-04","dhw_learning.py",379),
 ("D3-s3-05","legionella.py",453)]
RATCHET = "43dd4c34"
budgets = mt.load_budgets()
inv = mt.inventory()
unp = {(s["file"], s["line"], s["kind"]) for s in mt.unpinned_sites(budgets, inv)}
by = {}
for s in inv:
    by.setdefault((s["file"], s["line"]), []).append(s["kind"])
for fid, f, ln in SEAMS:
    rel = mt.PKG + f
    kinds = by.get((rel, ln), [])
    pinned = [k for k in kinds if (rel, ln, k) not in unp]
    bl = subprocess.run(["git","blame","-L",f"{ln},{ln}","--porcelain","HEAD","--",rel],
                        capture_output=True,text=True).stdout.split()
    sha = bl[0][:8]
    after = subprocess.run(["git","merge-base","--is-ancestor",RATCHET,sha]).returncode == 0
    date = subprocess.run(["git","show","-s","--format=%ad","--date=short",sha],capture_output=True,text=True).stdout.strip()
    print(f"{fid:9} {f}:{ln:<5} inventoried={','.join(kinds) or 'NO':22} pinned={','.join(pinned) or '-':10} born={sha} {date} after_ratchet={int(after)}")
