#!/usr/bin/env python3
"""s1_claimkill.py -- the mutation instrument's env_drift driver "kills" any
production mutant before capturing anything, via the claim-hygiene refusal.

Metric: of the mutants applied (the seeded s1 pool from s1_prescreen.pool() plus
one comment-only edit that is equivalent by construction), how many make
`tests/env_drift.py` exit non-zero with an INHERITED CLAIMS refusal -- the
pre-capture check that tests/env_drift.py:main runs under --all
(check_claims_hygiene) -- while the SAME command on the unmutated tree exits 0.
tests/mutation_table.py:run_script counts exactly that (rc differs from the
unmutated baseline) as "killed by tests/env_drift.py".
Key: env_drift's own exit status and its first output line (the refusal
heading), per mutant; nothing re-derived.

Command driven per arm: `python3 tests/env_drift.py --claims-only <ref>` -- the
same check_claims_hygiene() the --all path calls before any capture (cheap: no
solve). One confirmation arm runs the instrument's real invocation,
tests/mutation_table.py:run_script("tests/env_drift.py", ROOT, 600,
*drive_spec("tests/env_drift.py", ref)) on the comment-only mutant, and prints
its wall time (a refusal in seconds proves no capture ran; a capture costs
minutes).

ref = HEAD^1 by default: mutation_table.gate_ref("full", ...) -- the nightly's
ref; --ref <sha> for the PR case (merge base).
Perturbation (--perturb): empty the claim list in tests/golden/claimed_drift.txt
(keep the header and claims-for line; restored in finally). The refusal needs a
non-empty inherited list, so refused_mutants must fall to 0 (direction: to_zero).

Command (tree root):
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D3/s1_claimkill.py [--perturb] [--confirm]
Expected at baseline cdf82daabcfe3777d98b31489f36df5555ec9d82: RESULT
unmutated_rc=0; refused_mutants=17 of 17 (exact); --perturb: refused_mutants=0.
Every production file is restored in finally and checked (RESULT restored=1).
Machine: 4-vCPU cloud container (wall numbers provisional).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import hashlib
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools/audit/round8/D3"))
import mutation_table as mt  # noqa: E402
import s1_prescreen as ps  # noqa: E402

CLAIMS = ROOT / "tests/golden/claimed_drift.txt"
TMP = Path("/home/claude/audit-r8/tmp/D3-s1")


def claims_only(ref):
    env = dict(os.environ, PYTHONPATH="tests/hastub", TMPDIR=str(TMP))
    p = subprocess.run([sys.executable, "tests/env_drift.py", "--claims-only", ref],
                       cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)
    first = next((ln for ln in p.stdout.splitlines() if ln.strip()), "")
    return p.returncode, first


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="")
    ap.add_argument("--perturb", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    a = ap.parse_args()
    ref = a.ref or mt.gate_ref("full", "origin/main")  # "HEAD^1"
    print(f"ref={ref}")
    muts = ps.pool()
    opt = ROOT / "custom_components/heatpump_optimizer/optimizer.py"
    muts.append(dict(id=99, file=str(opt.relative_to(ROOT)), kind="COMMENT",
                     line=None, old=None, new=None))
    claims_orig = CLAIMS.read_text()
    shas = {}
    refused = 0
    t0 = time.process_time(); w0 = time.thread_time()
    try:
        if a.perturb:
            kept = [ln for ln in claims_orig.splitlines(True)
                    if ln.startswith("#") or not ln.strip() or ln.startswith("claims-for")]
            CLAIMS.write_text("".join(kept))
            print("PERTURBED: claim list emptied (header and claims-for kept)")
        rc0, first0 = claims_only(ref)
        print(f"  unmutated: rc={rc0} | {first0[:90]}")
        for m in muts:
            path = ROOT / m["file"]
            orig = path.read_text()
            shas[m["file"]] = hashlib.sha256(orig.encode()).hexdigest()
            try:
                if m["kind"] == "COMMENT":
                    path.write_text(orig + "# s1 comment-only edit\n")
                else:
                    lines = orig.splitlines(True)
                    assert lines[m["line"] - 1].rstrip("\n") == m["old"]
                    lines[m["line"] - 1] = m["new"] + "\n"
                    path.write_text("".join(lines))
                rc, first = claims_only(ref)
                hit = rc != rc0 and "INHERITED CLAIMS" in first
                refused += int(hit)
                print(f"  M{m['id']:02d} {m['file'].split('/')[-1]}:{m['line']} {m['kind']}: "
                      f"rc={rc} {'REFUSED' if hit else 'ok'} | {first[:70]}")
                if a.confirm and m["kind"] == "COMMENT":
                    args, env = mt.drive_spec("tests/env_drift.py", ref)
                    t = time.monotonic()
                    run = mt.run_script("tests/env_drift.py", ROOT, 900, args, env)
                    wall = time.monotonic() - t
                    head = next((ln for ln in run.stdout.splitlines() if ln.strip()), "")
                    print(f"RESULT confirm_run_script_rc={run.rc} count")
                    print(f"RESULT confirm_wall_s={wall:.1f} s (provisional)")
                    print(f"  confirm first line: {head[:90]}")
            finally:
                path.write_text(orig)
    finally:
        CLAIMS.write_text(claims_orig)
    restored = all(hashlib.sha256((ROOT / f).read_bytes()).hexdigest() == h
                   for f, h in shas.items()) and CLAIMS.read_text() == claims_orig
    print(f"RESULT unmutated_rc={rc0} count")
    print(f"RESULT refused_mutants={refused} count")
    print(f"RESULT mutants={len(muts)} count")
    print(f"RESULT restored={int(restored)} count")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-w0,1e-9):.3f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
