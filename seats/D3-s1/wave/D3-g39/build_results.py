#!/usr/bin/env python3
# Box D3-g39: writes results/<key>.json for every gated key not yet recorded, from
# gates/<key>.json (fullgate.py's record), classify.json (this seat's step-4 reading),
# probes/out/probe_<key>.out (the executed probe numbers) and reach.json (closure scripts
# whose traced fast-net baseline, state/baselines.json, executes the line).
# Command: python3 dev/audit/rounds/round11/D3/s1/wave/D3-g39/build_results.py  (prints one line per record written)
import json, re, sys
from pathlib import Path
W = Path(__file__).resolve().parent
R = "dev/audit/rounds/round11/D3/s1/wave/D3-g39"
S1 = W.parents[1]
keys = [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
cls = json.loads((W / "classify.json").read_text())
reach = json.loads((W / "reach.json").read_text())
null = json.loads((W / "gates" / "null.json").read_text())
for row in keys:
    key, src, file, line, func, cluster = row[:6]
    kind = row[8]
    g = W / "gates" / f"{key}.json"
    out = W / "results" / f"{key}.json"
    if not g.exists() or out.exists():
        continue
    gate = json.loads(g.read_text())
    mut = json.loads((S1 / "state" / "results" / "complete" / f"{key}.json").read_text())["mutant"]
    v = gate.get("verdict")
    site = f"{Path(file).name}:{line} {kind}"
    rec = {"key": key, "site": site, "file": file, "line": int(line),
           "patch": f"{mut['old'].strip()} -> {mut['new'].strip()}", "function": func, "cluster": cluster,
           "gate": {k: gate.get(k) for k in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end",
                                            "failed_scripts", "fail_lines", "more_fails_than_null", "summary", "command", "cap_s")},
           "gate_record": f"{R}/gates/{key}.json", "provisional": True,
           "machine": "box D3-g39: 4 vCPU Intel Xeon @ 2.30GHz, 16 GB (MACHINE.txt)"}
    rec["gate"]["null_failed_scripts"] = null.get("failed_scripts")
    if v == "KILLED":
        rec["class"] = "killed"
        rec["non_finding"] = {"claim": f"{site} mutant {key} is KILLED by the full gate",
                              "command": f"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src {src} --key {key}",
                              "value": f"killed_by={gate.get('killed_by')}; fail_lines={gate.get('fail_lines')}; gate_rc={gate.get('gate_rc')}; wall {gate.get('wall_s')} s (provisional)"}
    elif v == "TIMEOUT":
        rec["class"] = "timeout"
        log = W / "gates" / f"{key}.log"
        last = ""
        if log.exists():
            m = re.findall(r"(tests/[\w./-]+\.(?:py|mjs|sh))", log.read_text(errors="replace"))
            last = m[-1] if m else ""
        rec["timeout"] = {"cap_s": gate.get("cap_s"), "last_script_in_log": last or "no log"}
    else:
        c = cls[key]
        pout = (W / "probes" / "out" / f"probe_{key}.out").read_text()
        res = dict(re.findall(r"^RESULT (\S+?)=(.*)$", pout, re.M))
        cases = sorted({k.rsplit("_", 1)[0] for k in res if k.endswith(("_baseline", "_mutant"))})
        cmd = f"PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 {R}/probes/probe_{key}.py"
        prim = c["primary"]
        probe = {"path": f"{R}/probes/probe_{key}.py", "helper": f"{R}/probes/_mutload.py", "command": cmd,
                 "output": f"{R}/probes/out/probe_{key}.out",
                 "cases_moved": int(res.get("cases_moved", -1)), "null_cases_moved": int(res.get("null_cases_moved", -1)),
                 "inputs_tried": {k: {"baseline": res.get(k + "_baseline"), "mutant": res.get(k + "_mutant")} for k in cases}}
        if prim:
            probe["metric_case"] = prim
            probe["baseline_value"], probe["mutant_value"] = res[prim + "_baseline"], res[prim + "_mutant"]
        else:
            probe["baseline_value"] = probe["mutant_value"] = "equal on every input tried"
        rec["class"] = c["class"]
        rec["probe"] = probe
        rec["should_fail"] = {"scripts": reach.get(f"{Path(file).name}:{line}", []),
                              "trace_source": "dev/audit/rounds/round11/D3/s1/state/baselines.json (fast-net traced baseline hits)",
                              "assertion": c["assertion"]}
        if c["class"] == "candidate":
            hdr = (W / "probes" / f"probe_{key}.py").read_text()
            metric = re.search(r"^# Metric: (.*)$", hdr, re.M).group(1)
            direction = re.search(r"Direction: (.*)$", hdr, re.M).group(1)
            nullc = re.search(r"^# Null control: (.*)$", hdr, re.M).group(1)
            rec["finding"] = {
                "title": c["title"], "step": "D3.M3", "scope": "D3-s1", "class_guess": "I1",
                "severity_claimed": c["severity"],
                "claim": f"Mutant {key} ({site}: {rec['patch']}) survives the GATE_SCOPE=full GOLDEN_MODE=drift gate "
                         f"(verdict {v}, gate_rc {gate.get('gate_rc')}) yet changes behaviour: on input '{prim}' "
                         f"the probe reads {probe['baseline_value']} on the baseline and {probe['mutant_value']} under the mutant. "
                         f"{c['consequence']}. Should have failed: {', '.join(rec['should_fail']['scripts'])} execute the line "
                         f"on the traced baseline; {c['assertion']}.",
                "instrumented_symbol": f"custom_components.heatpump_optimizer.{Path(file).stem}:{func} (line {line})",
                "metric_definition": metric,
                "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", probe["path"], probe["helper"]],
                "evidence_command": f"{cmd}; PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src {src} --key {key}",
                "perturbation": f"{rec['patch']} (the one-line mutant). Direction: {direction}",
                "null_control": f"{nullc} Gate null: fullgate.py null on this box ({R}/gates/null.json, failed_scripts {null.get('failed_scripts')}).",
                "value": f"{prim}: baseline {probe['baseline_value']}, mutant {probe['mutant_value']}; null cases moved {probe['null_cases_moved']}"}
        else:
            rec["non_finding"] = {"claim": f"{site} mutant {key} survives the full gate but is equivalent on every input tried",
                                  "command": cmd,
                                  "value": f"cases_moved=0 over {len(cases)} inputs ({', '.join(cases)}); {c['assertion']}"}
    out.write_text(json.dumps(rec, indent=1) + "\n")
    print("wrote", key, v, rec["class"])
