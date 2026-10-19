"""Round-3 review seat: where revision 2's convergence depends on gate-attempt timing.

    python3 -I tools/rerun_tail.py <rev2>/measure/rev

gate_sim.py scores every gate attempt at one timing: listed at t0, reads the API at
t0+5, completes at t0+15; the sweep fires 20 s after a green gate and skips any run
that is not `completed` (a re-run request on a running run is refused by GitHub).
Here a hook's RE-RUN attempt keeps its read but its run is reported `completed` only
TAIL s later than gate_sim assumes (job teardown and run finalisation). Arm READ-LATE
moves the read to 2 s before completion instead, so only the read-to-completion gap
matters. Rows: REV2 under both chain arms over gate_sim's 41 scenarios; END-BAD =
final merge box differs from the oracle under some reading. For the first END-BAD
scenario the event log is printed."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
import gate_sim as GS  # noqa: E402


class Tail(GS.World):
    tail, read_late = 0, False

    def start_gate(self, r):
        super().start_gate(r)
        x = self.tail if r["attempt"] > 1 else 0
        r["gate_len"] = GS.GATE + x
        r["gate_rd"] = (GS.GATE - 2 + x) if self.read_late else GS.GATE_READ

    def gate_tick(self, r, phase):
        t0 = r.get("gate_t0")
        if t0 is None or r["status"] != "in_progress":
            return
        if phase == "read" and r["gate_read"] is None and self.t >= t0 + r["gate_rd"]:
            r["gate_read"] = self.eval_gate(r)
            self.log.append((self.t, f"run {r['id']} attempt {r['attempt']} reads: {'green' if r['gate_read'][0] else 'red'}"))
        if phase == "finish" and self.t >= t0 + r["gate_len"]:
            self.log.append((self.t, f"run {r['id']} attempt {r['attempt']} completes"))
            self.finish_gate(r)

    def hooks(self):
        for item in [x for x in self.todo if x[0] == self.t and x[1] in ("refresh", "sweep")]:
            busy = [o["id"] for o in self.runs if o["head"] == item[2]["head"] and o is not item[2]
                    and o["status"] == "in_progress" and o["attempt"] > 1]
            self.log.append((self.t, f"{item[1]} from run {item[2]['id']} (skips running re-run attempts {busy})"))
        super().hooks()


def score(tail, late, chain):
    bad, first = [], None
    for label, evs, truth, plant in GS.SCEN + GS.crosshead() + GS.STRESS:
        tag = label.split()[0]
        if tag in GS.CAPPED:
            continue
        w = Tail("REV2", truth, plant, chain=chain); w.tail, w.read_late = tail, late
        s = w.run(evs, until=12000)
        _, bc, bd, be, orc = s[-1]
        ok = (bc, bd, be) == (False, False, False) if tag in GS.MUST_FAIL else (bc == orc and bd == orc and be == orc)
        if not ok:
            bad.append(f"{tag}(oracle {GS.fmt(orc)}: created {GS.fmt(bc)} completed {GS.fmt(bd)} every {GS.fmt(be)})")
            if first is None:
                first = (label, [f"    t={t} {m}" for t, m in w.log if "reads" in m or "completes" in m or "from run" in m])
    return bad, first


shown = False
for late in (False, True):
    print(f"## arm {'READ-LATE (read 2 s before completion)' if late else 'TAIL (read at +5 s, completion +TAIL s later)'}")
    for tail in (0, 20, 30, 35, 40, 45, 50, 60, 120, 300):
        for chain in (True, False):
            bad, first = score(tail, late, chain)
            print(f"  tail {tail:3d} s {'chain  ' if chain else 'nochain'} END-BAD {len(bad)}  {'; '.join(bad)}")
            if first and not shown:
                shown = True
                print(f"  -- event log of {first[0]!r} at tail {tail} s, {'chain' if chain else 'nochain'} (after t=2500):")
                print("\n".join(l for l in first[1] if int(l.split('t=')[1].split()[0]) >= 2500))
