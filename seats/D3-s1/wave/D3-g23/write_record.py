#!/usr/bin/env python3
"""Box D3-g23 (audit round 11, seat D3-s1): write results/<key>.json for one gated key.

Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g23/write_record.py <key>
Reads keys.tsv, the key's mutant (state/results/<src>/<key>.json), its gate record (gates/<key>.json), the null
(gates/null.json) and the probe's recorded output (probes/<key>/probe_output.txt); the per-key step-4 answer and
probe reading are the SPEC table below. Writes only results/<key>.json beside it.
"""
import json, re, sys
from pathlib import Path

W = Path(__file__).resolve().parent
S1 = W.parents[1]
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
PROBE_DIR = "dev/audit/rounds/round11/D3/s1/wave/D3-g23/probes"
FULLGATE = "dev/audit/rounds/round11/D3/s1/fullgate.py"
MACHINE = "box D3-g23: Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14, alone on the box"
REL = "tests/manual_plan.py (test_safety_release, test_give_up_is_per_channel, test_release_always_resolves)"
SEAM = "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv  (the wave list; this box's keys: dev/audit/rounds/round11/D3/s1/wave/D3-g23/keys.tsv)"

# class: what the probe makes the key IF the gate leaves it standing (SURVIVED / RED-AS-NULL)
SPEC = {
 "c6679b9b114e5732": dict(cls="equivalent-candidate", metric="direct_short_pins", base="([],[])", mut="IndexError",
   reach="unreachable through production: optimize() pads/truncates pins to n_steps in _normalise_pins (optimizer.py:5014-5017); 0 of 3 optimize() solves with 95/50/1-long pin arrays differ; 0 of 11 release calls over 7 manual-plan solves see a pin array shorter than the schedule",
   inputs=["space_pins one shorter than the schedule (direct)", "empty space_pins (direct)", "optimize() with pin arrays of length 95, 50, 1 (winter_extreme, 16.9 C, step 0 off)", "reach count over the 7 REACH_SCENARIOS"],
   should="none through production; only a direct _safety_release_steps call with a short pin array separates (tests/manual_plan.py drives the function only through optimize())"),
 "8ef1027c9e221b64": dict(cls="candidate", metric="direct_half_pin_release", base="([],[])", mut="([0],[])",
   reach="optimize() accepts any float pin (_normalise_pins copies it); 5 of 55 optimize() solves with 0.5 pins (winter_extreme, 16.6-17.6 C) return a different plan; the manual-plan service itself only writes 0.0/1.0",
   inputs=["0.5 pin at floor+0.1 after an off step (direct)", "1.0 pin (null)", "55 optimize() solves: 11 start temperatures x 5 pin layouts with 0.5 pins"],
   should=REL + " -- no check passes a pin of exactly 0.5 (the on/off boundary _apply_pins_to_bounds and _safety_release_steps must agree on)",
   title="No check pins the 0.5 on/off boundary of the safety release's pinned-off test", sev="low", dirn="up",
   prop="A pin of 0.5 is classified the same way (not forced off) by _safety_release_steps as by the bounds that pin the step"),
 "ce686724ef107650": dict(cls="candidate", metric="direct_on_pin_at_floor_release", base="([],[])", mut="([0],[])",
   reach="through optimize(): 3 of 36 manual-plan solves with an off block followed by an on block (winter_extreme, 16.8-17.6 C) return a different plan",
   inputs=["on-pinned step at floor+0.1 after an off step (direct)", "the same step free (null)", "36 optimize() solves: 9 start temperatures x 4 off/on layouts"],
   should=REL + " -- no check puts a forced-ON step near the comfort floor after a forced-off block and asserts the off block is not released for it",
   title="No check covers a forced-on step near the floor; and->or in the pinned-off test is unseen", sev="medium", dirn="up",
   prop="Only forced-off steps (pin < 0.5) are judged by the pinned-off breach rule; a forced-on step is judged as free"),
 "8fd14c249b86abf7": dict(cls="candidate", metric="direct_off_step_at_floor_plus_0.1_release", base="([0],[])", mut="([],[])",
   reach="through optimize(): 11 of 55 manual-plan solves with short off blocks (winter_extreme, 16.6-17.6 C) return a different plan",
   inputs=["forced-off step at floor+0.1 (direct)", "the same step at floor-0.5 (null)", "55 optimize() solves: 11 start temperatures x 5 off-block layouts"],
   should=REL + " -- test_safety_release's cold case releases through the free-step rule as well, so no check isolates a forced-off step inside (floor-0.25, floor+0.15]",
   title="No check isolates the pinned-off breach band; disabling the rule leaves the gate green", sev="medium", dirn="to_zero",
   prop="A forced-off step whose room temperature ends at or below floor+0.15 releases its off block"),
 "0120a5a672990611": dict(cls="candidate", metric="direct_tie_release", base="([0],[])", mut="([],[])",
   reach="the tie (room exactly floor+0.15 at a forced-off step) is a solver float; not hit by any optimize() input tried, reachable only by coincidence",
   inputs=["temp == floor+0.15 (tie, direct)", "floor+0.10 and floor+0.20 (null)"],
   should=REL + " -- no check places a forced-off step at exactly floor+0.15",
   title="No check pins the pinned-off breach bound at exactly floor+0.15", sev="low", dirn="to_zero",
   prop="A forced-off step at exactly floor+0.15 counts as a breach (<=)"),
 "0ecb763c4bcb0828": dict(cls="candidate", metric="direct_tie_release", base="([],[])", mut="([0],[])",
   reach="the tie (room exactly floor-0.25 at a free step) is a solver float; reachable only by coincidence",
   inputs=["temp == floor-0.25 (tie, direct)", "floor-0.30 and floor-0.20 (null)"],
   should=REL + " -- no check places a free step at exactly floor-0.25",
   title="No check pins the free-step breach bound at exactly floor-0.25", sev="low", dirn="up",
   prop="A free step at exactly floor-0.25 is not a breach (strict <)"),
 "f2894b5754c254fe": dict(cls="equivalent-candidate", metric="direct_short_req", base="([],[])", mut="IndexError",
   reach="unreachable through production: 0 of 11 release calls over 7 manual-plan solves carry a DHW requirement shorter than the DHW schedule",
   inputs=["requirement of 2 for a 4-step DHW schedule (direct)", "requirement as long as the schedule (null)", "reach count over the 7 REACH_SCENARIOS"],
   should="none through production; only a direct call with a short requirement separates"),
 "bc3a42f14c903439": dict(cls="candidate", metric="direct_tie_release", base="([],[])", mut="([],[0])",
   reach="the tie (tank exactly requirement-0.5 after a forced-off step) is a solver float; reachable only by coincidence",
   inputs=["tank == req-0.5 (tie, direct)", "req-0.4 and req-0.6 (null)"],
   should="tests/block_duty.py, tests/features.py, tests/manual_plan.py execute the line on the traced baseline; none places the tank at exactly requirement-0.5",
   title="No check pins the DHW safety-release bound at exactly requirement-0.5", sev="low", dirn="up",
   prop="A tank at exactly requirement-0.5 is safe (>=), so its forced-off step is not released"),
 "856aa341a89a6ab0": dict(cls="candidate", metric="released_space", base="[0]", mut="[]",
   reach="through optimize(): winter_extreme, room/slab 16.9 C, only step 0 forced off -> manual_released_space [0] -> []; first-hour space energy 4.8809 -> 4.5000 kWh",
   inputs=["optimize() with only step 0 forced off at 16.8/16.9 C", "steps 0-3 off (null)", "direct: breach whose only preceding off step is step 0"],
   should="tests/block_duty.py, tests/features.py, tests/manual_plan.py execute the line; test_safety_release forces whole days off, where _expand_off_blocks reaches step 0 anyway -- no check forces only step 0 off",
   title="No check forces only step 0 off; the safety release's walk can skip step 0 unseen", sev="medium", dirn="to_zero",
   prop="A breach whose only preceding forced-off step is step 0 releases step 0"),
 "7303435ec1ab7701": dict(cls="equivalent-candidate", metric="direct_short_pins", base="([0],[])", mut="IndexError",
   reach="unreachable through production: _normalise_pins makes every pin array n_steps long; 0 of 3 optimize() solves with short arrays differ; 0 of 11 release calls see a short array",
   inputs=["1-long pins with a breach at step 2 (direct)", "full-length pins (null)", "optimize() with 95/50/1-long pins", "reach count over the 7 REACH_SCENARIOS"],
   should="none through production; only a direct call with a short pin array separates"),
 "5ce83ed87c36b9a5": dict(cls="candidate", metric="direct_half_pin_release", base="([0],[])", mut="([],[])",
   reach="optimize() accepts any float pin; 5 of 15 optimize() solves with 0.5 pins (winter_extreme, 16.9-17.3 C) return a different plan; the manual-plan service itself only writes 0.0/1.0",
   inputs=["0.5 pin between an off step and a breach (direct)", "1.0 pin (null)", "15 optimize() solves with 0.5 pins"],
   should="tests/block_duty.py, tests/features.py, tests/manual_plan.py execute the line; none passes a pin of exactly 0.5",
   title="No check pins the 0.5 boundary of _preceding_off's off-pin test", sev="low", dirn="to_zero",
   prop="_preceding_off returns only steps with pin < 0.5 (a 0.5 pin is not forced off)"),
 "fe3e41de6bdc640a": dict(cls="candidate", metric="released_space", base="[0,1]", mut="[]",
   reach="through optimize(): winter_extreme, room/slab 17.0 C, steps 0-1 off and step 2 on -> manual_released_space [0,1] -> []; first-hour space energy 4.8809 -> 3.0000 kWh",
   inputs=["optimize() with off then on blocks at 16.9-17.6 C (7 of 54 layouts move)", "steps 0-1 off only (null)"],
   should="tests/block_duty.py, tests/features.py, tests/manual_plan.py execute the line; no check puts a forced-on step between a forced-off block and a later breach",
   title="No check puts an on-pin between an off block and a breach; _preceding_off and->or is unseen", sev="medium", dirn="to_zero",
   prop="_preceding_off walks past forced-on steps to the nearest forced-OFF step"),
 "f25414a9d4e32d19": dict(cls="equivalent-candidate", metric="direct_long_guess", base="[1.0,2.0,5.0]", mut="IndexError",
   reach="unreachable through production: 0 of 14 _seed_pinned_guess calls over 7 solves pass a guess whose length differs from the bounds (both are n_steps)",
   inputs=["3-long guess with 2 bounds (direct)", "equal lengths (null)", "reach count over the 7 REACH_SCENARIOS"],
   should="none through production; only a direct call with mismatched lengths separates"),
 "70791cdb98f8ddd7": dict(cls="candidate", metric="buffer_cap_initial60", base="60.000 C", mut="35.000 C",
   reach="through optimize(): a 750 L valve tank, a -20 C day (charge ceiling 35 C), tank starting at 60 C -> 20 OptimizationResult fields differ (objective_value, deferred_energy_cost, buffer_temp_trajectory, heat_pump_on_schedule, ...)",
   inputs=["initial tank 60 C at -20 C (direct and optimize())", "initial 30 C (null)", "-5 C day (ceiling 70 C: no move)"],
   should="tests/features.py ('The optimizer can see the buffer tank (item 29)') and tests/validate.py execute the line; features.py checks the cap only with no initial tank temperature and at outdoor -5 C, where the ceiling is the 70 C rating",
   title="No check sets a start tank above the charge ceiling; the settlement floor at it is unseen", sev="medium", dirn="down",
   prop="The buffer settlement cap is floored at the solve's initial tank temperature (min(rating, max(ceiling, initial)))"),
 "7516dd3d9e66d3ef": dict(cls="candidate", metric="buffer_cap_initial60", base="60.000 C", mut="35.000 C",
   reach="through optimize(): a 750 L valve tank, a -20 C day (charge ceiling 35 C), tank starting at 60 C -> 20 OptimizationResult fields differ",
   inputs=["initial tank 60 C at -20 C (direct and optimize())", "initial 30 C (null)", "-5 C day (ceiling 70 C: no move)"],
   should="tests/features.py ('The optimizer can see the buffer tank (item 29)') and tests/validate.py execute the line; no check starts the tank above the charge ceiling",
   title="No check sets a start tank above the charge ceiling; max(ceiling, initial) dropped is unseen", sev="medium", dirn="down",
   prop="The buffer settlement cap is floored at the solve's initial tank temperature (min(rating, max(ceiling, initial)))"),
 "65e0ffa75d60d319": dict(cls="equivalent-candidate", metric="wood_cap", base="95.0", mut="None (stored kWh at a 99 C wood tank 361.75 -> 364.07)",
   reach="equivalent at the observable output: 0 OptimizationResult fields differ at 24/2/1 h horizons with the wood tank starting at 99 C; the cap's one reader (_stored_thermal_energy) moves, but the settlement differences two states whose wood side is the plan's own (_held_reference, optimizer.py:1041), so the term cancels",
   inputs=["two-tank house, caps (direct)", "_stored_thermal_energy at wood 99 C", "optimize() with wood 99 C at 24, 2, 1 h", "single-tank house (null)"],
   should="none at the observable output; a check of _settlement_caps' keys for a two-tank house would separate the dict, not any published value"),
}


