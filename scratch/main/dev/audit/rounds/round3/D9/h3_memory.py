"""D9 round 3 / H3 -- retained bytes per cycle, and the solve worker's RSS.

METRICS (from tools/audit/briefs/D9.md, verbatim where it fixes them):
  retained_bytes   = deep sys.getsizeof of every coordinator collection after
                     N cycles, reported as a SLOPE per cycle (bytes/cycle),
                     plus tracemalloc's traced total over the same N cycles,
                     plus ru_maxrss growth of this process.
  worker_rss_kib   = resident set size of the persistent child interpreter
                     coordinator._ensure_worker() spawns, read from `ps -o rss=`
                     after one real solve has gone through the process route.
                     This is the memory the integration adds to the host on top
                     of Home Assistant's own interpreter, permanently.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round3/D9/h3_memory.py

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, Apple M1,
python 3.11.5 / numpy 2.4.6 / scipy 1.17.1; two runs at load1 21.2 and 33.1):
  priced.cycles                         = 6       +-0
  priced.coordinator_collections        = 24      +-0     (exact)
  priced.deep_sizeof_slope_b_per_cycle  = -4      +-400   -> NO unbounded
  flat.deep_sizeof_slope_b_per_cycle    = +8      +-400      collection
  priced.traced_slope_b_per_cycle       = 5.1e4   +-20 %  (churn, not a leak)
  priced.traced_peak_bytes              = 4.98e5  +-20 %
  bare_interpreter_rss_kib              = 15680-15936     the RSS floor
  priced.worker_rss_kib                 = 43744-61552     PROVISIONAL (RSS),
      i.e. the persistent solve worker holds ~28-46 MiB above a bare
      interpreter, for the ~29.98 of every 30 minutes it is idle.

PERTURBATION: HPO_D9_CYCLES=<n> changes the cycle count; a genuine per-cycle
retention shows a slope that does not move with n, an artefact shows a slope
that does.  HPO_D9_NOWORKER=1 skips the process route; worker_rss_kib must
then be reported as 0 and the parent RSS must rise instead.

NULL CONTROL: the flat price profile runs the same cycles with no price
signal; a retention slope that only exists in the priced arm would be an
artefact of the arm.

INSTRUMENTED SYMBOLS: HeatPumpOptimizerCoordinator._async_update_data,
HeatPumpOptimizerCoordinator._build_data_dict,
coordinator._ensure_worker / coordinator._await_optimize.
"""
from __future__ import annotations

import asyncio
import gc
import json
import os
import resource
import subprocess
import sys
import tracemalloc

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round3", "D9"))
import d9lib  # noqa: E402
from d9lib import result, telemetry  # noqa: E402

CYCLES = int(os.environ.get("HPO_D9_CYCLES", "6"))
NOWORKER = os.environ.get("HPO_D9_NOWORKER") == "1"


def deep_sizeof(obj, seen=None) -> int:
    if seen is None:
        seen = set()
    oid = id(obj)
    if oid in seen:
        return 0
    seen.add(oid)
    size = sys.getsizeof(obj, 0)
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            size += deep_sizeof(k, seen) + deep_sizeof(v, seen)
    elif isinstance(obj, (list, tuple, set, frozenset)):
        for v in list(obj):
            size += deep_sizeof(v, seen)
    elif hasattr(obj, "__dict__"):
        size += deep_sizeof(vars(obj), seen)
    return size


def coordinator_collections(coord) -> dict[str, int]:
    """Every list/dict/set attribute the coordinator holds, deep-sized."""
    out = {}
    for name, value in list(vars(coord).items()):
        if isinstance(value, (list, dict, set, tuple)):
            out[name] = deep_sizeof(value)
    return out


def rss_kib(pid: int) -> int:
    try:
        out = subprocess.run(
            ["ps", "-o", "rss=", "-p", str(pid)],
            capture_output=True, text=True, timeout=20,
        ).stdout.strip()
        return int(out) if out else -1
    except Exception:  # noqa: BLE001
        return -1


def run(name: str, profile: str) -> None:
    from heatpump_optimizer import coordinator as C

    hass, coord = d9lib.build_coordinator(profile=profile)

    async def _noop(*a, **k):
        return None

    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop
    coord._async_learn_price_shape = _noop

    restore = d9lib.inline_solves() if NOWORKER else (lambda: None)
    try:
        # cycle 1: warm every lazily built structure, then take the baseline
        data = asyncio.run(coord._async_update_data())
        gc.collect()
        base_coll = coordinator_collections(coord)
        base_total = sum(base_coll.values())
        base_rss = rss_kib(os.getpid())
        tracemalloc.start()
        t0 = tracemalloc.get_traced_memory()[0]
        for _ in range(CYCLES):
            data = asyncio.run(coord._async_update_data())
        t1, tpeak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        gc.collect()
        end_coll = coordinator_collections(coord)
        end_total = sum(end_coll.values())
        end_rss = rss_kib(os.getpid())
    finally:
        restore()

    result(f"{name}.cycles", CYCLES, "count")
    result(f"{name}.data_dict_bytes", len(json.dumps(data, default=str).encode()), "bytes")
    result(f"{name}.coordinator_collections", len(end_coll), "count")
    result(f"{name}.deep_sizeof_after_1_cycle", base_total, "bytes")
    result(f"{name}.deep_sizeof_after_n_cycles", end_total, "bytes")
    result(
        f"{name}.deep_sizeof_slope_b_per_cycle",
        (end_total - base_total) / CYCLES,
        "bytes",
    )
    result(f"{name}.traced_slope_b_per_cycle", (t1 - t0) / CYCLES, "bytes")
    result(f"{name}.traced_peak_bytes", tpeak, "bytes")
    result(f"{name}.parent_rss_growth_kib", end_rss - base_rss, "KiB")
    result(f"{name}.parent_rss_kib", end_rss, "KiB")

    # the five collections that grew most, so a slope has a name attached
    grew = sorted(
        ((end_coll[k] - base_coll.get(k, 0), k) for k in end_coll),
        reverse=True,
    )
    for i, (delta, key) in enumerate(grew[:5]):
        result(f"{name}.grew{i}", f"{key}={delta / CYCLES:.1f}", "bytes/cycle")

    worker = C._PROCESS_WORKER
    if worker is not None and worker.poll() is None:
        result(f"{name}.worker_pid_alive", 1, "bool")
        result(f"{name}.worker_rss_kib", rss_kib(worker.pid), "KiB")
    else:
        result(f"{name}.worker_pid_alive", 0, "bool")
        result(f"{name}.worker_rss_kib", 0, "KiB")


def bare_interpreter_rss() -> int:
    """A python3 that imported nothing but the stdlib -- the RSS floor."""
    code = (
        "import os,subprocess;"
        "print(subprocess.run(['ps','-o','rss=','-p',str(os.getpid())],"
        "capture_output=True,text=True).stdout.strip())"
    )
    out = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=60
    ).stdout.strip()
    return int(out) if out else -1


def main() -> None:
    result("baseline_sha", "ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1", "sha")
    result("noworker", int(NOWORKER), "bool")
    result("self_maxrss_kib", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024, "KiB")
    result("bare_interpreter_rss_kib", bare_interpreter_rss(), "KiB")

    print("-- priced arm")
    run("priced", "tibber_like")
    print("-- NULL CONTROL: flat price profile")
    run("flat", "flat")

    result(
        "self_maxrss_kib_end",
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024,
        "KiB",
    )
    telemetry()


if __name__ == "__main__":
    main()
