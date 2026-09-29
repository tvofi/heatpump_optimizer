"""D2-v1 (verifier) harness for D2-s1-01: consequence of the DHW planner's humidity fallback.

Metric (one line): published (physics) DHW trajectory shortfall = max over the horizon of
(published DHW temp with ambient==forecast) - (published DHW temp with ambient=current), K,
i.e. how much colder the tank physically runs when the planner prices DHW COP at the current
humidity instead of the forecast; plus the minimum published tank temperature against
params.dhw_min_temp and the DHW electricity bought, per cell.

Differs from the finder's metric (planner re-sim vs published of the SAME run): this compares
two published trajectories, so it measures the delivered consequence, not the internal gap.
Grid: learned derate value {0.60, 0.85} x forecast {flat 90 %, diurnal 60..95 %} x weather
{winter_mild, shoulder}; plus the reverse arm (current humid 90, forecast dry 55).
Instrumented: ThermalModel.compute_cop_dhw / extend_dhw_temps via optimizer.optimize.
Perturbation: --thread-humidity sets params.ambient_humidity to the forecast mean before
optimize (the finder's matched arm); the baseline arm is ambient 55 %.
Null: derate None -> 0 K.

Command: OMP_NUM_THREADS=1 ... PYTHONPATH=tests/hastub python3 tools/audit/round8/D2/v1_dhw_humidity.py
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; 4-vCPU shared cloud container.
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
from heatpump_optimizer.defrost import DefrostDerate  # noqa: E402


def derate(value):
    if value is None:
        return None
    d = DefrostDerate()
    for t in (-2.0, 1.0, 3.0):
        for _ in range(20):
            d.observe(t, 90.0, value)
    return d


def run(weather, hum, ambient, dvalue):
    b = golden.make(dhw=True, weather_profile=weather, price_profile="winter_typical",
                    param_overrides=dict(defrost_derate=derate(dvalue), ambient_humidity=ambient))
    opt = b["optimizer"]
    n = len(b["prices"])
    outdoor = np.clip(np.asarray(b["outdoor"], dtype=float), -1.0, 4.5)
    res = opt.optimize(b["state"], b["prices"], outdoor, b["wind"], b["rain"], b["solar"],
                       golden.START, humidity=np.asarray(hum[:n], dtype=float))
    pub = np.asarray(res.dhw_temp_trajectory, dtype=float)
    e = float(np.sum(res.dhw_power_schedule) * 0.25)
    return pub, e, float(opt.model.params.dhw_min_temp)


def main():
    t0 = time.process_time(); th0 = time.thread_time()
    n = 96
    k = np.arange(n)
    forecasts = {
        "flat90": np.full(n, 90.0),
        "diurnal60_95": 77.5 + 17.5 * np.cos(2 * np.pi * (k * 0.25 - 3.0) / 24.0),
    }
    rows = []
    for dv in (0.60, 0.85):
        for fname, hum in forecasts.items():
            for w in ("winter_mild", "shoulder"):
                pub_bad, e_bad, dmin = run(w, hum, 55.0, dv)
                pub_ok, e_ok, _ = run(w, hum, float(np.mean(hum)), dv)
                short = float(np.max(pub_ok - pub_bad))
                rows.append((dv, fname, w, short, pub_bad.min(), pub_ok.min(), dmin, e_bad, e_ok))
                print(f"cell derate={dv} fc={fname} w={w}: shortfall={short:.3f} K "
                      f"min_pub bad={pub_bad.min():.2f} ok={pub_ok.min():.2f} dhw_min={dmin:.1f} "
                      f"e bad={e_bad:.3f} ok={e_ok:.3f} kWh")
    # reverse arm: current humid, forecast dry -> planner overbuys?
    pub_r, e_r, _ = run("winter_mild", np.full(n, 55.0), 90.0, 0.60)
    pub_r0, e_r0, _ = run("winter_mild", np.full(n, 55.0), 55.0, 0.60)
    # null: no derate
    pn, en, _ = run("winter_mild", forecasts["flat90"], 55.0, None)
    pn0, en0, _ = run("winter_mild", forecasts["flat90"], 90.0, None)
    s = np.array([r[3] for r in rows])
    s60 = np.array([r[3] for r in rows if r[0] == 0.60])
    s85 = np.array([r[3] for r in rows if r[0] == 0.85])
    print(f"RESULT shortfall_max={s.max():.4f} K")
    print(f"RESULT shortfall_max_derate060={s60.max():.4f} K")
    print(f"RESULT shortfall_max_derate085={s85.max():.4f} K")
    print(f"RESULT shortfall_drop_most_favourable={np.sort(s)[-2]:.4f} K")
    below = sum(1 for r in rows if r[4] < r[6] - 1e-6)
    print(f"RESULT cells_published_below_dhw_min={below} of {len(rows)}")
    print(f"RESULT min_published_bad={min(r[4] for r in rows):.3f} C")
    print(f"RESULT reverse_arm_extra_kwh={e_r - e_r0:.4f} kWh")
    print(f"RESULT reverse_arm_max_abs_traj_dev={float(np.max(np.abs(pub_r - pub_r0))):.4f} K")
    print(f"RESULT null_no_derate={float(np.max(np.abs(pn - pn0))):.4f} K")
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
