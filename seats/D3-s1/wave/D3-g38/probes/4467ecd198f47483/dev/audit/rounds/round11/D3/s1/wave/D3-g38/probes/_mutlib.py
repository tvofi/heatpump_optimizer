"""Shared driver for box D3-g38's probes: load the baseline module, re-compile ONE production
function with ONE line replaced (the mutant's exact old -> new text), in memory, never on disk.

ROOT is HPO_PROBE_ROOT when set (a clean baseline checkout, so a probe never reads the gate
tree while a gate has a mutant applied there), else the repository root above this file.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import importlib, inspect, sys
from pathlib import Path


def repo_root(start):
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = Path(os.environ["HPO_PROBE_ROOT"]) if os.environ.get("HPO_PROBE_ROOT") else repo_root(__file__)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests" / "hastub"))


def module(name="sysid"):
    mod = importlib.import_module(f"custom_components.heatpump_optimizer.{name}")
    assert Path(mod.__file__).resolve().is_relative_to(ROOT.resolve()), mod.__file__
    return mod


def mutant(mod, func, old, new, overrides=None):
    """The function ``func`` of ``mod`` with the line ``old`` (exact, with indentation)
    replaced by ``new``; ``overrides`` replace module globals in BOTH arms' view when
    given (returned base is then re-compiled unchanged under the same overrides)."""
    src = inspect.getsource(getattr(mod, func))
    assert src.count(old) == 1, f"anchor {old!r} not unique/missing in {func}"
    out = []
    for text in (src, src.replace(old, new, 1)):
        ns = dict(mod.__dict__)
        ns.update(overrides or {})
        exec(compile(text, mod.__file__, "exec"), ns)
        out.append(ns[func])
    return out  # [baseline (recompiled), mutant]
