#!/usr/bin/env python3
"""Issue #2674 (R10-LIVESTATE ls-r2): do the seven per-cycle writers lose an
increment to a store load still in flight?

Metric:   per lead, lost = 1 when the writer's increment is absent after the
          load resolves, 0 when it survives. Only meaningful where the writer
          writes at all (writer_wrote=1, read off the null arm); a writer that
          wrote nothing is reported as such, never as lost=0.
Count key: one probe per lead = one (load task, writer task) pair. null is the
          same writer run after the load resolved: the increment must be
          present, so null=0 means the probe can see an increment at all;
          null=1 is a broken probe, not a finding.
Command:  PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_store_load_leads.py
          from the root of the tree under test (tests/harness.py puts that
          root's custom_components first, so the cwd is the tree measured).
Null control: for every probed lead, a fresh coordinator whose load resolved
          first and whose writer ran second.
Perturbation: the tree under test (make the writer await the store's
          async_wait_for_read, or move the load ahead of the writer, and the
          lost figure must move), and the in-harness gate opener: a lead that
          is closed by reading is also run with the baseline the first cycle
          lacks (previous sample, pending prediction, boosted state), printed
          as <lead>_gate_open_*, so a "closed" lead is shown closed by exactly
          that gate and not by a dead probe.

Line kinds:
  RESULT <lead>_closed_by=<gate>   the writer cannot run before its load
        resolves on the first refresh; the gate is a function and condition.
        Backed by <lead>_fresh_call_writes (the writer called on a fresh
        coordinator moves nothing the load replaces: must be 0) and the
        first_refresh_* / baseline_assignments_* lines.
  RESULT <lead>_lost=<0|1> null=<0|1>   the race probe, where the writer runs.
  lost gives the writer five loop turns before the read lands;
        concurrent_lost the recipe's ordering (writer as a task, one yield,
        then the event, both awaited); wrote_before_read whether the writer
        moved the reading before the read landed (0 for a writer that waits).

Expected at baseline de794b537 (origin/main), macOS seat venv 3.14:
          price_shape_lost=1 null=0 and extra_legionella_observer_lost=1 null=0
          (the light setup refresh reaches the price fold; the observer needs
          no baseline); the six other leads closed_by their gate, with
          fresh_call_writes=0 and gate_open lost=1 null=0. At R10-PARAMS-OWNER's
          head both writers await the read: price_shape_lost=0 and
          extra_legionella_observer_lost=0, null 0, the rest unchanged.
GatedStore models QuarantiningStore.async_wait_for_read (return once the read
in flight has landed), so a writer that waits is measured waiting; no arm
awaits a writer before releasing the read, which would deadlock a waiting one.
Origin: R10-PARAMS-OWNER's #2674 probe-role seat.
"""
from __future__ import annotations

import asyncio
import inspect
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))

from harness import FakeEntry, FakeHass  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

PKG = ROOT / "custom_components" / "heatpump_optimizer"


class GatedStore:
    """A store whose async_load waits on an Event and then returns a payload."""

    bounded: dict = {}

    def __init__(self, payload: dict | None, open_: bool = False) -> None:
        self.payload = payload
        self.event = asyncio.Event()
        self.reading = False
        if open_:
            self.event.set()

    async def async_load(self):
        self.reading = True
        try:
            await self.event.wait()
            return self.payload
        finally:
            self.reading = False

    async def async_save(self, data):
        return None

    async def async_save_if_changed(self, data):
        return None

    async def async_wait_for_read(self):
        # QuarantiningStore's contract: return once the read in flight, if
        # any, has landed -- so a writer that waits is seen waiting.
        if self.reading:
            await self.event.wait()
            await asyncio.sleep(0)

    def async_delay_save(self, *a, **k):
        return None


def new_coord() -> HeatPumpOptimizerCoordinator:
    return HeatPumpOptimizerCoordinator(
        FakeHass(),
        FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home"}),
    )


