S = "custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator."

# ---------------- 466c95cb8978ea1d
write("466c95cb8978ea1d",
  "WARNING-or-higher log records and valve write attempts from one _command_valve_target() call in smart_write mode with NO valve write entity configured (the option left unset: None, or saved empty: ''). Count keyed on the records the coordinator's loggers emit.",
  ["RESULT warnings_baseline=0 count", "RESULT warnings_mutant=1 count  (per unset form: None and '')",
   "RESULT warnings_delta=2 count  (summed over the two unset forms)", "RESULT commanded_delta=0 count",
   "RESULT null_warnings_delta=0 count  (a configured number entity: both arms write 23.0 once, warn nothing)"],
  S + "_command_valve_target (coordinator.py:7733 `if not entity_id:`)",
  "`        if not entity_id:` -> `        if False:`. Direction: warnings 0 -> 1 per call (the write is attempted on a None/'' entity, fails inside _valve_write_problem and is latched as a WARNING 'Valve write entity None could not be commanded').",
  "mixing_valve_write_entity='number.valve' present in hass: the guard is not taken on either arm.",
  r'''
import logging
NAME, OLD, NEW = "_command_valve_target", "if not entity_id:", "if False:"


class Count(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING)
        self.n = 0

    def emit(self, record):
        self.n += 1


def run(entity):
    extra = {"mixing_valve_mode": "smart_write"}
    if entity is not None:
        extra["mixing_valve_write_entity"] = entity
    c = coord({"number.valve": FakeState("40", unit="°C")}, **extra)
    h = Count()
    root = logging.getLogger("custom_components.heatpump_optimizer")
    root.addHandler(h)
    try:
        asyncio.run(c._command_valve_target())
    finally:
        root.removeHandler(h)
    return h.n, c._valve_commanded_target, len(c.hass.services.calls)


logging.getLogger("custom_components.heatpump_optimizer").setLevel(logging.DEBUG)
logging.getLogger("custom_components.heatpump_optimizer").propagate = False
res = {e: both(NAME, OLD, NEW, lambda e=e: run(e)) for e in (None, "", "number.valve")}
for e in (None, ""):
    print(f"RESULT inputs[{e!r}] baseline={res[e][0]} mutant={res[e][1]}")
print(f"RESULT warnings_baseline={res[None][0][0]} count")
print(f"RESULT warnings_mutant={res[None][1][0]} count")
print(f"RESULT warnings_delta={sum(res[e][1][0] - res[e][0][0] for e in (None, ''))} count")
print(f"RESULT commanded_delta={sum(int(res[e][1][1:] != res[e][0][1:]) for e in (None, ''))} count")
nb, nm = res["number.valve"]
print(f"RESULT null_warnings_delta={nm[0] - nb[0]} count")
print(f"RESULT null_commanded={nb[1]},{nm[1]}")
tail()
''')

# ---------------- confidence margins shared
CM = r'''
import numpy as np


def cm(mae, sigma, n=4):
    """_confidence_margins(n) with the tracker's temperature MAE fixed (trust() runs for real) and one
    0.25 h lead bucket of the given sigma (sigma() runs for real)."""
    c = coord(confidence_margins_enabled=True)
    acc = c._accuracy
    acc.lead_sigma = {0.25: sigma}
    acc.lead_counts = {0.25: 5}
    with mock.patch.object(type(acc), "temperature_mae", lambda self: mae):
        r = c._confidence_margins(n)
    return None if r is None else [float(x) for x in r]


def show(v):
    return "None" if v is None else f"array[{len(v)}] max={max(v):.6g}"
'''
write("a7dd3153718e531b",
  "Whether _confidence_margins(4) returns None (the byte-inert 'no margin') or an array, when the damping 1 - trust() lies in (0, 1e-9] and a lead bucket's sigma exceeds 1 C. Count = inputs whose None/array outcome differs between arms.",
  ["RESULT outcome_baseline=None", "RESULT outcome_mutant=array[4] max=2e-09  (sigma 2 C, mae 0.25+1.75e-9 -> damp 9.9999997e-10)",
   "RESULT differing_inputs=2 count  (sigma 2 and 5 C at that mae)", "RESULT null_differing=0 count  (damp exactly 0: mae 0.25 and 0.1; damp 0.5)"],
  S + "_confidence_margins (coordinator.py:9153 `if damp <= 1e-9:`), driven through the real AccuracyTracker.trust()/sigma()",
  "`        if damp <= 1e-9:` -> `        if False:`. Direction: None -> an array of sigma*damp (~2e-9 C) on the damp window (0, 1e-9] with sigma > 1 C.",
  "damp == 0 exactly (trust clipped to 1) and damp = 0.5: both arms agree (None from the final any(>1e-9) test, or the same array).",
  CM + r'''
NAME, OLD, NEW = "_confidence_margins", "if damp <= 1e-9:", "if False:"
tiny = 0.25 + 1.75e-9
cells = [(tiny, 2.0), (tiny, 5.0), (tiny, 0.5), (tiny, 1.0)]
nulls = [(0.25, 2.0), (0.1, 5.0), (1.125, 2.0)]
diff = 0
for mae, sig in cells:
    b, m = both(NAME, OLD, NEW, lambda: cm(mae, sig))
    diff += int((b is None) != (m is None))
    print(f"RESULT input mae={mae!r} sigma={sig}: baseline={show(b)} mutant={show(m)}")
nd = 0
for mae, sig in nulls:
    b, m = both(NAME, OLD, NEW, lambda: cm(mae, sig))
    nd += int(b != m)
b, m = both(NAME, OLD, NEW, lambda: cm(tiny, 2.0))
print(f"RESULT outcome_baseline={show(b)}")
print(f"RESULT outcome_mutant={show(m)}")
print(f"RESULT differing_inputs={diff} count")
print(f"RESULT null_differing={nd} count")
tail()
''')

