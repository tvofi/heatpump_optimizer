#!/usr/bin/env python3
"""Box D3-g07: write results/<key>.json for one gated key (step 3 of the brief).

usage: build_record.py <key>   (cwd: the tree root $HOME/audit-r11-D3-s1)
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
S1 = ROOT / "dev/audit/rounds/round11/D3/s1"
W = S1 / "wave/D3-g07"
PR = "dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes"
PY = "/opt/hpo/venv-ci/bin/python3"
FULLGATE = "dev/audit/rounds/round11/D3/s1/fullgate.py"

G = "custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator."
FEAT = "tests/features.py"

SPEC = {
    "d3cad40ffce9b765": dict(
        cls="candidate", b="scale_baseline_at_min", m="scale_mutant_at_min",
        inputs="30 sunny folds, irradiance 200..780 W/m2 in 20 W/m2 steps, residual = 1.5x modelled solar gain; null 29 folds; 31 folds (both arms move)",
        reach=[FEAT],
        should="tests/features.py (the only closure script whose traced baseline executes coordinator.py:9402) has no check that "
               "the solar-aperture scale moves off 1.0 on exactly the SOLAR_APERTURE_MIN_SAMPLES-th varying sunny fold",
        title="No check pins the solar-aperture learner's first correction at exactly SOLAR_APERTURE_MIN_SAMPLES folds",
        claim="Mutating coordinator.py:9402 `m[\"n\"] >= SOLAR_APERTURE_MIN_SAMPLES` to `>` delays the solar-aperture scale's first "
              "correction by one fold (scale 2.0 -> 1.0 after 30 folds) and the full GATE_SCOPE=full GOLDEN_MODE=drift gate stays green.",
        severity="low", direction="down",
        metric="_solar_aperture['scale'] after exactly 30 varying sunny-step folds of _fold_solar_aperture (ratio)"),
    "e163f6fbc359cd4c": dict(
        cls="candidate", b="scale_baseline_tie", m="scale_mutant_tie",
        inputs="moment state n=100, cov=2e-6, x == mx, start variance searched over representable floats until v - a*v == 1e-6 exactly "
               "(found); null: variance one float above the tie; 36 realistic fold sequences (31/60/200 folds x irradiance ramps "
               "150/300/600 W/m2 x 5/20 W/m2 steps x residual ratio 0.6/1.5): 0 differ",
        reach=[FEAT],
        should="tests/features.py (traced reach of coordinator.py:9402) has no check of the `var > 1e-6` guard at its exact tie; "
               "the tie is a float-equality event the probe could only reach by constructing the moment state, never by a realistic "
               "fold sequence (0 of 36 differ)",
        title="No check pins the solar-aperture variance guard at its exact 1e-6 tie",
        claim="Mutating coordinator.py:9402 `m[\"var\"] > 1e-6` to `>= 1e-6` moves the learned scale 1.0 -> 2.0 when the EWMA "
              "variance lands exactly on 1e-6, and the full gate stays green; no realistic fold sequence tried reaches the tie.",
        severity="low", direction="up",
        metric="_solar_aperture['scale'] after one fold whose variance update lands exactly on 1e-6 (ratio)"),
    "67495f7b404053fc": dict(
        cls="equivalent-candidate", b="fields_differing", m="fields_differing",
        inputs="weather forecast 0/1/10/48 h x solar series 0/48 h x Open-Meteo off/on = 16 cases, each on a first and a second "
               "call of one coordinator, all 10 ForecastArrays fields compared NaN-aware: 0 differ; positive arm: the outdoor list "
               "after the padding loop is 96 long on the baseline and 97 under the mutant (the mutant runs, its extra element is "
               "sliced off by [:n_steps] before any array is built, and the lists are rebuilt per call)",
        reach=["tests/config_flow_steps.py", "tests/entities.py", FEAT, "tests/solar_alignment.py"],
        should="none: no observable output of _forecast_arrays changes (every series is sliced [:n_steps]); a check could only "
               "read the internal list length"),
    "f0146f6f4901ec82": dict(
        cls="candidate", b="humidity_mean_baseline", m="humidity_mean_mutant",
        inputs="weather entity 85 % for 48 h, Open-Meteo hourly relative_humidity_2m 95 % for 72 h built by the production "
               "_parse_block, clock frozen at golden.START in UTC; null: Open-Meteo 85 %",
        reach=["tests/entities.py", "tests/solar_alignment.py"],
        should="tests/entities.py and tests/solar_alignment.py execute coordinator.py:7491 on the traced baseline, yet neither "
               "asserts that ForecastArrays.humidity carries Open-Meteo's humidity where the client has it",
        title="No check pins Open-Meteo's humidity overlay onto the forecast horizon",
        claim="Disabling coordinator.py:7491 `if rh is not None:` drops Open-Meteo's hourly humidity from the horizon "
              "(mean 95 % -> the entity's 85 %) and the full gate stays green.",
        severity="medium", direction="down",
        metric="mean of ForecastArrays.humidity over the 96-step horizon from _forecast_arrays (%)"),
    "5f950692fab8eb1b": dict(
        cls="equivalent-candidate", b="production_inputs_differing", m="production_inputs_differing",
        inputs="Open-Meteo hourly humidity 150 / 95 / -5 / NaN through the production _parse_block (max_value=100): 0 of 4 differ "
               "(out-of-range and non-finite samples are dropped before humidity_for, whose mean of in-range samples stays in "
               "[0, 100]); reach: line 7492 executes 96 times per call in the probe; positive arm: a 150 % series injected past "
               "the parser gives 100 vs 150, an input no production path builds",
        reach=[],
        should="none: the clamp is the identity on every value the only producer (open_meteo._parse_block, max_value=100) "
               "can deliver. No traced baseline executes coordinator.py:7492 (the closure scripts never drive an available "
               "Open-Meteo client with humidity); the probe reaches it, so the line is reachable, not dead"),
    "4410da4e8eb84cb8": dict(
        cls="candidate", b="hold_baseline", m="hold_mutant",
        inputs="dhw_enabled False, dhw_temperature 40 C < dhw_min_temp 45 C, room 21 C, floor 17 C; null: dhw 55 C",
        reach=[FEAT],
        should="tests/features.py (traced reach of coordinator.py:8838) has no _guard_floor_hold check with hot water disabled "
               "and a low tank reading asserting False",
        title="No check pins _guard_floor_hold's hot-water arm to installs with hot water enabled",
        claim="Mutating coordinator.py:8838 `params.dhw_enabled and ...` to `or` makes a disabled tank's low reading hold the "
              "peak/price guard (verdict 0 -> 1) and the full gate stays green.",
        severity="low", direction="up",
        metric="_guard_floor_hold() verdict, 1 hold / 0 none, for one coordinator state (bool)"),
    "7ec91efc2c6deffd": dict(
        cls="candidate", b="hold_baseline", m="hold_mutant",
        inputs="dhw_enabled True, dhw_temperature == dhw_min_temp == 45.0 C (the tie); null 44.9 C",
        reach=[FEAT],
        should="tests/features.py (traced reach of coordinator.py:8838) has no _guard_floor_hold check at dhw_temperature == "
               "dhw_min_temp asserting False",
        title="No check pins _guard_floor_hold's hot-water comparison at its tie",
        claim="Mutating coordinator.py:8838 `dhw_temperature < dhw_min_temp` to `<=` makes a tank exactly at its minimum hold "
              "the guard (verdict 0 -> 1) and the full gate stays green.",
        severity="low", direction="up",
        metric="_guard_floor_hold() verdict, 1 hold / 0 none, for one coordinator state (bool)"),
    "f11665aaedbf2550": dict(
        cls="candidate", b="hold_baseline", m="hold_mutant",
        inputs="dhw_enabled True, dhw_temperature 40 C < dhw_min_temp 45 C, room 21 C; null: room 16 C under the 17 C floor",
        reach=[FEAT],
        should="tests/features.py (traced reach of coordinator.py:8838) has no _guard_floor_hold check with hot water enabled "
               "and the tank under dhw_min_temp asserting True",
        title="No check pins that a cold hot-water tank overrides the peak/price guard",
        claim="Removing coordinator.py:8838's hot-water arm (`if False:`) lets the peak/price guard keep suppressing while the "
              "tank sits under dhw_min_temp (verdict 1 -> 0) and the full gate stays green.",
        severity="medium", direction="down",
        metric="_guard_floor_hold() verdict, 1 hold / 0 none, for one coordinator state (bool)"),
    "9b72b944ac12fa25": dict(
        cls="candidate", b="hold_baseline", m="hold_mutant",
        inputs="two_zone_enabled True, upper floor 16 C under the 17 C floor, room 21 C; null: room 16 C as well",
        reach=[FEAT],
        should="tests/features.py (traced reach of coordinator.py:8842) has no two-zone _guard_floor_hold check with a zone "
               "under min_temp asserting True",
        title="No check pins that a breached zone floor overrides the peak/price guard",
        claim="Disabling coordinator.py:8842 `if params.two_zone_enabled:` lets the guard keep suppressing while a floor zone "
              "is under min_temp (verdict 1 -> 0) and the full gate stays green.",
        severity="medium", direction="down",
        metric="_guard_floor_hold() verdict, 1 hold / 0 none, for one coordinator state (bool)"),
    "fd1cc23d380739ba": dict(
        cls="candidate", b="hold_baseline", m="hold_mutant",
        inputs="room == min_temp == 17.0 C (the tie), hot water off; null 17.1 C",
        reach=[FEAT],
        should="tests/features.py (traced reach of coordinator.py:8847) has no _guard_floor_hold check at a temperature "
               "exactly on the floor asserting False",
        title="No check pins _guard_floor_hold's comfort-floor comparison at its tie",
        claim="Mutating coordinator.py:8847 `float(t) < floor` to `<=` makes a room exactly at min_temp hold the guard "
              "(verdict 0 -> 1) and the full gate stays green.",
        severity="low", direction="up",
        metric="_guard_floor_hold() verdict, 1 hold / 0 none, for one coordinator state (bool)"),
    "c20f346300d7efc1": dict(
        cls="candidate", b="margin_baseline", m="margin_mutant",
        inputs="now 2026-01-15T12:00Z; events now-1 d, now-2 d and one stamped -05:00 whose instant is 1 h inside the 14-day "
               "cutoff; null: that event stamped +00:00",
        reach=[FEAT],
        should="tests/features.py (traced reach of coordinator.py:9292) has no _immersion_dhw_margin check with an aware event "
               "stamped in another offset than now's, asserting it is counted by its true instant",
        title="No check pins _immersion_dhw_margin to an event's true instant across UTC offsets",
        claim="Mutating coordinator.py:9292 `when.tzinfo is None and ...` to `or` re-labels an aware event with now's zone, "
              "dropping a -05:00 event 1 h inside the cutoff out of the window (margin 2.0 -> 0.0 K); the full gate stays green.",
        severity="low", direction="down",
        metric="_immersion_dhw_margin(now) for three immersion events (K)"),
    "60f673da42f9d671": dict(
        cls="candidate", b="margin_baseline", m="margin_mutant",
        inputs="now 2026-01-15T12:00Z; events now-1 d, now-2 d and one exactly at now-14 d (the tie); null: 1 s inside",
        reach=[FEAT],
        should="tests/features.py (traced reach of coordinator.py:9294) has no _immersion_dhw_margin check with an event "
               "exactly at the 14-day cutoff asserting it counts",
        title="No check pins _immersion_dhw_margin's 14-day window at its boundary",
        claim="Mutating coordinator.py:9294 `when >= cutoff` to `>` drops an event exactly 14 days old from the count "
              "(margin 2.0 -> 0.0 K) and the full gate stays green.",
        severity="low", direction="down",
        metric="_immersion_dhw_margin(now) for three immersion events (K)"),
    "661116d11d6faa49": dict(
        cls="equivalent-candidate", b="inputs_differing", m="inputs_differing",
        inputs="indoor_humidity_entity unset / None / '' x bus empty / live 55 % sensor / unavailable sensor / 150 % sensor "
               "= 12 inputs, comparing the value and the count of log records at every level: 0 differ (InputReader(hass, {}) "
               "with no entity id returns ok=False and its InputHealth is local to the call); positive arm: a configured entity "
               "reads 55.0 in both",
        reach=["tests/config_flow_steps.py", "tests/entities.py", FEAT],
        should="none: with no entity id, the fall-through read returns ok=False, so the function returns None as the early "
               "exit does"),
    "b6ac2d53028d45a3": dict(
        cls="candidate", b="space_kw_baseline", m="space_kw_mutant",
        inputs="power entity configured; observed mode hot-water-only (space_heat False, dhw True), plan 0 kW space / 1.5 kW "
               "hot water, meter 1.5 kW; also mode off, meter 0 kW (None -> 0.0 as well); null: space-heat mode 2 kW / 2 kW",
        reach=["tests/boost_drift_replay.py", "tests/entities.py", FEAT],
        should="tests/boost_drift_replay.py, tests/entities.py and tests/features.py execute coordinator.py:5049 on the traced "
               "baseline, yet none asserts _interval_space_power() is None while the observed mode heats no rooms",
        title="No check pins that a mode heating no rooms yields no space-power sample",
        claim="Disabling coordinator.py:5049's mode guard turns a hot-water-only interval's skipped sample (None) into a "
              "confident 0.0 kW space-heat sample for the interval learners, and the full gate stays green.",
        severity="medium", direction="to_zero",
        metric="_interval_space_power() in kW, None printed as -1, for one observed-mode interval"),
    "7f2768bd0a78b4bf": dict(
        cls="equivalent-candidate", b="inputs_differing", m="inputs_differing",
        inputs="outdoor -60..+34 C in 1 K steps plus NaN, +inf, -inf (98 values) x cop_scale 0.5 / 1.0 / 1.5 x tank dhw / "
               "buffer = 588 inputs: 0 differ, min COP seen 1.0 (ThermalModel.compute_cop's only return is _cop_law's "
               "max(cop, 1.0); max(nan, 1.0) is nan in both arms); positive arm: compute_cop forced to 0.5 gives 123.153 vs "
               "61.576 degC/h, so the probe sees the clamp when it acts",
        reach=["tests/block_duty.py", "tests/boost_drift_replay.py", "tests/config_flow_steps.py", "tests/entities.py", FEAT,
               "tests/finite_boundary.py", "tests/manual_plan.py", "tests/solar_alignment.py"],
        should="none: the clamp duplicates the floor compute_cop already applies; no input reaches cop < 1"),
    "1ee0ec8960fb9a66": dict(
        cls="candidate", b="rise_dhw_baseline", m="rise_dhw_mutant",
        inputs="default parameters with a 200 L DHW tank (0.232 kWh/K) and the default buffer (0.0406 kWh/K), 5 kW electrical, "
               "outdoor 5 C, tank 'dhw'; null: tank 'buffer'",
        reach=["tests/block_duty.py", "tests/boost_drift_replay.py", "tests/config_flow_steps.py", "tests/entities.py", FEAT,
               "tests/finite_boundary.py", "tests/manual_plan.py", "tests/solar_alignment.py"],
        should="eight closure scripts execute coordinator.py:5104 on the traced baseline (block_duty, boost_drift_replay, "
               "config_flow_steps, entities, features, finite_boundary, manual_plan, solar_alignment), yet none asserts "
               "_max_pump_rise('dhw') == thermal_kw / dhw_store.capacity_kwh_per_c",
        title="No check pins _max_pump_rise('dhw') to the hot-water tank's own capacity",
        claim="Disabling coordinator.py:5104 `if tank == \"dhw\":` computes the DHW tank's maximum pump rise from the buffer's "
              "mass (71.659 -> 409.483 degC/h), raising the external-heat threshold on the DHW tank 5.7x, and the full gate stays green.",
        severity="medium", direction="up",
        metric="_max_pump_rise('dhw') in degC/h on default parameters with a 200 L tank"),
}


def results(probe):
    p = subprocess.run([PY, probe], cwd=ROOT, env=dict(os.environ, PYTHONPATH="tests/hastub"), capture_output=True,
                       text=True, timeout=900)
    out = {}
    for ln in p.stdout.splitlines():
        m = re.match(r"RESULT\s+(\w+)=(\S+)", ln)
        if m:
            out[m.group(1)] = m.group(2)
    return p.returncode, out


def main(key):
    row = next(l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.split("\t")[0] == key)
    _k, src, file, line, function, cluster, slice_, fullnet, kind, reach, m4src = row
    mut = json.loads((S1 / "state/results/complete" / f"{key}.json").read_text())["mutant"]
    gate = json.loads((W / "gates" / f"{key}.json").read_text())
    verdict = gate["verdict"]
    sp = SPEC[key]
    probe = f"{PR}/probe_{key}.py"
    rc, res = results(probe)
    rec = {
        "key": key,
        "site": f"{file}:{line} {kind}",
        "patch": f"{mut['old'].strip()} -> {mut['new'].strip()}",
        "function": function,
        "cluster": cluster,
        "slice": slice_,
        "m4_source": m4src,
        "gate": {k: gate.get(k) for k in ("verdict", "killed_by", "gate_rc", "failed_scripts", "summary", "wall_s",
                                          "child_cpu_s", "load1_start", "load1_end", "provisional", "command", "cap_s")
                 if k in gate},
        "gate_record": f"dev/audit/rounds/round11/D3/s1/wave/D3-g07/gates/{key}.json",
        "gate_command": f"PYTHONPATH=tests/hastub python3 {FULLGATE} run --src {src} --key {key}",
        "machine": "box D3-g07: nproc 4, Intel(R) Xeon(R) Processor @ 2.10GHz, 16 GB; wall/CPU/load provisional",
    }
    if verdict == "KILLED":
        logp = W / "gates" / f"{key}.log"
        lines = []
        if logp.exists():
            lines = [l.rstrip() for l in logp.read_text(errors="replace").splitlines()
                     if re.search(r"\bFAIL|FAILED|Traceback|Error\b", l)][:40]
        rec.update({"class": "killed", "failing_check_lines": lines,
                    "non_finding": f"the suite fails on it: killed by {', '.join(gate.get('killed_by') or [])}"})
    elif verdict == "TIMEOUT":
        logp = W / "gates" / f"{key}.log"
        last = None
        if logp.exists():
            heads = re.findall(r"^=== (.+?) ===", logp.read_text(errors="replace"), re.M)
            last = heads[-1] if heads else None
        rec.update({"class": "timeout", "cap_s": gate.get("cap_s", 14400), "last_section_running": last})
    else:
        rec["class"] = sp["cls"]
        rec["red_as_null"] = verdict == "RED-AS-NULL"
    rec["probe"] = {"path": probe, "command": f"PYTHONPATH=tests/hastub {PY} {probe}", "rc": rc,
                    "baseline_value": res.get(sp["b"]), "mutant_value": res.get(sp["m"]),
                    "baseline_result": sp["b"], "mutant_result": sp["m"], "all_results": res,
                    "inputs_tried": sp["inputs"]}
    rec["traced_reach"] = sp["reach"]
    rec["should_fail"] = sp["should"]
    if rec["class"] == "candidate":
        sym = G + function.split(".", 1)[1]
        rec["finding"] = {
            "title": sp["title"], "claim": sp["claim"], "step": "D3.M3", "scope": "D3-s1", "class_guess": "I1",
            "severity_claimed": sp["severity"], "stop_rule_class": "bug",
            "metric_definition": sp["metric"],
            "instrumented_symbol": sym,
            "harness_paths": [FULLGATE, probe],
            "evidence_command": f"PYTHONPATH=tests/hastub python3 {FULLGATE} run --src {src} --key {key}  (gate: {verdict}); "
                                f"PYTHONPATH=tests/hastub {PY} {probe}  ({sp['b']}={res.get(sp['b'])}, {sp['m']}={res.get(sp['m'])})",
            "perturbation": {"change": f"{file}:{line} `{mut['old'].strip()}` -> `{mut['new'].strip()}` (applied in memory by "
                                       "the probe; on disk by fullgate.py for the gate)",
                             "expected_direction": sp["direction"],
                             "observed_value": f"{res.get(sp['b'])} -> {res.get(sp['m'])}"},
            "null_control": {"command": f"PYTHONPATH=tests/hastub {PY} {probe}",
                             "value": f"null_baseline={res.get('null_baseline')}, null_mutant={res.get('null_mutant')}",
                             "note": "the same mutant on an input where the edited condition cannot matter; gate null: "
                                     "dev/audit/rounds/round11/D3/s1/wave/D3-g07/gates/null.json"},
            "phenomenon_property": "every guard of " + function + " that changes its returned value has a check that fails when the guard is mutated",
            "seam_rule": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv  (the wave's full-gate survivors; this box: dev/audit/rounds/round11/D3/s1/wave/D3-g07/keys.tsv)",
            "files": [file] + sp["reach"],
            "proposed_fix_scope": f"a check in {sp['reach'][0] if sp['reach'] else 'tests/features.py'} driving {function} on the "
                                  "probe's input and asserting the baseline value",
        }
    (W / "results" / f"{key}.json").write_text(json.dumps(rec, indent=1) + "\n")
    print(f"RECORD {key} verdict={verdict} class={rec['class']} probe {sp['b']}={res.get(sp['b'])} {sp['m']}={res.get(sp['m'])} rc={rc}")


if __name__ == "__main__":
    for k in sys.argv[1:]:
        main(k)
