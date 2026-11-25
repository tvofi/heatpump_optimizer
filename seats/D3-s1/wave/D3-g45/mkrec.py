#!/usr/bin/env python3
"""mkrec.py <key> <class> <probe_json_file>: writes results/<key>.json from gates/<key>.json + keys.tsv + a small spec."""
import csv, json, sys
key, cls, specf = sys.argv[1:4]
spec = json.load(open(specf))
g = json.load(open(f"gates/{key}.json"))
row = next(r for r in csv.DictReader(open("keys.tsv"), delimiter="\t") if r["key"] == key)
m = g["mutant"]
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
rec = {
 "key": key, "site": f"{m['file']}:{m['line']} {m['kind']}", "patch": f"{m['old'].strip()} -> {m['new'].strip()}",
 "function": row["function"], "cluster": row["cluster"],
 "gate": {k: g.get(k) for k in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end")} | {"failed_scripts": g["failed_scripts"], "provisional": True},
 "class": cls, "probe": spec["probe"], "should_fail": spec["should_fail"],
}
if cls == "candidate":
    f = spec["finding"]
    f.update({"step": "D3.M3", "scope": "D3-s1", "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", spec["probe"]["path"]],
      "evidence_command": f"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key {key}; PYTHONPATH=tests/hastub python3 {spec['probe']['path']}",
      "null_control": "fullgate.py null on box D3-g45: gate_rc=1, red scripts closure.py selftest, entities.py, harness_headers.py (stripped-tree artefacts); the mutant's red set is identical (killed_by empty)"})
    rec["finding"] = f
json.dump(rec, open(f"results/{key}.json", "w"), indent=1)
print("wrote", key, cls)
