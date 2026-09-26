import sys
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from datetime import datetime, timedelta, timezone
from harness import FakeHass, FakeEntry, Results, UTC
from homeassistant.util import dt as dt_util
from heatpump_optimizer import away as away_mode
from heatpump_optimizer import boost as boost_mod
from heatpump_optimizer.comfort_learning import ComfortLearner
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
R = Results("si-pins")
_T2_DATA = {"tibber_token": "x", "weather_entity": "weather.home"}
def _t2_coord(**config):
    return HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=dict(_T2_DATA, **config)))
# ---------------------------------------------------------------------------
R.section("P1/P2 — a stored instant loads aware, or not at all (D1-s1-01, D1-s3-01, D1-s1-02, D1-s3-05)")
# Round 9 (#1644 P2, #1647 P1, #1660 N-future-instant). Every loader below
# parsed a persisted instant with fromisoformat and handed a naive one to a
# consumer that diffs it against Home Assistant's always-aware now, which
# raised on every cycle until something rewrote the leaf. One rule now loads
# it: drift.stored_instant. The future bound is the store boundary's, pinned
# by tests/finite_boundary.py's instant arm, not here.
import asyncio as _si_aio  # noqa: E402
import json as _si_json  # noqa: E402
from zoneinfo import ZoneInfo as _SiZone  # noqa: E402

from heatpump_optimizer import drift as _si_drift  # noqa: E402
from heatpump_optimizer import pump_arbiter as _si_pa  # noqa: E402
from heatpump_optimizer.curve_learning import CurveLearner as _SiCurve  # noqa: E402
from heatpump_optimizer.snapshots import SnapshotRing as _SiRing  # noqa: E402
from homeassistant.helpers import storage as _si_storage  # noqa: E402

_SI_NOW = datetime(2026, 6, 20, 12, 0, tzinfo=UTC)
_SI_NAIVE = "2026-06-01T12:00:00"


def _si_raises(fn) -> str | None:
    try:
        fn()
    except Exception as err:  # noqa: BLE001
        return type(err).__name__
    return None


R.check(
    "the stored-instant rule reads a naive stamp as UTC, keeps an aware one, "
    "drops garbage, and honours the zone it is given",
    _si_drift.stored_instant(_SI_NAIVE) == datetime(2026, 6, 1, 12, tzinfo=UTC)
    and _si_drift.stored_instant("2026-06-01T14:00:00+02:00")
    == datetime(2026, 6, 1, 12, tzinfo=UTC)
    and _si_drift.stored_instant("garbage") is None
    and _si_drift.stored_instant(7) is None
    and _si_drift.stored_instant(_SI_NAIVE, _SiZone("Europe/Stockholm")).utcoffset()
    == timedelta(hours=2),
    f"{_si_drift.stored_instant(_SI_NAIVE)!r}",
)

# D1-s1-01: the three sibling loaders, each consumer driven with an aware now.
_si_ring = _SiRing.from_dict({"snapshots": [{"taken_at": _SI_NAIVE, "healthy": True}]})
_si_curve = _SiCurve.from_dict({"bias": -1.0, "last_step_at": _SI_NAIVE})
_si_comfort = ComfortLearner.from_dict(
    {"configured_weight": 10.0, "learned_weight": 12.0, "evidence": 1.0,
     "last_update": _SI_NAIVE},
    10.0,
)
_si_errs = {
    "snapshot due": _si_raises(lambda: _si_ring.due(_SI_NOW)),
    "curve step": _si_raises(lambda: _si_curve._step_down(_SI_NOW)),
    "comfort decay": _si_raises(lambda: _si_comfort._decay(_SI_NOW)),
}
R.check(
    "a naive persisted stamp no longer raises in the snapshot, curve or comfort "
    "consumer against an aware clock (D1-s1-01)",
    not any(_si_errs.values()) and _si_ring.due(_SI_NOW)
    and _si_ring.snapshots[0]["taken_at"] == "2026-06-01T12:00:00+00:00",
    f"{_si_errs}; taken_at={_si_ring.snapshots[0]['taken_at']!r}",
)

