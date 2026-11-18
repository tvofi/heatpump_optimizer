#!/usr/bin/env python3
"""The probe's sweep driver: starts `gate.py --sweep --run <id>` where `workflow_run` cannot.

DESIGN-P2.md section 10 (R4-2), N5-1. `gate-sweep.yml` fires only from the default branch, so
on a probe PR a seat runs this beside it, with its own token. It only READS (`gh api`, GET):
the child's re-runs are the only writes. Every POLL s (never under 60, tvofi 2026-10-19) it
lists the PR's `ci.yml` runs at the live head and, per run, reads each attempt up to
`run_attempt` it has not yet swept (N5-1: attempts, not status transitions, since the next
attempt may be running when a poll looks). A completed attempt starts one concurrent child:
only attempt 1 under --nochain, every attempt under --chain. An attempt first seen already
superseded is logged `superseded=1`. One log line per sweep, when its child ends.
Before each poll it reads /rate_limit and backs off below 20 % remaining, and on any 403
(A1 item 5). Exits once every run is completed, no child lives and 900 s passed without a
completion.

    python3 tools/audit/seat/sweep_driver.py --repo O/R --pr N --nochain|--chain \
        [--gate <tree>/tools/ci/gate.py] [--poll 60] [--idle 900]
    python3 tools/audit/seat/sweep_driver.py --self-test
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

POLL_FLOOR, IDLE_S, LOW_FRACTION = 60, 900, 0.20
CI_PATH = ".github/workflows/ci.yml"


class Backoff(Exception):
    def __init__(self, wait, why):
        super().__init__(why)
        self.wait, self.why = wait, why


def gh_get(path, run=subprocess.run):
    """`gh api -i <path>` (a GET: no method or field flag exists in this command) -> (status, headers, json)."""
    p = run(["gh", "api", "-i", path], capture_output=True, text=True)
    head, _, body = p.stdout.partition("\r\n\r\n") if "\r\n\r\n" in p.stdout else p.stdout.partition("\n\n")
    lines = head.splitlines()
    status = int(lines[0].split()[1]) if lines and lines[0].startswith("HTTP") else 0
    headers = {k.lower(): v.strip() for k, _, v in (x.partition(":") for x in lines[1:])}
    try:
        return status, headers, json.loads(body)
    except ValueError:
        return status, headers, {}


def spawn(argv, env=None):
    return subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)


def child_env(repo, environ=os.environ, run=subprocess.run):
    """The child's environment. `gate.py --sweep` hands sweep.main `--run <id>` alone, and
    ghapi reads GITHUB_TOKEN or GH_TOKEN, so off Actions the repository and the token reach
    the child only here: GITHUB_REPOSITORY is the driver's --repo, and the seat's `gh` token
    is taken once when neither variable is set."""
    env = dict(environ, GITHUB_REPOSITORY=repo)
    if not (env.get("GITHUB_TOKEN") or env.get("GH_TOKEN")):
        p = run(["gh", "auth", "token"], capture_output=True, text=True)
        if p.returncode == 0 and p.stdout.strip():
            env["GH_TOKEN"] = p.stdout.strip()
    return env


class Driver:
    def __init__(self, repo, pr, gate, chain, gh=gh_get, spawn=spawn, out=print, sleep=time.sleep,
                 clock=time.time, poll=POLL_FLOOR, idle=IDLE_S, env=None):
        if poll < POLL_FLOOR:
            raise SystemExit(f"--poll {poll}: refused, the floor is {POLL_FLOOR} s")
        self.repo, self.pr, self.gate, self.chain, self.gh, self.spawn = repo, pr, gate, chain, gh, spawn
        self.out, self.sleep, self.clock, self.poll, self.idle = out, sleep, clock, poll, idle
        self.swept, self.children, self.last = set(), [], clock()
        self.env = child_env(repo, os.environ if env is None else env)  # env: the base environment

    def get(self, path):
        status, headers, body = self.gh(f"repos/{self.repo}/{path}")
        if status in (403, 429):
            reset = int(headers.get("x-ratelimit-reset", 0) or 0)
            raise Backoff(max(self.poll, reset - self.clock()), f"{status} on {path}")
        if status != 200:
            raise RuntimeError(f"GET {path}: {status}")
        return body

    def rate_ok(self):
        status, _, body = self.gh("rate_limit")
        if status in (403, 429):
            raise Backoff(self.poll, f"{status} on /rate_limit")
        core = body.get("resources", {}).get("core", {})
        if status == 200 and core.get("limit") and core["remaining"] < LOW_FRACTION * core["limit"]:
            raise Backoff(max(self.poll, core["reset"] - self.clock()), f"rate limit {core['remaining']}/{core['limit']}")

    def start(self, run, n, att, superseded):
        argv = [sys.executable, "-I", self.gate, "--sweep", "--run", str(run["id"])]
        self.children.append((self.spawn(argv, self.env), run["id"], n, att.get("updated_at"), self.clock(), superseded))
        self.last = self.clock()

    def look(self):
        """One poll: list the runs at the live head, start a sweep for each unswept completed attempt."""
        self.rate_ok()
        head = self.get(f"pulls/{self.pr}")["head"]["sha"]
        runs = [r for r in self.get(f"actions/runs?head_sha={head}&per_page=100")["workflow_runs"]
                if r.get("path", "").split("@")[0] == CI_PATH]
        for run in runs:
            for n in range(1, run["run_attempt"] + 1):
                if (run["id"], n) in self.swept:
                    continue
                if n > 1 and not self.chain:
                    self.swept.add((run["id"], n))
                    continue
                att = self.get(f"actions/runs/{run['id']}/attempts/{n}")
                if att.get("status") == "completed":
                    self.swept.add((run["id"], n))
                    self.start(run, n, att, n < run["run_attempt"])
        return all(r["status"] == "completed" for r in runs)

    def reap(self):
        for c in list(self.children):
            proc, rid, n, done_at, t0, sup = c
            if proc.poll() is None:
                continue
            self.children.remove(c)
            text = " | ".join((proc.stdout.read() or "").split("\n")).strip(" |")
            self.out(f"SWEEP run={rid} attempt={n} completed_at={done_at} started={int(t0)} "
                     f"superseded={int(sup)} rc={proc.returncode} :: {text}")

    def loop(self):
        while True:
            try:
                all_done = self.look()
            except Backoff as b:
                self.out(f"BACKOFF {b.wait:.0f}s: {b.why}")
                self.sleep(b.wait)
                continue
            self.reap()
            if all_done and not self.children and self.clock() - self.last >= self.idle:
                self.out("IDLE-EXIT: every run completed, no sweep alive, nothing new for the idle bound")
                return 0
            self.sleep(self.poll)


def main(argv):
    if argv == ["--self-test"]:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import sweep_driver_selftest
        return sweep_driver_selftest.run_self()
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pr", type=int, required=True)
    arm = ap.add_mutually_exclusive_group(required=True)
    arm.add_argument("--chain", action="store_true")
    arm.add_argument("--nochain", action="store_true")
    ap.add_argument("--gate", default="tools/ci/gate.py")
    ap.add_argument("--poll", type=int, default=POLL_FLOOR)
    ap.add_argument("--idle", type=int, default=IDLE_S)
    a = ap.parse_args(argv)
    return Driver(a.repo, a.pr, a.gate, a.chain, poll=a.poll, idle=a.idle).loop()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
