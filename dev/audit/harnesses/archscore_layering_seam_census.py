#!/usr/bin/env python3
"""Count the layering spellings the part-3 rule resolves, one counter each, over a set of trees.

WHY IT EXISTS. `calibrate.py --measure-corpus --only-metric layering` re-derived the
corpus vectors for the `layering` job and `corpus_vectors.json` came back
byte-identical. That reads two ways: the rule reads those trees exactly as the
round-1 rule did, or the re-measure was vacuous and nothing was compared. This is
the control. It counts, over the same trees, the instances of each spelling the
rule resolves -- an absolute self-import on a `from` statement and on the plain
dotted `import`, a constant-name dynamic import whose name is passed positionally
or as the `name` keyword, and an import inside a guard the runtime runs (an
`else`, or a test that is not the bare sentinel) -- and it refuses to report
anything without first firing on a tree that carries every one of them
(`PRECONDITION`). A census that matched nothing is the defect it exists to catch,
so it exits 1 rather than printing a zero.

THE FORMS ARE COUNTED APART. An earlier version filed `ast.ImportFrom` and plain
`ast.Import` of this package under one `absolute_self_import` counter and planted
only the `from` form, so a tree carrying the dotted spelling -- which the rule did
not resolve until round 3 -- read as "the corpus carries this and the rule handles
it". A counter that cannot separate the resolved spelling from the unresolved one
prints a zero that means nothing (#2320 round-2 review).

    python3 dev/audit/harnesses/archscore_layering_seam_census.py <repo>
    python3 dev/audit/harnesses/archscore_layering_seam_census.py <repo> --corpus

`--corpus` censuses every commit `tools/audit/archscore/calibration/corpus.tsv`
names (each pull request and its parent); without it, the tree at `<repo>`.

Measured (R10-ARCHSCORE-COVERAGE part 3, #2320 round 3, 2026-10-16, Apple M1):
87 corpus trees, `absolute_self_import=0` and `absolute_self_import_dotted=0` -- neither absolute
self-import spelling occurs in any corpus tree, so the re-measured vectors cannot move --
`constant_dynamic_import=30` (every one `threadpoolctl`), `guard_not_body=58`,
`guard_not_body_imports=0`; the planted precondition tree reads 2 / 1 / 3 / 4 / 2.
"""
from __future__ import annotations

import ast
import csv
import subprocess
import sys
import tempfile
from pathlib import Path

PKG = "custom_components/heatpump_optimizer"
SELF = PKG.replace("/", ".")
PIN = "7952d8f9e4fbe9945bc8742e8dc02be8fbe4582c"
#: one counter per spelling, so a tree carrying the dotted form is not read as carrying the from form.
SPELLINGS = ("absolute_self_import", "absolute_self_import_dotted", "constant_dynamic_import",
             "guard_not_body", "guard_not_body_imports")


def census(root: Path) -> tuple[dict[str, int], set[str]]:
    """Per tree: the count of each spelling, and the constant names dynamic imports name."""
    out = dict.fromkeys(SPELLINGS, 0)
    names: set[str] = set()
    for p in sorted((root / PKG).glob("*.py")):
        for n in ast.walk(ast.parse(p.read_text())):
            if isinstance(n, ast.ImportFrom) and n.level == 0 and n.module and n.module.startswith(SELF):
                out["absolute_self_import"] += 1
            elif isinstance(n, ast.Import) and any(a.name.startswith(SELF) for a in n.names):
                out["absolute_self_import_dotted"] += 1
            elif isinstance(n, ast.Call) and (name := _dynamic(n)) is not None:
                out["constant_dynamic_import"] += 1
                names.add(name)
            elif isinstance(n, ast.If) and "TYPE_CHECKING" in ast.unparse(n.test):
                bare = (isinstance(n.test, ast.Name) and n.test.id == "TYPE_CHECKING") or (
                    isinstance(n.test, ast.Attribute) and n.test.attr == "TYPE_CHECKING")
                if n.orelse or not bare:
                    # the branches that run: the `else`, and a test that is not the bare sentinel
                    out["guard_not_body"] += 1
                    runs = list(n.orelse) + ([] if bare else list(n.body))
                    for stmt in runs:
                        for m in ast.walk(stmt):
                            if isinstance(m, (ast.Import, ast.ImportFrom)):
                                out["guard_not_body_imports"] += 1
    return out, names


