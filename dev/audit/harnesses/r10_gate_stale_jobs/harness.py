#!/usr/bin/env python3
"""Finder's harness for the stale jobs listing: gate.judge over a world whose listing
catches up at a set time. python3 harness.py <tree with tools/ci> ; prints one line per shape.
Shapes carry the measured lower-bound lags of the runs they name."""
import sys
sys.path.insert(0, sys.argv[1] + "/tools/ci")
import gate as G
ENV = {"GITHUB_SHA": "M", "GITHUB_REPOSITORY": "o/r", "GITHUB_RUN_ID": "100", "GITHUB_RUN_ATTEMPT": "1"}
EV = {"action": "synchronize", "pull_request": {"number": 7, "base": {"ref": "main"}, "head": {"sha": "H"}}}
ctx = G.context("pull_request", EV, ENV)
NAMES = ["prelude"] + list(G.REQUIRED["pr-cc"])
PULL = {"state": "open", "head": {"sha": "H", "repo": {"full_name": "o/r"}}, "base": {"ref": "main"}}


def world(stale=None, absent=None, real=None):
    """stale/absent: name -> seconds until the listing shows it; real: name -> its true conclusion."""
    stale, absent, real = stale or {}, absent or {}, real or {}
    clock = [0.0]

    def get(path, params=None):
        if path.endswith("/pulls/7"):
            return 200, {}, PULL
        if path.endswith("ci.yml/runs"):
            return 200, {}, {"workflow_runs": []}
        if path.endswith("/runs/100/jobs"):
            jobs = []
            for n in NAMES:
                if clock[0] < absent.get(n, 0):
                    continue
                if clock[0] < stale.get(n, 0):
                    jobs.append({"name": n, "status": "in_progress", "conclusion": None, "id": 1})
                else:
                    jobs.append({"name": n, "status": "completed", "conclusion": real.get(n, "success"), "id": 1})
            return 200, {}, {"jobs": jobs}
        return 404, {}, None
    naps = []

    def sleep(s):
        naps.append(s)
        clock[0] += s
    return get, sleep, (lambda: clock[0]), naps


SHAPES = [
    ("41870314676 proof: mutation/closures stale >=285 s", dict(stale={"tests / mutation": 285, "tests / closures": 181}), "PASS"),
    ("41870522291 main: real red hidden, stale 171 s", dict(stale={"tests / closures": 375, "tests / mutation": 171}, real={"tests / mutation": "failure"}), "FAIL"),
    ("41876634563 prelude stale, 704 s", dict(stale={"prelude": 704}), "PASS"),
    ("41863133083 prelude stale, 134 s", dict(stale={"prelude": 134}), "PASS"),
    ("41094975103 prelude really failed, stale 357 s", dict(stale={"prelude": 357}, real={"prelude": "failure"}), "FAIL"),
    ("41289450679 pr-contract absent, 20 s", dict(absent={"pr-contract / pr-contract": 20}), "PASS"),
    ("past the bound: stale 800 s", dict(stale={"tests / closures": 800}), "FAIL"),
    ("null: fresh listing", dict(), "PASS"),
    ("null: real red, fresh listing", dict(real={"tests / closures": "failure"}), "FAIL"),
]
bad = 0
for name, kw, want in SHAPES:
    get, sleep, now, naps = world(**kw)
    out, why, _ = G.judge(ctx, {"kind": "code", "pr": "7"}, get, lambda b, h: True, sleep, now)
    ok = out.split()[0] == want
    bad += not ok
    print(f"{'ok  ' if ok else 'BAD '} want {want:4} got {out[:58]:58} waited {int(sum(naps)):4} s  {name}")
print(f"mismatches {bad} of {len(SHAPES)}")