class Lead:
    name = ""

    def setup(self, c, store): raise NotImplementedError
    def loader(self, c): raise NotImplementedError
    def payload(self): raise NotImplementedError
    def open_gate(self, c): pass
    def writer(self, c): raise NotImplementedError
    def reading(self, c): raise NotImplementedError
    def stored_reading(self): raise NotImplementedError


class BufferCooling(Lead):
    name = "buffer_cooling"

    def setup(self, c, store): c._thermal_learning_store = store
    def loader(self, c): return c._async_load_thermal_learning
    def payload(self): return {"buffer_cooling_rate": 1.0, "buffer_cooling_samples": 5}

    def open_gate(self, c):
        c._last_buffer_temp_sample = 55.0
        c._last_buffer_sample_time = dt_util.now() - timedelta(hours=1.0)
        c._buffer_heating_since_sample = False

    def writer(self, c): return lambda: c._async_learn_buffer_cooling(54.0)
    def reading(self, c): return c._buffer_cooling_samples
    def stored_reading(self): return 5


class DhwDynamics(Lead):
    name = "dhw_dynamics"

    def setup(self, c, store): c._dhw_learner.profile_store = store
    def loader(self, c): return c._dhw_learner.async_load_profile
    def payload(self): return {"cooling_rate": 1.0, "cooling_samples": 5}

    def open_gate(self, c):
        learner = c._dhw_learner
        learner.last_temp_sample = 55.0
        learner.last_sample_time = dt_util.now() - timedelta(hours=1.0)
        learner.heating_since_sample = False

    def writer(self, c): return lambda: c._dhw_learner.async_learn_dynamics(54.0)
    def reading(self, c): return c._dhw_learner.cooling_samples
    def stored_reading(self): return 5


_STORED_AT = "2026-01-01T00:00:00+00:00"
_STORED_TS = datetime.fromisoformat(_STORED_AT).timestamp()


class LegionellaCycle(Lead):
    name = "legionella_cycle"

    def setup(self, c, store): c._legionella.store = store
    def loader(self, c): return c._legionella.async_load
    def payload(self): return {"last_cycle": _STORED_AT, "last_attempt": _STORED_AT}

    def open_gate(self, c):
        # A boost commanded last cycle that has closed now, with a peak seen.
        lg = c._legionella
        lg._params.dhw_legionella_enabled = True
        lg.boost_active = True
        lg.boost_started = dt_util.now() - timedelta(hours=1.0)
        lg.boost_peak = 50.0
        c._current_action = {"dhw_reason": "untagged"}

    def writer(self, c): return lambda: c._legionella.async_track_cycle(50.0)

    def reading(self, c):
        a = c._legionella.attempt
        return None if a is None else int(a.timestamp())

    def stored_reading(self): return int(_STORED_TS)


class LegionellaObserver(LegionellaCycle):
    """Not one of the seven leads: the observer async_track also writes the
    state async_load replaces (last_cycle). Probed because it shares the load."""

    name = "extra_legionella_observer"

    def open_gate(self, c):
        c._legionella._params.dhw_legionella_temp = 60.0

    def writer(self, c): return lambda: c._legionella.async_track(61.0)

    def reading(self, c):
        a = c._legionella.last_cycle
        return None if a is None else int(a.timestamp())


def _full_day_entries(day: str) -> list[dict]:
    return [{"starts_at": f"{day}T{h:02d}:00:00+00:00", "total": 0.5 + 0.1 * (h % 7)}
            for h in range(24)]


class PriceShape(Lead):
    name = "price_shape"
    DAY = "2026-03-10"

    def setup(self, c, store): c._price_model_store = store
    def loader(self, c): return c._async_load_price_model
    def payload(self): return {"model": {}, "days_seen": ["2026-01-01"], "quarter_days_seen": []}
    def open_gate(self, c): c._prices = _full_day_entries(self.DAY)

    def writer(self, c):
        c._prices = _full_day_entries(self.DAY)
        return c._async_learn_price_shape

    def reading(self, c): return int(self.DAY in c._price_learner.days_seen)
    def stored_reading(self): return 0


