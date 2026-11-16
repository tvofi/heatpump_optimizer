#!/usr/bin/env python3
"""D9-s3 M2: does the stress gate see a 2x regression in a PER-CYCLE metric?

Metric (one line): for each injected 2x regression arm, (a) the per-cycle
metric it doubles, measured on a real coordinator cycle
(`heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_update_data`,
FakeHass, the worker pipe `coordinator:_run_in_process` replaced by an
in-process call so the solve is countable), and (b) every reading the stress
gate's channels take of the same tree -- `stress.build_case`'s
`solver_evals`, `solver_simulate_steps`, `solver_calls` and the tracemalloc
peak around it (the memory probe's traced arm), on five sweep scenarios --
as the arm's ratio over the clean arm. Count keys: entries into
`optimizer:_multi_start_minimize` per cycle (solves_per_cycle); JSON bytes of
the dict `_async_update_data` returns (payload_bytes); tracemalloc current
growth per cycle after a warm-up cycle (retained_bytes); calls of the
optimizer's GIL yields `time.sleep` (gil yields, the j5_gil.py lever).

Arms (each is the perturbation; `clean` is the null control):
  solves2x  coordinator's `optimize_in_process` reference runs the solve twice
  payload2x `_build_data_dict` publishes a second copy of itself
  retain    each cycle's published dict is retained on the coordinator module
  noyield   the optimizer's sleep(0.002) GIL yields become no-ops
Expected at 92d38ecb: the arm's own metric moves (solves 2 -> 4 per cycle,
payload x~2, retained growth from ~0 to ~payload bytes/cycle, yields -> 0)
while every gate reading stays at x1.000 (+/-0.01 traced) on all five
scenarios: the gate cannot see any of them.

Run (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
    dev/audit/rounds/round11/D9/s3/percycle.py [--arms clean,solves2x,...]
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: cloud box B3,
  Linux x86_64, Python 3.14 (counts and bytes final; no timing is reported).
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
import resource  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import tracemalloc  # noqa: E402
import types  # noqa: E402
from datetime import timedelta  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--arms", default="clean,solves2x,payload2x,retain,noyield")
ap.add_argument("--cycles", type=int, default=4)
args = ap.parse_args()

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

GATE_SCENARIOS = ["winter/1z/space", "winter/1z/dhw", "winter/2z/dhw",
                  "heavy_old/shoulder", "winter/cycle"]
COUNTS = {"msm": 0, "yield": 0}
_LEAK: list = []


@contextlib.contextmanager
def instrument():
    """Count `_multi_start_minimize` entries and the optimizer's yields."""
    orig_msm = opt._multi_start_minimize

    def msm(*a, **k):
        COUNTS["msm"] += 1
        return orig_msm(*a, **k)

    opt._multi_start_minimize = msm
    real_tm = opt._time_mod
    real_time = getattr(opt, "time", None)

    def make_shim(noop):
        shim = types.SimpleNamespace(**{k: getattr(real_tm, k) for k in dir(real_tm)
                                        if not k.startswith("__")})

        def sleep(s):
            # Counted only when it really yields: the noyield arm's no-op
            # sleeps are not GIL releases.
            if not noop:
                COUNTS["yield"] += 1
                real_tm.sleep(s)
        shim.sleep = sleep
        return shim

    instrument.make_shim = make_shim
    opt._time_mod = make_shim(False)
    if real_time is not None:
        opt.time = opt._time_mod
    try:
        yield
    finally:
        opt._multi_start_minimize = orig_msm
        opt._time_mod = real_tm
        if real_time is not None:
            opt.time = real_time


@contextlib.contextmanager
def arm(name):
    saved = []

    def swap(obj, attr, val):
        saved.append((obj, attr, getattr(obj, attr)))
        setattr(obj, attr, val)

    C = cm.HeatPumpOptimizerCoordinator
    if name == "solves2x":
        orig = cm.optimize_in_process

        def twice(optimizer, inputs):
            orig(optimizer, inputs)
            return orig(optimizer, inputs)
        swap(cm, "optimize_in_process", twice)
    elif name == "payload2x":
        orig_b = C._build_data_dict

        def doubled(self, *a, **k):
            d = orig_b(self, *a, **k)
            d["_d9s3_dup"] = copy.deepcopy({k2: v for k2, v in d.items()})
            return d
        swap(C, "_build_data_dict", doubled)
    elif name == "retain":
        orig_b = C._build_data_dict

        def leaky(self, *a, **k):
            d = orig_b(self, *a, **k)
            _LEAK.append(copy.deepcopy(d))
            return d
        swap(C, "_build_data_dict", leaky)
    elif name == "noyield":
        shim = instrument.make_shim(True)
        swap(opt, "_time_mod", shim)
        if hasattr(opt, "time"):
            swap(opt, "time", shim)
    try:
        yield
    finally:
        for obj, attr, val in reversed(saved):
            setattr(obj, attr, val)
        _LEAK.clear()


