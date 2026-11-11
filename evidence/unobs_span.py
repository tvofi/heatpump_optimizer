"""Reviewer harness: a counter span with an observed (bridged) hot-water charge
and one cycle whose mode read was not live. Prints the span's space figure."""
import sys
from datetime import datetime, timedelta, timezone
from custom_components.heatpump_optimizer import heat_energy as he
NOW = datetime(2026, 1, 10, 22, 0, tzinfo=timezone.utc)
BOUNDS = (0.5, 6.0)

def run(unobserved_cycle, charge=True):
    m = he.HeatEnergyMeter()
    # 5 reads, 30 min apart: space 2 kWh/step, a 5 kWh charge in step 2
    # 12 reads, 30 min apart: 1 kWh per space step; with ``charge`` the step to read 3 is a 5 kWh charge, mode DHW from read 2
    reads, kwh = [], 10.0
    for i in range(12):
        kwh += 0.0 if i == 0 else (5.0 if charge and i == 3 else 1.0)
        reads.append(kwh)
    modes = [he.MODE_DHW if charge and i == 2 else he.MODE_HEAT for i in range(12)]
    ev = None
    for i, kwh in enumerate(reads):
        at = NOW + timedelta(hours=0.5 * i)
        live = i != unobserved_cycle
        changed = at - timedelta(hours=1) if i == 0 else (at if modes[i] != modes[i - 1] else None)
        m.observe_mode(at, modes[i], live, changed)
        m.observe_counters(at, kwh, None, configured=True, cadence_h=0.5, bounds_h=BOUNDS, max_heat_kw=30.0)
        got = m.settle({"house": True, "lower": True}, (1.0, 0.0), ("s", at))
        ev = got or ev
    return ev

for label, unobs, charge in (("charge, all observed", None, True),
                             ("charge, cycle 6 mode not live", 6, True),
                             ("no charge, cycle 6 mode not live (null)", 6, False)):
    ev = run(unobs, charge)
    if ev is None or ev.energy is None:
        print(f"RESULT {label}: no span closed ({ev})"); continue
    sh = he.span_heat(ev, 3.0)
    print(f"RESULT {label}: heat_kw={sh.heat_kw} space_kw={sh.space_kw} dhw_kwh={ev.energy.dhw_kwh} "
          f"observed={ev.attribution.observed} hours={ev.energy.hours}")
