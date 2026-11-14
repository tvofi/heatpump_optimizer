#!/usr/bin/env python3
"""Revise step 3 (R6): every first-parent commit of main in the window that is not one of the 215 changes,
by kind and with its time. Writes data/main_moves.json."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
PD_DATA = _os.environ.get("PD_DATA", _os.path.join(_HERE, "..", "data")) + "/"
PD_REPO = _os.environ.get("PD_REPO", _os.path.abspath(_os.path.join(_HERE, "..", "..", "..", "..", "..", "..")))
import json, subprocess, collections, re
rows = {r["pr"] for r in json.load(open(PD_DATA + "baseline-2026-11-07.json"))}
o = subprocess.run(["git", "-C", PD_REPO, "log", "--first-parent", "--format=%H\t%ct\t%an\t%s", "--since=2026-11-07T00:00:00Z", "--until=2026-11-14T00:00:00Z", "origin/main"], capture_output=True, text=True).stdout
moves = []; c = collections.Counter()
for l in o.strip().splitlines():
    h, ct, an, s = l.split("\t", 3); m = re.match(r"Merge pull request #(\d+) from [^/\s]+/(\S+)", s)
    if m and int(m.group(1)) in rows: continue
    k = ("record pull request" if m and m.group(2).startswith("record/") else "dependabot pull request" if m and m.group(2).startswith("dependabot/")
         else "other pull request" if m else "stamp" if re.match(r"v\d+\.\d+\.\d+", s) else "ledger App push" if s.startswith("ci: ") else "other direct push")
    c[k] += 1; moves.append({"sha": h, "t": int(ct), "kind": k})
json.dump(moves, open(PD_DATA + "main_moves.json", "w"))
print("first-parent commits of main in the window that are not among the 215:", len(moves), dict(c))
