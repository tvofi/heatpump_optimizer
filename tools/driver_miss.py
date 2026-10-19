#!/usr/bin/env python3
"""Round-5 seat: a status-diffing probe driver can miss a completion.

Revision 4's sweep_driver.py (DESIGN-P2.md section 10) lists the probe PR's runs every
5 s and starts a sweep "for each run attempt it sees newly completed". driver_arm.py
scores it as a constant start latency. A driver that diffs the runs listing only sees a
completion if the run is still completed at that attempt when it looks; if `refresh`
(or another sweep) re-runs the run's gate before then, the listing already shows the
next attempt in progress, and under --nochain that first-attempt completion is never
swept. The workflow cannot miss it: `workflow_run` delivers one event per completion.

Arm MISS: a sweep scheduled at a green completion fires only if, at its start time
(completion + latency), the run is still completed at the same attempt. Arm KEYED: the
driver reads every attempt (runs/<id>/attempts/<n>), so it never misses one; this is
driver_arm.py's model. Imports gate_sim.py unchanged.

  python3 -I tools/driver_miss.py <rev4>/measure/rev
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
import gate_sim as S  # noqa: E402

MISSED = []


class MissWorld(S.World):
    miss = False

    def finish_gate(self, r):
        n = len(self.todo)
        super().finish_gate(r)
        if self.miss:
            for i in range(n, len(self.todo)):
                it = self.todo[i]
                if it[1] == "sweep" and it[2] is r:
                    self.todo[i] = (it[0], "sweep", r, ("attempt", r["attempt"]))

    def hooks(self):
        if self.miss:
            for it in [x for x in self.todo if x[0] == self.t and x[1] == "sweep" and len(x) == 4]:
                r, (_, a) = it[2], it[3]
                if r["attempt"] != a or r["status"] != "completed":
                    self.todo.remove(it)
                    self.log.append((self.t, f"driver missed run {r['id']} attempt {a}"))
                    MISSED.append(r["id"])
        super().hooks()


def main():
    S.World = MissWorld
    scen = S.SCEN + S.crosshead() + S.STRESS
    rc = 0
    for lat in (20, 35, 65, 125):
        S.SWEEP = lat
        for miss in (False, True):
            MissWorld.miss = miss
            for chain in (True, False):
                MISSED.clear()
                rows = S.score("REV2", chain, scen)
                bad = S.end_bad(rows)
                fg = [r[1] for r in rows if r[2][4] > S.WINDOW_OK]
                print(f"latency {lat:3d} s {'MISS ' if miss else 'KEYED'} {'--chain  ' if chain else '--nochain'} "
                      f"END-BAD {len(bad)}  sweeps missed {len(MISSED)}  false-green rows {fg}  {'; '.join(bad)[:200]}")
                if not miss:
                    rc |= bool(bad)
    print(f"DRIVER-MISS done (rc reflects KEYED only) rc {rc}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
