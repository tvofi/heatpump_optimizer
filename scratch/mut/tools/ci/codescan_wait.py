#!/usr/bin/env python3
"""pr-contract's code-scanning wait, then the alerts it owes (DESIGN-P2 4.3 steps 1-5; R10-CI-LAYOUT P2b, unit U6).

    python3 -I tools/ci/codescan_wait.py --pr N --base B [--base-repeats]    # one red per line on stdout
    python3 -I tools/ci/codescan_wait.py --self-test

Reads GITHUB_REPOSITORY and GITHUB_RUN_ID (the caller's run: a called workflow
shares it). Steps 1-3 here, step 4's poll here, steps 4-5's reading in
alert_list.py (`match`, `reds`), never re-implemented:
  1. S, the run whose codeql unit this verdict covers: this run when its title's
     workset owns codeql, else the newest other run at this head that names this
     PR and the PR's live base, owns codeql, and whose codeql jobs have all
     completed (gate.py's source rule). None yet is polled for as step 4
     polls, under the same bound: an edit run starts while its code run's
     codeql unit is still analysing (#2675).
  2. The legs S uploaded: each `codeql / Analyze (<leg>)` job whose step "Perform
     CodeQL Analysis" concluded success (a scope stand-down skips it).
  3. M, S's `sha=` token; R, refs/pull/<N>/merge when S's event is pull_request,
     else refs/heads/<S's head_branch>.
  4. Poll `match` every POLL_S (the 60 s floor on a GitHub poll, tvofi 2026-10-19)
     until every uploaded leg has its analysis at M; WAIT_MAX_S bounds the whole
     wait, and an absent analysis at the bound FAILs.
  5. `alert_list.reds`: the open alerts of those analyses.
Exit 0 with the reds on stdout; 1 with `FAIL closed: <why>` (a rate limit included)
on stderr, so the job log shows it while stdout goes to the alert file.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))                      # -I drops the script's directory
import alert_list  # noqa: E402
import ghapi  # noqa: E402
from gate import UNITS  # noqa: E402
from prelude import parse_title, title_sha, workset  # noqa: E402

POLL_S = 60
WAIT_MAX_S = 600
STEP = "Perform CodeQL Analysis"
CODEQL = tuple(f"codeql / {n}" for n in UNITS["codeql"])


class Fail(Exception):
    pass


def _get(get, path, what):
    st, _, doc = get(path)
    if st != 200 or not isinstance(doc, dict):
        raise Fail(f"{what}: HTTP {st}")
    return doc


def _jobs(get, repo, run_id):
    return ghapi.paginate(f"repos/{repo}/actions/runs/{run_id}/jobs", {"filter": "latest"}, get=get)


def owns_codeql(run, pr):
    t = parse_title(run.get("display_title") or "")
    return t is not None and "codeql" in workset(t[0], t[1]) and t[1] == pr


def source(get, repo, run_id, pr, base, stop, sleep=time.sleep, now=time.monotonic):
    """(S's run object, S's jobs): step 1, polled until `stop`."""
    me = _get(get, f"repos/{repo}/actions/runs/{run_id}", "this run")
    if owns_codeql(me, pr):
        return me, _jobs(get, repo, me["id"])
    if pr:
        base = _get(get, f"repos/{repo}/pulls/{pr}", f"pull request {pr}")["base"]["ref"]
    while True:
        runs = ghapi.paginate(f"repos/{repo}/actions/workflows/ci.yml/runs", {"head_sha": me["head_sha"]}, get=get)
        for r in sorted(runs, key=lambda r: r["id"], reverse=True):
            t = parse_title(r.get("display_title") or "")
            if r["id"] == me["id"] or r["status"] == "action_required" or t is None or t[2] != base or not owns_codeql(r, pr):
                continue
            jobs = _jobs(get, repo, r["id"])
            done = {j["name"]: j["status"] for j in jobs}
            if all(done.get(n) == "completed" for n in CODEQL):
                return r, jobs
        if now() + POLL_S > stop:
            raise Fail(f"no run at this head owns a finished codeql unit for base {base!r} after {WAIT_MAX_S} s")
        sleep(POLL_S)


def legs_uploaded(jobs):
    """Step 2."""
    out = []
    for j in jobs:
        name = j["name"]
        if name in CODEQL and any(s["name"] == STEP and s["conclusion"] == "success" for s in j.get("steps") or []):
            out.append(name[name.index("(") + 1:-1])
    return sorted(out)


def wait(get, ref, sha, legs, stop, sleep=time.sleep, now=time.monotonic):
    """Step 4: poll until every uploaded leg has its analysis at (ref, sha)."""
    while True:
        missing = [x for x in legs if x not in alert_list.match(get, ref, sha, legs)]
        if not missing:
            return
        if now() + POLL_S > stop:
            raise Fail(f"no analysis at {ref} with commit_sha {sha} for leg(s) {', '.join(missing)} after {WAIT_MAX_S} s")
        sleep(POLL_S)


def run(get, repo, run_id, pr, base, base_repeats, sleep=time.sleep, now=time.monotonic):
    kw = dict(sleep=sleep, now=now)
    stop = now() + WAIT_MAX_S                      # one bound over steps 1 and 4
    s, jobs = source(get, repo, run_id, pr, base, stop, **kw)
    legs = legs_uploaded(jobs)
    sha = title_sha(s.get("display_title") or "")
    if not sha:
        raise Fail(f"run {s['id']}: its title carries no sha=")
    ref = f"refs/pull/{pr}/merge" if s["event"] == "pull_request" else f"refs/heads/{s['head_branch']}"
    rel = alert_list.bind(get, repo)
    wait(rel, ref, sha, legs, stop, **kw)
    ok, got = alert_list.reds(rel, ref, sha, legs, base, base_repeats)
    if not ok:
        raise Fail(got.removeprefix("FAIL closed: "))
    return got


def main(argv, get=ghapi.get, env=os.environ, **kw):
    ap = argparse.ArgumentParser(prog="codescan_wait.py")
    ap.add_argument("--pr", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--base-repeats", action="store_true")
    a = ap.parse_args(argv)
    try:
        got = run(get, env["GITHUB_REPOSITORY"], env["GITHUB_RUN_ID"], a.pr, a.base, a.base_repeats, **kw)
    except Fail as e:
        print(f"FAIL closed: {e}", file=sys.stderr)
        return 1
    except (ghapi.RateLimited, ghapi.ApiError, KeyError) as e:
        print(f"FAIL closed: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    print("\n".join(got))
    return 0


# ---- the self-test: the ported step over alert_list's own fixtures ------------------------
def self_test() -> int:
    A = alert_list
    repo, pr, head = "o/r", "77", "H"
    ev = dict(display_title=f"CI code pr={pr} base=main sha={A.M}", head_sha=head, event="pull_request", head_branch="b")
    edit = dict(id=200, display_title=f"CI edit pr={pr} base=main sha=e1", head_sha=head, status="in_progress", event="pull_request")
    code = dict(ev, id=100, status="completed")
    steps = lambda ok: [{"name": STEP, "conclusion": "success" if ok else "skipped"}]       # noqa: E731

    def jobs(skip=()):
        return [{"name": n, "status": "completed", "steps": steps(n.split("(")[1][:-1] not in skip)} for n in CODEQL]

    def world(analyses, sarifs, alerts, runs=None, run_jobs=None, at=A.R, **kw):
        inner = A.world(analyses, sarifs, alerts, **kw)
        runs = {100: code, 200: edit, **(runs or {})}
        run_jobs = run_jobs or {100: jobs()}

        def get(path, params=None, headers=None):
            tail = path.removeprefix(f"repos/{repo}/")
            if tail.startswith("actions/runs/") and tail.endswith("/jobs"):
                rid = int(tail.split("/")[2])
                return (200, {}, {"jobs": run_jobs[rid]}) if rid in run_jobs else (404, {}, None)
            if tail.startswith("actions/runs/"):
                r = runs.get(int(tail.rsplit("/", 1)[1]))
                return (200, {}, r) if r else (404, {}, None)
            if tail == "actions/workflows/ci.yml/runs":
                return 200, {}, {"workflow_runs": [r for r in runs.values() if r["head_sha"] == (params or {})["head_sha"]]}
            if tail == f"pulls/{pr}":
                return 200, {}, {"base": {"ref": "main"}}
            if tail == A.LISTING and (params or {}).get("ref") != at:
                return 200, {}, []                   # an analysis is listed only under the ref it was uploaded to
            return inner(tail, params, headers)
        return get

    n = bad = 0

    def check(label, good, detail=""):
        nonlocal n, bad
        n += 1
        bad += not good
        print(f"{'ok ' if good else 'BAD'} {label}{detail}")

    plant = {13: A.sarif((7, A.PLANT)), **A.EMPTY}
    one = [f"code-scanning alert 7 ({A.PLANT})"]
    live = [A.alert(7, A.PLANT, "open")]
    nosleep = dict(sleep=lambda s: None)

    def go(get, run_id=100, **kw):
        try:                                       # a bounded clock: a mutant that never finds an analysis ends, not hangs
            return run(get, repo, run_id, pr, "main", False, **{"now": iter(range(0, 10_000, 100)).__next__}, **nosleep, **kw)
        except Fail as e:
            return f"FAIL {e}"

    check("1 the plant: a code run lists the python-only alert", go(world(A.THREE, plant, live)) == one)
    check("2 null: the same run without the plant lists nothing", go(world(A.THREE, {13: A.sarif(), **A.EMPTY}, [])) == [])
    check("3 carried: an edit run takes S from the code run and lists the same alert", go(world(A.THREE, plant, live), 200) == one)
    check("4 a leg that stood down uploaded nothing: not waited for, not read",
          go(world(A.THREE[1:], A.EMPTY, [], run_jobs={100: jobs(skip=("python",))})) == [])
    check("5 case 7: an analysis id answering 404 FAILs closed", str(go(world(A.THREE, A.EMPTY, live))).startswith("FAIL "))
    check("6 no finished codeql unit at this head for an edit run FAILs",
          str(go(world(A.THREE, plant, live, runs={100: dict(code, status="in_progress")},
                       run_jobs={100: [dict(j, status="in_progress") for j in jobs()]}), 200)).startswith("FAIL no run"))
    check("7 a code run of another base is no source",
          str(go(world(A.THREE, plant, live, runs={100: dict(code, display_title=code["display_title"].replace("base=main", "base=dev"))}), 200)
              ).startswith("FAIL no run"))
    check("8 an uploaded leg with no analysis at the bound FAILs", str(go(world(A.THREE[1:], A.EMPTY, []))).startswith("FAIL no analysis"))
    naps = []

    def lagging(path, params=None, headers=None):
        return world(A.THREE if len(naps) >= 2 else A.THREE[1:], plant, live)(path, params, headers)

    check("9 a leg whose analysis lands late is waited for at the 60 s poll, then listed",
          run(lagging, repo, 100, pr, "main", False, sleep=naps.append, now=iter(range(0, 10_000, 1)).__next__) == one and naps == [POLL_S, POLL_S])
    check("10 the poll is the 60 s floor", POLL_S >= 60)
    disp = dict(code, event="workflow_dispatch", head_branch="bot/x")
    check("11 a dispatch source is read at refs/heads/<its branch>, and not found at the merge ref (null)",
          go(world(A.THREE, plant, live, runs={100: disp}, at="refs/heads/bot/x")) == one
          and str(go(world(A.THREE, plant, live, runs={100: disp}, at=A.R))).startswith("FAIL no analysis"))

    def limited(path, params=None, headers=None):
        raise ghapi.RateLimited(path, 1, "limit")

    env = {"GITHUB_REPOSITORY": repo, "GITHUB_RUN_ID": "100"}
    check("12 main: a rate limit FAILs closed, rc 1", main(["--pr", pr, "--base", "main"], get=limited, env=env) == 1)
    check("13 null: main on the plant exits 0", main(["--pr", pr, "--base", "main"], get=world(A.THREE, plant, live), env=env) == 0)
    reads = []

    def finishing(path, params=None, headers=None):
        if path.endswith("/runs/100/jobs"):
            reads.append(path)
        done = len(reads) > 2                      # the code run's codeql unit completes on the third read
        return world(A.THREE, plant, live, runs={100: dict(code, status="completed" if done else "in_progress")},
                     run_jobs={100: jobs() if done else [dict(j, status="in_progress") for j in jobs()]})(path, params, headers)

    naps = []
    try:
        got = run(finishing, repo, 200, pr, "main", False, sleep=naps.append, now=iter(range(0, 10_000, 1)).__next__)
    except Fail as e:
        got = f"FAIL {e}"
    check("14 an edit run whose code run's codeql unit is still running waits at the 60 s poll, then lists (#2675)",
          got == one and naps == [POLL_S, POLL_S], f" (got {got!r}, slept {naps})")
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = main(["--pr", pr, "--base", "main"], get=limited, env=env)
    check("15 the FAIL line is on stderr, where the job log shows it, and stdout (the alert file) is empty",
          rc == 1 and err.getvalue().startswith("FAIL closed: ") and out.getvalue() == "", f" (stdout {out.getvalue()!r})")
    out, err = io.StringIO(), io.StringIO()
    still = world(A.THREE, plant, live, runs={100: dict(code, status="in_progress")},
                  run_jobs={100: [dict(j, status="in_progress") for j in jobs()]})
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = main(["--pr", pr, "--base", "main"], get=still, env=dict(env, GITHUB_RUN_ID="200"),
                  sleep=lambda s: None, now=iter(range(0, 10_000, 100)).__next__)
    check("16 a refusal of the wait itself is on stderr too, stdout empty",
          rc == 1 and err.getvalue().startswith("FAIL closed: no run") and out.getvalue() == "", f" (stdout {out.getvalue()!r})")
    clock = [0]
    reads.clear()

    def late_then_absent(path, params=None, headers=None):    # the unit finishes at 540 s; no analysis ever lands
        if path.endswith("/runs/100/jobs"):
            reads.append(path)
        done = clock[0] >= 540
        return world(A.THREE[1:], A.EMPTY, [], runs={100: dict(code, status="completed" if done else "in_progress")},
                     run_jobs={100: jobs() if done else [dict(j, status="in_progress") for j in jobs()]})(path, params, headers)
    try:
        got = run(late_then_absent, repo, 200, pr, "main", False,
                  sleep=lambda s: clock.__setitem__(0, clock[0] + s), now=lambda: clock[0])
    except Fail as e:
        got = f"FAIL {e}"
    check("17 WAIT_MAX_S bounds steps 1 and 4 together, not each", str(got).startswith("FAIL no analysis")
          and clock[0] <= WAIT_MAX_S, f" (waited {clock[0]} s: {got!r})")
    print(f"codescan_wait self-test: {n} checks, {bad} failed")
    return 1 if bad else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(self_test())
    sys.exit(main(sys.argv[1:]))
