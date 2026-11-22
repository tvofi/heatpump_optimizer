#!/usr/bin/env python3
"""Write wave/D3-g19/results/<key>.json for one gated key: gate record + probe run (in the probe tree) + analysis."""
import json, os, re, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from analysis import A, EQUIV, FG

key = sys.argv[1]
HOME = Path.home()
TR = HOME / "audit-r11-D3-s1"; PT = HOME / "probe-tree"
REL = "dev/audit/rounds/round11/D3/s1"
W = TR / REL / "wave/D3-g19"; SEAT = HOME / "d3wave-seat/wave/D3-g19"
row = dict(zip(*[l.split("\t") for l in (W / "keys.tsv").read_text().splitlines() if l.split("\t")[0] in ("key", key)]))
mut = json.loads((TR / REL / "state/results" / row["src"] / f"{key}.json").read_text())["mutant"]
g = json.loads((W / "gates" / f"{key}.json").read_text())
probe_rel = f"{REL}/wave/D3-g19/probes/probe_{key}.py"
cmd = f"PYTHONPATH=tests/hastub python3 {probe_rel}"
rec = {"key": key, "site": f"{row['file'].split('/')[-1]}:{row['line']} {row['kind']}", "file": row["file"],
       "line": int(row["line"]), "patch": f"{mut['old'].strip()} -> {mut['new'].strip()}", "function": row["function"],
       "cluster": row["cluster"], "slice": row["slice"], "fullnet": row["fullnet"], "reach_carried": row["reach"],
       "m4_source": row["m4_source"],
       "gate": {k: g.get(k) for k in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end", "failed_scripts",
                                       "fail_lines", "more_fails_than_null", "summary", "cap_s", "note", "command")},
       "gate_record": f"{REL}/wave/D3-g19/gates/{key}.json", "gate_log": f"{REL}/wave/D3-g19/gates/{key}.log",
       "gate_command": f"PYTHONPATH=tests/hastub python3 {FG} run --src {row['src']} --key {key}",
       "provisional": "wall and load1 are provisional; nproc 4, Intel Xeon @ 2.10GHz, box D3-g19 alone on its machine"}
v = g["verdict"]
if v == "KILLED":
    log = (W / "gates" / f"{key}.log").read_text(errors="replace")
    lines, cur = [], None
    for ln in log.splitlines():
        m = re.match(r"^#{10} (.+?) #{10}$", ln)
        if m:
            cur = m.group(1); continue
        if cur and any(cur.endswith(k) or k in cur for k in g["killed_by"]) and re.match(r"^\s*(FAIL\b|\d+ of \d+ .*FAILED|>>> )", ln):
            lines.append(f"{cur}: {ln.strip()}")
    rec.update({"class": "killed", "killed_by": g["killed_by"], "failing_check_lines": lines[:40],
                "non_finding": f"the suite fails on it: KILLED by {', '.join(g['killed_by'])} (gate_rc {g['gate_rc']})"})
elif v == "TIMEOUT":
    log = W / "gates" / f"{key}.log"
    last = None
    if log.exists():
        for ln in log.read_text(errors="replace").splitlines():
            m = re.match(r"^#{10} (.+?) #{10}$", ln)
            if m: last = m.group(1)
    rec.update({"class": "timeout", "cap_s": g.get("cap_s"), "last_script_running": last})
else:
    out = subprocess.run(cmd, shell=True, cwd=PT, capture_output=True, text=True, timeout=1800)
    res = [l for l in out.stdout.splitlines() if l.startswith("RESULT ")]
    if out.returncode != 0:
        raise SystemExit(f"probe failed rc={out.returncode}: {out.stderr[-2000:]}")
    vals = dict(l[7:].split("=", 1) for l in res)
    hdr = (PT / probe_rel).read_text().split("import os", 1)[0]
    tried = next((l[2:].strip() for l in hdr.splitlines() if l.startswith("# Inputs tried:")), "")
    probe = {"path": probe_rel, "command": cmd, "results": res, "inputs_tried": tried,
             "load1": vals.get("load1"), "thread_factor": vals.get("thread_factor")}
    if key in EQUIV:
        rec.update({"class": "equivalent-candidate", "probe": probe, "equivalence": EQUIV[key],
                    "should_fail": "none: no input tried separates the arms (" + tried + ")"})
    else:
        a = A[key]
        # baseline/mutant pair: the first *_baseline / *_mutant RESULT pair
        bk = next(k for k in vals if k.endswith("_baseline")); mk = bk[: -len("_baseline")] + "_mutant"
        probe.update({"baseline_value": vals[bk], "mutant_value": vals.get(mk), "metric_key": bk[: -len("_baseline")]})
        nulls = {k: v for k, v in vals.items() if k.startswith("null")}
        rec.update({"class": "candidate", "probe": probe, "reach": a["reach"], "should_fail": a["should_fail"],
            "finding": {
                "title": a["title"], "claim": a["claim"], "step": "D3.M3", "scope": "D3-s1", "class_guess": "new",
                "severity_claimed": a["sev"], "stop_rule_class": a["stop"], "metric_definition": a["metric"],
                "instrumented_symbol": f"custom_components.heatpump_optimizer.{row['file'].split('/')[-1][:-3]}:{row['function']}",
                "harness_paths": [FG, probe_rel], "evidence_command": cmd,
                "perturbation": {"change": f"{row['file']}:{row['line']} {mut['old'].strip()} -> {mut['new'].strip()} (in memory)",
                                 "expected_direction": a["direction"], "observed_value": f"{vals[bk]} -> {vals.get(mk)}"},
                "null_control": {"command": cmd, "value": json.dumps(nulls), "note": "inputs where the arms must agree; full-gate null on this box: gates/null.json"},
                "phenomenon_property": a["prop"],
                "seam_rule": f"PYTHONPATH=tests/hastub python3 {probe_rel}",
                "proposed_fix_scope": a["fix"], "files": a["files"]}})
(W / "results").mkdir(exist_ok=True)
(W / "results" / f"{key}.json").write_text(json.dumps(rec, indent=1) + "\n")
(SEAT / "probes").mkdir(parents=True, exist_ok=True)
shutil.copy2(PT / probe_rel, SEAT / "probes" / f"probe_{key}.py")
print(f"WROTE {key} {v} {rec['class']}")
