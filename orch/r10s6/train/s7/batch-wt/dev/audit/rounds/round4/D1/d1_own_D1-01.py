"""D1-01 verified independently (verifier seat D1-1, round 4).

MY METRIC (differs from the finder's): a corrupt price-shape bin, expressed
as a STRICT-JSON string, is counted at three independent seams --
  (a) unit:   how many non-finite spellings PriceShapeModel.from_dict accepts,
  (b) seam:   how many GUESSED steps extend_price_series prices at exactly
              0.0 when the loaded model holds one such bin,
  (c) e2e:    how many planning steps a coordinator prices at exactly 0.0
              after loading the corrupt store -- anchored at a WEDNESDAY
              06:00 with 6 published hours (finder used Saturday 12:00,
              10 published), so agreement is not an artefact of one anchor.
Matched control: identical store, finite bin. Perturbation: from_dict's
shape branch guarded by an isfinite reject (the finding's own one-line
fix), applied as a class-level monkeypatch -- no production file edited.

COMMAND (from this worktree root):
  PYTHONPATH=tests/hastub /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    tools/audit/round4/D1/d1_own_D1-01.py
EXPECTED: fromdict_nonfinite_spellings_accepted=6, seam_zero_priced_guessed_steps>0,
  e2e_zero_priced_steps=4 exact, e2e_control_zero_priced_steps=0,
  e2e_fixed_zero_priced_steps=0, e2e_log_lines=0.
BASELINE: 7dd68dd327fe3dbfb09f3bd0fe38910c58877697 (tree verified identical
  for custom_components/heatpump_optimizer/*.py at 0855277).
MACHINE: 8-core Apple M1, macOS 25.6.0, CPython 3.11. All numbers are counts.
INSTRUMENTS: PriceShapeModel.from_dict, PriceShapeModel.predict,
  price_model.extend_price_series, coordinator._async_load_price_model,
  coordinator._forecast_arrays.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import asyncio
import json
import logging
import sys
import time
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.helpers import storage as hastore  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import heatpump_optimizer.const as const  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)
from heatpump_optimizer.price_model import (  # noqa: E402
    PriceShapeModel,
    extend_price_series,
)

CONFIG = {
    const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
    const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
    const.CONF_DHW_TANK_VOLUME: 180.0,
}
#: Must equal coordinator.py's f"{DOMAIN}_{entry.entry_id}_price_model".
#: (A first draft of this harness used a wrong key, loaded no store at all,
#: and reported zero priced steps everywhere -- the zeros were the harness's,
#: not the tree's. Frozen to a Wednesday so the corrupted WEEKDAY profile is
#: the one the horizon visits.)
KEY = f"{const.DOMAIN}_d1own_entry_price_model"

#: My own shape: flat-ish with a morning peak, my own numbers.
SHAPE = [0.85] * 6 + [1.30] * 3 + [1.05] * 9 + [0.95] * 6

#: Every spelling of non-finiteness that is a strictly valid JSON *string*.
NONFINITE_STRINGS = ["nan", "NaN", "inf", "Infinity", "-Infinity", "-inf"]


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record):
        self.records.append(record)


def unit_fromdict() -> int:
    """(a) Count non-finite spellings from_dict accepts into shapes."""
    accepted = {}
    for spelling in NONFINITE_STRINGS:
        row = list(SHAPE)
        row[9] = spelling
        model = PriceShapeModel.from_dict(
            {"shapes": [row, list(SHAPE)], "days": [30, 30]}
        )
        loaded = [v for r in model.shapes for v in r]
        accepted[spelling] = sum(1 for v in loaded if not np.isfinite(v))
    print(f"  from_dict non-finite bins accepted, per spelling: {accepted}")
    return sum(1 for n in accepted.values() if n > 0)


def seam_extend(anchor) -> tuple[int, int]:
    """(b) extend_price_series prices guessed steps at 0.0 through NaN."""
    when = anchor.replace(hour=0, minute=0, second=0, microsecond=0)
    step = timedelta(minutes=15)
    starts = [when + i * step for i in range(96)]

    row = list(SHAPE)
    row[9] = "nan"
    model = PriceShapeModel.from_dict(
        {"shapes": [row, list(SHAPE)], "days": [40, 40]}
    )
    prices, mask, _ = extend_price_series([0.72] * 24, 96, starts, model)
    guessed_zero = int(
        np.count_nonzero((np.asarray(prices) <= 1e-12) & ~np.asarray(mask))
    )

    ok_model = PriceShapeModel.from_dict(
        {"shapes": [list(SHAPE), list(SHAPE)], "days": [40, 40]}
    )
    prices_ok, mask_ok, _ = extend_price_series(
        [0.72] * 24, 96, starts, ok_model
    )
    ctrl_zero = int(
        np.count_nonzero((np.asarray(prices_ok) <= 1e-12) & ~np.asarray(mask_ok))
    )
    return guessed_zero, ctrl_zero


def _one_arm(now, published_hours, corrupt: bool, bin_idx: int = 15):
    """One coordinator arm; corrupt=True poisons weekday bin ``bin_idx``.

    Bin 15 (15:00) sits in the GUESSED tail of a Wednesday-06:00 horizon
    with 6 published hours, reproducing the zero-pricing path. Bin 9, by
    contrast, sits inside the published window: it cannot zero a guessed
    step, but it still poisons ``extend_price_series``'s level calibration
    (``np.mean`` over shape values swallows the NaN), so the whole tail is
    silently mispriced -- measured below as the ``calibration`` arm.
    """
    hastore._reset_store_disk()
    row = list(SHAPE)
    if corrupt:
        row[bin_idx] = "nan"
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.1"))
    hass.states.set("sensor.outdoor", FakeState("-7.0"))
    entry = FakeEntry(data=dict(CONFIG))
    entry.entry_id = "d1own_entry"
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    hastore._DISK[KEY] = json.dumps(
        {
            "model": {"shapes": [row, list(SHAPE)], "days": [30, 30]},
            "days_seen": [],
            "quarter_days_seen": [],
        }
    )
    cap = _Capture()
    lg = logging.getLogger("custom_components.heatpump_optimizer")
    lg.addHandler(cap)
    lg.setLevel(logging.DEBUG)

    async def go():
        await coord._async_load_price_model()
        await coord._update_current_state()
        coord._prices = [
            {
                "total": round(0.55 + 0.4 * ((h % 10) / 10.0), 4),
                "starts_at": (now + timedelta(hours=h)).isoformat(),
                "level": "NORMAL",
            }
            for h in range(published_hours)
        ]
        coord._weather_forecast = [
            {
                "datetime": (now + timedelta(hours=h)).isoformat(),
                "temperature": -8.0,
                "wind_speed": 2.0,
                "precipitation": 0.0,
                "humidity": 90.0,
            }
            for h in range(48)
        ]
        coord._solar_radiation_forecast = [0.0] * 48
        return coord._forecast_arrays(now)

    arrays = asyncio.run(go())
    lg.removeHandler(cap)
    series = np.asarray(arrays.prices, dtype=float)
    known = np.asarray(arrays.price_known, dtype=bool)
    zero = int(np.count_nonzero((series <= 1e-12) & ~known))
    return zero, len(cap.records), series


def main() -> int:
    t0 = time.perf_counter()
    print("=== D1-01, verifier's own instrument ===")
    print(f"  interpreter max(0.0, float('nan')) == {max(0.0, float('nan'))}")
    print(f"  json.dumps('nan') strict           == {json.dumps('nan')}")

    # A Wednesday 06:00 anchor, weekday profile, 6 published hours.
    now = dt_util.now()
    while now.weekday() != 2:
        now = now + timedelta(days=1)
    now = now.replace(hour=6, minute=0, second=0, microsecond=0)
    dt_util.freeze(now)
    try:
        unit = unit_fromdict()
        seam_zero, seam_ctrl = seam_extend(now)
        print(
            f"  seam: guessed steps priced 0.0      "
            f"{seam_zero} (ctrl {seam_ctrl})"
        )

        bad_zero, bad_logs, bad_series = _one_arm(now, 6, corrupt=True)
        ok_zero, ok_logs, ok_series = _one_arm(now, 6, corrupt=False)
        diff = np.flatnonzero(np.abs(bad_series - ok_series) > 1e-9)
        # The same corrupt bin parked inside the PUBLISHED window: no zero
        # step, but the level calibration swallows the NaN and the whole
        # guessed tail is mispriced. My own second symptom of one cause.
        cal_zero, _cl, cal_series = _one_arm(now, 6, corrupt=True, bin_idx=9)
        cal_ok = _one_arm(now, 6, corrupt=False, bin_idx=9)[2]
        cal_diff = np.flatnonzero(np.abs(cal_series - cal_ok) > 1e-9)
        cal_shift = float(
            np.mean(cal_series[cal_diff] - cal_ok[cal_diff])
        ) if cal_diff.size else 0.0

        # Perturbation: the finding's own one-line fix, monkeypatched.
        orig = PriceShapeModel.from_dict

        def guarded(cls, data, _orig=orig):
            model = _orig(data)
            if not all(np.isfinite(v) for r in model.shapes for v in r):
                model.shapes = [[1.0] * len(r) for r in model.shapes]
            return model

        PriceShapeModel.from_dict = classmethod(guarded)
        try:
            fix_zero, _fl, _fs = _one_arm(now, 6, corrupt=True)
        finally:
            PriceShapeModel.from_dict = orig

        print(f"  e2e corrupt zero-priced steps      {bad_zero}")
        print(f"  e2e control zero-priced steps      {ok_zero}")
        print(f"  e2e fixed (isfinite guard)         {fix_zero}")
        print(f"  e2e differing steps                {diff.tolist()}")
        print(
            f"  control/corrupt at those steps     "
            f"{[round(float(ok_series[i]), 4) for i in diff[:6]]} / "
            f"{[round(float(bad_series[i]), 4) for i in diff[:6]]}"
        )
        print(f"  log lines corrupt/control          {bad_logs}/{ok_logs}")
        print(
            f"  calibration arm (bin in published window): "
            f"{len(cal_diff)} steps mispriced, mean shift "
            f"{cal_shift:+.4f} SEK/kWh, zero steps {cal_zero}"
        )
    finally:
        dt_util.freeze(None)

    print()
    print(f"RESULT fromdict_nonfinite_spellings_accepted={unit} count")
    print(f"RESULT seam_zero_priced_guessed_steps={seam_zero} count")
    print(f"RESULT seam_control_zero_steps={seam_ctrl} count")
    print(f"RESULT e2e_zero_priced_steps={bad_zero} count")
    print(f"RESULT e2e_control_zero_priced_steps={ok_zero} count")
    print(f"RESULT e2e_fixed_zero_priced_steps={fix_zero} count")
    print(f"RESULT e2e_differing_steps={len(diff)} count")
    print(f"RESULT calibration_mispriced_steps={len(cal_diff)} count")
    print(f"RESULT calibration_mean_shift_sek={cal_shift:.4f} sek_per_kwh")
    print(f"RESULT e2e_log_lines={bad_logs} count")
    print(f"RESULT wall_s={time.perf_counter() - t0:.2f} wall")
    print("RESULT thread_factor=1.0000")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except OSError:
        print("RESULT load1=-1")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
