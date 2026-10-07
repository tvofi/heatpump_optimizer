#!/usr/bin/env python3
"""May a verdicted pull request merge without a fresh CI run? (process review item 2B)

The orchestrator merges only on green CI at a head that contains current
`main`. When `main` moved after that CI ran, the old answer was "merge main in
and wait" -- a whole gate run for a change it may not be able to reach. This
answers the narrower question the measured closures can: did anything `main`
changed since the pull request's CI base land inside a closure the pull
request's own scoped gate selected? If not, every script that graded the pull
request reads exactly what it read then, and the merge needs no new run.

    python3 tools/audit/merge_fastpath.py --head <sha> [--main origin/main] [--ci-base <sha>]
    python3 tools/audit/merge_fastpath.py --self-test

Exit 0 prints `FASTPATH ELIGIBLE`; exit 1 prints `FASTPATH REFUSED` with one
`REFUSE <class>: <detail>` line per reason; exit 2 is a question it could not
ask (a ref that does not resolve), which is a refusal too.

WHAT IT REFUSES, every class conservative:
  * merged     -- the head is already in `main`.
  * ci-base    -- `--ci-base` is not between the fork point and `main`.
  * conflict   -- `git merge-tree --write-tree` reports a conflict.
  * workflow   -- either side touches `.github/`: the gate itself moved.
  * claim      -- either side touches a golden claim file (`claim-files.md`).
  * grader     -- either side touches a path a required job restores from the
                  base (the pathspecs `codeowners_gap.RESTORE` reads): a grader on
                  one side and what it grades on the other is the semantic
                  conflict a merge-tree cannot see (#1589 against #1592).
  * budget     -- either side touches a `*_budgets.json` no closure records
                  (`policy_budgets.json`): two changes inside one cap's
                  headroom can sum past it, and no scoped script would see it.
                  A cap a script reads is in its closure, so `overlap` has it.
  * full       -- the pull request's own selection was FULL (a gate file, an
                  unmeasured file, a table that does not describe the tree),
                  under `main`'s table or the head's: every script graded it.
  * unrecorded -- either side changes a file no closure records while `tests/run.sh`
                  has a `run_always` script, and the file is one such a script
                  may read: a non-INERT file, one `inert_reads` in
                  tests/closures.json lists for it, or a sibling in a directory
                  it lists a file from. A `run_always` script runs whatever the
                  plan says; `harness_headers.py` opens LICENSE and three docs/
                  pages as INERT reads, and DISCLAIMER.md as a closure read, through
                  D6's `claims.py` (#1823 review: a link the pull request adds to
                  DISCLAIMER.md, to a file main
                  deletes, is a false claim on the merged tree that neither
                  side's CI saw). A docs/delivery row nothing opens is not one
                  (R9-F10.9d). A table with no `inert_reads` keeps the old
                  answer: every unrecorded file is a read.
  * overlap    -- a file `main` changed since the CI base is in the closure of
                  a script the pull request selected, or of a `run_always`
                  script, which is selected on every run, under either table.

WHAT IT DOES NOT ANSWER, said so the orchestrator does not read more into it:
the jobs no closure scopes -- `policy-docs`, `env-matrix`, `wave-script`,
`briefs`, `typing`, `browser`, `mutation`, CodeQL, `hassfest`, `validate-hacs`
-- grade the whole tree and were not re-run on the merged one. Their backstop
is the push to `main`, which is FULL and unscoped, and a red there is
reverted first. Nor does it read CI: green on the head, a merge verdict at it
and a green `main` tip are the orchestrator's preconditions, checked before
this runs.

The CI base defaults to the fork point, `git merge-base <main> <head>`. A
pull-request run grades a merge with the `main` tip of its own moment, never an
older one, so the fork point can only charge the pull request with MORE of
`main`'s changes than its CI saw: a refusal it did not need, never a merge it
should not have had. `--ci-base` narrows that to the tip the run really used
(`fast`'s log prints it as GOLDEN_REF) and is refused unless it lies between the
fork point and `main`.
"""

from __future__ import annotations

import fnmatch
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
import closure  # noqa: E402  (tests/closure.py: the gate's own selection)
from layout import locate  # noqa: E402  old path while the restore puts the base copy there

