"""Hub loads and owned attributes of the coordinator seams.

Hub loads are loads of ``_opt_config``, ``_thermal_params`` and
``_current_state`` through a state root, the attribute walk
``tests/structure.py`` ``seam_metrics`` uses. That script does not print the
row. Owned attributes are the ones a seam stores. The second tree is main
immediately before the #1887 merge, archived so the function text of
``seam_metrics`` is the one this tree runs on both.

    python3 tools/audit/harnesses/eg_b7_seam_hubs.py
"""
from __future__ import annotations

import ast
import importlib.util
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

HUBS = ("_opt_config", "_thermal_params", "_current_state")
BASE = "31567b71820fe8e3380be30a19b7342360c3b6b8"


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


REPO = repo_root(__file__)


def measure(root: Path, label: str):
    spec = importlib.util.spec_from_file_location(
        "hpo_structure", root / "tests" / "structure.py")
    s = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s)
    trees = [(p, ast.parse(p.read_text(encoding="utf-8"), filename=str(p)))
             for p in sorted(s.PACKAGE_DIR.rglob("*.py"))]
    pkg = s.Package(trees)
    roles = s.CoordinatorRoles(pkg)
    helpers = roles.coordinator_helpers()
    coord = pkg.classes[(s.COORDINATOR_MODULE, s.COORDINATOR_CLASS_NAME)]
    seams = s.load_seam_map()
    methods = {m.name for m in coord.body
               if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))}
    units = {m.name: (m, s.SELF_ROOT) for m in coord.body
             if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))}
    units.update(helpers)
    loads: Counter = Counter()
    owners: dict[str, set[str]] = {}
    for name, (fn, roots) in units.items():
        bucket = seams[name]
        aliases, hops = s.state_root_bindings(fn, roots)
        for node in ast.walk(fn):
            if not (isinstance(node, ast.Attribute) and id(node) not in hops
                    and s.is_state_root(node.value, aliases, roots)
                    and node.attr not in methods):
                continue
            if isinstance(node.ctx, ast.Store):
                owners.setdefault(node.attr, set()).add(bucket)
            if node.attr in HUBS and isinstance(node.ctx, ast.Load):
                loads[(bucket, node.attr)] += 1
    owned = {lab: sorted(a for a, bs in owners.items() if lab in bs)
             for lab in s.SEAM_LABELS}
    print(f"tree {label}")
    for lab in (*s.SEAM_LABELS, "core"):
        total = sum(loads[(lab, h)] for h in HUBS)
        parts = " ".join(f"{h}={loads[(lab, h)]}" for h in HUBS)
        print(f"hub_loads {lab} {total} {parts}")
    for lab in s.SEAM_LABELS:
        print(f"owned {lab} {len(owned[lab])} {' '.join(owned[lab])}")
    return owned


def main() -> None:
    head_owned = measure(REPO, "HEAD")
    with tempfile.TemporaryDirectory(prefix="hpo-b7-base-") as tmp:
        raw = subprocess.check_output(
            ["git", "-C", str(REPO), "archive", BASE, "custom_components", "tests"])
        subprocess.run(["tar", "-x", "-C", tmp], input=raw, check=True)
        base_owned = measure(Path(tmp), BASE)
    for lab in head_owned:
        print(f"owned_equal {lab} {head_owned[lab] == base_owned[lab]}")


if __name__ == "__main__":
    main()
