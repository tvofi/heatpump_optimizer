"""D2-s2 harness: an entity price source's unit is never read.

Metric: planning price per step delivered by Coordinator._price_series divided
by the true SEK/kWh (spot converted by the entity's own unit, + the SEK/kWh grid
fee), median over the 96 steps; and the grid-fee day/night step's share of the
planning-price spread. Count key: the value the production seam
(coordinator.HeatPumpOptimizerCoordinator._price_series, fed through
price_model.pull_prices from a HACS-Nord-Pool-style sensor) delivers.

Command (repo root):
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  VECLIB_MAXIMUM_THREADS=1 PYTHONPATH=tests/hastub python3 tools/audit/round8/D2/s2_price_unit.py
Perturbation: the sensor's unit attribute SEK/kWh -> öre/kWh (values x100, the
Nord Pool "price_in_cents" option) or SEK/MWh (x1000). The misread ratio moves
1.0 -> 83.0 / 828.6 (import) and 100 / 1000 (export) at baseline; a fix that
honours the unit keeps every ratio at 1.0.
Null control: the SEK/kWh arm (ratio exactly 1.0).
Expected (baseline): ratio_SEK_per_kWh=1.000, ratio_ore_per_kWh=83.01,
ratio_SEK_per_MWh=828.6; export_ratio 1 / 100 / 1000 (deterministic, exact to 1e-9).
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sys.path.insert(0, "tests")
sys.path.insert(0, ".")
import numpy as np
from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
from custom_components.heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)

t0p, t0t = time.process_time(), time.thread_time()
TZ = ZoneInfo("Europe/Stockholm")
midnight = datetime(2026, 11, 3, tzinfo=TZ)  # a Tuesday, in Nov-Mar
spot = np.array([0.30, 0.28, 0.27, 0.26, 0.27, 0.35, 0.80, 1.40, 1.60, 1.20,
                 0.90, 0.80, 0.75, 0.70, 0.72, 0.85, 1.10, 1.70, 1.90, 1.50,
                 1.00, 0.70, 0.50, 0.40])  # SEK/kWh, hourly
FEE_RULES = "Nov-Mar Mon-Fri 06:00-22:00 = 0.25"
FEE_FIXED = 0.05
SCALE = {"SEK/kWh": 1.0, "öre/kWh": 100.0, "SEK/MWh": 1000.0}


def run(unit):
    s = SCALE[unit]
    raw = [{"start": (midnight + timedelta(hours=h)).isoformat(),
            "end": (midnight + timedelta(hours=h + 1)).isoformat(),
            "value": float(spot[h] * s)} for h in range(24)]
    state = FakeState(str(spot[0] * s), unit=unit, attributes={
        "raw_today": raw, "raw_tomorrow": [], "currency": "SEK",
        "price_in_cents": unit == "öre/kWh"})
    cfg = {"price_source": "entity", "price_entity": "sensor.nordpool",
           "weather_entity": "weather.home", "indoor_temp_entity": "sensor.indoor",
           "outdoor_temp_entity": "sensor.outdoor",
           "grid_fee_mode": "rules", "grid_fee_rules": FEE_RULES,
           "grid_fee_fixed": FEE_FIXED}
    coord = HeatPumpOptimizerCoordinator(FakeHass({"sensor.nordpool": state}),
                                         FakeEntry(data=cfg))
    asyncio.run(coord._fetch_tibber_prices())
    out = coord._price_series(96, midnight, 0)
    prices = out[0]
    hours = np.repeat(np.arange(24), 4)
    fee = FEE_FIXED + np.where((hours >= 6) & (hours < 22), 0.25, 0.0)
    truth = np.repeat(spot, 4) + fee
    ratio = float(np.median(prices / truth))
    fee_step = 0.25
    share = fee_step / float(prices.max() - prices.min())
    true_share = fee_step / float(truth.max() - truth.min())
    return ratio, share, true_share


def export_ratio(unit):
    """Second seam: Coordinator._pv_export_price reading a spot-linked export
    price sensor (0.45 SEK/kWh true) published in ``unit``."""
    s = SCALE[unit]
    cfg = {"price_source": "tibber", "tibber_token": "x",
           "weather_entity": "weather.home", "indoor_temp_entity": "sensor.indoor",
           "outdoor_temp_entity": "sensor.outdoor", "pv_enabled": True,
           "pv_export_price_entity": "sensor.export"}
    st = FakeState(str(0.45 * s), unit=unit)
    coord = HeatPumpOptimizerCoordinator(FakeHass({"sensor.export": st}),
                                         FakeEntry(data=cfg))
    return coord._pv_export_price() / 0.45


for unit in SCALE:
    tag = unit.replace("/", "_per_").replace("ö", "o")
    print(f"RESULT export_ratio_{tag}={export_ratio(unit):.4f} ratio")
    r, sh, tsh = run(unit)
    print(f"RESULT ratio_{tag}={r:.4f} ratio")
    print(f"RESULT fee_share_of_spread_{tag}={sh:.5f} ratio (true {tsh:.5f})")

pc_, tc_ = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc_ / max(tc_, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
print(f"RESULT swapins={sw}")
