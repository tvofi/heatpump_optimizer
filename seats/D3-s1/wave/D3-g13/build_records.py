#!/usr/bin/env python3
"""Box D3-g13: write results/<key>.json for every gated key of keys.tsv that has none yet.

Command: python3 dev/audit/rounds/round11/D3/s1/wave/D3-g13/build_records.py [--probe-root DIR] [--key K]
Runs each SURVIVED / RED-AS-NULL key's probe from a clean baseline worktree (--probe-root, default
$HOME/probe-tree: never the gate's tree, which holds a mutant on disk while a gate runs), captures its RESULT
lines, and joins them with the gate record (gates/<key>.json), the box's null (gates/null.json), the slice
box's carried M4 answer and this box's step-4 analysis (keyinfo.json).
"""
import argparse, json, os, re, shutil, subprocess, sys
from pathlib import Path

W = Path(__file__).resolve().parent
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g13"
S1 = W.parent.parent
TREE = S1.parents[4]
KEYS = [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()]
HDR, ROWS = KEYS[0], [dict(zip(KEYS[0], r)) for r in KEYS[1:] if r and r[0]]
INFO = json.loads((W / "keyinfo.json").read_text())
MACHINE = "box D3-g13: Linux x86_64, nproc 4, Intel Xeon @ 2.30GHz, 16 GB, venv-ci CPython, alone on the box"
PY = "/opt/hpo/venv-ci/bin/python3"


def m4(row):
    k = row["key"]
    for f in sorted(S1.glob(row["m4_source"].split("/")[-1])):
        d = json.loads(f.read_text())
        if isinstance(d, dict) and k in d:
            return d[k]
        if isinstance(d, list):
            for x in d:
                if isinstance(x, dict) and (x.get("key") == k or k in json.dumps(x)[:200]):
                    return x
        if isinstance(d, dict):
            for v in d.values():
                if isinstance(v, list):
                    for x in v:
                        if isinstance(x, dict) and x.get("key") == k:
                            return x
    return None


def run_probe(key, root):
    rel = f"{REL}/probes/probe_{key}.py"
    dst = Path(root) / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(W / "probes" / f"probe_{key}.py", dst)
    env = dict(os.environ, PYTHONPATH="tests/hastub")
    p = subprocess.run([PY, rel], cwd=root, env=env, capture_output=True, text=True, timeout=900)
    lines = [l for l in p.stdout.splitlines() if l.startswith("RESULT ")]
    return p.returncode, lines, p.stderr[-800:]


def grab(lines, spec):
    """spec 'metric' -> the value after 'metric='; 'metric|field' -> the value after 'field=' on the metric's line."""
    metric, _, field = spec.partition("|")
    val = r"(\([^)]*\)|\[[^\]]*\]|[^\s]+)"
    for l in lines:
        body = l[len("RESULT "):]
        if not body.startswith(metric):
            continue
        m = re.search((re.escape(field) + "=" if field else "^" + re.escape(metric) + r"\s*=\s*") + val, body)
        if m:
            return m.group(1)
    return None


def fail_lines(key):
    log = W / "gates" / f"{key}.log"
    if not log.exists():
        return []
    out, cur = [], None
    for ln in log.read_text(errors="replace").splitlines():
        m = re.match(r"^#+ (.+?) #+$", ln.strip())
        if m:
            cur = m.group(1)
        if re.match(r"^\s*FAIL\b", ln) or re.match(r"^\s*\d+ of \d+ .*FAILED", ln) or ln.startswith(">>> FAILED"):
            out.append(f"[{cur}] {ln.strip()}"[:300])
    return out[:60]


def last_script(key):
    log = W / "gates" / f"{key}.log"
    if not log.exists():
        return None
    last = None
    for ln in log.read_text(errors="replace").splitlines():
        m = re.match(r"^#+ (.+?) #+$", ln.strip())
        if m:
            last = m.group(1)
    return last


