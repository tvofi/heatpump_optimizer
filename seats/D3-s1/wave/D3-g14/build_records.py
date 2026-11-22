#!/usr/bin/env python3
# Box D3-g14 (round 11, D3-s1): writes results/<key>.json for every key whose gates/<key>.json exists,
# joining the gate record with this box's probe answer (the PROBE table below, numbers copied from the
# probes' own RESULT lines, re-run by the command each row names).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g14/build_records.py [key ...]
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
S1 = HERE.parents[1]
PR = "dev/audit/rounds/round11/D3/s1/wave/D3-g14/probes"
FG = "dev/audit/rounds/round11/D3/s1/fullgate.py"
DP = "custom_components/heatpump_optimizer/dhw_planner.py"


def cmd(k):
    return f"PYTHONPATH=tests/hastub python3 {PR}/probe_{k}.py"


# class: candidate | equivalent-candidate (when the gate does not kill). reach: whether production inputs move it.
PROBE = {
 "3685cdbd27c1680f": dict(
  cls="candidate", base="baseline_step0_kw=3.000000 kW", mut="mutant_step0_kw=5.000000 kW",
  inputs=["plan [5.0,0.1,0..] tank 30 C ceiling 55 C (delta 2.0 kW)", "plan [-1.0,0.1,0..] (delta 1.0 kW)",
          "in-range plan [3.0,0.1,0..] (null, delta 0)", "three ordinary days through _build_dhw_requirements (realistic_delta 0.0 kW)"],
  reach="unit only: the caller hands _apply_dhw_min_run the greedy planner's plan, already inside [0, p_dhw_max]; realistic_delta_kw=0.000000 on three ordinary days",
  should=("tests/features.py (traced baseline executes dhw_planner.py:2076; also tests/entities.py, tests/env_drift.py)",
          "no direct _apply_dhw_min_run check feeds a plan entry outside [0, p_dhw_max] on the jointly-raised path and asserts the result is clipped to [0, p_dhw_max]"),
  title="No check feeds _apply_dhw_min_run's jointly-raised path an out-of-range entry; dropping its [0, p_dhw_max] clip is unseen",
  sev="low", metric="plan value (kW) _apply_dhw_min_run returns at a step given 5.0 kW with p_dhw_max 3.0, on the path where all weak slots fit jointly",
  direction="up (3.0 -> 5.0 kW: the mutant returns the unclipped entry)"),
 "1c0e818b4bb24fcd": dict(
  cls="candidate", base="baseline_plan=[0,3,3,0,0,3,0.6,0] kW", mut="mutant_plan=[0,3,3,-1,0,5,0.6,-1] kW (delta 2.0 kW); random_plans_separating=220 of 400",
  inputs=["plan [0,3,3,-1,0.1,5,0.3,-1] at 48.971 C, ceiling 55 C (per-slot path)", "400 seeded random plans over {-1,0,0.1,0.3,3,5}^8, tank 30..56 C: 220 separate",
          "same plan with entries in range (null, delta 0)", "three ordinary days (realistic_delta 0.0 kW)"],
  reach="unit only: production plans reaching the per-slot path are already inside [0, p_dhw_max]; realistic_delta_kw=0.000000",
  should=("tests/features.py (traced baseline executes dhw_planner.py:2106; also block_duty.py, manual_plan.py, entities.py, optimality.py)",
          "no _apply_dhw_min_run check on the per-slot path (joint raise does not fit) feeds an entry above p_dhw_max or below 0 and asserts the returned plan lies in [0, p_dhw_max]"),
  title="No check feeds _apply_dhw_min_run's per-slot path an out-of-range entry; dropping its final [0, p_dhw_max] clip is unseen",
  sev="low", metric="max |plan| difference (kW) of _apply_dhw_min_run's return between the arms on one per-slot-path plan with entries outside [0, p_dhw_max]",
  direction="up (0 -> 2.0 kW: entries above p_dhw_max and below 0 leave unclipped)"),
 "0b51e1d1975513aa": dict(
  cls="candidate", base="short_pins_returns_plan_baseline=1", mut="short_pins_returns_plan_mutant=0 (IndexError); empty pins likewise",
  inputs=["pins shorter than the plan (2 of 4)", "empty pins", "equal-length and longer pins (null: identical)"],
  reach="unit only: HeatPumpOptimizer._normalise_pins pads every pin array to the horizon (optimizer.py:5003-5018), so _apply_dhw_pins never sees a short array in production",
  should=("tests/manual_plan.py / tests/features.py (traced baseline executes dhw_planner.py:1645; also block_duty.py)",
          "no check calls _apply_dhw_pins with a pin array shorter than the plan and asserts it returns the plan with the tail untouched"),
  title="No check calls _apply_dhw_pins with pins shorter than the plan; the length bound on its loop is unpinned",
  sev="low", metric="1 if _apply_dhw_pins returns a plan for a pin array shorter than the plan, 0 if it raises IndexError",
  direction="down (1 -> 0)"),
 "0e3fc2bc64c2bf63": dict(
  cls="candidate", base="baseline_kw_at_pin_0p5=0.600000 kW", mut="mutant_kw_at_pin_0p5=0.000000 kW",
  inputs=["pin exactly 0.5 (separates)", "pins 0, 1, NaN, 0.49999, 0.50001 (null: identical)", "ordinary day with pins {0,1,NaN} (realistic_delta 0.0 kW)"],
  reach="unit only: manual_plan.channel_pins emits only PIN_ON 1.0, PIN_OFF 0.0 and NaN (manual_plan.py:41-42, 215-220); a 0.5 pin needs a SolveInputs caller passing fractional pins",
  should=("tests/manual_plan.py / tests/features.py (traced baseline executes dhw_planner.py:1649)",
          "no check pins the force-on threshold at exactly 0.5 (a 0.5 pin must force the step on)"),
  title="No check pins _apply_dhw_pins' force-on boundary at a pin of exactly 0.5",
  sev="low", metric="plan value (kW) _apply_dhw_pins returns at a 0 kW step pinned exactly 0.5 (min_run_power 0.6)",
  direction="down (0.6 -> 0.0 kW)"),
 "4813f0fd25bc8bb4": dict(
  cls="equivalent-candidate", base="inputs_separating=0 of 11", mut="inputs_separating=0 of 11",
  inputs=["p_max 4, 0, -1, 1e-9, 0.125, +inf, -inf, NaN", "p_max 4 with p_run_cap None, 0.05, 2.0"],
  reach="none found: min(0.8p, p) differs from 0.8p only for p < 0 (and NaN), where max(0.1, .) returns 0.1 in both arms",
  should=("none: no input separates the arms", "n/a (equivalent on every input tried)")),
 "b25e80c59b31c20d": dict(
  cls="candidate", base="baseline_shortfall_c=0.2711 C (4.3727 kWh)", mut="mutant_shortfall_c=6.3719 C (3.5974 kWh)",
  inputs=["manual DHW pins OFF on cheap night steps 8-15, window 18:00-20:00 min 45 C, tank 48 C (separates)", "no pins (null, 0)", "on-only pins (null, 0)"],
  reach="production: a manual plan's DHW channel yields 0.0 pins on every step outside its slots (manual_plan.channel_pins), which optimize passes through _normalise_pins to _build_dhw_requirements",
  should=("tests/manual_plan.py (traced baseline executes dhw_planner.py:1184; the 'last safe DHW off' check near line 419-440)",
          "the off-pin check asserts only that the pinned step is 0 and not released; none asserts the tank still meets its requirement, i.e. that the energy removed by an off-pin is re-bought in the free steps"),
  title="No check asserts a DHW off-pin's energy is re-bought; dropping the pins' forced_off mask leaves the tank 6.4 C short unseen",
  sev="medium", metric="worst simulated tank shortfall (C) below the plan's own floor/ready requirement, plan built with DHW pins OFF on the cheap night steps 8-15",
  direction="up (0.27 -> 6.37 C)"),
 "6999e2dab9790b53": dict(
  cls="candidate", base="pin0p5_kwh_baseline=4.5899 kWh", mut="pin0p5_kwh_mutant=4.6043 kWh; pin0p5_delta_kw=0.773378 kW",
  inputs=["one pin exactly 0.5 at step 13 under a cheap night (separates)", "pins 1.0, 0.0, NaN, 0.49999, 0.50001 at step 13 (null: identical)"],
  reach="unit only: manual_plan.channel_pins emits only 0.0, 1.0, NaN (manual_plan.py:41-42, 215-220)",
  should=("tests/manual_plan.py / tests/features.py (traced baseline executes dhw_planner.py:1187; also block_duty.py)",
          "no check pins that a 0.5 pin is not forced off for the planners (the force-off threshold agrees with _apply_dhw_pins' force-on at >= 0.5)"),
  title="No check pins _build_dhw_requirements' forced-off threshold at a pin of exactly 0.5",
  sev="low", metric="max |schedule| difference (kW) of _build_dhw_requirements with one DHW pin of exactly 0.5 at step 13",
  direction="up (0 -> 0.77 kW)"),
 "cd7bc939ea82fecd": dict(
  cls="candidate", base="baseline_shortfall_c=0.2711 C (4.3727 kWh)", mut="mutant_shortfall_c=6.3719 C (3.5974 kWh)",
  inputs=["manual DHW pins OFF on cheap night steps 8-15, window 18:00-20:00 min 45 C, tank 48 C (separates)", "no pins (null, 0)", "on-only pins, mask all False (null, 0)"],
  reach="production: a manual plan's DHW channel pins every step outside its slots to 0.0 (manual_plan.channel_pins)",
  should=("tests/manual_plan.py (traced baseline executes dhw_planner.py:1188; the 'last safe DHW off' check near line 419-440)",
          "no check asserts the tank still meets its requirement after an off-pin (the off-pinned energy re-bought in the free steps)"),
  title="No check asserts DHW off-pins reach the planners as forced_off; the mask.any() assignment is unpinned",
  sev="medium", metric="worst simulated tank shortfall (C) below the plan's own floor/ready requirement, plan built with DHW pins OFF on the cheap night steps 8-15",
  direction="up (0.27 -> 6.37 C)"),
 "de02e0a048abc451": dict(
  cls="candidate", base="suppressed_steps_baseline=0 (schedule sum 0.0)", mut="suppressed_steps_mutant=1 (schedule sum 0.0)",
  inputs=["blocked=True, external heat on, tank 48 C, cheap steps 1-7 (separates the published count)", "blocked=True, external heat off (null 0,0)", "blocked=False (null, delta 0)"],
  reach="production: a pump mode that makes no hot water (blocked) together with external heat or the peak guard active; only DhwPlan.external_heat_suppressed_steps moves, the schedule is zeroed at line 1368 in both arms",
  should=("tests/features.py (traced baseline executes dhw_planner.py:1190; also entities.py, manual_plan.py)",
          "no blocked-mode check asserts external_heat_suppressed_steps == 0 (nothing planned, so nothing suppressed) with external heat active"),
  title="No check pins the suppressed-step count in a blocked DHW mode; dropping the blocked forced_off reports a phantom suppression",
  sev="low", metric="DhwPlan.external_heat_suppressed_steps with blocked=True and external heat active",
  direction="up (0 -> 1)"),
 "7f026b4dd7d44269": dict(
  cls="candidate", base="cr2_kwh_baseline=7.5261 kWh; cr5_kwh_baseline=8.7203 kWh", mut="cr2_kwh_mutant=7.5303 kWh (delta 0.712 kW); cr5_kwh_mutant=8.7937 kWh (delta 0.600 kW)",
  inputs=["dhw_cooling_rate 0.3 (hold 28.0 h > 24 h horizon: null, delta 0)", "cooling rate 2.0 (hold 4.21 h, separates)", "cooling rate 5.0 (hold 2.80 h, separates)"],
  reach="production with a leaky tank (learned cooling rate >= ~1 C/h, hold time below the horizon) and a cheap block more than the hold time before the window",
  should=("tests/features.py (traced baseline executes dhw_planner.py:1214; also block_duty.py, manual_plan.py, optimality.py)",
          "no check with a hold time shorter than the horizon asserts heating is not bought earlier than max_lead_steps before the need"),
  title="No check bounds DHW pre-heat lead by the tank's hold time; dropping the min(n_steps, hold/dt) cap is unseen",
  sev="low", metric="kWh _build_dhw_requirements plans on a cheap-night day for a tank with cooling rate 5 C/h (hold 2.8 h)",
  direction="up (8.7203 -> 8.7937 kWh)"),
 "a1576c7241b67401": dict(
  cls="candidate", base="suppressed_baseline=1, step0_kw_baseline=0.0", mut="suppressed_mutant=0, step0_kw_mutant=3.2 kW",
  inputs=["tank 44.646992926832446 C: coasting after step 0 equals requirement-0.5 exactly (separates)", "its float predecessor (null, 0)", "+0.01 C (null, 0)"],
  reach="production only at an exact float tie between the coasting temperature and requirement - 0.5 (measure-zero)",
  should=("tests/features.py (traced baseline executes dhw_planner.py:1342; also env_drift.py)",
          "no check places the coasting temperature exactly on requirement - 0.5 and asserts the step counts as covered"),
  title="No check pins the external-heat 'covered' boundary at coasting == requirement - 0.5",
  sev="low", metric="DhwPlan.external_heat_suppressed_steps at the exact tie tank temperature 44.646992926832446 C",
  direction="down (1 -> 0; step 0 power 0 -> 3.2 kW)"),
 "8fa714bbb756e11e": dict(
  cls="candidate", base="suppressed_baseline=1, kwh_steps0_7_baseline=0.0000 kWh", mut="suppressed_mutant=0, kwh_steps0_7_mutant=0.8000 kWh",
  inputs=["external heat on, tank 48 C, cheap steps 1-7 (separates)", "external heat off (null)", "tank 55 C on/off (null)"],
  reach="production: any solve with external heat or the peak guard active and a discretionary slot in hours 0.25-2 of the horizon",
  should=("tests/features.py (traced baseline executes dhw_planner.py:1343; the '#7 suppression flag' pair near line 19295)",
          "the pair asserts peak-guard == external-heat and that the gate bites somewhere; none asserts the suppression spans the 2 h horizon (no discretionary slot in steps 1-7 while coasting is covered)"),
  title="No check pins the external-heat suppression horizon at 2 h; shrinking it to one step buys electric DHW under a running external source unseen",
  sev="medium", metric="kWh _build_dhw_requirements plans in steps 0-7 with external heat active, tank 48 C, cheap steps 1-7",
  direction="up (0.0 -> 0.8 kWh)"),
 "8fbdb8a5c1e67d5e": dict(
  cls="equivalent-candidate", base="inputs_separating=0 of 100", mut="inputs_separating=0 of 100",
  inputs=["dt 0.25, 1.0, 1e-7, 1e-9, 0 (ZeroDivisionError at line 1214 in both arms), -0.25, -1.0, -1e-9, NaN (ValueError in both), +inf",
          "tanks 30/44/46/50/60 C", "n 8 and 24", "all-day window, external heat on"],
  reach="none found: only dt <= 0 can differ; dt == 0 and NaN raise earlier in both arms, and for dt < 0 the planners plan nothing to suppress",
  should=("none: no input separates the arms", "n/a")),
 "94c2cc27ea61db25": dict(
  cls="equivalent-candidate", base="inputs_separating=0 of 321", mut="inputs_separating=0 of 321",
  inputs=["legionella 60 C / 7 d, hours since 160-169 (legionella steps 0,1,3,5,7)", "tank 58-62 C in 0.1 C", "single cheap step at 1/3/5/7 or none",
          "windows 18-20, 01-03, 04-06, 10-12 with min 45/55 C and draw 150/400 L/day, step 0 at 0.01 vs 3.0", "external heat on"],
  reach="none found: when coasting covers the legionella step (>= requirement - 0.5) the planners leave that step unpowered, so the mask has nothing to remove there",
  should=("none found: no horizon tried separates the arms", "n/a")),
 "defeacb89de279a1": dict(
  cls="equivalent-candidate", base="inputs_separating=0 of 144; slots_in_0_1e-5_kw=0", mut="inputs_separating=0 of 144",
  inputs=["external heat on; tanks 40-56 C step 2", "cheap blocks 0-7, 1-7, 2-5, flat", "windows 18-20 and 06-08, min 45 C", "p_max 4.0 and 0.3"],
  reach="none found: the min-run repair and the clamp zero every slot below min_run_power, so no slot in (0, 1e-5] kW reaches line 1348 (0 seen over 144 plans)",
  should=("none: no input separates the arms", "n/a")),
 "c9404a6ea551b041": dict(
  cls="equivalent-candidate", base="typed_inputs_separating=0 of 20", mut="typed_inputs_separating=0 of 20",
  inputs=["empty plan with max_temp 60, empty array, NaN, inf, None x initial_temp 50, NaN, inf, -inf", "n=0 horizon through _build_dhw_requirements (both ok, size 0)",
          "non-empty plan (null, identical)", "out-of-type initial_temp None: baseline returns, mutant TypeError (outside the annotated float domain)"],
  reach="none on the declared domain; only an out-of-type initial_temp=None separates (TypeError in the mutant)",
  should=("none on typed inputs", "n/a")),
}