CLAIM_FILES = ("tests/golden/claimed_drift.txt", "tests/golden/card_claimed_drift.txt")
# `run_always <interpreter> tests/<script>` in tests/run.sh: the scripts no scope skips.
ALWAYS = re.compile(r"^\s*run_always\s+\S+\s+(tests/[\w./-]+\.(?:py|mjs))\b", re.M)


def always_scripts(run_sh_texts: list[str]) -> list[str]:
    """Every script a `tests/run.sh` text runs with `run_always`."""
    return sorted({m for t in run_sh_texts for m in ALWAYS.findall(t)})


def _codeowners_gap():
    """The pin reader `policy-docs` runs, so the grader set is the one CI pins."""
    path = ROOT / locate("tools/audit/round6/D11/fix/codeowners_gap.py", root=ROOT)
    spec = importlib.util.spec_from_file_location("codeowners_gap", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def grader_specs(workflow_texts: list[str]) -> list[str]:
    """Every pathspec a restore names, checked out or listed."""
    restore = _codeowners_gap().RESTORE
    specs: set[str] = set()
    for text in workflow_texts:
        for m in restore.finditer(text):
            specs.update(re.findall(r"'([^']+)'", m.group(1)))
    return sorted(specs)


def _spec_hit(spec: str, path: str) -> bool:
    if any(ch in spec for ch in "*?["):
        return fnmatch.fnmatch(path, spec)
    return path == spec or path.startswith(spec.rstrip("/") + "/")


def select_under(table: dict, files: list[str]) -> dict:
    """`closure.select` over `files` with `table` as tests/closures.json."""
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "closures.json"
        p.write_text(json.dumps(table))
        saved = closure.CLOSURES
        closure.CLOSURES = p
        try:
            return closure.select(files)
        finally:
            closure.CLOSURES = saved


def inert_read_dirs(tables: dict[str, dict], always) -> "tuple[set[str], set[str]] | None":
    """(files, their directories) the `run_always` scripts opened among INERT files.

    None when a table carries no `inert_reads` (the recorder never measured it):
    the caller then keeps the old answer, every unrecorded file is a read.
    A directory counts because a script that globs a folder reads files nobody
    recorded yet, whatever the one it happened to open.
    """
    if any("inert_reads" not in t for t in tables.values()):
        return None
    files = {f for t in tables.values() for s in always for f in t["inert_reads"].get(s, ())}
    return files, {str(Path(f).parent) for f in files}


def file_class(f: str, graders: list[str], measured: "set[str] | frozenset[str]" = frozenset()) -> str | None:
    """The refusal class one changed file carries whatever the other side did:
    workflow, claim, grader or budget, else None. With `measured` empty every
    `*_budgets.json` is a budget: merge_train.py's batch routes them all serial."""
    if f.startswith(".github/"):
        return "workflow"
    if f in CLAIM_FILES:
        return "claim"
    if any(_spec_hit(s, f) for s in graders):
        return "grader"
    if f.endswith("_budgets.json") and closure.unit_of(f) not in measured:
        return "budget"
    return None


FILE_CLASS_DETAIL = {"workflow": "", "claim": "",
                     "grader": ", a grader required jobs restore from the base",
                     "budget": ", a cap no closure measures"}


def decide(pr_files: list[str], main_files: list[str], tables: dict[str, dict],
           graders: list[str], conflict: str | None,
           always: "list[str] | tuple[str, ...]" = ()) -> list[tuple[str, str]]:
    """Every refusal, as (class, detail); empty means eligible. Pure: no git."""
    out: list[tuple[str, str]] = []
    reads = inert_read_dirs(tables, always)
    if conflict:
        out.append(("conflict", conflict))
    if not main_files:
        # main has not moved since the CI base: that run graded this very tree.
        return out
    measured = {f for t in tables.values() for fs in t["closures"].values() for f in fs}
    both = [("pull request", f) for f in pr_files] + [("main", f) for f in main_files]
    for side, f in both:
        cls = file_class(f, graders, measured)
        if cls:
            out.append((cls, f"{side} changes {f}{FILE_CLASS_DETAIL[cls]}"))
        elif always and closure.unit_of(f) not in measured and (
                reads is None or not closure.is_inert(f)
                or f in reads[0] or str(Path(f).parent) in reads[1]):
            out.append(("unrecorded", f"{side} changes {f}, which no closure records, and "
                        f"run_always {', '.join(always)} read the tree whatever is selected"))
    if not pr_files:
        out.append(("full", "the pull request changes no file that could be determined"))
        return out
    units = {closure.unit_of(f) for f in main_files}
    for where, table in tables.items():
        plan = select_under(table, pr_files)
        if plan["mode"] != "scoped":
            out.append(("full", f"under {where}'s table: {plan['reason']}"))
            continue
        cl = table["closures"]
        for s in sorted(set(plan["run"]) | set(always)):
            hit = sorted(units & set(cl.get(s, ())))
            if hit:
                more = f" (+{len(hit) - 3})" if len(hit) > 3 else ""
                out.append(("overlap", f"under {where}'s table, {s} selected by the pull "
                            f"request reads {', '.join(hit[:3])}{more}, which main changed"))
    return out


def _git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()[:200]}")
    return r.stdout


