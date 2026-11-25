#!/usr/bin/env python3
# Metric: PeakTracker billed peak (kW) and threshold_kw (kW) after one as_dict -> from_dict round trip (a
#   restart) of a month whose recorded peaks are [4.0, 0.0004, 0.0003] kW (as_dict rounds them to
#   [4.0, 0.0, 0.0]), tariff peaks_averaged=3. Also: number of peaks reloaded, and the closed month's billed peak.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g40/probes/probe_3e9a439baa86a074.py
# EXPECTED RESULT peaks_reloaded_baseline=3 count, peaks_reloaded_mutant=1 count
# EXPECTED RESULT billed_peak_kw_baseline=1.333 kW, billed_peak_kw_mutant=4.0 kW (before the restart 1.3336)
# EXPECTED RESULT threshold_kw_baseline=0.0 kW, threshold_kw_mutant=4.0 kW (before the restart 0.0003)
# EXPECTED RESULT null_delta=0 kW (peaks [4,3,2]: both arms identical)
# Tolerance: exact (1e-9).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g40 (4 vCPU Intel Xeon @ 2.10GHz).
# Instrumented symbol: custom_components.heatpump_optimizer.tariff:_stored_peaks (tariff.py:528
#   `if not math.isfinite(value) or value < 0.0:`), caller PeakTracker.from_dict (tariff.py:416, 419).
# Perturbation: `value < 0.0` -> `value <= 0.0` (key 3e9a439baa86a074), applied in a temp copy of the package
#   archived from the baseline. Direction: a stored 0.0 peak is dropped on load -> billed peak up, threshold up.
# Null control: peaks [4.0, 3.0, 2.0] (no zero entry), same round trip, both arms.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe_lib

SNIP = r'''
import json
from custom_components.heatpump_optimizer.tariff import PeakTracker, CapacityTariff
tar = CapacityTariff(enabled=True, price_per_kw=50.0, peaks_averaged=3)
out = {}
for name, peaks in (("zero", [4.0, 0.0004, 0.0003]), ("null", [4.0, 3.0, 2.0])):
    t = PeakTracker(month="2026-11", peaks=list(peaks), peak_days=["2026-11-03", "2026-11-04", "2026-11-05"],
                    closed_month="2026-10", closed_peaks=list(peaks))
    before = (t.billed_peak_kw(tar), t.threshold_kw(tar))
    t2 = PeakTracker.from_dict(t.as_dict())
    out[name] = {"before_billed": before[0], "before_threshold": before[1], "n": len(t2.peaks),
                 "billed": t2.billed_peak_kw(tar), "threshold": t2.threshold_kw(tar),
                 "closed_billed": t2.billing_statements(tar)[0][1]}
print(json.dumps(out))
'''

if __name__ == "__main__":
    b, m = probe_lib.two_arms(SNIP, 528, "if not math.isfinite(value) or value < 0.0:",
                              "if not math.isfinite(value) or value <= 0.0:")
    print("baseline", b); print("mutant", m)
    z0, z1 = b["zero"], m["zero"]
    print(f"RESULT billed_peak_before_restart={z0['before_billed']:.6f} kW")
    print(f"RESULT peaks_reloaded_baseline={z0['n']} count")
    print(f"RESULT peaks_reloaded_mutant={z1['n']} count")
    print(f"RESULT billed_peak_kw_baseline={z0['billed']:.6f} kW")
    print(f"RESULT billed_peak_kw_mutant={z1['billed']:.6f} kW")
    print(f"RESULT threshold_kw_baseline={z0['threshold']:.6f} kW")
    print(f"RESULT threshold_kw_mutant={z1['threshold']:.6f} kW")
    print(f"RESULT closed_month_billed_baseline={z0['closed_billed']:.6f} kW")
    print(f"RESULT closed_month_billed_mutant={z1['closed_billed']:.6f} kW")
    nd = max(abs(b["null"][k] - m["null"][k]) for k in ("billed", "threshold", "closed_billed", "n"))
    print(f"RESULT null_delta={nd:.3g} kW")
    probe_lib.machine_lines()
