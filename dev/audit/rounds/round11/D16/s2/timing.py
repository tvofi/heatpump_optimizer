#!/usr/bin/env python3
"""D16.M3 (timing and order) on the reference plant: which plan step's command is in force on the
pump, minute by minute, per actuator, against the step the clock is in.

Metric (one line): stale_share[channel] = minutes, at least GRACE_MIN after a step boundary, whose
in-force value is not the step's own command / minutes graded for that channel; keyed on the value
the entity holds after the production write (the device stub applies each service call), never on
an input attribute.

Command:  PYTHONPATH=tests/hastub ~/venv-ci/bin/python3 dev/audit/rounds/round11/D16/s2/timing.py
          [--perturb P1|null-docstring] [--interval MIN] [--phases 1,6,11,16,21,26] [--json PATH]
Expected (baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, unperturbed, 30-min cycle, six phases):
  RESULT stale_share_supply=0, stale_share_mode=0, stale_share_flow_class=0 (exact);
  RESULT stale_share_mqtt_displace / curve_offset / frequency ~0.33-0.5 (+-0.05);
  --interval 15 --phases 0 (cycle on every boundary, the null arm): every share 0.
  --perturb P1 (pump_arbiter._step_index one step late): supply and mode shares > 0.3.
Machine: box B11 (shared). Thread pin below; no timing number is produced (counts only).

The oracle: the step covering a minute is found by plain arithmetic on the plan's own timestamps
(rig.oracle_index), and its command read by plain indexing of the plan's own series:
supply = heat_pump_on_schedule[k]; mode = Heating where only space is booked, the hot-water mode
where only the tank is, either on a both step (its order is graded apart), anything on idle;
flow class = above the gate (25 C) exactly where power_schedule[k] > 0; mqtt displace and the
heat-curve offset = displace_schedule[k] (the plan's own number); frequency = the value the cycle
wrote for that step kind when it was cut and written inside such a step (a value grade is M2's).
Nothing here imports a step selection from pump_arbiter.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from contextlib import contextmanager
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402
from harness import FakeState  # noqa: E402
from heatpump_optimizer import pump_arbiter  # noqa: E402

GRACE_MIN = 1  # the arbiter's and the supply's tick period
WALK = ["idle", "partial", "full", "partial", "dhw-only", "both", "idle", "partial", "idle", "full",
        "dhw-only", "partial", "both", "min-cold-tank", "idle", "partial", "full", "idle"]
DHW_MODE = "DHW (Hot Water)"
GATE_C = 25.0


def rows_for(kinds, f, P):
    tab = {"idle": (0.0, 0.0), "min-cold-tank": (f, 0.0), "partial": ((f + P) / 2, 0.0), "full": (P, 0.0),
           "dhw-only": (0.0, 2 * f + 0.5), "both": ((f + P) / 2, 2 * f + 0.5)}
    return [tab[k] for k in kinds]


@contextmanager
def perturbed(which):
    """P1: the arbiter's step selection one step late (the one-line edit ``- 1`` -> ``- 2`` in
    ``_step_index``). null-docstring: the docstring of the house-only row edited alone."""
    if which == "P1":
        # Every step lookup the arbiter makes (``_step_index``, ``_planned_room``, ``_share``)
        # goes through its module's ``bisect``; one step late is ``bisect_right(...) - 1`` more.
        import bisect as _bisect
        import types
        real = pump_arbiter.bisect

        def late(a, x, *rest, **kw):
            return max(0, _bisect.bisect_right(a, x, *rest, **kw) - 1)
        pump_arbiter.bisect = types.SimpleNamespace(bisect_right=late, bisect_left=_bisect.bisect_left)
        try:
            yield
        finally:
            pump_arbiter.bisect = real
    elif which == "lead-hold":
        # the one-line edit in ``_lead_mode``: ``hold(coord, now)`` before its ``_write``, so a
        # record the entity no longer reads is dropped and the mode is sent ahead of the switch-on
        real = pump_arbiter._write

        async def _write(coord, inp, slot, value, now, command=None):
            import inspect
            if slot == "mode" and inspect.stack()[1].function == "_lead_mode":
                pump_arbiter.hold(coord, now)
            return await real(coord, inp, slot, value, now, command)
        pump_arbiter._write = _write
        try:
            yield
        finally:
            pump_arbiter._write = real
    elif which == "null-docstring":
        real = pump_arbiter.__doc__
        pump_arbiter.__doc__ = real.replace("space only     Heating, if offered  configured, or",
                                            "space only     Heating, if offered  any, or      ")
        try:
            yield
        finally:
            pump_arbiter.__doc__ = real
    else:
        yield


def oracle(kind_rows, plan, k, channel):
    """The step's own command for ``channel`` from the plan by plain indexing; None = not graded."""
    space, dhw = plan.power_schedule[k], plan.dhw_power_schedule[k]
    if channel == "supply":
        return "on" if plan.heat_pump_on_schedule[k] else "off"
    if channel == "mode":
        if space > 0 and dhw == 0:
            return "Heating"
        if space == 0 and dhw > 0:
            return DHW_MODE
        return None
    if channel == "flow_class":
        return "heat" if space > 0 else "gate"
    if channel == "mqtt_displace":
        return str(int(round(plan.displace_schedule[k])))
    if channel == "curve_offset":
        # the entity arm sends the displace inside the configured band (const default 3 K) on
        # the entity's own 1-K step; the oracle is the plan's number, clamped by that band
        band = float(rig.config().get("heat_curve_offset_band_k", 3.0))
        v = max(-band, min(band, float(int(round(plan.displace_schedule[k])))))
        return str(int(v))
    return None