def _seed_pending(c) -> None:
    c._pending_prediction = {
        "when": dt_util.now() - timedelta(minutes=30),
        "power": 1.0, "space_power": 0.6, "dhw_power": 0.4,
        "price": 1.0, "spot_price": 0.8, "grid_fee": 0.2, "predicted_temp": 20.0,
    }
    c._measured_power = 1.0


class _Settle(Lead):
    def open_gate(self, c): _seed_pending(c)

    def writer(self, c):
        async def run():
            c._record_accuracy()
        return run


class EnergyTotals(_Settle):
    name = "energy_totals"
    KEY = "space_energy_kwh"

    def setup(self, c, store): c._energy_store = store
    def loader(self, c): return c._async_load_energy_totals
    def payload(self): return {self.KEY: 5.0}
    def reading(self, c): return round(c._energy_totals[self.KEY], 6)
    def stored_reading(self): return 5.0


class Ledger(_Settle):
    name = "ledger"

    def setup(self, c, store): c._ledger_store = store
    def loader(self, c): return c._async_load_ledger
    def payload(self): return {"ledger": {"months": {}}}

    def reading(self, c):
        return sum(len(m.get("lines", {})) for m in c._ledger.as_dict()["months"].values())

    def stored_reading(self): return 0


class Accuracy(_Settle):
    name = "accuracy"

    def setup(self, c, store): c._accuracy_store = store
    def loader(self, c): return c._async_load_accuracy
    def payload(self): return {"accuracy": {"samples": []}}
    def reading(self, c): return len(c._accuracy.as_dict()["samples"])
    def stored_reading(self): return 0


LEADS = [BufferCooling(), DhwDynamics(), LegionellaCycle(), PriceShape(),
         EnergyTotals(), Ledger(), Accuracy(), LegionellaObserver()]

GATES = {
    "buffer_cooling":
        "_async_learn_buffer_cooling:previous_temp_is_None_or_previous_time_is_None"
        "(_last_buffer_temp_sample_init_None,_assigned_only_inside_it)",
    "dhw_dynamics":
        "DhwProfileLearner.async_learn_dynamics:previous_temp_is_None_or_previous_time_is_None"
        "(last_temp_sample_init_None,_assigned_only_inside_it)",
    "legionella_cycle":
        "LegionellaGuard.async_track_cycle:commanded_false_and_boost_active_false"
        "(_current_action_init_{},_boost_active_init_False,_plan_adopted_after_learners)",
    "energy_totals":
        "_record_accuracy:pending_is_None,_then_0.05<=elapsed<=2.0"
        "(_pending_prediction_init_None,_first_set_at_end_of__record_accuracy)",
    "ledger":
        "_record_accuracy:pending_is_None,_then_0.05<=elapsed<=2.0"
        "(_pending_prediction_init_None,_first_set_at_end_of__record_accuracy)",
    "accuracy":
        "_record_accuracy:pending_is_None,_then_0.05<=elapsed<=2.0"
        "(_pending_prediction_init_None,_first_set_at_end_of__record_accuracy)",
}


async def race(lead: Lead, c, store, *, writer_first_completes: bool) -> None:
    load_task = asyncio.ensure_future(lead.loader(c)())
    await asyncio.sleep(0)
    writer_task = asyncio.ensure_future(lead.writer(c)())
    if writer_first_completes:
        await writer_task
        store.event.set()
        await load_task
    else:
        await asyncio.sleep(0)
        store.event.set()
        await asyncio.gather(load_task, writer_task)


