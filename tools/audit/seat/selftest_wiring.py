#!/usr/bin/env python3
"""Refuse a self-testing tool that no CI step runs.

    python3 -I tools/audit/seat/selftest_wiring.py --check
    python3 -I tools/audit/seat/selftest_wiring.py --self-test

WHY THIS EXISTS. `tools/` is INERT in tests/closure.py, so the scoped gate
never selects a tool, and a self-test runs in CI only if a workflow step names
it. When R10-TICK-SELFTEST-CI was cut, 24 of the 32 self-testing files under
`tools/audit/seat/` were named in no workflow. The orchestrator tick was one of
them: #2406 removed a symbol it read, and the crash was first seen in review on
#2422. #2444 then found seven self-tests outside that directory in the same
position, so the rule covers all of `tools/` (#2444's forward-carry).

THE RULE. A file under tools/ (not *.md or *.json) is SELF-TESTING when its
text matches `--self-test` or `self-test)` (a case arm). It is WIRED when some
step of a .github/workflows/*.yml file has a `run:` line, with comments
removed, naming `tools/<path>` and then `self-test` later on that same line.
Comments are removed the way the shell reads them: from a `#` that starts the
line or follows whitespace, to the line's end. The `self-test` must follow the
path within the same command (before the next tools path, `;`, `&` or `|`). So
a comment, a step name, an `env:` value, or a run line that names the file
without its self-test (a `--check` call) does not wire it. Stripping a `#`
inside a quoted string can only make a file read unwired, never wired.

Blind spots, stated: a self-test whose entry point is spelled neither way;
a step that never runs (`if: false`, a job no event triggers); a step whose
exit is ignored (`continue-on-error`, `|| true`).
"""
from __future__ import annotations

import contextlib
import io
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLS = "tools"
SEAT = "tools/audit/seat"
SELF_TEST_RE = re.compile(r"--self-test|self-test\)")
RUN_RE = re.compile(r"^(?P<indent>\s*)(?:-\s+)?run:\s*(?P<rest>.*)$")
COMMENT_RE = re.compile(r"(?:^|(?<=\s))#.*$")


def self_testing(root: Path) -> list[str]:
    """Every self-testing file under tools/, relative to it."""
    out: list[str] = []
    for p in sorted((root / TOOLS).rglob("*")):
        if (not p.is_file() or "__pycache__" in p.parts
                or p.suffix in (".md", ".json")):
            continue
        if SELF_TEST_RE.search(p.read_text(errors="replace")):
            out.append(p.relative_to(root / TOOLS).as_posix())
    return out


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
    the path, before the next tools path or a `;`, `&` or `|`."""
    found: set[str] = set()
    path = re.compile(re.escape(TOOLS) + r"/([\w./-]+)")
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
        print(f"  UNWIRED {TOOLS}/{name}: no workflow run line names its self-test")
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
        (root / ".github" / "workflows").mkdir(parents=True)
        (root / ".github" / "workflows" / "ci.yml").write_text(workflow)
        for name, body in files.items():
            p = root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body)
        return root

    seat = "tools/audit/seat"
    st = {f"{seat}/a.py": "if argv == ['--self-test']: pass\n"}
    head = "jobs:\n  j:\n    steps:\n"
    cases = [
        ("an inline run line wires it (null control)", True,
         head + f"      - run: python3 -I {seat}/a.py --self-test\n"),
        ("a block run line wires it (null control)", True,
         head + "      - name: x\n        run: |\n          set -o pipefail\n"
         f"          python3 {seat}/a.py --self-test | tee t\n"),
        ("a comment line naming it does not", False,
         head + f"      # python3 {seat}/a.py --self-test\n      - run: true\n"),
        ("a shell comment inside the run block does not", False,
         head + "      - run: |\n"
         f"          # {seat}/a.py --self-test\n          true\n"),
        ("a trailing comment on a run line does not", False,
         head + f"      - run: true  # {seat}/a.py --self-test\n"),
        ("a run line naming it without its self-test does not", False,
         head + f"      - run: python3 {seat}/a.py --check\n"),
        ("a step name naming it does not", False,
         head + f"      - name: {seat}/a.py --self-test\n        run: true\n"),
        ("a basename alone does not (the rule wants the path)", False,
         head + f"      - run: cd {seat} && python3 a.py --self-test\n"),
        ("a sibling's self-test on the line does not wire it", False,
         head + f"      - run: python3 {seat}/ab.py --self-test\n"),
        ("a self-test that belongs to the next command on the line does not", False,
         head + f"      - run: python3 {seat}/a.py --check; {seat}/b.sh --self-test\n"),
        ("nor one after a pipe", False,
         head + f"      - run: python3 {seat}/a.py | grep self-test\n"),
        ("the block ends at its indentation: a later step's text is not run", False,
         head + "      - run: |\n          true\n      - name: n\n"
         f"        env:\n          X: {seat}/a.py --self-test\n"),
    ]
    for name, want, wf in cases:
        _, unwired = check(tree(wf, st))
        ck(name, (unwired == []) == want)
    # The widened scope: a file outside the seat directory, and a nested one
    # under it, are wired by the same rule, and an unmentioned one is not.
    for name, want, rel, wf in (
        ("a file outside tools/audit/seat/ is wired by its run line", True,
         "tools/pr/head_note.py",
         head + "      - run: python3 -I tools/pr/head_note.py --self-test\n"),
        ("a nested file is wired by its run line", True,
         "tools/policy/record-predicate/x.py",
         head + "      - run: python3 -I tools/policy/record-predicate/x.py --self-test\n"),
        ("a file under another tools/ directory with no run line is unwired", False,
         "tools/coverage/partition.py", head + "      - run: true\n"),
    ):
        _, unwired = check(tree(wf, {rel: "if argv == ['--self-test']: pass\n"}))
        ck(name, (unwired == []) == want)
    tests, unwired = check(tree(head + "      - run: true\n", {
        **st,
        f"{seat}/b.sh": "case $1 in --self-test) ;; esac\n",
        f"{seat}/c.sh": "self-test) exit 0 ;;\n",
        f"{seat}/d.py": "print('no entry point')\n",
        f"{seat}/e.md": "--self-test\n",
        "tools/pr/f.py": "if argv == ['--self-test']: pass\n",
        "tools/policy/g.json": "--self-test\n",
        "tools/coverage/__pycache__/h.py": "--self-test\n",
    }))
    ck("the enumeration takes --self-test and a case arm at any tools/ path, "
       "not a file without one, a .md or .json, or a __pycache__ file",
       tests == ["audit/seat/a.py", "audit/seat/b.sh", "audit/seat/c.sh", "pr/f.py"]
       and unwired == tests)
    # The refusal is report()'s exit code, which `--check` returns: grade it,
    # not only check()'s list (a `return 0` there passed every check above).
    for name, want, wf in ((
            "--check exits 1 on an unwired file", 1, head + "      - run: true\n"), (
            "--check exits 0 when every file is wired (null control)", 0,
            head + f"      - run: python3 -I {seat}/a.py --self-test\n")):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = report(tree(wf, st))
        ck(f"{name} (rc={rc})", rc == want
           and f", {want} unwired" in out.getvalue())
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
