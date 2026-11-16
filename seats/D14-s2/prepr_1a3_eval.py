"""N-body-lint-bounce barrier (D14-s2, round 11): does prepr.sh --self-test's step-1a3 drive eval a parseable block?

Metric: syntax errors bash reports when the self-test's own extraction of step
1a3 (the `blk1a3=$(sed ...)` line of tools/pr/prepr.sh, read from the file and
run as written, never copied) is eval'd the way its `early_head` drive evals
it, for each stub arm rc (1 = refuse, 0 = null control); plus whether each arm
still reaches the verdict the self-test pins (refuse: exit 1 naming the line;
null: falls through). Key: bash's own stderr from the eval and the drive's
output, under tools/pr/prepr.sh at the export root.

Perturbation (``--anchor``): the extraction's end anchor moved from
`^# --- 1b0\\.` to the first line after step 1a3's `fi`
(`^# One interpreter resolution`) in memory -> syntax_errors 1 -> 0, both pins
unchanged.

Run: python3 dev/audit/rounds/round11/D14/s2/prepr_1a3_eval.py [--anchor]
Expected at 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: RESULT syntax_errors=1 (the null arm),
RESULT refuse_pin=1, RESULT null_pin=1, RESULT block_lines=N (exact; no timing).
"""
import os

for _threads in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_threads, "1")

import argparse
import re
import subprocess
import sys
import tempfile
import time

PREPR = "tools/pr/prepr.sh"

DRIVE = r'''
blk1a3=$(%s)
early_head() {
  local o r
  o=$( STUBRC=$1; rc=0; BASE=x
    head_arm() { echo "stub-head-line"; return "$STUBRC"; }
    step() { echo "STEP $1 $2 $3"; [ "$2" -eq 0 ] || rc=1; }
    summary_end() { :; }
    set -- "$BODY"
    eval "$blk1a3"; echo FELL-THROUGH ); r=$?
  echo "$r:$o"
}
echo "LINES $(printf '%%s\n' "$blk1a3" | wc -l)"
echo "ARM1 $(early_head 1 | tr '\n' ' ')"
echo "ARM0 $(early_head 0 | tr '\n' ' ')"
'''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--anchor", action="store_true")
    a = ap.parse_args()
    t0, c0 = time.thread_time(), time.process_time()
    src = open(PREPR, encoding="utf-8").read()
    m = re.search(r"^\s*blk1a3=\$\((sed .*)\)\s*$", src, re.M)
    assert m, "the self-test's blk1a3 extraction moved"
    ext = m.group(1).replace('"$PREPR_PATH"', f'"{PREPR}"')
    if a.anchor:
        ext = ext.replace(r"/^# --- 1b0\./", r"/^# One interpreter resolution/")
    print(f"# extraction: {ext}")
    with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as td:
        body = os.path.join(td, "wiring-body.md")
        open(body, "w").write("## Head\n")
        p = subprocess.run(["bash", "-c", DRIVE % ext], capture_output=True, text=True,
                           env=dict(os.environ, BODY=body, TMPDIR=td))
    out, err = p.stdout, p.stderr
    print(out.strip())
    for line in err.strip().splitlines():
        print(f"# stderr: {line}")
    errors = err.count("syntax error")
    arm1 = next((l for l in out.splitlines() if l.startswith("ARM1 ")), "")
    arm0 = next((l for l in out.splitlines() if l.startswith("ARM0 ")), "")
    lines = next((l.split()[1] for l in out.splitlines() if l.startswith("LINES ")), "?")
    print(f"RESULT block_lines={lines}")
    print(f"RESULT syntax_errors={errors}")
    print(f"RESULT refuse_pin={int(arm1.startswith('ARM1 1:') and 'stub-head-line' in arm1 and 'FELL-THROUGH' not in arm1)}")
    print(f"RESULT null_pin={int(arm0.startswith('ARM0 0:') and 'FELL-THROUGH' in arm0)}")
    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as f:
            print("RESULT swapins=" + next(l.split()[1] for l in f if l.startswith("pswpin")))
    except OSError:
        print("RESULT swapins=unknown")
    return 0


if __name__ == "__main__":
    sys.exit(main())
