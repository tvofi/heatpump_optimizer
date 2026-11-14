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
        self.head_repo = "o/r"
        self.attempt_reads = 0
        self.caller = None      # GITHUB_RUN_ID of the job calling the sweep: V's own id is ci.yml's sweep-self

    def get(self, path, params=None):
        if self.limit:
            raise sweep.RateLimited(self.limit)
        if m := re.search(r"/actions/runs/(\d+)/attempts/(\d+)/jobs", path):     # a past attempt's gate, or 404
            self.attempt_reads += 1
            g = self.runs[int(m[1])].get("attempts", {}).get(int(m[2]))
            jobs = [{"name": f"u{k}"} for k in range(40)] + [g]       # #3544's 41 jobs, the gate past a default page
            return (200, {}, {"jobs": jobs[:min((params or {}).get("per_page", 30), 100)]}) if g else (404, {}, {})
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
            return 200, {}, {"head": {"sha": self.live_head, "ref": "fix/b", "repo": {"full_name": self.head_repo}},
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
                        self.sleep, lambda: self.t, env={"GITHUB_RUN_ID": str(self.caller or 0)})
        return rc, "\n".join(out)


def run(rid, created, status="completed", attempt=1, g="failure", gstatus="completed", started="2", units=None):
    """`units`: the run's other jobs' completion stamps (None: still running)."""
    gate = {"id": rid * 10, "name": "gate", "status": gstatus, "conclusion": g if gstatus == "completed" else None,
            "started_at": started, "completed_at": started if gstatus == "completed" else None}
    return {"id": rid, "created_at": created, "status": status, "run_attempt": attempt, "gate": gate,
            "conclusion": g if status == "completed" and gstatus == "completed" else None,
            "units": [{"name": f"u{k}", "completed_at": c} for k, c in enumerate(units or ())]}


def v_run(rid=9, created="3"):
    return run(rid, created, g="success", started="4")


def finish(rid, g):
    def fn(w):
        r = w.runs[rid]
        r.update(status="completed", conclusion=g)
        r["gate"].update(status="completed", conclusion=g, completed_at=r["gate"]["started_at"])
    return fn


BOT = "github-actions[bot]"     # the login of gate-sweep.yml's github.token, the recorded runs' triggering_actor

