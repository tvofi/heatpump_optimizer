#!/usr/bin/env python3
"""Recorded days, fed through the real coordinator one cycle at a time.

#1499 -- Heat Pump Action reading "off" all day while the pump heated the
tank -- was found by the owner in use, after seven audit rounds of synthetic
matrices had passed it. What those matrices never had was a day a real
install lives through: the inputs arriving together, in their real order, for
twenty-four hours. This lane replays such days.

A day is a fixture under ``tests/replay/``: the JSON ``tools/replay/export.py``
writes from a Home Assistant recorder (the config entry, and the state history
of every entity it maps). For each fixture, in its own interpreter with the
fixture's time zone:

* the clock is frozen at each cycle's instant, and every recorded input is set
  to the state it had then (``last_reported`` capped at that instant, so no
  row reports from the future);
* ``HeatPumpOptimizerCoordinator._async_update_data`` runs -- the real cycle:
  input reads, price fetch, weather fetch, solve, actuation;
* every entity the six platforms publish is read back, and judged.

WHAT IS SUBSTITUTED, and nothing else: the worker's child interpreter
(``_ensure_worker``) -- the job still goes through ``_await_optimize``, the
pickle transport and ``process_worker.run_worker``, but in this process, so
its CPU is on this process's clock (spawning the child is
``tests/deployment_shape.py``'s and ``tests/nightly_ha.py``'s subject, not this
lane's); the weather entity's ``get_forecasts`` answers from the recorded
weather itself -- the recorder keeps no forecast, so the forecast is the
weather that actually came; a Tibber install's price fetch answers from the
price sensor the export names (``price_series_entity``). A price-entity
install needs no substitution. Learned state starts from a fresh install:
the export carries no ``.storage`` store of this integration.

THE INVARIANTS, per cycle and per published entity:

``finite``           no NaN or infinity in a state or an attribute;
``unit``             the unit is one Home Assistant allows for the device
                     class, an enum's state is one of its options;
``no_default``       no temperature published as available that is a
                     ``ThermalState`` constructor default -- unless an input
                     read that same value this cycle (a real 21.0 is a
                     reading, not a default);
``agreement``        Heat Pump Action and the climate entity do not say "off"
                     while the pump runs: not ``off``/``idle`` beside
                     ``heat_pump_on``, not ``off`` while the plan's current
                     step draws (space ``power`` + ``dhw_power`` clears the
                     optimizer's own on threshold), and ``hvac_action`` not
                     idle while ``heat_pump_on`` (#1499's shape);
``cycle``            every cycle returns data and no entity property raises;

and once per fixture:

``not_frozen``       a published number that mirrors an input -- equal to it,
                     to 0.05, on at least three cycles and half the cycles
                     both were readable -- moves when that input moves by more
                     than 0.2;
``cycle_cost``       what one cycle costs (#1544: no budgeted script ran the
                     coordinator cycle). CPU is the mean process CPU of a
                     cycle -- the update and the sweep of every entity --
                     over the median ``tests/stress.py`` reference solve run
                     in the same process, so a busy or slow runner lifts
                     both; memory is the largest tracemalloc peak of one
                     cycle. Each lies in (budget / COST_DETECTION, budget]
                     of ``COST_BUDGETS``: over it is a regression, under it
                     a budget that could not see a doubling (stress.py's
                     rule). The first cycle is traced instead of timed, and
                     must run the five per-cycle files ``COST_FILES`` names.
                     ``loop_cpu_ratio`` is the event-loop thread's own share
                     (the cycle's thread CPU less its executor jobs), banded
                     the same way, because doubling a minority of the cycle
                     stays inside the whole cycle's band (R9 D9-s2-02). The lane
                     then replays the fixture three more times with the
                     cycle's CPU, its memory peak, and its loop-thread work
                     doubled in memory, and each must turn it red.

Each invariant is also driven on a hand-built bad and good record before any
fixture runs (``control:*``), so a detector that cannot fire fails here
rather than passing every night. The lane further re-runs the export's
sanitiser (and ``tests/nightly_ha.py``'s A10 coordinate rule) over every
fixture, and regenerates the synthetic fixture through
``tools/replay/synthesize.py`` and requires it byte-identical to the committed
one.

The fixture replays are nightly, never per pull request (``tests/closure.py``
NOT_A_TEST). The cheap half is not: ``tests/entities.py`` runs the controls,
the sanitiser checks and the regeneration on every pull request that touches
this file, a fixture, or ``tools/replay/``.

    python3 tests/replay.py                  # every fixture
    python3 tests/replay.py --fixture F.json --step-minutes 60
"""
from __future__ import annotations

import argparse
import asyncio
import contextlib
import dataclasses
import importlib
import io
import json
import math
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "replay"
REPLAY_TOOLS = ROOT / "tools" / "replay"
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components", REPLAY_TOOLS):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

MARK = "<<<replay-json>>>"
MIRROR_TOL = 0.05
MIRROR_MIN_HITS = 3
INPUT_MOVE = 0.2

#: Home Assistant's ``DEVICE_CLASS_UNITS`` for the device classes this
#: integration publishes, copied from upstream's sensor ``const.py``. Used only
#: when the real table is not importable (``tests/hastub`` has none).
UNITS_FALLBACK = {
    "temperature": {"°C", "°F", "K"},
    "power": {"mW", "W", "kW", "MW", "GW", "TW", "BTU/h"},
    "energy": {"mWh", "Wh", "kWh", "MWh", "GWh", "TWh", "MJ", "GJ",
               "cal", "kcal", "Mcal", "Gcal"},
    "energy_storage": {"mWh", "Wh", "kWh", "MWh", "GWh", "TWh", "MJ", "GJ",
                       "cal", "kcal", "Mcal", "Gcal"},
    "battery": {"%"},
    "frequency": {"Hz", "kHz", "MHz", "GHz"},
    "irradiance": {"W/m²", "BTU/(h⋅ft²)"},
    "volume_storage": {"L", "mL", "gal", "fl. oz.", "m³", "ft³", "CCF"},
    "enum": {None},
    "timestamp": {None},
}


def units_table() -> dict:
    try:
        from homeassistant.components.sensor.const import DEVICE_CLASS_UNITS
    except ImportError:
        return UNITS_FALLBACK
    return {str(k): {None if u is None else str(u) for u in v}
            for k, v in DEVICE_CLASS_UNITS.items()}


# --- the invariants, pure over records ----------------------------------------
#
# A record is one published entity at one cycle: entity_id, available, state,
# attributes, device_class, unit, options. Each function returns offenders.


def _nonfinite(node: object, path: str, out: list[str]) -> None:
    if isinstance(node, bool):
        return
    if isinstance(node, dict):
        for key, value in node.items():
            _nonfinite(value, f"{path}.{key}", out)
    elif isinstance(node, (list, tuple)):
        for i, value in enumerate(node):
            _nonfinite(value, f"{path}[{i}]", out)
    elif isinstance(node, (int, float)) and not math.isfinite(float(node)):
        out.append(f"{path}={node!r}")


def inv_finite(records: list[dict]) -> list[str]:
    out: list[str] = []
    for rec in records:
        _nonfinite(rec["state"], rec["entity_id"], out)
        _nonfinite(rec["attributes"], rec["entity_id"], out)
    return out


def inv_unit(records: list[dict], table: dict) -> list[str]:
    out = []
    for rec in records:
        dc = rec.get("device_class")
        if not dc or not rec["available"]:
            continue
        allowed = table.get(str(dc))
        if str(dc) == "monetary":
            unit = rec.get("unit")
            if unit is not None and not (isinstance(unit, str) and len(unit) == 3):
                out.append(f"{rec['entity_id']}: monetary unit {unit!r}")
            continue
        if allowed is not None and rec.get("unit") not in allowed:
            out.append(f"{rec['entity_id']}: {dc} in {rec.get('unit')!r}")
        if str(dc) == "enum" and rec["state"] is not None:
            options = rec.get("options")
            if options is not None and rec["state"] not in options:
                out.append(f"{rec['entity_id']}: state {rec['state']!r} not in its options")
    return out


def thermal_defaults() -> list[float]:
    from heatpump_optimizer.thermal_model import ThermalState

    state = ThermalState()
    out = []
    for field in dataclasses.fields(state):
        value = getattr(state, field.name)
        if isinstance(value, (int, float)) and not isinstance(value, bool) \
                and math.isfinite(float(value)):
            out.append(float(value))
    return out


def _is(a: object, b: float, tol: float = 1e-9) -> bool:
    return isinstance(a, (int, float)) and not isinstance(a, bool) and abs(float(a) - b) <= tol


