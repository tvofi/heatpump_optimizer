"""Verifier VD3L V2 helper: load a whole-module mutant from the file on disk.

Unlike the finders' probes (which recompile ONE function from inspect.getsource),
this re-executes the entire module text with exactly one physical line replaced
(file:line must equal `old`, else REFUSE), as a fresh module object in the same
package, so every in-module caller sees the mutant. sys.modules is not touched.
"""
import importlib, importlib.util, sys, types
from pathlib import Path

PKG = "custom_components.heatpump_optimizer"


def root():
    import os
    return Path(os.environ.get("VROOT", ".")).resolve()


def load(mod, line=None, old=None, new=None):
    sys.path.insert(0, str(root()))
    base = importlib.import_module(f"{PKG}.{mod}")
    if line is None:
        return base
    path = Path(base.__file__)
    lines = path.read_text().split("\n")
    if lines[line - 1].strip() != old.strip():
        raise SystemExit(f"REFUSE {path.name}:{line} is {lines[line-1]!r}")
    indent = lines[line - 1][: len(lines[line - 1]) - len(lines[line - 1].lstrip())]
    lines[line - 1] = indent + new.strip()
    m = types.ModuleType(f"{PKG}.{mod}")
    m.__file__ = str(path)
    m.__package__ = PKG
    saved = sys.modules[m.__name__]
    sys.modules[m.__name__] = m  # dataclasses resolve string annotations via sys.modules
    try:
        exec(compile("\n".join(lines), str(path), "exec"), m.__dict__)
    finally:
        sys.modules[m.__name__] = saved
    return base, m
