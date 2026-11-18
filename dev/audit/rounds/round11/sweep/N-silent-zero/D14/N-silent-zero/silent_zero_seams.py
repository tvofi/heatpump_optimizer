"""N-silent-zero class sweep (round 11, D14 steps 3-4).

Class mechanism: a derivation's failure path returns the same empty value as its success
path, so the caller (or a count over the result) reads a failure as a clean value. One
family per shape the round-11 findings took, each an AST rule over the production package
and tools/replay (the debug-bundle instruments D15 judged):

  A  absent == unparseable   a parser that returns None both from an emptiness guard and
                             from a None-on-failure parse call (stored_instant, parse_*,
                             fromisoformat via a helper): the caller cannot tell "cleared"
                             from "garbage" (D10-s1-01).
  B  refusal acknowledged    an entity action handler (async_press / async_turn_on|off /
                             async_set_value / async_select_option / _press / _async_set_*)
                             that hands a coordinator action to off_the_action (not awaited)
                             or awaits one and discards a result the coordinator method can
                             return non-None (a reason / a bool) (D10-s1-02).
  C1 sentinel zero           a dict entry whose key names a measurement (_ms, _kwh, _s,
                             count, n_) published as the literal 0 next to a not-run/failed
                             status, which a consumer folds as a real measurement (D15-s3-01).
  C2 no evidence passes      `if <v> is not None:` whose body rejects (continue / return
                             None|False) with no else: a missing value skips the check and
                             passes the filter as clean (D17-s3-03).
  D1 fixed denominator       a RESULT/verdict f-string `{N - len(x)}/N` with N a literal (D15-s1-03).
  D2 vacuous check           a check over `<doc>.get(k) or {}|[]` whose emptiness is not
                             itself checked (D15-s1-03's replay-clean).
  D3 unloaded replay         a tools/replay entry that constructs the coordinator through the
                             harness without enable_store_loads, so a load-gated path
                             (`if not self._<x>_loaded: return`) is silently never run (D15-s2-03);
                             listed with every load-gated early return in the package.

Run:  python3 silent_zero_seams.py [--json]
      --null    a clean fixture (distinct failure value, awaited+checked action, filtered
                sentinel, derived denominator)                      -> seams=0
      --plant F the clean fixture plus ONE line of family F (A|B|C1|C2|D1|D2) -> that family = 1
"""
from __future__ import annotations

import ast
import json
import pathlib
import re
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[6]
SCOPES = [REPO / "custom_components" / "heatpump_optimizer", REPO / "tools" / "replay"]
PARSERS = re.compile(r"(^|_)(parse|instant|fromiso|from_iso)", re.I)
ACTIONS = re.compile(r"^(async_press|async_turn_on|async_turn_off|async_set_value|async_select_option|_press|_async_set_\w+|async_set_\w+)$")
MEAS = re.compile(r"(_ms|_kwh|_s|_count|count|^n_|_n)$")
NOTRUN = re.compile(r"not_run|failed|skipped|unsolved|error", re.I)


def _const_none(n):
    return isinstance(n, ast.Constant) and n.value is None


def _rel(path):
    return str(path.relative_to(REPO))


def nonnull_returners(trees):
    """Coordinator (any class) async methods with a `return <non-None>` -- a refusal channel."""
    out = set()
    for _, tree in trees:
        for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
            for fn in cls.body:
                if isinstance(fn, ast.AsyncFunctionDef):
                    for r in ast.walk(fn):
                        if isinstance(r, ast.Return) and r.value is not None and not _const_none(r.value):
                            out.add(fn.name)
                            break
    return out


