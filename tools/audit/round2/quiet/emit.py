#!/usr/bin/env python
"""Emit tools/audit/round2/QUIET.md and quiet.json from the quiet-window logs.

Every `quiet` value below is parsed out of the log named on the row; the
`original` is the fan-out value the finder's report.json / REPORT.md states.
`reproduced` applies the tolerance the report states (timing +-25 % unless the
report is tighter). Run from the export root:  python tools/audit/round2/quiet/emit.py
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
RND = os.path.dirname(HERE)

def vals(log):
    d = {}
    p = os.path.join(HERE, log)
    if not os.path.exists(p):
        return d
    for line in open(p, errors="replace"):
        if line.startswith("QUIET_"):
            k, _, v = line.rstrip("\n").partition("="); d[k] = v; continue
        m = re.match(r"RESULT (\S+?)=(\S+)(?: (.*))?$", line.rstrip("\n"))
        if not m: continue
        name, raw = m.group(1), m.group(2)
        try: v = float(raw)
        except ValueError: v = raw
        if name in d and name.endswith(".long_gap"): d[name] = f"{d[name]} | {raw}"
        else: d[name] = v
    return d

L = {n: vals(n + ".log") for n in (
    "D9-h1", "D9-h1b", "D9-h3", "D9-h3-run2", "D9-h3-run3", "D9-h3-run4",
    "D9-h4", "D9-h4-redo", "D9-h5", "D9-h7", "D0-race_grid", "D1-lifecycle", "D10-coverage")}

ROWS = []
def R(fid, harness, log, metric, original, tol, note="", quiet=None):
    """tol: 'exact' | float relative | None (reported, not gated)."""
    d = L[log]
    q = d.get(metric) if quiet is None else quiet
    rep = None
    if tol is not None and q is not None and original is not None:
        if tol == "exact":
            rep = (q == original)
        elif isinstance(original, tuple):          # an accepted range from the report
            lo, hi = original
            rep = (lo * (1 - tol) <= q <= hi * (1 + tol))
        else:
            rep = abs(q - original) <= abs(original) * tol
    ROWS.append({
        "id": fid, "harness": harness, "metric": metric,
        "original": list(original) if isinstance(original, tuple) else original,
        "quiet": q,
        "load1": d.get("RESULT_load1", d.get("load1")),
        "thread_factor": d.get("thread_factor"),
        "swapins": d.get("swapins"),
        "reproduced": rep,
        "tolerance": ("exact" if tol == "exact" else (f"+-{tol:.0%}" if isinstance(tol, float) else "reported, not gated")),
        "log": f"tools/audit/round2/quiet/{log}.log",
        "note": note,
    })

H1 = "tools/audit/round2/D9/h1_grad_equivalents.py"
H1B = "tools/audit/round2/D9/h1b_dhw_loops.py"
H3 = "tools/audit/round2/D9/h3_gil_hold.py"
H4 = "tools/audit/round2/D9/h4_loop_thread_work.py"
H5 = "tools/audit/round2/D9/h5_retained_bytes.py"
H7 = "tools/audit/round2/D9/h7_stress_gate.py"
RG = "tools/audit/round2/D0/race_grid.py --quiet"
LC = "tools/audit/round2/D1/lifecycle_realloop.py"
CS = "tools/audit/round2/D10/coverage_suite.sh"

# ---- D9-01: counts and ratios final, absolute CPU provisional
for m, o in (("pin_zero_range_two_zone_dhw.equivalents_per_gradient", 9221.55),
             ("two_zone_dhw.equivalents_per_gradient", 297.32),
             ("pin_zero_range.equivalents_per_gradient", 9294.55),
             ("dhw_cap_zero_range.equivalents_per_gradient", 9221.85),
             ("dhw_cap_one_step_zero_range.equivalents_per_gradient", 294.0),
             ("pin_zero_range_two_zone_dhw.simulate_step_calls", 1595328.0),
             ("dhw_cap_zero_range.simulate_step_calls", 1512384.0),
             ("two_zone_dhw.simulate_step_calls", 20736.0)):
    R("D9-01", H1, "D9-h1", m, o, "exact", "count: contention-immune")
for m, o in (("two_zone_dhw.solve_over_reference", 38.5),
             ("pin_zero_range_two_zone_dhw.solve_over_reference", 751.0),
             ("dhw_cap_zero_range.solve_over_reference", (711.0, 750.0)),
             ("dhw_cap_one_step_zero_range.solve_over_reference", 54.7),
             ("pin_zero_range.solve_over_reference", 39.1)):
    R("D9-01", H1, "D9-h1", m, o, 0.25, "CPU ratio against reference_solve")
for m, o in (("two_zone_dhw.solve_cpu", 908.0),
             ("pin_zero_range_two_zone_dhw.solve_cpu", 25046.0),
             ("dhw_cap_zero_range.solve_cpu", (17700.0, 23700.0)),
             ("dhw_cap_one_step_zero_range.solve_cpu", 1824.0),
             ("pin_zero_range.solve_cpu", 923.0)):
    R("D9-01", H1, "D9-h1", m, o, 0.25, "absolute CPU ms: the fan-out figure was inflated by contention")
R("D9-01", H1, "D9-h1", "reference_solve_cpu", (18.0, 33.0), 0.25, "the ruler itself; fan-out 18-33 ms")
# ---- D9-03
for m, o in (("two_zone_dhw.scalar_steps_per_gradient", 201.32),
             ("perturb_memo_two_zone_dhw.scalar_steps_per_gradient", 100.66),
             ("perturb_memo_two_zone_dhw.batch_rows_per_gradient", 96.0),
             ("two_zone_dhw.nfev", 103.0), ("two_zone_dhw.njev", 103.0)):
    R("D9-03", H1, "D9-h1", m, o, "exact", "count")
R("D9-03", H1, "D9-h1", "perturb_memo_two_zone_dhw.solve_cpu", 789.0, 0.25, "absolute CPU ms")
# ---- D9 non-finding (single-zone ratios)
R("D9-NF-solve-ratios", H1, "D9-h1", "single_zone_nodhw.solve_over_reference", 2.72, 0.25)
R("D9-NF-solve-ratios", H1, "D9-h1", "single_zone_dhw.solve_over_reference", 6.10, 0.25)
# ---- D9-04
for m, o in (("two_zone_dhw.simulate_dhw_only_per_planning_call", 64.0),
             ("two_zone_dhw.tank_steps_per_planning_call", 6144.0),
             ("two_zone_dhw.compute_cop_dhw_calls", 14168.0),
             ("perturb_h48_two_zone_dhw.simulate_dhw_only_per_planning_call", 118.0),
             ("perturb_h48_two_zone_dhw.tank_steps_per_planning_call", 22656.0)):
    R("D9-04", H1B, "D9-h1b", m, o, "exact", "count")
R("D9-04", H1B, "D9-h1b", "single_zone_dhw.planner_share_of_solve", 0.6296, 0.15, "share, report tolerance +-15 %")
R("D9-04", H1B, "D9-h1b", "two_zone_dhw.minrun_share_of_planner", 0.48, 0.15, "share")
R("D9-04", H1B, "D9-h1b", "two_zone_dhw.planner_over_reference", (3.4, 3.8), 0.15, "ratio to reference_solve")
R("D9-04", H1B, "D9-h1b", "two_zone_dhw.planner_cpu", (70.0, 76.0), 0.25, "absolute CPU ms")
R("D9-04", H1B, "D9-h1b", "perturb_h48_two_zone_dhw.planner_over_reference", 13.5, 0.25, "perturbation 24->48 h")
R("D9-04", H1B, "D9-h1b", "perturb_h48_two_zone_dhw.planner_cpu", 266.0, 0.25, "absolute CPU ms")
# ---- D9-05 (canonical sample = run4, the only one with load1 < 1.5 at both ends)
for m, o, t, n in (
    ("two_zone_dhw.starvation_share", 0.967, 0.05, "the finding's headline; report tolerance +-5 %"),
    ("dhw_cap_zero_range.starvation_share", 0.998, 0.05, ""),
    ("single_zone_dhw.starvation_share", 0.748, 0.05, ""),
    ("idle_control.starvation_share", 0.0, 0.05, "null control"),
    ("two_zone_dhw.wall", 795.0, 0.25, "wall ms"),
    ("dhw_cap_zero_range.wall", 14700.0, 0.25, "wall ms"),
    ("idle_control.ticks_per_second", 779.0, 0.25, "null control"),
    ("two_zone_dhw.ticks_per_second", 74.0, 0.25, "loop turn rate under the solve"),
    ("two_zone_dhw.gap_p50", 13.3, 0.25, "median loop gap"),
    ("two_zone_dhw.gap_p99", 35.8, 0.25, ""),
    ("two_zone_dhw.longest_gil_hold", 39.4, 0.25,
     "report range 39-75 ms; four quiet samples give 265/313/376/412 ms - the defect is LARGER than reported"),
    ("perturb_switch50ms_two_zone_dhw.starvation_share", 0.961, 0.05, "perturbation arm"),
):
    R("D9-05", H3, "D9-h3-run4", m, o, t, n)
R("D9-05", H3, "D9-h3", "perturb_switch50ms_two_zone_dhw.longest_gil_hold", 82.9, 0.25,
  "perturbation arm; only sampled in run 1")
# ---- D9 non-finding h4 (canonical = the redo; the first run was at load1 3.54)
for m, o, n in (("two_zone_dhw.cycle3.loop_thread_cpu", 3.08, ""),
                ("two_zone_dhw.cycle3.executor_cpu", 712.6, "absolute CPU ms"),
                ("two_zone_dhw.cycle3.stage._build_data_dict", 1.31, ""),
                ("perturb_h48_two_zone_dhw.cycle3.loop_thread_cpu", 4.36, ""),
                ("perturb_price_tiles.cycle3.loop_thread_cpu", 3.73, "")):
    R("D9-NF-loop-work", H4, "D9-h4-redo", m, o, 0.25, n)
R("D9-NF-loop-work", H4, "D9-h4-redo", "two_zone_dhw.cycle3.loop_over_executor", 0.0043, 0.25,
  "the ratio the non-finding rests on")
# ---- D9 non-finding h5
for m, o, t, n in (("ru_maxrss_after_12_cycles", 99991552.0, 0.25, "RSS"),
                   ("ru_maxrss_after_48_cycles", 101924864.0, 0.25, "RSS"),
                   ("deep_after_cycle1", 361805.0, "exact", "deterministic byte count"),
                   ("deep_after_cycle16", 381989.0, "exact", "deterministic byte count"),
                   ("deep_slope_second_half", (521.0, 773.0), 0.25, "B/cycle"),
                   ("traced_slope_second_half", 4385.0, 0.25, "B/cycle"),
                   ("growth_total_traced_excl_harness", 3354.0, 0.25, "B/cycle"),
                   ("growth_own_total", 1681.0, 0.25, "B/cycle"),
                   ("store_saves_per_cycle.total", 2.125, "exact", ""),
                   ("store_bytes_per_cycle.total", (7041.0, 9605.0), 0.25, "")):
    R("D9-NF-retained-bytes", H5, "D9-h5", m, o, t, n)
# ---- D9-02
for m, o, t in (("smallest_detectable_uniform_regression", 4.685, 0.20),
                ("plain.worst_ratio", 298.8, 0.20), ("plain.sweep_ratio", 50.7, 0.20),
                ("plain.median_ratio", 33.9, 0.20), ("injected_2x.worst_ratio", 590.5, 0.20),
                ("injected_2x.sweep_ratio", 105.2, 0.20),
                ("plain.per_scenario_tripped", 0.0, "exact"), ("plain.sweep_tripped", 0.0, "exact"),
                ("injected_2x.per_scenario_tripped", 0.0, "exact"),
                ("injected_2x.sweep_tripped", 0.0, "exact"),
                ("ci_sets_stress_ratio", 0.0, "exact"), ("tests_memory_instrumentation", 0.0, "exact")):
    R("D9-02", H7, "D9-h7", m, o, t, "report tolerance +-20 % on the ratios")
# ---- D0-02
R("D0-02", RG, "D0-race_grid", "production_cpu_total", 111.80, 0.25,
  "the one provisional number in D0; the quiet box is FASTER, which is the expected direction")
R("D0-02", RG, "D0-race_grid", "wall_total", 780.0, 0.25, "report: about 13 min under load")
for m, o in (("restart_improves_tz", 15.0), ("pg_above_pgtol_tz", 64.0), ("cells_with_gap_tz", 49.0),
             ("step0_differs_among_gap_cells", 28.0)):
    R("D0-02", RG, "D0-race_grid", m, o, "exact", "count: contention-immune")
for m, o in (("mean_restart_gap_sek_tz", 0.0519), ("mean_gap_sek_tz", 0.1088),
             ("max_gap_sek_tz", 2.5099), ("null_flat_mean_gap_sek_tz", 0.1553),
             ("nonflat_mean_gap_sek_tz", 0.1022), ("loo_mean_gap_pct_tz", 0.232)):
    R("D0-02", RG, "D0-race_grid", m, o, "exact", "SEK gap, report tolerance +-1e-3: bit-identical")
# ---- D1-02
for m, o, n in (("midsolve_eager.sched_zombie_service_calls", 3.0, "the finding's headline value"),
                ("sched_midsolve_zombie_actuations", 1.0, ""), ("sched_midsolve_zombie_saves", 2.0, ""),
                ("notready_leaked_listeners", 10.0, ""), ("notready_leaked_mqtt_subs", 5.0, ""),
                ("notready_zombie_coordinators", 5.0, ""), ("total_escaped_exceptions", 0.0, "")):
    R("D1-02", LC, "D1-lifecycle", m, o, "exact", n)
R("D1-02", LC, "D1-lifecycle", "midsolve_lazy.sched_zombie_service_calls", 6.0, "exact",
  "DID NOT REPRODUCE: 3, not 6. The lazy arm issued one zombie cycle here, not two; "
  "the eager arm (the finding's headline) reproduced exactly")
# ---- D10-14
for m, o, t, n in (("coverage_total_pct", 88.4, 0.011, "report tolerance +-1.0 pt"),
                   ("coverage_config_flow_pct", 86.4, 0.012, "+-1.0 pt"),
                   ("coverage_statements", 12877.0, "exact", ""),
                   ("coverage_modules_ge95", 20.0, "exact", ""),
                   ("coverage_missing", 1493.0, 0.01, ""),
                   ("scripts_nonzero_exit", 2.0, "exact", "entities.py and golden.py, both export artefacts"),
                   ("wall_s", 1818.0, 0.25, "the provisional number; quiet box is 46 % faster")):
    R("D10-14", CS, "D10-coverage", m, o, t, n)

# ---------------- Part 2
D3 = []
for mid, fid in (("M31", "D3-01"), ("M19", "D3-02"), ("M13", "D3-03"),
                 ("M32", "D3-04"), ("M21", "D3-05"), ("M30", "D3-06")):
    log = f"D3-{mid}.gate.log"
    txt = open(os.path.join(HERE, log), errors="replace").read()
    survived = bool(re.search(r"^ALL TEST SCRIPTS PASSED$", txt, re.M))
    fails = re.findall(r"^>>> FAILED: (.*)$", txt, re.M)
    scripts = re.findall(r"^ +\d+s +(.*)$", txt, re.M)
    wall = re.search(r"^QUIET_WALL_S=(\d+)", txt, re.M)
    D3.append({
        "mutant": mid, "finding": fid, "survived": survived,
        "killed_by": fails,
        "log": f"tools/audit/round2/quiet/{log}",
        "wall_s": int(wall.group(1)) if wall else None,
        "scripts_run": len([s for s in scripts if not s.startswith("TOTAL")]),
    })

json.dump({"retaken": ROWS, "d3_confirmed": D3},
          open(os.path.join(RND, "quiet.json"), "w"), indent=1)
n_ok = sum(1 for r in ROWS if r["reproduced"] is True)
n_no = sum(1 for r in ROWS if r["reproduced"] is False)
print(f"quiet.json: {len(ROWS)} rows ({n_ok} reproduced, {n_no} not), {len(D3)} D3 rows")
for r in ROWS:
    if r["reproduced"] is False:
        print(f"  NOT REPRODUCED  {r['id']:22s} {r['metric']:52s} {r['original']} -> {r['quiet']}")
