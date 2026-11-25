#!/usr/bin/env python3
"""Generate probe_<key>.py for box D3-g35 from one spec table (scratch tool, not a harness)."""
import json, sys
from pathlib import Path

OUT = Path("/root/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes")
EXP = json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv) > 1 else {}

L2141 = "        if solution.shape[0] >= 3:"
L2146 = "            if drift_c_per_h is not None:"
L2154 = "            if not (-0.5 <= gains_kw <= 2.0):"
L2162 = "            gains_kw = float(np.clip(gains_kw, 0.0, 2.0))"
L2187 = "        if drift_c_per_h is not None and a.shape[1] >= 4:"
L2208 = "        if drift_c_per_h is not None and a.shape[1] >= 4 and excursion > 1e-9:"
L2223 = "        if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0):"
L2237 = "            and abs(drift_c_per_h) < self.config.sensor_drift_prior_c_per_h"
L2244 = "                if abs(den) > 1e-6:"
L2246 = "                    if ua_ss > 0.0 and abs(ua_ss - ua) / ua > 0.10:"

QS = "[3.0 + 0.05 * i for i in range(40)]"

# key: (line_no, old, new, kind, extra-cases code, what the extra case is)
SPECS = {
 "31bb6bebd6b45f0e": (2141, L2141, "        if solution.shape[0] > 3:", "CMP_BOUND",
   "", "solution.shape[0] is 4 (four-column solve) or 2 (two-column fallback), never 3"),
 "501a5e7cda702183": (2146, L2146, "            if False:", "GUARD_OFF",
   "", "a sensor drifting +0.01 C/h: the intercept keeps the drift term, so internal_gains_kw moves"),
 "20cde1046cbd5681": (2154, L2154, "            if not (-0.5 <= gains_kw < 2.0):", "CMP_BOUND",
   f"HUNT = (L, 'gains_kw', lambda x, s: c.plant_samples(m, gains=x, q=s), 1.9, 2.1, 2.0, {QS})",
   "a plant whose fitted gains_kw lands on exactly 2.0 (hunted over true gains and step power)"),
 "6cfdb101dc87a6ea": (2154, L2154, "            if not (-0.5 < gains_kw <= 2.0):", "CMP_BOUND",
   f"HUNT = (L, 'gains_kw', lambda x, s: c.plant_samples(m, gains=x, q=s), -0.6, -0.4, -0.5, {QS})",
   "a plant whose fitted gains_kw lands on exactly -0.5 (hunted over true gains and step power)"),
 "d203230963349f60": (2162, L2162, "            gains_kw = float((gains_kw))", "CLAMP_DROP",
   "", "a plant with true gains -0.3 kW (inside the accepted [-0.5, 2] band, below the clip)"),
 "078e78462859ff6b": (2187, L2187, "        if drift_c_per_h is not None or a.shape[1] >= 4:", "BOOLOP",
   "", "drift_c_per_h is None exactly on the two-column fallback, where a.shape[1] == 2"),
 "5654f855fcc27724": (2187, L2187, "        if drift_c_per_h is not None and a.shape[1] > 4:", "CMP_BOUND",
   "", "a sensor drifting +0.01 C/h: the excursion keeps the drift ramp, so confidence moves"),
 "c303df62a0b7b9bc": (2187, L2187, "        if False:", "GUARD_OFF",
   "", "a sensor drifting +0.01 C/h: the excursion keeps the drift ramp, so confidence moves"),
 "ed00e6c2abf2aa66": (2208, L2208, "        if drift_c_per_h is not None and a.shape[1] >= 4 and excursion >= 1e-9:", "CMP_BOUND",
   "HUNT = (L, 'excursion', lambda x, s: c.plant_samples(m, q=x, drift=s), 0.0, 1e-8, 1e-9, [0.0, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3])",
   "a window whose drift-corrected excursion is exactly 1e-9 C (hunted over step power and drift)"),
 "4593852cf3862b3c": (2223, L2223, "        if not (0.1 < tau <= 200.0) or not (0.01 <= ua <= 5.0):", "CMP_BOUND",
   f"HUNT = (L, 'tau', lambda x, s: c.plant_samples(m, ua=x, cap=0.3, gains=0.0, cadence_min=1.0, q=s), 3.0, 3.5, 0.1, {QS})",
   "a fast plant whose fitted tau lands on exactly 0.1 h (hunted over UA and step power)"),
 "64f3ef1feaaf7bc9": (2223, L2223, "        if not (0.1 <= tau <= 200.0) or not (0.01 < ua <= 5.0):", "CMP_BOUND",
   f"HUNT = (L, 'ua', lambda x, s: c.plant_samples(m, ua=x, cap=1.0, gains=0.0, q=s), 0.009, 0.011, 0.01, {QS})",
   "a plant whose fitted UA lands on exactly 0.01 kW/C (hunted over UA and step power)"),
 "784e362919d88a92": (2223, L2223, "        if not (0.1 <= tau <= 200.0) or not (0.01 <= ua < 5.0):", "CMP_BOUND",
   f"HUNT = (L, 'ua', lambda x, s: c.plant_samples(m, ua=x, cap=10.0, gains=0.0, q=10.0 * s), 4.9, 5.1, 5.0, {QS})",
   "a plant whose fitted UA lands on exactly 5.0 kW/C (hunted over UA and step power)"),
 "d661d68f54982097": (2223, L2223, "        if not (0.1 <= tau < 200.0) or not (0.01 <= ua <= 5.0):", "CMP_BOUND",
   f"HUNT = (L, 'tau', lambda x, s: c.plant_samples(m, ua=x, cap=3.0, gains=0.0, q=s), 0.0145, 0.0155, 200.0, {QS})",
   "a slow plant whose fitted tau lands on exactly 200 h (hunted over UA and step power)"),
 "a5b06d898bf0ba03": (2237, L2237, "            and abs(drift_c_per_h) <= self.config.sensor_drift_prior_c_per_h", "CMP_BOUND",
   "", "sensor_drift_prior_c_per_h set to exactly the fitted |drift| (fixed point), unsettled settle"),
 "c51115b0104a8bf5": (2244, L2244, "                if abs(den) >= 1e-6:", "CMP_BOUND",
   "", "the last settling sample reads exactly 1e-6 C above outdoor (den == 1e-6)"),
 "4da9d281d4714565": (2246, L2246, "                    if ua_ss > 0.0 and abs(ua_ss - ua) / ua >= 0.10:", "CMP_BOUND",
   "HUNT = (L, 'abs(ua_ss - ua) / ua', lambda x, s: c.plant_samples(m, start_steady=False, t0=x, q=s[0], gains=s[1]), 1.30, 1.40, 0.10, [(3.0 + 0.1 * i, 0.3 + 0.002 * j) for i in range(16) for j in range(10)])",
   "an unsettled settle whose steady-state UA disagrees with the fit by exactly 10 % (hunted)"),
}