# #3308 at head 6016f9dd, recorded 2026-11-08 from `gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>/attempts/<n>/jobs`
# (the state the sweep for run 42471173865's attempt 24 read at 11:48:1x, after which runs 42470642055 and
# 42470643072 were re-run at 11:48:33). Trimmed: run 42470642055's 41 jobs to its gate, its skipped jobs, and
# five sources; the edit runs whole. Rows: (job id, name, conclusion, started, completed), times on 2026-11-08 UTC.
# A skipped job's stamps are GitHub's re-stamp at its run's last gate re-run, not a source finishing.
REC3308 = {
    42470642055: ("10:15:21", 38, [
        (128721141457, "kernel-points", "skipped", "11:46:40", "11:46:40"),
        (128721141679, "cancel-superseded", "success", "10:15:24", "10:15:36"),
        (128721142283, "governance / delivery-status-publish", "skipped", "11:46:41", "10:15:55"),
        (128721142833, "tests / mutation-pins", "skipped", "11:46:41", "10:45:32"),
        (128721143058, "tests / mutation-autofix", "skipped", "11:46:41", "10:45:32"),
        (128721143069, "gate", "failure", "11:46:44", "11:47:23"),
        (128721143188, "tests / claims-autofix", "skipped", "11:46:41", "10:40:04"),
        (128721143295, "tests / ci-ratchet", "skipped", "11:46:41", "10:55:41"),
        (128721143592, "tests / closures-autofix", "skipped", "11:46:41", "10:55:41"),
        (128721164571, "prelude", "success", "10:15:24", "10:15:55"),
        (128721166777, "codeql / Analyze (python)", "success", "10:15:58", "10:46:54"),
        (128721168852, "governance / record", "skipped", "11:46:48", "10:15:55"),
        (128721175140, "codeql / Analyze (actions)", "failure", "10:15:58", "10:17:21"),
        (128721177543, "refresh", "success", "10:15:24", "10:15:51"),
    ]),
    42470643072: ("10:15:22", 24, [
        (128721143207, "cancel-superseded", "success", "10:15:25", "10:15:36"),
        (128721143539, "gate", "failure", "11:46:43", "11:47:13"),
        (128721143587, "refresh", "success", "10:15:25", "10:16:00"),
        (128721143691, "hassfest", "skipped", "11:46:41", "11:46:41"),
        (128721143984, "arch-score / arch-score", "success", "10:15:54", "10:17:08"),
        (128721144134, "codeql", "skipped", "11:46:41", "11:46:41"),
        (128721144270, "governance", "skipped", "11:46:41", "11:46:41"),
        (128721144288, "kernel-points", "skipped", "11:46:41", "11:46:41"),
        (128721144361, "budget-raise-gate / budget-raise-gate", "success", "10:15:55", "10:16:20"),
        (128721144413, "tests", "skipped", "11:46:41", "11:46:41"),
        (128721144462, "pr-contract", "skipped", "11:46:41", "11:46:41"),
        (128721164089, "prelude", "success", "10:15:25", "10:15:52"),
        (128721177333, "validate", "skipped", "11:46:50", "11:46:41"),
    ]),
    42471173865: ("10:22:40", 24, [
        (128721349953, "hassfest", "skipped", "11:47:37", "11:47:37"),
        (128721349979, "gate", "failure", "11:47:39", "11:48:10"),
        (128721350133, "prelude", "success", "10:22:43", "10:23:06"),
        (128721350617, "tests", "skipped", "11:47:37", "11:47:37"),
        (128721350659, "arch-score / arch-score", "success", "10:23:09", "10:24:24"),
        (128721370684, "kernel-points", "skipped", "11:47:43", "11:47:37"),
        (128721376633, "codeql", "skipped", "11:47:44", "11:47:37"),
        (128721378973, "budget-raise-gate / budget-raise-gate", "success", "10:23:09", "10:23:41"),
        (128721379915, "refresh", "success", "10:22:44", "10:23:21"),
        (128721380679, "governance", "skipped", "11:47:46", "11:47:37"),
        (128721382358, "validate", "skipped", "11:47:46", "11:47:37"),
        (128721384599, "pr-contract", "skipped", "11:47:47", "11:47:37"),
        (128721384912, "cancel-superseded", "success", "10:22:43", "10:22:52"),
    ]),
}


def world3308(v_id=42471173865, edit=None):
    """The #3308 recording as a World; `edit(runs)` perturbs it first. Every attempt past the first was the bot's."""
    stamp = lambda t: f"2026-11-08T{t}Z"
    runs = []
    for rid, (created, attempt, jobs) in REC3308.items():
        js = [{"id": i, "name": n, "status": "completed", "conclusion": c, "started_at": stamp(s), "completed_at": stamp(e)}
              for i, n, c, s, e in jobs]
        runs.append({"id": rid, "created_at": stamp(created), "status": "completed", "run_attempt": attempt,
                     "triggering_actor": {"login": BOT},
                     "gate": next(j for j in js if j["name"] == "gate"), "units": [j for j in js if j["name"] != "gate"]})
    if edit:
        edit({r["id"]: r for r in runs})
    return World(runs, v_id)


