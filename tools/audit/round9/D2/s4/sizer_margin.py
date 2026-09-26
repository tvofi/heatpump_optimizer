"""D2-s4 (round 9, D2.M5): the sysid step is sized to the abort bound with no noise margin.

Metric: over seeded draws of the production experiment (SystemIdentification.arm/step,
the step sized by SystemIdentification._size_step_power at the plant's own
max_electrical_power), the count of experiments ABORTED with "room temperature drifted
beyond the allowed excursion" -- i.e. the estimator never reaches a fit -- per cell of
preset x white sensor sigma x cadence. Count key: the production result's reason
string after the run (SystemIdentification.result.reason), not an input attribute.

Command (from the export root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/s4/sizer_margin.py [--seeds 16] [--perturb none|margin]

Perturbation (in memory): margin -- SystemIdentification._size_step_power's returned
electrical step multiplied by 0.85 (a 15 % sizing margin under the same abort bound):
the abort count must go DOWN (to ~0 at sigma <= 0.02).
Null control: sigma = 0 at 0.25 h cadence (the sizer's own integration step): 0 aborts.
Grid: presets {light_new, typical_slab, heavy_old} x sigma {0, 0.01, 0.02, 0.05} x cadence {0.25, 0.5} h.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box B6 (4 CPU cloud container).
Expected: see REPORT.md (counts exact for the fixed seed set).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
import argparse
import warnings

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import gate_bias as G  # noqa: E402
from heatpump_optimizer import sysid as S  # noqa: E402

warnings.simplefilter("ignore", RuntimeWarning)
ABORT = "room temperature drifted beyond the allowed excursion"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=16)
    ap.add_argument("--perturb", default="none")
    a = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()
    if a.perturb == "margin":
        orig = S.SystemIdentification._size_step_power

        def sized(self, *args, **kw):
            q = orig(self, *args, **kw)
            return None if q is None else 0.85 * q
        S.SystemIdentification._size_step_power = sized
    tot = tot_abort = 0
    rates = []
    for pname in ("light_new", "typical_slab", "heavy_old"):
        p = G.plant(pname)
        for sig in (0.0, 0.01, 0.02, 0.05):
            for dt in (0.25, 0.5):
                n = aborts = 0
                peaks = []
                for k in range(a.seeds if sig else 1):
                    sid, res, ua = G.drive(p, G.SEED0 + k, "white", sig, dt,
                                           max_kw=float(p.max_electrical_power))
                    n += 1
                    aborts += res.reason == ABORT
                tag = f"{pname}_s{sig}_dt{dt}"
                print(f"RESULT {tag}_runs={n} count")
                print(f"RESULT {tag}_aborted={aborts} count", flush=True)
                tot += n; tot_abort += aborts
                if sig:
                    rates.append(aborts / n)
    print(f"RESULT runs_total={tot} count")
    print(f"RESULT aborted_total={tot_abort} count")
    r = sorted(rates)
    print(f"RESULT noisy_cells={len(r)} count")
    print(f"RESULT noisy_cell_abort_rate_min={r[0]:.3f} ratio")
    print(f"RESULT noisy_cell_abort_rate_max={r[-1]:.3f} ratio")
    print(f"RESULT noisy_cell_abort_rate_mean={np.mean(r):.3f} ratio")
    print(f"RESULT noisy_cell_abort_rate_mean_drop_max={np.mean(r[:-1]):.3f} ratio")
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
