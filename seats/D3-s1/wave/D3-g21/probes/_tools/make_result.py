#!/usr/bin/env python3
"""make_result.py <key>: the box's results/<key>.json from gates/<key>.json, the probe run and classify.json."""
import json, re, shutil, sys
from pathlib import Path
key = sys.argv[1]
HOME = Path.home()
W = HOME / "audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g21"
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g21"
row = next(l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.startswith(key))
_, src, file, line, function, cluster, slc, fullnet, kind, reach, m4src = row
mut = json.loads((HOME / f"audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/state/results/{src}/{key}.json").read_text())["mutant"]
g = json.loads((W / "gates" / f"{key}.json").read_text())
cl = json.loads((HOME / "probe-src/classify.json").read_text())[key]
probe_rel = f"{REL}/probes/probe_{key}.py"
cmd = f"PYTHONPATH=tests/hastub python3 {probe_rel}"
# the probe and its executed output travel with the record
(W / "probes").mkdir(exist_ok=True)
shutil.copy(HOME / f"probe-tree/{probe_rel}", W / "probes" / f"probe_{key}.py")
out = (HOME / f"probe-src/out_{key}.txt").read_text()
(W / "probes" / f"out_{key}.txt").write_text(out)
res = dict(re.findall(r"^RESULT\s+([A-Za-z0-9_]+)=(.*)$", out, re.M))
gate = {k: g.get(k) for k in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end", "failed_scripts", "fail_lines", "more_fails_than_null", "summary", "command")}
gate["record"] = f"{REL}/gates/{key}.json"
gate["log"] = f"{REL}/gates/{key}.log"
gate["provisional"] = "wall and load are provisional (box D3-g21: nproc 4, Intel Xeon @ 2.10GHz; the judge re-takes them)"
rec = {"key": key, "site": f"{file}:{line} {kind}", "patch": f"{mut['old'].strip()} -> {mut['new'].strip()}",
       "function": function, "cluster": cluster, "slice": slc, "m4_source": m4src, "gate": gate}
v = g.get("verdict")
if v == "KILLED":
    log = (W / "gates" / f"{key}.log").read_text(errors="replace")
    lines = [ln for ln in log.splitlines() if re.search(r"FAIL|>>> FAILED", ln)][:40]
    rec.update({"class": "killed", "killed_by": g.get("killed_by"), "failing_check_lines": lines,
                "non_finding": f"the suite fails on it: KILLED by {', '.join(g.get('killed_by') or [])} (gate_rc {g.get('gate_rc')})"})
elif v == "TIMEOUT":
    rec.update({"class": "timeout", "cap_s": g.get("cap_s")})
else:
    rec["class"] = cl["class"]
    rec["probe"] = {"path": probe_rel, "command": cmd, "metric": cl["metric"],
                    "baseline_value": res.get(cl["bname"]), "mutant_value": res.get(cl["mname"]),
                    "baseline_name": cl["bname"], "mutant_name": cl["mname"],
                    "inputs_tried": cl["inputs"], "results": res, "output": f"{REL}/probes/out_{key}.txt"}
    rec["should_fail"] = cl["should_fail"]
    if cl["class"] == "equivalent-candidate":
        rec["note"] = cl["note"]
    else:
        nd = res.get("null_delta", res.get("null_delta_kw"))
        rec.update({
            "title": cl["title"], "claim": f"Mutant {key} at {file}:{line} ({mut['old'].strip()} -> {mut['new'].strip()}) is not failed by the full gate ({v}), yet the probe's {cl['metric']} moves: baseline {res.get(cl['bname'])}, mutant {res.get(cl['mname'])}.",
            "step": "D3.M3", "scope": "D3-s1", "class_guess": "new", "severity_claimed": cl["severity"],
            "stop_rule_class": "hygiene",
            "phenomenon_property": cl["property"],
            "metric_definition": cl["metric"],
            "instrumented_symbol": f"custom_components.heatpump_optimizer.optimizer:{function}",
            "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", probe_rel],
            "evidence_command": cmd,
            "perturbation": {"change": f"optimizer.py:{line} {mut['old'].strip()} -> {mut['new'].strip()}, applied in memory by the probe (method recompiled from its own source); full gate: python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src {src} --key {key}",
                             "expected_direction": cl["direction"]},
            "null_control": {"command": cmd, "value": f"null_delta={nd}", "note": "the probe's null arm, where the edit cannot matter; and the box's full-gate null control gates/null.json"},
            "files": cl["files"],
            "proposed_fix_scope": "tests only: a check at the probe's distinguishing input that pins the baseline value",
        })
(W / "results" / f"{key}.json").write_text(json.dumps(rec, indent=1) + "\n")
print(f"results/{key}.json class={rec['class']} verdict={v}")
