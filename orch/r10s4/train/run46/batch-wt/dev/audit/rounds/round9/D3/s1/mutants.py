#!/usr/bin/env python3
"""D3.M1 candidate list for coordinator.py, weighted by consequence, sampled with a seed.

METRIC: the number of mutation candidates the AST scan yields in
  custom_components/heatpump_optimizer/coordinator.py, per operator, and the
  seeded weighted sample (at most MAX_PER_MODULE = 4, D3.md step 1) drawn from them.
RUN:      PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D3/s1/mutants.py [--list] [--show ID]
EXPECTED: RESULT candidates_total=<n> count (exact for a given tree); RESULT sampled=4 count
BASELINE: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
MACHINE:  box B1 (4 vCPU cloud container, Linux 6.18), CPython 3.14.0rc2
ROOT:     resolved from the working directory (Path(".")), never from __file__.

Operators (weight = operator weight x consequence weight of the enclosing function):
  GUARD_DROP   `if <test>:` whose body is a single early exit (return/raise/continue/break)
               -> `if False:`                              operator weight 3
  CMP_BOUND    `<`<->`<=`, `>`<->`>=` in a comparison      operator weight 2
  MINMAX_SWAP  builtin `min(` <-> `max(` with >= 2 args     operator weight 2
  CONST_SHIFT  a numeric literal compared against -> x2 (0 -> 1)   operator weight 1
Consequence weight of the enclosing function name: 3 if it matches CONSEQUENCE_RE
(payload, publish, stale, guard, fallback, price, comfort, dhw, reason, service,
valid, finite, store, clamp, limit, fresh, age, sensor, setpoint, write),
1 otherwise; 0 (excluded) for a line that mentions _LOGGER or a node inside a
function whose name starts with `_log`/`__repr__`.

The seed is SEED below (round 9, dimension 3, seat 1). Everything here is a
count read from the AST of the production file; the mutant's effect on the suite
is measured by prescreen.py, not here.
"""
from __future__ import annotations

import os

for _threads in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_threads, "1")

import ast
import json
import random
import re
import sys
import time
from pathlib import Path

TARGET = Path("custom_components/heatpump_optimizer/coordinator.py")
SEED = 90301
MAX_PER_MODULE = 4
OP_WEIGHT = {"GUARD_DROP": 3, "CMP_BOUND": 2, "MINMAX_SWAP": 2, "CONST_SHIFT": 1}
CONSEQUENCE_RE = re.compile(
    r"payload|publish|stale|guard|fallback|price|comfort|dhw|reason|service|valid|"
    r"finite|store|clamp|limit|fresh|age|sensor|setpoint|write", re.I)
CMP_SWAP = {ast.Lt: "<=", ast.LtE: "<", ast.Gt: ">=", ast.GtE: ">"}
CMP_TXT = {ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">="}


def _enclosing(tree: ast.AST) -> dict[int, str]:
    """Map every node id to the qualified name of its innermost def."""
    owner: dict[int, str] = {}

    def walk(node: ast.AST, name: str) -> None:
        for child in ast.iter_child_nodes(node):
            n = name
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                n = f"{name}.{child.name}" if name else child.name
            owner[id(child)] = n
            walk(child, n)

    walk(tree, "")
    return owner