SPECIAL = {
 "501a5e7cda702183": "EXTRA = [('KEY drift+0.01', c.plant_samples(m, drift=0.01), None)]\nMEASURE_KEY = 'internal_gains_kw'",
 "d203230963349f60": "EXTRA = [('KEY gains-0.3', c.plant_samples(m, gains=-0.3), None)]\nMEASURE_KEY = 'internal_gains_kw'",
 "5654f855fcc27724": "EXTRA = [('KEY drift+0.01', c.plant_samples(m, drift=0.01), None)]\nMEASURE_KEY = 'confidence'",
 "c303df62a0b7b9bc": "EXTRA = [('KEY drift+0.01', c.plant_samples(m, drift=0.01), None)]\nMEASURE_KEY = 'confidence'",
 "c51115b0104a8bf5": "EXTRA = [('KEY settle_dT_1e-6', c.plant_samples(m, last_settle_room=1e-6), None)]\nMEASURE_KEY = 'completed'",
 "a5b06d898bf0ba03": "EXTRA = fixed_point_case(m)\nMEASURE_KEY = 'completed'",
 "d661d68f54982097": ("# found by a random search (seed 1, 42394 evaluations) over cap, step power and UA\n"
   "s = c.plant_samples(m, ua=0.011370575082848609, cap=2.273167336967812, gains=0.0, q=4.770168220478481)\n"
   "print(f'RESULT key_tapped_tau={c.tapped(c.load_tap(L, \"tau\"), s)[0]!r}')\n"
   "EXTRA = [('KEY tau==200', s, None)]\nMEASURE_KEY = 'completed'"),
 "ed00e6c2abf2aa66": ("tap = c.load_tap(L, 'excursion')\n"
   "for q in (1e-3, 1e-4, 1e-5, 3e-6, 1e-6, 3e-7, 1e-7, 3e-8, 1e-8, 1e-9, 1e-10, 0.0):\n"
   "    v, r = c.tapped(tap, c.plant_samples(m, q=q))\n"
   "    print(f'RESULT sweep_q[{q}].excursion={v!r} completed={int(r.completed)} reason={r.reason!r}')"),
}

