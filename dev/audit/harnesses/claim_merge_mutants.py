#!/usr/bin/env python3
"""claim_merge_mutants.py -- one mutant per rule of the claimnotes driver, against its committed checks (R10-996-RUNNER-CLAIMS, #3066).

Copies ``tests/`` and ``.gitattributes`` into a temporary directory, applies
each mutant below to the COPY of ``tests/env_drift.py`` (the tree is never
written, so an interrupted run leaves nothing mutated), and runs the
claim-file merge-driver section of ``tests/entities.py`` -- from its
``# --- the claim-file merge driver`` banner to the ledger driver's -- in a
fresh interpreter. A mutant is killed when that section exits non-zero.

    python3 dev/audit/harnesses/claim_merge_mutants.py

The unmutated copy runs first as the null control: it must pass, or every
kill below is the runner's and not the mutant's. A mutant whose text no
longer occurs once in the driver prints ``stale`` rather than a verdict.
The M* and R-* rows are the #3066 review's own mutants (M5 retired with the
two-way survival check it mutated); N* mutate the stamp and ``may-drift``
decision. RESULT lines count the rows.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DRIVER = "tests/env_drift.py"

# (name, the text replaced, its replacement) -- each must occur exactly once.
MUTANTS = (
    ("M1-ours-change-takes-main", "        elif main == was:\n            lines = our_blocks.get(name)",
     "        elif main == was:\n            lines = their_blocks.get(name)"),
    ("M2-conflict-takes-ours", "            refused.append(name)\n            continue",
     "            lines = our_blocks.get(name)"),
    ("M3-main-deletion-undone",
     "        if mine == main or mine == was:\n            lines = their_blocks.get(name)",
     "        if mine == main or mine == was:\n"
     "            lines = our_blocks.get(name) or their_blocks.get(name)"),
    ("M4-no-stamp-guard", "    if both_changed and not (", "    if False and not ("),
    ("M6-no-own-lines-check",
     "            return f\"the claims for '{name}' are neither side's own\"", "            pass"),
    ("R-keep-deleted", "        if lines:\n            decided[name] = lines",
     "        lines = lines or our_blocks.get(name) or their_blocks.get(name)\n"
     "        if lines:\n            decided[name] = lines"),
    ("R-mine-eq-main-only", "        if mine == main or mine == was:", "        if mine == was:"),
    ("N1-no-union-cut",
     "    comments = [ln for ln in comments if _marker_key(ln) is None or ln in keep]\n", ""),
    ("N2-marker-refuse-nothing",
     "    return _decide_per_key(_marker_blocks(base), mine, main, mine, main)",
     "    return _decide_per_key(_marker_blocks(base), mine, main, mine, main)[0], []"),
    ("N3-file-ignores-marker-refusal", "    if decided is None or marker_refused:",
     "    if decided is None:"),
    ("N4-defect-no-marker-check", "    if got_md != want_md:\n", "    if False:\n"),
    ("N6-refusal-unnamed", "            for name in marker_refused\n", "            for name in []\n"),
    ("N7-stamp-not-a-marker", "        return CLAIM_VERSION_MARKER\n", "        return None\n"),
    ("N8-maydrift-not-a-marker", "        return f\"{MAY_DRIFT_MARKER} {name}\"\n",
     "        return None\n"),
    ("N9-maydrift-key-ignores-name", "        return f\"{MAY_DRIFT_MARKER} {name}\"\n",
     "        return MAY_DRIFT_MARKER\n"),
)

# Run in the copy: the section's own prelude, then the section, then its exit.
RUNNER = r'''
import os, sys
from pathlib import Path
os.chdir(sys.argv[1]); sys.path[:0] = ["tests", "tests/hastub"]
from throwaway_git import throwaway_git_env, throwaway_git_init
from harness import Results
import env_drift as _env_drift
import tempfile as _tempfile, subprocess as _subprocess
R = Results("CM")
src = open("tests/entities.py").read().splitlines(keepends=True)
start = next(i for i, l in enumerate(src) if l.startswith("# --- the claim-file merge driver"))
end = next(i for i in range(start, len(src)) if src[i].startswith("# The ledger merge driver"))
__file__ = os.path.abspath("tests/entities.py")
exec(compile("".join(src[start:end]), "entities-cm", "exec"), globals())
sys.exit(R.close("CM"))
'''


def run_section(copy: Path) -> tuple[int, list[str]]:
    proc = subprocess.run([sys.executable, "-c", RUNNER, str(copy)],
                          capture_output=True, text=True, timeout=600)
    fails = [ln.strip()[:100] for ln in proc.stdout.splitlines() if ln.startswith("  FAIL")]
    return proc.returncode, fails


def main() -> int:
    original = (ROOT / DRIVER).read_text()
    killed = survived = stale = 0
    with tempfile.TemporaryDirectory() as td:
        copy = Path(td) / "repo"
        shutil.copytree(ROOT / "tests", copy / "tests",
                        ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy(ROOT / ".gitattributes", copy / ".gitattributes")
        target = copy / DRIVER
        rc, fails = run_section(copy)
        print(f"baseline   rc={rc} {'pass' if rc == 0 else 'FAIL ' + '; '.join(fails)}")
        print(f"RESULT baseline_pass={int(rc == 0)}")
        if rc != 0:
            return 1
        for name, old, new in MUTANTS:
            if original.count(old) != 1:
                print(f"{name:32} stale (its text occurs {original.count(old)} times)")
                stale += 1
                continue
            target.write_text(original.replace(old, new))
            rc, fails = run_section(copy)
            target.write_text(original)
            verdict = "killed" if rc != 0 else "SURVIVED"
            killed += rc != 0
            survived += rc == 0
            print(f"{name:32} {verdict:8} failing={len(fails)}"
                  + (f" first: {fails[0]}" if fails else ""))
    print(f"RESULT killed={killed}")
    print(f"RESULT survived={survived}")
    print(f"RESULT stale={stale}")
    return 1 if survived or stale else 0


if __name__ == "__main__":
    sys.exit(main())
