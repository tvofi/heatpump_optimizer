#!/usr/bin/env python3
# Metric: the step list HeatPumpOptimizer._expand_off_blocks returns, baseline vs mutant: on a pin of exactly 0.5 (the
#   tie), and the count of differing outputs over 5000 seeded random pin arrays drawn from the values production
#   writes (manual_plan PIN_OFF 0.0, PIN_ON 1.0, PIN_FREE NaN; channel_pins builds every pin from these three).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g21/probes/probe_904118eef67fced3.py
# EXPECTED RESULT tie_baseline=[2]
# EXPECTED RESULT tie_mutant=[0,1,2]
# EXPECTED RESULT production_domain_differ=0 count  (of 5000)
# EXPECTED RESULT null_delta=0 count  (pins 0.0/1.0 only)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g21 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer._expand_off_blocks
#   (line 5271 `while j >= 0 and not _pin_is_free(float(pins[j])) and float(pins[j]) < 0.5:`), callers 5257-5258.
# Perturbation: line 5271 `< 0.5` -> `<= 0.5` (CMP_BOUND 904118eef67fced3), in memory. Direction: a 0.5 pin joins the
#   released off-block; no move on the {0, 1, NaN} pins the integration writes.
# Null control: pins of 0.0 and 1.0 only.
#@PRE
from custom_components.heatpump_optimizer.manual_plan import PIN_FREE, PIN_OFF, PIN_ON  # noqa: E402
NAME = "_expand_off_blocks"
OLD = "while j >= 0 and not _pin_is_free(float(pins[j])) and float(pins[j]) < 0.5:"
NEW = "while j >= 0 and not _pin_is_free(float(pins[j])) and float(pins[j]) <= 0.5:"
f = lambda p, b: repr(HeatPumpOptimizer._expand_off_blocks(np.asarray(p, float), b))  # noqa: E731
tie = ([0.5, 0.5, 0.0, 1.0], [2])
null = ([0.0, 1.0, 0.0, 0.0], [3])
rng = np.random.default_rng(11)
dom = np.array([PIN_OFF, PIN_ON, PIN_FREE])
FUZZ = []
for _ in range(5000):
    n = int(rng.integers(1, 30))
    FUZZ.append((dom[rng.integers(0, 3, n)], sorted(set(rng.integers(0, n, int(rng.integers(1, 4))).tolist()))))
b = (f(*tie), f(*null), [f(*c) for c in FUZZ])
with mutated(NAME, OLD, NEW):
    m = (f(*tie), f(*null), [f(*c) for c in FUZZ])
print(f"RESULT tie_baseline={b[0].replace(' ', '')}")
print(f"RESULT tie_mutant={m[0].replace(' ', '')}")
print(f"RESULT production_domain_differ={sum(x != y for x, y in zip(b[2], m[2]))} count")
print(f"RESULT null_delta={int(b[1] != m[1])} count")
