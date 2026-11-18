#!/usr/bin/env python3
"""The COP learner's duty floor and ratio gates (#2066's fixer's instrument).

Written by the #2066 fixer, not by the finder: the live-install finding
committed no harness. The ``selfmod`` rows reproduce the #2066 round-1
reviewer's probe 3 (hpo-seats/review-2066/ev/reviewer_probe3.py) as a control.

Drives the real coordinator's ``_learn_measured_cop`` with synthetic intervals
on a 14 kW-nameplate install with a 1.0 kW modulation floor (and an overstated
3.0 kW one), outside the frost band. Each interval also feeds #2065's
running-draw window, which the off-ask refusal reads, as the cycle does. Run it from a worktree root, at the base
and at the head:

    PYTHONPATH=tests/hastub:custom_components:tests \
        python3 dev/audit/harnesses/cop_duty_floor.py

Rows, each "folded/intervals scale":
  * ``duty_floor_kw`` -- the floor both folds read.
  * ``min1_*``/``min3_*`` -- the pump draws what the plan asked (3 intervals
    per draw). ``running`` is the defect (0 at the base); ``idle``,
    ``standby`` and ``duty_cycled`` are what the floor exists to refuse. The
    3.0 kW rows are the gap this PR leaves for the observed-draw cap
    (dev/programme/carries/carry-2065.json).
  * ``selfmod_independent`` -- the reviewer's probe: the plan asks 1.0-2.0 kW,
    the pump draws 1.9-2.55 kW regardless; true COP equals the model's, so the
    right scale is 1.000. ``selfmod_matched`` is its control: draw == ask.
  * ``true_<s>`` -- a heat-led pump whose true COP scale is ``s``: the meter
    reads ask x current scale / s, with +-5 % meter noise (seeded). The right
    scale is ``s``; a gate on the ask level alone would never fold these.
  * ``true_0.7_4kw`` -- the same on a correctly sized 4 kW nameplate, which
    the base could already learn: the head must not lose it.
  * ``fixed3_duty<d>`` -- a fixed-speed pump (min == max == 3 kW) at duty
    ``d``, plan and meter both averaging: the behaviour change on such pumps.
  * ``selfset_<shape>`` -- round 2's reviewer probe 5: 2.2 kW drawn whatever
    is asked, asks stepping hourly, three-hourly or flat; right scale 1.000.
  * ``p4_<shape>`` -- round 2's reviewer probe 4: a correctly modulating 6 kW
    pump with +-10/20 % meter noise, a one-tick lag, and a 1/0.8 efficiency
    shift (open loop, so its absolute scale is not the truth).
  * ``true_0.7_reload150`` -- the draw evidence round-tripped through its
    store form at tick 150, as a restart does.
  * ``liveness`` -- a 4 kW nameplate whose old floor (1.2 kW) already
    admitted 2.2 kW: a zero at the base is the floor, not a dead learner.
  * ``<row>_warm_<fill>`` (R10-COP-LEARNER-DRAW-FLOOR) -- the row behind a
    running-draw window ``draw_range.fold`` filled first. ``run_led``: 60
    intervals asked 3.0-5.0 kW drawing 0.6 x the ask (an overstated 3.0 kW
    minimum: the pump runs at 1.8 kW); ``run_low``: the same drawing 0.3 x
    (low end 0.9 kW, under ``on_threshold_kw``); ``own``: 60 of the row's own
    interval. The capped floor moves ``min3_running`` under ``run_led`` and
    ``run_low`` and nothing under ``own``, whose asks sit below the minimum.
  * ``held_full`` / ``held_filling`` -- 96 intervals asked 2.6 kW drawing 3.2
    on a 3.0 kW minimum and 4 kW nameplate, behind a full window of such asks,
    and behind one that fills at interval 48: no evidence ever arrives, so the
    folded count must equal the base's (a held interval is not a lost one).
  * ``true_0.6_max_cycle_move`` -- the largest change of the COP scale in one
    cycle of the ``true_0.6`` run: a release folds many held intervals at once.
  * ``sub_min_true_0.6_x<n>`` -- the round-1 handoff reviewer's row: a heat-led
    pump of true scale 0.6 whose plan never asks at or above its configured
    minimum (min == max == 3 kW, asks 1.9-2.55 kW), over ``n`` intervals. No
    run-asked pair ever exists, so the evidence is pending until the window
    is full (``draw_range.WINDOW`` running samples) and unobtainable after.
    From there the heat-ask probe judges it (R11-OUTSIDE-SELF-SETTING-PUMP,
    round-3 design): two asks in three are under the duty floor, so no two
    admitted intervals are consecutive, no pair completes, and the verdict
    stays pending with nothing folded (``x1440`` is 30 days of it). Before
    that design the departures base folded waited for the window, then folded.
  * ``selfset_<kw>_flat_*`` / ``selfset_<kw>_within_*`` and
    ``heatled_true_<s>_flat_*`` (R11-OUTSIDE-SELF-SETTING-PUMP, owner ruling
    D4) -- a 4 kW nameplate under flat asks of 1.5 kW +-2 % (``flat``), which
    never span ``draw_range.FOLLOW_ASK_SPAN``, so the window's evidence turns
    unobtainable: a pump drawing ``kw`` +-3 % whatever is asked (2.2 beyond
    ``COP_ASK_TOLERANCE``, 1.6 and 1.4 within it; right scale 1.000), or a
    heat-led one of true scale ``s``. ``_from<s0>`` starts at a persisted
    scale ``s0`` (an install the released learner already walked);
    ``_reload70_400`` round-trips the COP record at ticks 70 and 400,
    ``_lost`` without its scale-response key. ``selfset_2.2_swing*`` and
    ``selfset_2.2_mix*`` (fix review 1 of #3662): the 2.2 kW pump whose draw
    swings on its own (``swing``, seeds 1 to 5 as ``_s<seed>``), ``swing0_control`` its null control;
    ``_p2``/``_p3``/``_p4`` swing over 2 to 4 cycles, the length of the
    probe's own pairs.
    Each line adds the lowest and
    highest scale, the cycles off 1.000 by more than 5 % (a dither cycle at
    +-7.2 % counts), the probes started, the furthest the scale sat from a
    running probe's base in dither steps (``band``: 0.500 is the centred
    level, 1.000 the one-sided level at a clamp), and the verdict.
    These runs are open loop: the ask stays fixed whatever the scale, as the
    live plan's does only where the ask is pinned (flat asks are that case).
  * ``heatled_true_0.68_flat_max_cycle_move`` -- the largest change of the
    scale in one cycle of ``heatled_true_0.68_flat_x672``, beside
    ``true_0.6_max_cycle_move``: the hold a pending probe built folds at once.
  * ``repriced_heat1.2_true_0.8`` (design verdict item 1b98ae3f) -- the same
    asks re-priced each tick against the scale, as an unpinned plan does:
    asked = 1.2 kW of heat over the scale, drawn = 1.2 over the true 0.8. The
    heat ask stays flat under the dither, so the probe has no contrast: the
    row must not read does_not_follow.
  * ``null_dither0_<pump>`` -- null control 1 of the round-3 design note: the
    dither's amplitude forced to zero (``ScaleDither.levels`` returning the
    base twice). The verdict comes from the dither, so neither a heat-led
    nor a self-setting pump may latch one. ``-`` at a tree without the dither.
  * ``defrost_inferred_<pump>_<t>C`` -- design-verdict item e98d0ab9: the
    defrost derate's inferred factor after 96 flat-ask intervals with no
    defrost flag, at 2 °C (frost band) and 8 °C; ``selfset_2.2`` against
    ``matched`` (draw equal to the ask) as its control.
  * ``held_<fill>_heatled_true_0.8`` -- the ``held_*`` windows behind a
    heat-led pump of true scale 0.8: the control for the ``held_*`` rows,
    whose fixed 3.2 kW draw is a self-setting pump's.

The folded column is ``_cop_samples`` at the end of the run, replays included.
"""
from __future__ import annotations

