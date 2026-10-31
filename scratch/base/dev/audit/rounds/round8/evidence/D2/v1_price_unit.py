"""D2-v1 (verifier) harness for D2-s2-02: unit-blind entity prices, parse seam and plan consequence.

Metric (one line): (a) parse seam: price_model.prices_from_entity_state row 'total' / true SEK/kWh,
median over 24 rows, for a HACS-Nord-Pool-style state in SEK/kWh, öre/kWh, SEK/MWh (with the
configured surcharge 0.10 SEK/kWh, so the additive term is exposed too); (b) plan consequence:
HeatPumpOptimizer.optimize on golden.make(winter_cold) with the price series scaled x100 vs x1 --
compressor_starts, room-temperature degree-hours below min_temp, energy kWh, and the plan's
predicted_cost ratio.
Differs from the finder's metric (coordinator _price_series ratio): (a) reads the lower seam
directly; (b) measures what the solver does with the mis-scaled price, not the price itself.
Instrumented: price_model.prices_from_entity_state; optimizer.HeatPumpOptimizer.optimize.
Perturbation: the unit attribute (SEK/kWh -> öre/kWh -> SEK/MWh) with the same true price.
Null: SEK/kWh arm (ratio 1, plan identical by construction: x1).

Command: OMP_NUM_THREADS=1 ... PYTHONPATH=tests/hastub python3 tools/audit/round8/D2/v1_price_unit.py
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; 4-vCPU shared cloud container.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
sys.path.insert(0, ".")
sys.path.insert(0, "tests")
import numpy as np  # noqa: E402
import golden  # noqa: E402
from harness import FakeState  # noqa: E402
from heatpump_optimizer import price_model as PM  # noqa: E402

TZ = ZoneInfo("Europe/Stockholm")
SCALE = {"SEK/kWh": 1.0, "öre/kWh": 100.0, "SEK/MWh": 1000.0}
SURCHARGE = 0.10


def parse_ratio(unit):
    rng = np.random.default_rng(7)
    spot = rng.uniform(0.2, 2.0, 24)
    t0 = datetime(2026, 11, 3, tzinfo=TZ)
    s = SCALE[unit]
    raw = [{"start": (t0 + timedelta(hours=h)).isoformat(), "end": (t0 + timedelta(hours=h + 1)).isoformat(),
            "value": float(spot[h] * s)} for h in range(24)]
    st = FakeState(str(spot[0] * s), unit=unit, attributes={"raw_today": raw, "raw_tomorrow": [],
                                                            "unit_of_measurement": unit})
    rows = PM.prices_from_entity_state(st, 1.0, SURCHARGE)
    tot = np.array([r["total"] for r in rows], dtype=float)
    return float(np.median(tot / (spot + SURCHARGE)))


def plan(scale, fee=False, weather="winter_cold"):
    b = golden.make(dhw=True, weather_profile=weather, price_profile="winter_typical")
    opt = b["optimizer"]
    prices = np.asarray(b["prices"], dtype=float) * scale
    if fee:  # a SEK/kWh day/night grid-fee step folded AFTER the (mis-scaled) spot, as the coordinator does
        hrs = (golden.START.hour + np.arange(prices.size) * 0.25) % 24
        prices = prices + 0.05 + np.where((hrs >= 6) & (hrs < 22), 0.25, 0.0)
    res = opt.optimize(b["state"], prices, b["outdoor"], b["wind"], b["rain"], b["solar"], golden.START)
    room = np.asarray(res.room_temp_trajectory, dtype=float)
    lo = float(opt.config.min_temp)
    dh = float(np.sum(np.clip(lo - room, 0, None)) * 0.25)
    kwh = float((np.sum(res.power_schedule) + np.sum(res.dhw_power_schedule or [0])) * 0.25)
    return res.compressor_starts, dh, kwh, float(res.predicted_cost), float(room.min())


def main():
    t0 = time.process_time(); th0 = time.thread_time()
    for u in SCALE:
        tag = u.replace("/", "_per_").replace("ö", "o")
        print(f"RESULT parse_ratio_{tag}={parse_ratio(u):.4f} ratio")
    s1, d1, k1, c1, m1 = plan(1.0)
    s100, d100, k100, c100, m100 = plan(100.0)
    print(f"# x1:   starts={s1} below_min_Kh={d1:.4f} kWh={k1:.3f} cost={c1:.3f} room_min={m1:.3f}")
    print(f"# x100: starts={s100} below_min_Kh={d100:.4f} kWh={k100:.3f} cost={c100:.3f} room_min={m100:.3f}")
    print(f"RESULT plan_starts_x1={s1} count")
    print(f"RESULT plan_starts_x100={s100} count")
    print(f"RESULT plan_below_min_Kh_x1={d1:.4f} Kh")
    print(f"RESULT plan_below_min_Kh_x100={d100:.4f} Kh")
    print(f"RESULT plan_room_min_x1={m1:.3f} C")
    print(f"RESULT plan_room_min_x100={m100:.3f} C")
    print(f"RESULT plan_kwh_x1={k1:.3f} kWh")
    print(f"RESULT plan_kwh_x100={k100:.3f} kWh")
    print(f"RESULT published_cost_ratio={c100 / c1:.3f} ratio")
    f1 = plan(1.0, fee=True)
    f100 = plan(100.0, fee=True)
    print(f"# fee x1:   {f1}")
    print(f"# fee x100: {f100}")
    print(f"RESULT fee_plan_starts_x1={f1[0]} count")
    print(f"RESULT fee_plan_starts_x100={f100[0]} count")
    print(f"RESULT fee_plan_kwh_delta={f100[2] - f1[2]:.3f} kWh")
    print(f"RESULT fee_plan_below_min_Kh_delta={f100[1] - f1[1]:.4f} Kh")
    for w in ("winter_mild", "shoulder"):
        a = plan(1.0, fee=True, weather=w)
        z = plan(100.0, fee=True, weather=w)
        print(f"# {w} fee x1: {a}")
        print(f"# {w} fee x100: {z}")
        print(f"RESULT {w}_fee_starts_x1={a[0]} count")
        print(f"RESULT {w}_fee_starts_x100={z[0]} count")
        print(f"RESULT {w}_fee_kwh_delta={z[2] - a[2]:.3f} kWh")
        print(f"RESULT {w}_fee_below_min_Kh_delta={z[1] - a[1]:.4f} Kh")
    a = plan(1.0, weather="winter_mild"); z = plan(100.0, weather="winter_mild")
    print(f"RESULT winter_mild_nofee_kwh_delta={z[2] - a[2]:.3f} kWh (pure x100 scale, no SEK additive term)")
    pc = time.process_time() - t0; tc = time.thread_time() - th0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
    except Exception:
        sw = 'n/a'
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
