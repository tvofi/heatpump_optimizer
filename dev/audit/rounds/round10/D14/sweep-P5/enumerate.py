"""Class P5 seam enumerator (round 10, D14 steps 3-4).

Seam rule: a gate that freezes, rejects or adopts learning, decided on a
quantity that contains the model bias the gated learner exists to remove
(a replay residual), rather than on the bias-independent condition it names.

Lists, across every .py under the package root given (default the package):
  cusum   - every Cusum(...) detector, and whether its .update() is fed a
            name containing "residual" (a model-replay residual)
  reject  - every abs(<..residual..>) > X comparison
  freeze  - every string reason _learning_frozen returns
  adopt   - every adoption function of the sysid path
An "instance" candidate is a residual-fed Cusum whose .tripped is read inside
_learning_frozen. Usage: python3 enumerate.py [root]
"""
from __future__ import annotations
import ast, sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[6] / "custom_components/heatpump_optimizer"

def _names(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(node) if isinstance(n, ast.Attribute)}

def scan(root: Path):
    seams = []
    for f in sorted(root.rglob("*.py")):
        tree = ast.parse(f.read_text())
        rel = f.relative_to(root).as_posix()
        cusums, fed, gated = {}, set(), set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) and getattr(node.value.func, "id", None) == "Cusum":
                for t in node.targets:
                    if isinstance(t, ast.Attribute):
                        cusums[t.attr] = node.lineno
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "update" and isinstance(node.func.value, ast.Attribute):
                if any("residual" in n for a in node.args for n in _names(a)):
                    fed.add(node.func.value.attr)
            if isinstance(node, ast.Compare) and isinstance(node.left, ast.Call) and getattr(node.left.func, "id", None) == "abs":
                if any("residual" in n for n in _names(node.left)):
                    seams.append(("reject", rel, f"abs(residual)>X@{node.lineno}"))
            if isinstance(node, ast.FunctionDef):
                if node.name == "_learning_frozen":
                    for sub in ast.walk(node):
                        if isinstance(sub, ast.If):
                            for a in ast.walk(sub.test):
                                if isinstance(a, ast.Attribute) and a.attr == "tripped" and isinstance(a.value, ast.Attribute):
                                    gated.add(a.value.attr)
                        if isinstance(sub, ast.Return) and sub.value is not None and not (isinstance(sub.value, ast.Constant) and sub.value.value is None):
                            seams.append(("freeze", rel, f"{node.name}:{ast.unparse(sub.value)}@{sub.lineno}"))
                if node.name in ("_adopt_system_identification", "adoption_decision"):
                    seams.append(("adopt", rel, f"{node.name}@{node.lineno}"))
        for name, line in cusums.items():
            kind = "cusum-INSTANCE" if (name in fed and name in gated) else "cusum"
            seams.append((kind, rel, f"{name}@{line} fed_residual={name in fed} gates_learning={name in gated}"))
    return seams

if __name__ == "__main__":
    s = scan(ROOT)
    for row in s:
        print("\t".join(row))
    print(f"SEAMS {len(s)} INSTANCE_CANDIDATES {sum(r[0]=='cusum-INSTANCE' for r in s)}")
