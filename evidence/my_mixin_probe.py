"""Reviewer's own behavioural probe (not the finder's, not the fixer's).
For every sensor class that, AT HEAD, takes native_value from _PayloadNumberMixin, build the payload
at the head's _payload_path and read native_value on the class from TREE (base or head).
Usage: python3 my_mixin_probe.py HEAD_TREE TREE OUT.json
"""
import sys, json, math, importlib, inspect, types
import numpy as np
head_tree, tree, out = sys.argv[1], sys.argv[2], sys.argv[3]

def load(root):
    for m in [k for k in sys.modules if k == "heatpump_optimizer" or k.startswith("heatpump_optimizer.")]:
        del sys.modules[m]
    sys.path.insert(0, root + "/custom_components")
    mod = importlib.import_module("heatpump_optimizer.sensor")
    sys.path.pop(0)
    return mod

H = load(head_tree)
paths = {}
for n, c in inspect.getmembers(H, inspect.isclass):
    if c.__module__ != H.__name__ or not hasattr(H, "_PayloadNumberMixin"):
        continue
    if issubclass(c, H._PayloadNumberMixin) and c._payload_path and issubclass(c, H.HeatPumpOptimizerEntity):
        owner = next(k for k in c.__mro__ if "native_value" in vars(k) and not getattr(vars(k)["native_value"].fget, "_finite_scrubbed", False)) if False else None
        paths[n] = list(c._payload_path)
M = load(tree) if tree != head_tree else H

class AllOk(dict):
    def get(self, k, d=None): return True
    def __getitem__(self, k): return True
    def __contains__(self, k): return True

PROBES = {"float": 21.456, "int": 3, "zero": 0, "neg": -4.25, "np_f64": np.float64(2.5), "np_i64": np.int64(7),
          "none": None, "true": True, "false": False, "np_bool": np.bool_(True), "text": "21.5", "nan": float("nan"),
          "inf": float("inf"), "np_nan": np.float64("nan")}

def show(v):
    if isinstance(v, float) and math.isnan(v): return "nan"
    if isinstance(v, np.generic): return f"np:{type(v).__name__}:{v.item()!r}"
    return f"{type(v).__name__}:{v!r}"

res = {}
for n, path in sorted(paths.items()):
    c = getattr(M, n, None)
    if c is None:
        res[n] = "MISSING"; continue
    row = {}
    for pn, pv in PROBES.items():
        data = {"reading_ok": AllOk()}
        node = data
        for k in path[:-1]:
            node = node.setdefault(k, {})
        node[path[-1]] = pv
        obj = c.__new__(c)
        obj.coordinator = types.SimpleNamespace(data=data, last_update_success=True)
        try:
            row[pn] = show(obj.native_value)
        except Exception as e:
            row[pn] = f"EXC:{type(e).__name__}"
    res[n] = row
json.dump({"paths": paths, "res": res}, open(out, "w"), indent=1, sort_keys=True)
print("classes", len(paths))
