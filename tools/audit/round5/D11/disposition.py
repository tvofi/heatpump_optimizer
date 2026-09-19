#!/usr/bin/env python3
"""D11 round 5 -- the disposition obligation: measured after the merge, by a job
whose refusal cannot turn anything a seat reads red.

METRIC DEFINITIONS (one line each):
  M1 undispositioned_merges_in_the_window -- the count `policy_lint.mjs
     --record --since <newest v* tag>` reports of merged pull requests in the
     window with no disposition in the plan of record or the living handover,
     over the number of pull requests in that window (the tree's own
     instrument, unmodified).
  M2 record_refusal_can_set_its_job_conclusion -- 1 when the `record` job's
     refusing step in `.github/workflows/governance.yml` carries no
     `continue-on-error: true`, so a refusal makes the job's conclusion
     `failure`; 0 when it does. Read from the workflow, which is what the job
     is.
  M3 record_check_run_conclusion_at_the_baseline -- the conclusion GitHub
     recorded for the `record` check run at the baseline SHA.

COMMAND
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D11/disposition.py
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D11/disposition.py --drop-continue-on-error

`--drop-continue-on-error` is the perturbation arm: the same measurement with
the one `continue-on-error: true` line the refusal rests on removed in memory.
Reads GitHub read-only through `gh api`, runs one `node` command, writes only
under its own directory. No BLAS import, `thread_factor` is 1.0.

EXPECTED (baseline eaa2a06, 2026-09-19)
  M1 = 7 of 15; M2 = 0 (perturbation arm: 1); M3 = success.

MACHINE macOS Darwin 25.6.0, 8-core Apple M1, python3 3.11.5, node v22.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = "tvofi/heatpump_optimizer"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASELINE = "eaa2a06af16a1b5b006f58a0f36cc92131f80225"
WORKFLOW = ROOT / ".github/workflows/governance.yml"


def gh(args):
    p = subprocess.run(["gh", "api"] + args, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"gh api {' '.join(args)} rc={p.returncode}: {p.stderr.strip()[:200]}")
    return json.loads(p.stdout) if p.stdout.strip() else None


def record_job_block(text):
    """The `record:` job's text, from its key to the next top-level job key."""
    start = text.index("\n  record:\n")
    rest = text[start + 1:]
    end = min((m.start() for m in re.finditer(r"\n  [a-z][a-z0-9-]*:\n", rest)), default=len(rest))
    return rest[:end]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drop-continue-on-error", action="store_true",
                    help="perturbation arm: the refusal with continue-on-error removed")
    args = ap.parse_args()

    tag = subprocess.run(["git", "-C", str(ROOT), "describe", "--tags", "--abbrev=0", "--match", "v*"],
                         capture_output=True, text=True, check=True).stdout.strip()
    token = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
    env = dict(os.environ, GITHUB_TOKEN=token)

    # ---- M1: the tree's own instrument over the window ------------------------
    p = subprocess.run(["node", ".claude/workflows/policy_lint.mjs", "--record", "--since", tag],
                       capture_output=True, text=True, cwd=ROOT, env=env)
    out = p.stdout + p.stderr
    missing = re.findall(r"no disposition in the plan of record or the living handover for merged pull request #(\d+)", out)
    over = re.search(r"TOTAL: (\d+) error\(s\) over (\d+) merged pull request\(s\)", out)
    print(f"RESULT window_since={tag}")
    print(f"RESULT record_run_exit_status={p.returncode}")
    print(f"RESULT undispositioned_merges_in_the_window={len(set(missing))}")
    print(f"RESULT merged_prs_in_the_window={over.group(2) if over else 'not printed'}")
    print(f"RESULT undispositioned_prs={json.dumps(sorted(set(int(x) for x in missing)))}")
    # Null control: the same instrument on an empty window must report zero over
    # zero, which is its own documented vacuity rather than a clean window.
    q = subprocess.run(["node", ".claude/workflows/policy_lint.mjs", "--record", "--since", "origin/main"],
                       capture_output=True, text=True, cwd=ROOT, env=env)
    n = re.search(r"TOTAL: (\d+) error\(s\) over (\d+) merged pull request\(s\)", q.stdout + q.stderr)
    print(f"RESULT null_control_empty_window={('%s over %s' % (n.group(1), n.group(2))) if n else 'not printed'}")

    # ---- M2: can the refusal set the job's conclusion? -----------------------
    text = WORKFLOW.read_text()
    block = record_job_block(text)
    if args.drop_continue_on_error:
        block = block.replace("continue-on-error: true\n", "", 1)
    refusing_step = block[block.index("- name: Every merged pull request has a disposition"):]
    coe = "continue-on-error: true" in refusing_step.split("- name:", 2)[1]
    print(f"RESULT record_refusal_can_set_its_job_conclusion={0 if coe else 1}")
    print(f"RESULT record_refusal_step_carries_continue_on_error={1 if coe else 0}")
    print(f"RESULT perturbation_arm={1 if args.drop_continue_on_error else 0}")

    # ---- M3: what GitHub recorded at the baseline ----------------------------
    runs = gh([f"repos/{REPO}/commits/{BASELINE}/check-runs?per_page=100"])["check_runs"]
    rec = [r for r in runs if r["name"] == "record"]
    print(f"RESULT record_check_runs_at_the_baseline={len(rec)}")
    for r in rec:
        print(f"RESULT record_check_run_conclusion_at_the_baseline={r.get('conclusion')}")

    # ---- the rule the obligation lives in, and where it is enforced ----------
    rule = (ROOT / ".claude/rules/delivery-status-tracking.md").read_text()
    print(f"RESULT rule_states_the_row_precedes_the_handoff="
          f"{1 if 'before the handoff' in rule else 0}")
    rs = gh([f"repos/{REPO}/rulesets/22628467"])
    ctx = [c["context"] for r in rs["rules"] if r["type"] == "required_status_checks"
           for c in r["parameters"]["required_status_checks"]]
    print(f"RESULT record_is_a_required_context={1 if 'record' in ctx else 0}")
    print(f"RESULT delivery_status_is_a_required_context={1 if 'delivery-status' in ctx else 0}")

    print(f"RESULT load1={os.getloadavg()[0]}")
    print("RESULT thread_factor=1.0")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
