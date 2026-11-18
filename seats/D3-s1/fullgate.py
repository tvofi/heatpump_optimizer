#!/usr/bin/env python3
# Metric: full-gate verdict of one mutant -- KILLED (run.sh exits non-zero and names
#   >=1 failing script that the null-control run did not fail) or SURVIVED (exit 0).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src <pre|c2|c3c6|...> --key <16-hex key>
#          PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py null
# Expected: null -> RESULT gate_rc=0 (the comment-only marker commit passes the full gate);
#   a mutant -> RESULT killed=0|1, tolerance exact (counts); wall is provisional.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-top6 (4 vCPU Xeon @ 2.30GHz).
# Instrumented symbol: the production line the mutant dict names (file:line old->new),
#   driven through the whole suite `GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=<baseline> GATE_JOBS=1 ./tests/run.sh`.
# Perturbation: the one-line mutant edit itself (null control: a trailing comment on the same file,
#   under which the verdict must be gate_rc=0; a mutant the gate kills moves killed 0 -> 1).
# Procedure (D3-top6 brief T2): apply the line in this worktree, commit it (HEAD leaves the baseline),
# take the gate_lock lease, run the gate, record, `git reset --hard <baseline>`, release the lease.
# Writes only state/gates/<key>.{json,log} under its own directory.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, json, re, subprocess, sys, time
from pathlib import Path

BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
STATE = HERE / "state"
GATES = STATE / "gates"
LABEL = "D3-s1-r11"


def sh(*a, check=True, **kw):
    return subprocess.run(a, cwd=ROOT, check=check, text=True, capture_output=True, **kw)


def load1():
    return float(Path("/proc/loadavg").read_text().split()[0])


def head():
    return sh("git", "rev-parse", "HEAD").stdout.strip()


def apply(m):
    p = ROOT / m["file"]
    lines = p.read_text().split("\n")
    i = int(m["line"]) - 1
    if lines[i] != m["old"]:
        raise SystemExit(f"REFUSE line {m['file']}:{m['line']} is {lines[i]!r}, not {m['old']!r}")
    lines[i] = m["new"]
    p.write_text("\n".join(lines))


def gate(key, mutant, msg):
    if head() != BASE:
        raise SystemExit(f"REFUSE HEAD {head()} is not the baseline")
    GATES.mkdir(parents=True, exist_ok=True)
    if mutant is None:  # null control: comment-only marker
        p = ROOT / "custom_components/heatpump_optimizer/tariff.py"
        p.write_text(p.read_text() + "# D3-s1 null-control marker\n")
        files = ["custom_components/heatpump_optimizer/tariff.py"]
    else:
        apply(mutant)
        files = [mutant["file"]]
    sh("git", "commit", "-q", "-m", msg, "--", *files)
    sh("python3", "tests/gate_lock.py", "take", "--label", LABEL, "--lease-seconds", "43200",
       "--owner-pid", str(os.getpid()))
    l0 = load1()
    t0 = time.time()
    c0 = os.times()
    env = dict(os.environ, GATE_SCOPE="full", GOLDEN_MODE="drift", GOLDEN_REF=BASE, GATE_JOBS="1")
    log = GATES / f"{key}.log"
    try:
        with open(log, "w") as fh:
            rc = subprocess.run(["./tests/run.sh"], cwd=ROOT, env=env, stdout=fh, stderr=subprocess.STDOUT).returncode
    finally:
        wall = time.time() - t0
        c1 = os.times()
        l1 = load1()
        sh("git", "reset", "-q", "--hard", BASE)
        sh("python3", "tests/gate_lock.py", "release", check=False)
    text = log.read_text(errors="replace")
    failed = sorted(set(re.findall(r"^>>> (?:FAILED|ENDED BEFORE ITS SUMMARY): ([^\n(]+?)\s*(?:\(|$)", text, re.M)))
    summary = [ln for ln in text.splitlines() if re.search(r"TEST SCRIPT\(S\)|ALL TEST SCRIPTS PASSED", ln)]
    rec = {"key": key, "mutant": mutant, "gate_rc": rc, "failed_scripts": failed, "summary": summary[-1:] ,
           "wall_s": round(wall, 1), "child_cpu_s": round((c1.children_user + c1.children_system) - (c0.children_user + c0.children_system), 1),
           "load1_start": l0, "load1_end": l1, "provisional": True, "baseline": BASE,
           "command": "GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=%s GATE_JOBS=1 ./tests/run.sh" % BASE}
    (GATES / f"{key}.json").write_text(json.dumps(rec, indent=1) + "\n")
    print(f"RESULT gate_rc={rc} code")
    print(f"RESULT failed_scripts={len(failed)} count")
    print(f"RESULT wall={wall:.0f} s")
    print("RESULT thread_factor=1.0 ratio")
    print(f"RESULT load1={l1}")
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "null"])
    ap.add_argument("--src")
    ap.add_argument("--key")
    a = ap.parse_args()
    if a.cmd == "null":
        rec = gate("null", None, "D3-s1 full-gate null control (comment-only marker)")
    else:
        m = json.loads((STATE / "results" / a.src / f"{a.key}.json").read_text())["mutant"]
        rec = gate(a.key, m, f"D3-s1 full-gate mutant {a.key} {m['file']}:{m['line']}")
        null = json.loads((GATES / "null.json").read_text()) if (GATES / "null.json").exists() else {"failed_scripts": []}
        new = sorted(set(rec["failed_scripts"]) - set(null["failed_scripts"]))
        rec["killed_by"] = new
        rec["verdict"] = "KILLED" if (rec["gate_rc"] != 0 and new) else ("SURVIVED" if rec["gate_rc"] == 0 else "RED-AS-NULL")
        (GATES / f"{a.key}.json").write_text(json.dumps(rec, indent=1) + "\n")
        print(f"RESULT killed={int(rec['verdict'] == 'KILLED')} count")
        print(f"VERDICT {a.key} {rec['verdict']} {','.join(new)}")


if __name__ == "__main__":
    sys.exit(main())
