"""One tree to its score vector.

    python3 tools/audit/archscore/vector.py ROOT        JSON on stdout

ROOT holds ``custom_components/heatpump_optimizer``. The vector is SCORE_METRICS plus the
gate-only tripwires, each a deterministic static count.

Where a metric already exists in ``tests/structure.py`` this file reads THAT definition, on a
freshly loaded copy of the module re-pointed at the tree being measured (a planted or a
historic tree is not the working tree), so there is one clone window, one reach census, one
dead-member census and one import graph:

    duplication_copies             structure.duplicate_clones, copies not pairs
    coordinator_private_reach      structure.private_reach_sites, writes weighted
    coordinator_multiassigned_attrs  structure.coordinator_writers
    import_cycle_modules           structure.import_cycle_modules
    dead_members                   structure's dead_methods + dead_top_level_symbols

Three things are done to that copy and never to ``tests/structure.py`` itself, because each is a
red-team counter and the ratchet must not move with it (``counters.py``): statements dead by data
flow are dropped before a clone window is cut (C3), a passthrough property reads as its private (C5),
and the seam cut is stubbed -- it needs a seam-map entry for every coordinator method, which a
planted or a historic tree does not carry, and no score metric uses it.

The metrics structure.py has no row for (the hub and shared-object write censuses, the payload
contract, the entity families, the unused public surface and the coordinator footprint) come from
``metrics/``, which has its own role engine: a coordinator-rooted PATH engine, where structure's
``CoordinatorRoles`` answers only "is this value the coordinator".
"""
from __future__ import annotations

import ast
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))

from archscore import counters as K  # noqa: E402
from archscore.metrics import (  # noqa: E402
    common as C,
    family_splits,
    footprint,
    hub_solve_writes,
    public_surface,
    shared_inplace_writes,
    untyped_payload_keys,
)

_IS_ANY = untyped_payload_keys.is_any

# metric -> (register class it guards or None, the property it prices)
SCORE_METRICS = {
    "hub_solve_writes": ("N-shared-config", "writes into the live config hubs reachable from the solve"),
    "shared_inplace_writes": ("N-shared-config", "in-place writes of operation values into long-lived shared objects"),
    "duplication_copies": ("P2+P3", "copies of a function sharing an AST-identical statement window, package-wide"),
    "untyped_payload_keys": ("P6", "coordinator payload keys published with no declared type"),
    "dead_members": ("N-structure-blind", "members and top-level symbols no production root reaches"),
    "family_splits": ("N-name-sort", "entity families the name sort splits"),
    "coord_footprint": (None, "logic statements in the coordinator plus every function handed it"),
    "coordinator_multiassigned_attrs": (None, "coordinator attributes stored by more than one function, in or out of it"),
    "coordinator_private_reach": (None, "reads of coordinator privates from outside it, writes weighted"),
    "import_cycle_modules": (None, "modules in an import cycle, function-scope imports included"),
    "public_unused": (None, "public names nothing uses"),
    "params_over_10": (None, "functions with more than 10 parameters (the fragment-chain guard)"),
}
# Weight 0: must not rise, never counted. They retire when the role engine reads these spellings.
GATE_ONLY = ("reflective_writes", "computed_attr_access", "family_orphan_overrides", "unread_private_globals")


def ablated() -> set[str]:
    """``ARCHSCORE_ABLATE=C1,C3`` switches counters off. It exists to prove a counter load-bearing: the
    game it closes must then read IMPROVES (or the counter is decoration), and nothing else uses it."""
    return {c for c in os.environ.get("ARCHSCORE_ABLATE", "").split(",") if c}


