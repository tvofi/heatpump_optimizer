#!/usr/bin/env python3
"""Reviewer-built: swap the presence probe cat-file -e -> rev-parse --verify -q
in the two sites, re-run the reviewer's class harnesses, restore, assert clean."""
import subprocess, sys, pathlib
WT = pathlib.Path("/private/tmp/rev-2883-r2/wt")
MT = WT/"tools/audit/merge_throughput.py"
RL = WT/"tools/audit/seat/roster_lib.py"
mt_orig, rl_orig = MT.read_text(), RL.read_text()
try:
    a = '"cat-file", "-e", f"{sha}:{path}"'
    b = '"rev-parse", "--verify", "--quiet", f"{sha}:{path}"'
    assert mt_orig.count(a) == 1, mt_orig.count(a)
    c = '"cat-file", "-e", f"{ref}:{CRITICAL_PATH_NAME}"'
    e = '"rev-parse", "--verify", "--quiet", f"{ref}:{CRITICAL_PATH_NAME}"'
    assert rl_orig.count(c) == 1, rl_orig.count(c)
    MT.write_text(mt_orig.replace(a, b)); RL.write_text(rl_orig.replace(c, e))
    for h in ("class_open.py", "class_open2.py"):
        r = subprocess.run([sys.executable, "-I", f"/private/tmp/rev-2883-r2/harness/{h}"],
                           capture_output=True, text=True)
        print(f"--- {h} (patched)")
        print("\n".join(l for l in r.stdout.splitlines() if "RESULT" in l))
finally:
    MT.write_text(mt_orig); RL.write_text(rl_orig)
clean = subprocess.run(["git","-C",str(WT),"status","--porcelain"],capture_output=True,text=True).stdout.strip()==""
print("RESULT restored_clean =", clean)
