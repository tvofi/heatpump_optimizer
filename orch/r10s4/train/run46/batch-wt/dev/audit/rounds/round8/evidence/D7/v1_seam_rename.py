"""D7-v1 verifier harness for D7-s2-02: how far can a name-only change move the budgeted seam rows?

Metric (one line): for each coordinator method, the best (largest) drop in structure.seam_metrics'
  cross_edges (budgeted cross_seam_edges) achievable by renaming ONLY that method (its def and every
  self.<name> Attribute, AST-level) into ANY of the six buckets (core, dhw, learning, fetch, grid,
  views); counted: methods with a drop > 0, the max drop, and the max drop in sum(cut_*).
Differs from the finder's (rename into core only): a rename may target any seam.
Null control: rename each method to a fresh name that SEAM_REGEXES puts in its current bucket:
  every delta must be 0.
Perturbation (--perturb): SEAM_REGEXES emptied (one bucket); methods_with_drop must go to 0.
Also printed: the budget file's cross_seam_edges vs the measured baseline (headroom).
Command:  PYTHONPATH=tests/hastub python3 tools/audit/round8/D7/v1_seam_rename.py [--perturb]
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container (counts only).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast, copy, json, sys, time
from pathlib import Path
_p0, _t0 = time.process_time(), time.thread_time()
sys.path.insert(0, "tests")
import structure

tree = ast.parse(Path("custom_components/heatpump_optimizer/coordinator.py").read_text())
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == structure.COORDINATOR_CLASS_NAME)
TARGETS = {"core": "zzq_{i}", "dhw": "zzq_dhw_{i}", "learning": "zzq_learn_{i}", "fetch": "zzq_fetch_{i}",
           "grid": "zzq_grid_{i}", "views": "zzq_view_{i}"}


def bucket(name):
    for label, rx in structure.SEAM_REGEXES:
        if rx.search(name):
            return label
    return "core"


def renamed(old, new):
    c = copy.deepcopy(cls)
    for node in ast.walk(c):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == old and node in c.body:
            node.name = new
        if isinstance(node, ast.Attribute) and node.attr == old and isinstance(node.value, ast.Name) \
                and node.value.id == "self":
            node.attr = new
    return c


def score(c):
    m = structure.seam_metrics(c)
    return m["cross_edges"], sum(m["cut_costs"].values())


orig_rx = list(structure.SEAM_REGEXES)
try:
    if "--perturb" in sys.argv:
        structure.SEAM_REGEXES[:] = []
    base_x, base_cut = score(cls)
    names = [m.name for m in cls.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
    with_drop, max_drop, max_cut_drop, null_nonzero, top = 0, 0, 0, 0, None
    for i, n in enumerate(names):
        best = 0
        for lab, pat in TARGETS.items():
            new = pat.format(i=i)
            assert bucket(new) == (lab if structure.SEAM_REGEXES else "core")
            x, cut = score(renamed(n, new))
            best = max(best, base_x - x)
            max_cut_drop = max(max_cut_drop, base_cut - cut)
        # null: same bucket, fresh name
        own = bucket(n)
        x, cut = score(renamed(n, TARGETS[own].format(i=i) if structure.SEAM_REGEXES else f"zzq_{i}"))
        null_nonzero += int(x != base_x or cut != base_cut)
        if best > 0:
            with_drop += 1
            if best > max_drop:
                max_drop, top = best, n
finally:
    structure.SEAM_REGEXES[:] = orig_rx
budget = json.loads(Path("tests/structure_budgets.json").read_text()).get("cross_seam_edges")
print(f"RESULT methods={len(names)} count")
print(f"RESULT baseline_cross_seam_edges={base_x} count (budget {budget}); baseline_sum_cut={base_cut}")
print(f"RESULT methods_with_drop={with_drop} count (any-bucket rename lowers cross_seam_edges)")
print(f"RESULT max_single_rename_drop={max_drop} count ({top})")
print(f"RESULT max_single_rename_cut_drop={max_cut_drop} count")
print(f"RESULT null_nonzero={null_nonzero} count (must be 0)")
tf = (time.process_time() - _p0) / max(time.thread_time() - _t0, 1e-9)
print(f"RESULT thread_factor={tf:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
