#!/usr/bin/env python3
"""D3-s1 box D3-u1d: list this slice's full-net (or pre) results whose drive
window overlaps a cgroup OOM kill, or that hold a signal-killed run (rc < 0,
not a timeout). Such a verdict is not trusted: an OOM SIGKILL of one worker's
test (or its process_worker child) reads as a kill in mutation_table.killed.

Metric: count of results per class (RCNEG, OVERLAP-KILLED, OVERLAP-SURVIVED).
Run: python3 dev/audit/rounds/round11/D3/s1/oom_overlap.py [--sub complete] [--write]
Reads state/oom.log (oomwatch.sh), state/keys-D3-u1d.txt, state/results/<sub>/.
--write: print the suspect keys one per line to state/oom-requeue-<sub>.txt.
Window: [mtime - complete_wall (or wall), mtime] of the result file.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-u1d.
"""
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = HERE / "state"
sub = sys.argv[sys.argv.index("--sub") + 1] if "--sub" in sys.argv else "complete"
ooms = []
for line in (S / "oom.log").read_text().splitlines():
    ts = line.split()[1]
    ooms.append(dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=dt.timezone.utc).timestamp())
keys = {k for k in (S / "keys-D3-u1d.txt").read_text().split()}
out = {"RCNEG": [], "OVERLAP-KILLED": [], "OVERLAP-SURVIVED": []}
for p in sorted((S / "results" / sub).glob("*.json")):
    if p.stem not in keys:
        continue
    r = json.loads(p.read_text())
    end = p.stat().st_mtime
    start = end - float(r.get("complete_wall") or r.get("wall") or 0) - 5
    neg = [s for s, j in r["runs"].items() if j["rc"] < 0 and not j.get("timed_out")]
    hit = any(start <= t <= end for t in ooms)
    if neg:
        out["RCNEG"].append((p.stem, r["verdict"], neg))
    elif hit:
        out["OVERLAP-" + ("KILLED" if r["verdict"] == "KILLED" else "SURVIVED")].append(
            (p.stem, r["verdict"], r["killed_by"]))
for c, v in out.items():
    print(f"RESULT {c.lower().replace('-', '_')}={len(v)}")
    for x in v:
        print("  ", *x)
if "--write" in sys.argv:
    (S / f"oom-requeue-{sub}.txt").write_text(
        "".join(k + "\n" for k, *_ in out["RCNEG"] + out["OVERLAP-KILLED"]))
