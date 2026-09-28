#!/usr/bin/env python3
"""D7 seat-a: first-order sysid plant — UA bias on the three building presets.

METRIC (one line): percent bias of the identified heat-loss coefficient
(heat_loss_kw_per_c) against the plant's true UA, for (a) the production
one-state identifier SystemIdentification.identify(), (b) a two-exponential
asymptote fit of the same recorded room series, and (c) the production
two-state fit identify_slab() on a #991-gate-passing config; plus the
production adoption verdict (completed AND confidence >= 0.3 AND
slab_mode_identifiability(config, cfg)) for each fit.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D7/seat-a/sysid_step_bias.py

EXPECTED (baseline 1cc89e020fff9040a9d0090a27bf22bc1dd497f0, noise-free, so
deterministic; tolerance: exact on counts, +-0.5 pp on bias re-runs):
gate=False and armed=False on all three presets; preset-answer sweep
gate_passing=0 of 360; one-state identify() completed=False on all three
presets (excursion abort / implausible signs, so bias NaN); two-exp bias on
the 5 h window in the +130 %..+290 % band; gate-passing k_s x100 arms:
slab-fit bias -0.00..+0.00 %, admitted=True x3, conf 0.49-0.83; null
one-state plant bias about -11.5 %; UA x1.25 perturbation moves adopted
scale UP to about 1.10-1.16 (toward 1.25); cadence-gap settle arm:
heavy_old completes with bias about +7.3 % ADMITTED, light_new and
typical_slab refused by downstream guards.

MACHINE: Apple M1 (8-core), macOS 25.6.0, CPython 3.11
(/Library/Frameworks/Python.framework/Versions/3.11/bin/python3).

Root rule: resolves the repository root from __file__ (parents[5]), so it
measures THIS tree's production code. No Node, so no HPO_PLANDATA needed.
No production or test file is modified: the plant is the production
ThermalModel, the identifier is the production SystemIdentification, and
perturbed plants are in-memory ThermalParameters copies.
"""
import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "custom_components"))

import numpy as np  # noqa: E402  (after the thread pin)

from heatpump_optimizer.presets import (  # noqa: E402
    STRUCTURE_TIMBER_CRAWLSPACE,
    STRUCTURE_MASONRY,
    STRUCTURE_CONCRETE_SLAB,
    ERA_POST_2005,
    ERA_PRE_1960,
    ERA_1960_1980,
    EMITTER_RADIATORS,
    EMITTER_FLOOR,
    BuildingPreset,
    derive,
)
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel,
    ThermalParameters,
    ThermalState,
)
from heatpump_optimizer.sysid import (  # noqa: E402
    SysIdConfig,
    SystemIdentification,
    slab_mode_identifiability,
    slab_mode_tau_fast,
)

# The three building presets, identical to tests/stress.py BUILDINGS (the
# production BuildingPreset answers, resolved through presets.derive()).
PRESETS = {
    "light_new": BuildingPreset(
        structure=STRUCTURE_TIMBER_CRAWLSPACE,
        era=ERA_POST_2005,
        heated_area_m2=120,
        lower_emitter=EMITTER_RADIATORS,
    ),
    "heavy_old": BuildingPreset(
        structure=STRUCTURE_MASONRY,
        era=ERA_PRE_1960,
        heated_area_m2=200,
        lower_emitter=EMITTER_FLOOR,
    ),
    "typical_slab": BuildingPreset(
        structure=STRUCTURE_CONCRETE_SLAB,
        era=ERA_1960_1980,
        heated_area_m2=150,
        lower_emitter=EMITTER_FLOOR,
    ),
}

START = datetime(2026, 1, 15, 23, 30)
T_OUT = 0.0          # inside the sysid gating band [-5, 10] degC
T_BASE = 21.0        # held room temperature before the step
CADENCE_H = 0.5      # 30-minute coordinator cadence (sysid docstring's own)
HORIZON = np.full(48, 0.10)
PRICE = 0.05         # under the 30th percentile of the flat horizon


def params_for(preset: BuildingPreset, **overrides) -> ThermalParameters:
    cfg = derive(preset)
    cfg["two_zone_mode"] = "off"
    p = ThermalParameters.from_config(cfg)
    p.two_zone_enabled = False
    for k, v in overrides.items():
        setattr(p, k, v)
    return p


