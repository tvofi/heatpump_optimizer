"""Fixed-span counter rule (design R10-HEAT-METER revision 1, point 2).
Integer-kWh heat counter (q = 1 kWh), 30 min reads, span = K cycles fixed in advance.
The span is accepted or refused on an independent figure (the electric counter's
energy times the reference COP; here the true energy, i.e. a perfect proxy), never
on the heat delta itself, so no selection on the quantised value. Accept when
q / expected_kwh <= EPS. Null: 3.0 kW must read 3.0."""
import math, random
EPS = 0.5
def run(P, K=3, spans=20000, seed=1):
    rnd = random.Random(seed); E = rnd.random(); out = []; ref = 0
    for _ in range(spans):
        c0 = math.floor(E); E += P * 0.5 * K; d = math.floor(E) - c0
        if 1.0 / (P * 0.5 * K) <= EPS: out.append(d / (0.5 * K))
        else: ref += 1
    if not out: return f"all {ref} spans refused (resolution bound)"
    m = sum(out) / len(out); sd = (sum((x - m) ** 2 for x in out) / len(out)) ** 0.5
    return f"accepted {len(out)}, mean of span means {m:.3f} kW (sd {sd:.3f}), refused {ref}"
for P in (0.6, 1.5, 2.2, 3.0):
    print(f"true {P} kW: {run(P)}")
