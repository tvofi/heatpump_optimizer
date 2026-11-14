#!/usr/bin/env python3
"""Reviewer's mutation driver for PR #3547 at b4f8038e, round 4 (round 2 driver, head and output path changed) (reviewer-built, not the finder's).

Each mutant: a fresh detached worktree at the head, one exact text replacement
(asserted to match exactly once), then the named self-test. KILLED = non-zero rc
or a failed count > 0. Prints one RESULT line per mutant.
"""
import concurrent.futures as cf
import os
import re
import subprocess
import sys

REPO = "/home/user/heatpump_optimizer"
HEAD = "b4f8038e2e19e34c88008e0c768544b9442c3a82"
OUT = "/tmp/tmp.m3pXKqU35o/ev/mutants"
GP = "tools/pr/gate_priority.py"
PS = "tools/pr/prepr.sh"
GP_TEST = ["python3", GP, "--self-test"]
PS_TEST = ["bash", PS, "--self-test"]

MUTANTS = [
    ("G1-is_hotfix-eq-inverted", GP,
     "return _rank(branch, repo=repo, ref=ref, fetch=fetch) == roster_lib.RANK_HOTFIX",
     "return _rank(branch, repo=repo, ref=ref, fetch=fetch) != roster_lib.RANK_HOTFIX", GP_TEST),
    ("G2-unmapped-fails-open", GP,
     "        if group is None:\n            return None\n",
     "        if group is None:\n            return roster_lib.RANK_HOTFIX\n", GP_TEST),
    ("G3-except-fails-open", GP,
     "    except Exception:  # noqa: BLE001 -- a pre-pr helper must never crash a run\n        return None\n",
     "    except Exception:  # noqa: BLE001 -- a pre-pr helper must never crash a run\n        return roster_lib.RANK_HOTFIX\n", GP_TEST),
    ("G4-derived-drops-top", GP,
     "    return {roster_lib.RANK_HOTFIX: HOTFIX_PRIORITY,\n            roster_lib.RANK_TOP: TOP_PRIORITY}.get(rank, PRIORITY_NORMAL)",
     "    return {roster_lib.RANK_HOTFIX: HOTFIX_PRIORITY}.get(rank, PRIORITY_NORMAL)", GP_TEST),
    ("G5-cli-hotfix-inverted", GP,
     "print(int(is_hotfix(branch, repo=args.repo, ref=args.ref, fetch=not args.no_fetch)))",
     "print(int(not is_hotfix(branch, repo=args.repo, ref=args.ref, fetch=not args.no_fetch)))", GP_TEST),
    ("G5b-cli-hotfix-inverted-prepr", GP,
     "print(int(is_hotfix(branch, repo=args.repo, ref=args.ref, fetch=not args.no_fetch)))",
     "print(int(not is_hotfix(branch, repo=args.repo, ref=args.ref, fetch=not args.no_fetch)))", PS_TEST),
    ("P1-class-pred-inverted", PS,
     '  [ "$(hotfix_class "$1")" = 1 ] || return 0\n',
     '  [ "$(hotfix_class "$1")" != 1 ] || return 0\n', PS_TEST),
    ("P2-code-unset-test-dropped", PS,
     '  [ -n "${PREPR_SKIP_CODE+x}" ] || PREPR_SKIP_CODE=hotfix\n',
     '  PREPR_SKIP_CODE=hotfix\n', PS_TEST),
    ("P3-closures-unset-test-dropped", PS,
     '  [ -n "${PREPR_SKIP_CLOSURES+x}" ] || PREPR_SKIP_CLOSURES=1\n',
     '  PREPR_SKIP_CLOSURES=1\n', PS_TEST),
    ("P4-bothset-return-dropped", PS,
     '  if [ -n "${PREPR_SKIP_CODE+x}" ] && [ -n "${PREPR_SKIP_CLOSURES+x}" ]; then return 0; fi\n',
     '', PS_TEST),
    ("P5-scope-line-dropped", PS,
     '  say ok "hotfix scope" "$1 is a hotfix',
     '  : say ok "hotfix scope" "$1 is a hotfix', PS_TEST),
    ("P6-main-call-dropped", PS,
     'hotfix_scope "$(git rev-parse --abbrev-ref HEAD 2>/dev/null)"\n',
     '', PS_TEST),
    ("P7-HOTFIX_SCOPED-dropped", PS,
     '  HOTFIX_SCOPED=1\n',
     '', PS_TEST),
    ("P8-classifier-asks-priority", PS,
     '  python3 tools/pr/gate_priority.py --hotfix --branch "$1" 2>/dev/null\n',
     '  python3 tools/pr/gate_priority.py --branch "$1" 2>/dev/null\n', PS_TEST),
    ("P9r-export-readded", PS,
     '  [ -n "${PREPR_SKIP_CLOSURES+x}" ] || PREPR_SKIP_CLOSURES=1\n',
     '  [ -n "${PREPR_SKIP_CLOSURES+x}" ] || PREPR_SKIP_CLOSURES=1\n  export PREPR_SKIP_CODE PREPR_SKIP_CLOSURES\n', PS_TEST),
    ("P10-classifier-drops-branch", PS,
     '  python3 tools/pr/gate_priority.py --hotfix --branch "$1" 2>/dev/null\n',
     '  python3 tools/pr/gate_priority.py --hotfix 2>/dev/null\n', PS_TEST),
    ("P11-codesteps-drops-hotfix-eq", PS,
     '  if [ -n "${HOTFIX_SCOPED:-}" ] && [ "$1" = hotfix ]; then',
     '  if [ -n "${HOTFIX_SCOPED:-}" ]; then', PS_TEST),
    ("P12-codesteps-drops-scoped-test", PS,
     '  if [ -n "${HOTFIX_SCOPED:-}" ] && [ "$1" = hotfix ]; then',
     '  if [ "$1" = hotfix ]; then', PS_TEST),
    ("P13-main-uses-inline-receipt-line", PS,
     'code_steps_line "$REUSE"\n',
     '[ -z "$REUSE" ] || say ok "code steps" "reused from the receipt at ${REUSE:0:12}: no heavy slot, and the steps keyed to the code alone are dropped"\n', PS_TEST),
    ("G6-cli-ignores-ref", GP,
     "print(int(is_hotfix(branch, repo=args.repo, ref=args.ref, fetch=not args.no_fetch)))",
     "print(int(is_hotfix(branch, repo=args.repo, ref=None, fetch=not args.no_fetch)))", GP_TEST),
    ("NULL-comment-only", PS,
     '# A hotfix group\'s branch runs the scoped prepr by default',
     '# (null) A hotfix group\'s branch runs the scoped prepr by default', PS_TEST),
]


