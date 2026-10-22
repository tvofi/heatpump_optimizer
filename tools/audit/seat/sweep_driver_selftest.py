"""sweep_driver.py's self-test: the driver over a fake `gh api`, a fake clock and fake children."""
from __future__ import annotations

import io
import re

import sweep_driver as D


class Proc:
    def __init__(self, argv):
        self.argv, self.returncode, self.stdout = argv, 0, io.StringIO("SWEEP-DONE reruns=0\n")

    def poll(self):
        return 0


class World:
    """runs: {id: [attempt_count, [statuses per attempt]]}; `limit`/`s403` script the rate limit."""

    def __init__(self, runs, limit=(5000, 5000), s403=0):
        self.runs, self.limit, self.s403, self.t, self.sleeps = runs, limit, s403, 1000.0, []
        self.calls, self.spawned, self.out = [], [], []

    def gh(self, path):
        self.calls.append(path)
        if path == "rate_limit":
            return 200, {}, {"resources": {"core": {"limit": self.limit[1], "remaining": self.limit[0], "reset": self.t + 300}}}
        if self.s403 and path.startswith("repos/"):
            self.s403 -= 1
            return 403, {"x-ratelimit-reset": str(int(self.t + 200))}, {"message": "API rate limit exceeded"}
        if "/pulls/" in path:
            return 200, {}, {"head": {"sha": "H"}}
        if "/attempts/" in path:
            rid, n = map(int, re.search(r"runs/(\d+)/attempts/(\d+)", path).groups())
            return 200, {}, {"status": self.runs[rid][1][n - 1], "updated_at": f"t{rid}.{n}"}
        runs = [{"id": i, "path": D.CI_PATH, "run_attempt": len(v[1]), "status": v[1][-1]} for i, v in self.runs.items()]
        return 200, {}, {"workflow_runs": runs + [{"id": 99, "path": ".github/workflows/other.yml", "run_attempt": 1, "status": "completed"}]}

    def sleep(self, s):
        self.sleeps.append(s)
        self.t += s

    def spawn(self, argv):
        self.spawned.append(argv)
        return Proc(argv)

    def driver(self, chain, **kw):
        return D.Driver("o/r", 7, "tree/tools/ci/gate.py", chain, self.gh, self.spawn, self.out.append,
                        self.sleep, lambda: self.t, **kw)


def run_checks():
    checks = []

    def ok(name, cond):
        checks.append((name, bool(cond)))

    done = lambda *a: ["completed"] * a[0]  # noqa: E731
    for chain, want in ((False, [1]), (True, [1, 2, 3])):
        w = World({5: [3, done(3)]})
        d = w.driver(chain)
        d.look(), d.reap()
        arm = "--chain" if chain else "--nochain"
        ok(f"{arm} sweeps attempt(s) {want}", len(w.spawned) == len(want))
        ok(f"{arm} logs attempts first seen already superseded", sum("superseded=1" in x for x in w.out) == (2 if chain else 1))
    w = World({5: [2, ["completed", "in_progress"]]})
    d = w.driver(True)
    d.look(), d.look()
    ok("an attempt still running is not swept, and an attempt is swept once", len(w.spawned) == 1)
    w = World({5: [1, ["completed"]]})
    d = w.driver(False)
    d.look()
    ok("the child is `python3 -I <tree>/gate.py --sweep --run <id>`",
       w.spawned[0][1:] == ["-I", "tree/tools/ci/gate.py", "--sweep", "--run", "5"] and "other" not in " ".join(w.calls))
    ok("the driver only reads: no call but a path to `gh api` GET", all(not c.startswith(("-", "POST")) for c in w.calls))
    cmd = []
    D.gh_get("repos/o/r/pulls/7", run=lambda a, **k: (cmd.append(a), type("P", (), {"stdout": "HTTP/2.0 200 OK\n\n{}"}))[1])
    ok("gh_get issues a plain `gh api -i <path>` (no method or field flags)", cmd == [["gh", "api", "-i", "repos/o/r/pulls/7"]])
    try:
        w.driver(False, poll=5)
        ok("a poll under 60 s is refused", False)
    except SystemExit:
        ok("a poll under 60 s is refused", True)
    w = World({5: [1, ["completed"]]}, s403=1)
    d = w.driver(False)
    try:
        d.look()
        ok("a 403 backs off and starts no sweep", False)
    except D.Backoff as b:
        ok("a 403 backs off to the reset and starts no sweep", w.spawned == [] and b.wait >= 60)
    w = World({5: [1, ["completed"]]})
    w.driver(False).look()
    ok("null: with no 403 the same completion IS swept", len(w.spawned) == 1)
    w = World({5: [1, ["completed"]]}, limit=(900, 5000))
    try:
        w.driver(False).look()
        ok("below 20 % remaining nothing is listed", False)
    except D.Backoff:
        ok("below 20 % remaining nothing is listed", w.spawned == [] and not any("actions/runs" in c for c in w.calls))
    w = World({5: [1, ["completed"]]})
    d = w.driver(False)
    rc = d.loop()
    ok("it exits after 900 s without a completion, every run completed and no child alive",
       rc == 0 and w.t - 1000 >= 900 and any("IDLE-EXIT" in x for x in w.out) and len(w.spawned) == 1)
    ok("every sleep is at least the 60 s floor", min(w.sleeps) >= 60)
    w = World({5: [1, ["in_progress"]]})
    real = w.sleep
    w.sleep = lambda s: (_ for _ in ()).throw(KeyboardInterrupt) if w.t > 1000 + 5000 else real(s)
    d = w.driver(False)
    try:
        d.loop()
    except KeyboardInterrupt:
        pass
    ok("a run still in progress never idles out", not any("IDLE-EXIT" in x for x in w.out))
    return checks


def run_self():
    checks = run_checks()
    for name, good in checks:
        if not good:
            print(f"FAIL {name}")
    bad = sum(1 for _, g in checks if not g)
    print(f"sweep_driver self-test: {len(checks)} checks, {bad} failed")
    return 1 if bad else 0
