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

Round 3 (review/2711 at b43ea541) plants the same getter once per channel a
callee can hand state on through (return, yield, raise, an argument it stores
into, mutates or calls, a ``global``) and once per way it can be reached (its
class, a literal name, ``vars``/``__dict__``, a bound method handed on, a
parameter not spelt ``self``, a dunder, a class-body descriptor): ``ROUND3``.
Each must read at least the clean figure (a dunder reached by every
whole-value use of the coordinator, or a computed name read as every stored
attribute, reads more). ``DISPOSITIONED`` prints the one arm the
body dispositions rather than closes; ``NULL`` plants one new cross-seam edge,
called and referenced, which must cost +2 either way.

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
    return plant(f"    def _cop_state(self):\n{body}\n", unpack)


def plant(defs: str, call: str):
    """``defs`` added to the class before ``_raise_cop_issue`` (learning), and
    ``_scores_view`` (views) reading ``baseline, cusum`` by ``call`` in place
    of its two direct reads."""
    return (
        ("    def _raise_cop_issue(self, baseline: float) -> None:\n",
         f"{defs}\n    def _raise_cop_issue(self, baseline: float) -> None:\n"),
        ("        operation = self._operation_score\n        return compose_scores(",
         f"        operation = self._operation_score\n        {call}\n"
         "        return compose_scores("),
        ("machine_score(self._cop_baseline, self._cop_health_cusum.stat),",
         "machine_score(baseline, cusum.stat),"),
    )


