"""Reviewer's own companion (not the fixer's scratch one): count preheat_weather per arm of probe.py."""
import sys, runpy
probe, wt = sys.argv[1], sys.argv[2]
sys.argv = [probe, wt]
src = open(probe).read()
cut = src.index("\nif __name__") if "\nif __name__" in src else len(src)
g = {"__name__": "probe_mod"}
exec(compile(src[:cut], probe, "exec"), g)
H = g["HeatPumpOptimizer"]; orig = H.optimize; last = {}
def wrap(self, *a, **k):
    r = orig(self, *a, **k); last["r"] = r; return r
H.optimize = wrap
for name, f in g["ARMS"]:
    if name.split()[0] in ("1", "7b", "s1", "s3", "4"):
        f(); sr = list(last["r"].space_reasons)
        print(f"ARM {name.split()[0]:<3} preheat_weather={sr.count('preheat_weather')} of {len(sr)}")
