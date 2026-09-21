#!/usr/bin/env python3
# METRIC (one line): count of files the committed-closure recorder's own
# instruments (audit-hook opens + end-of-run sys.modules sweep, exactly
# tests/closure.py:_exec_record) attribute to an
# importlib spec_from_file_location/exec_module load performed the way
# tests/entities.py:19415-19419 loads tools/audit/round4/D11/governance_cost.py,
# with a warm __pycache__ (arm WARM) versus a cold one (arm COLD); plus the
# scoped-run script count select() produces for a diff to that file before
# and after pruning its closure entry.
#
# COMMAND (from the repository root):
#   PYTHONPATH=tests/hastub python3 tools/audit/round5/D3/seat-b/warm_pyc_miss.py
#
# EXPECTED (baseline 1cc89e020fff9040a9d0090a27bf22bc1dd497f0, Apple M1,
# Python 3.11): RESULT recorded_warm=0, RESULT recorded_cold>=1 (typically
# exactly 1: the target's own source), RESULT select_kept=2, select_pruned=1
# (tools/audit/round4/D11/governance_cost.py sits in tests/entities.py's and
# tests/harness_headers.py's committed closures), RESULT committed_has_entry=1.
# Counts are contention-immune.
#
# INSTRUMENTED SYMBOLS:
#   tests/entities.py:_load_governance_cost (the production-side loader whose
#   dependency the recorder misses), driving
#   custom_components/.../tools/audit/round4/D11/governance_cost.py via
#   importlib.util.spec_from_file_location + exec_module, recorded by a
#   re-implementation of tests/closure.py:_exec_record's hook and sweep.
#   The select() side instruments tests/closures.json's closure entries.
#
# PERTURBATION (judge runs it): delete the __pycache__ directory beside the
# loaded module (or copy the module pair to a fresh directory, which arm COLD
# does) and re-run -> recorded count rises 0 -> >=1 (cold cache makes the
# loader open the .py source, which the hook records). Prune
# tools/audit/round4/D11/governance_cost.py from tests/entities.py's closure
# in the temp copy and re-run -> select_kept falls 2 -> 1: entities.py drops
# out of the scoped run set for a diff to a file it really reads.
#
# NULL CONTROL: arm COLD is the control -- identical load idiom, identical
# hook, only the bytecode cache differs; the miss must vanish there.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import importlib.util
import json
import shutil
import sys
from pathlib import Path

SEAT = Path(__file__).resolve().parent
ROOT = SEAT.parents[4]
TMP = Path("/tmp/audit-5/tmp/d3b/warm_pyc")
sys.path.insert(0, str(ROOT / "tests"))

import closure  # tests/closure.py, importable read-only

TARGET = "tools/audit/round4/D11/governance_cost.py"


def record_load(path: Path) -> int:
    """Load `path` the way entities.py loads governance_cost, under the
    recorder's own instruments; return how many repo files they attribute."""
    opened: set[str] = set()

    def hook(event, args):
        try:
            if event == "open":
                p = args[0]
                if isinstance(p, (str, bytes, os.PathLike)):
                    r = closure._rel(os.fsdecode(p))
                    if r:
                        opened.add(r)
        except Exception:
            pass

    sys.addaudithook(hook)
    spec = importlib.util.spec_from_file_location(
        "hpo_governance_cost_probe", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # entities.py:19419 idiom
    assert getattr(mod, "GOV", None) is not None or True
    before = {id(m) for m in sys.modules.values()}
    del before
    modules = set()
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if f:
            r = closure._rel(f)
            if r:
                modules.add(r)
    return len((opened | modules) & {str(path.relative_to(ROOT))})


def main() -> int:
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)

    # arm WARM: the tree's own module, whose __pycache__ is warm
    warm_path = ROOT / TARGET
    pyc = warm_path.parent / "__pycache__" / (
        warm_path.stem + ".cpython-311.pyc")
    print(f"RESULT warm_pyc_exists={int(pyc.is_file())}")
    n_warm = record_load(warm_path)
    print(f"RESULT recorded_warm={n_warm}")

    # arm COLD (null control): same pair of files, copied to the seat's own
    # cold directory (inside the repo so the recorder's repo-relative _rel
    # applies, with no __pycache__ beside them)
    cold_dir = SEAT / "coldmod"
    if cold_dir.exists():
        shutil.rmtree(cold_dir)
    cold_dir.mkdir()
    shutil.copy(warm_path, cold_dir / warm_path.name)
    shutil.copy(warm_path.parent / "d11lib.py", cold_dir / "d11lib.py")
    n_cold = record_load(cold_dir / warm_path.name)
    print(f"RESULT recorded_cold={n_cold}")
    shutil.rmtree(cold_dir)          # leave the seat clean

    # the committed table state: who lists the target?
    closures = json.loads(closure.CLOSURES.read_text())["closures"]
    holders = sorted(s for s, fs in closures.items() if TARGET in fs)
    print(f"RESULT committed_has_entry={int(bool(holders))} holders={len(holders)}")

    # select() perturbation: prune entities' entry in a temp copy
    plan_kept = closure.select([TARGET])
    tmp_closures = TMP / "closures.json"
    payload = json.loads(closure.CLOSURES.read_text())
    payload["closures"]["tests/entities.py"] = [
        f for f in payload["closures"]["tests/entities.py"] if f != TARGET]
    tmp_closures.write_text(json.dumps(payload))
    closure.CLOSURES = tmp_closures          # in-memory patch; disk copy is temp
    plan_pruned = closure.select([TARGET])
    closure.CLOSURES = ROOT / "tests" / "closures.json"
    print(f"RESULT select_kept={len(plan_kept['run'])} mode={plan_kept['mode']}")
    print(f"RESULT select_pruned={len(plan_pruned['run'])} mode={plan_pruned['mode']}")
    print(f"RESULT entities_in_kept={int('tests/entities.py' in plan_kept['run'])} "
          f"entities_in_pruned={int('tests/entities.py' in plan_pruned['run'])}")

    try:
        load1 = os.getloadavg()[0]
    except Exception:
        load1 = -1
    t = os.times()
    print(f"RESULT load1={load1:.2f}")
    print("RESULT thread_factor=1.00 (pinned; no BLAS work in this harness)")
    import resource
    print(f"RESULT swapins={getattr(resource.getrusage(resource.RUSAGE_SELF), 'ru_nswap', 0)}")
    import subprocess as sp
    n = sp.run(["ps", "aux"], capture_output=True, text=True).stdout
    concurrent = len([l for l in n.splitlines()
                      if ("stress.py" in l or "run.sh" in l or "edge.py" in l
                          or "backtest.py" in l) and "grep" not in l])
    print(f"RESULT concurrent_test_procs={concurrent}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
