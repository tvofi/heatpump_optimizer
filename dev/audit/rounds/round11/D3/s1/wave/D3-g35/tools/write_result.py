#!/usr/bin/env python3
"""Write results/<key>.json for box D3-g35 from gates/<key>.json + the probe's recorded output."""
import csv, json, re, subprocess, sys
from pathlib import Path

TREE = Path("/root/audit-r11-D3-s1")
W = TREE / "dev/audit/rounds/round11/D3/s1/wave/D3-g35"
PROBES = "dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes"
FN = "custom_components/heatpump_optimizer/sysid.py"
FEAT = ("tests/features.py (its traced baseline executes the line: the slice box's closure trace; "
        "the one-state identify() checks near features.py:7850-7972 and 29353-29387 drive it)")

# key -> (class, should_fail assertion it lacks, title, claim, severity rationale, direction)
INFO = {
 "31bb6bebd6b45f0e": ("equivalent-candidate",
   "none possible: solution.shape[0] is 4 (four-column solve) or 2 (fallback), never 3, so >= 3 and > 3 agree on every reachable input", None, None, None),
 "501a5e7cda702183": ("candidate",
   "a drifting-sensor identify() check asserting completed and internal_gains_kw == the drift-free gains (0.30 kW at +0.01 C/h drift)",
   "identify() drift subtraction from the intercept (sysid.py:2146) can be switched off with the full gate green",
   "With the guard at sysid.py:2146 forced False, a clean step test on a sensor drifting +0.01 C/h no longer completes (baseline completed, gains 0.300 kW; mutant refuses 'sensor drift collapsed into heat-loss'), and 18 of 30 probe cases change; GATE_SCOPE=full GOLDEN_MODE=drift stays green.",
   "up"),
 "20cde1046cbd5681": ("candidate",
   "an identify() check on a fit whose gains_kw is exactly 2.0 asserting it completes with internal_gains_kw == 2.0",
   "identify() gains band upper bound (sysid.py:2154) is not pinned at its edge",
   "A step test whose fitted gains_kw is exactly 2.0 completes at the baseline and is refused 'fitted gains outside plausible bounds' under `gains_kw < 2.0`; the full gate stays green.",
   "to_zero"),
 "6cfdb101dc87a6ea": ("candidate",
   "an identify() check on a fit whose gains_kw is exactly -0.5 asserting it completes with internal_gains_kw clipped to 0.0",
   "identify() gains band lower bound (sysid.py:2154) is not pinned at its edge",
   "A step test whose fitted gains_kw is exactly -0.5 completes (gains clipped to 0.0) at the baseline and is refused 'fitted gains outside plausible bounds' under `-0.5 < gains_kw`; the full gate stays green.",
   "to_zero"),
 "d203230963349f60": ("candidate",
   "an identify() check on a plant with gains -0.3 kW asserting internal_gains_kw == 0.0 (the clip)",
   "identify() publishes negative internal gains when the clip at sysid.py:2162 is dropped, gate green",
   "Dropping np.clip(gains_kw, 0.0, 2.0) at sysid.py:2162 publishes internal_gains_kw -0.300 kW instead of 0.0 on a plant with true gains -0.3 kW; the full gate stays green.",
   "sign_flip"),
 "078e78462859ff6b": ("equivalent-candidate",
   "none possible: drift_c_per_h is None exactly on the two-column fallback, where a.shape[1] == 2, so `and` and `or` agree on every reachable input", None, None, None),
 "5654f855fcc27724": ("candidate",
   "a drifting-sensor identify() check asserting the published confidence equals the drift-corrected excursion's (0.98131 at +0.01 C/h)",
   "identify() excursion drift correction (sysid.py:2187, >= 4 -> > 4) is unpinned",
   "With `a.shape[1] > 4` at sysid.py:2187 the excursion is no longer drift-corrected; on a +0.01 C/h drifting sensor the published confidence moves 0.981307 -> 0.981529 and 14 of 30 probe cases change; the full gate stays green.",
   "up"),
 "c303df62a0b7b9bc": ("candidate",
   "a drifting-sensor identify() check asserting the published confidence equals the drift-corrected excursion's (0.98131 at +0.01 C/h)",
   "identify() excursion drift correction (sysid.py:2187) can be switched off with the full gate green",
   "With the guard at sysid.py:2187 forced False the excursion is no longer drift-corrected; on a +0.01 C/h drifting sensor the published confidence moves 0.981307 -> 0.981529 and 14 of 30 probe cases change; the full gate stays green.",
   "up"),
 "ed00e6c2abf2aa66": ("equivalent-candidate",
   "none found: every completing fit tried has excursion >= 2.04e-7 C (q swept 1e-3..0); below that the fit is refused before publication, so excursion == 1e-9 never reaches a published result", None, None, None),
 "4593852cf3862b3c": ("candidate",
   "an identify() check on a fit whose tau is exactly 0.1 h asserting it completes",
   "identify() tau lower bound (sysid.py:2223) is not pinned at its edge",
   "A fast-plant step test whose fitted tau is exactly 0.1 h completes at the baseline and is refused 'fitted parameters outside plausible bounds' under `0.1 < tau`; the full gate stays green.",
   "to_zero"),
 "64f3ef1feaaf7bc9": ("candidate",
   "an identify() check on a fit whose UA is exactly 0.01 kW/C asserting it completes",
   "identify() UA lower bound (sysid.py:2223) is not pinned at its edge",
   "A step test whose fitted UA is exactly 0.01 kW/C completes at the baseline and is refused 'fitted parameters outside plausible bounds' under `0.01 < ua`; the full gate stays green.",
   "to_zero"),
 "784e362919d88a92": ("candidate",
   "an identify() check on a fit whose UA is exactly 5.0 kW/C asserting it completes",
   "identify() UA upper bound (sysid.py:2223) is not pinned at its edge",
   "A step test whose fitted UA is exactly 5.0 kW/C completes at the baseline and is refused 'fitted parameters outside plausible bounds' under `ua < 5.0`; the full gate stays green.",
   "to_zero"),
 "d661d68f54982097": ("candidate",
   "an identify() check on a fit whose tau is exactly 200.0 h asserting it completes",
   "identify() tau upper bound (sysid.py:2223) is not pinned at its edge",
   "A slow-plant step test whose fitted tau is exactly 200.0 h completes at the baseline and is refused 'fitted parameters outside plausible bounds' under `tau < 200.0`; the full gate stays green.",
   "to_zero"),
 "a5b06d898bf0ba03": ("candidate",
   "an identify() check with sensor_drift_prior_c_per_h equal to the fitted |drift| asserting the settle cross-check is skipped (completed)",
   "identify() settle cross-check precondition |drift| < prior (sysid.py:2237) is not pinned at its edge",
   "With sensor_drift_prior_c_per_h equal to the fitted |drift| (0.009999981 C/h) on an unsettled settle, the baseline skips the cross-check and completes; under `<=` the cross-check runs and refuses 'sensor drift collapsed into heat-loss'; the full gate stays green.",
   "to_zero"),
 "c51115b0104a8bf5": ("candidate",
   "an identify() check whose last settling sample reads exactly 1e-6 C above outdoor asserting the cross-check is skipped (completed)",
   "identify() settle cross-check zero-ΔT guard (sysid.py:2244) is not pinned at its edge",
   "When the last settling sample reads exactly 1e-6 C above outdoor, the baseline skips the steady-state UA and completes; under `>= 1e-6` ua_ss = (P+G)/1e-6 refuses 'sensor drift collapsed into heat-loss'; the full gate stays green.",
   "to_zero"),
 "4da9d281d4714565": ("candidate",
   "an identify() check whose settle UA disagrees with the fit by exactly 10 % asserting it completes",
   "identify() settle cross-check 10 % tolerance (sysid.py:2246) is not pinned at its edge",
   "A step test whose steady-state settle UA disagrees with the fit by exactly 0.10 completes at the baseline and is refused 'sensor drift collapsed into heat-loss' under `>= 0.10`; the full gate stays green.",
   "to_zero"),
}


