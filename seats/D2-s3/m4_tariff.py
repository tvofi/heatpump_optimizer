"""D2.M4 tariff and price identities, every cell of the step.

Run (the zone is read once at import, so it is set on the command line):
  HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D2/s3/m4_tariff.py [--perturb NAME]
Perturbations (each moves exactly its named RESULT to zero):
  --perturb weekday   FeeRule.applies tests datetime.weekday()      -> fee_mismatch_steps to_zero
  --perturb minor     normalize_price_per_kwh divides minor units by 100 -> unit_mismatches to_zero
  --perturb tomorrow  prices_from_tibber_payload also reads 'tomorrow'   -> tibber_rows_dropped to_zero
  --perturb oneperday _one_per_day keeps each day's highest window       -> tracker_peak_err to_zero
  --perturb topk      _exact_topk_sum takes the k largest                -> peak_cost_err to_zero
  --perturb realhours ledger.month_hours counts the month's real hours   -> coverage_full_23h to 1.0

Metric definitions (one line each), count keyed on the production value delivered:
  fold_err            = max_step |coordinator._price_series step price - time mean of the entries over [s, s+15min)|
  fold_sum_err        = |sum(step price*0.25 h) - integral of the entry series over the horizon|
  dst_steps           = steps of the local day priced by _price_series against its real quarter count (92/100/96)
  coverage_full       = ledger.coverage_factor of a month settled every real hour (identity: 1.0)
  peak_cost_err       = |OptimizationResult.peak_cost - price/k * sum(k largest window excesses)| (distinct_days off)
  tracker_peak_err    = |PeakTracker.billed_peak_kw - mean of the 3 highest per-day window maxima| (distinct_days on)
  capacity_line_err   = |ledger capacity line after book_capacity twice - price*billed peak|
  fee_mismatch_steps  = quarter steps of one week where GridFeeSchedule.fee_vector != the rule text's calendar meaning
  unit_mismatches     = units among the price grammar where prices_from_entity_attributes' total != value * true factor
  tibber_rows_dropped = rows of a today+tomorrow Tibber payload not returned by prices_from_tibber_payload
  pv_piecewise_err    = max |energy_cost_fn(P) - sum(export*min(P,s) + import*max(P-s,0))*dt| over random P, s
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B6 (shared).
"""
import _common  # noqa: F401
from _common import footer, np

import argparse
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ap = argparse.ArgumentParser()
ap.add_argument("--perturb", default="")
ap.add_argument("--section", default="")
A = ap.parse_args()

sys.path.insert(0, "custom_components")
import harness  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import grid_fee, inputs as inputs_mod, ledger, price_model, tariff  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
import heatpump_optimizer.coordinator as coord_mod  # noqa: E402
import golden  # noqa: E402
import profiles  # noqa: E402

STHLM = ZoneInfo("Europe/Stockholm")
UTC = timezone.utc
assert dt_util.DEFAULT_TIME_ZONE is not None and str(dt_util.DEFAULT_TIME_ZONE) == "Europe/Stockholm", \
    "run with HASTUB_TZ=Europe/Stockholm"

# ---- perturbations (in memory) -------------------------------------------
if A.perturb == "weekday":
    def _applies(self, when):
        if self.months is not None and when.month not in self.months:
            return False
        if self.days is not None and when.weekday() not in self.days:
            return False
        if self.hours is not None:
            if not grid_fee.hour_in_windows(when.hour + when.minute / 60.0, list(self.hours)):
                return False
        return True
    grid_fee.FeeRule.applies = _applies
if A.perturb == "minor":
    _orig_norm = inputs_mod.normalize_price_per_kwh

    def _norm(value, unit):
        out = _orig_norm(value, unit)
        if out is not None and unit and str(unit).partition("/")[0].strip().lower() in inputs_mod.PRICE_MINOR_UNITS:
            out /= 100.0
        return out
    price_model.normalize_price_per_kwh = _norm
if A.perturb == "oneperday":
    def _opd(ranked):
        best, undated = {}, []
        for kw, day in ranked:
            if not day:
                undated.append((kw, day))
            elif day not in best or kw > best[day][0]:
                best[day] = (kw, day)
        return undated + list(best.values())
    tariff._one_per_day = _opd