import itertools
import math
import random
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

from heatpump_optimizer import draw_range  # noqa: E402
from heatpump_optimizer.accuracy import AccuracySample  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.thermal_model import on_threshold_kw  # noqa: E402

CFG = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "heat_pump_power_entity": "sensor.pump_power",
}
STATES = {
    "sensor.indoor": FakeState("21.0", unit="°C"),
    "sensor.outdoor": FakeState("8.0", unit="°C"),
    "sensor.pump_power": FakeState("2200", unit="W"),
}
#: Synthetic draw classes, kW. Idle: controller and crankcase heater.
#: Standby: circulation pump, at or under ``on_threshold_kw`` (0.5 kW here).
#: Duty-cycled: the pump at its 1.0 kW floor for 50 % / 70 % of the interval
#: over a 0.05 kW idle. Running: the live install's band, and the floor itself.
CLASSES = {
    "idle": (0.02, 0.05, 0.1),
    "standby": (0.2, 0.3, 0.5),
    "duty_cycled": (0.525, 0.715),
    "running": (1.0, 1.2, 1.9, 2.2, 2.55),
}
ASKED = (1.0, 1.25, 1.5, 1.75, 2.0)
DRAWN = (1.9, 2.2, 2.55)


def coord(p_max: float = 14.0, p_min: float = 1.0) -> HeatPumpOptimizerCoordinator:
    c = HeatPumpOptimizerCoordinator(
        FakeHass(dict(STATES)),
        FakeEntry(data=dict(CFG, heat_pump_max_power=p_max, heat_pump_min_power=p_min)),
    )
    c._current_state.outdoor_temperature = 8.0
    return c


