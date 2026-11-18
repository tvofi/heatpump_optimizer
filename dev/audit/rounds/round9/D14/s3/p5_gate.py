#!/usr/bin/env python3
"""P5 detector (D14.M3): a sysid adoption gate keyed on a quantity other than the bias it gates.

Metric (one line): over a synthetic-bias sweep driving the production experiment
(sysid:SystemIdentification arm/step/_finish on a declared plant, the plant rolled on the
production thermal_model:ThermalModel) and ruled by sysid:adoption_decision, RESULT
p5_admitted_over_bar counts ADMITTED fits whose true UA error |ln(UA_hat/UA_true)| exceeds
the gate's own bar UA_ADOPTION_HALFWIDTH_BAR (ln 1.10, i.e. +-10 %); p5_monotone_breaks counts
(preset, source) series whose admission is not non-increasing in the injected bias magnitude
while the realised |UA error| grows.

Count key: the UA the production fit returns (result.heat_loss_kw_per_c) against the plant's
true UA (heat_loss_coefficient * house_heat_loss_scale of the rolled plant), and the admit bit
adoption_decision returns -- a fix must change what the gate admits or what the fit returns.

Bias sources (the plant differs from what the experiment is told; each at graded magnitudes):
  gains  -- the plant's free heat exceeds the declared internal gains by dG kW
  drift  -- the room sensor ramps at d C/h while the house does not
  ks     -- the declared slab_heat_transfer is m x the plant's
  cap    -- the declared room_thermal_mass is m x the plant's
  gains_neg -- the plant's free heat is BELOW the declared gains (round-7 D7-01's cell: true 0 kW)
Magnitude 0 of every source is the null control (no injected bias).

Command (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D14/s3/p5_gate.py
    [--seams]               # static: list every site writing a learned thermal parameter
    [--perturb bar_tight]   # in-memory: UA_ADOPTION_HALFWIDTH_BAR -> ln(1.10)/10 (gate 10x tighter)
    [--perturb prior_true]  # in-memory: SysIdConfig.gains_prior_kw := the plant's true free heat
Expected: counts printed by the run (exact; deterministic, no noise); bar_tight -> down,
prior_true -> down on the gains series.
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box B8 (4 cores, 15 GB).
Instrumented symbols: sysid:adoption_decision, sysid:SystemIdentification.identify_slab (reached
through step()/_finish on a declared plant).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import copy
import json
import sys
import time
from datetime import UTC, datetime, timedelta
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402

from profiles import house  # noqa: E402
from stress import BUILDINGS  # noqa: E402
from heatpump_optimizer import presets  # noqa: E402
from heatpump_optimizer import sysid as S  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402

NOW = datetime(2026, 1, 15, 23, 0, tzinfo=UTC)
COP = 3.0
MAX_KW = 3.5
SOURCES = {
    "gains": (0.0, 0.1, 0.2, 0.4, 0.8),
    "gains_neg": (0.0, -0.1, -0.2, -0.3),
    "drift": (0.0, 0.05, 0.1, 0.2, 0.3),
    "ks": (1.0, 1.25, 1.5, 2.0, 3.0),
    "cap": (1.0, 1.25, 1.5, 2.0, 3.0),
}
STATE = {"prior_true": False}


def preset(name):
    cfg = house(two_zone=False, dhw=False)
    d = presets.derive(BUILDINGS[name])
    d.pop("heating_response_hours", None)
    cfg.update(d)
    p = ThermalParameters.from_config(cfg)
    p.two_zone_enabled = False
    return p


def drive(true_p, source, mag):
    decl = copy.deepcopy(true_p)
    plant = copy.deepcopy(true_p)
    drift = 0.0
    if source in ("gains", "gains_neg"):
        plant.internal_gains = float(true_p.internal_gains) + mag
    elif source == "drift":
        drift = mag
    elif source == "ks":
        decl.slab_heat_transfer = float(true_p.slab_heat_transfer) * mag
    elif source == "cap":
        decl.room_thermal_mass = float(true_p.room_thermal_mass) * mag
    model = ThermalModel(plant)
    ua_true = float(plant.heat_loss_coefficient * plant.house_heat_loss_scale)
    g_true = float(plant.internal_gains)
    # Production builds the config with gains_prior_kw = the DECLARED internal gains
    # (coordinator.py, the SysIdConfig(...) construction); the perturbation hands it the truth.
    prior = g_true if STATE["prior_true"] else float(decl.internal_gains)
    cfg = S.SysIdConfig(enabled=True, min_days_between_runs=0.0, gains_prior_kw=prior)
    sid = S.SystemIdentification(cfg)
    if not sid.arm(NOW, plant=decl):
        return {"armed": False, "reason": sid.result.reason}
    outdoor = 0.0
    ks = max(float(plant.slab_heat_transfer), 1e-9)
    hold = max(ua_true * (21.0 - outdoor) - g_true, 0.0)
    state = ThermalState(room_temperature=21.0, slab_temperature=21.0 + hold / ks,
                         outdoor_temperature=outdoor)
    prices = np.full(48, 1.0)
    when = NOW
    dt_h = 0.25
    hours = 0.0
    for _ in range(int(8.0 / dt_h)):
        reading = state.room_temperature + drift * hours
        override = sid.step(
            now=when, room_temp=reading, outdoor_temp=outdoor, price=0.1, price_horizon=prices,
            learner_samples=0, max_power_kw=MAX_KW, cop=COP, plan_power_kw=hold / COP,
            house_ua=float(decl.heat_loss_coefficient * decl.house_heat_loss_scale),
            house_capacity=float(decl.room_thermal_mass), house_gains=float(decl.internal_gains),
            house_slab_mass=float(decl.slab_thermal_mass),
            house_slab_transfer=float(decl.slab_heat_transfer),
        )
        if not sid.active:
            break
        elec = hold / COP if override is None else float(override)
        state = model.simulate_step(state, electrical_power=0.0, outdoor_temp=outdoor,
                                    dt_hours=dt_h, external_heat_kw=elec * COP)
        hours += dt_h
        when += timedelta(hours=dt_h)
    res = sid.result
    out = {"armed": True, "completed": bool(res.completed), "reason": res.reason,
           "slab_fit": bool(sid._slab_fit_used), "ua_true": ua_true}
    if res.completed and res.heat_loss_kw_per_c is not None:
        if hasattr(S, "adoption_decision"):
            dec = S.adoption_decision(res, decl, sid.config)
            admit, why, weight = bool(dec.admit), dec.reason, float(dec.weight)
            hw = S.slab_ua_adoption_halfwidth(res.ua_profile_halfwidth, res.ua_prior_halfwidth)
        else:
            # Pre-#1525 trees only (the --ref re-find): the gate then lived in
            # coordinator._adopt_system_identification as the profile half-width bar
            # followed by slab_mode_identifiability -- transcribed, not re-derived.
            hw = res.ua_profile_halfwidth
            ok = hw is not None and not hw > S.UA_ADOPTION_HALFWIDTH_BAR
            ok = ok and S.slab_mode_identifiability(decl, sid.config)[0]
            admit, why = bool(ok), ("adopted" if ok else "refused (pre-#1525 gate)")
            weight = (1.0 - hw / S.UA_ADOPTION_HALFWIDTH_BAR) if ok else 0.0
        out.update(ua_hat=float(res.heat_loss_kw_per_c),
                   err_log=float(np.log(res.heat_loss_kw_per_c / ua_true)),
                   admit=admit, why=why, hw=hw, weight=weight,
                   # the blend _adopt_system_identification applies: weight * error, in log space
                   blend_err_log=float(weight * np.log(res.heat_loss_kw_per_c / ua_true)) if admit else 0.0)
    else:
        out.update(admit=False)
    return out


LEARNED = ("house_heat_loss_scale", "cop_scale", "buffer_cooling_rate", "lower_floor_loss_ratio",
           "solar_aperture_scale", "internal_gains_profile", "defrost_derate")


def adoption_seams():
    """Every production site that writes a LEARNED thermal parameter (the P5 seam rule).

    A seam is a call of an ``_apply_<learned>`` setter or a direct assignment to
    ``<x>._thermal_params.<learned>``, keyed by its enclosing function. Reads the
    imported package's own source (module.__file__), so a --ref worktree run lists its tree.
    """
    import ast
    from pathlib import Path
    import heatpump_optimizer as pkg
    seams = []
    for path in sorted(Path(pkg.__file__).parent.glob("*.py")):
        tree = ast.parse(path.read_text())
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for n in ast.walk(fn):
                hit = None
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and \
                        n.func.attr in tuple(f"_apply_{k}" for k in LEARNED):
                    hit = n.func.attr[len("_apply_"):]
                elif isinstance(n, ast.Assign):
                    for t in n.targets:
                        if isinstance(t, ast.Attribute) and t.attr in LEARNED and \
                                isinstance(t.value, ast.Attribute) and t.value.attr == "_thermal_params":
                            hit = t.attr
                if hit and fn.name != f"_apply_{hit}":
                    seams.append((path.stem, fn.name, hit, n.lineno))
    return sorted(set(seams))


def main():
    a = sys.argv[1:]
    if "--seams" in a:
        seams = adoption_seams()
        for m, f, k, ln in seams:
            print(f"SEAM {m}:{f} writes {k} (line {ln})")
        print(f"RESULT p5_adoption_seams={len(seams)} count")
        print(f"RESULT p5_adoption_seam_functions={len({(m, f) for m, f, _, _ in seams})} count")
        return
    pert = a[a.index("--perturb") + 1] if "--perturb" in a else None
    patches = []
    if pert == "bar_tight":
        patches.append(mock.patch.object(S, "UA_ADOPTION_HALFWIDTH_BAR", float(np.log(1.10)) / 10))
    STATE["prior_true"] = pert == "prior_true"
    t0 = time.process_time(); tt0 = time.thread_time(); w0 = time.time()
    bar = float(np.log(1.10))
    rows = []
    for p in patches:
        p.start()
    try:
        for name in BUILDINGS:
            tp = preset(name)
            for src, mags in SOURCES.items():
                for m in mags:
                    r = drive(tp, src, m)
                    r.update(preset=name, source=src, mag=m)
                    rows.append(r)
                    e = r.get("err_log")
                    print(f"CELL {name:12s} {src:5s} mag={m:<5} armed={int(r['armed'])} done={int(r.get('completed', 0))} "
                          f"slab={int(r.get('slab_fit', 0))} admit={int(r['admit'])} "
                          f"err={'%+.2f%%' % (100*np.expm1(e)) if e is not None else 'na':>9} "
                          f"hw={'%.4f' % r['hw'] if r.get('hw') is not None else 'na'} "
                          f"why={(r.get('why') or r.get('reason') or '')[:70]}", flush=True)
    finally:
        for p in patches:
            p.stop()
    over = [r for r in rows if r["admit"] and abs(r["err_log"]) > bar]
    breaks = 0
    series = 0
    for name in BUILDINGS:
        for src in SOURCES:
            s = [r for r in rows if r["preset"] == name and r["source"] == src]
            series += 1
            # admission must not rise while the realised error rises
            for lo, hi in zip(s, s[1:]):
                if hi["admit"] and not lo["admit"] and abs(hi.get("err_log", 0)) > abs(lo.get("err_log", 0) or 0):
                    breaks += 1
                    break
    null = [r for r in rows if r["mag"] in (0.0, 1.0)]
    print(f"RESULT p5_cells={len(rows)} count")
    print(f"RESULT p5_admitted={sum(r['admit'] for r in rows)} count")
    print(f"RESULT p5_admitted_over_bar={len(over)} count")
    print(f"RESULT p5_admitted_over_bar_null={sum(1 for r in null if r['admit'] and abs(r['err_log']) > bar)} count")
    print(f"RESULT p5_worst_blended_shift_pct={100*max((abs(np.expm1(r['blend_err_log'])) for r in rows if r['admit']), default=0):.3f} %")
    print(f"RESULT p5_worst_admitted_err_pct={100*max((abs(np.expm1(r['err_log'])) for r in rows if r['admit']), default=0):.3f} %")
    for src in SOURCES:
        sub = [r for r in over if r["source"] == src]
        print(f"RESULT p5_admitted_over_bar_{src}={len(sub)} count")
    if over:
        worst = max(over, key=lambda r: abs(r["err_log"]))
        print(f"RESULT p5_admitted_over_bar_drop_worst={len(over) - 1} count")
    print(f"RESULT p5_monotone_breaks={breaks}/{series} count")
    out = os.environ.get("P5_JSON")
    if out:
        with open(out, "w") as fh:
            json.dump(rows, fh, indent=1, default=str)
    pc = time.process_time() - t0; tc = time.thread_time() - tt0
    print(f"RESULT wall_s={time.time()-w0:.1f} s provisional")
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
    except Exception:
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
