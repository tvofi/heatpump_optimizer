"""review-2074c step 11: latest-per-name at the head, vs the required list from
ruleset 23698884. Names ABSENT required contexts as absent; lists every run whose
latest conclusion is neither success nor skipped/neutral."""
import json
import re
import subprocess
import sys
from collections import defaultdict

HEAD = "c54beab894db7210c570cd67f7cfb61212ed301c"
EV = "/Users/timmalmstrom/hpo-seats/review-2074c/ev"
polls = sorted(
    [p for p in subprocess.run(["ls", EV], capture_output=True, text=True).stdout
     .split() if re.match(r"checkruns_poll_\d+\.tsv$", p)],
    key=lambda s: int(re.findall(r"\d+", s)[0]))
rows = []
for p in polls:
    for ln in open(f"{EV}/{p}"):
        parts = ln.rstrip("\n").split("\t")
        if len(parts) >= 4:
            rows.append(parts)
# keep the LAST occurrence per (name, url) then latest per name
latest = {}
for name, status, concl, url in rows:
    latest[name] = (status, concl, url)
req = [c["context"] for c in
       (json.load(open(f"{EV}/ruleset_raw.json"))["rules"][0]["parameters"]
        ["required_status_checks"])]
print(f"polled files: {len(polls)} (last {polls[-1]})   distinct names: {len(latest)}")
print("\n## required contexts")
absent, bad = [], []
for c in req:
    if c not in latest:
        absent.append(c)
        print(f"  ABSENT   {c}")
    else:
        st, concl, url = latest[c]
        ok = st == "completed" and concl == "success"
        print(f"  {'success ' if ok else 'NOT-OK  '} {c:36s} {st}/{concl}")
        if not ok:
            bad.append((c, st, concl, url))
print(f"\nrequired: {len(req)}  absent: {len(absent)}  not-success: {len(bad)}")
print("\n## every name at the head whose latest is not success/skipped/neutral")
for name, (st, concl, url) in sorted(latest.items()):
    if not (st == "completed" and concl in ("success", "skipped", "neutral")):
        print(f"  {name}: {st}/{concl}  {url}")
print("\n## all names, latest-per-name")
for name, (st, concl, url) in sorted(latest.items()):
    print(f"  {name:38s} {st:10s} {concl}")
