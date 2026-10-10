#!/usr/bin/env python3
import sys, os
FIX = os.environ["FIX"]
a = " ".join(sys.argv[1:])
if "pr list" in a:
    sys.stdout.write(open(os.path.join(FIX, "prs")).read())
elif "pr view" in a:
    sys.stdout.write(open(os.path.join(FIX, "head")).read().strip() + "\n")
elif "check-runs" in a:
    rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(FIX, "cr.tsv")) if l.strip()]
    if "group_by" in a:
        latest = {}
        for n, st, con, ts in rows:
            if n not in latest or ts >= latest[n][3]:
                latest[n] = (n, st, con, ts)
        for n in sorted(latest):
            if latest[n][2] == "failure":
                print(n)
    elif "length" in a:
        print(len(rows))
    else:
        for r in rows:
            print("\t".join(r))
elif "/rulesets/" in a:
    sys.stdout.write(open(os.path.join(FIX, "required")).read())
elif "/rulesets" in a:
    sys.stdout.write(open(os.path.join(FIX, "ruleset-id")).read())
else:
    sys.exit(0)
