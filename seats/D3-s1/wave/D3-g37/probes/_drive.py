# Shared driver for the box D3-g37 probes (not a harness itself; no RESULT lines).
# Drives the production SystemIdentification state machine against the production ThermalModel
# plant, ported from dev/audit/rounds/round5/D7/seat-a/sysid_step_bias.py:run_experiment (main tree):
# arm -> settle -> step -> relax -> identify (identify_slab when a plant is declared, identify()
# otherwise), so every sysid symbol the probes mutate is reached the way the coordinator reaches it.
import _mut  # noqa: F401  (thread pin and sys.path first)
from datetime import datetime, timedelta

import numpy as np

from custom_components.heatpump_optimizer.presets import (
    STRUCTURE_TIMBER_CRAWLSPACE, STRUCTURE_MASONRY, STRUCTURE_CONCRETE_SLAB,
    ERA_POST_2005, ERA_PRE_1960, ERA_1960_1980, EMITTER_RADIATORS, EMITTER_FLOOR,
    BuildingPreset, derive,
)
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from custom_components.heatpump_optimizer import sysid
from custom_components.heatpump_optimizer.sysid import SysIdConfig, SystemIdentification

PRESETS = {
    "light_new": BuildingPreset(structure=STRUCTURE_TIMBER_CRAWLSPACE, era=ERA_POST_2005,
                                heated_area_m2=120, lower_emitter=EMITTER_RADIATORS),
    "heavy_old": BuildingPreset(structure=STRUCTURE_MASONRY, era=ERA_PRE_1960,
                                heated_area_m2=200, lower_emitter=EMITTER_FLOOR),
    "typical_slab": BuildingPreset(structure=STRUCTURE_CONCRETE_SLAB, era=ERA_1960_1980,
                                   heated_area_m2=150, lower_emitter=EMITTER_FLOOR),
}
START = datetime(2026, 1, 15, 23, 30)
T_OUT = 0.0
T_BASE = 21.0
CADENCE_H = 0.5
HORIZON = np.full(48, 0.10)
PRICE = 0.05


def params_for(preset, **overrides):
    cfg = derive(PRESETS[preset])
    cfg["two_zone_mode"] = "off"
    p = ThermalParameters.from_config(cfg)
    p.two_zone_enabled = False
    for k, v in overrides.items():
        setattr(p, k, v)
    return p


def sysid_config(p):
    return SysIdConfig(enabled=True, gains_prior_kw=float(p.internal_gains),
                       thermal_mass_prior=float(p.room_thermal_mass))


def run(config_params, *, declare_plant=True, true_params=None, noise=0.0, seed=0, cadence_h=CADENCE_H):
    house = true_params or config_params
    plant = ThermalModel(house)
    cfg = sysid_config(config_params)
    si = SystemIdentification(cfg)
    armed = si.arm(START, plant=config_params if declare_plant else None)
    if not armed:
        return {"armed": False, "result": si.result}
    rng = np.random.default_rng(seed)
    cop = float(plant.compute_cop(T_OUT))
    ua_house = house.heat_loss_coefficient * house.house_heat_loss_scale
    k_s = max(house.slab_heat_transfer, 1e-9)
    q_hold = ua_house * (T_BASE - T_OUT) - house.internal_gains
    state = ThermalState(room_temperature=T_BASE, slab_temperature=T_BASE + q_hold / k_s,
                         outdoor_temperature=T_OUT)
    now = START
    overrides = []
    for _ in range(240):
        room = state.room_temperature + (float(rng.normal(0.0, noise)) if noise else 0.0)
        override = si.step(
            now=now, room_temp=room, outdoor_temp=T_OUT, price=PRICE, price_horizon=HORIZON,
            learner_samples=0, max_power_kw=float(config_params.max_electrical_power), cop=cop,
            plan_power_kw=q_hold / cop, house=sysid.HousePlant.of_params(config_params),
        )
        overrides.append(None if override is None else round(float(override), 12))
        q = q_hold if override is None else float(override) * cop
        state = plant.simulate_step(state, electrical_power=0.0, outdoor_temp=T_OUT,
                                    dt_hours=cadence_h, external_heat_kw=q)
        now = now + timedelta(hours=cadence_h)
        if not si.active:
            break
    return {"armed": True, "result": si.result, "slab_fit_used": si._slab_fit_used,
            "samples": len(si.samples), "overrides": overrides}


def summary(out):
    r = out["result"]
    if r is None:
        return "result=None"
    f = lambda v: "None" if v is None else (f"{v:.12g}" if isinstance(v, float) else str(v))
    return (f"completed={r.completed} reason={r.reason!r} ua={f(r.heat_loss_kw_per_c)} "
            f"conf={f(r.confidence)} hw={f(getattr(r, 'ua_profile_halfwidth', None))}")


# tests/features.py:_drift_drive (#1308's harness shape), the one-state fit path on a first-order plant.
D_UA, D_C, D_G, D_TOUT, D_BASE, D_COP = 0.20, 10.0, 0.30, 2.0, 20.5, 3.0
D_NOW = datetime(2026, 4, 10, 23, 0)


