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
link read from its second; and, waited on while still running with no
tally grep as the prepr step is, a slow non-zero exit and a slow pass. Each
refusal arm must refuse and each control must pass, first on the library as committed (M0) and then
on three mutants of bg_wait: M1 returns 0 in place of the recorded
status, M2 returns 0 for a launcher gone with no status, X8 returns 0 after
its first poll finds the command still running, M3 drops bg_wait's read
marker, M4 makes bg_unread pass with names unread. Three arms more drive
bg_unread over the job's five names: four read and one never read is refused
and named, all five read passes. W2 deletes the job's last step, which must
run bg_unread under !cancelled(): the shape check refuses it. Prints one line per
arm and mutant, and `RESULT survivors=<n>`; exit 1 when a mutant survived or
M0 failed.

`replay` runs the job's steps from WF in order, each `run:` in its own
`bash --noprofile --norc -eo pipefail` with one RUNNER_TEMP, the runner's
skip rule for a step without `!cancelled()` after a failure, and prints each
step's seconds and the total. `bg` runs only the launcher and the steps that
call bg_wait or bg_unread; `all` runs every step. WF may be any copy of the workflow, e.g.
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
bg_start slowbad bash -c 'sleep 8; echo partial; exit 5'
bg_start slowok bash -c 'sleep 15; echo partial'
( bg_run c1 bash -c 'exit 3'; bg_run c2 bash -c 'echo "x self-test: 1 checks, 0 failed"' ) < /dev/null > /dev/null 2>&1 &
bg_pid "$!" c1 c2
( bg_run d1 bash -c 'sleep 600'; bg_run d2 true ) < /dev/null > /dev/null 2>&1 &
bg_pid "$!" d1 d2
sleep 2; kill -9 "$(cat "$RUNNER_TEMP/bg/killed.pid")" "$(cat "$RUNNER_TEMP/bg/d1.pid")"
( bg_wait slowbad > /dev/null ) && echo "FAIL refuse slow bad" || echo "PASS refuse slow bad"
( bg_wait slowok > /dev/null ) && echo "PASS control slow ok" || echo "FAIL control slow ok"
wait 2> /dev/null || true
( bg_wait c1 > /dev/null ) && echo "FAIL refuse chained bad" || echo "PASS refuse chained bad"
( bg_wait c2 | grep -Eq "$2" ) && echo "PASS control chained tally" || echo "FAIL control chained tally"
( bg_wait d2 > /dev/null 2>&1 ) && echo "FAIL refuse chain killed" || echo "PASS refuse chain killed"
( bg_wait ok > /dev/null ) && echo "PASS control ok" || echo "FAIL control ok"
( bg_wait bad > /dev/null ) && echo "FAIL refuse bad" || echo "PASS refuse bad"
( bg_wait killed > /dev/null 2>&1 ) && echo "FAIL refuse killed" || echo "PASS refuse killed"
( bg_wait notally | grep -Eq "$2" ) && echo "FAIL refuse notally" || echo "PASS refuse notally"
( bg_wait ok | grep -Eq "$2" ) && echo "PASS control tally" || echo "FAIL control tally"
RUNNER_TEMP="$RUNNER_TEMP/u"; mkdir -p "$RUNNER_TEMP/bg"
for n in prepr beatd open-pr pr-args update-pr; do bg_start "$n" true; done
for n in beatd open-pr pr-args update-pr; do bg_wait "$n" > /dev/null; done
( bg_unread > /dev/null 2>&1 ) && echo "FAIL refuse unread" || echo "PASS refuse unread"
( { bg_unread 2>&1 || true; } | grep "^UNREAD prepr:" > /dev/null ) && echo "PASS names unread" || echo "FAIL names unread"
bg_wait prepr > /dev/null
( bg_unread > /dev/null 2>&1 ) && echo "PASS control all read" || echo "FAIL control all read"
'''

MUTANTS = {
    "M1": ('return "$(cat "$d/$1.rc")"', "return 0"),
    "M2": ('echo "$1: its launcher exited with no status" >&2; return 1', "return 0"),
    "X8": ("    sleep 5\n", "    sleep 5; return 0\n"),
    "M3": (': > "$d/$1.read"; ', ""),
    "M4": ('test "$u" -eq 0', "true"),
}
UNREAD_STEP = "Refuse a detached self-test whose status no step read"


def steps(wf):
    with open(wf) as f:
        return yaml.safe_load(f)["jobs"][JOB]["steps"]


def library(wf):
    run = next(s["run"] for s in steps(wf) if s.get("name") == LAUNCHER)
    return re.search(r"<<'LIB'\n(.*?)\nLIB\n", run, re.S).group(1)


def shape(st):
    """The job's last step runs bg_unread under !cancelled(), after every bg_wait."""
    last = st[-1]
    ok = (last.get("name") == UNREAD_STEP and "bg_unread" in last.get("run", "")
          and "!cancelled()" in last.get("if", ""))
    return f"{'PASS' if ok else 'FAIL'} shape last step reads bg_unread"


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
    base = arms(lib) + [shape(steps(WORKFLOW))]
    for ln in base:
        print(f"M0 {ln}")
    ok0 = len(base) == 14 and all(ln.startswith("PASS") for ln in base)
    survivors = 0
    w2 = shape(steps(WORKFLOW)[:-1])
    print(f"W2 {'KILLED by ' + w2 if w2.startswith('FAIL') else 'SURVIVED'}")
    survivors += not w2.startswith("FAIL")
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
        if mode == "bg" and s["name"] != LAUNCHER and not re.search(r"\bbg_(wait|unread)\b", s["run"]):
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