def walk(phase, interval=30, perturb=None, kinds=WALK, att=None):
    sim = rig.Sim()
    if att is not None:
        att.install(sim.hass)
    c = sim.coord
    f = float(c._thermal_model.params.min_electrical_power)
    P = float(c._thermal_model.params.max_electrical_power)
    plan = rig.plan(rows_for(kinds, f, P))
    n = len(kinds)
    samples = []  # (minute, k, {channel: in-force})
    freq_writes = []
    order = []  # per both step: (k, mode writes in order)
    with perturbed(perturb):
        for m in range(n * 15 + 30):
            t = rig.T0 + timedelta(minutes=m)
            sim.at(t)
            k = rig.oracle_index(plan, t)
            kind = kinds[k] if k is not None else "baseline"
            for e, v in (("sensor.indoor", "20.5"), ("sensor.outdoor", "-2.0"), ("sensor.hp_power", "0.0"),
                         ("sensor.hp_return", "30.0"),
                         ("sensor.tank", "20.0" if kind == "min-cold-tank" else "44.0")):
                st = sim.hass.states.get(e)
                st.state, st.last_updated, st.last_reported = v, t, t
            before = len(sim.dev.log)
            if m >= phase and (m - phase) % interval == 0:
                sim.cycle(plan)
            sim.tick()
            for (wt, dom, svc, data) in sim.dev.log[before:]:
                if dom == "number" and data.get("entity_id") == rig.ENT["freq"]:
                    freq_writes.append((m, k, kind, data["value"]))
            flow = float(sim.value("flow"))
            samples.append((m, k, kind, {
                "supply": sim.value("switch"), "mode": sim.value("mode"),
                "flow_class": "heat" if flow > GATE_C else "gate",
                "mqtt_displace": sim.mqtt_payload(), "curve_offset": sim.value("curve"),
                "frequency": sim.value("freq"), "space_pump": sim.value("space_pump"),
            }))
    # The frequency each kind is written with when its cut and its write share the step.
    by_kind = defaultdict(Counter)
    for (m, k, kind, v) in freq_writes:
        by_kind[kind][str(v)] += 1
    freq_for = {kind: cnt.most_common(1)[0][0] for kind, cnt in by_kind.items()}
    graded = Counter()
    stale = Counter()
    stale_cells = defaultdict(Counter)
    for (m, k, kind, vals) in samples:
        if k is None or m - k * 15 < GRACE_MIN or m <= phase:
            continue  # before the first cycle no plan has been adopted
        for ch in ("supply", "mode", "flow_class", "mqtt_displace", "curve_offset", "frequency", "space_pump"):
            if ch == "flow_class" and (vals["supply"] != "on" or kind == "both"):
                # a stopped pump runs nothing whatever its set-point; a both step's legs are
                # graded by their order below
                continue
            if ch == "frequency":
                want = freq_for.get(kind) if plan.heat_pump_on_schedule[k] else None
            elif ch == "space_pump":
                want = "on" if plan.power_schedule[k] > 0 else None
            else:
                want = oracle(None, plan, k, ch)
            if want is None:
                continue
            graded[ch] += 1
            if vals[ch] != want:
                stale[ch] += 1
                stale_cells[ch][kind] += 1
    # Order on a both step and on idle -> running steps: the mode lands before the switch-on.
    log = sim.dev.log
    mode_after_on = 0
    on_writes = 0
    for i, (wt, dom, svc, data) in enumerate(log):
        if dom == "switch" and svc == "turn_on" and data.get("entity_id") == rig.ENT["switch"]:
            on_writes += 1
            k = rig.oracle_index(plan, wt)
            if k is None:
                continue
            want = oracle(None, plan, k, "mode")
            # the mode in force at the switch-on, i.e. after every write before it
            if want is not None and sim_mode_at(log, i) != want:
                mode_after_on += 1
    both_order = []
    for k, kind in enumerate(kinds):
        if kind != "both":
            continue
        t0, t1 = plan.timestamps[k], plan.timestamps[k] + rig.STEP
        seq = [d["option"] for (wt, dom, svc, d) in log if dom == "select" and t0 <= wt < t1]
        both_order.append(seq)
    return {"graded": dict(graded), "stale": dict(stale),
            "stale_by_kind": {ch: dict(v) for ch, v in stale_cells.items()},
            "mode_not_led_at_switch_on": mode_after_on, "switch_on_writes": on_writes,
            "both_mode_sequences": both_order, "freq_for": freq_for}


