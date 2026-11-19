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
The coordinator ships every solve to a child interpreter (coordinator._run_in_process ->
process_worker.py). filecov follows it: a sitecustomize.py in a private temp dir, put on
PYTHONPATH (coordinator._worker_env keeps it), installs the same PY_START monitor in the
child and appends each production file to a temp list the first time one of its functions starts, so the solver's own files (runs.py,
batchmath.py, process_worker.py) count as driven where the child ran them.
`--parent-only` (first argument) drops the child monitor: those files read UNDRIVEN.
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


_CHILD_SITE = """
import os, sys
_out, _pkg = os.environ.get("D12S3_COV_OUT"), os.environ.get("D12S3_COV_PKG")
if _out and _pkg and hasattr(sys, "monitoring"):
    _seen = set()
    _T = sys.monitoring.COVERAGE_ID
    def _s(code, _o):
        f = code.co_filename
        if f.startswith(_pkg) and code.co_name != "<module>" and f not in _seen:
            _seen.add(f)
            with open(_out, "a") as fh:  # at first sight: a SIGTERM/SIGKILL reap loses nothing
                fh.write(f + "\\n")
        return sys.monitoring.DISABLE
    try:
        sys.monitoring.use_tool_id(_T, "d12s3-child")
        sys.monitoring.register_callback(_T, sys.monitoring.events.PY_START, _s)
        sys.monitoring.set_events(_T, sys.monitoring.events.PY_START)
    except Exception:
        pass
"""


def main():
    follow = sys.argv[1] != "--parent-only"
    if not follow:
        del sys.argv[1]
    child_out = None
    if follow:
        import tempfile
        tmp = tempfile.mkdtemp(prefix="d12s3cov")
        child_out = os.path.join(tmp, "child_seen.txt")
        with open(os.path.join(tmp, "sitecustomize.py"), "w") as fh:
            fh.write(_CHILD_SITE)
        os.environ["D12S3_COV_OUT"] = child_out
        os.environ["D12S3_COV_PKG"] = PKG
        os.environ["PYTHONPATH"] = os.pathsep.join([tmp] + ([os.environ["PYTHONPATH"]] if os.environ.get("PYTHONPATH") else []))
    target = sys.argv[1]
    sys.argv = [f"{target}.py", *sys.argv[2:]]
    sys.monitoring.use_tool_id(TOOL, "d12s3-filecov")
    sys.monitoring.register_callback(TOOL, sys.monitoring.events.PY_START, _start)
    sys.monitoring.set_events(TOOL, sys.monitoring.events.PY_START)
    mod = importlib.import_module(target)
    try:
        mod.main()
    finally:
        sys.monitoring.set_events(TOOL, 0)
        sys.monitoring.free_tool_id(TOOL)
    child = set()
    if child_out:
        from heatpump_optimizer import coordinator
        coordinator._shutdown_process_pool()
        if os.path.exists(child_out):
            child = {os.path.relpath(x) for x in open(child_out).read().split()}
    seen.update(child)
    print(f"RESULT child_files={len(child)} count")
    universe = sorted(os.path.relpath(p) for p in glob.glob(os.path.join(PKG, "*.py")))
    for f in universe:
        print(("DRIVEN " if f in seen else "UNDRIVEN ") + f)
    print(f"RESULT files_universe={len(universe)} count")
    print(f"RESULT files_driven={sum(f in seen for f in universe)} count")


if __name__ == "__main__":
    main()
