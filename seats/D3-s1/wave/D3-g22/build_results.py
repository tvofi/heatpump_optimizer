#!/usr/bin/env python3
# Box D3-g22: writes results/<key>.json for every key of keys.tsv whose gate record gates/<key>.json exists and whose
# result is not yet written (or all of them with --force). The probe numbers below are the ones the probes print
# (each deterministic; re-run with its command). Command, from the tree root:
#   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/build_results.py [--force]
import json
import re
import sys
from pathlib import Path

W = Path(__file__).resolve().parent
S1 = W.parent.parent
PD = "dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes"
FG = "dev/audit/rounds/round11/D3/s1/fullgate.py"
CMD = "PYTHONPATH=tests/hastub python3 " + PD + "/"
REACH = CMD + "reach_scan.py"
SEAM = ("awk -F'\\t' '$6==\"gate\"' dev/audit/rounds/round11/D3/s1/SURVIVORS.tsv  (the wave list; this box's keys: "
        "dev/audit/rounds/round11/D3/s1/wave/D3-g22/keys.tsv)")

# key -> probe outcome. cls: candidate | equivalent-candidate (applies to SURVIVED / RED-AS-NULL gates only).
P = {
 "ea0b9abd134c33cd": dict(probe="probe_ea0b9abd.py", cls="equivalent-candidate",
   baseline="short_outdoor (power 4, outdoor 3): 4 values (pads with outdoor[-1])", mutant="IndexError",
   inputs=["power 4 / outdoor 3 (moves: 4 -> IndexError)", "power 48 / outdoor 48 linspace (equal_len_delta=0)",
           "7 real solves (reach_scan.py: disp_outdoor_shorter_than_power=0)"],
   why="unreachable through production: the one caller (optimizer.py:3881) passes h.outdoor_temps and space_power, "
       "both n_steps long, so the padding branch never runs (reach 0 of 7 real solves)",
   should="tests/features.py (R9-F2.1 P3 block, ~68727) calls _power_to_displace_schedule only with equal-length "
          "series; no check passes an outdoor series shorter than the power schedule"),
 "fa67e0922f51edda": dict(probe="probe_fa67e092.py", cls="equivalent-candidate",
   baseline="max_abs_delta=0.0 displace", mutant="identical",
   inputs=["out_t 0.0, -0.0, 1e-300, -1e-300, 5e-324, nan, -10, 5 x power zeros / 3 kW / ramp (24 cells)"],
   why="equivalent mutant: at out_t == 0 the branch adds min(2, |0|*0.08) = 0.0",
   should="none: no check can distinguish (equivalent)"),
 "ef9a378b671791ca": dict(probe="probe_ef9a378b.py", cls="candidate",
   baseline="tau 0.01 h (alpha 2.5 unclipped): [-19.6 x4, 20.0 x8, -19.6 x12]", mutant="alternating -20.0 / 20.0 every step; "
   "max_abs_delta=40.0 displace, steps_moved=20 of 24",
   inputs=["tau 0.01/0.1 h (alpha 2.5): delta 40.0, 20 steps", "tau 0.2 h (alpha 1.25): delta 2.5, 10 steps",
           "tau 0.25 h (config-flow floor, alpha 1.0): delta 0.0", "tau 1.5 h (default): delta 0.0"],
   why="moves on a set_thermal_parameters input the service admits (ecl110_pid_time_constant_hours >= 0.01 h, "
       "services.py:516, mapped at coordinator.py:2739, floored to 0.1 h at thermal_model.py:725; the step is a fixed "
       "15 min), and the schedule is the ECL110 displace command get_current_action reads (optimizer.py:6581-6585)",
   should="tests/features.py: no check drives _power_to_displace_schedule with ecl110_pid_tau_hours below dt_hours "
          "(features.py:50928 sets 0.6 h, alpha 0.42; the R9-F2.1 block ~68727 uses the default 1.5 h); the assertion "
          "it lacks: with tau < dt the filtered schedule equals the clipped raw command (alpha clamped to 1), "
          "i.e. no step-to-step overshoot"),
 "1897b1e8f0e09c02": dict(probe="probe_1897b1e8.py", cls="equivalent-candidate",
   baseline="admitted windows: max_abs_delta=0.0 over 576 cells", mutant="refused windows (d_min 2 / d_max -2): "
   "max_abs_delta=2.0",
   inputs=["windows (-20,20) (-30,0) (0,30) (0,0) (-0.5,0.5) (-30,30) x tau 0.01/0.25/1.5/24 h x 4 power x 3 outdoor "
           "x 2 forecast factors: delta 0.0", "windows (2,10) and (-10,-2), refused by config flow and service: delta 2.0"],
   why="equivalent on every window the config flow (config_flow.py:1888, [-30,0] / [0,30]) and the service "
       "(services.py:517-522) admit: alpha is clipped to [0,1] at line 6504 and the EWMA starts at 0, which every "
       "admitted window contains, so it never leaves the window; it moves only for a window excluding 0",
   should="none reachable: a check would need a displace window excluding 0, which no input surface admits"),
 "c859178ad2524ff8": dict(probe="probe_c859178a.py", cls="equivalent-candidate",
   baseline="n-long trajectory breaching at step 0: power_cap_breach_c=1.0", mutant="0.0",
   inputs=["trajectory n long (moves 1.0 -> 0.0)", "trajectory n+1 long (null_delta=0)",
           "7 real solves (reach_scan.py: breach_traj_eq_n=0)"],
   why="unreachable through production: result.sensor_trajectory carries n+1 entries in every solve (traj 49 for n 48)",
   should="none reachable: the n-long trajectory is never produced"),
 "e658b77d3e5ca8f6": dict(probe="probe_e658b77d.py", cls="equivalent-candidate",
   baseline="empty temp_min_bounds: power_cap_breach_c=0.0", mutant="ValueError (np.max of an empty array)",
   inputs=["temp_min_bounds [] with n 0 (moves)", "4-step plan with bounds (null_delta=0)",
           "7 real solves (reach_scan.py: tmin 48, traj 49)"],
   why="unreachable through production: steps = min(n, n) >= 1 in every solve",
   should="none reachable: steps == 0 needs an empty horizon"),
 "6ab21fd9f9fe4953": dict(probe="probe_6ab21fd9.py", cls="equivalent-candidate",
   baseline="requirement None + DHW trajectory set: dhw_floor_breach_c=0.0", mutant="IndexError",
   inputs=["4 cells requirement None/set x trajectory []/set (cells_moved=1: requirement None with a trajectory)",
           "real solve, DHW-disabled install with dhw_blocked=True (requirement None, trajectory []): 0.0 both arms"],
   why="unreachable through production: a DHW trajectory comes only from the DHW solve, which sets _dhw_requirement in "
       "the same pass (optimizer.py:5747); the reachable requirement-None case (DHW off, mode blocks hot water) has an "
       "empty trajectory and publishes 0.0 under both arms (reach_scan.py: breach_dhw_req_none_with_traj=0)",
   should="none reachable"),
 "1d0c70b3b63230eb": dict(probe="probe_1d0c70b3.py", cls="equivalent-candidate",
   baseline="DHW trajectory as long as the requirement, short at step 0: dhw_floor_breach_c=5.0", mutant="0.0",
   inputs=["trajectory n / requirement n (moves 5.0 -> 0.0)", "trajectory n+1 / requirement n (null_delta=0)",
           "7 real solves (reach_scan.py: breach_dhw_traj_eq_req=0)"],
   why="unreachable through production: the DHW trajectory carries n+1 entries against an n-entry requirement",
   should="none reachable"),
 "d600d4886444a718": dict(probe="probe_d600d488.py", cls="equivalent-candidate",
   baseline="trajectory n+2 / requirement n: dhw_floor_breach_c=2.0", mutant="ValueError (broadcast)",
   inputs=["trajectory n+2 (moves)", "trajectory n+1 (null_delta=0)", "trajectory shorter than requirement (delta 0)",
           "7 real solves (reach_scan.py: breach_dhw_planned_longer_than_req_after_trim=0)"],
   why="unreachable through production: after the index-0 trim the trajectory and requirement are both n long",
   should="none reachable"),
 "6e420d1efdf4895b": dict(probe="probe_6e420d1e.py", cls="equivalent-candidate",
   baseline="empty requirement: dhw_floor_breach_c=0.0", mutant="ValueError",
   inputs=["requirement [] (moves)", "one-entry trajectory (trimmed? no: size 1 not > 4; steps 1; delta 0)",
           "production shape (null_delta=0)"],
   why="unreachable through production: the requirement carries n_steps >= 1 entries (reach_scan.py req 48)",
   should="none reachable"),
 "7da20bf51cc217e6": dict(probe="probe_7da20bf5.py", cls="candidate",
   baseline="real DHW-blocked solve, tank 60 C: dhw_floor_breach_c=0.0 (tank 65 C: 0.0)",
   mutant="tank 60 C: -1.394; tank 65 C: -5.908",
   inputs=["tank 45 C: 11.739 both arms (null)", "tank 55 C: 3.121 both arms", "tank 60 C: 0.0 -> -1.394",
           "tank 65 C: 0.0 -> -5.908"],
   why="moves in a real HeatPumpOptimizer.optimize with SolveLimits.dhw_blocked=True (a pump-mode entity in a "
       "heating-only mode) whenever the tank coasts above its requirement; the method's own comment documents "
       "\"zero when the tank coasted through anyway\"",
   should="tests/features.py v5.3.0 mode-block section (_mb_dhw = _mb_run(dhw_blocked=True), ~36841): its checks read "
          "dhw_power_schedule, power_schedule, dhw_reasons and mode_blocked_* but never predictive_info"
          "['dhw_floor_breach_c']; no script in the closure reads the key (grep dhw_floor_breach tests/ is empty). The "
          "assertion it lacks: a DHW-blocked plan whose tank stays above its requirement publishes "
          "dhw_floor_breach_c == 0.0 (and >= 0 always)"),
 "1f1dc504455f17da": dict(probe="probe_1f1dc504.py", cls="equivalent-candidate",
   baseline="max_abs_delta=0.0 kWh", mutant="identical at the published 3 dp",
   inputs=["surplus exactly 1e-6 everywhere / at one step, 0, 9.99e-7, 1.01e-6, 3 kW x power 0 / 6 kW / ramp x "
           "dt 0.25 / 1.0 (36 cells)"],
   why="equivalent at the published value: only a surplus of exactly 1e-6 kW differs and its served energy, at most "
       "n*1e-6*dt kWh, rounds to 0.000",
   should="none: no published value distinguishes"),
 "9fe0782a9839475e": dict(probe="probe_9fe0782a.py", cls="equivalent-candidate",
   baseline="power 10 / surplus 8: 1.5 kWh", mutant="ValueError (broadcast)",
   inputs=["power longer than surplus (moves)", "power shorter (delta 0)", "48/48 (null_delta=0.0)",
           "7 real solves (reach_scan.py: pvsc_power_longer_than_surplus=0)"],
   why="unreachable through production: _prepare_series slices/pads the surplus to exactly n_steps "
       "(optimizer.py:4695-4707) and every caller passes an n_steps power schedule",
   should="none reachable"),
 "7c2ae6b70ec6acb7": dict(probe="probe_7c2ae6b7.py", cls="equivalent-candidate",
   baseline="surplus max exactly 1e-6 kW: pv_surplus [] (each forecast step's pv_surplus null)",
   mutant="[0.0] * 48",
   inputs=["exactly 1e-6 everywhere (moves: [] -> 48 x 0.0)", "zeros, 9.99e-7, 1.01e-6, 3 kW block (null_delta=0)"],
   why="moves only when the surplus maximum is exactly 1e-6 kW (1 mW), a measure-zero value of "
       "clip(production - load, 0) (pv.py:80-91); its consequence is a published 0.0 instead of null per step; "
       "recorded as equivalent-candidate with the moving input disclosed so a later seat may promote it",
   should="none practical: a check would pin the threshold's tie at 1e-6"),
 "97da0984453a53bb": dict(probe="probe_97da0984.py", cls="equivalent-candidate",
   baseline="room trajectory n long, forced-off pins at the floor: space releases [0, 1, 2]", mutant="IndexError",
   inputs=["room n long (moves)", "room n+1 long (null_delta=0)",
           "real pinned solve (reach_scan.py pins_off arm: rel_room_not_n_plus_1=0)"],
   why="unreachable through production: the loop runs i < n and the room trajectory has n+1 entries, so "
       "i + 1 <= n < len(room) and the else-branch never runs",
   should="none reachable"),
 "af94ce8be7140e87": dict(probe="probe_af94ce8b.py", cls="equivalent-candidate",
   baseline="temp_min_bounds n-1 long: space releases [0, 1, 2]", mutant="IndexError",
   inputs=["bounds n-1 long (moves)", "bounds n long (null_delta=0)",
           "real pinned solve (reach_scan.py: rel_bounds_shorter_than_power=0)"],
   why="unreachable through production: temp_min_bounds carries n_steps entries for an n-step power schedule",
   should="none reachable"),
}

