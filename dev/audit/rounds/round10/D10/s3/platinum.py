"""D10-s3 platinum-tier rule census (D10.M1/M2, axis platinum).
Metric: per platinum rule, count of AST violations in custom_components/heatpump_optimizer:
  inject_websession  = aiohttp.ClientSession(...) / aiohttp.request(...) constructions (should be 0)
  async_dependency   = imports of sync HTTP libs (requests, urllib.request, httpx sync, http.client) (should be 0)
  strict_typing      = py.typed present (1) and functions in the package lacking a return annotation
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D10/s3/platinum.py
Expected: inject_websession=0, async_dependency=0, py_typed=1 (unannotated count reported, +-0).
Baseline 17f1c55fad1b; machine: macOS arm64 B3. Count key: AST call/import nodes in production source.
Perturbation: add `aiohttp.ClientSession()` to price_model._tibber_post -> inject_websession 0->1.
"""
import os
for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")
import ast, pathlib
PKG = pathlib.Path("custom_components/heatpump_optimizer")
sess = sync = unann = funcs = 0
SYNC = {"requests", "urllib.request", "http.client", "urllib3", "httpx"}
for p in sorted(PKG.glob("*.py")):
    t = ast.parse(p.read_text())
    for n in ast.walk(t):
        if isinstance(n, ast.Call):
            s = ast.unparse(n.func)
            if s in ("aiohttp.ClientSession", "ClientSession", "aiohttp.request"):
                sess += 1; print("SESSION", p, n.lineno)
        elif isinstance(n, ast.Import):
            for a in n.names:
                if a.name in SYNC: sync += 1; print("SYNCIMPORT", p, n.lineno, a.name)
        elif isinstance(n, ast.ImportFrom) and n.module in SYNC:
            sync += 1; print("SYNCIMPORT", p, n.lineno, n.module)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs += 1
            if n.returns is None: unann += 1
print("thread_factor 1")
print(f"RESULT inject_websession={sess} count")
print(f"RESULT async_dependency={sync} count")
print(f"RESULT py_typed={int((PKG/'py.typed').exists())} count")
print(f"RESULT functions={funcs} count")
print(f"RESULT unannotated_returns={unann} count")
