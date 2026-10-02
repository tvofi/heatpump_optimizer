"""Unit tests for the v2.8.0 feature modules.

    PYTHONPATH=tests/hastub python tests/features.py

Each module is driven directly rather than through a full optimization run.
The end-to-end scripts already cover "does the plan come out sensible"; what
they cannot cover is a detector that never fires, a watchdog that lets a
flatline through, or a tariff term that charges a month's fee once per hour.
Those failures produce a *plausible* plan, which is exactly why they need
tests that look at the mechanism rather than at the outcome.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone

from harness import FakeHass, FakeState, Results, UTC, minutes_ago

import numpy as np

from heatpump_optimizer import away as away_mode
from heatpump_optimizer import boost as boost_mod
from heatpump_optimizer import battery as battery_view
from heatpump_optimizer import presets, pv
from heatpump_optimizer.accuracy import (
    AccuracySample,
    AccuracyTracker,
    delivered_ratio,
)
from heatpump_optimizer.comfort_learning import (
    COMFORT_WEIGHT_MAX,
    COMFORT_WEIGHT_MIN,
    ComfortLearner,
    OverrideEvent,
)
from heatpump_optimizer.const import COP_SCALE_MAX, COP_SCALE_MIN
from heatpump_optimizer.defrost import (
    DEFROST_LOSS_MULTIPLIER,
    DERATE_CONFIDENCE_SAMPLES,
    DERATE_MAX,
    DefrostDerate,
    DefrostWindow,
    derate_from_duty,
)
from heatpump_optimizer.external_heat import (
    ExternalHeatConfig,
    ExternalHeatDetector,
    ExternalHeatObservation,
)
from heatpump_optimizer import inputs as inputs_mod
from heatpump_optimizer import flow_lift, pump_mode, pump_signals
from heatpump_optimizer.pump_signals import PumpSignals
from heatpump_optimizer.inputs import (
    InputReader,
    InputReading,
    normalize_power_kw,
    parse_bool,
    stale_summary,
)
from heatpump_optimizer.price_model import (
    PriceShapeModel,
    extend_price_series,
    hourly_from_entries,
)
from heatpump_optimizer.sysid import (
    PHASE_ARMED,
    PHASE_DONE,
    SysIdConfig,
    SystemIdentification,
)
from heatpump_optimizer.tariff import (
    CapacityTariff,
    PeakTracker,
    _smooth_topk_sum,
    peak_cost,
    peak_cost_smooth,
    realised_peak,
)
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord
from heatpump_optimizer.dhw_learning import DhwProfileLearner
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState

R = Results("Feature modules")


import json as _si_json
# ---------------------------------------------------------------------------
R.section("P1/P2/N-min-gap — the defrost, price-shape and peak stores and the feed parsers (D1-s4-01, D1-s4-03, D1-s5-02, D1-s5-03, D1-s5-04)")
# Round 9 F3.3 (#1644 P2, #1647 P1, #1680 N-min-gap). A learner store loads
# into the domain its own update path writes, cell by cell, through the store
# boundary's scrub (QuarantiningStore turns a non-finite leaf into None before
# any loader sees it, so these payloads are driven through that scrub); one
# unreadable row of a price or irradiance feed drops that row, not the feed;
# and one off-grid stamp does not set Open-Meteo's resolution.
import logging as _f33_logging  # noqa: E402

from heatpump_optimizer import defrost as _f33_df  # noqa: E402
from heatpump_optimizer import open_meteo as _f33_om  # noqa: E402
from heatpump_optimizer import price_model as _f33_pm  # noqa: E402
from heatpump_optimizer import store as _f33_store  # noqa: E402
from heatpump_optimizer import tariff as _f33_tf  # noqa: E402


class _F33Warnings(_f33_logging.Handler):
    def __init__(self):
        super().__init__(_f33_logging.WARNING)
        self.n = 0

    def emit(self, record):
        self.n += 1


_f33_log = _F33Warnings()
_f33_logging.getLogger("custom_components.heatpump_optimizer").addHandler(_f33_log)
_f33_logging.getLogger("heatpump_optimizer").addHandler(_f33_log)


def _f33_stored(payload):
    """``payload`` as a loader receives it from a QuarantiningStore."""
    return _f33_store._sanitize(_si_json.loads(_si_json.dumps(payload)))


def _f33_load(loader, payload):
    """(loaded object, WARNINGs it logged) for ``payload`` through the store."""
    _f33_log.n = 0
    got = loader(_f33_stored(payload))
    return got, _f33_log.n


_F33_NT = len(_f33_df.TEMP_EDGES) - 1
_F33_NH = len(_f33_df.HUMIDITY_EDGES) - 1


def _f33_defrost(**over):
    grid = lambda v: [[v] * _F33_NH for _ in range(_F33_NT)]  # noqa: E731
    payload = {"version": 2, "factors": grid(0.9), "counts": grid(15),
               "duty": grid(0.05), "duty_counts": grid(20), "duty_events": grid(3)}
    for key, cells in over.items():
        for (t, h), value in cells.items():
            payload[key][t][h] = value
    return payload


# D1-s4-01: a duty cell observe_duty cannot write (finite and out of [0, 1],
# or non-finite and scrubbed to None) restarts its own bucket unmeasured; the
# other buckets keep their duty and counts. The healthy store loads exactly.
_f33_bad = {(0, 0): 1e300, (1, 1): -0.5, (2, 1): "nan"}
_f33_d, _f33_dw = _f33_load(_f33_df.DefrostDerate.from_dict, _f33_defrost(duty=_f33_bad))
_f33_h, _f33_hw = _f33_load(_f33_df.DefrostDerate.from_dict, _f33_defrost())
_f33_kept = [
    (t, h) for t in range(_F33_NT) for h in range(_F33_NH)
    if _f33_d.duty[t][h] == 0.05 and _f33_d.duty_counts[t][h] == 20
]
R.check(
    "a stored defrost duty outside [0, 1] restarts only its own bucket "
    "unmeasured, with a warning; a healthy store loads as written (D1-s4-01)",
    all(_f33_d.duty[t][h] == 0.0 and _f33_d.duty_counts[t][h] == 0 for t, h in _f33_bad)
    and len(_f33_kept) == _F33_NT * _F33_NH - len(_f33_bad)
    and _f33_dw == 1
    and _f33_h.as_dict() == _f33_defrost() and _f33_hw == 0,
    f"duty={_f33_d.duty} counts={_f33_d.duty_counts} warnings={_f33_dw}/{_f33_hw}",
)

# D1-s4-03: one unreadable duty_counts cell in a v2 store costs that bucket,
# not the eleven measured ones beside it, and is not called a v5.3.0 upgrade;
# a v1 store (no measured half) still is.
_f33_one, _ = _f33_load(
    _f33_df.DefrostDerate.from_dict, _f33_defrost(duty_counts={(3, 0): "abc"})
)
_f33_whole, _f33_wholew = _f33_load(
    _f33_df.DefrostDerate.from_dict, dict(_f33_defrost(), duty_counts="x")
)
_f33_v1 = {k: v for k, v in _f33_defrost().items() if k in ("factors", "counts")}
_f33_up, _ = _f33_load(_f33_df.DefrostDerate.from_dict, _f33_v1)
R.check(
    "one unreadable cell in a v2 defrost store costs one bucket, and neither "
    "it nor a wholly unreadable measured half is labelled migrated; a v1 "
    "store is (D1-s4-03)",
    not _f33_one.migrated
    and sum(c == 20 for row in _f33_one.duty_counts for c in row) == _F33_NT * _F33_NH - 1
    and not _f33_whole.migrated and _f33_wholew == 1
    and _f33_up.migrated,
    f"migrated={_f33_one.migrated}/{_f33_whole.migrated}/{_f33_up.migrated} "
    f"counts={_f33_one.duty_counts}",
)

# D1-s5-02, price shape: bins observe_day cannot write (zero, negative, 1e300)
# are put through its own clip and renormalisation, a variance above
# RESIDUAL_VAR_MAX restarts at zero and a negative day count at zero; the
# guessed tail then stays positive and bounded. A learned model round-trips.
_f33_rng = np.random.default_rng(3)
_f33_pmh = PriceShapeModel()
for _f33_i in range(10):
    _f33_day = datetime(2026, 1, 5, tzinfo=UTC) + timedelta(days=_f33_i)
    _f33_hours = list(1.0 + 0.8 * _f33_rng.random(24))
    _f33_pmh.observe_day(_f33_day, _f33_hours)
    _f33_pmh.observe_day_quarters(
        _f33_day, [p * f for p in _f33_hours for f in (0.9, 1.0, 1.0, 1.1)]
    )
_f33_good = _f33_pmh.as_dict()
_f33_corrupt = _si_json.loads(_si_json.dumps(_f33_good))
_f33_corrupt["shapes"][0][3] = 0
_f33_corrupt["shapes"][0][7] = -2.0
_f33_corrupt["shapes"][1][9] = 1e300
_f33_corrupt["quarter_factors"][0][40] = 1e300
_f33_corrupt["residual_var"][0][10] = 1e300
_f33_corrupt["days"] = [-3, 7]
_f33_corrupt["quarter_days"] = [7, -2]
_f33_pmc, _f33_pmw = _f33_load(PriceShapeModel.from_dict, _f33_corrupt)
_f33_counts = (list(_f33_pmc.days), list(_f33_pmc.quarter_days))
_f33_pmr, _f33_pmrw = _f33_load(PriceShapeModel.from_dict, _f33_good)
_f33_starts = [datetime(2026, 1, 21, tzinfo=UTC) + timedelta(hours=i) for i in range(72)]
_f33_tail = []
for _f33_m in (_f33_pmc,):
    _f33_m.days = [7, 7]  # full trust, so the corrupt bins would reach the tail
    _f33_px, _f33_mask, _f33_sig = extend_price_series([1.0] * 12, 72, _f33_starts, _f33_m)
    _f33_tail = list(_f33_px[~_f33_mask])
R.check(
    "a stored price shape, quarter factor or variance outside what the "
    "learner writes is brought back into its domain; a learned model loads "
    "as written (D1-s5-02)",
    min(_f33_tail) > 0.0 and max(_f33_tail) < 20.0
    and max(max(s) for s in _f33_pmc.residual_var) <= _f33_pm.RESIDUAL_VAR_MAX
    and _f33_counts == ([0, 7], [7, 0]) and _f33_pmw == 4
    and _f33_pmr.as_dict() == _f33_good and _f33_pmrw == 0,
    f"tail {min(_f33_tail):.3g}..{max(_f33_tail):.3g} days={_f33_counts} "
    f"warnings={_f33_pmw}/{_f33_pmrw}",
)

# D1-s5-02, peaks: a negative stored peak is dropped like a non-finite one,
# and an open window the tracker could not have written restarts empty, so
# no threshold or billed peak goes negative. A real tracker round-trips.
_f33_tariff = CapacityTariff(enabled=True, price_per_kw=50.0)
_f33_pt = PeakTracker()
for _f33_q in range(4 * 30):
    _f33_pt.observe(
        datetime(2026, 1, 3, tzinfo=UTC) + timedelta(minutes=15 * _f33_q),
        2.0 + (_f33_q % 7) * 0.5, _f33_tariff,
    )
_f33_ptgood = _f33_pt.as_dict()
_f33_neg = dict(_f33_ptgood, peaks=[-50.0] + _f33_ptgood["peaks"][1:])
_f33_win = dict(_f33_ptgood, window_sum=-400.0, window_factor=5.0)
_f33_ptn, _ = _f33_load(PeakTracker.from_dict, _f33_neg)
_f33_ptw, _f33_ptww = _f33_load(PeakTracker.from_dict, _f33_win)
_f33_ptr, _f33_ptrw = _f33_load(PeakTracker.from_dict, _f33_ptgood)
_f33_ptw.observe(datetime(2026, 1, 6, 12, tzinfo=UTC), 3.0, _f33_tariff)
R.check(
    "a negative stored peak is dropped and an out-of-domain open window "
    "restarts empty; a real tracker loads as written (D1-s5-02)",
    min(_f33_ptn.peaks) >= 0.0 and len(_f33_ptn.peaks) == len(_f33_ptgood["peaks"]) - 1
    and _f33_ptw.threshold_kw(_f33_tariff) >= 0.0
    and _f33_ptw.billed_peak_kw(_f33_tariff) >= 0.0
    and _f33_ptww == 1
    and _f33_ptr.as_dict() == _f33_ptgood and _f33_ptrw == 0,
    f"peaks={_f33_ptn.peaks} threshold={_f33_ptw.threshold_kw(_f33_tariff)} "
    f"billed={_f33_ptw.billed_peak_kw(_f33_tariff)} warnings={_f33_ptww}/{_f33_ptrw}",
)

# D1-s5-03: a JSON integer too large for a double drops its own row from the
# price entity, the Tibber payload, the adjustments and the Open-Meteo block,
# as every other unreadable value already did.
_F33_HUGE = 10 ** 400
_f33_rows = [
    {"start": f"2026-01-15T{h:02d}:00:00+01:00", "value": 0.5 + 0.02 * h} for h in range(24)
] + [{"start": "2026-01-16T00:00:00+01:00", "value": _F33_HUGE}]
def _f33_count(fn):
    """Rows ``fn`` delivers, or the name of what it raised: a raise is the
    whole payload lost, the defect this pins."""
    try:
        got = fn()
    except Exception as err:  # noqa: BLE001
        return type(err).__name__
    return len(got) if isinstance(got, list) else got


_f33_t0 = datetime(2026, 3, 10, tzinfo=UTC)
_f33_block = {
    "time": [(_f33_t0 + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(73)],
    _f33_om._VARIABLE: [100.0] * 72 + [_F33_HUGE],
}
_f33_got = {
    "entity": _f33_count(lambda: _f33_pm.prices_from_entity_attributes(
        {"raw_today": _f33_rows, "unit_of_measurement": "SEK/kWh"}
    )),
    "tibber": _f33_count(lambda: _f33_pm.prices_from_tibber_payload({"data": {"viewer": {"homes": [
        {"currentSubscription": {"priceInfo": {"today": [
            {"total": r["value"], "startsAt": r["start"]} for r in _f33_rows
        ]}}}
    ]}}})),
    "learned days": _f33_count(lambda: list(_f33_pm.hourly_from_entries(
        [{"startsAt": r["start"], "total": r["value"]} for r in _f33_rows[:24]]
        + [{"startsAt": "2026-01-15T05:15:00+01:00", "total": _F33_HUGE}]
    ))),
    "adjusted": _f33_count(lambda: _f33_pm.apply_price_adjustments(
        [{"total": 0.5}, {"total": _F33_HUGE}], 1.25, 0.1
    )),
    "irradiance": _f33_count(
        lambda: list(_f33_om._parse_block(_f33_block, _f33_om._VARIABLE).times)
    ),
}
R.check(
    "a huge JSON integer drops its own price or irradiance row, not the "
    "whole payload (D1-s5-03)",
    _f33_got == {
        "entity": 24, "tibber": 24, "learned days": 1, "adjusted": 1, "irradiance": 72,
    },
    f"{_f33_got}",
)

# D1-s5-04: the resolution is the dominant gap. One stray off-grid stamp
# leaves it at the grid's hour; a missing sample still does not double it
# (the smallest-gap rule's own reason, kept).
_f33_res = {}
for _f33_name, _f33_extra, _f33_drop in (
    ("stray_1min", 1, None), ("stray_30min", 30, None), ("missing", None, 30),
):
    _f33_ts = [_f33_t0 + timedelta(hours=i) for i in range(72) if i != _f33_drop]
    if _f33_extra is not None:
        _f33_ts = sorted(_f33_ts + [_f33_t0 + timedelta(hours=30, minutes=_f33_extra)])
    _f33_res[_f33_name] = _f33_om._parse_block(
        {"time": [t.strftime("%Y-%m-%dT%H:%M") for t in _f33_ts],
         _f33_om._VARIABLE: [100.0] * len(_f33_ts)},
        _f33_om._VARIABLE,
    ).resolution
R.check(
    "one off-grid stamp does not shrink Open-Meteo's inferred resolution, "
    "and one missing sample does not double it (D1-s5-04)",
    set(_f33_res.values()) == {timedelta(hours=1)},
    f"{_f33_res}",
)

sys.exit(R.close("F33"))
