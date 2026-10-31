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
`${name[@]+"${name[@]}"}`, unless the line carries
`# never-empty: <reason>` with a reason, stating why the array cannot be empty
there. `"${name[*]}"`, `${#name[@]}` and `"${name[@]:...}"` are not matched.
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


def sites(text: str) -> list[tuple[int, str]]:
    """(line number, line) of each refused expansion in one script's text."""
    if not SET_U.search(text):
        return []
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("#") or MARK.search(line):
            continue
        for m in BARE.finditer(line):
            if not line[: m.start()].endswith("${%s[@]+" % m.group(1)):
                out.append((n, line.strip()))
                break
    return out


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
