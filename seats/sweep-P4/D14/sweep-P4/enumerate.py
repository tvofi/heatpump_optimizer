"""Round 11 class sweep P4: every optimizer start set and stop in the package.

Class P4: "the optimizer seed set or stop tolerance does not bracket the
optimum". Seam rule (from D0-s3-02's `grep starts = \\[|starts.append|extra_starts`
and D0-s2-01's `wood_seeds.py --census`, widened):

  S (static)  every call in the package to a numerical optimizer or its
              wrappers (_multi_start_minimize, _lbfgsb_run, _lbfgsb_restart,
              _scoped_minimize, scipy minimize, linprog), by AST, with its
              enclosing function. Listed for disposition.
  Z (runtime) a production _multi_start_minimize call site whose start set
              holds no lower-bound (all-off) vector on some cell: the set
              cannot bracket an optimum at the bound (D0-s3-02).
  C (runtime) a call site where two or more starts coincide after clipping
              to the bounds on some cell: the multi-start collapses to fewer
              basins than it pays for (D0-s2-01's wood share zeroing 4 of 5).

Runtime arms record every call through d0s3_lib's Capture idiom (D0-s3's own
builder), keyed on the production caller (function and line), over CELLS.

Usage (from the worktree root):
  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep-P4/enumerate.py [--null | --perturb] [--json PATH]
  --null     the same calls, each start set replaced by a bracketing one
             (the lower bound added, coincident starts dropped): Z=0 C=0
  --perturb  one-line re-introduction in memory: optimizer._LOW_ENERGY_START_FRACTION
             = 1.0 (the R1-D0-01 low-energy anchor collapses onto the
             full-energy price-ranked start): C rises at every site that
             carries both
"""
from __future__ import annotations

import ast
import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
PKG = ROOT / "custom_components" / "heatpump_optimizer"
sys.path.insert(0, str(ROOT / "dev/audit/rounds/round11/D0/s3"))
sys.path.insert(0, str(ROOT / "dev/audit/rounds/round11/D0/s2"))

CELLS = [
    "summer_negative/summer_warm/single-zone/no-dhw/valve-storage/24h",  # D0-s3-02, space-only
    "summer_negative/summer_warm/single-zone/dhw/valve-storage/24h",     # D0-s3-02, _solve_space
    "winter_typical/shoulder/two-zone/no-dhw/wood/24h",                  # D0-s2-01, space-only
    "winter_typical/shoulder/two-zone/dhw/wood/24h",                     # wood beside hot water
    "winter_typical/winter_mild/single-zone/no-dhw/plain/24h",
    "winter_typical/winter_mild/single-zone/dhw/plain/24h",
    # D0-s2's own wood plant (wood_furnace_enabled, 1000 L, charged tank): its cells.cell_record
    "s2:winter_typical/shoulder/two-zone/no-dhw/wood/24h",                # D0-s2-01 race cell
    "s2:winter_narrow/summer_cool/two-zone/no-dhw/wood/24h",              # D0-s2-01 race cell
    "s2:winter_typical/shoulder/two-zone/dhw/wood/24h",                   # the same tank beside hot water
    "s2:winter_narrow/summer_cool/two-zone/dhw/wood/24h",
    # a learned stop and a start price: _relaxed_plans' free-room re-run runs
    "stops:summer_negative/summer_warm/single-zone/dhw/valve-storage/24h",
    "stops:winter_typical/winter_mild/single-zone/dhw/plain/24h",
]
OPT_CALLS = {"_multi_start_minimize", "_lbfgsb_run", "_lbfgsb_restart", "_scoped_minimize",
             "minimize", "linprog", "milp", "minimize_scalar", "differential_evolution"}


def static_sites() -> list[dict]:
    out = []
    for p in sorted(PKG.rglob("*.py")):
        tree = ast.parse(p.read_text(encoding="utf-8"))

        def walk(node, stack):
            for ch in ast.iter_child_nodes(node):
                if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    walk(ch, stack + [ch.name])
                    continue
                if isinstance(ch, ast.Call):
                    f = ch.func
                    name = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
                    if name in OPT_CALLS:
                        out.append({"file": p.relative_to(PKG).as_posix(), "line": ch.lineno,
                                    "symbol": ".".join(stack) or "<module>", "call": name})
                walk(ch, stack)
        walk(tree, [])
    return out


