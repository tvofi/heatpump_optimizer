#!/usr/bin/env python3
"""D7 verify-v2 for D7-s1-01: the reverse direction of the finder's harness.

Metric (one line): over every plain coordinator method (not a property, not a
dunder, not referenced as a bare ``self.m`` value, no ``super()``), the change
in sum(cut_*) + cross_seam_edges that production tests/structure.py:seam_metrics
reports when that method is moved out of the class as a module-level
``_m(coord, ...)`` helper -- simulated on the AST: the method is dropped from
the ClassDef and from the seam map, and every ``self.m(...)`` call becomes
``_m(self, ...)`` (a Name call, which seam_metrics does not count).

Prints RESULT eligible=<n>, rewarded=<methods whose extraction lowers the sum>,
priced=<methods whose extraction raises it>, total_drop=<sum of drops>,
max_drop=<largest single drop> (+name), and a null control
(methods with no state-root reference (production is_state_root) and no incoming self.m() call: delta must be 0).
Counts; contention-immune.

Run (repository root):
    PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D7/verify-v2/extract_reward.py
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, cloud container linux.
Writes nothing.
"""
from __future__ import annotations
import os
for _p in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_p, "1")
import ast, copy, sys, time  # noqa: E402
from pathlib import Path  # noqa: E402
sys.path.insert(0, str(Path.cwd() / "tests"))
import structure  # noqa: E402


def score(m: dict) -> int:
    return sum(m["cut_costs"].values()) + m["cross_edges"]


def main() -> int:
    c0, t0 = time.process_time(), time.thread_time()
    src = (structure.PACKAGE_DIR / "coordinator.py").read_text()
    tree = ast.parse(src)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
               and n.name == structure.COORDINATOR_CLASS_NAME)
    seams = structure.load_seam_map()
    # synthetic null cell: a pure method nobody calls; its extraction must move nothing
    cls.body.append(ast.parse("def _v2_null(self, x):\n    return x + 1\n").body[0])
    seams = {**seams, "_v2_null": "core"}
    base = structure.seam_metrics(cls, seams)
    s0 = score(base)
    methods = [m for m in cls.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
    names = {m.name for m in methods}
    # bare value refs self.m (not called)
    called, bare = set(), set()
    for n in ast.walk(cls):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and isinstance(n.func.value, ast.Name) and n.func.value.id == "self":
            called.add(id(n.func))
    for n in ast.walk(cls):
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) \
                and n.value.id == "self" and n.attr in names and id(n) not in called:
            bare.add(n.attr)
    rows = []
    for m in methods:
        if m.name.startswith("__") or structure.is_property_getter(m) or m.name in bare \
                or any(isinstance(d, ast.Attribute) for d in m.decorator_list) \
                or any(isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id == "super"
                       for x in ast.walk(m)):
            continue
        c = copy.deepcopy(cls)
        c.body = [b for b in c.body if not (isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef))
                                             and b.name == m.name)]
        for n in ast.walk(c):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                    and isinstance(n.func.value, ast.Name) and n.func.value.id == "self" \
                    and n.func.attr == m.name:
                n.args = [ast.Name("self", ast.Load())] + n.args
                n.func = ast.Name("_" + m.name, ast.Load())
        sm = {k: v for k, v in seams.items() if k != m.name}
        d = score(structure.seam_metrics(c, sm)) - s0
        al, _h = structure.state_root_bindings(m)
        own_refs = sum(1 for x in ast.walk(m) if isinstance(x, ast.Attribute)
                       and structure.is_state_root(x.value, al))
        incoming = sum(1 for x in ast.walk(cls) if isinstance(x, ast.Call)
                       and isinstance(x.func, ast.Attribute) and isinstance(x.func.value, ast.Name)
                       and x.func.value.id == "self" and x.func.attr == m.name)
        rows.append((d, m.name, own_refs + incoming))
    rows.sort()
    for d, n, r in rows[:12]:
        print(f"  extract {n:40s} delta={d:+d} self_refs={r}")
    rewarded = [r for r in rows if r[0] < 0]
    priced = [r for r in rows if r[0] > 0]
    null = [r for r in rows if r[2] == 0]
    print(f"RESULT baseline_score={s0} count")
    print(f"RESULT eligible={len(rows)} count")
    print(f"RESULT rewarded={len(rewarded)} count")
    print(f"RESULT priced={len(priced)} count")
    print(f"RESULT total_drop={-sum(r[0] for r in rewarded)} count")
    print(f"RESULT max_drop={-rows[0][0]} count ({rows[0][1]})")
    print(f"RESULT null_control_cells={len(null)} nonzero={sum(1 for r in null if r[0])} count")
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={(c1-c0)/max(t1-t0,1e-9):.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
