"""sweep.py's self-test: the decision program driven over a fake GitHub (no network)."""
from __future__ import annotations

import re
import sys

import sweep


class World:
    """Runs at one head; `script` maps a sleep count to a mutation applied after that sleep."""

    def __init__(self, runs, v_id, script=None, limit=None, post_limit=None):
        self.runs, self.v_id, self.script = {r["id"]: r for r in runs}, v_id, script or {}
        self.live_head, self.posts, self.listings, self.sleeps, self.t = "H", [], 0, [], 0
        self.limit, self.post_limit = limit, post_limit

    def get(self, path, params=None):
        if self.limit:
            raise sweep.RateLimited(self.limit)
        if m := re.search(r"/actions/runs/(\d+)/jobs", path):
            r = self.runs[int(m[1])]
            return 200, {}, {"jobs": [r["gate"]] if r.get("gate") else []}
        if m := re.search(r"/actions/runs/(\d+)$", path):
            r = self.runs[int(m[1])]
            return 200, {}, dict(r, head_sha="H", pull_requests=[{"number": 7}])
        if path.endswith("/actions/runs"):
            self.listings += 1
            return 200, {}, {"workflow_runs": [dict(r, path=sweep.CI_PATH) for r in self.runs.values()]}
        if re.search(r"/pulls/7$", path):
            return 200, {}, {"head": {"sha": self.live_head}}
        return 404, {}, {}

    def post(self, path, body=None):
        if self.post_limit:
            raise sweep.RateLimited(self.post_limit)
        self.posts.append(path)
        return 201, {}, {}

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


def run(rid, created, status="completed", attempt=1, g="failure", gstatus="completed", started="2"):
    gate = {"id": rid * 10, "name": "gate", "status": gstatus, "conclusion": g if gstatus == "completed" else None,
            "started_at": started}
    return {"id": rid, "created_at": created, "status": status, "run_attempt": attempt, "gate": gate}


def v_run(rid=9, created="3"):
    return run(rid, created, g="success", started="4")


def finish(rid, g):
    def fn(w):
        r = w.runs[rid]
        r["status"] = "completed"
        r["gate"].update(status="completed", conclusion=g)
    return fn


def run_checks():
    checks = []

    def ok(name, cond):
        checks.append((name, bool(cond)))

    w = World([run(1, "1"), run(2, "2", g="success"), v_run()], 9)
    rc, out = w.sweep()
    ok("a red older gate is re-run (the null for the plants below)", rc == 0 and w.posts == ["repos/o/r/actions/jobs/10/rerun"])
    ok("a green run and the triggering run are never re-run", all("/20/" not in p and "/90/" not in p for p in w.posts))
    w = World([run(1, "1"), run(9, "3", g="failure", started="4")], 9)
    rc, out = w.sweep()
    ok("a triggering run whose gate is red re-runs nothing", w.posts == [] and out.startswith("SKIP"))
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
    ok("a gate that does not cover the newest event sweeps nothing", w.sweep()[1].startswith("SKIP") and w.posts == [])
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
    return checks


def run_self():
    checks = run_checks()
    for name, good in checks:
        if not good:
            print(f"FAIL {name}")
    bad = sum(1 for _, g in checks if not g)
    print(f"sweep self-test: {len(checks)} checks, {bad} failed")
    return 1 if bad else 0
