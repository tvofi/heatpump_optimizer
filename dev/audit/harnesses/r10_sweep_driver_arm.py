#!/usr/bin/env python3
"""R10-CI-LAYOUT-P2A-U0B: DESIGN-P2's `driver_arm.py`, re-scored with tools/ci/sweep.py's own decisions.

gate_sim.py (commit 1371a0a6, `measure/rev/gate_sim.py` and `gate_model.py`; read through
`git show`, never copied in) models the sweep with inline predicates. Here its World's `hooks`
is replaced so every sweep decision -- covers the newest event, re-run a completed red gate,
poll a not-completed one, never take a run to attempt 45 -- is `sweep.covers_newest`,
`sweep.must_rerun` and `sweep.pollable`. Arms: the driver latencies 20, 35, 65 and 125 s, both
chain arms, at the 5 s poll the oracle used (must reproduce driver_arm.txt row for row) and at
the 60 s floor the program polls at. Null: the driver not running (the `sweep` ablation), which
must move every-suite off 34/34.

    python3 -I dev/audit/harnesses/r10_sweep_driver_arm.py     exit 0 iff every row is END-BAD 0 and the null moves
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

PLAN_SHA = "1371a0a6"


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tools" / "ci"))
import sweep  # noqa: E402


def load_sim():
    tmp = Path(tempfile.mkdtemp(prefix="sweeparm-"))
    for f in ("gate_model.py", "gate_sim.py"):
        (tmp / f).write_text(subprocess.run(["git", "-C", str(ROOT), "show", f"{PLAN_SHA}:measure/rev/{f}"],
                                            check=True, capture_output=True, text=True).stdout)
    sys.path.insert(0, str(tmp))
    spec = importlib.util.spec_from_file_location("gate_sim", tmp / "gate_sim.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gate_sim"] = mod
    spec.loader.exec_module(mod)
    return mod


S = load_sim()


def gview(w, o):
    """sweep.py's view of run o's latest gate attempt."""
    g = w.latest_gate(o)
    if g is None:
        return None
    return {"status": "completed" if g["completed"] is not None else "in_progress",
            "conclusion": "success" if g["ok"] else "failure", "started_at": g["created"]}


def covers(w, src):
    return sweep.covers_newest(gview(w, src), [{"created_at": o["created"]} for o in w.runs if o["head"] == src["head"]])


class World(S.World):
    def hooks(self):
        for item in [x for x in self.todo if x[0] == self.t]:
            self.todo.remove(item)
            what, src = item[1], item[2]
            if what == "sweep-poll":
                o, deadline = item[3], item[4]
                if src["head"] != self.head:
                    continue
                if o["status"] != "completed":
                    if self.t + S.SWEEP_POLL <= deadline:
                        self.todo.append((self.t + S.SWEEP_POLL, "sweep-poll", src, o, deadline))
                    else:
                        self.log.append((self.t, f"sweep: run {o['id']} still running at the bound; left as is"))
                    continue
                if covers(self, src) and sweep.must_rerun(gview(self, o), o["attempt"]):
                    self.log.append((self.t, f"sweep: polled run {o['id']} completed red; re-run"))
                    self.rerun_gate(o)
                continue
            if what == "supersede":
                if src["status"] == "in_progress" and src["head"] == self.head:
                    for o in self.runs:
                        if (o["id"] < src["id"] and o["head"] != src["head"] and o["status"] in ("pending", "in_progress")
                                and o["event"] in ("pull_request", "workflow_dispatch") and o.get("cancel_at") is None):
                            o["cancel_at"] = self.t + S.CANCEL_LAG
                continue
            if src["head"] != self.head:
                continue
            if what == "sweep" and "poll" not in self.ablate and covers(self, src):
                for o in self.runs:
                    if o is not src and o["head"] == src["head"] and o["id"] < src["id"] and sweep.pollable(
                            {"status": "in_progress"} if o["status"] != "completed" and o.get("gate_t0") is not None else None):
                        self.todo.append((self.t + S.SWEEP_POLL, "sweep-poll", src, o, self.t + S.SWEEP_WAIT))
            for o in self.runs:
                if o is src or o["head"] != src["head"] or o["status"] != "completed":
                    continue
                g = gview(self, o)
                if g is None or g["status"] != "completed":
                    continue
                if what == "refresh" and g["conclusion"] == "success":
                    if o["attempt"] >= S.ATTEMPT_CAP:
                        self.log.append((self.t, f"refresh: run {o['id']} at attempt {o['attempt']} not re-run"))
                        continue
                    self.rerun_gate(o)
                elif what == "sweep" and o["id"] < src["id"] and sweep.must_rerun(g, o["attempt"]):
                    self.rerun_gate(o)


S.World = World   # S.score builds `World(...)`: the module-level name


def rows(poll, chain, scen, **kw):
    S.SWEEP_POLL = poll
    return S.score("REV2", chain, scen, **kw)


def main():
    rc = 0
    scen = S.SCEN + S.crosshead() + S.STRESS
    unplanted = [x for x in scen if x[0].split()[0] not in S.MUST_FAIL | S.CAPPED]
    base = S.SWEEP
    for poll in (5, sweep.POLL_FLOOR):
        print(f"## sweep.py's decisions, poll {poll} s{' (the oracle driver_arm.txt used 5 s)' if poll == 5 else ' (the floor)'}")
        for lat in (20, 35, 65, 125):
            S.SWEEP = lat
            for chain in (True, False):
                r = rows(poll, chain, scen)
                bad = S.end_bad(r)
                att = max(x[4] for x in r if x[1] not in S.CAPPED)
                nogood = [x[1] for x in r if not x[3]]
                rc |= bool(bad)
                print(f"  driver latency {lat:3d} s {'--chain  ' if chain else '--nochain'} END-BAD {len(bad)}  "
                      f"most attempts {att:2d}  rows not ok (window, cap) {len(nogood)} {nogood}  {'; '.join(bad)[:160]}")
    S.SWEEP = base
    print("  null control: the driver not running (the `sweep` ablation); every-suite must move")
    for chain in (True, False):
        r = rows(5, chain, unplanted, ablate=("sweep",))
        agree = [sum(x[2][j] == x[2][0] for x in r) for j in (1, 2, 3)]
        rc |= agree[2] == len(r)
        print(f"  no driver {'--chain  ' if chain else '--nochain'} agree newest-created {agree[0]}/{len(r)}, "
              f"newest-completed {agree[1]}/{len(r)}, every-suite {agree[2]}/{len(r)}")
    print(f"\nSWEEP-ARM rc {rc}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
