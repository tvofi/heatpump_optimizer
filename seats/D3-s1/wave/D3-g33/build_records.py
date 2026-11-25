#!/usr/bin/env python3
"""Box D3-g33: write results/<key>.json for a gated key from gates/<key>.json, the probe's two RESULT runs and a per-key spec.

Command: python3 dev/audit/rounds/round11/D3/s1/wave/D3-g33/build_records.py <key> [<key> ...]
"""
import json, os, sys
from pathlib import Path
TR = Path(__file__).resolve().parents[8]  # the export root
W = "dev/audit/rounds/round11/D3/s1/wave/D3-g33"
PO = TR / W / "probe_runs"  # the probes' two RESULT runs per key (<key>.base, <key>.mut)
MACH = "cloud box D3-g33 (re-fire container): Linux x86_64, nproc 4, Intel Xeon @ 2.30GHz, 16 GB, venv-ci CPython; probe run while a gate ran (load1 ~0.7)"
FEAT = "tests/features.py (traced, executes sysid.py:{line})"
S = {
 "0b6e291153f1d738": dict(line=1546, kind="CMP_BOUND", fn="conditions_met", cl="conditions_met@1541-1557",
   patch="in_window = cfg.start_hour <= hour < cfg.end_hour -> in_window = cfg.start_hour <= hour <= cfg.end_hour",
   cls="equivalent-candidate", metric="open_hours_flat", null="open_hours_default",
   inputs="windows (23,5) default, (1,5), (0,6), (22,2); each over hours 0..23",
   reach="unreachable through production (open_hours_default 6 under both arms)",
   sf="none through production: coordinator.py:4045 builds SysIdConfig without start_hour/end_hour, so only the wrapping default (23, 5) runs and the non-wrapping branch at sysid.py:1546 never executes in production; a direct unit call with window (1,5) separates (4 -> 5 open hours)"),
 "e38d4bea802156c3": dict(line=1546, kind="CMP_BOUND", fn="conditions_met", cl="conditions_met@1541-1557",
   patch="in_window = cfg.start_hour <= hour < cfg.end_hour -> in_window = cfg.start_hour < hour < cfg.end_hour",
   cls="equivalent-candidate", metric="open_hours_flat", null="open_hours_default",
   inputs="windows (23,5) default, (1,5), (0,6), (22,2); each over hours 0..23",
   reach="unreachable through production (open_hours_default 6 under both arms)",
   sf="none through production: coordinator.py:4045 builds SysIdConfig without start_hour/end_hour, so only the wrapping default (23, 5) runs and the non-wrapping branch at sysid.py:1546 never executes in production; a direct unit call with window (1,5) separates (4 -> 3 open hours)"),
 "20e001c48fb19330": dict(line=1549, kind="CMP_BOUND", fn="conditions_met", cl="conditions_met@1541-1557",
   patch="in_window = hour >= cfg.start_hour or hour < cfg.end_hour -> in_window = hour >= cfg.start_hour or hour <= cfg.end_hour",
   cls="candidate", metric="open_hours", null="open_hours_flat",
   inputs="default window (23,5) over hours 0..23; null (1,5); (22,2)",
   reach="reachable: production builds the default wrapping window (23, 5); under the mutant the 05:00-05:59 hour is admitted",
   sf=FEAT + ": no conditions_met check at hour == SysIdConfig().end_hour (5) under the default window asserting it refuses with 'outside the night window'",
   title="No check pins conditions_met's exclusive night-window end (05:00) on the default window; < -> <= is unseen",
   md="open_hours = hours of 0..23 (at :30) for which SystemIdentification.conditions_met at the production default SysIdConfig (window 23..5) does not refuse with 'outside the night window'.",
   dir="up", sev="low", nullarm="open_hours_flat (non-wrapping window (1,5), branch not taken): 4 -> 4"),
 "d435f0054d7c9881": dict(line=1557, kind="BOOLOP", fn="conditions_met", cl="conditions_met@1541-1557",
   patch="if price_horizon is not None and len(price_horizon): -> if price_horizon is not None or len(price_horizon):",
   cls="equivalent-candidate", metric="raised", null="ok_ramp",
   inputs="price_horizon None, np.array([]), ramp 0.5..2.0 (24 steps), flat ones(24); price 0.5",
   reach="unreachable through production: the only caller (sysid.py:1756) runs after coordinator.py:6379 has returned 'no_prices' for any horizon of fewer than 4 steps, so neither None nor an empty horizon reaches it",
   sf="none through production; a direct unit call with price_horizon None or empty separates (raised 0 -> 2)"),
 "95090bc58c6535b2": dict(line=1913, kind="CMP_BOUND", fn="identify", cl="identify@1913-2246",
   patch="if len(usable) < 6: -> if len(usable) <= 6:",
   cls="candidate", metric="reached_fit_6", null="reached_fit_7",
   inputs="5, 6 (the tie), 7, 21 samples at 0.25 h on the tests/features.py _sid_samples plant",
   reach="reachable: an experiment that collects exactly six usable samples (a 1.5 h run at the 15-min cadence) is refused 'not enough samples' under the mutant",
   sf=FEAT + ": no identify check on exactly six usable samples asserting it gets past the sample-count gate (the documented minimum is six)",
   title="No check pins identify's six-sample minimum at the tie; < 6 -> <= 6 is unseen",
   md="reached_fit_6 = 1 when SystemIdentification.identify on exactly six usable 15-min samples of the features.py plant returns a reason other than 'not enough samples' / 'not enough usable intervals'.",
   dir="down", sev="low", nullarm="reached_fit_7 (seven samples): 1 -> 1"),
 "505422349a01c3ff": dict(line=1922, kind="CMP_BOUND", fn="identify", cl="identify@1913-2246",
   patch="if dt_h <= 1e-3 or dt_h > 2.0: -> if dt_h < 1e-3 or dt_h > 2.0:",
   cls="candidate", metric="reached_fit_tie", null="reached_fit_null",
   inputs="interval 0.001 h (the tie), 0.0009 h, 0.0011 h, 0.0 h; null all 0.25 h; ua_31 on tests/features.py's 31-sample series with one 3.6 s interval",
   reach="reachable only when two samples land exactly 3.6 s apart: a float tie a coordinator cycle rarely produces",
   sf=FEAT + ": no identify check with an interval exactly 1e-3 h asserting it is dropped as unusable",
   title="No check pins identify's exclusive 1e-3 h minimum interval at the tie; <= -> < is unseen",
   md="reached_fit_tie = 1 when identify gets past the usable-interval gate on six samples whose third interval is exactly 1e-3 h, the others 15 min.",
   dir="up", sev="low", nullarm="reached_fit_null (all 15-min intervals): 1 -> 1"),
 "7dbbb95252ced538": dict(line=1922, kind="CMP_BOUND", fn="identify", cl="identify@1913-2246",
   patch="if dt_h <= 1e-3 or dt_h > 2.0: -> if dt_h <= 1e-3 or dt_h >= 2.0:",
   cls="candidate", metric="reached_fit_tie", null="reached_fit_null",
   inputs="interval 2.0 h (the tie), 1.99 h, 2.01 h; null all 0.25 h; ua_31 on tests/features.py's 31-sample series with one 2.0 h interval",
   reach="reachable only when two samples are exactly 7200 s apart (a stalled cycle landing on the edge)",
   sf=FEAT + ": no identify check with an interval exactly 2.0 h asserting it is kept as usable",
   title="No check pins identify's inclusive 2.0 h maximum interval at the tie; > -> >= is unseen",
   md="reached_fit_tie = 1 when identify gets past the usable-interval gate on six samples whose third interval is exactly 2.0 h, the others 15 min.",
   dir="down", sev="low", nullarm="reached_fit_null (all 15-min intervals): 1 -> 1"),
 "b413c17079bb8176": dict(line=1922, kind="GUARD_OFF", fn="identify", cl="identify@1913-2246",
   patch="if dt_h <= 1e-3 or dt_h > 2.0: -> if False:",
   cls="candidate", metric="raised_dup", null="reached_fit_null",
   inputs="interval 3.0 h, 0.0 h (duplicate timestamp), 1e-4 h; null all 0.25 h; ua_31 on tests/features.py's 31-sample series with one 3 h gap",
   reach="reachable: a duplicated sample timestamp (dt 0) or a stalled-cycle gap over 2 h is an ordinary input; under the mutant the gap is fitted as one interval and a duplicate raises ZeroDivisionError out of identify",
   sf=FEAT + ": no identify check feeding a duplicated timestamp or a > 2 h gap asserting the interval is dropped (identify returns without raising and the gap is not fitted)",
   title="No check exercises identify's usable-interval guard; removing it entirely (duplicate timestamp -> ZeroDivisionError) is unseen",
   md="raised_dup = 1 when SystemIdentification.identify raises on six 15-min samples with one duplicated timestamp; reached_fit_gap = 1 when a 3.0 h gap is accepted as a usable interval.",
   dir="up", sev="medium", nullarm="reached_fit_null (all 15-min intervals): 1 -> 1"),
 "aa6d264aa0411bcd": dict(line=1942, kind="CMP_BOUND", fn="identify", cl="identify@1913-2246",
   patch="if len(rows) < 5: -> if len(rows) <= 5:",
   cls="candidate", metric="reached_fit_6", null="reached_fit_7",
   inputs="6 samples (5 intervals, the tie), 7 samples, 8 samples with one 3.6 s interval (5 usable)",
   reach="reachable: six usable samples give five usable intervals, which the mutant refuses 'not enough usable intervals'",
   sf=FEAT + ": no identify check on exactly five usable intervals asserting it gets past the interval-count gate",
   title="No check pins identify's five-interval minimum at the tie; < 5 -> <= 5 is unseen",
   md="reached_fit_6 = 1 when identify on six usable 15-min samples (five usable intervals, noise-free plant) gets past both sample-count gates.",
   dir="down", sev="low", nullarm="reached_fit_7 (six intervals): 1 -> 1"),
}

