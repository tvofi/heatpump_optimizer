#!/usr/bin/env python3
"""R11-OWNER-STEP-KICK: the space set-point's step-start kick to the ceiling, counted.

The design's harness (design/R11-OWNER-STEP-KICK 09fecb1b, section 4). No
finder harness exists: the owner's live report is the evidence. Reads one
``hpo-debug/1`` bundle (HA's ``data``/``debug`` wrappers unwrapped; its
``replay`` half: the entry's config and the entities' recorded states; its
``cycle_rows``: the action's level) and prints counts only: no entity id,
text or value of a bundle is printed, and a bundle is never committed.

Definitions (section 4):

* a swap: a mode write to Heating after a hot-water mode, or a space write
  rising off the gate within 15 minutes of one (a gate transport), within
  90 s of a step boundary;
* its class, by the start's first space write: ``hot_inlet`` (at least the
  ceiling less 0.5 K, the pump-loop return within the lift of the ceiling),
  ``other`` (at least that, a cool return), ``both_internal`` (the mode was
  Heating + DHW throughout the 15 minutes before), ``none``.

Arms:

  (none)      the self-test: a synthetic bundle of ``--days`` (default 4) drawn
              from ``--seed`` (default 3881), through every arm below, with the
              perturbations and nulls the design names; the EXPECTED lines.
  --bundle B  leg R (pre-merge replay): the classes; each swap's first write
              recomputed from the bundle's own series through
              ``thermal_model.modulation_floor_flow_c`` and
              ``flow_setpoint_for_level``, once with today's inlet and once
              with ``flow_anchor``'s settled anchor (``Served.anchor_c``);
              fidelity (before within one entity step of the recorded write on
              90 % of replayable swaps, else the leg is void); hot_inlet after,
              I1 (after never above before), I2 (the first write past the
              settle unchanged); and leg S's and H1's counts for that bundle.
  --soak BEFORE AFTER  leg S's pass rule (H2) over two bundles.

The owner's bundle is not run here: leg R's "before" is taken on
R11-OWNER-MODE-LEGS' merged code (design section 6), deferred by the
orchestrator's ruling of 2026-11-22, and leg S runs after the deploy.

Metric: RESULT lines, counts and seconds.
Command (repository root):
    PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_owner_step_kick.py [--bundle B | --soak B A]
Expected (no arguments, the synthetic self-test at seed 3881, 4 days):
    EXPECTED RESULT swaps=96
    EXPECTED RESULT hot_inlet=40
    EXPECTED RESULT other=8
    EXPECTED RESULT both_internal=8
    EXPECTED RESULT none=40
    EXPECTED RESULT replayable=88
    EXPECTED RESULT fidelity_hits=80
    EXPECTED RESULT fidelity_ok=True
    EXPECTED RESULT hot_inlet_after=0
    EXPECTED RESULT none_after_moved=0
    EXPECTED RESULT i1_violations=0
    EXPECTED RESULT i2_violations=0
    EXPECTED RESULT leg_r_pass=True
    EXPECTED RESULT perturb_raise_delta=5
    EXPECTED RESULT perturb_lower_delta=-5
    EXPECTED RESULT soak_events=88
    EXPECTED RESULT soak_delay_moves_median=True
    EXPECTED RESULT soak_delete_missed_delta=3
    EXPECTED RESULT soak_null_pass=True
Baseline SHA: e3cb5c019b. Machine: Linux x86_64, venv-ci python3; no solve.
Perturbation: raise the first write of 5 ``none`` starts to the ceiling with the
    return within the lift: hot_inlet rises by exactly 5; lower 5 ``hot_inlet``
    first writes: it falls by 5. Delay the restart after 3 soak swaps by 120 s:
    the median latency moves; delete it on 3: missed starts rise by 3.
Null control: the bundle against itself passes leg S; ``none_after_moved``,
    the ``none`` swaps (a cool return) whose settled write differs from
    today's, reads 0, the anchor moving only a hot return's floor; H1's
    windows shifted +7.5 min, and space starts with no hot-water leg in the
    15 minutes before.
Instrumented symbols: flow_anchor:Served, flow_anchor:FLOW_INLET_KEYS,
    flow_anchor:SPACE_SIDE_KEYS, thermal_model:modulation_floor_flow_c,
    thermal_model:flow_setpoint_for_level, thermal_model:start_flow_min_lift_k,
    thermal_model:configured_flow_heat_c, thermal_model:on_threshold_kw,
    pump_mode:resolve.
"""
from __future__ import annotations