write("b6b6e82fb4a33703",
  "Count of damping values 1 - trust() reachable through AccuracyTracker.trust() (any temperature MAE) that equal 1e-9 exactly -- the only input where `<=` and `<` differ -- plus the None/array outcome on the nearest reachable damps, both arms.",
  ["RESULT exact_tie_reachable=0 count  (1 - t for a float t near 1 moves in steps of 2**-53 ~ 1.1e-16; 1e-9 is not on that grid)",
   "RESULT differing_inputs=0 count  (the 2001 trust values bracketing 1 - 1e-9, sigma 2 and 5 C)",
   "RESULT forced_tie_differs=1 count  (trust() patched to return a value with 1 - t == 1e-9 does not exist; damp forced by patching numpy-free arithmetic is not reachable, recorded as the unreachable input)"],
  S + "_confidence_margins (coordinator.py:9153 `if damp <= 1e-9:`)",
  "`        if damp <= 1e-9:` -> `        if damp < 1e-9:`. Direction: at damp == 1e-9 exactly the mutant computes margins instead of returning None.",
  "the same scan with the unmutated method: differing count 0 by construction.",
  CM + r'''
import math
NAME, OLD, NEW = "_confidence_margins", "if damp <= 1e-9:", "if damp < 1e-9:"
# every float trust value within 1000 ulps of 1 - 1e-9: does 1.0 - t ever equal 1e-9?
t0 = 1.0 - 1e-9
ts = [t0]
for d in (1, -1):
    t = t0
    for _ in range(1000):
        t = math.nextafter(t, d * math.inf)
        ts.append(t)
exact = sum(1 for t in ts if 1.0 - t == 1e-9)
print(f"RESULT nearest_damp_above={min(1.0 - t for t in ts if 1.0 - t > 1e-9)!r}")
print(f"RESULT nearest_damp_below={max(1.0 - t for t in ts if 1.0 - t < 1e-9)!r}")


def cm_trust(t, sigma):
    c = coord(confidence_margins_enabled=True)
    acc = c._accuracy
    acc.lead_sigma = {0.25: sigma}
    acc.lead_counts = {0.25: 5}
    with mock.patch.object(type(acc), "trust", lambda self: t):
        r = c._confidence_margins(4)
    return None if r is None else [float(x) for x in r]


diff = 0
step = max(1, len(ts) // 2001)
for t in ts[::step]:
    for sig in (2.0, 5.0):
        b, m = both(NAME, OLD, NEW, lambda: cm_trust(t, sig))
        diff += int(b != m)
# through the MAE as well: trust = clip(1 - (mae - 0.25)/1.75): scan mae around 0.25 + 1.75e-9
maes = [0.25 + 1.75e-9]
for d in (1, -1):
    x = maes[0]
    for _ in range(200):
        x = math.nextafter(x, d * math.inf)
        maes.append(x)
mdiff = sum(int(both(NAME, OLD, NEW, lambda: cm(mae, 2.0))[0] != both(NAME, OLD, NEW, lambda: cm(mae, 2.0))[1]) for mae in maes)
print(f"RESULT trust_values_scanned={len(ts[::step])} count")
print(f"RESULT mae_values_scanned={len(maes)} count")
print(f"RESULT exact_tie_reachable={exact} count")
print(f"RESULT differing_inputs={diff + mdiff} count")
tail()
''')

