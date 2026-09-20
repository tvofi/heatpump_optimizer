"""D9 round 4 / H7 -- what the stress gate's memory budget can and cannot see.

HISTORY (#950 D9-INST re-record, 2026-09-14): at the 7dd68dd baseline this
harness measured the pre-#949 rule -- RSS failed at
``probe_rss > recorded_rss + max(150.0, recorded_rss*(factor-1))`` and the
traced arm at ``recorded*factor + 2`` -- and found it blind: the 150 MiB
floor dominated every record, a scenario had to reach 2.53-2.64x its
record before failing, and all fifty-one passed a doubling (D9-06,
verified). PR #989 (2026-09-14) replaced the rule: the check budgets the
SCENARIO-ATTRIBUTABLE component -- probe watermark minus a same-run
empty-probe baseline -- under a pure multiplicative
``MEMORY_BUDGET_FACTOR``, with no additive floor on either axis. This
harness now reads the rule from the module itself
(``stress.rss_attrib_fail_threshold`` / ``stress.traced_fail_threshold``)
and probes through the gate's own entry point
(``stress._run_memory_probe``, the exact interpreter/env the memory pass
uses), so it cannot re-transcribe a rule that has moved; only the
injection arm keeps a local probe child, because the shipped entry has no
injection hook, and that child is the shipped body plus the allocation.

METRIC: ``attrib_multiple_required_to_fail(label)`` =
``stress.rss_attrib_fail_threshold(recorded rss_attrib_mb) /
recorded rss_attrib_mb``, computed from the EXECUTED module functions and
the committed ``tests/stress_budgets.json``; ``scenarios_where_2x_fails``
= how many of the fifty-one would fail if their attributable component
doubled (multiple <= DETECTION_TARGET).

It is not left as arithmetic. Three arms are EXECUTED on the recorded
attributable-RSS leader, through the shipped entry points:

  baseline  the empty probe (``--memory-baseline``): interpreter+numpy,
            subtracted from every probe below
  clean     the scenario as shipped (``--memory-probe``)
  inject2x  the shipped probe body plus a numpy allocation sized to double
            the probe's RSS WATERMARK -- the round-4 demonstration's own
            synthetic regression, kept verbatim (see the sizing note at
            INJECT_SRC); against the attributable rule it lands the
            component several times over its clean draw

and the module's own rule is then applied to all three.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round4/D9/h7_memory_gate.py

EXPECTED (re-recorded at ad7bcdf 2026-09-14, post-#989; the 7dd68dd
expectations -- 2.5 - 2.7x to fail, a doubling passing all 51 -- are the
finding's frozen record and history now):
  scenarios_recorded = 51, memory_top_n = 6,
  min/max_attrib_rss_multiple_required_to_fail = 1.5 (+/- 0),
  scenarios_where_2x_attrib_rss_fails = 51,
  inject2x_attrib_rule_fires = True.
Tolerance: the multiples are exact rationals of committed numbers (+/- 0);
the probe MiB are PROVISIONAL.

live-header: this header is maintained against the tree; harness_headers.py executes it.

FINAL RESULT (exact; #1005 review follow-up -- the marker above puts
this harness in tests/harness_headers.py's executed set, which compares
these lines to the run):
    RESULT scenarios_recorded=51
    RESULT memory_top_n=6
    RESULT memory_budget_factor=1.5
    RESULT detection_target=2
    RESULT min_attrib_rss_multiple_required_to_fail=1.5
    RESULT max_attrib_rss_multiple_required_to_fail=1.5
    RESULT scenarios_where_2x_attrib_rss_fails=51
    RESULT min_traced_multiple_required_to_fail=1.5
    RESULT max_traced_multiple_required_to_fail=1.5
    RESULT scenarios_where_2x_traced_fails=51
    RESULT scenarios_memory_probed=6
    RESULT scenarios_never_memory_probed=45
    RESULT attrib_leader_label=typical_slab/winter
    RESULT attrib_fail_threshold_mb=25.05
    RESULT traced_fail_threshold_mb=5.145
    RESULT clean_attrib_rule_fires=False
    RESULT inject2x_attrib_rule_fires=True
Every pinned value derives from tests/stress_budgets.json or the stress
module's constants -- exact rationals, no timing, no BLAS -- except the
two rule-fires booleans, whose PROVISIONAL inputs sat 3.4-3.6x from the
threshold at the re-record (clean 7.4 MiB vs 26.55, inject2x 90.1 vs
26.55); the probe MiB themselves stay unpinned. A landing that re-records
stress_budgets.json or moves the rule owes this block the same
re-record -- that drift alarm is the marker's purpose.

PERTURBATION: ``H7_PERTURB=factor`` sets ``STRESS_MEMORY_FACTOR=1.05``
before importing stress, and ``min_attrib_rss_multiple_required_to_fail``
must FALL to 1.05 -- the direction the finding's perturbation could not
move, because the retired 150 MiB floor pinned it at 2.53. The old
``nofloor`` arm is gone with the floor it removed.

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
if PERTURB == "factor":
    os.environ["STRESS_MEMORY_FACTOR"] = "1.05"

import stress  # noqa: E402  (module-level __main__ guard: importing runs no sweep)

TABLE_PATH = "tests/stress_budgets.json"

# The shipped probe body plus the injection: identical imports, the same
# ``stress.build_case`` / ``stress.rss_mb`` calls ``--memory-probe`` makes,
# then a numpy allocation sized to double the probe's RSS WATERMARK -- the
# round-4 demonstration's own construction, kept verbatim. The sizing is
# on the watermark, not the attributable component, because ru_maxrss is
# a high-water mark: an allocation smaller than the headroom under the
# build_case peak is absorbed and moves nothing (measured: a
# recorded-component-sized injection landed the attributable draw at 0.37x
# clean). Doubling the watermark lands the attributable component several
# times over its clean draw, which is what the rule must catch.
INJECT_SRC = r'''
import json, os, sys, tracemalloc
sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
sys.path.insert(0, os.path.join(os.getcwd(), "tests", "hastub"))
sys.path.insert(0, os.path.join(os.getcwd(), "custom_components"))
import numpy as np
import stress
spec = json.loads(sys.argv[1])
tracemalloc.start()
stress.build_case(**spec)
base = stress.rss_mb()
hold = np.zeros(int(base * 1024 * 1024 / 8), dtype=np.float64)
hold[:] = 1.0
_cur, traced = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(json.dumps({"rss_mb": round(stress.rss_mb(), 1),
                  "traced_mb": round(traced / (1024.0 * 1024.0), 2)}))
'''


def probe_env() -> dict:
    """The env the memory pass itself launches probes under."""
    return stress._memory_probe_env()


def inject_probe(spec: dict) -> dict:
    out = subprocess.run(
        [sys.executable, "-c", INJECT_SRC, json.dumps(spec)],
        capture_output=True, text=True, env=probe_env(),
    )
    line = (out.stdout or "").strip().splitlines()
    if not line:
        raise RuntimeError((out.stderr or "no output")[-400:])
    return json.loads(line[-1])


def memory_probe_labels(table: dict) -> list[str]:
    """Mirror of stress.py's nested ``_memory_probe_labels``: half the
    check-exposed set by traced peak, half by RSS watermark, from the
    committed table, stable order, deduped. Transcribed because the
    original is nested inside the check flow and not importable; the
    threshold rules above are NOT transcribed -- they are the module's."""
    half = max(1, stress.MEMORY_TOP_N // 2)
    chosen: list[str] = []
    for key in ("traced_peak_mb", "rss_peak_mb"):
        ranked = sorted(
            (-float(entry[key]), label)
            for label, entry in table.items()
            if isinstance(entry, dict) and float(entry.get(key, 0.0)) > 0.0
        )
        taken = 0
        for _peak, label in ranked:
            if taken >= half:
                break
            if label in chosen:
                continue
            chosen.append(label)
            taken += 1
    return chosen


def main():
    t0 = C.span_start()
    print(f"# baseline=7dd68dd  perturb={PERTURB or 'none'}  "
          f"# re-recorded 2026-09-14 at ad7bcdf, post-#989")
    print(f"# procs_at_start={C.concurrent_procs()} load1={C.load1():.2f}")
    table = json.load(open(TABLE_PATH))
    scenarios = {k: v for k, v in table.items()
                 if isinstance(v, dict) and "rss_attrib_mb" in v}
    C.result("scenarios_recorded", len(scenarios), "scenarios")
    C.result("memory_top_n", stress.MEMORY_TOP_N, "scenarios")
    C.result("memory_budget_factor", float(stress.MEMORY_BUDGET_FACTOR))
    C.result("detection_target", float(stress.DETECTION_TARGET))
    probed = memory_probe_labels(scenarios)
    C.result("scenarios_memory_probed", len(probed), "scenarios")
    C.result("scenarios_never_memory_probed",
             len(scenarios) - len(probed), "scenarios")

    mults = {}
    tmults = {}
    for label, entry in scenarios.items():
        rec_attrib = float(entry["rss_attrib_mb"])
        rec_traced = float(entry["traced_peak_mb"])
        mults[label] = stress.rss_attrib_fail_threshold(rec_attrib) / rec_attrib
        tmults[label] = stress.traced_fail_threshold(rec_traced) / rec_traced
    C.result("min_attrib_rss_multiple_required_to_fail", float(min(mults.values())))
    C.result("max_attrib_rss_multiple_required_to_fail", float(max(mults.values())))
    C.result("scenarios_where_2x_attrib_rss_fails",
             sum(1 for m in mults.values() if m <= stress.DETECTION_TARGET),
             "scenarios")
    C.result("min_traced_multiple_required_to_fail", float(min(tmults.values())))
    C.result("max_traced_multiple_required_to_fail", float(max(tmults.values())))
    C.result("scenarios_where_2x_traced_fails",
             sum(1 for m in tmults.values() if m <= stress.DETECTION_TARGET),
             "scenarios")

    # the recorded attributable-RSS leader, probed for real through the
    # gate's own entry points
    leader = max(scenarios, key=lambda k: float(scenarios[k]["rss_attrib_mb"]))
    rec_attrib = float(scenarios[leader]["rss_attrib_mb"])
    rec_traced = float(scenarios[leader]["traced_peak_mb"])
    C.result("attrib_leader_label", leader)
    combos = {c["label"]: {k: v for k, v in c.items() if k != "label"}
              for c in stress.sweep_combinations()}
    spec = combos[leader]
    env = probe_env()
    baseline = stress._run_memory_probe(["--memory-baseline"], env)
    clean = stress._run_memory_probe(["--memory-probe", json.dumps(spec)], env)
    inj = inject_probe(spec)
    C.result("empty_probe_baseline_rss_mb_PROVISIONAL",
             float(baseline["rss_mb"]), "MiB")
    clean_attrib = max(0.0, clean["rss_mb"] - baseline["rss_mb"])
    inj_attrib = max(0.0, inj["rss_mb"] - baseline["rss_mb"])
    C.result("clean_probe_rss_mb_PROVISIONAL", float(clean["rss_mb"]), "MiB")
    C.result("clean_attrib_rss_mb_PROVISIONAL", float(clean_attrib), "MiB")
    C.result("inject2x_probe_rss_mb_PROVISIONAL", float(inj["rss_mb"]), "MiB")
    C.result("inject2x_attrib_rss_mb_PROVISIONAL", float(inj_attrib), "MiB")
    C.result("inject2x_attrib_over_clean",
             float(inj_attrib / clean_attrib) if clean_attrib
             else float("nan"))
    C.result("attrib_fail_threshold_mb",
             float(stress.rss_attrib_fail_threshold(rec_attrib)), "MiB")
    C.result("clean_attrib_rule_fires",
             clean_attrib > stress.rss_attrib_fail_threshold(rec_attrib))
    C.result("inject2x_attrib_rule_fires",
             inj_attrib > stress.rss_attrib_fail_threshold(rec_attrib))
    C.result("traced_fail_threshold_mb",
             float(stress.traced_fail_threshold(rec_traced)), "MiB")
    C.result("clean_traced_rule_fires",
             clean["traced_mb"] > stress.traced_fail_threshold(rec_traced))
    C.result("inject2x_traced_rule_fires",
             inj["traced_mb"] > stress.traced_fail_threshold(rec_traced))
    # #950 D9-INST: the whole-span factor, parent-side; every probe is a
    # separate process launched under the pinned env this harness set in
    # its own first lines, so the parent's ratio is the signal.
    C.telemetry(C.span_factor(t0))


if __name__ == "__main__":
    main()
