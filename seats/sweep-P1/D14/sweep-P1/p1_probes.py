#!/usr/bin/env python3
"""Round-11 class sweep P1: probes for the seams p1_seams.py lists beyond the judged sites.

  PYTHONPATH=tests/hastub:. python3 p1_probes.py [--perturb ARM]

Arms (each prints RESULT <arm>=<count>; a non-zero count is a failing probe):
  config-effective  config_flow._effective (opt-float): the options-flow band check reads the
                    STORED option through float() with no guard; a wrong-typed stored option
                    (an older entry, D1-s2-05's population) makes _power_errors / _partload_errors raise instead of
                    returning a form error. Counts stored spellings that raise.
                    Null: well-typed stored options raise 0. --perturb config-effective wraps
                    _effective in the guard (unparseable stored value -> default): 0.
  price-extreme     price_model ingress (feed-instant seams _raw_start, _entries_by_day, _noon):
                    Tibber and entity rows stamped 0001-01-01 / 9999-12-31; counts raises in
                    prices_from_* -> hourly_from_entries / quarters_from_entries.
  manual-extreme    manual_plan._parse_dt via parse_channel/build_override (service data):
                    slot stamps at the datetime range ends; counts raises other than the
                    service's own ValueError refusal.
  store-bool        bool leaves on the store loaders the enumerator lists under bool-number
                    (DrawStats.from_dict, tariff._stored_peaks, off_restore._entry_of,
                    ComfortLearner.from_dict): counts loaders that admit True as the number 1.0.
                    Evidence for the disposition only (see sweep-P1.md), not an instance count.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from custom_components.heatpump_optimizer import config_flow, manual_plan, price_model
from custom_components.heatpump_optimizer import dhw_draws, tariff, off_restore, comfort_learning


def arm_config(perturb: bool) -> tuple[int, int]:
    if perturb:
        orig = config_flow._effective

        def guarded(candidate, current, key, default):
            try:
                return orig(candidate, current, key, default)
            except (TypeError, ValueError):
                return float(default)
        config_flow._effective = guarded
    keys = [config_flow.CONF_HEAT_PUMP_MIN_POWER, config_flow.CONF_HEAT_PUMP_MAX_POWER,
            config_flow.CONF_HEAT_PUMP_COP_PARTLOAD_DERATE]
    checks = (config_flow._power_errors, config_flow._partload_errors)  # the two _effective callers
    bad = ["abc", None, {"x": 1}, [1.0]]
    raised = 0
    for check in checks:
        for k in keys:
            for v in bad:
                try:
                    check({}, {k: v})
                except (TypeError, ValueError):
                    raised += 1
    null = 0
    for check in checks:
        for k in keys:
            try:
                check({}, {k: 0.1})
            except (TypeError, ValueError):
                null += 1
    return raised, null


def arm_opt_other() -> dict[str, int]:
    """The other option reads the widened opt-float rule lists, each through its public caller."""
    from custom_components.heatpump_optimizer import topology, quiet_windows
    from custom_components.heatpump_optimizer.const import (CONF_WOOD_TANK_VOLUME, CONF_MIXING_VALVE_TARGET,
        CONF_MIXING_VALVE_TARGET_ENTITY, CONF_COMPRESSOR_FREQ_MIN_HZ, CONF_COMPRESSOR_FREQ_SENSOR)
    out = {}
    cases = {
        "topology.describe_setup": lambda v: topology.describe_setup({CONF_WOOD_TANK_VOLUME: v}),
        "topology._slot_extras": lambda v: topology._slot_extras(CONF_MIXING_VALVE_TARGET_ENTITY,
                                                                 {CONF_MIXING_VALVE_TARGET: v}),
        "quiet_windows.silent_cap_kw->measured_ceiling_kw": lambda v: quiet_windows.measured_ceiling_kw(
            {CONF_COMPRESSOR_FREQ_MIN_HZ: v, CONF_COMPRESSOR_FREQ_SENSOR: "sensor.hz"},
            lambda _e: None, 9.0),
    }
    for name, call in cases.items():
        n = 0
        for v in ("abc", {"x": 1}, [1.0]):
            try:
                call(v)
            except (TypeError, ValueError):
                n += 1
        null = 0
        try:
            call(1.0 if "describe" not in name else 200.0)
        except (TypeError, ValueError):
            null += 1
        out[name] = (n, null)
    return out


def arm_price() -> int:
    raised = 0
    stamps = ["0001-01-01T00:00:00+00:00", "9999-12-31T23:00:00+00:00"]
    for s in stamps:
        rows = [{"startsAt": s, "total": 1.0}] + [
            {"startsAt": (datetime(2026, 11, 18, tzinfo=timezone.utc) + timedelta(hours=h)).isoformat(), "total": 1.0}
            for h in range(24)]
        payload = {"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {"today": rows, "tomorrow": []}}}]}}}
        attrs = {"raw_today": [{"start": r["startsAt"], "value": 1.0} for r in rows], "raw_tomorrow": []}
        for build in (lambda: price_model.prices_from_tibber_payload(payload),
                      lambda: price_model.prices_from_entity_attributes(attrs)):
            try:
                entries = build()
                if isinstance(entries, list):
                    price_model.hourly_from_entries(entries)
                    price_model.quarters_from_entries(entries)
            except Exception:  # noqa: BLE001 -- any raise is the count
                raised += 1
    return raised


def arm_manual() -> int:
    now = datetime(2026, 11, 18, 12, tzinfo=timezone.utc)
    raised = 0
    for start, end in (("0001-01-01T00:00:00+00:00", "2026-11-18T13:00:00+00:00"),
                       ("2026-11-18T12:30:00+00:00", "9999-12-31T23:59:59+00:00")):
        raw = [{"start": start, "end": end, "on": True}]
        try:
            manual_plan.build_override(dhw_slots=raw, space_slots=None,
                                       expires_at=now + timedelta(hours=2), now=now)
        except ValueError:
            pass  # the service's refusal, surfaced as a validation error
        except Exception:  # noqa: BLE001
            raised += 1
    return raised


def arm_store_bool() -> list[str]:
    admitted: list[str] = []
    if dhw_draws.DrawStats.from_dict({"reservoirs": {"a": [True]}}).reservoirs.get("a") == [1.0]:
        admitted.append("dhw_draws.DrawStats.from_dict")
    if [kw for kw, _ in tariff._stored_peaks([True], None)] == [1.0]:
        admitted.append("tariff._stored_peaks")
    if off_restore._entry_of(True) == 1.0:
        admitted.append("off_restore._entry_of")
    lr = comfort_learning.ComfortLearner.from_dict({"configured_weight": True, "learned_weight": 0.5}, 1.0)
    if abs(lr.learned_weight - 0.5) < 1e-9:
        admitted.append("comfort_learning.ComfortLearner.from_dict")
    # The coordinator's energy-totals loader and the legionella guard's load, on a stub self/store.
    import asyncio
    from custom_components.heatpump_optimizer import coordinator, legionella

    class _Store:
        def __init__(self, data):
            self.data = data

        async def async_load(self):
            return self.data
    co = coordinator.HeatPumpOptimizerCoordinator.__new__(coordinator.HeatPumpOptimizerCoordinator)
    co._energy_store = _Store({"heat_pump_kwh": True})
    co._energy_totals = {"heat_pump_kwh": 0.0}
    try:
        asyncio.run(co._async_load_energy_totals())
    except AttributeError:
        pass  # past the leaf under test; the totals are already folded
    if co._energy_totals.get("heat_pump_kwh") == 1.0:
        admitted.append("coordinator._async_load_energy_totals")
    co2 = coordinator.HeatPumpOptimizerCoordinator.__new__(coordinator.HeatPumpOptimizerCoordinator)
    co2._ledger_store = _Store({"operation_score": True})
    co2._operation_score = None
    try:
        asyncio.run(co2._async_load_ledger())
    except Exception:  # noqa: BLE001 -- the riders after the score need members the stub lacks
        pass
    if co2._operation_score == 1.0:
        admitted.append("coordinator._async_load_ledger")
    g = legionella.LegionellaGuard.__new__(legionella.LegionellaGuard)
    g.store = _Store({"last_attempt": "2026-11-17T10:00:00+00:00", "last_attempt_peak": True})
    g.attempt = None
    g.attempt_peak = None
    g.last_cycle = None
    g._load_switch_record = lambda _s: None
    try:
        asyncio.run(g.async_load())
    except Exception:  # noqa: BLE001 -- the stub lacks the fresh-install path's members
        pass
    if g.attempt_peak == 1.0 and not isinstance(g.attempt_peak, bool):
        admitted.append("legionella.LegionellaGuard.async_load")
    return admitted


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", choices=["config-effective"])
    a = ap.parse_args()
    raised, null = arm_config(a.perturb == "config-effective")
    print(f"RESULT config_effective_stored_wrong_type_raised={raised}")
    print(f"RESULT config_effective_null_well_typed_raised={null}")
    if a.perturb:
        return
    for name, (n, null) in arm_opt_other().items():
        print(f"RESULT opt_other {name} stored_wrong_type_raised={n} null={null}")
    print(f"RESULT price_extreme_stamp_raised={arm_price()}")
    print(f"RESULT manual_extreme_stamp_raised={arm_manual()}")
    got = arm_store_bool()
    print(f"RESULT store_bool_admitted_as_number={len(got)} of 7 ({','.join(got)})")


if __name__ == "__main__":
    main()
