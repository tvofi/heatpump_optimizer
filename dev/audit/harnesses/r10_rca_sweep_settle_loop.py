#!/usr/bin/env python3
"""R10-RCA-SWEEP-SETTLE-LOOP: replay gate-sweep.yml in a CLOSED loop over a recorded head.

    python3 -I dev/audit/harnesses/r10_rca_sweep_settle_loop.py replay [--ci DIR] [--no-restamp] [--alarm N]
    python3 -I dev/audit/harnesses/r10_rca_sweep_settle_loop.py census FILE --since ISO --until ISO [--alarm N]

replay   the #3319 head 8d4ff2f2 (two ci.yml runs, a code run 42469369199 and an edit run
         42469369682, both with a real red: budget-raise-gate failed) from
         r10_rca_sweep_settle_loop.json, through DIR's `sweep.main` (default: this tree's
         tools/ci; a baseline is `git archive <sha> tools/ci | tar -x -C $D` and `--ci $D/tools/ci`).
         The loop the single-pass replays and sweep_selftest.py never closed: every re-run the
         sweep posts becomes the run's next attempt, with GitHub's recorded re-run transition
         applied -- the jobs attempt 2 changed (every SKIPPED job's stamps, the gate's) shifted
         to the new gate start, all other jobs byte-identical, the gate red again for its
         recorded duration -- and that attempt's completion fires the sweep again, as
         gate-sweep.yml does on every CI completion. It stops at a fixed point (no sweep
         re-runs anything) or at GitHub's 50-attempt ceiling.
         `--no-restamp` is the hand-written fixtures' world (a re-run moves no job but the
         gate): the null control. Prints one line per re-run, then
         `RESULT replay reruns=<n> max_attempt=<m> sim_minutes=<t> alarm=<yes|no>`, where alarm is
         the loop detector's predicate: some run's attempt reached N (default 10).
census   the same predicate over a saved `gh api --paginate .../workflows/ci.yml/runs` TSV
         (id, run_attempt, created_at, ...): runs created in [since, until) whose attempt is >= N.
         `RESULT census runs=<n> reattempts=<r> at_or_over_alarm=<k> at_cap=<c> max_attempt=<m>`.
"""
from __future__ import annotations

import argparse
import csv
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

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


HERE = Path(__file__).resolve().parent
ROOT = repo_root(__file__)
FIXTURE = HERE / "r10_rca_sweep_settle_loop.json"
GITHUB_CEILING = 50          # GitHub refuses a run's 51st attempt
SWEEP_DELAY_S = 12           # gate-sweep.yml's first read after a CI completion (#3282 replay: +11 s)


