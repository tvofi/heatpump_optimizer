#!/usr/bin/env python3
"""Decide whether one CodeQL leg may skip a pull request whose diff it cannot read.

    python3 -I tools/pr/codeql_scope.py changed --base BASE --head HEAD > CHANGED.txt
    python3 -I tools/pr/codeql_scope.py decide --language LEG --event EVENT \
        --files-from CHANGED.txt
    python3 -I tools/pr/codeql_scope.py extracted --language LEG --archive SRC.ZIP
    python3 -I tools/pr/codeql_scope.py stand-in --language LEG --base-sha SHA --out FILE
    python3 -I tools/pr/codeql_scope.py --self-test

`decide` prints one word on stdout, `analyze` or `skip`, and its reason on
stderr. `.github/workflows/codeql.yml`'s `scope` job runs it once per leg, and
the leg's init and analyze steps run unless the word is `skip`, so a leg that
skips still reports its required `Analyze (<leg>)` context, as `success`.

WHY (O17, 2026-10-18). A pull request whose diff is a roster or a delivery row
paid `Analyze (python)`'s 23-26 minutes, its critical path, for an analysis
that cannot differ from main's: no file the python extractor reads changed.
That was 76 of the 144 pull requests merged in round 10.

D-5 (owner ruling, DESIGN-P2 6): INERT is an allow-list, not a measured
closure, so `extracted` checks it against the extractor on every push run
(which analyzes in full): the leg's extracted source archive (the database's
`src.zip`) must hold no file whose suffix is on that leg's INERT list. A file
the extractor read and the list calls inert is a pull request that would skip
a leg that could have found something; the push run goes red instead.

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
  * a SKIPPED leg still uploads its category (r10-codeql-dependabot): code
    scanning compares a pull request's configurations with main's, and a
    category main carries that the pull request lacks reads "1 configuration
    not found" on every skipping PR. `stand-in` writes MAIN'S OWN analysis of
    that category as the stand-in -- the one at the PR's base commit, else
    main's newest error-free one -- and the leg uploads it under its own
    category and analysis key. It is truthful by O17's own premise: the diff
    is inert to that extractor, so the merge ref's alerts ARE the base's. No
    such analysis (exit 3) and the leg analyzes instead, never uploads nothing.
    The upload step is not "Perform CodeQL Analysis", so
    tools/ci/codescan_wait.py never counts a stand-in as the PR's own alerts;
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


ANALYSIS_KEY = ".github/workflows/ci.yml:analyze"


def pick_stand_in(analyses: list[dict], base_sha: str, language: str) -> dict | None:
    """Main's analysis of `language` to stand in for a skipped leg: the one at
    `base_sha`, else the newest; only the umbrella's key, never an errored one."""
    ok = [a for a in analyses
          if a.get("ref") == "refs/heads/main" and a.get("analysis_key") == ANALYSIS_KEY
          and a.get("category") == f"/language:{language}" and not a.get("error")]
    ok.sort(key=lambda a: a.get("created_at", ""), reverse=True)
    at_base = [a for a in ok if a.get("commit_sha") == base_sha]
    return (at_base or ok or [None])[0]


def stand_in_sarif(doc: dict) -> dict:
    """The downloaded SARIF made uploadable for the pull request: main's
    provenance and category dropped (upload-sarif sets this run's)."""
    for run in doc.get("runs") or []:
        run.pop("versionControlProvenance", None)
        run.pop("automationDetails", None)
    return doc


