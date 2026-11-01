#!/usr/bin/env python3
"""Refuse a bare `"${name[@]}"` in a tracked tools/ shell script that runs under `set -u`.

    python3 -I tools/audit/seat/bare_array.py --check [--ref <commit>]
    python3 -I tools/audit/seat/bare_array.py --self-test

WHY. macOS /bin/bash 3.2 rejects the expansion of an EMPTY array under `set -u`
(`name[@]: unbound variable`); bash 4.4+ and so CI's bash 5 expand it cleanly.
A run-time test on CI therefore passes on the defect, and the rule that
`bus.sh`, `body_push.sh` and `seat_venv.sh` each state in prose did not stop
`bus.sh orphans` (`"${arms[@]}"`, R10-FLY-ORPHANS-REWRITTEN) from dying on the
operator's machine (triage P303). This is the static half.

THE RULE, per file: a file with a `set` command carrying the `u` option is
judged; a file without one is not. In a judged file, each non-comment line is
refused for every `"${name[@]}"` that is not the guarded form
`${name[@]+"${name[@]}"}`, unless `# never-empty: <reason>` with a reason,
stating why the array cannot be empty there, sits on the line itself or on a
comment-only line directly above it. A line that ends in a `# mut:<name>`
marker takes the reason on the line above: its self-test finds the mutant line
by that marker at the line's end (`pr_args.sh`'s header), so a reason appended
after the marker unanchors the mutant: such a line is refused in every file,
judged or not (`pr_args.sh` has no `set -u` and is sourced by scripts that do). `"${name[*]}"`, `${#name[@]}` and `"${name[@]:...}"` are not matched.
The `set -u` test is textual and file-wide: a `set +u` window is not modelled,
so a site inside one takes the marker too.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

SET_U = re.compile(r"^\s*set\s+(?:-[A-Za-z]*u[A-Za-z]*|-o\s+nounset)\b", re.M)
BARE = re.compile(r'"\$\{([A-Za-z_]\w*)\[@\]\}"')
MARK = re.compile(r"#\s*never-empty:\s*\S")
MUT = re.compile(r"#\s*mut:\S")


def marked(line: str) -> bool:
    """The line's own never-empty reason, unless it follows a `# mut:` marker."""
    mark, mut = MARK.search(line), MUT.search(line)
    return bool(mark) and not (mut and mut.start() < mark.start())


def sites(text: str) -> list[tuple[int, str]]:
    """(line number, line) of each refused expansion in one script's text."""
    lines = text.splitlines()
    # A reason after a mut marker is refused in every file, judged or not.
    out = {n for n, ln in enumerate(lines, 1) if MARK.search(ln) and not marked(ln)}
    if SET_U.search(text):
        above = False  # the previous line is a comment-only never-empty reason
        for n, line in enumerate(lines, 1):
            comment = line.lstrip().startswith("#")
            excused, above = above, comment and bool(MARK.search(line))
            if comment or excused or marked(line):
                continue
            for m in BARE.finditer(line):
                if not line[: m.start()].endswith("${%s[@]+" % m.group(1)):
                    out.add(n)
                    break
    return [(n, lines[n - 1].strip()) for n in sorted(out)]


def scan(ref: str | None = None) -> list[str]:
    """`path:line: text` per refused site across tracked tools/**/*.sh."""
    root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    if ref:
        names = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", ref, "--", "tools"], text=True, cwd=root).split()
    else:
        names = subprocess.check_output(
            ["git", "ls-files", "--", "tools"], text=True, cwd=root).split()
    out = []
    for p in sorted(n for n in names if n.endswith(".sh")):
        if ref:
            text = subprocess.check_output(["git", "show", f"{ref}:{p}"], text=True, cwd=root)
        else:
            text = (Path(root) / p).read_text()
        out += [f"{p}:{n}: {t}" for n, t in sites(text)]
    return out


def self_test() -> int:
    fails = []

    def st(got, want, name):
        if got != want:
            fails.append(f"{name}: got {got!r}, want {want!r}")

    head = "#!/bin/bash\nset -uo pipefail\n"
    bare = head + 'f "${arms[@]}" x\n'
    st(len(sites(bare)), 1, "a bare expansion under set -u is refused")
    st(sites(head + 'f ${arms[@]+"${arms[@]}"} x\n'), [], "the guarded form passes")
    st(sites(head + 'f "${a[@]}" # never-empty: argv of this script, checked above\n'), [],
       "an allow-marked never-empty site passes (null)")
    st(len(sites(head + 'f "${a[@]}" # never-empty:\n')), 1, "a marker with no reason does not excuse")
    st(sites('#!/bin/bash\nset -e\nf "${a[@]}"\n'), [], "a file without set -u is not judged (null)")
    st(len(sites('set -euo pipefail\nf "${a[@]}"\n')), 1, "set -euo counts as set -u")
    st(sites(head + '# f "${a[@]}"\n'), [], "a comment line is skipped")
    st(len(sites(head + 'f ${b[@]+"${b[@]}"} "${a[@]}"\n')), 1,
       "a guard on one array does not excuse another on the line")
    st(len(sites(head + 'f ${b[@]+"${a[@]}"}\n')), 1, "a guard names its own array")
    st(sites(head + 'n=${#a[@]}; f "${a[*]}"\n'), [], "length and star forms are not matched")
    st(sites(head + '# never-empty: argv, checked above\nf "${a[@]}"  # mut:x\n'), [],
       "a reason on the comment line above excuses the next line (null)")
    st(len(sites(head + '# never-empty: argv\n\nf "${a[@]}"\n')), 1,
       "a reason above excuses only the line directly below it")
    st(len(sites(head + 'f "${a[@]}"  # mut:x  # never-empty: argv\n')), 1,
       "a reason after a mut marker does not excuse: it unanchors the mutant")
    st(sites(head + 'f "${a[@]}"  # never-empty: argv  # mut:x\n'), [],
       "a reason before the mut marker excuses (null)")
    st(len(sites('#!/bin/bash\nf x  # mut:x  # never-empty: argv\n')), 1,
       "a reason after a mut marker is refused in an unjudged file too")
    st(len(sites(head + 'f x  # mut:x  # never-empty: argv\n')), 1,
       "a reason after a mut marker is refused in a judged file on a line with no bare expansion")
    st(len(sites(head + 'f ${a[@]+"${a[@]}"}  # mut:x  # never-empty: argv\n')), 1,
       "a reason after a mut marker is refused in a judged file on a guarded line")
    st(sites(head + 'f x  # never-empty: argv  # mut:x\n'), [],
       "a judged file's non-bare line with the reason before the marker passes (null)")
    for f in fails:
        print("FAIL", f)
    print("bare_array self-test:", "FAILED" if fails else "ok")
    return 1 if fails else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    if "--check" in sys.argv:
        ref = sys.argv[sys.argv.index("--ref") + 1] if "--ref" in sys.argv else None
        hits = scan(ref)
        print("\n".join(hits))
        sys.exit(1 if hits else 0)
    print(__doc__)
    sys.exit(2)
