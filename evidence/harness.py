#!/usr/bin/env python3
"""Fix-review harness for PR #2873 (issue #2814's residue) -- REVIEWER-BUILT.

Disclosed as the reviewer's, not the finder's: the finding (#2814) ships no
committed harness (its `Reproduction` is prose over a live download), so this
one was written for the review, from the issue's own reproduction rule. It is
the round-1 fix reviewer's harness (carried in `review/2873`,
`evidence/harness.py`), landed by the round-3 fixer under fixer.md step 18 with
arms R1-R8 unchanged; R9 is the round-3 fixer's, for the round-3 finding.

R9 -- the reader's precedence of a fault code over staleness, and the export's
re-judging of it. Read past its own limit, an implausible temperature and a
negative polling flow meter must both read `implausible` from `InputReader`
(the base read the flow meter `stale`: `read_flow_kg_s` set the fault only on
a reading not already stale), and a fresh implausible entry exported past its
limit must stay `implausible`. Null control: the flow meter read inside its
limit reads `implausible` at both ends.

It drives only the public download entry point
(`diagnostics.async_get_config_entry_diagnostics`) and the collector's public
`as_dict` / `async_bundle`, so it runs UNCHANGED at the merge base and at the
head. Nothing here reads the branch; every number is a printed output.

    PYTHONPATH=tests/hastub python3 <this file>      (cwd = the tree measured)

Metric: for a download taken A minutes after a payload was published at
PUBLISHED, the ages/verdicts the download states under
`inputs.input_ages_minutes`, `inputs.input_problems[].age_minutes`,
`plan.plan_stale`, `plan.plan_age_minutes`, and the debug manifest's
`self_tests_at` / `self_tests_age_hours`.
Count key: the value the download PUBLISHES under those keys (never an input
attribute), so an honest re-base must move it and a relabel cannot.
Perturbation / null control: the export clock. At `PUBLISHED` exactly the
download must read the published ages (2.0); the same payload exported 14
minutes later must read 16.0 at the head and 2.0 at the base.
"""
from __future__ import annotations

import asyncio
import json
import sys
import tempfile
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from homeassistant.util import dt as dt_util

from harness import FakeCoordinator, FakeEntry, FakeHass
from heatpump_optimizer import debugger
from heatpump_optimizer import diagnostics as diagnostics_mod
from heatpump_optimizer.store import admitted

T0 = datetime(2026, 1, 12, tzinfo=timezone.utc)
PUBLISHED = T0 + timedelta(hours=8)

RESULTS: list[tuple[str, str]] = []


def result(name: str, value: object) -> None:
    text = str(value)
    RESULTS.append((name, text))
    print(f"RESULT {name}: {text}")


def _payload(**extra) -> dict:
    """A last-cycle payload as the coordinator publishes it, at PUBLISHED."""
    base = {
        "mode": "auto",
        "optimization_status": "ok",
        "last_optimization": PUBLISHED - timedelta(minutes=1),
        "next_optimization": PUBLISHED + timedelta(minutes=29),
        "current_action": "idle",
        "plan_stale": False,
        "input_health": "ok",
        "stale_inputs": [],
        "input_problems": [{"input": "indoor", "entity_id": "sensor.indoor",
                            "problem": "stale", "age_minutes": 2.0,
                            "max_age_minutes": 30.0}],
        "problem_inputs": ["sensor.indoor"],
        "problem_messages": ["sensor.indoor: stale (last report 2 min)"],
        "input_ages_minutes": {"indoor": 2.0, "outdoor": 5.0},
        "input_ages_at": PUBLISHED,
        "learners_frozen": False,
        "learner_freeze_reason": None,
        "space_plan": {"forecast": [1], "slots": [1], "total_cost": 1.0},
        "dhw_plan": {},
    }
    base.update(extra)
    return base


async def _download(payload: dict, after: timedelta, config: dict | None = None) -> dict:
    coord = FakeCoordinator(dict(payload), **({"_config": config} if config else {}))
    entry = FakeEntry(entry_id="review", options={})
    entry.runtime_data = coord
    dt_util.freeze(PUBLISHED + after)
    try:
        return await diagnostics_mod.async_get_config_entry_diagnostics(FakeHass(), entry)
    finally:
        dt_util.freeze(None)


def _at(doc: dict, path: str):
    node = doc
    for part in path.split("."):
        if isinstance(node, list):
            try:
                node = node[int(part)]
            except (ValueError, IndexError):
                return "<absent>"
        elif isinstance(node, dict):
            node = node.get(part, "<absent>")
        else:
            return "<absent>"
    return node


def _collector(folder: str | None = None):
    def spawn(coro):
        coro.close()
    hass = FakeHass()
    if folder:
        hass.config.path = lambda *parts: str(Path(folder, *parts))
    return debugger.DebugCollector(hass, "dbg", spawn)