def inv_no_default(records: list[dict], defaults: list[float], readings: list[float]) -> list[str]:
    """A temperature equal to a constructor default, which no input read."""
    out = []

    def judge(label: str, value: object) -> None:
        try:
            v = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return
        if any(_is(v, d) for d in defaults) and not any(_is(v, r) for r in readings):
            out.append(f"{label}={v}")

    for rec in records:
        if not rec["available"]:
            continue
        if str(rec.get("device_class")) == "temperature":
            judge(rec["entity_id"], rec["state"])
        if rec["entity_id"].startswith("climate."):
            # The readings only: a target is a setpoint the config supplies.
            judge(f"{rec['entity_id']}.current_temperature",
                  (rec["attributes"] or {}).get("current_temperature"))
    return out


POWER_TOL = 0.05


def inv_agreement(records: list[dict], plan_draws: bool | None,
                  plan_kw: float | None = None) -> list[str]:
    """Heat Pump Action and hvac_action agree with the pump actually running.

    ``plan_draws`` is whether the plan's current step clears the optimizer's
    own on threshold on space + DHW power, or None when no plan exists.
    ``plan_kw`` is that step's space + DHW draw, read from the plan's own
    space action and DHW forecast; Heat Pump Action's ``power_kw`` must equal
    it (#1499's power half: a DHW-only step published 0 kW).
    """
    out = []
    for rec in records:
        if not rec["available"]:
            continue
        attrs = rec["attributes"] or {}
        if rec.get("key") == "heat_pump_action":
            if rec["state"] in ("off", "idle") and attrs.get("heat_pump_on") is True:
                out.append(f"{rec['entity_id']}: state {rec['state']!r} "
                           "while its heat_pump_on attribute is true")
            if rec["state"] == "off" and plan_draws:
                out.append(f"{rec['entity_id']}: state 'off' while the plan's "
                           "current step draws space + DHW power")
            published = attrs.get("power_kw")
            if plan_kw is not None and isinstance(published, (int, float)) \
                    and abs(float(published) - plan_kw) > POWER_TOL:
                out.append(f"{rec['entity_id']}: power_kw {published} while the "
                           f"plan's current step draws {plan_kw:.2f} kW")
        if rec["entity_id"].startswith("climate."):
            action = attrs.get("hvac_action")
            if action in ("idle", "off") and attrs.get("_heat_pump_on") is True \
                    and rec["state"] not in ("off", None):
                out.append(f"{rec['entity_id']}: hvac_action {action!r} "
                           "while the current action has heat_pump_on")
    return out


def frozen_offenders(
    published: dict[str, list[float | None]],
    inputs: dict[str, list[float | None]],
) -> list[str]:
    """A published number that mirrors an input and stayed put when it moved."""
    out = []
    for pkey, pvals in published.items():
        for ikey, ivals in inputs.items():
            both = [(p, i) for p, i in zip(pvals, ivals) if p is not None and i is not None]
            matched = [i for p, i in both if abs(p - i) <= MIRROR_TOL]
            # Two distinct matched values at least: a published 0.0 beside an
            # input idling at 0.0 is a coincidence of zeros, not a mirror.
            if len(matched) < MIRROR_MIN_HITS or len(matched) * 2 < len(both) \
                    or len({round(v, 3) for v in matched}) < 2:
                continue
            for k in range(1, len(pvals)):
                p0, p1, i0, i1 = pvals[k - 1], pvals[k], ivals[k - 1], ivals[k]
                if None in (p0, p1, i0, i1):
                    continue
                if abs(i1 - i0) > INPUT_MOVE and abs(p1 - p0) < 1e-9:
                    out.append(f"{pkey} stayed {p1} at cycle {k} while {ikey} "
                               f"moved {i0} -> {i1}")
                    break
    return out


#: The five files of the per-cycle path #1544 found no budgeted script ran.
COST_FILES = ("coordinator.py", "sensor.py", "process_worker.py",
              "price_model.py", "narrative.py")
#: Executor-job CPU on the loop thread (the test double runs jobs inline),
#: accumulated by run_fixture's meter so the loop thread's own share is
#: the cycle's thread CPU less this.
_EXEC_CPU = [0.0]
#: CPU the perturbation arms burnt, on the clock their metric reads, so the
#: lane can show an arm doubled the whole span its metric times (#2205).
_INJECTED_CPU = [0.0]
#: The multiple a budget must be able to see, as ``tests/stress.py``'s
#: DETECTION_TARGET: a budget is recorded at sqrt(2) x the measured cost, so
#: the measurement sits in (budget / 2, budget] and a doubled cycle is over it.
COST_DETECTION = 2.0
#: Per fixture: ``cpu_ratio`` (cycle CPU / reference-solve CPU, mean over the
#: timed cycles) and ``peak_kib`` (largest per-cycle tracemalloc peak), each
#: sqrt(2) x a clean run's figure, which the lane's ``record:`` line prints.
#: One-sided: re-record down when the cycle got cheaper; a raise is a
#: regression argued in the commit message. The commit that records a figure
#: names the machine; the band check validates it on whichever runner reads
#: it, since a run outside (budget / 2, budget] is red and prints its own.
#: Across several runs, record the largest ``record:`` value, and keep it
#: under every doubled arm's figure.
#: ``loop_cpu_ratio`` (R9 D9-s2-02): the cycle's LOOP-THREAD CPU alone --
#: its thread CPU less its executor jobs, plus the entity reads -- over the
#: PURE-PYTHON reference (``reference_loop``), recorded and banded exactly as
#: ``cpu_ratio``. The whole-cycle ratio cannot see a 2x of it: the loop is a
#: minority of the cycle, so doubling it at the band's centre moves
#: ``cpu_ratio`` inside its sqrt(2) band. Entry allowed by tvofi (card B1).
#: The ruler was changed from the BLAS solve to a pure-Python workload
#: (#2270, owner decision 2026-10-15): the numerator is interpreter-bound and
#: the solve is BLAS-bound, so the figure tracked the runner CLASS, not the
#: code -- corr(loop_cpu_ratio, ref_ms) = -0.94 over 30 nightly runs. The
#: series splits by ref_ms: ~22-34 (fast) read 0.316-0.405, ~52-55 (slow)
#: read 0.244-0.274, 1.66x overall; the class shift is the interpreter speed
#: (loop_cpu 10.0 -> 13.5 ms, 1.35x) over the BLAS speed (ref_ms 28.6 ->
#: 53.2 ms, 1.86x). Normalising by a workload of the loop's own kind, on its
#: own clock, cancels MOST of the interpreter factor, not all of it: the
#: numerator's work does not scale with the ruler's, so a runner that speeds
#: the ruler faster than the cycle's own loop still lifts the figure. The
#: scheduled slow lanes after #2339 read a tight 0.0868-0.0877 while their
#: rulers sat 1.26x apart (loop_ref_ms 128-161), and 0.1114 on a runner
#: 1.5-1.9x faster than those at the ruler (84.05 ms) whose loop CPU in
#: absolute time fell (9.36 ms) -- the runner, not loop work, over the cap.
#: ``dev/audit/harnesses/r10_replay_loopnorm.py --series`` derives the series
#: by ruler era. Recorded at the CENTRE of its measured spread:
#: twelve clean runs read 0.0618-0.0903 (median 0.0786) at load average
#: 15-29; sqrt(2) x 0.0786 is 0.111, both edges inside (0.0555, 0.111], and
#: a doubled loop arm ~0.156 is over the cap. The 0.1114 run falsifies that
#: recording; re-recording from the series is a raise (above the measured
#: median), which is the owner's under CLAUDE.md rule 2, not a lane fix.
#: ``cpu_ratio`` re-recorded down the same way (#2205): #2142's solve memo
#: cut the cycle to 0.656x (R10-RCA-2205's interleaved medians), so all 36
#: timed slow lanes before it, 1.915-2.824, project to 1.256-1.853; the two
#: after it read 1.880 and 1.391; sqrt(2) x the geometric midpoint of 1.256
#: and 1.880 is 2.173, each edge 15.6 % inside the band (floor 1.087).
#: Re-centre at the next timed week, not on one run.
COST_BUDGETS: dict[str, dict[str, float]] = {
    "synthetic-dhw-only.json": {"cpu_ratio": 2.173, "peak_kib": 2686.0,
                                "loop_cpu_ratio": 0.111},
}
#: A reference solve after every this many cycles, beside the ones before
#: and after the day, so the unit tracks the runner through the replay.
COST_REF_EVERY = 8

#: The loop figure's ruler: a fixed, pure-Python workload, the interpreter-
#: bound twin of ``stress.reference_solve``. The numerator is the cycle's
#: THREAD CPU -- interpreter work -- while ``reference_solve`` is BLAS-bound;
#: dividing one by the other made ``loop_cpu_ratio`` track the runner class,
#: corr(loop_cpu_ratio, ref_ms) = -0.94 over 30 nightly runs (R10-RCA-2205):
#: a runner whose BLAS outruns its interpreter read the loop low, and the
#: spread was 0.2441-0.405 (1.66x), the runner, not the code. Normalising by
#: work on the SAME clock and of the SAME kind cancels MOST of the interpreter
#: factor, not all of it: the ratio keeps a residual runner-class spread, so it
#: is bounded, not invariant, across runners. Fixed iterations, no numpy, no
#: data dependence, so every call
#: costs the same and no integration change can move it -- the property that
#: makes ``reference_solve`` the right ruler for the solve, for the loop.
#: SIZED to a couple of hundred ms, as ``reference_solve`` is: 1e6 steps read
#: 154 ms idle and 170-195 ms at load average 15-29, so its own variation
#: sits under the loop's rather than deciding the ratio.
_LOOP_REF_STEPS = 1_000_000
#: Lookup keys, read through a dict, so the mix carries CPython's dict load
#: beside the arithmetic -- the interpreter work a coordinator cycle is
#: mostly made of, not a bare arithmetic loop a runner's FPU could speed up.
_LOOP_REF_KEYS = ("x", "y", "z")


