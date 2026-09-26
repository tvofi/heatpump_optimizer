#!/usr/bin/env python3
"""D7 verify-v3 (D7-s2-01): the sysid UA bias across the coordinator cadences
the config flow allows (10..120 min, default 30), truth integrated at 1 min.

Metric (one line): per cadence, presets (of 3) whose production
sysid:SystemIdentification.identify_slab UA has |UA/UA_true-1|>5% or no
completed fit, and presets adopted by sysid:adoption_decision, on a noise-free
truth == declared params integrated at 1-minute steps.
Count key: result.heat_loss_kw_per_c and AdoptionDecision.admit (the value the
production seam delivers). Reuses the finder's step driver (drive, declared_params)
from tools/audit/round9/D7/s2/sysid_plant.py by import, changing only CADENCE_H
and the truth substep count; the fit, the gate and the state machine are production.
Run (repository root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/verify-v3/sysid_cadence.py [--substep-rollout]
Perturbation: --substep-rollout (the finder's one-line in-memory edit, 6 sub-steps
per sample in sysid._valve_drive): bias_gt5pct must fall at every cadence >= 30.
Expected: exact counts (noise 0), see verify-v3.md. Machine: cloud container linux x86_64.
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import importlib.util, sys, time  # noqa: E401,E402
import numpy as np  # noqa: E402

spec = importlib.util.spec_from_file_location("sysid_plant", "tools/audit/round9/D7/s2/sysid_plant.py")
H = importlib.util.module_from_spec(spec)
spec.loader.exec_module(H)  # applies --substep-rollout itself when in argv
S = H.S


def main() -> int:
    c0, t0 = time.process_time(), time.thread_time()
    tot_b = tot_a = 0
    for minutes in (10, 15, 30, 60, 120):
        H.CADENCE_H = minutes / 60.0
        biased = adopted = 0
        cells = []
        for b in H.PRESETS:
            dec = H.declared_params(b)
            sid, ua_t = H.drive(dec, minutes)  # 1-minute truth
            r = sid.result
            d = S.adoption_decision(r, dec, sid.config)
            bias = (r.heat_loss_kw_per_c / ua_t - 1) if r.heat_loss_kw_per_c else float("nan")
            if not (np.isfinite(bias) and abs(bias) <= 0.05):
                biased += 1
            adopted += int(bool(d.admit))
            cells.append(f"{b}:{bias:+.3f}{'A' if d.admit else ''}")
        tot_b += biased
        tot_a += adopted
        print(f"  cadence {minutes:3d} min: {' '.join(cells)}")
        print(f"RESULT cad{minutes}_bias_gt5pct={biased} count")
        print(f"RESULT cad{minutes}_adopted={adopted} count")
    print(f"RESULT all_cadences_bias_gt5pct={tot_b} count  # of 15")
    print(f"RESULT all_cadences_adopted={tot_a} count  # of 15")
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={(c1-c0)/max(t1-t0,1e-9):.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = next((ln.split()[1] for ln in open("/proc/vmstat") if ln.startswith("pswpin")), "n/a")
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
