"""D2-s1 harness: two COP laws for one lift -- DHW tank vs buffer tank at the same water temperature.

Metric (one line): max over a (tank temp x outdoor) grid of
  ThermalModel.marginal_cop(o, "dhw", T) / ThermalModel.marginal_cop(o, "buffer", T)
with cop_flow_carnot=True (the only configuration where the buffer is priced by its lift).
Physics: the same compressor lifting water to the same temperature at the same outdoor air has
one COP; a DHW coil needs a condensing temperature at or above the tank's, so the ratio should
be <= 1. Also reported: the DHW law's boost below the 35 degC reference
(compute_cop_dhw(o, T<35) / compute_cop(o)), which the space law refuses by design
("a below-ref tank must not earn a COP boost it never gets"), and the outdoor-dependence of the
DHW lift penalty (ratio of warm/cold COP for each law at 55 degC).
Count key: the COP the production methods return (no constants re-derived).

Command:  PYTHONPATH=tests/hastub python3 tools/audit/round8/D2/s1_cop_laws.py [--perturb]
  --perturb : the one-line production edit, applied by class-attribute swap and restored in
              finally -- compute_cop_dhw's `dhw_penalty = max(0.5, 1.0 - 0.008 * (dhw_temp - 35.0))`
              replaced by `dhw_penalty = self.flow_lift_factor(outdoor_temp, dhw_temp)`.
              Expected: ratio_max -> 1.0000, boost_below_ref -> 1.0000.
Expected at baseline: ratio_max 1.43 (+-0.01), boost_below_ref 1.12 (+-0.01).
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container (shared).
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


def _perturbed_cop_dhw(self, outdoor_temp, dhw_temp, humidity=None):
    base_cop = self._cop_law(outdoor_temp, humidity, None)
    dhw_penalty = self.flow_lift_factor(outdoor_temp, dhw_temp)  # the one-line edit
    return max(base_cop * dhw_penalty, 1.0)


def main():
    t0 = time.process_time(); th0 = time.thread_time()
    orig = tm.ThermalModel.compute_cop_dhw
    if "--perturb" in sys.argv:
        tm.ThermalModel.compute_cop_dhw = _perturbed_cop_dhw
    try:
        temps = (40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0)
        outs = (-15.0, -5.0, 0.0, 7.0, 12.0)
        cells = {}
        for nominal in (2.8, 3.5, 4.5):
            m = tm.ThermalModel(tm.ThermalParameters(cop_flow_carnot=True, cop_nominal=nominal,
                                                     two_zone_enabled=True, mixing_valve_mode="manual"))
            for T in temps:
                for o in outs:
                    r = m.marginal_cop(o, "dhw", T) / m.marginal_cop(o, "buffer", T)
                    cells[(nominal, T, o)] = r
        m = tm.ThermalModel(tm.ThermalParameters(cop_flow_carnot=True, two_zone_enabled=True,
                                                 mixing_valve_mode="manual"))
        boost = max(m.compute_cop_dhw(o, T) / m.compute_cop(o) for o in outs for T in (20.0, 25.0, 30.0))
        dhw_span = m.compute_cop_dhw(7.0, 55.0) / m.compute_cop_dhw(-5.0, 55.0)
        buf_span = m.marginal_cop(7.0, "buffer", 55.0) / m.marginal_cop(-5.0, "buffer", 55.0)
    finally:
        tm.ThermalModel.compute_cop_dhw = orig
    v = np.array(list(cells.values()))
    keys = list(cells.keys())
    worst = int(np.argmax(v))
    print(f"worst cell (cop_nominal, tank_C, outdoor_C) = {keys[worst]}")
    print(f"RESULT ratio_max={v.max():.4f} ratio")
    print(f"RESULT ratio_min={v.min():.4f} ratio")
    print(f"RESULT ratio_drop_most_favourable={np.delete(v, worst).max():.4f} ratio")
    print(f"RESULT cells={v.size}")
    print(f"RESULT cells_ratio_gt_1_01={int((v > 1.01).sum())}")
    print(f"RESULT boost_below_ref={boost:.4f} ratio")
    print(f"RESULT warm_over_cold_dhw_law_55C={dhw_span:.4f} ratio")
    print(f"RESULT warm_over_cold_buffer_law_55C={buf_span:.4f} ratio")
    # null control: at the reference flow (35 degC) both laws must agree exactly
    nc = max(abs(m.marginal_cop(o, "dhw", 35.0) / m.marginal_cop(o, "buffer", 35.0) - 1.0) for o in outs)
    print(f"RESULT null_at_reference_flow={nc:.6f} abs_dev")
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
