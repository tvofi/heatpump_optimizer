#!/usr/bin/env python3
"""D11-s3 (round 11, D11.M4): neuter each wired Claude Code hook and ask the check that guards them.

Metric: per arm, the verdict tools/policy/policy_lint.mjs:cmdHooks (`--hooks`, the
  governance.yml `policy-docs` step) prints for the edited hook; a hook arm is
  ACCEPTED when that verdict is `ok`. Count key: cmdHooks's own per-row verdict
  and exit status, never the harness's edit.
How: a detached `git worktree` of HEAD in a private temp dir; one edit per arm,
  `node tools/policy/policy_lint.mjs --hooks` run in the worktree, the edit reverted.
Arms, for each of the four hooks .claude/settings.json wires (pre-bash, pre-edit,
  session-start, stop-selfcheck):
  control_<hook>_decision_gutted  the hook's last `exit 2` (the wrapper's refusal exit,
                                  never the self-test's `[ "$fail" -eq 0 ] || exit 2`
                                  tally line) -> `exit 0`: the hook still runs its
                                  self-test, whose end-to-end cases must fail.
                                  session-start refuses nothing and has no control arm.
  gap_<hook>_noop                 `exit 0` inserted as line 2: the hook does nothing
                                  on any payload AND its `--self-test` exits 0 with
                                  no output
  null                            unedited: every row ok
Expected: null 4 ok; 3 of 3 controls refused (pre-bash, pre-edit, stop-selfcheck);
  every gap arm ACCEPTED (4 of 4), exact.
Command: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/hooks_arms.py [--perturb]
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B7 (4 vCPU container).
Perturbation (production, one line): `--perturb` edits cmdHooks's verdict in the
  worktree from `code === 0 ? 'ok'` to `code === 0 && /^[1-9]\\d* passed, 0 failed$/.test(tail) ? 'ok'`
  (the tally every wired hook's self-test already prints): gap_noop_accepted falls 4 -> 0,
  the null arm stays 4 ok.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path.cwd()
NODE = os.environ.get("NODE", "/opt/node22/bin/node")
HOOKS = ["pre-bash", "pre-edit", "session-start", "stop-selfcheck"]
OLD = "verdict: code === 0 ? 'ok' : 'SELF-TEST FAILED'"
NEW = "verdict: code === 0 && /^[1-9]\\d* passed, 0 failed$/.test(tail) ? 'ok' : 'SELF-TEST FAILED'"


def git(wt, *a):
    return subprocess.run(["git", *a], cwd=wt, capture_output=True, text=True)


def hooks_run(wt, env):
    r = subprocess.run([NODE, "tools/policy/policy_lint.mjs", "--hooks"], cwd=wt, env=env,
                       capture_output=True, text=True, timeout=900)
    verdicts = {}
    for line in r.stdout.splitlines():
        m = re.match(r"\s+(\S.*?)\s{2,}\S+\s+\.claude/hooks/([\w-]+)\.sh", line)
        if m:
            verdicts[m.group(2)] = m.group(1).strip()
    return r.returncode, verdicts


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    head = git(ROOT, "rev-parse", "HEAD").stdout.strip()
    if not head:
        raise SystemExit("needs a git checkout of the baseline")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="d11s3-hooks-"))
    wt = tmp / "wt"
    r = git(ROOT, "worktree", "add", "-q", "--detach", str(wt), head)
    if r.returncode:
        raise SystemExit(r.stderr)
    (tmp / "plandata").mkdir()
    env = dict(os.environ, HPO_PLANDATA=str(tmp / "plandata"))
    perturb = "--perturb" in sys.argv
    res = {}
    try:
        def prep():
            if perturb:
                f = wt / "tools/policy/policy_lint.mjs"
                s = f.read_text()
                if OLD in s:
                    assert s.count(OLD) == 1
                    f.write_text(s.replace(OLD, NEW))
        prep()
        if perturb:
            print("PERTURBED: cmdHooks requires the self-test's `N passed, 0 failed` tally")
        rc, v = hooks_run(wt, env)
        res["null"] = (rc, v)
        print("null: rc=%d %s" % (rc, v))
        for h in HOOKS:
            p = wt / (".claude/hooks/%s.sh" % h)
            src = p.read_text()
            ms = list(re.finditer(r"^([ \t]*)exit 2[ \t]*$", src, re.M))
            if ms:
                m = ms[-1]
                p.write_text(src[:m.start()] + m.group(1) + "exit 0" + src[m.end():])
                rc, v = hooks_run(wt, env)
                res["control_%s_decision_gutted" % h] = (rc, v)
                print("control_%s_decision_gutted: rc=%d verdict=%s" % (h, rc, v.get(h)))
                p.write_text(src)
            lines = src.split("\n")
            p.write_text("\n".join(lines[:1] + ["exit 0"] + lines[1:]))
            # the neutered hook's own self-test, read directly
            st = subprocess.run(["bash", str(p), "--self-test"], cwd=wt, capture_output=True, text=True)
            rc, v = hooks_run(wt, env)
            res["gap_%s_noop" % h] = (rc, v)
            print("gap_%s_noop: self-test rc=%d out=%r; --hooks rc=%d verdict=%s"
                  % (h, st.returncode, st.stdout.strip()[-60:], rc, v.get(h)))
            p.write_text(src)
            prep()
    finally:
        git(ROOT, "worktree", "remove", "--force", str(wt))
        shutil.rmtree(tmp, ignore_errors=True)
    null_ok = sum(1 for h in HOOKS if res["null"][1].get(h) == "ok")
    controls = [k for k in res if k.startswith("control_")]
    ctrl_ref = sum(1 for k in controls if res[k][1].get(k.split("_")[1]) != "ok")
    gap_acc = sum(1 for h in HOOKS if res["gap_%s_noop" % h][1].get(h) == "ok")
    print("RESULT null_rc=%d" % res["null"][0])
    print("RESULT null_ok=%d count" % null_ok)
    print("RESULT control_arms=%d count" % len(controls))
    print("RESULT control_refused=%d count" % ctrl_ref)
    print("RESULT gap_noop_arms=%d count" % len(HOOKS))
    print("RESULT gap_noop_accepted=%d count" % gap_acc)
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print("RESULT thread_factor=%.3f ratio" % (tp / tt if tt else 1.0))
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