def record(row, root):
    key = row["key"]
    g = json.loads((W / "gates" / f"{key}.json").read_text())
    mut = json.loads((S1 / "state/results/complete" / f"{key}.json").read_text())["mutant"]
    info = INFO[key]
    verdict = g.get("verdict")
    rec = {
        "key": key,
        "site": f"{row['file'].split('/')[-1]}:{row['line']} {row['kind']}",
        "file": row["file"], "line": int(row["line"]),
        "patch": f"{mut['old'].strip()} -> {mut['new'].strip()}",
        "function": row["function"], "cluster": row["cluster"], "slice": row["slice"], "fullnet": row["fullnet"],
        "reach": row["reach"],
        "gate": {k: g.get(k) for k in ("verdict", "killed_by", "gate_rc", "failed_scripts", "wall_s", "child_cpu_s",
                                       "load1_start", "load1_end", "provisional", "command", "cap_s", "note")},
        "gate_record": f"{REL}/gates/{key}.json",
        "gate_command": f"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src {row['src']} --key {key}",
        "m4_carried": {"source": row["m4_source"], "answer": m4(row)},
    }
    if verdict == "KILLED":
        rec["class"] = "killed"
        rec["failing_checks"] = fail_lines(key)
        rec["should_fail"] = f"it does: {', '.join(g.get('killed_by') or [])}"
    elif verdict == "TIMEOUT":
        rec["class"] = "timeout"
        rec["timeout"] = {"cap_s": g.get("cap_s", 14400), "last_script_running": last_script(key)}
        rec["should_fail"] = info["should_fail"]
    else:
        rc, lines, err = run_probe(key, root)
        rec["class"] = info["class_if_survived"]
        rec["probe"] = {
            "path": f"{REL}/probes/probe_{key}.py",
            "command": f"PYTHONPATH=tests/hastub python3 {REL}/probes/probe_{key}.py",
            "rc": rc, "results": lines, "inputs_tried": info["inputs"],
            "baseline_value": grab(lines, info["baseline_line"]) if info.get("baseline_line") else None,
            "mutant_value": grab(lines, info["mutant_line"]) if info.get("mutant_line") else None,
            "load1": float(grab(lines, "load1") or 0), "thread_factor": float(grab(lines, "thread_factor") or 1),
        }
        if rc != 0:
            rec["probe"]["stderr_tail"] = err
        rec["should_fail"] = info["should_fail"]
        if info.get("reach_note"):
            rec["reach_note"] = info["reach_note"]
        if rec["class"] == "equivalent-candidate":
            rec["equivalence"] = info["equiv_reason"]
        else:
            pcmd = rec["probe"]["command"]
            rec["finding"] = {
                "title": info["title"], "claim": info["claim"].replace("survives the full gate",
                                                                      f"survives the full gate ({verdict})"),
                "step": "D3.M3", "scope": "D3-s1", "class_guess": info["class_guess"],
                "severity_claimed": info["severity"], "stop_rule_class": "hygiene",
                "metric_definition": info["metric_definition"],
                "phenomenon_property": info["phenomenon_property"],
                "seam_rule": "awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv (the wave list); this key's row",
                "instrumented_symbol": f"custom_components.heatpump_optimizer.{row['file'].split('/')[-1][:-3]}:{row['function']}",
                "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", rec["probe"]["path"]],
                "evidence_command": pcmd,
                "evidence": {"command": pcmd, "harness_path": rec["probe"]["path"],
                             "value": rec["probe"]["mutant_value"], "unit": info["metric_definition"],
                             "baseline_sha": "92d38ecb640bd462f2e19c0814d0f0b7df1ee692", "machine": MACHINE,
                             "cpu_or_wall": "n/a",
                             "contention_note": "deterministic value; probe ran on the box while its own full gates ran (GATE_JOBS=1)",
                             "tolerance": "exact", "load1": rec["probe"]["load1"],
                             "thread_factor": rec["probe"]["thread_factor"]},
                "perturbation": {"change": f"mutant {key} ({rec['patch']}) applied in memory by the probe; full gate: {rec['gate_command']}",
                                 "expected_direction": info["direction"],
                                 "observed_value": rec["probe"]["mutant_value"]},
                "null_control": {"command": pcmd, "note": info["null"]},
                "reproduction_steps": [pcmd, rec["gate_command"]],
                "proposed_fix_scope": info["proposed_fix_scope"], "files": info["files"],
                "mechanism": f"Check that should have failed (D3.M4): {info['should_fail']}"
                             + (f" Reach: {info['reach_note']}" if info.get("reach_note") else ""),
            }
    (W / "results").mkdir(exist_ok=True)
    (W / "results" / f"{key}.json").write_text(json.dumps(rec, indent=1) + "\n")
    return rec["class"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-root", default=os.path.expanduser("~/probe-tree"))
    ap.add_argument("--key")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    for row in ROWS:
        k = row["key"]
        if a.key and k != a.key:
            continue
        if not (W / "gates" / f"{k}.json").exists():
            continue
        if (W / "results" / f"{k}.json").exists() and not a.force:
            continue
        print(f"RECORD {k} {record(row, a.probe_root)}")


if __name__ == "__main__":
    main()
