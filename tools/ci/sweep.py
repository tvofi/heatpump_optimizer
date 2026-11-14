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
source of ANOTHER run, below, finished; or a higher-id run's gate started while it judged,
the lagging-listing pair, of which the lower id is re-run, or the higher where the lower ended
green). A source is a job that ran: a skipped job is none, because GitHub re-stamps every
skipped job of a run at each re-run of its gate, so a stamp it carries says when a sibling's
sweep re-ran that gate, not when anything finished (R10-HOTFIX-SWEEP-SETTLE-LOOP: read as
sources, two runs at #3308's head re-ran each other's gates to attempt 39). And settle never
re-runs a gate attempt the bot started (`SWEEP_ACTOR`: this sweep's token, and refresh's) unless
a source finished after it, so it re-runs a gate at most once per source change: its re-runs
are bounded by the sources that finish, never by the arms, which looped on re-stamped skips.
A rate limit prints `RATE-LIMITED`, re-runs nothing further and exits 1: reset_epoch is
printed, a caller re-runs nothing before it.

SWEEP-SELF (R10-HOTFIX-SWEEP-TOKEN-ACTOR; dev/audit/rca/R10-RCA-SWEEP-TOKEN-ACTOR.md): GitHub
starts no workflow from an event its GITHUB_TOKEN caused, so gate-sweep.yml's `workflow_run`
never fires for a ci.yml run whose actor is the bot (a token push's approved pull_request run, a
github.token dispatch). ci.yml's `sweep-self` job (SELF_JOB, after `gate`) sweeps such a run
from inside it: the caller's GITHUB_RUN_ID is V. V is then still in_progress (its SELF_JOB runs),
so settle never waits on V itself, and a SELF_JOB is never a source. From inside V, settle never
waits on another gate still judging either (that run's own completion sweeps: SKIP, no runner
held); it does poll a run whose gate has completed and whose run has not (its own sweep-self,
seconds), as a red gate in such a run is polled on the green branch: GitHub refuses a re-run
inside a running run.

A STALE PIN is never re-run (`stale_pin`; dev/audit/rca/r10-gate-busy-defer-2.md 5.2). A
pull_request or review run's gate restores tools/ci/*.py from the event's `base.sha`, and a
job re-run replays that event, so it judges with the programs of that pin however far the
base has moved since: #3261's pair re-ran a pre-#3246 busy() ten times. Where the base
changed tools/ci/*.py after the pin, the sweep instead dispatches ONE fresh ci.yml run at the
head (`pr`, `base`: that run rev-parses origin/<base> when its job starts) and prints
`STALE-PIN`; that run's gate is the newest at the head, and its completion sweeps. A dispatched
run created after the stale gate concluded is that fresh judge already, so nothing is
dispatched twice for one red and the branch cannot loop. That run's green `gate` is a check of its
own suite and replaces no other run's red (#3400 at 7326025c: the edit run's stale red stood until
re-run by hand), so the sweep of the fresh run itself -- ci.yml's sweep-self, its actor being the
token's -- re-runs each stale red once (`fresh` returns False); the re-run's completion settles,
where V is no green judge, and is left. A dispatch whose first gate attempt was green stays that judge
after a refresh re-ran its gate red (R10-HOTFIX-SWEEP-DEFERRAL-DISPATCH, #3544: a review event re-ran it,
it deferred, and a second code run went out); its own red is re-run in place, never pinned. Nor does a
DEFERRAL red dispatch where a green gate covers the newest event (`covered_deferral`): gate() reads busy()
before any source, so a red judged while another run's source was unfinished is the deferral, no verdict,
and is re-run in place, within ATTEMPT_CAP and `settled` like any red; with nothing green (#3261's pair)
it still dispatches. This sweep runs main's copy
(gate-sweep.yml), so the countermeasure reaches every PR at once; gate.py's `refresh` runs
the pinned copy itself, which is why it lives here.

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
PINNED_EVENTS = ("pull_request", "pull_request_review")   # ci.yml's restore reads github.event.pull_request.base.sha
PINNED_PROGRAMS = "tools/ci/"                             # its pathspec 'tools/ci/*.py' (a git glob crosses '/')
SWEEP_ACTOR = "github-actions[bot]"   # gate-sweep.yml's github.token; ci.yml's refresh posts as it too
SELF_JOB = "sweep-self"               # ci.yml's job sweeping its own run from inside it (module doc)


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


def sources(jobs):
    """The jobs of a listing a gate reads as sources: never a gate, a SELF_JOB or a skipped job (module doc)."""
    return [j for j in jobs if j.get("name") not in ("gate", SELF_JOB) and j.get("conclusion") != "skipped"]


def source_after(t0, others):
    """A source of another run finished after `t0`, or has not finished."""
    return any((j.get("completed_at") or "~") > t0 for jobs in others.values() for j in sources(jobs))


def settled(run, gate, others):
    """The bot started this gate's latest attempt and no source finished after it: settle leaves it."""
    return (run.get("run_attempt", 1) > 1 and (run.get("triggering_actor") or {}).get("login") == SWEEP_ACTOR
            and not source_after(gate.get("started_at") or "", others))


def undecided(gate, run_id, others):
    """The other runs (id -> latest jobs) this gate's verdict may have deferred to: one with a
    source (`sources`) that finished after this gate started or has not finished; or a HIGHER-id
    run whose gate started while this one judged (a listing lagging that start reads the run
    busy, and busy()'s tie-break makes the lower id the one that decides, so only the lower is
    re-run); or a LOWER-id run whose gate judged while this one did and ended green (that pair
    seen from its higher side, which deferred to the decider: re-run, it starts after that gate
    concluded; a red lower is re-run by the arm before, never both). What keeps a re-run from
    being re-run again is `settled`, not these arms (module doc)."""
    t0, t1 = gate.get("started_at") or "", gate.get("completed_at") or "~"
    out = []
    for i, jobs in others.items():
        g = latest_gate(jobs) or {}
        gs, ge = g.get("started_at") or "", g.get("completed_at") or "~"
        if (source_after(t0, {i: jobs})
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
    def __init__(self, repo, get, post, out=print, sleep=time.sleep, clock=time.monotonic, caller=None):
        self.repo, self.get, self.post, self.out, self.sleep, self.clock = repo, get, post, out, sleep, clock
        self.caller = caller          # the calling run's id: V's own is sweep-self (module doc)
        self.green = None             # V, once its gate is green and covers the newest event
        self.reruns, self.rerun_ids = 0, set()
        self.pull, self.pin, self.dispatches = None, (), 0

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
        self.pull = self.j(f"pulls/{pr}")
        return self.pull["head"]["sha"] == head

    def stale_pin(self, run):
        """The base sha this run's gate restores its programs from, where the base has changed
        tools/ci/*.py since it; else None. Read once per sweep: every pull_request run at the live
        head pins the PR's base.sha (a push moves the head, a base change re-runs as an edit)."""
        if run.get("event") not in PINNED_EVENTS:
            return None
        if self.pin == ():
            base, head_repo = self.pull["base"], (self.pull["head"].get("repo") or {}).get("full_name")
            files = [] if head_repo != self.repo else self.j(f"compare/{base['sha']}...{base['ref']}").get("files") or []
            moved = len(files) >= 300 or any(f["filename"].startswith(PINNED_PROGRAMS) and f["filename"].endswith(".py")
                                             for f in files)        # a listing capped at 300 files may hide one
            self.pin = base["sha"] if moved else None
        return self.pin

    def fresh(self, run, gate, runs, pin):
        """Re-judge a stale-pinned red gate by one dispatched run at the head, unless one exists: True.
        False where V is that fresh judge and green: its check replaces no other run's red (#3400), so
        the stale gate is re-run, once, the run judging after every run here concluded; False too for a
        covered deferral, no verdict (module doc). A dispatch at
        the head that is not completed, or concluded success, is that judge whenever it was created:
        a re-run stale gate completes after it, and keying on creation re-dispatched (#3446)."""
        later = [r["id"] for r in runs if r.get("event") == "workflow_dispatch" and self.judged(r)]
        if self.green in later:
            self.out(f"STALE-PIN {pin}: run {self.green}, this head's fresh judge, is green and replaces no "
                     f"other run's red; run {run['id']}'s gate is re-run")
            return False
        if later:
            self.out(f"STALE-PIN {pin}: run {later[0]} re-judges this head with fresh programs; run {run['id']} left")
            return True
        if self.dispatches:
            self.out(f"STALE-PIN {pin}: run {run['id']} left to this sweep's dispatched run")
            return True
        if self.covered_deferral(run, gate, runs):
            self.out(f"STALE-PIN {pin}: run {run['id']}'s red is a deferral and a green gate covers the newest "
                     "event: no verdict to re-judge; re-run in place")
            return False
        base, ref = self.pull["base"]["ref"], self.pull["head"]["ref"]
        st, _, _ = self.post(f"repos/{self.repo}/actions/workflows/ci.yml/dispatches",
                             {"ref": ref, "inputs": {"pr": str(self.pull_number), "base": base}})
        self.dispatches += 1
        self.out(f"STALE-PIN {pin}: run {run['id']}'s gate restores programs older than {base}'s tools/ci; "
                 f"re-judged by a fresh run dispatched on {ref} (HTTP {st})")
        return True

    def judged(self, r):
        """A dispatch at the head is its fresh judge while not completed, green, or green at its first
        attempt (a refresh re-run red judged nothing new); an unreadable first attempt is none: dispatch."""
        if r.get("status") in NOT_COMPLETED or r.get("conclusion") == "success":
            return True
        if r.get("run_attempt", 1) < 2:
            return False
        st, _, body = self.get(f"repos/{self.repo}/actions/runs/{r['id']}/attempts/1/jobs", {"per_page": 100})
        return st == 200 and (latest_gate((body or {}).get("jobs") or []) or {}).get("conclusion") == "success"

    def covered_deferral(self, run, gate, runs):
        """A source of another run finished after this red gate started, or has not (it deferred: gate()
        reads busy() first), and a green gate at the head covers the newest event (module doc)."""
        others = {r["id"]: self.jobs_of(r["id"]) for r in runs if r["id"] != run["id"]}
        return source_after(gate.get("started_at") or "", others) and (
            self.green is not None or any(covers_newest(latest_gate(js), runs) for js in others.values()))

    def runs_at(self, head):
        runs = self.j("actions/runs", {"head_sha": head, "per_page": 100})["workflow_runs"]
        return [r for r in runs if r.get("path", "").split("@")[0] == CI_PATH]

    def judge(self, run, gate, why, runs=()):
        """Re-run a completed, not-successful gate once, if its run is idle and has attempts left;
        a stale-pinned one is re-judged by a fresh run instead (module doc)."""
        if gate.get("conclusion") == "success" or run["id"] in self.rerun_ids:
            return
        if run["status"] != "completed" or not must_rerun(gate, run["run_attempt"]):
            self.out(f"SWEEP left run {run['id']}: attempt {run['run_attempt']} at the cap, or the run still busy; push a new commit")
            return
        pin = self.stale_pin(run)
        if pin and self.fresh(run, gate, runs, pin):
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
        pr = self.pull_number = prs[0]["number"]
        runs = self.runs_at(head)
        vg = self.gate_of(run_id)
        if not covers_newest(vg, runs):
            return self.settle(run_id, pr, head)
        self.green = v["id"]
        polled = {}
        for r in sorted((r for r in runs if r["id"] != v["id"]), key=lambda r: r["id"]):
            g = self.gate_of(r["id"])
            if g and g.get("status") == "completed" and (r["status"] == "completed" or g.get("conclusion") == "success"):
                self.judge(r, g, "completed red", runs)
            elif g and g.get("status") == "completed":     # its run still busy (its sweep-self): GitHub refuses a re-run
                polled[r["id"]] = r["status"]
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
                self.judge(listing[i], self.gate_of(i), "polled, completed red", list(listing.values()))
            for i in polled:
                polled[i] = listing.get(i, {}).get("status", polled[i])
        for i, st in polled.items():
            self.out(f"SWEEP left run {i} still {st} at the {POLL_WAIT} s bound; red until the next event")
        self.out(f"SWEEP-DONE run={run_id} reruns={self.reruns} dispatches={self.dispatches}")
        return 0


    def settle(self, run_id, pr, head):
        """No green gate covers the newest event: once every gate at the head has concluded,
        re-run each red one that judged before another run's sources finished (module doc)."""
        deadline = self.clock() + POLL_WAIT
        while True:
            runs = self.runs_at(head)
            jobs = {r["id"]: self.jobs_of(r["id"]) for r in runs}
            gates = {i: latest_gate(js) or {} for i, js in jobs.items()}
            finishing = [r["id"] for r in runs if r["id"] != self.caller and (gates[r["id"]].get("status") == "in_progress"
                         or (gates[r["id"]].get("status") == "completed" and r["status"] != "completed"))]
            judging = self.caller == run_id and any(gates[i].get("status") == "in_progress" for i in finishing)
            if not finishing or judging or self.clock() + POLL_FLOOR > deadline:
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
            others = {i: js for i, js in jobs.items() if i != r["id"]}
            late = undecided(g, r["id"], others)
            if g.get("conclusion") == "success" or not late:
                continue
            if settled(r, g, others):
                self.out(f"SWEEP left run {r['id']}: attempt {r['run_attempt']}, the bot's re-run, judged after "
                         "every source finished")
                continue
            self.judge(r, g, f"judged before run(s) {late} finished", runs)
        self.out(f"SWEEP-DONE run={run_id} reruns={self.reruns} dispatches={self.dispatches}")
        return 0


def main(argv, get, post, out=print, sleep=time.sleep, clock=time.monotonic, env=None):
    env = os.environ if env is None else env
    run_id = None
    repo = env.get("GITHUB_REPOSITORY", "")
    it = iter(argv)
    for a in it:
        if a == "--run":
            run_id = next(it, None)
        elif a == "--repo":
            repo = next(it, "")
    if not run_id or not str(run_id).isdigit() or not repo:
        out("FAIL usage: --run <id> (and GITHUB_REPOSITORY or --repo)")
        return 2
    s = Sweep(repo, get, post, out, sleep, clock, caller=int(run_id) if env.get("GITHUB_RUN_ID") == str(run_id) else None)
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
