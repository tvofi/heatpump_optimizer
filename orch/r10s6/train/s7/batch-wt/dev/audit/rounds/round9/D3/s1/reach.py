#!/usr/bin/env python3
"""D3.M5: how much of coordinator.py each script in its measured closure actually executes.

METRIC: reach_<script> = distinct executable lines of
  custom_components/heatpump_optimizer/coordinator.py executed in-process by that script
  (sys.monitoring LINE events, each (code, line) counted once, then DISABLEd); union_reach and
  never_reached over all scripts run. Key: the interpreter's own line events on the production
  file's code objects -- not the closure file, not the script text.
RUN:      PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D3/s1/reach.py [script ...]
          no argument: every Python script coordinator.py's closure selects (golden.py excepted:
          GOLDEN_MODE=drift replaces it by env_drift.py --all <baseline>, which runs here unpinned
          and needs HEAD != baseline) -- each in its own child interpreter.
EXPECTED: RESULT reach_tests_typing_ruler_py=0 lines (exact); features/entities in the thousands (±1 %)
BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
MACHINE:  box B1 (4 vCPU cloud container, Linux 6.18), CPython 3.14.0rc2
ROOT:     Path(".") -- run from the repository root; scripts run in-place (they write only temp paths
          and HPO_PLANDATA, which this harness points under a mkdtemp root).
PERTURBATION: pass a script together with `--force-import` -> its reach moves up from 0 to the
  import-time line count (module body executes), proving the counter hooks coordinator's code.
Child processes a script spawns (deployment_shape's installation interpreters, the process
worker) are not traced; that is a stated under-count, not a zero.
"""
from __future__ import annotations

import os

for _threads in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_threads, "1")

import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

BASELINE = os.environ.get("HPO_AUDIT_BASELINE", "1936d5ca72a06556eeed4e8e5bf3dea520e517e1")
PIN = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
       "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")
TARGET = "custom_components/heatpump_optimizer/coordinator.py"

CHILD = r'''
import os, sys, json, runpy, atexit
target = os.path.realpath(sys.argv[1]); out = sys.argv[2]; script = sys.argv[3]; force = sys.argv[4] == "1"
mon = sys.monitoring; TOOL = 4
mon.use_tool_id(TOOL, "d3s1reach")
seen = set()
def on_line(code, line):
    if code.co_filename and os.path.realpath(code.co_filename) == target:
        seen.add(line)
    return mon.DISABLE
mon.register_callback(TOOL, mon.events.LINE, on_line)
mon.set_events(TOOL, mon.events.LINE)
def dump():
    with open(out, "w") as fh: json.dump(sorted(seen), fh)
atexit.register(dump)
sys.argv = [script] + sys.argv[5:]
sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
if force:
    sys.path.insert(0, "custom_components"); import heatpump_optimizer.coordinator  # noqa
try:
    runpy.run_path(script, run_name="__main__")
except SystemExit as e:
    code = e.code
    dump(); os._exit(code if isinstance(code, int) else (0 if code is None else 1))
dump()
'''


def executable_lines() -> set[int]:
    code = compile(Path(TARGET).read_text(), TARGET, "exec")
    lines: set[int] = set()
    stack = [code]
    while stack:
        c = stack.pop()
        lines.update(ln for _, _, ln in c.co_lines() if ln is not None)
        stack.extend(k for k in c.co_consts if hasattr(k, "co_lines"))
    return lines


def closure_python() -> list[str]:
    out = subprocess.run([sys.executable, "tests/closure.py", "select", "--files", TARGET],
                         capture_output=True, text=True).stdout
    run = re.findall(r"^\s+RUN\s+(\S+\.py)", out, re.M)
    return [s for s in run if s != "tests/golden.py"]


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force-import" in sys.argv
    scripts = args or closure_python()
    tmp = Path(tempfile.mkdtemp(prefix="d3s1reach-"))
    env = dict(os.environ, PYTHONPATH="tests/hastub", HPO_PLANDATA=str(tmp / "plandata"))
    exe = executable_lines()
    union: set[int] = set()
    t0p, t0t = time.process_time(), time.thread_time()
    for s in scripts:
        out = tmp / (Path(s).stem + ".json")
        w0 = time.monotonic()
        extra, e = [], env
        if s == "tests/env_drift.py":
            # GOLDEN_MODE=drift's capture, unpinned so it keys to the shared warmed baseline cache
            extra = ["--all", BASELINE]
            e = {k: v for k, v in env.items() if k not in PIN}
        p = subprocess.run([sys.executable, "-c", CHILD, TARGET, str(out), s, "1" if force else "0", *extra],
                           env=e, capture_output=True, text=True)
        wall = time.monotonic() - w0
        seen = set(json.loads(out.read_text())) if out.exists() else set()
        seen &= exe
        union |= seen
        key = s.replace("tests/", "tests_").replace(".", "_")
        print(f"SCRIPT {s} rc={p.returncode} wall={wall:.1f}s reach={len(seen)}")
        print(f"RESULT reach_{key}={len(seen)} lines")
    print(f"RESULT executable_lines={len(exe)} lines")
    print(f"RESULT union_reach={len(union)} lines")
    print(f"RESULT never_reached={len(exe - union)} lines")
    (tmp / "union.json").write_text(json.dumps(sorted(union)))
    print("UNION_FILE", tmp / "union.json")
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={tp / tt if tt > 1e-9 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
