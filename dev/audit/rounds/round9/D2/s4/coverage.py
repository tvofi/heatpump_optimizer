"""D2-s4 (round 9, D2.M5): calibration of the sysid adoption interval on the fits it admits.

Metric: over seeded draws of the production experiment (SystemIdentification.arm/step
-> _finish -> identify_slab -> sysid.adoption_decision) on a two-state preset plant
with white room-sensor noise, the count of ADMITTED fits whose true UA lies outside
their own 95 % interval, i.e. |log(UA_fit/UA_true)| > slab_ua_adoption_halfwidth(
ua_profile_halfwidth, ua_prior_halfwidth) -- the quantity the gate bounds and the
blend weight reads. A calibrated 95 % interval misses ~5 % of the time.
Count key: the production fit's delivered heat_loss_kw_per_c and its published
half-widths, against the simulated plant's true UA (never an input attribute).

Command (from the export root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/s4/coverage.py [--seeds 40] [--perturb none|anchor|sigma0|bar5]

Perturbations (in memory):
  anchor -- sysid._simulate_slab_path's first_room_c replaced by the plant's true
            first room temperature (the rollout no longer anchors on a noisy reading):
            the miss count must go DOWN.
  sigma0 -- sensor noise 0 in every cell (null control): misses must go TO ZERO.
  bar5   -- sysid.UA_ADOPTION_HALFWIDTH_BAR = log(1.05): admitted count goes down.
Grid: presets {typical_slab, heavy_old} x sigma {0.01, 0.02, 0.05} degC x cadence
{0.25, 0.5} h = 12 cells; leave-one-out printed.
Expected (baseline): see REPORT.md, counts exact for the fixed seed set.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box B6 (4 CPU cloud container).
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
import gate_bias as G  # noqa: E402  (same directory: the production drive)
from heatpump_optimizer import sysid as S  # noqa: E402

warnings.simplefilter("ignore", RuntimeWarning)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=40)
    ap.add_argument("--perturb", default="none")
    a = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()
    anchor = {"v": None}
    if a.perturb == "anchor":
        orig = S._simulate_slab_path

        def patched(ua, rc, g, sm, st, first, *rest, **kw):
            return orig(ua, rc, g, sm, st, anchor["v"], *rest, **kw)
        S._simulate_slab_path = patched
    if a.perturb == "bar5":
        S.UA_ADOPTION_HALFWIDTH_BAR = float(np.log(1.05))
    tot_adm = tot_miss = tot_done = tot_done_miss = 0
    all_adm_bias = []
    adopted_err = []
    cell_rates = []
    for pname in ("typical_slab", "heavy_old"):
        p = G.plant(pname)
        base_u = float(p.heat_loss_coefficient)
        for sig in (0.01, 0.02, 0.05):
            for dt in (0.25, 0.5):
                level = 0.0 if a.perturb == "sigma0" else sig
                adm = miss = done = done_miss = 0
                for k in range(a.seeds if level else 1):
                    anchor["v"] = 21.0  # the drive starts every plant held at 21.0 degC
                    sid, res, ua = G.drive(p, G.SEED0 + k, "white", level, dt)
                    if not res.completed:
                        continue
                    hw = S.slab_ua_adoption_halfwidth(
                        res.ua_profile_halfwidth, res.ua_prior_halfwidth)
                    err = abs(float(np.log(res.heat_loss_kw_per_c / ua)))
                    if hw is not None and np.isfinite(hw):
                        done += 1
                        done_miss += err > hw
                    dec = S.adoption_decision(res, p, sid.config)
                    if dec.admit:
                        adm += 1
                        miss += err > hw
                        all_adm_bias.append(res.heat_loss_kw_per_c / ua - 1.0)
                        # the blended house scale's error, learner standing at the truth
                        adopted_err.append(dec.weight * (dec.scale - ua / base_u))
                tag = f"{pname}_s{sig}_dt{dt}"
                print(f"RESULT {tag}_admitted={adm} count")
                print(f"RESULT {tag}_admitted_missed={miss} count")
                print(f"RESULT {tag}_finite_interval_fits={done} count")
                print(f"RESULT {tag}_finite_interval_missed={done_miss} count", flush=True)
                tot_adm += adm; tot_miss += miss; tot_done += done; tot_done_miss += done_miss
                cell_rates.append((adm, miss))
    print(f"RESULT admitted_total={tot_adm} count")
    print(f"RESULT admitted_missed_total={tot_miss} count")
    print(f"RESULT admitted_miss_rate={tot_miss / max(tot_adm, 1):.3f} ratio")
    print(f"RESULT finite_interval_miss_rate={tot_done_miss / max(tot_done, 1):.3f} ratio")
    if all_adm_bias:
        print(f"RESULT admitted_bias_mean={np.mean(all_adm_bias)*100:+.2f} %")
        print(f"RESULT admitted_bias_positive={sum(b > 0 for b in all_adm_bias)} count")
        print(f"RESULT admitted_bias_max={max(all_adm_bias)*100:+.2f} %")
        print(f"RESULT adopted_scale_err_mean={np.mean(adopted_err)*100:+.2f} %")
        print(f"RESULT adopted_scale_err_max={max(adopted_err)*100:+.2f} %")
    # leave-one-out over cells with admissions: drop the cell with the most misses
    rated = [(m / ad, ad, m) for ad, m in cell_rates if ad]
    if len(rated) >= 2:
        worst = max(rated, key=lambda r: r[2])
        rest_ad = tot_adm - worst[1]; rest_m = tot_miss - worst[2]
        print(f"RESULT cells_with_admissions={len(rated)} count")
        print(f"RESULT cell_miss_rate_min={min(r[0] for r in rated):.3f} ratio")
        print(f"RESULT cell_miss_rate_max={max(r[0] for r in rated):.3f} ratio")
        print(f"RESULT miss_rate_drop_worst_cell={rest_m / max(rest_ad, 1):.3f} ratio")
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
