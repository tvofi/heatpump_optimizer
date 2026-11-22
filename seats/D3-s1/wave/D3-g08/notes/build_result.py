#!/usr/bin/env python3
"""Box D3-g08: write wave/D3-g08/results/<key>.json from the gate record, the probe run and the analysis.

usage: build_result.py <key>   (runs the probe from the clean baseline checkout $REPO, never the gate tree)
"""
import json, os, re, subprocess, sys
from pathlib import Path

KEY = sys.argv[1]
HOME = Path.home()
REPO = Path("/home/user/heatpump_optimizer")
TR = HOME / "audit-r11-D3-s1"
S1 = TR / "dev/audit/rounds/round11/D3/s1"
W = S1 / "wave/D3-g08"
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g08"
SCR = Path(__file__).resolve().parent
A = json.loads((SCR / "analysis.json").read_text())[KEY]
lines = (W / "keys.tsv").read_text().splitlines()
hdr = lines[0].split("\t")
row = next(dict(zip(hdr, l.split("\t"))) for l in lines[1:] if l.startswith(KEY + "\t"))
mut = json.loads((S1 / "state/results/complete" / f"{KEY}.json").read_text())["mutant"]
gate = json.loads((W / "gates" / f"{KEY}.json").read_text())
verdict = gate.get("verdict")

def fail_lines(log, script):
    if not log.exists():
        return []
    out, cur = [], None
    for ln in log.read_text(errors="replace").splitlines():
        m = re.match(r"^#{5,} (.+?) #{5,}$", ln.strip())
        if m:
            cur = m.group(1).strip()
            continue
        if cur == script and re.match(r"^\s*FAIL\b", ln):
            out.append(ln.strip()[:300])
    return out

rec = {
    "key": KEY, "site": f"{row['file']}:{row['line']} {row['kind']}",
    "patch": f"{mut['old'].strip()} -> {mut['new'].strip()}",
    "function": row["function"], "cluster": row["cluster"], "slice": row["slice"],
    "m4_source": row["m4_source"],
    "gate": {k: gate.get(k) for k in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end",
                                       "failed_scripts", "fail_lines", "command", "provisional", "cap_s", "note")
             if k in gate},
    "gate_record": f"{REL}/gates/{KEY}.json",
}
rec["gate"]["machine"] = "box D3-g08: nproc 4, Intel Xeon @ 2.10GHz, 16 GB (MACHINE.txt); walls and load1 provisional"

if verdict == "KILLED":
    rec["class"] = "killed"
    null_log = W / "gates" / "null.log"
    kl = {}
    for s in gate.get("killed_by") or []:
        mine, base = fail_lines(W / "gates" / f"{KEY}.log", s), fail_lines(null_log, s)
        kl[s] = [x for x in mine if x not in base] or mine
    rec["killed_by"] = gate.get("killed_by")
    rec["failing_checks"] = kl
    rec["non_finding"] = {"claim": f"mutant {KEY} at {rec['site']} is killed by the full gate ({', '.join(gate.get('killed_by') or [])})",
                          "command": f"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src {row['src']} --key {KEY}",
                          "value": f"gate_rc={gate.get('gate_rc')}; failing checks beyond the box null: " +
                                   "; ".join(f"{s}: {len(v)}" for s, v in kl.items())}
elif verdict == "TIMEOUT":
    rec["class"] = "timeout"
    log = W / "gates" / f"{KEY}.log"
    last = None
    if log.exists():
        for ln in log.read_text(errors="replace").splitlines():
            m = re.match(r"^#{5,} (.+?) #{5,}$", ln.strip())
            if m:
                last = m.group(1).strip()
    rec["timeout"] = {"cap_s": gate.get("cap_s", 14400), "last_script_running": last}
else:
    probe = f"{REL}/probes/probe_{KEY}.py"
    cmd = f"PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 {probe}"
    env = dict(os.environ, PYTHONPATH="tests/hastub")
    p = subprocess.run(["/opt/hpo/venv-ci/bin/python3", str(TR / probe)], cwd=REPO, env=env,
                       capture_output=True, text=True, timeout=600)
    out = p.stdout + (("\n" + p.stderr) if p.returncode else "")
    (W / "probes" / f"probe_{KEY}.out").write_text(out)
    assert p.returncode == 0, out[-2000:]
    rec["class"] = A["probe_class"]
    rec["probe"] = {"path": probe, "command": cmd, "output": f"{REL}/probes/probe_{KEY}.out",
                    "result_lines": [l for l in out.splitlines() if l.startswith("RESULT")][-40:],
                    "baseline_value": A["baseline_value"], "mutant_value": A["mutant_value"],
                    "inputs_tried": A["inputs_tried"], "run_from": "a clean checkout of the baseline (the gate tree carries mutants while gates run)"}
    rec["reach"] = A["reach"]
    if "equivalence" in A:
        rec["equivalence"] = A["equivalence"]
    if "related" in A:
        rec["related"] = A["related"]
    rec["should_fail"] = A["should_fail"]
    if rec["class"] == "candidate":
        sym = f"custom_components.heatpump_optimizer.coordinator:{row['function']}"
        rec["finding"] = {
            "title": A["title"], "claim": A["claim"] + f" Full gate verdict {verdict}.",
            "step": "D3.M3", "scope": "D3-s1", "class_guess": "new", "severity_claimed": A["severity"],
            "stop_rule_class": "hygiene",
            "mechanism": f"Reach: {A['reach']}. Check that should have failed (D3.M4): {A['should_fail']['script']}: {A['should_fail']['assertion']}.",
            "metric_definition": A["metric_definition"],
            "phenomenon_property": A["phenomenon_property"],
            "seam_rule": "awk -F'\\t' 'NR>1' dev/audit/rounds/round11/D3/s1/wave/D3-g08/keys.tsv (this box's full-gate survivors; the wave list: awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv)",
            "instrumented_symbol": sym,
            "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", probe],
            "evidence_command": cmd,
            "evidence": {"command": cmd, "harness_path": probe, "value": A["evidence_value"], "unit": A["evidence_unit"],
                         "baseline_sha": "92d38ecb640bd462f2e19c0814d0f0b7df1ee692",
                         "machine": "box D3-g08: Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython",
                         "cpu_or_wall": "n/a", "tolerance": "exact",
                         "contention_note": "deterministic value; the full-gate wall and load1 are provisional"},
            "perturbation": {"change": f"mutant {KEY} at {row['file']}:{row['line']} ({mut['old'].strip()} -> {mut['new'].strip()}), applied in memory by the probe; full gate: fullgate.py run --src {row['src']} --key {KEY}",
                             "expected_direction": A["direction"]},
            "null_control": {"command": cmd, "value": "0 count", "note": A["null_note"] +
                             "; full-gate null: this box's fullgate.py null (gates/null.json)"},
            "reproduction_steps": [cmd, f"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src {row['src']} --key {KEY}"],
            "proposed_fix_scope": "tests only: a check at the probe's moving input pinning the baseline value",
            "files": [row["file"], "tests/features.py"],
        }
(W / "results").mkdir(exist_ok=True)
(W / "results" / f"{KEY}.json").write_text(json.dumps(rec, indent=1) + "\n")
print(f"wrote results/{KEY}.json class={rec['class']} verdict={verdict}")
