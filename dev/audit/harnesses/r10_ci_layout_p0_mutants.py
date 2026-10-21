#!/usr/bin/env python3
"""R10-CI-LAYOUT PR 0: the stub's and the ci-ratchet payments' pins, each against a mutant.

    python3 dev/audit/harnesses/r10_ci_layout_p0_mutants.py            # all
    python3 dev/audit/harnesses/r10_ci_layout_p0_mutants.py M0 M3      # named

Run from the branch's worktree with its work committed. Each mutant gets its
own detached worktree of HEAD (removed afterwards, the branch's own tree is
never edited), one text substitution that must apply exactly once, and a full
`PYTHONPATH=tests/hastub python3 tests/entities.py` run; the runs go in
parallel (`--jobs N`, default all). M0 is the unmutated head and must pass
every check. A mutant is KILLED when entities exits non-zero AND one of the
checks it is aimed at is among the FAIL lines; any other red reads OFF-TARGET.

  M1  ci.yml gains a `push:` trigger              -> the stub-inert check
  M2  ci.yml leaves closure.py's GATE_FILES        -> the stub-inert check
  M3  arch_score_head.py back in lane_units        -> the placement pin
  M4  the floor re-validation re-measures all      -> _coverage_revalidation
  M5  script_runs() counts `reused` rows again     -> _CIR_REUSE
  M6  script_runs_per_push loosened 53 -> 54       -> the every-script-once pin
  M7  the reused-row ledger filter deleted         -> the ledger check (round-1 review)
  M8  harness_headers.py back into lane_units      -> the run-alone pin (round-2 review)

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

STUB = "the ci.yml umbrella stub is inert"
MUTANTS: dict[str, tuple[list[tuple[str, str, str]], list[str]]] = {
    "M0": ([], []),
    "M1": ([(".github/workflows/ci.yml", "on:\n  workflow_dispatch:\n",
             "on:\n  push:\n  workflow_dispatch:\n")], [STUB]),
    "M2": ([("tests/closure.py", '    ".github/workflows/ci.yml",\n', "")], [STUB]),
    "M3": ([("tests/run.sh", '  run "$PYTHON" tests/arch_score_head.py\n}\n', "}\n"),
            ("tests/run.sh", '  run "$PYTHON" tests/structure.py\n',
             '  run "$PYTHON" tests/structure.py\n  run "$PYTHON" tests/arch_score_head.py\n')],
           ["the architecture-score pair runs in lane_golden"]),
    "M4": ([("tools/coverage/coverage_tree.sh",
             "    PLAN=$(echo \"$_reused\" | sed 's/^/measure\\t/')\n",
             '    rm -f "$OUT/per"/.coverage.* "$OUT/per"/*.nodata "$OUT/per/provenance.tsv" "$OUT/scripts.tsv"\n'
             "    PLAN=$(echo \"$SCRIPTS\" | sed 's/^/measure\\t/')\n")],
           ["the coverage floor re-validation re-measures only the scripts it reused"]),
    "M5": ([("tests/ci_ratchet.py", ' and r["class"] != "reused")', ")")],
           ["the CI ratchet counts no `reused` coverage row as a script run"]),
    "M6": ([("tests/ci_budgets.json", '"script_runs_per_push": 53', '"script_runs_per_push": 54')],
           ["one script run past the every-script-once budget"]),
    "M7": ([("tools/coverage/coverage_tree.sh",
             '    for _f in "$OUT/scripts.tsv" "$OUT/per/provenance.tsv"; do\n'
             '      awk -F\'\\t\' \'$2!="reused"\' "$_f" > "$_f.tmp" && mv "$_f.tmp" "$_f"\n'
             '    done\n', "")],
           ["after a floor-FAIL re-validation each coverage ledger holds one row"]),
    "M8": ([("tests/run.sh", '  run_always "$PYTHON" tests/harness_headers.py\n}\n', "}\n"),
            ("tests/run.sh", '  run "$PYTHON" tests/finite_boundary.py\n',
             '  run "$PYTHON" tests/finite_boundary.py\n  run_always "$PYTHON" tests/harness_headers.py\n')],
           ["the CPU-bounded harness check runs alone"]),
}


def run_one(name: str) -> tuple[str, int, list[str], str]:
    edits, aimed = MUTANTS[name]
    tmp = Path(tempfile.mkdtemp(prefix=f"p0-{name}-"))
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
        hit = [f for f in fails if any(f.startswith(a) for a in aimed)]
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
            verdict = "PASS" if rc == 0 else "FAIL"
            m0_bad = rc != 0
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
