#!/usr/bin/env python3
"""R10-PLAN-ARTIFACT: each behaviour plan_page.py's self-test pins dies alone.

Each mutant is one exact one-occurrence replacement in
tools/audit/seat/plan_page.py or tools/plan/replan.py (the freshness rule the
page shares). The driver applies one, runs `plan_page.py --self-test`, restores
the file byte for byte, and refuses to start on a file with uncommitted edits.
Metric, one line per mutant:

  RESULT mutant=<name> rc=<rc> fails=<n> verdict=killed|SURVIVED|CRASHED

then the FAIL lines. A mutant that kills only by crashing (no FAIL line) is
CRASHED, not killed. Null control: M0, nothing replaced, must print rc=0
fails=0; a replacement whose text is not found exactly once aborts.

    python3 dev/audit/harnesses/r10_plan_page_mutants.py [NAME ...]
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
PAGE = "tools/audit/seat/plan_page.py"
PLAN = "tools/plan/replan.py"

MUTANTS = [
    ("M0", PAGE, None, None),
    ("live", PAGE, "elif _stage(entry) in replan.LIVE_STAGES:", "elif False:"),
    ("blocked", PAGE, "elif blk and not part:", "elif False:"),
    ("partial", PAGE, "if m and m.group(1) in G:", "if False:"),
    ("blocked-by-less-done", PAGE,
     "blk = [a for a in entry.get(\"after\") or [] if a in G and a not in done]",
     "blk = [a for a in entry.get(\"after\") or [] if a in G]"),
    ("pr-by-merge-commit", PAGE,
     "if sha.startswith(commit) or commit.startswith(sha[:len(commit)]):", "if False:"),
    ("pr-by-branch", PAGE, "            by_group[g] = p[\"number\"]", "            pass"),
    ("pr-sha8-fallback", PAGE, "label, pr = f\"merged at {commit[:8]}\", \"merged\"",
     "label, pr = \"folded into another group (no merge of its own)\", \"merged\""),
    ("branch-tail-fallback", PAGE,
     "return tails.get(tail) or tails.get(tail.replace(\"-pr\", \"\"))", "return None"),
    ("title-fallback", PAGE,
     "return named.pop() if len(named) == 1 else None", "return None"),
    ("closed-strike", PAGE, "(\"\" if is_open else \" closed\")", "\"\""),
    ("tracking-excluded", PAGE,
     "if i[\"state\"] == \"OPEN\" and i[\"number\"] != TRACKING_ISSUE)",
     "if i[\"state\"] == \"OPEN\")"),
    ("page-refuses-stale", PAGE, "    if stale:\n        bad.append", "    if False:\n        bad.append"),
    ("freshness-rule", PLAN, "if have != want:", "if False:"),
    ("stamp-on-axis", PAGE,
     "end = max([_t(plan[\"summary\"][\"closure\"])] + [_t(s[\"at\"]) for s in plan[\"stamps\"]])",
     "end = _t(plan[\"summary\"][\"closure\"])"),
]


def main(argv: list[str]) -> int:
    want = set(argv)
    for rel in (PAGE, PLAN):
        if subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", "--", rel]).returncode:
            print(f"refused: {rel} has uncommitted edits")
            return 2
    survived = 0
    for name, rel, old, new in MUTANTS:
        if want and name not in want:
            continue
        path = ROOT / rel
        orig = path.read_bytes()
        try:
            if old is not None:
                text = orig.decode()
                if text.count(old) != 1:
                    print(f"abort: {name}: {old!r} occurs {text.count(old)} times in {rel}")
                    return 2
                path.write_text(text.replace(old, new), encoding="utf-8")
            r = subprocess.run([sys.executable, "-I", str(ROOT / PAGE), "--self-test"],
                               capture_output=True, text=True)
        finally:
            path.write_bytes(orig)
        fails = [ln for ln in r.stdout.splitlines() if ln.startswith("FAIL")]
        if name == "M0":
            verdict = "null" if r.returncode == 0 and not fails else "SURVIVED"
        elif fails and r.returncode:
            verdict = "killed"
        elif r.returncode:
            verdict = "CRASHED"
        else:
            verdict = "SURVIVED"
        survived += verdict in ("SURVIVED", "CRASHED")
        print(f"RESULT mutant={name} rc={r.returncode} fails={len(fails)} verdict={verdict}")
        for ln in fails:
            print("   ", re.sub(r"\(got: .*", "", ln))
    print(f"RESULT survived={survived}")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
