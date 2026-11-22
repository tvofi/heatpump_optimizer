#!/usr/bin/env python3
"""Write results/<key>.json for one gated key of box D3-g25 (step 3 of the box brief)."""
import json, os, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from spec import S
from sf import SF
key = sys.argv[1]
TR = Path.home() / "audit-r11-D3-s1"
PB = Path.home() / "probe-base"  # a clean baseline worktree: the gate tree carries a mutant while a gate runs
W = TR / "dev/audit/rounds/round11/D3/s1/wave/D3-g25"
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g25"
keys = {l.split("\t")[0]: l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()}
row = keys[key]
src, file, line, func, cluster, slice_, fullnet, kind = row[1:9]
g = json.loads((W / "gates" / f"{key}.json").read_text())
line_no, old, new, metric, _k, inputs, direction, _ = S[key]
assert int(line) == line_no
title, should_fail, sev, prop = SF[key]
probe_rel = f"{REL}/probes/probe_{key}.py"
cmd = f"PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 {probe_rel}"
gate_cmd = f"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src {src} --key {key}"
rec = {"key": key, "site": f"{file}:{line} {kind}", "patch": f"{old} -> {new}", "function": func, "cluster": cluster,
       "slice": slice_, "fullnet": fullnet,
       "gate": {k: g.get(k) for k in ("verdict", "killed_by", "gate_rc", "wall_s", "child_cpu_s", "load1_start", "load1_end", "failed_scripts", "fail_lines")},
       "gate_path": f"{REL}/gates/{key}.json", "gate_command": gate_cmd}
rec["gate"]["provisional_note"] = "wall/CPU/load provisional: nproc 4, Intel Xeon @ 2.30GHz, one gate at a time (judge re-takes)"
v = g.get("verdict")
if v == "TIMEOUT":
    log = W / "gates" / f"{key}.log"
    last = ""
    if log.exists():
        runs = re.findall(r"^(?:==+|--+|\[\w+\])?\s*(python3 tests/\S+|node tests/\S+)", log.read_text(errors="replace"), re.M)
        last = runs[-1] if runs else ""
    rec.update({"class": "timeout", "cap_s": g.get("cap_s", 14400), "last_script": last or "unknown (no log)"})
elif v == "KILLED":
    rec.update({"class": "killed", "killed_by": g.get("killed_by"),
                "non_finding": f"the suite fails on mutant {key}: killed_by {g.get('killed_by')}"})
else:
    out = subprocess.run(["nice", "-n", "19", sys.executable, probe_rel], cwd=PB, env={**os.environ, "PYTHONPATH": "tests/hastub"},
                         capture_output=True, text=True, timeout=600)
    res = dict(re.findall(r"^RESULT (\w+)=(.*)$", out.stdout, re.M))
    tried = re.findall(r"^INPUT \d+: (.*)$", out.stdout, re.M)
    if out.returncode or "moved" not in res:
        sys.exit(f"probe failed rc={out.returncode}\n{out.stdout}\n{out.stderr[-2000:]}")
    moved = res["moved"].split()[0] == "1"
    rec["probe"] = {"path": probe_rel, "command": cmd, "metric": f"{metric} of the action get_current_action returns ('raised:<exc>' when it raises)",
                    "baseline_value": res["baseline_value"], "mutant_value": res["mutant_value"], "moved": int(moved),
                    "null_moved": int(res.get("null_moved", "0").split()[0]), "inputs_tried": tried,
                    "load1": float(res["load1"]), "thread_factor": float(res["thread_factor"]),
                    "carried_m4": "from " + row[10]}
    rec["should_fail"] = should_fail
    if moved:
        rec["class"] = "candidate"
        rec["finding"] = {
            "title": title,
            "claim": f"Mutant {key} at optimizer.py:{line} (`{old.strip()}` -> `{new.strip()}`) survives the full gate ({v}, gate_rc {g.get('gate_rc')}), yet the probe's {metric} moves: baseline {res['baseline_value']}, mutant {res['mutant_value']}.",
            "step": "D3.M3", "scope": "D3-s1", "class_guess": "new", "severity_claimed": sev, "stop_rule_class": "hygiene",
            "instrumented_symbol": "custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer.get_current_action",
            "metric_definition": f"{metric} of get_current_action's action on the probe's first input, baseline arm vs the in-memory mutant arm"[:200],
            "phenomenon_property": prop,
            "seam_rule": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
            "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", probe_rel],
            "evidence_command": cmd,
            "perturbation": {"change": f"optimizer.py:{line} `{old.strip()}` -> `{new.strip()}`, applied in memory by the probe; full gate: {gate_cmd}",
                             "direction": direction, "expected_direction": "up", "observed_value": res["mutant_value"]},
            "null_control": {"command": cmd, "value": f"null_moved={res.get('null_moved')}",
                             "note": "the probe's [null] input, where the mutated comparison evaluates alike in both arms; the box's gate null is gates/null.json"},
            "files": [file, "tests/features.py"],
            "proposed_fix_scope": "tests only: a check at the probe's first input pinning the baseline value " + res["baseline_value"],
        }
    else:
        rec["class"] = "equivalent-candidate"
(W / "results" / f"{key}.json").write_text(json.dumps(rec, indent=1) + "\n")
print(key, v, rec["class"])