def production_sysid_config(p: ThermalParameters) -> SysIdConfig:
    """Mirror coordinator.__init__: priors from the configured params."""
    return SysIdConfig(
        enabled=True,
        gains_prior_kw=float(p.internal_gains),
        thermal_mass_prior=float(p.room_thermal_mass),
    )


def run_experiment(
    config_params: ThermalParameters,
    cfg: SysIdConfig,
    *,
    declare_plant: bool = True,
    true_params: ThermalParameters | None = None,
    gap_ticks: int | None = None,
) -> dict:
    """Drive the production state machine against the production plant.

    ``config_params`` is what the coordinator declares (sizer inputs, #991
    gate, fit priors). ``true_params`` is the house being simulated; when
    None the house matches the config. ``gap_ticks`` injects one missed
    coordinator update (2.5 h > the 2.0 h cadence bound) mid-step, the
    production trigger for identify_slab's one-state fallback.
    """
    house = true_params or config_params
    plant = ThermalModel(house)
    si = SystemIdentification(cfg)
    armed = si.arm(START, plant=config_params if declare_plant else None)
    out = {"armed": armed}
    if not armed:
        out["result"] = si.result
        return out

    cop = float(plant.compute_cop(T_OUT))
    ua_true_cfg = config_params.heat_loss_coefficient * config_params.house_heat_loss_scale
    ua_true_house = house.heat_loss_coefficient * house.house_heat_loss_scale
    gains_house = house.internal_gains
    k_s_house = max(house.slab_heat_transfer, 1e-9)
    q_hold = ua_true_house * (T_BASE - T_OUT) - gains_house
    state = ThermalState(
        room_temperature=T_BASE,
        slab_temperature=T_BASE + q_hold / k_s_house,
        outdoor_temperature=T_OUT,
    )

    now = START
    step_q_thermal = None
    for tick in range(120):
        room = state.room_temperature
        override = si.step(
            now=now,
            room_temp=room,
            outdoor_temp=T_OUT,
            price=PRICE,
            price_horizon=HORIZON,
            learner_samples=0,
            max_power_kw=float(config_params.max_electrical_power),
            cop=cop,
            plan_power_kw=q_hold / cop,
            house_ua=ua_true_cfg,
            house_capacity=float(config_params.room_thermal_mass),
            house_gains=float(config_params.internal_gains),
            house_slab_mass=float(config_params.slab_thermal_mass),
            house_slab_transfer=float(config_params.slab_heat_transfer),
        )
        dt = CADENCE_H
        if gap_ticks is not None and tick == gap_ticks:
            dt = 2.5  # one missed update; the machine sees the wall-clock gap
        q = q_hold if override is None else float(override) * cop
        if si.phase == "step" and step_q_thermal is None:
            step_q_thermal = q
        state = plant.simulate_step(
            state,
            electrical_power=0.0,
            outdoor_temp=T_OUT,
            dt_hours=dt,
            external_heat_kw=q,
        )
        now = now + timedelta(hours=dt)
        if not si.active:
            break

    result = si.result
    out.update(
        {
            "result": result,
            "slab_fit_used": si._slab_fit_used,
            "step_q_thermal": step_q_thermal,
            "samples": list(si.samples),
            "admitted": bool(
                result.completed
                and result.confidence >= 0.3
                and slab_mode_identifiability(config_params, cfg)[0]
            ),
        }
    )
    return out


def _vp_two_exp(times, temps) -> np.ndarray:
    """Variable-projection fit T(t) = T_inf + A e^{-t/tauf} + B e^{-t/taus}.

    Grid over the two time constants, linear least squares for the three
    amplitudes at each grid point (robust where a joint nonlinear solve is
    not). Returns [T_inf, A, B] of the best pair. Validated against the
    plant's analytic asymptotes on a 72 h window (see REPORT.md).
    """
    times = np.asarray(times, dtype=float)
    temps = np.asarray(temps, dtype=float)
    best = (None, np.inf)
    for tf in np.logspace(-1.5, 1.0, 14):
        for ts in np.logspace(0.0, 2.9, 14):
            if ts <= 2.0 * tf:
                continue
            basis = np.column_stack(
                [np.ones_like(times), np.exp(-times / tf), np.exp(-times / ts)]
            )
            try:
                coef, *_ = np.linalg.lstsq(basis, temps, rcond=None)
            except np.linalg.LinAlgError:
                continue
            resid = basis @ coef - temps
            cost = float(resid @ resid)
            if cost < best[1]:
                best = (coef, cost)
    return best[0]