def epoch(s):
    return None if s is None else datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def iso(t):
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class World:
    """Two ci.yml runs at one head, re-run as GitHub re-ran them on 2026-11-08."""

    def __init__(self, fx, sweep, restamp):
        self.fx, self.sweep, self.restamp = fx, sweep, restamp
        self.runs, self.pending, self.events, self.reruns = {}, [], [], []
        for r in fx["runs"]:
            a1 = {j["name"]: dict(j) for j in r["attempt1_jobs"]}
            a2 = r["later_attempts_changed_jobs"]["2"]
            g2 = next(j for j in a2 if j["name"] == "gate")
            t2 = epoch(g2["started_at"])
            # the re-run transition, relative to the new gate's start (recorded attempt 2)
            tmpl = {j["name"]: {k: (None if j[k] is None else epoch(j[k]) - t2)
                                for k in ("started_at", "completed_at")} | {"conclusion": j["conclusion"]}
                    for j in a2}
            self.runs[r["id"]] = {"id": r["id"], "created_at": r["created_at"], "run_attempt": 1,
                                  "status": "completed", "jobs": a1, "tmpl": tmpl,
                                  "done_at": epoch(a1["gate"]["completed_at"])}
        last = max(self.runs.values(), key=lambda r: r["done_at"])
        # The replay starts at the later attempt-1 completion (code run, 10:22:13Z), the first moment
        # both runs had concluded; the earlier run's own completion sweep (09:59Z, the code run still
        # running) is not replayed.
        self.now = last["done_at"]
        self.events.append((self.now + SWEEP_DELAY_S, last["id"]))

    # -- the Actions API as sweep.py reads it ------------------------------------------------
    def apply(self):
        """Transitions whose time has come: a re-run's gate starts, completes red, the run completes."""
        for p in [p for p in self.pending if p[0] <= self.now]:
            self.pending.remove(p)
            _, rid, what = p
            r = self.runs[rid]
            if what == "start":
                r["jobs"]["gate"].update(status="in_progress")
            else:
                r["jobs"]["gate"].update(status="completed", conclusion=r["tmpl"]["gate"]["conclusion"],
                                         completed_at=iso(self.now))
                r["status"], r["done_at"] = "completed", self.now
                self.events.append((self.now + SWEEP_DELAY_S, rid))

    def get(self, path, params=None):
        self.apply()
        fx = self.fx
        tail = path.split(f"repos/{fx['repo']}/", 1)[1]
        if tail == f"pulls/{fx['pr']}":
            return 200, {}, {"head": {"sha": fx["head"]}}
        if tail == "actions/runs":
            return 200, {}, {"workflow_runs": [self.run_view(r) for r in self.runs.values()]}
        if tail.endswith("/jobs"):
            rid = int(tail.split("/")[2])
            return 200, {}, {"jobs": [dict(j) for j in self.runs[rid]["jobs"].values()]}
        rid = int(tail.split("/")[2])
        return 200, {}, self.run_view(self.runs[rid])

    def run_view(self, r):
        return {"id": r["id"], "created_at": r["created_at"], "status": r["status"],
                "run_attempt": r["run_attempt"], "path": self.sweep.CI_PATH, "head_sha": self.fx["head"],
                "pull_requests": [{"number": self.fx["pr"]}]}

    def post(self, path, body=None):
        rid = next(i for i, r in self.runs.items() if f"/jobs/{r['jobs']['gate']['id']}/rerun" in path)
        r = self.runs[rid]
        r["run_attempt"] += 1
        r["status"] = "in_progress"
        g0 = self.now + 4                                   # the re-run's gate starts ~4 s after the post
        for name, t in r["tmpl"].items():
            if name != "gate" and not self.restamp:
                continue
            j = r["jobs"][name]
            j.update({k: (None if t[k] is None else iso(g0 + t[k])) for k in ("started_at", "completed_at")})
            if name == "gate":
                j.update(status="queued", conclusion=None, completed_at=None, id=j["id"] + 1)
        dur = r["tmpl"]["gate"]["completed_at"]
        self.pending += [(g0, rid, "start"), (g0 + dur, rid, "done")]
        self.reruns.append((iso(self.now), rid, r["run_attempt"]))

    # -- the loop ---------------------------------------------------------------------------
    def drive(self, out):
        t_first = min(t for t, _ in self.events)
        while True:
            self.pending.sort()
            self.events.sort()
            nxt = min([e[0] for e in self.events] + [p[0] for p in self.pending], default=None)
            if nxt is None or max(r["run_attempt"] for r in self.runs.values()) >= GITHUB_CEILING:
                break
            self.now = max(self.now, nxt)
            self.apply()
            due = [e for e in self.events if e[0] <= self.now]
            for e in due:
                self.events.remove(e)
                before = len(self.reruns)
                lines = []

                def sleep(s):
                    self.now += s
                    self.apply()
                self.sweep.main(["--run", str(e[1]), "--repo", self.fx["repo"]], self.get, self.post,
                                lines.append, sleep, lambda: self.now)
                for t, rid, att in self.reruns[before:]:
                    out(f"replay: {t} the sweep for run {e[1]}'s completion re-ran gate of run {rid} -> attempt {att}")
        return (self.now - t_first) / 60


def load_sweep(ci):
    sys.path.insert(0, str(ci))
    for m in ("sweep", "sweep_selftest"):
        sys.modules.pop(m, None)
    return importlib.import_module("sweep")


def replay(ci, restamp, alarm):
    fx = json.loads(FIXTURE.read_text())
    w = World(fx, load_sweep(ci), restamp)
    minutes = w.drive(print)
    top = max(r["run_attempt"] for r in w.runs.values())
    print(f"RESULT replay reruns={len(w.reruns)} max_attempt={top} sim_minutes={minutes:.0f} "
          f"alarm={'yes' if top >= alarm else 'no'}")
    return 0


def census(path, since, until, alarm):
    rows = [r for r in csv.reader(open(path), delimiter="\t") if since <= r[2] < until]
    at = [int(r[1]) for r in rows]
    print(f"RESULT census runs={len(at)} reattempts={sum(a - 1 for a in at)} "
          f"at_or_over_alarm={sum(a >= alarm for a in at)} at_cap={sum(a >= 44 for a in at)} "
          f"max_attempt={max(at, default=0)}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("replay")
    r.add_argument("--ci", default=str(ROOT / "tools" / "ci"))
    r.add_argument("--no-restamp", action="store_true")
    r.add_argument("--alarm", type=int, default=10)
    c = sub.add_parser("census")
    c.add_argument("file")
    c.add_argument("--since", required=True)
    c.add_argument("--until", required=True)
    c.add_argument("--alarm", type=int, default=10)
    a = ap.parse_args(argv)
    if a.cmd == "replay":
        return replay(Path(a.ci).resolve(), not a.no_restamp, a.alarm)
    return census(a.file, a.since, a.until, a.alarm)


if __name__ == "__main__":
    sys.exit(main())
