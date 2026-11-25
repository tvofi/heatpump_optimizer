"""Probe 6fa8436f09ad7e06: 2906 CLAMP_DROP max(flow_set-floor_temp,1e-6)
metric: wood_share(wood, hp>flow, flow, floor==flow)
command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g47-h/probes/probe_6fa8436f09ad7e06.py
expected: baseline and mutant print the same value if equivalent; a different value (or an exception on one side) makes the key a candidate
baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (git show of thermal_model.py in a scratch package, never the gate tree)
machine: see wave/D3-g47-h/MACHINE.txt (provisional)
instrumented symbol: custom_components/heatpump_optimizer/thermal_model.py:wood_share
perturbation: '        span = max(flow_set - floor_temp, 1e-6)' -> '        span = (flow_set - floor_temp)' applied to a scratch copy of the baseline source
"""
import importlib.util, os, subprocess, sys, tempfile, math
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
OLD = '        span = max(flow_set - floor_temp, 1e-6)'
NEW = '        span = (flow_set - floor_temp)'
def load(mutant):
    d = tempfile.mkdtemp()
    pk = os.path.join(d, "custom_components"); subprocess.run(
        "git archive %s custom_components | tar -x -C %s" % (BASE, d), shell=True, check=True,
        cwd=os.environ.get("HPO_REPO", "."))
    f = os.path.join(pk, "heatpump_optimizer", "thermal_model.py")
    s = open(f).read()
    if mutant:
        assert s.count(OLD) == 1, s.count(OLD)
        open(f, "w").write(s.replace(OLD, NEW))
    sys.path.insert(0, d)
    for m in [m for m in sys.modules if m.startswith("custom_components")]: del sys.modules[m]
    import importlib
    mod = importlib.import_module("custom_components.heatpump_optimizer.thermal_model")
    sys.path.remove(d)
    return mod
def run(mod, args):
    try:
        v = mod.wood_share(*args)
        return repr(v)
    except Exception as e:
        return "EXC " + type(e).__name__
b, m = load(False), load(True)
for args in ((30.0, 50.0, 40.0, 40.0), (50.0, 50.0, 40.0, 40.0), (30.0, 50.0, 40.0, 45.0), (30.0, 50.0, 40.0, 20.0), (39.0, 50.0, 40.0, 40.0)):
    print("INPUT", args, "base", run(b, args), "mut", run(m, args))
args = (30.0, 50.0, 40.0, 40.0)
print("RESULT wood_share_floor_eq_flow_base=%s mutant=%s" % (run(b, args), run(m, args)))
