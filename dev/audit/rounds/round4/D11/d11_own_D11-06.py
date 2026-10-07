#!/usr/bin/env python3
"""VERIFIER-OWN harness for D11-06 (round 4, verifier seat 1).

METRIC (my own definition):
  stats_would_open     -- issues the `--stats` friction histogram says it
                          WOULD open, run LIVE with a token over --since v6.4.1.
  stats_blocked_count  -- the histogram's `blocked` verdict-class count and the
                          printed threshold, parsed from the output.
  stats_exit_code      -- rc of the --stats run (0 = opens nothing, cannot fail).
  sunset_or_true       -- 1 when governance.yml wires --sunset under `|| true`.
  stats_or_true        -- 1 when governance.yml wires --stats under `|| true`.
  search_recurring     -- total_count of `search/issues` for "recurring
                          friction" in this repository (has the detector ever
                          opened its issue?).
  obligation_mentions  -- lines in the ROLE CONTRACTS (tools/audit/briefs/*.md,
                          excluding the D11 brief itself and round evidence)
                          obliging a seat to READ or ACT ON --stats/--sunset
                          output.
  corpus_headroom      -- tokens of headroom from `policy_lint --budgets`
                          (corpus tokens minus cap; negative impossible, 0 =
                          zero headroom).

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub GITHUB_TOKEN=$(gh auth token) \
    python3 tools/audit/round4/D11/d11_own_D11-06.py

EXPECTED (tolerance: exact; live window grows with merges):
  stats_would_open=1 stats_blocked_count>=3 stats_exit_code=0
  stats_or_true=1 sunset_or_true=1 search_recurring=0 obligation_mentions=0
  corpus_headroom=0
MACHINE: verifier seat 1 worktree audit-r4-verify-D11-1, 2026-09-12.

PERTURBATION. Post a real "[policy] recurring friction" issue and
search_recurring must rise to 1 — NOT RUN: read-only stance. The executed
perturbation is instead on the histogram itself: set --since to the older tag
v6.4.0 and the blocked count must move (a window-derived number, not a
constant).
"""

import json
import os
import re
import subprocess
import sys

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                      capture_output=True, text=True).stdout.strip()
REPO = "tvofi/heatpump_optimizer"


def sh(cmd, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=e)
    return p.returncode, p.stdout + p.stderr


def main():
    tok = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()
    env = {"GITHUB_TOKEN": tok}

    rc, out = sh(["node", ".claude/workflows/policy_lint.mjs", "--stats",
                  "--since", os.environ.get("D11_OWN_SINCE", "v6.4.1")], env)
    would = re.search(r"WOULD OPEN: (\d+) issue", out)
    blocked = re.search(r"^\s+(\d+)\s+blocked", out, re.M)
    thresh = re.search(r"threshold: (\d+)", out)
    print(f"--stats rc={rc}; would_open={would.group(1) if would else '?'}; "
          f"blocked={blocked.group(1) if blocked else '?'}; "
          f"threshold={thresh.group(1) if thresh else '?'}")

    rc2, out2 = sh(["node", ".claude/workflows/policy_lint.mjs", "--stats",
                    "--since", "v6.4.0"], env)
    blocked2 = re.search(r"^\s+(\d+)\s+blocked", out2, re.M)
    print(f"perturbation --since v6.4.0: blocked={blocked2.group(1) if blocked2 else '?'} "
          f"(must differ from the v6.4.1 window)")

    gov = open(os.path.join(ROOT, ".github/workflows/governance.yml"), encoding="utf-8").read()
    stats_ot = bool(re.search(r"policy_lint\.mjs --stats[^\n]*\|\| true", gov))
    sunset_ot = bool(re.search(r"policy_lint\.mjs --sunset[^\n]*\|\| true", gov))
    print(f"governance.yml: --stats under || true: {stats_ot}; --sunset under || true: {sunset_ot}")

    p = subprocess.run(["gh", "api", f'search/issues?q=repo:{REPO}+"recurring+friction"'],
                       capture_output=True, text=True)
    total = json.loads(p.stdout).get("total_count") if p.returncode == 0 else None
    print(f'search "recurring friction" total_count={total}')

    oblig = []
    bdir = os.path.join(ROOT, "tools/audit/briefs")
    for f in sorted(os.listdir(bdir)):
        if not f.endswith(".md") or f == "D11.md":
            continue
        for i, line in enumerate(open(os.path.join(bdir, f), encoding="utf-8",
                                      errors="replace"), 1):
            if re.search(r"(--stats|--sunset|friction histogram)", line, re.I):
                oblig.append((f, i, line.strip()[:110]))
    print("role-contract mentions of --stats/--sunset/histogram:")
    for o in oblig:
        print(f"  {o[0]}:{o[1]}  {o[2]}")
    if not oblig:
        print("  (none)")

    rc3, out3 = sh(["node", ".claude/workflows/policy_lint.mjs", "--budgets"])
    m = re.search(r"corpus:\s+~(\d+) tokens, cap (\d+)", out3)
    headroom = int(m.group(2)) - int(m.group(1)) if m else None
    print(f"--budgets corpus: {m.group(0) if m else '?'} -> headroom {headroom}")

    print()
    print(f"RESULT stats_exit_code={rc}")
    print(f"RESULT stats_would_open={would.group(1) if would else -1}")
    print(f"RESULT stats_blocked_count={blocked.group(1) if blocked else -1}")
    print(f"RESULT stats_threshold={thresh.group(1) if thresh else -1}")
    print(f"RESULT perturbation_blocked_v640={blocked2.group(1) if blocked2 else -1}")
    print(f"RESULT stats_or_true={int(stats_ot)}")
    print(f"RESULT sunset_or_true={int(sunset_ot)}")
    print(f"RESULT search_recurring={total}")
    print(f"RESULT obligation_mentions={len(oblig)}")
    print(f"RESULT corpus_headroom={headroom}")


if __name__ == "__main__":
    main()
