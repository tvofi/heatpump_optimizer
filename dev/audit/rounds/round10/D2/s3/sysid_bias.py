"""D2-s3 M5: sysid.SystemIdentification.identify UA bias vs the confidence it reports.

Metric: relative UA error (identified/true - 1) and reported confidence, per
noise arm (clean, white 0.05 C, quantised 0.1 C, drift 0.05 C/h), over 20
seeds x 3 plants; RESULT lines give the median |err|, worst |err| among fits
with confidence >= 0.3 (the adoption gate), and the count of such admitted
fits whose |err| > 20 %. Samples are an exact first-order plant
(C dT/dt = Q + G - UA (T - Tout)) at 5-min spacing through settle/step/relax.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D2/s3/sysid_bias.py
Non-finding harness; the clean arm is the null control. Expected: clean and
drift median err 0.0000, admitted_over_20pct=0 in every arm.
Baseline 17f1c55fad1b, macOS arm64 audit box B6.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, math
from datetime import datetime, timedelta, timezone
import numpy as np
sys.path.insert(0, ".")
from custom_components.heatpump_optimizer import sysid as S  # noqa: E402

PLANTS = [(0.15, 8.0), (0.25, 12.0), (0.10, 15.0)]  # UA kW/C, C kWh/C
DT = 5 / 60.0


def synth(ua, c, arm, rng, gains=0.3):
    t0 = datetime(2026, 1, 10, 23, tzinfo=timezone.utc)
    tout = 0.0
    T = 21.0
    q_hold = ua * (T - tout) - gains
    phases = [(S.PHASE_SETTLING, 1.0, q_hold), (S.PHASE_STEP, 2.0, q_hold + 1.5),
              (S.PHASE_RELAX, 2.0, 0.0)]
    out, k, tt = [], 0, 0.0
    for ph, hrs, q in phases:
        for _ in range(int(round(hrs / DT))):
            meas = T
            if arm == "white":
                meas += rng.normal(0, 0.05)
            elif arm == "quant":
                meas = round(T * 10) / 10
            elif arm == "drift":
                meas += 0.05 * tt
            out.append(S.SysIdSample(t0 + timedelta(minutes=5 * k), meas, tout, q, ph))
            # exact exponential step
            a = ua / c
            Teq = tout + (q + gains) / ua
            T = Teq + (T - Teq) * math.exp(-a * DT)
            k += 1
            tt += DT
    return out


def main():
    c0, th0 = time.process_time(), time.thread_time()
    for arm in ("clean", "white", "quant", "drift"):
        errs, admitted, bad = [], [], 0
        for ua, c in PLANTS:
            for seed in range(20):
                si = S.SystemIdentification(S.SysIdConfig())
                si.samples = synth(ua, c, arm, np.random.default_rng(seed))
                r = si.identify()
                if not r.completed or r.heat_loss_kw_per_c is None:
                    continue
                e = r.heat_loss_kw_per_c / ua - 1
                errs.append(abs(e))
                if r.confidence >= 0.3:
                    admitted.append(abs(e))
                    bad += abs(e) > 0.20
        med = float(np.median(errs)) if errs else float("nan")
        wa = max(admitted) if admitted else float("nan")
        print(f"RESULT {arm}_completed={len(errs)} of 60")
        print(f"RESULT {arm}_median_abs_ua_err={med:.4f} ratio")
        print(f"RESULT {arm}_admitted={len(admitted)} worst_admitted_abs_ua_err={wa:.4f} admitted_over_20pct={bad}")
    tf = (time.process_time() - c0) / max(time.thread_time() - th0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
