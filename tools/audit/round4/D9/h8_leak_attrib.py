"""D9 round 4 / H8 -- attribute the per-cycle allocation slope H4 measured.

H4 reported ``traced_bytes_slope_per_cycle`` around 5 kB/cycle in the
coordinator's own process while every coordinator collection's deep size
stayed flat. This harness asks WHERE those bytes live: ``tracemalloc``
snapshots taken after cycle 2 and after cycle N, differenced by
``filename:lineno`` and split into production
(``custom_components/heatpump_optimizer/``), test-stub
(``tests/``) and everything else.

A slope that lands outside production is a harness artefact and is
reported as such; only a production line is a lead.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round4/D9/h8_leak_attrib.py

EXPECTED (baseline 7dd68dd, H8_CYCLES=10): total_growth_bytes 20 000 -
80 000; the split across production / tests / other is the result.
Tolerance +/- 40 % (allocation counts wobble with dict resizing).

PERTURBATION: ``H8_PERTURB=leak`` appends a 96-float list to
``coord._prices`` each cycle from the harness; ``production_growth_bytes``
must stay put while ``other_growth_bytes`` rises by ~800 B/cycle, showing
the attribution separates a harness allocation from a production one.

BYTES ARE FINAL.
"""
from __future__ import annotations

import os

for _t in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_t, "1")

import asyncio  # noqa: E402
import sys  # noqa: E402
import tracemalloc  # noqa: E402

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round4", "D9"))

import d9common as C  # noqa: E402

from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import coordinator as CO  # noqa: E402

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round4", "D9"))
from h4_retained import build_coordinator  # noqa: E402

CYCLES = int(os.environ.get("H8_CYCLES", "10"))
PERTURB = os.environ.get("H8_PERTURB", "")
PROD = os.path.join("custom_components", "heatpump_optimizer")


def main():
    print(f"# baseline=7dd68dd  perturb={PERTURB or 'none'}  cycles={CYCLES}")
    dt_util.freeze(C.START)
    tracemalloc.start(1)
    coord = build_coordinator()
    snap0 = None
    try:
        for i in range(CYCLES):
            asyncio.run(coord._async_update_data())
            if PERTURB == "leak":
                coord._prices.append({"total": 0.0, "pad": [0.0] * 96})
            if i == 1:
                snap0 = tracemalloc.take_snapshot()
        snap1 = tracemalloc.take_snapshot()
    finally:
        dt_util.freeze(None)
    diff = snap1.compare_to(snap0, "lineno")
    buckets = {"production": 0, "tests": 0, "other": 0}
    prod_lines = []
    for st in diff:
        fn = st.traceback[0].filename if st.traceback else ""
        delta = st.size_diff
        if PROD in fn:
            buckets["production"] += delta
            if delta > 0:
                prod_lines.append((delta, f"{fn}:{st.traceback[0].lineno}"))
        elif f"{os.sep}tests{os.sep}" in fn:
            buckets["tests"] += delta
        else:
            buckets["other"] += delta
    total = sum(buckets.values())
    span = CYCLES - 2
    C.result("cycles_differenced", span, "cycles")
    C.result("total_growth_bytes", total, "bytes")
    C.result("production_growth_bytes", buckets["production"], "bytes")
    C.result("tests_growth_bytes", buckets["tests"], "bytes")
    C.result("other_growth_bytes", buckets["other"], "bytes")
    C.result("production_growth_bytes_per_cycle",
             float(buckets["production"] / span) if span else float("nan"),
             "bytes/cycle")
    prod_lines.sort(reverse=True)
    for delta, where in prod_lines[:10]:
        C.result(f"production.top.{where}", delta, "bytes")
    tracemalloc.stop()
    CO._shutdown_process_pool()
    C.telemetry()


if __name__ == "__main__":
    main()
