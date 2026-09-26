#!/usr/bin/env python3
"""D7 verify-v2 for D7-s3-02: an independent attribute-reference screen of class members.

Metric (one line): class-body functions (methods AND @property getters, dunders
and structure.py's HA convention names excluded) under
custom_components/heatpump_optimizer whose name is never an ast.Attribute
attr and never a getattr/hasattr/setattr string literal anywhere in the
package -- set beside tests/structure.py:measure()['metrics']['dead_methods'].
Then partitions the members my screen lists: how many structure.py skips as
@property, and how many a same-named bare Name load / import alias in the
package keeps alive in structure.py's name set.

Null arm: the same screen with an injected synthetic class member no one
reads must list exactly one more member (+1), and injecting one Attribute
read of it must bring it back (0). Counts; contention-immune.

Run (repository root):
    PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D7/verify-v2/member_screen.py
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, cloud container linux. Writes nothing.
"""
from __future__ import annotations
import os
for _p in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_p, "1")
import ast, contextlib, io, sys, time  # noqa: E402
from pathlib import Path  # noqa: E402
sys.path.insert(0, "tests")
import structure as S  # noqa: E402

PKG = Path("custom_components/heatpump_optimizer")


def is_prop(fn):
    return any((isinstance(d, ast.Name) and d.id in ("property", "cached_property"))
               or (isinstance(d, ast.Attribute) and d.attr in ("setter", "getter", "deleter", "cached_property"))
               for d in fn.decorator_list)


def screen(extra_src: str = ""):
    trees = [(p, ast.parse(p.read_text())) for p in sorted(PKG.rglob("*.py"))]
    if extra_src:
        trees.append((PKG / "_v2_synthetic.py", ast.parse(extra_src)))
    attr_refs, names = set(), set()
    for _p, t in trees:
        for n in ast.walk(t):
            if isinstance(n, ast.Attribute):
                attr_refs.add(n.attr)
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                    and n.func.id in ("getattr", "hasattr", "setattr") and len(n.args) >= 2 \
                    and isinstance(n.args[1], ast.Constant) and isinstance(n.args[1].value, str):
                attr_refs.add(n.args[1].value)
            elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                names.add(n.id)
            elif isinstance(n, (ast.Import, ast.ImportFrom)):
                for a in n.names:
                    names.add(a.name.split(".")[-1])
                    if a.asname:
                        names.add(a.asname)
    dead = []
    for p, t in trees:
        for cls in [n for n in ast.walk(t) if isinstance(n, ast.ClassDef)]:
            for fn in cls.body:
                if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                nm = fn.name
                if nm.startswith("__") and nm.endswith("__"):
                    continue
                if nm in S.HA_CONVENTION_NAMES or S.is_ha_convention_method(nm):
                    continue
                if any(isinstance(d, ast.Attribute) and d.attr in ("setter", "deleter") for d in fn.decorator_list):
                    continue
                if nm in attr_refs:
                    continue
                dead.append((str(p), cls.name, nm, is_prop(fn), nm in names))
    return dead


def main() -> int:
    c0, t0 = time.process_time(), time.thread_time()
    dead = screen()
    for d in dead:
        print(f"  DEAD {d[0]}:{d[1]}.{d[2]} property={d[3]} bare_name_alias={d[4]}")
    with contextlib.redirect_stdout(io.StringIO()):
        dm = S.measure()["metrics"]["dead_methods"]
    print(f"RESULT structure_dead_methods={dm} count")
    print(f"RESULT my_dead_members={len(dead)} count")
    print(f"RESULT my_dead_properties={sum(1 for d in dead if d[3])} count")
    print(f"RESULT my_dead_plain_methods={sum(1 for d in dead if not d[3])} count")
    print(f"RESULT hidden_by_property_rule_only={sum(1 for d in dead if d[3] and not d[4])} count")
    print(f"RESULT hidden_by_bare_name_only={sum(1 for d in dead if not d[3] and d[4])} count")
    print(f"RESULT hidden_by_both={sum(1 for d in dead if d[3] and d[4])} count")
    syn = "class _V2Syn:\n    def v2_never_read_member(self):\n        return 1\n"
    n1 = len(screen(syn))
    n2 = len(screen(syn + "_V2Syn().v2_never_read_member()\n"))
    print(f"RESULT null_injected_dead_delta={n1 - len(dead)} count (expect 1)")
    print(f"RESULT null_injected_read_delta={n2 - len(dead)} count (expect 0)")
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={(c1-c0)/max(t1-t0,1e-9):.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