# #3544 at a60a65d8, recorded 2026-11-14 (`gh api .../actions/runs/<id>/attempts/<n>/jobs`): the dispatched run D's
# first gate was green; review runs R1 and R2 came; R1's refresh re-ran D's green gate, which deferred to them (attempt 2);
# R1's gate deferred to R2, whose gate went green. R2's sweep re-ran D in place and, R1 being stale-pinned and no green
# dispatch listed, dispatched run 43574296856: a full code run whose gate held the PR BLOCKED. Trimmed to the gates and
# the sources that bound them. Rows: (name, conclusion, started, completed), times on 2026-11-14 UTC.
D3544, R1_3544, R2_3544 = 43531915583, 43572050013, 43572059623
REC3544 = {     # the three bot-attempt pull_request runs: refresh re-ran their green gates, which deferred to R1 and R2
    43512354900: ("pull_request", "2026-11-13T21:37:33", 5, BOT, [("gate", "failure", "07:50:57", "07:51:55")]),
    43512355939: ("pull_request", "2026-11-13T21:37:34", 4, BOT, [("gate", "failure", "07:50:18", "07:51:01")]),
    43531447639: ("pull_request", "00:02:37", 2, BOT, [("gate", "failure", "07:48:16", "07:48:59")]),
    D3544: ("workflow_dispatch", "00:06:36", 2, BOT, [
        ("gate", "failure", "07:41:32", "07:42:13"), ("tests / closures", "success", "00:08:46", "00:21:25"),
        ("pr-contract / pr-contract", "success", "01:10:24", "01:11:34")]),
    R1_3544: ("pull_request_review", "07:38:36", 1, "tvofi", [
        ("gate", "failure", "07:54:14", "07:55:15"), ("refresh", "success", "07:40:21", "07:41:29"),
        ("prelude", "success", "07:41:55", "07:42:56"), ("budget-raise-gate / budget-raise-gate", "success", "07:44:20", "07:45:06")]),
    R2_3544: ("pull_request_review", "07:38:43", 1, "tvofi", [
        ("gate", "success", "08:00:44", "08:01:40"), ("refresh", "success", "07:45:41", "07:46:32"),
        ("prelude", "success", "07:46:48", "07:47:44"), ("budget-raise-gate / budget-raise-gate", "success", "07:57:19", "07:57:52")]),
}
D3544_FIRST_GATE = ("gate", "success", "01:12:52", "01:13:48")


