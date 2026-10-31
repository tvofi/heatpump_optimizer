"""Table the RESULT lines run_q1.sh wrote, plus the leave-one-plant-out band.

Command (repository root): python3 dev/audit/rounds/round10/study-ident/collect_q1.py OUTDIR
Reads OUTDIR/*.out only; computes nothing it does not print the source of.
"""
import glob
import re
import sys

import numpy as np

ARMS = ["fix0.50", "fix0.75", "fix1.00", "fix1.25", "fix1.50", "fix2.00", "none", "learn", "learn+gains",
        "dark0.50", "dark1.00", "dark2.00"]


def main(out):
    rows = {}
    for f in sorted(glob.glob(f"{out}/*.out")):
        d = {}
        for line in open(f):
            m = re.match(r"RESULT (P\d\.\w+\.g[\d.]+)\.(ua_bias|vent_tripped_share|joint|solar_scale)\.(\S+?)=(\S+)", line)
            if m:
                tag, kind, k, v = m.groups()
                d["tag"] = tag
                d[(kind, k)] = v
        if "tag" in d:
            rows[d["tag"]] = d
    print("ua_bias per arm (effective house UA / truth - 1, last 7 of 42 days)")
    print("tag".ljust(18) + "".join(a[:9].rjust(10) for a in ARMS))
    for t, d in sorted(rows.items()):
        print(t.ljust(18) + "".join(d.get(("ua_bias", a), "")[:8].rjust(10) for a in ARMS))
    print()
    print("joint IV fit / solar learner / vent trips")
    print("tag".ljust(18) + "  cond    corr  uaSepIV uaSepOLS   apSep   apSE nSun10%  solLearn vent(fix1) vent(none)")
    for t, d in sorted(rows.items()):
        g = lambda k: d.get(("joint", k), "")  # noqa: E731
        print(t.ljust(18) + f"{g('cond')[:6]:>6} {g('corr_dT_qsol')[:6]:>7} {g('ua_sep_err')[:7]:>8} "
              f"{g('ua_sep_err_ols')[:7]:>8} {g('ap_sep_err')[:7]:>7} {g('ap_se')[:6]:>6} {g('n_sunny_for_10pct')[:6]:>7} "
              f"{d.get(('solar_scale', 'learn'), '')[:6]:>9} {d.get(('vent_tripped_share', 'fix1.00'), ''):>10} "
              f"{d.get(('vent_tripped_share', 'none'), ''):>10}")
    # sensitivity of UA bias to the aperture state, per autumn plant: slope of
    # ua_bias on (model aperture / truth - 1) over the fixed arms, and LOO
    print()
    slopes = {}
    for t, d in sorted(rows.items()):
        if ".autumn.g1.00" not in t:
            continue
        xs = [float(a[3:]) - 1.0 for a in ARMS[:6]]
        ys = [float(d[("ua_bias", a)]) for a in ARMS[:6]]
        slopes[t.split(".")[0]] = float(np.polyfit(xs, ys, 1)[0])
        dark = [float(d[("ua_bias", a)]) for a in ARMS[9:12] if ("ua_bias", a) in d]
        print(f"RESULT sens.{t}=slope {slopes[t.split('.')[0]]:+.4f} per unit aperture error; "
              f"fixed-arm spread {max(ys) - min(ys):.4f}; night-only spread {(max(dark) - min(dark)) if dark else float('nan'):.4f}")
    if len(slopes) >= 5:
        v = np.asarray(list(slopes.values()))
        best = min(slopes, key=lambda k: abs(slopes[k]))
        rest = np.asarray([s for k, s in slopes.items() if k != best])
        print(f"RESULT sens.pooled range={v.min():+.4f}..{v.max():+.4f} mean={v.mean():+.4f} n={len(v)} "
              f"loo_drop={best} loo_range={rest.min():+.4f}..{rest.max():+.4f}")


if __name__ == "__main__":
    main(sys.argv[1])
