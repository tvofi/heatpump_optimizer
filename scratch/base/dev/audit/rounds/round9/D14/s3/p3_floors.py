#!/usr/bin/env python3
"""P3 detector (D14.M3): a capacity floor or divisor applied inconsistently across sibling formulas.

Metric (one line): number of quantities (canonical leaf name) that the package reads both
through a positive-constant floor ``max(Q, c)`` / ``max(c, Q)`` and raw as an arithmetic
operand (divisor or factor), or through two different floor constants -- each such quantity
is one P3 seam group; RESULT p3_seam_groups counts them, p3_raw_divisor_groups counts the
subset where at least one raw read is a *divisor* (the R7 D2-01 shape).

Count key: the canonical quantity a read resolves to -- an attribute's leaf name
(``p.buffer_tank_thermal_mass`` -> ``buffer_tank_thermal_mass``), a local name resolved
through its single plain assignment in the same function (``C_buf = p.buffer_tank_thermal_mass``
-> ``buffer_tank_thermal_mass``), otherwise the local name itself scoped to its function.
An honest fix changes what the production *source* reads, so the key cannot be satisfied
by relabelling.

Command (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D14/s3/p3_floors.py
    [--ref <git-rev>]        # enumerate the package at another commit (pre-fix re-find)
    [--reintroduce]          # perturbation: in-memory re-introduction of `/ max(C_buf, 0.01)`
    [--fixture]              # clean fixture: a synthetic module with one floor per quantity, no raw read
    [--json]                 # dump every seam
Expected: baseline p3_seam_groups printed by the run (exact; static), reintroduce -> +1 group
containing buffer_tank_thermal_mass; fixture -> 0; --ref ab71960d^ -> the buffer/wood/dhw
groups present.
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box B8 (4 cores, 15 GB).
Instrumented symbols: the source of custom_components/heatpump_optimizer/*.py as imported
(module.__file__ of the imported package, not a path literal), in particular
thermal_model:ThermalModel._simulate_step_two_zone for the perturbation.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast
import json
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

PKG = "custom_components/heatpump_optimizer"


def _const_value(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        v = _const_value(node.operand)
        return -v if v is not None else None
    if isinstance(node, ast.Name) and node.id.isupper():
        return node.id  # a module constant used as a floor
    return None


def _leaf(node):
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return None


class FuncScan:
    """Collect floored and raw reads inside one function body (nested defs included)."""

    def __init__(self, module, qual, func):
        self.module, self.qual, self.func = module, qual, func
        # A local name is an alias of an attribute when every non-constant value it is
        # assigned is that same attribute (``C_buf = p.buffer_tank_thermal_mass`` then
        # ``if C_buf < 1e-6: C_buf = 0.04`` still reads the buffer's capacity).
        vals = defaultdict(set)
        for n in ast.walk(func):
            if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                v = n.value
                if _const_value(v) is not None and not isinstance(_const_value(v), str):
                    continue
                vals[n.targets[0].id].add(v.attr if isinstance(v, ast.Attribute) else None)
        self.alias = {k: next(iter(v)) for k, v in vals.items() if len(v) == 1 and None not in v}
        self.floored = []   # (key, floor, lineno)
        self.raw = []       # (key, role, lineno)
        self._inside_floor = set()

    def key(self, node):
        if isinstance(node, ast.Attribute):
            return node.attr
        if isinstance(node, ast.Name):
            if node.id in self.alias:
                return self.alias[node.id]
            return f"{self.module}:{self.qual}:{node.id}"
        return None



def scan_source(module, src):
    tree = ast.parse(src)
    out = []

    def walk(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qual = f"{prefix}{child.name}"
                fs = FuncScan(module, qual, child)
                calls = [n for n in ast.walk(child) if isinstance(n, ast.Call)]
                # single pass in two phases
                for n in calls:
                    _floor_only(fs, n)
                for n in ast.walk(child):
                    if isinstance(n, ast.BinOp):
                        _raw_only(fs, n)
                out.append(fs)
                walk(child, qual + ".")
            elif isinstance(child, ast.ClassDef):
                walk(child, f"{prefix}{child.name}.")
    walk(tree, "")
    return out


def _floor_only(fs, node):
    if isinstance(node.func, ast.Name) and node.func.id == "max" and len(node.args) == 2 and not node.keywords:
        a, b = node.args
        for q, c in ((a, b), (b, a)):
            cv = _const_value(c)
            if cv is not None and (isinstance(cv, str) or cv > 0) and isinstance(q, (ast.Name, ast.Attribute)):
                k = fs.key(q)
                if k and not isinstance(_const_value(q), (float, str)):
                    fs.floored.append((k, cv, node.lineno))
                    fs._inside_floor.add(id(q))


def _raw_only(fs, node):
    if isinstance(node.op, (ast.Div, ast.Mult, ast.FloorDiv)):
        div = isinstance(node.op, (ast.Div, ast.FloorDiv))
        for side, role in ((node.left, "factor"), (node.right, "divisor" if div else "factor")):
            if isinstance(side, (ast.Name, ast.Attribute)) and id(side) not in fs._inside_floor:
                if isinstance(side, ast.Name) and side.id.isupper():
                    continue
                k = fs.key(side)
                if k:
                    fs.raw.append((k, role, node.lineno))


def enumerate_seams(sources):
    floored = defaultdict(list)
    raw = defaultdict(list)
    for module, src in sources.items():
        for fs in scan_source(module, src):
            for k, c, ln in fs.floored:
                floored[k].append((c, f"{module}:{ln}", fs.qual))
            for k, role, ln in fs.raw:
                raw[k].append((role, f"{module}:{ln}", fs.qual))
    seams = {}
    for k, fl in floored.items():
        consts = sorted({str(c) for c, _, _ in fl})
        # a function-local key (module:qual:name) only sees its own function
        rr = raw.get(k, [])
        if len(consts) > 1 or rr:
            seams[k] = {
                "floors": consts,
                "floored_at": [f"{loc} {q} max(.,{c})" for c, loc, q in fl],
                "raw_at": [f"{loc} {q} {role}" for role, loc, q in rr],
                "raw_divisor": any(role == "divisor" for role, _, _ in rr),
            }
    return seams


def load_sources(ref=None):
    if ref:
        names = subprocess.run(["git", "ls-tree", "--name-only", ref, PKG + "/"],
                               capture_output=True, text=True, check=True).stdout.split()
        return {Path(n).stem: subprocess.run(["git", "show", f"{ref}:{n}"], capture_output=True,
                                             text=True, check=True).stdout
                for n in names if n.endswith(".py")}
    import importlib
    sys.path.insert(0, "custom_components")
    pkg = importlib.import_module("heatpump_optimizer")
    root = Path(pkg.__file__).parent
    return {p.stem: p.read_text() for p in sorted(root.glob("*.py"))}


FIXTURE = '''
class M:
    def step(self, p, q):
        c = max(p.cap_a, 0.01)
        d = max(p.cap_b, 0.5)
        return q / c + q / d + q / max(p.cap_a, 0.01)
'''

REINTRO_OLD = "                - q_buf_loss + wood_draw\n            ) / C_buf\n"
REINTRO_NEW = "                - q_buf_loss + wood_draw\n            ) / max(C_buf, 0.01)\n"


def main():
    t0 = time.process_time(); tt0 = time.thread_time()
    args = sys.argv[1:]
    ref = args[args.index("--ref") + 1] if "--ref" in args else None
    if "--fixture" in args:
        sources = {"fixture": FIXTURE}
    else:
        sources = load_sources(ref)
    if "--reintroduce" in args:
        s = sources["thermal_model"]
        assert s.count(REINTRO_OLD) == 1, "re-introduction anchor not found"
        sources["thermal_model"] = s.replace(REINTRO_OLD, REINTRO_NEW)
    seams = enumerate_seams(sources)
    if "--json" in args:
        print(json.dumps(seams, indent=1, sort_keys=True))
    for k in sorted(seams):
        s = seams[k]
        print(f"SEAM {k} floors={s['floors']} n_floored={len(s['floored_at'])} n_raw={len(s['raw_at'])} raw_divisor={s['raw_divisor']}")
    cap_keys = [k for k in seams if any(t in k.lower() for t in ("thermal_mass", "capacity", "c_buf", "c_w", "c_dhw", "volume"))]
    print(f"RESULT p3_seam_groups={len(seams)} count")
    print(f"RESULT p3_raw_divisor_groups={sum(1 for s in seams.values() if s['raw_divisor'])} count")
    print(f"RESULT p3_capacity_groups={len(cap_keys)} count")
    print(f"RESULT buffer_tank_thermal_mass_seam={int('buffer_tank_thermal_mass' in seams)} count")
    pc = time.process_time() - t0; tc = time.thread_time() - tt0
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
    except Exception:
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