CAND = {
 "ef9a378b671791ca": dict(
   title="No check runs the ECL110 displace filter with a PID time constant below the 15-min step; dropping the alpha "
         "clamp is unseen",
   severity="medium",
   metric="max |baseline - mutant| of the published displace schedule (displace units) for a 0 -> max -> 0 power step "
          "at -5 C with ecl110_pid_time_constant_hours = 0.01 h (alpha 2.5)",
   value=40.0, unit="displace", direction="up",
   prop="The ECL110 displace schedule's first-order filter gain is clamped to [0, 1], so a PID time constant below "
        "the step length tracks the command without overshoot",
   symbol="custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._power_to_displace_schedule",
   null="tau 1.5 h (default) and 0.25 h (config-flow floor): 0.0 displace"),
 "7da20bf51cc217e6": dict(
   title="No check reads dhw_floor_breach_c; a DHW-blocked plan could publish a negative tank shortfall unseen",
   severity="low",
   metric="dhw_floor_breach_c (C) published by a real DHW-blocked solve (features.py v5.3.0 January scenario) with the "
          "tank starting at 60 C",
   value=-1.394, unit="C", direction="down",
   prop="dhw_floor_breach_c is the worst tank shortfall clipped at zero: never negative, 0.0 when the tank coasts "
        "through a hot-water block",
   symbol="custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._publish_breach_reports",
   null="tank 45 C (a real shortfall, 11.739 C both arms): 0.0 C"),
}


