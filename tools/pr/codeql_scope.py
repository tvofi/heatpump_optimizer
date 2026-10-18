#!/usr/bin/env python3
"""Decide whether one CodeQL leg may skip a pull request whose diff it cannot read.

    python3 -I tools/pr/codeql_scope.py changed --base BASE --head HEAD > CHANGED.txt
    python3 -I tools/pr/codeql_scope.py decide --language LEG --event EVENT \
        --files-from CHANGED.txt
    python3 -I tools/pr/codeql_scope.py --self-test

`decide` prints one word on stdout, `analyze` or `skip`, and its reason on
stderr. `.github/workflows/codeql.yml`'s `scope` job runs it once per leg, and
the leg's init and analyze steps run unless the word is `skip`, so a leg that
skips still reports its required `Analyze (<leg>)` context, as `success`.

WHY (O17, 2026-10-18). A pull request whose diff is a roster or a delivery row
paid `Analyze (python)`'s 23-26 minutes, its critical path, for an analysis
that cannot differ from main's: no file the python extractor reads changed.
That was 76 of the 144 pull requests merged in round 10.

THE RULE, fail-closed in every arm:
  * only `pull_request` may skip. `push`, `schedule`, `merge_group` and
    `workflow_dispatch` always analyze, so main keeps a full analysis of
    every merged tree;
  * a leg skips only when EVERY changed file has a suffix on that leg's
    INERT list -- an allow-list of what the leg's extractor provably never
    reads, never a list of what it does, so an unknown suffix analyzes;
  * a file under `.github/` (workflows, CodeQL configuration) analyzes every
    leg: it changes what the analysis is. This file is `.py`, on no leg's
    INERT list, so editing the decision analyzes every leg too;
  * an empty or unreadable file list analyzes;
  * the list is `changed`'s, with rename detection OFF: porcelain `git diff`
    detects renames by default and lists only a rename's destination, so
    `lib.py` -> `lib.md` would list `lib.md` alone and the python leg would
    skip a tree that lost a module (#2405 round 1). `--no-renames` lists both.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import PurePosixPath

LEGS = ("actions", "javascript-typescript", "python")
SELF = "tools/pr/codeql_scope.py"  # the self-test's: an edit here analyzes
#: What no leg's extractor reads: prose and raster data.
_PROSE = frozenset({".md", ".mdc", ".txt", ".png", ".jpg", ".jpeg", ".gif",
                    ".csv", ".tsv"})
#: Per leg. `.json` is inert to the python and actions extractors, never to
#: javascript-typescript, whose extractor reads JSON (and YAML and HTML).
INERT = {
    "actions": _PROSE | {".json"},
    "javascript-typescript": _PROSE,
    "python": _PROSE | {".json"},
}
FORCE_PREFIXES = (".github/",)


def decide(language: str, event: str, files: list[str]) -> tuple[str, str]:
    """(`analyze` | `skip`, reason) for one leg over one diff."""
    if language not in INERT:
        return "analyze", f"unknown leg {language!r}"
    if event != "pull_request":
        return "analyze", f"event {event!r} always analyzes"
    files = [f.strip() for f in files if f.strip()]
    if not files:
        return "analyze", "no changed file list"
    for f in files:
        if f.startswith(FORCE_PREFIXES):
            return "analyze", f"{f} changes the analysis itself"
        suffix = PurePosixPath(f).suffix.lower()
        if suffix not in INERT[language]:
            return "analyze", f"{f} ({suffix or 'no suffix'}) may be read by the {language} extractor"
    return "skip", f"all {len(files)} changed file(s) are inert to the {language} extractor"


def changed_files(base: str, head: str, cwd: str = ".",
                  env: dict | None = None) -> list[str]:
    """The pull request's three-dot file list, BOTH sides of every rename.
    Raises CalledProcessError when git cannot diff: the caller fails, and a
    failed scope job leaves every leg analyzing."""
    out = subprocess.run(["git", "diff", "--name-only", "--no-renames",
                          f"{base}...{head}"], cwd=cwd, env=env,
                         capture_output=True, text=True, check=True).stdout
    return [line for line in out.splitlines() if line.strip()]


def _rename_probe() -> tuple[list[str], list[str]]:
    """(changed_files, porcelain `git diff --name-only`) over a throwaway repo
    (tests/throwaway_git.py, the one way a tracked script builds one) whose
    one commit is `git mv lib.py lib.md`."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    os.pardir, os.pardir, "tests"))
    from throwaway_git import throwaway_git_init
    with tempfile.TemporaryDirectory() as td:
        env = throwaway_git_init(td, "-q")

        def git(*a: str) -> str:
            return subprocess.run(["git", *a], cwd=td, env=env, capture_output=True,
                                  text=True, check=True).stdout
        with open(os.path.join(td, "lib.py"), "w", encoding="utf-8") as fh:
            fh.write("def sanitize(x):\n    return x.strip()\n" * 20)
        git("add", "-A")
        git("commit", "-qm", "base")
        base = git("rev-parse", "HEAD").strip()
        git("mv", "lib.py", "lib.md")
        git("commit", "-qm", "rename")
        # rename-null-control: porcelain on purpose, the form round 1 shipped.
        porcelain = [l for l in git("diff", "--name-only", f"{base}...HEAD").splitlines() if l]  # rename-null-control
        return changed_files(base, "HEAD", cwd=td, env=env), porcelain


