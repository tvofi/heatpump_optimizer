"""Probe 5b6489f7860d73b1: 2852 CLAMP_DROP min(...,100) on rh
metric: mold_safe_room_floor(20, rh, 0, 0.7) for rh_percent>100
command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g47-h/probes/probe_5b6489f7860d73b1.py
expected: baseline and mutant print the same value if equivalent; a different value (or an exception on one side) makes the key a candidate
baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (git show of thermal_model.py in a scratch package, never the gate tree)
machine: see wave/D3-g47-h/MACHINE.txt (provisional)
instrumented symbol: custom_components/heatpump_optimizer/thermal_model.py:mold_safe_room_floor
perturbation: '    rh = min(max(indoor_rh_percent, 0.0), 100.0) / 100.0' -> '    rh = (max(indoor_rh_percent, 0.0)) / 100.0' applied to a scratch copy of the baseline source
"""
import importlib.util, os, subprocess, sys, tempfile, math
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
OLD = '    rh = min(max(indoor_rh_percent, 0.0), 100.0) / 100.0'
NEW = '    rh = (max(indoor_rh_percent, 0.0)) / 100.0'
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
        v = mod.mold_safe_room_floor(*args)
        return repr(v)
    except Exception as e:
        return "EXC " + type(e).__name__
b, m = load(False), load(True)
for rh in (100.0, 100.0001, 120.0, 150.0, 1e6):
    for args in ((20.0, rh, 0.0, 0.7),):
        print("INPUT", args, "base", run(b, args), "mut", run(m, args))
rb, rm = run(b, (20.0, 150.0, 0.0, 0.7)), run(m, (20.0, 150.0, 0.0, 0.7))
print("RESULT floor_at_rh150_base=%s mutant=%s" % (rb, rm))
