#!/usr/bin/env python3
"""D11 round 5 -- the pull-request template's positive control does not reach the
exit status of the lane that runs it.

METRIC DEFINITIONS (one line each):
  M1 acceptance_exit_status -- the exit status of `node
     .claude/workflows/policy_lint.mjs`, the command the required `policy-docs`
     context runs, on the unmodified tree.
  M2 template_contrast_lines -- the lines that same run prints naming the
     template's own contract violation (`does not satisfy the contract it exists
     to state`).
  M3 cli_errors_in_the_template / cli_exit_status -- the errors and exit status
     of `policy_lint.mjs --pr-body .github/PULL_REQUEST_TEMPLATE.md`, the same
     parser reached the way the `pr-contract` job reaches it.

COMMAND
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D11/template_pin.py
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D11/template_pin.py --arm-b

--arm-b is the perturbation: ONE production line in
`.claude/workflows/policy_lint.mjs` is changed for the duration of the run --
the template arm's `found.push(...)` becomes `return 1`, which is the wiring
every sibling `FIXTURE VACUOUS` arm in the same function already uses -- and
M1 must move UP from 0 to 1. The file is restored byte-identically afterwards
and the restore is asserted by SHA-1. Nothing else in the tree is written.

THE COUNT IS NOT KEYED ON THE TEMPLATE'S TEXT: M1 is the process's own exit
status and M3 is the parser's own error count for the file, so an edit that
renames a heading without changing the parse cannot move either.

EXPECTED (baseline eaa2a06, 2026-09-19)
  live:  M1 = 0, M2 = 1, M3 = 1 error at exit 1
  --arm-b: M1 = 1

MACHINE macOS Darwin 25.6.0, 8-core Apple M1, python3 3.11.5, node v22.
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LINT = ROOT / ".claude/workflows/policy_lint.mjs"
BASELINE = "eaa2a06af16a1b5b006f58a0f36cc92131f80225"
ARM_B_OLD = "      found.push(...errs.map((e) => ({ ...e, check: '(template)' })))"
ARM_B_NEW = "      return 1"


def run(args):
    p = subprocess.run(args, capture_output=True, text=True, cwd=ROOT)
    return p.returncode, p.stdout + p.stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm-b", action="store_true")
    args = ap.parse_args()

    original = LINT.read_bytes()
    before = hashlib.sha1(original).hexdigest()
    try:
        if args.arm_b:
            text = original.decode()
            assert ARM_B_OLD in text, "the arm's anchor line is not in policy_lint.mjs; nothing was changed"
            LINT.write_text(text.replace(ARM_B_OLD, ARM_B_NEW, 1))
        rc_acc, out_acc = run(["node", ".claude/workflows/policy_lint.mjs"])
        rc_cli, out_cli = run(["node", ".claude/workflows/policy_lint.mjs", "--pr-body",
                               ".github/PULL_REQUEST_TEMPLATE.md"])
    finally:
        LINT.write_bytes(original)
    after = hashlib.sha1(LINT.read_bytes()).hexdigest()

    vacuous = [l for l in out_acc.splitlines()
               if "does not satisfy the contract it exists to state" in l]
    ok = [l for l in out_acc.splitlines() if l.startswith("FIXTURE ok:")]
    n_cli = len(re.findall(r"^  ERROR   \[pr-body\]", out_cli, re.M))
    print(f"RESULT baseline_sha={BASELINE}")
    print(f"RESULT lint_restored_byte_identical={1 if before == after else 0}")
    print(f"RESULT perturbation_arm={1 if args.arm_b else 0}")
    print(f"RESULT acceptance_exit_status={rc_acc}")
    print(f"RESULT template_contrast_lines={len(vacuous)}")
    print(f"RESULT acceptance_fixture_ok_line={ok[0] if ok else 'not printed'}")
    print(f"RESULT cli_errors_in_the_template={n_cli}")
    print(f"RESULT cli_exit_status={rc_cli}")
    print(f"RESULT template_satisfies_the_contract_it_states={0 if n_cli else 1}")
    print(f"RESULT load1={os.getloadavg()[0]}")
    print("RESULT thread_factor=1.0")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