def scan(trees, refusers):
    seams = []

    def add(fam, path, node, sym, text):
        seams.append({"family": fam, "file": _rel(path), "line": node.lineno, "symbol": sym, "text": text[:110]})

    for path, tree in trees:
        parents = {}
        for p in ast.walk(tree):
            for c in ast.iter_child_nodes(p):
                parents[c] = p

        def owner(node):
            names = []
            cur = node
            while cur in parents:
                cur = parents[cur]
                if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    names.append(cur.name)
            return ".".join(reversed(names)) or "<module>"

        for fn in (n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))):
            sym = fn.name if owner(fn) == "<module>" else f"{owner(fn)}.{fn.name}"
            rets = [r for r in ast.walk(fn) if isinstance(r, ast.Return)]
            # A: guard returns None AND a parse call is returned
            guard_none = any(_const_none(r.value) for r in rets)
            parse_ret = [r for r in rets if isinstance(r.value, ast.Call) and PARSERS.search(
                (r.value.func.attr if isinstance(r.value.func, ast.Attribute) else getattr(r.value.func, "id", "")) or "")]
            if guard_none and parse_ret and PARSERS.search(fn.name):
                add("A", path, fn, sym, f"returns None on its guard and {ast.unparse(parse_ret[0].value)[:60]}")
            # B: entity action handlers
            if ACTIONS.match(fn.name) and "custom_components" in str(path) and path.stem not in ("coordinator",):
                for c in ast.walk(fn):
                    if not isinstance(c, ast.Call):
                        continue
                    f = c.func
                    name = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")
                    if name == "off_the_action" and len(c.args) >= 2 and isinstance(c.args[1], ast.Call):
                        inner = c.args[1].func
                        iname = inner.attr if isinstance(inner, ast.Attribute) else ""
                        if iname != "async_request_refresh":
                            add("B", path, c, sym, f"off_the_action(.., {ast.unparse(c.args[1])[:60]}) -- not awaited")
                for st in ast.walk(fn):
                    if isinstance(st, ast.Expr) and isinstance(st.value, ast.Await) and isinstance(st.value.value, ast.Call):
                        f = st.value.value.func
                        if isinstance(f, ast.Attribute) and "coordinator" in ast.unparse(f.value) and f.attr in refusers:
                            add("B", path, st, sym, f"await {ast.unparse(f)}(..) result discarded; it can return non-None")
            # C2: `if v is not None:` rejecting body, no else
            for n in ast.walk(fn):
                if (isinstance(n, ast.If) and not n.orelse and isinstance(n.test, ast.Compare)
                        and len(n.test.ops) == 1 and isinstance(n.test.ops[0], ast.IsNot) and _const_none(n.test.comparators[0])):
                    rejects = any(isinstance(b, ast.Continue) or (isinstance(b, ast.Return) and (
                        b.value is None or _const_none(b.value) or (isinstance(b.value, ast.Constant) and b.value.value is False)))
                        for b in ast.walk(ast.Module(body=n.body, type_ignores=[])))
                    if rejects:
                        add("C2", path, n, sym, f"if {ast.unparse(n.test)}: <reject> -- None passes")
            # D3: load-gated silent early return
            for n in ast.walk(fn):
                if (isinstance(n, ast.If) and isinstance(n.test, ast.UnaryOp) and isinstance(n.test.op, ast.Not)
                        and isinstance(n.test.operand, ast.Attribute) and n.test.operand.attr.endswith("_loaded")
                        and len(n.body) == 1 and isinstance(n.body[0], ast.Return)):
                    add("D3", path, n, sym, f"if not {ast.unparse(n.test.operand)}: return (silent)")
        # C1: sentinel zero next to a not-run status in one dict literal
        for d in (n for n in ast.walk(tree) if isinstance(n, ast.Dict)):
            vals = {k.value: v for k, v in zip(d.keys, d.values) if isinstance(k, ast.Constant) and isinstance(k.value, str)}
            status = any(isinstance(v, ast.Constant) and isinstance(v.value, str) and NOTRUN.search(v.value) for v in vals.values())
            if status:
                for k, v in vals.items():
                    if MEAS.search(k) and isinstance(v, ast.Constant) and v.value == 0 and not isinstance(v.value, bool):
                        add("C1", path, v, owner(d), f'"{k}": 0 beside a not-run status')
        # D1 / D2 (instrument code: tools/ and any RESULT printer)
        for n in ast.walk(tree):
            if isinstance(n, ast.JoinedStr):
                src = ast.unparse(n)
                m = re.search(r"\{(\d+) - len\([^}]*\)\}/(\d+)", src)
                if m and m.group(1) == m.group(2):
                    add("D1", path, n, owner(n), f"fixed denominator /{m.group(2)}")
            if (isinstance(n, ast.BoolOp) and isinstance(n.op, ast.Or) and len(n.values) == 2
                    and isinstance(n.values[0], ast.Call) and isinstance(n.values[0].func, ast.Attribute)
                    and n.values[0].func.attr == "get" and isinstance(n.values[1], (ast.Dict, ast.List))
                    and not (n.values[1].keys if isinstance(n.values[1], ast.Dict) else n.values[1].elts)
                    and "tools" in str(path)):
                add("D2", path, n, owner(n), f"{ast.unparse(n)} -- an absent section reads as an empty clean one")
    # D3 entry side: tools/replay coordinator builders without enable_store_loads
    for path, tree in trees:
        if "tools" not in str(path):
            continue
        src = ast.unparse(tree)
        if "HeatPumpOptimizerCoordinator(" in src and "enable_store_loads" not in src:
            n = next(x for x in ast.walk(tree) if isinstance(x, ast.Call) and "HeatPumpOptimizerCoordinator" in ast.unparse(x.func))
            add("D3", path, n, "<builder>", "builds the coordinator without enable_store_loads")
    return seams