import argparse
import bisect
import gzip
import json
import random
import statistics
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, "custom_components")

from heatpump_optimizer import flow_anchor, pump_mode  # noqa: E402
from heatpump_optimizer.const import (  # noqa: E402
    CONF_HEAT_PUMP_FAULT_ENTITY,
    CONF_HEAT_PUMP_MAX_POWER,
    CONF_HEAT_PUMP_MIN_POWER,
    CONF_HEAT_PUMP_MODE_ENTITY,
    CONF_HEAT_PUMP_RETURN_TEMP_ENTITY,
    CONF_POWER_ENTITY,
    CONF_SPACE_SETPOINT_ENTITY,
)
from heatpump_optimizer.duty_switch import STOP_WINDOW_S  # noqa: E402
from heatpump_optimizer.pump_arbiter import FEEDBACK_START_HOLD, FLOW_GATE_C, LEASE_MINUTES  # noqa: E402
from heatpump_optimizer.thermal_model import (  # noqa: E402
    configured_flow_heat_c,
    flow_setpoint_for_level,
    modulation_floor_flow_c,
    on_threshold_kw,
    start_flow_min_lift_k,
)

STEP = timedelta(minutes=15)
BOUNDARY_S = 90.0
CEILING_MARGIN_K = 0.5
FIRST_WRITE = timedelta(minutes=5)
H1_WINDOW = timedelta(minutes=5)
H1_SHIFT = timedelta(minutes=7.5)
CLEAR = {"off", "0", "false", "ok", "normal", "none", "no fault", "unknown", "unavailable", ""}
T0 = datetime(2026, 1, 10, tzinfo=timezone.utc)


def load(path: str) -> dict:
    raw = Path(path).read_bytes()
    doc = json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)
    doc = doc.get("data", doc) if isinstance(doc.get("data"), dict) else doc
    return doc["debug"] if isinstance(doc.get("debug"), dict) else doc


def _num(value):
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if out == out else None


class Series:
    """One entity's recorded states, oldest first: ``at`` is the value held at a time."""

    def __init__(self, rows) -> None:
        pts = sorted((datetime.fromisoformat(r[0]), r[1], r[2] if len(r) > 2 else None) for r in rows or [])
        self.t = [p[0] for p in pts]
        self.v = [p[1] for p in pts]
        self.attrs = next((p[2] for p in reversed(pts) if isinstance(p[2], dict)), {}) or {}

    def at(self, when):
        i = bisect.bisect_right(self.t, when) - 1
        return self.v[i] if i >= 0 else None

    def changes(self, lo=None, hi=None):
        return [(t, v) for t, v, p in zip(self.t, self.v, [None, *self.v]) if v != p
                and (lo is None or t >= lo) and (hi is None or t < hi)]


class Install:
    """A bundle's config, series and cycle levels, read once."""

    def __init__(self, doc: dict) -> None:
        replay = doc.get("replay") or {}
        entry = replay.get("entry") or {}
        self.cfg = {**(entry.get("data") or {}), **(entry.get("options") or {})}
        states = replay.get("states") or {}
        self.series = {key: Series(states.get(self.cfg.get(key))) for key in (
            CONF_SPACE_SETPOINT_ENTITY, CONF_HEAT_PUMP_MODE_ENTITY, CONF_POWER_ENTITY,
            CONF_HEAT_PUMP_FAULT_ENTITY, *flow_anchor.FLOW_INLET_KEYS)}
        rows = sorted((datetime.fromisoformat(r["t"]), _num(r.get("action_kw")))
                      for r in doc.get("cycle_rows") or [] if r.get("t"))
        self.level_t, self.level_v = [r[0] for r in rows], [r[1] for r in rows]
        self.ceiling = configured_flow_heat_c(self.cfg)
        self.lift = start_flow_min_lift_k(self.cfg)
        sp = self.series[CONF_SPACE_SETPOINT_ENTITY]
        self.gate = max(FLOW_GATE_C, _num(sp.attrs.get("min")) or FLOW_GATE_C)
        self.grid = _num(sp.attrs.get("step")) or 0.5
        self.band = (_num(self.cfg.get(CONF_HEAT_PUMP_MIN_POWER)), _num(self.cfg.get(CONF_HEAT_PUMP_MAX_POWER)))
        self.ran_kw = on_threshold_kw(SimpleNamespace(min_electrical_power=self.band[0] or 0.0))

    def mode(self, when):
        return pump_mode.resolve(self.series[CONF_HEAT_PUMP_MODE_ENTITY].at(when))

    def value(self, key, when):
        return _num(self.series[key].at(when))

    def first(self, keys, when):
        return next((v for v in (self.value(k, when) for k in keys) if v is not None), None)

    def level(self, when):
        i = bisect.bisect_right(self.level_t, when) - 1
        return self.level_v[i] if i >= 0 else None

    def running(self, when):
        power = self.value(CONF_POWER_ENTITY, when)
        return power is not None and power >= self.ran_kw


