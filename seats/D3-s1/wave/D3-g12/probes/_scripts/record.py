import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); from meta import M
S = Path.home() / "audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1"; W = S / "wave/D3-g12"
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g12"
EQUIV = {"fc4fe0f49de831a8"}
rows = {l.split("\t")[0]: dict(zip(open(W / "keys.tsv").readline().rstrip("\n").split("\t"), l.rstrip("\n").split("\t"))) for l in list(open(W / "keys.tsv"))[1:] if l.strip()}

def results(out):
    r = {}
    for line in out.splitlines():
        m = re.match(r"RESULT (\S+?)=(.*)$", line)
        if m: r[m.group(1)] = m.group(2)
    return r

def build(key):
    row, meta = rows[key], M[key]
    g = json.loads((W / "gates" / f"{key}.json").read_text())
    mut = json.loads((S / "state/results/complete" / f"{key}.json").read_text())["mutant"]
    verdict = g.get("verdict")
    gate = {k: g.get(k) for k in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end", "failed_scripts", "summary", "command")}
    gate["record"] = f"{REL}/gates/{key}.json"; gate["provisional_timing"] = True
    rec = {"key": key, "site": f"{row['file']}:{row['line']} {row['kind']}",
           "patch": f"{mut['old'].strip()} -> {mut['new'].strip()}", "function": row["function"], "cluster": row["cluster"],
           "slice": row["slice"], "m4_source": row["m4_source"], "gate": gate}
    cmd = f"PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 {REL}/probes/probe_{key}.py"
    if verdict == "KILLED":
        log = (W / "gates" / f"{key}.log")
        fails = [l.strip() for l in (log.read_text(errors="replace").splitlines() if log.exists() else []) if re.search(r"\bFAIL", l)][:40]
        rec.update({"class": "killed", "failing_check_lines": fails,
                    "non_finding": f"the full gate fails on it: run.sh rc {g.get('gate_rc')}, killed by {', '.join(g.get('killed_by') or [])}"})
        return rec
    if verdict == "TIMEOUT":
        log = W / "gates" / f"{key}.log"
        last = [l for l in (log.read_text(errors="replace").splitlines() if log.exists() else []) if l.strip()][-5:]
        rec.update({"class": "timeout", "cap_s": g.get("cap_s", 14400), "last_log_lines": last})
        return rec
    out = (W / "probes" / f"probe_{key}.out").read_text()
    r = results(out)
    rec["probe"] = {"path": f"{REL}/probes/probe_{key}.py", "output": f"{REL}/probes/probe_{key}.out", "command": cmd,
                    "baseline_value": f"{meta['rb']}={r.get(meta['rb'])}", "mutant_value": f"{meta['rm']}={r.get(meta['rm'])}",
                    "inputs_tried": meta["inputs"], "results": r}
    rec["should_fail"] = meta["should"]
    if key in EQUIV:
        rec["class"] = "equivalent-candidate"
        rec["equivalence"] = ("derate_from_duty returns min(DERATE_MAX, max(DERATE_MIN, 1 - duty*1.5)) with duty clamped to DEFROST_DUTY_MAX; "
                              f"DERATE_MIN={r.get('derate_min')} equals 1 - 1.5*0.30={r.get('one_minus_loss_x_cap')}, so a duty above 0.30 lands on the floor under either cap: "
                              f"{r.get('points_differ')} of {r.get('grid_points')} duties differ (max |diff| {r.get('max_abs_diff')}); the published factor and summary at duty 0.5 are identical")
        return rec
    rec["class"] = "candidate"
    rec["finding"] = {
        "title": meta["title"], "claim": meta["claim"], "step": "D3.M3", "scope": "D3-s1", "class_guess": "I1",
        "severity_claimed": meta["sev"], "stop_rule_class": "bug" if meta["sev"] != "low" or key not in ("3e3fbb5fcbbe9bcc", "0e3569fef6b39497") else "hygiene",
        "metric_definition": open(W / "probes" / f"probe_{key}.py").read().split("# Metric: ", 1)[1].split("\n", 1)[0][:200],
        "instrumented_symbol": open(W / "probes" / f"probe_{key}.py").read().split("# Instrumented symbol: ", 1)[1].split("\n", 1)[0],
        "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", f"{REL}/probes/probe_{key}.py"],
        "evidence_command": f"(gate) cd <tree> && python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src {row['src']} --key {key}  -> {verdict}, gate_rc {g.get('gate_rc')}; (probe) {cmd}",
        "perturbation": {"change": open(W / "probes" / f"probe_{key}.py").read().split("# Perturbation: ", 1)[1].split("\n", 1)[0],
                         "expected_direction": meta["dir"], "observed_value": f"{r.get(meta['rb'])} -> {r.get(meta['rm'])}"},
        "null_control": {"command": "python3 dev/audit/rounds/round11/D3/s1/fullgate.py null (this box)", "value": "see gates/null.json",
                         "note": "gate null: comment-only marker on the same box; probe null: " + open(W / "probes" / f"probe_{key}.py").read().split("# Null control: ", 1)[1].split("\n", 1)[0]},
        "phenomenon_property": "a production line whose one-line mutant changes the value its symbol delivers must turn the full GATE_SCOPE=full GOLDEN_MODE=drift gate red",
        "seam_rule": "awk -F'\\t' '$6==\"gate\"' dev/audit/rounds/round11/D3/s1/SURVIVORS.tsv",
        "files": [row["file"]],
    }
    if verdict == "RED-AS-NULL": rec["gate"]["note"] = "red, but no script beyond the null control: read as survived"
    return rec

if __name__ == "__main__":
    for key in sys.argv[1:]:
        rec = build(key)
        (W / "results" / f"{key}.json").write_text(json.dumps(rec, indent=1))
        print(key, rec["gate"]["verdict"], rec["class"])
