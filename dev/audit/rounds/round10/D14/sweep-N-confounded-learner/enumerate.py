"""D14 sweep, class N-confounded-learner: enumerator, controls, perturbation, probes.

Class mechanism: an online estimator absorbs the error of an unmodelled or
mis-modelled covariate into the parameter it learns (seed finding D2-s3-71).

Seam rule (syntactic, whole package): a function that folds a model RESIDUAL
(an identifier containing "residual", or a call to learner_newton_step) into
persisted learned state (an augmented/attribute assignment on self/m/... or a
returned refit scale). Every function so listed is a seam; each is then
dispositioned below as instance / guarded / not-applicable.

Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-N-confounded-learner/enumerate.py
Prints SEAM lines, CONTROL lines (positive, null, perturbation) and PROBE lines.
A PROBE line "FAIL" means the probe detects the confound on current code.
"""
import ast, os, sys, math, pathlib
from datetime import datetime, timedelta, timezone
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
PKG = ROOT / "custom_components" / "heatpump_optimizer"


def seams_in_source(src: str, fname: str):
    out = []
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        names = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
        calls = {getattr(c.func, "attr", getattr(c.func, "id", None))
                 for c in ast.walk(node) if isinstance(c, ast.Call)}
        uses_resid = any("residual" in n for n in names) or "learner_newton_step" in calls
        if not uses_resid or node.name == "learner_newton_step":
            continue
        writes_state = False
        for a in ast.walk(node):
            tgts = []
            if isinstance(a, ast.AugAssign):
                tgts = [a.target]
            elif isinstance(a, ast.Assign):
                tgts = a.targets
            for t in tgts:
                if isinstance(t, (ast.Attribute, ast.Subscript)):
                    writes_state = True
        calls_apply = any(c and (c.startswith("_apply_") or c.startswith("_fold_")
                                 or c == "_clipped_refit_scale") for c in calls)
        if writes_state or calls_apply:
            out.append((fname, node.name))
    return out


def enumerate_pkg():
    seams = []
    for p in sorted(PKG.glob("*.py")):
        seams += seams_in_source(p.read_text(), p.name)
    return seams


DISPOSITION = {
    ("coordinator.py", "_async_learn_house_heat_loss"): ("instance", "probe_house_ua", False),
    ("coordinator.py", "_async_learn_lower_floor_loss"): ("instance", "probe_lower_floor", True),
    ("accuracy.py", "heat_loss_refit"): ("instance", "probe_refit", True),
    ("coordinator.py", "_fold_internal_gains"): ("instance", "probe_internal_gains", True),
}
NON_INSTANCE = {
    ("coordinator.py", "_fold_solar_aperture"): ("guarded", "demeaned EWMA covariance regression on modelled Q_solar, sunny intervals only; probe_aperture passes (1.003 at +10 % UA error)"),
    ("diagnosis.py", "attribute"): ("not applicable", "one-shot diagnostic attribution, writes no persisted learned parameter"),
    ("drift.py", "update"): ("not applicable", "CUSUM change detector on the residual; a statistic, not a parameter estimate"),
    ("flow_lift.py", "observe"): ("not applicable", "sole learned term over the curve; it is meant to absorb all curve error at current conditions, no second parameter is biased"),
    ("price_model.py", "observe_day"): ("not applicable", "descriptive price-shape estimator; no physical covariate in its model"),
    ("sysid.py", "identify"): ("guarded", "night-gated experiment (module docstring 'must be gated') plus the intercept column G that absorbs residual solar/gains"),
    ("sysid.py", "identify_slab"): ("guarded", "same night gate and slab intercept prior SLAB_INTERCEPT_PRIOR_SD_KW"),
    ("sysid.py", "_lm_solve"): ("not applicable", "solver helper; the regressor set is chosen by its callers"),
    ("sysid.py", "_slab_ua_profile_halfwidth"): ("not applicable", "uncertainty half-width, not an estimate"),
}

# --- probes: each simulates a plant whose ONLY model error is in the other
# covariate and asserts the learner under test stays at truth. FAIL = confound.

C, DT_H = 10.0, 1.0  # kWh/C, h
from custom_components.heatpump_optimizer.thermal_model import learner_newton_step  # noqa


def _day(n_days=20):
    """Hourly (hour, irradiance W/m2, deltaT K) with cold clear-sky days."""
    rows = []
    for d in range(n_days):
        for h in range(24):
            irr = max(0.0, 600 * math.sin(math.pi * (h - 6) / 12)) if 6 <= h <= 18 else 0.0
            dT = 22.0 - (-2.0 + 6.0 * math.sin(math.pi * (h - 9) / 12))  # warmer afternoon
            rows.append((h, irr, dT))
    return rows


def _ua_walk(aperture_err, sunny_gate=None):
    q_per_irr = 0.004  # kW per W/m2 modelled solar gain
    scale = 1.0
    for h, irr, dT in _day():
        if sunny_gate is not None and irr > sunny_gate:
            continue
        # unmodelled solar surplus, minus what the replay with the current
        # scale already removes (closed loop, as the coordinator replays)
        resid = (aperture_err * q_per_irr * irr + (scale - 1.0) * 0.15 * dT) * DT_H / C
        st = learner_newton_step(scale, 0.15, C, resid, dT, DT_H, trust_region=0.3,
                                 alpha=0.02, max_step_fraction=0.02)
        if st:
            scale = st[1]
    return scale


def probe_house_ua():
    s = _ua_walk(0.3)
    return abs(s - 1.0) < 0.02, f"ua_scale={s:.3f} at aperture_err=+0.30 (truth 1.000)"


