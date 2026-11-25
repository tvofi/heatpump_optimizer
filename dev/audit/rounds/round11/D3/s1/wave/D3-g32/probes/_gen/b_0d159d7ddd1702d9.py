from datetime import datetime, timedelta, timezone
from custom_components.heatpump_optimizer import price_model as pm

OLD = "        if model is None or model.confidence(when) <= 0.0:"
NEW = "        if model is None or model.confidence(when) < 0.0:"
mut = mutate(pm, "extend_price_series", OLD, NEW)
t0 = datetime(2026, 1, 14, 12, 0, tzinfo=timezone.utc)  # a Wednesday
times = [t0 + timedelta(hours=i) for i in range(6)]
known = [1.0, 2.0, 3.0]


def tail_prices(fn, model):
    prices, mask, sigma = fn(list(known), 6, times, model)
    return [float(x) for x in prices[3:]], [float(s) for s in sigma[3:]]


fresh = pm.PriceShapeModel()  # nothing learned: confidence 0.0 on every hour
assert fresh.confidence(times[3]) == 0.0
b, bs = tail_prices(pm.extend_price_series, fresh)
m, ms = tail_prices(mut, fresh)
print(f"RESULT guessed_tail_baseline={b}")
print(f"RESULT guessed_tail_mutant={m}")
print(f"RESULT guessed_tail_delta={max(abs(x - y) for x, y in zip(b, m)):.4f} SEK/kWh")
print(f"RESULT sigma_delta={max(abs(x - y) for x, y in zip(bs, ms)):.4f} SEK/kWh")
# null control: no model at all, where both arms take the flat repeat
nb, _ = tail_prices(pm.extend_price_series, None)
nm, _ = tail_prices(mut, None)
print(f"RESULT null_delta={max(abs(x - y) for x, y in zip(nb, nm)):.4f} SEK/kWh")
# null control 2: a constant known window, where mean == last price
known = [2.0, 2.0, 2.0]
cb, _ = tail_prices(pm.extend_price_series, fresh)
cm, _ = tail_prices(mut, fresh)
print(f"RESULT flat_known_delta={max(abs(x - y) for x, y in zip(cb, cm)):.4f} SEK/kWh")
tail()
