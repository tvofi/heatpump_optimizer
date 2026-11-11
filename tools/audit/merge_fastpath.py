#!/usr/bin/env python3
"""The refusal class a changed file carries, for merge_train.py's batch routing.

`merge_train.py` routes a pull request touching a workflow, claim, grader or
unmeasured budget file serial -- never in a batch -- so a change to the gate
itself, a claim, a required grader or a cap no closure measures cannot
interleave with what it grades. `file_class` is that classifier; `grader_specs`
and `workflow_texts` read it the restore pathspecs the workflows name.
(The ELIGIBLE ask-step this module once also served was retired: 0 of 45
measured merge decisions would ever have been ELIGIBLE -- R9-F10.9d, every
main move lands through wave merges touching refusal classes by design.)

    python3 tools/audit/merge_fastpath.py --self-test

`governance.yml` greps the `checks, 0 failed` line the self-test prints.
"""

from __future__ import annotations

import fnmatch
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
import closure  # noqa: E402  (tests/closure.py: the gate's own selection)
from layout import locate  # noqa: E402  old path while the restore puts the base copy there

CLAIM_FILES = ("tests/golden/claimed_drift.txt", "tests/golden/card_claimed_drift.txt")


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


def workflow_texts(rev: str, git=None) -> list[str]:
    """Every workflow file at <rev>: what `grader_specs` reads its restores from.
    `git(*args) -> stdout` defaults to this module's; merge_train.py passes its own."""
    git = git or _git
    return [git("show", f"{rev}:.github/workflows/{p}")
            for p in git("ls-tree", "--name-only", f"{rev}:.github/workflows").split()
            if p.endswith((".yml", ".yaml"))]


def _git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()[:200]}")
    return r.stdout


def self_test() -> int:
    """The classes `file_class` assigns, and the grader specs the workflows'
    restore pathspecs yield, against null controls."""
    fails = n = 0

    def check(name: str, got, want) -> None:
        nonlocal fails, n
        n += 1
        ok = got == want
        fails += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name}" + ("" if ok else f": got {got!r}, want {want!r}"))

    graders = [".claude/workflows/*.mjs", "tools/audit/*.sh"]
    check("file_class with nothing measured calls every budget file a budget "
          "(merge_train.py's batch routing)",
          [file_class(f, graders) for f in ("tests/a_budgets.json", ".github/x.yml",
                                             "tests/golden/claimed_drift.txt",
                                             "tools/audit/x.sh", "tests/a.py")],
          ["budget", "workflow", "claim", "grader", None])
    check("... and a measured one is no class of its own (null control)",
          file_class("tests/a_budgets.json", graders, {"tests/a_budgets.json"}), None)
    check("the grader specs are the restore pathspecs the workflows name",
          grader_specs(["git checkout \"$PINNED\" -- \\\n  '.claude/workflows/*.py' \\\n"
                        "  'tools/audit/*.sh'\n", "git checkout HEAD -- 'x.mjs'"]),
          [".claude/workflows/*.py", "tools/audit/*.sh"])
    check("this tree's workflows pin the governance programs",
          ".claude/workflows/*.mjs" in grader_specs(
              [p.read_text() for p in sorted((ROOT / ".github/workflows").glob("*.yml"))]), True)
    print(f"merge_fastpath self-test: {n} checks, {fails} failed")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    print(__doc__.split("\n\n")[0], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