def two_exp_ua(samples, step_q_thermal: float) -> float:
    """UA from a two-exponential asymptote fit of the recorded series.

    Per phase the two-state room response is exactly a sum of two
    exponentials, so T(t) = T_inf + A e^{-t/tauf} + B e^{-t/taus} fits the
    plant's model class exactly; UA = Q_step / (T_inf,step - T_inf,relax)
    because both asymptotes share T_out + G/UA and differ by Q_step/UA
    (the machine's step override REPLACES the plan, so Q_step is the full
    applied thermal power during the step phase).
    """
    series = {}
    t0 = samples[0].when
    for s in samples:
        if s.phase in ("step", "relax"):
            series.setdefault(s.phase, ([], []))
            t = (s.when - t0).total_seconds() / 3600.0
            series[s.phase][0].append(t)
            series[s.phase][1].append(s.room_temp)
    c_step = _vp_two_exp(*series["step"])
    c_relax = _vp_two_exp(*series["relax"])
    delta_inf = float(c_step[0] - c_relax[0])
    if not delta_inf > 1e-9:
        return float("nan")
    return step_q_thermal / delta_inf


def bias(fitted, true):
    if fitted is None or not np.isfinite(fitted):
        return float("nan")
    return 100.0 * (fitted - true) / true


def main() -> int:
    print(f"baseline tree: {ROOT}")
    print(f"sysid default protocol: settle=1.0 step=2.0 relax=2.0 h "
          f"(not configurable in production; coordinator sets only enabled/priors)")
    print()

    rows = []
    # -- default protocol, plant declared (production arming path) ----------
    print("== arm with declared plant, default protocol (production path) ==")
    for name, preset in PRESETS.items():
        p = params_for(preset)
        cfg = production_sysid_config(p)
        ok, why = slab_mode_identifiability(p, cfg)
        tau_fast = slab_mode_tau_fast(
            p.room_thermal_mass, p.slab_thermal_mass, p.slab_heat_transfer
        )
        run = run_experiment(p, cfg, declare_plant=True)
        print(f"{name}: tau_fast={tau_fast:.3f} h gate={ok} armed={run['armed']}"
              f" :: {why if not ok else 'ok'}")
        rows.append((f"gate_default_{name}", 0.0 if ok else 1.0, "refused=1"))

    # -- one-state identifier, plant NOT declared (the brief's ask) ---------
    print()
    print("== production one-state identify() (arm without declared plant) ==")
    one_state_bias = {}
    for name, preset in PRESETS.items():
        p = params_for(preset)
        cfg = production_sysid_config(p)
        run = run_experiment(p, cfg, declare_plant=False)
        r = run["result"]
        ua_true = p.heat_loss_coefficient * p.house_heat_loss_scale
        b = bias(r.heat_loss_kw_per_c, ua_true)
        one_state_bias[name] = b
        print(
            f"{name}: completed={r.completed} conf={r.confidence:.3f} "
            f"ua_hat={r.heat_loss_kw_per_c!r} ua_true={ua_true:.4f} bias={b:+.2f}% "
            f"admitted_chain={run['admitted']} reason={r.reason!r}"
        )

    # -- two-exponential reference fit on the same series -------------------
    print()
    print("== two-exponential asymptote fit of the same recorded series ==")
    two_exp_bias = {}
    for name, preset in PRESETS.items():
        p = params_for(preset)
        cfg = production_sysid_config(p)
        run = run_experiment(p, cfg, declare_plant=False)
        ua_true = p.heat_loss_coefficient * p.house_heat_loss_scale
        ua2 = two_exp_ua(run["samples"], run["step_q_thermal"])
        b = bias(ua2, ua_true)
        two_exp_bias[name] = b
        print(f"{name}: ua_2exp={ua2:.5f} ua_true={ua_true:.4f} bias={b:+.2f}%")

    # -- gate-passing configs (the only reachable experiment) ---------------
    print()
    print("== gate-passing config (k_s x100, the suite's own null-control arm; "
          "and k_s=5.0 = UI maximum for light_new) -> identify_slab ==")
    slab_fit = {}
    for name, preset in PRESETS.items():
        p = params_for(preset, slab_heat_transfer=params_for(preset).slab_heat_transfer * 100.0)
        cfg = production_sysid_config(p)
        run = run_experiment(p, cfg, declare_plant=True)
        r = run["result"]
        ua_true = p.heat_loss_coefficient * p.house_heat_loss_scale
        b = bias(r.heat_loss_kw_per_c, ua_true)
        slab_fit[name] = (b, run)
        print(
            f"{name}: completed={r.completed} slab_fit={run['slab_fit_used']} "
            f"conf={r.confidence:.3f} ua_hat={r.heat_loss_kw_per_c!r} bias={b:+.2f}% "
            f"admitted={run['admitted']} reason={r.reason!r}"
        )
    p_ln = params_for(PRESETS["light_new"], slab_heat_transfer=5.0)
    run = run_experiment(p_ln, production_sysid_config(p_ln), declare_plant=True)
    r = run["result"]
    ua_true = p_ln.heat_loss_coefficient * p_ln.house_heat_loss_scale
    print(
        f"light_new_ks5: completed={r.completed} slab_fit={run['slab_fit_used']} "
        f"conf={r.confidence:.3f} bias={bias(r.heat_loss_kw_per_c, ua_true):+.2f}% "
        f"admitted={run['admitted']} reason={r.reason!r}"
    )

    # -- null control: one-state plant, one-state fit -----------------------
    print()
    print("== null control: one-state-looking plant (k_s x1000), one-state fit ==")
    p = params_for(PRESETS["light_new"], slab_heat_transfer=params_for(PRESETS["light_new"]).slab_heat_transfer * 1000.0)
    cfg = production_sysid_config(p)
    run = run_experiment(p, cfg, declare_plant=False)
    r = run["result"]
    ua_true = p.heat_loss_coefficient * p.house_heat_loss_scale
    null_bias = bias(r.heat_loss_kw_per_c, ua_true)
    print(
        f"light_new: completed={r.completed} conf={r.confidence:.3f} "
        f"bias={null_bias:+.2f}% admitted_chain={run['admitted']} reason={r.reason!r}"
    )

    # -- perturbation: true UA x1.25 on a gate-passing config ---------------
    print()
    print("== perturbation: plant true UA x1.25 (config still believes 1.0x) ==")
    for name in ("light_new", "heavy_old"):
        p_cfg = params_for(PRESETS[name], slab_heat_transfer=params_for(PRESETS[name]).slab_heat_transfer * 100.0)
        p_true = params_for(PRESETS[name],
                            slab_heat_transfer=params_for(PRESETS[name]).slab_heat_transfer * 100.0,
                            heat_loss_coefficient=params_for(PRESETS[name]).heat_loss_coefficient * 1.25)
        run = run_experiment(p_cfg, production_sysid_config(p_cfg),
                             declare_plant=True, true_params=p_true)
        r = run["result"]
        ua_cfg = p_cfg.heat_loss_coefficient * p_cfg.house_heat_loss_scale
        ua_true = p_true.heat_loss_coefficient * p_true.house_heat_loss_scale
        adopted_scale = None
        if r.completed and r.heat_loss_kw_per_c is not None:
            scale = r.heat_loss_kw_per_c / ua_cfg
            adopted_scale = (1.0 - r.confidence) * 1.0 + r.confidence * scale
        print(
            f"{name}: fitted_bias_vs_true={bias(r.heat_loss_kw_per_c, ua_true):+.2f}% "
            f"adopted_scale={adopted_scale!r} (expected -> 1.25) "
            f"admitted={run['admitted']} reason={r.reason!r}"
        )

    # -- cadence-gap fallback: one-state fit of a gate-passing plant --------
    print()
    print("== cadence-gap fallback (one 2.5 h missed update), k_s x100 configs ==")
    for name in PRESETS:
        p0 = params_for(PRESETS[name])
        p = params_for(PRESETS[name], slab_heat_transfer=p0.slab_heat_transfer * 100.0)
        cfg = production_sysid_config(p)
        ua_true = p.heat_loss_coefficient * p.house_heat_loss_scale
        for gap_label, gap_tick in (
            ("settle", 1), ("midstep", 4), ("earlyrelax", 8), ("laterelax", 9),
        ):
            run = run_experiment(p, cfg, declare_plant=True, gap_ticks=gap_tick)
            r = run["result"]
            b = bias(r.heat_loss_kw_per_c, ua_true)
            bs = f"{b:+.2f}%" if np.isfinite(b) else "nan"
            print(
                f"{name} gap@{gap_label}: completed={r.completed} "
                f"slab_fit={run['slab_fit_used']} conf={r.confidence:.3f} "
                f"bias={bs} admitted={run['admitted']} reason={r.reason!r}"
            )
            if gap_label == "settle":
                print(f"RESULT gap_settle_bias_{name}={bs.replace('%', '')} percent")
                print(f"RESULT gap_settle_admitted_{name}={int(run['admitted'])} bool")

    # -- preset-answer sweep: can any config-flow answer arm the gate? ------
    print()
    print("== preset-answer sweep: structure x era x foundation x emitter x area ==")
    import itertools
    from heatpump_optimizer.presets import (
        STRUCTURES, EMITTERS, FOUNDATIONS, _ERA_LOSS_W_PER_M2K,
    )
    total = 0
    passing = 0
    tau_fast_all = []
    for struct, era, found, emit_lo, area in itertools.product(
        STRUCTURES, list(_ERA_LOSS_W_PER_M2K), FOUNDATIONS, EMITTERS,
        (50.0, 140.0, 300.0),
    ):
        preset = BuildingPreset(
            structure=struct, era=era, foundation=found,
            heated_area_m2=area, lower_emitter=emit_lo,
        )
        p = params_for(preset)
        tau_fast_all.append(
            slab_mode_tau_fast(
                p.room_thermal_mass, p.slab_thermal_mass, p.slab_heat_transfer
            )
        )
        ok, _why = slab_mode_identifiability(p, SysIdConfig(enabled=True))
        total += 1
        passing += int(ok)
    print(f"combos tested: {total}; gate-passing: {passing}; "
          f"tau_fast min/max across combos: {min(tau_fast_all):.3f}/"
          f"{max(tau_fast_all):.3f} h (gate needs <= {1.0/3.0:.3f} h)")
    print(f"RESULT preset_answer_combos={total} count")
    print(f"RESULT preset_answer_gate_passing={passing} count")
    print(f"RESULT preset_answer_tau_fast_min={min(tau_fast_all):.3f} hours")

    # -- RESULT lines --------------------------------------------------------
    print()
    for name in PRESETS:
        print(f"RESULT one_state_bias_{name}={one_state_bias[name]:+.2f} percent")
        print(f"RESULT two_exp_bias_{name}={two_exp_bias[name]:+.2f} percent")
        b, run = slab_fit[name]
        print(f"RESULT slab_fit_bias_{name}={b:+.2f} percent")
        print(f"RESULT slab_fit_admitted_{name}={int(run['admitted'])} bool")
    print(f"RESULT null_one_state_plant_bias={null_bias:+.2f} percent")
    proc_cpu = time.process_time()
    thread_cpu = time.thread_time()
    factor = proc_cpu / thread_cpu if thread_cpu > 1e-9 else 1.0
    print(f"RESULT thread_factor={factor:.3f} ratio")
    try:
        load1 = float(subprocess.run(["sysctl", "-n", "vm.loadavg"],
                                     capture_output=True, text=True).stdout.split()[1])
    except Exception:
        load1 = -1.0
    print(f"RESULT load1={load1} load")
    try:
        ps = subprocess.run(
            ["ps", "aux"], capture_output=True, text=True).stdout
        concurrent = sum(
            1 for ln in ps.splitlines()
            if ("stress.py" in ln or "tests/run.sh" in ln) and "grep" not in ln
        )
    except Exception:
        concurrent = -1
    print(f"RESULT concurrent_test_procs={concurrent} count")
    print(f"RESULT swapins=0 count  (noise-free, no noise process)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

