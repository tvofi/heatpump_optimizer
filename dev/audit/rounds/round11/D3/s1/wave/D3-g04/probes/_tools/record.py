import json, re, subprocess, sys, os
from pathlib import Path
exec(open('/root/pgen/meta.py').read())
key = sys.argv[1]
TR = Path('/root/audit-r11-D3-s1'); S1 = TR / 'dev/audit/rounds/round11/D3/s1'; W = S1 / 'wave/D3-g04'
PT = Path('/root/probe-tree')
row = [l.split('\t') for l in (W / 'keys.tsv').read_text().splitlines()]
hdr = row[0]; row = dict(zip(hdr, [r for r in row if r[0] == key][0]))
g = json.loads((W / 'gates' / f'{key}.json').read_text())
mut = json.loads((S1 / 'state/results/complete' / f'{key}.json').read_text())['mutant']
m = META[key]
probe = f"{PD}/probe_{key}.py"
cmd = f"PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 {probe}"
# the probe runs from a clean baseline worktree, never the gate tree
(PT / PD).mkdir(parents=True, exist_ok=True)
src = Path('/root/d3wave-seat/wave/D3-g04/probes') / f'probe_{key}.py'
(PT / probe).write_text(src.read_text())
out = subprocess.run(["/opt/hpo/venv-ci/bin/python3", probe], cwd=PT, env={**os.environ, "PYTHONPATH": "tests/hastub"},
                     capture_output=True, text=True, timeout=600)
res = {}
for line in out.stdout.splitlines():
    mm = re.match(r"RESULT ([A-Za-z_0-9]+)=(.*)$", line)
    if mm:
        res[mm.group(1)] = mm.group(2)
(W / 'probes').mkdir(exist_ok=True)
(W / 'probes' / f'probe_{key}.out').write_text(out.stdout + (("\nSTDERR\n" + out.stderr) if out.returncode else ""))
v = g.get('verdict')
cls = {"KILLED": "killed", "TIMEOUT": "timeout"}.get(v, m["cls"])
rec = {
  "key": key,
  "site": f"{row['file']}:{row['line']} {row['kind']}",
  "patch": f"{mut['old'].strip()} -> {mut['new'].strip()}",
  "function": row['function'], "cluster": row['cluster'], "slice": row['slice'], "m4_source": row['m4_source'],
  "gate": {k: g.get(k) for k in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end", "failed_scripts", "child_cpu_s", "command")}
          | {"record": f"dev/audit/rounds/round11/D3/s1/wave/D3-g04/gates/{key}.json", "provisional": True,
             "machine": "nproc 4, Intel Xeon Processor @ 2.10GHz, 16 GB"},
  "class": cls,
}
if cls == "killed":
    log = (W / 'gates' / f'{key}.log')
    lines = [l for l in (log.read_text(errors='replace').splitlines() if log.exists() else []) if re.search(r"\bFAIL\b|FAILED", l)]
    rec["killed_lines"] = (g.get("fail_lines") or lines)[:40]
    rec["non_finding"] = f"KILLED by {', '.join(g.get('killed_by') or [])}: the full gate fails on this mutant ({cmd.split()[0]} not needed); gate_rc {g.get('gate_rc')}"
elif cls == "timeout":
    log = (W / 'gates' / f'{key}.log')
    last = [l for l in (log.read_text(errors='replace').splitlines() if log.exists() else []) if l.strip()]
    rec["timeout"] = {"cap_s": g.get("cap_s", 14400), "last_log_line": last[-1] if last else None}
if cls != "killed":
    rec["probe"] = {"path": probe, "command": cmd, "rc": out.returncode,
                    "baseline_value": f"{m['bm'][0]}={res.get(m['bm'][0])}", "mutant_value": f"{m['bm'][1]}={res.get(m['bm'][1])}",
                    "results": res, "inputs_tried": m["inputs"], "output": f"dev/audit/rounds/round11/D3/s1/wave/D3-g04/probes/probe_{key}.out"}
    rec["should_fail"] = m["should_fail"]
if cls == "candidate":
    rec["finding"] = {
      "title": m["title"], "claim": m["claim"], "step": "D3.M3", "scope": "D3-s1",
      "class_guess": m["class_guess"], "severity_claimed": m["severity"], "stop_rule_class": "bug",
      "metric_definition": m["metric"],
      "instrumented_symbol": f"custom_components.heatpump_optimizer.coordinator:{row['function']} ({row['file']}:{row['line']})",
      "harness_paths": [FG, probe],
      "evidence_command": cmd + f"  ;  {row['file']}:{row['line']} full gate: GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh via {FG} run --src complete --key {key}",
      "perturbation": m["pert"],
      "null_control": f"the probe's null arm (null_delta/null_differing RESULT = {res.get('null_delta', res.get('null_differing', res.get('null_warnings_delta')))}) and this box's fullgate.py null gate (gates/null.json)",
    }
(W / 'results' / f'{key}.json').write_text(json.dumps(rec, indent=1, default=str))
print(key, v, cls, rec.get("probe", {}).get("baseline_value"), rec.get("probe", {}).get("mutant_value"), "probe_rc", out.returncode)
