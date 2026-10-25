#!/usr/bin/env python3
"""R10-PLAN-ISSUES-CHART: each behaviour the issues chart's self-test pins dies alone.

Each mutant is one exact one-occurrence replacement in
tools/audit/seat/plan_page.py. The driver applies one, runs
`plan_page.py --self-test`, restores the file byte for byte, and refuses to
start on a file with uncommitted edits. One line per mutant:

  RESULT mutant=<name> rc=<rc> fails=<n> verdict=killed|SURVIVED|CRASHED

then the FAIL lines. A mutant that kills only by crashing (no FAIL line) is
CRASHED, not killed. Null control: M0, nothing replaced, must print rc=0
fails=0; a replacement whose text is not found exactly once aborts.

    python3 dev/audit/harnesses/r10_plan_issues_chart_mutants.py [NAME ...]
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from r10_plan_page_mutants import fail_name  # noqa: E402 -- the one FAIL-line grammar

ROOT = Path(__file__).resolve().parents[3]
PAGE = "tools/audit/seat/plan_page.py"

MUTANTS = [
    ("M0", None, None),
    ("earlier-finish", "close_at[n] = max(close_at.get(n, t), t)",
     "close_at[n] = min(close_at.get(n, t), t)"),
    ("closed-counted", "            if n not in open_now:", "            if False:"),
    ("unplanned-dropped", "                unplanned.add(n)", "                pass"),
    ("unplanned-also-closes", "        close_at.pop(n, None)", "        pass"),
    ("other-uncounted", "\"other\": open_now - set(close_at) - unplanned}", "\"other\": set()}"),
    ("offline-not-omitted", "    if snap.get(\"offline\"):", "    if False:"),
    ("gh-missing-crashes", "    except (OSError, subprocess.CalledProcessError) as exc:",
     "    except ZeroDivisionError as exc:"),
    ("not-first", "{{issues_chart}}\n<section>\n  <h2>Swimlanes</h2>",
     "<section>\n  <h2>Swimlanes</h2>"),
]


def main(argv: list[str]) -> int:
    want = set(argv)
    if subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", "--", PAGE]).returncode:
        print(f"refused: {PAGE} has uncommitted edits")
        return 2
    survived = 0
    path = ROOT / PAGE
    for name, old, new in MUTANTS:
        if want and name not in want:
            continue
        orig = path.read_bytes()
        try:
            if old is not None:
                text = orig.decode()
                if text.count(old) != 1:
                    print(f"abort: {name}: {old!r} occurs {text.count(old)} times")
                    return 2
                path.write_text(text.replace(old, new), encoding="utf-8")
            run = subprocess.run([sys.executable, "-I", str(path), "--self-test"],
                                 capture_output=True, text=True)
        finally:
            path.write_bytes(orig)
        fails = [ln for ln in run.stdout.splitlines() if ln.startswith("FAIL")]
        rc = run.returncode
        if name == "M0":
            verdict = "null" if rc == 0 and not fails else "SURVIVED"
        elif fails and rc:
            verdict = "killed"
        elif rc:
            verdict = "CRASHED"
        else:
            verdict = "SURVIVED"
        survived += verdict in ("SURVIVED", "CRASHED")
        print(f"RESULT mutant={name} rc={rc} fails={len(fails)} verdict={verdict}")
        for ln in fails:
            print("   ", fail_name(ln))
    print(f"RESULT survived={survived}")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
