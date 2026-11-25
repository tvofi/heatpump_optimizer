#!/usr/bin/env python3
# Shared loader for box D3-g39's step-4 probes (not a probe itself).
# load(module, old, new) returns (baseline_module, mutant_module): the mutant is the
# production module's own source with exactly one line replaced (`old` must occur
# once), compiled under a sibling module name inside the same package so its
# relative imports resolve to the baseline's modules. The file on disk is never
# written, so the probe is safe beside a running gate as long as it runs from a
# separate baseline tree (box D3-g39 ran them from a second worktree, $HOME/probe-tree).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import importlib
import sys
import types
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


ROOT = repo_root(__file__)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PKG = "custom_components.heatpump_optimizer"


def load(modname, old, new, line=None):
    base = importlib.import_module(f"{PKG}.{modname}")
    src = Path(base.__file__).read_text()
    lines = src.splitlines(keepends=True)
    hits = [i for i, l in enumerate(lines) if l.rstrip("\n") == old]
    if line is not None:
        # the mutant names its line: anchor there (the text may recur elsewhere in the file)
        assert (line - 1) in hits, f"line {line} is not {old!r}"
        hits = [line - 1]
    assert len(hits) == 1, f"anchor line found {len(hits)} times: {old!r}"
    lines[hits[0]] = new + "\n"
    name = f"{PKG}._mut_{modname}"
    mod = types.ModuleType(name)
    mod.__file__ = base.__file__
    mod.__package__ = PKG
    sys.modules[name] = mod
    exec(compile("".join(lines), base.__file__, "exec"), mod.__dict__)
    return base, mod, hits[0] + 1


def arm(fn, *a, **k):
    """Call fn, mapping an exception to its type name (an observable outcome)."""
    try:
        return fn(*a, **k)
    except Exception as e:  # noqa: BLE001
        return f"raises {type(e).__name__}"