def workflow_texts(rev: str, git=None) -> list[str]:
    """Every workflow file at <rev>: what `grader_specs` reads its restores from.
    `git(*args) -> stdout` defaults to this module's; merge_train.py passes its own."""
    git = git or _git
    return [git("show", f"{rev}:.github/workflows/{p}")
            for p in git("ls-tree", "--name-only", f"{rev}:.github/workflows").split()
            if p.endswith((".yml", ".yaml"))]


def _is_ancestor(a: str, b: str) -> bool:
    return subprocess.run(["git", "merge-base", "--is-ancestor", a, b], cwd=ROOT).returncode == 0


def run(head: str, main: str, ci_base: str | None) -> int:
    try:
        head = _git("rev-parse", "--verify", head + "^{commit}").strip()
        tip = _git("rev-parse", "--verify", main + "^{commit}").strip()
        fork = _git("merge-base", tip, head).strip()
        base = _git("rev-parse", "--verify", (ci_base or fork) + "^{commit}").strip()
    except RuntimeError as e:
        print(f"FASTPATH REFUSED: cannot ask -- {e}")
        return 2
    print(f"head {head}\nmain {tip}\nfork {fork}\nci-base {base}"
          f"{' (the fork point)' if base == fork else ''}")
    if _is_ancestor(head, tip):
        print(f"REFUSE merged: {head[:12]} is already in {main}\nFASTPATH REFUSED: 1 reason")
        return 1
    if not (_is_ancestor(fork, base) and _is_ancestor(base, tip)):
        print(f"REFUSE ci-base: {base[:12]} is not between the fork point {fork[:12]} "
              f"and {main}\nFASTPATH REFUSED: 1 reason")
        return 1
    pr_files = sorted(set(_git("diff", "--no-renames", "--name-only", f"{fork}...{head}").split()))
    main_files = sorted(set(_git("diff", "--no-renames", "--name-only", base, tip).split()))
    mt = subprocess.run(["git", "merge-tree", "--write-tree", "--name-only", tip, head],
                        cwd=ROOT, capture_output=True, text=True)
    conflict = None
    if mt.returncode != 0:
        named = [ln for ln in mt.stdout.splitlines()[1:] if ln] or [mt.stderr.strip()]
        conflict = "merge-tree reports a conflict: " + ", ".join(named)[:300]
    wf = [t for rev in (tip, head) for t in workflow_texts(rev)]
    tables = {"main": json.loads(_git("show", f"{tip}:tests/closures.json")),
              "head": json.loads(_git("show", f"{head}:tests/closures.json"))}
    print(f"pull request changes {len(pr_files)} file(s) ({fork[:12]}...{head[:12]}); "
          f"main changed {len(main_files)} since the CI base ({base[:12]}..{tip[:12]})")
    always = always_scripts([_git("show", f"{rev}:tests/run.sh") for rev in (tip, head)])
    found = decide(pr_files, main_files, tables, grader_specs(wf), conflict, always)
    for cls, detail in found:
        print(f"REFUSE {cls}: {detail}")
    if found:
        print(f"FASTPATH REFUSED: {len(found)} reason(s)")
        return 1
    print(f"FASTPATH ELIGIBLE: {head[:12]} may merge onto {tip[:12]} without a fresh CI run; "
          "main's FULL push gate grades the merged tree, and a red there is reverted first")
    return 0