write("10ba5036744c9a99",
  "Max |difference| of _confidence_margins(n) between arms over the step lengths production can hand it (OptimizationConfig.time_step_minutes, never assigned outside its 15.0 default), and over sub-minute steps fed in directly.",
  ["RESULT production_step_minutes=15.0", "RESULT max_abs_delta_production=0.0 C  (15 >= 1: max() is the identity)",
   "RESULT max_abs_delta_subminute>0 C  (separates only on a sub-minute step, which nothing in production sets)",
   "RESULT null_max_abs_delta=0.0 C (step 5, 15, 60)"],
  S + "_confidence_margins (coordinator.py:9155 `dt_h = max(ctx._opt_config.time_step_minutes, 1.0) / 60.0`)",
  "`max(time_step_minutes, 1.0)` -> `(time_step_minutes)`. Direction: identical for steps >= 1 min; a sub-minute step shortens every lead.",
  "steps of 5, 15 and 60 minutes: identical by construction of max().",
  CM + r'''
import dataclasses
NAME = "_confidence_margins"
OLD = "dt_h = max(ctx._opt_config.time_step_minutes, 1.0) / 60.0"
NEW = "dt_h = (ctx._opt_config.time_step_minutes) / 60.0"


def cm_step(step):
    c = coord(confidence_margins_enabled=True)
    acc = c._accuracy
    acc.lead_sigma = {0.01: 0.3, 0.1: 0.6}
    acc.lead_counts = {0.01: 5, 0.1: 5}
    # the context is a frozen dataclass: swap in a copy of its OptimizationConfig with this step
    object.__setattr__(c._ctx, "_opt_config", dataclasses.replace(c._ctx._opt_config, time_step_minutes=step))
    with mock.patch.object(type(acc), "temperature_mae", lambda self: 1.125):
        r = c._confidence_margins(8)
    return None if r is None else [float(x) for x in r]


def delta(step):
    b, m = both(NAME, OLD, NEW, lambda: cm_step(step))
    if b is None or m is None or isinstance(b, str) or isinstance(m, str):
        return 0.0 if b == m else float("inf")
    return max(abs(x - y) for x, y in zip(b, m))


prod = coord()._ctx._opt_config.time_step_minutes
print(f"RESULT production_step_minutes={prod}")
print(f"RESULT max_abs_delta_production={delta(prod)} C")
sub = {s: delta(s) for s in (0.0, 0.25, 0.5, 0.999)}
for s, d in sub.items():
    print(f"RESULT input step={s} delta={d}")
print(f"RESULT max_abs_delta_subminute={max(sub.values())} C")
print(f"RESULT null_max_abs_delta={max(delta(s) for s in (5.0, 15.0, 60.0))} C")
tail()
''', extra="Reachability: grep shows no assignment of time_step_minutes outside optimizer.py:2667's dataclass default (15.0); no config key sets it.")

write("7457d714cd44306c",
  "Whether _confidence_margins(4) returns None or an array when every margin equals 1e-9 exactly (sigma*damp == 1e-9: sigma 2e-9 C at damp 0.5, mae 1.125). Count = inputs whose None/array outcome differs.",
  ["RESULT outcome_baseline=None", "RESULT outcome_mutant=array[4] max=1e-09",
   "RESULT differing_inputs=2 count  (sigma 2e-9 at damp 0.5, mae 1.125; sigma 4e-9 at damp 0.25, mae 0.6875)", "RESULT null_differing=0 count (sigma 1e-8 and 1e-10)"],
  S + "_confidence_margins (coordinator.py:9166 `return margins if bool(np.any(margins > 1e-9)) else None`)",
  "`margins > 1e-9` -> `margins >= 1e-9`. Direction: None -> array of 1e-9 C at the exact tie.",
  "sigma 1e-8 (array on both arms) and 1e-10 (None on both).",
  CM + r'''
NAME = "_confidence_margins"
OLD = "return margins if bool(np.any(margins > 1e-9)) else None"
NEW = "return margins if bool(np.any(margins >= 1e-9)) else None"
cells = [(1.125, 2e-9), (0.6875, 4e-9)]
diff = 0
for mae, sig in cells:
    b, m = both(NAME, OLD, NEW, lambda: cm(mae, sig))
    diff += int((b is None) != (m is None))
    print(f"RESULT input mae={mae} sigma={sig}: baseline={show(b)} mutant={show(m)}")
nd = sum(int(x[0] != x[1]) for x in (both(NAME, OLD, NEW, lambda s=s: cm(1.125, s)) for s in (1e-8, 1e-10)))
b, m = both(NAME, OLD, NEW, lambda: cm(1.125, 2e-9))
print(f"RESULT outcome_baseline={show(b)}")
print(f"RESULT outcome_mutant={show(m)}")
print(f"RESULT differing_inputs={diff} count")
print(f"RESULT null_differing={nd} count")
tail()
''')

CC = r'''
def cc(kwh=10.0, sek=12.0, fee=3.0, mean=1.5, fixed=None):
    """_contract_comparison() over a ledger with this month's spot line, grid-fee line and spot mean."""
    c = coord(**({"contract_fixed_price": fixed} if fixed is not None else {}))
    now = co.dt_util.now()
    if kwh or sek:
        c._ledger.add(now, "spot", kwh=kwh, sek=sek)
    if fee:
        c._ledger.add(now, "grid_fee", kwh=kwh, sek=fee)
    if mean is not None:
        c._ledger.observe_meta_mean(now, "spot_price", mean)
    return c._contract_comparison()
'''
write("6aeb83e5435c9cac",
  "The published grid_fee_sek key of _contract_comparison() on a month whose ledger carries a 3.00 SEK grid-fee line (10 kWh, 12 SEK spot, mean spot 1.5).",
  ["RESULT grid_fee_sek_baseline=3.0", "RESULT grid_fee_sek_mutant=absent", "RESULT keys_lost=1 count",
   "RESULT null_delta=0 count  (no grid-fee line: both arms omit the key)"],
  S + "_contract_comparison (coordinator.py:10428 `if fee_line[\"sek\"]:`)",
  "`        if fee_line[\"sek\"]:` -> `        if False:`. Direction: grid_fee_sek 3.0 -> absent (the contract comparison never carries the grid fee).",
  "a month with no grid-fee line (fee 0): both arms omit grid_fee_sek.",
  CC + r'''
NAME, OLD, NEW = "_contract_comparison", 'if fee_line["sek"]:', "if False:"
b, m = both(NAME, OLD, NEW, cc)
print(f"RESULT baseline={b}")
print(f"RESULT mutant={m}")
print(f"RESULT grid_fee_sek_baseline={b.get('grid_fee_sek', 'absent')}")
print(f"RESULT grid_fee_sek_mutant={m.get('grid_fee_sek', 'absent')}")
print(f"RESULT keys_lost={len(set(b) - set(m))} count")
nb, nm = both(NAME, OLD, NEW, lambda: cc(fee=0.0))
print(f"RESULT null_delta={int(nb != nm)} count")
tail()
''')

