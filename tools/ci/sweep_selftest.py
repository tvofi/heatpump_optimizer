"""sweep.py's self-test: the decision program driven over a fake GitHub (no network)."""
from __future__ import annotations

import itertools
import re
import sys

import sweep
from sweep import POLL_FLOOR


class World:
    """Runs at one head; `script` maps a sleep count to a mutation applied after that sleep."""

    def __init__(self, runs, v_id, script=None, limit=None, post_limit=None):
        self.runs, self.v_id, self.script = {r["id"]: r for r in runs}, v_id, script or {}
        self.live_head, self.posts, self.listings, self.sleeps, self.t = "H", [], 0, [], 0
        self.limit, self.post_limit = limit, post_limit
        self.base_files, self.bodies, self.compares = [], [], 0     # the base's changes since the PR's pin

    def get(self, path, params=None):
        if self.limit:
            raise sweep.RateLimited(self.limit)
        if m := re.search(r"/actions/runs/(\d+)/jobs", path):
            r = self.runs[int(m[1])]
            return 200, {}, {"jobs": ([r["gate"]] if r.get("gate") else []) + r.get("units", [])}
        if m := re.search(r"/actions/runs/(\d+)$", path):
            r = self.runs[int(m[1])]
            return 200, {}, dict(r, head_sha="H", pull_requests=[{"number": 7}])
        if path.endswith("/actions/runs"):
            self.listings += 1
            return 200, {}, {"workflow_runs": [dict(r, path=sweep.CI_PATH) for r in self.runs.values()]}
        if re.search(r"/pulls/7$", path):
            return 200, {}, {"head": {"sha": self.live_head, "ref": "fix/b", "repo": {"full_name": "o/r"}},
                             "base": {"sha": "P0", "ref": "main"}}
        if path.endswith("/compare/P0...main"):
            self.compares += 1
            return 200, {}, {"files": [{"filename": f} for f in self.base_files]}
        return 404, {}, {}

    def post(self, path, body=None):
        if self.post_limit:
            raise sweep.RateLimited(self.post_limit)
        self.posts.append(path)
        self.bodies.append(body)
        return (204 if path.endswith("/dispatches") else 201), {}, {}

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s
        if fn := self.script.get(len(self.sleeps)):
            fn(self)

    def sweep(self):
        out = []
        rc = sweep.main(["--run", str(self.v_id), "--repo", "o/r"], self.get, self.post, out.append,
                        self.sleep, lambda: self.t)
        return rc, "\n".join(out)


def run(rid, created, status="completed", attempt=1, g="failure", gstatus="completed", started="2", units=None):
    """`units`: the run's other jobs' completion stamps (None: still running)."""
    gate = {"id": rid * 10, "name": "gate", "status": gstatus, "conclusion": g if gstatus == "completed" else None,
            "started_at": started, "completed_at": started if gstatus == "completed" else None}
    return {"id": rid, "created_at": created, "status": status, "run_attempt": attempt, "gate": gate,
            "units": [{"name": f"u{k}", "completed_at": c} for k, c in enumerate(units or ())]}


def v_run(rid=9, created="3"):
    return run(rid, created, g="success", started="4")


def finish(rid, g):
    def fn(w):
        r = w.runs[rid]
        r["status"] = "completed"
        r["gate"].update(status="completed", conclusion=g, completed_at=r["gate"]["started_at"])
    return fn


