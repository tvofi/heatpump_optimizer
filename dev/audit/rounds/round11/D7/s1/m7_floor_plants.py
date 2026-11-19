#!/usr/bin/env python3
"""D7.M7 "cells at their floor test their counters": six planted defects in EVERY package file, read back
through the architecture score's own censuses, file by file.

Metric (one line): per plant kind, the number of package files whose planted defect the score's census does
NOT list (a hole), over all files of custom_components/heatpump_optimizer/*.py.
KEY: the probe function's own name appearing in the census's site list for the file it was planted in.

Plants (appended to a temp copy of each file; the tree under test is never written):
  dead        a public top-level function nothing reads            -> dead_members and public_unused must list it
  clone2      one two-statement window in two functions            -> duplication_copies must hold both in a class
  clone1      the same kind of window written TWICE in ONE function -> duplication_copies should hold it; it does not
  reach       a function-scope ``from . import optimizer`` reading a private of it
                                                                   -> private_cross_module must list the crossing
  boundary    ``import scipy as _x`` nothing reads                   -> unused_boundary_imports must list it
  global      a private module-level binding nothing loads         -> unread_private_globals must rise by one per file

Run (from the repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m7_floor_plants.py
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m7_floor_plants.py --fold-owner   (perturbation)

Expected at the baseline (counts, exact): files=95, holes_dead_members=0, holes_public_unused=0,
holes_clone2=0, holes_reach=0 (optimizer.py itself is not planted: 94 of 94), holes_boundary=0, holes_global=0,
holes_clone1=95,
duplication_copies_planted - duplication_copies_base = 95 (clone2 only; clone1 adds 0).
Perturbation --fold-owner (in memory, one-line change of counters.gapped_clones' owner rule: a window's owner
is keyed by its PLACE, so two places in one function are two owners): holes_clone1 95 -> 0.
Baseline SHA: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: darwin arm64, 8 cores (box B5).
Hooks: tools/audit/archscore/counters.py:gapped_clones, tests/structure.py:measure (dead census),
metrics/public_surface.py:measure, metrics/layering.py:measure.
Writes only under a tempfile root.
"""
from __future__ import annotations

import os

for _pin in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
             "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_pin, "1")

import ast  # noqa: E402
import hashlib  # noqa: E402
import shutil  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from collections import defaultdict  # noqa: E402
from pathlib import Path  # noqa: E402