def self_test() -> int:
    fails = n = 0

    def check(name: str, got, want) -> None:
        nonlocal fails, n
        n += 1
        ok = got == want
        fails += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name}" + ("" if ok else f": got {got!r}, want {want!r}"))

    roster = ["dev/programme/rosters/wave-r10-groups.json", "dev/programme/delivery/2380.md"]
    row = ["dev/programme/delivery/2391.md"]
    word = lambda leg, ev, fs: decide(leg, ev, fs)[0]  # noqa: E731

    check("a roster PR skips python", word("python", "pull_request", roster), "skip")
    check("a roster PR skips actions", word("actions", "pull_request", roster), "skip")
    check("a roster PR analyzes javascript-typescript: its extractor reads .json",
          word("javascript-typescript", "pull_request", roster), "analyze")
    for leg in LEGS:
        check(f"a record PR (one .md row) skips {leg}", word(leg, "pull_request", row), "skip")
    check("a .py file analyzes python (null control)",
          word("python", "pull_request", roster + ["tools/audit/seat/roster_lib.py"]), "analyze")
    check("a .mjs file analyzes javascript-typescript (null control)",
          word("javascript-typescript", "pull_request", row + ["tools/policy/brief_lint.mjs"]), "analyze")
    check("a card .js file analyzes javascript-typescript",
          word("javascript-typescript", "pull_request",
               ["custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"]), "analyze")
    check("a .sh file analyzes python: not on the allow-list, so fail-closed",
          word("python", "pull_request", ["tools/pr/prepr.sh"]), "analyze")
    check("a file with no suffix analyzes", word("python", "pull_request", ["VERSION"]), "analyze")
    check("an upper-case suffix is the same suffix", word("python", "pull_request", ["docs/README.MD"]), "skip")
    for leg in LEGS:
        check(f"a workflow edit analyzes {leg}",
              word(leg, "pull_request", row + [".github/workflows/codeql.yml"]), "analyze")
        check(f"a .md under .github/ analyzes {leg}",
              word(leg, "pull_request", [".github/PULL_REQUEST_TEMPLATE.md"]), "analyze")
        check(f"editing this decision analyzes {leg}", word(leg, "pull_request", [SELF]), "analyze")
        for ev in ("push", "schedule", "merge_group", "workflow_dispatch", ""):
            check(f"event {ev or '(none)'} analyzes {leg} on an inert diff", word(leg, ev, row), "analyze")
    check("an empty file list analyzes", word("python", "pull_request", []), "analyze")
    check("a blank-lines-only file list analyzes", word("python", "pull_request", ["", "  "]), "analyze")
    check("an unknown leg analyzes", word("ruby", "pull_request", row), "analyze")
    check("the reason names the file that forced analysis",
          "roster_lib.py" in decide("python", "pull_request", roster + ["tools/audit/seat/roster_lib.py"])[1], True)
    check("main: an unreadable list exits non-zero, never a word",
          main(["decide", "--language", "python", "--event", "pull_request",
                "--files-from", "/nonexistent/o17-changed.txt"]), 2)
    check("main: a usage error exits 2", main(["decide", "--language"]), 2)
    check("main: changed with a bad range exits 2, never a list",
          main(["changed", "--base", "0" * 40, "--head", "1" * 40]), 2)

    # The list itself (#2405 round 1): a module renamed to an inert suffix.
    listed, porcelain = _rename_probe()
    check("a rename lists its source too: lib.py -> lib.md lists both",
          sorted(listed), ["lib.md", "lib.py"])
    check("so the python leg analyzes the rename",
          word("python", "pull_request", listed), "analyze")
    check("the seam is real: porcelain git diff lists only lib.md (null control)",
          porcelain, ["lib.md"])

    print(f"codeql_scope self-test: {n} checks, {fails} failed")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    opts = dict(zip(argv[1::2], argv[2::2]))
    if argv[:1] == ["changed"] and len(argv) == 5 and set(opts) == {"--base", "--head"}:
        try:
            files = changed_files(opts["--base"], opts["--head"])
        except subprocess.CalledProcessError as e:
            print(f"codeql_scope: cannot diff {opts['--base']}...{opts['--head']}: "
                  f"{(e.stderr or '').strip()[:200]}", file=sys.stderr)
            return 2
        print("\n".join(files))
        return 0
    if argv[:1] != ["decide"] or len(argv) != 7 or set(opts) != {"--language", "--event", "--files-from"}:
        print("usage: codeql_scope.py decide --language LEG --event EVENT --files-from FILE"
              " | changed --base BASE --head HEAD | --self-test",
              file=sys.stderr)
        return 2
    try:
        with open(opts["--files-from"], encoding="utf-8") as fh:
            files = fh.read().splitlines()
    except OSError as e:
        print(f"codeql_scope: cannot read the changed-file list: {e}", file=sys.stderr)
        return 2
    word, why = decide(opts["--language"], opts["--event"], files)
    print(f"codeql_scope: {opts['--language']}: {word}: {why}", file=sys.stderr)
    print(word)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
