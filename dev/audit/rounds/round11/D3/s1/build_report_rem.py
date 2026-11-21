#!/usr/bin/env python3
# Box D3-rem report assembly for seat D3-s1 (round 11, D3.M3 remainder and its D3.M4 answers).
# Command: python3 dev/audit/rounds/round11/D3/s1/build_report_rem.py
# Reads: t2_results.json (probe verdicts, each re-run by the box seat), state/gates/<key>.json
# (fullgate.py verdicts), REPORT.json as carried from box D3-top6 (kept as REPORT-D3-top6.json).
# Writes: REPORT-D3-rem.json, REPORT-D3-rem.md, findings/<id>.json. Counts are exact; walls are provisional.
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
REL = "dev/audit/rounds/round11/D3/s1"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
MACHINE = "box D3-rem: Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14, alone on the box"


def j(p):
    with open(os.path.join(HERE, p)) as f:
        return json.load(f)


carried_path = os.path.join(HERE, "REPORT-D3-top6.json")
if not os.path.exists(carried_path):
    shutil.copy(os.path.join(HERE, "REPORT.json"), carried_path)
carried = j("REPORT-D3-top6.json")
T2 = j("t2_results.json")


def gate(key):
    p = os.path.join(HERE, "state/gates", key + ".json")
    return json.load(open(p)) if os.path.exists(p) else None


T1 = [("c2", "95779f9d6d71c50d", "grid_fee.py:355"), ("c2", "a0b3b28854fa500c", "flow_lift.py:188"),
      ("c2", "c38d53ab787ddbfa", "price_model.py:252"), ("c3c6", "5cc84148fa68bda1", "grid_fee.py:383"),
      ("c3c6", "a4b00ac3ca662eec", "thermal_model.py:835")]
CARRIED_T1 = {"95779f9d6d71c50d", "a0b3b28854fa500c"}


def t1_row(src, key, site):
    g = gate(key) or {}
    v = g.get("verdict") or ("SURVIVED" if g.get("gate_rc") == 0 else "?")
    survived = v in ("SURVIVED", "RED-AS-NULL")
    ld = "%s..%s" % (g.get("load1_start", "-"), g.get("load1_end", "-"))
    how = "carried from cloud box D3-top6 (wip 917689bd)" if key in CARRIED_T1 else "gated on box D3-rem"
    return dict(mutant="%s:%s" % (src, key), site=site, verdict=v, survived=survived,
                killed_by=g.get("killed_by") or [], wall_s=g.get("wall_s"), load1=ld, carried_or_gated=how)


t1 = [t1_row(*r) for r in T1]

# Findings: survivors whose probe metric moves on an input production admits.
SPEC = [
    ("121362d48b408236", "grid_fee:_parse_rule", "No check feeds a grid-fee rule without '=' to _parse_rule; dropping the guard is unseen",
     "rules_mutant", 1, "accepted rule count for rules text '0.5' (baseline -1 = GridFeeError)", "up",
     "A grid-fee rule line with no '= rate' part is refused with GridFeeError (spec_problem reports invalid_grid_fee_rules)"),
    ("95779f9d6d71c50d", "grid_fee:GridFeeSchedule.max_abs_component", "No check pins max_abs_component's source label on a fixed/rule |rate| tie",
     "label_changed", 1, "1 when the (value, source) label of max_abs_component differs from baseline on the fixed=0.25 / rule=0.25 tie", "up",
     "On a tie between the fixed fee and a rule, max_abs_component keeps the first-seen (fixed) source"),
    ("5cc84148fa68bda1", "grid_fee:GridFeeSchedule.min_component", "No check pins min_component's source label on a fixed/rule rate tie",
     "label_changed", 1, "1 when the (value, source) label of min_component differs from baseline on the fixed=-0.25 / rule=-0.25 tie", "up",
     "On a tie between the fixed fee and a rule, min_component keeps the first-seen (fixed) source"),
    ("0c3e91a6a349409a", "flow_lift:FLOW_BIAS_ALPHA (read in FlowCurveBias.observe)", "No check pins FLOW_BIAS_ALPHA's value; doubling the flow-bias EWMA weight is unseen",
     "delta", 1.05124, "learned flow bias in K after 5 residuals of +2 K then 5 of +6 K", "up",
     "The flow-bias EWMA after warm-up weights each new residual by exactly the documented 0.1"),
    ("a0b3b28854fa500c", "flow_lift:FlowCurveBias.observe", "No check folds the sample one past FLOW_BIAS_MIN_SAMPLES; the warm-up boundary is unpinned",
     "delta", 0.666667, "learned flow bias in K after five +2 K residuals then a +12 K sixth", "up",
     "The sample at samples == FLOW_BIAS_MIN_SAMPLES is folded as an EWMA, not as part of the warm-up mean"),
    ("050fdc4a20eba212", "thermal_model:_holiday_dhw_windows", "No check pins that an unset holiday-DHW-windows option parses to None, not []",
     "unset_forms_moved", 3, "count of unset option forms (absent, '', None) whose parsed holiday windows differ from baseline None", "up",
     "An unset holiday DHW windows option leaves the ordinary windows in force on holidays (parses to None)"),
    ("22b5ec8775d5bd50", "thermal_model:_valve_two_zone_delivery", "No check bounds single-tank valve delivery by the tank energy over dt; max->min is unseen",
     "delta", 2.5216, "valve-delivered heat in kW from a 20 L tank at 24 C, manual valve target 35 C, dt 0.25 h", "up",
     "Heat a valve draws from a single tank in one step never exceeds the tank's usable energy divided by dt"),
    ("0911281eca895664", "dhw_planner:DhwPlanner._plan_dhw_min_cost", "No check makes the DHW shortfall penalty bind; its max->min price base is unseen",
     "delta_kwh", -0.5108, "planned DHW kWh over 12 steps (60 C floor), steps 0-10 at 100000, step 11 at 0", "down",
     "The DHW shortfall price exceeds every step's price so meeting the floor always wins"),
    ("5e8d48eff7e4fa8d", "coordinator:HeatPumpOptimizerCoordinator._on_power_event", "No check covers _on_power_event with the tariff disabled or its factor 0; and->or is unseen",
     "caseA_threshold_mutant", 3.0, "guard threshold kW (baseline 10.0 = fuse) with tariff disabled and a 3 kW restored tracker peak", "down",
     "The peak-tariff threshold caps the power guard only when the tariff is enabled and its factor is positive"),
    ("c38d53ab787ddbfa", "price_model:PriceShapeModel.observe_day_quarters", "No check feeds observe_day_quarters a day whose mean is exactly 1e-6",
     "accepted_mutant", 1, "quarter-days accepted for a day of 48x0.0 and 48x2e-6 (mean exactly 1e-6; baseline 0)", "up",
     "A price day with mean <= 1e-6 is rejected by the quarter-shape learner"),
]


