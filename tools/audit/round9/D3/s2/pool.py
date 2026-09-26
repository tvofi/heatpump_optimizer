#!/usr/bin/env python3
"""D3-s2 round 9, step D3.M1: the seeded, weighted mutant pool for eight solver-side modules.

Metric: the pool itself -- N single-line mutants drawn from the candidate inventory of
  custom_components/heatpump_optimizer/{optimizer,thermal_model,sysid,defrost,flow_lift,
  price_model,tariff,grid_fee}.py, at most PER_MODULE per module, weighted by consequence.
Command:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D3/s2/pool.py
          (tranche 2: D3S2_POOL=pool2.json D3S2_SEED=90303 D3S2_PER_MODULE=1, same command)
Expected: RESULT pool_size=32 mutants (exact; deterministic under SEED), pool.json byte-identical on re-run.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B2 (4-CPU Linux container).
Instrumented symbol: tests/mutation_table.py:candidates (the gate's own six operators) plus two
  operators added here (NP_CLIP: np.clip(x, lo, hi) -> x; EXCEPT_RAISE: first line of a one-line
  except handler -> raise). Perturbation: SEED or PER_MODULE changes the draw (pool.json moves).
Key: a mutant is keyed on (file, line, kind); weights are recorded in pool.json.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import ast
import json
import random
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as mt  # noqa: E402

HERE = Path(__file__).resolve().parent
SEED = int(os.environ.get("D3S2_SEED", "90302"))
PER_MODULE = int(os.environ.get("D3S2_PER_MODULE", "4"))
PKG = "custom_components/heatpump_optimizer/"
# Tranche 2 (D3S2_POOL=pool2.json D3S2_SEED=90303 D3S2_PER_MODULE=1): draws only sites no
# earlier pool file holds, ids prefixed T.
POOL_OUT = os.environ.get("D3S2_POOL", "pool.json")
# Consequence weights (recorded, M1): money/comfort-bearing modules and clamps weigh most.
MODULE_W = {"optimizer": 3.0, "thermal_model": 3.0, "tariff": 3.0, "grid_fee": 2.5,
            "price_model": 2.5, "sysid": 2.0, "defrost": 2.0, "flow_lift": 2.0}
KIND_W = {"CLAMP_DROP": 3.0, "NP_CLIP": 3.0, "GUARD_OFF": 2.0, "BOOLOP": 2.0,
          "CONST": 2.0, "EXCEPT_RAISE": 2.0, "RAISE_DEL": 2.0, "RETURN_DEL": 1.5}


def _log_only(body) -> bool:
    for st in body:
        if not (isinstance(st, ast.Expr) and isinstance(st.value, ast.Call)
                and isinstance(st.value.func, ast.Attribute)
                and isinstance(st.value.func.value, ast.Name)
                and st.value.func.value.id in ("_LOGGER", "LOGGER", "logger", "log")):
            return False
    return True


def extra(path: Path, rel: str):
    src = path.read_text()
    lines = src.splitlines()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "clip" and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "np" and len(node.args) == 3
                and node.lineno == getattr(node, "end_lineno", -1)):
            line = lines[node.lineno - 1]
            seg = ast.get_source_segment(src, node)
            a0 = ast.get_source_segment(src, node.args[0])
            if seg and a0 and line.count(seg) == 1:
                yield dict(kind="NP_CLIP", file=rel, line=node.lineno, old=line,
                           new=line.replace(seg, f"np.asarray({a0})"))
        if isinstance(node, ast.ExceptHandler) and node.body:
            st = node.body[0]
            if st.lineno == getattr(st, "end_lineno", -1) and not isinstance(st, ast.Raise):
                line = lines[st.lineno - 1]
                yield dict(kind="EXCEPT_RAISE", file=rel, line=st.lineno, old=line,
                           new=mt._indent(line) + "raise")


def inventory():
    out = []
    for mod in MODULE_W:
        rel = f"{PKG}{mod}.py"
        path = ROOT / rel
        src = path.read_text()
        tree = ast.parse(src)
        ifs = {n.lineno: n for n in ast.walk(tree) if isinstance(n, ast.If)}
        seen = set()
        for m in list(mt.candidates(path)) + list(extra(path, rel)):
            m["file"] = rel
            key = (m["file"], m["line"], m["kind"])
            if key in seen or m["new"] == m["old"]:
                continue
            seen.add(key)
            stripped = m["old"].strip()
            if m["kind"] == "GUARD_OFF":
                node = ifs.get(m["line"])
                if node is None or _log_only(node.body) or "TYPE_CHECKING" in stripped:
                    continue
            lines = src.splitlines()
            lines[m["line"] - 1] = m["new"]
            try:
                ast.parse("\n".join(lines))
            except SyntaxError:
                continue
            m["module"] = mod
            m["weight"] = MODULE_W[mod] * KIND_W[m["kind"]]
            out.append(m)
    return out


def sample(inv):
    rng = random.Random(SEED)
    if POOL_OUT != "pool.json":
        prior = {(m["file"], m["line"], m["kind"])
                 for m in json.loads((HERE / "pool.json").read_text())["pool"]}
        inv = [m for m in inv if (m["file"], m["line"], m["kind"]) not in prior]
    pool = []
    for mod in MODULE_W:
        cands = [m for m in inv if m["module"] == mod]
        for _ in range(min(PER_MODULE, len(cands))):
            tot = sum(c["weight"] for c in cands)
            r = rng.uniform(0, tot)
            acc = 0.0
            for i, c in enumerate(cands):
                acc += c["weight"]
                if acc >= r:
                    pool.append(cands.pop(i))
                    break
    for i, m in enumerate(pool, 1):
        m["id"] = f"{'M' if POOL_OUT == 'pool.json' else 'T'}{i:02d}"
    return pool


def main() -> int:
    inv = inventory()
    pool = sample(inv)
    by_mod = {}
    for m in inv:
        by_mod.setdefault(m["module"], 0)
        by_mod[m["module"]] += 1
    doc = {"seed": SEED, "per_module": PER_MODULE, "module_weights": MODULE_W,
           "kind_weights": KIND_W, "inventory_per_module": by_mod,
           "inventory_size": len(inv), "pool": pool}
    (HERE / POOL_OUT).write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    for m in pool:
        print(f"{m['id']} {m['kind']:12s} {m['file'].split('/')[-1]}:{m['line']}  {m['old'].strip()[:90]}")
    print(f"RESULT inventory_size={len(inv)} sites")
    print(f"RESULT pool_size={len(pool)} mutants")
    return 0


if __name__ == "__main__":
    sys.exit(main())