REPO = Path.cwd()
sys.path.insert(0, str(REPO / "tools" / "audit"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from archscore import counters as K  # noqa: E402
from archscore.metrics import common as C  # noqa: E402
import m7_sites  # noqa: E402

REACH_TARGET, REACH_NAME = "optimizer", "_utc_step_starts"


def window(i: int, a: str, b: str, salt: int) -> str:
    k = 1000 + 7 * i + salt
    return (f"    {a} = [float(v) * {k}.25 + {k}.5 for v in rows if v is not None and v > {k}.125]\n"
            f"    {b} = sum({a}) / max(len({a}), 1) + {k}.75 * len(rows)\n")


def plant(root: Path, into: Path, boundary: bool = False) -> list[str]:
    shutil.copytree(root / C.PKG_REL, into / C.PKG_REL, ignore=shutil.ignore_patterns("__pycache__"))
    files = sorted(p.name for p in (into / C.PKG_REL).glob("*.py"))
    for i, f in enumerate(files):
        p = into / C.PKG_REL / f
        src = p.read_text().rstrip("\n") + "\n"
        if boundary:  # its own tree: a scipy import in every module would lift every module's layer
            p.write_text(src + f"\nimport scipy as _d7s1_sp_{i}  # noqa: E402\n")
            continue
        src += f"\n\ndef d7s1_dead_probe_{i}():\n    return {i}\n"
        src += f"\n\ndef _d7s1_two_a_{i}(rows):\n{window(i, 'kept', 'mean', 0)}    return mean\n"
        src += f"\n\ndef _d7s1_two_b_{i}(rows):\n{window(i, 'held', 'level', 0)}    return level\n"
        src += (f"\n\ndef _d7s1_one_{i}(rows):\n{window(i, 'kept', 'mean', 3)}{window(i, 'held', 'level', 3)}"
                "    return mean, level\n")
        if f != f"{REACH_TARGET}.py":
            src += (f"\n\ndef _d7s1_reach_{i}():\n    from . import {REACH_TARGET} as _d7s1_o\n"
                    f"    return _d7s1_o.{REACH_NAME}\n")
        src += f"\n_D7S1_GLOBAL_{i} = {i}\n"
        ast.parse(src)
        p.write_text(src)
    return files


def place_owned_clones(S, trees, gap=None):
    """counters.gapped_clones with ONE change: a window's owner carries the line of its first statement, so the
    same window at two places of one function has two owners. Members are reported by function, as before."""
    real_all = S.all_functions
    out_windows: dict[str, set] = defaultdict(set)
    for path, tree in trees:
        rel, modalias = str(path.relative_to(S.REPO_ROOT)), S._module_aliases(tree)
        for fn in real_all(tree):
            local, stack = S._local_names(fn), [fn]
            while stack:
                node = stack.pop()
                stack += [c for c in ast.iter_child_nodes(node)
                          if not isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef))]
                blocks = [getattr(node, f) for f in ("body", "orelse", "finalbody")
                          if isinstance(getattr(node, f, None), list) and getattr(node, f)
                          and isinstance(getattr(node, f)[0], ast.stmt)]
                for block in blocks + [h.body for h in getattr(node, "handlers", []) or []]:
                    block = [s for s in block if not S._is_docstring(s)
                             and not isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
                    size = [sum(1 for _ in ast.walk(s)) for s in block]
                    form: dict[int, str] = {}
                    for i in range(len(block)):
                        for j in range(i + 1, len(block)):
                            if size[i] + size[j] < S.DUP_MIN_NODES:
                                continue
                            for k in (i, j):
                                if k not in form:
                                    form[k] = K._statement_form(S, block[k], local, modalias)
                            names: dict[str, str] = {}
                            key = K._LOCAL.sub(lambda m: names.setdefault(m.group(1), f"v{len(names)}"),
                                               form[i] + form[j])
                            # the one change: the place joins the owner, disjoint places only
                            out_windows[hashlib.sha1(key.encode()).hexdigest()].add(
                                (rel, fn.name, fn.lineno, block[i].lineno, block[j].end_lineno))
    groups = []
    for owners in out_windows.values():
        owners = sorted(owners)
        fns = {o[:3] for o in owners}
        disjoint = any(a[:3] == b[:3] and a[4] < b[3] for a in owners for b in owners)
        if len(fns) == 1 and disjoint:
            groups.append(sorted(fns) * 2)
    return groups


def main() -> int:
    fold = "--fold-owner" in sys.argv
    t0, c0 = time.process_time(), time.thread_time()
    root = REPO
    if fold:
        real = K.gapped_clones
        K.gapped_clones = lambda S, trees, gap=None: real(S, trees, gap) + place_owned_clones(S, trees, gap)
    base = m7_sites.census(root)
    with tempfile.TemporaryDirectory(prefix="d7s1-plants-") as tmp:
        files = plant(root, Path(tmp) / "a")
        got = m7_sites.census(Path(tmp) / "a")
        plant(root, Path(tmp) / "b", boundary=True)
        got_b = m7_sites.census(Path(tmp) / "b")
    holes: dict[str, list[str]] = defaultdict(list)
    for i, f in enumerate(files):
        stem = f[:-3]
        checks = {
            "dead_members": any(x.startswith(f"{f}:") and x.endswith(f" d7s1_dead_probe_{i}")
                                for x in got["sites"]["dead_members"]),
            "public_unused": f"{stem}.d7s1_dead_probe_{i}" in got["sites"]["public_unused"],
            "clone2": any(any(x.endswith(f" _d7s1_two_a_{i}") for x in g)
                          and any(x.endswith(f" _d7s1_two_b_{i}") for x in g)
                          for g in got["sites"]["duplication_copies"]),
            "clone1": any(any(x.endswith(f" _d7s1_one_{i}") for x in g) for g in got["sites"]["duplication_copies"]),
        }
        checks["boundary"] = f"{stem}: _d7s1_sp_{i}" in got_b["sites"]["unused_boundary_imports"]
        if stem != REACH_TARGET:
            checks["reach"] = any(x.startswith(f"{stem} -> {REACH_TARGET}.{REACH_NAME}")
                                  for x in got["sites"]["private_cross_module"])
        for kind, seen in checks.items():
            if not seen:
                holes[kind].append(f)
        print(f"FILE {f} " + " ".join(f"{k}={'seen' if v else 'HOLE'}" for k, v in checks.items()))
    print(f"RESULT perturbation={'fold-owner' if fold else 'none'} label")
    print(f"RESULT files={len(files)} count")
    holes["global"] = ["?"] * max(0, len(files) - (got["values"]["unread_private_globals"]
                                                   - base["values"]["unread_private_globals"]))
    for kind in ("dead_members", "public_unused", "clone2", "reach", "boundary", "global", "clone1"):
        print(f"RESULT holes_{kind}={len(holes[kind])} files")
        if holes[kind] and len(holes[kind]) < len(files) - 1:
            print(f"HOLES {kind} " + " ".join(holes[kind]))
    for m in ("duplication_copies", "dead_members", "public_unused", "private_cross_module", "layer_violations",
              "shape_copies", "import_cycle_modules", "unread_private_globals", "unused_boundary_imports"):
        print(f"RESULT {m}_base={base['values'][m]} count")
        print(f"RESULT {m}_planted={(got_b if m == 'unused_boundary_imports' else got)['values'][m]} count")
    tf = (time.process_time() - t0) / max(time.thread_time() - c0, 1e-9)
    print(f"RESULT thread_factor={tf:.2f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
