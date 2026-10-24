"""R10-STRUCTURE-ALIAS: the finder's two plants, replayed in memory, and the getter census.

The plants are the round-10 fix review's (probe/rev-2620-654004be, ev/plant_p2.diff
and ev/plant_p3.diff), re-anchored to the text they edit rather than to line numbers:
the alias binds ``prices = self._prices`` in ``_raise_cop_issue``; the getter adds a
``_cop_state`` in the learning seam returning ``(self._cop_baseline,
self._cop_health_cusum)`` and makes ``_scores_view`` read through it. Each is parsed
from the tree's own ``coordinator.py`` and priced by the tree's own
``tests/structure.py`` ``seam_metrics``, so the same command reads a base and a head.
A plant whose anchor is gone prints ``anchor-gone`` rather than a figure.

The getter is also planted in the five spellings its fix review (review/2711,
ev/variants.py) found still paying -- a leading ``pass``, ``tuple((...))``, a
``[:]`` copy, ``dict(...)``, a trailing ``None`` -- and two more of the same
plant: ``(a,) + (b,)`` and a list built by ``append``.

The census is the fixer.md step-8 rule: every coordinator unit whose return value
may hold state, as ``seam_metrics`` reads it (``returned_state``; ``<state>`` is
the coordinator itself), and every call crossing a seam into one, by a syntactic
over-approximation (a ``.name`` or ``name(...)`` naming the unit).

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
GETTER_BODIES = {
    "getter": "        return self._cop_baseline, self._cop_health_cusum",
    "getter_pass": "        pass\n        return self._cop_baseline, self._cop_health_cusum",
    "getter_tuple_call": "        return tuple((self._cop_baseline, self._cop_health_cusum))",
    "getter_slice_copy": "        return (self._cop_baseline, self._cop_health_cusum)[:]",
    "getter_dict_call": "        return dict(b=self._cop_baseline, c=self._cop_health_cusum)",
    "getter_trailing_none": "        return self._cop_baseline, self._cop_health_cusum, None",
    "getter_concat": "        return (self._cop_baseline,) + (self._cop_health_cusum,)",
    "getter_append": ("        out = []\n        out.append(self._cop_baseline)\n"
                      "        out.append(self._cop_health_cusum)\n        return out"),
}


def getter(body: str):
    """The O19 getter plant with ``body`` as ``_cop_state``'s body."""
    unpack = ("st = self._cop_state(); baseline, cusum = st['b'], st['c']" if "dict(" in body
              else "baseline, cusum, _none = self._cop_state()" if "None" in body
              else "baseline, cusum = self._cop_state()")
    return (
        ("    def _raise_cop_issue(self, baseline: float) -> None:\n",
         f"    def _cop_state(self):\n{body}\n\n"
         "    def _raise_cop_issue(self, baseline: float) -> None:\n"),
        ("        operation = self._operation_score\n        return compose_scores(",
         f"        operation = self._operation_score\n        {unpack}\n"
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
                               *((n, getter(b), {"_cop_state": "learning"})
                                 for n, b in GETTER_BODIES.items())):
        text = planted(source, edits)
        print(f"RESULT {name}_seam_cut_total="
              f"{'anchor-gone' if text is None else seam_cut(text, seams)} count")

    pkg = S.Package(S.module_trees())
    cls = pkg.classes[(S.COORDINATOR_MODULE, S.COORDINATOR_CLASS_NAME)]
    seams = S.load_seam_map()
    metrics = S.seam_metrics(cls, seams, S.CoordinatorRoles(pkg).coordinator_helpers())
    if "returned_state" not in metrics:
        print("# census: this tree's structure.py prices no callee by its return value")
        return 0
    escapes, transparent = metrics["returned_state"], metrics["transparent"]
    for n, held in sorted(escapes.items()):
        if held:
            print(f"# returns-state {n} seam={seams[n]} transparent={n in transparent}"
                  f" holds={sorted(held)}")
    # Every call crossing a seam into a unit that hands state back: each is
    # priced as what escapes (plus the edge unless transparent).
    pairs = set()
    for n, (fn, roots) in [*((m.name, (m, S.SELF_ROOT)) for m in cls.body
                             if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))),
                           *S.CoordinatorRoles(pkg).coordinator_helpers().items()]:
        for node in ast.walk(fn):
            callee = (node.func.attr if isinstance(node, ast.Call)
                      and isinstance(node.func, ast.Attribute) else
                      node.attr if isinstance(node, ast.Attribute) else
                      f"coordinator.{node.func.id}" if isinstance(node, ast.Call)
                      and isinstance(node.func, ast.Name) else None)
            if callee in escapes and escapes[callee] and seams[n] != seams[callee]:
                pairs.add((seams[n], callee))
    for caller, callee in sorted(pairs):
        print(f"# cross-seam {caller} -> {callee} ({seams[callee]})")
    print(f"RESULT units_returning_state={sum(1 for v in escapes.values() if v)} count")
    print(f"RESULT transparent_callees={len(transparent)} count")
    print(f"RESULT units_returning_coordinator="
          f"{sum(1 for v in escapes.values() if S.STATE_ESCAPE in v)} count")
    print(f"RESULT cross_seam_calls_of_state_returners={len(pairs)} count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
