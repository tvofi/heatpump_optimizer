#!/usr/bin/env python3
"""Writes results/<key>.json for every gated key of keys.tsv (judgement table J below + gates/<key>.json + the probe's printed numbers).
Command: python3 dev/audit/rounds/round11/D3/s1/wave/D3-g42/build_results.py   (from the tree root; PYTHONPATH=tests/hastub; runs each probe)"""
import json, csv, subprocess, sys, os
from pathlib import Path
W = Path(__file__).resolve().parent; S1 = W.parent.parent
ROOT = S1.parents[5]
PY = os.path.expanduser("~/venv-ci/bin/python3")
# class, severity, title, claim/answer, should_fail, class_guess
J = {
"5a66d572bfdd1491": ("equivalent-candidate", None, "", "dT_buf == dT_cap writes identical values in both branches: refused=(dT_buf-dT_cap)*C=0 and dT_buf=dT_cap. 1170 line hits over a 90-cell grid incl. T_buf at buffer_max_temp: 0 output differences; 53 cells have refused>0", "", ""),
"5b8e7044ee7974f8": ("candidate", "low", "apply_dhw_coil lifts a wood tank colder than the DHW inlet up to the inlet when no coil heat flows (q_coil == 0)",
  "With state.wood_tank_temperature below dhw_inlet_reference (no floor ties it to the inlet outside draw steps: coordinator.py:6746-6756), the baseline leaves it unchanged; the `>= 0.0` mutant runs the decrement with q_coil=0 and clamps the wood tank UP to the inlet (2.0 -> 10.0, 9.5 -> 10.0).",
  "tests/features.py: a unit asserting that apply_dhw_coil with wood < dhw_inlet_reference leaves wood_tank_temperature unchanged (and the drawn kW unchanged)", "missing-boundary-test"),
"7684dd370eaae807": ("equivalent-candidate", None, "", "radiation == 0: product is 0.0 for every finite parameter set (default, 1e6 m2, zero area, negative scale); the only difference over 15 cells is the sign of a zero (-0.0 for input -0.0 / negative scale, equal under ==)", "", ""),
"f7e051cc469b465f": ("candidate", "low", "compute_solar_gain's `<= 0` early return is the only barrier to negative solar gain, and no test feeds a negative irradiance",
  "The solar sensor path (coordinator.py:6709-6713) and the forecast path (7341-7342) apply no max(0); with the guard off compute_solar_gain(-10) returns a negative kW (heat loss booked as solar) where the baseline returns 0.0.",
  "any closure script that executes line 3517 (tests/features.py, tests/validate.py, tests/optimality.py): assert compute_solar_gain(-10.0) == 0.0", "missing-boundary-test"),
"523356020b4bb37b": ("equivalent-candidate", None, "", "to == from: hot == cold so log(1)=0 and clip gives 0.0 (hot<=0 returns 0.0 first); 48 input cells (from 10..55, ambient 10/20/25, to = from or from-1e-9): 0 differences", "", ""),
"eb094b1749a24474": ("equivalent-candidate", None, "", "With the to>=from guard off, to>=from still returns 0.0 through hot<=0 or the clip (default UA, 3 cells). It diverges (0.0 -> 168.0) only for ua_kw_per_c == 0, which the config cannot produce: dhw_tank_heat_loss_coefficient clips dhw_cooling_rate at DHW_COOLING_RATE_MIN=0.05 (cooling_rate 0, -5, 1e-12 all give ua 4.64e-4); the zero was reached only by priming the memo cache", "", ""),
"402ffd06ddbd856a": ("candidate", "low", "dhw_coast_hours returns 168 h instead of 0 for a tank at exactly ambient",
  "from_temp == ambient_temp (e.g. 20/10/20, 30/10/30): baseline 0.0 (tank never coasts), mutant `hot < 0.0` falls to the cold<=0 branch and returns 168.0.",
  "tests/features.py or tests/validate.py: dhw_coast_hours(20.0, 10.0, 20.0) == 0.0", "missing-boundary-test"),
"d90533f4d17cfa14": ("candidate", "low", "dhw_coast_hours's hot<=0 guard has no test: a tank at or below ambient coasts 168 h",
  "from_temp <= ambient: baseline 0.0; guard off gives 168.0 (15/10/20, 20/10/20, 10/5/20).",
  "tests/features.py: dhw_coast_hours(15.0, 10.0, 20.0) == 0.0", "missing-boundary-test"),
"c3ce2c5919d2c385": ("equivalent-candidate", None, "", "ua == 0 is the only input the edit changes (baseline 168.0, mutant ZeroDivisionError) and is not config-reachable: DHW_COOLING_RATE_MIN=0.05 floors ua at 4.64e-4 (cooling_rate 0/-5/1e-12 probed); ua=1e-12 gives 168.0 in both", "", ""),
"011b9e2e975b5e98": ("candidate", "medium", "dhw_coast_hours's [0,168] clip has no test; at the config's minimum cooling rate the coast reads 346.6 h",
  "ThermalParameters(dhw_cooling_rate=0.0) (clipped to ua 4.64e-4) gives coast hours 168.0 on the baseline and 346.57 with the clip dropped; reachable from configuration, not only forced.",
  "tests/features.py or tests/optimality.py: dhw_coast_hours(60, 40) <= 168.0 at dhw_cooling_rate=0.0", "missing-boundary-test"),
"9df41596c4fa89c6": ("candidate", "low", "Rain threshold boundary: precipitation == 0.1 mm/h is dry on the baseline",
  "effective_heat_loss_coefficient(0.1, 0, 0.1): baseline equals the dry value, `>=` applies the 5 % ramp of the 1.15 multiplier. Any weather entity reporting exactly 0.1 mm reaches it.",
  "tests/features.py: effective_heat_loss_coefficient at precipitation 0.1 equals the dry value", "missing-boundary-test"),
"029c040224dc4e38": ("candidate", "medium", "Heavy-rain heat-loss multiplier is uncapped without the min(.., 1.0): no test has rain above 2 mm/h",
  "precipitation 4/10/50 mm/h: baseline saturates at rain_heat_loss_multiplier (1.15); the mutant scales the loss linearly (x1.30 at 4, x1.75 at 10 mm/h) with no ceiling. Forecast rain is clamped only to >=0 and <=1000 (coordinator.py:2980, 7334).",
  "tests/features.py: effective_heat_loss_coefficient(precip=10) == effective(precip=2)", "missing-boundary-test"),
"5141eb1194306254": ("equivalent-candidate", None, "", "flow == cop_flow_reference_temp: carnot_flow == carnot_ref exactly, ratio 1.0, so both arms return 1.0; 24 cells over 4 parameter sets x 6 outdoor temps: 0 differences", "", ""),
"babeb7b3990a574b": ("equivalent-candidate", None, "", "The 1.0 K lift floor only binds when cop_reference_temp > flow_temp (the outdoor cap exceeds the flow); default params (7 C / 35 C) never reach it. Moves only with cop_reference_temp 40-50 C, which no config or option surface sets (no field in const.py/config_flow.py, no clamp)", "", ""),
"256e285aadb8b31d": ("equivalent-candidate", None, "", "carnot_ref <= 1e-9 needs cop_flow_reference_temp <= -273.15 C; for ref in -100..60 C (24 cells) both arms agree; the only divergence (ZeroDivisionError) is at ref=-273.15, outside any physical configuration", "", ""),
}
def probe_nums(key):
    p = W / "probes" / f"probe_{key}.py"
    r = subprocess.run([PY, str(p)], capture_output=True, text=True, cwd=ROOT, env=dict(os.environ, PYTHONPATH="tests/hastub"))
    (W / "probes" / f"probe_{key}.out").write_text(r.stdout + r.stderr)
    d = {}
    for l in r.stdout.splitlines():
        if l.startswith("RESULT "):
            k, v = l[7:].split("=", 1); d[k] = v
    return d
