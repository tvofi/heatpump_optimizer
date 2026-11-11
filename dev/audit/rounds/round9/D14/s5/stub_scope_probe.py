#!/usr/bin/env python3
# D14-s5 failing probe for the I2 seam set closure_divergence.py lists.
#
# METRIC: red_and_skipped = 1 when a one-line edit to a tests/hastub file that
#   tests/deployment_shape.py's CHILD process imports turns deployment_shape.py
#   red (rc != 0) AND tests/closure.py:select([that file]) returns mode
#   "scoped" with deployment_shape.py skipped; else 0.  Count key: select()'s
#   plan and the script's exit status, both measured in a scratch copy.
# INSTRUMENTED SYMBOLS: tests/closure.py:select; tests/deployment_shape.py:main
#   (driven as the gate drives it, `python tests/deployment_shape.py`).
# EDIT: append `import gate_lock as _d14s5_probe  # noqa` to
#   tests/hastub/homeassistant/helpers/update_coordinator.py -- a stub that
#   resolves a module from tests/, which every `python tests/<x>.py` run can
#   see (sys.path[0] is tests/) and the -P driver child cannot (the #511 shape).
# COMMAND (repo root):
#   PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
#     tools/audit/round9/D14/s5/stub_scope_probe.py [--perturb union]
# EXPECTED (baseline 1936d5ca, box B9): control rc=0; edited rc!=0;
#   red_and_skipped=1 exact.  --perturb union (the child's reads folded into
#   deployment_shape.py's closure, the fix shape) -> red_and_skipped=0.
# MACHINE: box B9 cloud container, CPython 3.14.0rc2.  BASELINE: 1936d5ca72a0.
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path.cwd()
STUB = "tests/hastub/homeassistant/helpers/update_coordinator.py"
SCRIPT = "tests/deployment_shape.py"


def sh(cmd, cwd, env=None):
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", choices=["none", "union"], default="none")
    a = ap.parse_args()
    tmp = Path(tempfile.mkdtemp(prefix="d14s5-probe-"))
    tree = tmp / "tree"
    tree.mkdir()
    # A scratch copy of the tracked tree at HEAD, with its own git index so
    # deployment_shape.py's `git ls-files` works; nothing touches ROOT.
    arc = subprocess.run(["git", "archive", "HEAD"], cwd=ROOT, capture_output=True)
    subprocess.run(["tar", "-x", "-C", str(tree)], input=arc.stdout, check=True)
    g = ["git", "-c", "user.name=probe", "-c", "user.email=probe@invalid"]
    sh(g + ["init", "-q"], tree); sh(g + ["add", "-A"], tree)
    sh(g + ["commit", "-q", "-m", "probe base"], tree)
    env = dict(os.environ, PYTHONPATH=str(tree / "tests" / "hastub"))

    ctl = sh([sys.executable, SCRIPT], tree, env)
    print(f"control: {SCRIPT} rc={ctl.returncode}")
    p = tree / STUB
    p.write_text(p.read_text() + "\nimport gate_lock as _d14s5_probe  # noqa\n")
    red = sh([sys.executable, SCRIPT], tree, env)
    fails = [l.strip() for l in red.stdout.splitlines() if l.strip().startswith("FAIL")]
    print(f"edited:  {SCRIPT} rc={red.returncode} FAIL lines={len(fails)}")
    for l in fails[:4]:
        print("   ", l[:160])

    if a.perturb == "union":
        cj = tree / "tests" / "closures.json"
        t = json.loads(cj.read_text())
        stub = sorted(str(q.relative_to(tree)) for q in (tree / "tests/hastub").rglob("*.py"))
        t["closures"][SCRIPT] = sorted(set(t["closures"][SCRIPT]) | set(stub))
        cj.write_text(json.dumps(t, indent=1))
    code = ("import sys,json; sys.path.insert(0,'tests'); import closure; "
            f"print(json.dumps(closure.select([{STUB!r}])))")
    plan = json.loads(sh([sys.executable, "-c", code], tree, env).stdout)
    skipped = plan["mode"] == "scoped" and SCRIPT not in plan["run"]
    print(f"select([{STUB}]) mode={plan['mode']} runs {len(plan['run'])} scripts; "
          f"{SCRIPT} {'SKIPPED' if skipped else 'run'}")
    ok_ctl = ctl.returncode == 0
    print(f"RESULT control_green={int(ok_ctl)} count")
    print(f"RESULT edited_red={int(red.returncode != 0)} count")
    print(f"RESULT red_and_skipped={int(ok_ctl and red.returncode != 0 and skipped)} count")
    print("RESULT thread_factor=1.000")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=n/a")
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