write("d06a2d8e53342785",
  "The monthly-average-spot keys of _contract_comparison() (monthly_avg_spot_sek, load_profile_value_per_kwh) and its 'cheapest' verdict, on a month of 10 kWh at 12 SEK hourly spot, mean spot 1.5 and 1.0 (when monthly average is the cheapest contract).",
  ["RESULT monthly_avg_spot_sek_baseline=15.0", "RESULT monthly_avg_spot_sek_mutant=absent",
   "RESULT keys_lost=3 count  (monthly_avg_spot_sek, load_profile_value_per_kwh, and cheapest: hourly spot alone leaves one contract)",
   "RESULT cheapest_baseline=monthly_avg_spot  (mean 1.0, fixed 1.4)", "RESULT cheapest_mutant=hourly_spot",
   "RESULT null_delta=0 count  (no spot mean recorded: both arms omit the keys)"],
  S + "_contract_comparison (coordinator.py:10433 `if kwh > 0 and mean_spot is not None:`)",
  "`if kwh > 0 and mean_spot is not None:` -> `if False:`. Direction: the monthly-average contract disappears from the published comparison and from the cheapest verdict.",
  "a month with no spot-price mean: both arms omit the keys.",
  CC + r'''
NAME, OLD, NEW = "_contract_comparison", "if kwh > 0 and mean_spot is not None:", "if False:"
b, m = both(NAME, OLD, NEW, cc)
print(f"RESULT baseline={b}")
print(f"RESULT mutant={m}")
print(f"RESULT monthly_avg_spot_sek_baseline={b.get('monthly_avg_spot_sek', 'absent')}")
print(f"RESULT monthly_avg_spot_sek_mutant={m.get('monthly_avg_spot_sek', 'absent')}")
print(f"RESULT keys_lost={len(set(b) - set(m))} count")
b2, m2 = both(NAME, OLD, NEW, lambda: cc(mean=1.0, fixed=1.4))
print(f"RESULT cheapest_baseline={b2.get('cheapest')}")
print(f"RESULT cheapest_mutant={m2.get('cheapest')}")
nb, nm = both(NAME, OLD, NEW, lambda: cc(mean=None))
print(f"RESULT null_delta={int(nb != nm)} count")
tail()
''')

write("9789e0e7faa1b53a",
  "Count of ledger inputs on which _contract_comparison() differs between `kwh > 0` and `kwh >= 0` in its cheapest-contract guard. The arms differ only at kwh == 0, where costs holds hourly_spot alone (both other contracts need kwh > 0), so len(costs) > 1 is false on both.",
  ["RESULT differing_inputs=0 count over 8 inputs (kwh 0 with/without spot cost, mean, fixed price, fee; kwh -1; kwh nan; kwh 1e-12)",
   "RESULT null_delta=0 count (kwh 10, mean and fixed: both arms carry cheapest)"],
  S + "_contract_comparison (coordinator.py:10445 `if kwh > 0 and len(costs) > 1:`)",
  "`kwh > 0` -> `kwh >= 0`. Direction: none on any input: at kwh == 0 the costs dict has one entry.",
  "kwh 10 with a mean and a fixed price: both arms publish cheapest.",
  CC + r'''
NAME, OLD, NEW = "_contract_comparison", "if kwh > 0 and len(costs) > 1:", "if kwh >= 0 and len(costs) > 1:"
inputs = [dict(kwh=0.0, sek=0.0, fixed=1.0), dict(kwh=0.0, sek=5.0, fixed=1.0), dict(kwh=0.0, sek=0.0, mean=1.0, fixed=2.0),
          dict(kwh=0.0, sek=-3.0, mean=0.5, fixed=0.7, fee=0.0), dict(kwh=-1.0, sek=1.0, fixed=1.0),
          dict(kwh=float("nan"), sek=1.0, fixed=1.0), dict(kwh=1e-12, sek=0.0, fixed=1.0), dict(kwh=0.0, sek=0.0, mean=None)]
diff = 0
for a in inputs:
    b, m = both(NAME, OLD, NEW, lambda a=a: cc(**a))
    d = int(repr(b) != repr(m))
    diff += d
    print(f"RESULT input {a}: differs={d}")
print(f"RESULT differing_inputs={diff} count")
nb, nm = both(NAME, OLD, NEW, lambda: cc(mean=1.0, fixed=1.4))
print(f"RESULT null_delta={int(nb != nm)} count")
tail()
''')