def world3544(v_id=R2_3544, edit=None, ids=tuple(REC3544)):
    """The #3544 recording as a World at a stale pin (main changed tools/ci/gate.py after the PR's base sha)."""
    stamp = lambda t: t + "Z" if "T" in t else f"2026-11-14T{t}Z"
    job = lambda k, n, c, s, e: {"id": k, "name": n, "status": "completed", "conclusion": c,
                                 "started_at": stamp(s), "completed_at": stamp(e)}
    runs = []
    for rid in ids:
        ev, created, attempt, actor, rows = REC3544[rid]
        js = [job(rid * 10 + k, *row) for k, row in enumerate(rows)]
        kind = "review" if ev == "pull_request_review" else "code"       # ci.yml's run-name (prelude.title)
        runs.append({"id": rid, "event": ev, "created_at": stamp(created), "status": "completed", "run_attempt": attempt,
                     "display_title": f"CI {kind} pr=7 base=main sha=H",
                     "conclusion": js[0]["conclusion"], "triggering_actor": {"login": actor}, "gate": js[0], "units": js[1:]})
    w = World(runs, v_id)
    if D3544 in w.runs:
        w.runs[D3544]["attempts"] = {1: job(D3544 * 10, *D3544_FIRST_GATE)}
    w.base_files = ["tools/ci/gate.py"]
    if edit:
        edit(w.runs)
    return w


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
    ok("a red gate in a still-running run is not re-run while it runs (GitHub refuses it): polled, left at the bound",
       w.posts == [] and "left run 1 still in_progress" in out and len(w.sleeps) == 10)
    w = World([run(1, "1", status="in_progress", g="failure"), v_run()], 9, {1: finish(1, "failure")})
    w.runs[1]["gate"]["status"] = "completed"
    w.sweep()
    ok("a red gate whose run was still running (its own sweep-self) is re-run once the run completes",
       w.posts == ["repos/o/r/actions/jobs/10/rerun"] and w.sleeps == [POLL_FLOOR])
    # R10-HOTFIX-SWEEP-TOKEN-ACTOR: ci.yml's sweep-self sweeps a run whose actor is the bot, from inside it
    # (gate-sweep.yml's workflow_run never fires for one). Its run is still in_progress, its sweep-self running.
    selfjob = {"name": sweep.SELF_JOB, "completed_at": None}
    def self_world(e_gate_started, caller=9):
        v = run(9, "1", status="in_progress", g="success", started="4", units=["3"])
        v["gate"]["completed_at"] = "7"
        v["units"].append(dict(selfjob))
        e = run(10, "5", started=e_gate_started)
        w = World([v, e], 9)
        w.caller = caller
        return w
    w = self_world("6")
    rc, out = w.sweep()
    ok("sweep-self: called from inside V (in_progress, gate green), it re-runs the edit gate that deferred to V, "
       "without polling", rc == 0 and w.posts == ["repos/o/r/actions/jobs/100/rerun"] and w.sleeps == [])
    w = self_world("8")
    rc, out = w.sweep()
    ok("sweep-self null: a red gate judged after V's gate concluded is final; V's running sweep-self is no source",
       w.posts == [] and w.sleeps == [] and "reruns=0" in out)
    w = self_world("6", caller=None)
    w.runs[9]["status"] = "completed"
    w.runs[9]["units"][-1].update(completed_at="9", conclusion="skipped")
    w.sweep()
    ok("sweep-self null: the workflow_run sweep of the same head (V completed, sweep-self skipped) re-runs alike",
       w.posts == ["repos/o/r/actions/jobs/100/rerun"] and w.sleeps == [])
    w = self_world("6")
    w.runs[11] = run(11, "5", status="in_progress", gstatus="in_progress", started="9")
    rc, out = w.sweep()
    ok("sweep-self: a gate still running elsewhere is not waited on from inside V (its completion sweeps)",
       w.posts == [] and w.sleeps == [] and out.startswith("SKIP"))
    w = self_world("6", caller=None)
    w.runs[9]["status"] = "completed"
    w.runs[9]["units"][-1].update(completed_at="9", conclusion="skipped")
    w.runs[11] = run(11, "5", status="in_progress", gstatus="in_progress", started="9")
    w.script[1] = finish(11, "success")
    w.sweep()
    ok("sweep-self null: the workflow_run sweep polls that gate as before", w.sleeps == [POLL_FLOOR])
    w = self_world("6")
    w.runs[10]["status"] = "in_progress"        # the edit run's own sweep-self still running
    w.script[1] = lambda w: w.runs[10].update(status="completed")
    w.sweep()
    ok("sweep-self: an edit run busy only past its gate is polled from inside V, then its deferral re-run",
       w.posts == ["repos/o/r/actions/jobs/100/rerun"] and w.sleeps == [POLL_FLOOR])
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
       "inputs": {"pr": "7", "base": "main"}}] and "STALE-PIN P0" in out and "(HTTP 204)" in out
       and "dispatches=1" in out)
    w = pinned(run(1, "1"), v_run(), files=("custom_components/heatpump_optimizer/x.py", "tools/ci/fixtures/f.json",
                                            "tools/pr/prepr.sh"))
    w.sweep()
    ok("stale pin null: a base that moved without touching tools/ci/*.py re-runs the gate as before",
       w.posts == ["repos/o/r/actions/jobs/10/rerun"])
    w = pinned(run(1, "1"), v_run(), files=[f"docs/f{k}.md" for k in range(300)])
    w.sweep()
    ok("stale pin: a compare listing at GitHub's 300-file cap may hide a tools/ci change: a fresh run",
       w.posts == [dispatch])
    w = pinned(run(1, "1"), v_run())
    w.head_repo = "fork/r"
    w.sweep()
    ok("stale pin null: a fork head (no branch here to dispatch on) is re-run as before, the base never compared",
       w.posts == ["repos/o/r/actions/jobs/10/rerun"] and w.compares == 0)
    w = pinned(run(1, "1"), v_run())
    w.runs[1]["event"] = "workflow_dispatch"
    w.sweep()
    ok("stale pin null: a dispatched run's gate (it rev-parses origin/<base> at its re-run) is re-run, the "
       "base never compared", w.posts == ["repos/o/r/actions/jobs/10/rerun"] and w.compares == 0)
    w = pinned(run(1, "1"), run(2, "2"), v_run())
    rc, out = w.sweep()
    ok("stale pin: two stale reds at one head take one dispatch, one compare, and the second says so",
       w.posts == [dispatch] and w.compares == 1 and "run 2 left to this sweep's dispatched run" in out)
    w = pinned(run(1, "1", started="5", units=["6"]), run(2, "1", started="5", units=["6"]), v=2)
    w.sweep()
    ok("stale pin, settle: the #3261 pair (two deferrals under a pre-fix program) takes one dispatch, no re-run",
       w.posts == [dispatch])
    w = pinned(run(1, "1", started="5", units=["6"]), run(2, "1", started="5", units=["6"]),
               run(5, "6", g="success", started="7"), v=2)
    w.runs[5]["event"] = "workflow_dispatch"
    rc, out = w.sweep()
    ok("stale pin, settle, no loop: settle hands judge the head's runs, so a dispatched run created after the "
       "pair's gates concluded is their fresh judge; nothing posted", w.posts == [] and "run 5 re-judges" in out)
    w = pinned(run(1, "1"), run(5, "3", g="success"), v_run(created="2"))
    w.runs[5]["event"] = "workflow_dispatch"
    rc, out = w.sweep()
    ok("stale pin, no loop: a dispatched run created after the stale gate concluded re-judges the head; "
       "nothing posted", w.posts == [] and "run 5 re-judges" in out)
    w = pinned(run(1, "1"), run(5, "2", g="success"), v_run())
    w.runs[5]["event"] = "workflow_dispatch"
    rc, out = w.sweep()
    ok("stale pin, no loop: a dispatched run created in the second the stale gate concluded is that fresh judge",
       w.posts == [] and "run 5 re-judges" in out)
    # R10-HOTFIX-GATE-REDISPATCH-LOOP arm 2 (#3446): re-running an old pull_request gate moved its
    # completion past every dispatch's creation, so each sweep dispatched again at a head already judged.
    for st, concl in (("completed", "success"), ("queued", None), ("in_progress", None)):
        w = pinned(run(1, "1"), run(5, "1", status=st, g="success", gstatus=st), v_run())
        w.runs[5]["event"] = "workflow_dispatch"
        w.runs[1]["gate"]["completed_at"] = "8"
        rc, out = w.sweep()
        ok(f"stale pin, one judge per head: a dispatch listed {st}, created before the stale gate's re-run completed "
           f"is the fresh judge; nothing dispatched", dispatch not in w.posts and "run 5 re-judges" in out)
    for concl in ("failure", "cancelled"):
        w = pinned(run(1, "1"), run(5, "1", g=concl), v_run())
        w.runs[5]["event"] = "workflow_dispatch"
        w.runs[1]["gate"]["completed_at"] = "8"
        rc, out = w.sweep()
        ok(f"stale pin null: with only a {concl} dispatch at the head it dispatches, once",
           w.posts.count(dispatch) == 1 and "dispatches=1" in out)
    # #3400 at 7326025c (roster carry 1, R10-HOTFIX-SWEEP-TOKEN-ACTOR): the App-actor decider's sweep left the stale
    # edit red "to this sweep's dispatched run"; that run (actor the bot) went green, its check replaced no other
    # run's red, and its completion fired no workflow_run. Its own sweep-self re-runs the stale reds, once.
    def shape3400():
        f = run(5, "5", status="in_progress", g="success", started="6", units=["5"])
        f["event"] = "workflow_dispatch"
        f["units"].append({"name": sweep.SELF_JOB, "completed_at": None})
        w = pinned(run(1, "1"), run(2, "1", started="3"), run(3, "1", g="success", started="4"), f, v=5)
        w.caller = 5
        return w
    w = shape3400()
    rc, out = w.sweep()
    ok("stale pin, #3400: the dispatched fresh judge, green, re-runs from inside itself the stale reds it was "
       "left, once each, dispatching nothing", w.posts == ["repos/o/r/actions/jobs/10/rerun", "repos/o/r/actions/jobs/20/rerun"]
       and w.sleeps == [] and "dispatches=0" in out)
    w = shape3400()
    w.runs[5]["gate"].update(status="in_progress", conclusion=None, completed_at=None)
    w.v_id, w.caller = 3, None
    w.script[1] = finish(5, "success")
    rc, out = w.sweep()
    ok("stale pin, #3400 null: the decider's own sweep, while the fresh judge runs and after it completes, re-runs "
       "nothing (the fresh judge's sweep owns it)", w.posts == [] and "run 5 re-judges" in out)
    w = shape3400()
    w.runs[5]["gate"]["conclusion"] = "failure"
    w.sweep()
    ok("stale pin, #3400 null: a fresh judge that ended red re-runs no stale red from inside itself",
       w.posts == [])
    # R10-HOTFIX-SWEEP-SETTLE-LOOP: the recorded #3308 loop. Run 42471173865's gate re-run re-stamped its
    # skipped jobs past the two sibling gates' starts; on main settle read them as sources and re-ran both,
    # whose re-runs re-stamped theirs, each pair re-running the other up to the attempt cap.
    for v in REC3308:
        w = world3308(v)
        rc, out = w.sweep()
        ok(f"#3308: skipped jobs re-stamped by a sibling's gate re-run are no source; settle re-runs nothing "
           f"(swept from run {v})", rc == 0 and w.posts == [] and "reruns=0" in out)

    def late_codeql(runs):     # null: a real source, codeql python, finishing after run 42470643072's gate started
        u = next(j for j in runs[42470642055]["units"] if j["name"] == "codeql / Analyze (python)")
        u["completed_at"] = "2026-11-08T11:47:30Z"
    w = world3308(edit=late_codeql)
    w.sweep()
    ok("#3308 null: a non-skipped source (codeql python) finishing after a sibling gate started re-runs that gate, once",
       w.posts == ["repos/o/r/actions/jobs/128721143539/rerun"])
    w.posts, r = [], w.runs[42470643072]
    r["run_attempt"] += 1
    r["gate"].update(started_at="2026-11-08T11:48:40Z", completed_at="2026-11-08T11:49:10Z")
    for u in r["units"]:
        if u["conclusion"] == "skipped":
            u.update(started_at="2026-11-08T11:48:38Z", completed_at="2026-11-08T11:48:38Z")
    for v in REC3308:
        w.v_id = v
        w.sweep()
    ok("#3308 null: that re-run, judged after the source, re-stamping its own skips, is final; no sweep re-runs a gate",
       w.posts == [])
    ok("sweep.SWEEP_ACTOR is the recorded bot login", getattr(sweep, "SWEEP_ACTOR", None) == BOT)
    # Fix (2): a gate attempt the bot itself started, with no non-skipped source finishing after it, is not
    # re-run again by settle, whichever arm reads it undecided (here the lagging-pair arm).
    for actor, want in ((BOT, []), ("tvofi", ["repos/o/r/actions/jobs/10/rerun"])):
        w = World([run(1, "1", attempt=2, started="5", units=["4"]), run(2, "1", attempt=2, started="5", units=["4"])], 2)
        for r in w.runs.values():
            r["gate"]["completed_at"], r["triggering_actor"] = "6", {"login": actor}
        w.sweep()
        ok(f"settle: an overlapping pair of re-run gates, re-run by {actor}, with no source after them, "
           f"{'is final' if not want else 'is re-judged (the lower id, null)'}", w.posts == want)
    # R10-HOTFIX-SWEEP-DEFERRAL-DISPATCH: a deferral red is no verdict where a green gate covers the newest event,
    # and a dispatched run whose first gate was green stays the head's fresh judge after a refresh re-ran it red.
    dispatch3544 = "repos/o/r/actions/workflows/ci.yml/dispatches"
    rerun_of = lambda rid: f"repos/o/r/actions/jobs/{rid * 10}/rerun"
    w = world3544()
    rc, out = w.sweep()
    ok("#3544: the recorded shape (green dispatch, review events, deferral reds, stale pin) dispatches nothing; "
       "D is re-run in place and R1 left to it, D's first green attempt being the head's fresh judge",
       rc == 0 and w.posts == [rerun_of(D3544)] and f"run {D3544} re-judges" in out and "dispatches=0" in out)
    w = world3544(v_id=R1_3544)
    rc, out = w.sweep()
    ok("#3544: gate-sweep run 43573334631, R1's settle, the sweep that dispatched run 43574296856, dispatches nothing; "
       "D is re-run in place, every stale-pinned deferral left to it", rc == 0 and w.posts == [rerun_of(D3544)]
       and "dispatches=0" in out and out.count(f"run {D3544} re-judges") == 4)
    w = world3544(ids=(R1_3544, R2_3544))
    rc, out = w.sweep()
    ok("#3544 without D: R1's deferral red under a stale pin, R2 green and newest-covering, is re-run in place, "
       "never dispatched", w.posts == [rerun_of(R1_3544)] and "dispatches=0" in out and "deferral" in out)

    def overlapped(runs):    # R2's last source finished while R1's gate ran: it may have read R2 busy, so a deferral
        runs[R2_3544]["units"][-1]["completed_at"] = "2026-11-14T07:55:00Z"
    w = world3544(ids=(R1_3544, R2_3544), edit=overlapped)
    w.sweep()
    ok("#3544: a source finishing while the red gate ran (after its start) makes it a deferral: re-run in place",
       w.posts == [rerun_of(R1_3544)])

    def old_red(runs):       # a third, older review run whose red gate is beside R2's green one, not covering
        r0 = dict(runs[R1_3544], id=R1_3544 - 1, created_at="2026-11-14T07:30:00Z")
        r0["gate"] = dict(r0["gate"], id=r0["id"] * 10, started_at="2026-11-14T07:50:00Z", completed_at="2026-11-14T07:51:00Z")
        r0["units"] = []
        runs[r0["id"]] = r0
    w = world3544(ids=(R1_3544, R2_3544), edit=old_red)
    w.sweep()
    ok("#3544: one green newest-covering gate covers the head whatever other reds sit beside it: both deferrals "
       "re-run in place, nothing dispatched", w.posts == [rerun_of(R1_3544 - 1), rerun_of(R1_3544)])

    def real_red(runs):      # R1's gate judged after every OTHER run's source had finished: a verdict, no deferral
        runs[R1_3544]["gate"].update(started_at="2026-11-14T08:02:00Z", completed_at="2026-11-14T08:02:30Z")
        runs[R1_3544]["units"].append({"name": "late own job", "conclusion": "success",
                                       "completed_at": "2026-11-14T08:02:10Z"})   # its own run's: busy() never reads it
    w = world3544(ids=(R1_3544, R2_3544), edit=real_red)
    rc, out = w.sweep()
    ok("#3544 null: a real red on a stale pin, no dispatch at the head, still takes one dispatch",
       w.posts == [dispatch3544] and "dispatches=1" in out)
    # Fix review of #3584 at b17c7877, cases B and C: a job of another run that busy() never reads, finishing after a
    # real red's start, made it a deferral. Deferral means busy() was true at the red gate's start, nothing wider.
    def late_report_job(runs):     # B: R2, green, covering, a higher id whose gate had started: busy() skips it
        real_red(runs)
        runs[R2_3544]["units"].append({"name": "tests / nightly-status", "conclusion": "failure",
                                       "started_at": "2026-11-14T08:01:50Z", "completed_at": "2026-11-14T08:02:10Z"})
    w = world3544(ids=(R1_3544, R2_3544), edit=late_report_job)
    w.sweep()
    ok("#3584 B: a real red beside the covering run's report-only job finishing after its start still dispatches",
       w.posts == [dispatch3544])
    for gate_start in ("2026-11-14T08:01:00Z", "2026-11-14T08:03:00Z"):
        def newer_run(runs, gs=gate_start):   # C: a newer review run, its budget-raise-gate done, a job after its gate
            real_red(runs)
            r3 = {"id": R2_3544 + 1, "event": "pull_request_review", "created_at": "2026-11-14T07:59:00Z",
                  "status": "completed", "run_attempt": 1, "conclusion": "success", "triggering_actor": {"login": "tvofi"},
                  "display_title": "CI review pr=7 base=main sha=H",
                  "gate": {"id": (R2_3544 + 1) * 10, "name": "gate", "status": "completed", "conclusion": "success",
                           "started_at": gs, "completed_at": "2026-11-14T08:03:30Z"},
                  "units": [{"name": "prelude", "conclusion": "success", "started_at": "2026-11-14T07:59:10Z",
                             "completed_at": "2026-11-14T07:59:40Z"},
                            {"name": "budget-raise-gate / budget-raise-gate", "conclusion": "success",
                             "started_at": "2026-11-14T07:59:45Z", "completed_at": "2026-11-14T08:00:20Z"},
                            {"name": "refresh", "conclusion": "success",      # no unit: busy() never reads it
                             "started_at": "2026-11-14T07:59:05Z", "completed_at": "2026-11-14T08:04:00Z"}]}
            runs[r3["id"]] = r3
        w = world3544(ids=(R1_3544, R2_3544), edit=newer_run)
        w.sweep()
        ok(f"#3584 C: a real red beside a newer run (gate started {gate_start[11:19]}) whose non-unit job finished "
           "after the red's start still dispatches", w.posts == [dispatch3544])
    w = world3544(ids=(R1_3544, R2_3544), edit=newer_run)
    w.runs[R2_3544 + 1]["units"][-1]["name"] = "governance / delivery-status-publish"
    w.sweep()
    ok("#3584 C null: that newer run, its gate not started, with a governance job unfinished at the red's start "
       "(busy() reads it as a unit) makes the red a deferral: re-run in place", w.posts == [rerun_of(R1_3544)])
    w = world3544(edit=real_red)
    rc, out = w.sweep()
    ok("#3544: a real red on a stale pin beside a dispatch whose first gate was green dispatches nothing",
       dispatch3544 not in w.posts and f"run {D3544} re-judges" in out)
    for why, perturb in (("whose first gate was red", lambda w: w.runs[D3544]["attempts"][1].update(conclusion="failure")),
                         ("whose first attempt cannot be read", lambda w: w.runs[D3544].pop("attempts"))):
        w = world3544(edit=real_red)
        perturb(w)
        rc, out = w.sweep()
        ok(f"#3544 null: a real red on a stale pin beside a red dispatch {why} dispatches, once",
           w.posts.count(dispatch3544) == 1 and "dispatches=1" in out)
    w = world3544(edit=real_red)
    w.runs[D3544].update(run_attempt=1)
    w.sweep()
    ok("#3544 null: a red dispatch at its first attempt is read as is, never its attempts (one dispatch)",
       w.posts.count(dispatch3544) == 1 and w.attempt_reads == 0)
    w = world3544(ids=(R1_3544, R2_3544), edit=lambda runs: runs[R1_3544].update(run_attempt=sweep.ATTEMPT_CAP - 1))
    rc, out = w.sweep()
    ok("#3544 bound: a deferral red at attempt 44 is left at the cap, neither re-run nor dispatched",
       w.posts == [] and "at the cap" in out)

    def deferred_again(runs):    # the in-place re-runs overlapped: D's went green, R1's deferred to it again
        runs[D3544].update(run_attempt=3, conclusion="success")
        runs[D3544]["gate"].update(conclusion="success", started_at="2026-11-14T08:02:20Z", completed_at="2026-11-14T08:03:10Z")
        runs[R1_3544].update(run_attempt=2, triggering_actor={"login": BOT})
        runs[R1_3544]["gate"].update(started_at="2026-11-14T08:02:30Z", completed_at="2026-11-14T08:03:00Z")
    w = world3544(v_id=R1_3544, edit=deferred_again)
    rc, out = w.sweep()
    ok("#3544 bound: R1's re-run that deferred again, swept from itself, is left by settle (the bot's attempt, "
       "no source after it)", w.posts == [] and "dispatches=0" in out)
    w = world3544(v_id=D3544, edit=deferred_again)
    w.runs[D3544].update(status="in_progress")
    w.runs[D3544]["units"].append({"name": sweep.SELF_JOB, "conclusion": None, "completed_at": None})
    w.caller = D3544
    rc, out = w.sweep()
    ok("#3544 bound: D, green, sweeping itself, re-runs each deferral at the head once in place and dispatches nothing",
       w.posts == [rerun_of(i) for i in sorted(REC3544) if i != D3544 and i != R2_3544] and "dispatches=0" in out)
    return checks


def run_self():
    checks = run_checks()
    for name, good in checks:
        if not good:
            print(f"FAIL {name}")
    bad = sum(1 for _, g in checks if not g)
    print(f"sweep self-test: {len(checks)} checks, {bad} failed")
    return 1 if bad else 0