def main():
    rows = list(csv.DictReader(open(W / "keys.tsv"), delimiter="\t"))
    for r in rows:
        k = r["key"]; g = W / "gates" / f"{k}.json"
        if not g.exists() or (W / "results" / f"{k}.json").exists() and "--force" not in sys.argv: continue
        gd = json.load(open(g)); m = json.load(open(S1 / "state/results/complete" / f"{k}.json"))["mutant"]
        nums = probe_nums(k)
        cls, sev, title, claim, sf, cg = J[k]
        verdict = gd.get("verdict")
        if verdict == "KILLED": cls = "killed"
        elif verdict == "TIMEOUT": cls = "timeout"
        moved = nums.get("metrics_moved")
        rec = dict(key=k, site=f"{m['file']}:{m['line']} {m['kind']}", patch=f"{m['old'].strip()} -> {m['new'].strip()}", function=r["function"], cluster=r["cluster"],
            gate={x: gd.get(x) for x in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end")}, **{"class": cls},
            probe=dict(path=f"dev/audit/rounds/round11/D3/s1/wave/D3-g42/probes/probe_{k}.py", command=f"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g42/probes/probe_{k}.py",
                       output=f"dev/audit/rounds/round11/D3/s1/wave/D3-g42/probes/probe_{k}.out", metrics_moved=moved, numbers=nums, provisional_machine="4 vCPU, see MACHINE.txt"),
            should_fail=sf, note=claim, carried_m4=r["m4_source"])
        if cls == "candidate":
            rec.update(title=title, claim=claim, step="D3.M3", scope="D3-s1", class_guess=cg, severity_claimed=sev,
                metric_definition=f"probe_{k}.py RESULT metrics_moved: count of probed outputs that differ between the baseline and the one-line mutant",
                harness_paths=["dev/audit/rounds/round11/D3/s1/fullgate.py", rec["probe"]["path"]], evidence_command=rec["probe"]["command"],
                perturbation=f"{rec['patch']} (thermal_model.py:{m['line']}); numbers move baseline -> mutant as listed in probe output",
                null_control="fullgate.py null (comment-only marker) is red only on the artefact scripts; inputs the line cannot distinguish in the same probe give no movement")
        (W / "results" / f"{k}.json").write_text(json.dumps(rec, indent=1))
        print("wrote", k, cls, moved)
if __name__ == "__main__": main()
