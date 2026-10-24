#!/usr/bin/env python3
"""R10-FLY-CLOUD-SETUP-TOOLCHAIN: cloud-setup.sh's self-test against each mutant.

    python3 -I dev/audit/harnesses/r10_cloud_setup_mutants.py [--runs 3] [M9 ...]

Each mutant replaces one string, present exactly once, in a temporary copy of
tools/audit/seat/cloud-setup.sh (the committed file is never edited) and runs
`bash <copy> --self-test` on a /dev/null stdin, --runs times. M0 is the
unmutated copy and must read `0 failed` on every run. A mutant is KILLED when
every run fails, SURVIVED when none does, and FLAKY otherwise; each line names
the failing arms. Prints `RESULT survivors=<n>`, exit 1 when any mutant
survived or flaked, or M0 failed.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "tools" / "audit" / "seat" / "cloud-setup.sh"

# name, what it removes, old (exactly once in the script), new
MUTANTS = [
    ("M1", "the profile's presence test (the merge base's line)",
     'case ":\\$PATH:" in *":$2/venv-ci/bin:"*) ;; *) export PATH="$2/venv-ci/bin:\\$PATH" ;; esac',
     'export PATH="$2/venv-ci/bin:\\$PATH"'),
    ("M2", "check's whole condition",
     'if [ "$py" = "$1/venv-ci/bin/python3" ] && [ -x "${HPO_TYPING_PYTHON:-}" ] \\\n'
     '    && [ "${OPENBLAS_CORETYPE:-}" = "$CORETYPE" ]; then', "if true; then"),
    ("M3", "check's HPO_TYPING_PYTHON half",
     ' && [ -x "${HPO_TYPING_PYTHON:-}" ]', ""),
    ("M4", "variables' venv-ci/bin prefix", '"PATH=$1/venv-ci/bin:$rest"', '"PATH=$rest"'),
    ("M5", "variables' HPO_TYPING_PYTHON line", '    "HPO_TYPING_PYTHON=$1/venv-ha/bin/python" ', "    "),
    ("M6", "variables' dedupe filter", '[ "$d" = "$1/venv-ci/bin" ] || ', ""),
    ("M7", "the profile's OPENBLAS_CORETYPE export", "export OPENBLAS_CORETYPE=$CORETYPE\nEOF", ":\nEOF"),
    ("M8", "variables' OPENBLAS_CORETYPE line", ' "OPENBLAS_CORETYPE=$CORETYPE"', ""),
    ("M9", "check's python3-is-venv-ci half", '[ "$py" = "$1/venv-ci/bin/python3" ] && ', ""),
    ("M10", "the profile's HPO_TYPING_PYTHON export",
     'export HPO_TYPING_PYTHON="$2/venv-ha/bin/python"', ":"),
    ("M11", "check's refusal exit", "  return 1\n}", "  return 0\n}"),
    # `check "$PREFIX"; exit 0` alone is an equivalent mutant: under `set -e` a
    # refusing check exits 1 before reaching it. M12 is the state the review
    # named (a refusal a seat would carry on past); M12b the other direction.
    ("M12", "--check's refusal exit", '--check) check "$PREFIX"; exit $? ;;',
     '--check) check "$PREFIX" || true; exit 0 ;;'),
    ("M12b", "--check's OK exit", '--check) check "$PREFIX"; exit $? ;;', '--check) check "$PREFIX"; exit 1 ;;'),
    ("M13", "check's OPENBLAS_CORETYPE half",
     ' \\\n    && [ "${OPENBLAS_CORETYPE:-}" = "$CORETYPE" ]', ""),
]


def self_test(path: Path) -> tuple[bool, list[str]]:
    r = subprocess.run(["bash", str(path), "--self-test"], stdin=subprocess.DEVNULL,
                       capture_output=True, text=True, timeout=300)
    fails = [ln[5:] for ln in r.stdout.splitlines() if ln.startswith("FAIL ")]
    return r.returncode == 0 and not fails, fails


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("names", nargs="*")
    args = ap.parse_args()
    src = SCRIPT.read_text()
    survivors = 0
    with tempfile.TemporaryDirectory() as td:
        base = Path(td) / "M0.sh"
        base.write_text(src)
        m0 = [self_test(base) for _ in range(args.runs)]
        m0_ok = all(ok for ok, _ in m0)
        print(f"M0 none: {'PASS' if m0_ok else 'FAIL'} {sum(ok for ok, _ in m0)}/{args.runs} runs 0 failed")
        for name, what, old, new in MUTANTS:
            if args.names and name not in args.names:
                continue
            if src.count(old) != 1:
                print(f"{name} {what}: NO-APPLY ({src.count(old)} occurrences)")
                survivors += 1
                continue
            mut = Path(td) / f"{name}.sh"
            mut.write_text(src.replace(old, new))
            runs = [self_test(mut) for _ in range(args.runs)]
            red = sum(not ok for ok, _ in runs)
            verdict = "KILLED" if red == args.runs else "SURVIVED" if red == 0 else "FLAKY"
            survivors += verdict != "KILLED"
            arms = sorted({f for _, fails in runs for f in fails})
            print(f"{name} {what}: {verdict} {red}/{args.runs} runs red; " + ("; ".join(arms) or "no arm failed"))
    print(f"RESULT survivors={survivors}")
    return 0 if survivors == 0 and m0_ok else 1


if __name__ == "__main__":
    sys.exit(main())
