import sys

sys.path.insert(
    0, "/tmp/claude-0/-home-user/67fb38f0-9f88-5c6b-9d2e-78b6cb07f57d/scratchpad"
)
from dataclasses import replace
from _common import (
    S,
    FOLD_LAST,
    FOLD_NOW,
    SP_LAST,
    SP_NOW,
    true_s,
    show,
    datetime,
    asyncio,
    dt_util,
    coord,
)
from heatpump_optimizer.thermal_model import ThermalState

HOUSE_MIN, HOUSE_MAX = 0.15, 1.5
BUF_MIN, BUF_MAX = 0.15, 3.0
# (label, previous, now)
PAIRS = [
    ("fold true 1h / wall 0", FOLD_LAST, FOLD_NOW),
    (
        "fold true 10min / wall -50min",
        datetime(2026, 10, 25, 2, 55, tzinfo=S),
        datetime(2026, 10, 25, 2, 5, tzinfo=S, fold=1),
    ),
    ("spring true 2min / wall 62min", SP_LAST, SP_NOW),
    (
        "spring true 5min / wall 65min",
        datetime(2026, 3, 29, 1, 55, tzinfo=S),
        datetime(2026, 3, 29, 3, 0, tzinfo=S),
    ),
]


def base_state():
    return ThermalState(
        room_temperature=21.0,
        upper_floor_temperature=21.0,
        lower_floor_temperature=20.0,
        slab_temperature=27.0,
        outdoor_temperature=-5.0,
    )


def drive_house(prev, now, lower=False):
    cfg = {}
    if lower:
        cfg = {
            "upper_floor_thermal_mass": 3.0,
            "lower_floor_thermal_mass": 8.0,
            "lower_floor_temp_entity": "sensor.lower",
        }
    c = coord(**cfg)
    seen = []
    base = base_state()
    c._last_house_sample = base
    c._last_house_sample_time = prev
    c._current_state = replace(
        base,
        lower_floor_temperature=19.9,
        room_temperature=20.9,
        upper_floor_temperature=20.9,
    )
    c._current_action = {"power": 2.0}
    c._learning_frozen = lambda *a, **k: None
    c._interval_space_power = lambda: 1.0
    c._current_weather = lambda: (0.0, 0.0)

    def sim(prev_state, power, outdoor, **kw):
        seen.append(kw.get("dt_hours"))
        return replace(
            prev_state,
            room_temperature=20.9,
            upper_floor_temperature=20.9,
            lower_floor_temperature=19.9,
        )

    c._thermal_model.simulate_step = sim
    dt_util.freeze(now)
    try:
        fn = (
            c._async_learn_lower_floor_loss if lower else c._async_learn_house_heat_loss
        )
        asyncio.run(fn())
    finally:
        dt_util.freeze(None)
    return seen


def expected_dt(prev, now, lo, hi):
    h = true_s(now, prev) / 3600.0
    return round(h, 4) if lo <= h <= hi else None


for tag, lower, line in (
    ("house", False, "coordinator.py:4703"),
    ("lower-floor", True, "coordinator.py:4892"),
):
    for lbl, a, b in PAIRS:
        seen = drive_house(a, b, lower)
        obs = round(seen[0], 4) if seen else None
        show(
            f"{line} {tag} learner replay dt_hours [{lbl}]",
            obs,
            expected_dt(a, b, HOUSE_MIN, HOUSE_MAX),
        )

# --- buffer cooling :4594
for lbl, a, b in PAIRS:
    c = coord()
    rates = []
    c._buffer_cooling_bounds = lambda: (0.0, 1e9)
    c._apply_buffer_cooling_rate = lambda r, rates=rates: rates.append(r)

    async def noop():
        return None

    c._async_save_thermal_learning = noop
    c._learning_frozen = lambda *a, **k: None
    c._current_action = {"power": 0.0}
    c._last_buffer_temp_sample = 50.0
    c._last_buffer_sample_time = a
    c._buffer_heating_since_sample = False
    dt_util.freeze(b)
    try:
        asyncio.run(c._async_learn_buffer_cooling(48.0))
    finally:
        dt_util.freeze(None)
    h = true_s(b, a) / 3600.0
    exp_sampled = BUF_MIN <= h <= BUF_MAX
    show(
        f"coordinator.py:4594 buffer cooling sample accepted [{lbl}]",
        bool(rates),
        exp_sampled,
    )
    if rates and exp_sampled:
        # rate scales as 1/dt_h: report ratio observed/expected
        pass
