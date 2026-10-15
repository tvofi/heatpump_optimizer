"""delta_S of each ARCH2-s3 patch, alone and in union, on main and on main + ARCH-s2's 99_combined.

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s3/run_scores.py [label ...]

Run from the repository root. Every counter on (ARCHSCORE_ABLATE must be unset; harness.py refuses
otherwise). Each line is harness.py's own output, filtered to the verdict, the moved metrics and the
revert-to-zero perturbation.
"""
import os
import re
import subprocess
import sys

BASE = "9061fbd3d"
D = "dev/audit/rounds/round10/D7/arch2-s3"
P = f"{D}/patches"
S2 = f"{P}/s2_99_combined.patch"
T1 = f"{P}/01_tariff_one_topk_rule.patch"
T1B = f"{P}/01b_tariff_one_plateau_rule_scalar_bisection_kept.patch"
T2 = f"{P}/02_slot_floor_owner.patch"
T3 = f"{P}/03_state_power_kw.patch"
T3S2 = f"{P}/03s2_state_power_kw_on_s2.patch"
SETS = [
    ("01_tariff", [T1], [T1]),
    ("01b_tariff_kept_bisection", [T1B], [T1B]),
    ("02_slot_floor", [T2], [T2]),
    ("03_power_kw", [T3], [T3S2]),
    ("union", [T1, T2, T3], [T1, T2, T3S2]),
    ("union_b", [T1B, T2, T3], [T1B, T2, T3S2]),
]
KEEP = re.compile(r"^Architecture|^  [a-z_]+ \d|RESULT (delta_S|admissible|perturbed)")


def run(pre, patches):
    cmd = [sys.executable, f"{D}/harness.py", "--base", BASE, *sum((["--pre", p] for p in pre), []), *patches]
    out = subprocess.run(cmd, capture_output=True, text=True, env=dict(os.environ)).stdout
    return "\n".join(ln for ln in out.splitlines() if KEEP.search(ln))


for label, on_main, on_s2 in SETS:
    if len(sys.argv) > 1 and label not in sys.argv[1:]:
        continue
    print(f"== {label} on main\n{run([], on_main)}", flush=True)
    print(f"== {label} on main+ARCH-s2\n{run([S2], on_s2)}", flush=True)
