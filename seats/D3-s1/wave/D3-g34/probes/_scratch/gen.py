import json, sys
from pathlib import Path
P = Path('/root/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes')
muts = {k: json.load(open(f'/root/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/state/results/complete/{k}.json'))['mutant']
        for k in [l.split('\t')[0] for l in open('/root/keys.tsv').read().splitlines()[1:] if l.strip()]}
SPEC = {
 'b8d5ec03e8eba5c7': dict(metric="identify()'s SysIdResult differs (repr) when the dt filter leaves fewer than 5 rows from >= 6 usable samples",
  cases='''[
    ("gap_4rows", L.samples([20, 20.2, 20.3, 20.1, 20.4, 19.9, 20.0], [0] * 7, [3, 3, 6, 6, 0, 0, 0],
                            [L.S, L.S, L.T, L.T, L.R, L.R, L.R], [0, 0.5, 1, 4, 4.5, 8, 8.5])),
    ("gap_0rows", L.samples([20, 20.5, 21, 20.8, 20.4, 20.2], [0] * 6, [3, 6, 6, 0, 0, 0],
                            [L.S, L.T, L.T, L.R, L.R, L.R], [0, 3, 6, 9, 12, 15])),
]''', nulls='''[("plant_20rows", L.plant()), ("plant_noisy", L.plant(noise=0.03, seed=4))]'''),
 '756f3bebd6a42efc': dict(metric="identify()'s SysIdResult differs (repr) when SysIdConfig.thermal_mass_prior < 0.1",
  cases='''[
    ("tm0.05_noisy", L.plant(noise=0.03, seed=4), sysid.SysIdConfig(thermal_mass_prior=0.05)),
    ("tm0.0", L.plant(), sysid.SysIdConfig(thermal_mass_prior=0.0)),
]''', nulls='''[("tm10_noisy", L.plant(noise=0.03, seed=4), sysid.SysIdConfig(thermal_mass_prior=10.0)),
           ("tm0.1_noisy", L.plant(noise=0.03, seed=4), sysid.SysIdConfig(thermal_mass_prior=0.1))]'''),
 '3918ca4fedbfc5bb': dict(metric="identify()'s SysIdResult differs (repr) at the smallest row counts the rows>=5 guard admits",
  cases='''[
    ("rows5_exact", L.plant(hours=(0.5, 1.0, 1.0), dt_h=0.5)[:6]),
    ("rows5_noisy", L.plant(hours=(0.5, 1.0, 1.0), dt_h=0.5, noise=0.03, seed=1)[:6]),
    ("rows6", L.plant(hours=(0.5, 1.0, 1.0), dt_h=0.5)[:7]),
    ("gap_4rows_guarded", L.samples([20, 20.2, 20.3, 20.1, 20.4, 19.9, 20.0], [0] * 7, [3, 3, 6, 6, 0, 0, 0],
                                    [L.S, L.S, L.T, L.T, L.R, L.R, L.R], [0, 0.5, 1, 4, 4.5, 8, 8.5])),
    ("plant", L.plant()),
]''', nulls='''[]'''),
 '84372c0eb1502d14': dict(metric="identify()'s SysIdResult differs (repr) on a noisy window whose first-pass UA/C slope is negative",
  cases='''[
    ("seed53_noise0.1", L.plant(ua=0.0831723946810419, cap=5.681713411968536, gains=0.5743780480979319, noise=0.1,
                                dt_h=0.5, drift=0.05, seed=53, q=(3.96809291432578, 7.542472144251088, 0.0))),
]''', nulls='''[("plant_clean", L.plant()), ("plant_noisy", L.plant(noise=0.03, seed=4))]'''),
 '20f72103eda78713': dict(metric="identify()'s SysIdResult differs (repr) when two same-phase samples share a timestamp (h_prev = 0) or sit 3600 us apart",
  cases='''[
    ("dup0_step", L.insert_after(L.plant(), 6, timedelta(0))),
    ("dup0_relax", L.insert_after(L.plant(), 15, timedelta(0))),
    ("tie3600us_step", L.insert_after(L.plant(), 6, timedelta(microseconds=3600))),
]''', nulls='''[("gap3601us_step", L.insert_after(L.plant(), 6, timedelta(microseconds=3601))),
           ("dup0_across_phases", L.insert_after(L.plant(), 3, timedelta(0)))]'''),
 '50daaa57683189c5': dict(metric="identify()'s SysIdResult differs (repr) when two same-phase samples are exactly 1e-6 h (3600 us) apart",
  cases='''[
    ("tie3600us_step", L.insert_after(L.plant(), 6, timedelta(microseconds=3600))),
    ("tie3600us_step2", L.insert_after(L.plant(), 10, timedelta(microseconds=3600))),
    ("tie3600us_relax", L.insert_after(L.plant(), 15, timedelta(microseconds=3600))),
]''', nulls='''[("dup0_step", L.insert_after(L.plant(), 6, timedelta(0))),
           ("gap3601us_step", L.insert_after(L.plant(), 6, timedelta(microseconds=3601)))]'''),
 '4eeb366191982f92': dict(metric="identify()'s SysIdResult differs (repr) on a window with exactly three in-phase second differences",
  cases='''[
    ("3triples_noise0.02", L.plant(hours=(0.75, 0.75, 0.75), noise=0.02, seed=0)[:9]),
    ("3triples_clean", L.plant(hours=(0.75, 0.75, 0.75))[:9]),
]''', nulls='''[("4triples_noise0.02", L.plant(hours=(1.0, 1.0, 0.75), noise=0.02, seed=0)[:12]),
           ("plant", L.plant())]'''),
 'a9bc37e9ba781833': dict(metric="identify()'s SysIdResult differs (repr) at the smallest row counts the rows>=5 guard admits",
  cases='''[
    ("rows5_exact", L.plant(hours=(0.5, 1.0, 1.0), dt_h=0.5)[:6]),
    ("rows5_noisy", L.plant(hours=(0.5, 1.0, 1.0), dt_h=0.5, noise=0.03, seed=1)[:6]),
    ("rows6", L.plant(hours=(0.5, 1.0, 1.0), dt_h=0.5)[:7]),
    ("gap_4rows_guarded", L.samples([20, 20.2, 20.3, 20.1, 20.4, 19.9, 20.0], [0] * 7, [3, 3, 6, 6, 0, 0, 0],
                                    [L.S, L.S, L.T, L.T, L.R, L.R, L.R], [0, 0.5, 1, 4, 4.5, 8, 8.5])),
    ("plant", L.plant()),
]''', nulls='''[]'''),
 '44bb0ce0b258242c': dict(metric="identify()'s SysIdResult differs (repr) when sigma2 equals x1_spread2/9 exactly in float64",
  cases='''[("sigma_tie", L.sigma_tie_series())]''',
  nulls='''[("sigma_tie_broken", L.sigma_tie_series(break_tie=True)), ("plant", L.plant())]'''),
 'b97b45a6162a2f00': dict(metric="identify()'s SysIdResult differs (repr) when sigma2 == 0 (no or fewer than three in-phase triples, or flat second differences)",
  cases='''[
    ("no_triples_relabelled_plant", L.relabel(L.plant(dt_h=0.5), L.ALT)),
    ("no_triples_exact_series", L.exact_series(0.5, 0.25, [4.0] * 9, [0.0, 4.0, -2.0, 8.0, 2.0, -4.0, 6.0, 0.0, 10.0])),
    ("two_triples", L.plant(hours=(0.5, 0.75, 0.5), dt_h=0.25)[:8]),
    ("no_triples_flat_delta", L.relabel(L.samples([20.0 + 0.25 * i for i in range(10)], [15.0 + 0.25 * i for i in range(10)],
                                         [2, 2, 2, 5, 5, 5, 0, 0, 0, 2], [L.S] * 10, list(range(10))), L.ALT)),
    ("sigma_tie", L.sigma_tie_series()),
    ("plant", L.plant()),
]''', nulls='''[]'''),
 '6b6a8493668dde1c': dict(metric="identify()'s SysIdResult differs (repr) when sigma2 == 0 (no or fewer than three in-phase triples, or flat second differences)",
  cases='''[
    ("no_triples_relabelled_plant", L.relabel(L.plant(dt_h=0.5), L.ALT)),
    ("no_triples_exact_series", L.exact_series(0.5, 0.25, [4.0] * 9, [0.0, 4.0, -2.0, 8.0, 2.0, -4.0, 6.0, 0.0, 10.0])),
    ("two_triples", L.plant(hours=(0.5, 0.75, 0.5), dt_h=0.25)[:8]),
    ("no_triples_flat_delta", L.relabel(L.samples([20.0 + 0.25 * i for i in range(10)], [15.0 + 0.25 * i for i in range(10)],
                                         [2, 2, 2, 5, 5, 5, 0, 0, 0, 2], [L.S] * 10, list(range(10))), L.ALT)),
    ("plant", L.plant()),
]''', nulls='''[]'''),
 '10665a84dc064489': dict(metric="identify()'s SysIdResult differs (repr) when the power and delta columns are exactly collinear (2-column fallback rank 1)",
  cases='''[
    ("power_prop_delta", L.collinear_series()),
    ("power_zero", L.exact_series(0.5, 0.25, [0.0] * 9, [0.0, 4.0, -2.0, 8.0, 2.0, -4.0, 6.0, 0.0, 10.0])),
]''', nulls='''[("power_const_rank2", L.exact_series(0.5, 0.25, [4.0] * 9, [0.0, 4.0, -2.0, 8.0, 2.0, -4.0, 6.0, 0.0, 10.0])),
           ("plant", L.plant())]'''),
 'd7421c10ed63c281': dict(metric="identify()'s SysIdResult differs (repr) when the 4-column solve is singular and the 2-column fallback has full rank 2",
  cases='''[("power_const_rank2", L.exact_series(0.5, 0.25, [4.0] * 9, [0.0, 4.0, -2.0, 8.0, 2.0, -4.0, 6.0, 0.0, 10.0]))]''',
  nulls='''[("power_prop_delta_rank1", L.collinear_series()), ("plant", L.plant())]'''),
 '07227ec96c3e14de': dict(metric="identify()'s SysIdResult differs (repr) when the fit's UA/C is negative (a room that runs away from outdoor)",
  cases='''[("negative_ua", L.plant(ua=-0.1, t_room=20.0))]''',
  nulls='''[("plant", L.plant()), ("plant_noisy", L.plant(noise=0.03, seed=4))]'''),
 '3e78e62aa0f2e687': None, '87c3101b5663f17b': None,
}
TIE = '''
def tie_cases(which):
    """Exact-model 2-column-fallback series (power constant, so the 4-column solve is singular) whose true
    coefficient on the guarded side is 1e-6 and its +-300 neighbouring floats, plus 1000 random outdoor
    sequences at the true value: the search for an input where the fitted value lands on 1e-6 exactly."""
    out = []
    outs = [0.0, 4.0, -2.0, 8.0, 2.0, -4.0, 6.0, 0.0, 10.0]
    for j in range(-300, 301):
        x = 1e-6
        for _ in range(abs(j)):
            x = math.nextafter(x, math.inf if j > 0 else -math.inf)
        out.append((f"ulp{j:+d}", L.exact_series(x, 0.25, [4.0] * 9, outs) if which == "k"
                    else L.exact_series(0.5, x, [4.0] * 9, outs)))
    rng = np.random.default_rng(1)
    for t in range(1000):
        o = [float(v) for v in rng.integers(-8, 12, 9)]
        out.append((f"rand{t}", L.exact_series(1e-6, 0.25, [4.0] * 9, o) if which == "k"
                    else L.exact_series(0.5, 1e-6, [4.0] * 9, o)))
    return out
'''
SPEC['3e78e62aa0f2e687'] = dict(metric="identify()'s SysIdResult differs (repr) when the fitted 1/C lands on 1e-6 exactly (the <= / < tie)",
  cases='''[("negative_ua", L.plant(ua=-0.1, t_room=20.0))] + tie_cases("p")''',
  nulls='''[("plant", L.plant())]''', tie=True)
