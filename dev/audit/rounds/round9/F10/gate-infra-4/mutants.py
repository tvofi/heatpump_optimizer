"""Break structure.py's new rules one at a time; run its self-check; print what goes red.

usage: mutants.py <tree-root>   (the head checkout)
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

WT = Path(sys.argv[1])
SRC = (WT / "tests" / "structure.py").read_text()

MUTANTS = [
    (
        "properties out of the member census",
        "            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):\n                key = (mod, cname, item.name)",
        "            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and not any(\n"
        "                    isinstance(d, ast.Name) and d.id == 'property' for d in item.decorator_list):\n"
        "                key = (mod, cname, item.name)",
    ),
    (
        "a bare name load keeps a member alive",
        "            name = None\n            if isinstance(child, ast.Attribute) and isinstance(child.ctx, ast.Load):",
        "            name = None\n            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):\n"
        "                name = child.id\n            elif isinstance(child, ast.Attribute) and isinstance(child.ctx, ast.Load):",
    ),
    (
        "another class's field does not make a name ambiguous",
        "        return len(by_name[key[2]]) == 1 and not fields[key[2]] - {(key[0], key[1])}",
        "        return len(by_name[key[2]]) == 1",
    ),
    (
        "liveness by name, not reachability",
        "            if src is not None and src not in live:\n                continue",
        "            pass",
    ),
    (
        "helpers not charged",
        "            if mod == COORDINATOR_MODULE and cls is None and self.params.get(fid):",
        "            if False:",
    ),
    (
        "role by parameter name only (no propagation)",
        "        self._propagate()\n",
        "        pass\n",
    ),
    (
        "in-place mutation is a read",
        "                    and n.func.attr in MUTATOR_METHODS:\n                mutated.add(id(n.func.value))",
        "                    and n.func.attr in MUTATOR_METHODS:\n                pass",
    ),
    (
        "writers outside the class dropped",
        "        roots = roles.roots(fid)\n        if not roots:\n            continue\n        where",
        "        roots = roles.roots(fid)\n        if not roots or cls != COORDINATOR_CLASS_NAME:\n            continue\n        where",
    ),
    (
        "duplication per module only",
        "normalized_window(stmts, local, modalias).encode()",
        "(rel + normalized_window(stmts, local, modalias)).encode()",
    ),
(
        "locals not renamed",
        "            if n.id in local:\n                n.id = mapping",
        "            if False:\n                n.id = mapping",
    ),
    (
        "TYPE_CHECKING imports are edges",
        "        skip = type_checking_ids(tree)\n        package",
        "        skip = set()\n        package",
    ),
    (
        "function-scope imports dropped",
        "            if id(n) in skip or not isinstance(n, ast.ImportFrom) or n.level == 0:",
        "            if id(n) in skip or not isinstance(n, ast.ImportFrom) or n.level == 0 \\\n"
        "                    or n not in tree.body:",
    ),
    (
        "star import binds nothing",
        '                if alias.name == "*":\n                    if src in mods:',
        '                if alias.name == "*":\n                    if False:',
    ),
]


def run(src: str) -> tuple[int, list[str]]:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        shutil.copytree(WT / "custom_components", tmp / "custom_components")
        (tmp / "tests").mkdir()
        shutil.copy(WT / "tests" / "seam_map.json", tmp / "tests" / "seam_map.json")
        shutil.copy(
            WT / "tests" / "structure_budgets.json",
            tmp / "tests" / "structure_budgets.json",
        )
        (tmp / "tests" / "structure.py").write_text(src)
        out = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; sys.path.insert(0, 'tests'); import structure as s; sys.exit(s.self_check())",
            ],
            cwd=tmp,
            capture_output=True,
            text=True,
        )
        return out.returncode, [
            l for l in out.stdout.splitlines() if l.startswith("FAIL")
        ]


rc, fails = run(SRC)
print(f"unmutated: rc={rc} {fails}")
for label, old, new in MUTANTS:
    if SRC.count(old) != 1:
        print(f"== {label}: ANCHOR {SRC.count(old)}")
        continue
    rc, fails = run(SRC.replace(old, new))
    print(f"== {label}: rc={rc}")
    for f in fails:
        print("   " + f)
