#!/usr/bin/env python3
"""Leads seat L2, round 9 (D12-s1 cell): the wood-vs-pump comparison on a non-SEK install.

METRIC (one line): over 6 currency scale factors k (SEK=1, EUR~1/11.3, NOK~0.98, DKK~0.65,
  USD~1/10.5, x100), the number of factors for which heatpump_optimizer.wood_fuel.
  build_wood_fuel_view -- the view the Wood Cheaper binary sensor and Wood-Burn Night Advisor
  publish -- changes its `cheaper_hour_count` when BOTH the spot prices and the wood price are
  expressed in that currency (k x the SEK numbers). 0 means the comparison is currency-agnostic:
  it is right in any currency as long as the wood price is typed in the instance currency.
  Also printed: the count when a EUR install types the wood price in SEK, as the form's
  'SEK/m3' unit asks (D4-s2-02), and the published keys that name SEK.
KEY: `cheaper_hour_count` returned by the production view, 96 x 15-min steps.
RUN (export root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D12/leads/l2_wood_currency.py
PERTURBATION: --perturb convert  wood_fuel.wood_sek_per_kwh treats the typed wood price as SEK
  and converts it into the arm's currency (x k), i.e. the key's SEK taken literally
  -> factors_changing_count goes UP (every k != 1 arm moves).
EXPECTED at 1936d5ca72a06556eeed4e8e5bf3dea520e517e1: factors_changing_count=0; exact.
MACHINE: leads box, 4-core Linux container. Pure function; no temp files.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time
from datetime import datetime, timedelta, timezone
sys.path[:0] = ["tests", "tests/hastub", "custom_components"]
from heatpump_optimizer import wood_fuel  # noqa: E402
from heatpump_optimizer import const  # noqa: E402

P0, T0 = time.process_time(), time.thread_time()
CUR_K = [1.0]
if "--perturb" in sys.argv and "convert" in sys.argv:
    _orig = wood_fuel.wood_sek_per_kwh
    wood_fuel.wood_sek_per_kwh = lambda p, t, k, e: _orig(p, t, k, e) * CUR_K[0]

CFG = {
    const.CONF_WOOD_FURNACE_ENABLED: True,
    const.CONF_WOOD_TANK_TOP_ENTITY: "sensor.wood_top",
    const.CONF_EXTERNAL_HEAT_ENABLED: True,
    const.CONF_WOOD_TYPE: "birch",
    const.CONF_WOOD_PACKING: next(iter(wood_fuel.WOOD_KWH_M3["birch"])),
    const.CONF_WOOD_FURNACE_EFFICIENCY: 75.0,
}
WOOD_SEK_M3 = 900.0
N = 96
t0 = datetime(2026, 1, 15, 0, 0, tzinfo=timezone.utc)
stamps = [t0 + timedelta(minutes=15 * i) for i in range(N)]
prices_sek = [0.6 + 2.4 * ((i // 4) % 24) / 23.0 for i in range(N)]  # 0.6..3.0 SEK/kWh
outdoor = [-5.0 + 4.0 * ((i // 4) % 24) / 23.0 for i in range(N)]
space = [3.0] * N
dhw = [0.0] * N


def count(prices, wood_price):
    view = wood_fuel.build_wood_fuel_view(
        {**CFG, const.CONF_WOOD_PRICE_SEK_M3: wood_price}, prices=prices, outdoor=outdoor,
        space_kw=space, dhw_kw=dhw, cop_at=lambda t: 2.5 + 0.05 * t, timestamps=stamps,
        forecast_kw=[], suppressing=False)
    return view["cheaper_hour_count"], view


base, view = count(prices_sek, WOOD_SEK_M3)
print(f"# SEK install: wood {WOOD_SEK_M3} SEK/m3 -> {view['sek_per_kwh']:.4f}/kWh, cheaper steps {base}")
changing = 0
for label, k in (("SEK", 1.0), ("EUR", 1 / 11.3), ("NOK", 0.98), ("DKK", 0.65),
                 ("USD", 1 / 10.5), ("x100", 100.0)):
    CUR_K[0] = k
    c, _ = count([p * k for p in prices_sek], WOOD_SEK_M3 * k)
    CUR_K[0] = 1.0
    print(f"# {label}: prices and wood price both x{k:.4f} -> cheaper steps {c}")
    changing += c != base
print(f"RESULT factors_changing_count={changing} count")
CUR_K[0] = 1 / 11.3
eur_label, _ = count([p / 11.3 for p in prices_sek], WOOD_SEK_M3)
CUR_K[0] = 1.0
print(f"RESULT eur_install_wood_typed_in_sek_cheaper_steps={eur_label} count (vs {base} typed in EUR)")
print(f"RESULT published_keys_naming_sek={sorted(k for k in view if 'sek' in k)}")
_p, _t = time.process_time() - P0, time.thread_time() - T0
print(f"RESULT thread_factor={(_p / _t) if _t > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")]
    print(f"RESULT swapins={_sw[0].split()[1] if _sw else 0}")
except OSError:
    print("RESULT swapins=na")
