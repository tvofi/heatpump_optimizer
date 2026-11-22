#!/usr/bin/env python3
"""Write results/<key>.json for box D3-g10 from keys.tsv, the gate record and the probe output."""
import json, re, sys, os
sys.path.insert(0, os.path.expanduser("~/pgen"))
exec(open(os.path.expanduser("~/pgen/meta.py")).read())
TR = os.path.expanduser("~/audit-r11-D3-s1")
S1 = f"{TR}/dev/audit/rounds/round11/D3/s1"
W = f"{S1}/wave/D3-g10"
PT = os.path.expanduser("~/probe-tree/dev/audit/rounds/round11/D3/s1/wave/D3-g10/probes")
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g10"
rows = {l.split("\t")[0]: dict(zip(open(f"{W}/keys.tsv").readline().rstrip("\n").split("\t"), l.rstrip("\n").split("\t")))
        for l in open(f"{W}/keys.tsv").read().splitlines()[1:]}
null = json.load(open(f"{W}/gates/null.json"))


def failing_lines(key, scripts):
    p = f"{W}/gates/{key}.log"
    if not os.path.exists(p):
        return []
    out = [ln.rstrip() for ln in open(p, errors="replace") if re.search(r"\bFAIL\b|FAILED", ln)]
    return out[:40]


def build(key):
    r = rows[key]
    mut = json.load(open(f"{S1}/state/results/{r['src']}/{key}.json"))["mutant"]
    g = json.load(open(f"{W}/gates/{key}.json"))
    v = g["verdict"]
    gate = {k: g.get(k) for k in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end",
                                  "failed_scripts", "more_fails_than_null", "child_cpu_s", "command", "cap_s", "note")}
    gate["record"] = f"{REL}/gates/{key}.json"
    gate["null_failed_scripts"] = null.get("failed_scripts")
    rec = {"key": key, "site": f"{r['file']}:{r['line']} {r['kind']}",
           "patch": f"{mut['old'].strip()} -> {mut['new'].strip()}", "function": r["function"], "cluster": r["cluster"],
           "slice": r["slice"], "fullnet": r["fullnet"], "m4_source": r["m4_source"], "gate": gate,
           "gate_command": f"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src {r['src']} --key {key}"}
    if v == "KILLED":
        rec["class"] = "killed"
        rec["killed_by"] = g.get("killed_by")
        rec["failing_check_lines"] = failing_lines(key, g.get("killed_by"))
        rec["note"] = f"non-finding: the full gate fails on this mutant ({', '.join(g.get('killed_by') or [])})"
        return rec
    if v == "TIMEOUT":
        rec["class"] = "timeout"
        log = f"{W}/gates/{key}.log"
        last = None
        if os.path.exists(log):
            for ln in open(log, errors="replace"):
                m = re.search(r"(tests/[\w./-]+\.(?:py|mjs|sh))", ln)
                if m:
                    last = m.group(1)
        rec["timeout"] = {"cap_s": g.get("cap_s", 14400), "last_script_seen": last}
        return rec
    m = M[key]
    probe = f"{REL}/probes/probe_{key}.py"
    out = open(f"{PT}/probe_{key}.out").read()
    res = [l for l in out.splitlines() if l.startswith("RESULT")]
    nm = [l for l in res if "null_moved=" in l]
    rec["class"] = "candidate"
    rec["probe"] = {"path": probe, "command": f"PYTHONPATH=tests/hastub python3 {probe}", "baseline": m["base"], "mutant": m["mut"],
                    "inputs_tried": m["inputs"], "result_lines": res}
    rec["should_fail"] = {"scripts_executing_line": m["scripts"],
                          "source": "dev/audit/rounds/round11/D3/s1/state/reach.tsv (traced baseline, exec= column)",
                          "assertion_lacking": m["assertion"]}
    rec["carried_m4"] = "see m4_source; re-answered here with the executed probe"
    rec["finding"] = {
        "title": m["title"], "scope": "D3-s1", "step": "D3.M3",
        "claim": f"Mutant {key} at {r['file'].split('/')[-1]}:{r['line']} ({mut['old'].strip()} -> {mut['new'].strip()}) "
                 f"{'survives' if v == 'SURVIVED' else 'is red only as the null is (RED-AS-NULL)'} the full GATE_SCOPE=full GOLDEN_MODE=drift gate, "
                 f"yet the probe's number moves: baseline {m['base']}, mutant {m['mut']}.",
        "mechanism": f"Check that should have failed (D3.M4): {m['assertion']}. Executing scripts (traced baseline): {', '.join(m['scripts'])}.",
        "class_guess": m["cls"], "severity_claimed": m["sev"], "stop_rule_class": "hygiene",
        "metric_definition": m["metric"],
        "phenomenon_property": m["prop"],
        "seam_rule": "for f in dev/audit/rounds/round11/D3/s1/wave/*/results/*.json; do python3 -c \"import json,sys;d=json.load(open(sys.argv[1]));print(d['key'],d['site']) if d['class']=='candidate' else None\" $f; done",
        "instrumented_symbol": f"custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.{m['sym']}",
        "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", probe],
        "evidence_command": f"PYTHONPATH=tests/hastub python3 {probe}",
        "evidence": {"command": f"PYTHONPATH=tests/hastub python3 {probe}", "harness_path": probe, "value": m["val"], "unit": m["unit"],
                     "baseline_sha": "92d38ecb640bd462f2e19c0814d0f0b7df1ee692",
                     "machine": "box D3-g10: Linux x86_64, nproc 4, Intel Xeon @ 2.30GHz, 16 GB, /opt/hpo/venv-ci CPython, alone on the box",
                     "cpu_or_wall": "n/a", "tolerance": "exact",
                     "contention_note": "deterministic value; the probe ran in a separate baseline worktree while this box's gates ran; gate walls provisional"},
        "perturbation": {"change": f"mutant {key} applied in memory by the probe; full gate: fullgate.py run --src {r['src']} --key {key}",
                         "expected_direction": m["dirn"], "observed_value": m["val"]},
        "null_control": {"command": f"PYTHONPATH=tests/hastub python3 {probe}", "value": nm[0].split("=", 1)[1] if nm else "n/a", "note": m["nulld"]},
        "reproduction_steps": [f"PYTHONPATH=tests/hastub python3 {probe}", rec["gate_command"]],
        "proposed_fix_scope": f"tests only: a check in {m['scripts'][-1] if 'tests/features.py' not in m['scripts'] else 'tests/features.py'} at the input above that pins the baseline value ({m['base']})",
        "files": [r["file"], "tests/features.py"],
    }
    return rec


if __name__ == "__main__":
    for key in sys.argv[1:]:
        rec = build(key)
        json.dump(rec, open(f"{W}/results/{key}.json", "w"), indent=1)
        print(f"wrote results/{key}.json class={rec['class']} verdict={rec['gate']['verdict']}")
