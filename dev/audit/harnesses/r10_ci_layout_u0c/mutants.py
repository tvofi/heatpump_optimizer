#!/usr/bin/env python3
"""R10-CI-LAYOUT P2b, unit U0c: the umbrella's and the sweep's pins, each against a mutant.

    python3 dev/audit/harnesses/r10_ci_layout_u0c/mutants.py [--jobs N]     # all
    python3 dev/audit/harnesses/r10_ci_layout_u0c/mutants.py M0 M3          # named

Run from the branch's worktree with its work committed. Each mutant gets its
own detached worktree of HEAD (removed afterwards), one text substitution per
edit that must apply exactly once, and a full
`PYTHONPATH=tests/hastub python3 tests/entities.py` run. M0 is the unmutated
head: it must fail no check outside KNOWN_RED. A mutant is KILLED when entities
exits non-zero AND one of the checks it is aimed at is among the FAIL lines;
any other red reads OFF-TARGET.

KNOWN_RED is the one check red at this unit's head by design: the base's
`policy_lint.mjs` finds the contract's workflow by `\n  pr-contract:\n`, and
ci.yml's caller now matches it too (2 files). That reader is U9b's, and CI runs
the base's copy; the unit's body escalates it rather than reshaping ci.yml to
miss the regex.

  M1  gate's if: skips merge_group               -> the umbrella pin
  M2  the merge_group trigger dropped            -> the umbrella pin
  M3  run-name loses its sha= token              -> the umbrella pin
  M4  the concurrency group keyed on the PR      -> the umbrella pin and the twin-route pin
  M5  gate granted statuses: write               -> the forgery pin
  M6  the forgery reader forgets statuses        -> the forgery pin (its plants go unread)
  M7  the sweep keyed on its exit code           -> the sweep pin
  M8  the sweep given a concurrency group        -> the sweep pin
  M9  gate-sweep.yml leaves GATE_FILES           -> the sweep pin
  M10 a caller guarded on the event, not the workset -> the umbrella pin

Prints one line per mutant with its exit code and the aimed checks that went
red, then `RESULT survivors=<n>`; exit 1 when any survived or M0 failed.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True, check=True).stdout.strip())

CI, GS = ".github/workflows/ci.yml", ".github/workflows/gate-sweep.yml"
UMB = "the CI umbrella: "
FORGE = "forgery: exactly one job"
SWEEP = "gate-sweep.yml: on CI's completion"
TWIN = "a superseded long-job pull-request run is cancelled"
KNOWN_RED = ["the template arm turns the acceptance red"]
MUTANTS: dict[str, tuple[list[tuple[str, str, str]], list[str]]] = {
    "M0": ([], []),
    "M1": ([(CI, "    if: ${{ !cancelled() }}\n",
             "    if: ${{ !cancelled() && github.event_name != 'merge_group' }}\n")], [UMB]),
    "M2": ([(CI, "  merge_group:\n    types: [checks_requested]\n", "")], [UMB]),
    "M3": ([(CI, " sha={3}',", "',")], [UMB]),
    "M4": ([(CI, "  group: CI-${{ github.run_id }}\n",
             "  group: CI-${{ github.event.pull_request.number || github.run_id }}\n")], [UMB, TWIN]),
    "M5": ([(CI, "    timeout-minutes: 15\n    permissions:\n      contents: read\n      actions: read\n",
             "    timeout-minutes: 15\n    permissions:\n      contents: read\n      statuses: write\n      actions: read\n")],
           [FORGE]),
    "M6": ([("tests/entities.py", '            for scope in ("checks", "statuses"):\n',
             '            for scope in ("checks",):\n')], [FORGE]),
    "M7": ([(GS, '          out=$(python3 -I tools/ci/gate.py --sweep --run "$RUN_ID" 2>&1)\n',
             '          python3 -I tools/ci/gate.py --sweep --run "$RUN_ID"; exit $?\n')], [SWEEP]),
    "M8": ([(GS, "permissions: {}\n",
             "permissions: {}\n\nconcurrency:\n  group: sweep-${{ github.run_id }}\n")], [SWEEP]),
    "M9": ([("tests/closure.py", '    ".github/workflows/gate-sweep.yml",\n', "")], [SWEEP]),
    "M10": ([(CI, "    if: contains(format(' {0} ', needs.prelude.outputs.workset), ' arch-score ')\n",
              "    if: needs.prelude.outputs.pr != '' && needs.prelude.outputs.kind != 'review'\n")], [UMB]),
}


def run_one(name: str) -> tuple[str, int, list[str], str]:
    edits, aimed = MUTANTS[name]
    tmp = Path(tempfile.mkdtemp(prefix=f"u0c-{name}-"))
    wt = tmp / "wt"
    try:
        subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "-q", "--detach",
                        str(wt), "HEAD"], check=True, capture_output=True)
        for rel, old, new in edits:
            p = wt / rel
            text = p.read_text()
            if text.count(old) != 1:
                return name, -1, [], f"edit to {rel} matched {text.count(old)} times"
            p.write_text(text.replace(old, new))
        env = {**os.environ, "PYTHONPATH": "tests/hastub"}
        res = subprocess.run([sys.executable, "tests/entities.py"], cwd=wt, env=env,
                             capture_output=True, text=True, timeout=7200)
        fails = [ln[len("  FAIL "):].split("  [")[0] for ln in res.stdout.splitlines()
                 if ln.startswith("  FAIL ")]
        tail = [ln for ln in res.stdout.splitlines() if "ENTITY CHECKS" in ln]
        hit = ([f for f in fails if not any(f.startswith(k) for k in KNOWN_RED)] if not aimed
               else [f for f in fails if any(f.startswith(a) for a in aimed)])
        return name, res.returncode, hit, tail[-1] if tail else "(no summary line)"
    finally:
        subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(wt)],
                       capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv: list[str]) -> int:
    jobs = len(MUTANTS)
    if "--jobs" in argv:
        i = argv.index("--jobs")
        jobs = int(argv[i + 1])
        del argv[i:i + 2]
    names = argv or list(MUTANTS)
    unknown = [n for n in names if n not in MUTANTS]
    if unknown:
        print(f"unknown mutant(s): {unknown}", file=sys.stderr)
        return 2
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        results = list(pool.map(run_one, names))
    survivors, m0_bad = 0, False
    for name, rc, hit, tail in results:
        if name == "M0":
            m0_bad = rc == -1 or bool(hit)
            verdict = "FAIL" if m0_bad else "PASS"
        elif rc == -1:
            verdict, survivors = "NOT RUN", survivors + 1
        elif rc != 0 and hit:
            verdict = "KILLED"
        elif rc != 0:
            verdict, survivors = "OFF-TARGET", survivors + 1
        else:
            verdict, survivors = "SURVIVED", survivors + 1
        print(f"{name} {verdict} rc={rc} | {tail} | aimed red: {hit}")
    print(f"RESULT survivors={survivors}")
    return 1 if survivors or m0_bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
