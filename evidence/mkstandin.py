"""Stand-in for the Linux strace recording of tests/harness_headers.py.

Takes the Darwin --single recording (audithook only; it records no inert_reads,
because harness_headers.py reads the harness files in child processes) and adds
one inert read, the one Linux strace recorded on main for #2017's file, at the
path this PR moves it to. A control arm adds an already-recorded harness instead.
"""
import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
src = json.load(open(os.path.join(here, "rec_hh", "harness_headers.py.json")))
for arm, path in (("standin_eg_b7", "dev/audit/harnesses/eg_b7_seam_hubs.py"),
                  ("standin_control", "dev/audit/harnesses/dual_path.py"),
                  ("standin_oldpath", "tools/audit/harnesses/eg_b7_seam_hubs.py")):
    rec = dict(src); rec["inert_reads"] = [path]
    d = os.path.join(here, arm); os.makedirs(d, exist_ok=True)
    json.dump(rec, open(os.path.join(d, "harness_headers.py.json"), "w"), indent=1)
    print(arm, path)