def _near_boundary(when) -> bool:
    off = (when - T0.replace(year=when.year, month=when.month, day=when.day)).total_seconds() % STEP.total_seconds()
    return min(off, STEP.total_seconds() - off) <= BOUNDARY_S


def _modes(inst: Install, lo, hi) -> set:
    held = {inst.mode(lo)}
    return held | {pump_mode.resolve(v) for _t, v in inst.series[CONF_HEAT_PUMP_MODE_ENTITY].changes(lo, hi)}


def starts(inst: Install) -> list[dict]:
    """Every swap (and Heating + DHW start) with its first space write and class."""
    sp = inst.series[CONF_SPACE_SETPOINT_ENTITY]
    out, seen = [], set()
    cand = [t for t, v in inst.series[CONF_HEAT_PUMP_MODE_ENTITY].changes()
            if pump_mode.resolve(v) == pump_mode.MODE_HEAT and inst.mode(t - timedelta(seconds=1)) == pump_mode.MODE_DHW]
    cand += [t for t, v in sp.changes() if (_num(v) or 0.0) > inst.gate + CEILING_MARGIN_K
             and (_num(sp.at(t - timedelta(seconds=1))) or 0.0) <= inst.gate + CEILING_MARGIN_K]
    for t in sorted(cand):
        if not _near_boundary(t) or any(abs((t - s).total_seconds()) <= BOUNDARY_S for s in seen):
            continue
        before = _modes(inst, t - STEP, t)
        both = before == {pump_mode.MODE_HEAT_DHW} and inst.mode(t) == pump_mode.MODE_HEAT_DHW
        if not both and pump_mode.MODE_DHW not in before:
            continue
        write = next(((wt, _num(v)) for wt, v in sp.changes(t - timedelta(seconds=BOUNDARY_S), t + FIRST_WRITE)
                      if _num(v) is not None and _num(v) > inst.gate + CEILING_MARGIN_K), None)
        if write is None:
            continue
        seen.add(t)
        ret = inst.value(CONF_HEAT_PUMP_RETURN_TEMP_ENTITY, write[0])
        out.append({"t": t, "write_t": write[0], "write": write[1], "ret": ret, "both": both,
                    "cls": classify(inst, write[1], ret, both)})
    return out


def classify(inst: Install, write, ret, both) -> str:
    if both:
        return "both_internal"
    if write < inst.ceiling - CEILING_MARGIN_K:
        return "none"
    return "hot_inlet" if ret is not None and ret >= inst.ceiling - inst.lift else "other"


def _write(inst: Install, level, inlet) -> float:
    """Today's map for one inlet, on the entity's grid, as ``pump_arbiter._flow_target`` bounds it."""
    floor = modulation_floor_flow_c(inlet, inst.gate, inst.lift)
    return _mapped(inst, level, floor)


def _mapped(inst: Install, level, floor) -> float:
    floor = 35.0 if floor is None else floor
    raw = flow_setpoint_for_level(level, inst.band[0], inst.band[1], inst.ceiling, floor)
    raw = min(max(raw, min(floor, inst.ceiling)), inst.ceiling)
    return round(raw / inst.grid) * inst.grid


def _space_inlet(inst: Install, start):
    """The return of the last running Heating sample before the leg ahead of ``start``."""
    power = inst.series[CONF_POWER_ENTITY]
    lo = start - timedelta(minutes=LEASE_MINUTES + 15)
    leg = max((t for t, v in inst.series[CONF_HEAT_PUMP_MODE_ENTITY].changes(lo, start)
               if pump_mode.resolve(v) == pump_mode.MODE_DHW), default=start)
    for t in reversed([t for t in power.t if lo <= t < leg]):
        if inst.mode(t) == pump_mode.MODE_HEAT and inst.running(t):
            value = inst.value(CONF_HEAT_PUMP_RETURN_TEMP_ENTITY, t)
            if value is not None:
                return (value, t)
    return None