def main(keys):
    w = HERE
    rows = [l.split("\t") for l in (w / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
    null = json.loads((w / "gates/null.json").read_text()) if (w / "gates/null.json").exists() else {}
    for r in rows:
        key, src, f, line, fn, cluster, slc, fullnet, kind = r[:9]
        if keys and key not in keys:
            continue
        g = w / "gates" / f"{key}.json"
        if not g.exists():
            continue
        gate = json.loads(g.read_text())
        m = json.loads((S1 / "state/results" / src / f"{key}.json").read_text())["mutant"]
        p = PROBE[key]
        v = gate.get("verdict")
        gfields = {k: gate.get(k) for k in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end",
                                            "failed_scripts", "fail_lines", "more_fails_than_null", "cap_s")}
        gfields["provisional"] = True
        gfields["record"] = f"dev/audit/rounds/round11/D3/s1/wave/D3-g14/gates/{key}.json"
        gfields["command"] = f"PYTHONPATH=tests/hastub python3 {FG} run --src {src} --key {key}"
        rec = {"key": key, "site": f"{f.split('/')[-1]}:{line} {kind}", "file": f, "line": int(line),
               "patch": f"{m['old'].strip()} -> {m['new'].strip()}", "function": fn, "cluster": cluster,
               "slice": slc, "gate": gfields}
        if v == "KILLED":
            log = (w / "gates" / f"{key}.log")
            lines = []
            if log.exists():
                txt = log.read_text(errors="replace").splitlines()
                lines = [l for l in txt if l.strip().startswith(("FAIL", ">>> FAILED")) or " FAILED" in l][:20]
            rec.update({"class": "killed", "killed_by": gate.get("killed_by"), "failing_check_lines": lines,
                        "non_finding": f"the suite fails on this mutant: {gfields['command']} -> KILLED by {', '.join(gate.get('killed_by') or [])}"})
        elif v == "TIMEOUT":
            rec.update({"class": "timeout", "cap_s": gate.get("cap_s", 14400),
                        "note": "past the box's gate cap: neither finding nor non-finding (unfinished)"})
        else:
            rec["class"] = p["cls"]
            rec["probe"] = {"path": f"{PR}/probe_{key}.py", "command": cmd(key), "baseline_value": p["base"],
                            "mutant_value": p["mut"], "inputs_tried": p["inputs"], "production_reach": p["reach"]}
            rec["should_fail"] = {"script": p["should"][0], "assertion": p["should"][1]}
            if p["cls"] == "candidate":
                rec["finding"] = {
                    "title": p["title"], "step": "D3.M3", "scope": "D3-s1", "class_guess": "new",
                    "severity_claimed": p["sev"], "stop_rule_class": "hygiene",
                    "claim": (f"Mutant {key} at {f.split('/')[-1]}:{line} ({rec['patch']}) {v} the full gate "
                              f"(gate_rc {gate.get('gate_rc')}), yet the probe's number moves: baseline {p['base']}, mutant {p['mut']}. "
                              f"Reach: {p['reach']}."),
                    "metric_definition": p["metric"],
                    "instrumented_symbol": f"custom_components.heatpump_optimizer.dhw_planner:{fn} line {line}",
                    "harness_paths": [FG, f"{PR}/probe_{key}.py", f"{PR}/_g14lib.py"],
                    "evidence_command": cmd(key),
                    "perturbation": {"change": f"the one-line mutant {key} ({rec['patch']}) applied in memory by the probe; full gate: {gfields['command']}",
                                     "direction": p["direction"]},
                    "null_control": {"command": cmd(key), "value": "null arm delta 0 (see the probe's null_* RESULT lines)",
                                     "gate_null": "dev/audit/rounds/round11/D3/s1/wave/D3-g14/gates/null.json"},
                    "files": [f, p["should"][0].split(" ")[0]],
                }
        (w / "results").mkdir(exist_ok=True)
        (w / "results" / f"{key}.json").write_text(json.dumps(rec, indent=1) + "\n")
        print(f"wrote results/{key}.json class={rec['class']} verdict={v}")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
