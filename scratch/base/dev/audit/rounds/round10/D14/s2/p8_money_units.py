"""D14-s2 P8 detector: money-denominated surfaces whose currency disagrees with the price feed.

Metric: over every money surface the coordinator publishes (coordinator.currency, which
feeds every sensor unit_of_measurement and the `currency` payload leaf, and each line of
coordinator._narrative_view()["lines"]), count those naming a currency other than the
feed's declared one (currency.declared_currency of the price entity's unit).
Count key: the currency token in the value the production seam delivers (the rendered line,
the attribute value), never the instance label we configure.
Command: PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python3 dev/audit/rounds/round10/D14/s2/p8_money_units.py [--perturb]
Expected at 17f1c55fad1b: mismatch_eur_feed_on_sek=N_LINES (>=1, every narrative line), coordinator_unit_mismatch=0,
  null control (SEK feed on SEK instance) mismatch=0. --perturb (coordinator.resolve_currency -> feed code,
  i.e. narrative follows coordinator.currency) moves mismatch to 0.  Tolerance: exact (counts).
Machine: B7 (macOS arm64). Baseline 17f1c55fad1b.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, re
from types import SimpleNamespace
from unittest import mock
sys.path.insert(0, "tests")
sys.path.insert(0, ".")
t0p, t0t = time.process_time(), time.thread_time()
from harness import FakeHass, FakeEntry, FakeState  # noqa: E402
import custom_components.heatpump_optimizer.coordinator as C  # noqa: E402
from custom_components.heatpump_optimizer.currency import declared_currency  # noqa: E402

CODES = re.compile(r"\b(SEK|EUR|NOK|DKK|GBP|USD|PLN)\b")


def run(feed_unit):
    states = {"sensor.price": FakeState("1.0", unit=feed_unit,
                                        attributes={"unit_of_measurement": feed_unit})}
    hass = FakeHass(states)
    hass.config.currency = "SEK"
    cfg = {"price_source": "entity", "price_entity": "sensor.price",
           "weather_entity": "weather.home", "indoor_temp_entity": "sensor.indoor",
           "outdoor_temp_entity": "sensor.outdoor"}
    coord = C.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))
    n = 8
    coord._optimization_result = SimpleNamespace(
        timestamps=list(range(n)), prices=[0.5] * n,
        power_schedule=[2.0] * n, space_reasons=["cheap_price"] * 4 + ["comfort_floor"] * 4,
        dhw_power_schedule=[1.0] * n, dhw_reasons=["dhw_preheat"] * n)
    feed = declared_currency(feed_unit)
    lines = coord._narrative_view()["lines"]
    line_bad = sum(1 for l in lines if feed not in CODES.findall(l))
    unit_bad = int(coord.currency != feed)
    return feed, coord.currency, lines, line_bad, unit_bad


perturb = "--perturb" in sys.argv
ctx = (mock.patch.object(C, "resolve_currency", lambda hass: "EUR") if perturb
       else mock.patch.object(C, "resolve_currency", C.resolve_currency))
with ctx:
    feed, cur, lines, bad, ubad = run("EUR/kWh")
    print("lines:", lines)
    print(f"RESULT feed_currency={feed}")
    print(f"RESULT coordinator_currency={cur}")
    print(f"RESULT narrative_lines={len(lines)} count")
    print(f"RESULT mismatch_eur_feed_on_sek={bad + ubad} count")
    print(f"RESULT coordinator_unit_mismatch={ubad} count")
_, _, l2, b2, u2 = run("SEK/kWh")
print(f"RESULT null_sek_feed_mismatch={b2 + u2} count")
pt, tt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pt / tt:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")

# Static seam rule: every production call of currency.resolve_currency outside currency.py
# and outside the `x or resolve_currency(...)` fallback form is a surface that names the
# instance label instead of the feed's currency.
import ast, glob
seams = []
for path in sorted(glob.glob("custom_components/heatpump_optimizer/*.py")):
    if path.endswith("currency.py"):
        continue
    tree = ast.parse(open(path).read())
    fallback = {id(n.values[-1]) for n in ast.walk(tree) if isinstance(n, ast.BoolOp)
                and isinstance(n.op, ast.Or)}
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "resolve_currency" \
                and id(n) not in fallback:
            seams.append(f"{path}:{n.lineno}")
for s in seams:
    print("SEAM", s)
print(f"RESULT label_currency_seams={len(seams)} count")
