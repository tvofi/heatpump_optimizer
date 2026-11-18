"""Round 11 class sweep P3: the modulation floor stated in two units.

Seam rule (from D16-s2-04's seam_rule, widened to the package): the modulation
floor exists twice -- as a power (``min_electrical_power``, the band bottom the
plan books) and as a set-point lift over the inlet (``FLOW_MIN_LIFT_K``, the
``flow_min_lift_k`` option, ``start_flow_min_lift_k``, ``modulation_floor_flow_c``).
Every function in the package that reads either is a seam. Arms:

  M  a function that reads both units (directly, or the power through a
     same-module helper that reads ``min_electrical_power``) and names no plant
     gain (``*per_kw*``, ``*_gain``): it books one floor and writes the other
     with nothing tying them, so the two agree only where lift == p_min * plant
     K/kW. Flagged.
  L  a read of the lift that is not the one owner ``start_flow_min_lift_k``
     (raw ``FLOW_MIN_LIFT_K``, ``configured_flow_min_lift_k``, the option key),
     outside the owner chain in thermal_model.  Flagged.
  P  every other reader of either unit, listed for disposition, not flagged.

Usage: PYTHONPATH=tests/hastub python3 enumerate.py [--null | --perturb] [--json PATH]
  --null     run over fixture_clean/ (expected M=0 L=0)
  --perturb  one-line re-introduction on a temp copy of the package:
             pump_arbiter._nudged's ``or 0.0`` floor fallback becomes
             ``or FLOW_MIN_LIFT_K`` (expected delta M=+1 L=+1)
"""
from __future__ import annotations

import ast
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
PKG = ROOT / "custom_components" / "heatpump_optimizer"

POWER_ATTR = "min_electrical_power"
LIFT_NAMES = {"FLOW_MIN_LIFT_K", "CONF_FLOW_MIN_LIFT_K", "DEFAULT_FLOW_MIN_LIFT_K"}
LIFT_CALLS_RAW = {"configured_flow_min_lift_k"}
LIFT_CALLS_OWNED = {"start_flow_min_lift_k", "modulation_floor_flow_c"}
# the owner chain: where the lift is defined, defaulted and combined
OWNERS = {
    ("thermal_model.py", "configured_flow_min_lift_k"),
    ("thermal_model.py", "start_flow_min_lift_k"),
    ("thermal_model.py", "modulation_floor_flow_c"),
}
GAIN_RE = re.compile(r"per_kw|_gain\b|k_per_kw")


def _name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


class _Fn:
    def __init__(self, file: str, qual: str, node: ast.AST) -> None:
        self.file, self.qual, self.node = file, qual, node
        self.power = False
        self.lift_raw: list[str] = []
        self.lift_owned = False
        self.calls: set[str] = set()
        self.gain = False


def _scan(path: Path, rel: str) -> list[_Fn]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: list[_Fn] = []

    def visit(node: ast.AST, stack: list[str], fn: _Fn | None) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                f = _Fn(rel, ".".join(stack + [child.name]), child)
                out.append(f)
                # default arguments belong to the def itself
                for d in child.args.defaults + child.args.kw_defaults:
                    if d is not None:
                        _note(d, f)
                for b in child.body:
                    _note_tree(b, f, stack + [child.name])
                continue
            if isinstance(child, ast.ClassDef):
                visit(child, stack + [child.name], fn)
                continue
            visit(child, stack, fn)

    def _note_tree(node: ast.AST, f: _Fn, stack: list[str]) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            visit(ast.Module(body=[node], type_ignores=[]), stack, None)
            return
        _note(node, f, shallow=True)
        for c in ast.iter_child_nodes(node):
            _note_tree(c, f, stack)

    def _note(node: ast.AST, f: _Fn, shallow: bool = False) -> None:
        nodes = [node] if shallow else list(ast.walk(node))
        for n in nodes:
            if isinstance(n, ast.Attribute) and n.attr == POWER_ATTR:
                f.power = True
            if isinstance(n, ast.Constant) and n.value == POWER_ATTR:
                f.power = True
            nm = _name(n) if isinstance(n, (ast.Name, ast.Attribute)) else None
            if nm in LIFT_NAMES:
                f.lift_raw.append(nm)
            if nm and GAIN_RE.search(nm):
                f.gain = True
            if isinstance(n, ast.Call):
                cn = _name(n.func)
                if cn:
                    f.calls.add(cn)
                if cn in LIFT_CALLS_RAW:
                    f.lift_raw.append(cn + "()")
                if cn in LIFT_CALLS_OWNED:
                    f.lift_owned = True

    visit(tree, [], None)
    return out


