"""Every ``_apply_house_heat_loss_scale`` caller against the refit accept path.

The accept path is ``async_adopt_heat_loss_refit``: it writes a scale only
when ``model_restart_advice`` carries a ``heat_loss_refit`` scale, and that
scale is what ``_clipped_refit_scale`` admitted. This drives each other
caller on the same two plants — no accuracy samples, and four settled days
— and prints the scale each one leaves beside the scale the accept path
leaves. A caller that is the accept path prints the same scale on both
plants. One that is not, does not.

    PYTHONPATH=tests/hastub python3 tools/audit/harnesses/scale_writer_seams.py

Run from anywhere; the script locates the repository from its own path.
"""
from __future__ import annotations

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


import asyncio
import logging
import os
import sys
from dataclasses import replace
from datetime import datetime, timedelta, timezone

ROOT = repo_root(__file__)
os.chdir(ROOT)
sys.path[:0] = [
    str(ROOT / "tests" / "hastub"),
    str(ROOT / "tests"),
    str(ROOT / "custom_components"),
]

logging.disable(logging.CRITICAL)

from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer.accuracy import AccuracySample  # noqa: E402
from heatpump_optimizer.const import (  # noqa: E402
    HOUSE_HEAT_LOSS_SCALE_MAX,
    HOUSE_HEAT_LOSS_SCALE_MIN,
)
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
    async_adopt_heat_loss_refit,
    model_restart_advice,
)

COORD = ROOT / "custom_components/heatpump_optimizer/coordinator.py"
T0 = datetime(2026, 1, 10, tzinfo=timezone.utc)
START = 1.8


def g(value: object) -> str:
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return format(value, ".10g")
    return str(value)


def emit(key: str, value: object) -> None:
    print(f"RESULT {key}={g(value)}")