def replay(inst: Install, swaps: list[dict]) -> dict:
    """Leg R: today's write and the settled write for each swap's first write."""
    out = {"replayable": 0, "fidelity_hits": 0, "hot_inlet_after": 0, "none_after_moved": 0,
           "i1_violations": 0, "i2_violations": 0}
    sp = inst.series[CONF_SPACE_SETPOINT_ENTITY]
    for s in swaps:
        level = inst.level(s["write_t"])
        if s["both"] or level is None or None in inst.band:
            continue
        out["replayable"] += 1
        served = flow_anchor.Served("space", s["t"], s["t"], _space_inlet(inst, s["t"]))
        before, after = _pair(inst, served, level, s["write_t"])
        out["fidelity_hits"] += abs(before - s["write"]) <= inst.grid + 1e-9
        out["i1_violations"] += after > before + 1e-9
        out["hot_inlet_after"] += classify(inst, after, s["ret"], False) == "hot_inlet"
        out["none_after_moved"] += s["cls"] == "none" and after != before
        late = next((t for t, _v in sp.changes(s["t"] + FEEDBACK_START_HOLD, s["t"] + STEP)), None)
        if late is not None and inst.level(late) is not None:
            b2, a2 = _pair(inst, served, inst.level(late), late)
            out["i2_violations"] += a2 != b2
    out["fidelity_ok"] = out["replayable"] > 0 and out["fidelity_hits"] >= 0.9 * out["replayable"]
    return out


def _pair(inst: Install, served, level, when) -> tuple[float, float]:
    live = inst.first(flow_anchor.FLOW_INLET_KEYS, when)
    side = inst.first(flow_anchor.SPACE_SIDE_KEYS, when)
    anchor = served.anchor_c(live, side, when, FEEDBACK_START_HOLD, timedelta(minutes=LEASE_MINUTES))
    today = modulation_floor_flow_c(live, inst.gate, inst.lift)
    settled = modulation_floor_flow_c(anchor, inst.gate, inst.lift)
    floors = [35.0 if f is None else f for f in (today, settled)]
    return _mapped(inst, level, floors[0]), _mapped(inst, level, min(floors))


def soak(inst: Install, swaps: list[dict], delay=0, delete=0) -> dict:
    """Leg S's H2 events: the swap stop, the restart, a missed start; per-day medians."""
    power = inst.series[CONF_POWER_ENTITY]
    events = []
    for s in swaps:
        if s["both"] or not inst.running(s["t"] - timedelta(seconds=60)):
            continue
        stop = next((t for t in power.t if s["t"] <= t <= s["t"] + timedelta(seconds=STOP_WINDOW_S)
                     and not inst.running(t)), None)
        if stop is None:
            events.append((s["t"], False, None))
            continue
        restart = next((t for t in power.t if stop < t < s["t"] + STEP and inst.running(t)), None)
        if restart is not None and len(events) < delete:
            restart = None
        elif restart is not None and len(events) < delay:
            restart += timedelta(seconds=120)
        events.append((s["t"], True, None if restart is None else (restart - stop).total_seconds()))
    lat = [e[2] for e in events if e[2] is not None]
    days: dict = {}
    for t, _stop, latency in events:
        if latency is not None:
            days.setdefault(t.date(), []).append(latency)
    medians = [statistics.median(v) for v in days.values()]
    return {"soak_events": len(events), "stop_at_swap": sum(e[1] for e in events),
            "missed_starts": sum(e[1] and e[2] is None for e in events),
            "median_latency_s": statistics.median(lat) if lat else None,
            "latency_day_spread_s": max(medians) - min(medians) if len(medians) >= 3 else None,
            "stop_day_spread": _stop_spread(events)}


def _stop_spread(events) -> float | None:
    days: dict = {}
    for t, stop, _l in events:
        days.setdefault(t.date(), []).append(stop)
    shares = [sum(v) / len(v) for v in days.values()]
    return max(shares) - min(shares) if len(shares) >= 3 else None


def soak_pass(before: dict, after: dict) -> bool:
    if before["soak_events"] < 20 or after["soak_events"] < 20 or before["latency_day_spread_s"] is None:
        return False
    if before["median_latency_s"] is None or after["median_latency_s"] is None:
        return False
    slack = max(60.0, before["latency_day_spread_s"])
    share = (after["stop_at_swap"] / after["soak_events"]) - (before["stop_at_swap"] / before["soak_events"])
    return (after["median_latency_s"] <= before["median_latency_s"] + slack
            and after["missed_starts"] <= before["missed_starts"]
            and abs(share) <= (before["stop_day_spread"] or 0.0))