def res(path):
    d = {}
    for l in open(path):
        if l.startswith("RESULT "):
            k, _, v = l[7:].strip().partition("=")
            d[k] = v
    return d

def main(k):
    s = S[k]; os.chdir(TR)
    g = json.load(open(f"{W}/gates/{k}.json"))
    b, m = res(PO / f"{k}.base"), res(PO / f"{k}.mut")
    probe_cmd = f"PYTHONPATH=tests/hastub python3 {W}/probes/probe_{k}.py"
    gate_cmd = f"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key {k}"
    site = f"sysid.py:{s['line']} {s['kind']}"
    v = g["verdict"]
    r = {"key": k, "site": site, "patch": s["patch"], "function": f"SystemIdentification.{s['fn']}",
         "cluster": f"sysid.py:SystemIdentification.{s['cl']}",
         "gate": {"verdict": v, "killed_by": g.get("killed_by", []), "gate_rc": g.get("gate_rc"), "wall_s": g.get("wall_s"),
                  "load1_start": g.get("load1_start"), "load1_end": g.get("load1_end"),
                  "failed_scripts": g.get("failed_scripts", []), "cap_s": g.get("cap_s"), "provisional": True},
         "gate_command": gate_cmd, "gate_record": f"{W}/gates/{k}.json"}
    if v == "KILLED":
        r["class"] = "killed"; r["should_fail"] = "n/a: the suite fails on it"
        r["fail_lines"] = {sc: g.get("fail_lines", {}).get(sc) for sc in g.get("killed_by", [])}
    elif v == "TIMEOUT":
        r["class"] = "timeout"; r["should_fail"] = "n/a: timeout"
    else:
        r["class"] = s["cls"]
    r["probe"] = {"path": f"{W}/probes/probe_{k}.py", "command": probe_cmd + " [--mutant]", "metric": s["metric"],
                  "baseline_value": b[s["metric"]], "mutant_value": m[s["metric"]], "null_metric": s["null"],
                  "null_baseline": b[s["null"]], "null_mutant": m[s["null"]],
                  "all_results_baseline": b, "all_results_mutant": m, "inputs_tried": s["inputs"], "machine": MACH}
    r["reach"] = s["reach"]
    if r["class"] in ("candidate", "equivalent-candidate"):
        r["should_fail"] = s["sf"]
    if r["class"] == "candidate":
        r.update({"title": s["title"],
          "claim": f"Mutant {k} at {site} ({s['patch']}) survives the full GATE_SCOPE=full GOLDEN_MODE=drift gate ({v}), yet the probe's {s['metric']} moves {b[s['metric']]} -> {m[s['metric']]} while its null {s['null']} stays {b[s['null']]} -> {m[s['null']]}. {s['reach']}.",
          "step": "D3.M3", "scope": "D3-s1", "class_guess": "I1", "severity_claimed": s["sev"],
          "instrumented_symbol": f"custom_components.heatpump_optimizer.sysid:SystemIdentification.{s['fn']}",
          "metric_definition": s["md"],
          "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", f"{W}/probes/probe_{k}.py"],
          "evidence_command": f"{probe_cmd}; {probe_cmd} --mutant",
          "perturbation": {"change": f"the one-line mutant at sysid.py:{s['line']} ({s['patch']}), applied in memory by the probe; full gate: {gate_cmd}",
                           "expected_direction": s["dir"], "baseline_value": b[s["metric"]], "observed_value": m[s["metric"]]},
          "null_control": {"probe_arm": s["nullarm"], "gate": f"fullgate.py null on box D3-g33 ({W}/gates/null.json)"}})
    json.dump(r, open(f"{W}/results/{k}.json", "w"), indent=1)
    print("wrote", k, v, r["class"])

if __name__ == "__main__":
    for k in sys.argv[1:]:
        main(k)
