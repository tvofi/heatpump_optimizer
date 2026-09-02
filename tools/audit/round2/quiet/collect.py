#!/usr/bin/env python
"""Build quiet.json / the QUIET.md tables from the quiet-window logs.

Each retake row names the finding, the harness, the original (fan-out) value
as the report states it, the quiet value parsed from the RESULT lines of the
log in this directory, and whether it reproduced within the report's
tolerance (timing: +-25 % unless the report says otherwise; counts: exact).

    python tools/audit/round2/quiet/collect.py   # from the export root

Writes tools/audit/round2/quiet.json and prints the markdown tables.
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "quiet.json")


def parse(log: str) -> dict:
    """RESULT name=value unit -> {name: value}; QUIET_* headers too."""
    d: dict = {}
    path = os.path.join(HERE, log)
    if not os.path.exists(path):
        return d
    for line in open(path, errors="replace"):
        line = line.rstrip("\n")
        if line.startswith("QUIET_"):
            k, _, v = line.partition("=")
            d[k] = v
            continue
        m = re.match(r"RESULT (\S+?)=(\S+)(?: (.*))?$", line)
        if not m:
            continue
        name, val, unit = m.group(1), m.group(2), m.group(3) or ""
        try:
            num = float(val)
        except ValueError:
            num = val
        # h3 prints several long_gap lines per label: keep them all
        if name in d and name.endswith(".long_gap"):
            d[name] = f"{d[name]}; {val}"
        else:
            d[name] = num
        d[name + "#unit"] = unit
    return d


def within(orig: float, quiet: float, rel: float) -> bool:
    if orig == 0:
        return abs(quiet) <= rel
    return abs(quiet - orig) / abs(orig) <= rel


def fmt(v) -> str:
    if isinstance(v, float):
        return f"{v:.4g}"
    return str(v)


ROWS: list[dict] = []


def row(id_, harness, log, metrics, tolerance_note, extra=None):
    """metrics: list of (name-in-log, original-value, rel-tolerance or 'exact' or None)."""
    d = parse(log)
    original, quiet, verdicts = {}, {}, []
    for name, orig, tol in metrics:
        q = d.get(name)
        original[name] = orig
        quiet[name] = q
        if tol is None or q is None or orig is None:
            continue
        if tol == "exact":
            ok = (q == orig)
        else:
            ok = within(float(orig), float(q), tol)
        verdicts.append(ok)
    if extra:
        quiet.update(extra)
    reproduced = all(verdicts) if verdicts else None
    ROWS.append({
        "id": id_,
        "harness": harness,
        "original": original,
        "quiet": quiet,
        "load1": d.get("load1"),
        "load1_before": d.get("QUIET_LOAD_BEFORE"),
        "thread_factor": d.get("thread_factor"),
        "swapins": d.get("swapins"),
        "wall_s": d.get("QUIET_WALL_S"),
        "log": f"tools/audit/round2/quiet/{log}",
        "reproduced": reproduced,
        "tolerance": tolerance_note,
    })
    return d


# ---------------------------------------------------------------- D9 (worktree audit-r2-D9)
# Originals: tools/audit/round2/D9/report.json + REPORT.md tables (fan-out, load1 2.3-9.4).
T = 0.25
row("D9-01 (h1: CPU ms, provisional)", "tools/audit/round2/D9/h1_grad_equivalents.py", "D9-h1.log", [
    ("two_zone_dhw.solve_cpu", 908.0, T),
    ("pin_zero_range.solve_cpu", 923.0, T),
    ("pin_zero_range_two_zone_dhw.solve_cpu", 25046.0, T),
    ("dhw_cap_zero_range.solve_cpu", 20700.0, T),          # report: 17.7-23.7 s
    ("dhw_cap_one_step_zero_range.solve_cpu", 1824.0, T),
], "timing +-25 % (absolute CPU ms; the report calls these provisional)")
row("D9-01 (h1: ratios and counts, final)", "tools/audit/round2/D9/h1_grad_equivalents.py", "D9-h1.log", [
    ("pin_zero_range_two_zone_dhw.equivalents_per_gradient", 9221.55, "exact"),
    ("two_zone_dhw.equivalents_per_gradient", 297.32, "exact"),
    ("pin_zero_range_two_zone_dhw.simulate_step_calls", 1595328.0, "exact"),
    ("two_zone_dhw.solve_over_reference", 38.5, T),
    ("pin_zero_range_two_zone_dhw.solve_over_reference", 751.0, T),
    ("dhw_cap_zero_range.solve_over_reference", 730.0, T),   # report: 711-750
    ("dhw_cap_one_step_zero_range.solve_over_reference", 54.7, T),
    ("pin_zero_range.solve_over_reference", 39.1, T),
], "counts exact; CPU ratios +-25 %")
row("D9-03 (h1: memo perturbation, CPU provisional)", "tools/audit/round2/D9/h1_grad_equivalents.py", "D9-h1.log", [
    ("two_zone_dhw.scalar_steps_per_gradient", 201.32, "exact"),
    ("perturb_memo_two_zone_dhw.scalar_steps_per_gradient", 100.66, "exact"),
    ("perturb_memo_two_zone_dhw.batch_rows_per_gradient", 96.0, "exact"),
    ("perturb_memo_two_zone_dhw.solve_cpu", 789.0, T),
], "counts exact; memo solve CPU +-25 %")
row("D9 non-finding (h1: single-zone ratios)", "tools/audit/round2/D9/h1_grad_equivalents.py", "D9-h1.log", [
    ("single_zone_nodhw.solve_over_reference", 2.72, T),
    ("single_zone_dhw.solve_over_reference", 6.10, T),
    ("single_zone_nodhw.solve_cpu", 64.0, T),
    ("single_zone_dhw.solve_cpu", 144.0, T),
], "ratios/CPU +-25 %")
row("D9-04 (h1b: planner share and CPU)", "tools/audit/round2/D9/h1b_dhw_loops.py", "D9-h1b.log", [
    ("single_zone_dhw.planner_share_of_solve", 0.6296, 0.15),
    ("two_zone_dhw.planner_cpu", 73.0, T),                    # report: 70-76 ms
    ("two_zone_dhw.planner_over_reference", 3.6, T),          # report: 3.4-3.8
    ("two_zone_dhw.simulate_dhw_only_per_planning_call", 64.0, "exact"),
    ("two_zone_dhw.tank_steps_per_planning_call", 6144.0, "exact"),
    ("two_zone_dhw.minrun_share_of_planner", 0.48, 0.15),
    ("perturb_h48_two_zone_dhw.planner_cpu", 266.0, T),
    ("perturb_h48_two_zone_dhw.planner_over_reference", 13.5, T),
], "share +-15 % (report); counts exact; CPU +-25 %")
row("D9-05 (h3: wall, provisional)", "tools/audit/round2/D9/h3_gil_hold.py", "D9-h3.log", [
    ("two_zone_dhw.starvation_share", 0.967, 0.05),
    ("dhw_cap_zero_range.starvation_share", 0.998, 0.05),
    ("single_zone_dhw.starvation_share", 0.748, 0.05),
    ("idle_control.starvation_share", 0.0, 0.05),
    ("two_zone_dhw.wall", 795.0, T),
    ("dhw_cap_zero_range.wall", 14700.0, T),
    ("two_zone_dhw.ticks_per_second", 74.0, None),
    ("two_zone_dhw.gap_p50", 13.3, None),
    ("two_zone_dhw.longest_gil_hold", 39.4, None),
    ("perturb_switch50ms_two_zone_dhw.longest_gil_hold", 82.9, None),
    ("perturb_switch50ms_two_zone_dhw.starvation_share", 0.961, 0.05),
    ("idle_control.ticks_per_second", 779.0, T),
    ("idle_control.longest_gil_hold", 2.1, None),
], "share +-5 % (report); wall +-25 %; gap distribution reported, not gated")
row("D9 non-finding (h4: loop-thread work)", "tools/audit/round2/D9/h4_loop_thread_work.py", "D9-h4-redo.log", [
    ("two_zone_dhw.cycle3.loop_thread_cpu", 3.08, T),
    ("two_zone_dhw.cycle3.executor_cpu", 712.6, T),
    ("two_zone_dhw.cycle3.loop_over_executor", 0.0043, T),
    ("two_zone_dhw.cycle3.stage._build_data_dict", 1.31, T),
    ("perturb_h48_two_zone_dhw.cycle3.loop_thread_cpu", 4.36, T),
    ("perturb_price_tiles.cycle3.loop_thread_cpu", 3.73, T),
], "CPU +-25 %")
row("D9 non-finding (h5: RSS and traced growth)", "tools/audit/round2/D9/h5_retained_bytes.py", "D9-h5.log", [
    ("ru_maxrss_after_12_cycles", 99991552.0, T),
    ("ru_maxrss_after_48_cycles", 101924864.0, T),
    ("deep_slope_second_half", 650.0, None),                  # report: 521-773 B/cycle
    ("traced_slope_second_half", 4385.0, None),
    ("growth_own_total", 1681.0, None),
    ("deep_after_cycle1", 361805.0, "exact"),
    ("deep_after_cycle16", 381989.0, "exact"),
], "RSS +-25 %; deterministic byte counts exact; slopes reported")
row("D9-02 (h7: stress-gate ratios)", "tools/audit/round2/D9/h7_stress_gate.py", "D9-h7.log", [
    ("smallest_detectable_uniform_regression", 4.685, 0.20),
    ("plain.worst_ratio", 298.8, 0.20),
    ("plain.sweep_ratio", 50.7, 0.20),
    ("plain.median_ratio", 33.9, 0.20),
    ("injected_2x.worst_ratio", 590.5, 0.20),
    ("injected_2x.sweep_ratio", 105.2, 0.20),
    ("injected_2x.per_scenario_tripped", 0.0, "exact"),
    ("injected_2x.sweep_tripped", 0.0, "exact"),
    ("plain.per_scenario_tripped", 0.0, "exact"),
    ("plain.sweep_tripped", 0.0, "exact"),
], "ratios +-20 % (report); tripped counts exact")

# ---------------------------------------------------------------- D0 (worktree audit-r2-D0)
row("D0-02 (race_grid --quiet: production CPU, provisional)", "tools/audit/round2/D0/race_grid.py --quiet", "D0-race_grid.log", [
    ("production_cpu_total", 111.80, T),
    ("restart_improves_tz", 15.0, "exact"),
    ("mean_restart_gap_sek_tz", 0.0519, None),
    ("pg_above_pgtol_tz", 64.0, "exact"),
    ("cells_with_gap_tz", 49.0, "exact"),
    ("mean_gap_sek_tz", 0.1088, None),
    ("null_flat_mean_gap_sek_tz", 0.1553, None),
    ("wall_total", 780.0, None),                              # report: about 13 min under load
], "CPU +-25 %; counts exact; SEK gaps +-1e-3 (checked in the table)")

# ---------------------------------------------------------------- D1 (export)
row("D1-02 (lifecycle_realloop: counts; the window's wall is a solve's duration)", "tools/audit/round2/D1/lifecycle_realloop.py", "D1-lifecycle.log", [
    ("midsolve_eager.sched_zombie_service_calls", 3.0, "exact"),
    ("sched_midsolve_zombie_actuations", 1.0, "exact"),
    ("sched_midsolve_zombie_saves", 2.0, "exact"),
    ("midsolve_lazy.sched_zombie_service_calls", 6.0, "exact"),
    ("notready_leaked_listeners", 10.0, "exact"),
], "counts exact; no timing RESULT in this harness (thread_factor is meaningless: CPU on worker threads)")

# ---------------------------------------------------------------- D10 (export)
row("D10-14 (coverage_suite.sh: scripts wall, provisional)", "tools/audit/round2/D10/coverage_suite.sh", "D10-coverage.log", [
    ("wall_s", 1818.0, T),
    ("coverage_total_pct", 88.4, None),
    ("coverage_config_flow_pct", 86.4, None),
    ("coverage_statements", 12877.0, "exact"),
    ("scripts_nonzero_exit", 2.0, "exact"),
], "wall +-25 %; coverage +-1.0 pt (checked in the table); counts exact")


def main():
    d3 = []
    for mid in ("M31", "M19", "M13", "M32", "M21", "M30", "M15"):
        log = f"D3-{mid}.gate.log"
        path = os.path.join(HERE, log)
        if not os.path.exists(path):
            continue
        text = open(path, errors="replace").read()
        survived = "\nALL TEST SCRIPTS PASSED" in text
        fails = re.findall(r"^>>> FAILED: (.*)$", text, re.M)
        other = re.findall(r"^(\d+ TEST SCRIPT\(S\) FAILED|LANE DID NOT FINISH.*|TEST NEVER RAN.*|UNWIRED TEST.*)$", text, re.M)
        m = re.search(r"^QUIET_WALL_S=(\d+)", text, re.M)
        d3.append({
            "mutant": mid,
            "survived": survived,
            "killed_by": fails + other,
            "log": f"tools/audit/round2/quiet/{log}",
            "wall_s": int(m.group(1)) if m else None,
        })
    json.dump({"retaken": ROWS, "d3_confirmed": d3}, open(OUT, "w"), indent=1)
    print(f"wrote {OUT}: {len(ROWS)} retake rows, {len(d3)} D3 rows")


if __name__ == "__main__":
    main()