CLEAN = '''
def _parse_when(raw):
    if not raw:
        return None
    out = stored_instant(raw)
    if out is None:
        raise ValueError(raw)
    return out
class B:
    async def async_press(self):
        reason = await self.coordinator.async_arm()
        if reason is not None:
            raise RuntimeError(reason)
class Coord:
    async def async_arm(self):
        return "refused"
def unsolved():
    return {"optimization_status": "not_run", "solve_time_ms": None}
def pick(snaps):
    for s in snaps:
        bias = s.get("bias")
        if bias is None or abs(bias) > 1:
            continue
        return s
def verdict(fails, checks):
    print(f"RESULT stages_ok={len(checks) - len(fails)}/{len(checks)}")
'''
PLANTS = {
    "A": "def _parse_at(raw):\n    if not raw:\n        return None\n    return stored_instant(raw)\n",
    "B": "class B2:\n    async def async_press(self):\n        off_the_action(self, self.coordinator.async_arm())\n",
    "C1": "def unsolved2():\n    return {\"optimization_status\": \"not_run\", \"solve_time_ms\": 0}\n",
    "C2": "def pick2(snaps):\n    for s in snaps:\n        bias = s.get('bias')\n        if bias is not None:\n            if abs(bias) > 1:\n                continue\n        return s\n",
    "D1": "def verdict2(fails):\n    print(f'RESULT stages_ok={12 - len(fails)}/12')\n",
    "D2": "def clean2(bundle):\n    doc = bundle.get('replay') or {}\n    return not violations(doc)\n",
}


def load(roots):
    out = []
    for root in roots:
        for p in sorted(root.rglob("*.py")):
            try:
                out.append((p, ast.parse(p.read_text(), str(p))))
            except SyntaxError:
                pass
    return out


def main() -> int:
    a = sys.argv[1:]
    global REPO
    with tempfile.TemporaryDirectory() as tmp:
        if "--null" in a or "--plant" in a:
            REPO = pathlib.Path(tmp)
            root = REPO / "tools" / "fixture"
            root.mkdir(parents=True)
            src = CLEAN + ("\n" + PLANTS[a[a.index("--plant") + 1]] if "--plant" in a else "")
            (root / "fix.py").write_text(src)
            # the fixture's entity class sits under custom_components for family B
            cc = REPO / "custom_components" / "fixture"
            cc.mkdir(parents=True)
            (cc / "ent.py").write_text(src)
            (root / "fix.py").write_text("\n".join(l for l in src.splitlines()))
            trees = load([cc]) if "--plant" in a and a[a.index("--plant") + 1] in ("B",) else load([root])
        else:
            trees = load(SCOPES)
        seams = scan(trees, nonnull_returners(trees))
    if "--json" in a:
        print(json.dumps(seams, indent=1))
    fam = {}
    for s in seams:
        fam[s["family"]] = fam.get(s["family"], 0) + 1
        print(f"SEAM {s['family']:3s} {s['file']}:{s['line']} {s['symbol']} :: {s['text']}")
    print("RESULT seams=%d %s" % (len(seams), " ".join(f"{k}={v}" for k, v in sorted(fam.items()))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
