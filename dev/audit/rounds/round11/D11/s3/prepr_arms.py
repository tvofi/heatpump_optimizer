#!/usr/bin/env python3
"""D11-s3 (round 11, D11.M4): empty one decision of tools/pr/prepr.sh and ask its --self-test.

Metric: the `<p> passed, <f> failed` line tools/pr/prepr.sh --self-test prints,
  per arm; an arm is KILLED when f > the null arm's f. Count key: the
  self-test's own tally, never the harness's edit.
How: a detached `git worktree` of HEAD per arm in a private temp dir (prepr.sh
  cd's to `git rev-parse --show-toplevel`), one exact-string edit per arm, the
  arms run concurrently.
Arms:
  null                       unedited
  version_edit_gutted        the step-5 decision function: `out=$(stamp_paths ...)`
                             -> `out=""` (version_edit then never reports a
                             VERSION / manifest / notes edit)
  step5_wiring_gutted        the step-5 call site in the main flow:
                             `step "no version edit" $? "$STAMPED"` ->
                             `step "no version edit" 0 "$STAMPED"`
Expected: null f=0; version_edit_gutted KILLED; step5_wiring_gutted: whatever
  the self-test says (the question this arm asks).
Command: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/prepr_arms.py
  (about 15-25 min wall on a shared 4-vCPU box: provisional, not a RESULT)
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B7 (4 vCPU container).
Perturbation: the two arms ARE the one-line production edits; the null arm is
  the control that the tally is 0 failed without them.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import concurrent.futures as cf
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path.cwd()
P = "tools/pr/prepr.sh"
ARMS = {
    "null": None,
    "version_edit_gutted": ('  out=$(stamp_paths "$names" "$manifest" "$notes")\n', '  out=""\n'),
    "step5_wiring_gutted": ('step "no version edit" $? "$STAMPED"\n', 'step "no version edit" 0 "$STAMPED"\n'),
}


WORKER_CPU = []


def run_arm(tmp, head, name):
    t0 = time.thread_time()
    try:
        return _run_arm(tmp, head, name)
    finally:
        WORKER_CPU.append(time.thread_time() - t0)


def _run_arm(tmp, head, name):
    wt = tmp / name
    r = subprocess.run(["git", "worktree", "add", "-q", "--detach", str(wt), head], cwd=ROOT,
                       capture_output=True, text=True)
    if r.returncode:
        return name, None, r.stderr
    try:
        edit = ARMS[name]
        if edit:
            f = wt / P
            s = f.read_text()
            if s.count(edit[0]) != 1:
                return name, None, "mutation did not apply exactly once"
            f.write_text(s.replace(edit[0], edit[1]))
        env = dict(os.environ, HPO_PLANDATA=str(tmp / ("plandata-" + name)),
                   TMPDIR=str(tmp / ("t-" + name)))
        (tmp / ("plandata-" + name)).mkdir()
        (tmp / ("t-" + name)).mkdir()
        p = subprocess.run(["bash", P, "--self-test"], cwd=wt, env=env, capture_output=True,
                           text=True, timeout=5400)
        out = p.stdout + p.stderr
        m = re.findall(r"^(\d+) passed, (\d+) failed$", out, re.M)
        fails = [l.strip() for l in out.splitlines() if l.startswith("  FAIL")][:5]
        return name, (int(m[-1][0]), int(m[-1][1])) if m else None, fails
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)], cwd=ROOT,
                       capture_output=True)


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                          text=True).stdout.strip()
    if not head:
        raise SystemExit("needs a git checkout of the baseline")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="d11s3-prepr-"))
    with cf.ThreadPoolExecutor(len(ARMS)) as ex:
        res = {n: (t, x) for n, t, x in ex.map(lambda n: run_arm(tmp, head, n), ARMS)}
    for n, (t, x) in res.items():
        print("arm %-22s tally=%s %s" % (n, t, x))
    null_f = res["null"][0][1] if res["null"][0] else -1
    for n, (t, _) in res.items():
        if t:
            print("RESULT %s_passed=%d count" % (n, t[0]))
            print("RESULT %s_failed=%d count" % (n, t[1]))
    killed = sum(1 for n, (t, _) in res.items() if n != "null" and t and t[1] > null_f)
    print("RESULT mutants=%d count" % (len(ARMS) - 1))
    print("RESULT mutants_killed=%d count" % killed)
    shutil.rmtree(tmp, ignore_errors=True)
    # The arms run on deliberate worker threads (README: the FakeHass trap's rule):
    # their CPU is subtracted and printed, and the residual is the factor.
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    wc = sum(WORKER_CPU)
    print("RESULT worker_thread_cpu=%.3f s" % wc)
    print("RESULT thread_factor=%.3f ratio" % ((tp - wc) / tt if tt else 1.0))
    print("RESULT load1=%.2f" % os.getloadavg()[0])
    sw = 0
    try:
        for l in open("/proc/vmstat"):
            if l.startswith("pswpin "):
                sw = int(l.split()[1])
    except OSError:
        pass
    print("RESULT swapins=%d count" % sw)


if __name__ == "__main__":
    sys.exit(main())