write("8b4f4adbf55981bc",
  "Count of reachable _weather_forecast values on which _current_humidity() differs between arms. The attribute is a list from __init__ (coordinator.py:3725) and is only ever assigned a non-empty list (7076) or a fabricated one (7111); the arms differ only on a non-iterable (None), which raises under the mutant.",
  ["RESULT init_type=list", "RESULT differing_reachable=0 count  ([], [{}], [{'humidity': None}], [{'humidity': 80}], a timestamped list)",
   "RESULT differing_unreachable=1 count  (None: baseline None, mutant raises TypeError)"],
  S + "_current_humidity (coordinator.py:9931 `if not self._weather_forecast:`)",
  "`if not self._weather_forecast:` -> `if False:`. Direction: on [] the loop runs zero times and best stays None: same None; only None raises.",
  "a forecast with humidity 80: both arms 80.0.",
  r'''
NAME, OLD, NEW = "_current_humidity", "if not self._weather_forecast:", "if False:"
c0 = coord()
print(f"RESULT init_type={type(c0._weather_forecast).__name__}")
now = co.dt_util.now()
reach = [[], [{}], [{"humidity": None}], [{"humidity": 80}],
         [{"datetime": now.isoformat(), "humidity": 55}, {"datetime": now.replace(year=now.year + 1).isoformat(), "humidity": 90}]]


def hum(fc):
    c = coord()
    c._weather_forecast = fc
    return c._current_humidity()


diff = 0
for fc in reach:
    b, m = both(NAME, OLD, NEW, lambda fc=fc: hum(fc))
    diff += int(b != m)
    print(f"RESULT input {fc!r}: baseline={b} mutant={m}")
ub, um = both(NAME, OLD, NEW, lambda: hum(None))
print(f"RESULT input None: baseline={ub} mutant={um}")
print(f"RESULT differing_reachable={diff} count")
print(f"RESULT differing_unreachable={int(ub != um)} count")
tail()
''')

MW = r'''
from custom_components.heatpump_optimizer import config_flow as cf


def mw(inlet=None, flow=None, tank=55.0):
    """_dhw_mixed_water() on a DHW entry; ``inlet`` sets the coordinator-resolved inlet (dhw_inlet_current)."""
    extra = {"dhw_enabled": True}
    if flow is not None:
        extra["shower_flow_lpm"] = flow
    c = coord(**extra)
    c._ctx._current_state.dhw_temperature = tank
    if inlet is not None:
        c._ctx._thermal_params.dhw_inlet_current = inlet
    return c._dhw_mixed_water()


def field_cfg(key):
    return dict([f for f in cf._OPTION_FIELDS if f.key == key][0].widget.config)


def inlet_reach():
    """The highest inlet production can resolve: the configured mean plus the seasonal amplitude (both
    option maxima), or a live probe, which _dhw_inlet_c refuses above 35 C."""
    cfg_max = field_cfg("dhw_inlet_temp")["max"] + field_cfg("dhw_inlet_seasonal_amplitude")["max"]
    fresh = co.dt_util.utcnow()
    live = {}
    for v in (30.0, 35.0, 35.5, 39.0):
        st = FakeState(str(v), unit="°C")
        for attr in ("last_updated", "last_reported", "last_changed"):
            try:
                setattr(st, attr, fresh)
            except Exception:  # noqa: BLE001
                pass
        live[v] = co._dhw_inlet_c(FakeHass({"sensor.inlet": st}), "sensor.inlet")
    return cfg_max, live
'''
write("c555c1a38da31dde",
  "_dhw_mixed_water()'s litres_40c at an inlet of exactly 39.0 C (40 - inlet == 1.0, the boundary of `< 1.0`), and the highest inlet production can resolve.",
  ["RESULT litres_baseline=3200.0 at inlet 39.0", "RESULT litres_mutant=absent ({})",
   "RESULT inlet_max_reachable=35.0 C  (options: 25 + 8 = 33; live probe refused above 35)",
   "RESULT differing_reachable=0 count", "RESULT null_delta=0 count (inlet 10)"],
  S + "_dhw_mixed_water (coordinator.py:4391 `if 40.0 - inlet < 1.0:`)",
  "`40.0 - inlet < 1.0` -> `40.0 - inlet <= 1.0`. Direction: at inlet 39.0 the mixed-water view is suppressed ({}); identical for every inlet production resolves (<= 35 C).",
  "inlet 10 C (the default): both arms publish the same litres.",
  MW + r'''
NAME, OLD, NEW = "_dhw_mixed_water", "if 40.0 - inlet < 1.0:", "if 40.0 - inlet <= 1.0:"
b, m = both(NAME, OLD, NEW, lambda: mw(inlet=39.0))
print(f"RESULT litres_baseline={b.get('litres_40c', 'absent')} at inlet 39.0")
print(f"RESULT litres_mutant={m.get('litres_40c', 'absent')}")
cfg_max, live = inlet_reach()
print(f"RESULT inlet_options_max={cfg_max} C")
print(f"RESULT live_inlet_accepted={live}")
reach_max = max([cfg_max] + [v for v, r in live.items() if r is not None])
print(f"RESULT inlet_max_reachable={reach_max} C")
grid = [x / 2 for x in range(-10, int(reach_max * 2) + 1)]
diff = sum(int(both(NAME, OLD, NEW, lambda i=i: mw(inlet=i))[0] != both(NAME, OLD, NEW, lambda i=i: mw(inlet=i))[1]) for i in grid)
print(f"RESULT inlets_scanned={len(grid)} (-5.0..{reach_max} step 0.5)")
print(f"RESULT differing_reachable={diff} count")
nb, nm = both(NAME, OLD, NEW, lambda: mw(inlet=10.0))
print(f"RESULT null_delta={int(nb != nm)} count")
tail()
''')

