#!/usr/bin/env python3
"""D16.M3 and D16.M4 over every cell ``tools/audit/enumerate.py d16-writes --cells`` prints.

One scenario per state on the reference plant (rig.py), with the pump model of effect.py on the
null plant (k_lift 5 K/kW, start hysteresis 2 K), the cycle every 30 min, the arbiter's and the
supply's one-minute ticks. Every service call and every log_held is attributed to the enumerator
site it came from (rig.Attribution, by the caller's file and line), so a cell's verdict rests on
an executed count: the site's calls/holds in that state's run, and the state's graded numbers.

Metric (one line): per state, m3_stale = minutes (>= 1 min after a step boundary, after the first
cycle) whose in-force supply/mode/flow class is not the step's own command read by plain indexing
of the plan; m4_error = (measured kWh - booked kWh) / booked kWh over the state's steps, measured
being the pump model's draw under what the production writes left on the entities.

Command:  PYTHONPATH=tests/hastub ~/venv-ci/bin/python3 dev/audit/rounds/round11/D16/s2/cells.py
          [--perturb P1|null-docstring] [--cells-out PATH]
Expected (baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692): RESULT cells_universe=532,
cells_examined_m3=cells_examined_m4=<universe less the upgrade cells>; per-state numbers in
REPORT.md. Machine: box B11 (shared); counts only.
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
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import effect  # noqa: E402
import rig  # noqa: E402
import timing  # noqa: E402
from heatpump_optimizer import boost, pump_arbiter  # noqa: E402

DHW_MODE = timing.DHW_MODE

#: Hold sites whose latch gates no actuator write, and why (D16.M1's rule: rowed, never dropped).
NO_WRITE = {
    "_await_off_loop": "the solve/worker fence: it gates no service call, a failed solve leaves the last plan",
    "_await_optimize": "the solve fence: no service call behind it",
    "HeatPumpOptimizerCoordinator.async_run_optimization": "the solve-failure latch cleared on success",
    "_note_solve_failure": "the solve-failure latch",
    "HeatPumpOptimizerCoordinator._solar_location": "the solar fetch",
    "HeatPumpOptimizerCoordinator._fetch_solar_forecast": "the solar fetch",
    "HeatPumpOptimizerCoordinator._price_series": "the price fetch",
    "HeatPumpOptimizerCoordinator._weather_series": "the weather fetch",
    "InputReader._age_gate": "an input-staleness read latch: it gates a reading, the write path reads it",
}

#: Which channel a write site's command is graded on.
SITE_CHANNEL = {
    "_command_frequency": "frequency", "_disinfection_switch": "disinfection switch",
    "HeatPumpOptimizerCoordinator._async_set_pump": "circulation pump",
    "publish_ecl110_topics": "ECL110 displace", "write_setpoint": "set-points (flow, tank, curve, valve)",
    "_write": "mode/set-points/silent", "switch_supply": "supply",
    "HeatPumpOptimizerCoordinator._command_valve_target": "valve target",
    "write_displace": "heat-curve offset", "_send": "heat-curve offset", "write_persistent": "heat-curve (persistent)",
    "_write_persistent_target": "heat-curve (persistent)", "async_arm": "off restore", "_restore_baseline": "off restore",
    "async_restore": "off restore", "_space_target": "space set-point",
}


#: The second configuration arm: the frequency control stage and the persistent heat-curve kind,
#: so the sites only those reach are driven in every state too.
ARM = {"A": {}, "B": {"compressor_freq_entity": rig.ENT["freq"], "freq_control_mode": "control",
                      "heat_curve_target_kind": "persistent"}}
CURRENT_ARM = ["A"]


class Run:
    """One state's scenario: the sim, the pump model, attribution and the graded numbers."""

    def __init__(self, state, kinds, k_state, cfg_extra=None, tank="44.0", attribute=True):
        self.state = state
        extra = {"compressor_freq_entity": None, "freq_control_mode": None,
                 "ecl110_command_topic": "ecl110/command",
                 "mixing_valve_mode": "smart_write", "mixing_valve_write_entity": "number.valve",
                 "dhw_disinfection_switch_entity": "switch.hp_disinfect", "dhw_disinfection_mode": "control",
                 "dhw_legionella_enabled": True}
        extra.update(ARM[CURRENT_ARM[0]])
        extra.update(cfg_extra or {})
        st = rig.states(rig.T0)
        from harness import FakeState
        st["number.valve"] = FakeState("30", attributes={"min": 10, "max": 60, "step": 1},
                                       last_updated=rig.T0 - timedelta(hours=2))
        st["switch.hp_disinfect"] = FakeState("off", last_updated=rig.T0 - timedelta(hours=2))
        self.cfg = rig.config(**extra)
        self.sim = rig.Sim(cfg=self.cfg, st=st, seed_freq=True)
        self.att = rig.Attribution() if attribute else None
        if self.att is not None:
            self.att.install(self.sim.hass)
        c = self.sim.coord
        self.f = float(c._thermal_model.params.min_electrical_power)
        self.P = float(c._thermal_model.params.max_electrical_power)
        self.kinds = kinds
        self.plan = rig.plan(timing.rows_for(kinds, self.f, self.P))
        self.k_state = set(k_state)
        self.pump = effect.Pump(self.f, self.P, 5.0, 2.0, tank=float(tank))
        self.kw = defaultdict(list)
        self.samples = []
        self.tank = tank

    def minute(self, m, cycle=True, phase=1, plan=None):
        sim = self.sim
        t = rig.T0 + timedelta(minutes=m)
        sim.at(t)
        k = rig.oracle_index(self.plan, t)
        kw = self.pump.minute(sim.value("switch"), sim.value("mode"), _num(sim.value("flow")),
                              _num(sim.value("dhw")))
        self.kw[k].append(kw)
        timing._fresh(sim, t, tank=f"{self.pump.tank:.2f}", power=f"{kw:.3f}")
        if cycle and m >= phase and (m - phase) % 30 == 0:
            sim.cycle(plan or self.plan)
        sim.tick()
        self.samples.append((m, k, sim.value("switch"), sim.value("mode"), _num(sim.value("flow")),
                             sim.value("dhw")))

    def m3_stale(self, first_cycle=1, rows=True):
        """Minutes of the state's steps whose in-force row is not the step's own (plain indexing)."""
        bad = graded = 0
        for (m, k, sw, md, flow, dhw) in self.samples:
            if k is None or k not in self.k_state or m - k * 15 < timing.GRACE_MIN or m <= first_cycle:
                continue
            if self.state == "unavailable" and flow is None:
                continue  # the written entity reads unavailable: graded by no write recorded
            space, dhw_kw = self.plan.power_schedule[k], self.plan.dhw_power_schedule[k]
            want_sw = "on" if self.plan.heat_pump_on_schedule[k] else "off"
            ok = sw == want_sw
            if rows and space > 0 and dhw_kw == 0:
                ok = ok and md == "Heating" and flow is not None and flow > timing.GATE_C
            if rows and space == 0 and dhw_kw > 0:
                ok = ok and md == DHW_MODE
            graded += 1
            bad += not ok
        return bad, graded

    def m4(self):
        ks = sorted(k for k in self.k_state if k in self.kw)
        booked = sum((self.plan.power_schedule[k] + self.plan.dhw_power_schedule[k]) * 0.25 for k in ks)
        measured = sum(sum(self.kw[k]) / 60 for k in ks)
        return booked, measured


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def scenario(state, perturb=None):
    """Run ``state``'s scenario; returns (Run, extra numbers)."""
    base = {"idle": (["partial", "partial", "idle", "idle", "partial", "idle"], [2, 3]),
            "min-cold-tank": (["idle", "idle", "min-cold-tank", "min-cold-tank", "idle", "idle"], [2, 3]),
            "partial": (["idle", "full", "partial", "partial", "idle", "idle"], [2, 3]),
            "full": (["idle", "partial", "full", "full", "idle", "idle"], [2, 3]),
            "dhw-only": (["idle", "partial", "dhw-only", "dhw-only", "idle", "idle"], [2, 3]),
            "both": (["idle", "partial", "both", "both", "idle", "idle"], [2, 3])}
    extra = {}
    with timing.perturbed(perturb):
        if state in base:
            kinds, ks = base[state]
            r = Run(state, kinds, ks, tank="20.0" if state == "min-cold-tank" else "44.0")
            for m in range(len(kinds) * 15):
                r.minute(m)
            if state == "both":
                seqs = []
                for k in ks:
                    t0, t1 = r.plan.timestamps[k], r.plan.timestamps[k] + rig.STEP
                    seqs.append([d["option"] for (wt, dom, s, d) in r.sim.dev.log if dom == "select" and t0 <= wt < t1])
                extra["mode_sequences"] = seqs
                extra["dhw_first"] = sum(1 for s in seqs if s and s[0] == DHW_MODE)
            return r, extra
        if state == "boost-partial":
            kinds = ["idle", "partial", "partial", "partial", "partial", "idle"]
            r = Run(state, kinds, [2, 3])
            for m in range(len(kinds) * 15):
                if m == 30:
                    boost.held_for(r.sim.coord).until[boost.CHANNEL_SPACE] = rig.T0 + timedelta(minutes=60)
                    boost.held_for(r.sim.coord).space_since = rig.T0 + timedelta(minutes=30)
                r.minute(m)
            top = max(v for v in (_num(s[4]) for s in r.samples) if v is not None)
            flows = [s[4] for s in r.samples if 31 <= s[0] < 60]
            extra["boost_flow_minutes_below_top"] = sum(1 for v in flows if v is None or v < top)
            extra["boost_top_seen"] = top
            return r, extra
        if state == "disinfection":
            # partial with the cycle held on: the plan books the anti-legionella cycle on steps 2-3
            # (dhw_reasons, the reason the action carries), the house partial throughout
            kinds = ["idle", "partial", "partial", "partial", "idle", "idle"]
            r = Run(state, kinds, [2, 3])
            reasons = [None, None, "legionella", "legionella", None, None]
            r.plan = rig.plan(timing.rows_for(kinds, r.f, r.P), dhw_reasons=reasons)
            for m in range(len(kinds) * 15):
                r.minute(m)
            target = float(r.sim.coord._ctx._thermal_params.dhw_legionella_temp)
            win = [s for s in r.samples if 31 <= s[0] < 60]
            extra["legionella_temp"] = target
            extra["dhw_minutes_below_target"] = sum(1 for s in win if _num(s[5]) is None or _num(s[5]) < target - 0.5)
            sw = [((wt - rig.T0).total_seconds() / 60, s_) for (wt, d, s_, dd) in r.sim.dev.log
                  if dd.get("entity_id") == "switch.hp_disinfect"]
            extra["disinfection_switch_writes"] = sw
            on_minutes = set()
            state_ = "off"
            idx = 0
            for m in range(len(kinds) * 15):
                while idx < len(sw) and sw[idx][0] <= m:
                    state_ = "on" if sw[idx][1] == "turn_on" else "off"
                    idx += 1
                if state_ == "on":
                    on_minutes.add(m)
            booked = {m for m in range(30, 60)}
            extra["switch_on_minutes_in_booked_window"] = len(on_minutes & booked)
            extra["switch_on_minutes_outside_window"] = len(on_minutes - booked)
            return r, extra
        if state == "baseline":
            kinds = ["partial", "partial", "partial"]
            r = Run(state, kinds, [])
            for m in range(0, 90):
                r.minute(m)
            tail = [s for s in r.samples if s[0] >= 47]
            extra["baseline_minutes_not_hdhw"] = sum(1 for s in tail if s[3] != "Heating + DHW")
            extra["baseline_minutes_dhw_not_configured"] = sum(1 for s in tail if _num(s[5]) != 50.0)
            extra["baseline_minutes_supply_off"] = sum(1 for s in tail if s[2] != "on")
            extra["baseline_first_hdhw_minute"] = next((s[0] for s in tail if s[3] == "Heating + DHW"), None)
            return r, extra
        if state == "upgrade":
            return upgrade(perturb)
        if state == "restart":
            kinds = ["idle", "partial", "partial", "partial", "partial", "idle"]
            r = Run(state, kinds, [2, 3, 4])
            for m in range(0, 35):
                r.minute(m)
            # the reload: unload (shutdown), then a new coordinator on the same entry, store and
            # state machine, whose first solve lands one minute later (the background first solve)
            r.sim.run(r.sim.coord.async_shutdown())
            old_log = len(r.sim.dev.log)
            sim2 = rig.Sim(hass=r.sim.hass, entry=r.sim.entry)
            sim2.coord._freq_map = r.sim.coord._freq_map
            r.sim = sim2
            for m in range(35, len(kinds) * 15):
                r.minute(m, cycle=False)
                if m == 36:
                    r.sim.cycle(r.plan)
            extra["reload_writes"] = [(round((wt - rig.T0).total_seconds() / 60, 1), d, s,
                                       dd.get("option", dd.get("value"))) for (wt, d, s, dd) in r.sim.dev.log[old_log:old_log + 12]]
            return r, extra
        if state == "unavailable":
            kinds = ["idle", "partial", "partial", "partial", "idle", "idle"]
            r = Run(state, kinds, [2, 3])
            held_vals = {}
            for m in range(len(kinds) * 15):
                st = r.sim.hass.states.get(rig.ENT["flow"])
                if m == 33:
                    held_vals["before"] = st.state
                    st.state = "unavailable"
                if m == 39:
                    st.state = held_vals["before"]
                r.minute(m)
                if 33 <= m < 39:
                    rec = pump_arbiter.state_for(r.sim.coord).written.get("space_setpoint")
                    if rec is not None and rec[1] >= rig.T0 + timedelta(minutes=33):
                        extra["write_recorded_while_unavailable"] = extra.get("write_recorded_while_unavailable", 0) + 1
            extra.setdefault("write_recorded_while_unavailable", 0)
            extra["calls_to_flow_while_unavailable"] = sum(
                1 for (wt, d, s, dd) in r.sim.dev.log if dd.get("entity_id") == rig.ENT["flow"]
                and rig.T0 + timedelta(minutes=33) <= wt < rig.T0 + timedelta(minutes=39))
            return r, extra
        if state in ("observe", "off"):
            kinds = ["idle", "partial", "partial", "partial", "idle", "idle"]
            r = Run(state, kinds, [2, 3], cfg_extra={"pump_duty_mode": state})
            for m in range(len(kinds) * 15):
                r.minute(m)
            arb = [x for x in r.sim.dev.log if x[1] in ("select",) or x[3].get("entity_id") in
                   (rig.ENT["dhw"], rig.ENT["flow"])]
            extra["arbiter_writes"] = len(arb)
            return r, extra
    raise ValueError(state)


