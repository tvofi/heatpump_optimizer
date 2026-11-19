#!/usr/bin/env python3
"""D5-s3: do the modules whose docstring says they are free of Home Assistant imports import without it?

Metric: count of D5-s3 cell modules whose own docstring/comment claims "free of Home Assistant
imports" / "no Home Assistant import" / "HA-free" (CLAIM regex below, matched over the module
source) yet whose import, in a fresh interpreter with every `homeassistant` import refused and the
package `__init__` bypassed, raises ImportError. Key: the import outcome of the production module
itself (what a unit test without Home Assistant would hit), not the comment text.
Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D5/s3/ha_free.py [--perturb]
Expected: RESULT claimed=11, RESULT claimed_but_needs_ha=1 (grid_fee, via currency) at the baseline; exact.
Perturbation (--perturb): currency.py's `from homeassistant.core import HomeAssistant` moved under
`if TYPE_CHECKING:` in memory (the annotation is a string under `from __future__ import annotations`);
expected claimed_but_needs_ha -> 0 (to_zero).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B3. Counts only; no timing.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import glob, re, subprocess, sys, time

PKG = "custom_components/heatpump_optimizer"
CLAIM = re.compile(r"free of\s+(?:#\s*)?Home\s+(?:#\s*)?Assistant imports|no Home Assistant import|HA-free|imports no Home Assistant", re.S)
CELL = re.compile(r"^" + PKG + r"/[_a-i][^/]*\.py$")
#: A claim whose subject is another module: config_flow's ``_device_records`` docstring says
#: ``device_prefill`` stays free of Home Assistant imports, so that module is the one imported.
SUBJECT = {"config_flow": "device_prefill"}

CHILD = r'''
import importlib.abc, importlib.util, sys, types
PERTURB = sys.argv[2] == "1"
class Refuse(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        if name == "homeassistant" or name.startswith("homeassistant."):
            raise ImportError("homeassistant refused: " + name)
        return None
sys.meta_path.insert(0, Refuse())
for n in ("custom_components", "custom_components.heatpump_optimizer"):
    m = types.ModuleType(n); m.__path__ = [n.replace(".", "/")]; sys.modules[n] = m
if PERTURB:
    name = "custom_components.heatpump_optimizer.currency"
    src = open("custom_components/heatpump_optimizer/currency.py", encoding="utf-8").read()
    old = "from homeassistant.core import HomeAssistant\n"
    assert old in src
    src = src.replace(old, "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from homeassistant.core import HomeAssistant\n", 1)
    spec = importlib.util.spec_from_loader(name, loader=None)
    mod = importlib.util.module_from_spec(spec); mod.__file__ = "custom_components/heatpump_optimizer/currency.py"
    mod.__package__ = "custom_components.heatpump_optimizer"
    sys.modules[name] = mod
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
try:
    importlib.import_module("custom_components.heatpump_optimizer." + sys.argv[1])
    print("OK")
except ImportError as e:
    print("NEEDS_HA", e)
'''


def main():
    perturb = "--perturb" in sys.argv
    t0, w0 = time.process_time(), time.time()
    files = sorted(p for p in glob.glob(PKG + "/*.py") if CELL.match(p))
    claimed, bad = [], []
    env = dict(os.environ)
    env["PYTHONPATH"] = "."  # no tests/hastub: Home Assistant genuinely absent
    for f in files:
        src = open(f, encoding="utf-8").read()
        m = CLAIM.search(src)
        if not m:
            continue
        line = src.count("\n", 0, m.start()) + 1
        mod = SUBJECT.get(os.path.basename(f)[:-3], os.path.basename(f)[:-3])
        out = subprocess.run([sys.executable, "-c", CHILD, mod, "1" if perturb else "0"], capture_output=True, text=True, env=env).stdout.strip()
        claimed.append(mod)
        print(f"   {os.path.basename(f)}:{line} -> {mod} {out.splitlines()[-1] if out else 'NO OUTPUT'}")
        if not out.startswith("OK"):
            bad.append(mod)
    print(f"RESULT claimed={len(claimed)} modules")
    print(f"RESULT claimed_but_needs_ha={len(bad)} modules {','.join(bad)}")
    pc = time.process_time() - t0
    print(f"RESULT thread_factor={(pc / max(time.thread_time(), 1e-9)):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
