"""The keep table for the told COP and outdoor widths (#3767, P5; R11-SEAM-learners).

``sysid._slab_ua_told_halfwidth`` prices four told quantities: the slab pair,
the COP (``TOLD_COP_LOG_SD``, log units) and the outdoor reading
(``TOLD_OUTDOOR_SD_K``, K). The two new widths are a liveness trade the owner
decides: each widens the adoption interval of every night, so a width large
enough to cover a real misstatement refuses honest nights too. This prints,
per width pair, how many of the derived single-zone presets' noise-free
nights (plant equal to its declaration) the gate still admits, against the
column ``0/0`` (the gate without the two terms): the price of each choice in
nights kept.

The night is the features check's (``_r9p5_derived_night``): 21 degC, outdoor
0 degC, the production ``SystemIdentification`` stepped on a 15-minute cadence
with the declared plant simulated at one-minute steps.

    PYTHONPATH=tests/hastub:tests python3 dev/audit/harnesses/sysid_told_keep.py

Rows: ``RESULT keep_cop<sd>_out<sd>K=<admitted>/<nights> of_untold=<admitted at 0/0>``.
A row at ``0/0`` that differs from ``of_untold`` is the harness lying.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
sys.path[:0] = ["tests", "custom_components"]

import numpy as np  # noqa: E402

import harness  # noqa: E402,F401
from profiles import house  # noqa: E402
from heatpump_optimizer import presets  # noqa: E402
from heatpump_optimizer import sysid as S  # noqa: E402
from heatpump_optimizer.sysid import HousePlant  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402

NIGHT = datetime(2026, 1, 15, 23, 0, tzinfo=timezone.utc)
STRUCTURES = (presets.STRUCTURE_TIMBER_CRAWLSPACE, presets.STRUCTURE_TIMBER_SLAB,
              presets.STRUCTURE_CONCRETE_SLAB, presets.STRUCTURE_MASONRY)
ERAS = (presets.ERA_PRE_1960, presets.ERA_1960_1980, presets.ERA_1980_2005, presets.ERA_POST_2005,
        presets.ERA_LOW_ENERGY)
COP_SDS = (0.0, 0.02, 0.03, 0.05)
OUT_SDS = (0.0, 0.25, 0.5, 1.0)


def night(structure: str, era: str) -> bool:
    """Whether the gate admits this derived preset's noise-free night."""
    cfg = house(two_zone=False, dhw=False)
    derived = presets.derive(presets.BuildingPreset(
        structure=structure, era=era, heated_area_m2=120, lower_emitter=presets.EMITTER_FLOOR))
    derived.pop("heating_response_hours", None)
    cfg.update(derived)
    decl = ThermalParameters.from_config(cfg)
    decl.two_zone_enabled = False
    model = ThermalModel(ThermalParameters.from_config(cfg))
    model.params.two_zone_enabled = False
    ua = float(decl.heat_loss_coefficient * decl.house_heat_loss_scale)
    sid = S.SystemIdentification(S.SysIdConfig(min_days_between_runs=0.0, gains_prior_kw=float(decl.internal_gains)))
    if not sid.arm(NIGHT, plant=decl):
        return False
    hold = max(ua * 21.0 - float(decl.internal_gains), 0.0)
    st = ThermalState(room_temperature=21.0,
                      slab_temperature=21.0 + hold / max(float(decl.slab_heat_transfer), 1e-9),
                      outdoor_temperature=0.0)
    when = NIGHT
    for _ in range(32):
        override = sid.step(
            now=when, room_temp=st.room_temperature, outdoor_temp=0.0, price=0.1,
            price_horizon=np.full(48, 1.0), learner_samples=0, max_power_kw=3.5, cop=3.0,
            plan_power_kw=hold / 3.0,
            house=HousePlant(ua=ua, capacity=float(decl.room_thermal_mass), gains=float(decl.internal_gains),
                             slab_mass=float(decl.slab_thermal_mass), slab_transfer=float(decl.slab_heat_transfer)),
        )
        if not sid.active:
            break
        el = hold / 3.0 if override is None else float(override)
        for _ in range(15):
            st = model.simulate_step(st, electrical_power=0.0, outdoor_temp=0.0, dt_hours=1.0 / 60,
                                     external_heat_kw=el * 3.0)
        when += timedelta(hours=0.25)
    return bool(S.adoption_decision(sid.result, decl, sid.config).admit)


def kept(cop_sd: float, out_sd: float) -> int:
    S.TOLD_COP_LOG_SD, S.TOLD_OUTDOOR_SD_K = cop_sd, out_sd
    return sum(night(s, e) for s in STRUCTURES for e in ERAS)


def main() -> None:
    shipped = (S.TOLD_COP_LOG_SD, S.TOLD_OUTDOOR_SD_K)
    n = len(STRUCTURES) * len(ERAS)
    untold = kept(0.0, 0.0)
    for cop_sd in COP_SDS:
        for out_sd in OUT_SDS:
            got = untold if (cop_sd, out_sd) == (0.0, 0.0) else kept(cop_sd, out_sd)
            mark = " shipped" if (cop_sd, out_sd) == shipped else ""
            print(f"RESULT keep_cop{cop_sd:g}_out{out_sd:g}K={got}/{n} of_untold={untold}{mark}", flush=True)
    S.TOLD_COP_LOG_SD, S.TOLD_OUTDOOR_SD_K = shipped


if __name__ == "__main__":
    main()
