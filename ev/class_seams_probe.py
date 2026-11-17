import sys; sys.path[:0] = ["tests/hastub", "custom_components"]
from heatpump_optimizer import draw_range as dr
good = {"samples": [[1.2, 1.0]] * 20, "engaged": True, "config": [0.53, 5.0], "idle": [], "ceiling": [],
        "overdraws": 0, "floor_since": 5, "floor_kw": 1.1}
g = dr.DrawRange.from_dict(good).as_dict()
print("null: good round-trips:", dr.DrawRange.from_dict(g).as_dict() == g, "| samples", len(g["samples"]), "engaged", g["engaged"], "floor", g.get("floor_kw"))
for leaf, bad in (("engaged", "x"), ("config", ["x", 3.3])):
    a = dr.DrawRange.from_dict({**g, leaf: bad}).as_dict()
    print(f"draw/{leaf}={bad!r}: samples {len(a['samples'])} engaged {a['engaged']} config {a.get('config')} floor {a.get('floor_kw')}")
