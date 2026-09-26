"""D9 verify-v3 (round 9, lens V3) for D9-s2-02: (a) which per-cycle files the
per-PR CPU gate's solve path (tests/stress.py:build_case) executes at all, and
(b) the smallest multiple of the loop-thread share of a replay cycle that
tests/replay.py:cost_offenders turns red, solved from replay's OWN cost_figures
and COST_BUDGETS on figures measured here.

Metric (one line): (a) count of distinct functions, by file, entered (sys.setprofile
'call' events) during stress.build_case over 3 sweep cells; (b) k_min such that
cost_offenders({"cpu_ratio": r0 * (1 + (k - 1) * L)}) is non-empty, where r0 is
the clean cycle cpu_ratio and L the loop share of the budgeted cycle -- both
taken as arguments from a replay-driven measurement (defaults: this seat's
re-run of the finder's m2_loop_blind.py, r0=2.5946, L=0.1605).
Command:
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python \
      tools/audit/round9/D9/verify-v3/v3_s2_02_reach.py [--r0 2.5946 --loop-share 0.1605]
Instrumented symbols: tests/stress.py:build_case (profiled), tests/replay.py:
cost_offenders / COST_BUDGETS (called, not re-implemented).
Perturbation: --loop-share 0.5 (a cycle whose loop half dominates) -> k_min
DOWN toward 2; the file counts are the reach answer and do not move.
Expected: coordinator.py/sensor.py/topology.py functions entered = 0 (exact);
k_min ~3.4 at the defaults. Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _v3 as V  # noqa: E402
import argparse, collections
import stress
import replay

WATCH = ("coordinator.py", "sensor.py", "topology.py", "optimizer.py", "thermal_model.py")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--r0", type=float, default=2.5946)
    ap.add_argument("--loop-share", type=float, default=0.1605)
    a = ap.parse_args()
    seen = collections.defaultdict(set)

    def prof(frame, event, arg):
        if event == "call":
            fn = frame.f_code.co_filename
            if "custom_components/heatpump_optimizer/" in fn:
                seen[os.path.basename(fn)].add(frame.f_code.co_qualname)
    for spec in (dict(season="winter", two_zone=True, dhw=True),
                 dict(season="shoulder", two_zone=False, dhw=True, power_cap_kw=3.68),
                 dict(season="summer", two_zone=False, dhw=False, pv=True, tariff=True)):
        sys.setprofile(prof)
        try:
            stress.build_case(**spec)
        finally:
            sys.setprofile(None)
    for f in WATCH:
        V.R(f"stress_functions_entered.{f}", len(seen.get(f, ())), "count (exact)")
    V.R("stress_files_reached", len(seen), "files")
    budget = replay.COST_BUDGETS["synthetic-dhw-only.json"]
    k = 1.0
    while k < 50:
        if replay.cost_offenders({"cpu_ratio": a.r0 * (1 + (k - 1) * a.loop_share),
                                  "peak_kib": budget["peak_kib"] / 1.5}, budget):
            break
        k = round(k + 0.01, 2)
    V.R("replay_cpu_ratio_budget", budget["cpu_ratio"], "ref_solves")
    V.R("replay_clean_band_ok", not replay.cost_offenders({"cpu_ratio": a.r0, "peak_kib": budget["peak_kib"] / 1.5}, budget))
    V.R("k_min_loop_multiple_to_trip", k, f"x loop share (L={a.loop_share}, r0={a.r0})")
    V.R("whole_cycle_multiple_to_trip", round(budget["cpu_ratio"] / a.r0, 3), "x whole cycle")
    V.trailer()


if __name__ == "__main__":
    main()
