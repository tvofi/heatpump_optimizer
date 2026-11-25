#!/usr/bin/env python3
"""write_result.py <key>: results/<key>.json for box D3-g01 from gates/<key>.json + analysis.py."""
import json, re, sys
from pathlib import Path
W = Path.home() / "audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g01"
S1 = W.parents[1]
exec(open(Path.home() / "pt/analysis.py").read())
key = sys.argv[1]
row = next(l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.startswith(key))
_, src, file, line, function, cluster, slice_, fullnet, kind, reach, m4src = row
mut = json.loads((S1 / "state/results" / src / f"{key}.json").read_text())["mutant"]
g = json.loads((W / "gates" / f"{key}.json").read_text())
null = json.loads((W / "gates" / "null.json").read_text())
verdict = g["verdict"]
a = A[key]
probe_path = P.format(key)
rec = {
    "key": key, "site": f"{file}:{line} {kind}", "patch": f"{mut['old'].strip()} -> {mut['new'].strip()}",
    "function": function, "cluster": cluster, "slice": slice_, "m4_source": m4src,
    "gate": {k: g.get(k) for k in ("verdict", "killed_by", "gate_rc", "failed_scripts", "more_fails_than_null",
                                   "wall_s", "child_cpu_s", "load1_start", "load1_end", "summary", "cap_s", "note")},
    "gate_command": f"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src {src} --key {key}",
    "gate_record": f"dev/audit/rounds/round11/D3/s1/wave/D3-g01/gates/{key}.json",
    "provisional": "wall/cpu/load are provisional (nproc 4, Intel Xeon @ " + __import__("os").environ.get("GATE_CPU","2.10GHz") + ", box alone); counts final",
}
if verdict == "KILLED":
    log = (W / "gates" / f"{key}.log").read_text(errors="replace")
    lines, cur = [], None
    for ln in log.splitlines():
        m = re.match(r"^#{10} (.+?) #{10}$", ln)
        if m:
            cur = m.group(1); continue
        if cur and any(k in cur or cur.endswith(k) for k in g["killed_by"]) and re.search(r"\bFAIL|FAILED", ln):
            lines.append(f"{cur}: {ln.strip()}"[:300])
    rec.update(**{"class": "killed"}); rec.update(killed_by=g["killed_by"], failing_check_lines=lines[:20],
               non_finding=f"mutant {key} at {file}:{line} is pinned by the full gate: KILLED by {', '.join(g['killed_by'])}")
elif verdict == "TIMEOUT":
    log_p = W / "gates" / f"{key}.log"
    last = None
    if log_p.exists():
        secs = re.findall(r"^#{10} (.+?) #{10}$", log_p.read_text(errors="replace"), re.M)
        last = secs[-1] if secs else None
    rec.update(**{"class": "timeout"}); rec.update(cap_s=g.get("cap_s"), last_script=last)
else:
    rec["class"] = a["cls"]
    rec["probe"] = {"path": probe_path, "command": CMD.format(key), "metric": a["metric"],
                    "baseline_value": a["base"], "mutant_value": a["mut"], "inputs_tried": a["inputs"],
                    "instrumented_symbol": a["symbol"]}
    rec["should_fail"] = a["should"]
    if a["cls"] == "candidate":
        rec["finding"] = {
            "title": a["title"], "step": "D3.M3", "scope": "D3-s1", "class_guess": "I1",
            "severity_claimed": a["sev"], "stop_rule_class": "bug",
            "claim": f"Mutant {key} at {file}:{line} ({mut['old'].strip()} -> {mut['new'].strip()}) is not killed by the full "
                     f"GATE_SCOPE=full GOLDEN_MODE=drift gate (verdict {verdict}, gate_rc {g.get('gate_rc')}, no script red beyond this box's null), "
                     f"yet the probe's number moves: baseline {a['base']}, mutant {a['mut']}.",
            "mechanism": f"Check that should have failed (D3.M4): {a['should']}.",
            "metric_definition": a["metric"],
            "instrumented_symbol": a["symbol"],
            "phenomenon_property": a["prop"],
            "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", probe_path],
            "evidence_command": CMD.format(key),
            "perturbation": {"change": f"the one-line mutant {key} applied in memory by the probe; full gate: "
                                       f"fullgate.py run --src {src} --key {key}",
                             "expected_direction": a["direction"], "unit": a["unit"]},
            "null_control": {"command": CMD.format(key), "value": "null_delta=0 count",
                             "gate_null": "fullgate.py null on box D3-g01: gate_rc %s, red %s" % (null.get("gate_rc"), null.get("failed_scripts"))},
            "files": [file, "tests/features.py"],
            "proposed_fix_scope": "tests only: a check at the probe's distinguishing input that pins the baseline value",
        }
    else:
        rec["non_finding"] = f"mutant {key} at {file}:{line} is not killed by the full gate (verdict {verdict}) and is equivalent on every input tried: {a['should']}"
(W / "results" / f"{key}.json").write_text(json.dumps(rec, indent=1) + "\n")
print("WROTE", key, verdict, rec.get("class") or rec.get("cls"))