def run(pairs, p_max=14.0, p_min=1.0, true=None, noise=0.0, reload_at=None, warm=(), moves=None,
        scale0=None, reload_cop=(), lose_verdict=False, stats=None, reprice=None, noise_seed=1) -> str:
    """Feed (asked, drawn) intervals as the cycle does: the running-draw fold
    (#2065's ``draw_range.fold``) and then the COP learner reading its
    evidence. ``true`` replaces drawn by a heat-led pump's (a callable: its
    true scale at each tick; ``noise_seed`` seeds its meter noise); ``reload_at``
    round-trips the draw evidence through its store form at that tick (a
    restart). ``warm``: (asked, drawn) intervals folded into the running-draw
    window before the counted ones. ``moves``: a list that receives each
    cycle's change of the COP scale. ``scale0``: the COP scale a store
    persisted, applied before the first interval (an upgraded install the
    released learner already walked). ``reload_cop``: ticks at which the COP
    learner's record round-trips through its store form (``lose_verdict``:
    without its scale-response key). ``stats``: a dict that receives the
    lowest and highest scale, the cycles off 1.000 by more than 5 %, the
    probes started and the furthest the scale sat from a running probe's
    base, in dither steps, and the latched scale-response verdict (``-``
    where the code has none). ``reprice``: the heat, kW, a plan re-pricing
    its ask against the scale asks for each tick (asked = reprice / scale,
    drawn = reprice / ``true``)."""
    rnd = random.Random(noise_seed)
    c = coord(p_max, p_min)
    if scale0 is not None:
        c._apply_cop_scale(scale0)
    lo = hi = c._cop_scale
    off = probes = 0
    band, based = None, False
    for asked, drawn in warm:
        draw_range.fold(c._accuracy.draw, drawn, (asked, 0.0), c._thermal_params,
                        frozen=False, distorted=False, defrost=False)
    learn = getattr(c._learn_measured_cop, "__code__", None)
    takes_draw = learn is not None and learn.co_argcount > 1
    for tick, (asked, drawn) in enumerate(pairs):
        if reprice is not None:
            asked, drawn = reprice / c._cop_scale, reprice / true
        elif true is not None:
            drawn = asked * c._cop_scale / (true(tick) if callable(true) else true)
        c._current_action = {"power": asked, "dhw_power": 0.0}
        c._measured_power = drawn * (1.0 + rnd.uniform(-noise, noise))
        draw = getattr(c._accuracy, "draw", None)
        if draw is not None:
            if tick == reload_at:
                c._accuracy.draw = draw = type(draw).from_dict(draw.as_dict())
            draw_range.fold(draw, c._measured_power, c._commanded_split(), c._thermal_params,
                            frozen=False, distorted=False, defrost=False)
        if tick in reload_cop:
            stored = c._measured_cop.as_dict()
            if lose_verdict:
                stored.pop("scale_response", None)
            c._measured_cop = type(c._measured_cop).from_dict(stored)
        before = c._cop_scale
        if takes_draw:
            c._learn_measured_cop(draw)
        else:
            c._learn_measured_cop()
        if moves is not None:
            moves.append(abs(c._cop_scale - before))
        lo, hi = min(lo, c._cop_scale), max(hi, c._cop_scale)
        off += abs(c._cop_scale - 1.0) > 0.05
        base = getattr(getattr(c._measured_cop, "probe", None), "base", None)
        probes += base is not None and not based
        based = base is not None
        if based:
            band = max(band or 0.0, abs(math.log(c._cop_scale / base)) / math.log(1.15))
    if stats is not None:
        stats.update(lowest=f"{lo:.3f}", highest=f"{hi:.3f}", off=off, probes=probes,
                     band="-" if band is None else f"{band:.3f}",
                     verdict=getattr(c._measured_cop, "scale_response", "-"))
    return f"{c._cop_samples}/{len(pairs)} {c._cop_scale:.3f}"


