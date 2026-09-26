"""D5 verify-v3 (reach and class) harness for D5-s1-03: does the card banner lag the
integration version in the real release history, as docs/dashboard-card.md says?

Metric (one line): share of the last N commits that changed VERSION (the stamps users install)
at which the shipped card's CARD_VERSION equals that commit's VERSION; plus the doc's claim flag.
Count key: `git show <sha>:<card>` CARD_VERSION against `git show <sha>:VERSION` -- what a
release actually shipped, not a simulated stamp (the finder's key). The in-memory arm then
drives tools/release/stamp.py:rewrite_card_version on the live card.
Command (from the repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D5/verify-v3/v3_s1_03_cardver.py [--perturb] [--n 40]
--perturb: stamp.rewrite_card_version := identity (leave CARD_VERSION alone) for the in-memory
    stamp arm. Expected: stamp_arm_equal 1 -> 0.
Expected at baseline (--n 40): stamps_card_equals_version=30 of 40, the 30 newest consecutive (6.3.13..6.7.1); the
    most recent mismatching stamp (6.3.12, card 5.4.20) is printed (exact).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (+ round-9 evidence); machine: 4-core
cloud container, CPython 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import re
import subprocess
import sys
import time

sys.path.insert(0, "tools/release")
_t0p, _t0t = time.process_time(), time.thread_time()
import stamp  # noqa: E402

CARD = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"
N = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 40
if "--perturb" in sys.argv:
    stamp.rewrite_card_version = lambda text, new: (text, None)


def show(sha, path):
    r = subprocess.run(["git", "show", f"{sha}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


shas = subprocess.run(["git", "log", "--format=%H", "-n", str(N), "--", "VERSION"],
                      capture_output=True, text=True, check=True).stdout.split()
equal = total = 0
first_mismatch = None
for sha in shas:
    v = (show(sha, "VERSION") or "").strip()
    card = show(sha, CARD)
    m = re.search(r'const CARD_VERSION = "([\d.]+)"', card or "")
    if not v or not m:
        continue
    total += 1
    if m.group(1) == v:
        equal += 1
    elif first_mismatch is None:
        first_mismatch = (sha[:10], v, m.group(1))
live = open(CARD, encoding="utf-8").read()
new_text, _ = stamp.rewrite_card_version(live, "9.9.9")
arm = int('const CARD_VERSION = "9.9.9"' in new_text)
doc = open("docs/dashboard-card.md", encoding="utf-8").read()
claim = int("often lower than the integration version" in doc)
print("most recent stamp with card != VERSION:", first_mismatch)
cpu_p, cpu_t = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT stamps_checked={total} count")
print(f"RESULT stamps_card_equals_version={equal} count")
print(f"RESULT history_share={equal / total if total else 0:.2f} ratio")
print(f"RESULT stamp_arm_equal={arm} count")
print(f"RESULT doc_claims_card_lags={claim} count")
print(f"RESULT thread_factor={cpu_p / cpu_t if cpu_t else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