def h1(inst: Install, swaps: list[dict]) -> dict:
    """Fault onsets within 5 minutes after each start, by class, beside its two nulls."""
    fault = inst.series[CONF_HEAT_PUMP_FAULT_ENTITY]
    onsets = [t for t, v in fault.changes() if str(v).strip().lower() not in CLEAR
              and str(fault.at(t - timedelta(seconds=1))).strip().lower() in CLEAR]

    def hits(times, shift=timedelta(0)):
        return sum(any(t + shift <= o < t + shift + H1_WINDOW for o in onsets) for t in times)
    out = {}
    for cls in ("hot_inlet", "other", "none"):
        times = [s["t"] for s in swaps if s["cls"] == cls]
        out[f"h1_{cls}"], out[f"h1_{cls}_shifted"] = hits(times), hits(times, H1_SHIFT)
    h2d = [t for t, v in inst.series[CONF_HEAT_PUMP_MODE_ENTITY].changes()
           if pump_mode.resolve(v) == pump_mode.MODE_DHW and inst.mode(t - timedelta(seconds=1)) == pump_mode.MODE_HEAT]
    out["h1_heat_to_dhw"], out["h1_heat_to_dhw_shifted"] = hits(h2d), hits(h2d, H1_SHIFT)
    cold = [t for t, v in inst.series[CONF_HEAT_PUMP_MODE_ENTITY].changes()
            if pump_mode.resolve(v) == pump_mode.MODE_HEAT and pump_mode.MODE_DHW not in _modes(inst, t - STEP, t)]
    out["h1_null_no_leg"] = hits(cold)
    return out


def counts(swaps) -> dict:
    out = {"swaps": len(swaps)}
    for cls in ("hot_inlet", "other", "both_internal", "none"):
        out[cls] = sum(s["cls"] == cls for s in swaps)
    return out


def leg_r(inst: Install, swaps) -> dict:
    out = {**counts(swaps), **replay(inst, swaps)}
    out["leg_r_pass"] = bool(out["fidelity_ok"] and out["hot_inlet_after"] == 0 and out["i1_violations"] == 0
                             and out["i2_violations"] == 0 and out["replayable"] >= 10)
    return out


def perturb(inst: Install, swaps, n: int, raise_: bool) -> int:
    """hot_inlet after planting ``n`` kicks into ``none`` starts, or lowering ``n`` kicks, less before."""
    pool = [s for s in swaps if s["cls"] == ("none" if raise_ else "hot_inlet")][:n]
    moved = []
    for s in swaps:
        if s in pool:
            write = inst.ceiling if raise_ else inst.ceiling - 5.0
            ret = inst.ceiling - inst.lift / 2 if raise_ else s["ret"]
            s = {**s, "write": write, "ret": ret, "cls": classify(inst, write, ret, s["both"])}
        moved.append(s)
    return counts(moved)["hot_inlet"] - counts(swaps)["hot_inlet"]