write("ff67ca31aba14e7f",
  "_dhw_mixed_water()'s litres_40c with the `40 - inlet < 1` guard removed, at inlets 39.5 and 40.0 C (span below one kelvin), and over every inlet production can resolve.",
  ["RESULT litres_baseline=absent at inlet 39.5", "RESULT litres_mutant=6200.0 at inlet 39.5; raises ZeroDivisionError at 40.0",
   "RESULT inlet_max_reachable=35.0 C", "RESULT differing_reachable=0 count", "RESULT null_delta=0 count (inlet 10)"],
  S + "_dhw_mixed_water (coordinator.py:4391 `if 40.0 - inlet < 1.0:`)",
  "`if 40.0 - inlet < 1.0:` -> `if False:`. Direction: above 39 C inlet a huge or infinite litres figure instead of {}; identical below.",
  "inlet 10 C: both arms the same litres.",
  MW + r'''
NAME, OLD, NEW = "_dhw_mixed_water", "if 40.0 - inlet < 1.0:", "if False:"
b, m = both(NAME, OLD, NEW, lambda: mw(inlet=39.5))
b40, m40 = both(NAME, OLD, NEW, lambda: mw(inlet=40.0))
print(f"RESULT litres_baseline={b.get('litres_40c', 'absent')} at inlet 39.5")
print(f"RESULT litres_mutant={m.get('litres_40c', 'absent') if isinstance(m, dict) else m} at inlet 39.5; at 40.0: {m40}")
cfg_max, live = inlet_reach()
reach_max = max([cfg_max] + [v for v, r in live.items() if r is not None])
print(f"RESULT live_inlet_accepted={live}")
print(f"RESULT inlet_max_reachable={reach_max} C")
grid = [x / 2 for x in range(-10, int(reach_max * 2) + 1)]
diff = sum(int(both(NAME, OLD, NEW, lambda i=i: mw(inlet=i))[0] != both(NAME, OLD, NEW, lambda i=i: mw(inlet=i))[1]) for i in grid)
print(f"RESULT inlets_scanned={len(grid)}")
print(f"RESULT differing_reachable={diff} count")
nb, nm = both(NAME, OLD, NEW, lambda: mw(inlet=10.0))
print(f"RESULT null_delta={int(nb != nm)} count")
tail()
''')

write("201955bf671ce8aa",
  "_dhw_mixed_water()'s outcome at shower_flow_lpm = 0 (baseline omits shower_minutes; mutant divides by zero), and whether the options flow lets 0 (or anything below 4) be stored.",
  ["RESULT outcome_baseline=no shower_minutes", "RESULT outcome_mutant=raises ZeroDivisionError",
   "RESULT flow_option_min=4", "RESULT flow_values_refused=3 count (0, -1, 3.9 refused by the option's NumberSelector)",
   "RESULT differing_reachable=0 count (flow 4..20)", "RESULT null_delta=0 count (flow 8)"],
  S + "_dhw_mixed_water (coordinator.py:4396 `if flow > 0:`)",
  "`if flow > 0:` -> `if flow >= 0:`. Direction: at flow 0 a ZeroDivisionError instead of an omitted key; identical on 4..20.",
  "flow 8 L/min (the default range): both arms the same.",
  MW + r'''
NAME, OLD, NEW = "_dhw_mixed_water", "if flow > 0:", "if flow >= 0:"
b, m = both(NAME, OLD, NEW, lambda: mw(flow=0.0))
print(f"RESULT outcome_baseline={'shower_minutes present' if 'shower_minutes' in b else 'no shower_minutes'}")
print(f"RESULT outcome_mutant={m if isinstance(m, str) else m}")
w = [f for f in cf._OPTION_FIELDS if f.key == "shower_flow_lpm"][0].widget
print(f"RESULT flow_option_min={field_cfg('shower_flow_lpm')['min']}")
refused = 0
for v in (0, -1, 3.9):
    try:
        w(v)
    except Exception:  # noqa: BLE001
        refused += 1
print(f"RESULT flow_values_refused={refused} count")
grid = [4 + x / 2 for x in range(33)]
diff = sum(int(both(NAME, OLD, NEW, lambda f=f: mw(flow=f))[0] != both(NAME, OLD, NEW, lambda f=f: mw(flow=f))[1]) for f in grid)
print(f"RESULT differing_reachable={diff} count")
nb, nm = both(NAME, OLD, NEW, lambda: mw(flow=8.0))
print(f"RESULT null_delta={int(nb != nm)} count")
tail()
''', extra="Reachability: EntryConfig parses shower_flow_lpm with finite_float alone (entry_config.py:193); the bound is the options flow's (config_flow.py:1811, 4..20).")