TEMPLATE = '''#!/usr/bin/env python3
"""D3-s1 (box D3-g35), audit round 11: step-4 probe for full-gate survivor {key}.

Metric (one line): differing_cases = how many inputs of this probe's case set give a different
published SystemIdentification.identify() result (completed, reason, UA, C, gains, drift,
confidence) under the mutant than at the baseline; the KEY case's {mkey} is printed per arm.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_{key}.py
Expected: {expected}
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (sysid.py read with git show, never the worktree file).
Machine: box D3-g35 cloud container, 4 cores, Intel Xeon @ 2.10GHz; counts exact, run time provisional.
Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.identify
(sysid.py:{line}, {kind}), driven through synthetic exact first-order step tests (sysid_probe_common.py).
Perturbation: the one-line mutant {key}, applied in memory to a copy of the module source:
  old: {old_s}
  new: {new_s}
Key case: {what}.
Count key: the value identify() returns (the production seam's output), not an input attribute.
A hunted case (HUNT) searches float inputs until the instrumentation arm (`_TAP.append` before
the mutated line, not the mutant) reads the boundary exactly; no hit means the case is absent.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sysid_probe_common as c  # noqa: E402

OLD = {old!r}
NEW = {new!r}
L = {tapline!r}
FIELDS = ("completed", "reason", "heat_loss_kw_per_c", "thermal_mass_kwh_per_c",
          "internal_gains_kw", "sensor_drift_c_per_h", "confidence")


def fixed_point_case(m):
    """sensor_drift_prior_c_per_h iterated to the fitted |drift| until they are equal exactly."""
    tap = c.load_tap("        if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0):", "drift_c_per_h")
    s = c.plant_samples(m, drift=0.01, start_steady=False, t0=1.3)
    p = 0.02
    for it in range(80):
        d, _ = c.tapped(tap, s, tap.SysIdConfig(enabled=True, sensor_drift_prior_c_per_h=p))
        if d is None:
            break
        if abs(d) == p:
            print(f"RESULT fixed_point_iterations={{it}}")
            print(f"RESULT prior_equal_to_fitted_drift={{p!r}}")
            return [("KEY prior==|drift|", s, {{"sensor_drift_prior_c_per_h": p}})]
        p = abs(d)
    print("RESULT fixed_point_iterations=none")
    return []


def main() -> int:
    m = c.load()
    EXTRA = []
    HUNT = None
    MEASURE_KEY = {mkey!r}
{special}
    if HUNT is not None:
        line, expr, make, lo, hi, target, seconds = HUNT
        x, s, tried = c.multi_hunt(line, expr, make, lo, hi, target, seconds)
        print(f"RESULT hunt_evaluations={{tried}}")
        print(f"RESULT hunt_hit={{int(x is not None)}}  # input x={{x!r}} secondary={{s!r}}")
        if x is not None:
            EXTRA = [("KEY hunted", make(x, s), None)]
    cases = EXTRA + c.std_cases(m)
    base, mut = c.load(), c.load(OLD, NEW)
    for label, samples, cfg in EXTRA:
        rb = c.run(base, samples, base.SysIdConfig(enabled=True, **(cfg or {{}})))
        rm = c.run(mut, samples, mut.SysIdConfig(enabled=True, **(cfg or {{}})))
        print(f"RESULT key_{{MEASURE_KEY}}.baseline={{getattr(rb, MEASURE_KEY)!r}}  # {{c.fmt(rb)}}")
        print(f"RESULT key_{{MEASURE_KEY}}.mutant={{getattr(rm, MEASURE_KEY)!r}}  # {{c.fmt(rm)}}")
    c.drive(OLD, NEW, c.outcome, cases)
    c.footer()
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

for key, (line, old, new, kind, hunt, what) in SPECS.items():
    sp = SPECIAL.get(key, "")
    mkey = "completed"
    body = []
    if hunt:
        body.append(hunt)
    if sp:
        body.append(sp)
    special = "\n".join("    " + ln for blk in body for ln in blk.split("\n"))
    if "MEASURE_KEY" in sp:
        mkey = sp.split("MEASURE_KEY = ")[1].strip().strip("'")
    expected = EXP.get(key, "(filled from the recorded run)")
    tapline = old if key != "a5b06d898bf0ba03" else L2223
    (OUT / f"probe_{key}.py").write_text(TEMPLATE.format(
        key=key, mkey=mkey, expected=expected, line=line, kind=kind, old=old, new=new,
        old_s=old.strip(), new_s=new.strip(), what=what, tapline=tapline, special=special))
print("written", len(SPECS))
