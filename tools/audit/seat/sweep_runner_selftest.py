#!/usr/bin/env python3
"""Self-test of sweep_runner.sh: one real pass over a temp checkout of stub instruments.

Invoked as `python3 -I tools/audit/seat/sweep_runner_selftest.py --self-test` (or `bash tools/audit/seat/sweep_runner.sh --self-test`). The stubs stand in for the
network instruments (replan, plan_page, state_docs, pulse, owed_unactioned, cancel_superseded,
git, gh); sweep_gantt.py, verdict_audit.py and roster_drain.py are the tracked ones, linked in.
Each owed line is proved present, then proved absent by a null control that changes one input.
"""
import json, os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
SH = os.path.join(HERE, "sweep_runner.sh")
N = BAD = 0


def check(name, cond):
    global N, BAD
    N += 1
    if not cond:
        BAD += 1
        print(f"FAIL {name}")


def w(path, text, mode=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)
    if mode:
        os.chmod(path, mode)


def one_pass(tmp, name, handoff_age_h, fire_age_h, html_same, queue=None):
    root = os.path.join(tmp, name)
    co, st, bin_ = (os.path.join(root, d) for d in ("co", "state", "bin"))
    for f in ("sweep_gantt.py", "verdict_audit.py", "roster_drain.py"):
        w(os.path.join(co, "tools/audit/seat", f), open(os.path.join(HERE, f)).read())
    stub = "import sys\nsys.exit(0)\n"
    for f in ("tools/audit/seat/pulse.py", "tools/audit/seat/owed_unactioned.py", "tools/pr/cancel_superseded.py"):
        w(os.path.join(co, f), stub)
    w(os.path.join(co, "tools/audit/seat/state_docs.py"), stub)
    now = time.time()
    plan = {"critical_path": ["G-CP"], "summary": {"closure": "2026-11-07T00:00:00Z"},
            "groups": {"G-CP": {"start": "2026-11-01T00:00:00Z", "finish": "2026-11-06T20:00:00Z", "done": False}}}
    w(os.path.join(co, "tools/plan/replan.py"),
      "import sys, json\nopen(sys.argv[sys.argv.index('--out') + 1], 'w').write(%r)\nprint('summary: stub')\n" % json.dumps(plan))
    w(os.path.join(co, "tools/audit/seat/plan_page.py"),
      "import sys\nopen(sys.argv[sys.argv.index('--html') + 1], 'w').write('<html>new</html>')\n")
    if html_same:
        w(os.path.join(st, "plan.html"), "<html>new</html>")
    else:
        w(os.path.join(st, "plan.html"), "<html>old</html>")
    roster = {"groups": [{"group": "G-CP", "resume": {"stage": "carries-open", "branch": "handoff/r10-cp"}}]}
    # git: fetch no-ops, show prints the roster, for-each-ref prints one handoff row of the given age
    w(os.path.join(bin_, "git"),
      "#!/bin/bash\ncase \"$1\" in show) echo '%s';; for-each-ref) printf 'abc\\trefs/gantt/handoff/r10-cp\\t%d\\n';; esac\nexit 0\n"
      % (json.dumps(roster), int(now - handoff_age_h * 3600)), 0o755)
    w(os.path.join(bin_, "gh"), "#!/bin/bash\necho '[]'\n", 0o755)
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - fire_age_h * 3600))
    w(os.path.join(st, "fired.ledger"), f"{stamp} FIRED r10-cp\n")
    env = dict(os.environ, SWEEP_STATE_DIR=st, SWEEP_CHECKOUT=co, SWEEP_REPO="o/r", SWEEP_ONCE="1",
               SWEEP_FIRED_LEDGER=os.path.join(st, "fired.ledger"), PATH=bin_ + os.pathsep + os.environ["PATH"])
    if queue is not None:
        w(os.path.join(st, "q.txt"), queue)
        env.update(SWEEP_ROSTER_QUEUE=os.path.join(st, "q.txt"), SWEEP_ROSTER_EDIT=os.path.join(root, "e"),
                   SWEEP_ROSTER_WT=os.path.join(root, "wt"), SWEEP_ROSTER_LINT=os.path.join(root, "l"))
        os.makedirs(env["SWEEP_ROSTER_EDIT"], exist_ok=True)
    r = subprocess.run(["bash", SH], env=env, capture_output=True, text=True, timeout=120)
    p = os.path.join(st, "sweep-runner", "new.txt")
    return r, (open(p).read() if os.path.exists(p) else "")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        # live handoff (2 h) -> the CP group is busy; a plan re-render differing from plan.html -> PLAN MOVED
        r, new = one_pass(tmp, "live", 2, 30, False)
        check("pass exits 0", r.returncode == 0)
        check("PLAN MOVED emitted when the render differs from the published page", "PLAN MOVED" in new)
        check("a 2 h-old handoff keeps the CP group busy (no GANTT slip)", "GANTT-SLIP IDLE:G-CP" not in new)
        # (a) the 12 h handoff filter: a 20 h-old tip is not work in flight
        r, new = one_pass(tmp, "stale", 20, 30, True)
        check("null control: unchanged plan page -> no PLAN MOVED", "PLAN MOVED" not in new)
        check("a 20 h-old handoff tip no longer counts: IDLE slip", "GANTT: GANTT-SLIP IDLE:G-CP" in new)
        # (a) the 12 h fire filter: a 2 h-old fire line is a live seat
        r, new = one_pass(tmp, "fired", 20, 2, True)
        check("a 2 h-old fire line keeps the group busy", "GANTT-SLIP IDLE:G-CP" not in new)
        # (b) verdict audit: gh returns no PRs here, so it prints nothing and the step must not fail
        check("verdict audit step ran without VERDICT-AUDIT failed", "VERDICT-AUDIT failed" not in new)
        # (d) roster drain: a ' #' line is skipped with its notice and reaches new.txt
        r, new = one_pass(tmp, "drain", 2, 2, True, queue="set-stage G done # tail\n")
        check("roster drain notice is forwarded", "ROSTER-SKIPPED" in new)
        r, new = one_pass(tmp, "nodrain", 2, 2, True)
        check("null control: no queue configured -> no roster line", "ROSTER-" not in new)
    rc = subprocess.run(["bash", "-n", SH]).returncode
    check("sweep_runner.sh parses", rc == 0)
    text = open(SH).read()
    check("the runner carries no host path", "/Users/" not in text and "/home/" not in text and "<STATE_DIR>" not in text)
    print(f"sweep_runner self-test: {N} checks, {BAD} failed")
    return 1 if BAD else 0


if __name__ == "__main__":
    sys.exit(main())