def flat(n: int, drawn=None, seed: int = 7) -> list[tuple[float, float]]:
    """``n`` flat asks of 1.5 kW +-2 %, each beside a draw of ``drawn`` kW
    +-3 % (a pump setting its own power), or of the ask where ``drawn`` is
    None (a heat-led ``true`` run replaces it)."""
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        ask = 1.5 * rng.uniform(0.98, 1.02)
        out.append((ask, ask if drawn is None else drawn * rng.uniform(0.97, 1.03)))
    return out


def swing(n: int, kw: float, parts, seed: int, phase: float = 0.0) -> list[tuple[float, float]]:
    """``n`` flat asks of 1.5 kW +-2 %, each beside a draw of ``kw`` x (1 +
    sum a sin(2 pi t / p + phase)) +-3 % for each (a, p) of ``parts``: a pump
    setting its own power, which swings over p cycles whatever is asked."""
    rng = random.Random(seed)
    out = []
    for t in range(n):
        ask = 1.5 * rng.uniform(0.98, 1.02)
        f = 1 + sum(a * math.sin(2 * math.pi * t / p + phase) for a, p in parts)
        out.append((ask, kw * f * rng.uniform(0.97, 1.03)))
    return out


def derate(pairs, outdoor: float) -> str:
    """The defrost derate's inferred factor at ``outdoor`` °C after ``pairs``
    (asked, drawn) intervals settle with no defrost flag, and its count."""
    c = coord(p_max=4.0)
    t0 = datetime(2026, 1, 10, tzinfo=timezone.utc)
    for i, (ask, kw) in enumerate(pairs):
        window = c._defrost_window.close(t0 + timedelta(minutes=30 * i))
        c._settle_defrost(AccuracySample(when=t0, predicted_power_kw=ask, actual_power_kw=kw, outdoor_temp=outdoor), window)
    t, h = c._defrost._bucket(outdoor, None)
    return f"factor={c._defrost.factors[t][h]:.3f}_count={c._defrost.counts[t][h]}"


