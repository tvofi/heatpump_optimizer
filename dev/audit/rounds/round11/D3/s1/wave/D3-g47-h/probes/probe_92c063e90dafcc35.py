"""Probe 92c063e90dafcc35: 2903 CMP_BOUND hp_temp > flow_set -> >=
metric: wood_share at hp_temp == flow_set
command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g47-h/probes/probe_92c063e90dafcc35.py
expected: baseline and mutant print the same value if equivalent; a different value (or an exception on one side) makes the key a candidate
baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (git show of thermal_model.py in a scratch package, never the gate tree)
machine: see wave/D3-g47-h/MACHINE.txt (provisional)
instrumented symbol: custom_components/heatpump_optimizer/thermal_model.py:wood_share
perturbation: '    if hp_temp > flow_set:' -> '    if hp_temp >= flow_set:' applied to a scratch copy of the baseline source
"""
import importlib.util, os, subprocess, sys, tempfile, math
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
OLD = '    if hp_temp > flow_set:'
NEW = '    if hp_temp >= flow_set:'
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
diff = None; n = 0
import itertools
for flow in (30.0, 40.0, 45.5, 55.0):
  for wood in (-5.0, 0.0, 20.0, flow - 5, flow - 1, flow - 0.1, flow - 1e-9, math.nextafter(flow, 0)):
    for floor in (-10.0, 0.0, 20.0, flow - 10, flow, flow + 3):
      for margin in (0.0, 1e-9, 1.0, 3.0, 5.0):
        args = (wood, flow, flow, floor, margin); n += 1
        rb, rm = run(b, args), run(m, args)
        if rb != rm and diff is None: diff = (args, rb, rm)
print("INPUTS tried", n, "first difference", diff)
args = (20.0, 40.0, 40.0, 20.0)
print("RESULT wood_share_hp_eq_flow_base=%s mutant=%s ndiff=%d" % (run(b, args), run(m, args), 0 if diff is None else 1))