def run_checks():
    checks = []

    def ok(name, cond):
        checks.append((name, bool(cond)))

    w = World([run(1, "1"), run(2, "2", g="success"), v_run()], 9)
    rc, out = w.sweep()
    ok("a red older gate is re-run (the null for the plants below)", rc == 0 and w.posts == ["repos/o/r/actions/jobs/10/rerun"])
    ok("a green run and the triggering run are never re-run", all("/20/" not in p and "/90/" not in p for p in w.posts))
    w = World([v_run(rid=1, created="1"), run(2, "1")], 1)     # an edit run numbered below its code run
    rc, out = w.sweep()
    ok("a red gate on a HIGHER-id run is re-run (an id orders nothing)", rc == 0 and w.posts == ["repos/o/r/actions/jobs/20/rerun"])
    w = World([v_run(rid=1, created="1"), run(2, "1", status="in_progress", gstatus="in_progress")], 1,
              {2: finish(2, "failure")})
    w.sweep()
    ok("a HIGHER-id gate still waiting is polled, and re-run once it expires red", w.posts == ["repos/o/r/actions/jobs/20/rerun"])
    w = World([run(1, "1"), run(9, "3", g="failure", started="4")], 9)
    rc, out = w.sweep()
    ok("a triggering run whose gate is red re-runs nothing (no source finished after either gate started)",
       w.posts == [] and "reruns=0" in out)
    for att, want in ((43, 1), (44, 0), (46, 0)):
        w = World([run(1, "1", attempt=att), v_run()], 9)
        w.sweep()
        ok(f"attempt {att} {'is re-run' if want else 'is refused'} (cap 45)", len(w.posts) == want)
    w = World([run(1, "1"), v_run()], 9, limit=1234)
    rc, out = w.sweep()
    ok("a rate limit prints RATE-LIMITED, re-runs nothing and exits 1",
       rc == 1 and out.startswith("RATE-LIMITED") and "1234" in out and w.posts == [])
    w = World([run(1, "1"), run(2, "2"), v_run()], 9, post_limit=77)
    rc, out = w.sweep()
    ok("a rate limit on a re-run stops after it", rc == 1 and w.posts == [] and "RATE-LIMITED" in out)
    w = World([run(1, "5"), v_run(created="3")], 9)     # V's gate started at "4", before run 1 was created
    ok("a gate that does not cover the newest event sweeps nothing", "reruns=0" in w.sweep()[1] and w.posts == [])
    for st in ("queued", "waiting", "pending", "requested", "in_progress"):
        w = World([run(1, "1", status=st, gstatus=st), v_run()], 9, {2: finish(1, "failure")})
        w.runs[1]["status"] = "in_progress"
        w.script[2] = lambda w: (finish(1, "failure")(w))
        w.sweep()
        ok(f"a {st} gate is polled, and re-run once it completes red", w.posts == ["repos/o/r/actions/jobs/10/rerun"])
    w = World([run(1, "1", status="in_progress", gstatus="in_progress"), v_run()], 9, {3: finish(1, "failure")})
    rc, out = w.sweep()
    ok("polls are >= 60 s apart, one runs listing each", min(w.sleeps) >= 60 and w.listings == len(w.sleeps) + 1 == 4)
    ok("a polled run is re-run at most once", len(w.posts) == 1)
    w = World([run(1, "1", status="in_progress", gstatus="in_progress"), v_run()], 9)
    rc, out = w.sweep()
    ok("a run still going at the bound is left, red, after at most 600 s", w.posts == [] and w.t <= 600 and "still" in out)
    ok("the bound is reached by polling", len(w.sleeps) == 10)
    w = World([run(1, "1", status="in_progress", gstatus="in_progress"), v_run()], 9, {1: lambda w: (setattr(w, "live_head", "H2"), finish(1, "failure")(w))})
    rc, out = w.sweep()
    ok("a push that moved the head stops the poll without a re-run", w.posts == [] and "SWEEP stop" in out)
    w = World([run(1, "1", status="in_progress", gstatus="in_progress"), v_run()], 9, {1: finish(1, "success")})
    w.sweep()
    ok("a polled run that completes green is not re-run", w.posts == [])
    w = World([run(1, "1", status="in_progress", g="failure"), v_run()], 9)
    w.runs[1]["gate"]["status"] = "completed"
    out = w.sweep()[1]
    ok("a red gate in a still-running run is left, not re-run (GitHub refuses it)", w.posts == [] and "left run 1" in out)
    # r10-gate-busy-defer-3: settle, where no green gate covers the newest event. Stamps compare as
    # strings, as GitHub's ISO times do; a unit stamp after a gate's start is a source it could not read.
    w = World([run(1, "1", started="5", units=["6"]), run(2, "1", started="5", units=["6"])], 2)
    rc, out = w.sweep()
    ok("settle: two gates that deferred to each other (each started before the other's units finished) are "
       "both re-run, the triggering run's included", sorted(w.posts) == ["repos/o/r/actions/jobs/10/rerun",
                                                                         "repos/o/r/actions/jobs/20/rerun"])
    for v in (1, 2):
        w = World([run(1, "1", started="5", units=["4"]), run(2, "1", started="5", units=["4"])], v)
        for r in w.runs.values():
            r["gate"]["completed_at"] = "6"
        w.sweep()
        ok(f"settle: a lagging-listing pair (sources done, gates overlapping) re-runs the lower id only, "
           f"swept from run {v}", w.posts == ["repos/o/r/actions/jobs/10/rerun"])
    w = World([run(1, "1", started="9", units=["4"]), run(2, "1", started="5", units=["4"])], 1)
    w.runs[1]["gate"]["completed_at"], w.runs[2]["gate"]["completed_at"] = "9", "6"
    rc, out = w.sweep()
    ok("settle null: that lower gate re-judged red after the pair is final, and the higher is not re-run (no loop)",
       w.posts == [] and "reruns=0" in out)
    for v in (1, 2):    # verdict/3287: the higher deferred to a lagging lower that ended green, created after its start
        w = World([run(1, "10", g="success", started="50", units=["40"]), run(2, "52", started="55", units=["53"])], v)
        w.runs[1]["gate"]["completed_at"], w.runs[2]["gate"]["completed_at"] = "60", "56"
        rc, out = w.sweep()
        ok(f"settle: the higher of a lagging pair, deferred to a lower gate that ended green but does not cover "
           f"the newest event, is re-run, swept from run {v}", w.posts == ["repos/o/r/actions/jobs/20/rerun"])
        w.runs[2]["run_attempt"], w.posts = 2, []
        w.runs[2]["gate"].update(started_at="70", completed_at="71")    # its re-run, red on its own sources
        rc, out = w.sweep()
        ok(f"settle null: that higher re-judged red after the lower's gate concluded is final, swept again from "
           f"run {v} (no loop)", w.posts == [] and "reruns=0" in out)
    w = World([run(1, "10", g="success", started="50", units=["40"]), run(2, "61", started="65", units=["63"])], 2)
    w.runs[1]["gate"]["completed_at"], w.runs[2]["gate"]["completed_at"] = "60", "66"
    rc, out = w.sweep()
    ok("settle null: a higher red gate that started after the lower's green gate concluded is final, never re-run",
       w.posts == [] and "reruns=0" in out)
    for v, want in ((2, []), (1, ["repos/o/r/actions/jobs/20/rerun"])):
        w = World([run(1, "10", g="success", started="70", units=["40"]), run(2, "52", started="55", units=["53"])], v)
        w.runs[1]["gate"]["completed_at"], w.runs[2]["gate"]["completed_at"] = "80", "56"
        w.sweep()
        ok(f"a lower green gate that started after the higher red concluded: settle from run 2 re-runs nothing, "
           f"the lower's own newest-covering sweep re-runs it (swept from run {v})", w.posts == want)
    # The census of a lagging pair's orderings (verdict/3287): the lower's conclusion, the higher created
    # before or after the lower gate started, the higher gate inside or after it. Every overlapping red
    # deferral is re-run by some sweep, the lower where it is red, else the higher; once each re-run
    # judges after both gates concluded (kept red, the worst case), the sweeps its completions fire
    # (a sweep runs per CI completion, so only a re-run run sweeps again) post nothing.
    for lo_g, hi_created, hi_gate in itertools.product(("success", "failure"), ("45", "52"), (("55", "56"), ("65", "66"))):
        def pair():
            w = World([run(1, "10", g=lo_g, started="50", units=["40"]),
                       run(2, hi_created, started=hi_gate[0], units=["44"])], 1)
            w.runs[1]["gate"]["completed_at"], w.runs[2]["gate"]["completed_at"] = "60", hi_gate[1]
            return w
        posts = set()
        for v in (1, 2):
            w = pair()
            w.v_id = v
            w.sweep()
            posts |= set(w.posts)
        overlap = hi_gate[0] <= "60"
        want = "repos/o/r/actions/jobs/10/rerun" if lo_g == "failure" else "repos/o/r/actions/jobs/20/rerun"
        tag = f"lower {lo_g}, higher created {hi_created}, its gate {'-'.join(hi_gate)}"
        if overlap:
            ok(f"census: an overlapping deferral is re-run ({tag})", want in posts)
        again = set()
        for v in sorted({int(re.search(r"/jobs/(\d+)/", p)[1]) // 10 for p in posts}):
            w = pair()
            for t, path in enumerate(sorted(posts)):
                r = w.runs[int(re.search(r"/jobs/(\d+)/", path)[1]) // 10]
                r["run_attempt"] = 2
                r["gate"].update(started_at=f"{7 + t}0", completed_at=f"{7 + t}1")
            w.v_id = v
            w.sweep()
            again |= set(w.posts)
        ok(f"census: the second round posts nothing ({tag}; first {sorted(posts)})", not again)
    w = World([run(1, "1", started="7", units=["6"]), run(2, "1", started="8", units=["6"])], 2)
    rc, out = w.sweep()
    ok("settle null: the same reds judged after every source finished, apart, are final, never re-run (no loop)",
       w.posts == [] and "reruns=0" in out)
    w = World([run(1, "1", started="2", units=["1"]), run(9, "1", started="8", units=["7"])], 9)
    w.sweep()
    ok("settle: a decider that ended red re-runs the gate that deferred to it, not itself",
       w.posts == ["repos/o/r/actions/jobs/10/rerun"])
    for st in ("queued", "waiting"):
        w = World([run(1, "1", started="2", units=["1"]), run(9, "1", status="in_progress", gstatus=st, units=[None])],
                  1)
        rc, out = w.sweep()
        ok(f"settle: a run whose gate is still {st} owns convergence (SKIP, nothing re-run)",
           w.posts == [] and out.startswith("SKIP") and w.sleeps == [])
    w = World([run(1, "1", started="2", units=["1"]),
               run(9, "1", status="in_progress", gstatus="in_progress", started="8", units=["7"])], 1,
              {1: finish(9, "failure")})
    w.sweep()
    ok("settle: a gate still running is polled, then the deferral it leaves red is re-judged",
       w.posts == ["repos/o/r/actions/jobs/10/rerun"] and w.sleeps == [POLL_FLOOR])
    w = World([run(1, "1", started="2", units=["1"])], 1)
    rc, out = w.sweep()
    ok("settle null: a lone red gate at its head is never re-run", w.posts == [] and "reruns=0" in out)
    # Stale pin (RCA r10-gate-busy-defer-2 5.2; carries 3 and 5): a pull_request run's gate restores
    # tools/ci/*.py from the event's base.sha, and a re-run replays that event, so it runs the programs
    # of that pin however far the base has moved. Where the base changed tools/ci since, a fresh run.
    dispatch = "repos/o/r/actions/workflows/ci.yml/dispatches"

    def pinned(*rs, v=9, files=("tools/ci/gate.py",)):
        for r in rs:
            r.setdefault("event", "pull_request")
        w = World(list(rs), v)
        w.base_files = list(files)
        return w
    w = pinned(run(1, "1"), v_run())
    rc, out = w.sweep()
    ok("stale pin: a red gate pinned before a tools/ci change on its base is re-judged by ONE dispatched run "
       "(pr, base), never re-run", w.posts == [dispatch] and w.bodies == [{"ref": "fix/b",
       "inputs": {"pr": "7", "base": "main"}}] and "STALE-PIN P0" in out and "dispatches=1" in out)
    w = pinned(run(1, "1"), v_run(), files=("custom_components/heatpump_optimizer/x.py", "tools/ci/fixtures/f.json",
                                            "tools/pr/prepr.sh"))
    w.sweep()
    ok("stale pin null: a base that moved without touching tools/ci/*.py re-runs the gate as before",
       w.posts == ["repos/o/r/actions/jobs/10/rerun"])
    w = pinned(run(1, "1"), v_run())
    w.runs[1]["event"] = "workflow_dispatch"
    w.sweep()
    ok("stale pin null: a dispatched run's gate (it rev-parses origin/<base> at its re-run) is re-run, the "
       "base never compared", w.posts == ["repos/o/r/actions/jobs/10/rerun"] and w.compares == 0)
    w = pinned(run(1, "1"), run(2, "2"), v_run())
    w.sweep()
    ok("stale pin: two stale reds at one head take one dispatch, one compare", w.posts == [dispatch] and w.compares == 1)
    w = pinned(run(1, "1", started="5", units=["6"]), run(2, "1", started="5", units=["6"]), v=2)
    w.sweep()
    ok("stale pin, settle: the #3261 pair (two deferrals under a pre-fix program) takes one dispatch, no re-run",
       w.posts == [dispatch])
    w = pinned(run(1, "1"), run(5, "3", g="success"), v_run(created="2"))
    w.runs[5]["event"] = "workflow_dispatch"
    rc, out = w.sweep()
    ok("stale pin, no loop: a dispatched run created after the stale gate concluded re-judges the head; "
       "nothing posted", w.posts == [] and "run 5 re-judges" in out)
    w = pinned(run(1, "1"), run(5, "1"), v_run())
    w.runs[5]["event"] = "workflow_dispatch"
    w.runs[1]["gate"]["completed_at"] = "2"
    w.sweep()
    ok("stale pin null: a dispatched run created before the stale gate concluded is no fresh judge: dispatch",
       dispatch in w.posts)
    return checks


def run_self():
    checks = run_checks()
    for name, good in checks:
        if not good:
            print(f"FAIL {name}")
    bad = sum(1 for _, g in checks if not g)
    print(f"sweep self-test: {len(checks)} checks, {bad} failed")
    return 1 if bad else 0
