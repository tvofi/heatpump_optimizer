"""Probe 1111a3e5d9c44e3f: 2854 CMP_BOUND e <= 1e-9 -> < 1e-9
metric: mold_safe_room_floor with vapour pressure e exactly 1e-9
command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g47-h/probes/probe_1111a3e5d9c44e3f.py
expected: baseline and mutant print the same value if equivalent; a different value (or an exception on one side) makes the key a candidate
baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (git show of thermal_model.py in a scratch package, never the gate tree)
machine: see wave/D3-g47-h/MACHINE.txt (provisional)
instrumented symbol: custom_components/heatpump_optimizer/thermal_model.py:mold_safe_room_floor
perturbation: '    if e <= 1e-9:' -> '    if e < 1e-9:' applied to a scratch copy of the baseline source
"""
import importlib.util, os, subprocess, sys, tempfile, math
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
OLD = '    if e <= 1e-9:'
NEW = '    if e < 1e-9:'
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
svp = b.saturation_vapor_pressure
tried = []
hit = None
for T in [x / 4.0 for x in range(-80, 160)]:
    s = svp(T)
    for rh in (1e-9 / s * 100.0, math.nextafter(1e-9 / s * 100.0, 0), math.nextafter(1e-9 / s * 100.0, 1e9)):
        e = (max(rh, 0.0)) / 100.0 * s
        tried.append((T, rh, e))
        if e == 1e-9 and hit is None: hit = (T, rh)
print("INPUTS tried", len(tried), "exactly-1e-9 hits", hit)
if hit:
    args = (hit[0], hit[1], 0.0, 0.7)
    print("RESULT floor_e_eq_1e-9_base=%s mutant=%s" % (run(b, args), run(m, args)))
else:
    print("RESULT no_input_with_e_eq_1e-9_found=1")