# --- the synthetic bundle: one swap per hour, today's writes recorded
def synthetic(days: int, seed: int) -> dict:
    """Per hour a hot-water leg then three heating steps; of every twelve starts
    after the leg, five meet a hot return (the kick), five a cool one, one a
    fault-held ceiling (``other``) and one is Heating + DHW throughout."""
    rng = random.Random(seed)
    ids = {CONF_SPACE_SETPOINT_ENTITY: "number.flow", CONF_HEAT_PUMP_MODE_ENTITY: "select.mode",
           CONF_POWER_ENTITY: "sensor.power", CONF_HEAT_PUMP_FAULT_ENTITY: "binary_sensor.fault",
           CONF_HEAT_PUMP_RETURN_TEMP_ENTITY: "sensor.ret", flow_anchor.SPACE_SIDE_KEYS[0]: "sensor.buffer"}
    cfg = {**ids, CONF_HEAT_PUMP_MIN_POWER: 1.5, CONF_HEAT_PUMP_MAX_POWER: 5.5}
    rows: dict = {v: [] for v in ids.values()}
    cycle = []
    attrs = {"min": 20, "max": 60, "step": 0.5}
    inst = Install({"replay": {"entry": {"data": cfg}, "states": {}}})
    inst.gate, inst.grid = 25.0, 0.5

    def put(key, t, v):
        rows[ids[key]].append([t.isoformat(), str(v), attrs if key == CONF_SPACE_SETPOINT_ENTITY else {}, None])
    put(CONF_HEAT_PUMP_FAULT_ENTITY, T0, "off")
    kinds = ("hot",) * 5 + ("cool",) * 5 + ("other", "both")
    for hour in range(days * 24):
        h = T0 + timedelta(hours=hour)
        kind = kinds[hour % len(kinds)]
        level = rng.choice((2.5, 3.0, 3.5))
        space_c = 29.0 + rng.choice((-1.0, 0.0, 1.0))
        for step in range(4):
            cycle.append({"t": (h + STEP * step).isoformat(), "action_kw": 0.0 if step == 0 else level})
        put(CONF_HEAT_PUMP_MODE_ENTITY, h - timedelta(minutes=20), "Heating")
        put(CONF_POWER_ENTITY, h - timedelta(minutes=20), 2.0)
        put(CONF_HEAT_PUMP_RETURN_TEMP_ENTITY, h - timedelta(minutes=20), space_c)
        put(CONF_HEAT_PUMP_RETURN_TEMP_ENTITY, h - timedelta(minutes=12), space_c)
        put(flow_anchor.SPACE_SIDE_KEYS[0], h, 31.0)
        put(CONF_HEAT_PUMP_MODE_ENTITY, h, "Heating + DHW" if kind == "both" else "DHW (Hot Water)")
        put(CONF_SPACE_SETPOINT_ENTITY, h, 25.0)
        swap = h + STEP + timedelta(seconds=rng.randint(0, 60))
        ret = 54.0 if kind == "hot" else 40.0 if kind == "other" else space_c
        put(CONF_HEAT_PUMP_RETURN_TEMP_ENTITY, h + timedelta(minutes=5), ret)
        if kind != "both":
            put(CONF_HEAT_PUMP_MODE_ENTITY, swap, "Heating")
        write = inst.ceiling if kind == "other" else _write(inst, level, ret)
        put(CONF_SPACE_SETPOINT_ENTITY, swap + timedelta(seconds=5), write)
        stop = swap + timedelta(seconds=rng.randint(20, 150))
        put(CONF_POWER_ENTITY, stop, 0.05)
        put(CONF_POWER_ENTITY, stop + timedelta(seconds=rng.randint(40, 120)), 2.2)
        cool = swap + FEEDBACK_START_HOLD + timedelta(seconds=30)
        put(CONF_HEAT_PUMP_RETURN_TEMP_ENTITY, cool, space_c + 2.0)
        put(CONF_SPACE_SETPOINT_ENTITY, cool + timedelta(seconds=5), _write(inst, level, space_c + 2.0))
        if kind == "other":
            put(CONF_HEAT_PUMP_FAULT_ENTITY, swap + timedelta(minutes=2), "on")
            put(CONF_HEAT_PUMP_FAULT_ENTITY, swap + timedelta(minutes=9), "off")
    return {"schema": "hpo-debug/1", "cycle_rows": cycle,
            "replay": {"format": "hpo-replay/1", "entry": {"data": cfg, "options": {}}, "states": rows}}


def _print(values: dict) -> None:
    for key, value in values.items():
        print(f"RESULT {key}={value}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle")
    ap.add_argument("--soak", nargs=2)
    ap.add_argument("--days", type=int, default=4)
    ap.add_argument("--seed", type=int, default=3881)
    args = ap.parse_args(argv)
    if args.soak:
        before, after = (Install(load(p)) for p in args.soak)
        sb, sa = soak(before, starts(before)), soak(after, starts(after))
        _print({**{f"before_{k}": v for k, v in sb.items()}, **{f"after_{k}": v for k, v in sa.items()},
                "soak_pass": soak_pass(sb, sa)})
        return 0
    inst = Install(load(args.bundle) if args.bundle else synthetic(args.days, args.seed))
    swaps = starts(inst)
    _print(leg_r(inst, swaps))
    _print({"perturb_raise_delta": perturb(inst, swaps, 5, True),
            "perturb_lower_delta": perturb(inst, swaps, 5, False)})
    base = soak(inst, swaps)
    _print({"soak_events": base["soak_events"],
            "soak_delay_moves_median": soak(inst, swaps, delay=3)["median_latency_s"] != base["median_latency_s"],
            "soak_delete_missed_delta": soak(inst, swaps, delete=3)["missed_starts"] - base["missed_starts"],
            "soak_null_pass": soak_pass(base, base) if base["soak_events"] >= 20 else None})
    if args.bundle:
        _print({k: v for k, v in base.items() if k != "soak_events"})
        _print(h1(inst, swaps))
    return 0


if __name__ == "__main__":
    sys.exit(main())
