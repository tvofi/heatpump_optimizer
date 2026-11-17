#!/usr/bin/env python3
"""D11-s3 (round 11, D11.M4): perturb the structural ratchet (tests/structure.py) at
both of its seams and count which budget rows refuse.

Metric: number of budget keys (tests/structure_budgets.json less recorded_at)
  for which tests/structure.py:ratchet returns 1 under the arm, and the set of
  keys its "FAIL <key>" lines name end to end. Count key: the ratchet's own
  return code / FAIL lines, never the harness's edit.
Arms:
  A (comparator, in memory): structure.measure() once on this tree, then per
    key metrics[key] += 1 -> ratchet(); and three malformed budgets (NaN,
    "x", -1) -> ratchet(). Null: the measured metrics unchanged -> 0.
  B (end to end, temp copy of custom_components/ + tests/): a 210-line dead
    method `_d11s3_probe` with one new attribute appended to
    HeatPumpOptimizerCoordinator; tests/structure.py run as CI runs it.
    Null: the same copy unedited.
Expected: A fires on 18 of 18 keys, all 3 malformed arms refused, null rc 0;
  B names >= 4 keys (method LOC, methods_over_150/200, class LOC, attrs).
Command: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/structure_arms.py
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B7 (4 vCPU container).
Perturbation (production, one line): in tests/structure.py:ratchet change
  `if current > budget:` to `if current > budget + 1:` -> arm A's
  keys_firing falls 18 -> 0 (run with --perturb, applied in memory by
  rebinding the function's source).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import contextlib
import importlib.util
import inspect
import io
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time

ROOT = pathlib.Path.cwd()


def load_structure():
    spec = importlib.util.spec_from_file_location("structure_under_test", ROOT / "tests" / "structure.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if "--perturb" in sys.argv:
        src = textwrap.dedent(inspect.getsource(mod.ratchet))
        if "if current > budget:" not in src:
            raise SystemExit("perturbation did not apply")
        ns = {}
        exec(compile(src.replace("if current > budget:", "if current > budget + 1:"),
                     "ratchet_perturbed", "exec"), mod.__dict__, ns)
        mod.ratchet = ns["ratchet"]
        print("PERTURBED: ratchet compares current > budget + 1")
    return mod


def quiet(fn, *a):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(*a)
    return rc, buf.getvalue()


def arm_a(mod):
    result = mod.measure()
    budgets = json.loads(mod.BUDGET_FILE.read_text())
    keys = sorted(k for k in budgets if k != "recorded_at")
    rc0, _ = quiet(mod.ratchet, result)
    firing = []
    for k in keys:
        r = json.loads(json.dumps(result))
        r["metrics"][k] = r["metrics"][k] + 1
        rc, out = quiet(mod.ratchet, r)
        if rc == 1 and ("FAIL %s " % k) in out:
            firing.append(k)
    malformed_refused = 0
    orig = mod.BUDGET_FILE
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="d11s3-struct-"))
    for bad in (float("nan"), "x", -1):
        b = dict(budgets)
        b[keys[0]] = bad
        p = tmp / "structure_budgets.json"
        p.write_text(json.dumps(b))
        mod.BUDGET_FILE = p
        rc, _ = quiet(mod.ratchet, result)
        malformed_refused += rc == 1
    mod.BUDGET_FILE = orig
    return keys, rc0, firing, malformed_refused


PROBE_LINES = 210


def arm_b():
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="d11s3-struct-e2e-"))
    out = {}
    for name in ("null", "probe"):
        root = tmp / name
        shutil.copytree(ROOT / "custom_components", root / "custom_components")
        shutil.copytree(ROOT / "tests", root / "tests",
                        ignore=shutil.ignore_patterns("__pycache__", "golden"))
        if name == "probe":
            f = root / "custom_components/heatpump_optimizer/coordinator.py"
            src = f.read_text()
            anchor = "\nHeatPumpOptimizerConfigEntry = "
            if anchor not in src:
                raise SystemExit("probe anchor missing")
            body = "\n".join("        v%d = self._d11s3_probe_attr + %d" % (i, i) for i in range(PROBE_LINES))
            meth = ("\n    def _d11s3_probe(self):\n        self._d11s3_probe_attr = 1\n%s\n        return v0\n\n"
                    % body)
            f.write_text(src.replace(anchor, meth + anchor, 1))
            sm = root / "tests/seam_map.json"
            m = json.loads(sm.read_text())
            m["seams"]["_d11s3_probe"] = "core"
            sm.write_text(json.dumps(m, indent=1))
        env = dict(os.environ, PYTHONPATH="tests/hastub")
        r = subprocess.run([sys.executable, "tests/structure.py"], cwd=root, env=env,
                           capture_output=True, text=True, timeout=600)
        fails = sorted(set(re.findall(r"^FAIL (\w+)", r.stdout, re.M)))
        out[name] = (r.returncode, fails)
    shutil.rmtree(tmp, ignore_errors=True)
    return out


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    mod = load_structure()
    keys, rc0, firing, malformed = arm_a(mod)
    print("arm A: null rc=%d; keys firing %d/%d; not firing %s" % (rc0, len(firing), len(keys),
          sorted(set(keys) - set(firing))))
    print("RESULT budget_keys=%d count" % len(keys))
    print("RESULT armA_null_rc=%d" % rc0)
    print("RESULT armA_keys_firing=%d count" % len(firing))
    print("RESULT armA_malformed_refused=%d count" % malformed)
    if "--skip-e2e" not in sys.argv:
        b = arm_b()
        new = sorted(set(b["probe"][1]) - set(b["null"][1]))
        print("arm B: null rc=%d fails=%s; probe rc=%d new fails=%s"
              % (b["null"][0], b["null"][1], b["probe"][0], new))
        print("RESULT armB_null_fail_keys=%d count" % len(b["null"][1]))
        print("RESULT armB_probe_new_fail_keys=%d count" % len(new))
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