def probe_numbers(key, out):
    txt = Path(out).read_text()
    g = lambda pat: (re.search(pat, txt) or [None, None])[1]
    base = g(r"RESULT key_\w+\.baseline=(\S+)")
    mut = g(r"RESULT key_\w+\.mutant=(\S+)")
    diff = g(r"RESULT differing_cases=(\d+)")
    cases = g(r"RESULT cases=(\d+)")
    hunt = re.search(r"RESULT hunt_hit=(\d)\s+# input (.*)", txt)
    inputs = [ln.split("RESULT ", 1)[1] for ln in txt.splitlines() if ln.startswith("RESULT case[")
              and ".baseline=" in ln]
    labels = [re.match(r"case\[(.*?)\]", s).group(1) for s in inputs]
    return {"baseline_value": base, "mutant_value": mut, "differing_cases": int(diff) if diff else None,
            "cases": int(cases) if cases else None,
            "hunt": (f"hit={hunt.group(1)} {hunt.group(2)}" if hunt else None),
            "inputs_tried": labels, "raw_out": txt}


def main(key, out):
    keys = {r["key"]: r for r in csv.DictReader(open(W / "keys.tsv"), delimiter="\t")}
    k = keys[key]
    gate = json.loads((W / "gates" / f"{key}.json").read_text())
    mut = json.loads((TREE / f"dev/audit/rounds/round11/D3/s1/state/results/complete/{key}.json").read_text())["mutant"]
    cls, should, title, claim, direction = INFO[key]
    verdict = gate.get("verdict")
    if verdict == "KILLED":
        cls = "killed"
    elif verdict == "TIMEOUT":
        cls = "timeout"
    pn = probe_numbers(key, out)
    cmd = f"PYTHONPATH=tests/hastub python3 {PROBES}/probe_{key}.py"
    rec = {
        "key": key,
        "site": f"{FN}:{k['line']} {k['kind']}",
        "patch": f"{mut['old'].strip()} -> {mut['new'].strip()}",
        "function": k["function"], "cluster": k["cluster"],
        "gate": {f: gate.get(f) for f in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end")},
        "gate_record": f"dev/audit/rounds/round11/D3/s1/wave/D3-g35/gates/{key}.json",
        "class": cls,
        "m4_carried": k["m4_source"],
        "probe": {"path": f"{PROBES}/probe_{key}.py", "command": cmd,
                  "baseline_value": pn["baseline_value"], "mutant_value": pn["mutant_value"],
                  "differing_cases": pn["differing_cases"], "cases": pn["cases"], "hunt": pn["hunt"],
                  "inputs_tried": pn["inputs_tried"]},
        "should_fail": {"script": FEAT, "assertion": should},
    }
    if verdict == "KILLED":
        rec["killed_by"] = gate.get("killed_by")
        rec["failing_lines"] = {"failed_scripts": gate.get("failed_scripts"), "fail_lines": gate.get("fail_lines"), "null_fail_lines": json.loads((W / "gates" / "null.json").read_text()).get("fail_lines")}
    if verdict == "TIMEOUT":
        rec["timeout_note"] = "past the 4 h cap; last script per the gate log"
    if cls == "candidate":
        rec.update({
            "title": title, "claim": claim, "step": "D3.M3", "scope": "D3-s1",
            "class_guess": "new",
            "severity_claimed": "low",
            "severity_reason": ("identify() is the harness-only one-state regression (#1395: the production "
                                "sequence with a declared plant routes to identify_slab), so the mutant reaches "
                                "no installed house; hygiene of the suite's pin, not user-visible"),
            "stop_rule_class": "hygiene",
            "metric_definition": "differing_cases: probe inputs whose published identify() result differs mutant vs baseline; plus the key case's value per arm",
            "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", f"{PROBES}/probe_{key}.py",
                              f"{PROBES}/sysid_probe_common.py"],
            "evidence_command": cmd,
            "perturbation": {"change": f"sysid.py:{k['line']} {mut['old'].strip()} -> {mut['new'].strip()} (in memory)",
                             "expected_direction": direction,
                             "observed_value": f"key case {pn['baseline_value']} -> {pn['mutant_value']}; differing_cases {pn['differing_cases']}/{pn['cases']}"},
            "null_control": {"command": "python3 dev/audit/rounds/round11/D3/s1/fullgate.py null (box D3-g35)",
                             "value": "see gates/null.json",
                             "note": "the probe's own null: the baseline arm vs itself is identical by construction (same module text, same inputs); differing_cases counts only mutant-vs-baseline"},
            "instrumented_symbol": "custom_components.heatpump_optimizer.sysid:SystemIdentification.identify",
            "files": [FN],
        })
    (W / "results" / f"{key}.json").write_text(json.dumps(rec, indent=1) + "\n")
    (W / "probes" / f"probe_{key}.out").write_text(pn["raw_out"])
    print("wrote", key, verdict, cls)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
