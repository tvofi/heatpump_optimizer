"""Run main's #1590 typing-census arm (source lifted verbatim from tests/doc_claims.py) against the tree at a given SHA."""
import ast, re, subprocess, sys, time
M = sys.argv[1]; shas = sys.argv[2:]
src = open(f"{M}/tests/doc_claims.py").read(); mod = ast.parse(src)
fns = [n for n in mod.body if isinstance(n, ast.FunctionDef) and n.name in ("_names_bare_entry", "bare_entry_annotations")]
ns = {"ast": ast}; exec(compile(ast.Module(body=fns, type_ignores=[]), "arm", "exec"), ns)
def show(sha, path): return subprocess.run(["git", "-C", M, "show", f"{sha}:{path}"], capture_output=True, text=True).stdout
for sha in shas:
    files = subprocess.run(["git", "-C", M, "ls-tree", "--name-only", sha, "custom_components/heatpump_optimizer/"], capture_output=True, text=True).stdout.split()
    t0 = time.perf_counter()
    trees = {f.rsplit("/", 1)[1]: ast.parse(show(sha, f)) for f in files if f.endswith(".py")}
    t1 = time.perf_counter(); hits = ns["bare_entry_annotations"](trees); t2 = time.perf_counter()
    y = show(sha, "custom_components/heatpump_optimizer/quality_scale.yaml")
    m = re.search(r"qs_entry_param_bare=(\d+)", y); claimed = int(m.group(1)) if m else None
    verdict = "no claim" if claimed is None else ("PASS" if claimed == len(hits) else "FAIL")
    print(f"{sha[:8]} claimed={claimed} census={len(hits)} {verdict}  walk={1000*(t2-t1):.1f}ms parse={1000*(t1-t0):.0f}ms  {hits[:6]}")