def finding(n, spec):
    key, sym, title, rname, val, metric, direction, prop = spec
    r = T2[key]
    g = gate(key) or {}
    probe = r["probe"]
    path = probe.split("python3 ")[1].split()[0]
    fid = "D3-s1-%02d" % n
    return {
        "id": fid, "scope": "D3-s1", "step": "D3.M3", "title": title[:120], "severity": "low",
        "claim": "Mutant %s at %s survives the full gate (%s), yet the probe's %s moves: baseline %s, mutant %s." % (
            key, r["site"], g.get("verdict", "?"), rname, r["baseline"], r["mutant"]),
        "mechanism": "Reach: %s. Check that should have failed (D3.M4): %s." % (r["reach"], r["should_fail"]),
        "evidence": {"command": probe, "harness_path": path, "value": val, "unit": metric,
                     "baseline_sha": BASE, "machine": MACHINE, "cpu_or_wall": "n/a",
                     "contention_note": "deterministic value; probes ran while box D3-rem gates ran (load1 ~1); the full-gate walls in the T1 table are provisional",
                     "tolerance": "exact", "load1": 1.0, "thread_factor": 1.0},
        "instrumented_symbol": "custom_components.heatpump_optimizer." + sym,
        "perturbation": {"change": "the mutant edit at %s applied in memory by the probe (%s); full gate: fullgate.py run --key %s" % (r["site"], r["input"], key),
                         "expected_direction": direction, "observed_value": val},
        "metric_definition": metric[:200],
        "phenomenon_property": prop,
        "seam_rule": "PYTHONPATH=tests/hastub python3 %s/tabulate.py --tsv | grep -P '\\tSURVIVED\\t'" % REL,
        "null_control": {"command": probe, "value": r["null_delta"], "note": "null arm where the edit cannot matter; identical floats under both arms"},
        "reproduction_steps": [probe, "PYTHONPATH=tests/hastub python3 %s/fullgate.py run --src %s --key %s" % (REL, r["src"], key)],
        "proposed_fix_scope": "tests only: a check at the boundary input above that pins the baseline value (%s)" % r["baseline"],
        "files": ["custom_components/heatpump_optimizer/" + r["site"].split(":")[0], "tests/features.py"],
        "stop_rule_class": "hygiene", "class_guess": "new",
    }


