"""V2 (independent) check of D9-s2-01: the #1269 sensor_advisor ranking is
recomputed on every plan-sensor state write.

Driver (own, not tests/replay.py): a coordinator with one real input-read
cycle (tests/entities.py:_honest_coordinator's two-liner, copied), the sensor
platform instantiated through the real sensor.async_setup_entry, then each
_PlanSensorBase subclass's extra_state_attributes read K times -- which is
what one async_write_ha_state of that entity evaluates.
Metric (own definition): ThermalModel.simulate_step calls and
topology.rank_sensor_advisor calls per plan-sensor attribute evaluation
(hooked, count); and CPU per evaluation with the production attribute vs with
sensor._sensor_advisor_attribute swapped for one memoised on (config,
power series) -- the fix shape -- as a saved fraction of the read, plus the
advisor CPU per evaluation over tests/stress.py:reference_solve.
Also: whether two evaluations with unchanged coordinator data return equal
rankings (a cache is lossless iff they do).
Count key: calls delivered to the production symbols.

Command (repo root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python \
      tools/audit/round9/D9/verify-v2/v2_advisor_read.py [--all-configured]
Perturbation: --all-configured configures every advisor candidate (ranking
None): simulate_step per read must go to 0. The memoised arm: calls per read
after the first -> 0.
Machine: x86_64 4-core Linux container, CPython 3.14.0rc2, OpenBLAS pinned 1.
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _v2 as V  # noqa: E402

import argparse
import asyncio
import statistics
import time

import stress
from harness import FakeHass, FakeState, FakeEntry
from heatpump_optimizer import const, sensor, topology
from heatpump_optimizer import thermal_model as tm
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

CNT = {"steps": 0, "rank": 0}
_step = tm.ThermalModel.simulate_step
_rank = topology.rank_sensor_advisor


def step(self, *a, **k):
    CNT["steps"] += 1
    return _step(self, *a, **k)


def rank(*a, **k):
    CNT["rank"] += 1
    return _rank(*a, **k)


def build(all_configured):
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    cfg = {const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
           const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
           const.CONF_DHW_TANK_VOLUME: 180.0}
    if all_configured:
        for key in topology._ADVISOR_CANDIDATES:
            cfg.setdefault(key, f"sensor.x_{key}")
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=cfg))
    asyncio.run(coord._update_current_state())
    coord.data = coord._build_data_dict()
    entry = FakeEntry(data=cfg)
    entry.runtime_data = coord
    added = []
    asyncio.run(sensor.async_setup_entry(FakeHass(), entry, lambda ents, *a: added.extend(ents)))
    plans = [e for e in added if isinstance(e, sensor._PlanSensorBase)]
    return coord, plans


def read(plans, k):
    t0 = time.thread_time()
    out = []
    for _ in range(k):
        for e in plans:
            out.append(e.extra_state_attributes.get("sensor_advisor"))
    return (time.thread_time() - t0) * 1000 / (k * len(plans)), out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all-configured", action="store_true")
    ap.add_argument("-k", type=int, default=40)
    args = ap.parse_args()
    ref = statistics.median(stress.reference_solve()[1] for _ in range(5))
    coord, plans = build(args.all_configured)
    tm.ThermalModel.simulate_step = step
    topology.rank_sensor_advisor = rank
    tag = "all_configured" if args.all_configured else "default"
    try:
        read(plans, 2)  # warm
        CNT.update(steps=0, rank=0)
        ms_prod, outs = read(plans, args.k)
        evals = args.k * len(plans)
        V.result(f"{tag}.plan_sensors", len(plans), "count")
        V.result(f"{tag}.simulate_steps_per_attr_eval", round(CNT["steps"] / evals, 2), "count (exact)")
        V.result(f"{tag}.rank_calls_per_attr_eval", round(CNT["rank"] / evals, 2), "count (exact)")
        V.result(f"{tag}.rankings_all_equal", int(all(o == outs[0] for o in outs)), "bool")
        # fix shape: memoise on (config, power series)
        orig_attr = sensor._sensor_advisor_attribute
        memo = {}

        def cached(c):
            key = (tuple(sorted((k, str(v)) for k, v in (getattr(c, "_config", {}) or {}).items())),
                   tuple((c.data or {}).get("heat_pump_power_series") or ()))
            if key not in memo:
                memo[key] = orig_attr(c)
            return memo[key]
        sensor._sensor_advisor_attribute = cached
        try:
            read(plans, 1)
            CNT.update(steps=0, rank=0)
            ms_memo, outs2 = read(plans, args.k)
        finally:
            sensor._sensor_advisor_attribute = orig_attr
        V.result(f"{tag}.memo_simulate_steps_per_attr_eval", round(CNT["steps"] / evals, 2), "count (exact)")
        V.result(f"{tag}.memo_output_equal", int(outs2 == outs), "bool")
        # alternate once more to cancel drift
        ms_prod2, _ = read(plans, args.k)
        mp = (ms_prod + ms_prod2) / 2
        V.result(f"{tag}.attr_eval_cpu_ms_prod", round(mp, 3), "ms (provisional)")
        V.result(f"{tag}.attr_eval_cpu_ms_memo", round(ms_memo, 3), "ms (provisional)")
        V.result(f"{tag}.saved_fraction_of_attr_eval", round(1 - ms_memo / mp, 4), "ratio")
        V.result(f"{tag}.advisor_cpu_per_eval_over_reference", round((mp - ms_memo) / ref, 4), "x reference_solve")
    finally:
        tm.ThermalModel.simulate_step = _step
        topology.rank_sensor_advisor = _rank
    V.result("reference_solve_cpu_ms", round(ref, 2), "ms (provisional)")
    V.trailer()


if __name__ == "__main__":
    main()
