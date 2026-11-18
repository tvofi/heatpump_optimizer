"""I1 per-seam probe: FAILS (exit 1, 'UNEXERCISED <seam>') for every LEN seam
whose guard operand never evaluated False in any gate script traced by
run_trace.sh; that guard's protective branch is unreachable to every check, so
removing it (and->or) cannot turn the gate red. Reads run.trace + enumerate.out.
Command: python dev/audit/rounds/round10/D14/sweep-I1/probe_unexercised.py [seam ...]
Null control: a seam with an F=1 outcome (coordinator.py:4060) prints EXERCISED.
"""
import os, sys
H = os.path.dirname(os.path.abspath(__file__))
seen = set(l.split()[0] + " " + l.split()[1] for l in open(f"{H}/run.trace") if l.strip())
seams = [l.split()[2] for l in open(f"{H}/enumerate.out") if l.startswith("SEAM LEN")]
want = sys.argv[1:] or seams
bad = 0
for s in want:
    if f"{s} 0" in seen:
        print("EXERCISED", s)
    else:
        bad += 1; print("UNEXERCISED", s)
print(f"RESULT unexercised={bad} of {len(want)} count")
sys.exit(1 if bad else 0)
