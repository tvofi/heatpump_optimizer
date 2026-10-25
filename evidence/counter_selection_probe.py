"""Design review R10-HEAT-METER, point 2: the counter rule's selection bias.

An integer-kWh heat counter read once per 30 min cycle, true heat P kW.
The note's rule (lines 45-50): a 0 delta while the pump draws is refused,
the baseline advances every cycle, an accepted delta is divided by one cycle.
Null control: P = 3.0 kW, a whole quantum every cycle, must read unbiased.
"""
import math

for P in (0.6, 1.5, 3.0):
    E = 0.0
    prev = 0
    acc = []
    for _ in range(2000):
        E += P * 0.5
        c = math.floor(E)
        d = c - prev
        prev = c
        if d > 0:
            acc.append(d / 0.5)
    print(f"true {P} kW: accepted mean {sum(acc)/len(acc):.3f} kW, accepted share {len(acc)/2000:.3f}")
