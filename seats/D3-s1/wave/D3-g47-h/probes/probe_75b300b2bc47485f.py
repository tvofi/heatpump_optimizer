"""Probe 75b300b2bc47485f: 2856 CLAMP_DROP max(surface_rh_limit,0.05)
metric: mold_safe_room_floor(20, 50, 0, 0.7, limit) for limit<=0.05
command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g47-h/probes/probe_75b300b2bc47485f.py
expected: baseline and mutant print the same value if equivalent; a different value (or an exception on one side) makes the key a candidate
baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (git show of thermal_model.py in a scratch package, never the gate tree)
machine: see wave/D3-g47-h/MACHINE.txt (provisional)
instrumented symbol: custom_components/heatpump_optimizer/thermal_model.py:mold_safe_room_floor
perturbation: '    t_surface_min = dew_point_for_pressure(e / max(surface_rh_limit, 0.05))' -> '    t_surface_min = dew_point_for_pressure(e / (surface_rh_limit))' applied to a scratch copy of the baseline source
"""
import importlib.util, os, subprocess, sys, tempfile, math
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
OLD = '    t_surface_min = dew_point_for_pressure(e / max(surface_rh_limit, 0.05))'
NEW = '    t_surface_min = dew_point_for_pressure(e / (surface_rh_limit))'
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
for lim in (0.8, 0.05, 0.04, 0.01, 0.0, -0.5):
    args = (20.0, 50.0, 0.0, 0.7, lim)
    print("INPUT", args, "base", run(b, args), "mut", run(m, args))
args = (20.0, 50.0, 0.0, 0.7, 0.01)
print("RESULT floor_at_limit0.01_base=%s mutant=%s" % (run(b, args), run(m, args)))
