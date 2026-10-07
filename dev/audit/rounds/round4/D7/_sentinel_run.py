"""Run by dead_methods_r4.py: wrap candidates, drive the real setup."""
import os, sys, inspect, functools
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
NAMES = set(filter(None, os.environ.get("HPO_D7_SENTINEL_NAMES", "").split(",")))
HITS = set()
CALLS = [0]


def _wrap(cls, name, fn):
    @functools.wraps(fn)
    def inner(*a, **k):
        HITS.add(name)
        CALLS[0] += 1
        return fn(*a, **k)
    setattr(cls, name, inner)


import pkgutil, importlib
import heatpump_optimizer as pkg
for mod in list(pkgutil.iter_modules(pkg.__path__)):
    try:
        importlib.import_module(f"heatpump_optimizer.{mod.name}")
    except Exception:
        pass
seen = set()
for modname, module in list(sys.modules.items()):
    if not modname.startswith("heatpump_optimizer"):
        continue
    for _, obj in list(vars(module).items()):
        if not inspect.isclass(obj) or obj in seen:
            continue
        seen.add(obj)
        for name in NAMES:
            fn = obj.__dict__.get(name)
            if callable(fn):
                _wrap(obj, name, fn)

import runpy
try:
    runpy.run_path("tests/entities.py", run_name="__entities_sentinel__")
except SystemExit:
    pass
except Exception as exc:  # noqa: BLE001
    print("SENTINEL_ERROR", type(exc).__name__, exc, file=sys.stderr)
for h in sorted(HITS):
    print("SENTINEL_HIT", h)
print("SENTINEL_CALLS", CALLS[0])
