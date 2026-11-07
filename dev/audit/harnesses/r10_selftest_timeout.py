#!/usr/bin/env python3
"""R10-HOTFIX-SELFTEST-TIMEOUT: instrument-self-tests' detached self-tests, against their mutants and as a replay.

    python3 dev/audit/harnesses/r10_selftest_timeout.py                  # arms and mutants
    python3 dev/audit/harnesses/r10_selftest_timeout.py replay WF MODE   # MODE: bg | all

Run from the repository root. The default mode reads the bg_start/bg_wait
library out of the launcher step of `.github/workflows/governance.yml`,
exactly as the step writes it, and drives it over four planted commands: a
pass with a tally (the control), a non-zero exit, a launcher killed before it
writes a status, and a pass printing no tally; and the same through a
chain of bg_run under one bg_pid, the launcher's form for pr_args.sh's three
callers: a failing first link, a passing second, a chain killed in its first
link read from its second. Each refusal arm must refuse
and each control must pass, first on the library as committed (M0) and then
on two mutants of its predicates: M1 returns 0 in place of the recorded
status, M2 returns 0 for a launcher gone with no status. Prints one line per
arm and mutant, and `RESULT survivors=<n>`; exit 1 when a mutant survived or
M0 failed.

`replay` runs the job's steps from WF in order, each `run:` in its own
`bash --noprofile --norc -eo pipefail` with one RUNNER_TEMP, the runner's
skip rule for a step without `!cancelled()` after a failure, and prints each
step's seconds and the total. `bg` runs only the launcher and the steps that
call bg_wait; `all` runs every step. WF may be any copy of the workflow, e.g.
the merge base's from `git show`.
"""
import os
import re
import subprocess
import sys
import tempfile
import time

import yaml

JOB = "instrument-self-tests"
LAUNCHER = "Start the five slowest self-tests beside the rest of the job"
WORKFLOW = ".github/workflows/governance.yml"
TALLY = r"^x self-test: [1-9][0-9]* checks, 0 failed$"

ARMS = r'''
set -eo pipefail
mkdir -p "$RUNNER_TEMP/bg"; . "$1"
bg_start ok bash -c 'echo "x self-test: 3 checks, 0 failed"'
bg_start bad bash -c 'echo "x self-test: 3 checks, 1 failed"; exit 7'
bg_start killed bash -c 'sleep 600'
bg_start notally bash -c 'echo hi'
( bg_run c1 bash -c 'exit 3'; bg_run c2 bash -c 'echo "x self-test: 1 checks, 0 failed"' ) < /dev/null > /dev/null 2>&1 &
bg_pid "$!" c1 c2
( bg_run d1 bash -c 'sleep 600'; bg_run d2 true ) < /dev/null > /dev/null 2>&1 &
bg_pid "$!" d1 d2
sleep 2; kill -9 "$(cat "$RUNNER_TEMP/bg/killed.pid")" "$(cat "$RUNNER_TEMP/bg/d1.pid")"; wait 2> /dev/null || true
( bg_wait c1 > /dev/null ) && echo "FAIL refuse chained bad" || echo "PASS refuse chained bad"
( bg_wait c2 | grep -Eq "$2" ) && echo "PASS control chained tally" || echo "FAIL control chained tally"
( bg_wait d2 > /dev/null 2>&1 ) && echo "FAIL refuse chain killed" || echo "PASS refuse chain killed"
( bg_wait ok > /dev/null ) && echo "PASS control ok" || echo "FAIL control ok"
( bg_wait bad > /dev/null ) && echo "FAIL refuse bad" || echo "PASS refuse bad"
( bg_wait killed > /dev/null 2>&1 ) && echo "FAIL refuse killed" || echo "PASS refuse killed"
( bg_wait notally | grep -Eq "$2" ) && echo "FAIL refuse notally" || echo "PASS refuse notally"
( bg_wait ok | grep -Eq "$2" ) && echo "PASS control tally" || echo "FAIL control tally"
'''

MUTANTS = {
    "M1": ('return "$(cat "$d/$1.rc")"', "return 0"),
    "M2": ('echo "$1: its launcher exited with no status" >&2; return 1', "return 0"),
}


def steps(wf):
    with open(wf) as f:
        return yaml.safe_load(f)["jobs"][JOB]["steps"]


def library(wf):
    run = next(s["run"] for s in steps(wf) if s.get("name") == LAUNCHER)
    return re.search(r"<<'LIB'\n(.*?)\nLIB\n", run, re.S).group(1)


def arms(lib):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "lib.sh")
        with open(p, "w") as f:
            f.write(lib)
        env = dict(os.environ, RUNNER_TEMP=d)
        r = subprocess.run(["bash", "-c", ARMS, "arms", p, TALLY], env=env,
                           capture_output=True, text=True, timeout=120)
        return [ln for ln in r.stdout.splitlines() if ln.startswith(("PASS", "FAIL"))]


def mutants():
    lib = library(WORKFLOW)
    base = arms(lib)
    for ln in base:
        print(f"M0 {ln}")
    ok0 = len(base) == 8 and all(ln.startswith("PASS") for ln in base)
    survivors = 0
    for name, (old, new) in MUTANTS.items():
        if lib.count(old) != 1:
            print(f"{name} NOT APPLIED: {old!r} occurs {lib.count(old)} times")
            survivors += 1
            continue
        fails = [ln for ln in arms(lib.replace(old, new)) if ln.startswith("FAIL")]
        print(f"{name} {'KILLED by ' + '; '.join(fails) if fails else 'SURVIVED'}")
        survivors += not fails
    print(f"RESULT survivors={survivors}")
    return 0 if ok0 and survivors == 0 else 1


def replay(wf, mode):
    env = dict(os.environ, RUNNER_TEMP=tempfile.mkdtemp())
    failed, t0 = False, time.time()
    for s in steps(wf):
        if "run" not in s:
            continue
        if mode == "bg" and s["name"] != LAUNCHER and "bg_wait" not in s["run"]:
            continue
        if failed and "!cancelled()" not in s.get("if", ""):
            print(f"SKIP          {s['name']}")
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as f:
            f.write(s["run"])
        a = time.time()
        r = subprocess.run(["bash", "--noprofile", "--norc", "-eo", "pipefail", f.name],
                           env=env, capture_output=True, text=True)
        os.unlink(f.name)
        failed |= r.returncode != 0
        print(f"{'OK  ' if r.returncode == 0 else 'FAIL'} {time.time() - a:7.1f}s {s['name']}", flush=True)
        if r.returncode:
            print((r.stdout + r.stderr)[-1500:], flush=True)
    print(f"RESULT replay_seconds={time.time() - t0:.0f} failed={int(failed)}")
    return int(failed)


if __name__ == "__main__":
    if sys.argv[1:2] == ["replay"]:
        sys.exit(replay(sys.argv[2], sys.argv[3]))
    sys.exit(mutants())
