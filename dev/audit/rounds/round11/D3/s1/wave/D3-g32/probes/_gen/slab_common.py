import numpy as np
from custom_components.heatpump_optimizer import sysid

SID = sysid.SystemIdentification
# The interval and confidence helpers are stubbed to constants in BOTH arms: the metric reads only the fields the
# mutated lines decide (completed, reason, internal_gains_kw, heat_loss_kw_per_c), never the stubbed ones.
STUBS = {"_slab_ua_profile_halfwidth": lambda *a, **k: 0.01, "_slab_ua_prior_halfwidth": lambda *a, **k: 0.01,
         "_slab_ua_told_halfwidth": lambda *a, **k: 0.01, "_slab_confidence": lambda *a, **k: 0.9}
ROOMS = np.full(20, 20.0)


def outcome(fn, ua, room_cap, gains, slab_mass=8.0, slab_transfer=0.5):
    s = SID(sysid.SysIdConfig(enabled=True))
    x = np.array([np.log(ua), np.log(room_cap), gains])
    with mock.patch.dict(fn.__globals__, STUBS):
        r = fn(s, x, ROOMS, lambda v: np.zeros(ROOMS.size), slab_mass, slab_transfer, lambda a, b: None)
    return (r.completed, r.reason, None if r.internal_gains_kw is None else round(r.internal_gains_kw, 6))


GRID = [(ua, c, g) for ua in (0.005, 0.2, 6.0) for c in (-1.0, 4.0) for g in (-0.8, -0.5, -0.3, 0.0, 0.4, 2.0, 2.5)]
