#!/usr/bin/env python3
"""D16.M4 (effect) on the reference plant: what a pump with an integrating speed loop and a start
hysteresis delivers under the arbiter's writes, against the plan's booked kW and runs.

Metric (one line): power_error[arm] = (mean measured electrical kW over the graded steps - the
plan's booked kW for them) / booked kW, the measured kW being the pump model's draw that the
production arbiter reads back through ``heat_pump_power_entity``; starts[arm] = compressor starts
over the run against the plan's runs (one per contiguous booked stretch). Keyed on the draw the
model produces from the set-point the production write left on the entity.

Command:  PYTHONPATH=tests/hastub ~/venv-ci/bin/python3 dev/audit/rounds/round11/D16/s2/effect.py
          [--perturb no-feedback|P1] [--json PATH]
Expected (baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692): partial |power_error| <= 0.0873 on
k_lift 2-8 (inside the loop's 10 % deadband), -0.18 at 10 (the 55 C ceiling); min-cold-tank
starts 1 on k_lift 2-6.5, 30 at 8 and 38 at 10 (exact), measured 0.602 / 0.5 kW against 1.0 booked;
``--cfg flow_min_lift_k=8``: 1 start at 8, 4 at 10. dhw-only on a 47 C tank: delivered 0 (exact).
The null arm is the plant whose flow lift per kW equals the open-loop map's (k_lift = 5 K/kW).
Machine: box B11 (shared). Counts and ratios only: no wall, CPU or RSS number.

The pump model (no production code): a space circuit whose water leaves at
inlet + k_lift * p (first-order, 2-min water lag), a compressor that starts once the space
set-point sits ``h_start`` above the water and the supply is on in a heating mode, whose speed
integrates the set-point error (dp/dt = KI * (set-point - flow), clamped to [f, P]) and which stops
when, at its floor, the water sits ``h_stop`` above the set-point; a tank that charges at
``dhw_kw`` in a hot-water mode once it reads below its set-point less ``h_dhw``, until it reaches it.
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
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402
import timing  # noqa: E402

KI = 0.08          # kW per K-minute
H_STOP = 2.0       # K
WATER_TAU = 2.0    # minutes
INLET = 30.0       # C, a large emitter/buffer: the return holds over the run


class Pump:
    def __init__(self, f, P, k_lift, h_start, h_dhw=5.0, dhw_kw=2.5, tank=44.0):
        self.f, self.P, self.k, self.h_start = f, P, k_lift, h_start
        self.h_dhw, self.dhw_kw = h_dhw, dhw_kw
        self.p = 0.0
        self.running = False
        self.flow = INLET
        self.starts = 0
        self.tank = tank
        self.charging = False
        self.dhw_starts = 0

    def minute(self, switch, mode, flow_sp, dhw_sp):
        heat_mode = mode in ("Heating", "Heating + DHW")
        dhw_mode = mode in ("DHW (Hot Water)", "Heating + DHW")
        on = switch == "on"
        # hot water first where the mode offers it (the pump's own priority)
        if on and dhw_mode and dhw_sp is not None:
            if not self.charging and self.tank < dhw_sp - self.h_dhw:
                self.charging = True
                self.dhw_starts += 1
            if self.charging and self.tank >= dhw_sp:
                self.charging = False
        else:
            self.charging = False
        if self.charging:
            self.tank += self.dhw_kw * 3.0 * (1 / 60) / (0.2 * 1.163)  # 200 l, COP 3
            self.running = False
            self.flow += (INLET - self.flow) / WATER_TAU
            return self.dhw_kw
        if not (on and heat_mode) or flow_sp is None:
            self.running, self.p = False, 0.0
        elif not self.running:
            if flow_sp - self.flow >= self.h_start:
                self.running, self.p = True, self.f
                self.starts += 1
        else:
            self.p = min(self.P, max(self.f, self.p + KI * (flow_sp - self.flow)))
            if self.p <= self.f and self.flow >= flow_sp + H_STOP:
                self.running, self.p = False, 0.0
        target = INLET + self.k * self.p if self.running else INLET
        self.flow += (target - self.flow) / WATER_TAU
        return self.p if self.running else 0.0


def run_space(k_lift, h_start, kind="partial", steps=10, perturb=None, cfg_extra=None, hyst_entity=False,
              phase=1):
    extra = dict(cfg_extra or {})
    extra.update({"compressor_freq_entity": None, "freq_control_mode": None})
    if hyst_entity:
        extra["space_hysteresis_entity"] = "sensor.space_hyst"
    st = rig.states(rig.T0)
    if hyst_entity:
        from harness import FakeState
        st["sensor.space_hyst"] = FakeState(str(h_start), unit="K", last_updated=rig.T0)
    sim = rig.Sim(cfg=rig.config(**extra), st=st)
    c = sim.coord
    f = float(c._thermal_model.params.min_electrical_power)
    P = float(c._thermal_model.params.max_electrical_power)
    kinds = ["idle"] + [kind] * steps + ["idle"]
    plan = rig.plan(timing.rows_for(kinds, f, P))
    pump = Pump(f, P, k_lift, h_start)
    draws = {}
    with timing.perturbed(perturb):
        for m in range(len(kinds) * 15):
            t = rig.T0 + timedelta(minutes=m)
            sim.at(t)
            k = rig.oracle_index(plan, t)
            kw = pump.minute(sim.value("switch"), sim.value("mode"), float(sim.value("flow")),
                             float(sim.value("dhw")))
            draws.setdefault(k, []).append(kw)
            timing._fresh(sim, t, power=f"{kw:.3f}")
            if hyst_entity:
                s_ = sim.hass.states.get("sensor.space_hyst")
                s_.last_updated = s_.last_reported = t
            if m >= phase and (m - phase) % 30 == 0:
                sim.cycle(plan)
            sim.tick()
    graded = [k for k in range(3, 1 + steps)]  # past the first 30 minutes of the stretch
    booked = sum(plan.power_schedule[k] for k in graded) / len(graded)
    measured = sum(sum(draws[k]) / len(draws[k]) for k in graded) / len(graded)
    per_step = [round(sum(draws[k]) / len(draws[k]), 3) for k in range(1, 1 + steps)]
    return {"k_lift": k_lift, "h_start": h_start, "kind": kind, "booked_kw": round(booked, 3),
            "measured_kw": round(measured, 3), "power_error": round((measured - booked) / booked, 4),
            "starts": pump.starts, "planned_runs": 1, "per_step_kw": per_step}


def run_dhw_only(tank, hyst_entity, perturb=None):
    """``dhw-only`` on a tank above its set-point less the pump's hysteresis (3531)."""
    extra = {"compressor_freq_entity": None, "freq_control_mode": None}
    st = rig.states(rig.T0)
    if hyst_entity:
        from harness import FakeState
        extra["dhw_hysteresis_entity"] = "sensor.dhw_hyst"
        st["sensor.dhw_hyst"] = FakeState("5", unit="K", last_updated=rig.T0)
    sim = rig.Sim(cfg=rig.config(**extra), st=st)
    c = sim.coord
    f = float(c._thermal_model.params.min_electrical_power)
    P = float(c._thermal_model.params.max_electrical_power)
    kinds = ["idle", "dhw-only", "dhw-only", "idle"]
    plan = rig.plan(timing.rows_for(kinds, f, P))
    pump = Pump(f, P, 5.0, 2.0, tank=tank)
    kwh = 0.0
    with timing.perturbed(perturb):
        for m in range(len(kinds) * 15):
            t = rig.T0 + timedelta(minutes=m)
            sim.at(t)
            kw = pump.minute(sim.value("switch"), sim.value("mode"), float(sim.value("flow")),
                             float(sim.value("dhw")))
            kwh += kw / 60
            timing._fresh(sim, t, tank=f"{pump.tank:.2f}", power=f"{kw:.3f}")
            if hyst_entity:
                s_ = sim.hass.states.get("sensor.dhw_hyst")
                s_.last_updated = s_.last_reported = t
            if m >= 1 and (m - 1) % 30 == 0:
                sim.cycle(plan)
            sim.tick()
    from heatpump_optimizer import pump_arbiter
    ledger = [r.get("verdict") for r in pump_arbiter.diagnostics_view(c).get("ledger", {}).get("steps", [])] \
        if isinstance(pump_arbiter.diagnostics_view(c).get("ledger"), dict) else pump_arbiter.diagnostics_view(c)
    booked = sum(plan.dhw_power_schedule) * 0.25
    return {"tank0": tank, "hyst_entity": hyst_entity, "booked_kwh": booked, "delivered_kwh": round(kwh, 3),
            "dhw_starts": pump.dhw_starts, "dhw_setpoint_written": sim.value("dhw"), "ledger": ledger}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", default=None)
    ap.add_argument("--json", default=None)
    ap.add_argument("--cfg", action="append", default=[],
                    help="a config override KEY=FLOAT for every arm, e.g. flow_min_lift_k=8 (the D16-s2-04 perturbation)")
    a = ap.parse_args()
    c0, t0 = time.process_time(), time.thread_time()
    cfg_extra = {"space_setpoint_power_feedback": False} if a.perturb == "no-feedback" else {}
    for kv in a.cfg:
        key, val = kv.split("=", 1)
        cfg_extra[key] = float(val)
    pert = None if a.perturb == "no-feedback" else a.perturb
    out = {"space": [], "dhw": []}
    for kind in ("partial", "min-cold-tank", "full"):
        for k_lift in (2.0, 3.5, 5.0, 6.5, 8.0, 10.0):
            r = run_space(k_lift, 2.0, kind=kind, perturb=pert, cfg_extra=cfg_extra)
            out["space"].append(r)
            print(f"{kind} k_lift={k_lift}: {json.dumps(r)}")
    for h, ent in ((7.0, False), (7.0, True)):
        r = run_space(5.0, h, kind="min-cold-tank", perturb=pert, cfg_extra=cfg_extra, hyst_entity=ent)
        out["space"].append(r)
        print(f"min-cold-tank h_start={h} hysteresis entity={ent}: {json.dumps(r)}")
    for kind in ("partial", "min-cold-tank"):
        rows = [r for r in out["space"] if r["kind"] == kind and r["h_start"] == 2.0]
        errs = [abs(r["power_error"]) for r in rows]
        null = [r for r in rows if r["k_lift"] == 5.0][0]
        drop = sorted(errs)[:-1]
        print(f"RESULT {kind}_abs_power_error_mean={sum(errs) / len(errs):.4f} ratio over {len(errs)} plants")
        print(f"RESULT {kind}_loo_min={min(errs):.4f} {kind}_loo_max={max(errs):.4f} "
              f"{kind}_loo_drop_most_favourable={sum(drop) / len(drop):.4f}")
        print(f"RESULT {kind}_null_k5_power_error={null['power_error']:.4f} ratio")
        print(f"RESULT {kind}_starts_over_runs={sum(r['starts'] for r in rows)}/{len(rows)} count")
        for r in rows:
            print(f"RESULT {kind}_k{r['k_lift']}_starts={r['starts']} count measured_kw={r['measured_kw']}")
    for tank, ent in ((47.0, False), (47.0, True), (40.0, False)):
        r = run_dhw_only(tank, ent, pert)
        out["dhw"].append(r)
        print(f"dhw-only tank={tank} hysteresis entity={ent}: {json.dumps(r, default=str)[:400]}")
        print(f"RESULT dhw_only_tank{int(tank)}_ent{int(ent)}_delivered_share="
              f"{r['delivered_kwh'] / r['booked_kwh']:.4f} ratio starts={r['dhw_starts']}")
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(out, fh, default=str)
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
