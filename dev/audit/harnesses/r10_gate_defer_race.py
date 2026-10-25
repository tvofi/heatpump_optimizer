#!/usr/bin/env python3
"""R10-GATE-DEFER: replay the runs at one PR head through a tree's own tools/ci programs.

    python3 dev/audit/harnesses/r10_gate_defer_race.py [--ci DIR] [--edit-s S] [scenario ...]

DIR holds the `tools/ci` and `tools/pr` copies to drive (default: this tree's).
To measure a baseline, export it first and point --ci at its tools/ci:

    git archive <sha> tools/ci tools/pr | tar -x -C "$D" && python3 ... --ci "$D/tools/ci"

A discrete-event replay with a simulated clock: each run is a thread whose
`prelude.outputs` (the non-code wait, whatever it is called in that tree) and
`gate.judge` read a fake Actions API over the shared state and sleep on the
simulated clock; one thread runs at a time, so a replay is deterministic.
`judge` gets the clock only where its signature takes `sleep`/`now`. Where the
tree has `tools/ci/sweep.py`, every run's completion starts that tree's sweep
on the same clock (gate-sweep.yml's trigger), and each re-run it posts re-judges
that run's gate (marked `sweep` below).

Scenarios:
  2754      PR #2754 at 8c409800: an edit run (40119473491) and a code run
            (40119473870) created the same second, the edit run numbered lower,
            and a review run (40119483652) 7 s later. Prelude starts and unit
            spans are the jobs API's for those runs (2026-10-24); the code run's
            unit span is an ESTIMATE (its gate had not started at read time).
            --edit-s replaces the edit run's measured 518 s body-unit span.
  2754-red  the same, with the code run's `tests / closures` red: the null
            for masking (every published verdict must be red).
  pair      two code runs whose gates start in the same second, each listed by
            the jobs API 5 s after it starts: the simultaneous-completion shape.
  cascade   three completed runs whose gates went red deferring, a queued review
            run (the decider), and a re-run of the oldest run's gate (#2748).
  editcode  2754 without its review run: the edit run, numbered lower, is the
            decider, so a code gate expiring at the bound (--edit-s past 740)
            is red on the HIGHER id (#2770 round-1 review).
  single    one code run alone at the head: the null (no wait, no red).

Per scenario it prints every published `gate` verdict with its simulated time,
then: UNDECIDED-RED (a FAIL whose reason is the deferral), MASKED (a PASS
published while a real red source exists), DEADLOCK (no gate PASS and no real
red: nothing at the head ever decides green), and the gates' total wait, all
over the gates the scenario runs; then RESIDUAL-RED, the runs whose latest
gate, after every sweep has converged, is still the deferral's red.
"""
from __future__ import annotations

import argparse
import heapq
import importlib
import inspect
import sys
import threading
from pathlib import Path

REPO, HEAD, PR = "o/r", "H" * 40, 7
MODULES = ("prelude", "gate", "ghapi", "codeql_scope", "sweep")
JUDGE_S = 20        # read to publish: #2754 edit gate step 18:22:44 -> 18:23:05 (21 s, jobs API)
PULL = {"state": "open", "head": {"sha": HEAD, "repo": {"full_name": REPO}}, "base": {"ref": "main"}}


class Sim:
    """A clock that advances only when every live thread sleeps; wakes one thread per step."""

    def __init__(self):
        self.t, self.cv, self.running, self.wakes, self.seq = 0, threading.Condition(), 0, [], 0

    def sleep(self, s):
        with self.cv:
            flag = [False]
            self.seq += 1
            heapq.heappush(self.wakes, (self.t + s, self.seq, flag))
            self.running -= 1
            self.cv.notify_all()
            while not flag[0]:
                self.cv.wait()

    def now(self):
        return self.t

    def later(self, fn, at):
        """Run fn on its own thread at simulated time `at`; safe to call from a running thread."""
        flag = [False]
        with self.cv:
            self.seq += 1
            heapq.heappush(self.wakes, (at, self.seq, flag))

        def body():
            with self.cv:
                while not flag[0]:
                    self.cv.wait()
            try:
                fn()
            finally:
                with self.cv:
                    self.running -= 1
                    self.cv.notify_all()
        threading.Thread(target=body, daemon=True).start()

    def spawn(self, fn):
        def body():
            try:
                fn()
            finally:
                with self.cv:
                    self.running -= 1
                    self.cv.notify_all()
        with self.cv:
            self.running += 1
        threading.Thread(target=body, daemon=True).start()

    def run(self):
        while True:
            with self.cv:
                while self.running > 0:
                    self.cv.wait()
                if not self.wakes:
                    return
                t, _, flag = heapq.heappop(self.wakes)
                self.t, flag[0] = t, True
                self.running += 1
                self.cv.notify_all()