# D1-s1-02: best_restore must never raise on a stored bias leaf of any shape.
_si_bias = {}
for _si_leaf in ("0.3", "garbage", [0.3], {"v": 0.3}, float("nan"), 0.9):
    _si_r = _SiRing.from_dict({"snapshots": [{
        "taken_at": "2026-06-01T12:00:00+00:00", "healthy": True,
        "accuracy": {"temperature_bias": _si_leaf}, "learners": {},
    }]})
    try:
        _si_bias[repr(_si_leaf)] = _si_r.best_restore() is not None
    except Exception as _si_err:  # noqa: BLE001
        _si_bias[repr(_si_leaf)] = type(_si_err).__name__
R.check(
    "best_restore skips a non-numeric or out-of-band stored bias instead of "
    "raising, and still restores an in-band numeric one (D1-s1-02)",
    _si_bias == {"'0.3'": True, "'garbage'": False, "[0.3]": False,
                 "{'v': 0.3}": False, "nan": False, "0.9": False},
    f"{_si_bias}",
)

# D1-s3-01: the typed return time is the user's wall clock, and boost, the
# arbiter and legionella read a naive stored stamp in the same zone: Home
# Assistant's, whose clock reads it back. Driven under a configured zone, as
# Home Assistant always runs; the stub's default clock is naive.
_SI_STHLM = _SiZone("Europe/Stockholm")
_si_zone0 = dt_util.DEFAULT_TIME_ZONE
dt_util.DEFAULT_TIME_ZONE = _SI_STHLM
try:
    _si_ret = away_mode._parse_return_time("2026-10-05T08:00")
    _si_until = boost_mod._parse_until(_SI_NAIVE)
    _si_c = _t2_coord()
    _si_key = f"heatpump_optimizer_{_si_c.entry.entry_id}_pump_duty"
    _si_storage._DISK[_si_key] = _si_json.dumps({"written": {"mode": ["heat", _SI_NAIVE]}})
    _si_pa.state_for(_si_c).loaded = False
    _si_aio.run(_si_pa._load(_si_c))
    _si_written = _si_pa.state_for(_si_c).written.get("mode")
    _si_storage._DISK[_si_c._legionella.store._key] = _si_json.dumps(
        {"last_cycle": _SI_NAIVE, "last_attempt": _SI_NAIVE}
    )
    _si_aio.run(_si_c._legionella.async_load())
finally:
    dt_util.DEFAULT_TIME_ZONE = _si_zone0
    _si_storage._DISK.clear()
_SI_LOCAL = datetime(2026, 6, 1, 12, tzinfo=_SI_STHLM)
R.check(
    "a tz-less set_away return_time is read in the user's zone and expires "
    "against an aware clock without raising (D1-s3-01)",
    _si_ret is not None and _si_ret.utcoffset() == timedelta(hours=2)
    and _si_raises(lambda: away_mode.expire_override(True, _si_ret, _SI_NOW)) is None,
    f"{_si_ret!r}",
)
R.check(
    "boost, the pump-duty arbiter and legionella read a naive stored stamp in "
    "Home Assistant's zone, aware (D1-s3-01)",
    _si_until == _SI_LOCAL and _si_until.tzinfo is not None
    and _si_written is not None and _si_written[1] == _SI_LOCAL
    and _si_written[1].tzinfo is not None
    and _si_c._legionella.last_cycle == _SI_LOCAL
    and _si_c._legionella.last_cycle.tzinfo is not None
    and _si_c._legionella.attempt == _SI_LOCAL
    and _si_c._legionella.attempt.tzinfo is not None,
    f"boost={_si_until!r} arbiter={_si_written!r} "
    f"legionella={_si_c._legionella.last_cycle!r}",
)

# D1-s3-05: the two-hour maximum is a duration. A clock stepped back J hours
# after a boost was set holds it two hours from the corrected now, not 2 + J.
_si_live = {}
for _si_j in (0, 1, 24):
    _si_b = boost_mod.BoostState()
    _si_b.set("space", True, _SI_NOW)
    _si_back = _SI_NOW - timedelta(hours=_si_j)
    _si_b.expire(_si_back)
    _si_live[_si_j] = (_si_b.until["space"] - _si_back).total_seconds() / 3600.0
R.check(
    "a boost outlives a backward clock step by no more than its two hours "
    "(D1-s3-05); unstepped it still runs the full two",
    _si_live == {0: 2.0, 1: 2.0, 24: 2.0},
    f"hours left after the step: {_si_live}",
)


sys.exit(R.close("SI PINS"))
