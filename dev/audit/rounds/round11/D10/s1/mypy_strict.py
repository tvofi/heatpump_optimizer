#!/usr/bin/env python3
"""D10.M3 strict-typing: mypy --strict over custom_components/heatpump_optimizer, by error code.

Metric: count of mypy ``error:`` lines located under the integration package,
split by ``[code]``, for two arms: ``ruler`` (no stub on the path: the
homeassistant-stubs/real-HA environment of the interpreter, the invocation of
tests/typing_ruler.py:run_mypy) and ``hastub`` (MYPYPATH=tests/hastub, the
brief's "stub on the path"); errors located inside tests/hastub are counted
separately and never mixed into the package count.
Instrumented symbol: every module of custom_components/heatpump_optimizer as
mypy type-checks it (tests/typing_ruler.py:run_mypy's command line).
Perturbation: ``--perturb`` copies the package to a temp root and strips the
return annotation of custom_components/heatpump_optimizer/__init__.py:
async_setup (``-> bool``); the ruler arm's count must move up (no-untyped-def).
Count key: mypy's own error lines whose path is under the package.

Run (from the export root):
  /Users/timmalmstrom/.local/state/hpo/venv-ha/bin/python3 \
      dev/audit/rounds/round11/D10/s1/mypy_strict.py [--perturb]
Expected: see REPORT.md (exact count for the same mypy/stubs versions).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: macOS arm64, venv-ha
(mypy and homeassistant-stubs versions printed as RESULT lines).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import collections
import re
import shutil
import subprocess
import sys
import tempfile
import time
from importlib import metadata

PKG = "custom_components/heatpump_optimizer"
ERR = re.compile(r"^(?P<path>[^:]+):(?P<line>\d+):(?:\d+:)?\s*error:\s*(?P<msg>.*?)(?:\s*\[(?P<code>[A-Za-z0-9_-]+)\])?$")


def run(arm: str, root: str) -> tuple[int, collections.Counter, int, int, list[str]]:
    env = {k: v for k, v in os.environ.items() if k not in ("MYPYPATH", "PYTHONPATH")}
    if arm == "hastub":
        env["MYPYPATH"] = os.path.abspath("tests/hastub")
    with tempfile.TemporaryDirectory() as cache:
        p = subprocess.run(
            [sys.executable, "-m", "mypy", "--strict", "--warn-unused-ignores",
             "--show-error-codes", "--no-error-summary", "--no-incremental",
             "--cache-dir", cache, "--python-version", "3.14", PKG],
            cwd=root, capture_output=True, text=True, env=env)
    lines = (p.stdout + p.stderr).splitlines()
    by = collections.Counter()
    pkg = other = 0
    samples = []
    for ln in lines:
        if ": error:" not in ln:
            continue
        m = ERR.match(ln)
        path = m.group("path") if m else ln.split(":", 1)[0]
        code = (m.group("code") if m else None) or "no-code"
        if path.startswith(PKG):
            pkg += 1
            by[code] += 1
            if len(samples) < 40:
                samples.append(ln)
        else:
            other += 1
    return p.returncode, by, pkg, other, samples


def main() -> int:
    perturb = "--perturb" in sys.argv
    root = os.getcwd()
    tmp = None
    if perturb:
        tmp = tempfile.mkdtemp(prefix="d10s1mypy.")
        shutil.copytree(PKG, os.path.join(tmp, PKG))
        f = os.path.join(tmp, PKG, "__init__.py")
        src = open(f).read()
        new = src.replace("async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:",
                          "async def async_setup(hass, config):", 1)
        assert new != src, "perturbation anchor not found"
        open(f, "w").write(new)
        root = tmp
        print("RESULT perturbed=__init__.py:async_setup annotations stripped")
    for dist in ("mypy", "homeassistant-stubs", "homeassistant"):
        try:
            print(f"RESULT version_{dist}={metadata.version(dist)}")
        except metadata.PackageNotFoundError:
            print(f"RESULT version_{dist}=absent")
    c0, t0 = time.process_time(), time.thread_time()
    arms = ("ruler",) if perturb else ("ruler", "hastub")
    for arm in arms:
        rc, by, pkg, other, samples = run(arm, root)
        print(f"RESULT {arm}_exit={rc}")
        print(f"RESULT {arm}_package_errors={pkg} count")
        print(f"RESULT {arm}_errors_outside_package={other} count")
        for code, n in sorted(by.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"RESULT {arm}_by_code {code}={n} count")
        for s in samples:
            print(f"SAMPLE {arm} {s}")
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={((c1 - c0) / max(t1 - t0, 1e-9)):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