def coordinator_metrics(cycles: int) -> dict:
    swap_run = cm._run_in_process
    cm._run_in_process = lambda fn, a: fn(*a)
    try:
        hass = FakeHass()
        hass.states.set("sensor.indoor", FakeState("21.0"))
        hass.states.set("sensor.outdoor", FakeState("-3.0"))
        coord = cm.HeatPumpOptimizerCoordinator(hass, FakeEntry(data={
            "tibber_token": "x", "weather_entity": "weather.home",
            "dhw_tank_volume": 200.0, "indoor_temp_entity": "sensor.indoor",
            "outdoor_temp_entity": "sensor.outdoor"}))
        hour = dt_util.now().replace(minute=0, second=0, microsecond=0)
        coord._prices = [{"total": round(0.6 + 0.5 * (h % 12) / 12, 4), "level": "NORMAL",
                          "starts_at": (hour + timedelta(hours=h - 2)).isoformat()}
                         for h in range(50)]
        coord._weather_forecast = [
            {"datetime": (hour + timedelta(hours=h)).isoformat(), "temperature": -5.0,
             "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0} for h in range(48)]

        async def nf():
            return None
        coord._fetch_tibber_prices = coord._fetch_weather_forecast = nf
        coord._fetch_solar_forecast = nf
        solves, payload, yields, mem = [], [], [], []

        async def go():
            await asyncio.gather(*getattr(hass, "_tasks", []))
            tracemalloc.start()
            for _ in range(cycles):
                m0, y0 = COUNTS["msm"], COUNTS["yield"]
                d = await coord._async_update_data()
                solves.append(COUNTS["msm"] - m0)
                yields.append(COUNTS["yield"] - y0)
                payload.append(len(json.dumps(d, default=str)))
                del d
                gc.collect()
                mem.append(tracemalloc.get_traced_memory()[0])
            tracemalloc.stop()
        asyncio.run(go())
        growth = [b - a for a, b in zip(mem[1:], mem[2:])]  # first cycle is warm-up
        return {"solves_per_cycle": sum(solves[1:]) / len(solves[1:]),
                "payload_bytes": sum(payload[1:]) / len(payload[1:]),
                "retained_growth_bytes": sum(growth) / max(1, len(growth)),
                "yields_per_cycle": sum(yields[1:]) / len(yields[1:])}
    finally:
        cm._run_in_process = swap_run


def gate_readings() -> dict:
    combos = {c["label"]: {k: v for k, v in c.items() if k != "label"}
              for c in stress.sweep_combinations()}
    out = {}
    for label in GATE_SCENARIOS:
        tracemalloc.start()
        run = stress.build_case(**combos[label])
        _cur, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        out[label] = {"evals": int(run["solver_evals"]),
                      "simulate": int(run["solver_simulate_steps"]),
                      "calls": int(run["solver_calls"]),
                      "traced_mb": peak / 1048576.0}
    return out


def main() -> int:
    t0, tt0 = time.process_time(), time.thread_time()
    arms = args.arms.split(",")
    res = {}
    with instrument():
        for name in arms:
            with arm(name):
                res[name] = {"coord": coordinator_metrics(args.cycles),
                             "gate": gate_readings()}
            c = res[name]["coord"]
            print(f"ARM {name}: solves/cycle {c['solves_per_cycle']:.2f} payload "
                  f"{c['payload_bytes']:.0f} B retained growth "
                  f"{c['retained_growth_bytes']:.0f} B/cycle yields/cycle "
                  f"{c['yields_per_cycle']:.1f}", flush=True)
    clean = res.get("clean")
    for name in arms:
        c = res[name]["coord"]
        print(f"RESULT {name}_solves_per_cycle={c['solves_per_cycle']:.2f} solves")
        print(f"RESULT {name}_payload_bytes={c['payload_bytes']:.0f} bytes")
        print(f"RESULT {name}_retained_growth={c['retained_growth_bytes']:.0f} bytes/cycle")
        print(f"RESULT {name}_yields_per_cycle={c['yields_per_cycle']:.1f} calls")
        if clean is None:
            continue
        worst = {"evals": 0.0, "simulate": 0.0, "calls": 0.0, "traced_mb": 0.0}
        for label in GATE_SCENARIOS:
            g, b = res[name]["gate"][label], clean["gate"][label]
            for key in worst:
                ratio = g[key] / b[key] if b[key] else 1.0
                worst[key] = max(worst[key], abs(ratio - 1.0))
            print(f"GATE {name} {label}: evals {g['evals']}/{b['evals']} simulate "
                  f"{g['simulate']}/{b['simulate']} calls {g['calls']}/{b['calls']} "
                  f"traced {g['traced_mb']:.3f}/{b['traced_mb']:.3f} MiB")
        for key, dev in worst.items():
            print(f"RESULT {name}_gate_{key}_max_dev={dev:.4f} ratio")
    pc, tc = time.process_time() - t0, time.thread_time() - tt0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_majflt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
