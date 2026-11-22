B = {}
B["7ffebcb567a4242e"] = dict(
metric="the previous plan's seeded value _open_loop_plan_value returns when `now` sits exactly one step (900 s) before the plan's first timestamp; None means 'the plan says nothing'.",
expected="seed_at_900s_baseline=42.0, seed_at_900s_mutant=None; seed_at_899s and seed_at_901s identical in both arms (42.0 / None)",
symbol="custom_components.heatpump_optimizer.coordinator:_open_loop_plan_value, line 2540",
pert="key 7ffebcb567a4242e CMP_BOUND, `starts[0] - now_s <= 900.0` -> `starts[0] - now_s < 900.0`, in memory (the function re-compiled from its own source and patched onto the module). Direction: 42.0 -> None at exactly 900 s.",
null="lead times 899 s and 901 s, where the bound is not tied: both arms agree.",
body='''
from datetime import datetime, timedelta, timezone
from custom_components.heatpump_optimizer import coordinator as c
OLD = "if starts[0] - now_s <= 900.0 else None"
mut = mutated(c._open_loop_plan_value, c, OLD, OLD.replace("<=", "<"))
start = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
plan = SimpleNamespace(timestamps=[start + timedelta(minutes=15 * i) for i in range(4)], tank_temp=[42.0, 43.0, 44.0, 45.0])
moved = 0
for lead in (899.0, 900.0, 901.0, 0.5, 1800.0):
    now = start - timedelta(seconds=lead)
    b = c._open_loop_plan_value(plan, "tank_temp", now)
    m = mut(plan, "tank_temp", now)
    tag = f"{lead:g}s"
    print(f"RESULT seed_at_{tag}_baseline={b!r}")
    print(f"RESULT seed_at_{tag}_mutant={m!r}")
    moved += b != m
print(f"RESULT inputs_moved={moved} count")
''')
B["845155d368e8b524"] = dict(
metric="what _outage_reading reports at a restart whose heartbeat gap is exactly OUTAGE_GAP_MINUTES (90 min); None means 'no outage'.",
expected="gap_90.0min_baseline=None, gap_90.0min_mutant='Update gap of 90 minutes'; gaps 89.0 and 91.0 min identical in both arms",
symbol="custom_components.heatpump_optimizer.coordinator:_outage_reading, line 900",
pert="key 845155d368e8b524 CMP_BOUND, `if gap_minutes <= OUTAGE_GAP_MINUTES:` -> `if gap_minutes < OUTAGE_GAP_MINUTES:`, in memory. Direction: None -> an outage reading at the tie.",
null="gaps of 89 and 91 minutes, where the bound is not tied.",
body='''
from datetime import datetime, timedelta, timezone
from custom_components.heatpump_optimizer import coordinator as c
OLD = "if gap_minutes <= OUTAGE_GAP_MINUTES:"
mut = mutated(c._outage_reading, c, OLD, OLD.replace("<=", "<"))
now = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
print(f"RESULT outage_gap_minutes={c.OUTAGE_GAP_MINUTES}")
moved = 0
for gap in (89.0, 90.0, 91.0, 89.999, 90.001):
    last = (now - timedelta(minutes=gap)).isoformat()
    b, m = c._outage_reading(last, now, False), mut(last, now, False)
    print(f"RESULT gap_{gap}min_baseline={b!r}")
    print(f"RESULT gap_{gap}min_mutant={m!r}")
    moved += b != m
print(f"RESULT inputs_moved={moved} count")
''')
_fr = '''
from custom_components.heatpump_optimizer import coordinator as c
OLD = "if not math.isfinite(value) or not lo <= value <= hi:"
mut = mutated(c._plausible_forecast_rows, c, OLD, OLD.replace(%r, %r))
moved = 0
for field, (lo, hi) in c._FORECAST_FIELD_RANGE.items():
    for name, v in (("lo", lo), ("hi", hi), ("mid", (lo + hi) / 2)):
        b = c._plausible_forecast_rows([{field: v}])[0][field]
        m = mut([{field: v}])[0][field]
        print(f"RESULT {field}_{name}_{v:g}_baseline={b!r}")
        print(f"RESULT {field}_{name}_{v:g}_mutant={m!r}")
        moved += b != m
print(f"RESULT fields_x_bounds_moved={moved} count")
'''
B["3e68dcd55f9567e5"] = dict(
metric="the value _plausible_forecast_rows keeps for a forecast field sitting exactly on the LOWER edge of its _FORECAST_FIELD_RANGE window (kept value, or None when dropped as implausible).",
expected="every field's lo edge: baseline the value, mutant None (e.g. precipitation 0.0 -> None, wind_speed 0.0 -> None, solar 0.0 -> None); hi edge and mid identical",
symbol="custom_components.heatpump_optimizer.coordinator:_plausible_forecast_rows, line 3013",
pert="key 3e68dcd55f9567e5 CMP_BOUND, `not lo <= value <= hi` -> `not lo < value <= hi`, in memory. Direction: a lower-edge reading (a dry hour's 0.0 mm, a calm 0.0 m/s, night's 0 W/m2) kept -> None.",
null="each field's window midpoint and upper edge, where the lower comparison is not tied.",
body=_fr % ("lo <= value", "lo < value"))
B["88ecd932bc81efec"] = dict(
metric="the value _plausible_forecast_rows keeps for a forecast field sitting exactly on the UPPER edge of its _FORECAST_FIELD_RANGE window (kept value, or None when dropped as implausible).",
expected="every field's hi edge: baseline the value, mutant None (e.g. humidity 100.0 -> None); lo edge and mid identical",
symbol="custom_components.heatpump_optimizer.coordinator:_plausible_forecast_rows, line 3013",
pert="key 88ecd932bc81efec CMP_BOUND, `not lo <= value <= hi` -> `not lo <= value < hi`, in memory. Direction: an upper-edge reading (saturated 100 % humidity, fog) kept -> None.",
null="each field's window midpoint and lower edge, where the upper comparison is not tied.",
body=_fr % ("value <= hi", "value < hi"))
B["4403a4c7bec83d8f"] = dict(
metric="state-machine lookups _price_entity_state makes with a falsy entity id for a config with no price entity (the API-price install), and whether the lookup raises under Home Assistant core's lookup shape (`get(id) or get(id.lower())`, modelled here: no homeassistant package is installed).",
expected="falsy_lookups_baseline=0, falsy_lookups_mutant=1; ha_shape_raises_baseline=0, ha_shape_raises_mutant=1; return value None in both arms on the suite's FakeStates",
symbol="custom_components.heatpump_optimizer.coordinator:_price_entity_state, line 3417",
pert="key 4403a4c7bec83d8f GUARD_OFF, `if not entity_id:` -> `if False:`, in memory. Direction: 0 -> 1 falsy lookups; a None id reaches `None.lower()` under core's shape.",
null="a configured price entity id, where the guard is false either way: identical lookups and state.",
body='''
from custom_components.heatpump_optimizer import coordinator as c
OLD = "    if not entity_id:"
mut = mutated(c._price_entity_state, c, OLD, "    if False:")


class Recording:
    """The suite's FakeStates shape (dict.get), counting lookups by a falsy id."""
    def __init__(self, states):
        self._s, self.falsy = dict(states), 0

    def get(self, entity_id):
        self.falsy += not entity_id
        return self._s.get(entity_id)


class CoreShape(Recording):
    """Home Assistant core's StateMachine.get shape: exact id, then the lower-cased id."""
    def get(self, entity_id):
        self.falsy += not entity_id
        return self._s.get(entity_id) or self._s.get(entity_id.lower())


def run(fn, states_cls, cfg):
    hass = SimpleNamespace(states=states_cls({"sensor.price": "STATE"}))
    try:
        value, raised = fn(hass, cfg), 0
    except Exception as err:  # noqa: BLE001 -- the count is the point
        value, raised = type(err).__name__, 1
    return value, hass.states.falsy, raised


for label, cfg in (("unset", {}), ("configured", {"price_entity": "sensor.price"})):
    for arm, fn in (("baseline", c._price_entity_state), ("mutant", mut)):
        v, n, _ = run(fn, Recording, cfg)
        _, _, r = run(fn, CoreShape, cfg)
        print(f"RESULT {label}_value_{arm}={v!r}")
        print(f"RESULT {label}_falsy_lookups_{arm}={n} count")
        print(f"RESULT {label}_ha_shape_raises_{arm}={r} count")
''')
