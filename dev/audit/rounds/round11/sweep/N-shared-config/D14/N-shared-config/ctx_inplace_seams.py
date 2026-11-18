"""N-shared-config class sweep (round 11, D14 steps 3-4): every in-place edit of a
CoordinatorContext member, i.e. a write that every context sharing that member sees.

CoordinatorContext is frozen and published whole (`coord._ctx = replace(ctx, ...)`), but
`replace` copies member references, so an edit INTO a member (`_opt_config`, `_thermal_params`,
`_current_state`, `_config`) reaches every superseded context still held across an await,
and a solve or reader holding one. A seam is, anywhere in the package (subpackages too):

  assign   an assignment / aug-assignment whose target is rooted at a member expression
           (`<x>.<member>.<field> = ...`, `<x>.<member>.<f>[k] = ...`) or at a local alias of one
           (`cfg = ctx._opt_config; cfg.f = ...`, `p = getattr(c, "_thermal_params")`);
  setattr  `setattr(<member or alias>, ...)` / `object.__setattr__(...)` / `vars(<m>).update`;
  mutate   a mutator call (append/extend/update/clear/pop/add/remove/insert/setdefault/discard)
           on a container reached from a member or alias.

The round-11 finder's seam rule (`enum_m4.py | grep ctx_inplace`) is the `assign` arm without
aliases or subpackages; this widens it.

Run:  python3 ctx_inplace_seams.py [--root PKG] [--json]
      --null    a clean fixture (publish by replace, reads only)                -> seams=0
      --plant   the clean fixture plus ONE aliased edit (`cfg.min_temp = 1.0`)  -> seams=1
"""
from __future__ import annotations

import ast
import json
import pathlib
import sys
import tempfile

MEMBERS = ("_opt_config", "_thermal_params", "_current_state", "_config")
MUTATORS = {"append", "extend", "update", "clear", "pop", "add", "remove", "insert", "setdefault", "discard", "popitem"}
PKG = pathlib.Path(__file__).resolve().parents[6] / "custom_components" / "heatpump_optimizer"


def _member_expr(n: ast.AST) -> str | None:
    if isinstance(n, ast.Attribute) and n.attr in MEMBERS:
        return n.attr
    if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "getattr"
            and len(n.args) >= 2 and isinstance(n.args[1], ast.Constant) and n.args[1].value in MEMBERS):
        return n.args[1].value
    return None


class _Scan(ast.NodeVisitor):
    def __init__(self, rel: str):
        self.rel, self.out, self.stack, self.alias = rel, [], [], [{}]

    def _sym(self):
        return ".".join(self.stack) or "<module>"

    def _root_member(self, n: ast.AST) -> str | None:
        """The member a target/receiver is reached from, walking .attr and [k] down to a root."""
        cur = n
        while isinstance(cur, (ast.Attribute, ast.Subscript)):
            m = _member_expr(cur.value) if isinstance(cur, (ast.Attribute, ast.Subscript)) else None
            if m:
                return m
            cur = cur.value
        if isinstance(cur, ast.Name):
            return self.alias[-1].get(cur.id)
        return None

    def _fn(self, node):
        self.stack.append(node.name); self.alias.append({})
        self.generic_visit(node)
        self.stack.pop(); self.alias.pop()

    visit_FunctionDef = visit_AsyncFunctionDef = _fn

    def visit_ClassDef(self, node):
        self.stack.append(node.name); self.generic_visit(node); self.stack.pop()

    def _add(self, node, kind, member, text):
        self.out.append({"file": self.rel, "line": node.lineno, "symbol": self._sym(), "kind": kind,
                         "member": member, "text": text})

    def _targets(self, targets, value, node):
        for t in targets:
            for e in (t.elts if isinstance(t, ast.Tuple) else [t]):
                if isinstance(e, ast.Name):
                    m = _member_expr(value) if value is not None else None
                    if m:
                        self.alias[-1][e.id] = m
                    else:
                        self.alias[-1].pop(e.id, None)
                elif isinstance(e, (ast.Attribute, ast.Subscript)):
                    m = self._root_member(e)
                    if m:
                        self._add(node, "assign", m, ast.unparse(e))

    def visit_Assign(self, node):
        self._targets(node.targets, node.value, node); self.generic_visit(node)

    def visit_AugAssign(self, node):
        self._targets([node.target], None, node); self.generic_visit(node)

    def visit_AnnAssign(self, node):
        self._targets([node.target], node.value, node); self.generic_visit(node)

    def visit_Call(self, node):
        f = node.func
        name = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)
        if name in ("setattr", "__setattr__") and node.args:
            m = _member_expr(node.args[0]) or self._root_member(node.args[0]) or (
                self.alias[-1].get(node.args[0].id) if isinstance(node.args[0], ast.Name) else None)
            if m:
                self._add(node, "setattr", m, ast.unparse(node)[:90])
        if isinstance(f, ast.Attribute) and f.attr in MUTATORS:
            recv = f.value
            m = None
            if isinstance(recv, ast.Call) and isinstance(recv.func, ast.Name) and recv.func.id == "vars" and recv.args:
                m = _member_expr(recv.args[0]) or self._root_member(recv.args[0])
            elif isinstance(recv, (ast.Attribute, ast.Subscript)) and not _member_expr(recv):
                m = self._root_member(recv)
            if m:
                self._add(node, "mutate", m, ast.unparse(node)[:90])
        self.generic_visit(node)


def scan(pkg: pathlib.Path) -> list[dict]:
    out = []
    for path in sorted(pkg.rglob("*.py")):
        s = _Scan(str(path.relative_to(pkg.parents[1])))
        s.visit(ast.parse(path.read_text(), str(path)))
        out.extend(s.out)
    return out


CLEAN = '''
from dataclasses import replace
async def set_target(self, t):
    ctx = self._ctx
    self._ctx = replace(ctx, _opt_config=replace(ctx._opt_config, target_temp=t))
def read(self):
    cfg = self._ctx._opt_config
    return cfg.min_temp + self._ctx._thermal_params.x
'''
PLANT = "def plant(self):\n    cfg = self._ctx._opt_config\n    cfg.min_temp = 1.0\n"


def main() -> int:
    args = sys.argv[1:]
    root = PKG
    if "--root" in args:
        root = pathlib.Path(args[args.index("--root") + 1])
    with tempfile.TemporaryDirectory() as tmp:
        if "--null" in args or "--plant" in args:
            root = pathlib.Path(tmp) / "custom_components" / "fixture"
            root.mkdir(parents=True)
            (root / "fix.py").write_text(CLEAN + ("\n" + PLANT if "--plant" in args else ""))
        seams = scan(root)
    if "--json" in args:
        print(json.dumps(seams, indent=1))
    for s in seams:
        print(f"SEAM {s['kind']:7s} {s['file']}:{s['line']} {s['symbol']} {s['member']} :: {s['text']}")
    by = {}
    for s in seams:
        by[s["kind"]] = by.get(s["kind"], 0) + 1
    print("RESULT seams=%d %s" % (len(seams), " ".join(f"{k}={v}" for k, v in sorted(by.items()))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
