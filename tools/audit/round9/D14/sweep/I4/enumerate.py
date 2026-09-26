#!/usr/bin/env python3
"""D14 round-9 class sweep, class I4 (round9/sweep/S4):
"Two independent parsers or definitions of one concept disagree."

Four of I4's five round-9 findings have offline whole-package harnesses,
re-run verbatim below. The fifth (D13-s1-01) needs a live origin/main tip
matching its window.json.gz snapshot (the snapshot only covers commits up to
the round-9 baseline, and mainRef() in policy_lint.mjs resolves to the live
remote-tracking origin/main, not HEAD) -- its recorded numbers are cited from
tools/audit/round9/D13/s1/REPORT.md instead; see SWEEP.md "network exposure".

COMMAND: PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/I4/enumerate.py
BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
"""
import subprocess

PY_FINDINGS = [
    ("D7-s3-02", ["python3", "tools/audit/round9/D7/s3/screen.py", "--no-property-exclusion", "--attribute-only"],
     "structure.py dead_methods reads 0 while 9-11 members are dead"),
    ("D14-s2-03", ["python3", "tools/audit/round9/D14/s2/i4_roster.py", "--seams"],
     "class roster and finding grammar have disagreeing readers"),
]
NODE_FINDINGS = [
    ("D11-s1-71", ["node", "tools/audit/round9/D11/leads/l3_frontmatter_parsers.mjs"],
     "rules_sync vs policy_lint disagree on 2 of 6 legal frontmatter paths: shapes"),
]


def run(cmd, timeout=90):
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return out.stdout + out.stderr
    except subprocess.TimeoutExpired as exc:
        return f"TIMEOUT: {exc}"


def gov_pin_probe():
    """D11-s1-72: entities.py's GOV pin reads governance.yml only."""
    return run(["python3", "tools/audit/round9/D11/leads/l3_gov_pin.py"])


def main():
    for fid, cmd, claim in PY_FINDINGS:
        print(f"== {fid}: {claim} ==")
        print(run(cmd)[-800:])
    for fid, cmd, claim in NODE_FINDINGS:
        print(f"== {fid}: {claim} ==")
        print(run(cmd)[-800:])
    print("== D11-s1-72: entities.py GOV pin reads governance.yml only ==")
    print(gov_pin_probe()[-800:])
    print("== D13-s1-01: CITED (needs live origin/main; see SWEEP.md) ==")
    print("stats_window_merges=201 subject_merges=253 gap=52 gap_marked=0 "
          "(tools/audit/round9/D13/s1/REPORT.md)")


if __name__ == "__main__":
    main()