def enumerate_seams(pkg: Path) -> dict:
    fns: list[_Fn] = []
    for p in sorted(pkg.rglob("*.py")):
        fns += _scan(p, p.relative_to(pkg).as_posix())
    direct = {(f.file, f.qual.split(".")[-1]) for f in fns if f.power}
    rows = []
    for f in fns:
        short = f.qual.split(".")[-1]
        via = sorted(c for c in f.calls if (f.file, c) in direct and c != short)
        power = f.power or bool(via)
        lift = f.lift_owned or bool(f.lift_raw)
        if not (power or lift):
            continue
        owner = (f.file, short) in OWNERS
        arms = []
        if power and lift and not f.gain and not owner:
            arms.append("M")
        if f.lift_raw and not owner:
            arms.append("L")
        rows.append({
            "file": f.file, "symbol": f.qual, "line": f.node.lineno,
            "power": "direct" if f.power else ("via " + ",".join(via) if via else ""),
            "lift": ("owned " if f.lift_owned else "") + " ".join(sorted(set(f.lift_raw))),
            "owner": owner, "arms": arms or ["P"],
        })
    count = {a: sum(a in r["arms"] for r in rows) for a in ("M", "L", "P")}
    return {"seams": rows, "count": count, "seams_total": len(rows)}


def _print(tag: str, res: dict) -> None:
    for r in res["seams"]:
        print(f"{'/'.join(r['arms']):3} {r['file']}:{r['line']} {r['symbol']}"
              f"  power={r['power'] or '-'} lift={r['lift'].strip() or '-'}{' OWNER' if r['owner'] else ''}")
    c = res["count"]
    print(f"RESULT {tag} M={c['M']} L={c['L']} P={c['P']} seams_total={res['seams_total']}")


def main(argv: list[str]) -> int:
    out = None
    if "--json" in argv:
        out = Path(argv[argv.index("--json") + 1])
    if "--null" in argv:
        res = enumerate_seams(HERE / "fixture_clean")
        _print("null", res)
        ok = res["count"]["M"] == 0 and res["count"]["L"] == 0
    elif "--perturb" in argv:
        base = enumerate_seams(PKG)
        with tempfile.TemporaryDirectory() as tmp:
            cp = Path(tmp) / "pkg"
            shutil.copytree(PKG, cp)
            pa = cp / "pump_arbiter.py"
            src = pa.read_text(encoding="utf-8")
            old = "floor = finite_float(_band_kw(inp)[0]) or 0.0"
            assert src.count(old) == 1, "perturbation anchor moved"
            pa.write_text(src.replace(old, "floor = finite_float(_band_kw(inp)[0]) or FLOW_MIN_LIFT_K"), encoding="utf-8")
            res = enumerate_seams(cp)
        _print("perturb", res)
        dm = res["count"]["M"] - base["count"]["M"]
        dl = res["count"]["L"] - base["count"]["L"]
        print(f"perturb_delta M={dm:+d} L={dl:+d} (expected +1 +1)")
        ok = dm == 1 and dl == 1
    else:
        res = enumerate_seams(PKG)
        _print("tree", res)
        hit = any(r["symbol"] == "_flow_target" and "M" in r["arms"] and r["file"] == "pump_arbiter.py"
                  for r in res["seams"])
        print(f"positive_control D16-s2-04 pump_arbiter._flow_target in M: {hit}")
        ok = hit
    if out:
        out.write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
