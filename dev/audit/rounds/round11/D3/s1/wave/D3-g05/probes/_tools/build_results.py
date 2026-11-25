#!/usr/bin/env python3
"""Write results/<key>.json for every gated key of box D3-g05 that has none yet. Prints WROTE <key> <class>."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from spec import SPEC, P, FG
W = Path.home() / "audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g05"
S1 = W.parent.parent
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
rows = [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
hdr = (W / "keys.tsv").read_text().splitlines()[0].split("\t")
force = "--force" in sys.argv


def log_sections(text):
    out, cur = {}, None
    for ln in text.splitlines():
        m = re.match(r"^#{10} (.+?) #{10}$", ln)
        if m:
            cur = m.group(1); out.setdefault(cur, []); continue
        if cur:
            out[cur].append(ln)
    return out


for r in rows:
    row = dict(zip(hdr, r)); key = row["key"]
    g = W / "gates" / f"{key}.json"
    res = W / "results" / f"{key}.json"
    if not g.exists() or (res.exists() and not force):
        continue
    gate = json.loads(g.read_text())
    mut = json.loads((S1 / "state/results/complete" / f"{key}.json").read_text())["mutant"]
    sp = SPEC[key]
    v = gate.get("verdict")
    rec = {"key": key, "site": f"{row['file'].split('/')[-1]}:{row['line']} {row['kind']}",
           "patch": f"{mut['old'].strip()} -> {mut['new'].strip()}", "function": row["function"], "cluster": row["cluster"],
           "slice": row["slice"], "fullnet": row["fullnet"], "reach": row["reach"],
           "gate": {k: gate.get(k) for k in ("verdict", "killed_by", "gate_rc", "failed_scripts", "more_fails_than_null",
                                              "fail_lines", "wall_s", "child_cpu_s", "load1_start", "load1_end", "cap_s", "note")},
           "gate_record": f"dev/audit/rounds/round11/D3/s1/wave/D3-g05/gates/{key}.json",
           "gate_command": f"PYTHONPATH=tests/hastub python3 {FG} run --src {row['src']} --key {key}",
           "provisional": {"wall_and_load": True, "nproc": 4, "cpu": "Intel(R) Xeon(R) Processor @ 2.10GHz"}}
    probe = {"path": f"{P}/probe_{key}.py", "command": f"PYTHONPATH=tests/hastub python3 {P}/probe_{key}.py",
             "output": f"{P}/probe_{key}.out", "baseline_value": sp["baseline"], "mutant_value": sp["mutant"],
             "inputs_tried": sp["inputs"]}
    if v == "KILLED":
        logt = (W / "gates" / f"{key}.log").read_text(errors="replace") if (W / "gates" / f"{key}.log").exists() else ""
        secs = log_sections(logt)
        lines = []
        for script in gate.get("killed_by", []):
            for name, body in secs.items():
                if name.endswith(script) or script in name:
                    lines += [f"{name}: {ln.strip()}" for ln in body if re.match(r"^\s*FAIL\b", ln) or re.search(r"\d+ of \d+ .*FAILED", ln)][:12]
        rec.update({"class": "killed", "killed_by": gate.get("killed_by"), "failing_check_lines": lines,
                    "non_finding": f"the full gate fails on it: killed by {', '.join(gate.get('killed_by') or [])}",
                    "probe": probe, "probe_note": "probe written before the verdict (step-4 answer carried); the gate decides: a non-finding",
                    "m4_answer": sp["answer"], "should_fail": sp["should_fail"]})
    elif v == "TIMEOUT":
        logt = (W / "gates" / f"{key}.log").read_text(errors="replace") if (W / "gates" / f"{key}.log").exists() else ""
        heads = re.findall(r"^#{10} (.+?) #{10}$", logt, re.M)
        rec.update({"class": "timeout", "cap_s": gate.get("cap_s", 14400), "last_script": heads[-1] if heads else None,
                    "probe": probe, "m4_answer": sp["answer"]})
    else:
        rec.update({"class": sp["cls"], "probe": probe, "m4_answer": sp["answer"], "should_fail": sp["should_fail"],
                    "verdict_read": "RED-AS-NULL read as survived" if v == "RED-AS-NULL" else "SURVIVED"})
        if sp["cls"] == "candidate":
            f = sp["finding"]
            rec["finding"] = {
                "scope": "D3-s1", "step": "D3.M3", "title": f["title"], "severity_claimed": f["severity"], "severity": f["severity"],
                "claim": f["claim"], "mechanism": f"Full gate {v} (gate_rc {gate.get('gate_rc')}). D3.M4: {sp['should_fail']}.",
                "class_guess": "I1", "stop_rule_class": "hygiene",
                "instrumented_symbol": f["symbol"], "metric_definition": f["metric"],
                "perturbation": {"change": f"the mutant edit {mut['old'].strip()!r} -> {mut['new'].strip()!r} at {row['file']}:{row['line']}, in memory by the probe; full gate: {rec['gate_command']}",
                                 "expected_direction": f["direction"], "observed_value": f["observed"]},
                "null_control": {"command": probe["command"], "value": "unchanged", "note": f["null"]},
                "harness_paths": [FG, probe["path"]], "evidence_command": probe["command"],
                "phenomenon_property": f["prop"],
                "seam_rule": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
                "files": [row["file"], "tests/features.py"], "proposed_fix_scope": f["fix"],
                "evidence": {"command": probe["command"], "harness_path": probe["path"], "value": f["observed"],
                             "unit": f["metric"], "baseline_sha": BASE,
                             "machine": "box D3-g05: Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14, alone on the box",
                             "cpu_or_wall": "n/a", "tolerance": "exact", "thread_factor": 1.0,
                             "contention_note": "deterministic value; run in a separate baseline worktree while this box's gates ran"},
                "reproduction_steps": [probe["command"], rec["gate_command"]]}
        else:
            rec["non_finding"] = f"equivalent-candidate: {sp['answer']}"
    res.write_text(json.dumps(rec, indent=1) + "\n")
    print("WROTE", key, rec["class"], v)
