"""Shared loader for the D3-g47 probes: the baseline thermal_model, or a copy with ONE line replaced, in memory."""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import importlib, sys, types
from pathlib import Path

def repo_root(start):
    here = Path(start).resolve()
    here = here.parent if here.is_file() else here
    for c in (here, *here.parents):
        if (c / "custom_components" / "heatpump_optimizer" / "manifest.json").is_file():
            return c
    raise RuntimeError("no repo root")

ROOT = repo_root(__file__)
sys.path[:0] = [str(ROOT), str(ROOT / "tests" / "hastub")]
PKG = "custom_components.heatpump_optimizer"
importlib.import_module(PKG)
SRC = (ROOT / "custom_components" / "heatpump_optimizer" / "thermal_model.py")

def load(line=None, old=None, new=None):
    """Baseline module (line None) or a private copy with `old` on `line` replaced by `new`."""
    text = SRC.read_text().split("\n")
    if line is not None:
        assert text[line - 1] == old, (text[line - 1], old)
        text[line - 1] = new
    name = f"{PKG}._g47_{'base' if line is None else line}_{abs(hash(new))}"
    mod = types.ModuleType(name)
    mod.__file__ = str(SRC); mod.__package__ = PKG
    sys.modules[name] = mod
    exec(compile("\n".join(text), str(SRC), "exec"), mod.__dict__)
    return mod

def call(fn, *a, **k):
    try:
        return fn(*a, **k)
    except Exception as e:  # the exception type is the observable
        return f"RAISES {type(e).__name__}"

import json, math

def _same(a, b):
    if isinstance(a, str) or isinstance(b, str):
        return a == b
    if isinstance(a, tuple):
        return isinstance(b, tuple) and len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, float) and isinstance(b, float):
        return (math.isnan(a) and math.isnan(b)) or a == b
    return a == b

def probe(key, fname, inputs, controls):
    """inputs: dicts of kwargs that may distinguish the edit; controls: kwargs where it cannot matter."""
    line, old, new = json.loads((Path(__file__).parent / "mutants.json").read_text())[key]
    base, mut = load(), load(line, old, new)
    diff = 0; first = None
    for tag, group in (("input", inputs), ("control", controls)):
        n = 0
        for kw in group:
            b, m = call(getattr(base, fname), **kw), call(getattr(mut, fname), **kw)
            d = not _same(b, m)
            print(f"{tag.upper()} {kw} base={b!r} mut={m!r} {'DIFF' if d else 'same'}")
            if d:
                n += 1
                if tag == "input" and first is None:
                    first = (b, m)
        if tag == "input":
            diff = n
        else:
            print(f"RESULT null_control_differing={n} count (of {len(group)})")
    print(f"RESULT inputs_differing={diff} count (of {len(inputs)})")
    if first:
        print(f"RESULT baseline_value={first[0]!r}")
        print(f"RESULT mutant_value={first[1]!r}")
