#!/usr/bin/env python3
"""R11-PRE-TOOLCHAIN-PIN carry 3 (MAIN-CANCEL-BOUNDED): each guard of the `main` arm dies alone.

Each mutant is one exact one-occurrence replacement in a COPY of
tools/pr/cancel_superseded.py (never the tree); the copy's own `--self-test`
is then run and must FAIL. Null control: M0, nothing mutated, must print
failed=0. A pattern not found exactly once aborts.

  M-newest     the newest main run of a workflow may be cancelled.
  M-row        the bound on a row of runs with no concluded one is dropped.
  M-bound      the bound is four, not three.
  M-older-side the row is not counted toward older runs.
  M-newer-side the row is not counted toward newer runs.
  M-planned    a cancel planned in this pass is not counted in later rows.
  M-full       a row reaching the old end of a full listing is cancelled.
  M-verdicts   a run that completed `skipped` counts as concluded.
  M-event      a main run of any event is read, not only `push`.
  M-branch     a push run on any branch is read, not only main.
  M-dry        `--dry-run` posts the cancels.

    python3 dev/audit/harnesses/r11_main_cancel_mutants.py

EXPECTED RESULT mutants=11
EXPECTED RESULT survived=0
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
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
TARGET = "tools/pr/cancel_superseded.py"
PLANTS = {
    "M-newest": ("        if i == len(rs) - 1:\n", "        if False:\n"),
    "M-row": ("        elif hi - lo + 1 > MAIN_ROW_MAX:\n", "        elif False:\n"),
    "M-bound": ("MAIN_ROW_MAX = 3 ", "MAIN_ROW_MAX = 4 "),
    "M-older-side": ("        while lo > 0 and empty[lo - 1]:\n", "        while False:\n"),
    "M-newer-side": ("        while hi < len(rs) - 1 and empty[hi + 1]:\n", "        while False:\n"),
    "M-planned": ("            empty[i] = True\n", "            pass\n"),
    "M-full": ("        elif lo == 0 and full:\n", "        elif False:\n"),
    "M-verdicts": ('VERDICTS = ("success", "failure", "timed_out")', 'VERDICTS = ("success", "failure", "timed_out", "skipped")'),
    "M-event": ('r.get("head_branch") == "main" and r.get("event") == "push"),', 'r.get("head_branch") == "main"),'),
    "M-branch": ('r.get("head_branch") == "main" and r.get("event") == "push"),', 'r.get("event") == "push"),'),
    "M-dry": ('            if a.dry_run:\n                print(f"cancel_superseded: would cancel {rid}")\n            else:\n'
              "                post_cancel(api, a.repo, rid, {}, time.time())\n        print(f\"CANCEL-MAIN",
              "            post_cancel(api, a.repo, rid, {}, time.time())\n        print(f\"CANCEL-MAIN"),
}


def main() -> int:
    src = (ROOT / TARGET).read_text()
    survived = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name in ["M0", *PLANTS]:
            text = src
            if name != "M0":
                old, new = PLANTS[name]
                if src.count(old) != 1:
                    print(f"ABORT {name}: pattern occurs {src.count(old)} times")
                    return 2
                text = src.replace(old, new)
            copy = Path(tmp) / name / "tools" / "pr" / "cancel_superseded.py"
            copy.parent.mkdir(parents=True)
            copy.write_text(text)
            r = subprocess.run([sys.executable, str(copy), "--self-test"], capture_output=True, text=True)
            failed = sum(1 for l in r.stdout.splitlines() if l.strip().startswith("FAIL"))
            if name == "M0":
                print(f"RESULT mutant=M0 failed={failed} verdict={'null-ok' if r.returncode == 0 and not failed else 'NULL-RED'}")
                if r.returncode:
                    return 2
                continue
            dead = r.returncode != 0 and failed > 0
            survived += not dead
            print(f"RESULT mutant={name} failed={failed} verdict={'killed' if dead else 'SURVIVED'}")
    print(f"RESULT mutants={len(PLANTS)}")
    print(f"RESULT survived={survived}")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())
