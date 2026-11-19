"""D9-s1 loop_thread_work: event-loop-thread CPU per coordinator cycle (B3),
plus a per-file census of which integration files run on the loop thread
and on executor threads during a cycle (the cell universe's coverage).

Metric (D9.md): time.thread_time() on the loop thread across one
HeatPumpOptimizerCoordinator._async_update_data, the executor excluded (a
REAL ThreadPoolExecutor, never FakeHass's inline one); reported beside it:
the state-write pass HA runs on the loop for each of the 82 entities after
the update (every public property HA reads at a state write) and the JSON
encode of their attributes.

Command (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D9/s1/h_loop_thread_work.py [--cycles 6]

Perturbation (production symbol): HeatPumpOptimizerCoordinator._build_data_dict
run twice per call (in memory) -> loop_ms must go UP by about its own share.
Null control: the same cycle with the solve's executor job a no-op is not
needed for a loop-thread figure; idle loop thread_time over a 1 s sleep is
printed instead (idle_loop_ms ~ 0).
Arms: default (two-zone DHW house), tiles_fuse, all_features (tests/golden.py
coord_all_features' switches plus tiles and a 20 A fuse).
Census pass (all_features; separate, profiled; times inflated, used for attribution only):
sys.setprofile on the loop thread and threading.setprofile on executor
threads, self time per integration file.

Expected: loop_ms tens of ms per cycle on the host; Pi = x F (5, assumed).
Wall/CPU provisional. Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692;
machine: box B1 container.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import statistics  # noqa: E402
import sys  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
from collections import defaultdict  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402
from datetime import timedelta  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d9s1lib as L  # noqa: E402

F_PI = 5.0
PKG = os.sep + os.path.join("custom_components", "heatpump_optimizer") + os.sep


class Census:
    """Self time per (thread kind, integration file) via per-thread profilers."""

    def __init__(self, loop_ident):
        self.loop_ident = loop_ident
        self.self_t = defaultdict(float)
        self.calls = defaultdict(int)
        self._st = threading.local()

    def prof(self, frame, event, arg):
        if event not in ("call", "return"):
            return
        st = getattr(self._st, "s", None)
        if st is None:
            st = self._st.s = []
        now = time.thread_time()
        kind = "loop" if threading.get_ident() == self.loop_ident else "executor"
        if st:
            f, t0 = st[-1]
            self.self_t[(kind, f)] += now - t0
            st[-1] = (f, now)
        if event == "call":
            fn = frame.f_code.co_filename
            key = fn.split(PKG, 1)[1] if PKG in fn else "(other)"
            self.calls[(kind, key)] += 1
            st.append((key, now))
        elif st:
            st.pop()
            if st:
                st[-1] = (st[-1][0], now)


async def run(arm_extra, cycles, perturb=False, census=None, ents_out=None):
    from heatpump_optimizer import coordinator as cm
    from homeassistant.util import dt as dtu
    from profiles import house

    loop = asyncio.get_running_loop()
    pool = ThreadPoolExecutor(max_workers=2,
                              initializer=(lambda: (sys.setprofile(census.prof)))
                              if census else None)
    hass = L.make_loop_hass(loop, pool)
    dtu.freeze(L.CYCLE_NOW)
    cfg = dict(house(two_zone=True, dhw=True))
    cfg.update(arm_extra)
    coord = L.make_coordinator(hass, cfg, entry_id="ltw")
    tags: list = []
    undo = L.inline_worker(tags)
    ents = await L.setup_entities(hass, coord)
    real_bdd = cm.HeatPumpOptimizerCoordinator._build_data_dict
    if perturb:
        def twice(self, *a, **k):
            real_bdd(self, *a, **k)
            return real_bdd(self, *a, **k)
        cm.HeatPumpOptimizerCoordinator._build_data_dict = twice
    rows = []
    try:
        for i in range(cycles):
            now = L.CYCLE_NOW + timedelta(minutes=30 * i)
            dtu.freeze(now)
            L.feed(coord, now)
            if census and i == cycles - 1:
                sys.setprofile(census.prof)
            t0 = time.thread_time()
            data = await coord._async_update_data()
            coord.data = data
            t1 = time.thread_time()
            L.write_states(ents)
            t2 = time.thread_time()
            nbytes = L.write_states(ents, as_json=True)
            t3 = time.thread_time()
            if census and i == cycles - 1:
                sys.setprofile(None)
            rows.append(((t1 - t0) * 1e3, (t2 - t1) * 1e3, (t3 - t2) * 1e3, nbytes))
    finally:
        cm.HeatPumpOptimizerCoordinator._build_data_dict = real_bdd
        undo()
        pool.shutdown()
    if ents_out is not None:
        ents_out.append(len(ents))
    return rows


def summarise(name, rows, warm):
    rows = rows[warm:]
    loop_ms = [r[0] for r in rows]
    write_ms = [r[1] for r in rows]
    json_ms = [r[2] for r in rows]
    tot = [r[0] + r[1] + r[2] for r in rows]
    L.result(f"{name}.loop_ms_median", statistics.median(loop_ms), "ms")
    L.result(f"{name}.loop_ms_max", max(loop_ms), "ms")
    L.result(f"{name}.state_write_ms_median", statistics.median(write_ms), "ms")
    L.result(f"{name}.json_ms_median", statistics.median(json_ms), "ms")
    L.result(f"{name}.total_ms_median", statistics.median(tot), "ms")
    L.result(f"{name}.total_ms_max", max(tot), "ms")
    L.result(f"{name}.total_pi_s_max", max(tot) / 1e3 * F_PI, "s")
    L.result(f"{name}.attr_json_bytes", rows[-1][3], "bytes")


def main():
    from heatpump_optimizer import const
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=8)
    ap.add_argument("--warm", type=int, default=2)
    ap.add_argument("--no-census", action="store_true")
    a = ap.parse_args()
    swap0 = L.swapins()
    # null: idle loop thread
    t = time.thread_time()
    asyncio.run(asyncio.sleep(1.0))
    L.result("idle_loop_ms", (time.thread_time() - t) * 1e3, "ms")
    n_ents: list = []
    tiles = {const.CONF_PRICE_TILES_ENABLED: True, const.CONF_MAIN_FUSE_A: 20}
    summarise("default", asyncio.run(run({}, a.cycles, ents_out=n_ents)), a.warm)
    summarise("tiles_fuse", asyncio.run(run(tiles, a.cycles)), a.warm)
    allf = {**tiles, "peak_tariff_enabled": True, "peak_tariff_price_per_kw": 45.0,
            "pv_enabled": True, "pv_peak_kw": 8.0, "pv_export_price": 0.3,
            "away_enabled": True, "external_heat_detection_enabled": True,
            "comfort_learning_enabled": True, "system_identification_enabled": True,
            "compressor_cycling_cost": 0.5}  # tests/golden.py coord_all_features + tiles/fuse
    summarise("all_features", asyncio.run(run(allf, a.cycles)), a.warm)
    summarise("perturb_build_data_dict_x2", asyncio.run(run({}, a.cycles, perturb=True)), a.warm)
    L.result("entities", n_ents[0], "count")
    if not a.no_census:
        c = Census(threading.get_ident())
        asyncio.run(run(allf, 3, census=c))
        for kind in ("loop", "executor"):
            files = sorted(((k[1], v) for k, v in c.self_t.items() if k[0] == kind),
                           key=lambda kv: -kv[1])
            total = sum(v for _, v in files) or 1.0
            L.result(f"census.{kind}.files_touched",
                     sum(1 for f, _ in files if f != "(other)"), "count")
            for f, v in files[:12]:
                L.result(f"census.{kind}.self_share.{f}", v / total, "1")
            print(f"CENSUS {kind} " + " ".join(sorted(f for f, _ in files if f != "(other)")))
    rclock = L.Clock()
    L.result("reference_solve_cpu_ms", L.ref_ms(), "ms")
    L.result("F_assumed", F_PI, "1")
    L.tail(rclock, swap0=swap0)


if __name__ == "__main__":
    main()
