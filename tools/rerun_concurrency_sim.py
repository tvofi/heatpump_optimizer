"""Review-2 seat's instrument: revision 1's gate_sim with ONE semantic added.

    python3 -I tools/rerun_concurrency_sim.py <rev1 checkout>/measure/rev

gate_sim.py re-runs a `gate` job (refresh, sweep) by flipping the old run to
in_progress OUTSIDE any concurrency group. GitHub re-runs a run as a new ATTEMPT of
the same run, which re-enters the run's concurrency group with the run's ORIGINAL
group key and cancel-in-progress. The tree measured this: PR contract run
37315758446 attempt 4 (a manual re-run, started 14:24:27Z) cancelled the NEWER run
37324419853 of the same group at 14:24:37Z (dev/audit/rca/R9-RC-PRCONTRACT.md:85,
:188, :227 "a rerunner inherits the group"; both runs read back via the API, ev/).

Arm SIM  = gate_sim.World unchanged (the revision's model).
Arm GH   = the same, except a re-run attempt applies the documented group rule:
           it cancels the group's pending run and, when its own cancel-in-progress
           is true, the group's in-progress run (after CANCEL_LAG).
Scenarios: the revision's 16 unplanted ones, plus this seat's.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
import gate_sim as S  # noqa: E402


class GH(S.World):
    def hooks(self):
        due = [x for x in self.todo if x[0] == self.t]
        before = {id(o): o.get("rerun_at") for o in self.runs}
        super().hooks()
        for o in self.runs:
            if o.get("rerun_at") == self.t and before.get(id(o)) != self.t and due:
                g = o.get("group")
                for p in self.runs:
                    if p is o or p.get("group") != g:
                        continue
                    if p["status"] == "pending":
                        p["status"], p["conclusion"], p["end"] = "completed", "cancelled", self.t
                    elif p["status"] == "in_progress" and self.cancels_running(o) and p.get("cancel_at") is None:
                        p["cancel_at"] = self.t + S.CANCEL_LAG
                        self.log.append((self.t, f"re-run of {o['id']} cancels {p['id']}"))


T = S.T
MINE = [
    ("R1 retarget after the code run is green (refresh re-runs C's gate)",
     [(0, "open"), (2100, "retarget", {"base": "release"})], T()),
    ("R2 body edit after an earlier edit's gate is green, new body breaks the contract",
     [(0, "open"), (2100, "edit", {"body": "b2"}), (2400, "edit", {"body": "bad"})],
     T(body=lambda b: b != "bad")),
    ("R3 approval, then dismissal 300 s later (scenario G, spaced)",
     [(0, "open"), (2600, "review", {"state": "approved"}), (2900, "review", {"state": "dismissed"})],
     T(brg=lambda rv: rv == "approved")),
    ("R4 edit and review both land while the code run is in flight",
     [(0, "open"), (300, "edit", {"body": "b2"}), (301, "review", {"state": "approved"})],
     T(brg=lambda rv: rv == "approved")),
    ("R5 a body that breaks the contract, then an edit 300 s later that fixes it",
     [(0, "open"), (2100, "edit", {"body": "bad"}), (2400, "edit", {"body": "b3"})],
     T(body=lambda b: b != "bad")),
    ("R6 changes requested on a raise, then the owner approves 300 s later",
     [(0, "open"), (2600, "review", {"state": "changes"}), (2900, "review", {"state": "approved"})],
     T(brg=lambda rv: rv == "approved")),
    ("R7 an approval, then a plain comment review 300 s later",
     [(0, "open"), (2600, "review", {"state": "approved"}), (2900, "review", {"state": "approved"})],
     T(brg=lambda rv: rv == "approved")),
]


def row(label, w, s):
    _, bc, bd, be, orc = s[-1]
    fg = S.max_win(s)
    ok = bc == orc and bd == orc and be == orc and fg <= S.WINDOW_OK
    canc = [m for _, m in w.log]
    return (f"{label[:74]:74s} oracle {S.fmt(orc):4s} created {S.fmt(bc):4s} completed {S.fmt(bd):4s} "
            f"every {S.fmt(be):4s} fg {fg:5d}  {'ok' if ok else 'BAD'}" + (f"  [{'; '.join(canc)}]" if canc else "")), ok


def main():
    base = [(l, e, t) for (l, e, t, p) in S.SCEN if l.split()[0] not in S.MUST_FAIL]
    bad = {"SIM": 0, "GH": 0}
    for arm, cls in (("SIM", S.World), ("GH", GH)):
        print(f"## arm {arm}")
        for label, evs, truth in base + MINE:
            w = cls("REV1", truth, {})
            line, ok = row(label, w, w.run(evs))
            bad[arm] += not ok
            print("  " + line)
        print()
    print(f"RERUN-CONCURRENCY-SIM: BAD rows, revision's model {bad['SIM']}, with re-runs in their group {bad['GH']}")


main()