def run(m):
    name, path, old, new, cmd = m
    wt = f"/root/mut/wt-{name}"
    subprocess.run(["git", "-C", REPO, "worktree", "remove", "--force", wt], capture_output=True)
    subprocess.run(["git", "-C", REPO, "worktree", "add", "-q", "--detach", wt, HEAD], check=True)
    f = os.path.join(wt, path)
    src = open(f).read()
    n = src.count(old)
    if n != 1:
        return f"RESULT {name}: NOT-APPLIED (matches={n})"
    open(f, "w").write(src.replace(old, new))
    diff = subprocess.run(["git", "-C", wt, "diff", "--stat"], capture_output=True, text=True).stdout.strip()
    p = subprocess.run(cmd, cwd=wt, capture_output=True, text=True, timeout=1500)
    log = p.stdout + p.stderr
    open(os.path.join(OUT, name + ".log"), "w").write(f"cmd: {' '.join(cmd)}\ndiff: {diff}\nrc: {p.returncode}\n" + log[-20000:])
    m1 = re.search(r"(\d+) passed, (\d+) failed", log)
    m2 = re.search(r"(\d+) checks, (\d+) failed", log)
    failed = int((m1 or m2).group(2)) if (m1 or m2) else None
    killed = p.returncode != 0 or (failed or 0) > 0
    fails = [l.strip() for l in log.splitlines() if re.match(r"\s*(FAIL|not ok|FAILED)", l)][:6]
    subprocess.run(["git", "-C", REPO, "worktree", "remove", "--force", wt], capture_output=True)
    return f"RESULT {name}: {'KILLED' if killed else 'SURVIVED'} rc={p.returncode} failed={failed} {fails}"


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    sel = sys.argv[1:]
    ms = [m for m in MUTANTS if not sel or m[0] in sel]
    with cf.ThreadPoolExecutor(max_workers=int(os.environ.get("J", "4"))) as ex:
        for r in ex.map(run, ms):
            print(r, flush=True)
    print("DRIVER DONE", flush=True)
