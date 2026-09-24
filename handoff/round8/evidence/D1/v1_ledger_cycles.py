"""D1 verifier v1 (round 8), own harness for D1-s2-01.

Metric (one line): with ONE persisted ledger leaf corrupted to a plausible
hand-edit (savings_baseline.sek = "12,5", a decimal comma) and loaded through
the real QuarantiningStore + _async_load_ledger, count of K=3 real refresh
cycles (coordinator.async_refresh -> _async_update_data, auto mode, real solve)
that end with last_update_success False; alongside: ERROR log records emitted,
cycles in which _apply_action (actuation) still ran, and whether the setup-time
first refresh (async_config_entry_first_refresh, _skip_solve_once) raises
ConfigEntryNotReady.

Arms: corrupt (current month), corrupt_old (a month 20 months back, inside
KEEP_MONTHS=24), null (same month, sek=12.5 as a float).
--perturb: fix-shaped one-site edit, in-process and restored in finally:
  MonthlyLedger.line coerces kwh/sek inside try/except (TypeError, ValueError)
  and returns zeros on failure. failed cycles must go to 0.
Command (tree root):
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D1/v1_ledger_cycles.py [--perturb]
Baseline cdf82daa; 4-vCPU shared cloud container; counts are final.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, "tools/audit/round8/D1")

from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.helpers.storage import _DISK, _reset_store_disk  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from heatpump_optimizer import ledger as lg  # noqa: E402
from v1_setback_race import config, states  # noqa: E402

PERTURB = "--perturb" in sys.argv
K = 3


class Count(logging.Handler):
    def __init__(self):
        super().__init__(logging.ERROR)
        self.n = 0

    def emit(self, record):
        self.n += 1


def month_back(n):
    now = dt_util.now()
    y, m = now.year, now.month - n
    while m <= 0:
        m += 12
        y -= 1
    return f"{y:04d}-{m:02d}"


def payload(month, sek):
    return {"ledger": {"months": {month: {
        "lines": {"savings_baseline": {"kwh": 10.0, "sek": sek},
                  "savings_actual": {"kwh": 8.0, "sek": 9.0},
                  "spot": {"kwh": 8.0, "sek": 9.0}},
        "meta": {"spot_price": {"sum": 3.0, "count": 3}}}}}}


async def arm(month, sek):
    _reset_store_disk()
    coord = cm.HeatPumpOptimizerCoordinator(FakeHass(states()), FakeEntry(data=config()))
    _DISK[coord._ledger_store._key] = json.dumps(payload(month, sek))
    await coord._async_load_ledger()
    await coord._update_current_state()
    actuations = {"n": 0}
    orig_apply = coord._apply_action

    async def counted():
        actuations["n"] += 1
        return await orig_apply()
    coord._apply_action = counted
    h = Count()
    lgr = logging.getLogger("custom_components.heatpump_optimizer")
    root = logging.getLogger()
    root.addHandler(h)
    # setup-time first refresh
    coord._skip_solve_once = True
    first_not_ready = 0
    try:
        await coord.async_config_entry_first_refresh()
    except Exception as err:  # noqa: BLE001
        first_not_ready = int(type(err).__name__ == "ConfigEntryNotReady")
    coord.last_update_success = True
    failed = 0
    errors_before = h.n
    for _ in range(K):
        await coord.async_refresh()
        failed += int(not coord.last_update_success)
    root.removeHandler(h)
    return {"failed": failed, "errors": h.n - errors_before, "actuated": actuations["n"],
            "first_not_ready": first_not_ready,
            "last_exc": type(getattr(coord.last_exception, "__cause__", None)).__name__}


def guarded_line(self, month, name):
    entry = self.months.get(month, {}).get("lines", {}).get(name)
    if not isinstance(entry, dict):
        return {"kwh": 0.0, "sek": 0.0}
    try:
        return {"kwh": float(entry.get("kwh", 0.0)), "sek": float(entry.get("sek", 0.0))}
    except (TypeError, ValueError):
        return {"kwh": 0.0, "sek": 0.0}


async def main():
    orig_line = lg.MonthlyLedger.line
    if PERTURB:
        lg.MonthlyLedger.line = guarded_line
    out = {}
    try:
        for name, month, sek in (("corrupt", month_back(0), "12,5"),
                                 ("corrupt_old", month_back(20), "12,5"),
                                 ("null", month_back(0), 12.5)):
            r = await arm(month, sek)
            print(f"  arm={name} {r}")
            out[f"{name}_failed_cycles"] = r["failed"]
            out[f"{name}_error_logs"] = r["errors"]
            out[f"{name}_actuated_cycles"] = r["actuated"]
            out[f"{name}_first_refresh_not_ready"] = r["first_not_ready"]
    finally:
        lg.MonthlyLedger.line = orig_line
        cm._shutdown_process_pool()
    return out


if __name__ == "__main__":
    pc0, tc0 = time.process_time(), time.thread_time()
    res = asyncio.run(main())
    for k, v in res.items():
        print(f"RESULT {k}={v} count")
    pc, tc = time.process_time() - pc0, time.thread_time() - tc0
    print(f"RESULT thread_factor={pc / tc if tc else float('nan'):.3f}")
    print(f"RESULT load1={open('/proc/loadavg').read().split()[0]}")
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')]
    print(f"RESULT swapins={sw[0].split()[1] if sw else 0}")
    print(f"RESULT perturbed={int(PERTURB)}")
