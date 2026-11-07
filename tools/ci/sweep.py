#!/usr/bin/env python3
"""`gate.py --sweep --run <id>`: re-judge the other red `gate` jobs at a head once one is green.

DESIGN-P2.md 4.3 items 1 and 4. Run for a `CI` completion V; acts only when V's latest
`gate` is green at the PR's LIVE head and covers the newest event (V's gate started
after every run at the head was created). Then, for every OTHER `ci.yml` run at the head,
lower or higher id (an id orders nothing: GitHub numbers a same-second push and body edit
out of order, and prelude.waits_on makes the higher-id code run's gate the one that waits):
  - its latest `gate` completed and not `success` -> re-run that `gate` job;
  - its `gate` attempt requested and not completed (N5-4: queued, waiting, pending,
    requested, in_progress) -> poll, and re-run it if it completes red.
Never the triggering run, never a green one, never past attempt 45 (N2: the sweep leaves a
run at 44 alone), each polled run re-run at most once. The poll lists runs ONCE per
poll for all of them, no faster than 60 s (tvofi 2026-10-19), for at most 600 s.

Where no green gate covers the newest event (`settle`, r10-gate-busy-defer-3): a gate defers at
once and holds no runner (gate.judge), so a deferral nothing green follows -- two gates that
deferred to each other, or a decider that ended red or cancelled -- would stay red. Once every
gate at the head has concluded (in_progress gates polled as above), every red gate, V's own
included, that may have judged an undecided head is re-run (`undecided`: it started before a
job of ANOTHER run, its gate aside, finished; or a higher-id run's gate started while it judged,
the lagging-listing pair, of which the lower id is re-run, or the higher where the lower ended
green). A re-run judges after every such job
finished and beside no gate starting, so it is never re-run again: the branch cannot loop.
A rate limit prints `RATE-LIMITED`, re-runs nothing further and exits 1: reset_epoch is
printed, a caller re-runs nothing before it.

Pure decision code over JSON: `get(path, params=None)` and `post(path, body=None)` are
injected and return (status, headers, json) as ghapi's do. RateLimited is ghapi's, matched
by name so a program run with `-I` needs no import of it.

    python3 tools/ci/sweep.py --self-test
"""
from __future__ import annotations

import os
import sys
import time

ATTEMPT_CAP = 45          # GitHub fails a run's 51st attempt; the sweep never takes one to 45
POLL_FLOOR, POLL_WAIT = 60, 600
NOT_COMPLETED = ("queued", "waiting", "pending", "requested", "in_progress")  # N5-4
CI_PATH = ".github/workflows/ci.yml"


class RateLimited(Exception):
    """Shim with ghapi.RateLimited's name and field; the real one propagates the same way."""

    def __init__(self, reset_epoch=0):
        super().__init__(f"rate limit exceeded, resets {reset_epoch}")
        self.reset_epoch = reset_epoch


def _is_rate_limited(exc):
    return type(exc).__name__ == "RateLimited"


def latest_gate(jobs):
    """The `gate` job of a `filter=latest` jobs listing, or None."""
    return next((j for j in jobs if j.get("name") == "gate"), None)


def undecided(gate, run_id, others):
    """The other runs (id -> latest jobs) this gate's verdict may have deferred to: one with a job,
    its gate aside, that finished after this gate started or has not finished (a source it could
    not read); or a HIGHER-id run whose gate started while this one judged (a listing lagging
    that start reads the run busy, and busy()'s tie-break makes the lower id the one that
    decides, so only the lower is re-run: re-judged, it is final, and nothing loops); or a
    LOWER-id run whose gate judged while this one did and ended green (that pair seen from its
    higher side, which deferred to the decider: re-run, it starts after that gate concluded, so
    it is final; a red lower is re-run by the arm before, never both, so nothing loops)."""
    t0, t1 = gate.get("started_at") or "", gate.get("completed_at") or "~"
    out = []
    for i, jobs in others.items():
        g = latest_gate(jobs) or {}
        gs, ge = g.get("started_at") or "", g.get("completed_at") or "~"
        if (any(j.get("name") != "gate" and (j.get("completed_at") or "~") > t0 for j in jobs)
                or (i > run_id and t0 <= gs <= t1)
                or (i < run_id and g.get("conclusion") == "success" and gs <= t1 and ge >= t0)):
            out.append(i)
    return sorted(out)


def covers_newest(v_gate, runs):
    """V's latest gate is green and completed and started after every run at the head was created."""
    return bool(v_gate and v_gate.get("status") == "completed" and v_gate.get("conclusion") == "success"
                and v_gate.get("started_at", "") >= max(r["created_at"] for r in runs))


def must_rerun(gate, attempt):
    """A completed, not-successful latest gate that has attempts left (N2): re-run it."""
    return bool(gate and gate.get("status") == "completed" and gate.get("conclusion") != "success"
                and attempt < ATTEMPT_CAP - 1)


def pollable(gate):
    """A gate attempt requested and not completed (N5-4)."""
    return bool(gate and gate.get("status") in NOT_COMPLETED)