def main(key):
    keys = {l.split("\t")[0]: l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()}
    row = keys[key]
    hdr = (W / "keys.tsv").read_text().splitlines()[0].split("\t")
    k = dict(zip(hdr, row))
    mut = json.loads((S1 / "state" / "results" / k["src"] / f"{key}.json").read_text())["mutant"]
    gate = json.loads((W / "gates" / f"{key}.json").read_text())
    null = json.loads((W / "gates" / "null.json").read_text())
    s = SPEC[key]
    verdict = gate.get("verdict")
    out_lines = [l.strip() for l in (W / "probes" / key / "probe_output.txt").read_text().splitlines() if l.startswith("RESULT")]
    pcmd = f"PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 {PROBE_DIR}/probe_{key}.py"
    gcmd = f"PYTHONPATH=tests/hastub python3 {FULLGATE} run --src {k['src']} --key {key}"
    rec = {
        "key": key,
        "site": f"{mut['file']}:{mut['line']} {mut['kind']}",
        "patch": f"{mut['old'].strip()} -> {mut['new'].strip()}",
        "function": k["function"], "cluster": k["cluster"], "slice": k["slice"], "m4_source": k["m4_source"],
        "gate": {x: gate.get(x) for x in ("verdict", "killed_by", "gate_rc", "failed_scripts", "fail_lines", "wall_s",
                                          "child_cpu_s", "load1_start", "load1_end", "cap_s", "note")} | {
            "command": gcmd, "record": f"dev/audit/rounds/round11/D3/s1/wave/D3-g23/gates/{key}.json",
            "null_fail_lines": null.get("fail_lines"), "provisional": True},
    }
    if verdict == "KILLED":
        lines = []
        log = W / "gates" / f"{key}.log"
        if log.exists():
            lines = [l.rstrip()[:300] for l in log.read_text(errors="replace").splitlines() if l.startswith("  FAIL") or ">>> FAILED" in l]
        rec["class"] = "killed"
        rec["killed_lines"] = lines[:40]
    elif verdict == "TIMEOUT":
        rec["class"] = "timeout"
        log = W / "gates" / f"{key}.log"
        last = ""
        if log.exists():
            runs = re.findall(r"^(?:>>> |=== |RUN |\+ )(.*)$", log.read_text(errors="replace"), re.M)
            last = runs[-1] if runs else ""
        rec["timeout"] = {"cap_s": gate.get("cap_s"), "last_script": last}
    else:
        rec["class"] = s["cls"]
    rec["probe"] = {"path": f"{PROBE_DIR}/probe_{key}.py", "command": pcmd, "metric": s["metric"],
                    "baseline_value": s["base"], "mutant_value": s["mut"], "reach": s["reach"],
                    "inputs_tried": s["inputs"], "results": out_lines}
    rec["should_fail"] = s["should"]
    if rec["class"] == "candidate":
        rec["finding"] = {
            "title": s["title"], "step": "D3.M3", "scope": "D3-s1", "class_guess": "I1", "severity_claimed": s["sev"],
            "stop_rule_class": "bug",
            "claim": f"Mutant {key} at optimizer.py:{mut['line']} ({mut['old'].strip()} -> {mut['new'].strip()}) leaves the full "
                     f"GATE_SCOPE=full GOLDEN_MODE=drift gate {verdict} on box D3-g23, yet the probe's {s['metric']} moves "
                     f"{s['base']} -> {s['mut']}.",
            "mechanism": f"Reach: {s['reach']}. Check that should have failed (D3.M4): {s['should']}.",
            "metric_definition": f"{s['metric']} printed by probe_{key}.py (baseline arm vs the mutant re-compiled in memory)"[:200],
            "phenomenon_property": s["prop"],
            "seam_rule": SEAM,
            "instrumented_symbol": f"custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer.{k['function'].split('HeatPumpOptimizer.')[-1]}",
            "harness_paths": [FULLGATE, f"{PROBE_DIR}/probe_{key}.py", f"{PROBE_DIR}/_g23_common.py"],
            "evidence_command": pcmd,
            "evidence": {"command": pcmd, "harness_path": f"{PROBE_DIR}/probe_{key}.py", "value": s["mut"],
                         "unit": s["metric"], "baseline_sha": BASE, "machine": MACHINE, "cpu_or_wall": "n/a",
                         "contention_note": "deterministic value; probes ran from a scratch baseline worktree beside the box's gates; gate walls provisional",
                         "tolerance": "exact"},
            "perturbation": {"change": f"the mutant edit at optimizer.py:{mut['line']} applied in memory by the probe; full gate: {gcmd}",
                             "expected_direction": s["dirn"], "observed_value": s["mut"]},
            "null_control": {"command": pcmd, "value": "0", "note": "the probe's null_* RESULT line: an input where the edit cannot matter, identical under both arms"},
            "reproduction_steps": [pcmd, gcmd],
            "files": [mut["file"]],
            "proposed_fix_scope": "tests only: a check in " + s["should"].split(" -- ")[0].split(" (")[0] + " that feeds the probe's distinguishing input and asserts the baseline outcome",
        }
    (W / "results").mkdir(exist_ok=True)
    (W / "results" / f"{key}.json").write_text(json.dumps(rec, indent=1) + "\n")
    print(f"RESULT {key} verdict={verdict} class={rec['class']}")


if __name__ == "__main__":
    for a in sys.argv[1:]:
        main(a)
