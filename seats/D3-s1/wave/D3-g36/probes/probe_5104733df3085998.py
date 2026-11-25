#!/usr/bin/env python3
# Box D3-g36 probe for mutant 5104733df3085998 (CMP_BOUND, sysid.py:835, _lm_solve).
# Metric: (1) the log-UA component _lm_solve returns for a three-parameter problem whose optimum is log(1e3) (outside the [log 1e-4, log 1e2] band); (2) rollouts identify_slab requests with UA or C_r outside the band, on a 22-sample night with 0.1 C noise and arm-time prior (UA, C_r) = (1e-3, 1e-3), counted until the first such request.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g36/probes/probe_5104733df3085998.py
# Expected: RESULT baseline_log_ua=4.605170 (clipped to log 1e2) ; RESULT mutant_log_ua=6.907755 ; RESULT baseline_out_of_band_rollouts=0 (fit completes in ~430 rollouts, 0.4 s) ; RESULT mutant_out_of_band_rollouts>=1 (the un-clipped iterate leaves the band; unbounded, that run did not finish in 200 s on this box: provisional) ; RESULT null_moved=0
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (sysid.py read with `git show`, so a gate's committed mutant never leaks in).
# Machine: box D3-g36, Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython; counts exact.
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:_lm_solve (line 835 `if x.size >= 3:`); _lm_solve is called by identify_slab at line 2380 with x.size == 3.
# Perturbation: `if x.size >= 3:` -> `if x.size > 3:`, applied in memory to the baseline source (g36_common.load(key)). Direction: the band projection of log UA and log C_r is skipped in the three-parameter full solve: iterates leave the band and the rollout is asked for out-of-band plants (the run then does not finish in 200 s).
# Null control: a two-parameter _lm_solve (size 2, untouched by either arm) and the default-prior noise-free night, where no iterate leaves the band.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g36_common as c  # noqa: E402
import numpy as np  # noqa: E402
from datetime import timedelta  # noqa: E402

KEY = "5104733df3085998"
T0 = c.start()
B, M = c.load(), c.load(KEY)

target = np.array([np.log(1e3), 0.0, 0.0])
xb, _ = B._lm_solve(lambda x: x - target, np.zeros(3))
xm, _ = M._lm_solve(lambda x: x - target, np.zeros(3))
t2 = np.array([np.log(1e3), 0.0])
nb_, _ = B._lm_solve(lambda x: x - t2, np.zeros(2), clip=None)
nm_, _ = M._lm_solve(lambda x: x - t2, np.zeros(2), clip=None)
LO_U, HI_U, LO_C, HI_C = (float(np.exp(B.SLAB_LOG_UA_LO)), float(np.exp(B.SLAB_LOG_UA_HI)),
                          float(np.exp(B.SLAB_LOG_ROOM_CAP_LO)), float(np.exp(B.SLAB_LOG_ROOM_CAP_HI)))


class OutOfBand(Exception):
    pass


def out_of_band(mod, **kw):
    s = c.slab_sid(mod, **kw)
    orig, box = mod._simulate_slab_path, {"n": 0, "oob": 0}

    def w(ua, room_cap, *a, **k):
        box["n"] += 1
        if not (LO_U * 0.999 <= ua <= HI_U * 1.001 and LO_C * 0.999 <= room_cap <= HI_C * 1.001):
            box["oob"] += 1
            raise OutOfBand()
        return orig(ua, room_cap, *a, **k)
    mod.__dict__["_simulate_slab_path"] = w
    try:
        r = c.fit(s.identify_slab())
    except OutOfBand:
        r = "stopped at the first out-of-band rollout"
    except Exception as e:
        r = f"raises:{type(e).__name__}"
    mod.__dict__["_simulate_slab_path"] = orig
    return r, box


rb, bb = out_of_band(B, prior=(1e-3, 1e-3), noise=0.1)
rm, bm = out_of_band(M, prior=(1e-3, 1e-3), noise=0.1)
ra, ba = out_of_band(B)
rz, bz = out_of_band(M)
print(f"RESULT baseline_log_ua={xb[0]:.6f}")
print(f"RESULT mutant_log_ua={xm[0]:.6f}")
print(f"RESULT baseline_out_of_band_rollouts={bb['oob']} count  # {rb}; {bb['n']} rollouts")
print(f"RESULT mutant_out_of_band_rollouts={bm['oob']} count  # {rm}; after {bm['n']} rollouts")
print(f"RESULT null_moved={int(abs(nb_[0] - nm_[0]) > 0) + int(ra != rz) + int(ba['oob'] != bz['oob'])} count")
c.footer(T0)
