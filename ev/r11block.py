import sys
from datetime import datetime, timedelta, timezone
from harness import FakeHass, FakeState, Results, UTC
from heatpump_optimizer.ledger import MonthlyLedger as _SavLedger, month_key as _sav_month_key
R = Results("r11 money block")
# R11-SEAM-money (D8-s1-02, D2-s3-07): the open month is scaled only once it has
# covered ledger.MIN_COVERAGE_HOURS, and a month's hours are its real hours.
# Finder harnesses: D8/s1/monthly.py (first_scale 2688.0 at the base) and
# D2/s3/m4_tariff.py --perturb realhours (coverage_full_23h 1.001346 at the base).
from types import SimpleNamespace as _r11m_NS  # noqa: E402
from zoneinfo import ZoneInfo as _r11m_Zone  # noqa: E402

from heatpump_optimizer import ledger as _r11m_ledger  # noqa: E402
from heatpump_optimizer.sensor import MonthlySavingsSensor as _r11m_Sensor  # noqa: E402

_r11m_sth = _r11m_Zone("Europe/Stockholm")
# The floor read by name, 24 h where the tree predates it, so the failing-first
# run at the base reaches every check below instead of stopping at the import.
_R11M_FLOOR_H = getattr(_r11m_ledger, "MIN_COVERAGE_HOURS", 24.0)
_r11m_hours = {
    "March, spring forward": (_r11m_ledger.month_hours(datetime(2026, 3, 20, 12, tzinfo=_r11m_sth)), 743.0),
    "October, fall back": (_r11m_ledger.month_hours(datetime(2026, 10, 20, 12, tzinfo=_r11m_sth)), 745.0),
    "March in UTC": (_r11m_ledger.month_hours(datetime(2026, 3, 20, 12, tzinfo=UTC)), 744.0),
    "December into January": (_r11m_ledger.month_hours(datetime(2026, 12, 31, 23, tzinfo=_r11m_sth)), 744.0),
    "naive February": (_r11m_ledger.month_hours(datetime(2026, 2, 10, 15)), 672.0),
}
R.check(
    "R11-SEAM-money: month_hours counts a month's real hours in its zone (743 / 745 across DST, 744 in UTC)",
    all(got == want for got, want in _r11m_hours.values()),
    repr(_r11m_hours),
)


def _r11m_settled(hours: float, start: datetime) -> dict:
    """A month's meta after ``hours`` hourly settlements from ``start``."""
    led = _SavLedger()
    whole, part = int(hours), hours - int(hours)
    for _h in range(whole):
        led.observe_spot_and_settle_savings(start + timedelta(hours=_h), 1.0, {"baseline_kw": 2.0}, 1.0, 1.0)
    if part:
        led.observe_spot_and_settle_savings(start + timedelta(hours=whole), 1.0, {"baseline_kw": 2.0}, part, part)
    return led.months[_sav_month_key(start)]["meta"]


_r11m_march_now = datetime(2026, 3, 31, 23, 30, tzinfo=_r11m_sth)
_r11m_march = _r11m_settled(743, datetime(2026, 3, 1, 0, tzinfo=_r11m_sth))
R.check(
    "R11-SEAM-money: a spring-forward March settled every real hour scales by exactly 1.0",
    _r11m_ledger.coverage_factor(_r11m_march, _r11m_march_now) == 1.0,
    repr(_r11m_ledger.coverage_factor(_r11m_march, _r11m_march_now)),
)
_r11m_feb_now = datetime(2026, 2, 10, 15, 0)
_r11m_at_floor = _r11m_settled(_R11M_FLOOR_H, datetime(2026, 2, 9, 15, 0))
_r11m_under = _r11m_settled(_R11M_FLOOR_H - 0.25, datetime(2026, 2, 9, 15, 0))
R.check(
    "R11-SEAM-money: coverage_factor is None a quarter-hour under MIN_COVERAGE_HOURS and scales at it",
    getattr(_r11m_ledger, "MIN_COVERAGE_HOURS", None) == 24.0
    and _r11m_ledger.coverage_factor(_r11m_under, _r11m_feb_now) is None
    and _r11m_ledger.coverage_factor(_r11m_at_floor, _r11m_feb_now) == 672.0 / 24.0,
    f"{_r11m_ledger.coverage_factor(_r11m_under, _r11m_feb_now)!r} / "
    f"{_r11m_ledger.coverage_factor(_r11m_at_floor, _r11m_feb_now)!r}",
)
# The calendar-day fallback (no coverage meta) takes the same floor on the hours
# the month has run: 8 h into 1 February is no estimate, 10 February is 28 / 10.
R.check(
    "R11-SEAM-money: the calendar-day fallback is None before the month has run MIN_COVERAGE_HOURS",
    _r11m_ledger.coverage_factor({}, datetime(2026, 2, 1, 8, 0)) is None
    and _r11m_ledger.coverage_factor({}, datetime(2026, 2, 2, 0, 0)) == 28.0 / 2
    and _r11m_ledger.coverage_factor({}, _r11m_feb_now) == 2.8,
    f"{_r11m_ledger.coverage_factor({}, datetime(2026, 2, 1, 8, 0))!r}",
)