# Round 3 (review/2711 at b43ea541): every channel a callee hands state on
# through, and every way the callee is reached, planted on the same getter.
# Each must read at least the clean figure. ``D`` is the two reads.
D = "self._cop_baseline, self._cop_health_cusum"
R = f"    def _cop_state(self):\n        return {D}\n"
ROUND3 = {
    # channel: the return value, spelt as review/2711's variants spelt it
    "ret_nested_def": (f"    def _cop_state(self):\n        def g():\n            return {D}\n"
                       "        return g()\n", "baseline, cusum = self._cop_state()"),
    "ret_lambda_call": (f"    def _cop_state(self):\n        return (lambda: ({D}))()\n",
                        "baseline, cusum = self._cop_state()"),
    "ret_dict_unpack": ("    def _cop_state(self):\n        return {**{'b': self._cop_baseline},"
                        " 'c': self._cop_health_cusum}\n",
                        "st = self._cop_state(); baseline, cusum = st['b'], st['c']"),
    "ret_iadd": ("    def _cop_state(self):\n        x = [self._cop_baseline]\n"
                 "        x += [self._cop_health_cusum]\n        return x\n",
                 "baseline, cusum = self._cop_state()"),
    "ret_try": (f"    def _cop_state(self):\n        try:\n            return {D}\n"
                "        finally:\n            pass\n", "baseline, cusum = self._cop_state()"),
    "ret_yield": ("    def _cop_state(self):\n        yield self._cop_baseline\n"
                  "        yield self._cop_health_cusum\n", "baseline, cusum = self._cop_state()"),
    # channel: an argument the callee stores into, mutates or calls
    "out_dict": ("    def _cop_state(self, out):\n        out['b'] = self._cop_baseline\n"
                 "        out['c'] = self._cop_health_cusum\n",
                 "st = {}; self._cop_state(st); baseline, cusum = st['b'], st['c']"),
    "out_append": ("    def _cop_state(self, out):\n        out.append(self._cop_baseline)\n"
                   "        out.append(self._cop_health_cusum)\n",
                   "st = []; self._cop_state(st); baseline, cusum = st"),
    "out_attr": ("    def _cop_state(self, out):\n        out.b = self._cop_baseline\n"
                 "        out.c = self._cop_health_cusum\n",
                 "st = types.SimpleNamespace(); self._cop_state(st); baseline, cusum = st.b, st.c"),
    "out_setattr": ("    def _cop_state(self, out):\n        setattr(out, 'b', self._cop_baseline)\n"
                    "        setattr(out, 'c', self._cop_health_cusum)\n",
                    "st = types.SimpleNamespace(); self._cop_state(st); baseline, cusum = st.b, st.c"),
    "out_extend": (f"    def _cop_state(self, out):\n        out.extend(({D}))\n",
                   "st = []; self._cop_state(st); baseline, cusum = st"),
    "out_alias": (f"    def _cop_state(self, out):\n        o = out\n        o.extend(({D}))\n",
                  "st = []; self._cop_state(st); baseline, cusum = st"),
    "out_part": (f"    def _cop_state(self, out):\n        out.setdefault('k', []).extend(({D}))\n",
                 "st = {}; self._cop_state(st); baseline, cusum = st['k']"),
    "out_forwarded": (f"    def _cop_state(self, out):\n        out.extend(({D}))\n\n"
                      "    def _cop_relay(self, out):\n        self._cop_state(out)\n",
                      "st = []; self._cop_relay(st); baseline, cusum = st"),
    "callback": (f"    def _cop_state(self, cb):\n        cb({D})\n",
                 "box = []; self._cop_state(lambda a, b: box.extend((a, b))); baseline, cusum = box"),
    "callback_kw": (f"    def _cop_state(self, *, cb):\n        f = cb\n        f({D})\n",
                    "box = []; self._cop_state(cb=lambda a, b: box.extend((a, b))); baseline, cusum = box"),
    "global": (f"    def _cop_state(self):\n        global _COP_SEEN\n        _COP_SEEN = ({D})\n",
               "self._cop_state(); baseline, cusum = _COP_SEEN"),
    # channel: an exception raised, let pass, or caught and handed on
    "raise": (f"    def _cop_state(self):\n        raise LookupError({D})\n",
              "try:\n            self._cop_state()\n        except LookupError as e:\n"
              "            baseline, cusum = e.args"),
    "raise_through": (f"    def _cop_state(self):\n        raise LookupError({D})\n\n"
                      "    def _cop_relay(self):\n        self._cop_state()\n",
                      "try:\n            self._cop_relay()\n        except LookupError as e:\n"
                      "            baseline, cusum = e.args"),
    "raise_caught": (f"    def _cop_state(self):\n        raise LookupError({D})\n\n"
                     "    def _cop_relay(self):\n        try:\n            self._cop_state()\n"
                     "        except LookupError as e:\n            return e.args\n",
                     "baseline, cusum = self._cop_relay()"),
    # reach: through the class, a literal name, a dict
    "call_type_self": (R, "baseline, cusum = type(self)._cop_state(self)"),
    "call_class_attr": (R, "baseline, cusum = self.__class__._cop_state(self)"),
    "call_class_name": (R, "baseline, cusum = HeatPumpOptimizerCoordinator._cop_state(self)"),
    "call_getattr": (R, "baseline, cusum = getattr(self, '_cop_state')()"),
    "body_const_getattr": ("    def _cop_state(self):\n        return getattr(self, '_cop_baseline'),"
                           " getattr(self, '_cop_health_cusum')\n",
                           "baseline, cusum = self._cop_state()"),
    "body_vars_dict": ("    def _cop_state(self):\n        return vars(self)['_cop_baseline'],"
                       " self.__dict__.get('_cop_health_cusum')\n",
                       "baseline, cusum = self._cop_state()"),
    "read_const_getattr": ("", "baseline, cusum = getattr(self, '_cop_baseline'),"
                           " getattr(self, '_cop_health_cusum')"),
    "computed_getattr": ("    def _cop_state(self):\n        n = '_cop_'\n"
                         "        return getattr(self, n + 'baseline'), getattr(self, n + 'health_cusum')\n",
                         "baseline, cusum = self._cop_state()"),
    "read_literal_loop": ("", "baseline, cusum = (getattr(self, n) for n in"
                          " ('_cop_baseline', '_cop_health_cusum'))"),
    "read_computed_getattr": ("", "n = '_cop_'; baseline, cusum = getattr(self, n + 'baseline'),"
                              " getattr(self, n + 'health_cusum')"),
    # reach: handed on uncalled
    "call_bound_alias": (R, "g = self._cop_state; baseline, cusum = g()"),
    "call_partial": (R, "baseline, cusum = functools.partial(self._cop_state)()"),
    "call_dunder_call": (R, "baseline, cusum = self._cop_state.__call__()"),
    "call_higher_order": (R, "baseline, cusum = (lambda f: f())(self._cop_state)"),
    # reach: the coordinator in a parameter not spelt self
    "param_me": ("    def _cop_state(me):\n        return me._cop_baseline, me._cop_health_cusum\n",
                 "baseline, cusum = self._cop_state()"),
    "param_extra": ("    def _cop_state(self, me):\n        return me._cop_baseline, me._cop_health_cusum\n",
                    "baseline, cusum = self._cop_state(self)"),
    "param_static": ("    @staticmethod\n    def _cop_state(me):\n"
                     "        return me._cop_baseline, me._cop_health_cusum\n",
                     "baseline, cusum = self._cop_state(self)"),
    "param_alias": ("    def _cop_state(self, me):\n        return me._cop_baseline, me._cop_health_cusum\n",
                    "g = self._cop_state; baseline, cusum = g(self)"),
    "param_partial": ("    def _cop_state(self, me):\n        return me._cop_baseline, me._cop_health_cusum\n",
                      "baseline, cusum = functools.partial(self._cop_state, self)()"),
    # reach: a dunder Python calls unnamed
    "dunder_getitem": (f"    def __getitem__(self, k):\n        return ({D})[k]\n",
                       "baseline, cusum = self[0], self[1]"),
    "dunder_iter": (f"    def __iter__(self):\n        return iter(({D}))\n",
                    "baseline, cusum = self"),
    "dunder_getattr": (f"    def __getattr__(self, name):\n        return {D}\n",
                       "baseline, cusum = self._cop_pair"),
    # reach: a class-body descriptor
    "desc_lambda": (f"    _cop_pair = property(lambda s: (s._cop_baseline, s._cop_health_cusum))\n",
                    "baseline, cusum = self._cop_pair"),
    "desc_factory": ("    _cop_pair = _view_pair('_cop_baseline', '_cop_health_cusum')\n",
                     "baseline, cusum = self._cop_pair"),
    "desc_method": (f"    def _cop_get(self):\n        return {D}\n    _cop_pair = property(_cop_get)\n",
                    "baseline, cusum = self._cop_pair"),
}
# Dispositioned, not closed (the body says why): it prints its figure.
DISPOSITIONED = {
    # the reads copied into a slot that outlives the call: the slot is the state
    "snapshot_attr": (f"    def _cop_state(self):\n        self._cop_pair = ({D})\n",
                      "baseline, cusum = self._cop_pair"),
}
# Null control: a reference to a learning unit that hands nothing on is one
# new views -> learning edge, +2 (once in each seam's cut), called or not.
NULL = {
    "edge_called": ("    def _cop_touch(self):\n        self._cop_baseline = 0.0\n",
                    "self._cop_touch(); baseline, cusum = " + D),
    "edge_referenced": ("    def _cop_touch(self):\n        self._cop_baseline = 0.0\n",
                        "self.hass.async_create_task(self._cop_touch); baseline, cusum = " + D),
}


