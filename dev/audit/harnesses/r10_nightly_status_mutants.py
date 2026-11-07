"""R10-HOTFIX-NIGHTLY-STATUS mutation proof: one tree's check against another tree's grader.

Runs the superseded-failure checks of CHECK_TREE's ``tests/entities.py``
VERBATIM (sliced between their own section markers) against CODE_TREE's
``tests/nightly_status.py``, unmutated and then under each mutant below, one
per changed grading line of ``verdict`` and of ``main``'s in-flight fetch.

    python3 dev/audit/harnesses/r10_nightly_status_mutants.py CHECK_TREE CODE_TREE

Both arguments are checkout roots (a worktree or a ``git archive`` export).
A mutant is KILLED when any sliced check fails or the slice raises. Null
control: the unmutated row must read ``rc=0``, and a CODE_TREE whose
``verdict`` predates ``in_flight_jobs`` reads ``rc=1`` (TypeError).
"""
import os
import pathlib
import subprocess
import sys
import tempfile

MUTANTS = [
    ("M1-predicate-off", "    if bad and in_flight is not None and in_flight_jobs",
     "    if False and bad and in_flight is not None and in_flight_jobs"),
    ("M2-gt-to-ge", 'in_flight.get("created_at")) > started:',
     'in_flight.get("created_at")) >= started:'),
    ("M3-drop-newer", 'in_flight_jobs and parse_ts(\n            in_flight.get("created_at")) > started:',
     "in_flight_jobs:"),
    ("M4-success-to-ok", 'if j.get("conclusion") == "success"}',
     'if j.get("conclusion") in OK_CONCLUSIONS}'),
    ("M5-success-to-notfail", 'if j.get("conclusion") == "success"}',
     'if j.get("conclusion") != "failure"}'),
    ("M6-all-to-any", 'if all(j.get("name") in greens for j in bad):',
     'if any(j.get("name") in greens for j in bad):'),
    ("M7-keep-runfailed", "            bad, run_failed = [], False\n", "            bad = []\n"),
    ("M8-name-match", 'if all(j.get("name") in greens for j in bad):', "if greens:"),
    ("M9-drop-flyjobs-guard", "in_flight is not None and in_flight_jobs and parse_ts(",
     "in_flight is not None and parse_ts("),
    ("M10-main-nofetch", "fly_jobs = _jobs(args.repo", "fly_jobs = None and _jobs(args.repo"),
    ("M11-main-drop-failing-guard", "                and failing_jobs(jobs)):", "                ):"),
    ("M12-main-drop-concluded-guard", "if (in_flight is not None and concluded is not None\n",
     "if (in_flight is not None\n"),
    ("M13-main-drop-inner-except",
     "            except Unreadable:\n                fly_jobs = None  # no jobs yet",
     "            except ZeroDivisionError:\n                fly_jobs = None  # no jobs yet"),
    ("M14-main-wrong-run", 'fly_jobs = _jobs(args.repo, in_flight["id"],',
     'fly_jobs = _jobs(args.repo, concluded["id"],'),
    ("M15-main-not-passed", "record,\n            fly_jobs)", "record,\n            None)"),
    ("M16-main-guard-inverted", "if (in_flight is not None and concluded",
     "if (in_flight is None and concluded"),
]

SLICE = r'''
import sys
sys.path.insert(0, sys.argv[1])
src = open(sys.argv[2]).read()
code = (src[src.index("_NS_NOW = datetime(2026, 9, 10"):src.index("_NS_LAST_NIGHT =")]
        + src[src.index("# --- a failure a newer in-flight run"):
              src.index("# --- a run with no clock")])
class R:
    failed = []
    @staticmethod
    def check(name, ok, detail=""):
        if not ok:
            R.failed.append(name)
import contextlib as _contextlib, io as _io, os
from datetime import UTC, datetime, timedelta
import nightly_status as _nstatus
exec(code, dict(globals()))
print("checks failed:", R.failed)
sys.exit(1 if R.failed else 0)
'''


def run(code_dir: str, entities: pathlib.Path) -> int:
    return subprocess.run([sys.executable, "-I", "-c", SLICE, code_dir, str(entities)],
                          capture_output=True, text=True).returncode


def main() -> int:
    check_tree, code_tree = map(pathlib.Path, sys.argv[1:3])
    entities = check_tree / "tests/entities.py"
    src = (code_tree / "tests/nightly_status.py").read_text()
    print(f"RESULT unmutated rc={run(str(code_tree / 'tests'), entities)}")
    killed = 0
    with tempfile.TemporaryDirectory() as tmp:
        for label, old, new in MUTANTS:
            if src.count(old) != 1:
                print(f"RESULT {label} NOT-APPLICABLE (site count {src.count(old)})")
                continue
            d = os.path.join(tmp, label)
            os.makedirs(d)
            pathlib.Path(d, "nightly_status.py").write_text(src.replace(old, new))
            rc = run(d, entities)
            killed += rc != 0
            print(f"RESULT {label} rc={rc} {'KILLED' if rc else 'SURVIVED'}")
    print(f"RESULT killed={killed}/{len(MUTANTS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
