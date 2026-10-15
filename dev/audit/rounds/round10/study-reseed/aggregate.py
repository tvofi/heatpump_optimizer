"""Reseed study (R10): leave-one-out over the reseed_rolling.py plants.

Reads the RESULT lines reseed_rolling.py printed, one .out per plant, and
prints per metric the per-plant B/A (and F/E) ratios, their range, the mean
and the mean with the single most favourable plant to a reseed dropped.

Metric (one line): mean over wrong-prior plants of ratio_B_over_A.<m>
(post-reseed window) and ratio_F_over_E.<m> (after a reset to the prior);
< 1 favours the reseed.
Command (repository root):
    python3 dev/audit/rounds/round10/study-reseed/aggregate.py OUT_DIR
    (OUT_DIR holds base_<plant>.out and tr_<plant>.out from reseed_rolling.py)
Baseline SHA: 17f1c55fa. No production symbol is driven here; the numbers are
reseed_rolling.py's (instrumented symbols and perturbation in its header).
"""
import glob
import os
import re
import sys

NULLS = {"sz_null", "tz_null"}


def read(path):
    out = {}
    for line in open(path):
        m = re.match(r"RESULT (\S+?)=(-?[0-9.]+(?:e-?\d+)?|nan)", line)
        if m:
            out[m.group(1)] = float(m.group(2))
    return out


def main():
    d = sys.argv[1]
    runs = {os.path.basename(p)[5:-4]: read(p) for p in sorted(glob.glob(os.path.join(d, "base_*.out")))}
    metrics = ["ratio_B_over_A.house_step_rms_post", "ratio_B_over_A.house_std_post",
               "ratio_B_over_A.house_rmse_post", "ratio_B_over_A.fc_mae_post",
               "ratio_B_over_A.lower_std_post", "ratio_B_over_A.lower_rmse_post",
               "ratio_C_over_B.house_std_post", "ratio_C_over_B.house_rmse_post",
               "ratio_F_over_E.house_rmse_after_reset", "ratio_F_over_E.fc_mae_after_reset",
               "ratio_F_over_E.lower_rmse_after_reset"]
    for m in metrics:
        vals = {p: r.get(f"{p}.{m}") for p, r in runs.items()}
        wrong = {p: v for p, v in vals.items() if v is not None and p not in NULLS}
        null = {p: v for p, v in vals.items() if v is not None and p in NULLS}
        if not wrong:
            continue
        xs = sorted(wrong.values())
        loo = sum(xs[1:]) / (len(xs) - 1) if len(xs) > 1 else float("nan")  # most favourable (lowest) dropped
        name = m.replace(".", "_")
        print(f"{m}: " + ", ".join(f"{p}={v:.3f}" for p, v in sorted(wrong.items()))
              + (" | null " + ", ".join(f"{p}={v:.3f}" for p, v in sorted(null.items())) if null else ""))
        print(f"RESULT {name}.n={len(xs)}")
        print(f"RESULT {name}.mean={sum(xs) / len(xs):.4f}")
        print(f"RESULT {name}.range={xs[0]:.4f}..{xs[-1]:.4f}")
        print(f"RESULT {name}.loo_drop_best_mean={loo:.4f}")
    tr = {os.path.basename(p)[3:-4]: read(p) for p in sorted(glob.glob(os.path.join(d, "tr_*.out")))}
    for p, r in tr.items():
        for m in ("ratio_B_over_A.house_step_rms_post", "ratio_B_over_A.house_std_post", "ratio_B_over_A.house_rmse_post",
                  "ratio_B_over_A.lower_std_post"):
            v = r.get(f"{p}.{m}")
            if v is not None:
                print(f"RESULT perturbation_trust_region_off.{p}.{m}={v:.4f}")


if __name__ == "__main__":
    main()
