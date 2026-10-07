"""D2-s1 harness: the DHW planner prices COP without the step's forecast humidity.

Metric (one line): max over the horizon of |planner DHW temp - published DHW temp| (K),
where "planner" is ThermalModel.simulate_dhw_only (the model every DHW planning stage in
optimizer.py runs) re-run on the optimizer's own dhw_power_schedule, and "published" is
OptimizationResult.dhw_temp_trajectory (simulate_trajectory_with_dhw, which passes humidity).
Count key: the DHW temperature each seam delivers, not any input attribute.
Secondary: n_cop_calls_fallback = _cop_law calls inside optimize() that received humidity=None
while a finite forecast series was passed (hooked by class-attribute swap, restored in finally).

Command:  PYTHONPATH=tests/hastub python3 tools/audit/round8/D2/s1_dhw_humidity.py [--ambient-matches]
  --ambient-matches : perturbation arm -- params.ambient_humidity set equal to the forecast
                      humidity; the gap must go to zero (planner and physics then agree).
Expected: gap_max ~5.0 K (+-0.3) in the humid cells, exactly 0 in both null controls.
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container (shared).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
sys.path.insert(0, ".")
sys.path.insert(0, "tests")
import numpy as np  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer import thermal_model as tm  # noqa: E402  (golden.py puts custom_components on sys.path)
from heatpump_optimizer.defrost import DefrostDerate  # noqa: E402

AMBIENT = 55.0  # the current humidity the coordinator writes into params.ambient_humidity


def learned_derate(value=0.6):
    """A frost-band derate learned only in the humid buckets (the fallback estimator)."""
    d = DefrostDerate()
    for t in (-2.0, 1.0, 3.0):
        for _ in range(20):
            d.observe(t, 90.0, value)
    return d


def run_cell(weather, forecast_h, ambient, derate=True):
    b = golden.make(dhw=True, weather_profile=weather, price_profile="winter_typical",
                    param_overrides=dict(defrost_derate=learned_derate() if derate else None,
                                         ambient_humidity=ambient))
    opt = b["optimizer"]
    n = len(b["prices"])
    outdoor = np.clip(np.asarray(b["outdoor"], dtype=float), -1.0, 4.5)  # the frost band
    hum = np.full(n, float(forecast_h))
    calls = {"none": 0, "all": 0}
    orig = tm.ThermalModel._cop_law

    def spy(self, outdoor_temp, humidity, flow_temp):
        calls["all"] += 1
        if humidity is None or not np.isfinite(humidity):
            calls["none"] += 1
        return orig(self, outdoor_temp, humidity, flow_temp)

    tm.ThermalModel._cop_law = spy
    try:
        res = opt.optimize(b["state"], b["prices"], outdoor, b["wind"], b["rain"], b["solar"],
                           golden.START, humidity=hum)
    finally:
        tm.ThermalModel._cop_law = orig
    m = opt.model
    sched = np.asarray(res.dhw_power_schedule, dtype=float)
    hours = (golden.START.hour + golden.START.minute / 60.0 + np.arange(n) * 0.25) % 24.0
    plan = m.simulate_dhw_only(float(b["state"].dhw_temperature), sched, outdoor,
                               m.dhw_draw_rates(hours), 0.25)
    pub = np.asarray(res.dhw_temp_trajectory, dtype=float)
    gap = float(np.max(np.abs(plan - pub)))
    # thermal energy the planner believes is in the tank but physics does not deliver
    short_kwh = float(np.max(plan - pub)) * m.params.dhw_tank_thermal_mass
    return gap, short_kwh, float(sched.sum() * 0.25), calls["none"], calls["all"]


def main():
    matched = "--ambient-matches" in sys.argv
    t0 = time.process_time(); th0 = time.thread_time()
    cells = [(w, h) for w in ("winter_mild", "shoulder", "winter_cold") for h in (85.0, 95.0)]
    gaps = []
    for w, h in cells:
        amb = h if matched else AMBIENT
        gap, short, kwh, nnone, nall = run_cell(w, h, amb)
        gaps.append(gap)
        print(f"cell weather={w} forecast_h={h} ambient={amb}: gap={gap:.4f} K "
              f"short={short:.3f} kWh_th dhw_e={kwh:.3f} kWh cop_calls_fallback={nnone}/{nall}")
    # null controls: forecast equals ambient; and no learned derate at all
    nc1 = run_cell("winter_mild", AMBIENT, AMBIENT)[0]
    nc2 = run_cell("winter_mild", 95.0, AMBIENT, derate=False)[0]
    g = np.array(gaps)
    best = int(np.argmax(g))
    print(f"RESULT gap_max={g.max():.4f} K")
    print(f"RESULT gap_min_cell={g.min():.4f} K")
    print(f"RESULT gap_drop_most_favourable={np.delete(g, best).max():.4f} K")
    print(f"RESULT cells={len(g)}")
    print(f"RESULT null_forecast_equals_ambient={nc1:.4f} K")
    print(f"RESULT null_no_derate={nc2:.4f} K")
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