SW = r'''
def sweep_coord(dmin=None, zero_draws=True):
    """A DHW entry with a day of 1.0 prices; ``zero_draws`` gives every demand window a learned draw reservoir
    of twenty zero-kWh occurrences (a window the household never draws in: DrawStats._close appends 0.0)."""
    extra = {"dhw_enabled": True}
    if dmin is not None:
        extra.update(dhw_min_temperature=dmin, dhw_setpoint=60.0)
    c = coord(**extra)
    c._prices = [{"total": 1.0, "start": "x"}] * 24
    if zero_draws:
        for lab in co.labels_for(c._ctx._thermal_params.dhw_demand_windows):
            c._dhw_learner.draw_stats.reservoirs[lab] = [0.0] * 20
    return c


def rec(c, kp=None):
    r = c._dhw_setpoint_sweep(kp)
    return r["recommended_setpoint"], r["covers_heaviest_window"], tuple(x["meets_heaviest_window"] for x in r["candidates"])
'''
write("faf822994582adfc",
  "The DHW advisor's recommended_setpoint and per-candidate meets_heaviest_window when the configured tank minimum (dhw_min_temperature) sits above the lowest candidates and every demand window has learned a zero-kWh heaviest draw.",
  ["RESULT recommended_baseline=48 (min 55, zero draws)", "RESULT recommended_mutant=56",
   "RESULT meets_flipped=4 count (48..54 True -> False)", "RESULT differing_cells=2 of 8 (min 50 and 55 with zero draws)",
   "RESULT null_delta=0 count (profile-fallback heaviest 4.97 kWh: every candidate fails on both arms)"],
  S + "_dhw_setpoint_sweep (coordinator.py:4463 `usable_kwh = c_dhw * max(t - params.dhw_min_temp, 0.0)`)",
  "`max(t - dhw_min_temp, 0.0)` dropped. Direction: a candidate below the minimum gets negative usable energy, so it stops meeting a zero heaviest window and the recommendation moves up to the first candidate above the minimum.",
  "the fresh-install heaviest window (profile fallback, 4.97 kWh): nothing meets on either arm, recommendation 60 on both.",
  SW + r'''
NAME = "_dhw_setpoint_sweep"
OLD = "usable_kwh = c_dhw * max(t - params.dhw_min_temp, 0.0)"
NEW = "usable_kwh = c_dhw * (t - params.dhw_min_temp)"
cells = [(d, z) for d in (None, 48.0, 50.0, 55.0) for z in (False, True)]
diff = 0
for d, z in cells:
    b, m = both(NAME, OLD, NEW, lambda d=d, z=z: rec(sweep_coord(d, z)))
    diff += int(b != m)
    print(f"RESULT input min={d} zero_draws={z}: baseline={b} mutant={m}")
b, m = both(NAME, OLD, NEW, lambda: rec(sweep_coord(55.0, True)))
print(f"RESULT recommended_baseline={b[0]}")
print(f"RESULT recommended_mutant={m[0]}")
print(f"RESULT meets_flipped={sum(int(x != y) for x, y in zip(b[2], m[2]))} count")
print(f"RESULT differing_cells={diff} of {len(cells)}")
nb, nm = both(NAME, OLD, NEW, lambda: rec(sweep_coord(55.0, False)))
print(f"RESULT null_delta={int(nb != nm)} count")
tail()
''')

write("feed2751f4116bd1",
  "The DHW advisor's recommended_setpoint when a candidate's usable energy equals the heaviest window exactly: a zero-kWh learned heaviest window and a tank minimum equal to a candidate setpoint (usable 0 == heaviest 0).",
  ["RESULT recommended_baseline=48 (min 48, zero draws)", "RESULT recommended_mutant=50",
   "RESULT differing_cells=3 of 8 (min 48, 50, 55 with zero draws)", "RESULT null_delta=0 count (profile-fallback heaviest: no tie)"],
  S + "_dhw_setpoint_sweep (coordinator.py:4464 `meets = usable_kwh >= heaviest`)",
  "`>=` -> `>`. Direction: at the tie the candidate no longer meets and the recommendation moves up one or more steps.",
  "the fresh-install profile heaviest (4.97 kWh): no candidate ties, both arms recommend 60.",
  SW + r'''
NAME, OLD, NEW = "_dhw_setpoint_sweep", "meets = usable_kwh >= heaviest", "meets = usable_kwh > heaviest"
cells = [(d, z) for d in (None, 48.0, 50.0, 55.0) for z in (False, True)]
diff = 0
for d, z in cells:
    b, m = both(NAME, OLD, NEW, lambda d=d, z=z: rec(sweep_coord(d, z)))
    diff += int(b != m)
    print(f"RESULT input min={d} zero_draws={z}: baseline={b} mutant={m}")
b, m = both(NAME, OLD, NEW, lambda: rec(sweep_coord(48.0, True)))
print(f"RESULT recommended_baseline={b[0]}")
print(f"RESULT recommended_mutant={m[0]}")
print(f"RESULT differing_cells={diff} of {len(cells)}")
nb, nm = both(NAME, OLD, NEW, lambda: rec(sweep_coord(48.0, False)))
print(f"RESULT null_delta={int(nb != nm)} count")
tail()
''')

