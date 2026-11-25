#!/usr/bin/env python3
"""Write results/<key>.json for box D3-g29 from the gate record, the mutant record, the probe output and table.py."""
import json, os, re, shutil, sys
from pathlib import Path
SP = Path(__file__).resolve().parent
exec(open(SP / "table.py").read())
H = Path.home()
TR = H / "audit-r11-D3-s1"
S1 = TR / "dev/audit/rounds/round11/D3/s1"
W = S1 / "wave/D3-g29"
PT = H / "probe-tree/dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes"
POUT = SP / "pout"


def row(key):
    hdr, *rows = (W / "keys.tsv").read_text().splitlines()
    cols = hdr.split("\t")
    for r in rows:
        d = dict(zip(cols, r.split("\t")))
        if d["key"] == key:
            return d
    raise KeyError(key)


def results_of(out):
    return {m.group(1): m.group(2) for m in re.finditer(r"^RESULT (\S+?)=(.*)$", out, re.M)}


def build(key):
    r = row(key)
    mut = json.loads((S1 / "state/results" / r["src"] / f"{key}.json").read_text())["mutant"]
    g = json.loads((W / "gates" / f"{key}.json").read_text())
    t = T[key]
    (W / "probes").mkdir(exist_ok=True)
    for f in ("reach_sweep.py", "reach_sweep.out", f"probe_{key}.py"):
        if (PT / f).exists():
            shutil.copy2(PT / f, W / "probes" / f)
    out = (POUT / f"{key}.out").read_text()
    (W / "probes" / f"probe_{key}.out").write_text(out)
    cmd = f"PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 {t['probe']}"
    gate = {k: g.get(k) for k in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end", "failed_scripts", "more_fails_than_null", "child_cpu_s")}
    gate["path"] = f"dev/audit/rounds/round11/D3/s1/wave/D3-g29/gates/{key}.json"
    gate["command"] = f"PYTHONPATH=tests/hastub python3 {FG} run --src {r['src']} --key {key}"
    gate["provisional"] = "wall and load1 are provisional; nproc 4, Intel Xeon @ 2.10GHz"
    rec = {"key": key, "site": f"{r['file']}:{r['line']} {r['kind']}", "patch": f"{mut['old'].strip()} -> {mut['new'].strip()}",
           "function": r["function"], "cluster": r["cluster"], "slice": r["slice"], "m4_source": r["m4_source"], "gate": gate}
    v = g.get("verdict")
    if v == "KILLED":
        log = (W / "gates" / f"{key}.log").read_text(errors="replace") if (W / "gates" / f"{key}.log").exists() else ""
        lines, cur = [], None
        for ln in log.splitlines():
            m = re.match(r"^#{10} (.+?) #{10}$", ln)
            if m:
                cur = m.group(1); continue
            if cur and any(k in cur for k in g.get("killed_by", [])) and re.search(r"\bFAIL|FAILED|Error|Traceback", ln):
                lines.append(f"{cur}: {ln.strip()[:300]}")
        rec.update({"class": "killed", "killed_by": g.get("killed_by", []), "failing_check_lines": lines[:40],
                    "non_finding": f"the suite fails on this mutant: {', '.join(g.get('killed_by', []))} (gate_rc {g.get('gate_rc')})"})
    elif v == "TIMEOUT":
        log = (W / "gates" / f"{key}.log").read_text(errors="replace") if (W / "gates" / f"{key}.log").exists() else ""
        secs = re.findall(r"^#{10} (.+?) #{10}$", log, re.M)
        rec.update({"class": "timeout", "cap_s": g.get("cap_s", 14400), "last_script": secs[-1] if secs else None})
    else:
        res = results_of(out)
        rec["class"] = t["cls"]
        rec["probe"] = {"path": t["probe"], "command": cmd, "baseline_value": t["baseline"], "mutant_value": t["mutant"],
                        "inputs_tried": t["inputs"], "reach": t["reach"], "results": res,
                        "reach_command": f"PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g29/probes/reach_sweep.py",
                        "null_delta": res.get("null_delta")}
        rec["should_fail"] = {"script": t["should"][0], "assertion": t["should"][1]}
        if t["cls"] == "equivalent-candidate":
            rec["note"] = t["note"]
        if t["cls"] == "candidate":
            rec.update({
                "title": t["title"], "claim": t["claim"] + f" Full gate verdict {v}.", "step": "D3.M3", "scope": "D3-s1",
                "class_guess": "new", "severity_claimed": t["sev"], "stop_rule_class": "hygiene",
                "metric_definition": t["metric"], "instrumented_symbol": rec["site"],
                "harness_paths": [FG, t["probe"]], "evidence_command": cmd, "evidence_value": t["value"],
                "perturbation": {"change": f"the mutant {key} ({rec['patch']}) applied in memory by the probe; full gate: {gate['command']}",
                                 "expected_direction": t["direction"]},
                "null_control": {"command": cmd, "value": f"null_delta={res.get('null_delta')}",
                                 "note": "the probe's null inputs, where the edit cannot matter: identical under both arms"},
                "phenomenon_property": t["prop"], "files": t["files"],
                "proposed_fix_scope": "tests only: a check at the boundary input above that pins the baseline value",
                "reach": t["reach"]})
    p = W / "results" / f"{key}.json"
    p.write_text(json.dumps(rec, indent=1) + "\n")
    print(f"wrote {p.relative_to(TR)} class={rec['class']} verdict={v}")


if __name__ == "__main__":
    for k in sys.argv[1:]:
        build(k)