async def probe(lead: Lead, gate_open: bool) -> dict[str, int]:
    c = new_coord()
    store = GatedStore(lead.payload())
    lead.setup(c, store)
    if gate_open:
        lead.open_gate(c)
    before = lead.reading(c)
    load_task = asyncio.ensure_future(lead.loader(c)())
    await asyncio.sleep(0)
    writer_task = asyncio.ensure_future(lead.writer(c)())
    for _ in range(5):  # the writer's whole run, unless it waits for the read
        await asyncio.sleep(0)
    wrote_before_read = int(lead.reading(c) != before)
    store.event.set()
    await asyncio.gather(load_task, writer_task)

    c2 = new_coord()
    s2 = GatedStore(lead.payload())
    lead.setup(c2, s2)
    if gate_open:
        lead.open_gate(c2)
    await race(lead, c2, s2, writer_first_completes=False)
    lost_conc = int(lead.reading(c2) == lead.stored_reading())

    c3 = new_coord()
    s3 = GatedStore(lead.payload(), open_=True)
    lead.setup(c3, s3)
    await lead.loader(c3)()
    if gate_open:
        lead.open_gate(c3)
    await lead.writer(c3)()
    null = int(lead.reading(c3) == lead.stored_reading())
    wrote = int(not null)  # the writer moves the reading at all (null arm)
    lost = int(wrote and lead.reading(c) == lead.stored_reading())
    return {"wrote": wrote, "lost": lost, "lost_conc": lost_conc, "null": null,
            "wrote_before_read": wrote_before_read}


async def fresh_call_writes(lead: Lead) -> int:
    c = new_coord()
    lead.setup(c, GatedStore(lead.payload(), open_=True))
    before = lead.reading(c)
    await lead.writer(c)()
    return int(lead.reading(c) != before)


def static_facts() -> list[str]:
    src = inspect.getsource(coord_mod.HeatPumpOptimizerCoordinator._async_first_refresh_light)
    writers = ["_async_learn_buffer_cooling", "async_learn_dynamics", "async_track_cycle",
               "_async_learn_price_shape", "_accumulate_energy", "_record_accuracy",
               "_ledger.add", "_accuracy.record"]
    called = [w for w in writers if w in src]
    init_src = (PKG / "__init__.py").read_text(encoding="utf-8")
    coord_src = (PKG / "coordinator.py").read_text(encoding="utf-8")
    dhw_src = (PKG / "dhw_learning.py").read_text(encoding="utf-8")
    skip = int(bool(re.search(r"skip_first_solve\s*=\s*True", init_src)))
    return [
        f"RESULT first_refresh_light_reaches_writers={','.join(called) or 'none'}",
        f"RESULT setup_passes_skip_first_solve={skip}",
        "RESULT baseline_assignments__last_buffer_temp_sample="
        f"{len(re.findall(r'self\._last_buffer_temp_sample\s*=', coord_src))}"
        " (1 init + 1 inside _async_learn_buffer_cooling expected)",
        "RESULT baseline_assignments__pending_prediction="
        f"{len(re.findall(r'self\._pending_prediction\s*=', coord_src))}"
        " (1 init + 1 at the end of _record_accuracy expected)",
        "RESULT baseline_assignments_dhw_last_temp_sample="
        f"{len(re.findall(r'self\.last_temp_sample\s*=', dhw_src))}"
        " (1 init + 1 inside async_learn_dynamics expected)",
    ]


async def main() -> None:
    for line in static_facts():
        print(line)
    for lead in LEADS:
        closed = lead.name in GATES
        if closed:
            print(f"RESULT {lead.name}_closed_by={GATES[lead.name]}")
            print(f"RESULT {lead.name}_fresh_call_writes={await fresh_call_writes(lead)}")
        r = await probe(lead, gate_open=closed or lead.name.startswith("extra_"))
        tag = "gate_open_" if closed else ""
        print(f"RESULT {lead.name}_{tag}writer_wrote={r['wrote']}")
        print(f"RESULT {lead.name}_{tag}lost={r['lost']} null={r['null']}"
              f" concurrent_lost={r['lost_conc']} wrote_before_read={r['wrote_before_read']}")
        if lead.name == "price_shape":
            c = new_coord()
            s = GatedStore(lead.payload())
            lead.setup(c, s)
            load = asyncio.ensure_future(lead.loader(c)())
            await asyncio.sleep(0)
            writer = asyncio.ensure_future(lead.writer(c)())
            await asyncio.sleep(0)
            s.event.set()
            await asyncio.gather(load, writer)
            lost_before = int(lead.reading(c) == 0)
            lead.open_gate(c)
            await c._async_learn_price_shape()
            print("RESULT price_shape_refold_next_cycle_recovers="
                  f"{int(lost_before and lead.reading(c) == 1)} (lost_before={lost_before})")


asyncio.run(main())
