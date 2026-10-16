#!/usr/bin/env python3
"""Count the four layering spellings the part-3 round-2 repair resolves, over a set of trees.

WHY IT EXISTS. `calibrate.py --measure-corpus --only-metric layering` re-derived the
corpus vectors for the `layering` job and `corpus_vectors.json` came back
byte-identical. That reads two ways: the rule reads those trees exactly as the
round-1 rule did, or the re-measure was vacuous and nothing was compared. This is
the control. It counts, over the same trees, the instances of each spelling the
new rule resolves -- an absolute self-import, a constant-name dynamic import, and
an import inside a guard the runtime runs (an `else`, or a test that is not the
bare sentinel) -- and it refuses to report anything without first firing on a tree
that carries all four (`PRECONDITION`). A census that matched nothing is the
defect it exists to catch, so it exits 1 rather than printing a zero.

    python3 dev/audit/harnesses/archscore_layering_seam_census.py <repo>
    python3 dev/audit/harnesses/archscore_layering_seam_census.py <repo> --corpus

`--corpus` censuses every commit `tools/audit/archscore/calibration/corpus.tsv`
names (each pull request and its parent); without it, the tree at `<repo>`.

Measured (R10-ARCHSCORE-COVERAGE part 3, #2320 round 2, 2026-10-16, Apple M1):
87 corpus trees, `absolute_self_import=0`, `constant_dynamic_import=30` (every one
`threadpoolctl`), `guard_not_body=58`, `guard_not_body_imports=0`; the planted
precondition tree reads 1 / 2 / 4 / 2.
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


def census(root: Path) -> tuple[dict[str, int], set[str]]:
    """Per tree: the count of each spelling, and the constant names dynamic imports name."""
    out = {"absolute_self_import": 0, "constant_dynamic_import": 0,
           "guard_not_body": 0, "guard_not_body_imports": 0}
    names: set[str] = set()
    for p in sorted((root / PKG).glob("*.py")):
        for n in ast.walk(ast.parse(p.read_text())):
            if isinstance(n, ast.ImportFrom) and n.module and n.module.startswith(SELF):
                out["absolute_self_import"] += 1
            elif isinstance(n, ast.Import) and any(a.name.startswith(SELF) for a in n.names):
                out["absolute_self_import"] += 1
            elif isinstance(n, ast.Call) and _dynamic(n):
                out["constant_dynamic_import"] += 1
                names.add(n.args[0].value)
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


def _dynamic(n: ast.Call) -> bool:
    """A constant-name ``import_module``/``__import__`` call."""
    f = n.func
    named = (isinstance(f, ast.Name) and f.id in ("import_module", "__import__")) or (
        isinstance(f, ast.Attribute) and f.attr in ("import_module", "__import__")
        and isinstance(f.value, ast.Name))
    return bool(named and n.args and isinstance(n.args[0], ast.Constant)
                and isinstance(n.args[0].value, str))


def tree_of(repo: Path, sha: str, into: Path) -> Path:
    into.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(["git", "-C", str(repo), "archive", sha, PKG],
                             capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(into)], input=archive, check=True)
    return into


def plant(root: Path) -> None:
    """A tree that carries all four spellings, so a census that matches none is refused."""
    p = root / PKG / "silent_mode.py"
    src = p.read_text()
    anchor = "from .optimizer import _utc_step_starts\n"
    assert src.count(anchor) == 1, "the planted tree is not the pin"
    p.write_text(src.replace(
        anchor,
        "from custom_components.heatpump_optimizer.optimizer import _utc_step_starts\n"
        "import importlib\n"
        'importlib.import_module(".optimizer", __package__)\n'
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
    total = {"absolute_self_import": 0, "constant_dynamic_import": 0,
             "guard_not_body": 0, "guard_not_body_imports": 0}
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
    ok = all(planted.values())
    print(f"PRECONDITION {'ok' if ok else 'FAILED'}: a census that matched no spelling is refused, "
          "not reported as a zero")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