def write_stand_in(language: str, base_sha: str, out: str) -> int:
    """0 with the stand-in at `out`; 3 when main has none (the leg analyzes)."""
    import json
    repo = os.environ.get("GITHUB_REPOSITORY", "")

    def gh(*args: str) -> str:
        return subprocess.run(["gh", "api", *args], check=True, capture_output=True, text=True).stdout

    try:
        listing = json.loads(gh(f"repos/{repo}/code-scanning/analyses?ref=refs/heads/main&per_page=100"))
        pick = pick_stand_in(listing, base_sha, language)
        if pick is None:
            print(f"codeql_scope: {language}: main has no error-free {ANALYSIS_KEY} analysis to stand in", file=sys.stderr)
            return 3
        doc = json.loads(gh("-H", "Accept: application/sarif+json",
                            f"repos/{repo}/code-scanning/analyses/{pick['id']}"))
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"codeql_scope: {language}: cannot read main's analysis: {e}", file=sys.stderr)
        return 3
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(stand_in_sarif(doc), fh)
    where = "the base commit" if pick.get("commit_sha") == base_sha else f"main's newest ({pick.get('commit_sha', '')[:12]})"
    print(f"codeql_scope: {language}: stand-in is analysis {pick['id']} at {where}", file=sys.stderr)
    return 0


def extracted_violations(language: str, names: list[str], inert=None) -> list[str]:
    """The archive entries whose suffix is on the leg's INERT list (D-5). An
    unknown leg or an empty archive is itself a violation: nothing was read,
    so nothing was checked."""
    inert = INERT if inert is None else inert
    if language not in inert:
        return [f"unknown leg {language!r}"]
    names = [n for n in names if n and not n.endswith("/")]
    if not names:
        return ["the archive holds no file: nothing was checked"]
    return [n for n in names if PurePosixPath(n).suffix.lower() in inert[language]]


def check_extracted(language: str, archive: str) -> int:
    """0 when the archive holds no inert file, 1 on one, 2 when unreadable."""
    import zipfile
    try:
        with zipfile.ZipFile(archive) as z:
            names = z.namelist()
    except (OSError, zipfile.BadZipFile) as e:
        print(f"codeql_scope: cannot read the extracted archive {archive}: {e}", file=sys.stderr)
        return 2
    bad = extracted_violations(language, names)
    for n in bad[:20]:
        print(f"codeql_scope: {language}: extracted but inert: {n}", file=sys.stderr)
    print(f"codeql_scope: {language}: {len(names)} archive entries, {len(bad)} on the INERT list", file=sys.stderr)
    return 1 if bad else 0


def _closure():
    """tests/closure.py, the one changed-file producer every lane and the gate
    read (#2406), imported by path so `python3 -I` still finds it."""
    tests = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir, "tests")
    if tests not in sys.path:
        sys.path.insert(0, tests)
    import closure
    return closure


def changed_files(base: str, head: str, cwd: str = ".",
                  env: dict | None = None) -> list[str]:
    """The pull request's three-dot file list, BOTH sides of every rename:
    closure.changed_between's list, so CodeQL reads the gate's own list.
    Raises CalledProcessError when git cannot diff: the caller fails, and a
    failed scope job leaves every leg analyzing."""
    try:
        return _closure().changed_between(base, head, cwd=cwd, env=env)
    except SystemExit as e:
        raise subprocess.CalledProcessError(2, ["git", "diff", f"{base}...{head}"],
                                            stderr=str(e)) from None


