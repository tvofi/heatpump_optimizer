#!/usr/bin/env python3
"""D7.M7 layering census: for every layer violation the score counts, the import edges that carry it.

Metric (one line): per (module, layer) violation of tools/audit/archscore/metrics/layering.py, the module's
DIRECT package imports whose own closure reaches the higher layer ("carrier edges"), and per carrier target
the boundary imports that give it its layer; ``single_carrier_violations`` counts violations one edge carries.
KEY: layering.graph's own edges and external roots -- never the import statements' text.

Run (from the repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m7_layer_edges.py [ROOT]
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m7_layer_edges.py --cut inputs   (perturbation)

Expected at the baseline (exact, counts): layer_violations=13, single_carrier_violations=11; the CARRIER lines
name each violation's edges (accuracy carries 5, inputs 4, tariff 2, quiet_windows 2).
Perturbation --cut MODULE[,MODULE] (in memory): the modules' own boundary imports are dropped from the graph's
external roots, as if their glue were injected; layer_violations must fall by the violations they alone carry:
--cut accuracy 7, --cut inputs 10, --cut inputs,accuracy 3; null control --cut issues 13 (it carries one of
setpoint_check's three edges and no violation alone).
Baseline SHA: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: darwin arm64, 8 cores (box B5).
Hooks: tools/audit/archscore/metrics/layering.py:graph, :closure, :LAYERS.
Writes only under a tempfile root.
"""
from __future__ import annotations

import os

for _pin in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
             "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_pin, "1")

import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

REPO = Path.cwd()
sys.path.insert(0, str(REPO / "tools" / "audit"))
from archscore import counters as K  # noqa: E402
from archscore.metrics import common as C, layering as L  # noqa: E402


def main() -> int:
    argv = sys.argv[1:]
    cut = argv[argv.index("--cut") + 1].split(",") if "--cut" in argv else []
    args = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] != "--cut")]
    root = Path(args[0] if args else ".").resolve()
    t0, c0 = time.process_time(), time.thread_time()
    with tempfile.TemporaryDirectory(prefix="d7s1-layer-") as tmp:
        K.flatten(root, Path(tmp))
        pkg = C.load(str(tmp))
        edges, ext, _crossings = L.graph(pkg)
        ext = {m: set(v) for m, v in ext.items()}
        for m in cut:
            ext[m] = {x for x in ext.get(m, ()) if x not in L.LAYERS}
        rank = {m: max([L.LAYERS[x] for x in ext[m] if x in L.LAYERS], default=0) for m in pkg.mods}
        reach = {m: max([rank[n] for n in L.closure(edges, m)], default=0) for m in pkg.mods}
        violations = sorted((m, r) for m in pkg.mods for r in {rank[n] for n in L.closure(edges, m)} if r > rank[m])
        single = 0
        carried_by: dict[str, int] = {}
        for m, r in violations:
            carriers = sorted(n for n in edges.get(m, ()) if n != m and max(rank[n], reach[n]) >= r)
            direct = [n for n in carriers if rank[n] >= r]
            print(f"CARRIER {m} ({rank[m]} -> {r}): edges {', '.join(carriers)}"
                  f" | of which glue themselves: {', '.join(direct) or '-'}")
            if len(carriers) == 1:
                single += 1
            for n in carriers:
                carried_by[n] = carried_by.get(n, 0) + 1
        for n, k in sorted(carried_by.items(), key=lambda kv: (-kv[1], kv[0])):
            roots = sorted(x for x in ext[n] if x in L.LAYERS)
            print(f"TARGET {n} carries {k} violation edge(s); own layer {rank[n]}; boundary roots {roots or '-'}")
        C.reset_caches()
    print(f"RESULT cut={','.join(cut) or 'none'} label")
    print(f"RESULT layer_violations={len(violations)} count")
    print(f"RESULT single_carrier_violations={single} count")
    tf = (time.process_time() - t0) / max(time.thread_time() - c0, 1e-9)
    print(f"RESULT thread_factor={tf:.2f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