def seams() -> list[tuple[int, str, str]]:
    """Each ``_apply_house_heat_loss_scale`` hit with the def that contains it."""
    defs: list[tuple[int, str]] = []
    hits: list[tuple[int, str, str]] = []
    for n, line in enumerate(COORD.read_text().splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("def ") or stripped.startswith("async def "):
            defs.append((n, stripped.split("def ", 1)[1].split("(", 1)[0]))
        if "_apply_house_heat_loss_scale" not in line:
            continue
        owner = next((name for ln, name in reversed(defs) if ln <= n), "-")
        hits.append((n, owner, stripped))
    return hits


def plant(admitted: bool) -> HeatPumpOptimizerCoordinator:
    coord = HeatPumpOptimizerCoordinator(
        FakeHass({}),
        FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home"}),
    )
    coord._apply_house_heat_loss_scale(START)
    coord._snapshot_ring.alarmed = True
    if admitted:
        for i in range(1, int(round(4.0 * 24 / 0.5)) + 1):
            coord._accuracy.record(AccuracySample(
                when=T0 + timedelta(hours=0.5 * i),
                predicted_temp=21.0,
                actual_temp=20.97,
                outdoor_temp=-4.0,
            ))
    return coord


def refit_scale(coord: HeatPumpOptimizerCoordinator) -> float | None:
    refit = model_restart_advice(coord)["refit"]
    if not refit:
        return None
    return refit.get("scale")


async def accept(admitted: bool) -> tuple[bool, float, float | None]:
    coord = plant(admitted)
    offered = refit_scale(coord)
    applied = await async_adopt_heat_loss_refit(coord)
    return applied, float(coord._house_heat_loss_scale), offered


async def nameplate(admitted: bool) -> float:
    coord = plant(admitted)
    await coord.async_update_thermal_params({"house_heat_loss_coefficient": 0.3})
    return float(coord._house_heat_loss_scale)


def adopt(admitted: bool) -> tuple[float, str]:
    coord = plant(admitted)
    coord._thermal_params.slab_heat_transfer *= 100.0
    coord._sysid.result = replace(
        coord._sysid.result,
        completed=True,
        ua_profile_halfwidth=0.0,
        heat_loss_kw_per_c=0.30,
    )
    coord._adopt_system_identification()
    return float(coord._house_heat_loss_scale), str(coord._sysid.result.reason)


async def load(admitted: bool) -> float:
    coord = plant(admitted)

    async def stored() -> dict[str, float]:
        return {"house_heat_loss_scale": 1.4, "house_heat_loss_samples": 3}

    coord._thermal_learning_store.async_load = stored  # type: ignore[method-assign]
    await coord._async_load_thermal_learning()
    return float(coord._house_heat_loss_scale)


def reanchor(admitted: bool, anchor: float, coefficient: float) -> tuple[bool, float]:
    coord = plant(admitted)
    coord._thermal_params.heat_loss_coefficient = coefficient
    coord._house_heat_loss_samples = 200
    changed = coord._reanchor_house_heat_loss_scale(anchor)
    return bool(changed), float(coord._house_heat_loss_scale)


def payload(admitted: bool) -> float:
    coord = plant(admitted)
    coord._apply_learner_payloads(
        {"thermal_learning": {"house_heat_loss_scale": 1.25}}
    )
    return float(coord._house_heat_loss_scale)


async def learner(admitted: bool, *, observed: float) -> float:
    """One interval step. ``simulate_step`` is replaced so the residual is
    ``observed - 21.0``; the step, the guards and the setter are the
    coordinator's. ``observed == 21.0`` is the zero-residual control."""
    coord = plant(admitted)
    coord._learning_frozen = lambda *_a, **_k: None  # type: ignore[method-assign]
    coord._interval_space_power = lambda: 0.5  # type: ignore[method-assign]
    coord._current_state.room_temperature = observed
    coord._current_state.outdoor_temperature = -4.0
    coord._last_house_sample = replace(
        coord._current_state, room_temperature=21.0
    )
    coord._last_house_sample_time = dt_util.now() - timedelta(minutes=30)

    def simulate(*_a, **_k):
        return replace(coord._last_house_sample, room_temperature=21.0)

    coord._thermal_model.simulate_step = simulate  # type: ignore[method-assign]
    await coord._async_learn_house_heat_loss()
    return float(coord._house_heat_loss_scale)


def clipped() -> float:
    coord = plant(False)
    coord._apply_house_heat_loss_scale(9.0)
    return float(coord._house_heat_loss_scale)


async def main() -> int:
    found = seams()
    emit("seam_count", len(found))
    for n, owner, text in found:
        print(f"RESULT seam line={n} owner={owner} text={text}")

    empty_applied, empty_scale, empty_offer = await accept(False)
    full_applied, full_scale, full_offer = await accept(True)
    emit("accept_empty_applied", empty_applied)
    emit("accept_empty_scale", empty_scale)
    emit("accept_empty_offer", empty_offer)
    emit("accept_admitted_applied", full_applied)
    emit("accept_admitted_scale", full_scale)
    emit("accept_admitted_offer", full_offer)

    pairs = {
        "nameplate": (await nameplate(False), await nameplate(True)),
        "adopt": (adopt(False)[0], adopt(True)[0]),
        "load": (await load(False), await load(True)),
        "reanchor_in_range": (
            reanchor(False, 0.15, 0.20)[1],
            reanchor(True, 0.15, 0.20)[1],
        ),
        "reanchor_reset": (
            reanchor(False, 0.02, 0.30)[1],
            reanchor(True, 0.02, 0.30)[1],
        ),
        "reanchor_below_step": (
            reanchor(False, 0.15 * 1.02, 0.15)[1],
            reanchor(True, 0.15 * 1.02, 0.15)[1],
        ),
        "payload": (payload(False), payload(True)),
        "learner": (await learner(False, observed=20.97), await learner(True, observed=20.97)),
    }
    zero = await learner(False, observed=21.0)
    emit("learner_zero_residual_empty_scale", zero)
    emit("learner_zero_residual_empty_equals_accept", zero == empty_scale)
    emit("adopt_empty_reason", adopt(False)[1])
    emit("adopt_admitted_reason", adopt(True)[1])
    emit("setter_clip_of_9", clipped())
    emit("setter_min", HOUSE_HEAT_LOSS_SCALE_MIN)
    emit("setter_max", HOUSE_HEAT_LOSS_SCALE_MAX)
    for name, (left, right) in pairs.items():
        emit(f"{name}_empty_scale", left)
        emit(f"{name}_admitted_scale", right)
        emit(f"{name}_empty_equals_accept", left == empty_scale)
        emit(f"{name}_admitted_equals_accept", right == full_scale)

    # The accept path wrote the offered scale, and the offer was refused on
    # the empty plant. A mismatch here means the twins are not the operation
    # the other rows are compared with.
    same = (
        empty_offer is None
        and empty_applied is False
        and empty_scale == START
        and full_offer is not None
        and full_applied is True
        and full_scale == full_offer
    )
    emit("accept_matches_offer", same)
    return 0 if same else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
