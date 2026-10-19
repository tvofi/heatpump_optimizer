#!/usr/bin/env python3
"""Refuse a self-testing seat instrument that no CI step runs.

    python3 -I tools/audit/seat/selftest_wiring.py --check
    python3 -I tools/audit/seat/selftest_wiring.py --self-test

WHY THIS EXISTS. `tools/audit/` is INERT in tests/closure.py, so the scoped
gate never selects a seat instrument, and a self-test runs in CI only if a
workflow step names it. When R10-TICK-SELFTEST-CI was cut, 24 of the 32
self-testing files here were named in no workflow. The orchestrator tick was
one of them: #2406 removed a symbol it read, and the crash was first seen in
review on #2422.

THE RULE. A file directly under tools/audit/seat/ (not *.md) is
SELF-TESTING when its text matches `--self-test` or `self-test)` (a case arm).
It is WIRED when some step of a .github/workflows/*.yml file has a `run:`
line, with comments removed, naming `tools/audit/seat/<file>` and then
`self-test` later on that same line. Comments are removed the way the shell
reads them: from a `#` that starts the line or follows whitespace, to the
line's end. The `self-test` must follow the path within the same command
(before the next seat path, `;`, `&` or `|`). So a comment, a step name, an `env:` value, or a run line that
names the file without its self-test (a `--check` call) does not wire it.
Stripping a `#` inside a quoted string can only make a file read unwired,
never wired.

Blind spots, stated: a self-test whose entry point is spelled neither way;
a step that never runs (`if: false`, a job no event triggers); a step whose
exit is ignored (`continue-on-error`, `|| true`).
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SEAT = "tools/audit/seat"
SELF_TEST_RE = re.compile(r"--self-test|self-test\)")
RUN_RE = re.compile(r"^(?P<indent>\s*)(?:-\s+)?run:\s*(?P<rest>.*)$")
COMMENT_RE = re.compile(r"(?:^|(?<=\s))#.*$")


def self_testing(root: Path) -> list[str]:
    seat = root / SEAT
    return sorted(
        p.name for p in seat.iterdir()
        if p.is_file() and p.suffix != ".md"
        and SELF_TEST_RE.search(p.read_text(errors="replace")))


def run_lines(workflow: str) -> list[str]:
    """Every line of every `run:` value, comments removed."""
    out: list[str] = []
    lines = workflow.splitlines()
    i = 0
    while i < len(lines):
        m = RUN_RE.match(lines[i])
        i += 1
        if not m:
            continue
        rest = m.group("rest")
        if not re.fullmatch(r"[|>][-+0-9]*\s*(?:#.*)?", rest):
            out.append(rest)
            continue
        key_col = lines[i - 1].index("run:")
        while i < len(lines) and (not lines[i].strip()
                                  or len(lines[i]) - len(lines[i].lstrip()) > key_col):
            out.append(lines[i])
            i += 1
    return [COMMENT_RE.sub("", x) for x in out]


def wired(root: Path) -> set[str]:
    """Files a run line invokes with `self-test` in the same command: after
    the path, before the next seat path or a `;`, `&` or `|`."""
    found: set[str] = set()
    path = re.compile(re.escape(SEAT) + r"/([\w.-]+)")
    for wf in sorted((root / ".github" / "workflows").glob("*.yml")):
        for line in run_lines(wf.read_text()):
            hits = list(path.finditer(line))
            for k, m in enumerate(hits):
                end = hits[k + 1].start() if k + 1 < len(hits) else len(line)
                if re.match(r"[^;&|]*?\bself-test\b", line[m.end():end]):
                    found.add(m.group(1))
    return found


def check(root: Path) -> tuple[list[str], list[str]]:
    tests = self_testing(root)
    w = wired(root)
    return tests, [t for t in tests if t not in w]


def report(root: Path) -> int:
    tests, unwired = check(root)
    for name in unwired:
        print(f"  UNWIRED {SEAT}/{name}: no workflow run line names its self-test")
    print(f"selftest_wiring: {len(tests)} self-testing, "
          f"{len(tests) - len(unwired)} wired, {len(unwired)} unwired")
    return 1 if unwired else 0


def self_test() -> int:
    passed = failed = 0

    def ck(name: str, ok: bool) -> None:
        nonlocal passed, failed
        passed, failed = passed + ok, failed + (not ok)
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")

    def tree(workflow: str, files: dict[str, str]) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / SEAT).mkdir(parents=True)
        (root / ".github" / "workflows").mkdir(parents=True)
        (root / ".github" / "workflows" / "ci.yml").write_text(workflow)
        for name, body in files.items():
            (root / SEAT / name).write_text(body)
        return root

    st = {"a.py": "if argv == ['--self-test']: pass\n"}
    head = "jobs:\n  j:\n    steps:\n"
    cases = [
        ("an inline run line wires it (null control)", True,
         head + "      - run: python3 -I tools/audit/seat/a.py --self-test\n"),
        ("a block run line wires it (null control)", True,
         head + "      - name: x\n        run: |\n          set -o pipefail\n"
         "          python3 tools/audit/seat/a.py --self-test | tee t\n"),
        ("a comment line naming it does not", False,
         head + "      # python3 tools/audit/seat/a.py --self-test\n      - run: true\n"),
        ("a shell comment inside the run block does not", False,
         head + "      - run: |\n          # tools/audit/seat/a.py --self-test\n          true\n"),
        ("a trailing comment on a run line does not", False,
         head + "      - run: true  # tools/audit/seat/a.py --self-test\n"),
        ("a run line naming it without its self-test does not", False,
         head + "      - run: python3 tools/audit/seat/a.py --check\n"),
        ("a step name naming it does not", False,
         head + "      - name: tools/audit/seat/a.py --self-test\n        run: true\n"),
        ("a basename alone does not (the rule wants the path)", False,
         head + "      - run: cd tools/audit/seat && python3 a.py --self-test\n"),
        ("a sibling's self-test on the line does not wire it", False,
         head + "      - run: python3 tools/audit/seat/ab.py --self-test\n"),
        ("a self-test that belongs to the next command on the line does not", False,
         head + "      - run: python3 tools/audit/seat/a.py --check; tools/audit/seat/b.sh --self-test\n"),
        ("nor one after a pipe", False,
         head + "      - run: python3 tools/audit/seat/a.py | grep self-test\n"),
        ("the block ends at its indentation: a later step's text is not run", False,
         head + "      - run: |\n          true\n      - name: n\n"
         "        env:\n          X: tools/audit/seat/a.py --self-test\n"),
    ]
    for name, want, wf in cases:
        _, unwired = check(tree(wf, st))
        ck(name, (unwired == []) == want)
    tests, unwired = check(tree(head + "      - run: true\n",
                                {**st, "b.sh": "case $1 in --self-test) ;; esac\n",
                                 "c.sh": "self-test) exit 0 ;;\n",
                                 "d.py": "print('no entry point')\n",
                                 "e.md": "--self-test\n"}))
    ck("the enumeration takes --self-test and a case arm, not a file without one "
       "or a .md", tests == ["a.py", "b.sh", "c.sh"] and unwired == tests)
    print(f"selftest_wiring self-test: {passed + failed} checks, {failed} failed")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    if argv == ["--check"]:
        return report(ROOT)
    print(__doc__.split("\n\n")[0], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
