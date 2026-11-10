#!/usr/bin/env python3
"""R10-CARRY-SINK-BARRIER: which roster groups carry_audit accepts as a Carry destination.

    python3 dev/audit/harnesses/r10_carry_sink_barrier.py CODE_REV [ROSTER_REF]

Runs `Dests.check` from carry_audit.py and roster_lib.py as they stand at
CODE_REV, over every group of the round-10 roster at ROSTER_REF (default
origin/handoff/audit-r10-roster), and prints one RESULT line per stage:
`RESULT accepted[<stage>]=<n> of <m>`, plus `RESULT pending_on_accepted_closed=<n>`
-- the unmarked carries (`roster_lib.pending_carries`, no legacy exemption) on
groups at carries-open, refused or refuted that CODE_REV still accepts as a
destination. The defect reads non-zero at the base, zero at the fix; a live
stage (in-progress, not-started) reads the same at both ends (null control).
Reads only: `git show`; writes a temporary copy of the two modules.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROSTER = "dev/programme/rosters/wave-r10-groups.json"
MODULES = ("tools/audit/carry_audit.py", "tools/audit/seat/roster_lib.py")


def show(rev: str, path: str) -> str:
    return subprocess.run(["git", "show", f"{rev}:{path}"], check=True,
                          capture_output=True, text=True).stdout


def main(argv: list[str]) -> int:
    if not argv or len(argv) > 2:
        print(__doc__)
        return 2
    rev, ref = argv[0], (argv[1] if len(argv) > 1 else "origin/handoff/audit-r10-roster")
    roster = json.loads(show(ref, ROSTER))
    with tempfile.TemporaryDirectory() as d:
        for m in MODULES:
            p = Path(d, m)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(show(rev, m))
        sys.path[:0] = [str(Path(d, "tools/audit")), str(Path(d, "tools/audit/seat"))]
        import carry_audit
        import roster_lib
        dests = carry_audit.Dests(roster, set())
        total, ok, parked = Counter(), Counter(), 0
        for g in roster["groups"]:
            stage = (g.get("resume") or {}).get("stage")
            total[stage] += 1
            if dests.check(g["group"])[0]:
                ok[stage] += 1
                if stage in ("carries-open", "refused", "refuted"):
                    parked += len(roster_lib.pending_carries(g, {}))
    print(f"code {rev} roster {ref} ({subprocess.run(['git', 'rev-parse', ref], capture_output=True, text=True).stdout.strip()})")
    for stage in sorted(total):
        print(f"RESULT accepted[{stage}]={ok[stage]} of {total[stage]}")
    print(f"RESULT pending_on_accepted_closed={parked}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
