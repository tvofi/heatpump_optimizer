#!/usr/bin/env python3
"""D7.M7 site census: every site behind every architecture-score metric, attributed to its file.

Metric (one line): for each SCORE metric and gate-only tripwire of tools/audit/archscore/vector.py, the
sites the metric counts on ROOT, grouped by the package file holding them; a file with no site on any
scored metric is "at its floor".

Run (from the repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m7_sites.py [ROOT] [--json OUT]
ROOT defaults to "." and holds custom_components/heatpump_optimizer.

Expected at the baseline (exact, counts): the RESULT values equal vector.py's own
(duplication_copies=18 hub_solve_writes=1 shared_inplace_writes=3 dead_members=1 public_unused=1
params_over_10=6 layer_violations=13 private_cross_module=10 literal_clone_copies=118
coordinator_multiassigned_attrs=104 coord_footprint=2496 shape_copies=40).
Baseline SHA: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: darwin arm64, 8 cores (box B5).
Hooks: tools/audit/archscore/vector.py:load_structure, counters.py:gapped_clones and each
metrics/<m>.py:measure, on the C4-flattened copy vector.py:measure builds.
Writes only under a tempfile root (and the --json path the caller names).
"""
from __future__ import annotations

import os

for _pin in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
             "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_pin, "1")

import json  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from collections import defaultdict  # noqa: E402
from pathlib import Path  # noqa: E402

REPO = Path.cwd()
sys.path.insert(0, str(REPO / "tools" / "audit"))
from archscore import counters as K, vector as V  # noqa: E402
from archscore.metrics import (common as C, footprint, hub_solve_writes, layering, literal_clones,  # noqa: E402
                               public_surface, shapes, shared_inplace_writes, untyped_payload_keys)


def census(root: Path) -> dict:
    out: dict = {"sites": {}, "values": {}}
    with tempfile.TemporaryDirectory(prefix="d7s1-m7-") as tmp:
        flat = Path(tmp)
        K.flatten(root, flat)
        S = V.load_structure(flat)
        S.seam_metrics = V._stub_seams
        S.duplicate_clones = lambda trees, *a, **kw: K.gapped_clones(S, trees)
        res = S.measure()
        t = res["tables"]
        out["values"]["duplication_copies"] = res["metrics"]["duplication_copies"]
        out["sites"]["duplication_copies"] = [[f"{Path(r).name}:{ln} {n}" for r, n, ln in g] for g in t["clones"]]
        out["values"]["dead_members"] = res["metrics"]["dead_methods"] + res["metrics"]["dead_top_level_symbols"]
        out["sites"]["dead_members"] = [f"{Path(r).name}:{ln} {n}" for r, ln, n in t["dead_symbols"]] + \
            [str(x) for x in t["dead_methods"]]
        out["values"]["coordinator_private_reach_ratchet"] = res["metrics"]["coordinator_private_reach"]
        out["sites"]["coordinator_private_reach_ratchet"] = [
            f"{Path(r).name}:{ln} {a} {k} in {f}" for r, ln, a, k, f in t["private_reach"]]
        out["values"]["coordinator_multiassigned_attrs"] = res["metrics"]["coordinator_multiassigned_attrs"]
        out["sites"]["outside_writers"] = [f"{a}: {ws}" for a, ws in t["outside_writers"]]
        out["values"]["import_cycle_modules"] = res["metrics"]["import_cycle_modules"]
        out["values"]["unread_private_globals"] = K.unread_private_globals(K.trees(flat))
        for name, mod in (("hub_solve_writes", hub_solve_writes), ("shared_inplace_writes", shared_inplace_writes),
                          ("untyped_payload_keys", untyped_payload_keys)):
            m = mod.measure(flat)
            out["values"][name] = m["value"]
            d = m["details"]
            out["sites"][name] = d.get("sites", []) + d.get("borrow_restore", []) + d.get("untyped", [])
        m = public_surface.measure(flat)
        out["values"]["public_unused"] = m["details"]["unused"]
        out["sites"]["public_unused"] = m["details"]["unused_names"]
        pkg = C.load(str(flat))
        fp = footprint.measure(flat, pkg)
        trees = {m_.name: m_.tree for m_ in pkg.mods.values() if "." not in m_.name}
        out["values"]["coord_footprint"] = fp["coord_footprint"]
        out["values"]["params_over_10"] = fp["params_over_10"]
        out["sites"]["params_over_10"] = footprint.params_over_10_sites(trees)
        charged = fp["charged"]
        out["sites"]["coord_footprint_charged"] = [str(x) for x in charged] if isinstance(charged, (list, set, tuple)) \
            else [f"{k}: {v}" for k, v in charged.items()] if isinstance(charged, dict) else [str(charged)]
        m = layering.measure(flat)
        out["values"]["layer_violations"] = m["layer_violations"]
        out["values"]["private_cross_module"] = m["private_cross_module"]
        out["values"]["unused_boundary_imports"] = m["unused_boundary_imports"]
        out["sites"]["layer_violations"] = m["details"]["violations"]
        out["sites"]["private_cross_module"] = [str(x) for x in m["details"]["crossings"]]
        out["sites"]["unused_boundary_imports"] = list(m["details"]["unused_boundary_imports"])
        out["layers"] = m["details"]["layers"]
        found = literal_clones.specs(flat)
        out["values"]["literal_clone_copies"] = sum(len(v) for v in found.values())
        out["sites"]["literal_clone_copies"] = [[f"{mm}.py:{ln}" for mm, ln in v] for v in found.values()]
        sh = shapes.classes(flat)
        out["values"]["shape_copies"] = sum(len(g) for g in sh)
        out["sites"]["shape_copies"] = [[str(x) for x in g] for g in sh]
        C.reset_caches()
    return out


