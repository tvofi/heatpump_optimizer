#!/usr/bin/env python3
"""Round 9 verify, lens V1, unit D1-2: the verifier's own measurement of each finding.

Metric (one line per finding; each RESULT names its finding):
  s4_01  of the duty-cell corruptions below (one cell, 12 buckets each), how many leave
         the bucket's derate below the healthy bucket's after N zero-duty folds, with the
         payload passed (a) straight to DefrostDerate.from_dict and (b) through the
         production store boundary store._sanitize first (what QuarantiningStore.async_load
         hands the loader in real Home Assistant); plus folds-to-recover per scalar.
  s4_02  with scipy's minimize (optimizer.minimize, one level below the finder's
         _scoped_minimize) raising on every call: does HeatPumpOptimizer.optimize return
         a plan (status 'failed (...)') or raise; and the coordinator's _solve_failures /
         repair issues after 4 cycles.
  s4_03  of 12 buckets x 4 corruptions (NaN float via _sanitize -> None, "abc", None, [])
         in one duty cell of a version-2 payload: count loaded migrated=True, and count
         of the pre-v5.3.0 INFO line.
  s5_01  cells where age_of's delivered value and InputReader._age_minutes disagree
         (None vs number), driven through the real consumers _dhw_inlet_c and
         _indoor_humidity_value at their own limits.
  s5_02  price-model tail steps with price <= 0 or > 1000x mean for hand-built finite
         out-of-domain shape bins, and PeakTracker threshold_kw / billed_peak_kw for a
         stored negative peak -- both after store._sanitize.
  s5_03  rows delivered by price_model._raw_value over 24 rows + one 10**400 row; and
         open_meteo._parse_block samples for the same.
  s5_04  quarter-hour steps of 48 h with irradiance_for None after one stray stamp at
         offsets 1, 7, 20, 45 min (the finder used 1, 5, 30).

Command:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D1/verify-v1/u2/indep_d1_2.py
Expected: see the V1 report tools/audit/round9/D1/verify-v1-2.md (exact, deterministic).
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (evidence tree 6f51db2c).
Machine: 4 vCPU cloud container (box G1-V1), CPython 3.14.0rc2, numpy 2.4.6, scipy 1.17.1.
Writes nothing.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import copy
import logging
import math
import sys
import time
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest import mock

sys.path[:0] = [".", "tests", "tests/hastub"]
_p0, _t0 = time.process_time(), time.thread_time()

import numpy as np  # noqa: E402

from custom_components.heatpump_optimizer import defrost as D  # noqa: E402
from custom_components.heatpump_optimizer import store as S  # noqa: E402
from custom_components.heatpump_optimizer import price_model as PM  # noqa: E402
from custom_components.heatpump_optimizer import tariff as T  # noqa: E402
from custom_components.heatpump_optimizer import open_meteo as OM  # noqa: E402
from custom_components.heatpump_optimizer import inputs as I  # noqa: E402
from custom_components.heatpump_optimizer import optimizer as O  # noqa: E402
from custom_components.heatpump_optimizer import coordinator as C  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

logging.getLogger().setLevel(logging.CRITICAL)
NT, NH = len(D.TEMP_EDGES) - 1, len(D.HUMIDITY_EDGES) - 1


class _Rec(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.msgs = []

    def emit(self, record):
        self.msgs.append((record.levelno, record.getMessage()))


REC = _Rec()
_pkg = logging.getLogger("custom_components.heatpump_optimizer")
_pkg.addHandler(REC)
_pkg.setLevel(logging.DEBUG)
_pkg.propagate = False


def R(name, value, unit="count"):
    print(f"RESULT {name}={value} {unit}")


# ---------------------------------------------------------------- s4_01
def healthy_defrost():
    return {
        "version": 2,
        "factors": [[1.0] * NH for _ in range(NT)],
        "counts": [[0] * NH for _ in range(NT)],
        "duty": [[0.0] * NH for _ in range(NT)],
        "duty_counts": [[50] * NH for _ in range(NT)],
        "duty_events": [[0] * NH for _ in range(NT)],
    }


SCALARS = ["nan", "inf", float("nan"), float("inf"), 1e300, 1e308, 2 ** 70, 50.0, 2.0, 1.01,
           -0.5, -1e300]


def folds_to_recover(inst, t, h, cap=20000):
    tc, hc = D.TEMP_CENTERS[t], D.HUMIDITY_CENTERS[h]
    for n in range(cap + 1):
        if inst.factor(tc, hc) >= 1.0 - 1e-9 and math.isfinite(inst.duty[t][h]) and 0 <= inst.duty[t][h] <= 1:
            return n
        inst.observe_duty(tc, hc, 0.0, 0)
    return f">{cap}"


def s4_01():
    for arm in ("direct", "via_store_boundary"):
        stuck24 = pinned24 = total = 0
        per_scalar = {}
        for s in SCALARS:
            for t in range(NT):
                for h in range(NH):
                    p = healthy_defrost()
                    p["duty"][t][h] = s
                    if arm == "via_store_boundary":
                        p = S._sanitize(p)
                    inst = D.DefrostDerate.from_dict(p)
                    tc, hc = D.TEMP_CENTERS[t], D.HUMIDITY_CENTERS[h]
                    for _ in range(24):
                        inst.observe_duty(tc, hc, 0.0, 0)
                    total += 1
                    f = inst.factor(tc, hc)
                    if f < 1.0 - 1e-9:
                        stuck24 += 1
                        if abs(f - D.DERATE_MIN) < 1e-12:
                            pinned24 += 1
                    if t == 2 and h == 1:
                        inst2 = D.DefrostDerate.from_dict(
                            S._sanitize(healthy_defrost() | {"duty": [[s if (i, j) == (2, 1) else 0.0 for j in range(NH)] for i in range(NT)]})
                            if arm == "via_store_boundary" else
                            healthy_defrost() | {"duty": [[s if (i, j) == (2, 1) else 0.0 for j in range(NH)] for i in range(NT)]})
                        per_scalar[repr(s)] = folds_to_recover(inst2, 2, 1)
        R(f"s4_01.{arm}.below_healthy_after_24_folds", f"{stuck24}/{total}")
        R(f"s4_01.{arm}.pinned_at_DERATE_MIN_after_24_folds", f"{pinned24}/{total}")
        print(f"  s4_01.{arm}.folds_to_recover {per_scalar}")
    # null control: healthy payload
    inst = D.DefrostDerate.from_dict(S._sanitize(healthy_defrost()))
    R("s4_01.null_healthy_below_1", sum(1 for t in range(NT) for h in range(NH)
                                        if inst.factor(D.TEMP_CENTERS[t], D.HUMIDITY_CENTERS[h]) < 1.0 - 1e-9))


# ---------------------------------------------------------------- s4_03
def s4_03():
    migrated = info = total = discarded = 0
    for bad in (float("nan"), "abc", None, []):
        for key in ("duty", "duty_counts"):
            for t in range(NT):
                for h in range(NH):
                    p = healthy_defrost()
                    p["duty"] = [[0.1] * NH for _ in range(NT)]
                    p[key][t][h] = bad
                    p = S._sanitize(p)
                    REC.msgs.clear()
                    inst = D.DefrostDerate.from_dict(p)
                    total += 1
                    migrated += bool(inst.migrated)
                    info += any("pre-v5.3.0" in m for _, m in REC.msgs)
                    discarded += sum(1 for row in inst.duty_counts for c in row if c == 0)
    R("s4_03.v2_one_bad_cell_migrated", f"{migrated}/{total}")
    R("s4_03.pre_v530_info_lines", f"{info}/{total}")
    R("s4_03.measured_buckets_discarded", f"{discarded}/{total * NT * NH}")
    inst = D.DefrostDerate.from_dict(S._sanitize(healthy_defrost()))
    R("s4_03.null_healthy_migrated", int(inst.migrated))
    v1 = {"factors": [[0.9] * NH for _ in range(NT)], "counts": [[5] * NH for _ in range(NT)]}
    R("s4_03.true_v1_migrated", int(D.DefrostDerate.from_dict(v1).migrated))


# ---------------------------------------------------------------- s4_02
def s4_02():
    import golden
    from harness import FakeEntry, FakeHass

    def boom(*a, **k):
        raise RuntimeError("V1 injected scipy.minimize failure")

    b = golden.make(dhw=False, hours=12)
    names = ["prices", "outdoor", "wind", "rain", "solar"]
    arrs = [np.array(b[k], dtype=float) for k in names]
    for label, dhw in (("space_only", False), ("with_dhw", True)):
        b = golden.make(dhw=dhw, hours=12)
        arrs = [np.array(b[k], dtype=float) for k in names]
        # golden builds the optimizer from the bare ``heatpump_optimizer`` package
        # (custom_components on sys.path), a distinct module object: patch THAT one.
        omod = sys.modules[type(b["optimizer"]).__module__]
        with mock.patch.object(omod, "minimize", boom):
            try:
                res = b["optimizer"].optimize(b["state"], *arrs, golden.START)
                R(f"s4_02.optimize_{label}.raised", 0)
                R(f"s4_02.optimize_{label}.status_failed", int(str(res.status).startswith("failed")), f"({res.status[:40]!r})")
            except Exception as e:  # noqa: BLE001
                R(f"s4_02.optimize_{label}.raised", 1, f"({type(e).__name__})")

    START = golden.START

    async def inline(hass, optimizer, state, *pos, **kw):
        return O.optimize_in_process(optimizer, state, pos, kw)

    scen = golden.coordinator_scenarios()
    dt_util.freeze(START)
    try:
        for arm in ("minimize_raises", "null_minimize_ok"):
            hass = FakeHass()
            coord = C.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=scen["coord_minimal"]))
            coord._prices = [{"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
                              "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
                             for h in range(48)]
            coord._weather_forecast = [{"datetime": (START + timedelta(hours=h)).isoformat(),
                                        "temperature": -3.0, "wind_speed": 2.0, "precipitation": 0.0,
                                        "humidity": 80.0} for h in range(48)]
            coord._solar_radiation_forecast = [0.0] * 48
            pats = [mock.patch.object(C, "_await_optimize", inline)]
            if arm == "minimize_raises":
                pats.append(mock.patch.object(O, "minimize", boom))
            for p in pats:
                p.start()
            statuses = []
            try:
                for _ in range(4):
                    asyncio.run(coord.async_run_optimization())
                    r = coord._optimization_result
                    statuses.append(str(r.status)[:6] if r is not None else None)
            finally:
                for p in reversed(pats):
                    p.stop()
            issues = [i for i in getattr(hass, "issues", []) if i[1] == "solve_failures"]
            R(f"s4_02.coord.{arm}.solve_failures_after_4", coord._solve_failures)
            R(f"s4_02.coord.{arm}.issues", len(issues))
            R(f"s4_02.coord.{arm}.published_failed_status", sum(1 for s in statuses if s == "failed"))
    finally:
        dt_util.freeze(None)


# ---------------------------------------------------------------- s5_01
def s5_01():
    now = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
    reader = I.InputReader(None, {}, now=lambda: now)
    try:
        reader._utcnow()
    except Exception:  # noqa: BLE001
        reader._utcnow = lambda: now
    cells = []
    # (last_updated offset min, last_reported offset min); negative offset = future
    for upd in (30, 150, 1500, 3000):
        for rep in (1, upd):
            cells.append((upd, rep))
    for fut in (-5, -120):
        cells.append((fut, fut))
    div_dhw = div_hum = 0
    ncells = 0
    dt_util.freeze(now)
    try:
        for upd, rep in cells:
            st = SimpleNamespace(
                state="12.0", attributes={"unit_of_measurement": "°C"},
                last_updated=now - timedelta(minutes=upd), last_changed=now - timedelta(minutes=upd),
                last_reported=now - timedelta(minutes=rep))
            reader_age = reader._age_minutes(st)
            hass = SimpleNamespace(states=SimpleNamespace(get=lambda _e, st=st: st))
            dhw = C._dhw_inlet_c(hass, "sensor.inlet")
            reader_dhw = reader_age is not None and reader_age <= C.DHW_INLET_MAX_AGE_MINUTES
            hum_state = SimpleNamespace(**{**vars(st), "state": "45"})
            fake = SimpleNamespace(hass=SimpleNamespace(states=SimpleNamespace(get=lambda _e: hum_state)),
                                   _config={C.CONF_INDOOR_HUMIDITY_ENTITY: "sensor.rh"})
            hum = C.HeatPumpOptimizerCoordinator._indoor_humidity_value(fake)
            reader_hum = reader_age is not None and reader_age <= C.HUMIDITY_MAX_AGE_MINUTES
            ncells += 1
            d1 = (dhw is not None) != reader_dhw
            d2 = (hum is not None) != reader_hum
            div_dhw += d1
            div_hum += d2
            print(f"  s5_01 cell upd={upd} rep={rep}: reader_age={reader_age} dhw={dhw} hum={hum} div=({int(d1)},{int(d2)})")
    finally:
        dt_util.freeze(None)
    R("s5_01.divergent_cells_dhw_inlet", f"{div_dhw}/{ncells}")
    R("s5_01.divergent_cells_indoor_humidity", f"{div_hum}/{ncells}")


# ---------------------------------------------------------------- s5_02
def s5_02():
    start = datetime(2026, 1, 14, 0, 0, tzinfo=timezone.utc)  # a Wednesday
    times = [start + timedelta(hours=i) for i in range(48)]
    known = [1.0] * 24
    for label, bins in (("null_healthy", None), ("bin_zero", 0.0), ("bin_negative", -2.0), ("bin_1e6", 1e6)):
        shapes = [[1.0] * 24 for _ in range(2)]
        if bins is not None:
            shapes[0][6] = bins
            shapes[1][6] = bins
        payload = S._sanitize({"shapes": shapes, "days": [60, 60]})
        REC.msgs.clear()
        m = PM.PriceShapeModel.from_dict(payload)
        warn = sum(1 for lv, _ in REC.msgs if lv >= logging.WARNING)
        prices, mask, sigma = PM.extend_price_series(known, 48, times, m)
        tail = prices[24:]
        bad = int(np.sum((tail <= 0) | ~np.isfinite(tail) | (tail > 1000 * np.mean(known))))
        R(f"s5_02.price.{label}.bad_tail_steps", f"{bad}/24", f"(warnings={warn})")
    tariff = T.CapacityTariff(enabled=True, price_per_kw=50.0, peaks_averaged=3)
    for label, peaks in (("null_healthy", [5.0, 4.0, 3.5]), ("one_negative", [5.0, 4.0, -2.0]),
                         ("all_negative", [-1.0])):
        REC.msgs.clear()
        tr = T.PeakTracker.from_dict(S._sanitize({"month": "2026-01", "peaks": peaks}))
        warn = sum(1 for lv, _ in REC.msgs if lv >= logging.WARNING)
        R(f"s5_02.peak.{label}.threshold_kw", f"{tr.threshold_kw(tariff):.3f}", f"kW (warnings={warn})")
        R(f"s5_02.peak.{label}.billed_peak_kw", f"{tr.billed_peak_kw(tariff):.3f}", "kW")


# ---------------------------------------------------------------- s5_03
def s5_03():
    for label, hostile in (("control_str_1e999", "1e999"), ("huge_int", 10 ** 400)):
        rows = [{"value": 0.5 + i / 100} for i in range(24)] + [{"value": hostile}]
        try:
            n = sum(1 for r in rows if PM._raw_value(r) is not None)
        except OverflowError:
            n = 0
        R(f"s5_03.raw_value_rows.{label}", f"{n}/24")
        t0 = datetime(2026, 1, 14, 0, 0)
        block = {"time": [(t0 + timedelta(hours=i)).isoformat() for i in range(25)],
                 "shortwave_radiation": [100.0] * 24 + [hostile]}
        try:
            ser = OM._parse_block(block, "shortwave_radiation")
            n = len(ser.times)
        except OverflowError:
            n = 0
        R(f"s5_03.parse_block_samples.{label}", f"{n}/24")


# ---------------------------------------------------------------- s5_04
def s5_04():
    t0 = datetime(2026, 1, 14, 0, 0, tzinfo=timezone.utc)
    for off in (None, 1, 7, 20, 45):
        times = [t0 + timedelta(hours=i) for i in range(49)]
        vals = [200.0] * 49
        if off is not None:
            times.append(t0 + timedelta(hours=10, minutes=off))
            vals.append(200.0)
        block = {"time": [t.replace(tzinfo=None).isoformat() for t in times], "shortwave_radiation": vals}
        ser = OM._parse_block(block, "shortwave_radiation")
        solar = OM.OpenMeteoSolar.__new__(OM.OpenMeteoSolar)
        solar._observed = OM._EMPTY
        solar._forecast = ser
        none = sum(1 for k in range(192)
                   if solar.irradiance_for(t0 + timedelta(minutes=15 * k), timedelta(minutes=15)) is None)
        R(f"s5_04.stray_{off}min.none_steps", f"{none}/192", f"(resolution={ser.resolution})")


for fn in (s4_01, s4_03, s4_02, s5_01, s5_02, s5_03, s5_04):
    try:
        fn()
    except Exception as e:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        R(f"{fn.__name__}.harness_error", type(e).__name__)

pc, tc = time.process_time() - _p0, time.thread_time() - _t0
R("thread_factor", f"{pc / tc if tc else 1.0:.3f}", "")
R("load1", f"{os.getloadavg()[0]:.2f}", "")
R("swapins", next((ln.split()[1] for ln in open('/proc/vmstat') if ln.startswith('pswpin')), 'unknown'), "")
