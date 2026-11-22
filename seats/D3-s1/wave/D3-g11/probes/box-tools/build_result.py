#!/usr/bin/env python3
"""Write box D3-g11's results/<key>.json from gates/<key>.json and the key's probe (run in the clean baseline checkout)."""
import json, os, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from meta import M, F

BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
TR = Path.home() / "audit-r11-D3-s1"
W = TR / "dev/audit/rounds/round11/D3/s1/wave/D3-g11"
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g11"
CLEAN = Path("/home/user/heatpump_optimizer")  # the same baseline, never the gate's tree
MACHINE = "box D3-g11: Linux x86_64, nproc 4, Intel Xeon Processor @ 2.10GHz, 16 GB, venv-ci CPython, alone on the box"
NULLCMD = f"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py null  ({REL}/gates/null.json, {REL}/gates/null-note.txt)"


def last_script(log):
    if not log.exists():
        return None
    names = re.findall(r"^#{10} (.+?) #{10}$", log.read_text(errors="replace"), re.M)
    return names[-1] if names else None


def probe(m):
    path = f"{REL}/probes/probe_{m['p']}.py"
    cmd = f"PYTHONPATH=tests/hastub python3 {path}"
    env = dict(os.environ, PYTHONPATH="tests/hastub")
    out = subprocess.run(["python3", str(W / "probes" / f"probe_{m['p']}.py")], cwd=CLEAN, env=env,
                         capture_output=True, text=True, timeout=600)
    lines = [ln for ln in out.stdout.splitlines() if ln.startswith("RESULT")]
    return path, cmd, lines, out.returncode


def main(key):
    m = M[key]
    g = json.loads((W / "gates" / f"{key}.json").read_text())
    v = g.get("verdict")
    site = f"{F}:{m['line']} {m['kind']}"
    rec = {"key": key, "site": site, "patch": f"{m['old']} -> {m['new']}", "function": m["fn"],
           "cluster": f"coordinator.py:{m['fn']}",
           "gate": {k: g.get(k) for k in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end",
                                          "failed_scripts", "fail_lines", "more_fails_than_null", "cap_s", "note")},
           "gate_record": f"{REL}/gates/{key}.json",
           "gate_command": f"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src {'pre' if key == 'dc6c13eca2ca1737' else 'complete'} --key {key}",
           "provisional": "wall and load1 are provisional (nproc 4, Intel Xeon @ 2.10GHz); the verdict is a count"}
    if v == "KILLED":
        log = (W / "gates" / f"{key}.log").read_text(errors="replace")
        rec["class"] = "killed"
        rec["killed_lines"] = [ln.strip() for ln in log.splitlines()
                               if re.match(r"^\s*FAIL ", ln) or re.match(r"^\s*\d+ of \d+ .*FAILED", ln) or ln.startswith(">>> FAILED")][:40]
        rec["should_fail"] = "n/a: the suite fails on it (" + ", ".join(g.get("killed_by") or []) + ")"
    elif v == "TIMEOUT":
        rec["class"] = "timeout"
        rec["last_script_running"] = last_script(W / "gates" / f"{key}.log")
        rec["should_fail"] = m["should"]
    else:
        path, cmd, lines, rc = probe(m)
        rec["probe"] = {"path": path, "command": cmd, "rc": rc, "results": lines}
        if rc != 0:
            raise SystemExit(f"probe {path} rc {rc}")
        rec["should_fail"] = m["should"]
        if m["moved"]:
            base = mut = None
            for ln in lines:
                mm = re.match(rf"RESULT {re.escape(m['mkey'])}_baseline=(\S+)", ln)
                if mm:
                    base = mm.group(1)
                    mt = re.search(r" mutant=(\S+)", ln)
                    mut = mt.group(1) if mt else mut
                mm2 = re.match(rf"RESULT {re.escape(m['mkey'])}_mutant=(\S+)", ln)
                if mm2:
                    mut = mut or mm2.group(1)
            nullv = next((ln for ln in lines if ln.startswith("RESULT null_moved=")), "")
            rec["probe"].update(baseline_value=base, mutant_value=mut, inputs_tried=lines)
            if base is None or mut is None or base == mut:
                raise SystemExit(f"{key}: probe did not move ({base} vs {mut})")
            rec["class"] = "candidate"
            rec["finding"] = {
                "title": m["title"], "claim": m["claim"], "step": "D3.M3", "scope": "D3-s1",
                "class_guess": "I1", "severity_claimed": m["sev"], "stop_rule_class": "bug",
                "metric_definition": m["metric"],
                "instrumented_symbol": f"custom_components.heatpump_optimizer.coordinator:{m['fn']}",
                "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", path],
                "evidence_command": cmd,
                "evidence": {"command": cmd, "harness_path": path, "value": mut, "baseline_value": base,
                             "baseline_sha": BASE, "machine": MACHINE, "tolerance": "exact", "cpu_or_wall": "n/a"},
                "perturbation": {"change": f"mutant {key} at {F}:{m['line']}: `{m['old']}` -> `{m['new']}`, applied in memory by the probe",
                                 "expected_direction": m["direction"], "observed_value": f"{base} -> {mut}"},
                "null_control": {"command": cmd, "value": nullv.replace("RESULT ", ""),
                                 "note": "the probe's null arm (inputs where both arms must agree); the full-gate null is " + NULLCMD},
                "gate_null_control": NULLCMD,
                "phenomenon_property": m["prop"],
                "seam_rule": f"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key {key}",
                "files": [F],
                "proposed_fix_scope": f"a check in the closure script named in should_fail that drives {m['fn']} on the probe's distinguishing input and asserts the baseline value",
                "should_have_failed": m["should"],
            }
        else:
            rec["class"] = "equivalent-candidate"
            rec["probe"]["inputs_tried"] = lines
    (W / "results" / f"{key}.json").write_text(json.dumps(rec, indent=1) + "\n")
    print(f"{key} {v} {rec['class']}")


if __name__ == "__main__":
    for k in sys.argv[1:]:
        main(k)