def sim_mode_at(log, i):
    mode = "Heating + DHW"
    for (wt, dom, svc, data) in log[:i]:
        if dom == "select" and data.get("entity_id") == rig.ENT["mode"]:
            mode = data["option"]
    return mode


# ---------------------------------------------------------------------------
# The owed cells
# ---------------------------------------------------------------------------

def cell_3478(perturb=None):
    """``partial`` with the cycle held across the end of step k, step k-1 booked idle: the cycle is
    cut at minute 10 of step k (partial) and its writes land at minute 2 of step k+1 (full).
    Graded: the supply, the mode and the frequency in force from that write to the next boundary."""
    kinds = ["idle", "idle", "partial", "full", "full", "idle"]
    sim = rig.Sim()
    c = sim.coord
    f = float(c._thermal_model.params.min_electrical_power)
    P = float(c._thermal_model.params.max_electrical_power)
    plan = rig.plan(rows_for(kinds, f, P))
    out = {}
    in_k = []
    with perturbed(perturb):
        for m in range(0, 40):
            sim.at(rig.T0 + timedelta(minutes=m))
            _fresh(sim, rig.T0 + timedelta(minutes=m))
            if m == 1:
                sim.cycle(plan)
            sim.tick()
            if m >= 31:  # step k = 2 (partial), its boundary minute excluded
                in_k.append((sim.value("switch"), sim.value("mode")))
        # cut at minute 10 of step 2, the tail lands 7 minutes later, inside step 3
        cut = rig.T0 + timedelta(minutes=40)
        sim.at(cut)
        _fresh(sim, cut)
        sim.adopt(plan)
        sim.at(rig.T0 + timedelta(minutes=47))
        _fresh(sim, rig.T0 + timedelta(minutes=47))
        n0 = len(sim.dev.log)
        sim.run(sim._cycle_writes())
        landed = sim.dev.log[n0:]
        k = rig.oracle_index(plan, rig.T0 + timedelta(minutes=47))
        for m in range(41, 60):
            if m == 47:
                continue
            sim.at(rig.T0 + timedelta(minutes=m))
            _fresh(sim, rig.T0 + timedelta(minutes=m))
            sim.tick()
            if m < 45:
                in_k.append((sim.value("switch"), sim.value("mode")))
        freq_full = None
        # the frequency a cycle cut inside a full step writes (null arm of this cell)
        sim2 = rig.Sim()
        sim2.at(rig.T0 + timedelta(minutes=50))
        _fresh(sim2, rig.T0 + timedelta(minutes=50))
        sim2.cycle(plan)
        freq_full = sim2.value("freq")
    out = {"k_written": k, "kind_written": kinds[k],
           "step_k_minutes_not_partial_row": sum(1 for sw, md in in_k if (sw, md) != ("on", "Heating")),
           "step_k_minutes": len(in_k),
           "landed": [(d, s, dd.get("value", dd.get("option", dd.get("payload")))) for (_t, d, s, dd) in landed],
           "supply_in_force": sim.value("switch"), "mode_in_force": sim.value("mode"),
           "freq_in_force": sim.value("freq"), "freq_a_full_cut_writes": freq_full,
           "mqtt_in_force": sim.mqtt_payload(), "mqtt_full_step": str(int(plan.displace_schedule[k])),
           "mqtt_cut_step": str(int(plan.displace_schedule[k - 1]))}
    out["late_channels"] = [ch for ch, a, b in (("frequency", out["freq_in_force"], freq_full),
                                                 ("mqtt_displace", out["mqtt_in_force"], out["mqtt_full_step"]),
                                                 ("supply", out["supply_in_force"], "on"),
                                                 ("mode", out["mode_in_force"], "Heating")) if a != b]
    return out