def flat_row(name: str, pairs, **kw) -> None:
    """One flat-ask row on the 4 kW nameplate: "folded/intervals scale", then
    the lowest and highest scale, the cycles off 1.000 by more than 5 %, the
    probes started, the band (``run``) and the scale-response verdict."""
    st: dict = {}
    got = run(pairs, p_max=4.0, stats=st, **kw).replace(" ", "_scale=")
    print(f"RESULT {name}={got} lowest={st['lowest']} highest={st['highest']} off5={st['off']} "
          f"probes={st['probes']} band={st['band']} verdict={st['verdict']}")


def main() -> None:
    params = coord()._thermal_params
    print(f"RESULT duty_floor_kw={params.flow_lift_power_floor_kw:.3f}")
    print(f"RESULT on_threshold_kw={on_threshold_kw(params):.3f}")
    for p_min in (1.0, 3.0):
        for name, draws in CLASSES.items():
            got = [run([(kw, kw)] * 3, p_min=p_min).split()[0] for kw in draws]
            folded = sum(int(g.split("/")[0]) for g in got)
            print(f"RESULT min{p_min:g}_{name}_folded={folded}/{3 * len(draws)}")
    cyc = lambda xs, n: list(itertools.islice(itertools.cycle(xs), n))  # noqa: E731
    independent = list(zip(cyc(ASKED, 96), cyc(DRAWN, 96)))
    matched = [(d, d) for d in cyc(DRAWN, 96)]
    print(f"RESULT selfmod_independent={run(independent).replace(' ', '_scale=')}")
    print(f"RESULT selfmod_independent_4kw={run(independent, p_max=4.0).replace(' ', '_scale=')}")
    print(f"RESULT selfmod_matched={run(matched).replace(' ', '_scale=')}")
    for true in (0.6, 0.7, 0.8, 1.3):
        print(f"RESULT true_{true:g}={run(matched * 3, true=true, noise=0.05).replace(' ', '_scale=')}")
    print(f"RESULT true_0.7_4kw={run(matched * 3, p_max=4.0, true=0.7, noise=0.05).replace(' ', '_scale=')}")
    # A fixed-speed pump (min == max == 3 kW) whose plan prices part duty as an
    # average and whose meter averages too: the floor is 2.4 kW at the head.
    for duty in (0.5, 0.7, 0.85):
        kw = 3.0 * duty + 0.05 * (1.0 - duty)
        print(f"RESULT fixed3_duty{int(duty * 100)}={run([(kw, kw)] * 5, p_max=3.0, p_min=3.0).replace(' ', '_scale=')}")
    print(f"RESULT liveness_folded={run([(2.2, 2.2)] * 3, p_max=4.0).split()[0]}")
    # Round 2's reviewer probe 5: a pump drawing 2.2 kW +-3 % whatever is
    # asked, under asks stepping hourly, three-hourly, or flat.
    for name, block in (("hourly", 4), ("three_hour", 12), ("flat", 96)):
        rng = random.Random(7)
        asks: list[float] = []
        while len(asks) < 96:
            level = 1.5 if block == 96 else rng.uniform(1.0, 2.0)
            asks += [level * rng.uniform(0.98, 1.02) for _ in range(block)]
        pairs = [(a, 2.2 * rng.uniform(0.97, 1.03)) for a in asks[:96]]
        print(f"RESULT selfset_{name}={run(pairs).replace(' ', '_scale=')}")
    # Round 2's reviewer probe 4 shapes: 6 kW, 1.5 kW floor, asks 2-5 kW.
    def p4(seed, f):
        rng = random.Random(seed)
        a = [rng.uniform(2.0, 5.0) for _ in range(96)]
        return f(rng, a)
    shapes = {
        "follow_noise10": p4(1, lambda r, a: [(x, x * r.uniform(0.9, 1.1)) for x in a]),
        "follow_noise20": p4(2, lambda r, a: [(x, x * r.uniform(0.8, 1.2)) for x in a]),
        "eff0.8_noise5": p4(3, lambda r, a: [(x, x * 1.25 * r.uniform(0.95, 1.05)) for x in a]),
        "eff0.8_noise10": p4(4, lambda r, a: [(x, x * 1.25 * r.uniform(0.9, 1.1)) for x in a]),
        "follow_lag1tick": p4(5, lambda r, a: list(zip(a, [a[0]] + a[:-1]))),
    }
    for name, pairs in shapes.items():
        print(f"RESULT p4_{name}={run(pairs, p_max=6.0, p_min=1.5).replace(' ', '_scale=')}")
    # Evidence across a restart: the draw window is store state (#2065), so a
    # reload at tick 150 of a true-0.7 run must keep folding.
    print(f"RESULT true_0.7_reload150={run(matched * 3, true=0.7, noise=0.05, reload_at=150).replace(' ', '_scale=')}")
    # R10-COP-LEARNER-DRAW-FLOOR: the floor capped by the run-asked draw.
    led = [(a, 0.6 * a) for a in cyc((3.0, 3.5, 4.0, 4.5, 5.0), 60)]
    low = [(a, 0.3 * a) for a in cyc((3.0, 3.5, 4.0, 4.5, 5.0), 60)]
    for fill in ("run_led", "run_low", "own"):
        got = []
        for kw in CLASSES["running"]:
            warm = {"run_led": led, "run_low": low, "own": [(kw, kw)] * 60}[fill]
            got.append(int(run([(kw, kw)] * 3, p_min=3.0, warm=warm).split("/")[0]))
        print(f"RESULT min3_running_warm_{fill}_folded={sum(got)}/15 per_draw={got}")
    got = [int(run([(kw, kw)] * 3, warm=[(kw, kw)] * 60).split("/")[0]) for kw in CLASSES["duty_cycled"]]
    print(f"RESULT min1_duty_cycled_warm_own_folded={sum(got)}/6")
    for duty in (0.5, 0.7):
        kw = 3.0 * duty + 0.05 * (1.0 - duty)
        print(f"RESULT fixed3_duty{int(duty * 100)}_warm_own={run([(kw, kw)] * 5, p_max=3.0, p_min=3.0, warm=[(kw, kw)] * 60).replace(' ', '_scale=')}")
    # Hold-then-replay where the evidence never arrives: nothing base folded is lost.
    depart = [(2.6, 3.2)] * 96
    for name, n in (("full", draw_range.WINDOW), ("filling", draw_range.WINDOW - 48)):
        print(f"RESULT held_{name}={run(depart, p_max=4.0, p_min=3.0, warm=[(2.6, 3.2)] * n).replace(' ', '_scale=')}")
    moves: list[float] = []
    run(matched * 3, true=0.6, noise=0.05, moves=moves)
    print(f"RESULT true_0.6_max_cycle_move={max(moves):.3f}")
    # The wait before the evidence turns unobtainable (the unobtainable-arm decision's row).
    for n in (288, 384, 480, 1440):
        got = run(cyc(matched, n), p_max=3.0, p_min=3.0, true=0.6, noise=0.05)
        print(f"RESULT sub_min_true_0.6_x{n}={got.replace(' ', '_scale=')}")
    # R11-OUTSIDE-SELF-SETTING-PUMP (owner ruling D4): flat asks on a 4 kW
    # nameplate. The run is open loop: the ask stays fixed whatever the scale,
    # as the live plan's does only where the ask is pinned (flat asks are that
    # case); an unpinned plan re-prices its ask as the scale moves.
    for n in (96, 672):
        flat_row(f"selfset_2.2_flat_x{n}", flat(n, 2.2))
    for kw in (1.6, 1.4):
        flat_row(f"selfset_{kw:g}_within_x672", flat(672, kw))
    for true in (0.68, 0.8):
        flat_row(f"heatled_true_{true:g}_flat_x672", flat(672), true=true)
    # Design verdict item 1ff86b5f: the rows held while the probe is pending
    # fold in one cycle once it reads follows; the largest one-cycle move.
    moves = []
    run(flat(672), p_max=4.0, true=0.68, moves=moves)
    print(f"RESULT heatled_true_0.68_flat_max_cycle_move={max(moves):.3f}")
    for s0 in (0.5, 0.7):
        flat_row(f"selfset_2.2_flat_from{s0:g}", flat(672, 2.2), scale0=s0)
        flat_row(f"selfset_1.6_within_from{s0:g}", flat(672, 1.6), scale0=s0)
    for true in (0.45, 0.68):
        flat_row(f"heatled_true_{true:g}_flat_from0.5", flat(672), true=true, scale0=0.5)
    flat_row("selfset_2.2_flat_reload70_400", flat(672, 2.2), reload_cop=(70, 400))
    flat_row("selfset_2.2_flat_reload70_400_lost", flat(672, 2.2), reload_cop=(70, 400), lose_verdict=True)
    # Fix review 1 of #3662 (the reviewer's seven rows, over seeds 1 to 5): the same
    # pump's draw swinging on its own, whatever is asked; amplitude 0 is the null control.
    for seed in (1, 2, 3, 4, 5):
        for name, parts, phase in (
            ("swing0_control", [], 0.0), ("swing0.15_p64", [(0.15, 64)], 0.0), ("swing0.15_p80", [(0.15, 80)], 0.0),
            ("swing0.3_p96", [(0.3, 96)], 0.0), ("swing0.15_p120", [(0.15, 120)], 0.0),
            ("mix_daily0.1_5day0.2_phasepi", [(0.1, 48), (0.2, 240)], math.pi),
            ("mix_daily0.1_5day0.2_phase0", [(0.1, 48), (0.2, 240)], 0.0),
        ):
            flat_row(f"selfset_2.2_{name}_s{seed}", swing(672, 2.2, parts, seed, phase))
    # The round-3 design's rows: swings as short as the probe's own pairs, a
    # plan that re-prices its ask against the scale, and null control 1.
    for amp, period in ((0.3, 2), (0.4, 3), (0.3, 4)):
        flat_row(f"selfset_2.2_swing{amp:g}_p{period}_s1", swing(672, 2.2, [(amp, period)], 1))
    flat_row("repriced_heat1.2_true_0.8_x672", flat(672), true=0.8, reprice=1.2)
    dither = getattr(sys.modules[HeatPumpOptimizerCoordinator.__module__.rsplit(".", 1)[0] + ".accuracy"], "ScaleDither", None)
    if dither is None:
        print("RESULT null_dither0_heatled_true_0.8=- null_dither0_selfset_2.2=-")
    else:
        levels, dither.levels = dither.levels, staticmethod(lambda base: (base, base))
        try:
            flat_row("null_dither0_heatled_true_0.8", flat(672), true=0.8)
            flat_row("null_dither0_selfset_2.2", flat(672, 2.2))
        finally:
            dither.levels = staticmethod(levels)
    # Invariant h's control under the moving held_* rows: heat-led twins of
    # true 0.8 behind the same windows (a fixed 3.2 kW draw is self-setting).
    # Design-verdict item e98d0ab9: the defrost derate's inferred estimator
    # (``_settle_defrost`` with no defrost flag) reads ask over draw, the same
    # mechanism, in the frost band; this diff leaves it alone.
    for outdoor in (2.0, 8.0):
        for name, kw in (("selfset_2.2", 2.2), ("matched", None)):
            print(f"RESULT defrost_inferred_{name}_{outdoor:g}C={derate(flat(96, kw), outdoor)}")
    for name, n in (("full", draw_range.WINDOW), ("filling", draw_range.WINDOW - 48)):
        print(f"RESULT held_{name}_heatled_true_0.8={run(depart, p_max=4.0, p_min=3.0, true=0.8, warm=[(2.6, 3.2)] * n).replace(' ', '_scale=')}")


if __name__ == "__main__":
    main()
