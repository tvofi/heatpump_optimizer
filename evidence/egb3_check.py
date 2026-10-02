import ast, sys
from pathlib import Path
class _R:
    fails=0
    def check(self, name, ok, detail=""):
        print(("  ok   " if ok else "  FAIL ")+name+("" if ok else "  :: "+detail))
        if not ok: self.fails+=1
R=_R()
# EG-B3: the published key set, enumerated from the producers, equals Payload.
# Rule: the keys of every dict a producer returns, assigns to what it publishes
# or passes to ``update``, plus ``data["k"] =`` stores; a ``**x`` / ``update(x)``
# source is resolved through ``_egb3_resolve`` and a source not listed there
# fails, so a new spread cannot be missed (the review of #1852 found one that a
# golden-union and a read of the producers both missed).
_egb3_pkg = Path("custom_components/heatpump_optimizer")
_egb3_src = {p.stem: ast.parse(p.read_text()) for p in _egb3_pkg.glob("*.py")}


def _egb3_fn(mod, name, cls=None):
    for n in ast.walk(_egb3_src[mod]):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name:
            return n
    raise KeyError((mod, name))


def _egb3_lit(d):
    return {k.value for k in d.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)}


def _egb3_top(fn, names=("data", "out")):
    """String keys fn writes at its dict's top level: displays that are returned,
    assigned or passed to update, plus ``data["k"] =`` stores (tuple targets too)."""
    keys, merges, parent = set(), [], {}
    for p in ast.walk(fn):
        for c in ast.iter_child_nodes(p):
            parent[c] = p
    carried = set(names)  # local names whose dict is what the function publishes
    for n in ast.walk(fn):
        if isinstance(n, ast.Return) and isinstance(n.value, ast.Name):
            carried.add(n.value.id)
        if isinstance(n, ast.Dict):
            carried |= {v.id for k, v in zip(n.keys, n.values) if k is None and isinstance(v, ast.Name)}
    for n in ast.walk(fn):
        if isinstance(n, ast.Dict):
            par = parent.get(n)
            if (isinstance(par, ast.Return)
                    or (isinstance(par, ast.Call) and getattr(par.func, "attr", "") == "update")
                    or (isinstance(par, (ast.Assign, ast.AnnAssign))
                        and any(isinstance(t, ast.Name) and t.id in carried
                                for t in (par.targets if isinstance(par, ast.Assign) else [par.target])))):
                keys |= _egb3_lit(n)
                merges += [v for k, v in zip(n.keys, n.values) if k is None]
        if isinstance(n, ast.Assign):
            for t in n.targets:
                for s in (t.elts if isinstance(t, ast.Tuple) else [t]):
                    if (isinstance(s, ast.Subscript) and isinstance(s.slice, ast.Constant)
                            and isinstance(s.slice.value, str)
                            and isinstance(s.value, ast.Name) and s.value.id in names):
                        keys.add(s.slice.value)
        if (isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "update"
                and n.args and not isinstance(n.args[0], ast.Dict)):
            merges.append(n.args[0])
    return keys, merges


# How each merge source in a producer resolves: the one hand-written part, and it
# is checked: an unlisted source fails, so a new spread cannot slip past.
_egb3_resolve = {
    "self._legionella.disinfect.view()": ("disinfection", "view"),
    "self._away_state.as_dict()": ("away", "as_dict"),
    "_plan_settings_view(ctx._opt_config)": ("coordinator", "_plan_settings_view"),
    "plan_views": ("coordinator", "_build_plan_views"),
}
_egb3_inline = {"two_tank", "view()", "{k: round(v, 4) for k, v in self._energy_totals.items()}"}


def _egb3_energy():
    for n in ast.walk(_egb3_src["coordinator"]):
        if (isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Attribute)
                and n.target.attr == "_energy_totals" and isinstance(n.value, ast.Dict)):
            return _egb3_lit(n.value)
    raise KeyError("_energy_totals")


def _egb3_enumerate(fn, unresolved):
    keys, merges = _egb3_top(fn)
    for m in merges:
        src = ast.unparse(m)
        if src in _egb3_resolve:
            keys |= _egb3_enumerate(_egb3_fn(*_egb3_resolve[src]), unresolved)
        elif "_energy_totals" in src:
            keys |= _egb3_energy()
        elif src not in _egb3_inline:
            unresolved.add(src)
    return keys


def _egb3_published():
    build = _egb3_fn("coordinator", "_build_data_dict")
    roots = [build] + [_egb3_fn("coordinator", n) for n in (
        "_apply_result_payload", "_apply_unsolved_payload", "_with_sensor_advisor")]
    for n in ast.walk(build):  # the views the assembler loops over
        if isinstance(n, ast.For) and isinstance(n.iter, ast.Tuple):
            roots += [_egb3_fn("coordinator", e.attr) for e in n.iter.elts]
    unresolved, keys = set(), set()
    for r in roots:
        keys |= _egb3_enumerate(r, unresolved)
    return keys, unresolved


def _egb3_payload_keys():
    cls = next(n for n in _egb3_src["payload"].body
               if isinstance(n, ast.ClassDef) and n.name == "Payload")
    return {a.target.id for a in cls.body if isinstance(a, ast.AnnAssign)}

def _egb3_class(name):
    cls = next(n for n in _egb3_src["payload"].body
               if isinstance(n, ast.ClassDef) and n.name == name)
    return {a.target.id for a in cls.body if isinstance(a, ast.AnnAssign)}


def _egb3_insight():
    ret = next(n for n in ast.walk(_egb3_fn("coordinator", "_insight_view"))
               if isinstance(n, ast.Return) and isinstance(n.value, ast.Dict))
    nested = {k.value: v for k, v in zip(ret.value.keys, ret.value.values)
              if isinstance(k, ast.Constant)}["compressor_starts"]
    return _egb3_lit(ret.value), _egb3_lit(nested)


_egb3_pub, _egb3_unres = _egb3_published()
_egb3_pk = _egb3_payload_keys()
R.check(
    "EG-B3: every merge source in the payload producers is resolved",
    not _egb3_unres,
    repr(sorted(_egb3_unres)),
)
R.check(
    "EG-B3: Payload declares exactly the keys the producers publish",
    _egb3_pub == _egb3_pk,
    f"published-not-declared={sorted(_egb3_pub - _egb3_pk)} "
    f"declared-not-published={sorted(_egb3_pk - _egb3_pub)}",
)
_egb3_ins, _egb3_cs = _egb3_insight()
R.check(
    "EG-B3: Insight and CompressorStarts declare the keys _insight_view writes",
    _egb3_ins == _egb3_class("Insight") and _egb3_cs == _egb3_class("CompressorStarts"),
    f"insight={sorted(_egb3_ins ^ _egb3_class('Insight'))} "
    f"compressor_starts={sorted(_egb3_cs ^ _egb3_class('CompressorStarts'))}",
)



print("RESULT egb3_fails", R.fails, "published", len(_egb3_pub), "declared", len(_egb3_pk), "unresolved", sorted(_egb3_unres))