def new_units(defs: str) -> dict[str, str]:
    body = ast.parse("class _:\n" + defs).body[0].body if defs else []
    return {n.name: "learning" for n in body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


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
                                 for n, b in GETTER_BODIES.items()),
                               *((n, plant(d, c), new_units(d))
                                 for n, (d, c) in {**ROUND3, **DISPOSITIONED, **NULL}.items())):
        text = planted(source, edits)
        print(f"RESULT {name}_seam_cut_total="
              f"{'anchor-gone' if text is None else seam_cut(text, seams)} count")
    print(f"RESULT clean_again_seam_cut_total={seam_cut(source, {})} count")

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
    if "unresolved_unit_names" in metrics:
        # Round 3: the other channels, and every occurrence of a unit's name
        # the scan did not read as a call or a reference -- the seams a
        # syntactic census finds that seam_metrics does not price.
        left, raised = metrics["left_state"], metrics["raised_state"]
        for n, held in sorted(left.items()):
            if held:
                print(f"# leaves-state {n} seam={seams[n]} holds={sorted(held)}")
        for n, held in sorted(raised.items()):
            if held:
                print(f"# raises-state {n} seam={seams[n]} holds={sorted(held)}")
        for unit, line, name in metrics["unresolved_unit_names"]:
            print(f"# unresolved {unit}:{line} names {name}")
        for unit, line in metrics["computed_names"]:
            print(f"# computed-name {unit}:{line}")
        print(f"RESULT units_leaving_state={sum(1 for v in left.values() if v)} count")
        print(f"RESULT units_raising_state={sum(1 for v in raised.values() if v)} count")
        print(f"RESULT unresolved_unit_names={len(metrics['unresolved_unit_names'])} count")
        print(f"RESULT computed_names={len(metrics['computed_names'])} count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