# One settled quarter in February after a closed January: today's row scaled the
# quarter by 672 / 0.25 = 2688 (D8-s1-02). The open month has no row; January's
# row is the null control and is unchanged.
_r11m_two = _SavLedger()
for _h in range(48):
    _r11m_two.observe_spot_and_settle_savings(
        datetime(2026, 1, 20, 0, 0) + timedelta(hours=_h), 1.0, {"baseline_kw": 2.0}, 1.0, 1.0)
_r11m_jan_rows = _r11m_two.savings_months(datetime(2026, 2, 1, 0, 15))
_r11m_two.observe_spot_and_settle_savings(datetime(2026, 2, 1, 0, 0), 1.0, {"baseline_kw": 2.0}, 0.25, 0.25)
_r11m_feb_rows = _r11m_two.savings_months(datetime(2026, 2, 1, 0, 15))
R.check(
    "R11-SEAM-money: one settled quarter gives the open month no row; the closed month's row is unchanged",
    [r["month"] for r in _r11m_feb_rows] == ["2026-01"]
    and _r11m_feb_rows == _r11m_jan_rows and not _r11m_jan_rows[0]["estimated"],
    repr(_r11m_feb_rows),
)
_r11m_sensor = _r11m_NS(_rows=lambda: _r11m_feb_rows)
_r11m_two_day = _SavLedger.from_dict(_r11m_two.as_dict())
for _h in range(24):
    _r11m_two_day.observe_spot_and_settle_savings(
        datetime(2026, 2, 1, 0, 15) + timedelta(hours=_h), 1.0, {"baseline_kw": 2.0}, 1.0, 1.0)
_r11m_ready = _r11m_NS(_rows=lambda: _r11m_two_day.savings_months(datetime(2026, 2, 2, 0, 30)))
R.check(
    "R11-SEAM-money: MonthlySavingsSensor waits for open_month_coverage while only closed months have rows",
    _r11m_Sensor._waiting_for.fget(_r11m_sensor) == "open_month_coverage"
    and _r11m_Sensor._waiting_for.fget(_r11m_NS(_rows=lambda: [])) == "settled_savings_month"
    and _r11m_Sensor._waiting_for.fget(_r11m_ready) is None,
    f"{_r11m_Sensor._waiting_for.fget(_r11m_sensor)!r} / {_r11m_Sensor._waiting_for.fget(_r11m_ready)!r}",
)
# R11-SEAM-money (D14-s1-03): every money figure the options dialog labels,
# bounds and validates is in the currency the price feed declares, the one the
# sensors publish (currency.figure_currency): a HUF instance priced by a EUR/kWh
# entity labelled its four money fields and the fee page in HUF and let a
# 50/kWh fee through under the HUF bound. Finder harness:
# D14/s1/currency_precedence.py (money_seams 5, 6 under --instance HUF).
from heatpump_optimizer import config_flow as _r11m_cf  # noqa: E402
from heatpump_optimizer import grid_fee as _r11m_gf  # noqa: E402
import asyncio as _r11m_aio  # noqa: E402


