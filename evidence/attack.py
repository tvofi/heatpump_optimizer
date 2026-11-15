"""Reviewer's own configurations (round 1 on the PR) on the fixer's harness function cop_duty_floor.run.
Builder's instrument, reviewer's parameters. Run from a production tree: PYTHONPATH=tests/hastub:custom_components:tests."""
import importlib.util, itertools, random, sys
spec = importlib.util.spec_from_file_location("h", sys.argv[1]); h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
cyc = lambda xs, n: list(itertools.islice(itertools.cycle(xs), n))
matched = [(d, d) for d in cyc(h.DRAWN, 96)]
def r(name, *a, **k):
    try: print(f"RESULT rv2_{name}={h.run(*a, **k).replace(' ', '_scale=')}")
    except Exception as e: print(f"RESULT rv2_{name}=ERROR {type(e).__name__}: {e}")
# efficiency shifts, other nameplates and minima than round 1's
for pmax, pmin in ((8.0, 2.0), (10.0, 1.0), (4.0, 0.0), (2.6, 1.9)):
    for true in (0.5, 0.9, 1.5):
        r(f"true{true}_max{pmax:g}_min{pmin:g}", matched * 3, p_max=pmax, p_min=pmin, true=true, noise=0.05)
# noisier follower
r("true0.7_noise15", matched * 3, true=0.7, noise=0.15)
# zero evidence: a run shorter than MIN_SAMPLES (truth 0.6); everything a departure
for n in (10, 30, 47, 49):
    r(f"true0.6_max4_first{n}", (matched * 3)[:n], p_max=4.0, true=0.6, noise=0.05)
# self-setting pump, draw independent of the ask (truth 1.000), asks spanning and not spanning
rng = random.Random(7); asks = [rng.uniform(1.0, 4.0) for _ in range(288)]
for pmax in (4.0, 8.0):
    r(f"selfset_span_max{pmax:g}", [(a, 2.4 * rng.uniform(0.95, 1.05)) for a in asks], p_max=pmax)
    r(f"selfset_flatask_max{pmax:g}", [(2.0 * rng.uniform(0.98, 1.02), 2.9 * rng.uniform(0.95, 1.05)) for _ in asks], p_max=pmax)
# overstated minimum, pump follows the ask at 0.5x (asks at or above the minimum): the cap's install
led = [(a, 0.5 * a) for a in cyc((5.0, 5.5, 6.0, 7.0, 8.0), 288)]
r("led0.5_min5_max14", led, p_max=14.0, p_min=5.0)
# restart of the draw window during the hold
r("true0.6_max4_reload40", matched * 3, p_max=4.0, true=0.6, noise=0.05, reload_at=40)