def probe_lower_floor():
    # same Newton step about the lower zone; method has no irradiance gate
    src = (PKG / "coordinator.py").read_text()
    fn = src[src.index("async def _async_learn_lower_floor_loss"):]
    fn = fn[:fn.index("\n    async def ", 10)]
    gated = "solar_radiation" in fn
    s = _ua_walk(0.3, sunny_gate=50.0 if gated else None)
    return abs(s - 1.0) < 0.02, f"lower_ratio={s:.3f} gated={gated}"


def probe_refit():
    from custom_components.heatpump_optimizer.accuracy import AccuracySample, heat_loss_refit
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rows = []
    for i, (h, irr, dT) in enumerate(_day()):
        resid = 0.3 * 0.004 * irr * DT_H / C
        rows.append(AccuracySample(when=t0 + timedelta(hours=i), predicted_temp=21.0,
                                   actual_temp=21.0 + resid, outdoor_temp=21.0 - dT))
    r = heat_loss_refit(rows, current_scale=1.0, base_u=0.15, capacity=C, dt_hours=DT_H,
                        min_delta=3.0, max_residual=1.0, settle=timedelta(0), since=None)
    s = r["scale"]
    return s is not None and abs(s - 1.0) < 0.02, f"refit_scale={s}"


class _Ns:  # minimal coordinator stand-in for the _fold_* methods
    pass


def _fold_self():
    from types import SimpleNamespace as NS
    from custom_components.heatpump_optimizer import coordinator as co
    s = _Ns()
    s._ctx = NS(_config=NS(solar_aperture_learning_enabled=True,
                           internal_gains_learning_enabled=True),
                _thermal_params=NS(two_zone_enabled=False, room_thermal_mass=C,
                                   upper_floor_thermal_mass=C, internal_gains=0.3))
    s._solar_aperture = {"scale": 1.0, "n": 0.0, "mx": 0.0, "my": 0.0, "cov": 0.0, "var": 0.0}
    s._internal_gains_profile = None
    s._thermal_model = NS(compute_solar_gain=lambda irr: 0.004 * irr)
    return co, s


def probe_aperture():
    co, s = _fold_self()
    from types import SimpleNamespace as NS
    for h, irr, dT in _day():
        a = s._solar_aperture["scale"]
        # UA 10 % under-modelled, solar exact; replay already applies scale a
        resid = (-0.10 * 0.15 * dT - (a - 1.0) * 0.004 * irr) * DT_H / C
        co.HeatPumpOptimizerCoordinator._fold_solar_aperture(s, NS(solar_radiation=irr), resid, DT_H)
    a = s._solar_aperture["scale"]
    return abs(a - 1.0) < 0.02, f"aperture_scale={a:.3f} at ua_err=+10% (truth 1.000)"


def probe_internal_gains():
    co, s = _fold_self()
    from types import SimpleNamespace as NS
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i, (h, irr, dT) in enumerate(_day()):
        g = (s._internal_gains_profile or [0.3] * 24)[h]
        resid = (-0.10 * 0.15 * dT - (g - 0.3)) * DT_H / C
        co.HeatPumpOptimizerCoordinator._fold_internal_gains(
            s, t0 + timedelta(hours=i), NS(solar_radiation=irr), resid, DT_H)
    prof = [g for g in s._internal_gains_profile]
    dev = max(abs(g - 0.3) for g in prof) / 0.3
    return dev < 0.05, f"gains_max_rel_dev={dev:.3f} at ua_err=+10% (truth 0)"


NULL_FIXTURE = '''
class L:
    def learn(self, y, x):
        self.mean = 0.9 * self.mean + 0.1 * y
'''
PERTURB_LINE = "        residual = y - x\n        self.scale += 0.01 * residual\n"


def main():
    seams = enumerate_pkg()
    for s in seams:
        d = DISPOSITION.get(s) or NON_INSTANCE.get(s) or ("unclassified",)
        print("SEAM", s[0], s[1], d[0])
    found = set(seams)
    pos = ("coordinator.py", "_async_learn_house_heat_loss") in found
    print("CONTROL positive", "PASS" if pos else "FAIL", "(re-finds D2-s3-71 site)")
    n0 = len(seams_in_source(NULL_FIXTURE, "fixture"))
    print("CONTROL null", "PASS" if n0 == 0 else "FAIL", f"count={n0}")
    n1 = len(seams_in_source(NULL_FIXTURE + PERTURB_LINE, "fixture"))
    print("CONTROL perturbation", "PASS" if n1 == 1 else "FAIL", f"count {n0}->{n1}")
    # null control for the probes: zero covariate error must leave every learner at truth
    print("PROBE-NULL house_ua", "PASS" if abs(_ua_walk(0.0) - 1.0) < 1e-9 else "FAIL")
    for key, (disp, probe, _b) in DISPOSITION.items():
        ok, msg = globals()[probe]()
        print("PROBE", key[1], "PASS" if ok else "FAIL", msg)
    ok, msg = probe_aperture()
    print("PROBE-GUARD _fold_solar_aperture", "PASS" if ok else "FAIL", msg)
    print("PROBE-BARRIER house_ua sunny-gated", "PASS" if abs(_ua_walk(0.3, sunny_gate=50.0) - 1.0) < 1e-9 else "FAIL")
    unc = [s for s in seams if s not in DISPOSITION and s not in NON_INSTANCE]
    print("UNCLASSIFIED", len(unc))


if __name__ == "__main__":
    main()
