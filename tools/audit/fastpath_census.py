#!/usr/bin/env python3
"""How often would tools/audit/merge_fastpath.py have said ELIGIBLE? (R9-F10.9d)

    N=120 INJECT=1 python3 tools/audit/fastpath_census.py          # per-merge lines + the count
    N=120 INJECT=1 python3 tools/audit/fastpath_census.py --files  # which unrecorded files refuse

Pair k is head = M^2 and main = M^1 for each of main's last N first-parent
merges M (the question the orchestrator would have asked just before merging
M). A pair counts as ELIGIBLE only when main had moved since the CI base and
`merge_fastpath.run` returned 0: a pair with main unmoved is trivially 0 and
tells nothing. INJECT=1 overlays tests/closures.json's `inert_reads` on both
tables, since history has none; INJECT=0 is the predicate before F10.9d.
"""
import collections
import contextlib
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import merge_fastpath as m  # noqa: E402

READS = json.loads((m.ROOT / "tests/closures.json").read_text()).get("inert_reads", {})
_git = m._git


def _show(*a):
    out = _git(*a)
    if os.environ.get("INJECT") == "1" and a[0] == "show" and a[1].endswith(":tests/closures.json"):
        t = json.loads(out)
        t["inert_reads"] = READS
        return json.dumps(t)
    return out


m._git = _show
merges = subprocess.run(["git", "rev-list", "--first-parent", "--merges", "-n", os.environ.get("N", "30"),
                         "origin/main"], capture_output=True, text=True, cwd=m.ROOT).stdout.split()
elig, files = 0, collections.Counter()
for M in merges:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            rc = m.run(M + "^2", M + "^1", None)
        except Exception:  # noqa: BLE001 -- a pair git cannot answer is not eligible
            rc = 9
    text = buf.getvalue()
    moved = int((re.search(r"main changed (\d+) since", text) or [0, 0])[1])
    classes = sorted({ln.split()[1].rstrip(":") for ln in text.splitlines() if ln.startswith("REFUSE")})
    elig += rc == 0 and moved > 0
    for ln in text.splitlines():
        if ln.startswith("REFUSE unrecorded"):
            f = re.search(r"changes (\S+),", ln).group(1)
            files["dev/programme/delivery/N.md" if "/delivery/" in f else "/".join(f.split("/")[:2])] += 1
    if "--files" not in sys.argv:
        print(M[:8], rc, f"moved={moved}", ",".join(classes))
if "--files" in sys.argv:
    print(files.most_common(15))
else:
    print("ELIGIBLE (main moved, no refusal)", elig, "of", len(merges))
