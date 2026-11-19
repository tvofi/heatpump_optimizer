"""D9-s1 solves_per_cycle, diagnose path: full solves one diagnose press costs.

Metric: entries into optimizer._multi_start_minimize (and optimize_in_process
worker jobs, and their solver thread CPU) between the start and the return
of HeatPumpOptimizerCoordinator.async_diagnose_interval -- the diagnose
button's and service's entry -- on a coordinator that has run warm cycles.
Keyed on entries into the production solver symbol, tagged at
coordinator._await_process (job function qualname).

Command (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D9/s1/h_diagnose_refresh.py

Arms (5 houses x 2): two_zone_dhw, single_zone_dhw, single_zone (no DHW),
two_zone_dhw + price tiles, two_zone_dhw + priced duty switch; each press
measured at baseline and under the perturbation.
Perturbation (in memory, the coordinator instance): async_request_refresh
inside async_diagnose_interval replaced by async_set_updated_data(
_build_data_dict()) -- publishes the stored diagnosis without a cycle ->
msm per press must go to ZERO and the diagnosis must still be published
(insight.last_diagnosis present in coordinator.data).
Null control: the diagnosis job itself (diagnosis.diagnose_record) enters
the solver 0 times (printed as diagnose_record_msm).

Expected: baseline msm per press >= 1 (the main solve, 2 entries on a
two-zone DHW house), perturbed 0. Counts exact; CPU provisional.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B1 container.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections import defaultdict  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402
from datetime import timedelta  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d9s1lib as L  # noqa: E402

F_PI = 5.0


async def press(arm, extra, house_kw, duty, perturb):
    from heatpump_optimizer import coordinator as cm
    from heatpump_optimizer import duty_switch
    from heatpump_optimizer import optimizer as om
    from homeassistant.util import dt as dtu
    from profiles import house

    loop = asyncio.get_running_loop()
    pool = ThreadPoolExecutor(max_workers=2)
    hass = L.make_loop_hass(loop, pool)
    dtu.freeze(L.CYCLE_NOW)
    cfg = dict(house(**house_kw))
    cfg.update(extra)
    coord = L.make_coordinator(hass, cfg, entry_id=f"dg_{arm}_{int(perturb)}")
    tags: list = []
    undo = L.inline_worker(tags)
    real_pf = duty_switch.planner_fields
    if duty:
        duty_switch.planner_fields = lambda c: {
            "duty_switch_stop_probability": (0.5, 0.5),
            "duty_switch_off_seconds": (300.0, 300.0)}
    msm = defaultdict(int)
    real_msm = om._multi_start_minimize

    def hook(*a, **k):
        msm[L.TAG[0].split("|")[-1]] += 1
        return real_msm(*a, **k)

    om._multi_start_minimize = hook
    try:
        for i in range(3):  # warm cycles: a settled interval to diagnose
            now = L.CYCLE_NOW + timedelta(minutes=30 * i)
            dtu.freeze(now)
            L.feed(coord, now)
            coord.data = await coord._async_update_data()
        now = L.CYCLE_NOW + timedelta(minutes=30 * 2 + 7)
        dtu.freeze(now)
        if perturb:
            async def publish_only():
                # what DataUpdateCoordinator.async_set_updated_data does
                # (the stub lacks it): set data, notify listeners, no cycle
                coord.data = coord._build_data_dict()
                coord.async_update_listeners()
            coord.async_request_refresh = publish_only
        m0 = sum(msm.values())
        j0 = len(tags)
        t0 = time.process_time()
        report = await coord.async_diagnose_interval()
        cpu = time.process_time() - t0
        jobs = tags[j0:]
        published = isinstance(coord.data, dict) and (
            (coord.data.get("insight") or {}).get("last_diagnosis") is not None
            or coord.data.get("last_diagnosis") is not None)
        diag_msm = msm.get("diagnose_record", 0)
        return {"msm": sum(msm.values()) - m0, "jobs": len(jobs),
                "job_names": ",".join(sorted({j[1] for j in jobs})),
                "cpu": cpu, "report": report is not None, "published": published,
                "diag_msm": diag_msm}
    finally:
        om._multi_start_minimize = real_msm
        duty_switch.planner_fields = real_pf
        undo()
        pool.shutdown()


def main():
    from heatpump_optimizer import const
    arms = {
        "two_zone_dhw": ({}, {"two_zone": True, "dhw": True}, False),
        "single_zone_dhw": ({}, {"two_zone": False, "dhw": True}, False),
        "single_zone": ({}, {"two_zone": False, "dhw": False}, False),
        "two_zone_dhw_tiles": ({const.CONF_PRICE_TILES_ENABLED: True},
                               {"two_zone": True, "dhw": True}, False),
        "two_zone_dhw_duty": ({const.CONF_CYCLING_COST: 2.0},
                              {"two_zone": True, "dhw": True}, True),
    }
    swap0 = L.swapins()
    base_counts = []
    for arm, (extra, hk, duty) in arms.items():
        if not hk["dhw"]:
            extra = {**extra}
        for perturb in (False, True):
            r = asyncio.run(press(arm, extra, hk, duty, perturb))
            tag = f"{arm}." + ("perturbed" if perturb else "baseline")
            L.result(f"{tag}.msm_per_press", r["msm"], "count")
            L.result(f"{tag}.worker_jobs_per_press", r["jobs"], "count")
            L.result(f"{tag}.job_names", r["job_names"] or "-", "list")
            L.result(f"{tag}.process_cpu_per_press_s", r["cpu"], "s")
            L.result(f"{tag}.diagnosis_returned", int(r["report"]), "bool")
            L.result(f"{tag}.diagnosis_published", int(r["published"]), "bool")
            L.result(f"{tag}.diagnose_record_msm", r["diag_msm"], "count")
            if not perturb:
                base_counts.append(r["msm"])
    L.result("cells", len(base_counts), "count")
    L.result("msm_per_press_min", min(base_counts), "count")
    L.result("msm_per_press_max", max(base_counts), "count")
    rest = sorted(base_counts)[:-1]  # the claim's most favourable cell is the max
    L.result("msm_per_press_mean", sum(base_counts) / len(base_counts), "count")
    L.result("msm_per_press_mean_drop_max", sum(rest) / len(rest), "count")
    L.result("msm_per_press_min_drop_max", min(rest), "count")
    rclock = L.Clock()
    L.result("reference_solve_cpu_ms", L.ref_ms(), "ms")
    L.tail(rclock, swap0=swap0)


if __name__ == "__main__":
    main()
