#!/usr/bin/env python3
"""#817: a harness header's EXPECTED RESULT lines must match what it prints.

The headers are hand-maintained. Round 3's judge discarded sound instruments
because a header disagreed with the run. This script executes the cheap
harnesses that issue named and compares each EXPECTED RESULT to the printed
RESULT. Playwright and stress harnesses are not run here.

    PYTHONPATH=tests/hastub:custom_components:tests python3 tests/harness_headers.py
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "tests")
from harness import Results

R = Results("harness header EXPECTED vs RESULT (#817)")

ROOT = Path(__file__).resolve().parents[1]
RESULT = re.compile(r"RESULT\s+([A-Za-z0-9_]+)=(\S+)")
SKIP = {"thread_factor", "load1", "swapins", "concurrent_stress_procs"}

# Every harness whose header carries EXPECTED RESULT lines is executed and
# its printed numbers compared against the header. The static tuple this
# replaced named three files, and a fourth harness drifted on main for a day
# behind that limit (#987's review of the claims.py header): a header nobody
# executes is a header nobody re-records. Discovery is dynamic so a harness
# with a RESULT header joins the check the moment it lands. Populated after
# expected_from below. #951's qs_rules.py joins via its live-header marker;
# its declared_mismatch line is the quality-scale register's drift alarm, and
# its two coverage-bearing rows are pinned by tests/entities.py against
# tests/coverage_budgets.json instead (they need a coverage payload).


def expected_from(path: Path) -> dict[str, str]:
    text = path.read_text()
    # Header only: stop at the first import / from that is not inside the
    # opening docstring or comment block.
    head = []
    in_doc = False
    for line in text.splitlines():
        if line.startswith('"""') or line.startswith("'''"):
            in_doc = not in_doc or line.count('"""') == 1 or line.count("'''") == 1
            if line.strip() in ('"""', "'''") and head:
                in_doc = False
            head.append(line)
            continue
        if in_doc or line.startswith("#") or line.startswith("//"):
            head.append(line)
            continue
        if line.startswith("import ") or line.startswith("from "):
            break
        head.append(line)
    found = {}
    for line in head:
        for m in RESULT.finditer(line):
            if m.group(1) not in SKIP:
                found[m.group(1)] = m.group(2)
    return found


def _discover() -> tuple[str, ...]:
    # A harness header is executed only when the harness declares itself a
    # live instrument: a `live-header` line in the header. The corpus holds
    # two kinds of harness and executing both was measured wrong (#987's
    # review found the drift; extending execution to every header found
    # 30-of-145 red on round 4 alone): finder harnesses are FROZEN EVIDENCE
    # -- their headers record the finding's baseline, so on a fixed main
    # they print the fixed numbers and a forced comparison reds on success
    # -- while a few instruments are MAINTAINED (their keepers re-record
    # the header as the tree moves: claims.py, the D6-03 doc probe). The
    # marker makes that convention executable: a seat that re-records a
    # header as part of a fix marks the harness live, and from then on the
    # gate notices the next drift itself.
    live = {
        "tools/audit/round3/D2/dst_window_factors.py",
        "tools/audit/round3/D2/window_size_sweep.py",
        "tools/audit/round3/D5/option_doc_coverage.py",
    }
    marked = tuple(
        sorted(
            str(p.relative_to(ROOT))
            for p in (ROOT / "tools" / "audit").glob("round*/D*/*.py")
            if p.name != "__init__.py"
            and "live-header" in p.read_text()[:4000]
            and p.relative_to(ROOT).as_posix() not in live
        )
    )
    return tuple(sorted(live)) + marked


EXECUTE = _discover()


def printed_from(stdout: str) -> dict[str, str]:
    found = {}
    for line in stdout.splitlines():
        m = RESULT.search(line)
        if m and m.group(1) not in SKIP:
            found[m.group(1)] = m.group(2)
    return found


def run_harness(rel: str) -> str:
    env = dict(os.environ)
    env["PYTHONPATH"] = "tests/hastub:custom_components:tests"
    # 240 s, raised from 120 with h7_memory_gate.py's live-header marker
    # (#1005's review follow-up): the constant exists for hang detection,
    # not runtime policing, and 120 was set when the slowest executed
    # harness declared "< 5 s". h7 probes through the stress gate's own
    # subprocess entry points, two of its three arms being full
    # build_case runs of the recorded attributable-RSS leader -- 59.8 s
    # total, CPU-bound (user 58.9), on the seat that measured at load1
    # 2.1 -- so 120 sat at ~2x the measured runtime and a 1.5-2.5x-slower
    # CI core crosses it: a spurious red on every pull request. 240
    # restores the margin for the runner class without weakening hang
    # detection anywhere else.
    p = subprocess.run(
        [sys.executable, rel],
        cwd=ROOT,
        env=env,
        shell=False,
        capture_output=True,
        text=True,
        timeout=240,
    )
    R.check(
        f"{rel} exits 0",
        p.returncode == 0,
        f"rc={p.returncode} stderr={p.stderr[-300:]}",
    )
    return p.stdout


def main() -> int:
    for rel in EXECUTE:
        path = ROOT / rel
        R.check(f"{rel} exists", path.is_file(), rel)
        exp = expected_from(path)
        R.check(
            f"{rel} header names at least one EXPECTED RESULT",
            bool(exp),
            "header has no RESULT name=value the checker can execute",
        )
        out = run_harness(rel)
        got = printed_from(out)
        for name, want in exp.items():
            R.check(
                f"{rel} RESULT {name} matches header",
                got.get(name) == want,
                f"header={want!r} printed={got.get(name)!r}",
            )
    return R.close("HARNESS HEADER CHECKS")


if __name__ == "__main__":
    raise SystemExit(main())
