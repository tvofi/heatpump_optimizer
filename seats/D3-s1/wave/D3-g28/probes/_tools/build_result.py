"""results/<key>.json for one gated key of box D3-g28: gate record + probe output + classification."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from headers import H, F
from meta import M, EQ

W = Path.home() / "audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g28"
PROBES = "dev/audit/rounds/round11/D3/s1/wave/D3-g28/probes"
key = sys.argv[1]
g = json.loads((W / "gates" / f"{key}.json").read_text())
keys = {l.split("\t")[0]: l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()}
row = keys[key]
h, m = H[key], M[key]
out = (W / "probes" / f"out_{key}.txt").read_text()
res = dict(re.findall(r"^RESULT (\S+?)=(.*)$", out, re.M))
cmd = f"PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 {PROBES}/probe_{key}.py"
gate = {k: g.get(k) for k in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end", "failed_scripts", "fail_lines")}
gate["record"] = f"dev/audit/rounds/round11/D3/s1/wave/D3-g28/gates/{key}.json"
gate["command"] = f"python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src {row[1]} --key {key}"
gate["provisional"] = "wall and load1 provisional (box D3-g28, nproc 4, Intel Xeon @ 2.10GHz)"
verdict = g.get("verdict")
r = {"key": key, "site": f"{F}:{h['line']} {row[8]}", "patch": f"{h['old']} -> {h['new']}", "function": row[4],
     "cluster": row[5], "slice": row[6], "m4_source": row[10].strip(), "gate": gate}
if verdict == "KILLED":
    r["class"] = "killed"
    r["killed"] = {"killed_by": g.get("killed_by"), "fail_lines": g.get("fail_lines"),
                   "note": "non-finding: the full gate fails on the mutant beyond this box's null"}
elif verdict == "TIMEOUT":
    r["class"] = "timeout"
    r["timeout"] = {"cap_s": g.get("cap_s", 14400), "last_script": sys.argv[2] if len(sys.argv) > 2 else None}
else:
    r["class"] = m["cls"]
    r["probe"] = {"path": f"{PROBES}/probe_{key}.py", "command": cmd, "results": res, "inputs_tried": h["inputs"],
                  "direction": h["direction"], "metric": h["metric"]}
    if m["cls"] == "candidate":
        script, assertion = m["should"]
        r["should_fail"] = {"script": script, "assertion": assertion,
                            "why": "the slice's step-4 answer (m4_source) lists it among the closure scripts whose traced baseline executes the line"}
        r["finding"] = {"title": m["title"], "claim": m["claim"], "step": "D3.M3", "scope": "D3-s1", "class_guess": "I1",
                        "severity_claimed": m["sev"], "stop_rule_class": m["stop"],
                        "metric_definition": h["metric"][:200],
                        "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", f"{PROBES}/probe_{key}.py"],
                        "evidence_command": cmd,
                        "instrumented_symbol": f"heatpump_optimizer.optimizer:{h['sym']}",
                        "perturbation": {"change": f"{F}:{h['line']} `{h['old']}` -> `{h['new']}`",
                                         "expected_direction": m["dirn"], "observed_value": m["obs"]},
                        "null_control": {"command": cmd, "value": "; ".join(f"{k}={v}" for k, v in res.items() if k.startswith("null")),
                                         "note": "the null_* inputs, where the mutated line cannot matter, do not move; the gate's null is gates/null.json"},
                        "files": [F]}
    else:
        r["should_fail"] = None
        r["equivalence"] = EQ[key]
(W / "results" / f"{key}.json").write_text(json.dumps(r, indent=1) + "\n")
print(key, verdict, r["class"])