def load_structure(root: Path):
    """``tests/structure.py`` as a fresh module object measuring ``root``."""
    spec = importlib.util.spec_from_file_location("archscore_structure", REPO / "tests" / "structure.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.REPO_ROOT = root
    mod.PACKAGE_DIR = root / "custom_components" / "heatpump_optimizer"
    return mod


def _stub_seams(coord_class, seams=None, helpers=None):
    return {"seam_cut_total": 0, "seam_rows": [], "internal_call_edges": 0, "cross_edges": 0,
            "cross_seam_fraction": 0.0}


def structure_rows(root: Path) -> dict:
    off = ablated()
    S = load_structure(root)
    S.seam_metrics = _stub_seams
    plain, clones = S._is_docstring, S.duplicate_clones

    def clones_without_dead(trees, *a, **kw):
        dead = K.inert_statements(trees, S.all_functions)
        S._is_docstring = lambda s: plain(s) or id(s) in dead
        try:
            return clones(trees, *a, **kw)
        finally:
            S._is_docstring = plain

    if "C3" not in off:
        S.duplicate_clones = clones_without_dead
    sites = S.private_reach_sites

    def reach_with_passthrough(roles):
        found = list(sites(roles))
        coord = roles.pkg.classes.get((S.COORDINATOR_MODULE, S.COORDINATOR_CLASS_NAME))
        through = K.passthrough_properties(coord) if coord is not None else {}
        for fid, (mod, _cls, fn) in roles.pkg.units.items():
            if not through or roles.is_charged(fid):
                continue
            roots = roles.roots(fid)
            rel = roles.pkg.mods[mod][0]
            for n in ast.walk(fn):
                if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Load) and n.attr in through \
                        and roles.is_coord(n.value, roots, fid):
                    found.append((rel, n.lineno, through[n.attr], "read", fn.name))
                elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("getattr", "hasattr") \
                        and len(n.args) >= 2 and isinstance(n.args[1], ast.Constant) \
                        and n.args[1].value in through and roles.is_coord(n.args[0], roots, fid):
                    found.append((rel, n.lineno, through[n.args[1].value], "read", fn.name))
        return sorted(found)

    if "C5" not in off:
        S.private_reach_sites = reach_with_passthrough
    m = S.measure()["metrics"]
    return {"duplication_copies": m["duplication_copies"],
            "coordinator_multiassigned_attrs": m["coordinator_multiassigned_attrs"],
            "coordinator_private_reach": m["coordinator_private_reach"],
            "import_cycle_modules": m["import_cycle_modules"],
            "dead_members": m["dead_methods"] + m["dead_top_level_symbols"]}


def measure(root: Path) -> dict:
    """The score vector of ``root``. A metric that raises is recorded as None with its error."""
    root = Path(root).resolve()
    out: dict = {}
    with tempfile.TemporaryDirectory(prefix="archscore-") as tmp:
        flat = Path(tmp)
        off = ablated()
        out["_inlined_bases"] = K.flatten(root, flat, inline="C4" not in off)
        untyped_payload_keys.is_any = (lambda ann: False) if "C1" in off else _IS_ANY
        footprint.READ_KW_KEYS = "C11" not in off
        jobs = {
            "structure": lambda: structure_rows(flat),
            "hub_solve_writes": lambda: hub_solve_writes.measure(flat)["value"],
            "shared_inplace_writes": lambda: shared_inplace_writes.measure(flat)["value"],
            "untyped_payload_keys": lambda: untyped_payload_keys.measure(flat)["value"],
            "family_splits": lambda: family_splits.measure(flat)["value"],
            "public_unused": lambda: public_surface.measure(flat)["details"]["unused"],
            "footprint": lambda: footprint.measure(flat),
        }
        ts = K.trees(flat)
        tripwires = {
            "reflective_writes": lambda: K.reflective_writes(ts),
            "computed_attr_access": lambda: K.computed_attr_access(ts),
            "family_orphan_overrides": lambda: K.family_orphan_overrides(flat),
            "unread_private_globals": lambda: K.unread_private_globals(ts),
        }
        for name, fn in {**jobs, **tripwires}.items():
            if (name in ("reflective_writes", "computed_attr_access") and "C2" in off) \
                    or (name == "family_orphan_overrides" and "C6" in off) \
                    or (name == "unread_private_globals" and "C7" in off):
                out[name] = None
                continue
            try:
                v = fn()
            except Exception as err:  # recorded, never hidden
                out[f"_{name}_error"] = f"{type(err).__name__}: {err}"[:300]
                v = None
            if name == "structure":
                out.update(v or {k: None for k in ("duplication_copies", "coordinator_multiassigned_attrs",
                                                   "coordinator_private_reach", "import_cycle_modules",
                                                   "dead_members")})
            elif name == "footprint":
                out["coord_footprint"] = v["coord_footprint"] if v else None
                out["params_over_10"] = v["params_over_10"] if v else None
            else:
                out[name] = v
    C.reset_caches()
    return out


if __name__ == "__main__":
    print(json.dumps(measure(Path(sys.argv[1])), sort_keys=True))
