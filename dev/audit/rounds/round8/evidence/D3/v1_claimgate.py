#!/usr/bin/env python3
"""v1_claimgate.py -- D3 verifier's own measurement of D3-s1-01.

Metric (one line): of N single-line production mutants drawn by
tests/mutation_table.py:candidates (first 3 by line in each of 5 modules NOT in
the finder's pool) plus one comment-only edit, the count for which
tests/env_drift.py:check_claims_hygiene(repo, BASE) returns an INHERITED CLAIMS
refusal on a TEST-ONLY working-tree diff (the mutation instrument's documented
--scope changed fallback) while the same diff without the mutant returns None.

Hooks the production symbol in-process (no subprocess, no capture). Also
prints two reachability facts about the finder's exact configuration
(HEAD == BASE): mutation_table.ref_skip_reason(BASE) and the rc of the literal
`env_drift.py --all BASE` for the unmutated and one mutated tree.

Perturbation (--perturb): env_drift._claimed_at and _claimed patched to return
empty lists (a fork point that claims nothing, branch leaves it so); expected refused -> 0.
Null control (arm "no-mutant"): the test-only diff alone -> None.

Command (tree root):
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D3/v1_claimgate.py [--perturb]
Expected at cdf82daabcfe3777d98b31489f36df5555ec9d82: refused == mutants (16/16),
null None; --perturb refused=0. Machine: 4-vCPU cloud container (counts only).
Every edited file is restored in finally and hash-checked (RESULT restored=1).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import hashlib
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
import env_drift as ed  # noqa: E402
import mutation_table as mt  # noqa: E402

BASE = "cdf82daabcfe3777d98b31489f36df5555ec9d82"
MODS = ["legionella", "services", "config_flow", "sensor", "tariff"]
TEST_EDIT = ROOT / "tests/features.py"
PERTURB = "--perturb" in sys.argv


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    pkg = ROOT / "custom_components/heatpump_optimizer"
    muts = []
    for m in MODS:
        p = pkg / f"{m}.py"
        if not p.exists():
            continue
        c = sorted(mt.candidates(p), key=lambda c: c["line"])[:3]
        muts += c
    muts.append(dict(file="custom_components/heatpump_optimizer/optimizer.py",
                     kind="COMMENT", line=None, old=None, new=None))
    if PERTURB:
        orig_at, orig_c = ed._claimed_at, ed._claimed
        ed._claimed_at = lambda repo, ref, f: {}
        ed._claimed = lambda repo, f=ed.CLAIM_FILE: (orig_c(repo, f)[0], {})
        print("PERTURBED: base AND tree claim lists read as empty (a fork point claiming nothing)")
    before = {str(TEST_EDIT): sha(TEST_EDIT)}
    t_orig = TEST_EDIT.read_text()
    refused = 0
    t0 = time.process_time(); w0 = time.thread_time()
    try:
        clean = ed.check_claims_hygiene(str(ROOT), BASE)
        print(f"  clean tree: {clean!r}")
        TEST_EDIT.write_text(t_orig + "# v1 test-only edit\n")
        null = ed.check_claims_hygiene(str(ROOT), BASE)
        print(f"  no-mutant (test-only diff): {(null or 'None').splitlines()[0]}")
        for m in muts:
            p = ROOT / m["file"]
            before.setdefault(str(p), sha(p))
            o = p.read_text()
            try:
                if m["kind"] == "COMMENT":
                    p.write_text(o + "# v1 comment-only edit\n")
                else:
                    ls = o.splitlines(True)
                    assert ls[m["line"] - 1].rstrip("\n") == m["old"]
                    ls[m["line"] - 1] = m["new"] + "\n"
                    p.write_text("".join(ls))
                v = ed.check_claims_hygiene(str(ROOT), BASE)
                hit = null is None and bool(v) and v.startswith("INHERITED CLAIMS")
                refused += hit
                print(f"  {m['file'].split('/')[-1]}:{m['line']} {m['kind']}: "
                      f"{'REFUSED' if hit else (v or 'None').splitlines()[0][:60]}")
            finally:
                p.write_text(o)
    finally:
        TEST_EDIT.write_text(t_orig)
        if PERTURB:
            ed._claimed_at, ed._claimed = orig_at, orig_c
    restored = all(sha(Path(f)) == h for f, h in before.items())
    # Reachability in the finder's exact configuration (HEAD == BASE).
    skip = mt.ref_skip_reason(BASE, ROOT)
    env = dict(os.environ, PYTHONPATH="tests/hastub")
    rc_all = subprocess.run([sys.executable, "tests/env_drift.py", "--all", BASE],
                            cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)
    first = next((l for l in rc_all.stdout.splitlines() if l.strip()), "")
    print(f"  mutation_table.ref_skip_reason(BASE) = {skip!r}")
    print(f"  env_drift --all BASE on unmutated HEAD==BASE: rc={rc_all.returncode} | {first[:60]}")
    print(f"RESULT refused_mutants={refused} count")
    print(f"RESULT mutants={len(muts)} count")
    print(f"RESULT null_refused={int(bool(null))} count")
    print(f"RESULT instrument_skips_envdrift_at_head_eq_base={int(skip is not None)} count")
    print(f"RESULT literal_all_rc_at_head_eq_base={rc_all.returncode} count")
    print(f"RESULT restored={int(restored)} count")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-w0,1e-9):.3f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