def keys():
    rows = (W / "keys.tsv").read_text().splitlines()
    head = rows[0].split("\t")
    return [dict(zip(head, r.split("\t"))) for r in rows[1:] if r.strip()]


def build(row, force=False):
    k = row["key"]
    out = W / "results" / f"{k}.json"
    g = W / "gates" / f"{k}.json"
    if not g.exists() or (out.exists() and not force):
        return None
    gate = json.loads(g.read_text())
    mut = json.loads((S1 / "state" / "results" / "complete" / f"{k}.json").read_text())["mutant"]
    verdict = gate.get("verdict")
    p = P[k]
    rec = {
        "key": k,
        "site": f"{row['file']}:{row['line']} {row['kind']}",
        "patch": f"{mut['old'].strip()} -> {mut['new'].strip()}",
        "function": row["function"],
        "cluster": row["cluster"],
        "gate": {x: gate.get(x) for x in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end",
                                           "failed_scripts", "summary", "command", "provisional", "cap_s", "note")
                 if x in gate},
        "gate_record": f"dev/audit/rounds/round11/D3/s1/wave/D3-g22/gates/{k}.json",
        "gate_command": f"PYTHONPATH=tests/hastub python3 {FG} run --src {row['src']} --key {k}",
        "m4_carried": row["m4_source"],
    }
    if verdict == "KILLED":
        rec["class"] = "killed"
        rec["killed_by"] = gate.get("killed_by")
        log = W / "gates" / f"{k}.log"
        if log.exists():
            rec["failing_lines"] = [l for l in log.read_text(errors="replace").splitlines()
                                    if re.search(r"\bFAIL\b|FAILED|Traceback|Error:", l)][:20]
        rec["non_finding"] = (f"the full gate fails on it: {gate.get('killed_by')} "
                              f"(gate_rc {gate.get('gate_rc')}); command: {rec['gate_command']}")
    elif verdict == "TIMEOUT":
        rec["class"] = "timeout"
        log = W / "gates" / f"{k}.log"
        last = None
        if log.exists():
            for l in log.read_text(errors="replace").splitlines():
                m = re.search(r"(tests/[\w./-]+\.(?:py|mjs|sh))", l)
                if m:
                    last = m.group(1)
        rec["timeout"] = {"cap_s": gate.get("cap_s", 14400), "last_script_running": last}
    else:
        rec["class"] = p["cls"]
    rec["probe"] = {"path": f"{PD}/{p['probe']}", "command": CMD + p["probe"], "baseline_value": p["baseline"],
                    "mutant_value": p["mutant"], "inputs_tried": p["inputs"], "reach_census": REACH,
                    "answer": p["why"]}
    rec["should_fail"] = p["should"]
    if rec["class"] == "candidate":
        c = CAND[k]
        rec.update({
            "title": c["title"], "step": "D3.M3", "scope": "D3-s1", "class_guess": "I1",
            "severity_claimed": c["severity"], "stop_rule_class": "hygiene",
            "claim": (f"Mutant {k} at {row['file']}:{row['line']} ({rec['patch']}) survives the full GATE_SCOPE=full "
                      f"GOLDEN_MODE=drift gate ({verdict}), yet the probe's number moves: {p['baseline']} -> "
                      f"{p['mutant']}."),
            "mechanism": f"{p['why']}. Check that should have failed (D3.M4): {p['should']}.",
            "phenomenon_property": c["prop"],
            "seam_rule": SEAM,
            "metric_definition": c["metric"],
            "instrumented_symbol": c["symbol"],
            "harness_paths": [FG, f"{PD}/{p['probe']}", f"{PD}/g22_rig.py"]
                             + ([f"{PD}/breach_rig.py"] if "breach" in row["function"] else []),
            "evidence_command": CMD + p["probe"],
            "evidence": {"command": CMD + p["probe"], "harness_path": f"{PD}/{p['probe']}", "value": c["value"],
                         "unit": c["unit"], "baseline_sha": "92d38ecb640bd462f2e19c0814d0f0b7df1ee692",
                         "machine": "box D3-g22: Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython",
                         "cpu_or_wall": "n/a", "tolerance": "exact (deterministic)", "load1": 1.0,
                         "thread_factor": 1.0,
                         "contention_note": "deterministic value; probes ran in a clean baseline worktree while this "
                                            "box's gates ran (load1 ~1); gate walls are provisional"},
            "perturbation": {"change": f"the mutant edit at {row['file']}:{row['line']} applied in memory by the probe; "
                                       f"full gate: {rec['gate_command']}",
                             "expected_direction": c["direction"], "observed_value": c["value"]},
            "null_control": {"command": CMD + p["probe"], "value": c["null"]},
            "reproduction_steps": [CMD + p["probe"], rec["gate_command"]],
            "proposed_fix_scope": "tests only: a check at the input above pinning the baseline value",
            "files": [row["file"], "tests/features.py"],
        })
    out.write_text(json.dumps(rec, indent=1) + "\n")
    return rec["class"]


if __name__ == "__main__":
    force = "--force" in sys.argv
    for r in keys():
        c = build(r, force)
        if c:
            print(f"RESULT {r['key']}={c}")
