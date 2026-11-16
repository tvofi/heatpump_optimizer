"""D12-s3 (round 11): which of the seat's cells (the production files
check_scopes.py lists for D12-s3) a step's harness actually drove.

Metric (one line): per production file under custom_components/heatpump_optimizer,
whether at least one of its FUNCTION code objects (module bodies excluded: an
import is not an examination) started executing while the named harness ran
its cells; RESULT files_driven counts them, RESULT files_universe the denominator.

Count key: sys.monitoring PY_START events on code objects whose co_filename is a
production file -- what the production code executed, never a list kept here.

Run (from the export root), one per step arm:
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D12/s3/filecov.py surfaces --setup            # M3
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D12/s3/filecov.py duties                      # M3 (arbiter grid)
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D12/s3/filecov.py surfaces --setup --reference  # M5
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D12/s3/filecov.py duties --reference          # M5
Each prints `DRIVEN <file>` / `UNDRIVEN <file>` lines, then the RESULT lines.
Perturbation: `--cell switch:switch` (one cell instead of all) -> files_driven DOWN.
Expected at baseline 92d38ecb: see REPORT.md (exact; the set is deterministic).
Machine: box B6, Linux x86_64, python 3.14.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import glob
import importlib
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath("custom_components/heatpump_optimizer")
sys.path.insert(0, HERE)

seen: set[str] = set()
TOOL = sys.monitoring.COVERAGE_ID


def _start(code, _offset):
    f = code.co_filename
    if f.startswith(PKG) and code.co_name != "<module>":
        seen.add(os.path.relpath(f))
    return sys.monitoring.DISABLE


def main():
    target = sys.argv[1]
    sys.argv = [f"{target}.py", *sys.argv[2:]]
    sys.monitoring.use_tool_id(TOOL, "d12s3-filecov")
    sys.monitoring.register_callback(TOOL, sys.monitoring.events.PY_START, _start)
    sys.monitoring.set_events(TOOL, sys.monitoring.events.PY_START)
    try:
        importlib.import_module(target).main()
    finally:
        sys.monitoring.set_events(TOOL, 0)
        sys.monitoring.free_tool_id(TOOL)
    universe = sorted(os.path.relpath(p) for p in glob.glob(os.path.join(PKG, "*.py")))
    for f in universe:
        print(("DRIVEN " if f in seen else "UNDRIVEN ") + f)
    print(f"RESULT files_universe={len(universe)} count")
    print(f"RESULT files_driven={sum(f in seen for f in universe)} count")


if __name__ == "__main__":
    main()