class Head:
    def __init__(self, ci: Path, sim: Sim):
        sys.path[:0] = [str(ci)]
        for m in MODULES:
            sys.modules.pop(m, None)
        self.prelude, self.gate = importlib.import_module("prelude"), importlib.import_module("gate")
        self.sweep = importlib.import_module("sweep") if (ci / "sweep.py").exists() else None
        self.sim, self.runs, self.verdicts, self.waited = sim, {}, [], 0
        self.timed = "sleep" in inspect.signature(self.gate.judge).parameters

    def get(self, path, params=None):
        if path.endswith(f"/pulls/{PR}"):
            return 200, {}, PULL
        if path.endswith("ci.yml/runs"):
            return 200, {}, {"workflow_runs": [{"id": i, "display_title": r["title"], "status": r["status"]}
                                               for i, r in sorted(self.runs.items()) if r["created"] <= self.sim.t]}
        rid = int(path.split("/runs/")[1].split("/")[0])
        r = self.runs[rid]
        return 200, {}, {"jobs": [{"name": k, "status": s, "conclusion": c, "id": rid}
                                  for k, (s, c, seen) in r["jobs"].items() if seen <= self.sim.t]}

    def ctx(self, rid, kind, attempt=1):
        env = {"GITHUB_SHA": "M", "GITHUB_REPOSITORY": REPO, "GITHUB_RUN_ID": str(rid),
               "GITHUB_RUN_ATTEMPT": str(attempt)}
        pr = {"number": PR, "base": {"ref": "main"}, "head": {"sha": HEAD}, "labels": []}
        if kind == "review":
            return self.prelude.context("pull_request_review", {"action": "submitted", "pull_request": pr}, env)
        action = "edited" if kind == "edit" else "synchronize"
        return self.prelude.context("pull_request", {"action": action, "pull_request": pr}, env)

    def names(self, kind):
        ws = self.prelude.workset(kind, str(PR))
        return [f"{u} / {n}" for u in sorted(ws & set(self.gate.UNITS)) for n in self.gate.UNITS[u]]

    def add(self, rid, kind, created, prelude_at, units_s, red=(), lag=0, done=False):
        title = self.prelude.title(kind, str(PR), "main", "M")
        self.runs[rid] = {"title": title, "status": "queued", "created": created, "jobs": {}, "kind": kind,
                          "attempt": 1, "gate_at": 0}
        r = self.runs[rid]
        if done:                                   # a completed run whose gate went red deferring
            r["status"] = "completed"
            r["jobs"] = {n: ("completed", "success", 0) for n in ["prelude"] + self.names(kind)}
            r["jobs"]["gate"] = ("completed", "failure", 0)
            r["seeded"] = "FAIL (seeded) still being judged"
            return

        def life():
            self.sim.sleep(prelude_at - self.sim.t)
            r["status"] = "in_progress"
            r["jobs"]["prelude"] = ("in_progress", None, self.sim.t)
            c = self.ctx(rid, kind)
            _, why = self.prelude.outputs(c, [], self.get, self.sim.sleep)
            r["jobs"]["prelude"] = ("completed", "failure" if why else "success", self.sim.t)
            for n in self.names(kind):
                r["jobs"][n] = ("in_progress", None, self.sim.t)
            self.sim.sleep(units_s)
            for n in self.names(kind):
                r["jobs"][n] = ("completed", "failure" if n in red else "success", self.sim.t)
            self.judge(rid, kind, lag)
        self.sim.spawn(life)

    def rerun_gate(self, rid, at):
        def again():
            self.sim.sleep(at - self.sim.t)
            r = self.runs[rid]
            r["status"] = "in_progress"
            self.judge(rid, r["kind"], 0, attempt=2)
        self.sim.spawn(again)

    def judge(self, rid, kind, lag, attempt=1, by_sweep=False):
        r = self.runs[rid]
        r["attempt"], r["gate_at"] = attempt, self.sim.t
        r["jobs"]["gate"] = ("in_progress", None, self.sim.t + lag)
        c = self.ctx(rid, kind, attempt)
        t0 = self.sim.t
        kw = {"sleep": self.sim.sleep, "now": self.sim.now} if self.timed else {}
        out = self.gate.judge(c, {"kind": kind, "pr": str(PR)}, self.get, lambda b, h: True, **kw)[0]
        self.waited += self.sim.t - t0
        self.sim.sleep(JUDGE_S)                    # the job publishes its check-run after its last read
        self.verdicts.append((self.sim.t, rid, out, self.sim.t - JUDGE_S - t0, by_sweep))
        r["jobs"]["gate"] = ("completed", "success" if out == "PASS" else "failure", self.sim.t)
        r["status"] = "completed"
        if self.sweep:                             # gate-sweep.yml: on every CI run's completion
            self.sim.later(lambda: self.sweep.main(["--run", str(rid), "--repo", REPO], self.sweep_get,
                                                   self.sweep_post, lambda _: None, self.sim.sleep, self.sim.now),
                           self.sim.t)

    def sweep_get(self, path, params=None):
        """The Actions API as sweep.py reads it, over the same state."""
        stamp = "{:08d}".format
        if path.endswith(f"/pulls/{PR}"):
            return 200, {}, PULL
        listed = {i: r for i, r in self.runs.items() if r["created"] <= self.sim.t}
        row = {i: {"id": i, "status": r["status"], "run_attempt": r["attempt"], "created_at": stamp(r["created"]),
                   "head_sha": HEAD, "path": self.sweep.CI_PATH, "pull_requests": [{"number": PR}]}
               for i, r in listed.items()}
        if path.endswith("/actions/runs"):
            return 200, {}, {"workflow_runs": list(row.values())}
        rid = int(path.split("/runs/")[1].split("/")[0])
        if not path.endswith("/jobs"):
            return 200, {}, row[rid]
        r = self.runs[rid]
        s, c, seen = r["jobs"].get("gate", (None, None, self.sim.t + 1))
        gate = {"name": "gate", "id": rid, "status": s, "conclusion": c, "started_at": stamp(r["gate_at"])}
        return 200, {}, {"jobs": [gate] if seen <= self.sim.t else []}

    def sweep_post(self, path, body=None):
        rid = int(path.split("/jobs/")[1].split("/")[0])
        r = self.runs[rid]
        r["status"], r["jobs"]["gate"] = "in_progress", ("queued", None, self.sim.t)
        self.sim.later(lambda: self.judge(rid, r["kind"], 0, attempt=r["attempt"] + 1, by_sweep=True), self.sim.t)
        return 201, {}, {}


