"""D9 round 4 / H7 -- what the stress gate's memory budget can and cannot see.

``tests/stress.py`` records ``rss_peak_mb`` and ``traced_peak_mb`` for all
fifty-one sweep scenarios and, in check mode, re-probes ``MEMORY_TOP_N``
of them in subprocesses and compares each against the committed table:

    rss fails   when  probe_rss  > recorded_rss + max(150.0,
                                    recorded_rss * (MEMORY_BUDGET_FACTOR - 1))
    traced fails when probe_traced > recorded_traced * MEMORY_BUDGET_FACTOR + 2

The same file states a detection target, ``DETECTION_TARGET`` (2.0), which
the CPU rules are sized against. This harness asks whether the memory
rules meet it.

METRIC: ``rss_multiple_required_to_fail(label)`` = the shipped threshold
above divided by the recorded peak, computed from the EXECUTED module
constants ``stress.MEMORY_BUDGET_FACTOR`` / ``stress.DETECTION_TARGET`` /
``stress.MEMORY_TOP_N`` and the committed ``tests/stress_budgets.json``;
``scenarios_where_2x_rss_passes`` = how many of the fifty-one would still
pass with their RSS peak doubled.

It is not left as arithmetic. Two arms are EXECUTED through the shipped
probe body (``stress.build_case`` under ``tracemalloc`` plus
``stress.rss_mb``, which is exactly what ``--memory-probe`` runs), in a
fresh subprocess each, on the recorded RSS leader:

  clean     the scenario as shipped
  inject2x  the same scenario, then a numpy allocation sized to double the
            process RSS watermark -- the synthetic 2x memory regression

and the shipped rule is then applied to both probes' outputs.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round4/D9/h7_memory_gate.py

EXPECTED (baseline 7dd68dd, table recorded_at in tests/stress_budgets.json):
  scenarios_recorded = 51, memory_top_n = 6, scenarios_probed = 6,
  min_rss_multiple_required_to_fail = 2.5 - 2.7,
  scenarios_where_2x_rss_passes = 51,
  inject2x_rss_rule_fires = False.
Tolerance: the multiples are exact rationals of committed numbers (+/- 0);
the probe MiB are PROVISIONAL.

PERTURBATION: ``H7_PERTURB=factor`` sets ``STRESS_MEMORY_FACTOR=1.05``
before importing stress. ``min_rss_multiple_required_to_fail`` must NOT
move (the 150 MiB floor dominates), which is itself the finding;
``H7_PERTURB=nofloor`` additionally evaluates the rule with the 150.0
floor removed, and then the multiple must fall to MEMORY_BUDGET_FACTOR.

COUNTS AND RATIOS ARE FINAL; probe MiB are PROVISIONAL.
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

PERTURB = os.environ.get("H7_PERTURB", "")
if PERTURB in ("factor", "nofloor"):
    os.environ["STRESS_MEMORY_FACTOR"] = "1.05"

import stress  # noqa: E402  (module-level __main__ guard: importing runs no sweep)

TABLE_PATH = "tests/stress_budgets.json"

PROBE_SRC = r'''
import json, os, sys, tracemalloc
sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
sys.path.insert(0, os.path.join(os.getcwd(), "tests", "hastub"))
sys.path.insert(0, os.path.join(os.getcwd(), "custom_components"))
import numpy as np
import stress
spec = json.loads(sys.argv[1])
inject = sys.argv[2] == "1"
tracemalloc.start()
stress.build_case(**spec)
if inject:
    base = stress.rss_mb()
    hold = np.zeros(int(base * 1024 * 1024 / 8), dtype=np.float64)
    hold[:] = 1.0
_cur, traced = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(json.dumps({"rss_mb": round(stress.rss_mb(), 1),
                  "traced_mb": round(traced / (1024.0 * 1024.0), 2)}))
'''


def rss_threshold(recorded_rss, floor=150.0):
    return recorded_rss + max(floor, recorded_rss * (stress.MEMORY_BUDGET_FACTOR - 1.0))


def traced_threshold(recorded_traced):
    return recorded_traced * stress.MEMORY_BUDGET_FACTOR + 2.0


def probe(spec, inject):
    out = subprocess.run(
        [sys.executable, "-c", PROBE_SRC, json.dumps(spec), "1" if inject else "0"],
        capture_output=True, text=True,
    )
    line = (out.stdout or "").strip().splitlines()
    if not line:
        raise RuntimeError((out.stderr or "no output")[-400:])
    return json.loads(line[-1])


def main():
    print(f"# baseline=7dd68dd  perturb={PERTURB or 'none'}")
    print(f"# procs_at_start={C.concurrent_procs()} load1={C.load1():.2f}")
    table = json.load(open(TABLE_PATH))
    scenarios = {k: v for k, v in table.items()
                 if isinstance(v, dict) and "rss_peak_mb" in v}
    C.result("scenarios_recorded", len(scenarios), "scenarios")
    C.result("memory_top_n", stress.MEMORY_TOP_N, "scenarios")
    C.result("memory_budget_factor", float(stress.MEMORY_BUDGET_FACTOR))
    C.result("detection_target", float(stress.DETECTION_TARGET))
    C.result("scenarios_never_memory_probed",
             len(scenarios) - stress.MEMORY_TOP_N, "scenarios")

    mults = {}
    tmults = {}
    for label, entry in scenarios.items():
        r = float(entry["rss_peak_mb"])
        t = float(entry["traced_peak_mb"])
        mults[label] = rss_threshold(r) / r
        tmults[label] = traced_threshold(t) / t
    lo = min(mults.values())
    hi = max(mults.values())
    C.result("min_rss_multiple_required_to_fail", float(lo))
    C.result("max_rss_multiple_required_to_fail", float(hi))
    C.result("scenarios_where_2x_rss_passes",
             sum(1 for m in mults.values() if m > stress.DETECTION_TARGET),
             "scenarios")
    C.result("min_traced_multiple_required_to_fail", float(min(tmults.values())))
    C.result("max_traced_multiple_required_to_fail", float(max(tmults.values())))
    C.result("scenarios_where_2x_traced_passes",
             sum(1 for m in tmults.values() if m > stress.DETECTION_TARGET),
             "scenarios")
    if PERTURB == "nofloor":
        nf = {l: rss_threshold(float(e["rss_peak_mb"]), floor=0.0)
              / float(e["rss_peak_mb"]) for l, e in scenarios.items()}
        C.result("nofloor_min_rss_multiple_required_to_fail", float(min(nf.values())))

    # the recorded RSS leader, probed for real through the shipped body
    leader = max(scenarios, key=lambda k: float(scenarios[k]["rss_peak_mb"]))
    C.result("rss_leader_label", leader)
    combos = {c["label"]: {k: v for k, v in c.items() if k != "label"}
              for c in stress.sweep_combinations()}
    spec = combos[leader]
    clean = probe(spec, inject=False)
    inj = probe(spec, inject=True)
    rec_rss = float(scenarios[leader]["rss_peak_mb"])
    rec_tr = float(scenarios[leader]["traced_peak_mb"])
    C.result("clean_probe_rss_mb_PROVISIONAL", float(clean["rss_mb"]), "MiB")
    C.result("clean_probe_traced_mb", float(clean["traced_mb"]), "MiB")
    C.result("inject2x_probe_rss_mb_PROVISIONAL", float(inj["rss_mb"]), "MiB")
    C.result("inject2x_rss_over_clean",
             float(inj["rss_mb"] / clean["rss_mb"]) if clean["rss_mb"] else
             float("nan"))
    C.result("rss_fail_threshold_mb", float(rss_threshold(rec_rss)), "MiB")
    C.result("clean_rss_rule_fires", clean["rss_mb"] > rss_threshold(rec_rss))
    C.result("inject2x_rss_rule_fires", inj["rss_mb"] > rss_threshold(rec_rss))
    C.result("traced_fail_threshold_mb", float(traced_threshold(rec_tr)), "MiB")
    C.result("clean_traced_rule_fires",
             clean["traced_mb"] > traced_threshold(rec_tr))
    C.result("inject2x_traced_rule_fires",
             inj["traced_mb"] > traced_threshold(rec_tr))
    C.telemetry()


if __name__ == "__main__":
    main()
