"""D3-s2 M5 hook: counts HeatPumpOptimizer.optimize calls and harness
Results.check calls in every Python process started with this dir on
PYTHONPATH; writes <D3S2_COUNT_DIR>/<pid>.json at exit."""
import atexit
import importlib.abc
import importlib.util
import json
import os
import sys

_DIR = os.environ.get("D3S2_COUNT_DIR")
_C = {"solves": 0, "checks": 0, "argv": list(sys.argv)}


def _wrap_opt(mod):
    cls = getattr(mod, "HeatPumpOptimizer", None)
    if cls is None or getattr(cls.optimize, "_d3s2", False):
        return
    orig = cls.optimize

    def optimize(self, *a, **k):
        _C["solves"] += 1
        return orig(self, *a, **k)
    optimize._d3s2 = True
    cls.optimize = optimize


def _wrap_harness(mod):
    cls = getattr(mod, "Results", None)
    if cls is None or getattr(cls.check, "_d3s2", False):
        return
    orig = cls.check

    def check(self, *a, **k):
        _C["checks"] += 1
        return orig(self, *a, **k)
    check._d3s2 = True
    cls.check = check


_TARGETS = {"custom_components.heatpump_optimizer.optimizer": _wrap_opt,
            "heatpump_optimizer.optimizer": _wrap_opt,
            "harness": _wrap_harness}


class _Finder(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path, target=None):
        if name not in _TARGETS:
            return None
        sys.meta_path.remove(self)
        try:
            spec = importlib.util.find_spec(name)
        finally:
            sys.meta_path.insert(0, self)
        if spec is None or spec.loader is None:
            return spec
        loader = spec.loader
        orig_exec = loader.exec_module

        def exec_module(module, _o=orig_exec, _n=name):
            _o(module)
            _TARGETS[_n](module)
        loader.exec_module = exec_module
        return spec


if _DIR:
    sys.meta_path.insert(0, _Finder())

    @atexit.register
    def _dump():
        try:
            with open(os.path.join(_DIR, f"{os.getpid()}.json"), "w") as f:
                json.dump(_C, f)
        except OSError:
            pass
