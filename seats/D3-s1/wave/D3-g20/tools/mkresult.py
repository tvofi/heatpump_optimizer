#!/usr/bin/env python3
"""Box D3-g20: build results/<key>.json from gates/<key>.json, keys.tsv, the mutant record and (for a
SURVIVED / RED-AS-NULL gate) the key's probe, run now. Usage, from the tree root:
  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g20/tools/mkresult.py <key>
"""
import json, os, re, subprocess, sys
from pathlib import Path

S1 = Path("dev/audit/rounds/round11/D3/s1")
W = S1 / "wave" / "D3-g20"
META = json.loads((W / "tools" / "keymeta.json").read_text())
key = sys.argv[1]
row = dict(zip(*[l.split("\t") for l in (W / "keys.tsv").read_text().splitlines() if l.split("\t")[0] in ("key", key)]))
g = json.loads((W / "gates" / f"{key}.json").read_text())
mut = json.loads((S1 / "state" / "results" / "complete" / f"{key}.json").read_text())["mutant"]
m = META[key]
rec = {
    "key": key,
    "site": f"{row['file']}:{row['line']} {row['kind']}",
    "patch": f"{mut['old'].strip()} -> {mut['new'].strip()}",
    "function": row["function"], "cluster": row["cluster"], "slice": row["slice"], "fullnet": row["fullnet"],
    "m4_source": row["m4_source"],
    "gate": {k: g.get(k) for k in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end", "failed_scripts",
                                    "fail_lines", "cap_s", "note")} | {"record": str(W / "gates" / f"{key}.json"),
                                                                      "provisional": True, "nproc": 4,
                                                                      "cpu": "Intel(R) Xeon(R) Processor @ 2.10GHz"},
}
v = g.get("verdict")
probe = W / "probes" / f"probe_{key}.py"
cmd = f"PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 {probe}"
if v == "KILLED":
    rec["class"] = "killed"
    log = (W / "gates" / f"{key}.log").read_text(errors="replace").splitlines()
    rec["killed_lines"] = [l[:300] for l in log if re.match(r"\s+FAIL |>>> FAILED", l)][:40]
    rec["non_finding"] = {"claim": f"full gate kills {key} ({rec['site']}): {', '.join(g.get('killed_by') or [])}",
                          "command": "python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key " + key,
                          "value": f"verdict KILLED gate_rc {g.get('gate_rc')} killed_by {g.get('killed_by')}"}
elif v == "TIMEOUT":
    rec["class"] = "timeout"
    lp = W / "gates" / f"{key}.log"
    last = [l for l in lp.read_text(errors="replace").splitlines() if l.startswith(">>> ") or l.startswith("=== ")][-3:] if lp.exists() else []
    rec["timeout"] = {"cap_s": g.get("cap_s", 14400), "last_log_lines": last}
else:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    out = subprocess.run([sys.executable, str(probe)], capture_output=True, text=True, env=env)
    lines = [l for l in out.stdout.splitlines() if l.startswith("RESULT")]
    rec["probe"] = {"path": str(probe), "command": cmd, "rc": out.returncode, "result_lines": lines,
                    "baseline_value": m["baseline"], "mutant_value": m["mutant"], "inputs_tried": m["inputs"]}
    rec["class"] = m["class"]
    rec["should_fail"] = m["should_fail"]
    if m["class"] == "candidate":
        rec["finding"] = m["finding"] | {"step": "D3.M3", "scope": "D3-s1",
                                         "harness_paths": [str(S1 / "fullgate.py"), str(probe)],
                                         "evidence_command": cmd}
    else:
        rec["non_finding"] = {"claim": f"{key} ({rec['site']}) is an equivalent-candidate: {m['why']}",
                              "command": cmd, "value": "; ".join(lines[:3])}
(W / "results").mkdir(exist_ok=True)
(W / "results" / f"{key}.json").write_text(json.dumps(rec, indent=1) + "\n")
print(f"WROTE {key} {v} class={rec['class']}")
