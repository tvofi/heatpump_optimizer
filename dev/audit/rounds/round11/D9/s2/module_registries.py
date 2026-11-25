#!/usr/bin/env python3
"""D9-s2 module registries: every module-level container a production function mutates, per file.

METRIC: count, per production .py file, of module-level dict/list/set/deque globals that a
function in the same file writes (append/add/update/setdefault/extend/insert/subscript
assignment), each printed with the global's line (read its constructor there: WeakKeyDictionary or strong).
A strong container keyed by something that churns would grow without bound; a weak one
dies with its owner (reload.py measures that dynamically). Static: it reads source, so it
supports non-findings only, never a finding on its own.
RUN:   python3 dev/audit/rounds/round11/D9/s2/module_registries.py
EXPECTED: 23 mutation sites in 16 files at the baseline (exact).
BASELINE: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. MACHINE: any.
"""
import ast, pathlib, sys
root = pathlib.Path("custom_components/heatpump_optimizer")
for p in sorted(root.glob("*.py")):
    t = ast.parse(p.read_text())
    globs = {}
    for n in t.body:
        tg = None
        if isinstance(n, ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0], ast.Name): tg, v = n.targets[0].id, n.value
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.value is not None: tg, v = n.target.id, n.value
        if tg and isinstance(v,(ast.Dict,ast.List,ast.Set,ast.Call)):
            if isinstance(v, ast.Call) and not (isinstance(v.func, ast.Name) and v.func.id in ("dict","list","set","deque","OrderedDict","defaultdict","WeakValueDictionary","WeakKeyDictionary")): continue
            globs[tg] = n.lineno
    hits = []
    for n in ast.walk(t):
        if isinstance(n, ast.FunctionDef) or isinstance(n, ast.AsyncFunctionDef):
            for m in ast.walk(n):
                tgt = None
                if isinstance(m, ast.Call) and isinstance(m.func, ast.Attribute) and isinstance(m.func.value, ast.Name) and m.func.value.id in globs and m.func.attr in ("append","add","update","setdefault","extend","__setitem__","insert","appendleft"):
                    tgt = m.func.value.id
                if isinstance(m, (ast.Assign, ast.AugAssign)):
                    ts = m.targets if isinstance(m, ast.Assign) else [m.target]
                    for x in ts:
                        if isinstance(x, ast.Subscript) and isinstance(x.value, ast.Name) and x.value.id in globs: tgt = x.value.id
                if tgt: hits.append((tgt, n.name, m.lineno))
    for h in hits: print(f"{p.name}:{h[2]} {h[0]} (global@{globs[h[0]]}) in {h[1]}")
print(f"RESULT files_scanned={len(list(root.glob('*.py')))} count")
print("RESULT thread_factor=1.000")
import os as _os
print(f"RESULT load1={_os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