def _loop_reference_work() -> float:
    """A fixed pure-Python computation; the value is discarded.

    Its arithmetic is nobody's business but this file's: it must never be
    "improved", or the ruler moves and every historical ratio stops meaning
    anything (``reference_solve``'s own rule).
    """
    d = {"x": 1.5, "y": 2.5, "z": 0.75}
    kx, ky, kz = _LOOP_REF_KEYS
    acc = 0.0
    tail = [0.0, 0.0, 0.0, 0.0]
    for i in range(_LOOP_REF_STEPS):
        v = d[kx] * i + d[ky] - d[kz]
        if i & 1:
            acc += v * 0.5
        else:
            acc -= v * 0.25
        tail[i & 3] = acc
    return acc + sum(tail)


def reference_loop() -> float:
    """One pure-Python reference: this thread's CPU ms, the loop's own clock.

    ``own_loop`` is ``time.thread_time()``, so the ruler is timed on the same
    clock: a runner that runs bytecode slowly reads both high, and the ratio
    is the loop's work over this workload's, not the runner's speed.
    """
    began = time.thread_time()
    _loop_reference_work()
    return (time.thread_time() - began) * 1000.0


def cost_figures(cycle_cpu: list[float], ref_cpu: list[float],
                 peaks: list[int], loop_cpu: list[float] | None = None,
                 loop_ref: list[float] | None = None) -> dict[str, float]:
    ref = sorted(ref_cpu)[len(ref_cpu) // 2] if ref_cpu else 0.0
    out = {"cpu_ratio": round(sum(cycle_cpu) / len(cycle_cpu) / ref, 4)
           if cycle_cpu and ref > 0 else float("nan"),
           "peak_kib": round(max(peaks) / 1024.0, 1) if peaks else float("nan")}
    if loop_cpu is not None:
        # The loop figure is normalised by ``loop_ref`` (pure Python), never
        # by the BLAS solve: a solve reference that moved with the runner and
        # a thread measure that did not is exactly #2270.
        lref = sorted(loop_ref)[len(loop_ref) // 2] if loop_ref else 0.0
        out["loop_cpu_ratio"] = (round(sum(loop_cpu) / len(loop_cpu) / lref, 4)
                                 if loop_cpu and lref > 0 else float("nan"))
    return out


def cost_offenders(figures: dict[str, float], budget: dict[str, float] | None,
                   detection: float = COST_DETECTION) -> list[str]:
    """A cycle over its budget, or a budget too loose to see ``detection``x."""
    if not budget or not all(budget.get(k, 0) > 0 for k in figures):
        return [f"no recorded budget: record {k}={math.sqrt(detection) * v:.4g}"
                for k, v in figures.items()]
    out = []
    for key, value in figures.items():
        cap = budget[key]
        if not math.isfinite(value):
            out.append(f"{key} not measured")
        elif value > cap:
            out.append(f"{key} {value:.4g} over its budget {cap:.4g}")
        elif value * detection < cap:
            out.append(f"{key} {value:.4g}: budget {cap:.4g} cannot see a "
                       f"{detection:g}x cycle; re-record {math.sqrt(detection) * value:.4g}")
    return out


def short_doubling(injected_ratio: float) -> list[str]:
    """A perturbation arm that burnt less than the clean span its metric
    times is no doubling (#2205: the cpu arm spun the update alone, ~0.93)."""
    return [] if injected_ratio >= 1.0 else [
        f"injected {injected_ratio:.4g} x the clean span, a doubling is >= 1"]


def uncovered_files(traced: set[str]) -> list[str]:
    """COST_FILES no function of which ran in the traced cycle."""
    names = {Path(f).name for f in traced if "heatpump_optimizer" in Path(f).parts}
    return [f"{name}: no function ran in the traced cycle"
            for name in COST_FILES if name not in names]


# --- the controls: every invariant can fire, and does not fire on good data ----


def controls() -> list[tuple[str, bool, str]]:
    def rec(**kw):
        base = {"entity_id": "sensor.x", "key": "x", "available": True, "state": None,
                "attributes": {}, "device_class": None, "unit": None, "options": None}
        base.update(kw)
        return base

    table = UNITS_FALLBACK
    defaults = [21.0, 22.0, 5.0]
    res = []

    def pair(name, bad, good):
        res.append((f"control:{name}", bool(bad) and not good,
                    f"bad={bad[:2]} good={good[:2]}"))

    pair("finite", inv_finite([rec(state=float("nan"))]),
         inv_finite([rec(state=1.0, attributes={"a": [1, 2]})]))
    pair("unit",
         inv_unit([rec(device_class="temperature", unit="kW", state=1.0),
                   rec(device_class="enum", state="hot_water", options=["off"])], table),
         inv_unit([rec(device_class="temperature", unit="°C", state=1.0),
                   rec(device_class="enum", state="off", options=["off"])], table))
    pair("no_default",
         inv_no_default([rec(device_class="temperature", state=22.0)], defaults, [20.4]),
         inv_no_default([rec(device_class="temperature", state=21.0)], defaults, [21.0]))
    hpa = dict(entity_id="sensor.hpa", key="heat_pump_action")
    pair("agreement:attribute",
         inv_agreement([rec(**hpa, state="off", attributes={"heat_pump_on": True})], None),
         inv_agreement([rec(**hpa, state="hot_water", attributes={"heat_pump_on": True})], None))
    pair("agreement:plan",
         inv_agreement([rec(**hpa, state="off", attributes={"heat_pump_on": False})], True),
         inv_agreement([rec(**hpa, state="off", attributes={"heat_pump_on": False})], False))
    pair("agreement:power",
         inv_agreement([rec(**hpa, state="hot_water", attributes={"power_kw": 0.0})], True, 2.0),
         inv_agreement([rec(**hpa, state="hot_water", attributes={"power_kw": 2.0})], True, 2.0))
    pair("agreement:climate",
         inv_agreement([rec(entity_id="climate.x", state="auto",
                            attributes={"hvac_action": "idle", "_heat_pump_on": True})], None),
         inv_agreement([rec(entity_id="climate.x", state="auto",
                            attributes={"hvac_action": "heating", "_heat_pump_on": True})], None))
    inp = {"sensor.in": [1.0, 3.0, 1.0, 3.0, 2.0]}
    pair("not_frozen",
         frozen_offenders({"sensor.out": [1.0, 3.0, 1.0, 3.0, 3.0]}, inp),
         frozen_offenders({"sensor.out": [1.0, 3.0, 1.0, 3.0, 2.0]}, inp)
         + frozen_offenders({"sensor.zero": [0.0] * 5}, {"sensor.idle": [0.0] * 4 + [2.0]}))
    ref, clean = [10.0, 11.0, 9.0], cost_figures([20.0, 22.0], [10.0, 11.0, 9.0], [4096])
    budget = {k: math.sqrt(COST_DETECTION) * v for k, v in clean.items()}
    pair("cycle_cost:cpu", cost_offenders(cost_figures([40.0, 44.0], ref, [4096]), budget),
         cost_offenders(clean, budget))
    pair("cycle_cost:memory", cost_offenders(cost_figures([20.0, 22.0], ref, [8192]), budget),
         cost_offenders(clean, budget))
    pair("cycle_cost:loose_budget",
         cost_offenders(clean, {k: 3 * v for k, v in clean.items()}),
         cost_offenders(clean, budget))
    pair("cycle_cost:unrecorded", cost_offenders(clean, {"cpu_ratio": 0.0, "peak_kib": 0.0}),
         cost_offenders(clean, budget))
    # The loop-thread figure (D9-s2-02): a doubled loop inside an unchanged
    # cycle is over its own budget, where the whole-cycle figure is not. Its
    # ruler is the pure-Python reference, so it shares no clock with the solve.
    lref = [3.0, 3.1, 3.2]
    lclean = cost_figures([20.0, 22.0], ref, [4096], [2.0, 2.4], lref)
    lbudget = {k: math.sqrt(COST_DETECTION) * v for k, v in lclean.items()}
    lhot = cost_figures([22.0, 24.4], ref, [4096], [4.0, 4.8], lref)
    pair("cycle_cost:loop_thread", cost_offenders(lhot, lbudget),
         cost_offenders(lclean, lbudget))
    # The loop figure is normalised by the pure-Python reference, not the BLAS
    # solve (#2270): moving the solve reference must not move it, and moving
    # the loop reference must. Red before the normaliser changed (the ratio
    # followed the solve), green after.
    la = cost_figures([20.0, 22.0], ref, [4096], [2.0, 2.4], lref)
    solve_moved = la["loop_cpu_ratio"] != cost_figures(
        [20.0, 22.0], [r * 3 for r in ref], [4096], [2.0, 2.4], lref)["loop_cpu_ratio"]
    lref_moved = la["loop_cpu_ratio"] != cost_figures(
        [20.0, 22.0], ref, [4096], [2.0, 2.4], [r * 2 for r in lref])["loop_cpu_ratio"]
    res.append(("control:cycle_cost:loop_normaliser",
                not solve_moved and lref_moved,
                f"ratio {la['loop_cpu_ratio']}: solve x3 moved={solve_moved}, "
                f"loop_ref x2 moved={lref_moved}"))
    # The sibling figure and the reason the two rulers differ: the whole-cycle
    # figure IS normalised by the solve (the cycle is solve-dominated), so it
    # moves with the solve reference where the loop figure does not.
    cpu_solve_moved = clean["cpu_ratio"] != cost_figures(
        [20.0, 22.0], [r * 3 for r in ref], [4096])["cpu_ratio"]
    res.append(("control:cycle_cost:cpu_normaliser", cpu_solve_moved,
                f"cpu_ratio {clean['cpu_ratio']}: solve x3 moved={cpu_solve_moved}"))
    pair("cycle_cost:short_doubling", short_doubling(0.93), short_doubling(1.0001))
    pair("cycle_cost:unmetered_doubling", short_doubling(float("nan")), short_doubling(1.0))
    pkg = "/x/custom_components/heatpump_optimizer/"
    pair("cycle_cost:coverage", uncovered_files({pkg + f for f in COST_FILES[1:]}),
         uncovered_files({pkg + f for f in COST_FILES}))
    return res


def sanitiser_checks(paths: list[Path]) -> list[tuple[str, bool, str]]:
    """The export's rules, and nightly_ha's A10 coordinate rule, on each fixture."""
    import export
    import nightly_ha

    res = []
    for path in paths:
        found = export.check_file(path)
        res.append((f"sanitised:{path.name}", not found, "; ".join(found[:3])))
        checks = nightly_ha.Checks()
        nightly_ha.check_a10_no_precise_location(checks, json.loads(path.read_text()))
        res.append((f"a10_location:{path.name}", not checks.failures(),
                    str(checks.results)))
    # The null control: an unsanitised payload is refused by the same rules.
    raw = {"format": export.FORMAT, "entry": {"data": {"tibber_token": "abc123xyz",
           "solar_location": {"latitude": 59.334591}}, "options": {}},
           "states": {"camera.x": [["t", "idle", {"entity_picture": "/p?token=q"}, None]]}}
    found = export.violations(raw)
    joined = "; ".join(found)
    res.append(("control:sanitiser_refuses",
                all(k in joined for k in ("tibber_token", "latitude", "entity_picture")),
                joined))
    dropped: list[str] = []
    conf = export.entry_keys(*export.default_const_paths())
    res.append(("control:sanitise_clears",
                not export.violations(export.sanitise(raw, conf, dropped), conf),
                f"dropped {len(dropped)} value(s)"))
    return res + leak_probes() + tibber_price_checks()


#: The review of #1508's leak probe (the first eleven): shapes of private data a recorder
#: row or a config entry can carry, each of which passed the first exporter.
#: Every one must be dropped by the export AND refused by ``--check`` when it
#: is put back into a committed fixture by hand.
LEAK_PROBES = {
    "capital_Latitude": {"Latitude": 59.334591, "Longitude": 18.063240},
    "lat_lon_short": {"lat": 59.334591, "lon": 18.063240},
    "coord_list": {"location": [59.334591, 18.063240]},
    "coord_string": {"gps": "59.334591,18.063240"},
    "basic_auth_url": {"stream_source": "rtsp://admin:hunter2pass@192.168.1.5/live"},
    "apikey_query": {"url": "https://api.example.com/v1?apikey=ABCDEF0123456789"},
    "pin_code": {"pin": "482913", "access_code": "771234"},
    "psk": {"wifi_psk": "correct-horse-battery",
            "private_key": "-----BEGIN PRIVATE KEY-----MIIE"},
    "email": {"account_email": "owner@example.com"},
    "serial_mac": {"serial_number": "SN-0098-7766", "mac": "aa:bb:cc:dd:ee:ff"},
    "entry_address": {"tibber_home": "Storgatan 12, 111 22 Stockholm"},
    # Two more, each in a place the key allowlist lets through, so only the
    # value rule (``export.text_ok``) stands between them and the file.
    "entry_url_in_allowed_key": {"ecl110_state_topic": "mqtt://ecl:s3cretpw@10.0.0.7/ecl"},
    "state_address": {"state": "Storgatan 12, 111 22 Stockholm"},
    # The review's second probe (leakprobe2, round 2 of #1508): the right key
    # holding the wrong shape, a host without a scheme, a MAC without colons.
    "n1_options_dict": {"options": {"home_owner": "Anna Exempel", "street": "Storgatan"}},
    "n2_currency_name": {"currency": "Anna Exempel"},
    "n3_options_address": {"options": ["Storgatan 12", "Sodermalm 11"]},
    "n4_token_in_series": {"today": ["abcDEFghiJKLmnoPQRstu9vWX7yz"]},
    "state_n10_host_path": {"state": "nas.exempel.se/cam/front"},
    "n11_host_path_unit": {"unit_of_measurement": "home.local/api/x"},
    "entry_n13_text_in_entity_key": {"weather_entity": "Storgatan 12 Stockholm"},
    "n14_mac_no_colons": {"options": ["aabbccddeeff"]},
}
PROBE_ENTITY = "sensor.heat_pump_power"


def _probe_texts(values: object) -> list[str]:
    """Every leaf string of a probe, which must not appear in the export."""
    if isinstance(values, dict):
        return [t for v in values.values() for t in _probe_texts(v)]
    if isinstance(values, list):
        return [t for v in values for t in _probe_texts(v)]
    return [str(values)]


def leak_probes() -> list[tuple[str, bool, str]]:
    import export
    import synthesize

    res = []
    committed = json.loads((FIXTURES / "synthetic-dhw-only.json").read_text())
    conf = export.entry_keys(*export.default_const_paths())
    for name, values in LEAK_PROBES.items():
        in_entry = name.startswith("entry_")
        in_state = name.startswith("state_")
        series, data = synthesize._series, synthesize.ENTRY_DATA
        if in_entry:
            synthesize.ENTRY_DATA = {**data, **values}
        else:
            def patched(values=values, series=series, in_state=in_state):
                out = series()
                out[PROBE_ENTITY] = [
                    (t, values["state"], a) if in_state else (t, st, {**a, **values})
                    for t, st, a in out[PROBE_ENTITY]]
                return out
            synthesize._series = patched
        try:
            with tempfile.TemporaryDirectory() as tmp:
                db = synthesize.write_install(Path(tmp))
                payload = export.build_export(
                    Path(tmp), db, 1, (synthesize.DAY + timedelta(days=1)).date().isoformat(),
                    None, [], None)
            blob = json.dumps(payload)
            survived = [t for t in _probe_texts(values) if t in blob]
            outcome = f"written, survived={survived}"
        except SystemExit as err:
            survived, outcome = [], f"refused: {err}"
        finally:
            synthesize._series, synthesize.ENTRY_DATA = series, data
        res.append((f"leak_probe:{name}:export_drops", not survived, outcome))
        # Put back by hand into a committed fixture: --check must refuse it.
        planted = json.loads(json.dumps(committed))
        if in_entry:
            planted["entry"]["data"].update(values)
        elif in_state:
            planted["states"][PROBE_ENTITY][0][1] = values["state"]
        else:
            planted["states"][PROBE_ENTITY][0][2] = {
                **(planted["states"][PROBE_ENTITY][0][2] or {}), **values}
        found = export.violations(planted, conf)
        res.append((f"leak_probe:{name}:check_refuses", bool(found), "; ".join(found[:3])))
    return res


#: A Tibber install's registry rows, as Home Assistant core's Tibber
#: integration writes them (``export.py``'s TIBBER_* cite the source): the
#: price sensor's unique id is the bare home id; every other Tibber sensor's
#: is ``<home id>_<key>`` or ``<home id>_rt_<key>``.
_HOME_A = "96a14971-525a-4420-aae9-e5aedaa129ff"
_HOME_B = "4c1e6f3b-0d2a-4b7e-9a51-2f8c3d4e5a6b"
_TIBBER_PRICE_A = ("sensor.electricity_price_home_a", _HOME_A, "electricity_price")
_TIBBER_PRICE_B = ("sensor.electricity_price_home_b", _HOME_B, "electricity_price")
#: Entities that are not the price, each recorded with numeric states, one
#: per rule of ``export.tibber_price_candidates``: the month's cost (once with
#: no translation key, as an older registry stores it) and a real-time power
#: reading; Tibber's notify entity, keyed on the bare config-entry id; a
#: template sensor keyed on a bare UUID; and a Tibber sensor keyed on a bare
#: id under another translation key, which core does not publish today.
_TIBBER_DECOYS = (
    ("sensor.home_a_monthly_cost", f"{_HOME_A}_month_cost", "month_cost"),
    ("sensor.home_a_monthly_cost_2", f"{_HOME_A}_month_cost", None),
    ("sensor.home_a_power", f"{_HOME_A}_rt_power", "power"),
    ("notify.tibber", "01JTIBBERENTRY00000000000", None),
    ("sensor.template_price", "0b6a7d2e-3f41-4c5a-9e8d-7c6b5a4f3e2d", None, None, "template"),
    ("sensor.home_a_price_level", "e2b1c0d9-8f7e-4a6b-9c5d-4e3f2a1b0c9d", "price_level"),
)


def _tibber_export(rows: list[tuple], entry: dict, price_entity: str | None = None,
                   unrecorded: tuple[str, ...] = (),
                   unavailable: tuple[str, ...] = ()) -> str:
    """``price_series_entity`` of a Tibber install exported with ``rows`` in
    its registry, with its row count, or ``refused: <message>``. A row is
    (entity id, unique id, translation key[, disabled_by[, platform]]), the
    platform "tibber" unless given; each is recorded with an hourly numeric
    price, unless ``unrecorded`` names it (no rows) or ``unavailable`` does
    (rows, every one ``unavailable``)."""
    import export
    import synthesize

    series, data = synthesize._series, synthesize.ENTRY_DATA
    synthesize.ENTRY_DATA = {**{k: v for k, v in data.items() if k != "price_entity"},
                             "price_source": "tibber", **entry}

    def patched(series=series):
        out = series()
        for row in rows:
            if row[0] not in unrecorded:
                out[row[0]] = [(synthesize.DAY + timedelta(hours=h),
                                "unavailable" if row[0] in unavailable
                                else f"{0.8 + h / 100:.3f}",
                                {"unit_of_measurement": "SEK/kWh",
                                 "state_class": "measurement"}) for h in range(-1, 24)]
        return out

    synthesize._series = patched
    try:
        with tempfile.TemporaryDirectory() as tmp:
            db = synthesize.write_install(Path(tmp))
            reg_path = Path(tmp) / ".storage" / "core.entity_registry"
            reg = json.loads(reg_path.read_text())
            reg["data"]["entities"] += [
                {"entity_id": r[0], "platform": r[4] if len(r) > 4 else "tibber",
                 "unique_id": r[1],
                 "translation_key": r[2], "config_entry_id": "01JTIBBER",
                 "disabled_by": r[3] if len(r) > 3 else None} for r in rows]
            reg_path.write_text(json.dumps(reg))
            with contextlib.redirect_stderr(io.StringIO()):
                payload = export.build_export(
                    Path(tmp), db, 1, (synthesize.DAY + timedelta(days=1)).date().isoformat(),
                    None, [], price_entity)
        chosen = payload["price_series_entity"]
        return f"{chosen} rows={len(payload['states'].get(chosen) or [])}"
    except SystemExit as err:
        return f"refused: {err}"
    finally:
        synthesize._series, synthesize.ENTRY_DATA = series, data


def tibber_price_checks() -> list[tuple[str, bool, str]]:
    """With the Tibber source and no ``--price-entity``, the export picks the
    one Tibber price sensor the registry and the recorder agree on, and
    refuses -- naming the candidates -- when there is none or more than one."""
    a, b = _TIBBER_PRICE_A[0], _TIBBER_PRICE_B[0]
    decoys = list(_TIBBER_DECOYS)
    both = [_TIBBER_PRICE_A, _TIBBER_PRICE_B]

    def picked(eid: str):
        return lambda out: out.startswith(f"{eid} rows=") and not out.endswith("rows=0")

    cases = {
        # One home: its price sensor, not the cost or power sensor beside it.
        "one_home_picked": (_tibber_export([_TIBBER_PRICE_A] + decoys, {}), picked(a)),
        "none_refused": (_tibber_export(decoys, {}),
                         lambda o: o.startswith("refused") and "--price-entity" in o),
        "two_homes_refused": (_tibber_export(both + decoys, {}),
                              lambda o: o.startswith("refused") and a in o and b in o
                              and "--price-entity" in o),
        "flag_overrides_two": (_tibber_export(both, {}, price_entity=b), picked(b)),
        "flag_overrides_one": (_tibber_export([_TIBBER_PRICE_A, (*_TIBBER_PRICE_B[:2], "x")],
                                              {}, price_entity=_TIBBER_PRICE_B[0]), picked(b)),
        "entry_names_one": (_tibber_export(both, {"price_entity": b}), picked(b)),
        "disabled_skipped": (_tibber_export([_TIBBER_PRICE_A, (*_TIBBER_PRICE_B, "user")], {}),
                             picked(a)),
        "unrecorded_skipped": (_tibber_export(both, {}, unrecorded=(a,)), picked(b)),
        # A second home whose subscription ended: its row stays enabled and
        # the recorder holds only ``unavailable`` for it -- rows, no number.
        "unavailable_skipped": (_tibber_export(both, {}, unavailable=(b,)), picked(a)),
        # The entity source is untouched: no series entity is invented.
        "entity_source_untouched": (
            _tibber_export([_TIBBER_PRICE_A], {"price_source": "entity",
                                               "price_entity": "sensor.nordpool_kwh_se3_sek"}),
            lambda o: o.startswith("None rows=")),
    }
    return [(f"tibber_price:{name}", ok(out), out) for name, (out, ok) in cases.items()]


def synthetic_reproduces() -> tuple[str, bool, str]:
    """In this process, so a recorder of this interpreter sees both files read."""
    import synthesize

    committed = FIXTURES / "synthetic-dhw-only.json"
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "again.json"
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                rc = synthesize.main(["--out", str(out)])
        except (SystemExit, Exception) as err:  # noqa: BLE001 - one red check
            # The exporter refuses with SystemExit; inside tests/entities.py
            # that would end the whole run, not fail this one check.
            rc = f"{type(err).__name__}: {err}"
        same = rc == 0 and out.read_bytes() == committed.read_bytes()
        size = out.stat().st_size if out.exists() else None
    return ("synthetic_reproduces", same,
            f"rc={rc} regenerated={size} B committed={committed.stat().st_size} B")


# --- one fixture, in this interpreter -----------------------------------------


def _ts(raw: str | None) -> datetime | None:
    return datetime.fromisoformat(raw) if raw else None


class Recording:
    """The fixture's state rows, answerable as 'what was true at t'."""

    def __init__(self, states: dict[str, list[list]]) -> None:
        self.rows: dict[str, list[tuple[datetime, str, dict, datetime | None]]] = {}
        for entity_id, rows in states.items():
            attrs: dict = {}
            out = []
            for updated, state, maybe_attrs, reported in rows:
                if maybe_attrs is not None:
                    attrs = maybe_attrs
                out.append((_ts(updated), state, attrs, _ts(reported)))
            self.rows[entity_id] = out

    def at(self, entity_id: str, t: datetime):
        chosen = None
        for row in self.rows.get(entity_id, ()):
            if row[0] <= t:
                chosen = row
            else:
                break
        return chosen

    def after(self, entity_id: str, t: datetime):
        """The rows from the one in force at ``t`` onwards."""
        rows = self.rows.get(entity_id, [])
        first = max(0, sum(1 for r in rows if r[0] <= t) - 1)
        return rows[first:]


def _num(value: object) -> float | None:
    try:
        v = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


class InProcessWorker:
    """``_ensure_worker``'s child, as ``process_worker.run_worker`` in this process.

    ``_run_in_process`` pickles the job into ``stdin`` and flushes; the flush
    hands that one job to the worker's own loop, which answers into ``stdout``
    and returns at the end of its input, as the child does at EOF.
    """

    def __init__(self) -> None:
        worker = self

        class Pipe(io.BytesIO):
            def flush(self) -> None:
                job = self.getvalue()
                self.seek(0)
                self.truncate()
                if job:
                    worker.serve(job)

        self.stdin = Pipe()
        self.stdout = io.BytesIO()

    def poll(self) -> None:
        return None

    def serve(self, job: bytes) -> None:
        from types import SimpleNamespace
        from heatpump_optimizer import process_worker

        reply = io.BytesIO()
        saved = sys.stdin, sys.stdout
        sys.stdin = SimpleNamespace(buffer=io.BytesIO(job))  # type: ignore[assignment]
        sys.stdout = SimpleNamespace(buffer=reply)  # type: ignore[assignment]
        try:
            process_worker.run_worker()
        finally:
            sys.stdin, sys.stdout = saved
        self.stdout.seek(0)
        self.stdout.truncate()
        self.stdout.write(reply.getvalue())
        self.stdout.seek(0)


def _spin(clock, seconds: float) -> None:
    """The perturbation: burn ``seconds`` more of ``clock`` on this thread."""
    began = clock()
    while clock() < began + seconds:
        pass
    _INJECTED_CPU[0] += clock() - began


def inject_cost(cm, kind: str | None) -> None:
    """The perturbation: double one cycle's memory peak, in memory.

    Wraps ``_async_update_data`` rather than editing ``coordinator.py`` on
    disk, which a concurrent run in the same tree would import.
    """
    if kind != "memory":  # the cpu and loop arms are spun in run_fixture
        return
    import tracemalloc

    real = cm.HeatPumpOptimizerCoordinator._async_update_data

    async def doubled(self):
        out = await real(self)
        if tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
            ballast = bytearray(max(0, 2 * peak - current))
            del ballast
        return out

    cm.HeatPumpOptimizerCoordinator._async_update_data = doubled


def run_fixture(path: Path, step_minutes: int | None, inject: str | None = None) -> dict:
    import tracemalloc
    from stress import reference_solve  # first: it pins BLAS threads before numpy loads
    from homeassistant.util import dt as dt_util
    from homeassistant.helpers.update_coordinator import UpdateFailed
    from harness import FakeEntry, FakeHass, FakeState
    import heatpump_optimizer as integration
    from heatpump_optimizer import const
    from heatpump_optimizer import coordinator as cm

    fixture = json.loads(path.read_text())
    rec = Recording(fixture["states"])
    entry_data = dict(fixture["entry"]["data"])
    entry_options = dict(fixture["entry"]["options"])
    config = {**entry_data, **entry_options}
    start = _ts(fixture["window"]["start"])
    end = _ts(fixture["window"]["end"])
    step = timedelta(minutes=step_minutes or int(
        config.get(const.CONF_OPTIMIZATION_INTERVAL, const.DEFAULT_OPTIMIZATION_INTERVAL)))

    worker = InProcessWorker()
    cm._ensure_worker = lambda: worker
    inject_cost(cm, inject)

    hass = FakeHass()
    # Executor jobs run inline on this thread in the double, so the loop
    # thread's own work is the cycle's thread CPU less theirs.
    _EXEC_CPU[0] = 0.0
    _INJECTED_CPU[0] = 0.0
    _real_exec = hass.async_add_executor_job

    async def _metered_exec(func, *args):
        began_job = time.thread_time()
        try:
            return await _real_exec(func, *args)
        finally:
            _EXEC_CPU[0] += time.thread_time() - began_job

    hass.async_add_executor_job = _metered_exec
    weather_id = config.get(const.CONF_WEATHER_ENTITY)

    async def forecasts(call):
        now = dt_util.now()
        rows = rec.after(weather_id, now)
        out = []
        for h in range(48):
            # Walked in UTC (round-9 D14-s4-01): ``+`` on a zoned clock adds
            # wall time, doubling or dropping a forecast hour on a DST day.
            t = dt_util.as_utc(now) + timedelta(hours=h)
            row = next((r for r in reversed(rows) if r[0] <= t), rows[0] if rows else None)
            if row is None:
                break
            attrs = row[2]
            out.append({"datetime": t.isoformat(),
                        "temperature": attrs.get("temperature"),
                        "wind_speed": attrs.get("wind_speed", 0.0),
                        "precipitation": attrs.get("precipitation", 0.0),
                        "condition": row[1]})
        return {weather_id: {"forecast": out}} if out else {}

    if weather_id:
        hass.services.async_register("weather", "get_forecasts", forecasts)

    entry = FakeEntry(data=entry_data, options=entry_options)
    coord = cm.HeatPumpOptimizerCoordinator(hass, entry)
    entry.runtime_data = coord

    price_series = fixture.get("price_series_entity")
    if not cm._entity_price_source(config):
        async def recorded_prices() -> None:
            now = dt_util.now()
            day0 = now.replace(hour=0, minute=0, second=0, microsecond=0)
            span = 2 if now.hour >= 13 else 1
            rows = []
            # The day's quarters walked in UTC: a wall-clock walk invents the
            # spring gap's four quarters and folds the autumn hour onto one.
            t = dt_util.as_utc(day0)
            while t < day0 + timedelta(days=span):
                row = rec.at(price_series, t) if price_series else None
                value = _num(row[1]) if row else None
                if value is not None:
                    rows.append({"total": value, "starts_at": dt_util.as_local(t).isoformat(),
                                 "level": "NORMAL"})
                t += timedelta(minutes=15)
            if not rows:
                raise UpdateFailed("the fixture records no price series")
            coord._prices = rows

        coord._fetch_tibber_prices = recorded_prices

    entities: list = []
    for platform in integration.PLATFORM_LIST:
        module = importlib.import_module(f"heatpump_optimizer.{str(platform)}")
        asyncio.run(module.async_setup_entry(hass, entry, entities.extend))

    table = units_table()
    defaults = thermal_defaults()
    results: dict[str, list[str]] = {k: [] for k in
                                     ("finite", "unit", "no_default", "agreement", "cycle")}
    pub_series: dict[str, list[float | None]] = {}
    inp_series: dict[str, list[float | None]] = {}
    cycles = 0
    # The cycle clock steps in UTC (round-9 D14-s4-02, G3-V2): a fixture's
    # stamps read in its zone would otherwise step by wall time and skip the
    # autumn day's repeated hour.
    t = dt_util.as_utc(start)
    started = time.monotonic()
    reference_solve()  # scipy's first-call costs, thrown away as stress.py does
    ref_cpu = [reference_solve()[1] for _ in range(3)]
    reference_loop()  # the loop ruler warms the adaptive interpreter the same way
    loop_ref_cpu = [reference_loop() for _ in range(3)]
    cycle_cpu: list[float] = []
    loop_cpu: list[float] = []
    injected: list[tuple[float, float]] = []
    peaks: list[int] = []
    traced: set[str] = set()
    while t < end:
        dt_util.freeze(t)
        readings: list[float] = []
        for entity_id in fixture["inputs"]:
            row = rec.at(entity_id, t)
            if row is None:
                continue
            updated, state, attrs, reported = row
            last_reported = min(t, reported) if reported else updated
            hass.states.set(entity_id, FakeState(
                state, last_updated=updated, last_reported=last_reported, attributes=attrs))
            v = _num(state)
            inp_series.setdefault(entity_id, [None] * cycles)
            inp_series[entity_id].append(v)
            if v is not None:
                readings.append(v)
        for series in inp_series.values():
            if len(series) < cycles + 1:
                series.append(None)
        # Cycle 0 is traced for coverage, odd cycles for memory, even ones
        # timed: a tracer or tracemalloc inside a timed cycle would be timed.
        mode = "trace" if cycles == 0 else ("memory" if cycles % 2 else "cpu")
        if mode == "trace":
            sys.setprofile(lambda frame, event, arg: traced.add(frame.f_code.co_filename)
                           if event == "call" else None)
        elif mode == "memory":
            tracemalloc.start()
        began = time.process_time()
        began_thread, exec_before = time.thread_time(), _EXEC_CPU[0]
        injected_before = _INJECTED_CPU[0]
        try:
            data = asyncio.run(coord._async_update_data())
            coord.data = data
            coord.last_update_success = True
        except Exception as err:  # noqa: BLE001 - a raise is the observation
            results["cycle"].append(f"{t.isoformat()}: {type(err).__name__}: {err}")
            coord.last_update_success = False
            data = coord.data or {}

        action = data.get("current_action") or {}
        records = sweep(entities, action, results["cycle"], t)
        own_loop = (time.thread_time() - began_thread) - (_EXEC_CPU[0] - exec_before)
        # The arm's metric span before this point's spin, less any spin in it.
        clean_span = ((own_loop if inject == "loop" else time.process_time() - began)
                      - (_INJECTED_CPU[0] - injected_before))
        if inject in ("cpu", "loop"):
            # The perturbation: exactly that span again -- the loop thread's
            # own work, or the whole cycle's update, jobs and entity sweep.
            _spin(time.thread_time if inject == "loop" else time.process_time, clean_span)
        if mode == "cpu":
            cycle_cpu.append((time.process_time() - began) * 1000.0)
            loop_cpu.append(((time.thread_time() - began_thread)
                             - (_EXEC_CPU[0] - exec_before)) * 1000.0)
            injected.append((_INJECTED_CPU[0] - injected_before, clean_span))
        elif mode == "memory":
            peaks.append(tracemalloc.get_traced_memory()[1])
            tracemalloc.stop()
        else:
            sys.setprofile(None)
        if cycles % COST_REF_EVERY == COST_REF_EVERY - 1:
            ref_cpu.append(reference_solve()[1])
            loop_ref_cpu.append(reference_loop())
        results["finite"] += inv_finite(records)
        results["unit"] += inv_unit(records, table)
        results["no_default"] += inv_no_default(records, defaults, readings)
        results["agreement"] += [f"{t.isoformat()} {o}" for o in
                                 inv_agreement(records, plan_draws(coord, data, t),
                                               plan_draw_kw(data, t))]
        for r in records:
            for key, value in [("state", r["state"])] + list((r["attributes"] or {}).items()):
                label = f"{r['entity_id']}.{key}"
                pub_series.setdefault(label, [None] * cycles)
                pub_series[label].append(_num(value) if r["available"] else None)
        for series in pub_series.values():
            if len(series) < cycles + 1:
                series.append(None)
        cycles += 1
        t += step
    dt_util.freeze(None)
    ref_cpu += [reference_solve()[1] for _ in range(3)]
    loop_ref_cpu += [reference_loop() for _ in range(3)]
    results["not_frozen"] = frozen_offenders(pub_series, inp_series)
    figures = cost_figures(cycle_cpu, ref_cpu, peaks, loop_cpu, loop_ref_cpu)
    clean = sum(c for _, c in injected)
    share = ({"injected_ratio": round(sum(i for i, _ in injected) / clean, 4)}
             if inject in ("cpu", "loop") and clean > 0 else {})
    results["cycle_cost"] = uncovered_files(traced) + cost_offenders(
        figures, COST_BUDGETS.get(path.name))
    return {"fixture": path.name, "cycles": cycles, "entities": len(entities),
            "cost": {**figures, **share, "timed": len(cycle_cpu), "traced": len(peaks),
                     "ref_ms": sorted(ref_cpu)[len(ref_cpu) // 2],
                     "loop_ref_ms": sorted(loop_ref_cpu)[len(loop_ref_cpu) // 2]},
            "seconds": round(time.monotonic() - started, 1),
            "results": {k: v[:12] + ([f"... {len(v) - 12} more"] if len(v) > 12 else [])
                        for k, v in results.items()},
            "counts": {k: len(v) for k, v in results.items()}}


def _plan_step(data: dict, t: datetime) -> tuple[float, float] | None:
    """(space, DHW) kW of the plan's step covering ``t``: space from the
    current action, DHW from the plan's own DHW forecast -- not the action's
    ``dhw_power``, which is what the published power reads."""
    forecast = ((data.get("dhw_plan") or {}).get("forecast")) or []
    dhw = 0.0
    for row in forecast:
        start = _ts(row.get("t"))
        if start is not None and start <= t:
            dhw = float(row.get("dhw_power") or 0.0)
    action = data.get("current_action") or {}
    if "power" not in action:
        return None
    return float(action.get("power") or 0.0), dhw


def plan_draws(coord, data: dict, t: datetime) -> bool | None:
    """Whether the plan's step covering ``t`` runs the pump, by the optimizer's
    own helper -- the same call ``_build_result`` makes for its on schedule."""
    step = _plan_step(data, t)
    if step is None:
        return None
    return bool(coord._optimizer._power_to_heat_pump_schedule([step[0]], [step[1]])[0])


def plan_draw_kw(data: dict, t: datetime) -> float | None:
    step = _plan_step(data, t)
    return None if step is None else step[0] + step[1]


def sweep(entities: list, action: dict, errors: list[str], t: datetime) -> list[dict]:
    records = []
    for e in entities:
        entity_id = getattr(e, "entity_id", None) or getattr(e, "_attr_unique_id", repr(e))
        try:
            available = bool(e.available)
            if entity_id.startswith("climate."):
                state = e.hvac_mode
                attrs = dict(e.extra_state_attributes or {})
                attrs.update({"hvac_action": e.hvac_action,
                              "current_temperature": e.current_temperature,
                              "target_temperature": e.target_temperature,
                              # Not published: the value the climate entity is
                              # judged against, carried under a private key.
                              "_heat_pump_on": action.get("heat_pump_on")})
                unit = None
            elif hasattr(e, "native_value"):
                state = e.native_value
                attrs = dict(getattr(e, "extra_state_attributes", None) or {})
                unit = getattr(e, "native_unit_of_measurement", None)
            elif hasattr(e, "is_on"):
                state = e.is_on
                attrs = dict(getattr(e, "extra_state_attributes", None) or {})
                unit = None
            else:
                continue
            if isinstance(state, datetime):
                state = state.isoformat()
            records.append({
                "entity_id": entity_id,
                "key": getattr(e, "_attr_translation_key", None)
                or getattr(e, "translation_key", None),
                "available": available,
                "state": state,
                "attributes": attrs,
                "device_class": getattr(e, "device_class", None)
                or getattr(e, "_attr_device_class", None),
                "unit": unit,
                "options": getattr(e, "options", None) or getattr(e, "_attr_options", None),
            })
        except Exception as err:  # noqa: BLE001 - a raise is the observation
            errors.append(f"{t.isoformat()} {entity_id}: {type(err).__name__}: {err}")
    return records


# --- the driver ---------------------------------------------------------------


def child_env(tz: str) -> dict[str, str]:
    """A replay interpreter's environment: the stub, the zone, BLAS on one thread."""
    env = {**os.environ, "HASTUB_TZ": tz,
           "PYTHONPATH": os.pathsep.join(
               [str(ROOT / "tests" / "hastub"), os.environ.get("PYTHONPATH", "")])}
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        env.setdefault(var, "1")
    return env


def replay_one(R, path: Path, step_minutes: int | None, inject: str | None) -> dict | None:
    """One fixture in its own interpreter, BLAS pinned to one thread."""
    env = child_env(json.loads(path.read_text()).get("time_zone") or "UTC")
    cmd = [sys.executable, str(Path(__file__).resolve()), "--one", str(path)]
    if step_minutes:
        cmd += ["--step-minutes", str(step_minutes)]
    if inject:
        cmd += ["--inject-cost", inject]
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=ROOT)
    line = next((ln for ln in proc.stdout.splitlines() if ln.startswith(MARK)), None)
    label = f"{path.name}: the replay ran to the end" + (f" ({inject} doubled)" if inject else "")
    if not R.check(label, line is not None,
                   f"rc={proc.returncode}: {proc.stderr.strip()[-600:]}"):
        return None
    return json.loads(line[len(MARK):])


# --- P10 (#1658): model kernels stay off the event loop ---------------------
#
# Home Assistant runs the update cycle and every entity property read on the
# event loop, and gives CPU work no boundary by default; seven rounds found
# the class again (#199, #290, #783, #1337, #1399, #1658 twice). The rule this
# barrier holds: on a replayed day, a model kernel called in this interpreter
# outside ``process_worker.run_worker`` is zero. Counts, not time: no BLAS or
# load dependence, so an instance present when a budget is recorded is still
# seen (the ``loop_cpu_ratio`` gap). A kernel is every public
# ``ThermalModel.simulate_*`` method (derived, not listed) and the sysid
# experiment's CPU entry points; each call is counted once, at its outermost
# kernel, and attributed to the route it ran on. FakeHass runs an executor job
# inline, so the thread-local flags below see the route it was handed to.

#: The sysid experiment's CPU: the fit and the step-time sizing and gate.
SYSID_KERNELS = ("identify", "identify_slab", "_size_step_power", "_unadoptable")
#: The arms: ``base`` is the tree as it is; ``fallback`` makes the process
#: route unusable (the #511 degrade, whose work must land on the executor,
#: never the loop); ``sysid`` arms an experiment on the replayed night.
KERNEL_ARMS = {"base": 3.0, "fallback": 3.0, "sysid": 6.0}


def kernel_routes(arm: str, hours: float) -> dict:
    """Kernel calls per route over ``hours`` of the synthetic day, in this process."""
    import threading
    from collections import Counter

    import harness
    from heatpump_optimizer import coordinator as cm
    from heatpump_optimizer import process_worker as pw
    from heatpump_optimizer import sysid
    from heatpump_optimizer import thermal_model as tm

    tl = threading.local()
    counts: Counter = Counter()
    sites: Counter = Counter()

    def site() -> str:
        f = sys._getframe(2)
        while f is not None:
            fn = f.f_code.co_filename.replace("\\", "/")
            if "/heatpump_optimizer/" in fn and not fn.endswith(("thermal_model.py", "sysid.py")):
                return f"{Path(fn).name}:{f.f_code.co_name}"
            f = f.f_back
        return "?"

    def counted(real):
        def wrap(*a, **k):
            if not getattr(tl, "inside", 0):
                route = ("worker" if getattr(tl, "worker", 0)
                         else "executor" if getattr(tl, "executor", 0) else "loop")
                counts[route] += 1
                counts[f"{route}:{real.__name__}"] += 1
                if route != "worker":
                    sites[f"{route} {site()} {real.__name__}"] += 1
            tl.inside = getattr(tl, "inside", 0) + 1
            try:
                return real(*a, **k)
            finally:
                tl.inside -= 1
        return wrap

    def flagged(name, real):
        def wrap(*a, **k):
            setattr(tl, name, getattr(tl, name, 0) + 1)
            try:
                return real(*a, **k)
            finally:
                setattr(tl, name, getattr(tl, name) - 1)
        return wrap

    kernels = [(tm.ThermalModel, n) for n in dir(tm.ThermalModel) if n.startswith("simulate_")]
    kernels += [(sysid.SystemIdentification, n) for n in SYSID_KERNELS]
    for owner, name in kernels:
        setattr(owner, name, counted(getattr(owner, name)))
    pw.run_worker = flagged("worker", pw.run_worker)
    real_ex = harness.FakeHass.async_add_executor_job

    async def executor(self, func, *args):
        tl.executor = getattr(tl, "executor", 0) + 1
        try:
            return await real_ex(self, func, *args)
        finally:
            tl.executor -= 1

    harness.FakeHass.async_add_executor_job = executor
    if arm == "fallback":
        async def unusable(hass, fn, *args):
            raise cm.ProcessWorkerUnavailable("forced by the P10 fallback arm")

        cm._await_process = unusable
    elif arm == "sysid":
        # The night's own gates (the window, cheap prices, a thawed learner, a
        # mode that heats, the comfort excursion) are the experiment's
        # business, not this arm's: forced open, so the fit is reached. The
        # fixture's pump sits in hot-water-only mode, so the mode gate opens
        # for the experiment alone and the plan keeps its own (and its cost).
        from heatpump_optimizer import pump_signals

        blocked = pump_signals.PumpSignals.space_blocked
        pump_signals.PumpSignals.space_blocked = property(
            lambda self: not getattr(tl, "sysid", 0) and blocked.fget(self))
        real_run = cm.HeatPumpOptimizerCoordinator._run_system_identification

        if asyncio.iscoroutinefunction(real_run):
            async def run_sysid(self, prices):
                tl.sysid = 1
                try:
                    return await real_run(self, prices)
                finally:
                    tl.sysid = 0
        else:  # the tree before #1658 stepped the experiment synchronously
            def run_sysid(self, prices):
                tl.sysid = 1
                try:
                    return real_run(self, prices)
                finally:
                    tl.sysid = 0

        cm.HeatPumpOptimizerCoordinator._run_system_identification = run_sysid
        sysid.SystemIdentification.conditions_met = lambda self, *a, **k: (True, "ready")
        sysid.SystemIdentification._over_excursion = lambda self, room: False
        cm.HeatPumpOptimizerCoordinator._learning_frozen = lambda self, *a, **k: None
        real_update = cm.HeatPumpOptimizerCoordinator._async_update_data

        async def armed(self):
            if self._sysid.phase == sysid.PHASE_IDLE:
                self._sysid.config.enabled = True
                self._sysid.config.min_days_between_runs = 0.0
                self._sysid.arm(cm.dt_util.now(), plant=self._thermal_params)
            out = await real_update(self)
            counts[f"phase:{self._sysid.phase}"] = 1
            if self._sysid.phase == sysid.PHASE_ABORTED:
                counts[f"why:{self._sysid.result.reason}"] = 1
            return out

        cm.HeatPumpOptimizerCoordinator._async_update_data = armed
    src = json.loads((FIXTURES / "synthetic-dhw-only.json").read_text())
    start = datetime.fromisoformat(src["window"]["start"])
    src["window"]["end"] = (start + timedelta(hours=hours)).isoformat()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "day.json"
        path.write_text(json.dumps(src))
        with contextlib.redirect_stdout(io.StringIO()):
            run = run_fixture(path, 30)
    return {"arm": arm, "cycles": run["cycles"], "counts": dict(counts),
            "sites": dict(sites.most_common(8))}


def kernel_checks() -> list[tuple[str, bool, str]]:
    """Each arm in its own interpreter (patches never leak), run side by side."""
    tz = json.loads((FIXTURES / "synthetic-dhw-only.json").read_text()).get("time_zone") or "UTC"
    procs = {arm: subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve()), "--kernels", arm],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        env=child_env(tz), cwd=ROOT) for arm in KERNEL_ARMS}
    runs: dict[str, dict | None] = {}
    for arm, proc in procs.items():
        out, err = proc.communicate()
        line = next((ln for ln in out.splitlines() if ln.startswith(MARK)), None)
        runs[arm] = None if line is None else json.loads(line[len(MARK):])
        if line is None:
            print(f"  P10 arm {arm}: rc={proc.returncode}: {err.strip()[-600:]}")
    return kernel_verdicts(runs)


def kernel_verdicts(runs: dict[str, dict | None]) -> list[tuple[str, bool, str]]:
    """The P10 barrier over the three arms' counts (``None``: the arm did not run)."""
    def got(arm, key):
        return ((runs.get(arm) or {}).get("counts") or {}).get(key, 0)

    def detail(arm):
        run = runs.get(arm)
        return "did not run" if run is None else f"{run['counts']} {run['sites']}"

    return [
        ("P10: on a replayed day no model kernel runs on the event loop or an "
         "executor thread; every one runs in the process worker",
         runs.get("base") is not None and got("base", "worker") > 0
         and got("base", "loop") == 0 and got("base", "executor") == 0,
         detail("base")),
        ("P10: with the process route unusable the kernels land on the executor "
         "(the #511 trade, counted), never on the loop",
         runs.get("fallback") is not None and got("fallback", "executor") > 0
         and got("fallback", "loop") == 0,
         detail("fallback")),
        ("P10: an armed system identification sizes, gates and fits its night "
         "in the process worker, never on the loop",
         runs.get("sysid") is not None and got("sysid", "phase:done") == 1
         and got("sysid", "loop") == 0 and got("sysid", "executor") == 0
         and got("sysid", "worker:identify") + got("sysid", "worker:identify_slab") > 0,
         detail("sysid")),
    ]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--fixture", action="append", type=Path)
    ap.add_argument("--step-minutes", type=int)
    ap.add_argument("--one", type=Path, help=argparse.SUPPRESS)
    ap.add_argument("--inject-cost", choices=("cpu", "memory", "loop"), help=argparse.SUPPRESS)
    ap.add_argument("--kernels", choices=tuple(KERNEL_ARMS), help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    if args.kernels:
        print(MARK + json.dumps(kernel_routes(args.kernels, KERNEL_ARMS[args.kernels])))
        return 0

    if args.one:
        print(MARK + json.dumps(run_fixture(args.one, args.step_minutes, args.inject_cost)))
        return 0

    from harness import Results

    R = Results("Replay: recorded days through the real coordinator")
    began = time.monotonic()
    paths = args.fixture or sorted(FIXTURES.glob("*.json"))
    R.check("at least one fixture", bool(paths), str(FIXTURES))

    R.section("controls: each invariant fires on bad data and not on good")
    for name, ok, detail in controls():
        R.check(name, ok, detail)

    R.section("sanitising: the export's rules and nightly_ha's A10 rule")
    for name, ok, detail in sanitiser_checks(paths):
        R.check(name, ok, detail)
    name, ok, detail = synthetic_reproduces()
    R.check("the synthetic fixture is what synthesize.py + export.py write", ok, detail)

    for path in paths:
        R.section(f"replay {path.name}")
        out = replay_one(R, path, args.step_minutes, None)
        if out is None:
            continue
        print(f"  {out['cycles']} cycles over {out['entities']} entities "
              f"in {out['seconds']} s; cost {out['cost']}")
        print(f"  record: {path.name} " + " ".join(
            f"{k}={math.sqrt(COST_DETECTION) * out['cost'][k]:.4g}"
            for k in ("cpu_ratio", "peak_kib", "loop_cpu_ratio")))
        R.check(f"{path.name}: at least one cycle and one entity",
                out["cycles"] > 0 and out["entities"] > 0, str(out["cycles"]))
        for name, offenders in out["results"].items():
            R.check(f"{path.name}: {name}", not offenders,
                    f"{out['counts'][name]} offender(s): " + " | ".join(offenders[:6]))
        # The perturbation, every night: a doubled cycle must be over budget.
        for kind, key in (("cpu", "cpu_ratio"), ("memory", "peak_kib"),
                          ("loop", "loop_cpu_ratio")):
            hot = replay_one(R, path, args.step_minutes, kind)
            if hot is None:
                continue
            print(f"  {kind} doubled: cost {hot['cost']}")
            fired = [o for o in hot["results"]["cycle_cost"]
                     if o.startswith(f"{key} ") and "over its budget" in o]
            R.check(f"{path.name}: cycle_cost sees a doubled cycle {kind}", bool(fired),
                    f"{key} {hot['cost'][key]} against clean {out['cost'][key]}: "
                    + " | ".join(hot["results"]["cycle_cost"][:3]))
            if kind != "memory":
                short = short_doubling(hot["cost"].get("injected_ratio", float("nan")))
                R.check(f"{path.name}: the {kind} arm doubles the whole span {key} times",
                        not short, " | ".join(short))
    print(f"\nreplay lane wall time {time.monotonic() - began:.1f} s")
    return R.close("replay checks")


if __name__ == "__main__":
    sys.exit(main())
