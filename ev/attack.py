"""Reviewer's own configurations on the fixer's harness functions (cop_duty_floor.run)."""
import importlib.util, itertools, random, sys
spec = importlib.util.spec_from_file_location("h", "/tmp/rv/harness_head.py"); h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
cyc = lambda xs, n: list(itertools.islice(itertools.cycle(xs), n))
matched = [(d, d) for d in cyc(h.DRAWN, 96)]
def r(name, *a, **k):
    try: print(f"RESULT rv_{name}={h.run(*a, **k).replace(' ', '_scale=')}")
    except Exception as e: print(f"RESULT rv_{name}=ERROR {type(e).__name__}: {e}")
# efficiency shifts on other nameplates/minima (truth = the true value)
for pmax, pmin in ((4.0, 1.0), (6.0, 1.5), (14.0, 3.0), (14.0, 0.0), (3.0, 3.0)):
    for true in (0.6, 1.3):
        r(f"true{true}_max{pmax:g}_min{pmin:g}", matched * 3, p_max=pmax, p_min=pmin, true=true, noise=0.05)
# zero-evidence short runs: fewer intervals than MIN_SAMPLES (everything stays held)
r("true0.6_short40", matched[:40], true=0.6, noise=0.05)
# self-setting pump (draw ignores ask), other nameplates: truth 1.000
rng = random.Random(11); asks = [rng.uniform(1.0, 4.0) for _ in range(192)]
for pmax in (4.0, 6.0, 14.0):
    r(f"selfset_max{pmax:g}", [(a, 2.2 * rng.uniform(0.97, 1.03)) for a in asks], p_max=pmax)
# restart of the window mid-hold
r("true0.6_reload30", matched * 3, true=0.6, noise=0.05, reload_at=30)
# overstated minimum, pump follows at 0.6x: asks 3-5 on min 3 (run-asked), truth: efficiency 1/0.6?
led = [(a, 0.6 * a) for a in cyc((3.0, 3.5, 4.0, 4.5, 5.0), 192)]
r("led0.6_min3", led, p_min=3.0)
if "--long" in sys.argv:
    for n in (3, 4, 5):
        r(f"true0.6_max3_min3_x{n*96}", matched * n, p_max=3.0, p_min=3.0, true=0.6, noise=0.05)
