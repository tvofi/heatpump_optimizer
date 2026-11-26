#!/usr/bin/env python3
# D3 wave judge instrument, round 11. Run from the repository root of a checkout of the baseline
# 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 with dev/audit/rounds/round11/D3/ copied over it (git fetch the handoff ref first):
#   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/wave-judge/harness/build_master.py
# Order: build_master, rerun, gatecmp, cross, analyse, dedup, compose, render. Writes only under $JUDGE_DIR and $TMPDIR.
import os, json, glob, pathlib, collections
W = pathlib.Path.cwd()
D3 = W / "dev/audit/rounds/round11/D3"
ver = json.load(open(D3 / "wave-verify/verify.json"))
votes = {v["key"]: v for v in ver["votes"]}
recs = {}
for p in sorted(glob.glob(str(D3 / "s1/REPORT-D3-g*.json"))):
    r = json.load(open(p))
    box = r.get("box") or pathlib.Path(p).stem.replace("REPORT-", "")
    for i, g in enumerate(r.get("gate_survivors", [])):
        g = dict(g); g["box"] = box; g["order"] = i
        recs[g["key"]] = g
print("reports keys", len(recs), "votes", len(votes))
missing = [k for k in votes if k not in recs]
print("votes without record", len(missing), missing[:5])
extra = [k for k in recs if k not in votes]
print("records without vote", len(extra), extra[:10])
master = []
for k, v in votes.items():
    g = recs.get(k, {})
    master.append({"key": k, "box": v["box"], "site": v["site"], "patch": v["patch"], "vote": v["vote"],
                   "vsev": v["severity"], "csev": v.get("severity_claimed"), "rec": g})
json.dump(master, open(os.path.join(os.environ.get("JUDGE_DIR", "dev/audit/rounds/round11/D3/wave-judge"), "master.json"), "w"), indent=1)
cmds = collections.Counter()
for m in master:
    c = m["rec"].get("probe", {}).get("command", "")
    cmds["--mutant" in c or "mutant" in json.dumps(m["rec"].get("probe", {}).get("command_mutant", ""))] += 1
print(cmds)
print(collections.Counter(m["rec"].get("gate", {}).get("verdict") for m in master))
print(collections.Counter(tuple(sorted(m["rec"].get("probe", {}).keys())) for m in master).most_common(5))
