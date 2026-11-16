"""Reviewer's map (builder: the fix reviewer): verdict of a self-setting 2.2 kW pump under flat
1.5 kW asks whose draw swings sinusoidally, by period (cycles) and amplitude, seeds 1-5.
Also a weather-like mix: a daily (48-cycle) swing plus a multi-day one."""
import math, random, sys
sys.argv = sys.argv[:1]
sys.path.insert(0, "dev/audit/harnesses")
import cop_duty_floor as h
def sig(n, kw, parts, seed, phase=0.0):
    rng = random.Random(seed); out = []
    for t in range(n):
        ask = 1.5 * rng.uniform(0.98, 1.02)
        f = 1 + sum(a * math.sin(2 * math.pi * t / p + phase) for a, p in parts)
        out.append((ask, kw * f * rng.uniform(0.97, 1.03)))
    return out
import io, contextlib
def verdict(pairs):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        h.flat_row("x", pairs)
    line = buf.getvalue().strip()
    return line.split("verdict=")[1], line.split("=")[1].split()[0]
for period in (64, 80, 96, 120, 144):
    for amp in (0.15, 0.2, 0.3):
        v = [verdict(sig(672, 2.2, [(amp, period)], s)) for s in range(1, 6)]
        print(f"MAP period={period} amp={amp} follows={sum(x[0]=='follows' for x in v)}/5 end={[x[1] for x in v]}")
for phase in (0.0, math.pi / 2, math.pi, 3 * math.pi / 2):
    v = [verdict(sig(672, 2.2, [(0.1, 48), (0.2, 240)], s, phase)) for s in range(1, 6)]
    print(f"MIX daily0.1+5day0.2 phase={phase:.2f} follows={sum(x[0]=='follows' for x in v)}/5 end={[x[1] for x in v]}")
