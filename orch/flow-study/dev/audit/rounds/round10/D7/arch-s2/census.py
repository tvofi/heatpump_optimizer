"""Dump the four ARCH-s2 cells' members for one tree (the gapped clone classes, dead members,
unused public names, import cycles), using the score's own definitions.

    python3 dev/audit/rounds/round10/D7/arch-s2/census.py [ROOT]      default: the working tree
"""
import ast
import json
import sys
import tempfile
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


REPO = repo_root(__file__)
sys.path.insert(0, str(REPO / "tools" / "audit"))
from archscore import counters as K  # noqa: E402
from archscore import vector  # noqa: E402
from archscore.metrics import public_surface  # noqa: E402

root = Path(sys.argv[1] if len(sys.argv) > 1 else REPO).resolve()
with tempfile.TemporaryDirectory() as tmp:
    flat = Path(tmp)
    K.flatten(root, flat, inline=True)
    S = vector.load_structure(flat)
    trees = [(p, ast.parse(p.read_text())) for p in sorted(S.PACKAGE_DIR.glob("*.py"))]
    groups = K.gapped_clones(S, trees)
    print("CLONE_CLASSES", len(groups), "copies", sum(len(g) - 1 for g in groups))
    for g in sorted(groups, key=len, reverse=True):
        print(f"  [{len(g)}] " + " | ".join(f"{r.split('/')[-1]}:{f}:{ln}" for r, f, ln in g))
    S.seam_metrics = vector._stub_seams
    m = S.measure()
    for k in ("dead_methods", "dead_top_level_symbols", "import_cycle_modules"):
        print(k, m["metrics"].get(k), json.dumps(m.get("details", {}).get(k, ""))[:600])
    ps = public_surface.measure(flat)
    print("public_unused", ps["details"]["unused"],
          json.dumps({k: v for k, v in ps["details"].items() if k != "unused"})[:1500])
