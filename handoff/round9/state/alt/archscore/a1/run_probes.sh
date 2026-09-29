#!/bin/bash
# Re-apply every perturbation and measure the prototype metrics (probes.py); writes probes.tsv.
A=$(cd "$(dirname "$0")" && pwd); cd $A
python3 probes.py wt-base > out/base.probes.json
for f in perturb/[GBN]*.py; do p=$(basename $f .py); ./run_one.sh $p >/dev/null 2>&1 && python3 probes.py wt-p > out/$p.probes.json; done
python3 - <<'PY'
import json, glob, os
b = json.load(open("out/base.probes.json")); keys = list(b)
rows = ["perturbation\t" + "\t".join(keys)]
rows.append("BASE\t" + "\t".join(str(b[k]) for k in keys))
for f in sorted(glob.glob("out/*.probes.json")):
    p = os.path.basename(f)[:-len(".probes.json")]
    if p == "base": continue
    d = json.load(open(f))
    rows.append(p + "\t" + "\t".join(f"{d[k]-b[k]:+d}" for k in keys))
open("probes.tsv", "w").write("\n".join(rows) + "\n")
PY
echo done
