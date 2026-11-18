"""The plan's heating slots: a per-step power schedule as the slots a person reads.

A pure presentation of one channel's schedule, beside nothing it computes
with: the coordinator publishes the space and hot-water plans' ``slots`` from
it, and ``async_simulate`` counts a draft's slots with it. It reads no
coordinator state, so it is not the coordinator's (P141). It merges steps on
``thermal_model.channel_heating_steps``, beside the running rule it refines,
so it reaches neither the solver nor Home Assistant. It is not in
``payload.py`` beside :class:`~.payload.PlanSlot` because that module holds
the payload's shapes on the standard library alone, and this merge needs
numpy and the thermal model.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from .payload import PlanSlot
from .thermal_model import channel_heating_steps


def plan_slots(
    timestamps: list[datetime],
    powers: list[float],
    prices: list[float],
    dt_hours: float,
    reasons: list[str] | None = None,
    other_powers: list[float] | None = None,
) -> list[PlanSlot]:
    """Collapse a per-step power schedule into contiguous heating slots.

    The step schedule is what the optimizer produces, but what a person
    wants to see is "the pump runs from 02:00 to 04:30 and that costs 4.20".
    Consecutive steps the channel heats at (``channel_heating_steps``) are
    merged into one slot and summarised with their energy, price and cost.

    Each slot also carries the reason code that dominates it, so an
    unexpected slot is no longer indistinguishable from a bug.

    ``other_powers`` is the OTHER channel's schedule (hot water when
    these are space steps, and vice versa). Where both are active in
    the same step the pump is time-sharing the quarter hour — a
    deliberate relaxation, not double-booking — and the slot says so
    via ``shared_kwh``: the other channel's energy inside this slot's
    shared steps. Zero-overlap slots carry no key, so captures without
    overlap are unchanged.
    """
    slots: list[PlanSlot] = []
    start_idx: int | None = None
    heating = channel_heating_steps(powers, other_powers)
    other_heating = channel_heating_steps(other_powers or [], powers)

    def close(end_idx: int) -> None:
        assert start_idx is not None
        span = list(range(start_idx, end_idx))
        energy = sum(powers[i] for i in span) * dt_hours
        cost = sum(powers[i] * prices[i] for i in span) * dt_hours
        end_ts = (
            timestamps[end_idx]
            if end_idx < len(timestamps)
            else timestamps[-1] + timedelta(hours=dt_hours)
        )
        duration = len(span) * dt_hours
        slot: PlanSlot = {
            "start": timestamps[start_idx].isoformat(),
            "end": end_ts.isoformat(),
            "duration_hours": round(duration, 2),
            "avg_power_kw": round(energy / duration, 2) if duration else 0.0,
            "energy_kwh": round(energy, 3),
            "avg_price": (round(cost / energy, 4) if energy > 1e-9 else 0.0),
            "cost": round(cost, 2),
        }
        if other_powers is not None:
            shared = dt_hours * sum(
                other_powers[i] for i in span if i < len(other_heating) and other_heating[i]
            )
            if shared > 1e-9:
                slot["shared_kwh"] = round(shared, 3)
        if reasons:
            codes = [
                reasons[i]
                for i in span
                if i < len(reasons) and reasons[i] != "idle"
            ]
            if codes:
                # The most frequent code within the slot, which reads
                # better than a list when a slot spans two motivations.
                slot["reason"] = max(set(codes), key=codes.count)
                slot["reasons"] = sorted(set(codes))
        slots.append(slot)

    for i, on in enumerate(heating):
        if on:
            if start_idx is None:
                start_idx = i
        elif start_idx is not None:
            close(i)
            start_idx = None
    if start_idx is not None:
        close(len(powers))
    return slots
