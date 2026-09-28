"""P8 detector prototype: every published money unit must carry the currency
that DENOMINATES the numbers (the price feed's), not the label source.

METRIC: money_units_mismatched = published entities whose native unit names a
currency code different from the price feed's code, on a replayed hour.
ARMS: feed=EUR (price entity unit EUR/kWh, currency attr EUR) on the harness's
SEK-configured instance -- the D14-s2-02 / R7 D4-03 / R1 D4-04 configuration;
null: feed=SEK on the same instance.
Run from a tree root: PYTHONPATH=tests/hastub:tests:custom_components python3 <this> EUR|SEK
"""
import sys, json, tempfile, re
from pathlib import Path
from datetime import datetime, timedelta
feed = sys.argv[1]
import replay
captured = {}
real_sweep = replay.sweep
def sweep(entities, *a, **k):
    captured["e"] = entities
    return real_sweep(entities, *a, **k)
replay.sweep = sweep
src = json.loads(Path("tests/replay/synthetic-dhw-only.json").read_text())
pid = src["entry"]["data"]["price_entity"]
for row in src["states"][pid]:
    if row[2] is None: continue
    attrs = row[2]
    attrs["currency"] = feed
    attrs["unit_of_measurement"] = f"{feed}/kWh"
start = datetime.fromisoformat(src["window"]["start"])
src["window"]["end"] = (start + timedelta(hours=1)).isoformat()
with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "fx.json"; p.write_text(json.dumps(src)); run = replay.run_fixture(p, 30)
codes = re.compile(r"\b(SEK|EUR|NOK|DKK|USD|GBP)\b")
money, bad = 0, []
for e in captured["e"]:
    u = getattr(e, "native_unit_of_measurement", None) or getattr(e, "_attr_native_unit_of_measurement", None)
    if isinstance(u, str) and codes.search(u):
        money += 1
        if codes.search(u).group(1) != feed:
            bad.append(f"{getattr(e,'entity_id',None) or getattr(e,'_attr_unique_id','?')}={u}")
print(f"RESULT feed={feed} cycles={run['cycles']} money_units={money} money_units_mismatched={len(bad)}")
for b in bad[:12]: print("  MISMATCH", b)
