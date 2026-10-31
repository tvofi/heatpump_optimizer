"""D2-v1 (verifier) harness for D2-s1-02: is the DHW COP law physically consistent on its own?

Metric (one line): max over (tank T in 40..70 C, outdoor in -15..12 C) of the DHW law's implied
second-law (Carnot) efficiency at T relative to the same law at the 35 C reference,
  eta_rel(T,o) = [compute_cop_dhw(o,T) / carnot(T,o)] / [compute_cop_dhw(o,35) / carnot(35,o)],
carnot(T,o) = (T+273.15)/(T-o).  A physical lift law keeps eta_rel <= ~1 (exergetic efficiency
does not improve with lift); >1 means the law under-prices lift.  The same number is printed for
the buffer (Carnot) law as the comparison, and the count of DISTINCT cells in the finder's grid
(the ratio does not depend on cop_nominal) is printed as a grid-artefact check.
Instrumented: ThermalModel.compute_cop_dhw, ThermalModel.marginal_cop('buffer').
Perturbation (--perturb): compute_cop_dhw's penalty replaced by flow_lift_factor (the finder's
edit), class-attribute swap restored in finally; eta_rel_dhw must fall to the buffer's value.
Null: T = 35 C -> eta_rel = 1 exactly for both laws.
Uses outdoor clamped to cop_reference_temp (7 C) for the Carnot denominators, as flow_lift_factor
does, so the comparison is not an artefact of that cap.

Command: PYTHONPATH=tests/hastub python3 tools/audit/round8/D2/v1_cop_laws.py [--perturb]
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; 4-vCPU shared cloud container.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
sys.path.insert(0, ".")
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import thermal_model as tm  # noqa: E402


def carnot(T, o):
    o = min(o, 7.0)
    return (T + 273.15) / max(T - o, 1.0)


def _pert(self, outdoor_temp, dhw_temp, humidity=None):
    base = self._cop_law(outdoor_temp, humidity, None)
    return max(base * self.flow_lift_factor(outdoor_temp, dhw_temp), 1.0)


def main():
    t0 = time.process_time(); th0 = time.thread_time()
    orig = tm.ThermalModel.compute_cop_dhw
    if "--perturb" in sys.argv:
        tm.ThermalModel.compute_cop_dhw = _pert
    try:
        m = tm.ThermalModel(tm.ThermalParameters(cop_flow_carnot=True, two_zone_enabled=True,
                                                 mixing_valve_mode="manual"))
        Ts = np.arange(40.0, 70.1, 2.5)
        outs = np.arange(-15.0, 12.1, 1.0)
        eta_d, eta_b, floored = [], [], 0
        for o in outs:
            d35 = m.compute_cop_dhw(o, 35.0) / carnot(35.0, o)
            b35 = m.marginal_cop(o, "buffer", 35.0) / carnot(35.0, o)
            for T in Ts:
                cd = m.compute_cop_dhw(o, T)
                cb = m.marginal_cop(o, "buffer", T)
                if cd <= 1.0 + 1e-12 or cb <= 1.0 + 1e-12:
                    floored += 1
                    continue
                eta_d.append((cd / carnot(T, o)) / d35)
                eta_b.append((cb / carnot(T, o)) / b35)
        null = max(abs(m.compute_cop_dhw(o, 35.0) / m.marginal_cop(o, "buffer", 35.0) - 1) for o in outs)
        # finder-grid distinctness
        vals = {}
        for nom in (2.8, 3.5, 4.5):
            mm = tm.ThermalModel(tm.ThermalParameters(cop_flow_carnot=True, cop_nominal=nom,
                                                      two_zone_enabled=True, mixing_valve_mode="manual"))
            for T in (40., 45., 50., 55., 60., 65., 70.):
                for o in (-15., -5., 0., 7., 12.):
                    vals[(nom, T, o)] = round(mm.marginal_cop(o, "dhw", T) / mm.marginal_cop(o, "buffer", T), 9)
        distinct = len({(k[1], k[2], v) for k, v in vals.items()})
        # the reachable default: DHW setpoint 55, max 60
        at55 = max(m.compute_cop_dhw(o, 55.0) / m.marginal_cop(o, "buffer", 55.0) for o in outs)
        at60 = max(m.compute_cop_dhw(o, 60.0) / m.marginal_cop(o, "buffer", 60.0) for o in outs)
    finally:
        tm.ThermalModel.compute_cop_dhw = orig
    ed, eb = np.array(eta_d), np.array(eta_b)
    print(f"RESULT eta_rel_dhw_max={ed.max():.4f} ratio")
    print(f"RESULT eta_rel_buffer_max={eb.max():.4f} ratio")
    print(f"RESULT eta_rel_dhw_min={ed.min():.4f} ratio")
    print(f"RESULT cells_scored={ed.size} floored_skipped={floored}")
    print(f"RESULT cells_eta_dhw_gt_1_05={int((ed > 1.05).sum())}")
    print(f"RESULT finder_grid_distinct_cells={distinct} of {len(vals)}")
    print(f"RESULT dhw_over_buffer_max_at55={at55:.4f} ratio")
    print(f"RESULT dhw_over_buffer_max_at60={at60:.4f} ratio")
    print(f"RESULT null_at_35C={null:.6f} abs_dev")
    pc = time.process_time() - t0; tc = time.thread_time() - th0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
    except Exception:
        sw = 'n/a'
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