if A.perturb == "realhours":
    def _real_month_hours(now):
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        nxt = (start + timedelta(days=32)).replace(day=1)
        return (nxt.astimezone(UTC) - start.astimezone(UTC)).total_seconds() / 3600.0
    ledger.month_hours = _real_month_hours
if A.perturb == "topk":
    tariff._exact_topk_sum = lambda excess, k: float(np.sum(np.sort(excess)[-k:]))

RES = {}


def res(name, value, unit):
    RES[name] = (value, unit)


# ---- helpers ---------------------------------------------------------------
def coord_with(entries, **cfg):
    base = {"tibber_token": "x", "weather_entity": "weather.home",
            "target_temperature": 21.0, "min_temperature": 17.0, "max_temperature": 23.0}
    base.update(cfg)
    c = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=base))
    c._prices = entries
    return c


def day_values(shape, day_local, quarters):
    """The profile's 96 quarter prices for one local day (its own hour-of-day clock)."""
    p = profiles.prices(shape, datetime(2026, 1, 15))
    return [float(p[q]) for q in range(96)]


def entries_for(shape, first_local_midnight, days, resolution):
    """Entries walked in UTC from a local midnight, priced by local wall clock."""
    rows = []
    step = timedelta(minutes=15 if resolution == "15min" else 60)
    t = first_local_midnight.astimezone(UTC)
    end = (first_local_midnight + timedelta(days=days + 1)).replace(hour=0).astimezone(UTC)
    vals = day_values(shape, None, None)
    while t < end:
        loc = t.astimezone(STHLM)
        q = loc.hour * 4 + (loc.minute // 15)
        rows.append({"total": vals[q] + 0.001 * loc.day, "starts_at": loc.isoformat(), "level": "NORMAL"})
        t += step
    return rows


def entry_mean(rows, s, e):
    """Time mean of the step-function entry series over [s, e), UTC instants."""
    starts = [datetime.fromisoformat(r["starts_at"]).astimezone(UTC) for r in rows]
    vals = [r["total"] for r in rows]
    tot, w = 0.0, 0.0
    for i, st in enumerate(starts):
        en = starts[i + 1] if i + 1 < len(starts) else st + (st - starts[i - 1])
        lo, hi = max(st, s), min(en, e)
        if hi > lo:
            sec = (hi - lo).total_seconds()
            tot += vals[i] * sec
            w += sec
    return tot / w if w else float("nan"), w


def price_series(c, now_local, n):
    dt_util.freeze(now_local)
    try:
        midnight = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        start = now_local.replace(minute=(now_local.minute // 15) * 15, second=0, microsecond=0)
        offset = int(round((start - midnight).total_seconds() / 900)) if False else 0
        out = c._price_series(n, start, 0)
        return out, start
    finally:
        dt_util.freeze(None)


# ---- 1. price folding ------------------------------------------------------
SHAPES = ["flat", "shoulder", "summer_negative", "summer_typical", "winter_extreme",
          "winter_moderate", "winter_narrow", "winter_typical"]
worst_fold = 0.0
worst_sum = 0.0
if A.section in ("", "fold"):
    for shape in SHAPES:
        for resol in ("15min", "hourly"):
            day0 = datetime(2026, 1, 14, tzinfo=STHLM)
            rows = entries_for(shape, day0, 2, resol)
            c = coord_with(rows)
            cell_fold, cell_sum = 0.0, 0.0
            for now in (datetime(2026, 1, 14, 0, 7, tzinfo=STHLM), datetime(2026, 1, 14, 13, 37, tzinfo=STHLM)):
                (prices, known, _sig), start = price_series(c, now, 96)
                n = int(known.sum())
                s0 = start.astimezone(UTC)
                errs, integ = [], 0.0
                for i in range(n):
                    s = s0 + timedelta(minutes=15 * i)
                    m, _ = entry_mean(rows, s, s + timedelta(minutes=15))
                    errs.append(abs(prices[i] - m))
                    integ += m * 0.25
                cell_fold = max(cell_fold, max(errs))
                cell_sum = max(cell_sum, abs(float(np.sum(prices[:n]) * 0.25) - integ))
            worst_fold, worst_sum = max(worst_fold, cell_fold), max(worst_sum, cell_sum)
            print(f"CELL price-folding price_shape={shape} resolution={resol} fold_err={cell_fold:.3e} "
                  f"fold_sum_err={cell_sum:.3e} known_steps={n}", flush=True)
res("fold_err_max", f"{worst_fold:.3e}", "currency/kWh")
res("fold_sum_err_max", f"{worst_sum:.3e}", "currency")

# ---- 2. DST and month days -------------------------------------------------
if A.section in ("", "dst"):
    days = {"23h": datetime(2026, 3, 29, tzinfo=STHLM), "25h": datetime(2026, 10, 25, tzinfo=STHLM),
            "month_boundary": datetime(2026, 1, 31, tzinfo=STHLM)}
    for label, day in days.items():
        out = []
        for resol in ("15min", "hourly"):
            rows = entries_for("winter_typical", day - timedelta(days=1), 3, resol)
            c = coord_with(rows)
            now = day.replace(hour=0, minute=7)
            (prices, known, _sig), start = price_series(c, now, 192)
            s0 = start.astimezone(UTC)
            next_mid = (day + timedelta(days=1)).replace(hour=0).astimezone(UTC)
            in_day = [i for i in range(int(known.sum())) if s0 + timedelta(minutes=15 * i) < next_mid]
            errs = [abs(prices[i] - entry_mean(rows, s0 + timedelta(minutes=15 * i),
                                               s0 + timedelta(minutes=15 * i + 15))[0]) for i in in_day]
            real_q = int((next_mid - day.astimezone(UTC)).total_seconds() // 900)
            out.append(f"{resol}:steps={len(in_day)}/{real_q},err={max(errs):.2e}")
        # coverage of the month containing the day, settled every real hour
        month_start = day.replace(day=1, hour=0)
        nm = (month_start + timedelta(days=32)).replace(day=1)
        real_hours = (nm.astimezone(UTC) - month_start.astimezone(UTC)).total_seconds() / 3600
        led = ledger.MonthlyLedger()
        t = month_start
        led.observe_meta_mean(t, ledger.SETTLED_HOURS_META, real_hours)
        led.observe_meta_mean(t, ledger.SPOT_PRICE_META, 1.0)
        meta = led.months[ledger.month_key(t)]["meta"]
        last = (nm - timedelta(minutes=1))
        cov = ledger.coverage_factor(meta, last)
        res(f"coverage_full_{label}", f"{cov:.6f}", "ratio")
        print(f"CELL dst-and-month-days day={label} {' '.join(out)} month_real_hours={real_hours:.0f} "
              f"month_hours={ledger.month_hours(last):.0f} coverage_full={cov:.6f}", flush=True)

# ---- 3. capacity peak once -------------------------------------------------
if A.section in ("", "cap"):
    from heatpump_optimizer.optimizer import HeatPumpOptimizer  # noqa: F401
    worst_pc, worst_tr, worst_line = 0.0, 0.0, 0.0
    for shape in SHAPES:
        spec = dict(golden.SCENARIOS["capacity_tariff"])
        spec = {**spec, "price_profile": shape,
                "opt_overrides": {**spec["opt_overrides"], "peak_distinct_days": False, "peak_threshold_kw": 3.0}}
        rec = _common.solve_golden("capacity_tariff", spec, keep=False)
        opt, r = rec["opt"], rec["result"]
        cfg = opt.config
        house = np.asarray(r.power_schedule) + np.asarray(r.dhw_power_schedule or np.zeros(len(r.power_schedule)))
        house = house + cfg.baseline_load_array(len(house))
        win = tariff.metering_windows(house, cfg.peak_window_minutes, cfg.dt_hours,
                                      opt._window_offset_steps(golden.START, cfg.dt_hours))
        exc = np.maximum(0.0, win - cfg.peak_threshold_kw)
        k = min(cfg.peak_count, exc.size)
        expect = cfg.peak_price_per_kw * float(np.sum(np.sort(exc)[-k:]))
        pc_err = abs(r.peak_cost - expect)
        worst_pc = max(worst_pc, pc_err)
        # realised: three days of this plan's house power through the tracker, distinct days on
        cap = tariff.CapacityTariff(enabled=True, price_per_kw=cfg.peak_price_per_kw * cfg.peak_count,
                                    window_minutes=cfg.peak_window_minutes, peaks_averaged=cfg.peak_count,
                                    distinct_days=True)
        tr = tariff.PeakTracker()
        t0 = datetime(2026, 1, 12, 0, 0, tzinfo=STHLM)
        day_max = []
        for d in range(3):
            scale = 1.0 + 0.1 * d
            for i, kw in enumerate(house):
                tr.observe(t0 + timedelta(days=d, minutes=15 * i), float(kw * scale), cap)
            day_max.append(float(np.max(tariff.metering_windows(house * scale, cfg.peak_window_minutes, 0.25, 0))))
        tr.observe(t0 + timedelta(days=3), 0.0, cap)  # close the last window
        billed = tr.billed_peak_kw(cap)
        tr_err = abs(billed - float(np.mean(sorted(day_max)[-3:])))
        worst_tr = max(worst_tr, tr_err)
        led = ledger.MonthlyLedger()
        for _ in range(2):
            led.book_capacity("2026-01", billed, cap.price_per_kw)
        line_err = abs(led.line("2026-01", "capacity")["sek"] - billed * cap.price_per_kw)
        worst_line = max(worst_line, line_err)
        print(f"CELL capacity-peak-once price_shape={shape} peak_cost={r.peak_cost:.4f} expect={expect:.4f} "
              f"peak_cost_err={pc_err:.4f} tracker_billed={billed:.4f} expect_billed={np.mean(sorted(day_max)[-3:]):.4f} "
              f"tracker_peak_err={tr_err:.4f} capacity_line_err={line_err:.2e}", flush=True)
    res("peak_cost_err_max", f"{worst_pc:.4f}", "currency")
    res("tracker_peak_err_max", f"{worst_tr:.4f}", "kW")
    res("capacity_line_err_max", f"{worst_line:.2e}", "currency")

# ---- 4. grid-fee windows ---------------------------------------------------
if A.section in ("", "fee"):
    spec = "= 0.05, Mon-Fri 06:00-22:00 = 0.25, Sat-Sun = 0.10, Nov-Mar 22:00-06:00 = 0.02"

    def truth(when):
        fee = 0.05
        wd = when.weekday()  # Monday 0, by the calendar
        h = when.hour + when.minute / 60.0
        if wd <= 4 and 6.0 <= h < 22.0:
            fee += 0.25
        if wd >= 5:
            fee += 0.10
        if when.month in (11, 12, 1, 2, 3) and (h >= 22.0 or h < 6.0):
            fee += 0.02
        return fee
    week = [datetime(2026, 1, 12, tzinfo=STHLM) + timedelta(minutes=15 * i) for i in range(7 * 96)]
    total_mis = 0
    for mode in ("entity", "none", "rules"):
        sch = grid_fee.GridFeeSchedule.from_config(
            {"grid_fee_mode": mode, "grid_fee_rules": spec, "grid_fee_fixed": 0.0})
        vec = sch.fee_vector(week, 0.31)
        if mode == "rules":
            exp = np.array([truth(w) for w in week])
        elif mode == "entity":
            exp = np.full(len(week), 0.31)
        else:
            exp = np.zeros(len(week))
        mis = np.abs(vec - exp) > 1e-12
        n_mis = int(mis.sum())
        total_mis += n_mis if mode == "rules" else 0
        by_day = {}
        for w, m in zip(week, mis):
            if m:
                by_day[w.strftime("%a")] = by_day.get(w.strftime("%a"), 0) + 1
        fee_kwh_err = float(np.sum(np.abs(vec - exp)) * 0.25)
        print(f"CELL grid-fee-windows grid_fee_mode={mode} fee_mismatch_steps={n_mis}/{len(week)} "
              f"by_day={by_day} abs_fee_err_per_kwh_hour_sum={fee_kwh_err:.3f}", flush=True)
    res("fee_mismatch_steps", total_mis, "count")

# ---- 5. currency conversion and PV export ----------------------------------
if A.section in ("", "cur"):
    truth_factor = {"SEK/kWh": 1.0, "öre/kWh": 0.01, "ore/kWh": 0.01, "øre/kWh": 0.01, "c/kWh": 0.01,
                    "ct/kWh": 0.01, "cent/kWh": 0.01, "p/kWh": 0.01, "EUR/MWh": 0.001, "€/kWh": 1.0,
                    "kr/kWh": 1.0, "öre/MWh": 0.00001, "NOK/Wh": 1000.0, None: 1.0}
    um = []
    for unit, f in truth_factor.items():
        attrs = {"unit_of_measurement": unit,
                 "raw_today": [{"start": "2026-01-14T00:00:00+01:00", "value": 123.0}]}
        rows = price_model.prices_from_entity_attributes(attrs, 1.25, 0.1)
        got = rows[0]["total"]
        want = 123.0 * f * 1.25 + 0.1
        if abs(got - want) > 1e-9 * max(1.0, abs(want)):
            um.append(f"{unit}:{got:.4g}!={want:.4g}")
    # tibber: today + tomorrow, 96 quarters each
    qrows = lambda d: [{"total": 1.0 + q / 100, "startsAt": (datetime(2026, 1, d, tzinfo=STHLM)
                        + timedelta(minutes=15 * q)).isoformat(), "level": "NORMAL"} for q in range(96)]
    payload = {"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {
        "current": qrows(14)[0], "today": qrows(14), "tomorrow": qrows(15)}}}]}}}
    if A.perturb == "tomorrow":
        _orig_tp = price_model.prices_from_tibber_payload

        def _tp(data):
            out = _orig_tp(data)
            pi = data["data"]["viewer"]["homes"][0]["currentSubscription"]["priceInfo"]
            extra = [{"total": r["total"], "starts_at": r["startsAt"], "level": "NORMAL"} for r in pi.get("tomorrow") or []]
            return out + extra
        price_model.prices_from_tibber_payload = _tp
    trows = price_model.prices_from_tibber_payload(payload)
    dropped = 192 - len(trows)
    # what the plan then knows at 14:00 on the 14th, through the coordinator fold
    c = coord_with(trows)
    (pr, kn, _s), _st = price_series(c, datetime(2026, 1, 14, 14, 0, tzinfo=STHLM), 96)
    known_steps = int(kn.sum())
    # PV piecewise (both sources share it): production energy cost closure
    rec = _common.solve_golden("shoulder", keep=False)
    opt = rec["opt"]
    rng = np.random.default_rng(4)
    prices = np.array(rec["inputs"].forecast.prices[:96], dtype=float)
    prices[10:20] = -0.2  # negative import hours, export above import
    pv_err = 0.0
    for _ in range(20):
        P = rng.uniform(0, 6, 96)
        s = rng.uniform(0, 3, 96) * (rng.uniform(size=96) > 0.3)
        opt._pv_surplus = s
        f = opt._energy_cost_fn(prices, 0.25)
        exp = float(np.sum(opt.config.pv_export_price * np.minimum(P, s) + prices * np.maximum(P - s, 0)) * 0.25)
        pv_err = max(pv_err, abs(f(P) - exp))
    print(f"CELL currency-pv-export price_source=entity unit_mismatches={len(um)} {um} pv_piecewise_err={pv_err:.2e}")
    print(f"CELL currency-pv-export price_source=tibber tibber_rows_dropped={dropped}/192 "
          f"known_steps_at_14h={known_steps}/96 pv_piecewise_err={pv_err:.2e}")
    res("unit_mismatches", len(um), "count")
    res("tibber_rows_dropped", dropped, "count")
    res("tibber_known_steps_at_14h", known_steps, "count")
    res("pv_piecewise_err", f"{pv_err:.2e}", "currency")

for k, (v, u) in RES.items():
    print(f"RESULT {k}={v} {u}")
footer()
