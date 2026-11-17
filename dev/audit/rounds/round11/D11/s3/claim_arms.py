#!/usr/bin/env python3
"""D11-s3 (round 11, D11.M4): perturb the two golden claim files and count refusals.

Metric: number of perturbation arms the production validators refuse
  (a non-None error string), out of the arms run; the null arm (the files as
  committed) must give 0 refusals. Count key: the validator's return value.
Validators hooked:
  tests/env_drift.py:claim_version_error  (claims-for vs VERSION, solver file)
  tests/env_drift.py:may_drift_error      (claimed AND may-drift; out-of-scope name)
  tests/env_drift.py:may_drift_coverage_error (allowed name dropped from both lists)
  tests/card_rig.mjs:parseClaims + claimVersionError (card file stamp)
Arms (each in a private temp copy of VERSION + tests/golden/*claimed_drift.txt):
  solver: claims-for one digit up; stamp line removed; stamp 'next';
          a claimed name also marked may-drift; a may-drift name outside
          MAY_DRIFT_ALLOWED; a may-drift entry deleted while unclaimed.
  card:   claims-for one digit up; stamp line removed.
Expected: null 0 refusals; 8 of 8 arms refused, exact.
Command: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/claim_arms.py
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B7 (4 vCPU container).
Perturbation (production, one line): `--perturb` rebinds
  env_drift._looks_like_version to accept any text and patches
  env_drift._repo_version to return the declared stamp (as a
  claim_version_error that compared the stamp with itself would): the
  digit-up and not-a-version solver arms then pass (refused falls 8 -> 6;
  measured 2026-11-16).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import pathlib
import re
import subprocess
import sys
import tempfile
import time
from unittest import mock

ROOT = pathlib.Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
import env_drift  # noqa: E402

NODE = os.environ.get("NODE", "/opt/node22/bin/node")
SOLVER = "tests/golden/claimed_drift.txt"
CARD = "tests/golden/card_claimed_drift.txt"


def bump(text):
    m = re.search(r"^# claims-for: (\d+)\.(\d+)\.(\d+)$", text, re.M)
    a, b, c = m.groups()
    return text.replace(m.group(0), "# claims-for: %s.%s.%d" % (a, b, int(c) + 1), 1)


def drop_stamp(text):
    return re.sub(r"^# claims-for: .*\n", "", text, count=1, flags=re.M)


def mk(tmp, name, solver, card):
    d = tmp / name
    (d / "tests/golden").mkdir(parents=True)
    (d / "VERSION").write_text((ROOT / "VERSION").read_text())
    (d / SOLVER).write_text(solver)
    (d / CARD).write_text(card)
    return d


def solver_verdict(repo):
    errs = []
    e = env_drift.claim_version_error(str(repo))
    if e:
        errs.append(e.split("\n")[0])
    md = env_drift._may_drift(str(repo))
    declared, claims = env_drift._claimed(str(repo))
    e = env_drift.may_drift_error(md, claims)
    if e:
        errs.append(e.split("\n")[0])
    e = env_drift.may_drift_coverage_error(md, claims, declared, env_drift._repo_version(str(repo)))
    if e:
        errs.append(e.split("\n")[0][:80])
    return errs


def card_verdict(repo, tmp):
    drv = tmp / "card.mjs"
    drv.write_text(
        "const m = await import(process.argv[2]);\n"
        "const fs = await import('node:fs');\n"
        "const t = fs.readFileSync(process.argv[3], 'utf8');\n"
        "const v = fs.readFileSync(process.argv[4], 'utf8').trim();\n"
        "const e = m.claimVersionError(m.parseClaims(t).declared, v);\n"
        "console.log(JSON.stringify(e ? [e.split(':')[0]] : []));\n")
    r = subprocess.run([NODE, str(drv), str(ROOT / "tests/card_rig.mjs"), str(repo / CARD),
                        str(repo / "VERSION")], capture_output=True, text=True, cwd=ROOT,
                       env=dict(os.environ, HPO_PLANDATA=str(tmp / "plandata")), timeout=120)
    lines = [l for l in r.stdout.splitlines() if l.startswith("[")]
    if not lines:
        raise SystemExit("card driver failed: %s %s" % (r.stdout[-400:], r.stderr[-400:]))
    return json.loads(lines[-1])


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="d11s3-claims-"))
    (tmp / "plandata").mkdir()
    s0 = (ROOT / SOLVER).read_text()
    c0 = (ROOT / CARD).read_text()
    md0 = env_drift._may_drift(str(ROOT))
    _, claims0 = env_drift._claimed(str(ROOT))
    allowed_unclaimed = sorted(n for n in md0 if n not in claims0)
    target = allowed_unclaimed[0]
    claimed = sorted(claims0)
    solver_arms = {
        "solver_stamp_digit_up": bump(s0),
        "solver_stamp_removed": drop_stamp(s0),
        "solver_stamp_not_a_version": re.sub(r"^# claims-for: .*$", "# claims-for: next", s0, count=1, flags=re.M),
        "solver_claim_and_maydrift": s0 + "%s  # d11s3 probe claim\n" % target,
        "solver_maydrift_out_of_scope": s0 + "# may-drift: d11s3_not_allowed -- probe\n",
        "solver_maydrift_dropped": re.sub(r"^# may-drift: %s .*\n" % re.escape(target), "", s0, count=1, flags=re.M),
    }
    card_arms = {"card_stamp_digit_up": bump(c0), "card_stamp_removed": drop_stamp(c0)}

    patches = []
    if "--perturb" in sys.argv:
        # Make every stamp look current: _repo_version reports whatever the file declares.
        patches = [mock.patch.object(env_drift, "_repo_version",
                                     lambda repo: env_drift._claimed(repo)[0] or "0.0.0"),
                   mock.patch.object(env_drift, "_looks_like_version", lambda t: True)]
        for p in patches:
            p.start()
        print("PERTURBED: env_drift._repo_version returns the declared stamp")

    null = solver_verdict(mk(tmp, "null", s0, c0)) + card_verdict(mk(tmp, "nullc", s0, c0), tmp)
    print("arm null refused=%d %s" % (len(null), null))
    refused = 0
    rows = {}
    for name, text in solver_arms.items():
        v = solver_verdict(mk(tmp, name, text, c0))
        rows[name] = v
    for name, text in card_arms.items():
        v = card_verdict(mk(tmp, name, s0, text), tmp)
        rows[name] = v
    for name, v in rows.items():
        refused += bool(v)
        print("arm %-32s refused=%s %s" % (name, bool(v), v[:1]))
    for p in patches:
        p.stop()
    print("probe name used: %s; claimed at baseline: %s" % (target, claimed))
    print("RESULT null_refusals=%d count" % len(null))
    print("RESULT arms=%d count" % len(rows))
    print("RESULT arms_refused=%d count" % refused)
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
