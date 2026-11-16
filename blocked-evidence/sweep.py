"""Fixer's domain sweep: self-setting pump with an independent draw swing (must not latch
follows), and heat-led pumps incl. meter noise and a weather-swinging true COP (must latch follows)."""
import math, random, sys, io, contextlib, itertools
from multiprocessing import Pool
NPROC = int(sys.argv[1]) if len(sys.argv) > 1 else 4
sys.argv = sys.argv[:1]; sys.path.insert(0, "dev/audit/harnesses")
import cop_duty_floor as h
def sig(n, kw, parts, seed, phase=0.0):
    rng = random.Random(seed); out = []
    for t in range(n):
        ask = 1.5 * rng.uniform(0.98, 1.02)
        f = 1 + sum(a * math.sin(2 * math.pi * t / p + phase) for a, p in parts)
        out.append((ask, kw * f * rng.uniform(0.97, 1.03)))
    return out
def one(job):
    kind, kw, amp, per, seed, phase, s0, noise = job
    kwargs = {} if s0 is None else {"scale0": s0}
    buf = io.StringIO()
    if kind == "selfset":
        pairs = sig(672, kw, [(amp, per)] if amp else [], seed, phase)
        with contextlib.redirect_stdout(buf): h.flat_row("x", pairs, **kwargs)
    else:  # heat-led of true scale kw, its true COP swinging amp over per cycles, meter noise
        pairs = h.flat(672, seed=seed)
        trues = [kw * (1 + amp * math.sin(2 * math.pi * t / per + phase)) for t in range(672)]
        # custom loop mirroring h.run for heat-led with time-varying true
        rnd = random.Random(seed); c = h.coord(4.0, 1.0)
        if s0 is not None: c._apply_cop_scale(s0)
        from heatpump_optimizer import draw_range
        for t, (asked, _) in enumerate(pairs):
            drawn = asked * c._cop_scale / trues[t]
            c._current_action = {"power": asked, "dhw_power": 0.0}
            c._measured_power = drawn * (1 + rnd.uniform(-noise, noise))
            draw = c._accuracy.draw
            draw_range.fold(draw, c._measured_power, c._commanded_split(), c._thermal_params, frozen=False, distorted=False, defrost=False)
            c._learn_measured_cop(draw)
        return (job, c._measured_cop.scale_response, round(c._cop_scale, 3))
    line = buf.getvalue().strip()
    return (job, line.split("verdict=")[1], float(line.split("scale=")[1].split()[0]))
if __name__ == "__main__":
    jobs = []
    for kw in (1.6, 2.2, 3.0):
        for per in (8, 16, 32, 48, 64, 80, 96, 120, 144, 240):
            for amp in (0.15, 0.3, 0.4):
                for seed in range(1, 6):
                    for phase in (0.0, math.pi / 2, math.pi, 3 * math.pi / 2):
                        jobs.append(("selfset", kw, amp, per, seed, phase, None, 0))
    for s0 in (0.5, 0.7):
        for per in (48, 64, 96):
            for seed in range(1, 6):
                jobs.append(("selfset", 2.2, 0.3, per, seed, math.pi, s0, 0))
    for true in (0.45, 0.6, 0.68, 0.8, 1.3):
        for amp, per in ((0, 1), (0.15, 64), (0.3, 96), (0.3, 48)):
            for noise in (0.0, 0.05, 0.1):
                for seed in range(1, 4):
                    for s0 in (None, 0.5):
                        jobs.append(("heatled", true, amp, per, seed, 0.0, s0, noise))
    with Pool(NPROC) as p:
        res = p.map(one, jobs, chunksize=4)
    for job, v, sc in res:
        print("SWEEP", *job, v, sc)
