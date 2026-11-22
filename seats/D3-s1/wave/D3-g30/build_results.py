#!/usr/bin/env python3
# Box D3-g30's step-3 record writer (not a harness): for every key of keys.tsv whose gate record gates/<key>.json
# exists and whose results/<key>.json does not, write results/<key>.json from the gate record, the key's probe run
# afresh from a clean baseline worktree (PROBE_TREE, default $HOME/probe-base; never the gate's tree, which carries
# the mutant while a gate runs) and key_meta.json (class, step-4 answer, should_fail).
# Command: python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/build_results.py [--force KEY]
import json, os, re, subprocess, sys
from pathlib import Path

W = Path(__file__).resolve().parent
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g30"
S1 = W.parent.parent
TREE = Path(os.environ.get("PROBE_TREE", str(Path.home() / "probe-base")))
PY = "/opt/hpo/venv-ci/bin/python3"
meta = json.loads((W / "key_meta.json").read_text())
rows = [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()]
hdr, rows = rows[0], [dict(zip(rows[0], r)) for r in rows[1:] if r and r[0]]
force = sys.argv[2:] if sys.argv[1:2] == ["--force"] else []


def probe(key):
    rel = f"{REL}/probes/probe_{key}.py"
    dst = TREE / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text((W / "probes" / f"probe_{key}.py").read_text())
    dirty = subprocess.run(["git", "-C", str(TREE), "status", "--short", "custom_components"], capture_output=True, text=True).stdout
    assert not dirty.strip(), f"probe tree not clean: {dirty}"
    out = subprocess.run([PY, rel], cwd=TREE, env={**os.environ, "PYTHONPATH": "tests/hastub"}, capture_output=True, text=True, timeout=600)
    res = {}
    for line in out.stdout.splitlines():
        m = re.match(r"RESULT (\S+?)=(.*)$", line)
        if m:
            res[m.group(1)] = m.group(2)
    return f"PYTHONPATH=tests/hastub {PY} {rel}", res


def fail_lines(key, scripts):
    log = W / "gates" / f"{key}.log"
    if not log.exists():
        return []
    lines = [l for l in log.read_text(errors="replace").splitlines() if re.search(r"\bFAIL", l)]
    return [l[:300] for l in lines if not scripts or any(s.split("/")[-1].split(".")[0] in l for s in scripts)][:40] or lines[:40]


for r in rows:
    key = r["key"]
    g = W / "gates" / f"{key}.json"
    out = W / "results" / f"{key}.json"
    if not g.exists() or (out.exists() and key not in force):
        continue
    gate = json.loads(g.read_text())
    mut = json.loads((S1 / "state/results/complete" / f"{key}.json").read_text())["mutant"]
    v = gate.get("verdict")
    rec = {"key": key, "site": f"{r['file']}:{r['line']} {r['kind']}", "patch": f"{mut['old'].strip()} -> {mut['new'].strip()}",
           "function": r["function"], "cluster": r["cluster"], "slice": r["slice"], "m4_source": r["m4_source"],
           "gate": {k: gate.get(k) for k in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end", "failed_scripts",
                                              "more_fails_than_null", "command", "cap_s")} | {"record": f"{REL}/gates/{key}.json",
                                                                                        "provisional_timing": True}}
    if v == "KILLED":
        rec["class"] = "killed"
        rec["killed_fail_lines"] = fail_lines(key, gate.get("killed_by") or [])
        rec["non_finding"] = {"claim": f"{rec['site']} mutant is killed by the full gate ({', '.join(gate.get('killed_by') or [])})",
                              "command": gate.get("command"), "value": f"gate_rc={gate.get('gate_rc')} killed_by={gate.get('killed_by')}"}
    elif v == "TIMEOUT" or v is None:
        rec["class"] = "timeout"
        log = W / "gates" / f"{key}.log"
        last = [l for l in log.read_text(errors="replace").splitlines() if re.search(r"tests/\w+\.(py|mjs|sh)", l)][-1:] if log.exists() else []
        rec["timeout"] = {"cap_s": gate.get("cap_s", 14400), "last_script_line": last[0][:300] if last else None}
    else:
        m = meta[key]
        cmd, res = probe(key)
        rec["class"] = m["cls"]
        rec["probe"] = {"path": f"{REL}/probes/probe_{key}.py", "command": cmd,
                        "baseline": {p: res.get(f"{p}_baseline") for p in m["pick"]},
                        "mutant": {p: res.get(f"{p}_mutant") for p in m["pick"]},
                        "moved": {k: v2 for k, v2 in res.items() if k.endswith("_inputs_moved")},
                        "null_delta": res.get("null_delta"), "inputs_tried": res.get("inputs_tried"),
                        "all_results": res}
        rec["step4_answer"] = m["claim"]
        rec["should_fail"] = m["should_fail"]
        if m["cls"] == "candidate":
            rec["finding"] = {
                "title": m["title"], "claim": m["claim"], "step": "D3.M3", "scope": "D3-s1", "class_guess": "I1",
                "severity_claimed": m["sev"], "stop_rule_class": "bug",
                "metric_definition": (W / "probes" / f"probe_{key}.py").read_text().splitlines()[1].lstrip("# ").removeprefix("Metric: "),
                "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", f"{REL}/probes/probe_{key}.py"],
                "evidence_command": cmd + f"  &&  python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key {key}",
                "instrumented_symbol": f"custom_components.heatpump_optimizer.price_model ({r['function']}), {r['file']}:{r['line']}",
                "perturbation": f"the one-line mutant {key}: `{mut['old'].strip()}` -> `{mut['new'].strip()}`; direction "
                                + "; ".join(f"{p}: {res.get(p + '_baseline')} -> {res.get(p + '_mutant')}" for p in m["pick"]),
                "null_control": f"the probe's null_* inputs (null_delta={res.get('null_delta')}) and the box's full-gate null "
                                f"({REL}/gates/null.json); gate verdict {v}"}
        else:
            rec["non_finding"] = {"claim": m["claim"], "command": cmd,
                                  "value": "; ".join(f"{p}: {res.get(p + '_baseline')} -> {res.get(p + '_mutant')}" for p in m["pick"])}
    out.write_text(json.dumps(rec, indent=1) + "\n")
    print(f"WROTE {key} {v} {rec['class']}")