write("29bad645ca2c2438",
  "The DHW advisor's recommended_setpoint at a cost tie: a recent kWh price at which candidate 50's unrounded cost_per_day equals candidate 48's ROUNDED stored cost (0.05), every window with a zero-kWh learned heaviest draw. Found by scanning the price ulp by ulp from 0.05/K50.",
  ["RESULT tie_price=0.012022669199125837 SEK/kWh (found by the scan; must be found again, +-400 ulps)",
   "RESULT recommended_baseline=48", "RESULT recommended_mutant=50",
   "RESULT null_delta=0 count (kwh price 1.0: no tie)"],
  S + "_dhw_setpoint_sweep (coordinator.py:4471 `if meets and (best is None or cost_day < best[\"cost_per_day\"]):`)",
  "`cost_day < best[\"cost_per_day\"]` -> `<=`. Direction: on the tie the later (hotter) setpoint wins.",
  "kwh price 1.0: costs 3.97..5.10, no tie, both arms recommend 48.",
  SW + r'''
import math
NAME = "_dhw_setpoint_sweep"
OLD = 'if meets and (best is None or cost_day < best["cost_per_day"]):'
NEW = 'if meets and (best is None or cost_day <= best["cost_per_day"]):'
c = sweep_coord(None, True)
BIG = 1e12
K = {x["setpoint"]: x["cost_per_day"] / BIG for x in c._dhw_setpoint_sweep(BIG)["candidates"]}
mfn = mutant(NAME, OLD, NEW)
kp0 = 0.05 / K[50]
hit = None
for direction in (1, -1):
    kp = kp0
    for _ in range(400):
        if c._dhw_setpoint_sweep(kp)["recommended_setpoint"] != mfn(c, kp)["recommended_setpoint"]:
            hit = kp
            break
        kp = math.nextafter(kp, direction * math.inf)
    if hit is not None:
        break
print(f"RESULT tie_price={hit!r} SEK/kWh")
b, m = both(NAME, OLD, NEW, lambda: rec(c, hit))
print(f"RESULT recommended_baseline={b[0]}")
print(f"RESULT recommended_mutant={m[0]}")
nb, nm = both(NAME, OLD, NEW, lambda: rec(c, 1.0))
print(f"RESULT null_delta={int(nb != nm)} count")
tail()
''')

write("640a1a68b6c1eb23",
  "_entity_state(entity_id)'s outcome for an unset entity (None, the EntryConfig default of away_presence_entity, and '') under two states registries: the suite's FakeStates (dict.get) and a registry that follows Home Assistant's StateMachine.get contract (`_states_data.get(entity_id) or _states_data.get(entity_id.lower())`, written out below; Home Assistant itself is not installed in venv-ci).",
  ["RESULT fake_states_differing=0 count (None, '')", "RESULT ha_contract_baseline=(None, {}) for None",
   "RESULT ha_contract_mutant=raises AttributeError for None", "RESULT ha_contract_differing=1 count",
   "RESULT null_delta=0 count (a present entity 'binary_sensor.home' = 'on': both arms, both registries)"],
  S + "_entity_state (coordinator.py:9846 `if not entity_id:`), the call site _resolve_away (coordinator.py:9875) with away_presence_entity unset",
  "`if not entity_id:` -> `if False:`. Direction: None reaches hass.states.get; the suite's stub answers None (no change), a registry that lower()s the id raises.",
  "a configured, present presence entity: identical on both arms.",
  r'''
NAME, OLD, NEW = "_entity_state", "if not entity_id:", "if False:"


class HaContractStates:
    """Home Assistant's StateMachine.get, as the contract a real hass.states honours (core.py)."""

    def __init__(self, mapping):
        self._states_data = dict(mapping)

    def get(self, entity_id):
        return self._states_data.get(entity_id) or self._states_data.get(entity_id.lower())


present = {"binary_sensor.home": FakeState("on")}


def es(eid, ha):
    c = coord(present)
    if ha:
        c.hass.states = HaContractStates(present)
    return c._entity_state(eid)


fake_diff = sum(int(x[0] != x[1]) for x in (both(NAME, OLD, NEW, lambda e=e: es(e, False)) for e in (None, "")))
hb, hm = both(NAME, OLD, NEW, lambda: es(None, True))
ha_diff = sum(int(x[0] != x[1]) for x in (both(NAME, OLD, NEW, lambda e=e: es(e, True)) for e in (None, "")))
print(f"RESULT default_presence_entity={coord()._ctx._config.away_presence_entity!r}")
print(f"RESULT fake_states_differing={fake_diff} count")
print(f"RESULT ha_contract_baseline={hb} for None")
print(f"RESULT ha_contract_mutant={hm} for None")
print(f"RESULT ha_contract_differing={ha_diff} count")
nd = sum(int(x[0][0] != x[1][0]) for x in (both(NAME, OLD, NEW, lambda h=h: es("binary_sensor.home", h)) for h in (False, True)))
print(f"RESULT null_delta={nd} count")
tail()
''')
