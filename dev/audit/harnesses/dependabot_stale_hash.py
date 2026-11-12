#!/usr/bin/env python3
"""Census of stale --hash blocks in a commit's hash-locked requirement files.

A pin is STALE when its `name==version` line moved from the parent commit
but its set of `--hash=sha256:` values did not: distinct releases never
share a distribution digest, so an unchanged hash set under a new version
is the previous version's hashes (dev/audit/rca/r10-rca-dependabot-stale-hash.md).

    python3 dev/audit/harnesses/dependabot_stale_hash.py <commit> [<commit> ...]

Each commit is compared with its first parent over every `tests/requirements*.txt`
it changed.  Prints one `stale` line per stale pin and a `summary` line per
commit: moved = pins whose version changed, stale = moved pins whose hash set
did not.  Exit 1 when any commit carries a stale pin, 0 otherwise.
`--tree [<rev>]` lists the precondition instead (default: the working tree):
every comment line of a hash-locked file that names a pinned package as
`name==`, the shape whose rewrite marked all 9 stale pins of #3088, #3323
and #3414; exit 1 when any exists.
`--self-test` drives both modes over fabricated text, both directions.
"""
from __future__ import annotations

import re
import subprocess
import sys

PIN = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[^\]]*\])?==([^\s;\\]+)")
HASH = re.compile(r"--hash=sha256:([0-9a-f]{64})")


def parse(text: str) -> dict[str, tuple[str, frozenset[str]]]:
    """Map a normalised package name to (version, hash set)."""
    pins: dict[str, tuple[str, frozenset[str]]] = {}
    name = version = None
    hashes: set[str] = set()
    for line in text.splitlines():
        match = PIN.match(line)
        if match:
            if name is not None:
                pins[name] = (version, frozenset(hashes))
            name = re.sub(r"[-_.]+", "-", match.group(1)).lower()
            version, hashes = match.group(2), set()
        hashes.update(HASH.findall(line))
    if name is not None:
        pins[name] = (version, frozenset(hashes))
    return pins


def stale_pins(old: str, new: str) -> tuple[int, list[tuple[str, str, str]]]:
    """Return (moved count, [(name, old version, new version)] stale)."""
    before, after = parse(old), parse(new)
    moved = 0
    stale = []
    for name, (version, hashes) in sorted(after.items()):
        if name not in before or before[name][0] == version:
            continue
        moved += 1
        if hashes and hashes == before[name][1]:
            stale.append((name, before[name][0], version))
    return moved, stale


def exposed(text: str) -> list[tuple[str, str]]:
    """Return (package, comment line) for each comment naming a pin as `name==`."""
    names = [n for n, (_, hashes) in parse(text).items() if hashes]
    hits = []
    for line in text.splitlines():
        if not line.lstrip().startswith("#"):
            continue
        for name in names:
            spelled = r"[-_.]+".join(map(re.escape, re.split(r"[-_.]+", name)))
            if re.search(rf"(?i)(?<![\w.-]){spelled}(\[[^\]]*\])?\s*==", line):
                hits.append((name, line.strip()))
    return hits


def tree(rev: str | None) -> int:
    if rev:
        paths = git("ls-tree", "-r", "--name-only", rev, "tests/").split()
    else:
        paths = git("ls-files", "tests/").split()
    paths = [p for p in paths if re.fullmatch(r"tests/requirements[^/]*\.txt", p)]
    total = 0
    for path in paths:
        text = show(rev, path) if rev else open(path, encoding="utf-8").read()
        for name, line in exposed(text):
            total += 1
            print(f"exposed {path} {name}: {line}")
    print(f"summary tree={rev or 'worktree'} files={len(paths)} exposed={total}")
    return total


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], check=True, capture_output=True, text=True
    ).stdout


def show(rev: str, path: str) -> str:
    try:
        return git("show", f"{rev}:{path}")
    except subprocess.CalledProcessError:
        return ""


def census(commit: str) -> int:
    paths = [
        p
        for p in git("diff", "--name-only", f"{commit}^", commit).split()
        if re.fullmatch(r"tests/requirements[^/]*\.txt", p)
    ]
    moved_total = stale_total = 0
    for path in paths:
        moved, stale = stale_pins(show(f"{commit}^", path), show(commit, path))
        moved_total += moved
        stale_total += len(stale)
        for name, old, new in stale:
            print(f"stale {commit[:10]} {path} {name} {old} -> {new}")
    print(
        f"summary {commit[:10]} files={len(paths)} moved={moved_total} "
        f"stale={stale_total}"
    )
    return stale_total


def self_test() -> int:
    a, b, c = "a" * 64, "b" * 64, "c" * 64
    old = f"foo==1.0 \\\n    --hash=sha256:{a}\nbar==2.0 \\\n    --hash=sha256:{b}\n"
    fresh = f"foo==1.1 \\\n    --hash=sha256:{c}\nbar==2.0 \\\n    --hash=sha256:{b}\n"
    stale = f"foo==1.1 \\\n    --hash=sha256:{a}\nbar==2.0 \\\n    --hash=sha256:{b}\n"
    ok = stale_pins(old, fresh) == (1, []) and stale_pins(old, stale) == (
        1,
        [("foo", "1.0", "1.1")],
    )
    head = "# <overrides> holds Foo==1.0 and bar 2.0\n"
    ok = ok and [n for n, _ in exposed(head + old)] == ["foo"]
    ok = ok and exposed("# foo 1.0 and bar 2.0\n" + old) == []
    print("self-test", "OK" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    if argv[:1] == ["--tree"] and len(argv) <= 2:
        return 1 if tree(argv[1] if len(argv) == 2 else None) else 0
    if not argv:
        print(__doc__)
        return 2
    return 1 if sum(census(rev) for rev in argv) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
