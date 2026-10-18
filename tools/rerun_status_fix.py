"""Review-2 seat: gate_sim.py finishes a hook re-run TWICE.
    python3 -I tools/rerun_status_fix.py <rev1>/measure/rev
hooks() flips an old run to in_progress and schedules its gate GATE s later; but
step_run() also sees that run in_progress with its OLD gate_at, and calls
finish_gate() on the very next tick, marking the run completed 1 s after the re-run
instead of GATE (15) s. Two gates re-run together therefore never see each other as
`in_progress` for more than one tick, and the second-evaluated one reads the first as
completed. Arm FIXED: step_run() skips a run whose gate attempt is a hook re-run, so
the attempt is in_progress for GATE s, as a real re-run of the `gate` job is.
Also crossed with: a hook-requested attempt's completion fires the sweep (CHAIN) or not."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
import gate_sim as S


def make(fixed, chain):
    class W(S.World):
        def step_run(self, r):
            if fixed and r.get("rerun_at") is not None:
                return
            return S.World.step_run(self, r)

        def hooks(self):
            before = {id(o): o.get("rerun_at") for o in self.runs}
            S.World.hooks(self)
            for o in self.runs:
                if o.get("rerun_at") is not None and before.get(id(o)) is None:
                    o["hook_attempt"] = True

        def finish_gate(self, r):
            self.finishes = getattr(self, "finishes", 0) + 1
            n = len(self.todo)
            S.World.finish_gate(self, r)
            if r.pop("hook_attempt", False) and not chain:
                del self.todo[n:]
    return W


SC = [("X1 edit and review both land while the code run is in flight",
       [(0, "open"), (300, "edit", {"body": "b2"}), (301, "review", {"state": "approved"})],
       S.T(brg=lambda rv: rv == "approved")),
      ("X3 edit, then review 600 s later, both during the code run",
       [(0, "open"), (300, "edit", {"body": "b2"}), (900, "review", {"state": "approved"})],
       S.T(brg=lambda rv: rv == "approved")),
      ("X4 two reviews 600 s apart during the code run (approve, approve)",
       [(0, "open"), (300, "review", {"state": "approved"}), (900, "review", {"state": "approved"})],
       S.T(brg=lambda rv: rv == "approved"))]
base = [(l, e, t) for (l, e, t, p) in S.SCEN if l.split()[0] not in S.MUST_FAIL]
for fixed in (False, True):
    for chain in (True, False):
        W = make(fixed, chain); bad = 0
        print(f"## {'FIXED' if fixed else 'AS-IS'} {'CHAIN' if chain else 'NOCHAIN'}")
        for label, evs, truth in base + SC:
            w = W("REV1", truth, {}); s = w.run(evs); _, bc, bd, be, orc = s[-1]
            ok = bc == orc and bd == orc and be == orc; bad += not ok
            if not ok or label.startswith("X"):
                gs = ", ".join(f"{g['run']}@{g['created']}:{S.fmt(g['ok'])}" for g in w.gates)
                print(f"  {label[:62]:62s} oracle {S.fmt(orc)} created {S.fmt(bc)} completed {S.fmt(bd)} every {S.fmt(be)}  {'ok' if ok else 'BAD'}  gates[{gs}]")
        print(f"  BAD rows: {bad} of {len(base) + len(SC)}")


# Arm FIXED+SNAP: as FIXED, and every gate due in one tick reads the SAME state (on
# GitHub two gate jobs re-run together both query the API while the other is running).
def make_snap(chain):
    Base = make(True, chain)

    class W(Base):
        def hooks(self):
            due = [o for o in self.runs if o.get("rerun_at") is not None and self.t >= o["rerun_at"] + S.GATE]
            pre = {id(o): S.World.eval_gate(self, o) for o in due}
            for o in due:
                o["_pre"] = pre[id(o)]
            Base.hooks(self)

        def eval_gate(self, r):
            return r.pop("_pre") if "_pre" in r else S.World.eval_gate(self, r)
    return W


for chain in (True, False):
    W = make_snap(chain); bad = 0
    print(f"## FIXED+SNAP {'CHAIN' if chain else 'NOCHAIN'}")
    for label, evs, truth in base + SC:
        w = W("REV1", truth, {}); s = w.run(evs); _, bc, bd, be, orc = s[-1]
        ok = bc == orc and bd == orc and be == orc; bad += not ok
        if not ok or label.startswith("X"):
            gs = ", ".join(f"{g['run']}@{g['created']}:{S.fmt(g['ok'])}" for g in w.gates)
            print(f"  {label[:62]:62s} oracle {S.fmt(orc)} created {S.fmt(bc)} completed {S.fmt(bd)} every {S.fmt(be)}  {'ok' if ok else 'BAD'}  gates[{gs}]")
    print(f"  BAD rows: {bad} of {len(base) + len(SC)}")