def main() -> int:
    print(f"RESULT tree: {diagnostics_mod.__file__}")

    # R1 -- the age changes hands. Published 2.0 min old, exported 14 min later.
    late = asyncio.run(_download(_payload(), timedelta(minutes=14)))
    at_pub = asyncio.run(_download(_payload(), timedelta(0)))
    result("R1.input_ages_minutes.exported_14min_late",
           _at(late, "inputs.input_ages_minutes"))
    result("R1.input_problems_age.exported_14min_late",
           _at(late, "inputs.input_problems.0.age_minutes"))
    result("R1.input_ages_at.in_bundle",
           _at(late, "inputs.input_ages_at"))
    # R2 -- the null control: exported at the publish instant, ages unmoved.
    result("R2.NULL.input_ages_minutes.exported_at_publish",
           _at(at_pub, "inputs.input_ages_minutes"))
    result("R2.NULL.input_problems_age.exported_at_publish",
           _at(at_pub, "inputs.input_problems.0.age_minutes"))

    # R3 -- plan_stale re-judged at the export, with the coordinator's limit.
    payload_95 = _payload(last_optimization=PUBLISHED - timedelta(minutes=1))
    overdue = asyncio.run(_download(payload_95, timedelta(minutes=95)))
    result("R3.plan_stale.payload_false_plan_96min_old_at_export",
           _at(overdue, "plan.plan_stale"))
    result("R3.plan_age_minutes.same_download", _at(overdue, "plan.plan_age_minutes"))
    # the limit, not the floor: at a 15-min interval 3 cycles are 45 min, under
    # the 90-minute floor, so a 60-minute-old plan is fresh at both arms.
    floor = asyncio.run(_download(
        _payload(last_optimization=PUBLISHED - timedelta(minutes=60)),
        timedelta(0), {"optimization_interval": 15}))
    result("R3.plan_stale.interval_15_plan_60min_old", _at(floor, "plan.plan_stale"))

    # R4 -- the download time cannot be absent: no `input_ages_at` at all.
    no_instant = dict(_payload())
    no_instant.pop("input_ages_at")
    absent = asyncio.run(_download(no_instant, timedelta(minutes=14)))
    result("R4.absent_instant.input_ages_minutes.exported_14min_late",
           _at(absent, "inputs.input_ages_minutes"))
    result("R4.absent_instant.input_problems_age",
           _at(absent, "inputs.input_problems.0.age_minutes"))
    ahead = asyncio.run(_download(
        _payload(input_ages_at=PUBLISHED + timedelta(minutes=5)),
        timedelta(0)))
    result("R4.instant_ahead.input_ages_minutes",
           _at(ahead, "inputs.input_ages_minutes"))
    # a plan the clock cannot date, and one never judged
    undated = asyncio.run(_download(
        _payload(last_optimization=PUBLISHED + timedelta(minutes=5), plan_stale=True),
        timedelta(0)))
    result("R4.undated_plan.plan_stale_keeps_payload", _at(undated, "plan.plan_stale"))
    never = dict(_payload(last_optimization=None))
    never.pop("plan_stale")
    unjudged = asyncio.run(_download(never, timedelta(minutes=95)))
    result("R4.never_judged_plan.plan_stale", _at(unjudged, "plan.plan_stale"))

    # R5 -- which published age-named leaves move at all, base vs head is the
    # caller's comparison; this prints both exports of the same payload.
    def ages(node, prefix=""):
        out = {}
        if isinstance(node, dict):
            for key, item in node.items():
                path = f"{prefix}.{key}" if prefix else key
                named = any(word in key for word in
                            ("age", "_at", "hours", "minutes", "expired", "since"))
                if isinstance(item, (dict, list)):
                    if named:
                        out[path] = json.dumps(item, default=str, sort_keys=True)
                    out.update(ages(item, path))
                elif named:
                    out[path] = item
        elif isinstance(node, list):
            for index, item in enumerate(node):
                out.update(ages(item, f"{prefix}.{index}"))
        return out

    moved = {}
    base_ages, head_ages = ages(at_pub), ages(late)
    for key in sorted(set(base_ages) | set(head_ages)):
        if base_ages.get(key, "<absent>") != head_ages.get(key, "<absent>"):
            moved[key] = [base_ages.get(key, "<absent>"), head_ages.get(key, "<absent>")]
    result("R5.age_leaves_moved_between_publish_export", json.dumps(moved, default=str))
    result("R5.age_leaves_at_export", json.dumps(head_ages, default=str))

    # R8 -- the neighbouring verdicts beside the re-based ages.
    result("R8.input_health_and_flags.exported_14min_late",
           json.dumps({"input_health": _at(late, "inputs.input_health"),
                       "stale_inputs": _at(late, "inputs.stale_inputs"),
                       "problem_inputs": _at(late, "inputs.problem_inputs")},
                      default=str))
    # R8b -- the same verdicts when the re-based age crosses the input's own
    # max_age: 20 min old at read, max_age 30, exported 40 min later.
    crossed = asyncio.run(_download(_payload(
        input_ages_minutes={"indoor": 20.0},
        input_problems=[{"input": "indoor", "entity_id": "sensor.indoor",
                         "problem": "stale", "age_minutes": 20.0,
                         "max_age_minutes": 30.0}],
        problem_messages=["sensor.indoor: stale (last report 20 min)"],
        input_health="ok", stale_inputs=[], problem_inputs=[]),
        timedelta(minutes=40)))
    result("R8b.verdicts_beside_a_crossed_age.exported_40min_late",
           json.dumps({"input_health": _at(crossed, "inputs.input_health"),
                       "stale_inputs": _at(crossed, "inputs.stale_inputs"),
                       "problem_messages": _at(crossed, "inputs.problem_messages"),
                       "input_ages_minutes": _at(crossed, "inputs.input_ages_minutes"),
                       "problem_age": _at(crossed, "inputs.input_problems.0.age_minutes")},
                      default=str))

    # R6 -- the stored self-tests' run time and the manifest's age of it.
    stored = {"feeds": {"ms": 1.0}}
    stamped = T0 + timedelta(hours=5)
    with tempfile.TemporaryDirectory(prefix="review2873-") as folder:
        Path(folder, ".storage").mkdir()
        timed = _collector(folder)
        timed.started_at, timed.final, timed.self_tests = T0, True, stored
        setattr(timed, "self_tests_at", stamped)
        document = timed.as_dict()
        result("R6.as_dict.self_tests_at", document.get("self_tests_at", "<absent>"))
        result("R6.store_admits_self_tests_at",
               admitted("debug", {"self_tests": "{}", "self_tests_at": stamped.isoformat()}))
        result("R6.collector_attribute", getattr(timed, "self_tests_at", "<absent>"))
        bare = _collector(folder)
        setattr(bare, "self_tests_at", stamped)  # an instant with no stored results
        result("R6.as_dict.instant_without_results",
               bare.as_dict().get("self_tests_at", "<absent>"))
        dt_util.freeze(stamped)
        try:
            manifest = asyncio.run(timed.async_bundle(
                types.SimpleNamespace(integration_version="0")))["manifest"]
        finally:
            dt_util.freeze(None)
    result("R6.manifest.self_tests_at", manifest.get("self_tests_at", "<absent>"))
    result("R6.manifest.self_tests_age_hours", manifest.get("self_tests_age_hours", "<absent>"))

    # R7 -- the coordinator's own predicate, unbound over its two reads. The
    # config is a bare namespace so the interval's own type reaches the seam
    # (EntryConfig coerces a bool/string, so a FakeCoordinator would hide it).
    def stale(interval, age):
        fake = types.SimpleNamespace(
            effective_config=types.SimpleNamespace(optimization_interval=interval),
            _plan_age_minutes=lambda: age,
        )
        try:
            return diagnostics_mod.HeatPumpOptimizerCoordinator._plan_is_stale(fake)
        except Exception as exc:  # noqa: BLE001 -- the base arm raises here, which is the point
            return f"raised {type(exc).__name__}: {exc}"

    for interval, age in ((30, 90.0), (30, 90.1), (True, 100.0), ("15", 100.0)):
        result(f"R7._plan_is_stale.interval_{interval!r}_age_{age}",
               stale(interval, age))

    # R9 -- the fault code outranks staleness, at the reader and at the export.
    from harness import FakeState
    from heatpump_optimizer.inputs import InputReader

    def read_class(key, state, unit, read, after):
        """The class the reader gives ``state``, read ``after`` its last report;
        a polling source (last_reported past last_updated) is held to its limit."""
        reported = PUBLISHED - timedelta(hours=1)
        hass = FakeHass({"sensor.probe": FakeState(
            state, last_updated=reported - timedelta(hours=1),
            last_reported=reported, unit=unit)})
        reader = InputReader(hass, {key: "sensor.probe"}, now=lambda: reported + after)
        reading = read(reader, key)
        return reading.problem, reading.max_age_minutes

    flow = ("flow_meter_entity", "-1", "kg/s", lambda r, k: r.read_flow_kg_s(k))
    temp = ("outdoor_temp_entity", "-127", "°C", lambda r, k: r.read(k))
    for name, row in (("flow_negative", flow), ("temperature_minus_127", temp)):
        _, limit = read_class(*row, timedelta(minutes=1))
        result(f"R9.{name}.limit_minutes", limit)
        if isinstance(limit, (int, float)):
            result(f"R9.{name}.read_past_limit",
                   read_class(*row, timedelta(minutes=limit + 1))[0])
            result(f"R9.NULL.{name}.read_inside_limit",
                   read_class(*row, timedelta(minutes=1))[0])
    exported = asyncio.run(_download(_payload(
        input_ages_minutes={"flow": 5.0},
        input_problems=[{"input": "flow", "entity_id": "sensor.flow",
                         "problem": "implausible", "age_minutes": 5.0,
                         "max_age_minutes": 30.0}],
        problem_messages=["sensor.flow: outside its plausible range"],
        input_health="1 missing", stale_inputs=[], problem_inputs=["sensor.flow"]),
        timedelta(minutes=40)))
    result("R9.implausible_exported_past_limit",
           json.dumps({"problem": _at(exported, "inputs.input_problems.0.problem"),
                       "stale_inputs": _at(exported, "inputs.stale_inputs"),
                       "input_health": _at(exported, "inputs.input_health")},
                      default=str))

    print(f"RESULT checks: {len(RESULTS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
