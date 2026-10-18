#!/usr/bin/env python3
"""Decide whether one CodeQL leg may skip a pull request whose diff it cannot read.

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
  * an empty or unreadable file list analyzes.
"""
from __future__ import annotations

import sys
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

    print(f"codeql_scope self-test: {n} checks, {fails} failed")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    opts = dict(zip(argv[1::2], argv[2::2]))
    if argv[:1] != ["decide"] or len(argv) != 7 or set(opts) != {"--language", "--event", "--files-from"}:
        print("usage: codeql_scope.py decide --language LEG --event EVENT --files-from FILE | --self-test",
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
