"""Reviewer attack harness (extends the finder's ev/unobs_span.py): the unobserved
mode read at every position of the span, with and without the observed charge,
plus a charge whose own step is the unobserved one."""
from datetime import datetime, timedelta, timezone
from custom_components.heatpump_optimizer import heat_energy as he
NOW = datetime(2026, 1, 10, 22, 0, tzinfo=timezone.utc)
BOUNDS = (0.5, 6.0)

def run(unobs, charge=True, charge_at=3):
    m = he.HeatEnergyMeter()
    reads, kwh = [], 10.0
    for i in range(12):
        kwh += 0.0 if i == 0 else (5.0 if charge and i == charge_at else 1.0)
        reads.append(kwh)
    modes = [he.MODE_DHW if charge and i == charge_at - 1 else he.MODE_HEAT for i in range(12)]
    ev = None
    for i, kwh in enumerate(reads):
        at = NOW + timedelta(hours=0.5 * i)
        live = i not in unobs
        changed = at - timedelta(hours=1) if i == 0 else (at if modes[i] != modes[i - 1] else None)
        m.observe_mode(at, modes[i], live, changed)
        m.observe_counters(at, kwh, None, configured=True, cadence_h=0.5, bounds_h=BOUNDS, max_heat_kw=30.0)
        got = m.settle({"house": True, "lower": True}, (1.0, 0.0), ("s", at))
        ev = got or ev
    return ev

cases = [("charge all observed", (), True)]
for u in (0, 1, 2, 3, 4, 6, 10, 11):
    cases.append((f"charge unobs@{u}", (u,), True))
cases.append(("charge unobs@2,3 (charge cycle itself)", (2, 3), True))
cases.append(("charge unobs@1,6,11", (1, 6, 11), True))
for u in (1, 6, 11):
    cases.append((f"null no-charge unobs@{u}", (u,), False))
cases.append(("null no-charge all observed", (), False))
for label, unobs, charge in cases:
    ev = run(set(unobs), charge)
    if ev is None or ev.energy is None:
        print(f"RESULT {label}: no span closed"); continue
    sh = he.span_heat(ev, 3.0)
    print(f"RESULT {label}: heat_kw={sh.heat_kw:.3f} space_kw={sh.space_kw} dhw_kwh={ev.energy.dhw_kwh} "
          f"dhw_seen={getattr(ev.energy,'dhw_seen','n/a')} observed={ev.attribution.observed} hours={ev.energy.hours} span={ev.energy.start.time()}-{ev.energy.end.time()}")
