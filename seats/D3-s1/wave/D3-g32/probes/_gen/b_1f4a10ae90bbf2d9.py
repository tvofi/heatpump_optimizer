from datetime import datetime, timedelta, timezone
from custom_components.heatpump_optimizer import sysid

OLD = "        dt = utc_elapsed_seconds(rows[-1].when, rows[-2].when) / 3600.0 if len(rows) > 1 else 0.25"
NEW = "        dt = utc_elapsed_seconds(rows[-1].when, rows[-2].when) / 3600.0 if len(rows) >= 1 else 0.25"
mut = mutate(sysid.SystemIdentification, "_unadoptable", OLD, NEW)
t0 = datetime(2026, 1, 14, 2, 0, tzinfo=timezone.utc)


def outcome(fn, n_rows):
    s = sysid.SystemIdentification(sysid.SysIdConfig(enabled=True))
    s.samples = [sysid.SysIdSample(t0 + timedelta(minutes=15 * i), 20.0, -2.0, 0.0, sysid.PHASE_SETTLING)
                 for i in range(n_rows)]
    s._slab_pair, s._slab_prior, s._baseline_temp = (8.0, 0.5), (0.2, 6.0), 20.0
    try:
        return repr(fn(s, 1.0, -2.0))
    except Exception as err:  # noqa: BLE001
        return f"raised {type(err).__name__}"


for n in (0, 1, 2, 4):
    b, m = outcome(sysid.SystemIdentification._unadoptable, n), outcome(mut, n)
    print(f"RESULT rows{n}_baseline={b}")
    print(f"RESULT rows{n}_mutant={m}")
    print(f"RESULT rows{n}_moved={int(b != m)} count")
# reach: drive the state machine through step() from SETTLING, at 15-min and 60-min cadence, and count the
# settling rows _unadoptable sees when _begin_step_phase calls it
seen = []
real = sysid.SystemIdentification._unadoptable


def spy(self, step_kw, outdoor):
    seen.append(sum(1 for r in self.samples if r.phase == sysid.PHASE_SETTLING))
    return real(self, step_kw, outdoor)


import numpy as np
for minutes in (15, 30, 60, 90):
    s = sysid.SystemIdentification(sysid.SysIdConfig(enabled=True))
    s.phase, s.phase_started, s._baseline_temp = sysid.PHASE_SETTLING, t0, 20.0
    s._slab_pair, s._slab_prior = (8.0, 0.5), (0.2, 6.0)
    with mock.patch.object(sysid.SystemIdentification, "_unadoptable", spy):
        for i in range(8):
            s.step(t0 + timedelta(minutes=minutes * i), 20.0, -2.0, 0.5, np.array([0.5, 1.0, 2.0]), 100, 6.0, 3.0,
                   0.5, sysid.HousePlant(ua=0.2, capacity=6.0, gains=0.3, slab_mass=8.0, slab_transfer=0.5))
            if s.phase != sysid.PHASE_SETTLING:
                break
print(f"RESULT step_driven_unadoptable_calls={len(seen)} count  min_settling_rows={min(seen) if seen else None}")
tail()