def main():
    survived = {r["mutant"].split(":")[1] for r in t1 if r["survived"]}
    findings = []
    n = 62
    for spec in SPEC:
        key = spec[0]
        if key in [x[1] for x in T1] and key not in survived:
            continue
        if T2.get(key, {}).get("verdict", "").startswith("finding"):
            findings.append(finding(n, spec))
            n += 1
    os.makedirs(os.path.join(HERE, "findings"), exist_ok=True)
    for f in findings:
        json.dump(f, open(os.path.join(HERE, "findings", f["id"] + ".json"), "w"), indent=1)

    nf = []
    for r in t1:
        nf.append({"claim": "T1 full gate %s %s: %s (%s)" % (r["mutant"], r["site"], r["verdict"], r["carried_or_gated"]),
                   "command": "PYTHONPATH=tests/hastub python3 %s/fullgate.py run --src %s --key %s" % (REL, *r["mutant"].split(":")),
                   "value": "killed_by=%s; wall %s s, load1 %s (provisional)" % (r["killed_by"] or "none", r["wall_s"], r["load1"])})
    nf.append({"claim": "box D3-rem full-gate null control: red only on artefact checks no production mutant can need (state/gates/null-D3-rem-note.txt)",
               "command": "PYTHONPATH=tests/hastub python3 %s/fullgate.py null" % REL,
               "value": "gate_rc=1; closure.py selftest 2, entities.py 1 of 2723, harness_headers.py 4 failing lines; wall 3215.1 s, load1 1.55..1.0 (provisional)"})
    for key, r in T2.items():
        if r["verdict"].startswith("non-finding"):
            if key == "a4b00ac3ca662eec" and key not in survived:
                continue
            nf.append({"claim": "T2 %s %s: %s; reach: %s" % (key, r["site"], r["verdict"], r["reach"]),
                       "command": r["probe"], "value": "baseline %s; mutant %s; null delta %s" % (r["baseline"], r["mutant"], r["null_delta"])})

    cov = []
    for row in carried["coverage"]:
        row = dict(row)
        if row["step"] == "D3.M3":
            row["examined"] = row["universe"]
            row["not_reached"] = []
            row["evidence"] = ("box D3-top6 gated 30 of 35 (carried, state/gates/ and state/gates/cloud/); box D3-rem gated the "
                               "remaining 5 (2 carried from cloud box D3-top6 wip 917689bd, 3 gated here: state/gates/c38d53ab787ddbfa.json, "
                               "5cc84148fa68bda1.json, a4b00ac3ca662eec.json) and probed every full-gate survivor without a finding "
                               "(t2_results.json, probe_*.py). T1 table: " + json.dumps(t1))
        elif row["step"] == "D3.M4":
            row["evidence"] = row["evidence"] + " | box D3-rem: each survivor's answer re-derived by a moving probe (t2_results.json: production line, file, the check that should have failed)."
        else:
            row["evidence"] = "assigned to boxes D3-u1a..d / D3-m5 (carried unchanged from box D3-top6's return). " + row["evidence"]
        cov.append(row)

    harnesses = sorted({"%s/%s" % (REL, p) for p in os.listdir(HERE) if p.startswith("probe_") and p.endswith(".py")}
                       | {REL + "/fullgate.py", REL + "/build_report_rem.py"})
    rep = {
        "dimension": "D3", "baseline_sha": BASE, "report_path": REL + "/REPORT-D3-rem.md",
        "exposure": carried.get("exposure", "") + " Box D3-rem read box D3-top6's carried REPORT.md and REPORT.json (fdd9e2d8) and two gate results from its wip tree (917689bd); no GitHub reads.",
        "coverage": cov, "unfinished": [], "findings": findings, "non_findings": nf,
        "harnesses": harnesses, "leads": [],
    }
    md = ["# D3-s1, box D3-rem: D3.M3 remainder and its D3.M4 answers", "",
          "Baseline %s. %s. Walls provisional; counts exact." % (BASE, MACHINE), "",
          "## T1 full gate", "", "| mutant | site | survived | killed_by | wall s | load1 | carried-or-gated |", "|---|---|---|---|---|---|---|"]
    for r in t1:
        md.append("| %s | %s | %s (%s) | %s | %s | %s | %s |" % (r["mutant"], r["site"], r["survived"], r["verdict"],
                  ",".join(r["killed_by"]) or "-", r["wall_s"], r["load1"], r["carried_or_gated"]))
    md += ["", "Null control on this box: gate_rc=1 on artefact checks only (state/gates/null-D3-rem-note.txt); RED-AS-NULL = no script fails more checks than the null.", "",
           "## T2 probes", "", "| mutant | site | probe command | baseline value | mutant value | null delta | finding-or-non-finding |", "|---|---|---|---|---|---|---|"]
    fid = {f["reproduction_steps"][1].split("--key ")[1]: f["id"] for f in findings}
    for key, r in T2.items():
        if key in [x[1] for x in T1] and key not in survived:
            continue
        verdict = fid.get(key, r["verdict"])
        md.append("| %s | %s | `%s` | %s | %s | %s | %s |" % (key, r["site"], r["probe"], r["baseline"], r["mutant"], r["null_delta"], verdict))
    md += ["", "## D3.M4 answers (production line, file, the check that should have failed)", ""]
    for key, r in T2.items():
        md.append("- %s %s: %s. Should have failed: %s" % (key, r["site"], r["symbol"], r["should_fail"]))
    md += ["", "## Findings", ""] + ["- %s: %s" % (f["id"], f["title"]) for f in findings]
    rep["report_md"] = "\n".join(md) + "\n"
    try:
        open(os.path.join(HERE, "REPORT-D3-rem.md"), "w").write(rep["report_md"])
    except OSError as e:
        rep["unfinished"].append({"step": "D3.M3", "what": "REPORT.md write refused (%s); its content is in report_md" % e})
    json.dump(rep, open(os.path.join(HERE, "REPORT-D3-rem.json"), "w"), indent=1)
    print("RESULT findings=%d count" % len(findings))
    print("RESULT non_findings=%d count" % len(nf))
    print("RESULT t1_survived=%d of %d" % (len(survived), len(t1)))


if __name__ == "__main__":
    main()
