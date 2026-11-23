#!/usr/bin/env python3
"""Write results/<key>.json for one gated key of box D3-g26: build_result.py <key>."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from keymeta import META, CMD, PDIR  # noqa: E402

W = Path.home() / "audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g26"
WORK = Path.home() / "g26work"
MACHINE = "box D3-g26 cloud: Linux x86_64, nproc 4, Intel Xeon @ 2.30GHz, 16 GB, venv-ci CPython, alone on its machine"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"


def results(key):
    out = {}
    for ln in (WORK / f"probe_{key}.out").read_text().splitlines():
        m = re.match(r"RESULT (\w+)=(.*)$", ln)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def last_script(log):
    if not log.exists():
        return None
    names = re.findall(r"(tests/[\w/]+\.(?:py|mjs|sh))", log.read_text(errors="replace"))
    return names[-1] if names else None


def main(key):
    row = next(l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.startswith(key))
    _k, src, file, line, function, cluster, _sl, _fn, kind, _reach, m4 = row[:11]
    gate = json.loads((W / "gates" / f"{key}.json").read_text())
    mut = json.loads((W.parent.parent / "state/results/complete" / f"{key}.json").read_text())["mutant"]
    meta = META[key]
    verdict = gate["verdict"]
    rec = {
        "key": key,
        "site": f"{file}:{line} {kind}",
        "patch": f"{mut['old'].strip()} -> {mut['new'].strip()}",
        "function": function,
        "cluster": cluster,
        "m4_source": m4,
        "gate": {k: gate.get(k) for k in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end",
                                          "failed_scripts", "cap_s")},
        "gate_record": f"dev/audit/rounds/round11/D3/s1/wave/D3-g26/gates/{key}.json",
        "gate_command": f"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src {src} --key {key}"
                        " (GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=<baseline> GATE_JOBS=1 ./tests/run.sh), driven by gate_wave.sh run",
        "provisional": "wall and load1 are provisional (nproc 4, Intel Xeon @ 2.30GHz); the verdict is a count",
    }
    if verdict == "KILLED":
        rec["class"] = "killed"
        rec["killed_by"] = gate.get("killed_by")
        rec["fail_lines"] = gate.get("fail_lines", {})
        rec["non_finding"] = {"claim": f"mutant {key} at {file}:{line} is caught by the full gate",
                              "command": rec["gate_command"],
                              "value": f"KILLED by {', '.join(gate.get('killed_by') or [])} (gate_rc {gate.get('gate_rc')})"}
    elif verdict == "TIMEOUT":
        rec["class"] = "timeout"
        rec["timeout"] = {"cap_s": gate.get("cap_s", 14400),
                          "last_script": last_script(W / "gates" / f"{key}.log")}
    else:
        r = results(key)
        cmd = CMD.format(key=key)
        bval = r.get(meta["base_key"]) if meta["base_key"] else "0 (the metric is a baseline-vs-mutant delta)"
        mval = r.get(meta["mut_key"])
        rec["class"] = meta["cls"]
        rec["probe"] = {"path": f"{PDIR}/probe_{key}.py", "helper": f"{PDIR}/g26_common.py", "command": cmd,
                        "baseline_value": bval, "mutant_value": mval, "metric": meta["metric"], "unit": meta["unit"],
                        "all_results": r, "inputs_tried": meta["inputs"]}
        rec["should_fail"] = {"script": meta["should"][0], "assertion": meta["should"][1]}
        if meta["cls"] == "candidate":
            null = {k: v for k, v in r.items() if k.startswith("null")}
            rec["finding"] = {
                "title": meta["title"], "scope": "D3-s1", "step": "D3.M3", "class_guess": "I1",
                "severity_claimed": "low", "stop_rule_class": "hygiene",
                "claim": f"Mutant {key} ({rec['patch']}) at {file}:{line} {'survives the full gate (SURVIVED)' if verdict == 'SURVIVED' else 'leaves the full gate red only as the null is (RED-AS-NULL)'}, yet the probe's {meta['metric']} moves from {bval} to {mval}.",
                "metric_definition": meta["unit"] + f" ({meta['metric']}; probe header carries the full definition)",
                "phenomenon_property": meta["phen"],
                "instrumented_symbol": f"custom_components.heatpump_optimizer.optimizer:{function}",
                "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", f"{PDIR}/probe_{key}.py", f"{PDIR}/g26_common.py"],
                "evidence_command": cmd,
                "evidence": {"command": cmd, "harness_path": f"{PDIR}/probe_{key}.py", "value": mval, "unit": meta["unit"],
                             "baseline_sha": BASE, "machine": MACHINE, "cpu_or_wall": "count",
                             "contention_note": "deterministic count; probes ran in a separate baseline worktree while the box's GATE_JOBS=1 gates ran",
                             "tolerance": "exact", "load1": float(r.get("load1", "0").split()[0]),
                             "thread_factor": float(r.get("thread_factor", "1").split()[0])},
                "perturbation": {"change": f"{file}:{line} {rec['patch']}, applied in memory by the probe (and on disk by fullgate.py for the gate)",
                                 "expected_direction": meta["direction"], "observed_value": mval},
                "null_control": {"command": cmd, "value": "; ".join(f"{k}={v}" for k, v in null.items()) or "n/a"},
                "proposed_fix_scope": f"tests only: a check in {meta['should'][0].split(' ')[0]} at the distinguishing input above pinning the baseline value",
                "files": [file, meta["should"][0].split(" ")[0]],
            }
        else:
            rec["non_finding"] = {"claim": f"mutant {key} at {file}:{line} ({rec['patch']}) survives the full gate but is equivalent through production: {meta['should'][1]}",
                                  "command": cmd, "value": f"{meta['metric']}: baseline {bval}, mutant {mval}; " + "; ".join(meta["inputs"])}
    (W / "results").mkdir(exist_ok=True)
    (W / "results" / f"{key}.json").write_text(json.dumps(rec, indent=1) + "\n")
    print(f"WROTE results/{key}.json class={rec['class']} verdict={verdict}")


if __name__ == "__main__":
    for k in sys.argv[1:]:
        main(k)
