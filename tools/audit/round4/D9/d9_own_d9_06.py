"""VERIFIER-OWN harness for D9-06 (seat verify-0-1, round 4).

Re-measures D9-06 with instruments independent of the finder's h7:
  * h7 read the constants by importing ``stress``; this harness re-derives
    them from the SOURCE TEXT of ``tests/stress.py`` (regex over the
    ``MEMORY_BUDGET_FACTOR`` / ``DETECTION_TARGET`` / ``MEMORY_TOP_N``
    definitions) and from ``tests/stress_budgets.json`` directly.
  * h7 executed the probe body in its own subprocess wrapper; this harness
    launches the gate's own entry point ``tests/stress.py --memory-probe``
    in a subprocess -- byte-for-byte the code path a gate run exercises.

METRIC DEFINITIONS:
  v1_min_rss_multiple_required_to_fail = min over recorded scenarios of
      (recorded + max(150, recorded*(MBF-1))) / recorded   (rational, FINAL)
  v1_scenarios_2x_passes = count of scenarios whose multiple > 2.0
  v1_injected_rss_rule_fires = whether the probe RSS of the injected arm
      exceeds the shipped threshold for winter/pv (executed)

REQUIRES the D9V1_INJECT edit in tests/stress.py (this worktree only;
restored byte-identical after). The edit is inert unless D9V1_INJECT=1 and
the spec is exactly winter/pv (two_zone, dhw, pv, no tariff, cycling 0.0,
no building, 24 h).

COMMAND (from the repository root; lock held; step 2 is separate):

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round4/D9/d9_own_d9_06.py

    # then the confirming full-gate run (about 9 min):
    D9V1_INJECT=1 PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 ... \
      python3 tests/stress.py

EXPECTED: v1_min_rss_multiple_required_to_fail = 2.529 (exact rational);
v1_scenarios_2x_passes = 51; v1_injected_rss_rule_fires = False with the
probe reporting ~196 MiB (2x the 98.1 record).
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
import re  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402

ROOT = os.getcwd()
SRC = open(os.path.join(ROOT, "tests", "stress.py")).read()


def _const(name):
    m = re.search(
        rf'^{name}\s*=\s*float\(os\.environ\.get\([^)]*"([0-9.]+)"\)\)',
        SRC, re.M,
    )
    if m:
        return float(m.group(1))
    m = re.search(rf'^{name}\s*=\s*int\(os\.environ\.get\([^)]*"(\d+)"\)\)',
                  SRC, re.M)
    if m:
        return int(m.group(1))
    raise AssertionError(f"cannot read {name} from stress.py source")


MBF = _const("MEMORY_BUDGET_FACTOR")
DT = _const("DETECTION_TARGET")
TOPN = _const("MEMORY_TOP_N")

# the rule text as it appears in the check body (not the module constants)
RULE_PRESENT = bool(
    re.search(
        r"rss_peak > recorded_rss \+ max\(\s*150\.0, "
        r"recorded_rss \* \(MEMORY_BUDGET_FACTOR - 1\.0\)", SRC)
    and re.search(
        r"traced_peak > recorded_traced \* MEMORY_BUDGET_FACTOR \+ 2\.0",
        SRC)
)


def result(name, value, unit=""):
    text = f"{value:.6g}" if isinstance(value, float) else str(value)
    print(f"RESULT {name}={text} {unit}".rstrip(), flush=True)


def load1():
    try:
        return float(os.getloadavg()[0])
    except OSError:
        return float("nan")


def concurrent_procs():
    out = subprocess.run(
        ["ps", "aux"], capture_output=True, text=True, timeout=20
    ).stdout
    n = 0
    for line in out.splitlines():
        if "grep" in line:
            continue
        if "stress.py" in line or "tests/run.sh" in line:
            n += 1
    return n


def probe(spec, inject):
    env = dict(os.environ)
    env["PYTHONPATH"] = (
        os.path.join(ROOT, "tests", "hastub") + os.pathsep
        + os.path.join(ROOT, "custom_components")
    )
    if inject:
        env["D9V1_INJECT"] = "1"
    else:
        env.pop("D9V1_INJECT", None)
    out = subprocess.run(
        [sys.executable, os.path.join(ROOT, "tests", "stress.py"),
         "--memory-probe", json.dumps(spec)],
        capture_output=True, text=True, env=env,
    )
    lines = (out.stdout or "").strip().splitlines()
    if not lines:
        raise RuntimeError((out.stderr or "no output")[-400:])
    return json.loads(lines[-1])


def main():
    print(f"# verifier-own D9-06 harness; MBF={MBF} DT={DT} TOPN={TOPN} "
          f"from stress.py source text")
    print(f"# procs_at_start={concurrent_procs()} load1={load1():.2f}")
    result("v1_rule_text_present_in_source", RULE_PRESENT)
    result("v1_memory_budget_factor", MBF)
    result("v1_detection_target", DT)
    result("v1_memory_top_n", TOPN)

    table = json.load(open(os.path.join(ROOT, "tests", "stress_budgets.json")))
    sc = {k: v for k, v in table.items()
          if isinstance(v, dict) and "rss_peak_mb" in v}
    result("v1_scenarios_recorded", len(sc), "scenarios")
    mults = {
        k: (float(v["rss_peak_mb"])
            + max(150.0, float(v["rss_peak_mb"]) * (MBF - 1.0)))
        / float(v["rss_peak_mb"])
        for k, v in sc.items()
    }
    tmults = {
        k: (float(v["traced_peak_mb"]) * MBF + 2.0) / float(v["traced_peak_mb"])
        for k, v in sc.items()
    }
    result("v1_min_rss_multiple_required_to_fail", min(mults.values()))
    result("v1_max_rss_multiple_required_to_fail", max(mults.values()))
    result("v1_scenarios_2x_rss_passes",
           sum(1 for m in mults.values() if m > DT), "scenarios")
    result("v1_min_traced_multiple_required_to_fail", min(tmults.values()))
    result("v1_scenarios_2x_traced_passes",
           sum(1 for m in tmults.values() if m > DT), "scenarios")
    result("v1_scenarios_never_probed_in_check_mode",
           len(sc) - TOPN, "scenarios")

    # --- executed arms through the gate's own --memory-probe entry point ---
    winter_pv = {"season": "winter", "two_zone": True, "dhw": True,
                 "tariff": False, "pv": True, "cycling": 0.0}
    winter_cycle = {"season": "winter", "two_zone": True, "dhw": True,
                    "tariff": False, "pv": False, "cycling": 1.0}
    clean = probe(winter_pv, inject=False)
    inj = probe(winter_pv, inject=True)
    offtgt = probe(winter_cycle, inject=True)  # env set, wrong scenario
    rec_rss = float(sc["winter/pv"]["rss_peak_mb"])
    rec_tr = float(sc["winter/pv"]["traced_peak_mb"])
    thr_rss = rec_rss + max(150.0, rec_rss * (MBF - 1.0))
    thr_tr = rec_tr * MBF + 2.0

    result("v1_clean_probe_rss_mb", float(clean["rss_mb"]), "MiB")
    result("v1_clean_probe_traced_mb", float(clean["traced_mb"]), "MiB")
    result("v1_injected_probe_rss_mb", float(inj["rss_mb"]), "MiB")
    result("v1_injected_probe_traced_mb", float(inj["traced_mb"]), "MiB")
    result("v1_injected_rss_over_recorded",
           float(inj["rss_mb"] / rec_rss))
    result("v1_injected_traced_over_recorded",
           float(inj["traced_mb"] / rec_tr))
    result("v1_offtarget_probe_rss_mb", float(offtgt["rss_mb"]), "MiB")
    result("v1_offtarget_inert",
           offtgt["rss_mb"] < 120.0 and offtgt["traced_mb"] < 5.0)
    result("v1_rss_fail_threshold_mb", float(thr_rss), "MiB")
    result("v1_clean_rss_rule_fires", clean["rss_mb"] > thr_rss)
    result("v1_injected_rss_rule_fires", inj["rss_mb"] > thr_rss)
    result("v1_injected_traced_rule_fires", inj["traced_mb"] > thr_tr)
    result("thread_factor", float("nan"))  # no timing metric; see report
    result("load1", load1())
    result("concurrent_gate_procs", concurrent_procs())


if __name__ == "__main__":
    main()
