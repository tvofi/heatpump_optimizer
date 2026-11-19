#!/usr/bin/env python3
"""D11-s3 (round 11, D11.M4): perturb brief_lint.mjs's inputs and count what its CI run refuses.

Metric: the `TOTAL: <n> error(s)` that tools/policy/brief_lint.mjs:main prints
  on its no-argument run (the run tests.yml's `briefs` job makes), per arm,
  plus the number of roster files that run lints. Count key: brief_lint's own
  TOTAL line and its `== <file> ==` headers, never the harness's edits.
How: a detached `git worktree` of HEAD in a private temp dir (brief_lint reads
  `git ls-files`, so it needs a checkout; the finder export's wall-deleted
  files would otherwise be read as missing); each arm edits one file there.
Arms:
  null                    unedited
  control_3l_path         `tests/d11s3_no_such_probe.py` appended to the brief of
                          the one live group in .claude/workflows/wave-3l-groups.json
  control_3l_count        "the 19 metrics" appended to the same brief
  control_playbook_path   `tools/audit/check_scopes.py` -> `tools/audit/check_scopez.py`
                          in dev/audit/README.md
  gap_r10_path            the probe path appended to the first live group's brief
                          in dev/programme/rosters/wave-r10-groups.json
  gap_r9_path             the same in dev/programme/rosters/wave-r9-groups.json
  and, read-only, brief_lint run with each dev/programme/rosters roster named
  (the roster_edit.py write-gate form) to show what the CI run does not see.
Expected: null 0; each control > null; each gap arm == null, exact.
Command: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/brief_arms.py [--perturb]
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B7 (4 vCPU container).
  Wall per run is about 60 s on a shared box (provisional; not a RESULT).
Perturbation (production, one line): `--perturb` edits brief_lint.mjs's main()
  in the worktree so the no-argument run also lints ROSTERS_DIR's
  wave-*-groups.json: rosters_linted 1 -> 3, the null arm's TOTAL rises and
  both gap arms move up.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path.cwd()
NODE = os.environ.get("NODE", "/opt/node22/bin/node")
PROBE = " See `tests/d11s3_no_such_probe.py`."
R10 = "dev/programme/rosters/wave-r10-groups.json"
R9 = "dev/programme/rosters/wave-r9-groups.json"
L3 = ".claude/workflows/wave-3l-groups.json"
PLAYBOOK = "dev/audit/README.md"
LINT = "tools/policy/brief_lint.mjs"


def sh(*a, cwd=None):
    return subprocess.run(list(a), cwd=cwd, capture_output=True, text=True)


def edit_roster(wt, rel, suffix):
    p = wt / rel
    raw = p.read_text()
    d = json.loads(raw)
    g = next(g for g in d["groups"] if g.get("resume", {}).get("stage") != "done")
    old = json.dumps(g["brief"], ensure_ascii=True)[1:-1]
    new = json.dumps(g["brief"] + suffix, ensure_ascii=True)[1:-1]
    if old not in raw:
        raise SystemExit("brief text not found verbatim in %s" % rel)
    p.write_text(raw.replace(old, new, 1))
    return g["group"]


def perturb_lint(wt):
    p = wt / LINT
    s = p.read_text()
    old = "    ? workflowFiles(ROSTER_FILE_RE)\n"
    new = ("    ? [...fs.readdirSync(ROSTERS_DIR).filter((f) => ROSTER_FILE_RE.test(f))"
           ".map((f) => path.join(ROSTERS_DIR, f)), ...workflowFiles(ROSTER_FILE_RE)]\n")
    if old not in s:
        raise SystemExit("perturbation did not apply")
    p.write_text(s.replace(old, new, 1))


def run_lint(wt, tmp, *files):
    env = dict(os.environ, HPO_PLANDATA=str(tmp / "plandata"))
    r = subprocess.run([NODE, LINT, *files], cwd=wt, env=env, capture_output=True, text=True,
                       timeout=900)
    out = r.stdout + r.stderr
    m = re.search(r"^TOTAL: (\d+) error", out, re.M)
    headers = re.findall(r"^== (.+?) ==$", out, re.M)
    rosters = [h for h in headers if re.search(r"wave-.*-groups\.json$", h) and "fixtures" not in h]
    return (int(m.group(1)) if m else -1), rosters, r.returncode


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="d11s3-brief-"))
    (tmp / "plandata").mkdir()
    head = sh("git", "rev-parse", "HEAD", cwd=ROOT).stdout.strip()
    if not head:
        raise SystemExit("needs a git checkout of the baseline (brief_lint reads git ls-files)")
    arms = ["null", "control_3l_path", "control_3l_count", "control_playbook_path",
            "gap_r10_path", "gap_r9_path"]
    res = {}
    named = {}
    for arm in arms:
        wt = tmp / arm
        r = sh("git", "worktree", "add", "-q", "--detach", str(wt), head, cwd=ROOT)
        if r.returncode:
            raise SystemExit(r.stderr)
        try:
            if "--perturb" in sys.argv:
                perturb_lint(wt)
            what = ""
            if arm == "control_3l_path":
                what = edit_roster(wt, L3, PROBE)
            elif arm == "control_3l_count":
                what = edit_roster(wt, L3, " Pay against the 19 metrics.")
            elif arm == "control_playbook_path":
                p = wt / PLAYBOOK
                s = p.read_text()
                assert "`tools/audit/check_scopes.py`" in s
                p.write_text(s.replace("`tools/audit/check_scopes.py`", "`tools/audit/check_scopez.py`"))
                what = PLAYBOOK
            elif arm == "gap_r10_path":
                what = edit_roster(wt, R10, PROBE)
            elif arm == "gap_r9_path":
                what = edit_roster(wt, R9, PROBE)
            total, rosters, rc = run_lint(wt, tmp)
            res[arm] = (total, rosters, rc)
            print("arm %-22s edited=%-28s TOTAL=%d rc=%d rosters_linted=%s"
                  % (arm, what, total, rc, rosters))
            if arm == "null":
                for rel in (R10, R9):
                    n, _, _ = run_lint(wt, tmp, rel)
                    named[rel] = n
                    print("  named-file run %s: TOTAL=%d" % (rel, n))
        finally:
            sh("git", "worktree", "remove", "--force", str(wt), cwd=ROOT)
    null = res["null"][0]
    print("RESULT null_total=%d count" % null)
    for arm in arms[1:]:
        print("RESULT %s_total=%d count" % (arm, res[arm][0]))
    print("RESULT rosters_linted=%d count" % len(res["null"][1]))
    print("RESULT live_rosters_in_rosters_dir_unlinted=%d count"
          % sum(1 for rel in (R10, R9) if rel not in res["null"][1]))
    print("RESULT controls_fired=%d count" % sum(res[a][0] > null for a in arms if a.startswith("control_")))
    print("RESULT gap_arms_unmoved=%d count" % sum(res[a][0] == null for a in arms if a.startswith("gap_")))
    for rel, n in named.items():
        print("RESULT named_%s_errors=%d count" % (pathlib.Path(rel).stem.replace("-", "_"), n))
    shutil.rmtree(tmp, ignore_errors=True)
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
