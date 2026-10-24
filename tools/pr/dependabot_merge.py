#!/usr/bin/env python3
"""What .github/workflows/dependabot-automerge.yml does with one Dependabot PR.

    python3 -I tools/pr/dependabot_merge.py decide --update-type T
    python3 -I tools/pr/dependabot_merge.py owned --codeowners F --paths F
    python3 -I tools/pr/dependabot_merge.py --self-test

`decide` prints `merge` for a semver patch or minor update (fetch-metadata's
`update-type`, the group's highest) and `leave <why>` for anything else: a
major, or an update type fetch-metadata could not name, is a seat's review.
A security update is judged by the same rule: a major security bump is still
left (the workflow cannot read Dependabot alerts with its token, and a major
is a major).

`owned` prints the changed paths CODEOWNERS gives an owner, one per line. The
workflow approves only when it prints nothing: decision 0011 has the
hpo-approver App approve non-code-owned pull requests and only @tvofi review
code-owned ones, so a code-owned bump gets auto-merge armed and waits for him.
CODEOWNERS here is anchored paths only (`/dir/` or `/file`, no globs); the
last matching line wins and a line with no owner un-owns, as GitHub reads it.
A glob, which this reader does not model, refuses rather than guesses.
"""
from __future__ import annotations

import sys
from pathlib import Path

MERGEABLE = {"version-update:semver-patch", "version-update:semver-minor"}


def decide(update_type: str) -> str:
    t = (update_type or "").strip()
    if t in MERGEABLE:
        return "merge"
    if t == "version-update:semver-major":
        return "leave a major update is a seat's review"
    return f"leave update type {t or '(none)'} is not a patch or minor"


def rules(codeowners: str) -> list[tuple[str, bool]]:
    """(anchored pattern, has owner) per CODEOWNERS line, in file order."""
    out = []
    for raw in codeowners.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        pat, *owners = line.split()
        if not pat.startswith("/") or any(c in pat for c in "*?["):
            raise ValueError(f"CODEOWNERS pattern {pat!r} is not an anchored path; this reader refuses it")
        out.append((pat[1:], bool(owners)))
    return out


def owned(codeowners: str, paths: list[str]) -> list[str]:
    rs = rules(codeowners)
    hit = []
    for p in paths:
        last = None
        for pat, has in rs:
            if p == pat or (pat.endswith("/") and p.startswith(pat)):
                last = has
        if last:
            hit.append(p)
    return hit


def self_test() -> int:
    bad = []

    def check(name, got, want):
        print(f"  {'ok  ' if got == want else 'FAIL'}  {name}" + ("" if got == want else f": {got!r} != {want!r}"))
        if got != want:
            bad.append(name)

    check("patch merges", decide("version-update:semver-patch"), "merge")
    check("minor merges", decide("version-update:semver-minor"), "merge")
    check("major is left", decide("version-update:semver-major").split()[0], "leave")
    check("no update type is left", decide("").split()[0], "leave")
    co = "/.github/workflows/  @tvofi\n/tools/site/ @tvofi\n/tools/audit/briefs/ @tvofi\n/tools/audit/briefs/COMMON.md\n"
    check("an owned directory", owned(co, [".github/workflows/any.yml"]), [".github/workflows/any.yml"])
    check("an unowned manifest (the null control)", owned(co, ["tests/requirements-any.txt"]), [])
    check("a later owner-less line un-owns", owned(co, ["tools/audit/briefs/COMMON.md"]), [])
    check("a prefix is a directory, not a name stem", owned(co, ["tools/sitemap.txt"]), [])
    try:
        owned("*.js @x\n", ["a.js"])
        check("a glob refuses", "accepted", "refused")
    except ValueError:
        check("a glob refuses", "refused", "refused")
    real = Path(__file__).resolve().parents[2] / ".github" / "CODEOWNERS"
    if real.is_file():
        check("the tree's CODEOWNERS parses", bool(rules(real.read_text())), True)
        check("the tree's CODEOWNERS owns workflows, not the pip locks",
              owned(real.read_text(), [".github/workflows/any.yml", "tests/requirements-any.txt"]),
              [".github/workflows/any.yml"])
    print(f"dependabot_merge self-test: {len(bad)} failure(s)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    if len(argv) == 3 and argv[:2] == ["decide", "--update-type"]:
        print(decide(argv[2]))
        return 0
    if len(argv) == 5 and argv[0] == "owned" and argv[1] == "--codeowners" and argv[3] == "--paths":
        paths = [x.strip() for x in Path(argv[4]).read_text().splitlines() if x.strip()]
        if not paths:
            print("refused: the changed-path list is empty", file=sys.stderr)
            return 2
        try:
            for p in owned(Path(argv[2]).read_text(), paths):
                print(p)
        except ValueError as e:
            print(f"refused: {e}", file=sys.stderr)
            return 2
        return 0
    print(__doc__.split("\n\n")[1], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
