#!/usr/bin/env python3
"""Box D3-g36: write results/<key>.json for every gated key (gates/<key>.json + spec.py + probes/out).
Command: python3 dev/audit/rounds/round11/D3/s1/wave/D3-g36/build_results.py   (from the tree root)"""
import json, re, sys
from pathlib import Path
W = Path(__file__).resolve().parent
sys.path.insert(0, str(W))
from spec import SPEC  # noqa: E402
S1 = W.parents[1]
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g36"
MACHINE = "box D3-g36: Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, alone on the box"


def results(key):
    p = W / "probes" / "out" / f"probe_{key}.txt"
    out = {}
    for line in p.read_text().splitlines() if p.exists() else []:
        m = re.match(r"RESULT (\S+?)=(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


rows = [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
hdr = (W / "keys.tsv").read_text().splitlines()[0].split("\t")
n = 0
for r in rows:
    k = dict(zip(hdr, r))
    key = k["key"]
    gp = W / "gates" / f"{key}.json"
    if not gp.exists():
        continue
    g = json.loads(gp.read_text())
    mut = json.loads((S1 / "state/results/complete" / f"{key}.json").read_text())["mutant"]
    sp = SPEC[key]
    res = results(key)
    v = g.get("verdict")
    cmd = f"PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 {REL}/probes/probe_{key}.py"
    rec = {
        "key": key,
        "site": f"{mut['file']}:{mut['line']} {mut['kind']}",
        "patch": f"{mut['old'].strip()} -> {mut['new'].strip()}",
        "function": k["function"], "cluster": k["cluster"], "slice": k["slice"], "m4_source": k["m4_source"],
        "gate": {x: g.get(x) for x in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end",
                                       "failed_scripts", "fail_lines", "cap_s", "provisional")},
        "gate_record": f"{REL}/gates/{key}.json",
        "gate_command": f"python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src {k['src']} --key {key}",
        "probe": {"path": f"{REL}/probes/probe_{key}.py", "command": cmd,
                  "baseline_value": res.get(sp["b"]), "mutant_value": res.get(sp["m"]),
                  "results": res, "inputs_tried": sp["inputs"]},
        "should_fail": sp["should_fail"],
    }
    if v == "KILLED":
        log = W / "gates" / f"{key}.log"
        lines = [l for l in (log.read_text(errors="replace").splitlines() if log.exists() else [])
                 if re.search(r"FAILED|^\s*FAIL ", l)]
        rec["class"] = "killed"
        rec["failing_check_lines"] = lines[:40]
    elif v == "TIMEOUT":
        log = W / "gates" / f"{key}.log"
        ran = [l for l in (log.read_text(errors="replace").splitlines() if log.exists() else []) if l.startswith(">>>") or "python3 tests/" in l]
        rec["class"] = "timeout"
        rec["last_script"] = ran[-1] if ran else None
    else:
        rec["class"] = sp["cls"]
        if sp["cls"] == "candidate":
            rec["finding"] = {
                "title": sp["title"], "claim": sp["claim"], "step": "D3.M3", "scope": "D3-s1",
                "class_guess": sp["class_guess"], "severity_claimed": sp["severity"], "severity_reason": sp["sev_why"],
                "stop_rule_class": "bug",
                "metric_definition": sp["metric"],
                "instrumented_symbol": f"custom_components.heatpump_optimizer.sysid:{k['function']}",
                "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", f"{REL}/probes/probe_{key}.py"],
                "evidence_command": cmd,
                "evidence": {"command": cmd, "harness_path": f"{REL}/probes/probe_{key}.py",
                             "value": res.get(sp["m"]), "unit": "outcome", "baseline_sha": "92d38ecb640bd462f2e19c0814d0f0b7df1ee692",
                             "machine": MACHINE, "cpu_or_wall": "count", "contention_note": "final re-take after the last gate, nothing else running (counts; first takes ran beside the gates with the same values)",
                             "tolerance": "exact", "load1": float(res.get("load1", "0") or 0), "thread_factor": float(res.get("thread_factor", "1") or 1)},
                "perturbation": {"change": f"sysid.py:{mut['line']} `{mut['old'].strip()}` -> `{mut['new'].strip()}`",
                                 "expected_direction": sp["direction"], "observed_value": res.get(sp["m"])},
                "null_control": {"command": cmd, "value": res.get("null_moved"),
                                 "note": "null_moved counts the probe's null-arm inputs where baseline and mutant differ; full-gate null in gates/null.json + null-note.txt"},
                "phenomenon_property": f"every behaviour-changing one-line mutant of sysid.py:{k['function']} fails at least one check of the full gate",
                "seam_rule": "awk -F'\\t' '$6==\"gate\"' dev/audit/rounds/round11/D3/s1/SURVIVORS.tsv",
                "files": [mut["file"], sp["should_fail"].split(" ")[0]],
                "proposed_fix_scope": f"a test in {sp['should_fail'].split(' ')[0]} pinning the outcome the probe moves (the assertion named in should_fail)",
            }
    (W / "results" / f"{key}.json").write_text(json.dumps(rec, indent=1) + "\n")
    n += 1
    print(f"{key} {v} -> {rec['class']}")
print(f"RESULT written={n}")