def _fresh(sim, t, tank="44.0", power="0.0"):
    for e, v in (("sensor.indoor", "20.5"), ("sensor.outdoor", "-2.0"), ("sensor.hp_power", power),
                 ("sensor.hp_return", "30.0"), ("sensor.tank", tank)):
        st = sim.hass.states.get(e)
        st.state, st.last_updated, st.last_reported = v, t, t


def cell_3530(perturb=None):
    """``partial`` entered from ``idle`` by the step tick: the mode lands before the switch-on."""
    kinds = ["idle", "idle", "partial", "partial"]
    sim = rig.Sim()
    c = sim.coord
    f = float(c._thermal_model.params.min_electrical_power)
    P = float(c._thermal_model.params.max_electrical_power)
    plan = rig.plan(rows_for(kinds, f, P))
    sim.at(rig.T0 + timedelta(minutes=3))
    _fresh(sim, sim.now)
    # the pump was last left in hot water by an earlier plan
    sim.hass.states.get(rig.ENT["mode"]).state = DHW_MODE
    with perturbed(perturb):
        sim.cycle(plan)
        for m in range(4, 40):
            sim.at(rig.T0 + timedelta(minutes=m))
            _fresh(sim, sim.now)
            sim.tick()
    log = sim.dev.log
    on_idx = [i for i, (_t, d, s, dd) in enumerate(log) if d == "switch" and s == "turn_on"]
    first_on = on_idx[0] if on_idx else None
    mode_then = sim_mode_at(log, first_on) if first_on is not None else None
    on_at = log[first_on][0] if first_on is not None else None
    return {"first_switch_on_minute": None if on_at is None else int((on_at - rig.T0).total_seconds() // 60),
            "mode_at_switch_on": mode_then, "mode_led": mode_then == "Heating",
            "booked_step_start_minute": 30}


def cell_3530_record(perturb=None, external=True):
    """``partial`` entered from ``idle`` after the mode changed while the switch read off.

    partial (the arbiter writes Heating and records it), idle (the switch goes off), the mode
    select moved to the hot-water mode at minute 5 of the idle step (the pump's own reset, or a
    person), then partial again. Graded: the mode in force at the switch-on. ``external=False``
    is the null arm (no change while off)."""
    kinds = ["idle", "partial", "idle", "partial", "partial"]
    sim = rig.Sim()
    c = sim.coord
    f = float(c._thermal_model.params.min_electrical_power)
    P = float(c._thermal_model.params.max_electrical_power)
    plan = rig.plan(rows_for(kinds, f, P))
    with perturbed(perturb):
        for m in range(0, 60):
            t = rig.T0 + timedelta(minutes=m)
            sim.at(t)
            _fresh(sim, t)
            if m == 2:
                sim.cycle(plan)
            if external and m == 35:
                st = sim.hass.states.get(rig.ENT["mode"])
                st.state, st.last_changed, st.last_updated = DHW_MODE, t, t
            sim.tick()
    log = sim.dev.log
    ons = [i for i, (wt, d, s_, dd) in enumerate(log)
           if d == "switch" and s_ == "turn_on" and wt >= rig.T0 + timedelta(minutes=45)]
    mode_then = None
    if ons:
        mode_then = DHW_MODE if external else "Heating"
        for (wt, d, s_, dd) in log[:ons[0]]:
            if d == "select" and wt >= rig.T0 + timedelta(minutes=35):
                mode_then = dd["option"]
    fixed = [((wt - rig.T0).total_seconds() / 60, dd["option"]) for (wt, d, s_, dd) in log
             if d == "select" and wt >= rig.T0 + timedelta(minutes=35)]
    return {"switch_on_minute": None if not ons else (log[ons[0]][0] - rig.T0).total_seconds() / 60,
            "mode_at_switch_on": mode_then, "mode_led": mode_then == "Heating", "mode_writes_after": fixed}


def cell_3512(perturb=None):
    """``idle`` entered by a re-solve 3 minutes after ``partial`` switched the supply on; then a
    re-solve 2 minutes after the off books ``partial`` again. Graded: run and pause lengths against
    runs.MIN_RUN / MIN_PAUSE (10 min each), read from the switch's own transitions."""
    from heatpump_optimizer.runs import MIN_PAUSE, MIN_RUN
    sim = rig.Sim()
    c = sim.coord
    f = float(c._thermal_model.params.min_electrical_power)
    P = float(c._thermal_model.params.max_electrical_power)
    first = rig.plan(rows_for(["idle", "idle", "partial", "partial", "partial", "partial"], f, P))
    idle = rig.plan(rows_for(["idle", "idle", "idle", "idle", "idle", "idle"], f, P))
    again = rig.plan(rows_for(["idle", "idle", "partial", "partial", "partial", "partial"], f, P))
    with perturbed(perturb):
        for m in range(0, 80):
            t = rig.T0 + timedelta(minutes=m)
            sim.at(t)
            _fresh(sim, t)
            if m == 2:
                sim.cycle(first)  # step 2 (minute 30) switches the supply on
            if m == 33:  # the re-solve 3 minutes after that switch-on books step 2 idle
                sim.cycle(idle)
            if m == 42:  # 2 minutes after the held off lands (minute 40) it books partial again
                sim.cycle(again)
            sim.tick()
    edges = [((wt - rig.T0).total_seconds() / 60, s) for (wt, d, s, dd) in sim.dev.log
             if d == "switch" and dd.get("entity_id") == rig.ENT["switch"]]
    # collapse to transitions
    trans, last = [], "off"
    for mnt, s in edges:
        v = "on" if s == "turn_on" else "off"
        if v != last:
            trans.append((mnt, v))
            last = v
    runs = [(b[0] - a[0]) for a, b in zip(trans, trans[1:]) if a[1] == "on"]
    pauses = [(b[0] - a[0]) for a, b in zip(trans, trans[1:]) if a[1] == "off"]
    return {"transitions": trans, "runs_min": runs, "pauses_min": pauses,
            "min_run": MIN_RUN.total_seconds() / 60, "min_pause": MIN_PAUSE.total_seconds() / 60,
            "short_runs": sum(1 for r in runs if r < MIN_RUN.total_seconds() / 60),
            "short_pauses": sum(1 for p in pauses if p < MIN_PAUSE.total_seconds() / 60)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", default=None)
    ap.add_argument("--interval", type=int, default=30)
    ap.add_argument("--phases", default="1,6,11,16,21,26")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    c0 = time.process_time()
    t0 = time.thread_time()
    phases = [int(x) for x in a.phases.split(",")]
    per = {}
    for ph in phases:
        per[ph] = walk(ph, a.interval, a.perturb)
    chans = ("supply", "mode", "flow_class", "mqtt_displace", "curve_offset", "frequency", "space_pump")
    for ch in chans:
        shares = [per[ph]["stale"].get(ch, 0) / max(1, per[ph]["graded"].get(ch, 0)) for ph in phases]
        g = sum(per[ph]["graded"].get(ch, 0) for ph in phases)
        s = sum(per[ph]["stale"].get(ch, 0) for ph in phases)
        print(f"RESULT stale_share_{ch}={s / max(1, g):.4f} ratio (stale={s} graded={g})")
        if len(phases) >= 5:
            lo, hi = min(shares), max(shares)
            drop = sorted(shares)[1:] if shares else []
            print(f"RESULT loo_{ch}_min={lo:.4f} loo_{ch}_max={hi:.4f} "
                  f"loo_{ch}_drop_most_favourable={sum(drop) / max(1, len(drop)):.4f}")
    for ph in phases:
        print(f"phase {ph}: stale_by_kind={json.dumps(per[ph]['stale_by_kind'], sort_keys=True)}")
    led = sum(per[ph]["mode_not_led_at_switch_on"] for ph in phases)
    ons = sum(per[ph]["switch_on_writes"] for ph in phases)
    print(f"RESULT switch_on_with_wrong_mode={led} count (of {ons} switch-on writes)")
    print(f"both-step mode sequences (phase {phases[0]}): {per[phases[0]]['both_mode_sequences']}")
    c78 = cell_3478(a.perturb)
    print(f"cell 3478: {json.dumps(c78)}")
    print(f"RESULT cell3478_step_k_off_row={c78['step_k_minutes_not_partial_row']} minutes "
          f"(of {c78['step_k_minutes']})")
    print(f"RESULT cell3478_late_channels={len(c78['late_channels'])} count {c78['late_channels']}")
    c30 = cell_3530(a.perturb)
    print(f"cell 3530: {json.dumps(c30)}")
    print(f"RESULT cell3530_mode_led={int(c30['mode_led'])} bool")
    cr = cell_3530_record(a.perturb)
    crn = cell_3530_record(a.perturb, external=False)
    print(f"cell 3530 (mode moved while off): {json.dumps(cr)}; null arm: {json.dumps(crn)}")
    print(f"RESULT cell3530_record_wrong_mode_at_on={int(not cr['mode_led'])} bool (null arm "
          f"{int(not crn['mode_led'])})")
    c12 = cell_3512(a.perturb)
    print(f"cell 3512: {json.dumps(c12)}")
    print(f"RESULT cell3512_short_runs={c12['short_runs']} count")
    print(f"RESULT cell3512_short_pauses={c12['short_pauses']} count")
    if a.json:
        with open(a.json, "w") as fh:
            json.dump({"per_phase": per, "3478": c78, "3530": c30, "3512": c12}, fh, default=str)
    pc, tc = time.process_time() - c0, time.thread_time() - t0
    print(f"RESULT thread_factor={pc / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(l.split()[1]) for l in open("/proc/vmstat") if l.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
