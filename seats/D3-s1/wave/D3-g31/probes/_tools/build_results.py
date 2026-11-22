"""results/<key>.json for every gated key of box D3-g31 not yet recorded. Usage: build_results.py [--force]"""
import json, re, sys
from pathlib import Path
exec(open(Path(__file__).with_name("spec.py")).read())
TR = Path.home() / "audit-r11-D3-s1"
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g31"
W = TR / REL
force = "--force" in sys.argv
keys = [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
hdr = (W / "keys.tsv").read_text().splitlines()[0].split("\t")
out = []
for row in keys:
    r = dict(zip(hdr, row)); k = r["key"]
    g = W / "gates" / f"{k}.json"
    dst = W / "results" / f"{k}.json"
    if not g.exists() or (dst.exists() and not force):
        continue
    gate = json.loads(g.read_text())
    mrec = json.loads((TR / "dev/audit/rounds/round11/D3/s1/state/results" / r["src"] / f"{k}.json").read_text())["mutant"]
    v = gate.get("verdict")
    rec = {"key": k, "site": f"{r['file']}:{r['line']} {r['kind']}", "patch": f"`{mrec['old'].strip()}` -> `{mrec['new'].strip()}`",
           "function": r["function"], "cluster": r["cluster"], "slice": r["slice"], "m4_source": r["m4_source"],
           "gate": {x: gate.get(x) for x in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end", "failed_scripts",
                                             "more_fails_than_null", "summary", "child_cpu_s", "command", "provisional")},
           "gate_record": f"{REL}/gates/{k}.json", "gate_command": f"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src {r['src']} --key {k}",
           "machine": "box D3-g31: Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB (walls and loads provisional)"}
    s = S[k]
    probe = {"path": f"{REL}/probes/probe_{k}.py", "command": f"PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 {REL}/probes/probe_{k}.py",
             "output": f"{REL}/probes/probe_{k}.out", "baseline_value": s["base"], "mutant_value": s["mut"], "inputs_tried": s["inputs"]}
    if v == "KILLED":
        log = (W / "gates" / f"{k}.log").read_text(errors="replace") if (W / "gates" / f"{k}.log").exists() else ""
        lines, cur = [], None
        for ln in log.splitlines():
            mm = re.match(r"^#{10} (.+?) #{10}$", ln)
            if mm: cur = mm.group(1); continue
            if cur and any(cur.endswith(" " + kb) or kb in cur for kb in gate.get("killed_by", [])) and re.match(r"^\s*(FAIL\b|\d+ of \d+ .*FAILED)", ln):
                lines.append(f"{cur}: {ln.strip()[:300]}")
        rec.update({"class": "killed", "killed_by": gate.get("killed_by"), "failing_check_lines": lines[:40],
                    "non_finding": f"the suite fails on this mutant: gate_rc={gate.get('gate_rc')}, killed_by={gate.get('killed_by')}",
                    "probe": dict(probe, note="written before the gate; the kill makes the key a non-finding")})
    elif v == "TIMEOUT":
        log = W / "gates" / f"{k}.log"
        last = [m for m in re.findall(r"^#{10} (.+?) #{10}$", log.read_text(errors="replace"), re.M)] if log.exists() else []
        rec.update({"class": "timeout", "cap_s": gate.get("cap_s"), "last_script": last[-1] if last else None, "probe": probe})
    else:
        rec.update({"class": s["cls"], "probe": probe, "should_fail": s["should_fail"]})
        if s["cls"] == "equivalent-candidate":
            rec["note"] = s["note"]
        else:
            f = dict(s["finding"])
            f.update({"step": "D3.M3", "scope": "D3-s1", "class_guess": "I1", "severity_claimed": f.pop("severity"),
                      "stop_rule_class": "bug", "instrumented_symbol": f"custom_components.heatpump_optimizer.price_model:{r['function']}",
                      "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", probe["path"]],
                      "evidence_command": probe["command"] + " ; " + rec["gate_command"],
                      "seam_rule": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv (the wave list), each key's fullgate.py verdict",
                      "full_gate": f"{v} gate_rc={gate.get('gate_rc')} (null control: {REL}/gates/null.json)"})
            rec["finding"] = f
    dst.write_text(json.dumps(rec, indent=1) + "\n")
    out.append(f"{k} {v} {rec['class']}")
print("\n".join(out) or "nothing new")