class Sweep:
    def __init__(self, repo, get, post, out=print, sleep=time.sleep, clock=time.monotonic):
        self.repo, self.get, self.post, self.out, self.sleep, self.clock = repo, get, post, out, sleep, clock
        self.reruns, self.rerun_ids = 0, set()

    def j(self, path, params=None):
        status, _, body = self.get(f"repos/{self.repo}/{path}", params)
        if status != 200:
            raise RuntimeError(f"GET {path}: {status}")
        return body

    def jobs_of(self, run_id):
        return self.j(f"actions/runs/{run_id}/jobs", {"filter": "latest", "per_page": 100})["jobs"]

    def gate_of(self, run_id):
        return latest_gate(self.jobs_of(run_id))

    def live(self, pr, head):
        return self.j(f"pulls/{pr}")["head"]["sha"] == head

    def runs_at(self, head):
        runs = self.j("actions/runs", {"head_sha": head, "per_page": 100})["workflow_runs"]
        return [r for r in runs if r.get("path", "").split("@")[0] == CI_PATH]

    def judge(self, run, gate, why):
        """Re-run a completed, not-successful gate once, if its run is idle and has attempts left."""
        if gate.get("conclusion") == "success" or run["id"] in self.rerun_ids:
            return
        if run["status"] != "completed" or not must_rerun(gate, run["run_attempt"]):
            self.out(f"SWEEP left run {run['id']}: attempt {run['run_attempt']} at the cap, or the run still busy; push a new commit")
            return
        self.rerun_ids.add(run["id"])
        self.post(f"repos/{self.repo}/actions/jobs/{gate['id']}/rerun")
        self.reruns += 1
        self.out(f"SWEEP re-ran gate of run {run['id']} (attempt {run['run_attempt']}, {why})")

    def run(self, run_id):
        v = self.j(f"actions/runs/{run_id}")
        prs = v.get("pull_requests") or []
        head = v["head_sha"]
        if not prs or not self.live(prs[0]["number"], head):
            self.out(f"SKIP run {run_id}: no pull request, or its head is no longer the PR's live head")
            return 0
        pr = prs[0]["number"]
        runs = self.runs_at(head)
        vg = self.gate_of(run_id)
        if not covers_newest(vg, runs):
            return self.settle(run_id, pr, head)
        polled = {}
        for r in sorted((r for r in runs if r["id"] != v["id"]), key=lambda r: r["id"]):
            g = self.gate_of(r["id"])
            if g and g.get("status") == "completed":
                self.judge(r, g, "completed red")
            elif pollable(g):
                polled[r["id"]] = r["status"]
        deadline = self.clock() + POLL_WAIT
        while polled and self.clock() + POLL_FLOOR <= deadline:
            self.sleep(POLL_FLOOR)
            listing = {r["id"]: r for r in self.runs_at(head)}       # ONE listing per poll
            done = [i for i in polled if listing.get(i, {}).get("status") == "completed"]
            if done and not (self.live(pr, head) and covers_newest(self.gate_of(run_id), list(listing.values()))):
                self.out(f"SWEEP stop: head moved or run {run_id} re-judged; the newer run's sweep owns the rest")
                return 0
            for i in done:
                del polled[i]
                self.judge(listing[i], self.gate_of(i), "polled, completed red")
            for i in polled:
                polled[i] = listing.get(i, {}).get("status", polled[i])
        for i, st in polled.items():
            self.out(f"SWEEP left run {i} still {st} at the {POLL_WAIT} s bound; red until the next event")
        self.out(f"SWEEP-DONE run={run_id} reruns={self.reruns}")
        return 0


    def settle(self, run_id, pr, head):
        """No green gate covers the newest event: once every gate at the head has concluded,
        re-run each red one that judged before another run's sources finished (module doc)."""
        deadline = self.clock() + POLL_WAIT
        while True:
            runs = self.runs_at(head)
            jobs = {r["id"]: self.jobs_of(r["id"]) for r in runs}
            gates = {i: latest_gate(js) or {} for i, js in jobs.items()}
            finishing = [r["id"] for r in runs if gates[r["id"]].get("status") == "in_progress"
                         or (gates[r["id"]].get("status") == "completed" and r["status"] != "completed")]
            if not finishing or self.clock() + POLL_FLOOR > deadline:
                break
            self.sleep(POLL_FLOOR)
            if not self.live(pr, head):
                self.out(f"SWEEP stop: head moved while run {run_id}'s settle polled; the newer run's sweep owns the rest")
                return 0
        unconcluded = sorted(i for i, g in gates.items() if g.get("status") != "completed")
        if unconcluded:
            self.out(f"SKIP run {run_id}: its gate is not green and newest-covering, and run(s) {unconcluded} have "
                     "not concluded their gate; their completion sweeps")
            return 0
        for r in sorted(runs, key=lambda r: r["id"]):
            g = gates[r["id"]]
            late = undecided(g, r["id"], {i: js for i, js in jobs.items() if i != r["id"]})
            if g.get("conclusion") != "success" and late:
                self.judge(r, g, f"judged before run(s) {late} finished")
        self.out(f"SWEEP-DONE run={run_id} reruns={self.reruns}")
        return 0


def main(argv, get, post, out=print, sleep=time.sleep, clock=time.monotonic):
    run_id = None
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    it = iter(argv)
    for a in it:
        if a == "--run":
            run_id = next(it, None)
        elif a == "--repo":
            repo = next(it, "")
    if not run_id or not str(run_id).isdigit() or not repo:
        out("FAIL usage: --run <id> (and GITHUB_REPOSITORY or --repo)")
        return 2
    s = Sweep(repo, get, post, out, sleep, clock)
    try:
        return s.run(int(run_id))
    except Exception as exc:  # noqa: BLE001 - a rate limit is told apart by name below
        if not _is_rate_limited(exc):
            raise
        out(f"RATE-LIMITED reset_epoch={getattr(exc, 'reset_epoch', 0)}; no further re-runs before it")
        return 1


if __name__ == "__main__":
    if sys.argv[1:] != ["--self-test"]:
        sys.exit("sweep.py runs as `gate.py --sweep --run <id>`; here only --self-test")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import sweep_selftest
    sys.exit(sweep_selftest.run_self())