UPGRADE_KINDS = ["idle", "partial", "partial", "partial", "partial", "idle"]


def upgrade_writer(out_path):
    """Run under the previous tag's tree (D16_ROOT): partial for 35 minutes, then unload; dump
    the store and the entity states it left behind."""
    from homeassistant.helpers import storage
    r = Run("upgrade", UPGRADE_KINDS, [2, 3, 4], attribute=False)
    for m in range(0, 35):
        r.minute(m)
    r.sim.run(r.sim.coord.async_shutdown())
    st = {e: {"state": v.state, "attributes": v.attributes,
              "last_changed": v.last_changed.isoformat() if v.last_changed else None}
          for e, v in r.sim.hass.states._states.items()}
    with open(out_path, "w") as fh:
        json.dump({"disk": storage._DISK, "versions": storage._VERSIONS, "states": st,
                   "entry_id": r.sim.entry.entry_id, "cfg": r.cfg}, fh, default=str)


def upgrade(perturb=None):
    """``partial`` after a reload onto the store the previous tag (``git describe`` of VERSION's
    predecessor, v10.0.1 at this baseline) wrote mid-step."""
    import subprocess
    import tempfile
    from datetime import datetime
    from harness import FakeEntry, FakeHass, FakeState
    from homeassistant.helpers import storage
    tag = os.environ.get("D16_PREV_TAG", "v10.0.1")
    tmp = tempfile.mkdtemp(prefix="d16s2-upgrade-")
    old = os.path.join(tmp, "old")
    os.makedirs(old)
    arch = subprocess.run(["git", "-C", rig._ROOT, "archive", tag, "custom_components", "tests"],
                          capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", old], input=arch, check=True)
    dump = os.path.join(tmp, "store.json")
    env = dict(os.environ, D16_ROOT=old, PYTHONPATH=os.path.join(old, "tests", "hastub"),
               HPO_PLANDATA=os.path.join(tmp, "plandata"))
    subprocess.run([sys.executable, os.path.abspath(__file__), "--upgrade-writer", dump], env=env, check=True,
                   capture_output=True)
    with open(dump) as fh:
        d = json.load(fh)
    storage._DISK.update(d["disk"])
    storage._VERSIONS.update({k: int(v) for k, v in d["versions"].items()})
    t35 = rig.T0 + timedelta(minutes=35)
    states = {e: FakeState(v["state"], attributes=v["attributes"],
                           last_updated=datetime.fromisoformat(v["last_changed"]) if v["last_changed"] else t35)
              for e, v in d["states"].items()}
    r = Run("upgrade", UPGRADE_KINDS, [2, 3, 4])
    hass = FakeHass(states)
    hass._d16_device = rig.Device(hass)
    r.att.install(hass)
    sim2 = rig.Sim(hass=hass, entry=FakeEntry(data=d["cfg"], entry_id=d["entry_id"]), now=t35)
    r.sim = sim2
    r.samples = []
    n0 = len(hass._d16_device.log)
    with timing.perturbed(perturb):
        for m in range(35, len(UPGRADE_KINDS) * 15):
            r.minute(m, cycle=False)
            if m == 36:
                r.sim.cycle(r.plan)
    extra = {"prev_tag": tag, "writes_after_upgrade": [
        (round((wt - rig.T0).total_seconds() / 60, 1), dd.get("entity_id"), s_, dd.get("option", dd.get("value")))
        for (wt, dm, s_, dd) in hass._d16_device.log[n0:n0 + 10]]}
    return r, extra


def site_kind(site):
    parts = site.split()
    return parts[0], parts[1], parts[2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", default=None)
    ap.add_argument("--cells-out", default=None)
    ap.add_argument("--upgrade-writer", default=None)
    a = ap.parse_args()
    if a.upgrade_writer:
        upgrade_writer(a.upgrade_writer)
        return
    c0, t0 = time.process_time(), time.thread_time()
    cells = rig.enumerator_cells()
    states = sorted({c.split(" | ")[1] for c in cells})
    runs = {}
    for arm in ("B", "A"):  # A last: its numbers are the graded ones, B adds its sites' counts
        CURRENT_ARM[0] = arm
        for s in states:
            r, extra = scenario(s, a.perturb)
            bad, graded = r.m3_stale(rows=s not in ("observe", "off", "baseline"))
            booked, measured = r.m4()
            prev = runs.get(s)
            if prev is not None:
                r.att.calls.update(prev["r"].att.calls)
                r.att.holds.update(prev["r"].att.holds)
                r.att.holds_active.update(prev["r"].att.holds_active)
                r.att.unmatched.update(prev["r"].att.unmatched)
            runs[s] = {"r": r, "extra": extra, "m3_bad": bad + (prev["m3_bad"] if prev else 0),
                       "m3_graded": graded + (prev["m3_graded"] if prev else 0),
                       "m4_booked_kwh": round(booked, 3), "m4_measured_kwh": round(measured, 3),
                       "starts": r.pump.starts + r.pump.dhw_starts}
            print(f"arm {arm} state {s}: m3_stale={bad}/{graded} m4 booked={booked:.3f} kWh measured={measured:.3f} "
                  f"kWh starts={r.pump.starts}+{r.pump.dhw_starts} extra={json.dumps(extra, default=str)[:500]}")
    lines = []
    ex3 = ex4 = 0
    nr = []
    for cell in cells:
        site, state = cell.split(" | ")
        kind, loc, sym = site_kind(site)
        if state not in runs:
            nr.append(cell)
            lines.append(f"{cell} || M3: not_reached | M4: not_reached")
            continue
        run = runs[state]
        calls = run["r"].att.calls.get(site, 0)
        holds = run["r"].att.holds.get(site, 0)
        active = run["r"].att.holds_active.get(site, 0)
        if kind == "hold" and sym in NO_WRITE:
            v3 = v4 = f"gates no write ({NO_WRITE[sym]}); holds={holds} active={active}"
        elif kind == "hold":
            v3 = (f"gates {SITE_CHANNEL.get(sym, sym)}; holds={holds} active={active}; "
                  f"state m3_stale={run['m3_bad']}/{run['m3_graded']}")
            v4 = (f"gates {SITE_CHANNEL.get(sym, sym)}; holds={holds} active={active}; "
                  f"state booked={run['m4_booked_kwh']} measured={run['m4_measured_kwh']} kWh")
        else:
            v3 = (f"{SITE_CHANNEL.get(sym, sym)}: calls={calls}; state m3_stale={run['m3_bad']}/{run['m3_graded']}"
                  + ("; cycle-cadence channel, see timing.py" if sym in (
                      "_command_frequency", "publish_ecl110_topics", "_disinfection_switch") else ""))
            v4 = (f"{SITE_CHANNEL.get(sym, sym)}: calls={calls}; state booked={run['m4_booked_kwh']} "
                  f"measured={run['m4_measured_kwh']} kWh starts={run['starts']}")
        ex3 += 1
        ex4 += 1
        lines.append(f"{cell} || M3: {v3} | M4: {v4}")
    print(f"RESULT cells_universe={len(cells)} count")
    print(f"RESULT cells_examined_m3={ex3} count")
    print(f"RESULT cells_examined_m4={ex4} count")
    print(f"RESULT cells_not_reached={len(nr)} count")
    tot_bad = sum(v["m3_bad"] for v in runs.values())
    print(f"RESULT m3_stale_minutes_all_states={tot_bad} count (P1 moves it up)")
    unmatched = Counter()
    for v in runs.values():
        unmatched.update(v["r"].att.unmatched)
    print(f"RESULT unattributed_sites={len(unmatched)} count {dict(unmatched)}")
    if a.cells_out:
        with open(a.cells_out, "w") as fh:
            fh.write("\n".join(lines) + "\n")
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