def candidates(src: str) -> list[dict]:
    tree = ast.parse(src)
    lines = src.splitlines()
    owner = _enclosing(tree)
    out: list[dict] = []

    def add(node, op, line, old, new, extra=""):
        fn = owner.get(id(node), "")
        leaf = fn.rsplit(".", 1)[-1]
        text = lines[line - 1]
        if "_LOGGER" in text or leaf.startswith("_log") or leaf == "__repr__":
            return
        cw = 3 if CONSEQUENCE_RE.search(leaf) else 1
        out.append({"op": op, "line": line, "func": fn, "old": old, "new": new,
                    "weight": OP_WEIGHT[op] * cw, "consequence_weight": cw, "note": extra})

    for node in ast.walk(tree):
        if isinstance(node, ast.If) and len(node.body) == 1 and isinstance(
                node.body[0], (ast.Return, ast.Raise, ast.Continue, ast.Break)):
            seg = ast.get_source_segment(src, node.test)
            if seg and "\n" not in seg and node.test.lineno == node.lineno:
                add(node, "GUARD_DROP", node.lineno, seg, "False")
        elif isinstance(node, ast.Compare) and node.lineno == node.end_lineno:
            for op, right in zip(node.ops, node.comparators):
                if type(op) in CMP_SWAP:
                    add(node, "CMP_BOUND", node.lineno, CMP_TXT[type(op)], CMP_SWAP[type(op)],
                        ast.get_source_segment(src, node) or "")
                if (isinstance(right, ast.Constant) and isinstance(right.value, (int, float))
                        and not isinstance(right.value, bool)):
                    v = right.value
                    add(node, "CONST_SHIFT", right.lineno, repr(v), repr(1 if v == 0 else v * 2),
                        ast.get_source_segment(src, node) or "")
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
              and node.func.id in ("min", "max") and len(node.args) >= 2):
            add(node, "MINMAX_SWAP", node.lineno, node.func.id + "(",
                ("max" if node.func.id == "min" else "min") + "(",
                ast.get_source_segment(src, node) or "")
    out.sort(key=lambda c: (c["line"], c["op"], c["old"]))
    seen: dict = {}
    for i, c in enumerate(out):
        c["id"] = f"C{i:04d}"
        k = (c["line"], c["op"], c["old"])
        c["occ"] = seen.get(k, 0)  # which textual occurrence on the line (a chained compare has two)
        seen[k] = c["occ"] + 1
    return out


def apply(src: str, cand: dict) -> str:
    """Return src with the candidate applied: the occ-th occurrence of `old` on its line."""
    lines = src.split("\n")
    i = cand["line"] - 1
    text = lines[i]
    if cand["op"] == "GUARD_DROP":
        pos = text.index("if ") + 3
        j = text.index(cand["old"], pos)
        lines[i] = text[:j] + cand["new"] + text[j + len(cand["old"]):]
    elif cand["op"] == "CMP_BOUND":
        pat = re.compile(r"(?<![<>=!])" + re.escape(cand["old"]) + r"(?![<>=])")
        m = list(pat.finditer(text))[cand.get("occ", 0)]
        lines[i] = text[:m.start()] + cand["new"] + text[m.end():]
    else:
        pat = re.compile(r"(?<![\w.])" + re.escape(cand["old"]) + (r"(?![\w.])" if cand["op"] == "CONST_SHIFT" else ""))
        m = list(pat.finditer(text))[cand.get("occ", 0)]
        lines[i] = text[:m.start()] + cand["new"] + text[m.end():]
    out = "\n".join(lines)
    ast.parse(out)
    return out


def sample(cands: list[dict], k: int = MAX_PER_MODULE, seed: int = SEED) -> list[dict]:
    rng = random.Random(seed)
    pool = [c for c in cands if c["weight"] > 0]
    picked: list[dict] = []
    while pool and len(picked) < k:
        tot = sum(c["weight"] for c in pool)
        r = rng.uniform(0, tot)
        acc = 0.0
        for c in pool:
            acc += c["weight"]
            if acc >= r:
                picked.append(c)
                pool.remove(c)
                break
    return picked


def main() -> int:
    t0p, t0t = time.process_time(), time.thread_time()
    src = TARGET.read_text()
    cands = candidates(src)
    if "--show" in sys.argv:
        cid = sys.argv[sys.argv.index("--show") + 1]
        c = next(c for c in cands if c["id"] == cid)
        print(json.dumps(c, indent=1))
        return 0
    if "--list" in sys.argv:
        for c in cands:
            print(json.dumps(c))
    by_op: dict[str, int] = {}
    for c in cands:
        by_op[c["op"]] = by_op.get(c["op"], 0) + 1
    picked = sample(cands)
    for c in picked:
        apply(src, c)  # proves it applies and parses
        print("SAMPLED", json.dumps(c))
    print(f"RESULT candidates_total={len(cands)} count")
    for op, n in sorted(by_op.items()):
        print(f"RESULT candidates_{op}={n} count")
    print(f"RESULT weight_total={sum(c['weight'] for c in cands)} count")
    print(f"RESULT sampled={len(picked)} count")
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={tp / tt if tt > 1e-9 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
