"""Write results/<key>.json for box D3-g09 from the gate record, the keys.tsv row, the probe output and META."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
exec(open(Path(__file__).parent / "meta.py").read())
TR = Path.home() / "audit-r11-D3-s1"
S1 = TR / "dev/audit/rounds/round11/D3/s1"
W = S1 / "wave/D3-g09"
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g09"
MACHINE = "box D3-g09: 4 vCPU Intel(R) Xeon(R) Processor @ 2.10GHz, 16 GB, no swap"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
GATE_CMD = ("cd $TREE && GATE_JOBS=1 python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key {k}"
            "  (GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=" + BASE + " GATE_JOBS=1 ./tests/run.sh on the one-line mutant)")
EXPECTED_DIR = {"9cdf54d2309cfcc8": "up", "d8101520588009d9": "up", "3d83c32f185cf411": "up", "002980a15ae8b9a9": "down",
                "1785780ac9dd1b18": "to_zero", "326b26f53972df61": "sign_flip", "104db258fed59c2d": "up",
                "8daaf4fcaf8cd897": "to_zero", "3cfe39778305daba": "to_zero", "425a9196b86265d0": "up",
                "0c99189b7639f1bd": "to_zero", "df697cc04154fbdd": "to_zero"}


def row(key):
    lines = (W / "keys.tsv").read_text().splitlines()
    hdr = lines[0].split("\t")
    for l in lines[1:]:
        f = dict(zip(hdr, l.split("\t")))
        if f["key"] == key:
            return f
    raise KeyError(key)


def probe_out(key):
    t = (W / "probes" / f"out_{key}.txt").read_text()
    g = lambda n: float(re.search(rf"RESULT {n}=([0-9.]+)", t).group(1))
    return t, g("load1"), g("thread_factor")


def build(key):
    r = row(key)
    m = json.load(open(S1 / "state/results/complete" / f"{key}.json"))["mutant"]
    gate = json.load(open(W / "gates" / f"{key}.json"))
    v = gate.get("verdict")
    M = META[key]
    cmd = CMD.format(k=key)
    out, l1, tf = probe_out(key)
    rec = {
        "key": key,
        "site": f"{r['file']}:{r['line']} {r['kind']}",
        "patch": f"{m['old'].strip()} -> {m['new'].strip()}",
        "function": r["function"], "cluster": r["cluster"], "slice": r["slice"], "m4_source": r["m4_source"],
        "gate": {k: gate.get(k) for k in ("verdict", "killed_by", "gate_rc", "failed_scripts", "wall_s", "child_cpu_s",
                                           "load1_start", "load1_end", "summary", "command", "provisional", "cap_s", "note")
                 if k in gate},
        "gate_record": f"{REL}/gates/{key}.json",
        "gate_command": GATE_CMD.format(k=key),
    }
    if v == "KILLED":
        rec["class"] = "killed"
        log = (W / "gates" / f"{key}.log")
        lines = [l for l in log.read_text(errors="replace").splitlines() if re.search(r"\bFAIL\b|FAILED|✗|^\s*fail ", l)] if log.exists() else []
        rec["failing_check_lines"] = lines[:40]
        rec["probe"] = {"path": f"{REL}/probes/probe_{key}.py", "command": cmd, "baseline": M["base"], "mutant": M["mut"],
                        "inputs_tried": M["inputs"], "note": "written before the gate answered; kept as the executed step-4 number"}
        return rec
    if v == "TIMEOUT":
        rec["class"] = "timeout"
        log = (W / "gates" / f"{key}.log")
        last = [l for l in log.read_text(errors="replace").splitlines() if "tests/" in l][-1:] if log.exists() else []
        rec["last_script_seen"] = last
        return rec
    rec["class"] = M["cls"]
    rec["probe"] = {"path": f"{REL}/probes/probe_{key}.py", "output": f"{REL}/probes/out_{key}.txt", "command": cmd,
                    "metric": M["metric"], "baseline_value": M["base"], "mutant_value": M["mut"],
                    "inputs_tried": M["inputs"], "null_control": M["null"], "load1": l1, "thread_factor": tf}
    rec["should_fail"] = M["should"]
    if M["cls"] == "candidate":
        rec.update({
            "title": M["title"], "claim": M["claim"], "step": "D3.M3", "scope": "D3-s1",
            "class_guess": M["class_guess"], "severity_claimed": M["severity"], "stop_rule_class": "bug",
            "metric_definition": M["metric"][:200],
            "instrumented_symbol": f"custom_components.heatpump_optimizer.coordinator:{r['function']}",
            "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", f"{REL}/probes/probe_{key}.py"],
            "evidence_command": cmd,
            "evidence": {"command": cmd, "harness_path": f"{REL}/probes/probe_{key}.py", "value": M["mut"], "unit": "count",
                         "baseline_sha": BASE, "machine": MACHINE, "cpu_or_wall": "count",
                         "contention_note": "one full gate running on the box (GATE_JOBS=1); the probe's numbers are counts and values, contention-immune",
                         "tolerance": "exact", "load1": l1, "thread_factor": tf},
            "gate_evidence": {"command": GATE_CMD.format(k=key), "record": f"{REL}/gates/{key}.json", "verdict": v,
                              "gate_rc": gate.get("gate_rc"), "null_record": f"{REL}/gates/null.json"},
            "perturbation": {"change": f"mutant {key}: {m['old'].strip()} -> {m['new'].strip()} ({r['file']}:{r['line']}), applied in memory by the probe and on disk by fullgate.py",
                             "expected_direction": EXPECTED_DIR[key], "observed_value": M["mut"], "direction": M["direction"]},
            "null_control": {"command": cmd, "value": M["null"],
                             "note": "the probe's equal-arm cells; for the gate, this box's fullgate.py null (gates/null.json)"},
            "phenomenon_property": "a production line whose one-line mutant changes the value its own seam delivers on a stated input is pinned by at least one check of the closure that executes it",
            "seam_rule": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv  (the u1 full-net survivors; this box's keys: " + REL + "/keys.tsv)",
            "files": [r["file"]],
            "proposed_fix_scope": "tests only: add the distinguishing arm named in should_fail to the closure script that executes the line",
        })
    return rec


if __name__ == "__main__":
    for key in sys.argv[1:]:
        rec = build(key)
        (W / "results").mkdir(exist_ok=True)
        (W / "results" / f"{key}.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
        print(f"wrote results/{key}.json class={rec['class']} verdict={rec['gate'].get('verdict')}")
