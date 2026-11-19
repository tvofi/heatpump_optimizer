"""D0-s2 M6 queue (round 11): the cells D0.M6 must close-loop, from race.py's results.

A cell enters when race.py measured gap_pct > 0.05 (the tolerance) AND the best feasible challenger's
step-0 action differs from production's (race.py `step0_differs`); a gap cell whose step 0 is identical
is answered by the race itself (the executed action is the same; MPC re-plans before the plans part).
Order: largest gap first. Prints one cell per line. Not a measuring harness.
Command: python3 dev/audit/rounds/round11/D0/s2/m6_queue.py [--all-gap]
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOL = 0.05


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(HERE, "results", "m4_shard*.jsonl"))):
        for l in open(f):
            r = json.loads(l)
            if r.get("gap_pct", 0) > TOL and (r.get("step0_differs") or "--all-gap" in sys.argv):
                rows.append((r["gap_pct"], r["cell"]))
    for _, c in sorted(rows, reverse=True):
        print(c)


if __name__ == "__main__":
    main()