def _rename_probe() -> tuple[list[str], list[str]]:
    """(changed_files, the porcelain list) over a throwaway repo
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
    cl = _closure()
    real = cl.changed_between
    try:
        cl.changed_between = lambda *a, **k: ["from-closure"]
        try:
            got = changed_files("b", "h")
        except Exception as e:  # a private copy runs git on a bogus range
            got = f"raised {type(e).__name__}"
        check("the list is closure.changed_between's, not a copy (#2406)",
              got, ["from-closure"])
    finally:
        cl.changed_between = real

    # D-5: the INERT list against the extractor's own source archive.
    import zipfile
    arch = {"python": ["src/a.py", "src/pkg/", "src/b.py"],
            "javascript-typescript": ["src/card.js", "src/x.json", "src/y.html"],
            "actions": ["src/.github/workflows/ci.yml"]}
    for leg, names in arch.items():
        check(f"D-5: a {leg} archive of extractable files is sound (null control)",
              extracted_violations(leg, names), [])
    plant = {**INERT, "python": INERT["python"] | {".py"}}
    check("D-5 plant: .py joining python's INERT list fails the check",
          extracted_violations("python", arch["python"], plant), ["src/a.py", "src/b.py"])
    check("D-5 plant: .json is inert to python, so a json in the archive fails",
          extracted_violations("python", arch["python"] + ["src/c.json"]), ["src/c.json"])
    check("D-5: an upper-case suffix is the same suffix",
          extracted_violations("python", ["A.PY", "B.MD"]), ["B.MD"])
    check("D-5: an empty archive is not a pass", len(extracted_violations("python", ["d/"])), 1)
    check("D-5: an unknown leg is not a pass", len(extracted_violations("ruby", ["a.rb"])), 1)
    with tempfile.TemporaryDirectory() as td:
        def zipped(*names: str) -> str:
            path = os.path.join(td, f"z{len(os.listdir(td))}.zip")
            with zipfile.ZipFile(path, "w") as z:
                for nm in names:
                    z.writestr(nm, "x")
            return path
        check("D-5 main: a sound archive exits 0",
              main(["extracted", "--language", "python", "--archive", zipped("a.py")]), 0)
        check("D-5 main: an inert file in the archive exits 1",
              main(["extracted", "--language", "python", "--archive", zipped("a.py", "n.md")]), 1)
        check("D-5 main: a missing archive exits 2, never 0",
              main(["extracted", "--language", "python", "--archive", os.path.join(td, "none.zip")]), 2)
        bad = os.path.join(td, "bad.zip")
        with open(bad, "w", encoding="utf-8") as fh:
            fh.write("not a zip")
        check("D-5 main: a corrupt archive exits 2", main(["extracted", "--language", "python", "--archive", bad]), 2)

    # The stand-in for a skipped leg: main's analysis at the base, else main's
    # newest; never another key, category, ref or an errored one.
    an = lambda i, sha, at, **kw: {"id": i, "ref": "refs/heads/main", "analysis_key": ANALYSIS_KEY,  # noqa: E731
                                   "category": "/language:python", "error": "", "commit_sha": sha,
                                   "created_at": at, **kw}
    pool = [an(1, "b" * 40, "2026-10-24T01:00:00Z"), an(2, "c" * 40, "2026-10-24T02:00:00Z"),
            an(3, "b" * 40, "2026-10-24T03:00:00Z", error="unsuccessful execution"),
            an(4, "b" * 40, "2026-10-24T04:00:00Z", analysis_key=".github/workflows/codeql.yml:analyze"),
            an(5, "b" * 40, "2026-10-24T05:00:00Z", category="/language:actions"),
            an(6, "b" * 40, "2026-10-24T06:00:00Z", ref="refs/pull/7/merge")]
    pick = lambda base: (pick_stand_in(pool, base, "python") or {}).get("id")  # noqa: E731
    check("stand-in: the base commit's own analysis wins over a newer one", pick("b" * 40), 1)
    check("stand-in: no analysis at the base takes main's newest", pick("d" * 40), 2)
    check("stand-in: none for a leg main never analyzed (the leg analyzes)",
          pick_stand_in(pool, "b" * 40, "javascript-typescript"), None)
    sarif = stand_in_sarif({"runs": [{"automationDetails": {"id": "/language:python/"},
                                      "versionControlProvenance": [{"branch": "refs/heads/main"}],
                                      "results": [{"ruleId": "r"}]}]})
    check("stand-in: main's provenance and category are dropped, the results kept",
          sarif, {"runs": [{"results": [{"ruleId": "r"}]}]})

    print(f"codeql_scope self-test: {n} checks, {fails} failed")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    opts = dict(zip(argv[1::2], argv[2::2]))
    if argv[:1] == ["extracted"] and len(argv) == 5 and set(opts) == {"--language", "--archive"}:
        return check_extracted(opts["--language"], opts["--archive"])
    if argv[:1] == ["stand-in"] and len(argv) == 7 and set(opts) == {"--language", "--base-sha", "--out"}:
        return write_stand_in(opts["--language"], opts["--base-sha"], opts["--out"])
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
              " | changed --base BASE --head HEAD | extracted --language LEG --archive SRC.ZIP"
              " | stand-in --language LEG --base-sha SHA --out FILE"
              " | --self-test",
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
