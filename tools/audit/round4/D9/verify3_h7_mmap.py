"""D9 round 4 / verifier 3 -- the RSS arm's blind spot, executed standalone.

D9-06's finder arm injected a numpy allocation; tracemalloc sees it, so the
traced rule fired and only the RSS rule's silence carried the finding. The
quiet window closed this through the full gate with an anonymous mmap (an
RSS-resident, PyMem-invisible allocation). This harness reproduces that
blind-spot arm standalone, through the SHIPPED probe body, and applies both
shipped rules to the result.

METRIC (one line): whether stress.py's shipped RSS and traced rules fire on
the recorded RSS leader (winter/pv) when the probe retains an anonymous,
page-touched mmap sized to take its RSS watermark to 2x the recorded peak.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round4/D9/verify3_h7_mmap.py

EXPECTED (baseline 7dd68dd, committed tests/stress_budgets.json):
  mmap2x_rss_over_recorded = 1.9 - 2.2 (the mmap targets 2x the recorded
  98.1 MiB; the probe baseline adds noise)
  mmap2x_traced_over_recorded = 0.9 - 1.1 (the mmap is invisible to
  tracemalloc, so traced stays at the clean peak)
  mmap2x_rss_rule_fires = False, mmap2x_traced_rule_fires = False
Baseline SHA 7dd68dd327fe3dbfb09f3bd0fe38910c58877697; 8-core M1, 8 GB.
"""
from __future__ import annotations

import os

for _t in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_t, "1")

import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round4", "D9"))

import d9common as C  # noqa: E402

import stress  # noqa: E402  (__main__ guard: importing runs no sweep)

PROBE_SRC = r'''
import json, mmap, os, sys, tracemalloc
sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
sys.path.insert(0, os.path.join(os.getcwd(), "tests", "hastub"))
sys.path.insert(0, os.path.join(os.getcwd(), "custom_components"))
import stress
spec = json.loads(sys.argv[1])
target_mb = float(sys.argv[2])
tracemalloc.start()
stress.build_case(**spec)
# an anonymous, page-touched mmap: resident (RSS sees it) but outside PyMem
# (tracemalloc does not) -- stress.py:1512's documented blind spot. Pages
# are touched in 1 MiB chunks so no large PyMem allocation ever exists.
cur = stress.rss_mb()
need = max(0.0, target_mb - cur)
if need > 0:
    m = mmap.mmap(-1, int(need * 1024 * 1024))
    chunk = b"\x01" * (1024 * 1024)
    for off in range(0, len(m) - len(chunk) + 1, len(chunk)):
        m[off:off + len(chunk)] = chunk
    m.flush()
_cur, traced = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(json.dumps({"rss_mb": round(stress.rss_mb(), 1),
                  "traced_mb": round(traced / (1024.0 * 1024.0), 2)}))
'''


def probe(spec, target_mb):
    out = subprocess.run(
        [sys.executable, "-c", PROBE_SRC, json.dumps(spec), str(target_mb)],
        capture_output=True, text=True,
    )
    lines = (out.stdout or "").strip().splitlines()
    if not lines:
        raise RuntimeError((out.stderr or "no output")[-400:])
    return json.loads(lines[-1])


def main():
    print("# baseline=7dd68dd  verifier-3 mmap blind-spot arm")
    print(f"# procs_at_start={C.concurrent_procs()} load1={C.load1():.2f}")
    table = json.load(open("tests/stress_budgets.json"))
    scenarios = {k: v for k, v in table.items()
                 if isinstance(v, dict) and "rss_peak_mb" in v}
    leader = max(scenarios, key=lambda k: float(scenarios[k]["rss_peak_mb"]))
    rec_rss = float(scenarios[leader]["rss_peak_mb"])
    rec_tr = float(scenarios[leader]["traced_peak_mb"])
    combos = {c["label"]: {k: v for k, v in c.items() if k != "label"}
              for c in stress.sweep_combinations()}
    spec = combos[leader]
    clean = probe(spec, 0.0)
    inj = probe(spec, 2.0 * rec_rss)
    rss_thr = rec_rss + max(150.0, rec_rss * (stress.MEMORY_BUDGET_FACTOR - 1.0))
    tr_thr = rec_tr * stress.MEMORY_BUDGET_FACTOR + 2.0
    C.result("leader", leader)
    C.result("recorded_rss_mb", rec_rss, "MiB")
    C.result("recorded_traced_mb", rec_tr, "MiB")
    C.result("clean_probe_rss_mb_PROVISIONAL", float(clean["rss_mb"]), "MiB")
    C.result("clean_probe_traced_mb", float(clean["traced_mb"]), "MiB")
    C.result("mmap2x_probe_rss_mb_PROVISIONAL", float(inj["rss_mb"]), "MiB")
    C.result("mmap2x_probe_traced_mb", float(inj["traced_mb"]), "MiB")
    C.result("mmap2x_rss_over_recorded", float(inj["rss_mb"] / rec_rss))
    C.result("mmap2x_traced_over_recorded", float(inj["traced_mb"] / rec_tr))
    C.result("rss_fail_threshold_mb", float(rss_thr), "MiB")
    C.result("mmap2x_rss_rule_fires", bool(inj["rss_mb"] > rss_thr))
    C.result("traced_fail_threshold_mb", float(tr_thr), "MiB")
    C.result("mmap2x_traced_rule_fires", bool(inj["traced_mb"] > tr_thr))
    C.telemetry()


if __name__ == "__main__":
    main()
