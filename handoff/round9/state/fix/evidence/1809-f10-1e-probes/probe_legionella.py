import sys

sys.path.insert(
    0, "/tmp/claude-0/-home-user/67fb38f0-9f88-5c6b-9d2e-78b6cb07f57d/scratchpad"
)
from _common import *
from heatpump_optimizer.legionella import LegionellaGuard
from heatpump_optimizer.disinfection import DisinfectionSwitch
from heatpump_optimizer.thermal_model import ThermalParameters
from heatpump_optimizer.const import CONF_DHW_FREE_DISINFECTION_ENABLED
from heatpump_optimizer.optimizer import REASON_LEGIONELLA


def mk(cfg=None, action=None):
    return LegionellaGuard(
        FakeHass(),
        "dst",
        ThermalParameters.from_config({}),
        cfg or {},
        action=lambda: action or {},
        disinfect=DisinfectionSwitch({}, None, None),
        dhw_blocked=lambda: False,
    )


tgt = float(ThermalParameters.from_config({}).dhw_legionella_temp)

# --- :206 hold accumulation (free disinfection ON)
cases = {
    "fold true 1h/wall 0": (FOLD_LAST, FOLD_NOW),
    "fold true 60s/wall -3540s": (F60_LAST, F60_NOW),
    "spring true 2min/wall 62min": (SP_LAST, SP_NOW),
}
for lbl, (l, n) in cases.items():
    g = mk({CONF_DHW_FREE_DISINFECTION_ENABLED: True})
    g.hold_last = l
    g.hold_minutes = 0.0
    g.last_cycle = None
    dt_util.freeze(n)
    asyncio.run(g.async_track(tgt))
    exp_gap = min(true_s(n, l) / 60.0, 90.0)
    credited = g.last_cycle is not None
    exp_credit = exp_gap >= 20.0
    obs = "credited" if credited else f"hold_minutes={g.hold_minutes:g}"
    exp = "credited" if exp_credit else f"hold_minutes={exp_gap:g}"
    show(f"legionella.py:206 hold accum [{lbl}]", obs, exp)
dt_util.freeze(None)

# --- :222 min spacing between credits (free disinfection OFF = instant credit)
cases = {
    "fold true 1h/wall 0 (credit should pass)": (FOLD_LAST, FOLD_NOW, True),
    "spring true 40min/wall 1h40 (should be suppressed)": (
        datetime(2026, 3, 29, 1, 30, tzinfo=S),
        datetime(2026, 3, 29, 3, 10, tzinfo=S),
        False,
    ),
}
for lbl, (l, n, expect_credit) in cases.items():
    g = mk({})
    g.last_cycle = l
    dt_util.freeze(n)
    asyncio.run(g.async_track(tgt))
    show(
        f"legionella.py:222 credit spacing [{lbl}]",
        g.last_cycle is not l,
        expect_credit,
    )
dt_util.freeze(None)

# --- :300 boost bound (12 h)
started = datetime(2026, 10, 24, 22, 30, tzinfo=S)  # 20:30Z
now = datetime(2026, 10, 25, 9, 30, tzinfo=S)  # 08:30Z -> true 12.0 h, wall 11.0 h
g = mk({}, action={"dhw_reason": REASON_LEGIONELLA})
g.boost_active = True
g.boost_started = started
dt_util.freeze(now)


async def run():
    async def noop(*a, **k):
        return None

    g._drive_switch = noop
    await g.async_track_cycle(50.0)


asyncio.run(run())
dt_util.freeze(None)
print(
    "boost true h:", true_s(now, started) / 3600, "wall h:", wall_s(now, started) / 3600
)
show("legionella.py:300 boost bound closed at true 12h", g.boost_active is False, True)
