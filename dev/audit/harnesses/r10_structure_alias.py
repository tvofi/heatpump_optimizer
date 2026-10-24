"""R10-STRUCTURE-ALIAS: the finder's two plants, replayed in memory, and the getter census.

The plants are the round-10 fix review's (probe/rev-2620-654004be, ev/plant_p2.diff
and ev/plant_p3.diff), re-anchored to the text they edit rather than to line numbers:
the alias binds ``prices = self._prices`` in ``_raise_cop_issue``; the getter adds a
``_cop_state`` in the learning seam returning ``(self._cop_baseline,
self._cop_health_cusum)`` and makes ``_scores_view`` read through it. Each is parsed
from the tree's own ``coordinator.py`` and priced by the tree's own
``tests/structure.py`` ``seam_metrics``, so the same command reads a base and a head.
A plant whose anchor is gone prints ``anchor-gone`` rather than a figure.

The census is the fixer.md step-8 rule: every coordinator unit whose body is a bare
state getter, and every ``@property`` read from a seam other than its own.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_structure_alias.py
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tests"))
import structure as S  # noqa: E402

COORD = S.PACKAGE_DIR / "coordinator.py"

ALIAS = (
    ("    def _raise_cop_issue(self, baseline: float) -> None:\n"
     '        """One repair issue with the money the shortfall costs per month."""\n',
     "    def _raise_cop_issue(self, baseline: float) -> None:\n"
     '        """One repair issue with the money the shortfall costs per month."""\n'
     "        prices = self._prices\n"),
    ('for p in self._prices]))\n            if self._prices\n',
     "for p in prices]))\n            if prices\n"),
)
GETTER = (
    ("    def _raise_cop_issue(self, baseline: float) -> None:\n",
     "    def _cop_state(self):\n        return self._cop_baseline, self._cop_health_cusum\n\n"
     "    def _raise_cop_issue(self, baseline: float) -> None:\n"),
    ("        operation = self._operation_score\n        return compose_scores(",
     "        operation = self._operation_score\n        baseline, cusum = self._cop_state()\n"
     "        return compose_scores("),
    ("machine_score(self._cop_baseline, self._cop_health_cusum.stat),",
     "machine_score(baseline, cusum.stat),"),
)


def seam_cut(source: str, extra_seams: dict[str, str]) -> int:
    trees = [(p, ast.parse(source) if p == COORD else t) for p, t in S.module_trees()]
    pkg = S.Package(trees)
    cls = pkg.classes[(S.COORDINATOR_MODULE, S.COORDINATOR_CLASS_NAME)]
    helpers = S.CoordinatorRoles(pkg).coordinator_helpers()
    return S.seam_metrics(cls, {**S.load_seam_map(), **extra_seams}, helpers)["seam_cut_total"]


def planted(source: str, edits) -> str | None:
    for old, new in edits:
        if source.count(old) != 1:
            return None
        source = source.replace(old, new)
    return source


def main() -> int:
    source = COORD.read_text()
    print(f"RESULT clean_seam_cut_total={seam_cut(source, {})} count")
    for name, edits, seams in (("alias", ALIAS, {}),
                               ("getter", GETTER, {"_cop_state": "learning"})):
        text = planted(source, edits)
        print(f"RESULT {name}_seam_cut_total="
              f"{'anchor-gone' if text is None else seam_cut(text, seams)} count")

    if not hasattr(S, "state_getter_reads"):
        print("# census: this tree's structure.py has no bare-getter rule")
        return 0
    pkg = S.Package(S.module_trees())
    cls = pkg.classes[(S.COORDINATOR_MODULE, S.COORDINATOR_CLASS_NAME)]
    seams = S.load_seam_map()
    methods = {m.name: m for m in cls.body
               if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))}
    units = {n: (f, S.SELF_ROOT) for n, f in methods.items()}
    units.update(S.CoordinatorRoles(pkg).coordinator_helpers())
    getters = {n: r for n, (f, roots) in units.items()
               if (r := S.state_getter_reads(f, roots, methods)) is not None}
    for n, reads in sorted(getters.items()):
        print(f"# getter {n} seam={seams[n]} reads={sorted(reads)}")
    props = {n for n, m in methods.items() if S._is_property(m)}
    cross: dict[str, set[str]] = {}
    for n, (f, roots) in units.items():
        for node in ast.walk(f):
            if (isinstance(node, ast.Attribute) and node.attr in props
                    and isinstance(node.value, ast.Name) and node.value.id in roots
                    and seams[n] != seams[node.attr]):
                cross.setdefault(node.attr, set()).add(seams[n])
    for p, readers in sorted(cross.items()):
        print(f"# property {p} seam={seams[p]} read_from={sorted(readers)} getter={p in getters}")
    print(f"RESULT bare_getters={len(getters)} count")
    print(f"RESULT properties_read_cross_seam={len(cross)} count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
