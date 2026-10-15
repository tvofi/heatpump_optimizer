"""V2 independent clone census for the D7-arch2 duplication findings (02-07, 09).

Metric: dup_funcs = function/method definitions in custom_components/heatpump_optimizer whose
normalised body (ast.dump after: string/number constants -> placeholder, docstring dropped, local
variable/argument names -> positional placeholder; attribute and global names KEPT) has >= --min-stmts (default 3)
statements and >= --min-nodes AST nodes and collides with at least one other definition. Independent of archscore's C3 gapped
clone census (different unit: whole function bodies, not token windows).
Null control: --patch with the patch applied then reversed (rename-free round trip) must equal
baseline; and the no-patch arm is the baseline itself.
Perturbation: --patch P; dup_funcs must fall for a patch that removes copies.
Run (from a tree root): python3 dev/audit/rounds/round10/catchup/arch-s2/clone_v2.py [--patch P ...] [--roundtrip]
Expected: baseline count printed; each finding's patch lowers it; --roundtrip equals baseline.
Baseline 554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef. Machine: shared macOS box; counts only.
"""
import argparse, ast, os, shutil, subprocess, sys, tempfile
from collections import defaultdict
from pathlib import Path

def repo_root(start):
    here = Path(start).resolve().parent
    m = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for c in (here, *here.parents):
        if (c / m).is_file():
            return c
    raise RuntimeError("no root")

REPO = repo_root(__file__)
MIN_STMTS, MIN_NODES = 3, 0
BASE = "554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef"

class Norm(ast.NodeTransformer):
    def __init__(self, local):
        self.local = {n: f"v{i}" for i, n in enumerate(local)}
    def visit_Constant(self, n):
        return ast.copy_location(ast.Constant(value=type(n.value).__name__), n)
    def visit_Name(self, n):
        if n.id in self.local:
            n.id = self.local[n.id]
        return n
    def visit_arg(self, n):
        if n.arg in self.local:
            n.arg = self.local[n.arg]
        n.annotation = None
        return n

def key(fn):
    body = list(fn.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant):
        body = body[1:]
    if len(body) < MIN_STMTS or sum(1 for b in body for _ in ast.walk(b)) < MIN_NODES:
        return None
    local = [a.arg for a in fn.args.args + fn.args.kwonlyargs]
    for n in ast.walk(fn):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store) and n.id not in local:
            local.append(n.id)
    mod = ast.Module(body=[Norm(local).visit(b) for b in body], type_ignores=[])
    return ast.dump(mod, annotate_fields=False)

def census(pkg):
    groups = defaultdict(list)
    for p in sorted(pkg.glob("*.py")):
        for n in ast.walk(ast.parse(p.read_text())):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                k = key(n)
                if k:
                    groups[k].append(f"{p.stem}.{n.name}:{n.lineno}")
    return {k: v for k, v in groups.items() if len(v) > 1}

ap = argparse.ArgumentParser(); ap.add_argument("--patch", action="append", default=[], type=Path)
ap.add_argument("--roundtrip", action="store_true"); ap.add_argument("--min-stmts", type=int, default=3); ap.add_argument("--min-nodes", type=int, default=0); ap.add_argument("-v", action="store_true")
a = ap.parse_args()
MIN_STMTS, MIN_NODES = a.min_stmts, a.min_nodes
print(f"RESULT params min_stmts={MIN_STMTS} min_nodes={MIN_NODES}")
sys.path.insert(0, str(REPO / "tools" / "audit"))
from archscore.score import tree_of
tmp = Path(tempfile.mkdtemp(prefix="cv-arch-s2-clone-"))
try:
    tree = tree_of(BASE, tmp / "t")
    for p in a.patch:
        subprocess.run(["patch", "-p1", "-s", "-f", "-d", str(tree), "-i", str(p.resolve())], check=True,
                       stdout=subprocess.DEVNULL)
    if a.roundtrip:
        for p in reversed(a.patch):
            subprocess.run(["patch", "-R", "-p1", "-s", "-f", "-d", str(tree), "-i", str(p.resolve())],
                           check=True, stdout=subprocess.DEVNULL)
    g = census(tree / "custom_components" / "heatpump_optimizer")
    print(f"RESULT dup_groups={len(g)} count")
    print(f"RESULT dup_funcs={sum(len(v) for v in g.values())} count")
    if a.v:
        for v in g.values():
            print("  ", v)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
