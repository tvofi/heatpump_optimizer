"""D12.M3 -- a counter-metered pump whose spans hold hot-water charges, driven
through consecutive real coordinator cycles.

Metric (one line): over CYCLES cycles 30 min apart on a plant with an electric
and a heat counter (no power entity) and a DHW tank, RESULT bad_spans = closed
heat-counter spans that carried a hot-water charge (SpanEnergy.dhw_seen or a
DHW share in the attribution) whose space heat handed to the learners is NOT
net of the charge (space_kw > (heat_kwh - dhw_kwh)/hours + 1e-6, or a space
figure with dhw_kwh unknown); plus RESULT dhw_cop_records_unseen = measured-COP
records (accuracy.MeasuredCop.record) made while heat_meter_sees_dhw is False
for a hot-water curve (must be 0: a meter not declared to see the DHW circuit
measures no DHW COP). RESULT spans_closed / spans_with_dhw are the denominators.

Count key: what production hands on -- heat_energy.span_heat's returned
SpanHeat against the SpanEnergy it read, and MeasuredCop.record's arguments --
never the harness's own simulated counters.

The plant: switch, electric counter, heat counter, DHW 180 L with a tank
thermometer; per cycle the electric counter advances by the plan's commanded
energy for the half hour, the heat counter by 3x that, the tank rises 4 K in a
cycle whose plan step charges hot water (else falls 0.5 K).

Cycles 4-6 the pump's own DHW timer charges the tank at 2.5 kW whatever the plan
asked (FORCED_DHW), so closed spans carry a charge; --plan-only drops the timer.

Run:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D12/s3/counter_spans.py [--sees-dhw] [--no-mode] [--plan-only] [--perturb no-subtract]
--sees-dhw is the arm where a DHW COP record is allowed (dhw_cop_records counted, not judged).
--perturb no-subtract: heat_energy.span_heat with its DHW subtraction removed
(space_heat_kw on the whole span): bad_spans must go UP wherever spans_with_dhw > 0.
Expected at baseline 92d38ecb: bad_spans=0, dhw_cop_records_unseen=0 (exact); see REPORT.md for
spans_closed/spans_with_dhw.
Machine: box B6, Linux x86_64, python 3.14.
Instrumented: heatpump_optimizer.heat_energy:span_heat, heatpump_optimizer.accuracy:MeasuredCop.record,
heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_update_data.
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import bisect
import time
from datetime import timedelta
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import surfaces as S  # noqa: E402
from harness import FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import accuracy, heat_energy  # noqa: E402
from heatpump_optimizer import const as c  # noqa: E402

CYCLES = 16
#: The pump's own hot-water timer: cycles whose half hour it spends charging
#: the tank whatever the plan asked (a pump-side DHW schedule), so the step's
#: cell -- spans that hold a hot-water charge -- is exercised however the
#: plan places DHW. --plan-only drops it (the first run's arm: spans_with_dhw=0).
FORCED_DHW = range(4, 7)
FORCED_DHW_KW = 2.5
KWH = {"unit_of_measurement": "kWh", "device_class": "energy", "state_class": "total_increasing"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sees-dhw", action="store_true")
    ap.add_argument("--perturb", choices=["no-subtract", "unobserved-no-space"])
    ap.add_argument("--plan-only", action="store_true", help="no pump-side DHW timer: DHW only where the plan charges")
    ap.add_argument("--no-mode", action="store_true", help="no mode select: every span unobserved (plan split)")
    a = ap.parse_args()
    t0, c0, th0 = time.time(), time.process_time(), time.thread_time()
    spans, records = [], []
    real_span_heat, real_record = heat_energy.span_heat, accuracy.MeasuredCop.record

    def span_heat(ev, modelled_cop):
        got = real_span_heat(ev, modelled_cop)
        spans.append((ev, got))
        return got

    def no_subtract(ev, modelled_cop):
        got = real_span_heat(ev, modelled_cop)
        e = ev.energy
        if e is not None and got.heat_kw is not None:
            got = got._replace(space_kw=heat_energy.space_heat_kw(got.heat_kw, ev.attribution, integrated=True))
        spans.append((ev, got))
        return got

    closes = []
    real_close_span = heat_energy.close_span

    def close_span(*args, **kw):
        got = real_close_span(*args, **kw)
        if got.space_kw is not None:
            closes.append((got.space_kw, bool(got.house), bool(got.lower)))
        return got

    def unobserved_no_space(heat_kw, att, integrated):
        # Perturbation: an unobserved integrated span reads no space figure (one-line
        # production edit: `if integrated and not a.observed: return None` in space_heat_kw).
        if integrated and not att.observed:
            return None
        return real_space_heat_kw(heat_kw, att, integrated)
    real_space_heat_kw = heat_energy.space_heat_kw

    def record(self, cop, curve_dhw, dhw_temp, at):
        records.append(bool(curve_dhw))
        return real_record(self, cop, curve_dhw, dhw_temp, at)

    cfg = {**S.GEN_BASE, c.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.hp",
           c.CONF_ENERGY_ENTITY: "sensor.hp_energy", c.CONF_HEAT_ENERGY_ENTITY: "sensor.heat_energy",
           c.CONF_HEAT_METER_SEES_DHW: bool(a.sees_dhw)}
    if not a.no_mode:
        cfg[c.CONF_HEAT_PUMP_MODE_ENTITY] = "select.hp_mode"
    elec, heat, tank = 1000.0, 3000.0, 44.0
    mode, mode_at = "Heating", None
    states = {**S.GEN_STATES, "switch.hp": FakeState("on"),
              "sensor.hp_energy": FakeState(f"{elec:.3f}", attributes=KWH),
              "sensor.heat_energy": FakeState(f"{heat:.3f}", attributes=KWH),
              "sensor.dhw": S.T(tank)}
    start = dt_util.now().replace(minute=0, second=0, microsecond=0)
    dt_util.freeze(start)
    hass, coord = S.build(cfg, states, entry_id="d12s3_counter")
    ok = published = 0
    truth = []  # (start, end, space heat kWh, hot-water heat kWh) the plant really put out per half hour
    raised = []
    patches = [mock.patch.object(heat_energy, "span_heat", no_subtract if a.perturb == "no-subtract" else span_heat),
               mock.patch.object(accuracy.MeasuredCop, "record", record),
               mock.patch.object(heat_energy, "close_span", close_span)]
    if a.perturb == "unobserved-no-space":
        patches[0] = mock.patch.object(heat_energy, "span_heat", span_heat)
        patches.append(mock.patch.object(heat_energy, "space_heat_kw", unobserved_no_space))
    for p in patches:
        p.start()
    try:
        for i in range(CYCLES):
            now = start + timedelta(minutes=30 * i)
            dt_util.freeze(now)
            for k, v in (("sensor.hp_energy", elec), ("sensor.heat_energy", heat)):
                hass.states.set(k, FakeState(f"{v:.3f}", attributes=KWH, last_updated=now))
            hass.states.set("sensor.dhw", FakeState(f"{tank:.1f}", attributes={"unit_of_measurement": "°C"},
                                                    last_updated=now))
            if not a.no_mode:
                hass.states.set("select.hp_mode", FakeState(mode, attributes={"options": S.TUYA_OPTIONS},
                                                            last_updated=mode_at))
            for k in ("sensor.indoor", "sensor.outdoor"):
                hass.states.set(k, FakeState(states[k].state, attributes=dict(states[k].attributes),
                                             last_updated=now))
            try:
                asyncio.run(coord._async_update_data())
                ok += 1
            except Exception as err:  # noqa: BLE001
                raised.append(f"cycle {i}: {type(err).__name__}: {err}")
                continue
            res = coord._optimization_result
            if res is None:
                continue
            published += 1
            j = max(0, bisect.bisect_right(res.timestamps, now) - 1)
            sp = float(res.power_schedule[j]) if j < len(res.power_schedule) else 0.0
            dh = float((res.dhw_power_schedule or [0.0] * (j + 1))[j]) if res.dhw_power_schedule else 0.0
            if i in FORCED_DHW and not a.plan_only:
                dh = max(dh, FORCED_DHW_KW)
            truth.append((now, now + timedelta(minutes=30), 3.0 * sp * 0.5, 3.0 * dh * 0.5))
            elec += (sp + dh) * 0.5
            heat += 3.0 * (sp + dh) * 0.5
            tank = tank + 4.0 if dh > 0.05 else tank - 0.5
            # the pump serves the step the plan holds: one duty, as a single-duty Tuya select shows it
            new_mode = "DHW" if dh > 0.05 else "Heating"
            if new_mode != mode:
                mode, mode_at = new_mode, now
    finally:
        for p in patches:
            p.stop()
    closed = [(ev, got) for ev, got in spans if ev.energy is not None]
    with_dhw = [(ev, got) for ev, got in closed
                if ev.energy.dhw_seen or heat_energy.ran_hot_water(ev.attribution)]
    bad = 0
    for ev, got in closed:  # an unobserved span the plan split gave hot water reads no space figure
        if not ev.attribution.observed and ev.attribution.dhw > 0.0 and got.space_kw is not None:
            bad += 1
            print(f"BAD unobserved span with plan DHW share {ev.attribution.dhw:.2f} -> space {got.space_kw:.3f} kW")
    for ev, got in with_dhw:
        e = ev.energy
        if got.space_kw is None:
            continue
        if e.dhw_kwh is None or got.space_kw > (e.heat_kwh - e.dhw_kwh) / e.hours + 1e-6:
            bad += 1
            print(f"BAD span {e.start} {e.hours:.2f} h heat {e.heat_kwh:.2f} dhw {e.dhw_kwh} -> space {got.space_kw:.3f} kW")
    # Ground truth (the plant's own split, which production never sees): a space
    # figure above the span's true space heat carries hot water into the house learner.
    inflated = learned = 0
    for ev, got in closed:
        e = ev.energy
        if got.space_kw is None:
            continue
        true_space = sum(s_kwh for t0_, t1_, s_kwh, _d in truth if t0_ >= e.start and t1_ <= e.end)
        true_dhw = sum(d_kwh for t0_, t1_, _s, d_kwh in truth if t0_ >= e.start and t1_ <= e.end)
        if true_dhw > 0.0 and got.space_kw > true_space / e.hours + 0.05:
            inflated += 1
            folds = [(h, lo) for kw, h, lo in closes if abs(kw - got.space_kw) < 1e-9]
            learned += bool(folds and (folds[0][0] or folds[0][1]))
            print(f"INFLATED span {e.start} {e.hours:.2f} h observed={ev.attribution.observed} space {got.space_kw:.3f} kW vs true {true_space / e.hours:.3f} kW (hot water {true_dhw:.2f} kWh)")
    for r in raised:
        print("RAISED", r)
    print(f"RESULT arm={'sees_dhw' if a.sees_dhw else 'unseen'}{'+no_mode' if a.no_mode else '+tuya_mode'}{'+plan_only' if a.plan_only else '+dhw_timer'}{'+' + a.perturb if a.perturb else ''}")
    print(f"RESULT cycles_ok={ok} count (of {CYCLES})")
    print(f"RESULT plans_published={published} count")
    print(f"RESULT spans_closed={len(closed)} count")
    print(f"RESULT spans_with_dhw={len(with_dhw)} count")
    print(f"RESULT spans_observed={sum(ev.attribution.observed for ev, _ in closed)} count")
    print(f"RESULT spans_plan_dhw_share={sum((not ev.attribution.observed) and ev.attribution.dhw > 0 for ev, _ in closed)} count")
    print(f"RESULT bad_spans={bad} count")
    print(f"RESULT spans_true_dhw={sum(any(d > 0 and t0_ >= ev.energy.start and t1_ <= ev.energy.end for t0_, t1_, _s, d in truth) for ev, _ in closed)} count")
    print(f"RESULT inflated_space_spans={inflated} count")
    print(f"RESULT inflated_spans_folded={learned} count")
    print(f"RESULT space_spans_folded={sum(h or lo for _kw, h, lo in closes)} count")
    print(f"RESULT cop_records={len(records)} count")
    print(f"RESULT dhw_cop_records={sum(records)} count")
    print(f"RESULT dhw_cop_records_unseen={0 if a.sees_dhw else sum(records)} count")
    pc, tc = time.process_time() - c0, time.thread_time() - th0
    print(f"RESULT wall_s={time.time() - t0:.1f} s (provisional)")
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=" + str(next((int(x.split()[1]) for x in open('/proc/vmstat') if x.startswith('pswpin')), 0)))


if __name__ == "__main__":
    main()
