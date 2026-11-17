import sys; sys.path[:0] = ["tests/hastub", "custom_components"]
from heatpump_optimizer import store, draw_range as dr
keys = [k for k, d in store._ACCURACY.items() if not isinstance(d, str) and d.whole == store._DRAW_KEY]
print("rule returns:", keys)
