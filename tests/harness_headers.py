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

# Cheap, contention-immune. The issue's header-drift set that can run here.
EXECUTE = (
    "tools/audit/round3/D2/dst_window_factors.py",
    "tools/audit/round3/D2/window_size_sweep.py",
    "tools/audit/round3/D5/option_doc_coverage.py",
)


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
    p = subprocess.run(
        [sys.executable, rel],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
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
