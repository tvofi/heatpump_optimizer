#!/usr/bin/env python3
# Box D3-g40: write results/<key>.json for one gated key from keys.tsv, gates/<key>.json (fullgate.py's record),
# analysis.json (this box's probe classification) and the key's state/results/complete/<key>.json mutant record.
# Usage (tree root): python3 dev/audit/rounds/round11/D3/s1/wave/D3-g40/build_record.py <key>
import json, re, sys
from pathlib import Path

W = Path(__file__).resolve().parent
S1 = W.parent.parent
PROBES = "dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes"
PY = "PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3"


def gate_fields(g):
    keep = ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end", "failed_scripts", "cap_s", "note")
    out = {k: g.get(k) for k in keep if k in g}
    out["record"] = f"dev/audit/rounds/round11/D3/s1/wave/D3-g40/gates/{g.get('key', '')}.json"
    out["provisional"] = True
    return out


def fail_lines(key):
    log = W / "gates" / f"{key}.log"
    if not log.exists():
        return []
    lines = [l for l in log.read_text(errors="replace").splitlines() if re.search(r"\bFAIL\b|FAILED|Traceback|AssertionError", l)]
    return lines[:20]


def last_script(key):
    log = W / "gates" / f"{key}.log"
    if not log.exists():
        return None
    hits = re.findall(r"tests/[A-Za-z0-9_]+\.(?:py|mjs|sh)", log.read_text(errors="replace"))
    return hits[-1] if hits else None


def main(key):
    row = None
    lines = (W / "keys.tsv").read_text().splitlines()
    hdr = lines[0].split("\t")
    for l in lines[1:]:
        f = l.split("\t")
        if f[0] == key:
            row = dict(zip(hdr, f))
    assert row, key
    g = json.loads((W / "gates" / f"{key}.json").read_text())
    mrec = json.loads((S1 / "state" / "results" / "complete" / f"{key}.json").read_text())
    mut = mrec.get("mutant", {})
    a = json.loads((W / "analysis.json").read_text())[key]
    verdict = g.get("verdict")
    probe = f"{PROBES}/probe_{key}.py"
    should_scripts = mrec.get("should_have_failed") or sorted({r.get("script") for r in mrec.get("runs", []) if isinstance(r, dict) and r.get("script")} | set())
    rec = {
        "key": key,
        "site": f"{row['file']}:{row['line']} {row['kind']}",
        "patch": f"{mut.get('old', '').strip()} -> {mut.get('new', '').strip()}",
        "function": row["function"], "cluster": row["cluster"], "slice": row["slice"], "fullnet": row["fullnet"],
        "m4_source": row["m4_source"],
        "gate": gate_fields(g),
        "machine": "box D3-g40, nproc 4, Intel(R) Xeon(R) Processor @ 2.10GHz (MACHINE.txt); wall/load provisional",
    }
    if verdict == "KILLED":
        rec["class"] = "killed"
        rec["killed_by"] = g.get("killed_by")
        rec["failing_check_lines"] = fail_lines(key)
        rec["non_finding"] = {"claim": f"mutant {key} ({rec['patch']}) is killed by the full gate: {g.get('killed_by')}",
                              "command": f"python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src {row['src']} --key {key}",
                              "value": f"gate_rc {g.get('gate_rc')}, killed_by {g.get('killed_by')}"}
    elif verdict == "TIMEOUT":
        rec["class"] = "timeout"
        rec["timeout"] = {"cap_s": g.get("cap_s", 14400), "last_script": last_script(key)}
    else:
        rec["class"] = a["probe_class"]
    rec["probe"] = {"path": probe, "command": f"{PY} {probe}", "metric": a["metric"][0],
                    "baseline_value": a["metric"][1], "mutant_value": a["metric"][2], "unit": a["metric"][3],
                    "observed": a["observed"], "inputs_tried": a["inputs"], "run_output": f"{PROBES}/{key}/RUN.txt",
                    "probe_class": a["probe_class"]}
    rec["should_fail"] = {"scripts": should_scripts, "assertion_lacking": a["should_fail_assert"]}
    if rec["class"] == "candidate":
        rec["finding"] = {
            "title": a["title"], "claim": a["claim"], "step": "D3.M3", "scope": "D3-s1", "class_guess": "I1",
            "severity_claimed": a["severity"],
            "metric_definition": f"{a['metric'][0]} ({a['metric'][3]}) printed by the probe, baseline arm vs one-line-mutant arm",
            "instrumented_symbol": f"custom_components.heatpump_optimizer.tariff:{row['function']} ({row['file']}:{row['line']})",
            "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", probe],
            "evidence_command": f"{PY} {probe}",
            "perturbation": {"change": rec["patch"], "expected_direction": a["expected_direction"], "observed_value": a["observed"]},
            "null_control": "the box's fullgate.py null gate (gates/null.json) for the gate; inside the probe the baseline arm run twice (null_differing 0) or an unaffected input (null_delta 0)",
            "files": [row["file"]],
        }
    out = W / "results" / f"{key}.json"
    out.write_text(json.dumps(rec, indent=1) + "\n")
    print(f"RECORD {key} {verdict} class={rec['class']}")


if __name__ == "__main__":
    main(sys.argv[1])