def _dynamic(n: ast.Call) -> str | None:
    """The constant name an ``import_module``/``__import__`` call imports, passed positionally or as
    the ``name`` keyword, or None for any other call."""
    f = n.func
    named = (isinstance(f, ast.Name) and f.id in ("import_module", "__import__")) or (
        isinstance(f, ast.Attribute) and f.attr in ("import_module", "__import__")
        and isinstance(f.value, ast.Name))
    if not named:
        return None
    first = n.args[0] if n.args else next((k.value for k in n.keywords if k.arg == "name"), None)
    return first.value if isinstance(first, ast.Constant) and isinstance(first.value, str) else None


def tree_of(repo: Path, sha: str, into: Path) -> Path:
    into.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(["git", "-C", str(repo), "archive", sha, PKG],
                             capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(into)], input=archive, check=True)
    return into


def plant(root: Path) -> None:
    """A tree that carries every spelling the census counts, so a census that matches none is
    refused."""
    p = root / PKG / "silent_mode.py"
    src = p.read_text()
    anchor = "from .optimizer import _utc_step_starts\n"
    assert src.count(anchor) == 1, "the planted tree is not the pin"
    p.write_text(src.replace(
        anchor,
        "from custom_components.heatpump_optimizer.optimizer import _utc_step_starts\n"
        "from custom_components.heatpump_optimizer import optimizer as _o  # noqa: F401\n"
        "import custom_components.heatpump_optimizer.optimizer as _o2  # noqa: F401\n"
        "import importlib\n"
        'importlib.import_module(".optimizer", __package__)\n'
        'importlib.import_module(name=".optimizer", package=__package__)\n'
        "if not TYPE_CHECKING:\n    from .optimizer import HeatPumpOptimizer  # noqa: F401\n"
        "if TYPE_CHECKING:\n    from .optimizer import HeatPumpOptimizer  # noqa: F401\n"
        "else:\n    from .optimizer import HeatPumpOptimizer  # noqa: F401\n"))


def main(argv: list[str]) -> int:
    repo = Path(argv[1]).resolve()
    shas: list[str] = []
    if "--corpus" in argv:
        tsv = repo / "tools/audit/archscore/calibration/corpus.tsv"
        with open(tsv) as f:
            rows = list(csv.DictReader(f, delimiter="\t"))
        shas = sorted({r["sha"] for r in rows} | {r["parent"] for r in rows})
    total = dict.fromkeys(SPELLINGS, 0)
    names: set[str] = set()
    with tempfile.TemporaryDirectory(prefix="layering-seam-census-") as tmp:
        if shas:
            print(f"corpus trees censused: {len(shas)}")
            for sha in shas:
                c, ns = census(tree_of(repo, sha, Path(tmp) / sha[:8]))
                for k, v in c.items():
                    total[k] += v
                names |= ns
        else:
            c, ns = census(repo)
            total.update(c)
            names |= ns
        for k, v in total.items():
            print(f"RESULT {k}={v} count")
        if names:
            print(f"RESULT dynamic_names={sorted(names)} set")
        t = tree_of(repo, PIN, Path(tmp) / "planted")
        plant(t)
        planted, _ = census(t)
    for k, v in planted.items():
        print(f"RESULT planted_{k}={v} count")
    zero = sorted(k for k, v in planted.items() if not v)
    note = f"planted zero: {zero}" if zero else "every spelling fired on the planted tree"
    print(f"PRECONDITION {'ok' if not zero else 'FAILED'}: a census that matched no spelling is "
          f"refused, not reported as a zero ({note})")
    return 0 if not zero else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