def run_first_order(seed, cadence_min=30, sigma_c=0.02, drift_c_per_h=0.0, ua=D_UA, cap=D_C, gains=D_G):
    from datetime import timezone
    now0 = D_NOW.replace(tzinfo=timezone.utc)
    rng = np.random.default_rng(seed)
    sid = SystemIdentification(SysIdConfig(enabled=True, settle_hours=1.0, step_hours=2.0, relax_hours=2.0,
                                           max_excursion_c=0.8, gains_prior_kw=D_G, thermal_mass_prior=D_C))
    if not sid.arm(now=now0, plant=None):
        return {"armed": False, "result": sid.result, "overrides": []}
    cad = timedelta(minutes=cadence_min)
    hours = cadence_min / 60.0
    k = ua / cap
    temp_true = measured = D_BASE
    now = now0
    overrides = []
    while now < now0 + timedelta(hours=6) and sid.active:
        override = sid.step(now=now, room_temp=measured, outdoor_temp=D_TOUT, price=0.2,
                            price_horizon=np.full(96, 0.4), learner_samples=0, max_power_kw=5.0,
                            cop=D_COP, plan_power_kw=0.0)
        overrides.append(None if override is None else round(float(override), 12))
        q = override * D_COP if override else 0.0
        t_ss = D_TOUT + (q + gains) / ua
        temp_true = t_ss + (temp_true - t_ss) * np.exp(-k * hours)
        measured = temp_true + drift_c_per_h * ((now + cad) - now0).total_seconds() / 3600.0
        if sigma_c:
            measured += rng.normal(0.0, sigma_c)
        now += cad
    return {"armed": True, "result": sid.result, "overrides": overrides}


class LogCapture:
    """Every sysid logger record (any level) as its formatted message."""

    def __enter__(self):
        import logging
        self.msgs = []
        self.lg = logging.getLogger(sysid.__name__)
        self.old = (self.lg.level, self.lg.propagate)
        cap = self

        class H(logging.Handler):
            def emit(self, rec):
                cap.msgs.append(rec.getMessage())
        self.h = H()
        self.lg.addHandler(self.h)
        self.lg.setLevel(1)
        self.lg.propagate = False
        return self

    def __exit__(self, *exc):
        self.lg.removeHandler(self.h)
        self.lg.setLevel(self.old[0])
        self.lg.propagate = self.old[1]


def outcome(o, logs=()):
    """Everything a run publishes: result fields, the override sequence and the sysid log lines."""
    r = o["result"]
    rk = None if r is None else tuple(sorted((k, repr(v)) for k, v in vars(r).items()))
    return (rk, tuple(o.get("overrides") or ()), tuple(logs))


def what_differs(ob, om, lb, lm):
    """Which published parts differ: result fields (with baseline -> mutant), overrides, log lines."""
    out = []
    rb, rm = ob["result"], om["result"]
    if (rb is None) != (rm is None):
        out.append("result None-ness")
    elif rb is not None:
        for k, v in vars(rb).items():
            w = getattr(rm, k, None)
            if repr(v) != repr(w):
                out.append(f"{k}: {v!r} -> {w!r}"[:200])
    if tuple(ob.get("overrides") or ()) != tuple(om.get("overrides") or ()):
        out.append("overrides")
    if tuple(lb) != tuple(lm):
        diffs = [(a, b) for a, b in zip(lb, lm) if a != b]
        out.append(f"log lines ({len(lb)} vs {len(lm)}; first differing: {diffs[0] if diffs else None!r})"[:300])
    return "; ".join(out)


def sweep():
    """The production scenario list both drivers run: (label, thunk)."""
    cases = []
    truths = ({}, {"internal_gains": 2.5}, {"internal_gains": -1.5}, {"house_heat_loss_scale": 3.0},
              {"room_thermal_mass": 0.25})
    for preset in ("heavy_old", "typical_slab", "light_new"):
        for decl in (True, False):
            for ti, truth in enumerate(truths):
                for noise, seed, cad in ((0.0, 0, 0.5), (0.02, 0, 0.5), (0.05, 1, 0.5), (0.02, 2, 0.25)):
                    def th(preset=preset, decl=decl, truth=truth, noise=noise, seed=seed, cad=cad):
                        p = params_for(preset)
                        tp = params_for(preset, **truth) if truth else None
                        return run(p, declare_plant=decl, true_params=tp, noise=noise, seed=seed, cadence_h=cad)
                    cases.append((f"{preset},decl={decl},truth={truth},noise={noise},seed={seed},cad={cad}", th))
    for seed in range(1000, 1012):
        for sig, drift, cadm in ((0.02, 0.0, 30), (0.0, 0.0, 30), (0.02, 0.10, 30), (0.05, 0.0, 15)):
            def th(seed=seed, sig=sig, drift=drift, cadm=cadm):
                return run_first_order(seed, cadence_min=cadm, sigma_c=sig, drift_c_per_h=drift)
            cases.append((f"first_order,seed={seed},sigma={sig},drift={drift},cad={cadm}min", th))
    return cases


def reach(module, name, mut, spy=None):
    """Run the sweep with the baseline (optionally spied) and with the mutant; count differing outcomes."""
    differ = []
    cases = sweep()
    for label, th in cases:
        with LogCapture() as lb:
            if spy is not None:
                with _mut.swap(module, name, spy):
                    ob = th()
            else:
                ob = th()
        with LogCapture() as lm:
            with _mut.swap(module, name, mut):
                om = th()
        if outcome(ob, lb.msgs) != outcome(om, lm.msgs):
            differ.append((label, summary(ob), summary(om) + " | " + what_differs(ob, om, lb.msgs, lm.msgs)))
    return len(cases), differ
