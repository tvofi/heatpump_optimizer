"""R10 D3-s1-02: does the short-schedule check in tests/features.py kill every
`X and i < len(X)` guard of HeatPumpOptimizer.get_current_action?

Metric: each guard is flipped to `or`, in memory (the method re-compiled from
its source, patched onto the class), and the R10 D3-s1-02 block of
tests/features.py is executed against it. killed counts the flips under which
that block has a failing check.
Null: --null re-runs every arm with no flip (killed 0).

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_i1_action_guards.py [--null]
"""
import sys, re, inspect, textwrap, io, contextlib
sys.path[:0] = ["custom_components", "tests", "tests/hastub"]
from datetime import datetime as _SavDT, timedelta
import heatpump_optimizer.optimizer as opt
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
from harness import Results
src = open("tests/features.py").read()
block = src[src.index("# R10 D3-s1-02"):src.index("# #1499: Heat Pump Action")]
fn = opt.HeatPumpOptimizer.get_current_action
first = fn.__code__.co_firstlineno
lines = inspect.getsource(fn).split("\n")
G = re.compile(r"if result\.(\w+) and i < len\(result\.\1\)")
sites = [k for k, l in enumerate(lines) if G.search(l)]
null = "--null" in sys.argv
killed = 0
for k in sites:
    m = list(lines)
    if not null:
        m[k] = m[k].replace(" and i < len(", " or i < len(", 1)
    ns = {}
    exec(compile("\n" * (first - 1) + textwrap.dedent("\n".join(m)), opt.__file__, "exec"), opt.__dict__, ns)
    orig = opt.HeatPumpOptimizer.get_current_action
    opt.HeatPumpOptimizer.get_current_action = ns["get_current_action"]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            R = Results("g")
            env = dict(R=R, _SavOR=opt.OptimizationResult, timedelta=timedelta,
                       _bl_opt=opt.HeatPumpOptimizer(ThermalModel(ThermalParameters()), opt.OptimizationConfig()),
                       _ts_sav=[_SavDT(2026, 2, 10, 12, 0) + timedelta(minutes=15 * i) for i in range(4)])
            exec(block, env)
    finally:
        opt.HeatPumpOptimizer.get_current_action = orig
    dead = R.failures > 0
    killed += dead
    print(f"optimizer.py:{first + k} {G.search(lines[k]).group(1):26s} failures={R.failures} {'KILLED' if dead else 'survived'}")
print(f"RESULT guards={len(sites)} killed={killed} null={null}")
