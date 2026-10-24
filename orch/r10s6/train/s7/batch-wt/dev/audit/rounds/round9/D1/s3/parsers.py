"""D1-s3 M6/M2 non-findings: hostile external inputs through the parsers in
this seat's files. Each RESULT is a count of hostile inputs for which the
production parser either raised something other than its declared refusal or
returned a non-finite / out-of-contract value (expected 0 everywhere).

  setpoint_check._setpoint_and_unit   hostile pump set-point states
  freq_control.resolve_reading        hostile frequency number/sensor states and min/max attrs
  dhw_draws.DrawStats.from_dict       200 seeded hostile persisted payloads
  silent_mode.compose                 hostile silent-mode fraction / window options
  dhw_schedule.parse_windows          hostile and oversized (100 kB) window specs -> DHWWindowError only
  manual_plan.ManualOverride          naive/aware expiry round trip, is_expired against aware now

Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/s3/parsers.py [--perturb]
  --perturb  control that the counters can move: replaces inputs._finite with
             plain float() (drops the finiteness guard), so setpoint and
             frequency counts must go up.
Expected: every *_bad=0 (exact). --perturb: setpoint_bad>0, freq_bad>0.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box B5 (cloud container, linux).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("HASTUB_TZ", "Europe/Stockholm")
import sys
import math
import random
import time
from datetime import datetime, timedelta
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
from harness import FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import setpoint_check, freq_control, silent_mode, dhw_schedule, inputs  # noqa: E402
from heatpump_optimizer.dhw_draws import DrawStats  # noqa: E402
from heatpump_optimizer.manual_plan import ManualOverride  # noqa: E402

PERTURB = "--perturb" in sys.argv
_c0, _t0 = time.process_time(), time.thread_time()
HOSTILE = ["nan", "NaN", "inf", "-inf", "Infinity", "1e309", "-1e309", "", " ", "abc",
           "unknown", "unavailable", "None", "[]", "{}", "21,5", "0x10", "1e308", "-1e308",
           "\x00", "9" * 400, None, 1e308, float("nan")]


def _fin(x):
    return x is None or (isinstance(x, (int, float)) and math.isfinite(x))


def setpoint_bad():
    bad = 0
    for raw in HOSTILE:
        for unit in (None, "°C", "°F", "K", "bogus"):
            for attr_t in (None, "nan", "inf", 55):
                attrs = {"unit_of_measurement": unit} if unit else {}
                if attr_t is not None:
                    attrs["temperature"] = attr_t
                hass = FakeHass({"number.x": FakeState(raw, attributes=attrs, unit=unit)})
                try:
                    r = setpoint_check._setpoint_and_unit(hass, "number.x")
                except Exception:
                    bad += 1
                    continue
                if r is not None and not _fin(r[0]):
                    bad += 1
    return bad


def freq_bad():
    bad = 0
    for raw in HOSTILE:
        for lo, hi in ((None, None), ("nan", "inf"), (-1e309, 1e309), ("abc", 90), (20, 90)):
            st = FakeState(raw, attributes={"min": lo, "max": hi})
            for num, sen in (("number.f", None), (None, "sensor.f"), ("number.f", "sensor.f")):
                try:
                    rep, a, b, _ = freq_control.resolve_reading(num, sen, lambda _e: st, 20.0, 90.0)
                except Exception:
                    bad += 1
                    continue
                if not (_fin(rep) and _fin(a) and _fin(b)):
                    bad += 1
    return bad


def draws_bad():
    rng = random.Random(9)
    healthy = {"reservoirs": {"morning": [1.5, 2.5, 3.0], "evening": [2.0]},
               "open_label": "morning", "open_date": "2026-01-10", "open_kwh": 1.2}
    vals = [float("nan"), float("inf"), -1e9, 1e308, "x", None, [], {}, True, "nan", -0.0]
    bad = 0
    for _ in range(200):
        p = {"reservoirs": {k: list(v) for k, v in healthy["reservoirs"].items()}, **{k: v for k, v in healthy.items() if k != "reservoirs"}}
        op = rng.randrange(4)
        if op == 0:
            p["reservoirs"]["morning"][rng.randrange(3)] = rng.choice(vals)
        elif op == 1:
            p[rng.choice(["open_kwh", "open_label", "open_date"])] = rng.choice(vals)
        elif op == 2:
            p["reservoirs"] = rng.choice(vals)
        else:
            p = rng.choice(vals)
        try:
            s = DrawStats.from_dict(p)
            ok = all(math.isfinite(e) for ev in s.reservoirs.values() for e in ev) and math.isfinite(s._open_kwh)
            for lab in list(s.reservoirs) + ["morning"]:
                q = s.quantile(lab)
                ok = ok and _fin(q)
        except Exception:
            ok = False
        bad += not ok
    return bad


def silent_bad():
    bad = 0
    t0 = datetime(2026, 1, 10, 0, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)
    for frac in ("nan", float("nan"), float("inf"), -1.0, 1e308, "x", None, 0.0, 0.5, [], {}):
        for spec in ("22:00-06:00", "garbage", "25:00-26:00", 5, None, "Mon 22:00-06:00", "22:00-06:00," * 2000):
            cfg = {"silent_mode_power_fraction": frac, "silent_mode_windows": spec}
            try:
                out = silent_mode.compose(None, cfg, t0, 96, 0.25, 6.0)
            except Exception:
                bad += 1
                continue
            if out is not None and not (np.all(np.isfinite(out)) and np.all(out <= 6.0) and np.all(out > 0)):
                bad += 1
    return bad


def windows_bad():
    bad = 0
    for spec in ("x" * 100_000, "22:00-06:00," * 10_000, "\x00", "99:99-00:00", "Mon-Sun 00:00-24:00",
                 ["22:00-06:00", 5], [None], 3.5, {"a": 1}):
        try:
            dhw_schedule.parse_windows(spec)
            dhw_schedule.parse_weekly_windows(spec)
        except dhw_schedule.DHWWindowError:
            pass
        except Exception:
            bad += 1
    return bad


def manual_bad():
    bad = 0
    now = datetime(2026, 1, 10, 6, 0, tzinfo=dt_util.DEFAULT_TIME_ZONE)
    for exp in ("2026-01-10T08:00:00", "2026-01-10T08:00:00+01:00", "2026-01-10T04:00:00"):
        try:
            o = ManualOverride.from_dict({"expires_at": exp, "space_slots": [
                {"start": "2026-01-10T06:00:00", "end": "2026-01-10T07:00:00"}]})
            o.is_expired(now)
            o.channel_pins("space", [now + timedelta(minutes=15 * i) for i in range(8)])
        except Exception:
            bad += 1
    return bad


def main():
    return {"setpoint_bad": setpoint_bad(), "freq_bad": freq_bad(), "draws_bad": draws_bad(),
            "silent_bad": silent_bad(), "windows_bad": windows_bad(), "manual_bad": manual_bad()}

if PERTURB:
    with mock.patch.object(inputs, "_finite", lambda v: float(v) if v not in (None, "") else None), \
         mock.patch.object(freq_control, "_finite", lambda v: float(v) if v not in (None, "") else None):
        try:
            res = main()
        except Exception as e:  # the unguarded float() may raise outright
            res = {"setpoint_bad": f"raised {type(e).__name__}", "freq_bad": "n/a"}
else:
    res = main()
print(f"arm={'perturb' if PERTURB else 'default'}")
for k, v in res.items():
    print(f"RESULT {k}={v} count")
cpu, thr = time.process_time() - _c0, time.thread_time() - _t0
print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = 'na'
print(f"RESULT swapins={sw}")
