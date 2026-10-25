"""Revised counter rule: refused deltas keep the baseline; accepted delta / whole span.
Integer-kWh counter, 30 min reads, span cap 3 cycles (HOUSE_LOSS_MAX_SAMPLE_HOURS 1.5 h).
Accept when delta >= N quanta; past the cap, refuse and re-baseline."""
import math, random
def run(P, N, cap=3, cycles=20000, seed=1):
    rnd = random.Random(seed); E = rnd.random(); base = math.floor(E); n = 0; acc = []; refused = 0
    for _ in range(cycles):
        E += P * 0.5; n += 1; c = math.floor(E); d = c - base
        if d >= N:
            acc.append((d, n * 0.5)); base = c; n = 0
        elif n >= cap:
            refused += 1; base = c; n = 0
    if not acc: return "no accepted span"
    m = sum(d for d, _ in acc) / sum(h for _, h in acc)
    per = sum(d / h for d, h in acc) / len(acc)
    return f"accepted {len(acc)}, refused spans {refused}; energy-weighted mean {m:.3f} kW, mean of span means {per:.3f} kW"
for N in (1, 2):
    for P in (0.6, 1.5, 3.0):
        print(f"N={N} true {P} kW: {run(P, N)}")