def scenario(ci: Path, name: str, edit_s: int):
    sim = Sim()
    h = Head(ci, sim)
    real_red = False
    if name in ("2754", "2754-red"):
        red = ("tests / closures",) if name == "2754-red" else ()
        real_red = bool(red)
        h.add(40119473491, "edit", 0, 199, edit_s)           # prelude 18:13:40, gate 18:22:44 (created 18:10:21)
        h.add(40119473870, "code", 0, 363, 900, red=red)     # prelude 18:16:24; unit span ESTIMATED
        h.add(40119483652, "review", 7, 477, 30)             # prelude 18:18:18, budget-raise-gate ~20 s
    elif name == "editcode":
        h.add(40119473491, "edit", 0, 199, edit_s)
        h.add(40119473870, "code", 0, 363, 900)
    elif name == "pair":
        h.add(100, "code", 0, 30, 600, lag=5)
        h.add(101, "code", 0, 30, 600, lag=5)
    elif name == "cascade":
        for i in (90, 91, 92):
            h.add(i, "code", 0, 0, 0, done=True)
        h.add(99, "review", 0, 60, 30)
        h.rerun_gate(90, 30)
    elif name == "single":
        h.add(100, "code", 0, 30, 600)
    sim.run()
    defer = "still being judged"
    own = [v for v in h.verdicts if not v[4]]
    undecided = sum(1 for _, _, o, _, _ in own if o.startswith("FAIL") and defer in o)
    masked = sum(1 for _, _, o, _, _ in h.verdicts if o == "PASS") if real_red else 0
    deadlock = not real_red and not any(o == "PASS" for _, _, o, _, _ in h.verdicts)
    latest = {rid: r["seeded"] for rid, r in h.runs.items() if "seeded" in r}
    latest.update((rid, o) for _, rid, o, _, _ in h.verdicts)
    residual = sum(1 for o in latest.values() if o.startswith("FAIL") and defer in o)
    for t, rid, o, w, by in h.verdicts:
        print(f"  t={t:>5}s run {rid}{' sweep' if by else ''} (waited {w} s): {o}")
    print(f"{name}: verdicts {len(own)} UNDECIDED-RED {undecided} MASKED {masked} "
          f"DEADLOCK {'yes' if deadlock else 'no'} gate-wait {h.waited} s (judge takes a clock: {h.timed})")
    print(f"{name}: sweep {'present' if h.sweep else 'absent'} re-runs {len(h.verdicts) - len(own)} "
          f"RESIDUAL-RED {residual}")
    for m in MODULES:
        sys.modules.pop(m, None)
    sys.path.remove(str(ci))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ci", default=str(Path(__file__).resolve().parents[3] / "tools" / "ci"))
    ap.add_argument("--edit-s", type=int, default=518)
    ap.add_argument("scenarios", nargs="*", default=["2754", "2754-red", "pair", "cascade", "editcode", "single"])
    a = ap.parse_args()
    ci = Path(a.ci).resolve()
    for s in a.scenarios:
        scenario(ci, s, a.edit_s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