def classify(cands, bounds):
    import numpy as np
    lo = np.array([b[0] for b in bounds], dtype=float)
    hi = np.array([np.inf if b[1] is None else b[1] for b in bounds], dtype=float)
    xs = [np.clip(np.asarray(c, dtype=float), lo, hi) for c in cands]
    has_lo = any(np.allclose(x, lo, atol=1e-9) for x in xs)
    dup = 0
    for i, x in enumerate(xs):
        if any(np.allclose(x, xs[j], atol=1e-6) for j in range(i)):
            dup += 1
    return {"n": len(xs), "has_lo": has_lo, "dup": dup}


def bracket(cands, bounds):
    import numpy as np
    lo = np.array([b[0] for b in bounds], dtype=float)
    hi = np.array([np.inf if b[1] is None else b[1] for b in bounds], dtype=float)
    keep = []
    for c in [lo] + [np.clip(np.asarray(c, dtype=float), lo, hi) for c in cands]:
        if not any(np.allclose(c, k, atol=1e-6) for k in keep):
            keep.append(c)
    return keep


def runtime(mode: str) -> dict:
    import d0s3_lib as L
    om = L.om
    rows = defaultdict(lambda: {"calls": 0, "Z_cells": [], "C_cells": [], "max_dup": 0, "n": set()})
    if mode == "perturb":
        om._LOW_ENERGY_START_FRACTION = 1.0
    orig_ms = L.ORIG_MS
    for cell in CELLS:
        seen = []

        def ms(objective, candidates, bounds, args=(), maxiter=300, batch_objective=None, move_starts=None):
            fr = sys._getframe(1)
            key = f"optimizer.py:{fr.f_code.co_name}:{fr.f_lineno}"
            cands = bracket(candidates, bounds) if mode == "null" else list(candidates)
            seen.append((key, classify(cands, bounds)))
            kw = {} if move_starts is None else {"move_starts": move_starts}
            return orig_ms(objective, cands, bounds, args, maxiter=maxiter,
                           batch_objective=batch_objective, **kw)

        t = time.process_time()
        with L.mock.patch.object(om, "_multi_start_minimize", ms):
            if cell.startswith("s2:"):
                import cells as S2
                rec, _ = S2.cell_record(cell[3:])
                rec.optimizer().optimize(inputs=rec.inputs)
            elif cell.startswith("stops:"):
                b = L.build(cell[6:])
                b["optimizer"].config.duty_switch_stop_probability = (0.5, 0.5)
                b["optimizer"].config.cycling_cost = max(b["optimizer"].config.cycling_cost, 0.5)
                b["optimizer"].optimize(inputs=L.inputs_of(b))
            else:
                b = L.build(cell)
                b["optimizer"].optimize(inputs=L.inputs_of(b))
        for key, c in seen:
            r = rows[key]
            r["calls"] += 1
            r["n"].add(c["n"])
            if not c["has_lo"] and cell not in r["Z_cells"]:
                r["Z_cells"].append(cell)
            if c["dup"] and cell not in r["C_cells"]:
                r["C_cells"].append(cell)
            r["max_dup"] = max(r["max_dup"], c["dup"])
        print(f"cell {cell}: {len(seen)} multi-start call(s), cpu {time.process_time() - t:.1f}s", flush=True)
    return {k: {**v, "n": sorted(v["n"])} for k, v in rows.items()}


def main(argv: list[str]) -> int:
    mode = "null" if "--null" in argv else "perturb" if "--perturb" in argv else "tree"
    st = static_sites()
    rt = runtime(mode)
    for s in st:
        print(f"S   {s['file']}:{s['line']} {s['symbol']} -> {s['call']}")
    for k, v in sorted(rt.items()):
        arms = ("Z" if v["Z_cells"] else "") + ("C" if v["C_cells"] else "")
        print(f"{arms or '-':3} {k} calls={v['calls']} starts={v['n']} Z_cells={len(v['Z_cells'])} "
              f"C_cells={len(v['C_cells'])} max_dup={v['max_dup']}")
        for c in v["C_cells"]:
            print(f"      C {c}")
    z = sum(bool(v["Z_cells"]) for v in rt.values())
    c = sum(bool(v["C_cells"]) for v in rt.values())
    cc = sum(len(v["C_cells"]) for v in rt.values())
    print(f"RESULT {mode} S={len(st)} sites_runtime={len(rt)} Z={z} C={c} C_cells={cc}")
    if "--json" in argv:
        Path(argv[argv.index("--json") + 1]).write_text(
            json.dumps({"static": st, "runtime": rt, "mode": mode}, indent=1) + "\n", encoding="utf-8")
    if mode == "null":
        return 0 if z == 0 and c == 0 else 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
