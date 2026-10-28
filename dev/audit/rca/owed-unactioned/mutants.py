#!/usr/bin/env python3
"""Plant each predicate's mutant in a scratch copy of owed_unactioned.py and
demand its --self-test refuse it. Prints one row per mutant: KILLED or SURVIVED.

    python3 -I mutants.py <checkout>
"""
import os, shutil, subprocess, sys, tempfile

SRC = os.path.join(sys.argv[1], "tools/audit/seat/owed_unactioned.py")
MUTANTS = [
    ("fires one sweep late", 'elif s["sweeps"] >= after:', 'elif s["sweeps"] > after:'),
    ("an ack never lapses", "if exp > now:", "if True:"),
    ("a stale board reads clean", "a stale board cannot say a line was discharged\")\n        return 2",
     "a stale board cannot say a line was discharged\")\n        return 0"),
    ("any ack covers any tip", "x.startswith(a[0]) or (len(a[0]) >= 7 and a[0].startswith(x)) for x in ids)",
     "True for x in ids)"),
    ("a re-read board counts a sweep", "(1 if fresh else 0)", "1"),
    ("DISPATCH lines leave the family", "OWED|REVIEW OWED:|DISPATCH:|", "OWED|REVIEW OWED:|"),
    ("a future ack is accepted", "at > now + dt.timedelta(minutes=5)", "False"),
    ("an over-long ttl is accepted", "not 0 < ttl <= TTL_MAX", "not 0 < ttl"),
    ("an unkeyable line is skipped", 'raise Unreadable(f"an owed line names no topic', 'return "?", shas\n    raise Unreadable(f"an owed line names no topic'),
    ("an unreadable state starts fresh", 'out(f"UNREADABLE: state {state_path}: {e}")\n        return 2',
     'state = {"board": None, "keys": {}}'),
]
src = open(SRC).read()
bad = 0
with tempfile.TemporaryDirectory() as d:
    for name, a, b in MUTANTS:
        if src.count(a) != 1:
            print(f"UNAPPLIED\t{name}"); bad += 1; continue
        p = os.path.join(d, "owed_unactioned.py")
        open(p, "w").write(src.replace(a, b))
        r = subprocess.run([sys.executable, "-I", p, "--self-test"], capture_output=True, text=True)
        tag = "KILLED" if r.returncode != 0 else "SURVIVED"
        bad += tag != "KILLED"
        print(f"{tag}\t{name}\t{r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip()[-80:]}")
print(f"mutants: {len(MUTANTS)}, not killed {bad}")
sys.exit(1 if bad else 0)
