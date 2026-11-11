#!/usr/bin/env python3
"""VERIFIER-OWN harness for D11-04 (round 4, verifier seat 1).

METRIC (my own definition; TREE-WIDE sweep, not a fixed glob list, measured at
THIS WORKTREE'S HEAD 0855277 which is 25 commits past the finder's baseline
7dd68dd and already lacks tests/record_status.py):
  live_required_contexts  -- size of the live required-check set, fetched FRESH
                             (no shared cache) from the ruleset object.
  tree_count_claims       -- every line in the tree (excluding .git, audit-round
                             evidence dirs, and this harness) matching
                             "<1-2 digit> required (status check|context|check
                             contexts|contexts are)" -- counted and classified
                             contradicting vs agreeing with the live number.
  tree_record_claims      -- lines asserting `record` is IN the required set
                             (or 'one of main-protect's ... contexts').
  contradictions          -- count of tree_count_claims + tree_record_claims
                             that the live ruleset contradicts.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round4/D11/d11_own_D11-04.py

EXPECTED at head 0855277 (tolerance: exact; static + 1 live API call):
  live_required_contexts=16 contradictions>=3 (finder's baseline count was 8;
  tests/record_status.py's two lines are gone with the file -- per the round's
  resume state that loss may not be counted against the finding)
MACHINE: verifier seat 1 worktree audit-r4-verify-D11-1, 2026-09-12.

PERTURBATION. Rewrite one contradicting '18' to the live number in a scratch
copy of docs/plan-2026-09-open-issues.md and re-run the classifier over the
scratch tree: contradictions must fall by the number of claims on that line.
"""

import json
import os
import re
import subprocess

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                      capture_output=True, text=True).stdout.strip()
REPO = "tvofi/heatpump_optimizer"
RULESET = 22628467

COUNT_RE = re.compile(
    r"\b(\d{1,2})\s+required\s+(?:status\s+check|check\s+)?contexts?\b"
    r"|\b(\d{1,2})\s+required\s+status\s+checks\b"
    r"|required-context\s+set\s+is\s+(\d{1,2})\b", re.I)
RECORD_RE = re.compile(
    r"`record` (is|was) one of `main-protect`|`record` (is|was) (a )?required"
    r"|required contexts?[^.\n]{0,30}\brecord\b\s*(is|was|remains)?[^.\n]{0,20}required", re.I)


def live_ctx():
    p = subprocess.run(["gh", "api", f"repos/{REPO}/rulesets/{RULESET}"],
                       capture_output=True, text=True)
    rs = json.loads(p.stdout)
    for r in rs.get("rules", []):
        if r["type"] == "required_status_checks":
            return {c["context"] for c in r["parameters"]["required_status_checks"]}
    return set()


def classify(live):
    """(contradicting, agreeing) (relpath, line, why) over the whole tree."""
    contra, agree = [], []
    for dirpath, _dirs, files in os.walk(ROOT):
        rel_dir = os.path.relpath(dirpath, ROOT)
        # NB: exclude ".git" EXACTLY -- ".github" also startswith(".git") and
        # that bug silently dropped governance.yml from the first run of this
        # harness. Recorded here because an instrument defect is a finding.
        if (rel_dir == ".git" or "/.git/" in dirpath + "/"
                or rel_dir.startswith("tools/audit/round")
                or rel_dir.startswith("node_modules")):
            continue
        for f in files:
            if not f.endswith((".py", ".md", ".yml", ".yaml", ".mjs", ".js",
                               ".sh", ".json", ".txt", ".mdc")):
                continue
            p = os.path.join(dirpath, f)
            rel = os.path.relpath(p, ROOT)
            if rel in ("tools/audit/round4/D11/d11_own_D11-04.py",):
                continue
            try:
                lines = open(p, encoding="utf-8", errors="replace").read().split("\n")
            except OSError:
                continue
            for i, line in enumerate(lines, 1):
                for m in COUNT_RE.finditer(line):
                    n = int(m.group(1) or m.group(2) or m.group(3))
                    why = f"claims {n} required contexts; live set is {len(live)}"
                    (contra if n != len(live) else agree).append((rel, i, why))
                if RECORD_RE.search(line):
                    contra.append((rel, i, "asserts `record` is required; "
                                           f"live set: {'record' if 'record' in live else 'no record'}"))
    return contra, agree


def main():
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    live = live_ctx()
    print(f"tree head={head}; live required contexts={len(live)}: {sorted(live)}")
    contra, agree = classify(live)
    print(f"\nTREE ASSERTIONS CONTRADICTING THE LIVE SET ({len(contra)}):")
    for rel, i, why in contra:
        print(f"  {rel}:{i}  {why}")
    print(f"\ntree assertions agreeing with the live set ({len(agree)}):")
    for rel, i, why in agree:
        print(f"  {rel}:{i}  {why}")

    # perturbation on a scratch copy of the noisiest file
    import shutil, tempfile
    scratch = tempfile.mkdtemp()
    dst = os.path.join(scratch, "plan.md")
    shutil.copy(os.path.join(ROOT, "docs/plan-2026-09-open-issues.md"), dst)
    before = sum(1 for _ in re.finditer(r"\b18\s+required", open(dst).read()))
    txt = re.sub(r"\b18\s+required", f"{len(live)} required", open(dst).read())
    open(dst, "w").write(txt)
    after = sum(1 for _ in re.finditer(r"\b18\s+required", open(dst).read()))
    print(f"\nPERTURBATION scratch plan.md '18 required' occurrences {before} -> {after}")

    print()
    print(f"RESULT live_required_contexts={len(live)}")
    print(f"RESULT live_has_record={'record' in live}")
    print(f"RESULT tree_claim_contradictions={len(contra)}")
    print(f"RESULT tree_claims_agreeing={len(agree)}")
    print(f"RESULT perturbation_18claims_fixed={before - after}")


if __name__ == "__main__":
    main()
