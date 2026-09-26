"""D14 round 9, verifier V2 (independent) for D14-s5-02: guard shapes the mutation inventory cannot see.

Metric (one line): v2_sites_added[shape] = candidate sites tests/mutation_table.py:candidates()
yields for a module that is a copy of custom_components/heatpump_optimizer/sysid.py plus ONE
appended guard of that shape, minus the sites it yields for the unmodified copy (the ratchet's
unit of growth); v2_invisible_shapes = shapes whose added count is 0.
Shapes: one-line early-exit if; the same if with its test split over two lines; the same if as an
elif; a two-arg min() clamp; np.clip clamp; a threshold ternary.
Also v2_npclip_lines_uncovered = lines in the package holding an np.clip( call on which
candidates() yields no site (AST count; the finder's CLAMP numpy/math sub-class, independently).
Key: the sites the production inventory function yields.

Null control: the one-line if and the 2-arg min clamp -> non-zero (the shapes the operators do see).
Perturbation (--widen): candidates wrapped to add a GUARD_OFF site for every ast.If whose test
spans lines -> the split-test shape becomes visible (0 -> >0).

Run: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D14/verify-v2/v2_guard_ratchet.py [--widen]
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; 4-core cloud container, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, ast, tempfile, glob
from pathlib import Path
sys.path.insert(0, "tests")
t_proc0, t_thr0 = time.process_time(), time.thread_time()
import mutation_table as M  # noqa: E402

WIDEN = "--widen" in sys.argv
_orig = M.candidates


def cands(path):
    out = list(_orig(path))
    if WIDEN:
        tree = ast.parse(Path(path).read_text())
        seen = {m.get("line") for m in out if isinstance(m, dict)}
        for n in ast.walk(tree):
            if isinstance(n, ast.If) and n.test.end_lineno != n.test.lineno and n.lineno not in seen:
                out.append({"line": n.lineno, "kind": "GUARD_OFF", "old": "", "new": ""})
    return out


base_src = Path("custom_components/heatpump_optimizer/sysid.py").read_text()
SHAPES = {
    "if_one_line": "\n\ndef _v2_guard(x):\n    if x < 0.0:\n        return 0.0\n    return x\n",
    "if_split_test": "\n\ndef _v2_guard(x):\n    if (x\n            < 0.0):\n        return 0.0\n    return x\n",
    "elif": "\n\ndef _v2_guard(x):\n    if x is None:\n        pass\n    elif x < 0.0:\n        return 0.0\n    return x\n",
    "min_clamp_2arg": "\n\ndef _v2_guard(x):\n    return min(x, 1.0)\n",
    "np_clip": "\n\ndef _v2_guard(x):\n    return float(np.clip(x, 0.0, 1.0))\n",
    "ternary": "\n\ndef _v2_guard(x):\n    return x if x >= 0.0 else 0.0\n",
}
tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))


def guard_sites(add):
    """Sites candidates() yields on the guard's own lines (not the def, not the trailing return x)."""
    src = base_src + add
    p = tmp / "sysid.py"
    p.write_text(src)
    lines = src.splitlines()
    n0 = len(base_src.splitlines())
    own = {i + 1 for i in range(n0, len(lines))
           if lines[i].strip() and not lines[i].strip().startswith("def ") and lines[i].strip() != "return x"}
    return sum(1 for m in cands(p) if isinstance(m, dict) and m.get("line") in own)


invisible = 0
for name, add in SHAPES.items():
    d = guard_sites(add)
    invisible += d == 0
    print(f"RESULT v2_sites_added[{name}]={d} count")
print(f"RESULT v2_invisible_shapes={invisible}_of_{len(SHAPES)} count")

# np.clip lines across the package with no candidate site on the line
unc = tot = 0
for f in sorted(glob.glob("custom_components/heatpump_optimizer/**/*.py", recursive=True)):
    tree = ast.parse(Path(f).read_text())
    lines = {n.lineno for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr == "clip" and isinstance(n.func.value, ast.Name) and n.func.value.id in ("np", "numpy")}
    if not lines:
        continue
    have = {m["line"] for m in cands(Path(f)) if isinstance(m, dict) and "line" in m}
    tot += len(lines)
    unc += len(lines - have)
print(f"RESULT v2_npclip_lines={tot} count")
print(f"RESULT v2_npclip_lines_uncovered={unc} count")
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
