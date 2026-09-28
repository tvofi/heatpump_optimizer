#!/usr/bin/env python3
# METRIC (one line): count of entries in tests/closures.json's committed
# closures whose path is not an existing file ("phantom" entries), split into
# provable-at-baseline (paths outside tools/audit/round*, which the round
# export never strips) and export-ambiguous (under tools/audit/round*, which
# prepare_baseline.sh strips by design); plus select()'s mode and run-set size
# for a diff that re-creates the provable phantom path
# tests/record_status.py, before and after pruning that entry.
#
# COMMAND (from the repository root):
#   PYTHONPATH=tests/hastub python3 tools/audit/round5/D3/seat-b/phantoms.py
#
# EXPECTED (baseline 1cc89e020fff9040a9d0090a27bf22bc1dd497f0, round-5 export,
# Apple M1, Python 3.11): RESULT phantom_total=199, phantom_baseline_provable=1
# (tests/entities.py -> tests/record_status.py), entities_refs_record_status=0
# (tests/entities.py contains no reference to record_status), select_mode_kept
# =scoped select_run_kept=1, select_mode_pruned=full select_run_pruned=24.
# Counts are contention-immune.
#
# INSTRUMENTED SYMBOLS: tests/closures.json's closure entries (the committed
# table itself), via tests/closure.py:select applied to a temp-pruned copy;
# the loader-side proof is tests/entities.py's source text (zero references
# to record_status) against its committed closure entry.
#
# PERTURBATION (judge runs it): prune tests/record_status.py from
# tests/entities.py's closure in the temp copy and re-run -> the selection for
# a diff that re-adds tests/record_status.py flips MODE: SCOPED (1 script) ->
# FULL (24 scripts): the safety rule "an unmeasured file is not a safe skip"
# fires only once the phantom entry is gone.
#
# NULL CONTROL: the same select() with the entry present stays SCOPED with
# entities.py the sole selection -- the flip is caused by the phantom entry
# alone, nothing else in the temp copy differs.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import shutil
import sys
from pathlib import Path

SEAT = Path(__file__).resolve().parent
ROOT = SEAT.parents[4]
TMP = Path("/tmp/audit-5/tmp/d3b/phantoms")
sys.path.insert(0, str(ROOT / "tests"))

import closure  # tests/closure.py, importable read-only

PHANTOM = "tests/record_status.py"


def main() -> int:
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)

    closures = json.loads(closure.CLOSURES.read_text())["closures"]
    total = provable = 0
    provable_list = []
    for s, files in sorted(closures.items()):
        for f in files:
            if not (ROOT / f).is_file():
                total += 1
                if not f.startswith("tools/audit/round"):
                    provable += 1
                    provable_list.append(f"{s} -> {f}")
    print(f"RESULT phantom_total={total}")
    print(f"RESULT phantom_baseline_provable={provable}")
    for p in provable_list:
        print(f"  provable: {p}")

    # the loader-side proof: entities.py has no reference to the file its
    # committed closure claims it reads
    src = (ROOT / "tests" / "entities.py").read_text()
    print(f"RESULT entities_refs_record_status={src.count('record_status')}")

    # the merge-side mechanism: a full fold of a fresh record that does NOT
    # read the phantom still keeps the committed entry (never-shrink union),
    # and nothing in merge/check filters committed entries for existence
    record = {"script": "tests/entities.py", "rc": 0, "seconds": 1.0,
              "files": [f for f in closures["tests/entities.py"]
                        if f != PHANTOM and (ROOT / f).is_file()],
              "spawned": [], "how": "audithook+sys.modules",
              "argv": ["tests/entities.py"]}
    recdir = TMP / "records"
    recdir.mkdir()
    (recdir / "entities.py.json").write_text(json.dumps(record))
    # partial merge against a temp copy of the committed file
    tmp_closures = TMP / "closures.json"
    shutil.copy(closure.CLOSURES, tmp_closures)
    closure.CLOSURES = tmp_closures
    rc = closure.merge(recdir, tmp_closures, partial=True)
    merged = json.loads(tmp_closures.read_text())["closures"]
    closure.CLOSURES = ROOT / "tests" / "closures.json"
    print(f"RESULT merge_keeps_phantom="
          f"{int(PHANTOM in merged.get('tests/entities.py', []))} merge_rc={rc}")

    # the select-side perturbation: re-added phantom file, entry present
    plan_kept = closure.select([PHANTOM])
    payload = json.loads((ROOT / "tests" / "closures.json").read_text())
    payload["closures"]["tests/entities.py"] = [
        f for f in payload["closures"]["tests/entities.py"] if f != PHANTOM]
    tmp2 = TMP / "closures_pruned.json"
    tmp2.write_text(json.dumps(payload))
    closure.CLOSURES = tmp2
    plan_pruned = closure.select([PHANTOM])
    closure.CLOSURES = ROOT / "tests" / "closures.json"
    print(f"RESULT select_mode_kept={plan_kept['mode']} "
          f"select_run_kept={len(plan_kept['run'])}")
    print(f"RESULT select_mode_pruned={plan_pruned['mode']} "
          f"select_run_pruned={len(plan_pruned['run'])}")

    try:
        load1 = os.getloadavg()[0]
    except Exception:
        load1 = -1
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
