import asyncio, json, sys
sys.path[:0] = ["tests/hastub", "custom_components", "tests"]
from homeassistant.helpers import storage
from heatpump_optimizer import store as s, const
from heatpump_optimizer.accuracy import AccuracyTracker
from harness import FakeHass
key = f"{const.DOMAIN}_x_accuracy"
storage._DISK.clear(); storage._VERSIONS.clear()
storage._DISK[key] = json.dumps({"accuracy": {"lead_pending": [["2026-01-01T00:00:00+00:00", True, 2.0]]}})
d = asyncio.run(s.QuarantiningStore(FakeHass({}), 1, key, lead=None).async_load())
print("loaded leaf:", d["accuracy"]["lead_pending"][0][1])
print("in_domain(choice, True):", s.in_domain(s.DOMAINS["accuracy"]["accuracy/lead_pending/#/1"], True))
t = AccuracyTracker.from_dict(d["accuracy"]) if hasattr(AccuracyTracker, "from_dict") else None
print("tracker lead_pending:", t.lead_pending if t else "n/a")
