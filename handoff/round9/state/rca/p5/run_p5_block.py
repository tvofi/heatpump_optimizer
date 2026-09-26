"""Run the #1524 block and the R9-P5 block of tests/features.py alone, with a minimal Results stub.

Modes (argv[1]):
  defect     -- the tree as it is
  oracle     -- a stand-in for a fixed gate: a runner decision that admits a heat loss off the
                plant's by more than the bar becomes a refusal (the test knows the plant; the
                gate cannot). Shows the check is satisfiable and liveness survives it.
  null       -- every R9-P5 magnitude at identity (plant == declaration): the healthy tree
  bar_tight  -- UA_ADOPTION_HALFWIDTH_BAR / 10: a gate that refuses (almost) everything; the
                #1524 liveness checks must catch it
  empty      -- the R9-P5 axis tables emptied: the sweep must not go green by skipping
"""
import sys, time
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
mode = sys.argv[1] if len(sys.argv) > 1 else "defect"
src = open("tests/features.py").read()
start = src.index("# -- #1524: the experiment identifies a TWO-ZONE house")
r9 = src.index("# -- R9-P5: the gate refuses")
end = src.index('\nsys.exit(R.close("FEATURE CHECKS"))')
head = '''
import numpy as np
from datetime import datetime, timedelta, timezone
from profiles import house as _grad_house
from stress import BUILDINGS as _b942
from heatpump_optimizer import presets, const as _const922, sysid as _SysIdModule
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
class _R:
    fails = 0
    def check(self, name, ok, detail=""):
        print(("PASS " if ok else "FAIL ") + name[:110] + ("" if ok else f"  [{str(detail)[:600]}]"))
        self.fails += not ok
R = _R()
'''
pre, r9src = src[start:r9], src[r9:end]
if mode == "bar_tight":
    head += "_SysIdModule.UA_ADOPTION_HALFWIDTH_BAR = float(np.log(1.10)) / 10\n"
if mode == "newinput":
    # a future declared input the experiment is handed, with no axis yet
    head += """
import inspect as _i
_orig = _SysIdModule.SystemIdentification.step
_sig = _i.signature(_orig)
_orig.__signature__ = _sig.replace(parameters=[*_sig.parameters.values(),
    _i.Parameter("house_radiator_fraction", _i.Parameter.KEYWORD_ONLY, default=None)])
"""
    r9src = r9src.replace("(-0.2, 0.4, 0.8)", "(0.0,)").replace("(0.5, 2.0)", "(1.0,)").replace('{"drift": (0.1,)}', '{"drift": (0.0,)}').replace("(1.15,)", "(1.0,)").replace("(1.5,)", "(1.0,)")
if mode == "oracle":
    pre += '''
import functools
_z1524_real = _z1524_run
@functools.wraps(_z1524_real)
def _z1524_run(name, two_zone, true_ua=1.0, **kw):
    d, peak, why = _z1524_real(name, two_zone, true_ua=true_ua, **kw)
    if d.admit and abs(d.scale / true_ua - 1.0) > float(np.expm1(_SysIdModule.UA_ADOPTION_HALFWIDTH_BAR)):
        d = _SysIdModule.AdoptionDecision(False, 0.0, 0.0, "oracle: off the plant")
    return d, peak, why
'''
if mode == "null":
    r9src = r9src.replace("(-0.2, 0.4, 0.8)", "(0.0,)").replace("(0.5, 2.0)", "(1.0,)").replace('{"drift": (0.1,)}', '{"drift": (0.0,)}').replace("(1.15,)", "(1.0,)").replace("(1.5,)", "(1.0,)")
if mode == "empty":
    r9src = r9src.replace("(-0.2, 0.4, 0.8)", "()").replace("(0.5, 2.0)", "()").replace('{"drift": (0.1,)}', '{"drift": ()}').replace("(1.15,)", "()").replace("(1.5,)", "()")
if mode not in ("bar_tight", "oracle"):  # newinput too
    # the #1524 loops are not what this mode measures; keep only the runner and the bar
    pre = pre[:pre.index("_z1524_admitted = {True: 0")] + "_z1524_bar = float(np.expm1(_SysIdModule.UA_ADOPTION_HALFWIDTH_BAR))\n"
import stress, profiles, heatpump_optimizer.sysid  # already imported by features.py
t = time.time(); c0 = time.process_time()
exec(compile(head + pre + r9src, "features.py[#1524+R9-P5]", "exec"))
print(f"RESULT mode={mode} fails={R.fails} wall_s={time.time()-t:.2f} cpu_s={time.process_time()-c0:.2f}")
