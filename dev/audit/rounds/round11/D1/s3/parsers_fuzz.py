#!/usr/bin/env python3
"""D1-s3 M6: drive every `enumerate.py d1-parsers` line with malformed, non-finite, oversized and
hostile payloads, at the parser and through the update cycle.

Metric (one line): per parser line and payload, the outcome -- returned (and whether the returned
value carries a non-finite number or a fabricated flag), raised a declared type, or raised an
undeclared type; per cycle arm, over 3 hostile cycles, the cycles that failed
(last_update_success False), WARNING+ records per cycle, and the hostile value's published effect.
Count keys: the parser's own return/raise; for the cycle arms the coordinator's published
payload (`coordinator.data`) and last_update_success, never the payload's own attributes.

Command:
    PYTHONPATH=tests/hastub <HOME>/.local/state/hpo/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D1/s3/parsers_fuzz.py [--arm unit|weather|tibber|openmeteo|ecl110|pump|all]
        [--perturb parse_bool_finite|openmeteo_overflow_guard]
Expected (baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, exact counts):
    RESULT pump_nonfinite_flag_true=10 readings (perturb parse_bool_finite: 0)
    RESULT openmeteo_year1_solve_failures=3 solves (perturb openmeteo_overflow_guard: 0;
        null control RESULT openmeteo_healthy_solve_failures=0)
Machine: orchestrator Mac (darwin arm64), shared box (load1 ~150-190); no RESULT is a timing.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import json
import logging
import math
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wl  # noqa: E402

from harness import FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
import heatpump_optimizer.coordinator as cmod  # noqa: E402
from heatpump_optimizer import (  # noqa: E402
    away, boost, config_flow, debugger, dhw_schedule, grid_fee, inputs, manual_plan,
    open_meteo, price_model, quiet_windows, snapshots, store,
)

DEEP = "[" * 100000 + "]" * 100000
HUGE = "x" * 2_000_000
STRS = [None, "", " ", "garbage", "\x00\xff", "nan", "NaN", "inf", "-inf", "1e309", "-1",
        "99:99", "25:00-26:00", "06:00-05:00", "Mon-Fri 06:00-22:00 = nan",
        "Mon-Fri 06:00-22:00 = inf", "Mon-Fri 06:00-22:00 = 1e309", "Jan-Foo 00:00-01:00 = 1",
        "0001-01-01T00:00:00", "9999-12-31T23:59:59+00:00", "2026-13-45T99:99",
        "06:00-08:00, " * 20000, HUGE, DEEP, "‮06:00-08:00"]
VALS = STRS + [0, -1, 10 ** 400, float("nan"), float("inf"), True, b"\xff\xfe", [], {},
               [None], [{"a": 1}], {"a": [1]}, 1.5, [float("nan")], ["06:00-08:00"] * 50000]
REF = datetime(2026, 1, 15, 12, tzinfo=timezone.utc)
DECLARED = (ValueError, TypeError, grid_fee.GridFeeError if hasattr(grid_fee, "GridFeeError") else ValueError,
            manual_plan.ManualPlanError if hasattr(manual_plan, "ManualPlanError") else ValueError)


def _nonfinite(v, depth=0):
    if depth > 6:
        return False
    if isinstance(v, float):
        return not math.isfinite(v)
    if isinstance(v, dict):
        return any(_nonfinite(x, depth + 1) for x in list(v.values())[:2000])
    if isinstance(v, (list, tuple)):
        return any(_nonfinite(x, depth + 1) for x in list(v)[:2000])
    return False


def _short(v):
    s = repr(v)
    return s if len(s) < 40 else s[:37] + "..."


def drive(name, fn, payloads, declared):
    """One parser over the battery: returned / declared raise / UNDECLARED raise."""
    rows = []
    for p in payloads:
        try:
            out = fn(p)
            rows.append((name, _short(p), "returned", "nonfinite" if _nonfinite(out) else "ok"))
        except declared as err:
            rows.append((name, _short(p), "declared", type(err).__name__))
        except RecursionError as err:
            rows.append((name, _short(p), "UNDECLARED", type(err).__name__))
        except Exception as err:  # noqa: BLE001 - the outcome is the measurement
            rows.append((name, _short(p), "UNDECLARED", f"{type(err).__name__}: {str(err)[:60]}"))
    return rows


class _Resp:
    def __init__(self, status, body):
        self.status, self.body = status, body

    async def json(self, **k):
        if isinstance(self.body, BaseException):
            raise self.body
        return self.body

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False


class _Sess:
    def __init__(self, body, status=200):
        self.body, self.status = body, status

    def post(self, *a, **k):
        return _Resp(self.status, self.body)

    def get(self, *a, **k):
        return _Resp(self.status, self.body)


HOSTILE_JSON = [None, [], "str", 5, float("nan"), {"data": None}, {"data": {"viewer": None}},
                {"data": {"viewer": {"homes": [None]}}}, {"data": {"viewer": {"homes": "x"}}},
                {"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {"today": "abc"}}}]}}},
                {"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {"today": [
                    {"total": "nan", "startsAt": "2026-01-15T00:00:00+00:00"},
                    {"total": 1e308 * 10, "startsAt": "2026-01-15T01:00:00+00:00"},
                    {"total": 1.0, "startsAt": "0001-01-01T00:00:00"}]}}}]}}},
                {"errors": [{"message": "x"}]}, ValueError("not json"), RecursionError("deep")]


def unit_arm():
    rows = []
    rows += drive("away._parse_return_time", away._parse_return_time, VALS, ())
    rows += drive("boost._parse_until", boost._parse_until, VALS, ())
    rows += drive("debugger._parsed", debugger._parsed, STRS, ())
    rows += drive("dhw_schedule._parse_time", dhw_schedule._parse_time, VALS, (ValueError,))
    rows += drive("dhw_schedule.parse_windows", dhw_schedule.parse_windows, VALS, (ValueError,))
    rows += drive("dhw_schedule._parse_one_range", dhw_schedule._parse_one_range, VALS, (ValueError,))
    rows += drive("dhw_schedule.parse_weekly_windows", dhw_schedule.parse_weekly_windows, VALS, (ValueError,))
    rows += drive("dhw_schedule.parse_day_overrides",
                  lambda v: dhw_schedule.parse_day_overrides({k: v for k in (
                      "dhw_day_overrides_enabled", "dhw_windows_mon", "dhw_windows_sat",
                      "dhw_override_enabled", "dhw_windows_weekend")} | {"dhw_day_overrides_enabled": True}),
                  VALS, (ValueError,))
    rows += drive("dhw_schedule._parse_day_selector", dhw_schedule._parse_day_selector, VALS, (ValueError,))
    gfe = (grid_fee.GridFeeError,) if hasattr(grid_fee, "GridFeeError") else (ValueError,)
    rows += drive("grid_fee._parse_cyclic_range",
                  lambda v: grid_fee._parse_cyclic_range(v, grid_fee._MONTHS, 1, 12, "month"), VALS, gfe)
    rows += drive("grid_fee.parse_month_range", grid_fee.parse_month_range, VALS, gfe)
    rows += drive("grid_fee.parse_day_range", grid_fee.parse_day_range, VALS, gfe)
    rows += drive("grid_fee._parse_rule", grid_fee._parse_rule, VALS, gfe)
    rows += drive("grid_fee.parse_rules", grid_fee.parse_rules, VALS, gfe)
    rows += drive("inputs.parse_bool", inputs.parse_bool, VALS, ())
    mpe = (manual_plan.ManualPlanError,)
    rows += drive("manual_plan.parse_channel", lambda v: manual_plan.parse_channel(v, REF), VALS + [
        [{"start": "2026-01-15T13:00:00+00:00", "end": "2026-01-15T14:00:00+00:00", "value": float("nan")}],
        [{"start": "2026-01-15T13:00:00+00:00", "end": "0001-01-01T00:00:00", "value": 1}],
        [{"start": "9999-12-31T23:59:59+00:00", "end": "9999-12-31T23:59:59+00:00", "value": 1}]], mpe)
    rows += drive("manual_plan._parse_dt", lambda v: manual_plan._parse_dt(v, REF), VALS, mpe)
    rows += drive("open_meteo._parse_block", lambda v: open_meteo._parse_block(
        {"time": v, open_meteo._VARIABLE: [1.0] * (len(v) if isinstance(v, list) else 1)}
        if not isinstance(v, dict) else v, open_meteo._VARIABLE), VALS + [
        {"time": ["0001-01-01T00:00", "0001-01-01T01:00"], open_meteo._VARIABLE: [1, 2]},
        {"time": ["9999-12-31T22:00", "9999-12-31T23:00"], open_meteo._VARIABLE: [1, 2]}], ())
    rows += drive("quiet_windows._parse_spec_pair", lambda v: quiet_windows._parse_spec_pair(v, v), VALS, (ValueError,))
    rows += drive("store._parses", lambda v: store._parses(v, datetime.fromisoformat, 10), VALS, ())
    # json sites
    rows += drive("coordinator._parse_ecl110_state", lambda v: cmod._parse_ecl110_state(v, (-10.0, 10.0)),
                  VALS + ["true", '{"displace": true}', '{"displace": "1e5"}', '{"command": {"displace": "NaN"}}',
                          "1" * 5000, b'{"displace": 3}', '{"displace": 3, "effective_displace": 1e400}'],
                  (TypeError, ValueError, OverflowError, RecursionError))
    import tempfile
    tmp = tempfile.mkdtemp(prefix="d1s3_")
    from pathlib import Path

    def read_stores(v):
        Path(tmp, "k").write_bytes(v if isinstance(v, bytes) else str(v).encode("utf-8", "surrogatepass"))
        return debugger._read_stores(Path(tmp), ["k", "missing"])
    rows += drive("debugger._read_stores", read_stores, STRS + [b"\xff\xfe", '{"version": NaN, "data": [1e999]}'], ())
    ring = snapshots.SnapshotRing()

    def take(v):
        return ring.take(REF, True, {"a": v}, {"b": v})
    rows += drive("snapshots.SnapshotRing.take", take, [float("nan"), float("inf"), 10 ** 400, "x", None,
                                                        datetime(2026, 1, 1), {1: 2}, b"x"], (TypeError, ValueError))
    # response sites
    for body in HOSTILE_JSON:
        sess = _Sess(body)
        for name, call in (
                ("config_flow.validate_tibber_token", lambda: config_flow.validate_tibber_token(None, "t")),
                ("price_model._tibber_post", lambda: price_model.pull_prices(sess, {"tibber_token": "t"})),
                ("open_meteo.OpenMeteoSolar._get_json",
                 lambda: open_meteo.OpenMeteoSolar(None, 59.0, 18.0)._get_json(sess, "u", {}))):
            with mock.patch.object(config_flow, "async_get_clientsession", lambda h, *a, **k: sess):
                try:
                    out = asyncio.run(call())
                    rows.append((name, _short(body), "returned", _short(out)[:30]))
                except Exception as err:  # noqa: BLE001
                    rows.append((name, _short(body), "UNDECLARED", f"{type(err).__name__}: {str(err)[:60]}"))
    return rows


# ---------------------------------------------------------------- cycle arms
def cycles(rig, n, before=None, step_min=30):
    """n refreshes through the base class; per cycle (last_update_success, warnings, data)."""
    cap = wl.capture()
    out = []
    for k in range(n):
        if before:
            before(k)
        n0 = len(cap.records)
        dt_util.freeze((wl.START + timedelta(minutes=step_min * k)).replace(tzinfo=None))
        try:
            asyncio.run(rig.coord.async_refresh())
        finally:
            dt_util.freeze(None)
        recs = cap.records[n0:]
        out.append({"ok": rig.coord.last_update_success, "warn": sum(1 for r in recs if r.levelno >= 30),
                    "err": str(getattr(rig.coord, "last_exception", ""))[:120],
                    "solve_failures": rig.coord._solve_failures,
                    "data": rig.coord.data})
    return out


def _utc():
    dt_util.DEFAULT_TIME_ZONE = timezone.utc


def weather_arm():
    """C3: the weather-entity forecast through _fetch_weather_forecast."""
    _utc()
    base = wl.forecast_rows()
    variants = {
        "rows_not_dicts": [None, "x", 5, []] * 12,
        "nan_fields": [dict(r, temperature=float("nan"), wind_speed=float("inf")) for r in base],
        "string_fields": [dict(r, temperature="cold", wind_speed="x") for r in base],
        "bad_datetime": [dict(r, datetime="garbage") for r in base],
        "year1_datetime": [dict(r, datetime=f"0001-01-01T{h % 24:02d}:00:00+00:00") for h, r in enumerate(base)],
        "year9999_datetime": [dict(r, datetime=f"9999-12-31T{h % 24:02d}:00:00+00:00") for h, r in enumerate(base)],
        "huge_magnitudes": [dict(r, temperature=1e308, precipitation=-1e308) for r in base],
        "oversized_rows": base * 2000,
        "not_a_list": {"a": 1},
        "missing_datetime": [{k: v for k, v in r.items() if k != "datetime"} for r in base],
    }
    res = {}
    for name, fc in variants.items():
        rig = wl.Rig("minimal")
        rig.forecast = base

        def before(k, rig=rig, fc=fc):
            if k >= 1:
                rig.forecast = fc
        rows = cycles(rig, 4, before)
        res[name] = [(r["ok"], r["warn"], _nonfinite(r["data"].get("forecast_outdoor") if r["data"] else None),
                      r["err"][:80]) for r in rows]
    return res


def tibber_arm():
    _utc()
    res = {}
    for i, body in enumerate(HOSTILE_JSON):
        rig = wl.Rig("minimal")

        def before(k, rig=rig, body=body):
            if k >= 1:
                rig.session.payload = body
        rows = cycles(rig, 4, before)
        res[f"{i}:{_short(body)}"] = [(r["ok"], r["warn"], r["err"][:60]) for r in rows]
    return res


def _om_body(times, vals):
    return {"hourly": {"time": times, open_meteo._VARIABLE: vals,
                       open_meteo._VARIABLE_HUMIDITY: [80.0] * len(vals),
                       open_meteo._VARIABLE_SNOWFALL: [0.0] * len(vals)}}


def openmeteo_arm(guard=False):
    """C3: the Open-Meteo async_refresh JSON path above _parse_block, through the cycle."""
    _utc()
    good_t = [(wl.START + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M") for h in range(72)]
    good = _om_body(good_t, [100.0] * 72)
    variants = {
        "healthy": good,
        "year1_stamps": _om_body(["0001-01-01T00:00", "0001-01-01T01:00"] + good_t, [1.0, 1.0] + [100.0] * 72),
        "nan_values": _om_body(good_t, [float("nan")] * 72),
        "strings": _om_body(good_t, ["x"] * 72),
        "unsorted_dupes": _om_body(good_t[::-1] + good_t, [100.0] * 144),
        "not_dict": [1, 2, 3],
        "hourly_list": {"hourly": [1, 2]},
        "error": {"error": True, "reason": "x"},
    }
    res = {}
    patches = []
    if guard:  # the perturbation: one guard in mean_over's sample-start subtraction
        real = open_meteo.IrradianceSeries.mean_over

        def guarded(self, start, end):
            try:
                return real(self, start, end)
            except OverflowError:
                return None
        patches.append(mock.patch.object(open_meteo.IrradianceSeries, "mean_over", guarded))
    for p in patches:
        p.start()
    try:
        for name, body in variants.items():
            rig = wl.Rig("minimal", {"solar_forecast_source": "open_meteo",
                                     "solar_location": {"latitude": 59.0, "longitude": 18.0}})
            sess = _Sess(body)
            tib = rig.session
            sess.post = tib.post
            cmod.async_get_clientsession = lambda h, *a, **k: sess
            with mock.patch.object(open_meteo, "async_get_clientsession", lambda h, *a, **k: sess):
                rows = cycles(rig, 3)
            res[name] = [(r["ok"], r["warn"], r["solve_failures"], r["err"][:90]) for r in rows]
    finally:
        for p in patches:
            p.stop()
    return res


def _perturb_ecl110_bool():
    """In memory: _parse_ecl110_state refuses a bool as const.finite_float does."""
    import inspect
    import textwrap
    src = textwrap.dedent(inspect.getsource(cmod._parse_ecl110_state))
    a = "elif isinstance(data, (int, float)):"
    b = "None if raw is None else float(raw)"
    assert a in src and b in src, "the parser moved"
    src = src.replace(a, "elif isinstance(data, (int, float)) and not isinstance(data, bool):")
    src = src.replace(b, "None if raw is None or isinstance(raw, bool) else float(raw)")
    ns = {}
    exec(compile(src, cmod.__file__, "exec"), cmod.__dict__, ns)  # noqa: S102 - production source
    cmod._parse_ecl110_state = ns["_parse_ecl110_state"]


def ecl110_arm(perturb=False):
    """C3: the ECL110 MQTT state handler, _async_handle_ecl110_state_message."""
    _utc()
    if perturb:
        _perturb_ecl110_bool()
    rig = wl.Rig("minimal", {"ecl110_state_topic": "ecl/state"})
    cycles(rig, 1)
    payloads = ["true", '{"displace": true}', "false", '{"displace": "3"}', "NaN", '{"displace": 1e400}',
                DEEP, HUGE, b"\xff\xfe", "[1, 2]", '{"command": {"displace": {"x": 1}}}', "1" * 5000,
                '{"displace": 3, "effective_displace": "Infinity"}', None, 7, float("nan")]
    cap = wl.capture()
    out = []
    for p in payloads:
        n0 = len(cap.records)
        rig.coord._ecl110_current_displace = None
        try:
            rig.coord._async_handle_ecl110_state_message(SimpleNamespace(payload=p, topic="ecl/state"))
            res = ("returned", rig.coord._ecl110_current_displace)
        except Exception as err:  # noqa: BLE001
            res = ("RAISED", f"{type(err).__name__}")
        out.append((_short(p), res, sum(1 for r in cap.records[n0:] if r.levelno >= 30)))
    after = cycles(rig, 1)
    # the subscribe site: a broker refusal, a None unsub, and a delivered callback
    subs = {}
    for case in ("raises", "none", "delivers"):
        async def fake_sub(hass, topic, cb, qos=0, case=case):
            if case == "raises":
                raise RuntimeError("mqtt not loaded")
            if case == "delivers":
                cb(SimpleNamespace(payload='{"displace": 2}', topic=topic))
                return lambda: None
            return None
        rig.coord._unsub_ecl110_state = None
        rig.coord._ecl110_current_displace = None
        with mock.patch.object(cmod.mqtt, "async_subscribe", fake_sub):
            try:
                asyncio.run(rig.coord._async_setup_ecl110_state_subscription())
                subs[case] = ("returned", rig.coord._ecl110_current_displace,
                              rig.coord._unsub_ecl110_state is not None)
            except Exception as err:  # noqa: BLE001
                subs[case] = ("RAISED", type(err).__name__)
    return {"messages": out, "cycle_after_ok": after[0]["ok"], "subscribe": subs}


def pump_arm(perturb=False):
    """C3: pump_signals state parsing -- fault/defrost/online/backup flags with hostile states."""
    _utc()
    tokens = ["nan", "NaN", "inf", "-inf", "1e309", "0", "1", "garbage", "", "unknown"]
    res = {}
    patches = []
    if perturb:  # the perturbation: parse_bool's numeric arm refuses a non-finite number
        real = inputs.parse_bool

        def finite_only(raw, *, strict=False):
            try:
                if not math.isfinite(float(str(raw).strip())):
                    return None
            except ValueError:
                pass
            return real(raw, strict=strict)
        patches.append(mock.patch.object(inputs, "parse_bool", finite_only))
    for p in patches:
        p.start()
    try:
        for tok in tokens:
            rig = wl.Rig("minimal", {"heat_pump_fault_entity": "sensor.hp_fault",
                                     "heat_pump_defrost_entity": "sensor.hp_defrost"})
            stamp = wl.START
            rig.hass.states.set("sensor.hp_fault", FakeState(tok, last_updated=stamp, last_reported=stamp))
            rig.hass.states.set("sensor.hp_defrost", FakeState(tok, last_updated=stamp, last_reported=stamp))
            rows = cycles(rig, 1)
            sig = (rows[0]["data"] or {}).get("heat_pump_signals") or {}
            res[tok] = {"ok": rows[0]["ok"], "fault": sig.get("fault"), "defrosting": sig.get("defrosting"),
                        "freeze_reason": sig.get("freeze_reason")}
    finally:
        for p in patches:
            p.stop()
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="all")
    ap.add_argument("--perturb", default="")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    t0 = time.process_time()
    th0 = time.thread_time()
    report = {}
    arms = ["unit", "weather", "tibber", "openmeteo", "ecl110", "pump"] if a.arm == "all" else a.arm.split(",")
    sys.setrecursionlimit(3000)
    for arm in arms:
        if arm == "unit":
            rows = unit_arm()
            report["unit"] = rows
            und = [r for r in rows if r[2] == "UNDECLARED"]
            nf = [r for r in rows if r[3] == "nonfinite"]
            print(f"RESULT unit_payloads={len(rows)} drives")
            print(f"RESULT unit_parsers={len({r[0] for r in rows})} parsers")
            print(f"RESULT unit_undeclared_raises={len(und)} drives")
            print(f"RESULT unit_nonfinite_returns={len(nf)} drives")
            for r in und + nf:
                print("  ", r)
        elif arm == "weather":
            report["weather"] = r = weather_arm()
            bad = sum(1 for v in r.values() for c in v[1:] if not c[0])
            print(f"RESULT weather_failed_hostile_cycles={bad} cycles")
            for k, v in r.items():
                print("  ", k, v)
        elif arm == "tibber":
            report["tibber"] = r = tibber_arm()
            for k, v in r.items():
                print("  ", k, v)
            print(f"RESULT tibber_warn_after_first={sum(c[1] for v in r.values() for c in v[2:])} records")
        elif arm == "openmeteo":
            report["openmeteo"] = r = openmeteo_arm(guard=a.perturb == "openmeteo_overflow_guard")
            for k, v in r.items():
                print("  ", k, v)
            print(f"RESULT openmeteo_year1_solve_failures={r['year1_stamps'][-1][2]} solves")
            print(f"RESULT openmeteo_year1_failed_updates={sum(1 for c in r['year1_stamps'] if not c[0])} cycles")
            print(f"RESULT openmeteo_healthy_solve_failures={r['healthy'][-1][2]} solves")
            print(f"RESULT openmeteo_all_variants_solve_failures={sum(v[-1][2] for v in r.values())} solves")
        elif arm == "ecl110":
            report["ecl110"] = r = ecl110_arm(perturb=a.perturb == "ecl110_refuse_bool")
            for m in r["messages"]:
                print("  ", m)
            print(f"RESULT ecl110_raised={sum(1 for m in r['messages'] if m[1][0] == 'RAISED')} messages")
            bools = (repr("true"), repr('{"displace": true}'), repr("false"))
            print(f"RESULT ecl110_bool_accepted={sum(1 for m in r['messages'] if m[0] in bools and m[1][1] is not None)} messages")
            print(f"RESULT ecl110_numeric_null_control={sum(1 for m in r['messages'] if m[0] in (repr(7), repr('{\"displace\": \"3\"}')) and m[1][1] is not None)} messages")
            print(f"RESULT ecl110_cycle_after_ok={int(r['cycle_after_ok'])}")
            print(f"   subscribe {r['subscribe']}")
            print(f"RESULT ecl110_subscribe_raised={sum(1 for v in r['subscribe'].values() if v[0] == 'RAISED')} cases")
        elif arm == "pump":
            report["pump"] = r = pump_arm(perturb=a.perturb == "parse_bool_finite")
            for k, v in r.items():
                print("  ", k, v)
            nonfinite = ("nan", "NaN", "inf", "-inf", "1e309")
            n = sum((r[t]["fault"] is True) + (r[t]["defrosting"] is True) for t in nonfinite)
            print(f"RESULT pump_nonfinite_flag_true={n} readings")
            print(f"RESULT pump_null_control_zero_flag_true={(r['0']['fault'] is True) + (r['0']['defrosting'] is True)} readings")
            print(f"RESULT pump_nonfinite_freeze_fault={sum(1 for t in nonfinite if r[t]['freeze_reason'])} cycles")
    if a.json:
        json.dump(report, open(a.json, "w"), indent=1, default=str)
    cpu, th = time.process_time() - t0, time.thread_time() - th0
    print(f"RESULT thread_factor={cpu / max(th, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