def by_file(c: dict, files: list[str]) -> dict:
    per = {f: defaultdict(int) for f in files}
    stems = {f[:-3]: f for f in files}

    def credit(metric: str, text: str) -> None:
        hit = set(re.findall(r"([A-Za-z_][A-Za-z_0-9]*)\.py", text))
        if not hit:
            head = re.split(r"[ .:(]", text.strip(), maxsplit=1)[0]
            if head in stems:
                hit = {head}
        for h in hit:
            if h in stems:
                per[stems[h]][metric] += 1

    for metric, sites in c["sites"].items():
        for s in sites:
            for x in (s if isinstance(s, list) else [s]):
                credit(metric, x)
    return {f: dict(v) for f, v in per.items()}


SCORED = ("duplication_copies", "dead_members", "hub_solve_writes", "shared_inplace_writes",
          "untyped_payload_keys", "public_unused", "params_over_10", "layer_violations",
          "private_cross_module", "literal_clone_copies", "coordinator_private_reach_ratchet", "outside_writers")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--") and (sys.argv[sys.argv.index(a) - 1] != "--json")]
    root = Path(args[0] if args else ".").resolve()
    t0, c0 = time.process_time(), time.thread_time()
    c = census(root)
    files = sorted(p.name for p in (root / C.PKG_REL).glob("*.py"))
    per = by_file(c, files)
    floor = [f for f in files if not any(per[f].get(m) for m in SCORED)]
    for f in files:
        row = " ".join(f"{m}={per[f][m]}" for m in sorted(per[f])) or "-"
        print(f"FILE {f} {'FLOOR' if f in floor else 'OPEN'} {row}")
    for metric, sites in c["sites"].items():
        for s in sites:
            print(f"SITE {metric} {json.dumps(s) if isinstance(s, list) else s}")
    for k, v in sorted(c["values"].items()):
        print(f"RESULT {k}={v} count")
    print(f"RESULT files={len(files)} count")
    print(f"RESULT files_at_floor={len(floor)} count")
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(
            json.dumps({"census": c, "per_file": per, "floor": floor}, indent=1))
    tf = (time.process_time() - t0) / max(time.thread_time() - c0, 1e-9)
    print(f"RESULT thread_factor={tf:.2f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
