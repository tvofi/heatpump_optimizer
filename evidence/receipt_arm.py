import sys
from datetime import datetime, timezone
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from harness import FakeEntry, FakeHass
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
MARCH = datetime(2026, 3, 15, 12, 0, tzinfo=timezone.utc)
coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home"}))
led = coord._ledger
led.add(MARCH, "spot", kwh=100.0, sek=150.0)
led.add(MARCH, "grid_fee", kwh=105.0, sek=25.0)
led.add(MARCH, "immersion", kwh=5.0, sek=7.5)
led.add(MARCH, "wear", kwh=0.0, sek=12.0)
led.add(MARCH, "space", kwh=80.0, sek=120.0)
led.add(MARCH, "dhw", kwh=25.0, sek=37.5)
led.add(MARCH, "reason:cheap_hours", kwh=100.0, sek=150.0)
led.add(MARCH, "savings_baseline", kwh=120.0, sek=200.0)
led.add(MARCH, "savings_actual", kwh=105.0, sek=157.5)
r = coord._freeze_month_report("2026-03")
print("RESULT total_sek=%r basis=%r" % (r.get("total_sek"), r.get("basis")))
