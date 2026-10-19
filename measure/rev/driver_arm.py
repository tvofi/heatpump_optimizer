#!/usr/bin/env python3
"""Revision 4, R4-2: the probe's sweep driver, scored in gate_sim.py's own world.

`workflow_run` fires only for a workflow file on the default branch, so on a
`probe/ci-layout-*` ref `gate-sweep.yml` never runs. Before merge the sweep is
therefore driven by `tools/audit/seat/sweep_driver.py` (DESIGN-P2.md section 10): a
seat-side loop that lists the probe PR's `ci.yml` runs every DRIVER_POLL s and, for
each run it sees newly completed with a green latest `gate`, runs the identical entry
point `gate-sweep.yml` runs, `gate.py --sweep --run <id>`, with an `actions: write`
token. Its re-runs are the same program's; what differs is only WHEN a sweep starts:
gate_sim.py's SWEEP (20 s from a green gate to its sweep) becomes the driver's poll
interval plus the runs listing's lag plus start-up. And the driver fires on every
attempt's completion (`--chain`) or only on a first attempt's (`--nochain`), so both
of gate_sim's chain arms are drivable.

This arm re-scores revision 3's rules (layout REV2) over gate_sim's 42 sequences with
SWEEP set to each driver latency, both chain arms, END-BAD and the attempt cap as
gate_sim scores them; the null control is the driver not running (the `sweep`
ablation), which must move under the every-suite reading. gate_sim.py itself is not
changed by this file.

  python3 -I measure/rev/driver_arm.py      exit 0 iff every latency row is END-BAD 0 and the null moves
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate_sim as S  # noqa: E402

DRIVER_POLL = 5
LATENCIES = (20, 35, 65, 125)   # gate_sim's own 20 s; poll 5 s + listing lag 30, 60, 120 s


def main() -> int:
    rc = 0
    scen = S.SCEN + S.crosshead() + S.STRESS
    unplanted = [x for x in scen if x[0].split()[0] not in S.MUST_FAIL | S.CAPPED]
    print(f"## R4-2: the sweep started by the probe driver, SWEEP = latency from a green gate to its sweep "
          f"(driver poll {DRIVER_POLL} s)")
    base = S.SWEEP
    for lat in LATENCIES:
        S.SWEEP = lat
        for chain in (True, False):
            rows = S.score("REV2", chain, scen)
            bad = S.end_bad(rows)
            att = max(r[4] for r in rows if r[1] not in S.CAPPED)
            nogood = [r[1] for r in rows if not r[3]]
            rc |= bool(bad)
            print(f"  driver latency {lat:3d} s {'--chain  ' if chain else '--nochain'} END-BAD {len(bad)}  "
                  f"most attempts {att:2d}  rows not ok (window, cap) {len(nogood)} {nogood}  {'; '.join(bad)[:160]}")
    S.SWEEP = base
    print("  null control: the driver not running (the `sweep` ablation), unplanted scenarios; every-suite must move")
    for chain in (True, False):
        rows = S.score("REV2", chain, unplanted, ablate=("sweep",))
        agree = [sum(r[2][j] == r[2][0] for r in rows) for j in (1, 2, 3)]
        rc |= agree[2] == len(rows)
        print(f"  no driver {'--chain  ' if chain else '--nochain'} agree newest-created {agree[0]}/{len(rows)}, "
              f"newest-completed {agree[1]}/{len(rows)}, every-suite {agree[2]}/{len(rows)}")
    print(f"\nDRIVER-ARM rc {rc}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