def _r11m_money_units(feed_unit: str | None, source: str = "entity") -> tuple:
    """(field units, placeholder currency, fee bound, fee-page verdict) on a HUF instance."""
    hass = FakeHass()
    hass.config.currency = "HUF"
    cfg = {"price_source": "tibber"}
    if feed_unit is not None:
        hass.states.set("sensor.feed", FakeState("0.21", attributes={"unit_of_measurement": feed_unit}))
        cfg = {"price_source": source, "price_entity": "sensor.feed"}
    def built(of, place_of):
        try:
            return of(hass, cfg), place_of(hass, cfg)
        except TypeError:  # the base's one-argument forms, for the failing-first run
            return of(hass), place_of(hass)

    rows = [row.widget.of for row in _r11m_cf._OPTION_FIELDS if isinstance(row.widget, _r11m_cf._ByHass)]
    units = sorted(dict(built(of, _r11m_cf._fee_placeholders)[0].config).get("unit_of_measurement") for of in rows)
    place = built(rows[0], _r11m_cf._fee_placeholders)[1]
    verdict = _r11m_aio.run(_r11m_cf.HeatPumpOptimizerOptionsFlow._grid_fee_errors(
        _r11m_NS(hass=hass), {"grid_fee_rules": "Mon-Sun 00-24 = 50"}, cfg))
    return units, place["currency"], place["fee_bound"], verdict


_r11m_eur = _r11m_money_units("EUR/kWh")
_r11m_huf = _r11m_money_units(None)
R.check(
    "R11-SEAM-money: on a HUF instance priced in EUR the money fields, the fee page and its bound are in EUR",
    _r11m_eur == (["EUR", "EUR/kWh", "EUR/kWh", "EUR/m³"], "EUR", "10",
                  {"grid_fee_rules": _r11m_gf.ERROR_IMPLAUSIBLE}),
    repr(_r11m_eur),
)
# Null controls: a Tibber install has no feed and keeps the instance's HUF
# (bound 500, the 50/kWh fee accepted), even with a EUR entity left in its
# price-entity slot from an earlier entity setup; a feed declaring nothing
# ("öre/kWh") falls back to the instance as well.
_r11m_stale = _r11m_money_units("EUR/kWh", source="tibber")
R.check(
    "R11-SEAM-money: with no feed code, or a Tibber source, the options dialog keeps the instance currency",
    _r11m_huf == (["HUF", "HUF/kWh", "HUF/kWh", "HUF/m³"], "HUF", "500", {})
    and _r11m_money_units("öre/kWh") == _r11m_huf
    and _r11m_stale == _r11m_huf,
    f"{_r11m_huf!r} / {_r11m_money_units('öre/kWh')!r} / {_r11m_stale!r}",
)
# R11-SEAM-money pins, recorded "not reproduced at main, pinned" (owner ruling
# 2026-11-18): the finder's D2/s3/m4_tariff.py read 0 for these at main. Each
# check fails on the harness's planted inverse. The other four planted
# inverses are already killed by this file's checks, so they add none: the
# Tibber parser reading 'today' only (D2-s3-03) by "each Tibber failure names
# itself, and today and tomorrow both land"; top-k taking the smallest
# (D2-s3-06), one-per-day keeping a lower window (D2-s3-05) and the window
# projection weighting the current draw by the elapsed minutes (D17-s1-05) by
# the capacity-tariff and peak-guard checks.

# D2-s3-04 (inverse of m4_tariff.py --perturb weekday: a day test off by one,
# isoweekday()): a "Mon" rule applies on Monday 12 January 2026, not on the
# Sunday before it nor the Tuesday after.
_r11m_mon = _r11m_gf.parse_rules("Mon 00-24 = 1")[0]
R.check(
    "R11-SEAM-money: a Monday fee rule applies on a Monday and on neither neighbour (D2-s3-04, pinned)",
    [_r11m_mon.applies(datetime(2026, 1, d, 12, tzinfo=_r11m_sth)) for d in (11, 12, 13)] == [False, True, False],
    repr([_r11m_mon.applies(datetime(2026, 1, d, 12, tzinfo=_r11m_sth)) for d in (11, 12, 13)]),
)
# R11-SEAM-money (ADR-001 arm day): price_model._usable_day is the one test of
# a learnable day for both resolutions; a day whose mean sits on the 1e-6
# floor is not learned, one just above it is (np.mean of 24 x 1e-6 is 1e-6
# exactly, so the boundary is the comparison's own).
from heatpump_optimizer.price_model import PriceShapeModel as _R11mShape  # noqa: E402

_r11m_shape = _R11mShape()
R.check(
    "R11-SEAM-money: a day of prices averaging exactly the 1e-6 floor is not learned; 2e-6 is",
    [_r11m_shape.observe_day(datetime(2026, 1, 14), [1e-6] * 24),
     _r11m_shape.observe_day(datetime(2026, 1, 15), [2e-6] * 24)] == [False, True],
)
sys.exit(R.close("R11 CHECKS"))
