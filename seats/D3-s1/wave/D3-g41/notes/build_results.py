#!/usr/bin/env python3
"""Join gates/<key>.json with notes/analysis.py into results/<key>.json (box D3-g41). Idempotent; skips written records."""
import json, re, sys
from pathlib import Path
W = Path(__file__).resolve().parents[1]
ns = {}; exec((W / "notes" / "analysis.py").read_text(), ns); A = ns["A"]
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g41"
PY = "PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3"
null = json.loads((W / "gates" / "null.json").read_text())
null_log = (W / "gates" / "null.log").read_text(errors="replace") if (W / "gates" / "null.log").exists() else ""
null_fail = {l.strip() for l in null_log.splitlines() if re.search(r"\bFAIL\b", l)}
force = "--force" in sys.argv
for key in [l.split("\t")[0] for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]:
    g = W / "gates" / f"{key}.json"
    out = W / "results" / f"{key}.json"
    if not g.exists() or (out.exists() and not force):
        continue
    gate = json.loads(g.read_text()); a = A[key]
    rec = {"key": key, "site": f"{a['file']}:{a['line']} {a['kind']}", "patch": f"{a['old'].strip()} -> {a['new'].strip()}",
           "function": a["function"], "cluster": next(l.split("\t")[5] for l in (W / "keys.tsv").read_text().splitlines() if l.startswith(key)),
           "gate": {k: gate.get(k) for k in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end", "failed_scripts", "cap_s")},
           "gate_record": f"{REL}/gates/{key}.json", "gate_command": "python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key " + key,
           "provisional": True, "machine": "box D3-g41, nproc 4, Intel Xeon @ 2.30GHz"}
    v = gate.get("verdict")
    if v == "KILLED":
        log = (W / "gates" / f"{key}.log").read_text(errors="replace") if (W / "gates" / f"{key}.log").exists() else ""
        rec["class"] = "killed"
        rec["failing_check_lines"] = [l.strip()[:300] for l in log.splitlines() if re.search(r"\bFAIL\b", l) and l.strip() not in null_fail][:20]
    elif v == "TIMEOUT":
        log = (W / "gates" / f"{key}.log").read_text(errors="replace") if (W / "gates" / f"{key}.log").exists() else ""
        runs = re.findall(r"(tests/[\w_]+\.(?:py|mjs|sh))", log)
        rec["class"] = "timeout"; rec["last_script"] = runs[-1] if runs else None
    else:
        rec["class"] = a["cls"]
        probe = f"{REL}/probes/probe_{key}.py"
        rec["probe"] = {"path": probe, "command": f"{PY} {probe}", "output": f"{REL}/probes/out/probe_{key}.txt",
                        "metric": a["metric"], "baseline_value": a["base"], "mutant_value": a["mutv"], "inputs_tried": a["inputs"]}
        rec["should_fail"] = a["should"]
        if a["cls"] == "candidate":
            rec.update(title=a["title"], claim=a["claim"], step="D3.M3", scope="D3-s1", class_guess=a["class_guess"],
                       severity_claimed=a["severity"], metric_definition=a["metric_definition"],
                       harness_paths=["dev/audit/rounds/round11/D3/s1/fullgate.py", probe], evidence_command=f"{PY} {probe}",
                       perturbation={"change": a["change"], "expected_direction": a["direction"], "observed_value": a["mutv"]},
                       instrumented_symbol=f"custom_components.heatpump_optimizer.{Path(a['file']).stem}:{a['function']}",
                       files=[a["file"]],
                       null_control=f"probe null rows (see {REL}/probes/out/probe_{key}.txt) and the box null gate {REL}/gates/null.json (gate_rc {null.get('gate_rc')}, failed {null.get('failed_scripts')})")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(rec, indent=1) + "\n")
    print("wrote", out.name, rec["class"])
