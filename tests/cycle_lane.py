#!/usr/bin/env python3
"""The coordinator-cycle lane: per-cycle cost of a real coordinator update.

Finding D9-s3-02: the stress gate reads the solver and one-shot peaks, so a
2x regression in a PER-CYCLE quantity of
``HeatPumpOptimizerCoordinator._async_update_data`` (solves per cycle, bytes
published, bytes retained between cycles, GIL yields, loop-side Python calls)
left every gate reading unchanged. This script drives one warm-up cycle and
four measured cycles of a real coordinator (FakeHass, the three fetchers
no-ops, the worker pipe ``_run_in_process`` replaced by an inline call so the
solve is countable) on five sweep scenarios and compares five readings with
``tests/cycle_budgets.json``:

  solves      entries to optimizer._multi_start_minimize; FAIL above record
  payload_b   bytes of json.dumps(returned dict); FAIL above 1.5 x record
  retained_b_per_cycle
              tracemalloc current after gc.collect(), mean consecutive
              difference after warm-up; FAIL above max(1.5 x record,
              RETAIN_FLOOR_B)
  yields      optimizer sleep calls; FAIL below record / 1.5
  loop_calls  Python calls in coordinator.py frames, solve excluded;
              FAIL above 1.5 x record

Every channel is a count or bytes, never a time, so the lane is
contention-immune and runs with the parallel lanes.

    PYTHONPATH=tests/hastub python3 tests/cycle_lane.py [--record|--self-check|--arm X]

``--record`` writes the budgets; ``--arm`` (clean, solves2x, payload2x,
retain, noyield) injects a 2x regression that must redden its own channel;
``--self-check`` runs every arm in a subprocess and passes only if each arm
fails on its own channel and the clean arm passes.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import contextlib  # noqa: E402
import copy  # noqa: E402
import gc  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import tracemalloc  # noqa: E402
from datetime import timedelta  # noqa: E402

_argv = sys.argv
sys.argv = [_argv[0]]
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import stress  # noqa: E402
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from heatpump_optimizer import optimizer as opt  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

sys.argv = _argv

BUDGETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cycle_budgets.json")
LABELS = ["winter/1z/space", "winter/1z/dhw", "winter/2z/dhw",
          "heavy_old/shoulder", "winter/cycle"]
CHANNELS = ("solves", "payload_b", "retained_b_per_cycle", "yields", "loop_calls")
ARMS = ("clean", "solves2x", "payload2x", "retain", "noyield")
OWN_CHANNEL = {"solves2x": "solves", "payload2x": "payload_b",
               "retain": "retained_b_per_cycle", "noyield": "yields"}
WARMUP, MEASURED = 1, 4
RATIO = 1.5
# Set from the maximum of five clean runs plus the record run (1184-3393
# B/cycle here; percycle's own clean arms read up to 8406) with 2x the larger
# of those as headroom, so a clean run never flaps; the `retain` arm reads
# ~190 kB/cycle.
RETAIN_FLOOR_B = 16384

_C = {"msm": 0, "yield": 0, "calls": 0, "in_solve": False, "noyield": False,
      "replay": None, "record": []}
_LEAK: list = []
_real_sleep = time.sleep


def _sleep(s):
    """Count sleeps whose caller is optimizer.py (covers `_time_mod.sleep`,
    the same module attribute, and the function-local `import time` site)."""
    if sys._getframe(1).f_code.co_filename.endswith("optimizer.py"):
        if _C["noyield"]:
            return
        _C["yield"] += 1
    _real_sleep(s)


def _profile(frame, event, _arg):
    if (event == "call" and not _C["in_solve"]
            and frame.f_code.co_filename.endswith("coordinator.py")):
        _C["calls"] += 1


def _inline_run(fn, a):
    """Run the worker call inline. In the memory pass the solves recorded by
    the counting pass are replayed instead: tracemalloc slows a solve ~13x
    and the retained bytes concern the coordinator, not the solver."""
    if _C["replay"] is not None:
        return copy.deepcopy(_C["replay"].pop(0))
    _C["in_solve"] = True
    try:
        r = fn(*a)
        _C["record"].append(r)
        return r
    finally:
        _C["in_solve"] = False


@contextlib.contextmanager
def instrument(arm_name):
    orig_msm = opt._multi_start_minimize

    def msm(*a, **k):
        _C["msm"] += 1
        return orig_msm(*a, **k)

    saved = [(opt, "_multi_start_minimize", orig_msm), (time, "sleep", _real_sleep),
             (cm, "_run_in_process", cm._run_in_process)]
    opt._multi_start_minimize = msm
    time.sleep = _sleep
    cm._run_in_process = _inline_run
    C = cm.HeatPumpOptimizerCoordinator

    def swap(obj, attr, val):
        saved.append((obj, attr, getattr(obj, attr)))
        setattr(obj, attr, val)

    if arm_name == "solves2x":
        orig = cm.optimize_in_process

        def twice(optimizer, inputs):
            orig(optimizer, inputs)
            return orig(optimizer, inputs)
        swap(cm, "optimize_in_process", twice)
    elif arm_name in ("payload2x", "retain"):
        orig_b = C._build_data_dict

        def build(self, *a, **k):
            d = orig_b(self, *a, **k)
            if arm_name == "payload2x":
                d["_dup"] = copy.deepcopy(dict(d))
            else:
                _LEAK.append(copy.deepcopy(d))
            return d
        swap(C, "_build_data_dict", build)
    elif arm_name == "noyield":
        _C["noyield"] = True
    try:
        yield
    finally:
        _C["noyield"] = False
        for obj, attr, val in reversed(saved):
            setattr(obj, attr, val)
        _LEAK.clear()


def measure(label: str, trace: bool) -> dict:
    combo = next(c for c in stress.sweep_combinations() if c["label"] == label)
    cold = combo.get("season", "winter") == "winter"
    t_out = -3.0 if cold else 6.0
    cfg = {"tibber_token": "x", "weather_entity": "weather.home",
           "dhw_tank_volume": 200.0 if combo.get("dhw") else 0.0,
           "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
           "two_zone_mode": "on" if combo.get("two_zone") else "off"}
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.0"))
    hass.states.set("sensor.outdoor", FakeState(str(t_out)))
    coord = cm.HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))
    hour = dt_util.now().replace(minute=0, second=0, microsecond=0)
    coord._prices = [{"total": round(0.6 + 0.5 * (h % 12) / 12, 4), "level": "NORMAL",
                      "starts_at": (hour + timedelta(hours=h - 2)).isoformat()}
                     for h in range(50)]
    coord._weather_forecast = [
        {"datetime": (hour + timedelta(hours=h)).isoformat(), "temperature": t_out - 2.0,
         "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0} for h in range(48)]

    async def nf():
        return None
    coord._fetch_tibber_prices = coord._fetch_weather_forecast = nf
    coord._fetch_solar_forecast = nf
    rows, mem = [], []

    async def go():
        await asyncio.gather(*getattr(hass, "_tasks", []))
        if trace:
            tracemalloc.start()
        for _ in range(WARMUP + MEASURED):
            m0, y0, c0 = _C["msm"], _C["yield"], _C["calls"]
            sys.setprofile(_profile)
            try:
                d = await coord._async_update_data()
            finally:
                sys.setprofile(None)
            rows.append((_C["msm"] - m0, len(json.dumps(d, default=str).encode()),
                         _C["yield"] - y0, _C["calls"] - c0))
            del d
            gc.collect()
            if trace:
                mem.append(tracemalloc.get_traced_memory()[0])
        if trace:
            tracemalloc.stop()
    asyncio.run(go())
    rows = rows[WARMUP:]
    mem = mem[WARMUP:]
    diffs = [b - a for a, b in zip(mem, mem[1:])]
    return {"solves": max(r[0] for r in rows), "payload_b": max(r[1] for r in rows),
            "retained_b_per_cycle": int(sum(diffs) / len(diffs)) if diffs else 0,
            "yields": max(r[2] for r in rows), "loop_calls": max(r[3] for r in rows)}


def measure_label(label: str) -> dict:
    """Counting pass (real solves, no tracemalloc), then the memory pass."""
    _C["record"], _C["replay"] = [], None
    out = measure(label, False)
    _C["replay"] = _C["record"]
    try:
        out["retained_b_per_cycle"] = measure(label, True)["retained_b_per_cycle"]
    finally:
        _C["replay"] = None
    return out


def limit_and_ok(ch: str, v, rec):
    """(limit, ok) for one reading against its record."""
    if ch == "solves":
        return rec, v <= rec
    if ch == "yields":
        lim = rec / RATIO
        return round(lim, 1), v >= lim
    lim = RATIO * rec
    if ch == "retained_b_per_cycle":
        lim = max(lim, RETAIN_FLOOR_B)
    return round(lim), v <= lim


def run(arm_name: str, record: bool) -> tuple[int, int, list]:
    budgets = {}
    if not record:
        with open(BUDGETS) as f:
            budgets = json.load(f)
    out, results, bad, total = {}, [], 0, 0
    with instrument(arm_name):
        for label in LABELS:
            out[label] = measure_label(label)
    for label in LABELS:
        for ch in CHANNELS:
            v = out[label][ch]
            if record:
                continue
            total += 1
            row = budgets.get(label)
            if row is None:
                print(f"RESULT {label} {ch}={v} record=MISSING limit=- FAIL")
                bad += 1
                results.append((label, ch, False))
                continue
            lim, ok = limit_and_ok(ch, v, row[ch])
            bad += not ok
            results.append((label, ch, ok))
            print(f"RESULT {label} {ch}={v} record={row[ch]} limit={lim} {'ok' if ok else 'FAIL'}")
    if record:
        rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                             text=True).stdout.strip()
        with open(BUDGETS, "w") as f:
            json.dump({**out, "recorded_at": rev}, f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"recorded {len(out)} scenarios to {BUDGETS}")
    return total, bad, results


def self_check() -> int:
    fails = 0
    for arm_name in ARMS:
        p = subprocess.run([sys.executable, __file__, "--arm", arm_name],
                           capture_output=True, text=True, env=os.environ)
        failed = {ln.split()[2].split("=")[0] for ln in p.stdout.splitlines()
                  if ln.startswith("RESULT") and ln.endswith("FAIL")}
        want = OWN_CHANNEL.get(arm_name)
        ok = (p.returncode == 0 and not failed) if want is None else want in failed
        fails += not ok
        print(f"SELF-CHECK {arm_name}: failed channels={sorted(failed) or 'none'} "
              f"{'ok' if ok else 'FAIL'}")
    print("SELF-CHECK PASSED" if not fails else f"SELF-CHECK FAILED {fails} arm(s)")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--arm", choices=ARMS, default="clean")
    args = ap.parse_args()
    if args.self_check:
        return self_check()
    total, bad, _ = run(args.arm, args.record)
    if args.record:
        return 0
    if bad:
        print(f"FAILED {bad} of {total} checks")
        return 1
    print(f"ALL {total} checks PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