def self_test() -> int:
    """Each refusal class against its null control, through the gate's real
    `closure.select` over a synthetic table and roster."""
    fails = n = 0

    def check(name: str, got, want) -> None:
        nonlocal fails, n
        n += 1
        ok = got == want
        fails += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name}" + ("" if ok else f": got {got!r}, want {want!r}"))

    scripts = ["tests/a.py", "tests/b.py", "tests/h.py"]
    table = {"closures": {"tests/a.py": ["tests/a.py", "custom_components/x/one.py"],
                          "tests/h.py": ["tests/h.py", "tools/audit/x/claims.py"],
                          "tests/b.py": ["tests/b.py", "tests/golden/b.json",
                                         "tests/golden/claimed_drift.txt"]}}
    tables = {"main": table, "head": table}
    graders = [".claude/workflows/*.mjs", "tools/audit/*.sh"]
    saved = closure.selectable_scripts
    closure.selectable_scripts = lambda: list(scripts)
    try:
        def classes(pr, mn, conflict=None, t=tables, always=("tests/h.py",)):
            return sorted({c for c, _ in decide(pr, mn, t, graders, conflict, always)})

        check("disjoint closures are eligible (null control)",
              classes(["tests/golden/b.json"], ["custom_components/x/one.py"]), [])
        check("main changed a file the selected script reads",
              classes(["tests/golden/b.json"], ["tests/b.py"]), ["overlap"])
        check("... and the mirror: the pull request's file is in the closure main changed",
              classes(["custom_components/x/one.py"], ["tests/a.py"]), ["overlap"])
        check("an overlap only the head's table records still refuses",
              classes(["tests/golden/b.json"], ["tests/c.py"],
                      t={"main": table, "head": {"closures": {
                          **table["closures"], "tests/b.py": [*table["closures"]["tests/b.py"],
                                                              "tests/c.py"]}}}), ["overlap"])
        check("a merge-tree conflict refuses",
              classes(["tests/golden/b.json"], ["custom_components/x/one.py"], "x"), ["conflict"])
        check("a workflow change on main refuses",
              classes(["tests/golden/b.json"], [".github/workflows/tests.yml"]), ["workflow"])
        check("a claim-file change on the pull request refuses",
              classes(["tests/golden/b.json", "tests/golden/claimed_drift.txt"],
                      ["custom_components/x/one.py"]), ["claim"])
        check("a pinned grader changed on main refuses",
              classes(["tests/golden/b.json"], [".claude/workflows/policy_lint.mjs"]), ["grader"])
        check("an unmeasured budget file on either side refuses",
              classes(["tests/golden/b.json"], [".claude/workflows/policy_budgets.json"]), ["budget"])
        check("a measured one is the overlap's to judge, not a refusal of its own (null control)",
              classes(["tests/golden/b.json"], ["tests/a_budgets.json"],
                      t={"main": {"closures": {**table["closures"], "tests/a.py": [
                          *table["closures"]["tests/a.py"], "tests/a_budgets.json"]}},
                         "head": table}), [])
        check("file_class with nothing measured calls every budget file a budget "
              "(merge_train.py's batch routing)",
              [file_class(f, graders) for f in ("tests/a_budgets.json", ".github/x.yml",
                                                 "tests/golden/claimed_drift.txt",
                                                 "tools/audit/x.sh", "tests/a.py")],
              ["budget", "workflow", "claim", "grader", None])
        check("... and a measured one is no class of its own (null control)",
              file_class("tests/a_budgets.json", graders, {"tests/a_budgets.json"}), None)
        check("a gate file in the pull request is FULL and refuses",
              classes(["tests/run.sh"], ["docs/delivery/1.md"], always=()), ["full"])
        check("an unmeasured file in the pull request is FULL and refuses",
              classes(["custom_components/x/new.py"], ["docs/delivery/1.md"], always=()), ["full"])
        check("an INERT-only pull request selects nothing and is eligible against code "
              "when no script runs always (null control)",
              classes(["docs/delivery/1.md"], ["custom_components/x/one.py"], always=()), [])
        check("#1823's probe: the pull request links a file from SECURITY.md and main "
              "deletes it, and a run_always script reads both unrecorded",
              classes(["SECURITY.md"], ["tools/audit/README.md"]), ["unrecorded"])
        check("... the same pair with no run_always script is eligible (null control)",
              classes(["SECURITY.md"], ["tools/audit/README.md"], always=()), [])
        check("an unrecorded file on main's side alone refuses too",
              classes(["tests/golden/b.json"], ["docs/delivery/1.md"]), ["unrecorded"])
        rt = {"closures": table["closures"],
              "inert_reads": {"tests/h.py": ["SECURITY.md", "docs/setup.md"]}}
        rtabs = {"main": rt, "head": rt}
        check("R9-F10.9d: a docs/delivery row main adds, which no run_always script opened, "
              "is eligible once the table records the INERT reads",
              classes(["tests/golden/b.json"], ["docs/delivery/1.md"], t=rtabs), [])
        check("... and the pull request's own delivery row beside a code change main made",
              classes(["docs/delivery/2.md"], ["custom_components/x/one.py"], t=rtabs), [])
        check("a doc a run_always script opened still refuses (null control for the pair above)",
              classes(["tests/golden/b.json"], ["docs/setup.md"], t=rtabs), ["unrecorded"])
        check("... on the pull request's side too",
              classes(["SECURITY.md"], ["tools/audit/README.md"], t=rtabs), ["unrecorded"])
        check("a new page beside the docs a script opened refuses: it may glob the folder",
              classes(["tests/golden/b.json"], ["docs/new.md"], t=rtabs), ["unrecorded"])
        check("an unmeasured file that is not INERT refuses even then",
              classes(["tests/golden/b.json"], ["custom_components/x/new.py"], t=rtabs),
              ["unrecorded"])
        check("a table in which one side never measured the reads keeps the old answer",
              classes(["tests/golden/b.json"], ["docs/delivery/1.md"],
                      t={"main": rt, "head": table}), ["unrecorded"])
        check("this tree's table records harness_headers.py's INERT reads, LICENSE among them",
              "LICENSE" in json.loads((ROOT / "tests/closures.json").read_text())
              .get("inert_reads", {}).get("tests/harness_headers.py", ()), True)
        check("main changed what a run_always script reads, which the pull request never "
              "selected: overlap",
              classes(["tests/golden/b.json"], ["tools/audit/x/claims.py"]), ["overlap"])
        check("... and with that script not run_always, the same pair is eligible (null control)",
              classes(["tests/golden/b.json"], ["tools/audit/x/claims.py"], always=()), [])
        check("the run_always scripts are read from tests/run.sh",
              always_scripts(['  run_always "$PYTHON" tests/harness_headers.py\n',
                              '  run "$PYTHON" tests/edge.py\n']),
              ["tests/harness_headers.py"])
        check("this tree's run.sh runs harness_headers.py always",
              "tests/harness_headers.py" in always_scripts([(ROOT / "tests/run.sh").read_text()]),
              True)
        check("no determinable pull-request file refuses", classes([], ["tests/a.py"]), ["full"])
        check("main unmoved since the CI base: even a gate change is eligible (null control)",
              classes(["tests/run.sh", ".github/workflows/tests.yml"], []), [])
        check("... but never past a conflict", classes(["tests/run.sh"], [], "x"), ["conflict"])
        check("the grader specs are the restore pathspecs the workflows name",
              grader_specs(["git checkout \"$PINNED\" -- \\\n  '.claude/workflows/*.py' \\\n"
                            "  'tools/audit/*.sh'\n", "git checkout HEAD -- 'x.mjs'"]),
              [".claude/workflows/*.py", "tools/audit/*.sh"])
        check("this tree's workflows pin the governance programs",
              ".claude/workflows/*.mjs" in grader_specs(
                  [p.read_text() for p in sorted((ROOT / ".github/workflows").glob("*.yml"))]), True)
    finally:
        closure.selectable_scripts = saved
    print(f"merge_fastpath self-test: {n} checks, {fails} failed")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    args = dict(zip(argv[::2], argv[1::2]))
    if len(argv) % 2 or "--head" not in args or set(args) - {"--head", "--main", "--ci-base"}:
        print(__doc__.split("\n\n")[2], file=sys.stderr)
        return 2
    return run(args["--head"], args.get("--main", "origin/main"), args.get("--ci-base"))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