SPEC['87c3101b5663f17b'] = dict(metric="identify()'s SysIdResult differs (repr) when the fitted UA/C lands on 1e-6 exactly (the <= / < tie)",
  cases='''[("negative_ua", L.plant(ua=-0.1, t_room=20.0))] + tie_cases("k")''',
  nulls='''[("plant", L.plant())]''', tie=True)

for key, sp in SPEC.items():
    m = muts[key]
    rel = f"dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_{key[:8]}.py"
    head = f'''#!/usr/bin/env python3
# Metric: {sp['metric']}; counted per input as 1 when the baseline and mutant SysIdResult reprs differ
#   (every float exact). Count key: the SysIdResult identify() returns, never an input attribute.
# Command: PYTHONPATH=tests/hastub python3 {rel}
# EXPECTED: see the EXPECTED block below (filled from the first run on box D3-g34; exact, deterministic).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g34 (Linux x86_64, 4 vCPU Intel Xeon @ 2.10GHz,
#   16 GB, venv-ci CPython 3.14), probes run while the box's one full gate ran (load1 ~1).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:SystemIdentification.identify,
#   line {m['line']} `{m['old'].strip()}` ({m['kind']} {key}).
# Perturbation: line {m['line']} -> `{m['new'].strip()}`, applied in memory (the method recompiled from its own
#   source with the one line replaced; never on disk). Direction: cases_differing 0 -> >0 if the edit is observable.
# Null control: the null cases, inputs where the edit cannot matter; null_differing must read 0.
# Reach: identify() is harness-only at the baseline (sysid.py:1826-1835 and :2306-2313: production arms with a
#   declared plant and routes every finished experiment to identify_slab); tests/features.py drives it via arm/step.
'''
    body = f'''import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import math, sys
from datetime import timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _sysid_lib as L  # noqa: E402
import numpy as np  # noqa: E402,F401
from custom_components.heatpump_optimizer import sysid  # noqa: E402,F401

LINE = {m['line']}
OLD = {m['old']!r}
NEW = {m['new']!r}
{TIE if sp.get('tie') else ''}
CASES = {sp['cases']}
NULLS = {sp['nulls']}

if __name__ == "__main__":
    L.run_probe(LINE, OLD, NEW, CASES, NULLS)
'''
    (P / f"probe_{key[:8]}.py").write_text(head + body)
    print("wrote", rel)
