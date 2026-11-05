"""Reviewer's slicer: R9-F2.1 P3's storage solve, verbatim from tests/features.py, without the rest of the file."""
import sys, pathlib
sys.path.insert(0, "tests")
import numpy as np
from datetime import datetime
from profiles import solve_inputs
from heatpump_optimizer import optimizer as _f21_optmod
from heatpump_optimizer.optimizer import HeatPumpOptimizer as _f21_Opt, OptimizationConfig as _f21_Cfg
from heatpump_optimizer.thermal_model import ThermalModel as _f21_Model, ThermalParameters as _f21_Params
src = pathlib.Path("tests/features.py").read_text().splitlines()
a = next(i for i, l in enumerate(src) if l.startswith("from profiles import house as _f21_house"))
b = next(i for i, l in enumerate(src) if i > a and l.startswith("_f21_probe = ("))
class _R:
    def check(self, name, ok, detail=""):
        print(("  ok   " if ok else "  FAIL ") + name + ("" if ok else "  [" + detail + "]"))
g = dict(globals()); g["R"] = _R()
exec(compile("\n".join(src[a:b]), "features-slice", "exec"), g)
