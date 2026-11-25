import random  # noqa: E402
from custom_components.heatpump_optimizer import defrost  # noqa: E402

TC, HC = defrost.TEMP_CENTERS, defrost.HUMIDITY_CENTERS


def learned(seed):
    """A learner with every bucket measured and inferred to distinct values (no uniform-surroundings shortcut)."""
    rng = random.Random(seed)
    d = defrost.DefrostDerate()
    for t in range(len(defrost.TEMP_EDGES) - 1):
        for h in range(len(defrost.HUMIDITY_EDGES) - 1):
            d.duty[t][h] = rng.uniform(0.0, 0.3)
            d.duty_counts[t][h] = rng.choice((1, 5, 12, 40))
            d.factors[t][h] = rng.uniform(0.55, 1.0)
            d.counts[t][h] = rng.choice((0, 3, 20))
    return d


def probe_values():
    """Every centre, the span ends, values a hair either side of each centre, and non-finite inputs."""
    vals = set()
    for c in TC + HC:
        vals |= {c, c - 1e-9, c + 1e-9, -c}
    vals |= {-100.0, 100.0, 0.0, float("inf"), float("-inf"), float("nan")}
    return sorted(vals, key=lambda v: (v != v, v))


def factor_delta(fn, seeds=range(6)):
    """max |factor_mutant - factor_baseline| over every (t, h) pair of probe_values and every learner."""
    worst, pairs, tuple_moves = 0.0, 0, 0
    vals = probe_values()
    for seed in seeds:
        d = learned(seed)
        for t in vals:
            for h in vals + [None]:
                hh = h if h is not None else HC[0]
                b = d._factor_uncached(float(t), float(hh))
                with mock.patch.object(defrost, "_interp_position", fn):
                    m = d._factor_uncached(float(t), float(hh))
                pairs += 1
                if b != m and not (b != b and m != m):
                    worst = max(worst, abs(m - b) if (m == m and b == b) else float("inf"))
    for v in vals:
        for cs in (TC, HC):
            b, m = defrost._interp_position(v, cs), fn(v, cs)
            if b != m and not (b[1] != b[1] and m[1] != m[1] and b[0] == m[0]):
                tuple_moves += 1
    return worst, pairs, tuple_moves
